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

"""Tests for `plantuml.backends` (the jar/bin local backends, rulebook §4).

Offline: the argv shapes (list form, never a shell; charset validation), the
byte-safe error-block scan (both byte shapes — the frozen `ERROR / {line} /
{message}` one-liner and the three-line block 1.2026.8 actually emits,
recorded in `tests/fixtures/plantuml/aass_check_stderr.txt`), the probe
memoisation, and the configuration-defect verdicts (no subprocess on a bad
path). Env-gated (real parser): the canary validates, the canonical `aass`
fixture is invalid with the parsed error line/message, and the render proof
is an SVG temp file.
"""

import os
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.plantuml import backends
from tests.conftest import require_plantuml_source

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "plantuml"


class TestArgvShapes(unittest.TestCase):
    """The unified invocation shape (rulebook §4)."""

    def test_jar_prefix_is_java_dash_jar(self):
        result = backends._argv_prefix("jar", "/opt/plantuml/plantuml.jar")

        self.assertEqual(result, ["java", "-jar", "/opt/plantuml/plantuml.jar"])

    def test_bin_prefix_is_the_executable_alone(self):
        result = backends._argv_prefix("bin", "/usr/local/bin/plantuml-adapter")

        self.assertEqual(result, ["/usr/local/bin/plantuml-adapter"])

    def test_rejects_unknown_kind(self):
        with self.assertRaises(AssertionError):
            backends._argv_prefix("url", "http://x")  # type: ignore[arg-type]

    def test_check_argv_carries_flag_no_error_image_and_pipe(self):
        argv_prefix = backends._argv_prefix("jar", "/opt/plantuml/plantuml.jar")

        exit_code, out, err, transport_error = backends._run(
            [*argv_prefix, backends.FLAG_CHECK_SYNTAX, backends._FLAG_NO_ERROR_IMAGE, backends._FLAG_PIPE],
            b"",
        )

        self.assertIsNone(transport_error)
        self.assertIsNotNone(exit_code)  # an empty diagram is a verdict, not a transport failure


class TestSourceValueValidation(unittest.TestCase):
    """Configuration defects are decided without any subprocess."""

    def _assert_no_subprocess(self, reason_substring: str):
        with mock.patch.object(backends.subprocess, "run") as run:
            result = backends.probe_local("jar", self._value)
        run.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "misconfigured")
        self.assertIn(reason_substring, result.reason or "")

    def test_jar_set_but_empty_is_misconfigured(self):
        self._value = "   "
        self._assert_no_subprocess("set but empty")

    def test_jar_missing_path_is_misconfigured_naming_the_path(self):
        self._value = "/nonexistent/plantuml-1.2.0.jar"
        self._assert_no_subprocess("/nonexistent/plantuml-1.2.0.jar")

    def test_jar_without_java_is_misconfigured(self):
        self._value = str(_FIXTURES / "canary.puml")  # exists, so the java check is the blocker
        with mock.patch.object(backends.shutil, "which", return_value=None):
            with mock.patch.object(backends.subprocess, "run") as run:
                result = backends.probe_local("jar", self._value)
        run.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "misconfigured")
        self.assertIn("java is not on PATH", result.reason or "")

    def test_bin_missing_path_is_misconfigured(self):
        with mock.patch.object(backends.subprocess, "run") as run:
            result = backends.probe_local("bin", "/nonexistent/adapter")
        run.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "misconfigured")
        self.assertIn("/nonexistent/adapter", result.reason or "")

    def test_bin_not_executable_is_misconfigured(self):
        value = str(_FIXTURES / "canary.puml")  # exists but is not executable
        with mock.patch.object(backends.subprocess, "run") as run:
            result = backends.probe_local("bin", value)
        run.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "misconfigured")
        self.assertIn("not executable", result.reason or "")

    def test_path_with_nul_is_misconfigured(self):
        self._value = "/bad\0path"
        self._assert_no_subprocess("NUL")

    def test_probe_is_memoised_per_kind_and_value(self):
        value = str(_FIXTURES / "canary.puml")
        backends.clear_probe_cache()

        with mock.patch.object(backends.shutil, "which", return_value=None):
            with mock.patch.object(backends.subprocess, "run") as run:
                first = backends.probe_local("jar", value)
                second = backends.probe_local("jar", value)

        run.assert_not_called()
        self.assertEqual(first, second)
        self.assertIs(first, second)


class TestScanErrorBlocks(unittest.TestCase):
    """The byte-safe error-text scan (rulebook §4: raw output bytes, never a text channel)."""

    def test_scans_the_three_line_block_1_2026_8_emits(self):
        recorded = (_FIXTURES / "aass_check_stderr.txt").read_bytes()

        result = backends.scan_error_blocks(recorded)

        self.assertEqual(result, [(1, "Syntax Error? (Assumed diagram type: sequence)")])

    def test_scans_the_frozen_slash_shape(self):
        data = b"\x89PNG\r\n\x1a\nERROR / 1 / Syntax Error? (Assumed diagram type: sequence)\n\x00tail"

        result = backends.scan_error_blocks(data)

        self.assertEqual(result, [(1, "Syntax Error? (Assumed diagram type: sequence)")])

    def test_scans_multiple_blocks_and_dedupes(self):
        data = (
            b"ERROR\n2\nSyntax Error? (Assumed diagram type: sequence)\n"
            b"ERROR\n3\nSyntax error: end (Assumed diagram type: component)\n"
            b"ERROR\n2\nSyntax Error? (Assumed diagram type: sequence)\n"
        )

        result = backends.scan_error_blocks(data)

        self.assertEqual(
            result,
            [
                (2, "Syntax Error? (Assumed diagram type: sequence)"),
                (3, "Syntax error: end (Assumed diagram type: component)"),
            ],
        )

    def test_binary_contaminated_stream_still_yields_the_block(self):
        data = (
            b"\x89PNG\r\n\x1a\n" + b"\x00\xff\xfe" * 16 + b"ERROR\n7\nSyntax Error? (Assumed diagram type: sequence)\n"
        )

        result = backends.scan_error_blocks(data)

        self.assertEqual(result, [(7, "Syntax Error? (Assumed diagram type: sequence)")])

    def test_clean_bytes_yield_nothing(self):
        self.assertEqual(backends.scan_error_blocks(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64), [])
        self.assertEqual(backends.scan_error_blocks(b""), [])


class TestRealParser(unittest.TestCase):
    """Env-gated: run only when a jar/bin source answers its canary."""

    def test_canary_is_valid(self):
        info = require_plantuml_source(self)
        if info.kind not in ("jar", "bin"):
            self.skipTest("the real-parser tests apply only to a selected jar/bin source")
        assert info.value is not None

        verdict = backends.validate_local(info.kind, info.value, backends.CANARY_DIAGRAM, backends.FLAG_CHECK_SYNTAX)

        self.assertTrue(verdict.valid)
        self.assertEqual(verdict.errors, [])

    def test_canary_render_proof_is_an_svg_temp_file(self):
        info = require_plantuml_source(self)
        if info.kind not in ("jar", "bin"):
            self.skipTest("the real-parser tests apply only to a selected jar/bin source")
        assert info.value is not None

        verdict = backends.validate_local(info.kind, info.value, backends.CANARY_DIAGRAM, backends.FLAG_CHECK_SYNTAX)

        self.assertIs(verdict.rendered, True)
        self.assertIsNotNone(verdict.proof_path)
        assert verdict.proof_path is not None
        self.assertTrue(os.path.exists(verdict.proof_path))
        with open(verdict.proof_path, "rb") as handle:
            self.assertTrue(handle.read(4).startswith(b"<"))  # the SVG temp file (never inlined)

    def test_aass_fixture_is_invalid_with_the_parsed_error(self):
        info = require_plantuml_source(self)
        if info.kind not in ("jar", "bin"):
            self.skipTest("the real-parser tests apply only to a selected jar/bin source")
        assert info.value is not None

        diagram = (_FIXTURES / "aass_error.puml").read_text(encoding="utf-8")
        verdict = backends.validate_local(info.kind, info.value, diagram, backends.FLAG_CHECK_SYNTAX)

        self.assertFalse(verdict.valid)
        self.assertIs(verdict.rendered, None)
        self.assertEqual(len(verdict.errors), 1)
        self.assertEqual(verdict.errors[0].line, 1)
        self.assertIn("Syntax Error? (Assumed diagram type: sequence)", verdict.errors[0].message)

    def test_wrapped_aass_fixture_is_invalid_with_the_parsed_error(self):
        """The same fixture inside a structure-clean @startuml/@enduml block (the chain path)."""
        info = require_plantuml_source(self)
        if info.kind not in ("jar", "bin"):
            self.skipTest("the real-parser tests apply only to a selected jar/bin source")
        assert info.value is not None

        diagram = f"@startuml\n{(_FIXTURES / 'aass_error.puml').read_text(encoding='utf-8').rstrip()}\n@enduml\n"
        verdict = backends.validate_local(info.kind, info.value, diagram, backends.FLAG_CHECK_SYNTAX)

        self.assertFalse(verdict.valid)
        self.assertEqual(len(verdict.errors), 1)
        self.assertIn("Syntax Error? (Assumed diagram type: sequence)", verdict.errors[0].message)


if __name__ == "__main__":
    unittest.main()
