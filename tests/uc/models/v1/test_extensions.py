"""Tests for the Extensions Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import Extension, ExtensionAction, Extensions


class TestExtensions(unittest.TestCase):
    """Tests for the Extensions Pydantic model."""

    def test_valid_extensions_creation(self):
        """A valid extensions object with items must be created."""
        extensions = Extensions(
            items=[
                Extension(
                    step_reference="3a",
                    condition="If payment fails",
                    actions=[ExtensionAction(number="3a1", description="Retry")],
                ),
                Extension(
                    step_reference="4b",
                    condition="If inventory low",
                    actions=[ExtensionAction(number="4b1", description="Backorder")],
                ),
            ]
        )
        self.assertEqual(len(extensions.items), 2)

    def test_items_can_be_empty_list(self):
        """Items list can be empty (no extensions)."""
        extensions = Extensions(items=[])
        self.assertEqual(len(extensions.items), 0)

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            Extensions(
                items=[],
                extra="field",
            )


if __name__ == "__main__":
    unittest.main()
