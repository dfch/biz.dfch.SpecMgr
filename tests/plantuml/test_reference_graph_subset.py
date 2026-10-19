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
2026-10-15 tripwire amendment (feat-214-rel-invalid-diag Phase 100) + the env-gated
real-parser gates for the reference-graph emission subset.

The 2026-10-10 amendment (rulebook §7.1, both rulebooks): ``component`` joins
the declaration keyword set; the ``as`` alias grammar (frozen shapes + legacy
walk) accepts a bracketed ``[...]`` token with no whitespace and no brackets
inside, recorded in the declared set UNBRACKETED; ``_strip_operand`` unwraps
a fully-bracketed token so declaration and edge operands compare identically.

The 2026-10-15 tripwire amendment (the reference-graph rulebook §7.1): a
``package`` fragment that COLLECTS component declarations (a ``component``
keyword declaration line or a short-form ``[X]`` line) must close with a
``}`` line — a named ``end package`` close (after a braceless-open or a
curly-open) and an unclosed such fragment at a block boundary are errors in
BOTH modes with a curly-brace fix hint (the demonstrated false-negative
class: the pre-amendment checker reported zero findings in both modes over
the real-parser-rejected braceless ``package`` grouping). Content-
conditional: ``package`` fragments holding sequence content (participants —
the UC subset) are untouched.

The 2026-10-18 fix (feat-214-rel-invalid-diag Phase 150, E1/E2/I1): the two
firing sites the 2026-10-15 note froze WITHOUT a parser verdict — an
unclosed-at-block-boundary component-collecting ``package`` (every open
shape) and a bare-``@end`` close of one (every open shape) — are
parser-ACCEPTED by the pinned 1.2026.8 (file- and pipe-form; the feature
plan's More Information matrix), so the block-boundary site is a lenient
finding (warning in preflight, promoted error in standalone) and the
bare-``@end`` site carries the tripwire's own lenient finding; the NAMED-
CLOSE site stays an error in BOTH modes (parser-rejected, re-verified), and
the fix hint is split by the CLOSE KIND (the firing site — the Phase 160
axis correction of the 2026-10-18 open-shape split, which was precise for
only 2 of the 6 site × open-shape combinations: named close — replace the
``end package`` close with a ``}`` line; unclosed at boundary — add the
missing ``}`` line; bare ``@end`` close — replace the bare ``@end`` close
with a ``}`` line; the open shape stays named in the messages). Pinned
below (rulebook §7.1 Phase 150 note, Phase 160 correction).

``_EMITTED_SUBSET`` below is the rulebook §2.9 worked example verbatim (the
corrected 2026-10-15 layout) — the frozen emission subset the real-parser
gate verifies (component declarations, the 14-entry skinparam block,
label-free ``-->``/red-arrow edges, a self-loop, the curly ``component
"TYPE" { … }`` domain groups, a top-level ``<<UNRESOLVED>>`` node).

The gates are env-gated (the ``tests/conftest.py`` ``plantuml_source()``
machinery): where a ``SPECMGR_PLANTUML_*`` source is configured they run the
subset — and, since feat-214 Phase 100, EVERY committed reference-graph
golden (the parser sweep below) — through the real parser (parse + render,
with the render proof); where none is configured they skip cleanly
(reported via ``pytest -rs``) — but on the commit path they RUN: the CI job
``plantuml-parser`` (``.github/workflows/ci.yml``, feat-214 Phase 120;
single pinned Python 3.13.13, mirroring the docs-drift pin) hash-verifies
the pinned 1.2026.8 jar BEFORE use, exports ``SPECMGR_PLANTUML_JAR``, and
runs the full suite with ``pytest -n auto -rs`` so the gates execute and
pass instead of skipping (ACC-005 — rulebook §4.3, the Phase 120 amendment
note). Local dev runs the identical gates with zero repo changes via the
gitignored repo-root ``.env`` (loaded by ``tests/conftest.py`` at
collection — e.g. ``SPECMGR_PLANTUML_JAR=<jar path>``). The 2026-10-15
verdict — the pre-correction layout FAILS (``ERROR 25`` — Syntax Error?
(Assumed diagram type: component)), the corrected layout + label-free edges
PASS (exit 0; the SVG carries the palette fills, the node titles, and the
red ``#F00`` arrows), and "an emission layout is not frozen on a skipped
gate" — is recorded in the reference-graph rulebook §4.3 and in the feature
plan's Progress.
"""

import re
import unittest
from pathlib import Path

from biz.dfch.specmgr.plantuml import chain, structure
from biz.dfch.specmgr.plantuml.structure import (
    MODE_PREFLIGHT,
    MODE_STANDALONE,
    check_structure,
)
from tests.conftest import assert_rendered_svg, render_proof_body, require_plantuml_source

#: The frozen emission subset (the reference-graph rulebook §2.9 worked
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

component "REQ" {
component "Requirement A" as [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] <<REQ>>
}

component "UC" {
component "Use Case B" as [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] <<UC>>
}

component "FEAT" {
component "Feature: PlantUML Reference Graph Diagrams" as [feat-207-reference-graph] <<FEAT>>
}

[feat-207-reference-graph] --> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d]
[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] --> [DEC-9cfe511e-3f0f-4f0e-b3f4-9c8f5f1c1a2b]
[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] -[#red]-> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d]
[REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d] -[#red]-> [UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c]
[UC-6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c] -[#red]-> [REQ-1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d]
@enduml
"""

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "uc-diagrams"
_GOLDENS = Path(__file__).resolve().parents[1] / "fixtures" / "reference-graphs" / "goldens"

#: One resolved node line of the emission (``component "{label}" as
#: [alias] <<ST>>`` with a domain stereotype — the ``<<UNRESOLVED>>`` lines
#: are node lines too, but their verbatim-id label is an id, not a title).
_RESOLVED_NODE_LINE = re.compile(r'^component "(?P<label>.*)" as \[[^\[\]]+\] <<(?P<stereotype>[A-Z]+)>>$')


def _node_title_proof(text: str) -> str:
    """The render-proof string for one emission: the longest word of the FIRST resolved node's label.

    The label's ``#quot;`` escapes are undone before word selection (the
    rendered SVG carries the real quote character), and the proof is the
    longest ALL-ALPHA word of the label: the real renderer may wrap a long
    label across SVG lines at word boundaries, never inside a word, so one
    word is always present contiguously in the SVG body (the render-proof
    contract of the label-free layout — the former uniform edge label is
    no longer a text the SVG must carry).
    """
    first_label: str | None = None
    for line in text.split("\n"):
        match = _RESOLVED_NODE_LINE.match(line)
        if match is not None and match.group("stereotype") != "UNRESOLVED":
            first_label = match.group("label")
            break
    assert first_label is not None, "the emission carries no resolved node label for a render proof"
    label = first_label.replace("#quot;", '"')
    words = [word.strip('…"') for word in label.split()]
    candidates = [word for word in words if word and word.isalpha()]
    if not candidates:
        candidates = [word for word in words if word]
    assert candidates, f"no usable node-title word in label {first_label!r}"
    result = max(candidates, key=len)
    return result


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


class TestPackageComponentTripwire(unittest.TestCase):
    """The 2026-10-15 tripwire amendment (feat-214-rel-invalid-diag Phase 100, REQ-004 /
    rulebook §7.1): a ``package`` fragment that collects component
    declarations (a ``component`` keyword declaration line or a short-form
    ``[X]`` line) must close with a ``}`` line — a named ``end package``
    close (braceless-open or curly-open) is an error in BOTH modes with a
    curly-brace fix hint (the 2026-10-18 Phase 150 fix: the NAMED-CLOSE
    site is the only remaining both-modes error — the unclosed-at-boundary
    shapes it froze alongside were parser-accepted, and the block-boundary
    site is now a lenient finding, as is the bare-``@end`` close of a
    component-collecting ``package``). Content-conditional: sequence
    ``package`` fragments (participants) and the corrected curly
    ``component "TYPE" { … }`` form stay zero-finding."""

    def test_braceless_package_with_component_and_named_close_errors_both_modes(self):
        # the verified parser-failing shape Q1 (the pre-correction shipped
        # layout): the tripwire fires on the close line in both modes —
        # the Phase 160 strengthening pins the primary clause precise
        # (named-close site: replace the 'end package' close)
        text = '@startuml t\npackage "REQ"\ncomponent Foo\nend package\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertEqual(len(result.errors), 1, f"{mode}: {result.errors}")
                self.assertEqual(result.errors[0].line, 4)
                self.assertIn("named 'end package' close", result.errors[0].message)
                self.assertIn("opened at line 2, braceless", result.errors[0].message)
                self.assertIn("replace the 'end package' close", result.errors[0].fix_hint)
                self.assertIn("curly-brace", result.errors[0].fix_hint)
                self.assertIn('component "TYPE" {', result.errors[0].fix_hint)
                self.assertEqual(result.warnings, [])

    def test_curly_open_package_with_named_close_errors_both_modes(self):
        # the verified parser-failing shape R1 (curly-open + 'end package'
        # close): the open shape does not matter — the named close over a
        # component declaration is the error — the Phase 160
        # strengthening pins the primary clause precise (named-close site:
        # replace the 'end package' close)
        text = '@startuml t\npackage "REQ" {\ncomponent Foo\nend package\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertEqual(len(result.errors), 1, f"{mode}: {result.errors}")
                self.assertEqual(result.errors[0].line, 4)
                self.assertIn("named 'end package' close", result.errors[0].message)
                self.assertIn("opened at line 2, curly-open", result.errors[0].message)
                self.assertIn("replace the 'end package' close", result.errors[0].fix_hint)
                self.assertIn("curly-brace", result.errors[0].fix_hint)

    def test_unclosed_component_package_at_enduml_is_lenient_both_modes(self):
        # RE-PINNED 2026-10-18 (Phase 150, E1): the pre-fix version pinned
        # the block-boundary HARD ERROR on this parser-ACCEPTED shape
        # (braceless 'package "REQ"' + 'component Foo' + '@enduml' — the
        # pinned 1.2026.8 renders it, rc=0 + SVG, file- and pipe-form). The
        # lenient finding is attributed to the OPEN line (the note-unclosed
        # error's own convention), warning in preflight / promoted error in
        # standalone, with the block-boundary fix-hint variant (add the
        # missing '}' line — the Phase 160 close-kind key)
        text = '@startuml t\npackage "REQ"\ncomponent Foo\n@enduml\n'

        preflight = check_structure(text, MODE_PREFLIGHT)
        self.assertTrue(preflight.ok)
        self.assertEqual(preflight.errors, [])
        self.assertEqual(len(preflight.warnings), 1)
        self.assertEqual(preflight.warnings[0].line, 2)
        self.assertIn("unclosed at the block boundary", preflight.warnings[0].message)
        self.assertIn("opened at line 2, braceless", preflight.warnings[0].message)
        self.assertIn("add the missing '}'", preflight.warnings[0].fix_hint)
        self.assertIn('component "TYPE" {', preflight.warnings[0].fix_hint)

        standalone = check_structure(text, MODE_STANDALONE)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertEqual(standalone.errors[0].line, 2)
        self.assertIn("unclosed at the block boundary", standalone.errors[0].message)
        self.assertIn("add the missing '}'", standalone.errors[0].fix_hint)
        self.assertEqual(standalone.warnings, [])

    def test_unclosed_component_package_at_true_eof_is_lenient_both_modes(self):
        # RE-PINNED 2026-10-18 (Phase 150, E1): true EOF (no @enduml) — the
        # lenient tripwire finding fires alongside the missing-@enduml
        # lenient finding (two lenient findings: warning in preflight,
        # promoted errors in standalone); the pre-fix version pinned the
        # tripwire as a both-modes ERROR on this parser-accepted shape
        text = '@startuml t\npackage "REQ"\ncomponent Foo\n'

        preflight = check_structure(text, MODE_PREFLIGHT)
        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 2)
        tripwire = [w for w in preflight.warnings if "unclosed at the block boundary" in w.message]
        self.assertEqual(len(tripwire), 1)
        self.assertEqual(tripwire[0].line, 2)

        standalone = check_structure(text, MODE_STANDALONE)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 2)
        tripwire = [error for error in standalone.errors if "unclosed at the block boundary" in error.message]
        self.assertEqual(len(tripwire), 1)
        self.assertEqual(tripwire[0].line, 2)

    def test_short_form_component_line_trips_the_package(self):
        # the Q1 matrix's short `[Foo]` form: a line of exactly one bracketed
        # token is a component declaration to the parser — it trips the
        # braceless package
        text = "@startuml t\npackage REQ\n[Foo]\nend package\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("named 'end package' close" in error.message for error in result.errors))

    def test_component_declarations_outside_a_package_do_not_trip(self):
        # top-level component declarations (no enclosing package fragment)
        # carry no tripwire — the new layout's own shape
        text = "@startuml t\ncomponent Foo\ncomponent Bar\n[Foo] --> [Bar]\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_the_corrected_curly_component_group_is_zero_finding(self):
        # the parser-verified fix shape (the corrected emission layout's own
        # domain group): zero findings in both modes
        text = '@startuml t\ncomponent "REQ" {\ncomponent Foo\n}\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_sequence_package_stays_zero_finding(self):
        # the content condition: a package fragment holding SEQUENCE content
        # (participants — the UC subset) collects no component declaration
        # and keeps its zero-finding behavior (named close included)
        text = "@startuml t\npackage p\nparticipant A\nparticipant B\nA -> B: x\nend package\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_unclosed_sequence_package_keeps_only_the_lenient_finding(self):
        # an unclosed package WITHOUT a component declaration keeps the
        # pre-amendment lenient behavior (warning in preflight, promoted
        # error in standalone) — no tripwire message
        text = "@startuml t\npackage p\nparticipant A\nA -> A: x\n@enduml\n"

        preflight = check_structure(text, MODE_PREFLIGHT)
        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertIn("unclosed 'package' fragment", preflight.warnings[0].message)

        standalone = check_structure(text, MODE_STANDALONE)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("unclosed 'package' fragment", standalone.errors[0].message)

    # --- the 2026-10-17 fix (feat-214-rel-invalid-diag Phase 140, E1): the
    # parser-OK shapes — a curly-opened 'package' fragment closed with a '}'
    # line is REAL-PARSER-ACCEPTED over component declarations (the plan's
    # isolation matrix; re-verified against the pinned 1.2026.8, both shapes
    # exit 0), so the tripwire's own required close must not be reported as
    # unclosed at the block boundary (the pre-fix false positive) ---

    def test_curly_open_package_quoted_with_component_and_brace_close_is_zero_finding_both_modes(self):
        # parser-OK shape (quoted name, verified exit 0 on 1.2026.8): zero
        # findings in both modes — no tripwire, no lenient unclosed finding
        text = '@startuml t\npackage "REQ" {\ncomponent Foo\n}\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_curly_open_package_bare_name_with_component_and_brace_close_is_zero_finding_both_modes(self):
        # parser-OK shape (the isolation matrix's literal unquoted row,
        # verified exit 0 on 1.2026.8): zero findings in both modes
        text = "@startuml t\npackage REQ {\ncomponent Foo\n}\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_nested_curly_packages_with_components_close_innermost_first(self):
        # parser-OK nested shape (verified exit 0 on 1.2026.8): each '}' pops
        # the INNERMOST curly-open fragment (the inner package first), so no
        # fragment reaches the block boundary — zero findings in both modes.
        # (The pre-fix code left both open and reported BOTH with the
        # factually-wrong "never closed with '}'" tripwire error.)
        text = '@startuml t\npackage "A" {\npackage "B" {\ncomponent Foo\n}\n}\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"{mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    # --- the 2026-10-18 fix (feat-214-rel-invalid-diag Phase 150, E1/E2/I1,
    # hint axis corrected Phase 160): the parser-ACCEPTED
    # unclosed-at-boundary shapes (every open shape) and the bare-@end close
    # of a component-collecting package (every open shape) are pinned to the
    # lenient treatment with the close-kind-keyed fix hint — each shape
    # verified against the pinned 1.2026.8, file- AND pipe-form (rc=0 +
    # SVG; the feature plan's More Information matrix) ---

    def test_unclosed_curly_open_component_package_at_enduml_is_lenient_both_modes(self):
        # Phase 150 shape a2 (parser-ACCEPTED: curly-open 'package "REQ" {'
        # + component, unclosed at @enduml — rc=0 + SVG, both forms): the
        # lenient finding names the curly-open shape and carries the
        # block-boundary fix-hint variant (add the missing '}' line — the
        # Phase 160 axis correction: the close kind, not the open shape,
        # keys the hint; the pre-fix pin asserted the open-shape variant,
        # "replace the 'end package' close", which named a line that does
        # not exist here)
        text = '@startuml t\npackage "REQ" {\ncomponent Foo\n@enduml\n'

        preflight = check_structure(text, MODE_PREFLIGHT)
        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertEqual(preflight.warnings[0].line, 2)
        self.assertIn("unclosed at the block boundary", preflight.warnings[0].message)
        self.assertIn("opened at line 2, curly-open", preflight.warnings[0].message)
        self.assertIn("add the missing '}'", preflight.warnings[0].fix_hint)

        standalone = check_structure(text, MODE_STANDALONE)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("opened at line 2, curly-open", standalone.errors[0].message)
        self.assertIn("add the missing '}'", standalone.errors[0].fix_hint)
        self.assertEqual(standalone.warnings, [])

    def test_unclosed_braceless_component_package_with_later_content_is_lenient_both_modes(self):
        # Phase 150 shape a3 (parser-ACCEPTED: later content after the
        # unclosed braceless package — rc=0 + SVG, both forms): later
        # content does not change the treatment — the lenient finding is
        # attributed to the OPEN line
        text = '@startuml t\npackage "REQ"\ncomponent Foo\ncomponent Bar\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                findings = result.warnings if mode == MODE_PREFLIGHT else result.errors
                self.assertEqual(len(findings), 1, f"{mode}: {findings}")
                self.assertEqual(findings[0].line, 2)
                self.assertIn("unclosed at the block boundary", findings[0].message)
                self.assertIn("opened at line 2, braceless", findings[0].message)
                self.assertIn("add the missing '}'", findings[0].fix_hint)
                if mode == MODE_PREFLIGHT:
                    self.assertTrue(result.ok)
                    self.assertEqual(result.errors, [])
                else:
                    self.assertFalse(result.ok)
                    self.assertEqual(result.warnings, [])

    def test_unclosed_braceless_component_package_with_stray_brace_is_lenient_both_modes(self):
        # Phase 150 shape a4 (parser-ACCEPTED: braceless package + a stray
        # '}' line — rc=0 + SVG, both forms): the '}' does NOT pop the
        # braceless fragment (the Phase 140 pop closes curly-open fragments
        # only), so EXACTLY ONE lenient finding fires — the pre-fix code
        # errored here with the factually-wrong "never closed with '}'"
        # diagnosis (the author had already followed the old hint)
        text = '@startuml t\npackage "REQ"\ncomponent Foo\n}\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                findings = result.warnings if mode == MODE_PREFLIGHT else result.errors
                self.assertEqual(len(findings), 1, f"{mode}: {findings}")
                self.assertEqual(findings[0].line, 2)
                self.assertIn("unclosed at the block boundary", findings[0].message)
                self.assertIn("opened at line 2, braceless", findings[0].message)
                self.assertIn("add the missing '}'", findings[0].fix_hint)

    def test_bare_atend_closing_component_package_is_the_tripwire_lenient_finding(self):
        # Phase 150 shape b1 (parser-ACCEPTED: braceless package + bare
        # @end — rc=0 + SVG, both forms): the tripwire's OWN lenient
        # finding on the @end line (not the generic name-omission finding —
        # whose hint would steer the author to the parser-rejected 'end
        # package' close), with the bare-@end fix-hint variant (replace the
        # bare '@end' close — the Phase 160 axis correction; the pre-fix
        # pin asserted the open-shape variant, "add the missing '}'", which
        # is imprecise: the block IS closed, by the '@end' line)
        text = '@startuml t\npackage "REQ"\ncomponent Foo\n@end\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                findings = result.warnings if mode == MODE_PREFLIGHT else result.errors
                self.assertEqual(len(findings), 1, f"{mode}: {findings}")
                self.assertEqual(findings[0].line, 4)
                self.assertIn(
                    "bare @end closes the package fragment that collects component declarations",
                    findings[0].message,
                )
                self.assertIn("opened at line 2, braceless", findings[0].message)
                self.assertIn("replace the bare '@end' close", findings[0].fix_hint)
                self.assertIn('component "TYPE" {', findings[0].fix_hint)

    def test_bare_atend_closing_curly_component_package_is_the_tripwire_lenient_finding(self):
        # Phase 150 shape b2 (parser-ACCEPTED: curly-open package + bare
        # @end — rc=0 + SVG, both forms): the same treatment with the
        # bare-@end fix-hint variant (pins the close-kind keying at this
        # site — the Phase 160 axis correction; the open shape stays named
        # in the message; the pre-fix pin asserted the open-shape variant,
        # "replace the 'end package' close", which named a line that does
        # not exist here)
        text = '@startuml t\npackage "REQ" {\ncomponent Foo\n@end\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                findings = result.warnings if mode == MODE_PREFLIGHT else result.errors
                self.assertEqual(len(findings), 1, f"{mode}: {findings}")
                self.assertEqual(findings[0].line, 4)
                self.assertIn(
                    "bare @end closes the package fragment that collects component declarations",
                    findings[0].message,
                )
                self.assertIn("opened at line 2, curly-open", findings[0].message)
                self.assertIn("replace the bare '@end' close", findings[0].fix_hint)


class TestReferenceGraphSubsetParserGate(unittest.TestCase):
    """The Phase 100 real-parser gate (env-gated, ACC-001/ACC-002's parser half):
    the frozen emission subset must parse + render through the REAL PlantUML
    source. The 2026-10-15 verdict (rulebook §4.3, the feature plan's
    Progress): the pre-correction layout FAILS the pinned 1.2026.8 parser
    (``ERROR 25`` — Syntax Error? (Assumed diagram type: component)), the
    corrected subset (curly domain groups + label-free edges — the §2.9
    worked example) PASSES (exit 0, palette fills + node titles + the red
    ``#F00`` arrows in the SVG) — the red-arrow syntax ``-[#red]->`` and the
    label-free edge forms ship on this verdict. On a clean skip (no
    ``SPECMGR_PLANTUML_*`` source configured, e.g. a sourceless local run)
    the gate skips with the ``require_plantuml_source`` reason; an emission
    layout is NOT frozen on a skipped gate (the 2026-10-15 convention) —
    on the commit path the gate RUNS: the CI job ``plantuml-parser`` (feat-
    214 Phase 120) configures the hash-verified pinned jar and runs this
    test with ``-rs``, where no ``require_plantuml_source`` skip is
    tolerated (ACC-005), and the local dev flow is the gitignored repo-root
    ``.env`` (``SPECMGR_PLANTUML_JAR=...``, rulebook §4.3 Phase 120 note)."""

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
        # the render-proof contract (the 2026-10-15 proof-string change): the
        # selected source's own SVG body carries a node title (the label-free
        # edges no longer carry the uniform edge label) and no crash marker
        assert_rendered_svg(
            render_proof_body(info.kind, info.value, _EMITTED_SUBSET), _node_title_proof(_EMITTED_SUBSET)
        )


class TestReferenceGraphGoldenParserSweep(unittest.TestCase):
    """The env-gated golden parser sweep (feat-214-rel-invalid-diag Phase 100, REQ-003/REQ-006):
    EVERY committed reference-graph golden — all 22 byte-stable files under
    ``tests/fixtures/reference-graphs/goldens/`` — must parse + render
    through the REAL PlantUML source, extending the parser verification from
    the one synthetic subset (the §2.9 worked example) to the whole frozen
    golden set (the root-cause fix for the ship-on-a-skipped-gate gap: on
    the commit path the CI job ``plantuml-parser`` — feat-214 Phase 120,
    hash-verified pinned jar, full suite with ``-rs`` — makes this sweep
    RUN on every commit; the gitignored repo-root ``.env`` dev flow does
    the same locally, rulebook §4.3 Phase 120 note)."""

    def test_every_golden_renders_valid_through_the_real_parser(self):
        goldens = sorted(_GOLDENS.glob("*.puml"))
        # the whole frozen set — the count is part of the pin; it holds on a
        # sourceless (skipped) run too (the 2026-10-18 fix, Phase 150, I2 —
        # the pre-fix assert ran only after require_plantuml_source, so a
        # sourceless run would add a 23rd golden silently)
        self.assertEqual(len(goldens), 22)
        info = require_plantuml_source(self)
        assert info.kind is not None
        assert info.value is not None  # an available source always carries its configured value

        for path in goldens:
            text = path.read_text(encoding="utf-8")
            with self.subTest(golden=path.name):
                result = chain.validate_plantuml(text)

                self.assertEqual(result.checked_by, info.kind)
                self.assertTrue(result.available)
                self.assertEqual(result.source_state, chain.STATE_OK)
                self.assertTrue(result.structure_ok)
                self.assertIs(result.valid, True, f"{path.name}: {result}")
                self.assertIs(result.rendered, True, f"{path.name}: {result}")
                # the render-proof contract: the selected source's own SVG body
                # carries a node title (the label-free edges carry no text to
                # prove against) and no crash marker
                assert_rendered_svg(render_proof_body(info.kind, info.value, text), _node_title_proof(text))


if __name__ == "__main__":
    unittest.main()
