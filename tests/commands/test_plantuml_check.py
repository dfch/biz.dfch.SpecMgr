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

"""Tests for the ``plantuml-check`` command (feat-185-uc-diagrams, Phase 130).

The command is a thin, non-raising CLI over ``plantuml.chain.validate_plantuml``
(the rulebook §3 chain: structure pre-flight always, then the single
first-set-wins source). These tests pin the CLI's own contract: the per-file
verdict output (``checked_by``/``valid``/``rendered``/``source_state`` + the
feat-27-style findings), the pinned exit codes (0 valid / 1 invalid-or-
structure-red / 2 source misconfigured-or-unavailable / 3 inconclusive), the
worst-code-wins precedence (``2 > 3 > 1 > 0`` — the untrustworthy-source
verdicts outrank plain content verdicts), the usage-error pins (non-``.puml``
/ unreadable / missing paths → 2, reported before any chain run), and the
ACC-003 CLI-level no-fall-through (a misconfigured JAR with a set public URL
never contacts the URL). The env-gated live test runs the packaged example
against the configured source (ACC-007: clean skip with a reason otherwise).

Offline determinism: the three ``SPECMGR_PLANTUML_*`` vars are deleted for the
whole offline test class (the gitignored root ``.env`` is loaded by
``cli.py`` at import time, so the deletion must be explicit per test), and the
memoised canary probe caches are cleared on the way in and out. The
inconclusive scenario is mocked at the ``plantuml.url`` boundary (``fetch_svg``
— the transport seam), so no network is ever contacted.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.plantuml import chain, url
from biz.dfch.specmgr.plantuml.backends import CANARY_DIAGRAM
from biz.dfch.specmgr.plantuml.encode import encode_puml

from tests.conftest import assert_rendered_svg, render_proof_body, require_plantuml_source

runner = CliRunner()

_SOURCE_VARS = (chain.ENV_VAR_JAR, chain.ENV_VAR_BIN, chain.ENV_VAR_URL)

#: A structure-clean, parser-valid mini diagram (green at every layer).
_GREEN = "@startuml\nactor A\nparticipant B\nA -> B: hello\n@enduml\n"

#: No ``@startuml`` — structure red in both modes (the §3.7 short-circuit subject).
_RED = "participant Bob\nBob -> Alice: hello\n"

#: Structure green with one UNATTRIBUTED marker (a warning in both modes — the
#: zero-marker rule is agent-path only, never a checker/CLI error).
_MARKER = "@startuml\nactor A\nparticipant B\n' UNATTRIBUTED step 1: A -> B: hello\n@enduml\n"


class _PlantumlCheckOfflineBase(unittest.TestCase):
    """Shared setUp: all three source vars deleted (absence, not emptiness) + probe caches cleared."""

    def setUp(self) -> None:
        self._saved = {var: os.environ.get(var) for var in _SOURCE_VARS}
        for var in _SOURCE_VARS:
            os.environ.pop(var, None)
        chain.clear_probe_caches()
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.addCleanup(self._restore_env)
        self.addCleanup(chain.clear_probe_caches)

    def _restore_env(self) -> None:
        for var, value in self._saved.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    def _write(self, name: str, text: str) -> Path:
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    @staticmethod
    def _inconclusive_url_fetch():
        """A ``fetch_svg`` fake at the transport seam: the canary round-trips (200 real SVG) but every
        diagram request answers an unrecognised 500 — persistent INCONCLUSIVE (the frozen matrix's
        last row) after the chain's one retry. Fully offline."""

        def fake_fetch_svg(fetch_url: str):
            if encode_puml(CANARY_DIAGRAM) in fetch_url:
                return url.UrlResponse(status=200, body=b"<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>")
            return url.UrlResponse(status=500, body=b"<html>500 Internal Server Error</html>")

        return fake_fetch_svg


class TestPlantumlCheckAllUnset(_PlantumlCheckOfflineBase):
    """The all-unset structure-only floor (no source configured)."""

    def test_structure_green_floor_exits_0(self):
        """Structure green + all sources unset → exit 0 (the floor: structure green ⇒ valid), with the
        structure verdict printed (valid/rendered not-run, source_state none)."""
        green = self._write("ok.puml", _GREEN)

        result = runner.invoke(app, ["plantuml-check", str(green)])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("checked_by=structure", result.stdout)
        self.assertIn("valid=not-run", result.stdout)
        self.assertIn("rendered=not-run", result.stdout)
        self.assertIn("source_state=none", result.stdout)

    def test_structure_red_exits_1_with_actionable_findings(self):
        """Structure red (missing @startuml) → exit 1, with the feat-27-style finding (1-based line +
        cause + fix hint) and the short-circuit reason (no source was called)."""
        red = self._write("red.puml", _RED)

        result = runner.invoke(app, ["plantuml-check", str(red)])

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("checked_by=structure", result.stdout)
        self.assertIn("red.puml:1:", result.stdout)
        self.assertIn("(fix: ", result.stdout)

    def test_unattributed_marker_is_a_warning_not_an_error(self):
        """A structure-green file with an UNATTRIBUTED marker → exit 0 (the marker is a deliberate
        placeholder — a warning in both checker modes), printed with the warning tag."""
        marked = self._write("marked.puml", _MARKER)

        result = runner.invoke(app, ["plantuml-check", str(marked)])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("warning: ", result.stdout)

    def test_no_paths_is_a_usage_error(self):
        """Zero paths (the variadic argument is required) → the Typer usage error, exit 2."""
        result = runner.invoke(app, ["plantuml-check"])

        self.assertEqual(result.exit_code, 2, result.output)


class TestPlantumlCheckUsageErrors(_PlantumlCheckOfflineBase):
    """The usage-error pins: non-.puml / unreadable / missing paths → exit 2, all reported before any
    chain run (documented choice — the paths are invalid input, so nothing is validated)."""

    def test_non_puml_path_exits_2(self):
        text = self._write("ok.txt", _GREEN)

        result = runner.invoke(app, ["plantuml-check", str(text)])

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("not a .puml", result.output)

    def test_missing_file_exits_2(self):
        result = runner.invoke(app, ["plantuml-check", str(self.tmp / "nope.puml")])

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("unreadable", result.output)

    def test_all_usage_errors_reported_before_any_chain_run(self):
        text = self._write("ok.txt", _GREEN)

        with mock.patch(
            "biz.dfch.specmgr.plantuml.chain.validate_plantuml",
            side_effect=AssertionError("usage errors must not run the chain"),
        ):
            result = runner.invoke(app, ["plantuml-check", str(text), str(self.tmp / "nope.puml")])

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("not a .puml", result.output)
        self.assertIn("unreadable", result.output)


class TestPlantumlCheckSourceFailure(_PlantumlCheckOfflineBase):
    """Exit 2: the selected source is set but misconfigured/unavailable (the chain's hard failure)."""

    def test_misconfigured_jar_exits_2_naming_the_jar_and_never_calling_the_url(self):
        """The ACC-003 scenario at the CLI level: JAR set to a non-existent path + URL set to the public
        one → exit 2 with the JAR named in the output, and zero HTTP calls (no fall-through — the
        privacy invariant). ``shutil.which`` is pinned so the jar-path branch (not the java-on-PATH
        branch) fires deterministically on every machine."""
        green = self._write("ok.puml", _GREEN)
        jar = "/nonexistent/plantuml.jar"

        with mock.patch.dict(
            os.environ, {chain.ENV_VAR_JAR: jar, chain.ENV_VAR_URL: "https://www.plantuml.com/plantuml"}
        ):
            with mock.patch("shutil.which", return_value="/usr/bin/java"):
                with mock.patch(
                    "biz.dfch.specmgr.plantuml.url.fetch_svg",
                    side_effect=AssertionError("a misconfigured local source must never fall through to the URL"),
                ) as fetch:
                    result = runner.invoke(app, ["plantuml-check", str(green)])

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(jar, result.stdout)  # the reason names the JAR
        self.assertIn("SPECMGR_PLANTUML_JAR", result.stdout)
        self.assertIn("fix:", result.stdout)
        fetch.assert_not_called()


class TestPlantumlCheckInconclusive(_PlantumlCheckOfflineBase):
    """Exit 3: the source's verdict is inconclusive (persistent after the chain's one retry)."""

    def test_persistent_inconclusive_exits_3(self):
        """The canary round-trips but every diagram request is an unrecognised 500 (mocked at the
        plantuml.url boundary) → exit 3 with the source state and the chain's fix hint printed."""
        green = self._write("ok.puml", _GREEN)

        with mock.patch.dict(os.environ, {chain.ENV_VAR_URL: "http://localhost:8080"}):
            with mock.patch("biz.dfch.specmgr.plantuml.url.fetch_svg", side_effect=self._inconclusive_url_fetch()):
                result = runner.invoke(app, ["plantuml-check", str(green)])

        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("source_state=inconclusive", result.stdout)
        self.assertIn("fix:", result.stdout)


class TestPlantumlCheckPrecedence(_PlantumlCheckOfflineBase):
    """The worst-code-wins precedence (2 > 3 > 1 > 0) across mixed-verdict invocations.

    One source per invocation, so a green file and the source share one code; the structure-red file
    short-circuits to code 1 regardless of the source. 2 and 3 therefore cannot co-occur in one
    invocation — the total order is still pinned by the ``_SEVERITY_BY_CODE`` table, and the
    observable mixed pairs (2 over 1, 3 over 1, 1 over 0) are tested here.
    """

    def test_mixed_1_over_0_all_unset(self):
        """1 > 0: all-unset; a structure-red file + a structure-green file → exit 1."""
        red = self._write("red.puml", _RED)
        green = self._write("ok.puml", _GREEN)

        result = runner.invoke(app, ["plantuml-check", str(green), str(red)])

        self.assertEqual(result.exit_code, 1, result.output)

    def test_mixed_3_over_1_inconclusive_source(self):
        """3 > 1: an inconclusive source; a structure-red file (code 1) + a green file (code 3) →
        exit 3 (the red file's short-circuit verdict does not outrank the untrustworthy source)."""
        red = self._write("red.puml", _RED)
        green = self._write("ok.puml", _GREEN)

        with mock.patch.dict(os.environ, {chain.ENV_VAR_URL: "http://localhost:8080"}):
            with mock.patch("biz.dfch.specmgr.plantuml.url.fetch_svg", side_effect=self._inconclusive_url_fetch()):
                result = runner.invoke(app, ["plantuml-check", str(red), str(green)])

        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("red.puml", result.stdout)
        self.assertIn("checked_by=structure", result.stdout)

    def test_mixed_2_over_1_misconfigured_source(self):
        """2 > 1: a misconfigured JAR source; a structure-red file (code 1) + a green file (code 2) →
        exit 2 (the broken source makes the content verdicts untrustworthy — it outranks them)."""
        red = self._write("red.puml", _RED)
        green = self._write("ok.puml", _GREEN)
        jar = "/nonexistent/plantuml.jar"

        with mock.patch.dict(os.environ, {chain.ENV_VAR_JAR: jar}):
            with mock.patch("shutil.which", return_value="/usr/bin/java"):
                result = runner.invoke(app, ["plantuml-check", str(red), str(green)])

        self.assertEqual(result.exit_code, 2, result.output)


class TestPlantumlCheckLive(unittest.TestCase):
    """The env-gated live test (ACC-007: clean skip with a reason on unconfigured checkouts)."""

    def test_packaged_example_is_valid_at_the_selected_source(self):
        """The packaged, fully attributed example file → exit 0 with checked_by = the selected source
        (valid/rendered true) — the chain's authoritative layer, not the structure floor."""
        info = require_plantuml_source(self)
        assert info.kind is not None
        assert info.value is not None
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        example = tmp / "example.puml"
        example_text = read_packaged_text("uc", "plantuml_example")
        example.write_text(example_text, encoding="utf-8")

        result = runner.invoke(app, ["plantuml-check", str(example)])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(f"checked_by={info.kind}", result.stdout)
        self.assertIn("valid=true", result.stdout)
        self.assertIn("rendered=true", result.stdout)
        # the Phase 145 render-proof contract: `rendered=true` must mean a TRUE
        # render — the selected source's own render-proof SVG body carries the
        # diagram text and no crash marker (the pre-amendment example shape
        # returned a crash page that read rendered=true)
        assert_rendered_svg(render_proof_body(info.kind, info.value, example_text), "Buyer has goods")


if __name__ == "__main__":
    unittest.main()
