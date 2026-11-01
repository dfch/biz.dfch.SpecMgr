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
# along with this program.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for `plantuml.structure` (the two-mode checker, rulebook §6).

The five verified lenient cases ship as golden tests — each a minimal
diagram exercising exactly that case (all five verified to render OK
against the real 1.2026.8 parser, so preflight mode must accept them at
most as warnings and standalone mode must promote them to errors). The
template/example packaged data files must pass in both modes.
"""

import unittest

from biz.dfch.specmgr.plantuml import structure
from biz.dfch.specmgr.plantuml.structure import (
    MODE_PREFLIGHT,
    MODE_STANDALONE,
    UNATTRIBUTED_MARKER_PREFIX,
    check_structure,
    is_unattributed_marker,
)


def _errors(result: structure.StructureCheckResult) -> list[structure.Finding]:
    return result.errors


class TestLenientSet(unittest.TestCase):
    """The verified parser-lenient set (rulebook §6.4 — exactly five cases)."""

    def test_unclosed_fragment_at_eof_is_lenient(self):
        text = "@startuml\nparticipant A\nparticipant B\nalt c\nA -> B: x\n@enduml\n"

        preflight = check_structure(text, MODE_PREFLIGHT)
        standalone = check_structure(text, MODE_STANDALONE)

        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertIn("unclosed 'alt' fragment", preflight.warnings[0].message)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("unclosed 'alt' fragment", standalone.errors[0].message)

    def test_missing_enduml_is_lenient(self):
        text = "@startuml\nparticipant A\nparticipant B\nA -> B: x\n"

        preflight = check_structure(text, MODE_PREFLIGHT)
        standalone = check_structure(text, MODE_STANDALONE)

        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertIn("missing @enduml", preflight.warnings[0].message)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("missing @enduml", standalone.errors[0].message)

    def test_bare_at_end_is_lenient(self):
        text = "@startuml\nparticipant A\nparticipant B\nalt c\nA -> B: x\n@end\n@enduml\n"

        preflight = check_structure(text, MODE_PREFLIGHT)
        standalone = check_structure(text, MODE_STANDALONE)

        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertIn("bare @end closes the 'alt' fragment", preflight.warnings[0].message)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("bare @end closes the 'alt' fragment", standalone.errors[0].message)

    def test_dangling_arrow_is_lenient(self):
        text = "@startuml\nactor A\nA -->\n@enduml\n"

        preflight = check_structure(text, MODE_PREFLIGHT)
        standalone = check_structure(text, MODE_STANDALONE)

        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertIn("dangling arrow", preflight.warnings[0].message)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("dangling arrow", standalone.errors[0].message)

    def test_undeclared_participant_is_lenient(self):
        text = "@startuml\nparticipant A\nA -> B: x\n@enduml\n"

        preflight = check_structure(text, MODE_PREFLIGHT)
        standalone = check_structure(text, MODE_STANDALONE)

        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertIn("undeclared participant 'B'", preflight.warnings[0].message)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertIn("undeclared participant 'B'", standalone.errors[0].message)

    def test_clean_diagram_has_no_findings_in_either_mode(self):
        text = "@startuml T\nparticipant A\nparticipant B\nA -> B: x\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])


class TestBothModeErrors(unittest.TestCase):
    """Findings that are errors in BOTH modes (real errors, parser-verified)."""

    def test_missing_startuml_is_an_error_in_both_modes(self):
        text = "participant A\nA -> B: x\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertEqual(len(result.errors), 1)
                self.assertIn("no @startuml line found", result.errors[0].message)
                self.assertEqual(result.errors[0].line, 1)

    def test_unclosed_note_at_eof_is_an_error_in_both_modes(self):
        text = "@startuml\nparticipant A\nparticipant B\nA -> B: x\nnote right\n  hello\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("never closed" in error.message for error in result.errors))

    def test_stray_end_is_an_error_in_both_modes(self):
        text = "@startuml\nparticipant A\nparticipant B\nA -> B: x\nend\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("stray end" in error.message for error in result.errors))

    def test_end_note_without_open_note_is_an_error_in_both_modes(self):
        text = "@startuml\nparticipant A\nparticipant B\nA -> B: x\nend note\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("stray 'end note'" in error.message for error in result.errors))

    def test_bare_end_cannot_close_a_box(self):
        text = "@startuml\nbox b\nparticipant A\nA -> B: x\nend\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("cannot close the 'box' fragment" in error.message for error in result.errors))

    def test_unbalanced_quote_in_declaration_is_an_error_in_both_modes(self):
        text = '@startuml\nactor "Unfinished\nA -> B: x\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("unbalanced double quote" in error.message for error in result.errors))


class TestDeclarationStereotypes(unittest.TestCase):
    """Declarations with a trailing balanced ``<<stereotype>>`` — with or without
    an ``as`` alias (rulebook §6.1's declaration enumeration; the 2026-10-08
    amendment — the pre-amendment checker misparsed a bare label +
    ``<<stereotype>>`` WITHOUT an alias: the split consumed the `` <<``
    separator, misread the stereotype's inside as the alias, and the leftover
    ``>>`` failed the run check — a false rejection in BOTH modes of shapes
    the real 1.2026.8 parser accepts (verified live: 200 + real SVG))."""

    def test_bare_label_with_stereotype_and_no_alias_is_accepted_both_modes(self):
        for line in (
            "participant Alice <<user>>",
            "actor Bob <<customer>>",
            "usecase Login <<user goal>>",
        ):
            with self.subTest(line=line):
                text = f"@startuml\n{line}\n@enduml\n"
                for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
                    with self.subTest(mode=mode):
                        result = check_structure(text, mode)
                        self.assertTrue(result.ok, f"{mode}: {result.errors}")
                        self.assertEqual(result.errors, [])
                        self.assertEqual(result.warnings, [])

    def test_stereotype_with_and_without_alias_is_accepted_both_modes(self):
        # the carried shapes (alias before the run, double run, quoted label)
        # stay accepted — byte-identical to the pre-amendment behavior
        for line in (
            "participant Alice as al <<user>>",
            'actor "Credit card company" as p2',
            'usecase "Buy Goods" as uc <<summary>>',
            "participant A <<user>> <<admin>>",
            'actor "Bob" <<customer>>',
        ):
            with self.subTest(line=line):
                text = f"@startuml\n{line}\n@enduml\n"
                for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
                    with self.subTest(mode=mode):
                        result = check_structure(text, mode)
                        self.assertTrue(result.ok, f"{mode}: {result.errors}")
                        self.assertEqual(result.errors, [])

    def test_unbalanced_stereotype_still_errors_both_modes(self):
        # the negative control: a GENUINELY unbalanced <<stereotype>> (the real
        # parser answers it 400 SYNTAX INVALID — verified live) is an error in
        # both modes — the pre-amendment checker missed this shape entirely
        # (the ' <<' separator swallowed into the alias)
        text = "@startuml\nparticipant A <<user\nA -> A: x\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("unbalanced <<stereotype>>" in error.message for error in result.errors))

    def test_stereotype_before_the_alias_still_errors_both_modes(self):
        # the frozen shape is label [as alias] <<run>> — the reversed order is
        # not the emitted subset and the real parser rejects it (verified live:
        # 400 SYNTAX INVALID) — the pre-amendment error is preserved
        text = "@startuml\nparticipant A <<user>> as al\nA -> A: x\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("unbalanced <<stereotype>>" in error.message for error in result.errors))

    def test_quoted_label_with_unbalanced_stereotype_still_errors_both_modes(self):
        text = '@startuml\nactor "A" <<user\nA -> A: x\n@enduml\n'

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("unbalanced <<stereotype>>" in error.message for error in result.errors))


class TestUnattributedMarkers(unittest.TestCase):
    """UNATTRIBUTED-marker detection (rulebook §6.5: warnings in both modes)."""

    def test_all_three_grammar_forms_are_detected(self):
        for form in structure.UNATTRIBUTED_MARKER_FORMS:
            rendered = form.replace("{N}", "3").replace("{a}", "a").replace("{M}", "2").replace("<text>", "x")
            with self.subTest(form=form):
                text = f"@startuml\nparticipant A\n{rendered}\n@enduml\n"
                result = check_structure(text, MODE_STANDALONE)
                self.assertTrue(result.ok, f"{form!r} must be a warning, not an error")
                self.assertEqual(len(result.warnings), 1)
                self.assertIn("UNATTRIBUTED marker", result.warnings[0].message)
                self.assertEqual(result.warnings[0].line, 3)

    def test_detection_matches_the_shared_prefix(self):
        self.assertTrue(is_unattributed_marker("' UNATTRIBUTED step 1: x"))
        self.assertTrue(is_unattributed_marker("' UNATTRIBUTED ext 3a step 2: x"))
        self.assertTrue(is_unattributed_marker("' UNATTRIBUTED trigger: x"))
        self.assertTrue(is_unattributed_marker(UNATTRIBUTED_MARKER_PREFIX + "anything at all"))
        self.assertFalse(is_unattributed_marker("' a normal comment"))
        self.assertFalse(is_unattributed_marker("not a comment"))

    def test_marker_helpers_build_the_frozen_grammar(self):
        self.assertEqual(
            structure.unattributed_step_marker(3, "x"),
            "' UNATTRIBUTED step 3: x",
        )
        self.assertEqual(
            structure.unattributed_ext_marker("3a", 2, "x"),
            "' UNATTRIBUTED ext 3a step 2: x",
        )
        self.assertEqual(
            structure.unattributed_trigger_marker("x"),
            "' UNATTRIBUTED trigger: x",
        )

    def test_raw_quote_in_message_is_a_warning_not_an_error(self):
        text = '@startuml\nparticipant A\nparticipant B\nA -> B: say "hi"\n@enduml\n'

        result = check_structure(text, MODE_STANDALONE)

        self.assertTrue(result.ok)
        self.assertTrue(any("raw double quote" in warning.message for warning in result.warnings))


class TestNoteContent(unittest.TestCase):
    """Note-content lines are NOT block markers (rulebook §6.3, amended 2026-10-06 — the
    frozen contract "the checker must never reject what the real parser accepts"; both
    shapes below verified rendered by both independent sources, 2026-10-06)."""

    def test_note_content_lines_that_look_like_block_markers_are_content(self):
        """A note-content line starting with @startuml / @enduml / @end is content — the
        in_note state takes precedence over the block-marker detection (pre-amendment,
        such a line mangled the checker's block state)."""
        text = (
            "@startuml\n"
            "actor Buyer\n"
            "participant Company\n"
            "\n"
            "note left of Buyer\n"
            "  a line of content\n"
            "  @startuml\n"
            "  @enduml\n"
            "  @end\n"
            "  note right\n"
            "end note\n"
            "\n"
            "alt c\n"
            "Company -> Company: self\n"
            "end\n"
            "@enduml\n"
        )

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"errors in {mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_note_content_line_that_is_exactly_end_is_content(self):
        """A note-content line that is exactly `end` is ACCEPTED (verified rendered by both
        sources 2026-10-06) — the pre-amendment false error ('an end line inside a note
        block ... the real parser rejects a bare end here') is gone; `end note` still
        closes the block, and the bare-`end` lenient-case semantics outside notes are
        unchanged (pinned by the lenient-set goldens above)."""
        text = (
            "@startuml\n"
            "actor Buyer\n"
            "participant Company\n"
            "\n"
            "note left of Buyer\n"
            "  end\n"
            "end note\n"
            "\n"
            "Buyer -> Company: hi\n"
            "@enduml\n"
        )

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"errors in {mode}: {result.errors}")
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_end_note_still_closes_the_block(self):
        """Regression pin: the close is still exactly `end note` — a content `end` line does
        not close (an unclosed note is the error in both modes)."""
        text = "@startuml\nactor Buyer\n\nnote left of Buyer\n  end\nBuyer -> Buyer: hi\n@enduml\n"

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertFalse(result.ok)
                self.assertTrue(any("never closed" in error.message for error in result.errors))

    def test_anchored_note_form_is_accepted_in_both_modes(self):
        """The amended emission form (rulebook §2.9, amended 2026-10-06): `note left of
        {participant}` / `note right of {participant}` block notes are accepted (the
        checker's existing note-block shape — no new rule), in both modes."""
        for header in ("note left of Buyer", "note right of Buyer"):
            with self.subTest(header=header):
                text = (
                    "@startuml\n"
                    "actor Buyer\n"
                    "participant Company\n"
                    "\n"
                    f"{header}\n"
                    "  content\n"
                    "end note\n"
                    "\n"
                    "Buyer -> Company: hi\n"
                    "@enduml\n"
                )
                for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
                    with self.subTest(mode=mode):
                        result = check_structure(text, mode)
                        self.assertTrue(result.ok, f"errors in {mode}: {result.errors}")
                        self.assertEqual(result.errors, [])
                        self.assertEqual(result.warnings, [])


class TestMultiBlockScoping(unittest.TestCase):
    """Each ``@startuml``…``@enduml`` block is an independent linting unit
    (the 2026-10-08 amendment — the block-scoped state resets at every block
    boundary; the parser accepts multi-block files, verified against 1.2026.8)."""

    def test_unclosed_fragment_in_first_block_is_attributed_within_that_block(self):
        # (a) two blocks, an unclosed alt in block 1: the lenient finding is
        # attributed to the alt's own line (within block 1) — standalone:
        # error, preflight: warning — and block 2 is unaffected
        text = (
            "@startuml d1\n"
            "participant A\n"
            "participant B\n"
            "alt c\n"
            "A -> B: x\n"
            "@enduml\n"
            "@startuml d2\n"
            "participant C\n"
            "participant D\n"
            "C -> D: y\n"
            "@enduml\n"
        )

        preflight = check_structure(text, MODE_PREFLIGHT)
        standalone = check_structure(text, MODE_STANDALONE)

        self.assertTrue(preflight.ok)
        self.assertEqual(len(preflight.warnings), 1)
        self.assertEqual(preflight.warnings[0].line, 4)  # the alt line, within block 1
        self.assertIn("unclosed 'alt' fragment", preflight.warnings[0].message)
        self.assertFalse(standalone.ok)
        self.assertEqual(len(standalone.errors), 1)
        self.assertEqual(standalone.errors[0].line, 4)
        self.assertIn("unclosed 'alt' fragment", standalone.errors[0].message)

    def test_two_clean_blocks_have_no_findings(self):
        # (b) two clean blocks — no findings at all in either mode
        text = (
            "@startuml d1\nactor X\nparticipant Y\nX -> Y: hi\n@enduml\n"
            "@startuml d2\nactor Z\nparticipant W\nZ -> W: hi\n@enduml\n"
        )

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, result.errors)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])

    def test_block2_name_does_not_dedup_against_block1_tables(self):
        # (c) X is declared in block 1 only; block 2 uses X in a message
        # without declaring it — the pre-amendment shared declaration table
        # suppressed the lenient #5 finding for block 2; per-block scoping
        # reports it (standalone: error, preflight: warning)
        text = (
            "@startuml d1\nactor X\nparticipant Y\nX -> Y: hi\n@enduml\n"
            "@startuml d2\nparticipant Z\nX -> Z: hi\n@enduml\n"
        )

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                findings = result.warnings if mode == MODE_PREFLIGHT else result.errors
                self.assertTrue(
                    any(finding.line == 8 and "undeclared participant 'X'" in finding.message for finding in findings),
                    findings,
                )
                self.assertEqual(len(findings), 1)

    def test_lines_between_blocks_carry_no_findings(self):
        # an 'alt' opened OUTSIDE any block (between the two diagrams) is not
        # part of any linting unit — no spurious "unclosed fragment at EOF"
        # finding attributed to it (the pre-amendment bug: the shared fragment
        # stack carried it to the file's EOF)
        text = (
            "@startuml d1\nparticipant A\nA -> A: x\n@enduml\n"
            "alt stray\n"
            "@startuml d2\nparticipant B\nB -> B: y\n@enduml\n"
        )

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertEqual(result.errors, [])
                self.assertEqual(result.warnings, [])


class TestPackageDataFiles(unittest.TestCase):
    """The packaged template/example must pass the checker in both modes."""

    def test_template_passes_both_modes_with_zero_errors(self):
        from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

        text = read_packaged_text("uc", "plantuml_template")

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"template errors in {mode}: {result.errors}")

    def test_example_passes_both_modes_with_zero_errors_and_zero_warnings(self):
        from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

        text = read_packaged_text("uc", "plantuml_example")

        for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
            with self.subTest(mode=mode):
                result = check_structure(text, mode)
                self.assertTrue(result.ok, f"example errors in {mode}: {result.errors}")
                self.assertEqual(result.warnings, [], f"example warnings in {mode}: {result.warnings}")

    def test_example_carries_no_unattributed_markers(self):
        from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

        text = read_packaged_text("uc", "plantuml_example")

        marked = [line for line in text.split("\n") if is_unattributed_marker(line)]
        self.assertEqual(marked, [])


class TestImportFree(unittest.TestCase):
    """ADR 7a626b12: no specmgr import anywhere in the plantuml package."""

    def test_no_specmgr_imports(self):
        package_dir = __import__("pathlib").Path(structure.__file__).parent
        for py_file in sorted(package_dir.glob("*.py")):
            content = py_file.read_text(encoding="utf-8")
            for line_number, line in enumerate(content.split("\n"), start=1):
                with self.subTest(file=py_file.name, line=line_number):
                    self.assertFalse(
                        line.strip().startswith(("from biz", "import biz")),
                        f"{py_file.name}:{line_number} imports specmgr: {line.strip()!r}",
                    )


if __name__ == "__main__":
    unittest.main()
