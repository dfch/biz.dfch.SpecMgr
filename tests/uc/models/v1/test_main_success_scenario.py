"""Tests for the MainSuccessScenario Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import MainSuccessScenario, Step


class TestMainSuccessScenario(unittest.TestCase):
    """Tests for the MainSuccessScenario Pydantic model."""

    def test_valid_scenario_creation(self):
        """A valid scenario with steps must be created."""
        scenario = MainSuccessScenario(
            steps=[
                Step(number=1, description="Step 1"),
                Step(number=2, description="Step 2"),
            ]
        )
        self.assertEqual(len(scenario.steps), 2)
        self.assertEqual(scenario.steps[0].number, 1)

    def test_steps_must_not_be_empty(self):
        """Steps list must have at least one item."""
        with self.assertRaises(ValidationError):
            MainSuccessScenario(steps=[])

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            MainSuccessScenario(
                steps=[Step(number=1, description="Step 1")],
                extra="field",
            )

    def test_steps_must_start_at_one(self):
        """Steps must start numbering at 1, not some other number."""
        with self.assertRaises(ValidationError):
            MainSuccessScenario(
                steps=[
                    Step(number=2, description="Step 2"),
                    Step(number=3, description="Step 3"),
                ]
            )

    def test_steps_must_have_no_gaps(self):
        """Steps must be numbered contiguously, without skipping numbers."""
        with self.assertRaises(ValidationError):
            MainSuccessScenario(
                steps=[
                    Step(number=1, description="Step 1"),
                    Step(number=3, description="Step 3"),
                ]
            )

    def test_steps_must_not_be_out_of_order(self):
        """Steps must be in ascending order, even if numbers themselves are contiguous."""
        with self.assertRaises(ValidationError):
            MainSuccessScenario(
                steps=[
                    Step(number=2, description="Step 2"),
                    Step(number=1, description="Step 1"),
                ]
            )

    def test_steps_must_not_have_duplicates(self):
        """Steps must not repeat the same number."""
        with self.assertRaises(ValidationError):
            MainSuccessScenario(
                steps=[
                    Step(number=1, description="Step 1"),
                    Step(number=1, description="Step 1 again"),
                ]
            )


if __name__ == "__main__":
    unittest.main()
