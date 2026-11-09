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

"""Forwarder tests (no Docker, no model: localhost TCP with ephemeral ports).

The vLLM forwarder (Phase 110) is the only host-side process the run's
private network sees (besides the sidecar container): it binds the
network's gateway IP and relays to vLLM on the host loopback. Here the
"gateway" is 127.0.0.1 with an ephemeral port and the "vLLM" is a local
echo server -- the same code paths, no external dependency.

Covers the locked contract: connect -> echo -> close; a streaming write
stays intact; `stop` closes the listener (and unblocks the accept loop)
while active connections drain; client disconnects and a down target
never raise.
"""

import socket
import threading
import time
import unittest

from c4_skills import forwarder

#: How long tests wait for a socket/thread condition (generous for CI).
WAIT_S = 5.0


def _free_port() -> int:
    """Ask the kernel for a free localhost TCP port (test bind/close)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    result = port
    return result


def _start_echo_server() -> tuple[socket.socket, threading.Thread, int]:
    """Start a local echo server (one thread per connection).

    Returns:
        (listener, thread, port).
    """
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(16)
    port = listener.getsockname()[1]

    def echo_conn(conn: socket.socket) -> None:
        try:
            while True:
                data = conn.recv(65_536)
                if not data:
                    break
                conn.sendall(data)
        except OSError:
            pass
        finally:
            conn.close()

    def serve() -> None:
        while True:
            try:
                conn, _addr = listener.accept()
            except OSError:
                return  # listener closed
            threading.Thread(target=echo_conn, args=(conn,), daemon=True).start()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    result: tuple[socket.socket, threading.Thread, int] = (listener, thread, port)
    return result


def _connect(host: str, port: int, timeout_s: float = WAIT_S) -> socket.socket:
    """Connect with a small retry (the accept thread may still be starting)."""
    deadline = time.monotonic() + timeout_s
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        try:
            sock = socket.create_connection((host, port), timeout=timeout_s)
            result = sock
            return result
        except OSError as exc:
            last_error = exc
            time.sleep(0.02)
    assert last_error is not None
    raise last_error


class _ForwarderCase(unittest.TestCase):
    """The shared setUp/tearDown: an echo target + a forwarder in front of it."""

    def setUp(self) -> None:
        self._echo_listener, self._echo_thread, self._target_port = _start_echo_server()
        self.addCleanup(self._echo_listener.close)
        self._handle: forwarder.ForwarderHandle | None = None

    def _start(self, target_port: int | None = None) -> forwarder.ForwarderHandle:
        handle = forwarder.start_forwarder(
            bind_ip="127.0.0.1",
            bind_port=_free_port(),
            target_ip="127.0.0.1",
            target_port=target_port if target_port is not None else self._target_port,
        )
        self._handle = handle
        self.addCleanup(self._stop_handle, handle)
        result = handle
        return result

    def _stop_handle(self, handle: forwarder.ForwarderHandle) -> None:
        forwarder.stop(handle)


class TestForwarderRoundTrip(_ForwarderCase):
    """connect -> echo -> close (through the forwarder)."""

    def test_echo_round_trip(self) -> None:
        sut = self._start

        handle = sut()
        client = _connect(*handle.address)
        client.sendall(b"hello forwarder")
        answer = b""
        while len(answer) < len(b"hello forwarder"):
            chunk = client.recv(65_536)
            if not chunk:
                break
            answer += chunk
        client.close()

        self.assertEqual(answer, b"hello forwarder")

    def test_streaming_write_stays_intact(self) -> None:
        # a large payload in two delayed halves: the relay must not reorder,
        # interleave or drop bytes on the way through
        sut = self._start
        payload = bytes(range(256)) * 1024  # 256 KiB, all byte values present
        handle = sut()

        client = _connect(*handle.address)
        client.sendall(payload[: len(payload) // 2])
        time.sleep(0.2)
        client.sendall(payload[len(payload) // 2 :])
        received = b""
        while len(received) < len(payload):
            chunk = client.recv(65_536)
            if not chunk:
                break
            received += chunk
        client.close()

        self.assertEqual(received, payload)


class TestForwarderStop(_ForwarderCase):
    """stop closes the listener and unblocks; active connections drain."""

    def test_stop_closes_the_listener_and_new_connects_refuse(self) -> None:
        sut = self._start

        handle = sut()
        # one established connection to drain
        established = _connect(*handle.address)
        forwarder.stop(handle)

        accept_thread = handle._accept_thread
        self.assertIsNotNone(accept_thread)
        self.assertFalse(accept_thread.is_alive())  # stop unblocked the accept loop
        with self.assertRaises(OSError):
            socket.create_connection(handle.address, timeout=1.0)
        established.close()

    def test_stop_lets_an_active_connection_drain(self) -> None:
        sut = self._start
        payload = b"stream-through-stop"
        handle = sut()

        client = _connect(*handle.address)
        # wait for the accept loop to hand the connection to a worker, so this test
        # exercises ESTABLISHED-connection drain deterministically (bounded by WAIT_S)
        deadline = time.monotonic() + WAIT_S
        while handle.active_connections() < 1 and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertGreaterEqual(handle.active_connections(), 1, "worker for the test connection was not spawned")
        client.sendall(payload)
        # the echo is in flight; stop now (listener closes, relays drain)
        forwarder.stop(handle)
        received = b""
        while len(received) < len(payload):
            chunk = client.recv(65_536)
            if not chunk:
                break
            received += chunk
        client.close()

        self.assertEqual(received, payload)

    def test_stop_is_idempotent_and_never_raises(self) -> None:
        sut = self._start

        handle = sut()
        forwarder.stop(handle)
        forwarder.stop(handle)  # second stop on a dead listener: quiet


class TestForwarderRobustness(_ForwarderCase):
    """Client disconnects and a down target never raise."""

    def test_client_disconnect_leaves_the_forwarder_able_to_serve(self) -> None:
        sut = self._start
        handle = sut()

        # a client that disconnects mid-connection (no reply read)
        dropper = _connect(*handle.address)
        dropper.sendall(b"partial")
        dropper.close()
        accept_alive = handle._accept_thread is not None and handle._accept_thread.is_alive()
        self.assertTrue(accept_alive)  # noqa: S101 -- the accept loop survived
        # the disconnected connection's relays terminate (no leaked threads)
        deadline = time.monotonic() + WAIT_S
        while handle.active_connections() > 0 and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertEqual(handle.active_connections(), 0)

        # ...and the next connection still echoes
        client = _connect(*handle.address)
        client.sendall(b"still alive")
        answer = b""
        while len(answer) < 11:
            chunk = client.recv(65_536)
            if not chunk:
                break
            answer += chunk
        client.close()
        self.assertEqual(answer, b"still alive")

    def test_a_down_target_closes_the_client_quietly(self) -> None:
        # target port with nothing listening: the forwarder must not raise,
        # the client just sees the connection end
        dead_port = _free_port()
        sut = self._start
        handle = sut(target_port=dead_port)

        client = _connect(*handle.address)
        data = client.recv(65_536)

        self.assertEqual(data, b"")  # EOF: the relay dropped the connection
        client.close()
        deadline = time.monotonic() + WAIT_S
        while handle.active_connections() > 0 and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertEqual(handle.active_connections(), 0)  # the worker deregistered
        accept_alive = handle._accept_thread is not None and handle._accept_thread.is_alive()
        self.assertTrue(accept_alive)  # noqa: S101


if __name__ == "__main__":
    unittest.main()
