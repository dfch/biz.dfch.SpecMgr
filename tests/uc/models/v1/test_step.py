"""Tests for the Step Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import Step


class TestStep(unittest.TestCase):
    """Tests for the Step Pydantic model."""

    def test_valid_step_creation(self):
        """A valid step with number and description must be created."""
        step = Step(number=1, description="Buyer issues request")
        self.assertEqual(step.number, 1)
        self.assertEqual(step.description, "Buyer issues request")

    def test_step_number_must_be_positive(self):
        """Step number must be >= 1."""
        # Valid numbers
        for num in [1, 2, 100]:
            with self.subTest(number=num):
                step = Step(number=num, description="Description")
                self.assertEqual(step.number, num)

        # Invalid numbers
        for num in [0, -1]:
            with self.subTest(number=num):
                with self.assertRaises(ValidationError):
                    Step(number=num, description="Description")

    def test_description_must_not_be_empty(self):
        """Description must be non-empty."""
        with self.assertRaises(ValidationError):
            Step(number=1, description="")

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            Step(number=1, description="Description", extra="field")


if __name__ == "__main__":
    unittest.main()
