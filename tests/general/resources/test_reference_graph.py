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

"""Tests for the `specmgr://reference-graph` resource (`general.resources.reference_graph.reference_graph`).

The resource serves the frozen reference-graph rulebook
(``general/data/general_reference_graph.md``) as raw markdown (no dedicated
parse model — like ``specmgr://uc/plantuml``). Because the rulebook is the
spec the renderers, builders, and checker implement against, these tests pin
the load-bearing frozen strings (the 14-entry palette in block order, the
red-arrow syntax + the 2026-10-15 real-parser gate verdict (replacing the
2026-10-10 skip verdict) incl. the "not frozen on a skipped gate"
convention, the curly `component "TYPE" { … }` domain-group form + the
label-free edge form, the worked example, the env var + truncation, the
FEAT-exclusion / bare-`feat-NNN` rejection, the UC rulebook pointer) so a
silent edit of the packaged data file is caught here rather than surfacing
as a renderer/checker drift.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mcp.server.mcpserver.resources.base import Resource

from biz.dfch.specmgr.general.resources.reference_graph import reference_graph
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.server import mcp
from tests.plantuml.test_reference_graph_subset import _EMITTED_SUBSET

#: The frozen 14-entry palette, exactly in the skinparam block's order
#: (ALL_DOMAINS order + UNRESOLVED last).
_PALETTE_LINES = [
    "backgroundColor<<ADR>> LightYellow",
    "backgroundColor<<REQ>> LightBlue",
    "backgroundColor<<UC>> Pink",
    "backgroundColor<<TSK>> Honeydew",
    "backgroundColor<<QA>> LemonChiffon",
    "backgroundColor<<PRB>> LightCoral",
    "backgroundColor<<GOL>> Lavender",
    "backgroundColor<<RSK>> Orange",
    "backgroundColor<<DEC>> LightGreen",
    "backgroundColor<<SOP>> PowderBlue",
    "backgroundColor<<FEAT>> PaleTurquoise",
    "backgroundColor<<VCR>> Khaki",
    "backgroundColor<<SYSRS>> Thistle",
    "backgroundColor<<UNRESOLVED>> DarkRed",
]

#: The 2026-10-15 Phase 100 parser-gate verdict, verbatim fragments
#: (rulebook §4.3 — the verdict heading wraps across two lines in the
#: markdown, and the convention line is the load-bearing new rule).
_GATE_VERDICT_FRAGMENTS = (
    "Verdict, 2026-10-15 (feat-214-rel-invalid-diag Phase 100",
    "2026-10-10 skip verdict)",
    "an emission layout is NOT frozen on a skipped gate",
)


def _registered_resource(uri: str) -> Resource:
    """Return the registered Resource model for `uri` from the server's resource manager."""
    result = [resource for resource in mcp._resource_manager.list_resources() if resource.uri == uri]
    assert len(result) == 1, f"expected exactly one registration for {uri}, got {len(result)}"
    return result[0]


class TestReferenceGraphResource(unittest.TestCase):
    """Tests for the `reference_graph` resource function."""

    def test_is_registered_with_markdown_mime_type(self):
        resource = _registered_resource("specmgr://reference-graph")

        self.assertEqual(resource.name, "reference_graph")
        self.assertEqual(resource.mime_type, "text/markdown")

    def test_returns_the_packaged_data_file_verbatim(self):
        sut = reference_graph

        result = sut()

        on_disk = _packaged_data.packaged_data_path("general", "reference_graph")
        self.assertIsInstance(result, str)
        self.assertEqual(result, on_disk.read_text(encoding="utf-8"))
        self.assertTrue(result.startswith("# Reference Graph Diagram Rulebook"))

    def test_pins_the_frozen_palette_in_block_order(self):
        result = reference_graph()

        position = -1
        for line in _PALETTE_LINES:
            with self.subTest(line=line):
                found_at = result.find(line, position + 1)
                self.assertNotEqual(found_at, -1, f"palette line missing or out of order: {line!r}")
                position = found_at

    def test_pins_the_gate_verdict_and_red_syntax(self):
        result = reference_graph()

        for fragment in _GATE_VERDICT_FRAGMENTS:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, result)
        self.assertIn("-[#red]->", result)
        self.assertIn("@startuml", result)
        self.assertIn("left to right direction", result)
        self.assertIn('component "REQ" {', result)  # the corrected §2.7 domain-group form (in the shape + §2.9)
        self.assertNotIn(" : refers to", result)  # the edges are label-free — the former uniform label is gone
        self.assertNotIn("\nend package", result)  # no named-close group line anywhere in the emission shape
        self.assertIn("@enduml", result)

    def test_pins_the_worked_example_emitted_subset(self):
        # drift pin: the rulebook §2.9 worked example and the parser-gate's
        # candidate subset are the SAME text — a silent edit of either breaks
        # the gate's verdict basis
        result = reference_graph()

        self.assertIn(_EMITTED_SUBSET, result)

    def test_pins_the_env_var_title_and_truncation_rules(self):
        result = reference_graph()

        for fragment in (
            "SPECMGR_DIAGRAM_MAX_TITLE",
            "40",
            "Reference Graph",
            "#quot;",
            "…",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, result)

    def test_pins_the_feat_exclusion_and_bare_feat_rejection(self):
        result = reference_graph()

        for fragment in (
            "include_feat=False",
            "--no-feat",
            "A bare `feat-NNN` as the source id is REJECTED",
            "`list_feat`",
            "feat-NNN-slug",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, result)

    def test_pins_the_uc_rulebook_validation_pointer(self):
        # the validation chain is reused as-is from the UC rulebook §3-§6 —
        # the pointer (and the three source env vars it names) must survive
        result = reference_graph()

        for fragment in (
            "specmgr://uc/plantuml",
            "SPECMGR_PLANTUML_JAR",
            "SPECMGR_PLANTUML_BIN",
            "SPECMGR_PLANTUML_URL",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, result)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            rulebook_path = Path(tmp) / "general_reference_graph.md"
            rulebook_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=rulebook_path):
                sut = reference_graph

                first = sut()
                rulebook_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_rulebook_missing(self):
        """A missing packaged rulebook file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = reference_graph

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
