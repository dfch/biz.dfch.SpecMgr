"""Tests for the SubVariation Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import SubVariation


class TestSubVariation(unittest.TestCase):
    """Tests for the SubVariation Pydantic model."""

    def test_valid_subvariation_creation(self):
        """A valid sub-variation with step reference and variations must be created."""
        subvar = SubVariation(
            step_reference="1",
            variations=["Via phone", "Via email", "Via web"],
        )
        self.assertEqual(subvar.step_reference, "1")
        self.assertEqual(len(subvar.variations), 3)

    def test_step_reference_pattern_validation(self):
        """Step reference must match pattern 'NNN' (number only, no letters)."""
        # Valid references
        for ref in ["1", "10", "100"]:
            with self.subTest(ref=ref):
                subvar = SubVariation(
                    step_reference=ref,
                    variations=["Variation"],
                )
                self.assertEqual(subvar.step_reference, ref)

        # Invalid references (with letters)
        for ref in ["1a", "10b", "a", ""]:
            with self.subTest(ref=ref):
                with self.assertRaises(ValidationError):
                    SubVariation(
                        step_reference=ref,
                        variations=["Variation"],
                    )

    def test_variations_must_not_be_empty(self):
        """Variations list must have at least one item."""
        with self.assertRaises(ValidationError):
            SubVariation(
                step_reference="1",
                variations=[],
            )

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            SubVariation(
                step_reference="1",
                variations=["Variation"],
                extra="field",
            )


if __name__ == "__main__":
    unittest.main()
