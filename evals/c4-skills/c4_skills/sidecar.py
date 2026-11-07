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

"""The harness's own pinned `structurizr/mcp` sidecar (Task 100.110/120,
reworked for the Phase 110 egress-control change).

The development MCP (bound to `127.0.0.1:3000`) is never used. The sidecar
runs on the run's private `--internal` bridge network (`c4eval-<run_id>`,
the one the runner creates before starting it) on a FIXED container port,
is healthy-checked FROM THE HOST with a real MCP `initialize` +
`tools/list` round trip against the sidecar's container IP (the host can
reach container IPs on its own bridge networks), and is torn down after
the run. The trial containers reach it at
`http://<sidecar_ip>:<port>/mcp` (streamable HTTP; verified against the
pinned image).

No host port at all: the container's port lives in its own netns, and a
per-run network has no other container on it, so the Phase 100
port-collision retry (`free_host_port` TOCTOU, `SIDECAR_START_ATTEMPTS`,
the collision log analysis) is structurally obsolete and was removed.
A startup failure aborts the run after one attempt (the container's log
tail is included in the error).
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import pins

#: The sidecar container name prefix (one per run id).
CONTAINER_NAME_PREFIX = "c4eval-mcp-"

#: The sidecar's fixed container port. The "never 3000/9797" convention of
#: the Phase 100 sidecar (the dev services' ports) is kept -- this port is
#: a container-local value on a fresh per-run network, but it is never
#: published, and the convention documents the intent.
SIDECAR_PORT = 8181

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
    """A running sidecar (container IP + port + container id for teardown).

    Attributes:
        ip: The sidecar's IP on the run's private network (the host
            health-checks it; the trial containers reach it the same way).
        port: The fixed container port the sidecar answers on
            (:data:`SIDECAR_PORT`; a netns-local value, never published).
        container_id: The Docker container id.
        container_name: The Docker container name.
    """

    ip: str
    port: int
    container_id: str
    container_name: str


def _mcp_round_trip(host: str, port: int) -> list[str]:
    """Run an MCP `initialize` + `tools/list` round trip against the sidecar.

    The round trip runs FROM THE HOST against the sidecar's container IP
    on the run's private network (the host reaches container IPs on its
    own bridge networks; the `--internal` flag blocks only the containers'
    egress, not the host's ingress).

    Args:
        host: The sidecar's IP (or `127.0.0.1` for a local test double).
        port: The port the sidecar answers on.

    Returns:
        The tool names the sidecar registered.

    Raises:
        RuntimeError: On any HTTP/protocol failure (the sidecar is not
            healthy yet).
    """
    base = f"http://{host}:{port}/mcp"
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


def _sidecar_docker_run(name: str, network: str) -> subprocess.CompletedProcess[str]:
    """Start the pinned sidecar container detached (the docker run only).

    The container joins the run's private network and binds the fixed
    container port -- nothing is published to the host.
    """
    cmd = [
        "docker",
        "run",
        "-d",
        "--network",
        network,
        "--name",
        name,
        "-e",
        f"PORT={SIDECAR_PORT}",
        "-e",
        f"STRUCTURIZR_THEMES={SIDECAR_THEMES}",
        pins.STRUCTURIZR_MCP_IMAGE,
        *SIDECAR_ARGS,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)  # noqa: S603 -- fixed pinned image
    return proc


def _container_ip(name: str, network: str) -> str:
    """Return the container's IP on the run's network (empty while unset)."""
    proc = subprocess.run(  # noqa: S603 -- fixed container name + network
        [
            "docker",
            "inspect",
            "--format",
            f'{{{{(index .NetworkSettings.Networks "{network}").IPAddress}}}}',
            name,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"docker inspect {name} failed: {proc.stderr.strip()}")
    result = proc.stdout.strip()
    return result


def _resolve_container_ip(name: str, network: str) -> str:
    """Poll the container's IP on the network until it is set (or the budget ends).

    Docker assigns the IP when the container joins the network, i.e. right
    after `docker run -d` returns -- the poll covers the rare scheduler
    gap and a container that restarted before attaching. An EMPTY IP is
    the transient state that is polled; a failing `docker inspect`
    (container gone, docker broken) is NOT -- it aborts immediately via
    the :func:`_container_ip` RuntimeError.

    Args:
        name: The container name.
        network: The run's private network name.

    Returns:
        The container's IP on that network.

    Raises:
        RuntimeError: If the IP is still empty when the startup budget ends
            (the container never attached to the network), or `docker
            inspect` fails (propagated from :func:`_container_ip`).
    """
    deadline = time.monotonic() + STARTUP_BUDGET_S
    while time.monotonic() < deadline:
        ip = _container_ip(name, network)
        if ip:
            result = ip
            return result
        time.sleep(HEALTH_POLL_S)
    raise RuntimeError(f"sidecar IP not resolved on {network} after {STARTUP_BUDGET_S:.0f}s: empty IP address")


def _wait_healthy(name: str, container_id: str, ip: str) -> SidecarHandle:
    """Poll the MCP round trip until healthy (or the startup budget ends).

    Args:
        name: The container name (the handle's).
        container_id: The container id (the handle's).
        ip: The sidecar's IP on the run's network (the health-check host).

    Returns:
        The SidecarHandle once the MCP round trip succeeds.

    Raises:
        RuntimeError: If the sidecar is not healthy within the startup
            budget, or registers a tool set that differs from the pinned
            image's (a pin drift). The failed container is NOT removed
            here -- the caller reads its logs first and tears it down.
    """
    deadline = time.monotonic() + STARTUP_BUDGET_S
    last_error: str = "no probe run"
    while time.monotonic() < deadline:
        try:
            tools = _mcp_round_trip(ip, SIDECAR_PORT)
            if set(tools) != EXPECTED_TOOLS:
                raise RuntimeError(f"sidecar tool set {sorted(tools)} != pinned {sorted(EXPECTED_TOOLS)}")
            handle = SidecarHandle(ip=ip, port=SIDECAR_PORT, container_id=container_id, container_name=name)
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


def start_sidecar(run_id: str, network: str) -> SidecarHandle:
    """Start the pinned sidecar on the run's private network.

    One attempt, no port lottery: the sidecar joins `network` (the
    run's fresh `c4eval-<run_id>` `--internal` bridge, created by the
    runner beforehand) on the fixed container port
    (:data:`SIDECAR_PORT`) and is healthy-checked from the host against
    its resolved container IP. A failure (not healthy within the startup
    budget, a tool-set pin drift, or `docker run` itself failing) aborts
    the run immediately -- the failed container's log tail is read
    BEFORE the teardown and included in the error.

    Args:
        run_id: The run identifier (the container is named
            `c4eval-mcp-<run_id>`).
        network: The run's private network name (the sidecar joins it).

    Returns:
        The SidecarHandle once the MCP round trip succeeds.

    Raises:
        RuntimeError: If `docker run` itself fails, the container's IP
            never resolves on the network, the sidecar is not healthy
            within the startup budget, it registers a tool set that
            differs from the pinned image's (a pin drift), or
            `docker inspect` fails.
    """
    assert isinstance(run_id, str) and run_id
    assert isinstance(network, str) and network
    name = f"{CONTAINER_NAME_PREFIX}{run_id}"
    proc = _sidecar_docker_run(name, network)
    if proc.returncode != 0:
        raise RuntimeError(f"sidecar docker run failed rc={proc.returncode}: {proc.stderr.strip()}")
    container_id = proc.stdout.strip()
    try:
        ip = _resolve_container_ip(name, network)
        return _wait_healthy(name, container_id, ip)
    except RuntimeError as exc:
        logs = _container_logs(container_id)
        stop_sidecar(container_id=container_id, container_name=name)
        detail = f"sidecar failed on network {network} (container {name}): {exc}"
        tail = _log_tail(logs)
        if tail:
            detail += f"; container log tail: {tail}"
        raise RuntimeError(detail) from exc


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
