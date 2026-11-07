# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""The host-side vLLM forwarder (Phase 110, the egress-control change).

The trial containers live on the run's private `--internal` bridge network
(:data:`c4_skills.pins.NETWORK_MODE`): Docker enforces no route from that
network to the outside world, so the only endpoints a trial can reach are
the two the harness explicitly exposes on it -- the sidecar on its own
container IP, and the shared vLLM server (through this forwarder, or
through the server's own 0.0.0.0 bind when it already answers at the
gateway -- the mode selection lives in the runner, not here).

This forwarder is the PREFERRED vLLM access for the trials (the option-C
conditional of `runner.establish_vllm_access`): one listener bound to the
network's GATEWAY IP (a host interface address, which the host may bind)
and one thread per accepted connection. Each connection is relaying bytes
to the vLLM endpoint on the host loopback in both directions (one blocking
relay per direction, driven by the connection's own thread), so a
streaming OpenAI-compatible response flows intact while the request side
stays open. When the gateway address:port is already owned by the shared
vLLM's own 0.0.0.0 bind (EADDRINUSE), the runner uses the verified-direct
path instead and no forwarder is started -- this module is then not
involved.

Nothing here ever raises on the network side: a client disconnect, a
target that is down (the connection is closed to the client instead) and
a `stop` while traffic is in flight all terminate quietly -- the harness
teardown runs in a `finally` and must not mask the run's real outcome.
"""

from __future__ import annotations

import selectors
import socket
import threading

#: The recv buffer size of every relay copy (64 KiB keeps the memory bound
#: small; HTTP bodies and SSE streams copy in whole chunks).
RECV_BUF = 65_536

#: How long a connection may wait for the TARGET to accept (vLLM on the
#: loopback is local; a long hang here means the target is gone and the
#: connection is dropped to the client).
CONNECT_TIMEOUT_S = 30.0

#: The accept loop's poll timeout: short enough that a `stop` drains the
#: accept queue and the loop exits within a couple of these, long enough
#: that the idle loop costs nothing measurable (no wake-up protocol is
#: needed -- the poll itself observes the queue).
_ACCEPT_POLL_S = 0.1


class ForwarderHandle:
    """A running forwarder (listener + the connection threads).

    Attributes:
        bind_ip: The address the listener is bound to (the network's
            gateway IP -- a host interface address).
        bind_port: The port the listener answers on (vLLM's host port, so
            `http://<bind_ip>:<bind_port>/v1` works for the trial).
        target_ip: The upstream address connections are relayed to
            (the vLLM host loopback).
        target_port: The upstream port (vLLM's host port).
    """

    def __init__(self, bind_ip: str, bind_port: int, target_ip: str, target_port: int) -> None:
        self.bind_ip: str = bind_ip
        self.bind_port: int = bind_port
        self.target_ip: str = target_ip
        self.target_port: int = target_port
        self._listener: socket.socket | None = None
        self._stop_event: threading.Event = threading.Event()
        self._accept_thread: threading.Thread | None = None
        self._live: set[threading.Thread] = set()
        self._live_lock: threading.Lock = threading.Lock()

    @property
    def address(self) -> tuple[str, int]:
        """The (ip, port) the forwarder answers on."""
        result: tuple[str, int] = (self.bind_ip, self.bind_port)
        return result

    def active_connections(self) -> int:
        """Count the connection threads still draining (diagnostics)."""
        with self._live_lock:
            result: int = sum(1 for thread in self._live if thread.is_alive())
            return result


def _relay(src: socket.socket, dst: socket.socket) -> None:
    """Copy `src` -> `dst` until EOF or error; half-close `dst` afterwards.

    Never raises: a client or target disconnect ends this direction's copy
    and signals the peer by half-closing it (the peer's relay then sees the
    EOF and half-closes back).
    """
    try:
        while True:
            data = src.recv(RECV_BUF)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def _serve_connection(handle: ForwarderHandle, client: socket.socket) -> None:
    """Relay one accepted connection to the target, both directions.

    Never raises: a target that is down closes the client side (the trial
    then sees the connection refused/reset, exactly as if the vLLM port
    were closed); a client disconnect ends the relays.
    """
    upstream: socket.socket | None = None
    try:
        try:
            upstream = socket.create_connection((handle.target_ip, handle.target_port), timeout=CONNECT_TIMEOUT_S)
        except OSError:
            return  # target down: drop the client connection quietly
        upstream.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        to_target = threading.Thread(target=_relay, args=(client, upstream), daemon=True)
        to_client = threading.Thread(target=_relay, args=(upstream, client), daemon=True)
        to_target.start()
        to_client.start()
        to_target.join()
        to_client.join()
    finally:
        for sock in (client, upstream):
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass


def _accept_loop(handle: ForwarderHandle) -> None:
    """Accept connections until the stop event is set AND the queue drained (one thread each).

    Polls the listener with a short timeout instead of blocking in
    `accept()` (closing the fd from another thread does not reliably wake
    a blocked `accept()` on Linux): before the stop event, a poll timeout
    is just a loop (negligible overhead); after it, the loop keeps
    accepting while the queue is non-empty and exits once a poll finds it
    drained. The drain is structural -- every connection that completed
    its kernel-level handshake before the stop was `accept`ed and handed
    to a worker BEFORE :func:`stop` joins this thread and closes the
    listener, so a queued connection can never be reset by the close, and
    no byte of any real connection is ever consumed by the loop itself.
    """
    assert handle._listener is not None
    listener = handle._listener
    with selectors.DefaultSelector() as poll:
        poll.register(listener, selectors.EVENT_READ)
        while True:
            try:
                events = poll.select(timeout=_ACCEPT_POLL_S)
            except OSError:
                return  # the listener closed (a racing double stop) -- exit quietly
            if events:
                try:
                    client, _addr = listener.accept()
                except OSError:
                    return  # the listener closed between select and accept -- exit quietly
                try:
                    client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                except OSError:
                    pass
                thread = threading.Thread(target=_connection_worker, args=(handle, client), daemon=True)
                with handle._live_lock:
                    handle._live.add(thread)
                thread.start()
            elif handle._stop_event.is_set():
                return  # the stop event is set and the accept queue is drained


def _connection_worker(handle: ForwarderHandle, client: socket.socket) -> None:
    """The per-connection thread: the relay pair plus its own deregistration."""
    try:
        _serve_connection(handle, client)
    finally:
        with handle._live_lock:
            handle._live.discard(threading.current_thread())


def start_forwarder(*, bind_ip: str, bind_port: int, target_ip: str, target_port: int) -> ForwarderHandle:
    """Start the forwarder (listener + accept thread).

    Args:
        bind_ip: The address to bind (the network's gateway IP).
        bind_port: The port to bind (vLLM's host port).
        target_ip: The upstream address (the vLLM host loopback).
        target_port: The upstream port (vLLM's host port).

    Returns:
        The ForwarderHandle (stop it with :func:`stop`).

    Raises:
        OSError: When the bind address is unavailable (port already taken,
            or the IP is not a local interface address).
    """
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind((bind_ip, bind_port))
        listener.listen(128)
    except OSError:
        listener.close()
        raise
    handle = ForwarderHandle(bind_ip=bind_ip, bind_port=bind_port, target_ip=target_ip, target_port=target_port)
    handle._listener = listener
    handle._accept_thread = threading.Thread(
        target=_accept_loop, args=(handle,), name="c4eval-forwarder-accept", daemon=True
    )
    handle._accept_thread.start()
    result = handle
    return result


def stop(handle: ForwarderHandle) -> None:
    """Stop the accept loop (draining the queue) and only then close the listener.

    Never raises: `stop` runs in the harness teardown `finally` and may be
    called twice (or on a handle whose listener already went away -- the
    join on a dead thread returns immediately, the close is guarded).

    The ordering IS the contract: the stop event is set, the accept thread
    is JOINED first -- it exits only once the accept queue has drained, so
    every connection that completed its kernel-level handshake before the
    join was `accept`ed and handed to a worker -- and only then the
    listener closes. Joining before the close is what makes the close
    RST-free by construction (a queued connection can never be destroyed
    un-accepted). A join timeout still proceeds to the close (teardown
    must not hang; the loop then sees the closed fd and exits, and the
    daemon threads end with the process if the harness exits first).
    Active connections are not killed -- their relays finish on their own.
    """
    handle._stop_event.set()
    accept_thread = handle._accept_thread
    if accept_thread is not None:
        accept_thread.join(timeout=5.0)
    listener = handle._listener
    if listener is not None:
        try:
            listener.close()
        except OSError:
            pass
