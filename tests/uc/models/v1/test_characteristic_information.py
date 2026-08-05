"""Tests for the CharacteristicInformation Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import CharacteristicInformation, RelatedUseCases


class TestCharacteristicInformation(unittest.TestCase):
    """Tests for the CharacteristicInformation Pydantic model."""

    def test_valid_characteristic_information_creation(self):
        """A valid characteristic information with all required fields must be created."""
        ci = CharacteristicInformation(
            goal_in_context="Buyer issues request directly to our company",
            scope="Company (the system being designed as a black box)",
            level="Summary",
            preconditions=["We know Buyer", "We know Buyer's address"],
            success_end_condition=["Buyer has goods", "We have money for the goods"],
            primary_actor="Buyer",
            trigger="Buyer issues request",
        )
        self.assertEqual(ci.goal_in_context, "Buyer issues request directly to our company")
        self.assertEqual(ci.scope, "Company (the system being designed as a black box)")
        self.assertEqual(ci.level, "Summary")
        self.assertEqual(len(ci.preconditions), 2)
        self.assertEqual(len(ci.success_end_condition), 2)

    def test_level_enum_validation(self):
        """Level must be one of the allowed enum values."""
        # Valid levels
        for valid_level in ["Summary", "Primary task", "Subfunction"]:
            with self.subTest(level=valid_level):
                ci = CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level=valid_level,
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                )
                self.assertEqual(ci.level, valid_level)

        # Invalid level
        with self.assertRaises(ValidationError):
            CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Invalid Level",
                preconditions=["Precondition"],
                success_end_condition=["Success"],
                primary_actor="Actor",
                trigger="Trigger",
            )

    def test_preconditions_must_not_be_empty(self):
        """Preconditions list must have at least one item."""
        with self.assertRaises(ValidationError):
            CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Summary",
                preconditions=[],  # Empty list not allowed
                success_end_condition=["Success"],
                primary_actor="Actor",
                trigger="Trigger",
            )

    def test_success_end_condition_must_not_be_empty(self):
        """Success end condition list must have at least one item."""
        with self.assertRaises(ValidationError):
            CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Summary",
                preconditions=["Precondition"],
                success_end_condition=[],  # Empty list not allowed
                primary_actor="Actor",
                trigger="Trigger",
            )

    def test_optional_fields_can_be_none(self):
        """Optional fields like failed_end_condition, secondary_actors, etc. can be None."""
        ci = CharacteristicInformation(
            goal_in_context="Goal",
            scope="Scope",
            level="Summary",
            preconditions=["Precondition"],
            success_end_condition=["Success"],
            primary_actor="Actor",
            trigger="Trigger",
            failed_end_condition=None,
            secondary_actors=None,
            frequency=None,
            priority=None,
            performance_target=None,
            channels_to_primary_actor=None,
            channels_to_secondary_actors=None,
            related_use_cases=None,
        )
        self.assertIsNone(ci.failed_end_condition)
        self.assertIsNone(ci.secondary_actors)

    def test_optional_fields_can_have_values(self):
        """Optional fields can be populated with values."""
        ci = CharacteristicInformation(
            goal_in_context="Goal",
            scope="Scope",
            level="Summary",
            preconditions=["Precondition"],
            success_end_condition=["Success"],
            primary_actor="Actor",
            trigger="Trigger",
            failed_end_condition=["Failure condition"],
            secondary_actors=["Credit card company"],
            frequency="200 per day",
            priority="High",
            performance_target="5 minutes",
            channels_to_primary_actor=["interactive"],
            channels_to_secondary_actors=["database"],
        )
        self.assertEqual(ci.failed_end_condition, ["Failure condition"])
        self.assertEqual(ci.secondary_actors, ["Credit card company"])
        self.assertEqual(ci.frequency, "200 per day")
        self.assertEqual(ci.priority, "High")

    def test_related_use_cases_optional(self):
        """Related use cases can be provided as a nested object."""
        related = RelatedUseCases(
            superordinate="Parent Use Case",
            subordinate=["Child Use Case 1", "Child Use Case 2"],
        )
        ci = CharacteristicInformation(
            goal_in_context="Goal",
            scope="Scope",
            level="Summary",
            preconditions=["Precondition"],
            success_end_condition=["Success"],
            primary_actor="Actor",
            trigger="Trigger",
            related_use_cases=related,
        )
        self.assertIsNotNone(ci.related_use_cases)
        self.assertEqual(ci.related_use_cases.superordinate, "Parent Use Case")
        self.assertEqual(len(ci.related_use_cases.subordinate), 2)

    def test_all_required_fields_must_be_present(self):
        """All required fields must be provided."""
        required_fields = [
            "goal_in_context",
            "scope",
            "level",
            "preconditions",
            "success_end_condition",
            "primary_actor",
            "trigger",
        ]
        for field in required_fields:
            with self.subTest(field=field):
                kwargs = {
                    "goal_in_context": "Goal",
                    "scope": "Scope",
                    "level": "Summary",
                    "preconditions": ["Precondition"],
                    "success_end_condition": ["Success"],
                    "primary_actor": "Actor",
                    "trigger": "Trigger",
                }
                del kwargs[field]
                with self.assertRaises(ValidationError):
                    CharacteristicInformation(**kwargs)

    def test_no_extra_fields_allowed(self):
        """Extra fields not in the schema must be rejected."""
        with self.assertRaises(ValidationError):
            CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Summary",
                preconditions=["Precondition"],
                success_end_condition=["Success"],
                primary_actor="Actor",
                trigger="Trigger",
                extra_field="should fail",
            )


if __name__ == "__main__":
    unittest.main()
