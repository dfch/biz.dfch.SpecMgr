"""Tests for the ExtensionAction Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import ExtensionAction


class TestExtensionAction(unittest.TestCase):
    """Tests for the ExtensionAction Pydantic model."""

    def test_valid_extension_action_creation(self):
        """A valid extension action with compound number and description must be created."""
        action = ExtensionAction(number="3a1", description="Company informs buyer of out-of-stock items.")
        self.assertEqual(action.number, "3a1")
        self.assertEqual(action.description, "Company informs buyer of out-of-stock items.")

    def test_number_pattern_validation(self):
        """Number must match the compound pattern 'NNN[a]NNN' (digits, optional letter, digits)."""
        for number in ["3a1", "10b2", "1a1", "100z9"]:
            with self.subTest(number=number):
                action = ExtensionAction(number=number, description="Action")
                self.assertEqual(action.number, number)

        for number in ["a1", "3a", "3", "3A1", "3a-1", ""]:
            with self.subTest(number=number):
                with self.assertRaises(ValidationError):
                    ExtensionAction(number=number, description="Action")

    def test_description_must_not_be_empty(self):
        """Description must be non-empty."""
        with self.assertRaises(ValidationError):
            ExtensionAction(number="3a1", description="")

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            ExtensionAction(number="3a1", description="Action", extra="field")


if __name__ == "__main__":
    unittest.main()
