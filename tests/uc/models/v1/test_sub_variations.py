"""Tests for the SubVariations Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import SubVariation, SubVariations


class TestSubVariations(unittest.TestCase):
    """Tests for the SubVariations Pydantic model."""

    def test_valid_subvariations_creation(self):
        """A valid sub-variations object with items must be created."""
        subvars = SubVariations(
            items=[
                SubVariation(step_reference="1", variations=["Via phone", "Via email"]),
                SubVariation(step_reference="7", variations=["Option A", "Option B"]),
            ]
        )
        self.assertEqual(len(subvars.items), 2)

    def test_items_can_be_empty_list(self):
        """Items list can be empty (no sub-variations)."""
        subvars = SubVariations(items=[])
        self.assertEqual(len(subvars.items), 0)

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            SubVariations(
                items=[],
                extra="field",
            )


if __name__ == "__main__":
    unittest.main()
