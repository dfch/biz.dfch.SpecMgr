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

"""Sidecar port-collision retry tests (no Docker: the container layer is mocked).

Covers the Phase 100 review cycle 1 fix I1: the `free_host_port` bind/close
-> container-bind TOCTOU race is absorbed by a bounded retry loop that, on
a failed attempt, inspects the container's `docker logs` for a
bind/port-in-use failure, picks a fresh port, and retries; any other
failure aborts immediately, and the final error names every colliding port
and the log evidence.
"""

import subprocess
import unittest
from unittest import mock

from c4_skills import sidecar


def _fake_completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["docker"], returncode=returncode, stdout=stdout, stderr=stderr)


class TestPortCollisionEvidence(unittest.TestCase):
    """The pure decision: which log lines evidence a port collision."""

    def test_spring_port_in_use_line_is_evidence(self) -> None:
        logs = (
            "2026-11-02 07:00:00.001 ERROR --- o.s.b.web.embedded.netty.NettyWebServer\n"
            + "Port 45123 was already in use."
        )
        sut = sidecar._port_collision_evidence

        result = sut(logs, 45123)

        self.assertEqual(result, "Port 45123 was already in use.")

    def test_jvm_bind_exception_is_evidence(self) -> None:
        logs = "Caused by: java.net.BindException: Address already in use"
        sut = sidecar._port_collision_evidence

        result = sut(logs, 1)

        self.assertEqual(result, "Caused by: java.net.BindException: Address already in use")

    def test_docker_port_allocation_error_is_evidence(self) -> None:
        logs = "Error: driver failed programming external connectivity: port 51000 was already allocated"
        sut = sidecar._port_collision_evidence

        result = sut(logs, 51000)

        self.assertIsNotNone(result)
        self.assertIn("already allocated", result or "")

    def test_a_successful_bind_is_not_evidence(self) -> None:
        logs = "2026-11-02 07:00:00.500 INFO  --- Netty started on port 45123"
        sut = sidecar._port_collision_evidence

        result = sut(logs, 45123)

        self.assertIsNone(result)

    def test_an_unrelated_crash_is_not_evidence(self) -> None:
        logs = 'Exception in thread "main" java.lang.OutOfMemoryError: Java heap space'
        sut = sidecar._port_collision_evidence

        result = sut(logs, 45123)

        self.assertIsNone(result)

    def test_empty_logs_are_not_evidence(self) -> None:
        sut = sidecar._port_collision_evidence

        self.assertIsNone(sut("", 45123))


class TestStartSidecarRetry(unittest.TestCase):
    """The retry loop over mocked docker/log/health layers."""

    def _patches(self, ports: list[int], healthy_from_attempt: int | None, logs: dict[str, str]):
        """Wire the mocks.

        Args:
            ports: The port candidates, one per attempt.
            healthy_from_attempt: The 1-based attempt that becomes healthy
                (None = no attempt is healthy).
            logs: container_id -> the failed container's log text.
        """
        runs: list[tuple[str, int]] = []

        def fake_docker_run(name: str, port: int) -> subprocess.CompletedProcess:
            runs.append((name, port))
            return _fake_completed(0, stdout=f"cid-{len(runs)}\n")

        def fake_wait_healthy(name: str, container_id: str, port: int) -> sidecar.SidecarHandle:
            attempt = len(runs)
            if healthy_from_attempt is not None and attempt >= healthy_from_attempt:
                return sidecar.SidecarHandle(port=port, container_id=container_id, container_name=name)
            raise RuntimeError(f"sidecar not healthy after {sidecar.STARTUP_BUDGET_S:.0f}s: connection refused")

        def fake_container_logs(container_id: str) -> str:
            return logs.get(container_id, "")

        return (
            mock.patch.object(sidecar, "free_host_port", side_effect=ports),
            mock.patch.object(sidecar, "_sidecar_docker_run", side_effect=fake_docker_run),
            mock.patch.object(sidecar, "_wait_healthy", side_effect=fake_wait_healthy),
            mock.patch.object(sidecar, "_container_logs", side_effect=fake_container_logs),
            mock.patch.object(sidecar, "stop_sidecar"),
            runs,
        )

    def test_port_collision_retries_with_a_fresh_port(self) -> None:
        (
            port_patch,
            run_patch,
            wait_patch,
            logs_patch,
            stop_patch,
            runs,
        ) = self._patches(
            ports=[1000, 2000],
            healthy_from_attempt=2,
            logs={"cid-1": "Port 1000 was already in use."},
        )

        with port_patch, run_patch, wait_patch, logs_patch, stop_patch as stop_mock:
            handle = sidecar.start_sidecar("run-x")

        self.assertEqual(handle.port, 2000)
        self.assertEqual(runs, [("c4eval-mcp-run-x", 1000), ("c4eval-mcp-run-x", 2000)])
        # only the failed container was torn down, before the logs were read
        self.assertEqual(stop_mock.call_count, 1)
        self.assertEqual(stop_mock.call_args.kwargs["container_id"], "cid-1")

    def test_non_collision_failure_aborts_immediately(self) -> None:
        (
            port_patch,
            run_patch,
            wait_patch,
            logs_patch,
            stop_patch,
            runs,
        ) = self._patches(
            ports=[1000, 2000],
            healthy_from_attempt=None,
            logs={"cid-1": "java.lang.OutOfMemoryError: Java heap space"},
        )

        with port_patch, run_patch, wait_patch, logs_patch, stop_patch:
            with self.assertRaises(RuntimeError) as ctx:
                sidecar.start_sidecar("run-x")

        self.assertEqual(runs, [("c4eval-mcp-run-x", 1000)])  # no retry
        self.assertNotIn("collision", str(ctx.exception))
        self.assertIn("OutOfMemoryError", str(ctx.exception))
        self.assertIn("attempt 1/3", str(ctx.exception))

    def test_all_attempts_collide_names_every_port_and_the_evidence(self) -> None:
        (
            port_patch,
            run_patch,
            wait_patch,
            logs_patch,
            stop_patch,
            runs,
        ) = self._patches(
            ports=[1000, 2000, 3000],
            healthy_from_attempt=None,
            logs={
                "cid-1": "Port 1000 was already in use.",
                "cid-2": "Port 2000 was already in use.",
                "cid-3": "Port 3000 was already in use.",
            },
        )

        with port_patch, run_patch, wait_patch, logs_patch, stop_patch as stop_mock:
            with self.assertRaises(RuntimeError) as ctx:
                sidecar.start_sidecar("run-x")

        message = str(ctx.exception)
        self.assertEqual(len(runs), 3)
        self.assertEqual(stop_mock.call_count, 3)
        self.assertIn("port 1000", message)
        self.assertIn("port 2000", message)
        self.assertIn("port 3000", message)
        self.assertIn("log evidence", message)

    def test_docker_run_failure_is_not_retried(self) -> None:
        with (
            mock.patch.object(sidecar, "free_host_port", return_value=1000),
            mock.patch.object(sidecar, "_sidecar_docker_run", return_value=_fake_completed(125, stderr="no image")),
            mock.patch.object(sidecar, "_wait_healthy") as wait_patch,
        ):
            with self.assertRaises(RuntimeError) as ctx:
                sidecar.start_sidecar("run-x")

        self.assertIn("docker run failed", str(ctx.exception))
        self.assertFalse(wait_patch.called)


if __name__ == "__main__":
    unittest.main()
