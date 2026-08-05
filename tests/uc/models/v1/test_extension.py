"""Tests for the Extension Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import Extension, ExtensionAction


class TestExtension(unittest.TestCase):
    """Tests for the Extension Pydantic model."""

    def test_valid_extension_creation(self):
        """A valid extension with step reference, condition, and actions must be created."""
        ext = Extension(
            step_reference="3a",
            condition="If payment fails",
            actions=[
                ExtensionAction(number="3a1", description="Retry payment"),
                ExtensionAction(number="3a2", description="Notify customer"),
            ],
        )
        self.assertEqual(ext.step_reference, "3a")
        self.assertEqual(ext.condition, "If payment fails")
        self.assertEqual(len(ext.actions), 2)

    def test_step_reference_pattern_validation(self):
        """Step reference must match pattern 'NNN' or 'NNNa' (number with optional letter)."""
        # Valid references
        for ref in ["1", "10", "3a", "4b", "100z"]:
            with self.subTest(ref=ref):
                ext = Extension(
                    step_reference=ref,
                    condition="Condition",
                    actions=[ExtensionAction(number=f"{ref}1", description="Action")],
                )
                self.assertEqual(ext.step_reference, ref)

        # Invalid references
        for ref in ["a", "1a2", "1A", "1-a", ""]:
            with self.subTest(ref=ref):
                with self.assertRaises(ValidationError):
                    Extension(
                        step_reference=ref,
                        condition="Condition",
                        actions=[ExtensionAction(number="1a1", description="Action")],
                    )

    def test_condition_must_not_be_empty(self):
        """Condition must be non-empty."""
        with self.assertRaises(ValidationError):
            Extension(
                step_reference="3a",
                condition="",
                actions=[ExtensionAction(number="3a1", description="Action")],
            )

    def test_actions_must_not_be_empty(self):
        """Actions list must have at least one item."""
        with self.assertRaises(ValidationError):
            Extension(
                step_reference="3a",
                condition="Condition",
                actions=[],
            )

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            Extension(
                step_reference="3a",
                condition="Condition",
                actions=[ExtensionAction(number="3a1", description="Action")],
                extra="field",
            )

    def test_actions_must_be_numbered_sequentially(self):
        """Action numbers must be '{step_reference}1', '{step_reference}2', ... in order."""
        ext = Extension(
            step_reference="3a",
            condition="Condition",
            actions=[
                ExtensionAction(number="3a1", description="First"),
                ExtensionAction(number="3a2", description="Second"),
                ExtensionAction(number="3a3", description="Third"),
            ],
        )
        self.assertEqual(len(ext.actions), 3)

    def test_actions_must_match_step_reference_prefix(self):
        """An action number whose prefix doesn't match the extension's step_reference must be rejected."""
        with self.assertRaises(ValidationError):
            Extension(
                step_reference="3a",
                condition="Condition",
                actions=[ExtensionAction(number="4a1", description="Wrong prefix")],
            )

    def test_actions_must_have_no_gaps(self):
        """Action numbers must not skip a sequence number."""
        with self.assertRaises(ValidationError):
            Extension(
                step_reference="3a",
                condition="Condition",
                actions=[
                    ExtensionAction(number="3a1", description="First"),
                    ExtensionAction(number="3a3", description="Skipped second"),
                ],
            )

    def test_actions_must_not_be_out_of_order(self):
        """Action numbers must be in ascending order."""
        with self.assertRaises(ValidationError):
            Extension(
                step_reference="3a",
                condition="Condition",
                actions=[
                    ExtensionAction(number="3a2", description="Second"),
                    ExtensionAction(number="3a1", description="First"),
                ],
            )


if __name__ == "__main__":
    unittest.main()
