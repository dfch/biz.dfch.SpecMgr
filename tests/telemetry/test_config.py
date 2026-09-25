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

"""Tests for ``telemetry/config.py`` (feat-139-logging-telemetry, Phase 1, Task 1.2).

Covers the all-disabled defaults, every valid value and its normalization,
and each invalid/incomplete combination raising :class:`TelemetryConfigError`
-- including the two pairing rules and the unconditional-validation rule
(ACC-011: validation fires even when the parent enable switch is
``false``).
"""

import os
import unittest
from unittest import mock

from biz.dfch.specmgr.telemetry.config import (
    DEFAULT_LOG_ENABLED,
    DEFAULT_LOG_FILE_ENABLED,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_OTEL_ENABLED,
    DEFAULT_OTEL_EXPORTER,
    ENV_LOG_ENABLED,
    ENV_LOG_FILE_ENABLED,
    ENV_LOG_FILE_PATH,
    ENV_LOG_FORMAT,
    ENV_LOG_LEVEL,
    ENV_OTEL_ENABLED,
    ENV_OTEL_ENDPOINT,
    ENV_OTEL_EXPORTER,
    LOG_FORMATS,
    OTEL_EXPORTERS,
    TelemetryConfig,
    TelemetryConfigError,
    load_telemetry_config,
)


class TestConfigDefaults(unittest.TestCase):
    """The all-disabled/safe defaults (every variable defaulting to disabled)."""

    def test_defaults_from_an_empty_mapping(self):
        sut = load_telemetry_config({})
        expected = TelemetryConfig(
            log_enabled=DEFAULT_LOG_ENABLED,
            log_level=DEFAULT_LOG_LEVEL,
            log_format=DEFAULT_LOG_FORMAT,
            log_file_enabled=DEFAULT_LOG_FILE_ENABLED,
            log_file_path=None,
            otel_enabled=DEFAULT_OTEL_ENABLED,
            otel_exporter=DEFAULT_OTEL_EXPORTER,
            otel_endpoint=None,
        )
        self.assertEqual(sut, expected)

    def test_defaults_from_a_clean_os_environ(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            sut = load_telemetry_config()
        self.assertFalse(sut.log_enabled)
        self.assertEqual(sut.log_level, DEFAULT_LOG_LEVEL)
        self.assertEqual(sut.log_format, DEFAULT_LOG_FORMAT)
        self.assertFalse(sut.log_file_enabled)
        self.assertIsNone(sut.log_file_path)
        self.assertFalse(sut.otel_enabled)
        self.assertEqual(sut.otel_exporter, DEFAULT_OTEL_EXPORTER)
        self.assertIsNone(sut.otel_endpoint)


class TestConfigValidValues(unittest.TestCase):
    """Every valid value is accepted and normalized to its canonical form."""

    def test_every_var_at_a_valid_value(self):
        sut = load_telemetry_config(
            {
                ENV_LOG_ENABLED: "true",
                ENV_LOG_LEVEL: "DEBUG",
                ENV_LOG_FORMAT: "json",
                ENV_LOG_FILE_ENABLED: "true",
                ENV_LOG_FILE_PATH: "/tmp/specmgr.log.jsonl",
                ENV_OTEL_ENABLED: "true",
                ENV_OTEL_EXPORTER: "otlp",
                ENV_OTEL_ENDPOINT: "http://localhost:4318",
            }
        )
        self.assertTrue(sut.log_enabled)
        self.assertEqual(sut.log_level, "DEBUG")
        self.assertEqual(sut.log_format, "json")
        self.assertTrue(sut.log_file_enabled)
        self.assertEqual(sut.log_file_path, "/tmp/specmgr.log.jsonl")
        self.assertTrue(sut.otel_enabled)
        self.assertEqual(sut.otel_exporter, "otlp")
        self.assertEqual(sut.otel_endpoint, "http://localhost:4318")

    def test_level_is_case_insensitive_and_normalized_to_uppercase(self):
        for raw, canonical in (
            ("debug", "DEBUG"),
            ("Info", "INFO"),
            ("wArNiNg", "WARNING"),
            ("error", "ERROR"),
            ("Critical", "CRITICAL"),
        ):
            with self.subTest(raw=raw):
                sut = load_telemetry_config({ENV_LOG_LEVEL: raw})
                self.assertEqual(sut.log_level, canonical)

    def test_boolean_flags_are_case_insensitive(self):
        for raw, expected in (
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("false", False),
            ("FALSE", False),
            ("fAlSe", False),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(load_telemetry_config({ENV_LOG_ENABLED: raw}).log_enabled, expected)
                # the file-sink flag needs its companion path when true (pairing rule)
                self.assertEqual(
                    load_telemetry_config(
                        {ENV_LOG_FILE_ENABLED: raw, ENV_LOG_FILE_PATH: "/tmp/x.jsonl"}
                    ).log_file_enabled,
                    expected,
                )
                self.assertEqual(load_telemetry_config({ENV_OTEL_ENABLED: raw}).otel_enabled, expected)

    def test_format_and_exporter_accept_every_closed_set_value(self):
        for value in LOG_FORMATS:
            with self.subTest(value=value):
                sut = load_telemetry_config({ENV_LOG_FORMAT: value})
                self.assertEqual(sut.log_format, value)
        for value in OTEL_EXPORTERS:
            env = {ENV_OTEL_EXPORTER: value}
            # the otlp exporter needs its companion endpoint (pairing rule)
            if value == "otlp":
                env[ENV_OTEL_ENDPOINT] = "http://localhost:4318"
            with self.subTest(value=value):
                sut = load_telemetry_config(env)
                self.assertEqual(sut.otel_exporter, value)

    def test_blank_file_path_and_endpoint_count_as_unset(self):
        sut = load_telemetry_config({ENV_LOG_FILE_PATH: "   ", ENV_OTEL_ENDPOINT: ""})
        self.assertIsNone(sut.log_file_path)
        self.assertIsNone(sut.otel_endpoint)

    def test_file_path_and_endpoint_are_stored_as_given(self):
        sut = load_telemetry_config({ENV_LOG_FILE_PATH: "/tmp/a b.jsonl", ENV_OTEL_ENDPOINT: "http://host:4318"})
        self.assertEqual(sut.log_file_path, "/tmp/a b.jsonl")
        self.assertEqual(sut.otel_endpoint, "http://host:4318")


class TestConfigInvalidCombinations(unittest.TestCase):
    """Each invalid/incomplete combination raises TelemetryConfigError (ACC-011)."""

    def test_file_sink_enabled_without_a_path_raises(self):
        sut_env = {ENV_LOG_FILE_ENABLED: "true"}
        with self.assertRaises(TelemetryConfigError) as ctx:
            load_telemetry_config(sut_env)
        message = str(ctx.exception)
        self.assertIn(ENV_LOG_FILE_PATH, message)
        self.assertIn(ENV_LOG_FILE_ENABLED, message)

    def test_file_sink_enabled_with_a_blank_path_raises(self):
        sut_env = {ENV_LOG_FILE_ENABLED: "true", ENV_LOG_FILE_PATH: "   "}
        with self.assertRaises(TelemetryConfigError) as ctx:
            load_telemetry_config(sut_env)
        self.assertIn(ENV_LOG_FILE_PATH, str(ctx.exception))

    def test_otlp_exporter_without_an_endpoint_raises(self):
        sut_env = {ENV_OTEL_EXPORTER: "otlp"}
        with self.assertRaises(TelemetryConfigError) as ctx:
            load_telemetry_config(sut_env)
        message = str(ctx.exception)
        self.assertIn(ENV_OTEL_ENDPOINT, message)
        self.assertIn(ENV_OTEL_EXPORTER, message)

    def test_otlp_exporter_with_a_blank_endpoint_raises(self):
        sut_env = {ENV_OTEL_EXPORTER: "otlp", ENV_OTEL_ENDPOINT: "  "}
        with self.assertRaises(TelemetryConfigError) as ctx:
            load_telemetry_config(sut_env)
        self.assertIn(ENV_OTEL_ENDPOINT, str(ctx.exception))

    def test_file_sink_disabled_never_requires_a_path(self):
        sut = load_telemetry_config({ENV_LOG_FILE_ENABLED: "false"})
        self.assertFalse(sut.log_file_enabled)
        self.assertIsNone(sut.log_file_path)

    def test_console_exporter_never_requires_an_endpoint(self):
        sut = load_telemetry_config({ENV_OTEL_EXPORTER: "console"})
        self.assertEqual(sut.otel_exporter, "console")
        self.assertIsNone(sut.otel_endpoint)

    def test_log_format_outside_the_closed_set_raises(self):
        for bad in ("xml", "RICH", "Rich", "jsonl", "rich json", ""):
            with self.subTest(bad=bad):
                sut_env = {ENV_LOG_FORMAT: bad}
                with self.assertRaises(TelemetryConfigError) as ctx:
                    load_telemetry_config(sut_env)
                self.assertIn(ENV_LOG_FORMAT, str(ctx.exception))

    def test_otel_exporter_outside_the_closed_set_raises(self):
        for bad in ("grpc", "CONSOLE", "Console", "file", ""):
            with self.subTest(bad=bad):
                sut_env = {ENV_OTEL_EXPORTER: bad}
                with self.assertRaises(TelemetryConfigError) as ctx:
                    load_telemetry_config(sut_env)
                self.assertIn(ENV_OTEL_EXPORTER, str(ctx.exception))

    def test_log_level_outside_the_named_levels_raises(self):
        for bad in ("TRACE", "warn", "Info2", "1", "", "INFO "):
            with self.subTest(bad=bad):
                sut_env = {ENV_LOG_LEVEL: bad}
                with self.assertRaises(TelemetryConfigError) as ctx:
                    load_telemetry_config(sut_env)
                self.assertIn(ENV_LOG_LEVEL, str(ctx.exception))

    def test_boolean_flag_outside_true_false_raises(self):
        for bad in ("yes", "no", "1", "0", "on", "off", "True ", ""):
            for name in (ENV_LOG_ENABLED, ENV_LOG_FILE_ENABLED, ENV_OTEL_ENABLED):
                with self.subTest(name=name, bad=bad):
                    sut_env = {name: bad}
                    with self.assertRaises(TelemetryConfigError) as ctx:
                        load_telemetry_config(sut_env)
                    self.assertIn(name, str(ctx.exception))


class TestConfigUnconditionalValidation(unittest.TestCase):
    """Validation fires even when the parent enable switch is ``false`` (ACC-011)."""

    def test_file_sink_pairing_validates_while_logging_is_disabled(self):
        sut_env = {ENV_LOG_ENABLED: "false", ENV_LOG_FILE_ENABLED: "true"}
        with self.assertRaises(TelemetryConfigError) as ctx:
            load_telemetry_config(sut_env)
        self.assertIn(ENV_LOG_FILE_PATH, str(ctx.exception))

    def test_otlp_pairing_validates_while_telemetry_is_disabled(self):
        sut_env = {ENV_OTEL_ENABLED: "false", ENV_OTEL_EXPORTER: "otlp"}
        with self.assertRaises(TelemetryConfigError) as ctx:
            load_telemetry_config(sut_env)
        self.assertIn(ENV_OTEL_ENDPOINT, str(ctx.exception))

    def test_invalid_format_validates_while_logging_is_disabled(self):
        sut_env = {ENV_LOG_ENABLED: "false", ENV_LOG_FORMAT: "xml"}
        with self.assertRaises(TelemetryConfigError):
            load_telemetry_config(sut_env)

    def test_invalid_level_validates_while_logging_is_disabled(self):
        sut_env = {ENV_LOG_ENABLED: "false", ENV_LOG_LEVEL: "TRACE"}
        with self.assertRaises(TelemetryConfigError):
            load_telemetry_config(sut_env)


class TestConfigErrorShape(unittest.TestCase):
    """TelemetryConfigError is a ValueError subclass with a single-line message."""

    def test_config_error_is_a_value_error_subclass(self):
        self.assertTrue(issubclass(TelemetryConfigError, ValueError))

    def test_error_messages_are_single_lines(self):
        invalid_envs = [
            {ENV_LOG_FILE_ENABLED: "true"},
            {ENV_OTEL_EXPORTER: "otlp"},
            {ENV_LOG_FORMAT: "xml"},
            {ENV_OTEL_EXPORTER: "grpc"},
            {ENV_LOG_LEVEL: "TRACE"},
            {ENV_LOG_ENABLED: "yes"},
            {ENV_LOG_FILE_ENABLED: "1"},
            {ENV_OTEL_ENABLED: "on"},
        ]
        for sut_env in invalid_envs:
            with self.subTest(env=sut_env):
                with self.assertRaises(TelemetryConfigError) as ctx:
                    load_telemetry_config(sut_env)
                self.assertEqual(len(str(ctx.exception).splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
