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

"""Tests for `plantuml.chain` (the strict first-set-wins chain, rulebook §3).

The two pinned tests of the phase (both offline — mocked transport, no real
source needed):

- **ACC-003 no-fall-through privacy:** with ``SPECMGR_PLANTUML_JAR`` set to a
  NON-EXISTENT path AND ``SPECMGR_PLANTUML_URL`` set to the public
  plantuml.com base, ``validate_plantuml`` fails with a diagnostic naming the
  JAR, and the mocked ``urllib`` + ``subprocess`` prove **zero** HTTP
  requests and **zero** subprocesses — the set-but-unavailable local source
  must never contact the public server.
- **Structure-red short-circuit (§3.7):** structure-red content (missing
  ``@startuml``) yields ``checked_by="structure"``, ``valid=None``,
  ``rendered=None`` — and the mocked jar subprocess + url transport assert
  never called (no subprocess, no network).
"""

import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.plantuml import backends, chain, url

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "plantuml"

_CLEAN_DIAGRAM = "@startuml\nparticipant Bob\nparticipant Alice\nBob -> Alice: hello\n@enduml\n"
_RED_DIAGRAM = "Bob -> Alice: hello\n@enduml\n"  # no @startuml — structure red in both modes


class TestSelectSource(unittest.TestCase):
    """Strict selection: first SET of JAR → BIN → URL; no fall-through."""

    def test_all_unset_selects_none(self):
        self.assertIsNone(chain.select_source({}))

    def test_jar_wins_over_bin_and_url(self):
        env = {
            chain.ENV_VAR_JAR: "/opt/plantuml.jar",
            chain.ENV_VAR_BIN: "/usr/local/bin/adapter",
            chain.ENV_VAR_URL: "https://www.plantuml.com/plantuml",
        }

        self.assertEqual(chain.select_source(env), ("jar", "/opt/plantuml.jar"))

    def test_bin_wins_over_url(self):
        env = {
            chain.ENV_VAR_BIN: "/usr/local/bin/adapter",
            chain.ENV_VAR_URL: "https://www.plantuml.com/plantuml",
        }

        self.assertEqual(chain.select_source(env), ("bin", "/usr/local/bin/adapter"))

    def test_url_alone_selects_url(self):
        env = {chain.ENV_VAR_URL: "http://localhost:8080"}

        self.assertEqual(chain.select_source(env), ("url", "http://localhost:8080"))

    def test_set_but_empty_still_selects(self):
        env = {chain.ENV_VAR_JAR: ""}

        self.assertEqual(chain.select_source(env), ("jar", ""))


class TestNoFallThrough(unittest.TestCase):
    """ACC-003: a set-but-unavailable JAR with a set public URL never contacts the URL."""

    def setUp(self):
        backends.clear_probe_cache()
        url.clear_probe_cache()

    def test_jar_misconfigured_with_url_set_fails_naming_the_jar_and_makes_no_calls(self):
        jar_path = "/nonexistent/plantuml-1.2026.8.jar"
        env = {chain.ENV_VAR_JAR: jar_path, chain.ENV_VAR_URL: "https://www.plantuml.com/plantuml"}

        with (
            mock.patch.object(backends.subprocess, "run") as run_subprocess,
            mock.patch.object(url, "fetch_svg") as fetch,
        ):
            result = chain.validate_plantuml(_CLEAN_DIAGRAM, env=env)

        # zero HTTP requests, zero subprocesses — the privacy invariant
        run_subprocess.assert_not_called()
        fetch.assert_not_called()
        # the failure names the JAR (the exact problem, rulebook §3.3)
        self.assertFalse(result.available)
        self.assertEqual(result.source_state, chain.STATE_MISCONFIGURED)
        self.assertEqual(result.checked_by, "jar")
        self.assertIsNone(result.valid)
        self.assertIsNone(result.rendered)
        self.assertIn(jar_path, result.reason or "")
        self.assertIn("SPECMGR_PLANTUML_JAR", result.reason or "")
        self.assertIn("plantuml.jar", result.fix_hint or "")
        # the structure check still ran (always first) and is green
        self.assertTrue(result.structure_ok)

    def test_url_selected_never_touches_subprocess(self):
        env = {chain.ENV_VAR_URL: "http://localhost:1"}  # nothing listens on port 1

        with mock.patch.object(backends.subprocess, "run") as run_subprocess:
            result = chain.validate_plantuml(_CLEAN_DIAGRAM, env=env)

        run_subprocess.assert_not_called()
        self.assertEqual(result.checked_by, "url")
        self.assertFalse(result.available)
        self.assertIn(result.source_state, (chain.STATE_UNAVAILABLE, chain.STATE_INCONCLUSIVE))


class TestStructureRedShortCircuit(unittest.TestCase):
    """§3.7: structure red ⇒ the parser is never called (no subprocess, no network)."""

    def test_missing_startuml_short_circuits_with_a_jar_source_set(self):
        env = {chain.ENV_VAR_JAR: "/opt/plantuml.jar"}

        with (
            mock.patch.object(backends.subprocess, "run") as run_subprocess,
            mock.patch.object(url, "fetch_svg") as fetch,
        ):
            result = chain.validate_plantuml(_RED_DIAGRAM, env=env)

        run_subprocess.assert_not_called()
        fetch.assert_not_called()
        self.assertFalse(result.structure_ok)
        self.assertEqual(result.checked_by, chain.CHECKED_BY_STRUCTURE)
        self.assertIsNone(result.valid)  # None = "not run", never "run and failed"
        self.assertIsNone(result.rendered)
        self.assertFalse(result.available)
        self.assertTrue(any("no @startuml line found" in error.message for error in result.errors))

    def test_missing_startuml_short_circuits_on_the_all_unset_floor(self):
        with mock.patch.object(backends.subprocess, "run") as run_subprocess:
            result = chain.validate_plantuml(_RED_DIAGRAM, env={})

        run_subprocess.assert_not_called()
        self.assertFalse(result.structure_ok)
        self.assertEqual(result.checked_by, chain.CHECKED_BY_STRUCTURE)
        self.assertIsNone(result.valid)
        self.assertEqual(result.source_state, chain.STATE_NONE)


class TestAllUnsetFloor(unittest.TestCase):
    """§3.4: only the all-unset state degrades — to the structure checker alone."""

    def test_clean_diagram_is_structure_green(self):
        with (
            mock.patch.object(backends.subprocess, "run") as run_subprocess,
            mock.patch.object(url, "fetch_svg") as fetch,
        ):
            result = chain.validate_plantuml(_CLEAN_DIAGRAM, env={})

        run_subprocess.assert_not_called()
        fetch.assert_not_called()
        self.assertTrue(result.structure_ok)
        self.assertEqual(result.checked_by, chain.CHECKED_BY_STRUCTURE)
        self.assertIsNone(result.valid)
        self.assertIsNone(result.rendered)
        self.assertEqual(result.source_state, chain.STATE_NONE)
        self.assertFalse(result.available)
        self.assertIn("structure-only", result.reason or "")

    def test_lenient_set_is_promoted_to_errors_on_the_floor(self):
        text = "@startuml\nparticipant A\nparticipant B\nA -> B: x\n"  # missing @enduml (lenient #2)

        result = chain.validate_plantuml(text, env={})

        self.assertFalse(result.structure_ok)
        self.assertTrue(any("missing @enduml" in error.message for error in result.errors))


class TestResultShape(unittest.TestCase):
    """The §3.6 frozen shape (the non-raising structured result)."""

    def test_fields_match_the_frozen_shape(self):
        result = chain.validate_plantuml(_CLEAN_DIAGRAM, env={})

        for field in (
            "structure_ok",
            "valid",
            "rendered",
            "checked_by",
            "errors",
            "warnings",
            "source_state",
            "available",
            "reason",
            "fix_hint",
        ):
            with self.subTest(field=field):
                self.assertTrue(hasattr(result, field))

        self.assertIsInstance(result.structure_ok, bool)
        self.assertIsInstance(result.available, bool)
        self.assertIn(result.checked_by, ("jar", "bin", "url", "structure"))
        self.assertIn(
            result.source_state,
            ("ok", "misconfigured", "unavailable", "inconclusive", "none"),
        )

    def test_never_raises_on_content(self):
        for text in ("", "total garbage", "@startuml\n", "\n\n\n"):
            with self.subTest(text=text):
                result = chain.validate_plantuml(text, env={})
                self.assertIsInstance(result, chain.PlantumlValidationResult)


class TestAvailabilityMemoisation(unittest.TestCase):
    """One canary probe per process (rulebook §3.5) — the agent's loop must not re-probe."""

    def setUp(self):
        backends.clear_probe_cache()

    def test_probe_is_memoised_per_kind_and_value(self):
        jar = str(_FIXTURES / "canary.puml")  # exists, so the probe reaches the subprocess
        with mock.patch.object(
            backends.subprocess, "run", return_value=mock.Mock(returncode=0, stdout=b"", stderr=b"")
        ) as run:
            first = backends.probe_local("jar", jar)
            second = backends.probe_local("jar", jar)

        self.assertIs(first, second)
        self.assertEqual(run.call_count, 1)  # one canary round-trip, not one per probe call

    def test_validate_plantuml_does_not_reprobe_within_a_process(self):
        env = {chain.ENV_VAR_JAR: str(_FIXTURES / "canary.puml")}
        ok_run = mock.Mock(returncode=0, stdout=b"<svg></svg>", stderr=b"")
        with mock.patch.object(backends.subprocess, "run", return_value=ok_run) as run:
            chain.validate_plantuml(_CLEAN_DIAGRAM, env=env)
            chain.validate_plantuml(_CLEAN_DIAGRAM, env=env)

        # probe (1 canary check) + two validations (check + render each)
        self.assertEqual(run.call_count, 1 + 2 * 2)


if __name__ == "__main__":
    unittest.main()
