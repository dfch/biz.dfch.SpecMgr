# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""Tests for the ``validate_plantuml`` ``@mcp.tool()`` wrapper (feat-185-uc-diagrams, Phase 120).

The tool is a direct, thin wrapper over ``plantuml.chain.validate_plantuml``
(non-raising by construction): these tests pin the wrapper's own contract --
the offline chain outcomes (structure-red short-circuit with no source ever
called, the all-unset structure-only floor), the MCP-level serialization of
the §3.6 dataclass result (what the SDK ships to the client), and the
env-gated live tests against the configured source: the green/red pair
(ACC-004's MCP surface) plus the packaged-example green (the ACC-002
enabler, Phase 125); all skipped with a reason on unconfigured checkouts
(ACC-007).
"""

from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest import mock

from pydantic import TypeAdapter

from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.plantuml import chain
from biz.dfch.specmgr.plantuml.chain import PlantumlValidationResult
from biz.dfch.specmgr.uc.tools.validate_plantuml import validate_plantuml

from tests.conftest import require_plantuml_source

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "plantuml"
_EXAMPLE = read_packaged_text("uc", "plantuml_example")
_AASS = (_FIXTURES / "aass_error.puml").read_text(encoding="utf-8")
_AASS_DIAGRAM = f"@startuml\n{_AASS.rstrip()}\n@enduml\n"
#: The env-gated live test's minimal green subject: a small, fully attributed sequence diagram
#: that is valid by construction on the real parser (note left/right, no bare `note` block). The
#: packaged example is a live subject too (its own test below): the Phase 125 amendment
#: (2026-10-05, user-approved ruling) re-recorded its three unanchored notes as `note left`
#: after the real 1.2026.8 parser rejected the rulebook's former bare-`note` form (see the
#: rulebook §2.9 amendment note and the feat-185 Progress entry of 2026-10-05).
_LIVE_DIAGRAM = (
    "@startuml Buy Goods\n"
    "\n"
    "actor Buyer\n"
    "participant Company\n"
    "\n"
    "note left\n"
    "  We know Buyer\n"
    "end note\n"
    "\n"
    "Buyer -> Company: Buyer calls in with a purchase request.\n"
    "Company -> Buyer: Company confirms the order.\n"
    "\n"
    "note right\n"
    "  Order confirmed\n"
    "end note\n"
    "@enduml\n"
)
#: The §3.6 result model's frozen field set (the JSON the SDK ships must carry exactly these).
_RESULT_FIELDS = {
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
}


_SOURCE_VARS = (chain.ENV_VAR_JAR, chain.ENV_VAR_BIN, chain.ENV_VAR_URL)


class TestValidatePlantumlOffline(unittest.TestCase):
    """The wrapper's offline chain outcomes (no source configured).

    ``setUp`` deletes all three source env vars for the duration of the test
    (restoring whatever was there before, absence included, in ``addCleanup``):
    they must be *absent*, not empty -- a present-but-empty var is still
    **set** (it selects, then probes as misconfigured: the chain's own
    strictness-over-convenience rule), which is not the all-unset floor. The
    probe caches are cleared on the way in and out so a memoised canary from
    another test (or the conftest session gate) can never leak into these
    assertions.
    """

    def setUp(self) -> None:
        self._saved = {var: os.environ.get(var) for var in _SOURCE_VARS}
        for var in _SOURCE_VARS:
            os.environ.pop(var, None)
        chain.clear_probe_caches()
        self.addCleanup(self._restore_env)
        self.addCleanup(chain.clear_probe_caches)

    def _restore_env(self) -> None:
        for var, value in self._saved.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    def test_structure_red_short_circuits_with_no_source_configured(self):
        """Missing @startuml: structure red, the parser never called, checked_by = structure,
        valid/rendered = None (not run), source_state = none (all unset)."""
        result = validate_plantuml("participant Bob\nBob -> Alice: hello\n")

        self.assertIsInstance(result, PlantumlValidationResult)
        self.assertFalse(result.structure_ok)
        self.assertIsNone(result.valid)
        self.assertIsNone(result.rendered)
        self.assertEqual(result.checked_by, "structure")
        self.assertTrue(result.errors)
        for error in result.errors:
            self.assertGreaterEqual(error.line, 1)
            self.assertTrue(error.message)
            self.assertTrue(error.fix_hint)
        self.assertEqual(result.source_state, "none")
        self.assertFalse(result.available)
        self.assertIsNotNone(result.reason)

    def test_structure_red_with_a_source_configured_still_never_calls_the_parser(self):
        """The frozen §3.7 short-circuit: a set source changes nothing on structure red -- no
        subprocess, no network, source_state = none, and the reason disambiguates the floor
        from a probe outcome."""
        with mock.patch.dict(os.environ, {chain.ENV_VAR_URL: "http://localhost:1"}, clear=False):
            with mock.patch(
                "biz.dfch.specmgr.plantuml.url.probe_url",
                side_effect=AssertionError("the canary probe must not run on a structure red"),
            ) as probe:
                result = validate_plantuml("no startuml here\n")

        probe.assert_not_called()
        self.assertFalse(result.structure_ok)
        self.assertIsNone(result.valid)
        self.assertEqual(result.checked_by, "structure")
        self.assertEqual(result.source_state, "none")
        self.assertFalse(result.available)
        self.assertIn("no validation source was called", result.reason or "")

    def test_all_unset_floor_on_structure_green(self):
        """Structure green + all sources unset: the structure-only floor (checked_by = structure,
        valid/rendered = None, source_state = none, the all-unset reason)."""
        result = validate_plantuml(_EXAMPLE)

        self.assertTrue(result.structure_ok)
        self.assertIsNone(result.valid)
        self.assertIsNone(result.rendered)
        self.assertEqual(result.checked_by, "structure")
        self.assertEqual(result.source_state, "none")
        self.assertFalse(result.available)
        self.assertIn("all unset", result.reason or "")

    def test_result_serializes_to_the_frozen_field_set(self):
        """The §3.6 dataclass must MCP-serialize (the SDK's pydantic TypeAdapter path) with exactly
        the frozen field set -- the Phase 120 serialization-level use of the result model."""
        adapter = TypeAdapter(PlantumlValidationResult)
        payload = json.loads(adapter.dump_json(validate_plantuml(_EXAMPLE)))

        self.assertEqual(set(payload), _RESULT_FIELDS)
        self.assertTrue(payload["structure_ok"])
        self.assertIsNone(payload["valid"])
        self.assertEqual(payload["checked_by"], "structure")


class TestValidatePlantumlLive(unittest.TestCase):
    """The env-gated live tests (ACC-004's MCP surface + the Phase 125 packaged-example ACC-002
    enabler; clean skip on unconfigured checkouts, ACC-007)."""

    def test_valid_diagram_is_green_at_the_selected_source(self):
        """A parser-valid diagram must validate valid=true/rendered=true, checked_by = the selected
        source (see the _LIVE_DIAGRAM note for why the packaged example is not the live subject)."""
        info = require_plantuml_source(self)

        result = validate_plantuml(_LIVE_DIAGRAM)

        self.assertTrue(result.structure_ok)
        self.assertTrue(result.valid)
        self.assertTrue(result.rendered)
        self.assertEqual(result.checked_by, info.kind)
        self.assertEqual(result.source_state, "ok")
        self.assertTrue(result.available)

    def test_aass_error_diagram_is_invalid_at_the_selected_source(self):
        """The canonical aass error fixture must return valid=false (the structure checker passes it
        -- the error is the parser's, not the structure's)."""
        info = require_plantuml_source(self)

        result = validate_plantuml(_AASS_DIAGRAM)

        self.assertTrue(result.structure_ok)
        self.assertFalse(result.valid)
        self.assertEqual(result.checked_by, info.kind)
        self.assertTrue(result.errors)

    def test_packaged_example_is_green_at_the_selected_source(self):
        """The ACC-002 enabler (Phase 125): the packaged, fully attributed example file must
        validate green at the selected source -- its three unanchored notes were re-recorded
        as `note left` per the user-approved 2026-10-05 ruling (the former bare-`note` form
        was rejected by the real 1.2026.8 parser)."""
        info = require_plantuml_source(self)

        result = validate_plantuml(_EXAMPLE)

        self.assertTrue(result.structure_ok)
        self.assertTrue(result.valid)
        self.assertTrue(result.rendered)
        self.assertEqual(result.checked_by, info.kind)
        self.assertEqual(result.source_state, "ok")
        self.assertTrue(result.available)


if __name__ == "__main__":
    unittest.main()
