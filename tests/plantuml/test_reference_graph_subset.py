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

"""The 2026-10-10 structure-checker amendment (feat-207-reference-graph Phase 100) + the
env-gated real-parser gate for the candidate reference-graph emission subset.

The amendment (rulebook §6.1, both rulebooks): ``component`` joins the
declaration keyword set; the ``as`` alias grammar (frozen shapes + legacy
walk) accepts a bracketed ``[...]`` token with no whitespace and no brackets
inside, recorded in the declared set UNBRACKETED; ``_strip_operand`` unwraps
a fully-bracketed token so declaration and edge operands compare identically.
``_EMITTED_SUBSET`` below is the rulebook §2.9 worked example verbatim — the
frozen candidate emission subset the Phase 100 real-parser gate verifies
(component declarations, the 14-entry skinparam block, ``-->``/red-arrow
edges with the ``: refers to`` label, a self-loop, ``package … end package``
groups, a top-level ``<<UNRESOLVED>>`` node).

The gate is env-gated (the ``tests/conftest.py`` ``plantuml_source()``
machinery): where a ``SPECMGR_PLANTUML_*`` source is configured it runs the
subset through the real parser (parse + render); where none is configured it
skips cleanly (reported via ``pytest -rs``). The 2026-10-10 verdict of a
clean skip — "skipped -- candidate ``-[#red]->`` retained, re-verify where a
source is configured" — is recorded in the reference-graph rulebook §4.3 and
in the feature plan's Progress.
"""

import unittest
from pathlib import Path

from biz.dfch.specmgr.plantuml import chain, structure
from biz.dfch.specmgr.plantuml.structure import (
    MODE_PREFLIGHT,
    MODE_STANDALONE,
    check_structure,
)
from tests.conftest import assert_rendered_svg, render_proof_body, require_plantuml_source

#: The candidate emission subset (the reference-graph rulebook §2.9 worked
#: example, verbatim — the drift pin between the rulebook and this gate).
_EMITTED_SUBSET = """\
@startuml Requirement A

skinparam component {
  backgroundColor<<ADR>> LightYellow
  backgroundColor<<REQ>> LightBlue
  backgroundColor<<UC>> Pink
  backgroundColor<<TSK>> Honeydew
  backgroundColor<<QA>> LemonChiffon
  backgroundColor<<PRB>> LightCoral
  backgroundColor<<GOL>> Lavender
  backgroundColor<<RSK>> Orange
  backgroundColor<<DEC>> LightGreen
  backgroundColor<<SOP>> PowderBlue
  backgroundColor<<FEAT>> PaleTurquoise
  backgroundColor<<VCR>> Khaki
  backgroundColor<<SYSRS>> Thistle
  backgroundColor<<UNRESOLVED>> DarkRed
}

left to right direction

component "9cfe511e-3f0f-4f0e-b3f4-9c8f5f1c1a2b" as [DEC-9cfe511e-3f0f-4f0e-b3f4-9c8f5f1c1a2b] <<UNRESOLVED>>

package "REQ"
component "Requirement A" as [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] <<REQ>>
end package

package "UC"
component "Use Case B" as [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] <<UC>>
end package

package "FEAT"
component "Feature: PlantUML Reference Graph Diagrams" as [feat-207-reference-graph] <<FEAT>>
end package

[feat-207-reference-graph] --> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] : refers to
[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] --> [DEC-9cfe511e-3f0f-4f0e-b3f4-9c8f5f1c1a2b] : refers to
[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] -[#red]-> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] : refers to
[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] -[#red]-> [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] : refers to
[UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] -[#red]-> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] : refers to
@enduml
"""

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "uc-diagrams"


class TestReferenceGraphSubsetChecker(unittest.TestCase):
    """The amended checker over the reference-graph emission subset (ACC-002's
    zero-finding half — both modes, no source needed)."""

    def test_component_declaration_registers_label_and_alias(self):
        # edges reference the QUOTED LABEL, the UNBRACKETED BRACKETED ALIAS, a
        # self-loop, and the red-arrow line (the last is outside the frozen
        # line grammar — silently accepted, so it must contribute no finding)
        text = (
            "@startuml t\n"
            'component "Requirement A" as [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] <<REQ>>\n'
            'component "Use Case B" as [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] <<UC>>\n'
            '"Requirement A" --> [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] : refers to\n'
            "[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] --> [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] : refers to\n"
            "[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] --> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] : refers to\n"
            "[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] -[#red]-> [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] : refers to\n"
            "@enduml\n"
        )

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_emitted_subset_zero_findings_both_modes(self):
        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(_EMITTED_SUBSET, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_bracketed_alias_records_unbracketed_quoted_shape(self):
        label, alias, tail, findings = structure._declaration_parts(
            '"Requirement A" as [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] <<REQ>>'
        )

        self.assertEqual(label, "Requirement A")
        self.assertEqual(alias, "REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d")
        self.assertEqual(tail, "<<REQ>>")
        self.assertEqual(findings, [])

    def test_bracketed_alias_records_unbracketed_legacy_walk(self):
        # a shape the frozen regexes do not cover (the unbalanced run) falls to
        # the legacy walk — the bracketed alias must STILL record unbracketed
        label, alias, _tail, findings = structure._declaration_parts("A as [REQ-1] <<REQ")

        self.assertEqual(label, "A")
        self.assertEqual(alias, "REQ-1")
        self.assertEqual(len(findings), 1)
        self.assertIn("unbalanced <<stereotype>>", findings[0].message)

    def test_bracketed_alias_with_whitespace_still_errors_both_modes(self):
        # the negative control: whitespace inside the brackets is NOT the
        # frozen alias shape — the line falls to the legacy walk and the
        # unbalanced-<<stereotype>> tail check fires (error in both modes)
        text = '@startuml t\ncomponent "Requirement A" as [REQ bad] <<REQ>>\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("unbalanced <<stereotype>>" in error.message for error in result.errors))

    def test_unbalanced_stereotype_with_bracketed_alias_still_errors_both_modes(self):
        text = '@startuml t\ncomponent "Requirement A" as [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] <<REQ\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("unbalanced <<stereotype>>" in error.message for error in result.errors))

    def test_uc_goldens_stay_zero_finding(self):
        # the existing UC subset regression pin (ACC-002): the amendment is
        # additive — every UC golden passes the amended checker exactly as
        # before (the renderer-vs-golden byte-identity itself is pinned in
        # tests/uc/models/v2/test_renderer.py)
        for name in ("buy-goods.usecase.golden", "package.golden"):
            golden = (_FIXTURES / name).read_text(encoding="utf-8")
            for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
                with self.subTest(golden=name, mode=mode):
                    result = check_structure(golden, mode)
                    self.assertEqual(result.errors, [], f"{name} {mode}: {result.errors}")
                    self.assertEqual(result.warnings, [], f"{name} {mode}: {result.warnings}")

        sequence = (_FIXTURES / "buy-goods.sequence.golden").read_text(encoding="utf-8")
        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(sequence, mode)
                self.assertEqual(result.errors, [], f"sequence {mode}: {result.errors}")
                self.assertEqual(len(result.warnings), 5, f"sequence {mode}: {result.warnings}")
                for warning in result.warnings:
                    self.assertIn("UNATTRIBUTED marker", warning.message)


class TestReferenceGraphSubsetParserGate(unittest.TestCase):
    """The Phase 100 real-parser gate (env-gated, ACC-002's parser half): the
    candidate emission subset must parse + render through the REAL PlantUML
    source — the frozen red-arrow syntax ``-[#red]->`` ships on this verdict.
    On a clean skip (no ``SPECMGR_PLANTUML_*`` source configured) the
    recorded verdict is: "skipped -- candidate ``-[#red]->`` retained,
    re-verify where a source is configured" (rulebook §4.3, the feature
    plan's Progress)."""

    def test_candidate_subset_renders_valid_through_the_real_parser(self):
        info = require_plantuml_source(self)
        assert info.kind is not None
        assert info.value is not None  # an available source always carries its configured value

        result = chain.validate_plantuml(_EMITTED_SUBSET)

        self.assertEqual(result.checked_by, info.kind)
        self.assertTrue(result.available)
        self.assertEqual(result.source_state, chain.STATE_OK)
        self.assertTrue(result.structure_ok)
        self.assertIs(result.valid, True)
        self.assertIs(result.rendered, True)
        # the render-proof contract: the selected source's own SVG body carries
        # the diagram's uniform edge label and no crash marker
        assert_rendered_svg(render_proof_body(info.kind, info.value, _EMITTED_SUBSET), "refers to")


if __name__ == "__main__":
    unittest.main()
