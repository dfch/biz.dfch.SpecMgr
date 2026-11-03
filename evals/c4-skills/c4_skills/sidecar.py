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

"""The harness's own pinned `structurizr/mcp` sidecar (Task 100.110/120).

The development MCP (bound to `127.0.0.1:3000`) is never used. The sidecar
runs on the host network on a free ephemeral port, is healthy-checked with
a real MCP `initialize` + `tools/list` round trip, and is torn down after
the run. The trial containers reach it over `--network host` at
`http://127.0.0.1:<port>/mcp` (streamable HTTP; verified against the
pinned image).

Port selection is racy (bind/close -> container bind): when a sidecar
fails to become healthy and its container logs show a bind/port-in-use
failure, `start_sidecar` retries with a fresh port (up to
`SIDECAR_START_ATTEMPTS` attempts); the residual window (the port taken
after the log check) is absorbed by the same retry on the next attempt.
"""

from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import pins

#: The sidecar container name prefix (one per run id).
CONTAINER_NAME_PREFIX = "c4eval-mcp-"

#: The sidecar startup budget in seconds (the Spring Boot JVM needs a few).
STARTUP_BUDGET_S = 90.0

#: The health-check poll interval in seconds.
HEALTH_POLL_S = 2.0

#: The sidecar arguments (the dev compose reference: the DSL tools plus the
#: PlantUML and Mermaid exporters).
SIDECAR_ARGS: tuple[str, ...] = ("-dsl", "-plantuml", "-mermaid")

#: The env the sidecar needs (the image's entrypoint resolves `${PORT}`
#: through Spring's own placeholder mechanism; the themes path is the
#: image's installed theme set).
SIDECAR_THEMES = "/usr/local/structurizr-themes"

#: The six stateless DSL tools the pinned image registers (verified at pin
#: time); a health check that sees a different set is a pin drift.
EXPECTED_TOOLS: frozenset[str] = frozenset(
    {"inspect", "parse", "validate", "export-mermaid", "export-c4plantuml", "export-plantuml"}
)


@dataclass(frozen=True)
class SidecarHandle:
    """A running sidecar (port + container id for teardown).

    Attributes:
        port: The host port the sidecar answers on.
        container_id: The Docker container id.
        container_name: The Docker container name.
    """

    port: int
    container_id: str
    container_name: str


def free_host_port() -> int:
    """Ask the host kernel for a free TCP port on 127.0.0.1.

    The bind/close -> container-bind sequence is racy (TOCTOU): another
    process can take the port in the gap, and the sidecar then fails to
    bind. `start_sidecar` therefore retries with a fresh port when the
    container logs show a bind/port-in-use failure; this function is just
    the first candidate of that loop.

    Returns:
        A currently unbound port number.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    result = port
    return result


#: How many sidecar start attempts (fresh port each) before the run aborts.
SIDECAR_START_ATTEMPTS = 3

#: The case-insensitive log markers of a bind/port-in-use failure.
_PORT_COLLISION_MARKERS: tuple[str, ...] = (
    "address already in use",
    "port already in use",
    "was already allocated",
    "eaddrinuse",
)


def _port_collision_evidence(logs: str, port: int) -> str | None:
    """Return the first log line evidencing a port collision, or None.

    A collision means the port picked on the host was taken before the
    sidecar could bind it (the `free_host_port` TOCTOU window): the JVM's
    bind failure (`address already in use`, Spring's `Port N was already
    in use`, docker's `port ... was already allocated`). Any other failure
    (a crash for another reason, a tool-set drift) is NOT a collision and
    must abort immediately instead of burning another attempt.

    Args:
        logs: The failed container's combined `docker logs` output.
        port: The port the attempt was given (matches `Port N ...` lines).
    """
    for line in (logs or "").splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in _PORT_COLLISION_MARKERS):
            result = line.strip()
            return result
        if f"port {port}" in lowered and ("in use" in lowered or "already" in lowered):
            result = line.strip()
            return result
    return None


def _mcp_round_trip(port: int) -> list[str]:
    """Run an MCP `initialize` + `tools/list` round trip against the sidecar.

    Returns:
        The tool names the sidecar registered.

    Raises:
        RuntimeError: On any HTTP/protocol failure (the sidecar is not
            healthy yet).
    """
    base = f"http://127.0.0.1:{port}/mcp"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

    def raw_post(payload: dict) -> str:
        request = urllib.request.Request(base, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")

    def post(payload: dict) -> dict:
        body = raw_post(payload)
        for line in body.splitlines():
            if line.startswith("data:"):
                body = line[5:].strip()
                break
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise RuntimeError(f"MCP response is not an object: {body[:120]!r}")
        if "error" in parsed:
            raise RuntimeError(f"MCP error: {parsed['error']}")
        return parsed

    post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "c4eval", "version": "0.1.0"},
            },
        }
    )
    try:
        # notifications get a 202/empty body per the MCP spec; never parse it
        raw_post({"jsonrpc": "2.0", "method": "notifications/initialized"})
    except urllib.error.HTTPError:
        pass  # the pinned server is stateless and ignores this notification
    listing = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = [str(t["name"]) for t in listing["result"]["tools"]]
    result = tools
    return result


def _sidecar_docker_run(name: str, port: int) -> subprocess.CompletedProcess[str]:
    """Start the pinned sidecar container detached (the docker run only)."""
    cmd = [
        "docker",
        "run",
        "-d",
        "--network",
        "host",
        "--name",
        name,
        "-e",
        f"PORT={port}",
        "-e",
        f"STRUCTURIZR_THEMES={SIDECAR_THEMES}",
        pins.STRUCTURIZR_MCP_IMAGE,
        *SIDECAR_ARGS,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)  # noqa: S603 -- fixed pinned image
    return proc


def _wait_healthy(name: str, container_id: str, port: int) -> SidecarHandle:
    """Poll the MCP round trip until healthy (or the startup budget ends).

    Args:
        name: The container name (the handle's).
        container_id: The container id (the handle's).
        port: The host port the sidecar was told to bind.

    Returns:
        The SidecarHandle once the MCP round trip succeeds.

    Raises:
        RuntimeError: If the sidecar is not healthy within the startup
            budget, or registers a tool set that differs from the pinned
            image's (a pin drift). The failed container is NOT removed
            here -- the caller reads its logs first (the port-collision
            evidence) and tears it down.
    """
    deadline = time.monotonic() + STARTUP_BUDGET_S
    last_error: str = "no probe run"
    while time.monotonic() < deadline:
        try:
            tools = _mcp_round_trip(port)
            if set(tools) != EXPECTED_TOOLS:
                raise RuntimeError(f"sidecar tool set {sorted(tools)} != pinned {sorted(EXPECTED_TOOLS)}")
            handle = SidecarHandle(port=port, container_id=container_id, container_name=name)
            return handle
        except (urllib.error.URLError, RuntimeError, OSError, KeyError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            time.sleep(HEALTH_POLL_S)
    raise RuntimeError(f"sidecar not healthy after {STARTUP_BUDGET_S:.0f}s: {last_error}")


def _container_logs(container_id: str) -> str:
    """Return the failed container's combined logs (empty when unreadable).

    Read BEFORE the `docker rm` of the teardown (the logs die with the
    container). Never raises: log evidence is a diagnostic, not a gate.
    """
    try:
        proc = subprocess.run(  # noqa: S603 -- fixed container target
            ["docker", "logs", container_id],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    result = (proc.stdout or "") + (proc.stderr or "")
    return result


def _log_tail(logs: str, max_chars: int = 200) -> str:
    """Return the last non-empty log line (truncated) for error context."""
    lines = [line.strip() for line in (logs or "").splitlines() if line.strip()]
    if not lines:
        return ""
    tail = lines[-1]
    result = tail if len(tail) <= max_chars else tail[-max_chars:]
    return result


def start_sidecar(run_id: str) -> SidecarHandle:
    """Start the pinned sidecar on a free ephemeral host port.

    Port-collision retry (the `free_host_port` TOCTOU window): when an
    attempt's health check fails, the container's logs are inspected and
    a bind/port-in-use failure (`_port_collision_evidence`) triggers a
    retry with a FRESH port -- up to `SIDECAR_START_ATTEMPTS` attempts in
    total. Any other failure (a crash for another reason, a tool-set
    drift) aborts immediately. The aborting error names the port, the
    attempt, and the log evidence (the collision line, or the container
    log tail for a non-collision); after the last attempt it also names
    every earlier colliding port. A residual window remains: a port can
    still be taken between the log check and the retry's bind -- the
    same retry logic then absorbs it on the next attempt.

    Args:
        run_id: The run identifier (the container is named
            `c4eval-mcp-<run_id>`).

    Returns:
        The SidecarHandle once the MCP round trip succeeds.

    Raises:
        RuntimeError: If the sidecar is not healthy within the startup
            budget of the final attempt, registers a tool set that
            differs from the pinned image's (a pin drift), or `docker
            run` itself fails.
    """
    assert isinstance(run_id, str) and run_id
    name = f"{CONTAINER_NAME_PREFIX}{run_id}"
    collisions: list[str] = []
    for attempt in range(1, SIDECAR_START_ATTEMPTS + 1):
        port = free_host_port()
        proc = _sidecar_docker_run(name, port)
        if proc.returncode != 0:
            raise RuntimeError(f"sidecar docker run failed rc={proc.returncode}: {proc.stderr.strip()}")
        container_id = proc.stdout.strip()
        try:
            return _wait_healthy(name, container_id, port)
        except RuntimeError as exc:
            logs = _container_logs(container_id)
            stop_sidecar(container_id=container_id, container_name=name)
            evidence = _port_collision_evidence(logs, port)
            if evidence is None or attempt == SIDECAR_START_ATTEMPTS:
                detail = f"sidecar failed on port {port} (attempt {attempt}/{SIDECAR_START_ATTEMPTS}): {exc}"
                if evidence is not None:
                    detail += f"; log evidence: {evidence}"
                else:
                    tail = _log_tail(logs)
                    if tail:
                        detail += f"; container log tail: {tail}"
                if collisions:
                    detail += "; earlier port collision(s): " + "; ".join(collisions)
                raise RuntimeError(detail) from exc
            collisions.append(f"port {port}: {evidence}")
    raise AssertionError("unreachable: the attempt loop returns or raises")


def stop_sidecar(*, container_id: str | None = None, container_name: str | None = None) -> None:
    """Tear down one sidecar container (id or name, whichever is known).

    Never raises: a teardown failure is logged by the caller's context, the
    container is removed best-effort.
    """
    if not container_id and not container_name:
        return
    target = container_id or container_name
    assert target
    subprocess.run(  # noqa: S603 -- fixed container target
        ["docker", "rm", "-f", target],
        capture_output=True,
        text=True,
        timeout=60,
    )


def sidecar_container_list() -> list[str]:
    """Return the container ids of every live `c4eval-mcp-*` container.

    Used by preflight to refuse a run when a stale sidecar from a previous
    run is still up (one sidecar per run is the invariant).
    """
    proc = subprocess.run(  # noqa: S603 -- fixed arguments
        ["docker", "ps", "-q", "--filter", f"name={CONTAINER_NAME_PREFIX}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    result = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
    return result
