"""Tests for parse_uc (Task 1.3A)."""

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models.v1.parser import UcParseError, parse_uc

_EXAMPLE_PATH = Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-4-use-cases" / "uc_example.md"

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
