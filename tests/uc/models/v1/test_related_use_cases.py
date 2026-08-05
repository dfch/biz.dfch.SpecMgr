"""Tests for the RelatedUseCases Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import RelatedUseCases


class TestRelatedUseCases(unittest.TestCase):
    """Tests for the RelatedUseCases Pydantic model."""

    def test_valid_related_use_cases_creation(self):
        """A valid related use cases object must be created."""
        related = RelatedUseCases(
            superordinate="Parent Use Case",
            subordinate=["Child Use Case 1", "Child Use Case 2"],
        )
        self.assertEqual(related.superordinate, "Parent Use Case")
        self.assertEqual(len(related.subordinate), 2)

    def test_superordinate_can_be_none(self):
        """Superordinate can be None."""
        related = RelatedUseCases(superordinate=None, subordinate=["Child"])
        self.assertIsNone(related.superordinate)

    def test_subordinate_can_be_none(self):
        """Subordinate can be None."""
        related = RelatedUseCases(superordinate="Parent", subordinate=None)
        self.assertIsNone(related.subordinate)

    def test_both_can_be_none(self):
        """Both fields can be None."""
        related = RelatedUseCases(superordinate=None, subordinate=None)
        self.assertIsNone(related.superordinate)
        self.assertIsNone(related.subordinate)

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            RelatedUseCases(
                superordinate="Parent",
                subordinate=["Child"],
                extra="field",
            )


if __name__ == "__main__":
    unittest.main()
