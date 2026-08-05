"""Tests for the RelatedInformation Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import RelatedInformation


class TestRelatedInformation(unittest.TestCase):
    """Tests for the RelatedInformation Pydantic model."""

    def test_valid_related_information_creation(self):
        """A valid related information object must be created."""
        info = RelatedInformation(
            notes=["Note 1", "Note 2"],
            assumptions=["Assumption 1"],
        )
        self.assertEqual(len(info.notes), 2)
        self.assertEqual(len(info.assumptions), 1)

    def test_notes_can_be_none(self):
        """Notes can be None."""
        info = RelatedInformation(notes=None, assumptions=["Assumption 1"])
        self.assertIsNone(info.notes)
        self.assertEqual(len(info.assumptions), 1)

    def test_assumptions_can_be_none(self):
        """Assumptions can be None."""
        info = RelatedInformation(notes=["Note 1"], assumptions=None)
        self.assertEqual(len(info.notes), 1)
        self.assertIsNone(info.assumptions)

    def test_both_can_be_none(self):
        """Both notes and assumptions can be None."""
        info = RelatedInformation(notes=None, assumptions=None)
        self.assertIsNone(info.notes)
        self.assertIsNone(info.assumptions)

    def test_notes_can_be_empty_list(self):
        """Notes can be an empty list."""
        info = RelatedInformation(notes=[], assumptions=["Assumption 1"])
        self.assertEqual(len(info.notes), 0)

    def test_assumptions_can_be_empty_list(self):
        """Assumptions can be an empty list."""
        info = RelatedInformation(notes=["Note 1"], assumptions=[])
        self.assertEqual(len(info.assumptions), 0)

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            RelatedInformation(
                notes=["Note 1"],
                assumptions=["Assumption 1"],
                extra="field",
            )


if __name__ == "__main__":
    unittest.main()
