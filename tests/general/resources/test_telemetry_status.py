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

"""Tests for the ``specmgr://telemetry/status`` resource (feat-139-logging-telemetry, Phase 1, Task 1.3).

Covers the VCR ``f494d230-97f3-4db9-9ef9-ed9c903ee008`` acceptance
criteria: AC-001 (reading the resource returns a ``list[str]`` reporting
enablement plus mode) and AC-002 (the reported values match the actual
configuration, changing with the environment).
"""

import os
import unittest
from unittest import mock

from biz.dfch.specmgr.general.resources.telemetry_status import telemetry_status
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

#: All eight telemetry env vars, cleaned out of the process env below so
#: each test pins exactly the environment it asserts on.
_ALL_ENV_VARS = (
    ENV_LOG_ENABLED,
    ENV_LOG_LEVEL,
    ENV_LOG_FORMAT,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_OTEL_ENABLED,
    ENV_OTEL_EXPORTER,
    ENV_OTEL_ENDPOINT,
)


def _clean_environ() -> dict[str, str]:
    """The process env minus the eight telemetry env vars."""
    result = {name: value for name, value in os.environ.items() if name not in _ALL_ENV_VARS}
    return result


class TestTelemetryStatusResource(unittest.TestCase):
    """Tests for the ``telemetry_status`` resource function."""

    def test_returns_a_list_of_strings(self):
        """AC-001: reading the resource returns a ``list[str]`` of exactly two lines."""
        with mock.patch.dict(os.environ, _clean_environ(), clear=True):
            result = telemetry_status()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        for entry in result:
            self.assertIsInstance(entry, str)

    def test_default_config_reports_both_disabled(self):
        """AC-001/AC-002: with no telemetry env vars set, both features report disabled."""
        with mock.patch.dict(os.environ, _clean_environ(), clear=True):
            result = telemetry_status()
        self.assertEqual(result, ["logging: disabled", "telemetry: disabled"])

    def test_logging_enabled_telemetry_disabled_reports_mode(self):
        """AC-002: the VCR's own scenario (``SPECMGR_LOG_ENABLED=true``, ``SPECMGR_OTEL_ENABLED=false``)."""
        env = _clean_environ()
        env[ENV_LOG_ENABLED] = "true"
        env[ENV_OTEL_ENABLED] = "false"
        with mock.patch.dict(os.environ, env, clear=True):
            result = telemetry_status()
        self.assertEqual(result, ["logging: enabled (level=INFO, format=rich, file=off)", "telemetry: disabled"])

    def test_logging_enabled_with_all_modes_reports_them(self):
        """AC-002: level/format/file-sink mode all reach the status line (level normalized)."""
        env = _clean_environ()
        env[ENV_LOG_ENABLED] = "true"
        env[ENV_LOG_LEVEL] = "debug"
        env[ENV_LOG_FORMAT] = "json"
        env[ENV_LOG_FILE_ENABLED] = "true"
        env[ENV_LOG_FILE_PATH] = "/tmp/specmgr.jsonl"
        with mock.patch.dict(os.environ, env, clear=True):
            result = telemetry_status()
        self.assertEqual(result, ["logging: enabled (level=DEBUG, format=json, file=on)", "telemetry: disabled"])

    def test_telemetry_enabled_reports_the_exporter(self):
        """AC-002: the exporter mode reaches the telemetry status line."""
        env = _clean_environ()
        env[ENV_OTEL_ENABLED] = "true"
        env[ENV_OTEL_EXPORTER] = "otlp"
        env[ENV_OTEL_ENDPOINT] = "http://localhost:4318"
        with mock.patch.dict(os.environ, env, clear=True):
            result = telemetry_status()
        self.assertEqual(result, ["logging: disabled", "telemetry: enabled (exporter=otlp)"])

    def test_a_changed_environment_changes_the_reported_values(self):
        """AC-002: two reads under two different environments report accordingly (restart semantics)."""
        with mock.patch.dict(os.environ, _clean_environ(), clear=True):
            first = telemetry_status()
        env = _clean_environ()
        env[ENV_LOG_ENABLED] = "true"
        env[ENV_OTEL_ENABLED] = "true"
        with mock.patch.dict(os.environ, env, clear=True):
            second = telemetry_status()
        self.assertEqual(first, ["logging: disabled", "telemetry: disabled"])
        self.assertEqual(
            second,
            ["logging: enabled (level=INFO, format=rich, file=off)", "telemetry: enabled (exporter=console)"],
        )
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
