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

"""Sidecar tests (no Docker: the container layer is mocked).

Phase 110 rework (the egress-control change): the sidecar runs on the
run's private `--internal` network on a FIXED container port and is
healthy-checked from the host against its resolved container IP. The
Phase 100 port-collision retry (`free_host_port` TOCTOU,
`SIDECAR_START_ATTEMPTS`, the collision log analysis) is structurally
obsolete (a fixed port on a fresh per-run network: ports are per-netns,
so nothing can collide) and was removed -- these tests cover its
replacements:

- the `_mcp_round_trip` host parameterization (a local HTTP test double
  standing in for the sidecar's container IP);
- the `_resolve_container_ip` poll (empty IP transient, failing inspect
  immediate abort, budget exhaustion);
- the single-attempt `start_sidecar` over the private network (no retry;
  the failure path reads the log tail and tears the container down);
- the docker run shape itself (`--network <net>`, the fixed port, no
  host port published).
"""

import http.server
import json
import subprocess
import threading
import unittest
import urllib.error
from unittest import mock

from c4_skills import sidecar


def _fake_completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["docker"], returncode=returncode, stdout=stdout, stderr=stderr)


class _McpTestHandler(http.server.BaseHTTPRequestHandler):
    """A canned MCP server: answers initialize/notifications/tools/list."""

    def do_POST(self) -> None:  # noqa: N802 -- http.server API
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        method = payload.get("method")
        if method == "initialize":
            body = {"result": {"protocolVersion": "2025-03-26", "serverInfo": {"name": "test", "version": "0"}}}
        elif method == "tools/list":
            body = {"result": {"tools": [{"name": "inspect"}, {"name": "parse"}, {"name": "validate"}]}}
        else:
            body = {}  # notifications: empty result body
        data = (json.dumps(body) + "\n").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:  # silence the test server
        pass


class TestMcpRoundTripHostParameter(unittest.TestCase):
    """The host parameter: the round trip runs against whatever address it is given."""

    def setUp(self) -> None:
        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _McpTestHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self.addCleanup(self._server.shutdown)

    def test_round_trip_against_the_local_test_double(self) -> None:
        host, port = self._server.server_address[:2]

        sut = sidecar._mcp_round_trip

        result = sut(host, port)

        self.assertEqual(result, ["inspect", "parse", "validate"])

    def test_round_trip_against_a_dead_host_raises(self) -> None:
        # nothing listens on 127.0.0.1:1 (port 1, refused immediately);
        # the connection-level failure surfaces as URLError (an OSError),
        # which _wait_healthy is the layer that absorbs while polling
        sut = sidecar._mcp_round_trip

        with self.assertRaises(urllib.error.URLError):
            sut("127.0.0.1", 1)


class TestResolveContainerIp(unittest.TestCase):
    """The IP poll: empty is transient, a failing inspect aborts, the budget ends it."""

    def _fake_ip_run(self, values: list[str | Exception]):
        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            next_value = values.pop(0) if len(values) > 1 else values[0]
            if isinstance(next_value, Exception):
                raise next_value
            return _fake_completed(0, stdout=f"{next_value}\n")

        return fake_run

    def test_polls_until_the_ip_is_set(self) -> None:
        with (
            mock.patch.object(sidecar.subprocess, "run", side_effect=self._fake_ip_run(["", "", "172.21.0.3"])),
            mock.patch.object(sidecar, "HEALTH_POLL_S", 0.001),
        ):
            result = sidecar._resolve_container_ip("c4eval-mcp-run-x", "c4eval-run-x")

        self.assertEqual(result, "172.21.0.3")

    def test_a_failing_inspect_aborts_immediately(self) -> None:
        # inspect fails (container gone): no polling to the budget, the
        # RuntimeError propagates on the first call
        error = RuntimeError("docker inspect c4eval-mcp-run-x failed: No such object")
        with (
            mock.patch.object(sidecar.subprocess, "run", side_effect=error),
            mock.patch.object(sidecar, "HEALTH_POLL_S", 0.001),
            mock.patch.object(sidecar, "STARTUP_BUDGET_S", 90.0),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                sidecar._resolve_container_ip("c4eval-mcp-run-x", "c4eval-run-x")

        self.assertIn("No such object", str(ctx.exception))

    def test_an_persistent_empty_ip_hits_the_budget(self) -> None:
        with (
            mock.patch.object(sidecar.subprocess, "run", side_effect=self._fake_ip_run([""])),
            mock.patch.object(sidecar, "HEALTH_POLL_S", 0.001),
            mock.patch.object(sidecar, "STARTUP_BUDGET_S", 0.01),
        ):
            with self.assertRaises(RuntimeError) as ctx:
                sidecar._resolve_container_ip("c4eval-mcp-run-x", "c4eval-run-x")

        self.assertIn("not resolved", str(ctx.exception))


class TestSidecarDockerRunShape(unittest.TestCase):
    """The docker run command: the private network, the fixed port, nothing published."""

    def test_the_run_joins_the_network_on_the_fixed_port(self) -> None:
        captured: dict = {}

        def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            captured["cmd"] = cmd
            return _fake_completed(0, stdout="cid-1\n")

        with mock.patch.object(sidecar.subprocess, "run", side_effect=fake_run):
            sidecar._sidecar_docker_run("c4eval-mcp-run-x", "c4eval-run-x")

        cmd = captured["cmd"]
        self.assertEqual(cmd[:2], ["docker", "run"])
        self.assertIn("-d", cmd)
        self.assertEqual(cmd[cmd.index("--network") + 1], "c4eval-run-x")
        self.assertNotIn("host", cmd)
        self.assertEqual(cmd[cmd.index("-e") + 1], f"PORT={sidecar.SIDECAR_PORT}")
        # no host port at all: no -p / --publish
        self.assertNotIn("-p", cmd)
        self.assertNotIn("--publish", cmd)
        self.assertEqual(sidecar.SIDECAR_PORT, 8181)
        # the dev services' ports stay forbidden by convention
        self.assertNotIn(sidecar.SIDECAR_PORT, (3000, 9797))

    def test_the_old_host_network_machinery_is_gone(self) -> None:
        # Phase 100's racy port selection is structurally obsolete (a fixed
        # port on a fresh per-run network cannot collide): the symbols are
        # removed, not dead
        for name in ("free_host_port", "SIDECAR_START_ATTEMPTS", "_port_collision_evidence"):
            self.assertFalse(hasattr(sidecar, name), name)


class TestStartSidecar(unittest.TestCase):
    """The single-attempt start over mocked docker/health layers."""

    def _patches(self, ip: str | None, healthy: bool, logs: str = ""):
        runs: list[tuple[str, str]] = []

        def fake_resolve_ip(name: str, network: str) -> str:
            if ip is None:
                raise RuntimeError(f"sidecar IP not resolved on {network} after 90s: empty IP address")
            return ip

        def fake_wait_healthy(name: str, container_id: str, host_ip: str) -> sidecar.SidecarHandle:
            if not healthy:
                raise RuntimeError("sidecar not healthy after 90s: connection refused")
            return sidecar.SidecarHandle(
                ip=host_ip,
                port=sidecar.SIDECAR_PORT,
                container_id=container_id,
                container_name=name,
            )

        def fake_docker_run(name: str, network: str) -> subprocess.CompletedProcess:
            runs.append((name, network))
            return _fake_completed(0, stdout="cid-1\n")

        return (
            mock.patch.object(sidecar, "_resolve_container_ip", side_effect=fake_resolve_ip),
            mock.patch.object(sidecar, "_wait_healthy", side_effect=fake_wait_healthy),
            mock.patch.object(sidecar, "_sidecar_docker_run", side_effect=fake_docker_run),
            mock.patch.object(sidecar, "_container_logs", return_value=logs),
            mock.patch.object(sidecar, "stop_sidecar"),
            runs,
        )

    def test_start_returns_the_handle_with_ip_and_fixed_port(self) -> None:
        (ip_patch, wait_patch, run_patch, logs_patch, stop_patch, runs) = self._patches(ip="172.21.0.3", healthy=True)

        with ip_patch, wait_patch, run_patch, logs_patch, stop_patch as stop_mock:
            handle = sidecar.start_sidecar("run-x", "c4eval-run-x")

        self.assertEqual(handle.ip, "172.21.0.3")
        self.assertEqual(handle.port, sidecar.SIDECAR_PORT)
        self.assertEqual(runs, [("c4eval-mcp-run-x", "c4eval-run-x")])
        self.assertFalse(stop_mock.called)

    def test_an_unhealthy_sidecar_aborts_after_one_attempt_with_the_log_tail(self) -> None:
        (ip_patch, wait_patch, run_patch, logs_patch, stop_patch, runs) = self._patches(
            ip="172.21.0.3",
            healthy=False,
            logs="INFO started\nERROR boom: the JVM crashed\n",
        )

        with ip_patch, wait_patch, run_patch, logs_patch, stop_patch as stop_mock:
            with self.assertRaises(RuntimeError) as ctx:
                sidecar.start_sidecar("run-x", "c4eval-run-x")

        self.assertEqual(runs, [("c4eval-mcp-run-x", "c4eval-run-x")])  # no retry
        self.assertEqual(stop_mock.call_count, 1)
        self.assertEqual(stop_mock.call_args.kwargs["container_id"], "cid-1")
        message = str(ctx.exception)
        self.assertIn("c4eval-run-x", message)  # the network is named
        self.assertIn("the JVM crashed", message)  # the log tail is named
        self.assertNotIn("attempt", message)  # the retry vocabulary is gone

    def test_an_unresolved_ip_aborts_with_the_teardown(self) -> None:
        (ip_patch, wait_patch, run_patch, logs_patch, stop_patch, runs) = self._patches(ip=None, healthy=True)

        with ip_patch, wait_patch, run_patch, logs_patch, stop_patch as stop_mock:
            with self.assertRaises(RuntimeError) as ctx:
                sidecar.start_sidecar("run-x", "c4eval-run-x")

        self.assertEqual(stop_mock.call_count, 1)
        self.assertIn("not resolved", str(ctx.exception))
        self.assertEqual(runs, [("c4eval-mcp-run-x", "c4eval-run-x")])

    def test_docker_run_failure_is_immediate(self) -> None:
        with (
            mock.patch.object(sidecar, "_sidecar_docker_run", return_value=_fake_completed(125, stderr="no image")),
            mock.patch.object(sidecar, "_resolve_container_ip") as ip_patch,
        ):
            with self.assertRaises(RuntimeError) as ctx:
                sidecar.start_sidecar("run-x", "c4eval-run-x")

        self.assertIn("docker run failed", str(ctx.exception))
        self.assertFalse(ip_patch.called)


if __name__ == "__main__":
    unittest.main()
