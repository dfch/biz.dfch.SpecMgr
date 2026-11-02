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

    Returns:
        A currently unbound port number.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    result = port
    return result


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


def start_sidecar(run_id: str) -> SidecarHandle:
    """Start the pinned sidecar on a free ephemeral host port.

    Args:
        run_id: The run identifier (the container is named
            `c4eval-mcp-<run_id>`).

    Returns:
        The SidecarHandle once the MCP round trip succeeds.

    Raises:
        RuntimeError: If the sidecar is not healthy within the startup
            budget, or registers a tool set that differs from the pinned
            image's (a pin drift).
    """
    assert isinstance(run_id, str) and run_id
    port = free_host_port()
    name = f"{CONTAINER_NAME_PREFIX}{run_id}"
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
    if proc.returncode != 0:
        raise RuntimeError(f"sidecar docker run failed rc={proc.returncode}: {proc.stderr.strip()}")
    container_id = proc.stdout.strip()
    try:
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
    except BaseException:
        stop_sidecar(container_id=container_id, container_name=name)
        raise


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
