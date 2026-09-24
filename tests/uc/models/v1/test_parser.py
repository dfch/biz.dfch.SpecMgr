"""Tests for parse_uc (Task 1.3A)."""

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models.v1.parser import UcParseError, parse_uc

_EXAMPLE_PATH = (
    Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-4-use-cases" / "v1" / "uc_example-v1.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: uc-001
    version: 1.0.0
    status: draft
    created: 2026-08-05
    updated: 2026-08-05
    ---

    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request.

    ### Scope

    Company.

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in.
    2. Company ships goods.
    """
)


class TestParseUcExampleRoundTrip(unittest.TestCase):
    """Round-trip parsing of the full feature-plan example document."""

    def test_parses_full_example_document(self):
        text = _EXAMPLE_PATH.read_text()
        uc = parse_uc(text)

        self.assertEqual(uc.title, "Buy Goods")
        self.assertEqual(uc.frontmatter.id, "uc-001")
        self.assertEqual(uc.characteristic_information.level, "Summary")
        self.assertEqual(len(uc.characteristic_information.preconditions), 3)
        self.assertIsNotNone(uc.characteristic_information.related_use_cases)
        rel_uc = uc.characteristic_information.related_use_cases
        self.assertIsNotNone(rel_uc.subordinate)
        self.assertEqual(rel_uc.superordinate, "Manage customer relationship (UC-002)")
        self.assertEqual(len(rel_uc.subordinate), 3)

        self.assertEqual(len(uc.main_success_scenario.steps), 11)
        self.assertEqual(uc.main_success_scenario.steps[2].number, 3)
        self.assertIn("green screen", uc.main_success_scenario.steps[2].description)

        self.assertEqual(len(uc.extensions.items), 8)
        first_ext = uc.extensions.items[0]
        self.assertEqual(first_ext.step_reference, "3a")
        self.assertEqual([a.number for a in first_ext.actions], ["3a1", "3a2", "3a3"])
        self.assertIn("rarely happen", first_ext.actions[0].description)

        self.assertEqual(len(uc.sub_variations.items), 4)
        self.assertEqual(uc.sub_variations.items[0].step_reference, "1")

        self.assertEqual(len(uc.open_issues.items), 6)
        self.assertEqual(len(uc.related_information.notes), 4)
        self.assertEqual(len(uc.related_information.assumptions), 4)


class TestParseUcMinimalDocument(unittest.TestCase):
    """Parsing of a minimal document with only required sections."""

    def test_parses_minimal_document(self):
        uc = parse_uc(_MINIMAL_DOC)
        self.assertEqual(uc.title, "Buy Goods")
        self.assertEqual(len(uc.main_success_scenario.steps), 2)
        self.assertIsNone(uc.extensions)
        self.assertIsNone(uc.sub_variations)
        self.assertIsNone(uc.open_issues)
        self.assertIsNone(uc.related_information)
        self.assertIsNone(uc.characteristic_information.related_use_cases)


class TestParseUcStructuralErrors(unittest.TestCase):
    """Structural problems must raise UcParseError, not ValidationError."""

    def test_missing_h1_title_raises_parse_error(self):
        text = _MINIMAL_DOC.replace("# Buy Goods\n\n", "")
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_multiple_h1_headings_raises_parse_error(self):
        text = _MINIMAL_DOC.replace(
            "## Characteristic Information",
            "# Second Title\n\n## Characteristic Information",
        )
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_unrecognized_h2_heading_raises_parse_error(self):
        text = _MINIMAL_DOC + "\n## Not A Real Section\n\nSome text.\n"
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_duplicate_h2_heading_raises_parse_error(self):
        text = _MINIMAL_DOC + "\n## Main Success Scenario\n\n1. Duplicate step.\n"
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_unrecognized_h3_heading_under_characteristic_information_raises_parse_error(self):
        text = _MINIMAL_DOC.replace("### Trigger", "### Not A Real Field\n\nValue.\n\n### Trigger")
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_content_before_first_heading_raises_parse_error(self):
        text = _MINIMAL_DOC.replace("---\n\n# Buy Goods", "---\n\nStray text.\n\n# Buy Goods")
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_malformed_extension_heading_raises_parse_error(self):
        text = _MINIMAL_DOC + textwrap.dedent(
            """
            ## Extensions

            ### Not A Valid Extension Heading

            3a1. Some action.
            """
        )
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_malformed_sub_variation_heading_raises_parse_error(self):
        text = _MINIMAL_DOC + textwrap.dedent(
            """
            ## Sub-Variations

            ### Not A Valid Sub-Variation Heading

            - Some variation
            """
        )
        with self.assertRaises(UcParseError):
            parse_uc(text)

    def test_non_numbered_line_with_no_preceding_item_raises_parse_error(self):
        text = _MINIMAL_DOC.replace(
            "1. Buyer calls in.\n2. Company ships goods.\n",
            "Not a numbered item at all.\n",
        )
        with self.assertRaises(UcParseError):
            parse_uc(text)


_FRONTMATTER = "---\nid: uc-001\nversion: 1.0.0\nstatus: draft\ncreated: 2026-08-05\nupdated: 2026-08-05\n---\n\n"


def _doc(body: str) -> str:
    """Build a full use case document (frontmatter + body) for error-case tests."""
    result = _FRONTMATTER + body
    return result


def _expect_parse_error_without_title(
    test_case: "TestParseErrorMessagesOmitTitles", text: str, hidden_title: str, expected_message: str
) -> None:
    """Assert parse_uc raises UcParseError (unchanged type/raise condition) with the exact
    reworded message, which no longer contains the offending heading title."""
    sut = parse_uc

    with test_case.assertRaises(UcParseError) as ctx:
        sut(text)

    message = str(ctx.exception)
    test_case.assertNotIn(hidden_title, message)
    test_case.assertEqual(message, expected_message)


class TestParseErrorMessagesOmitTitles(unittest.TestCase):
    """feat-139 Task 6.7: the 13 reworded UcParseError sites no longer embed the heading title.

    One test per reworded call site: each builds a document that triggers
    exactly that site with a distinctive title and asserts the new message
    (a) no longer contains the title and (b) is the pinned reworded text --
    the exception's type (UcParseError) and raise condition are unchanged.
    The deprecated ADR domain's 9 title sites are an accepted residual gap
    (not tested here, not reworded); the path-embedding sites are
    scrub-covered and deliberately not reworded.
    """

    def test_the_second_h1_title_is_omitted_from_the_multiple_h1_message(self):
        hidden = "Secret Title Alpha"
        text = _doc(
            f"# Buy Goods\n\n# {hidden}\n\n## Characteristic Information\n\n### Goal in Context\n\nBuyer issues request.\n"
        )

        _expect_parse_error_without_title(self, text, hidden, "more than one top-level (H1) heading found")

    def test_the_h4_title_under_h1_is_omitted_from_the_level_message(self):
        hidden = "Secret Title Bravo"
        text = _doc(f"# Buy Goods\n\n#### {hidden}\n\nSome text.\n")

        _expect_parse_error_without_title(self, text, hidden, "heading level H4 is not part of the use case schema")

    def test_the_unrecognized_h2_title_is_omitted_from_the_unrecognized_h2_message(self):
        hidden = "Secret Title Charlie"
        text = _doc(f"# Buy Goods\n\n## {hidden}\n\nSome text.\n")

        _expect_parse_error_without_title(self, text, hidden, "unrecognized H2 heading")

    def test_the_h4_title_under_characteristic_information_is_omitted_from_the_level_message(self):
        hidden = "Secret Title Delta"
        text = _doc(f"# Buy Goods\n\n## Characteristic Information\n\n#### {hidden}\n\nSome text.\n")

        _expect_parse_error_without_title(self, text, hidden, "heading level H4 is not part of the use case schema")

    def test_the_unrecognized_h3_title_under_characteristic_information_is_omitted(self):
        hidden = "Secret Title Echo"
        text = _doc(f"# Buy Goods\n\n## Characteristic Information\n\n### {hidden}\n\nValue.\n")

        _expect_parse_error_without_title(
            self, text, hidden, "unrecognized H3 heading under Characteristic Information"
        )

    def test_the_duplicate_h3_title_under_characteristic_information_is_omitted(self):
        # The duplicated heading is a fixed schema title ("Scope") -- the
        # reworded message omits it just like a document-specific title.
        hidden = "Scope"
        text = _doc("# Buy Goods\n\n## Characteristic Information\n\n### Scope\n\nA.\n\n### Scope\n\nB.\n")

        _expect_parse_error_without_title(self, text, hidden, "duplicate H3 heading")

    def test_the_h4_title_under_related_information_is_omitted_from_the_level_message(self):
        hidden = "Secret Title Foxtrot"
        text = _doc(f"# Buy Goods\n\n## Related Information\n\n#### {hidden}\n\nSome text.\n")

        _expect_parse_error_without_title(self, text, hidden, "heading level H4 is not part of the use case schema")

    def test_the_unrecognized_h3_title_under_related_information_is_omitted(self):
        hidden = "Secret Title Golf"
        text = _doc(f"# Buy Goods\n\n## Related Information\n\n### {hidden}\n\n- x\n")

        _expect_parse_error_without_title(self, text, hidden, "unrecognized H3 heading under Related Information")

    def test_the_duplicate_h3_title_under_related_information_is_omitted(self):
        hidden = "Notes"
        text = _doc("# Buy Goods\n\n## Related Information\n\n### Notes\n\n- a\n\n### Notes\n\n- b\n")

        _expect_parse_error_without_title(self, text, hidden, "duplicate H3 heading")

    def test_the_h4_title_under_extensions_is_omitted_from_the_level_message(self):
        hidden = "Secret Title Hotel"
        text = _doc(f"# Buy Goods\n\n## Extensions\n\n#### {hidden}\n\nSome text.\n")

        _expect_parse_error_without_title(self, text, hidden, "heading level H4 is not part of the use case schema")

    def test_the_unrecognized_extension_heading_title_is_omitted(self):
        hidden = "Secret Title India"
        text = _doc(f"# Buy Goods\n\n## Extensions\n\n### {hidden}\n\n3a1. Some action.\n")

        _expect_parse_error_without_title(
            self, text, hidden, "unrecognized Extension heading (expected '{stepRef}. {condition}')"
        )

    def test_the_h4_title_under_sub_variations_is_omitted_from_the_level_message(self):
        hidden = "Secret Title Juliet"
        text = _doc(f"# Buy Goods\n\n## Sub-Variations\n\n#### {hidden}\n\nSome text.\n")

        _expect_parse_error_without_title(self, text, hidden, "heading level H4 is not part of the use case schema")

    def test_the_unrecognized_sub_variation_heading_title_is_omitted(self):
        hidden = "Secret Title Kilo"
        text = _doc(f"# Buy Goods\n\n## Sub-Variations\n\n### {hidden}\n\n- Some variation\n")

        _expect_parse_error_without_title(
            self, text, hidden, "unrecognized Sub-Variation heading (expected 'Step {N}: {label}')"
        )


class TestParseUcValidationErrors(unittest.TestCase):
    """Structurally-sound documents with invalid field values/invariants raise ValidationError."""

    def test_non_contiguous_steps_raise_validation_error(self):
        text = _MINIMAL_DOC.replace(
            "1. Buyer calls in.\n2. Company ships goods.", "1. Buyer calls in.\n3. Skipped step."
        )
        with self.assertRaises(ValidationError):
            parse_uc(text)

    def test_extension_step_reference_not_resolving_raises_validation_error(self):
        text = _MINIMAL_DOC + textwrap.dedent(
            """
            ## Extensions

            ### 9a. Non-existent step

            9a1. Some action.
            """
        )
        with self.assertRaises(ValidationError):
            parse_uc(text)

    def test_extension_action_wrong_prefix_raises_validation_error(self):
        text = _MINIMAL_DOC + textwrap.dedent(
            """
            ## Extensions

            ### 1a. Something goes wrong

            2a1. Mismatched prefix action.
            """
        )
        with self.assertRaises(ValidationError):
            parse_uc(text)


if __name__ == "__main__":
    unittest.main()
