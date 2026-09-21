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

"""Tests for the ``mcp`` command.

Requires the ``mcp`` extra (``pip install "biz-dfch-specmgr[mcp]"``).
"""

import io
import os
import subprocess
import sys
import unittest
from unittest import mock

import typer

from biz.dfch.specmgr.commands.mcp import _warn_on_public_binding, mcp
from biz.dfch.specmgr.telemetry.config import (
    ENV_LOG_ENABLED,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_LOG_FORMAT,
    ENV_LOG_LEVEL,
    ENV_OTEL_ENABLED,
    ENV_OTEL_ENDPOINT,
    ENV_OTEL_EXPORTER,
)

#: All eight telemetry env vars, removed from the subprocess env below so
#: each combination test pins exactly the environment it asserts on.
_ALL_TELEMETRY_ENV_VARS = (
    ENV_LOG_ENABLED,
    ENV_LOG_LEVEL,
    ENV_LOG_FORMAT,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_OTEL_ENABLED,
    ENV_OTEL_EXPORTER,
    ENV_OTEL_ENDPOINT,
)


class TestMcpCommand(unittest.TestCase):
    """Tests that each ``--transport`` branch calls ``mcp_server.run`` correctly."""

    def test_stdio_calls_run_with_stdio_transport(self):
        """``--transport stdio`` calls ``run(transport=\"stdio\")`` only."""
        with mock.patch("biz.dfch.specmgr.server.mcp") as mcp_server:
            mcp(transport="stdio", host="localhost", port=8000)
        mcp_server.run.assert_called_once_with(transport="stdio")

    def test_sse_calls_run_with_sse_transport(self):
        """``--transport sse`` calls ``run`` with ``transport=\"sse\"``, ``host``, and ``port``."""
        with mock.patch("biz.dfch.specmgr.server.mcp") as mcp_server:
            mcp(transport="sse", host="localhost", port=8000)
        mcp_server.run.assert_called_once_with(transport="sse", host="localhost", port=8000)

    def test_streamable_http_calls_run_with_streamable_http_transport(self):
        """``--transport streamable-http`` calls ``run`` with ``stateless_http=True``."""
        with mock.patch("biz.dfch.specmgr.server.mcp") as mcp_server:
            mcp(transport="streamable-http", host="localhost", port=8000)
        mcp_server.run.assert_called_once_with(
            transport="streamable-http", host="localhost", port=8000, stateless_http=True
        )


class TestWarnOnPublicBinding(unittest.TestCase):
    """Tests for the ``_warn_on_public_binding`` helper."""

    def test_silent_for_localhost(self):
        """No warning is written when the host is not a public bind address."""
        with mock.patch("sys.stderr") as stderr:
            _warn_on_public_binding("localhost")
        stderr.write.assert_not_called()

    def test_warns_for_all_interfaces_outside_a_container(self):
        """A warning is written for '0.0.0.0' when no container markers are set."""
        with (
            mock.patch("os.path.exists", return_value=False),
            mock.patch.dict("os.environ", {}, clear=True),
            mock.patch("sys.stderr") as stderr,
        ):
            _warn_on_public_binding("0.0.0.0")
        stderr.write.assert_called_once()

    def test_silent_for_all_interfaces_inside_a_container(self):
        """No warning is written for '0.0.0.0' when a container marker is set."""
        with (
            mock.patch("os.path.exists", return_value=True),
            mock.patch("sys.stderr") as stderr,
        ):
            _warn_on_public_binding("0.0.0.0")
        stderr.write.assert_not_called()


class TestMcpCommandConfigErrorHandling(unittest.TestCase):
    """ACC-011's CLI error surface (feat-139-logging-telemetry, Task 1.6): a
    static misconfiguration of the ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*`` env
    vars makes the ``mcp`` command refuse to start with a single clear
    stderr line naming the offending env var(s) and exit code 1 -- no raw
    traceback, nothing on stdout."""

    def test_invalid_combination_fails_before_stdio_with_one_clean_stderr_line(self):
        """Re-importing ``server.py`` under a broken env exits 1 with exactly one stderr line."""
        import biz.dfch.specmgr.server as server_module

        saved_server = server_module
        sys.modules.pop("biz.dfch.specmgr.server")
        stderr = io.StringIO()
        try:
            with (
                mock.patch.dict(
                    os.environ,
                    {
                        ENV_LOG_ENABLED: "false",
                        ENV_LOG_LEVEL: "INFO",
                        ENV_LOG_FORMAT: "rich",
                        ENV_LOG_FILE_ENABLED: "true",
                        ENV_LOG_FILE_PATH: "   ",
                        ENV_OTEL_ENABLED: "false",
                        ENV_OTEL_EXPORTER: "console",
                    },
                    clear=False,
                ),
                mock.patch("sys.stdin", new=io.StringIO("")),
                mock.patch("sys.stderr", new=stderr),
                self.assertRaises(typer.Exit) as raised,
            ):
                mcp(transport="stdio", host="localhost", port=8000)
        finally:
            sys.modules["biz.dfch.specmgr.server"] = saved_server

        self.assertEqual(raised.exception.exit_code, 1)
        lines = [line for line in stderr.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, f"expected exactly one stderr line, got: {stderr.getvalue()!r}")
        self.assertIn(ENV_LOG_FILE_PATH, lines[0])
        self.assertIn(ENV_LOG_FILE_ENABLED, lines[0])
        self.assertNotIn("Traceback", stderr.getvalue())


class TestMcpCommandStartupRefusal(unittest.TestCase):
    """End-to-end (subprocess): ``python -m biz.dfch.specmgr mcp`` with a
    broken telemetry env fails before touching stdio (empty stdout), with
    exactly one stderr line -- the ``TelemetryConfigError`` message itself,
    naming the offending env var(s) -- and exit code 1 (ACC-011, Task 1.6)."""

    def _run_cli(self, env_overrides: dict[str, str]) -> subprocess.CompletedProcess[str]:
        env = {name: value for name, value in os.environ.items() if name not in _ALL_TELEMETRY_ENV_VARS}
        env.update(env_overrides)
        result = subprocess.run(
            [sys.executable, "-m", "biz.dfch.specmgr", "mcp"],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )
        return result

    def _assert_refused_to_start(self, process: subprocess.CompletedProcess[str], *offending_vars: str) -> None:
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout, "")
        lines = [line for line in process.stderr.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, f"expected exactly one stderr line, got: {process.stderr!r}")
        for var in offending_vars:
            self.assertIn(var, lines[0])
        self.assertNotIn("Traceback", process.stderr)

    def test_file_sink_enabled_without_a_path_refuses_to_start(self):
        process = self._run_cli({ENV_LOG_FILE_ENABLED: "true"})
        self._assert_refused_to_start(process, ENV_LOG_FILE_PATH, ENV_LOG_FILE_ENABLED)
        self.assertEqual(
            process.stderr.splitlines()[0],
            "SPECMGR_LOG_FILE_PATH is required and must be non-blank when SPECMGR_LOG_FILE_ENABLED=true",
        )

    def test_otlp_exporter_without_an_endpoint_refuses_to_start(self):
        process = self._run_cli({ENV_OTEL_EXPORTER: "otlp"})
        self._assert_refused_to_start(process, ENV_OTEL_ENDPOINT, ENV_OTEL_EXPORTER)
        self.assertEqual(
            process.stderr.splitlines()[0],
            "SPECMGR_OTEL_ENDPOINT is required and must be non-blank when SPECMGR_OTEL_EXPORTER=otlp",
        )

    def test_invalid_log_format_refuses_to_start(self):
        process = self._run_cli({ENV_LOG_FORMAT: "xml"})
        self._assert_refused_to_start(process, ENV_LOG_FORMAT)
        self.assertEqual(process.stderr.splitlines()[0], "SPECMGR_LOG_FORMAT must be one of: rich/json; got 'xml'")


if __name__ == "__main__":
    unittest.main()
