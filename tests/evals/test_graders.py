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

"""Grader tests on pre-exported JSON fixtures (ACC-006, no model call).

The fixtures are the three committed workspaces under
`tests/evals/fixtures/workspaces/`:

- `good/` -- a full, valid workspace; its `export.json` is the real output
  of the pinned Structurizr CLI (`export -format json`), pre-exported at
  fixture creation;
- `weak/` -- a CLI-valid workspace that is thin: one container, a
  relationship without a technology, and no user-defined views (the JSON
  exporter auto-generates `generatedKey` views that must not count);
- `bad/` -- a syntactically broken workspace the CLI rejects (no export
  JSON exists; the collection recorded rc=1).

These tests prove the graders split a known-good from a known-bad
workspace purely on the CLI facts, with no Docker and no model call.
"""

import json
import unittest

from c4_skills.cases import Case
from c4_skills.graders import (
    GraderInputs,
    case_passed,
    grade_case,
    iter_containers,
    iter_people,
    iter_relationships,
    iter_systems,
    iter_views,
    relationship_technology_coverage,
)

from .conftest import FIXTURES_DIR

WORKSPACES = FIXTURES_DIR / "workspaces"


def _load_export(name: str) -> dict | None:
    path = WORKSPACES / name / "export.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs(name: str, validate_rc: int, export_rc: int) -> GraderInputs:
    dsl_path = WORKSPACES / name / "workspace.dsl"
    dsl_text = dsl_path.read_text(encoding="utf-8")
    export_json = _load_export(name)
    stderr = "" if validate_rc == 0 else "unexpected end of DSL content"
    return GraderInputs(
        dsl_path="workspace.dsl",
        dsl_text=dsl_text,
        validate_rc=validate_rc,
        validate_stderr=stderr,
        export_json=export_json,
        export_rc=export_rc,
        export_stderr="" if export_rc == 0 else "export failed",
        inspect_rc=None,
        inspect_findings=[],
    )


SMOKE_GATES = (
    "dsl_written",
    "cli_valid",
    "cli_export",
    "has_system",
    "has_person",
    "two_containers",
    "relationship_technology",
    "has_view",
)


class TestQueriesOverExportJson(unittest.TestCase):
    def test_good_export_element_counts(self) -> None:
        export = _load_export("good")
        assert export is not None

        sut_people = iter_people(export)
        sut_systems = iter_systems(export)
        sut_containers = iter_containers(export)
        sut_relationships = iter_relationships(export)
        sut_views = iter_views(export)

        self.assertEqual([p["name"] for p in sut_people], ["Customer"])
        self.assertEqual([s["name"] for s in sut_systems], ["Bookshop"])
        self.assertEqual(sorted(c["name"] for c in sut_containers), ["Order Processor", "Web Store"])
        # the systemContext `include *` duplicates the person->web
        # relationship as a linked copy; the dedup keeps the canonical one
        self.assertEqual(len(sut_relationships), 2)
        self.assertEqual(len(sut_views), 1)
        self.assertFalse(sut_views[0].get("generatedKey"))

    def test_weak_export_auto_generated_views_do_not_count(self) -> None:
        export = _load_export("weak")
        assert export is not None

        sut_views = iter_views(export)

        self.assertGreater(len(sut_views), 0)
        self.assertTrue(all(v.get("generatedKey") for v in sut_views))

    def test_weak_export_relationship_technology_coverage(self) -> None:
        export = _load_export("weak")
        assert export is not None

        sut = relationship_technology_coverage

        result = sut(export)

        # one of the two unique relationships carries no technology
        self.assertAlmostEqual(result if result is not None else -1.0, 0.5, places=6)

    def test_coverage_is_none_without_relationships(self) -> None:
        sut = relationship_technology_coverage

        result = sut({"model": {"people": [], "softwareSystems": []}})

        self.assertIsNone(result)


class TestGatesSplitGoodFromBad(unittest.TestCase):
    def test_good_workspace_passes_every_smoke_gate(self) -> None:
        case = Case(id="good", prompt="x", gates=SMOKE_GATES)
        inputs = _inputs("good", validate_rc=0, export_rc=0)

        sut = grade_case

        results = sut(case, inputs)

        self.assertTrue(case_passed(results))
        for gate in results:
            self.assertTrue(gate.passed, f"gate {gate.name} failed on good: {gate.detail}")

    def test_bad_workspace_fails_every_gate_after_dsl_written(self) -> None:
        # the broken file is still a .dsl file carrying the workspace
        # keyword, so `dsl_written` passes; every CLI-derived gate fails
        case = Case(id="bad", prompt="x", gates=SMOKE_GATES)
        inputs = _inputs("bad", validate_rc=1, export_rc=1)

        sut = grade_case

        results = sut(case, inputs)

        self.assertFalse(case_passed(results))
        by_name = {gate.name: gate for gate in results}
        self.assertTrue(by_name["dsl_written"].passed)
        for name in SMOKE_GATES[1:]:
            self.assertFalse(by_name[name].passed, f"gate {name} passed on bad")
        self.assertIn("rc=1", by_name["cli_valid"].detail)

    def test_weak_workspace_fails_only_the_semantic_gates(self) -> None:
        case = Case(id="weak", prompt="x", gates=SMOKE_GATES)
        inputs = _inputs("weak", validate_rc=0, export_rc=0)

        sut = grade_case

        results = sut(case, inputs)
        by_name = {gate.name: gate for gate in results}

        self.assertFalse(case_passed(results))
        self.assertTrue(by_name["dsl_written"].passed)
        self.assertTrue(by_name["cli_valid"].passed)
        self.assertTrue(by_name["cli_export"].passed)
        self.assertTrue(by_name["has_system"].passed)
        self.assertTrue(by_name["has_person"].passed)
        self.assertFalse(by_name["two_containers"].passed)
        self.assertFalse(by_name["relationship_technology"].passed)
        self.assertFalse(by_name["has_view"].passed)

    def test_missing_dsl_fails_with_explicit_detail(self) -> None:
        case = Case(id="missing", prompt="x", gates=SMOKE_GATES)
        inputs = GraderInputs(
            dsl_path=None,
            dsl_text=None,
            validate_rc=None,
            validate_stderr="no .dsl file in the work dir",
            export_json=None,
            export_rc=None,
            export_stderr="no .dsl file in the work dir",
            inspect_rc=None,
            inspect_findings=[],
        )

        sut = grade_case

        results = sut(case, inputs)

        self.assertFalse(case_passed(results))
        by_name = {gate.name: gate for gate in results}
        self.assertIn("no .dsl file", by_name["dsl_written"].detail)
        self.assertIn("no DSL file", by_name["cli_valid"].detail)
        self.assertIn("no DSL file", by_name["cli_export"].detail)

    def test_unknown_gate_name_raises(self) -> None:
        case = Case(id="unknown", prompt="x", gates=("no_such_gate",))
        inputs = _inputs("good", validate_rc=0, export_rc=0)

        sut = grade_case

        with self.assertRaises(KeyError):
            sut(case, inputs)


class TestFixtureFilesPresent(unittest.TestCase):
    def test_fixtures_are_committed_and_consistent(self) -> None:
        for name in ("good", "weak", "bad"):
            dsl = WORKSPACES / name / "workspace.dsl"
            self.assertTrue(dsl.is_file(), f"missing fixture {name}/workspace.dsl")
            self.assertGreater(dsl.stat().st_size, 0)
        for name in ("good", "weak"):
            export = WORKSPACES / name / "export.json"
            self.assertTrue(export.is_file(), f"missing fixture {name}/export.json")
            doc = json.loads(export.read_text(encoding="utf-8"))
            self.assertIn("model", doc)
        self.assertFalse((WORKSPACES / "bad" / "export.json").exists())


if __name__ == "__main__":
    unittest.main()
