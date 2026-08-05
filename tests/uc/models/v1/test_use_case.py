"""Tests for the UseCase root Pydantic model."""

import unittest
from datetime import date

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import (
    CharacteristicInformation,
    Extension,
    ExtensionAction,
    Extensions,
    MainSuccessScenario,
    OpenIssues,
    RelatedInformation,
    Step,
    SubVariation,
    SubVariations,
    UseCase,
    UseCaseFrontmatter,
)


class TestUseCase(unittest.TestCase):
    """Tests for the UseCase Pydantic model."""

    def _create_minimal_usecase(self):
        """Helper to create a minimal valid use case."""
        return UseCase(
            frontmatter=UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="draft",
                created=date(2026, 8, 5),
                updated=date(2026, 8, 5),
            ),
            title="Buy Goods",
            characteristic_information=CharacteristicInformation(
                goal_in_context="Buyer issues request directly to our company",
                scope="Company (the system being designed as a black box)",
                level="Summary",
                preconditions=["We know Buyer"],
                success_end_condition=["Buyer has goods"],
                primary_actor="Buyer",
                trigger="Buyer issues request",
            ),
            main_success_scenario=MainSuccessScenario(
                steps=[
                    Step(number=1, description="Buyer issues request"),
                    Step(number=2, description="System processes request"),
                ]
            ),
        )

    def test_valid_minimal_usecase_creation(self):
        """A valid use case with only required fields must be created."""
        uc = self._create_minimal_usecase()
        self.assertEqual(uc.title, "Buy Goods")
        self.assertEqual(uc.frontmatter.id, "uc-001")
        self.assertEqual(len(uc.main_success_scenario.steps), 2)

    def test_title_must_not_be_empty(self):
        """Title must be non-empty."""
        with self.assertRaises(ValidationError):
            UseCase(
                frontmatter=UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                ),
                title="",  # Empty title not allowed
                characteristic_information=CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level="Summary",
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                ),
                main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step")]),
            )

    def test_title_max_length_validation(self):
        """Title must not exceed 200 characters."""
        # Valid title (200 chars)
        valid_title = "A" * 200
        uc = UseCase(
            frontmatter=UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="draft",
                created=date(2026, 8, 5),
                updated=date(2026, 8, 5),
            ),
            title=valid_title,
            characteristic_information=CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Summary",
                preconditions=["Precondition"],
                success_end_condition=["Success"],
                primary_actor="Actor",
                trigger="Trigger",
            ),
            main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step")]),
        )
        self.assertEqual(len(uc.title), 200)

        # Invalid title (201 chars)
        invalid_title = "A" * 201
        with self.assertRaises(ValidationError):
            UseCase(
                frontmatter=UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                ),
                title=invalid_title,
                characteristic_information=CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level="Summary",
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                ),
                main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step")]),
            )

    def test_optional_sections_can_be_none(self):
        """Optional sections (extensions, sub_variations, open_issues, related_information) can be None."""
        uc = self._create_minimal_usecase()
        self.assertIsNone(uc.extensions)
        self.assertIsNone(uc.sub_variations)
        self.assertIsNone(uc.open_issues)
        self.assertIsNone(uc.related_information)

    def test_optional_sections_can_have_values(self):
        """Optional sections can be populated with values."""
        uc = UseCase(
            frontmatter=UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="draft",
                created=date(2026, 8, 5),
                updated=date(2026, 8, 5),
            ),
            title="Buy Goods",
            characteristic_information=CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Summary",
                preconditions=["Precondition"],
                success_end_condition=["Success"],
                primary_actor="Actor",
                trigger="Trigger",
            ),
            main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step")]),
            open_issues=OpenIssues(items=["Issue 1", "Issue 2"]),
            related_information=RelatedInformation(
                notes=["Note 1"],
                assumptions=["Assumption 1"],
            ),
        )
        self.assertIsNotNone(uc.open_issues)
        self.assertEqual(len(uc.open_issues.items), 2)
        self.assertIsNotNone(uc.related_information)
        self.assertEqual(len(uc.related_information.notes), 1)

    def test_all_required_sections_must_be_present(self):
        """All required sections must be provided."""
        required_sections = [
            "frontmatter",
            "title",
            "characteristic_information",
            "main_success_scenario",
        ]
        for section in required_sections:
            with self.subTest(section=section):
                uc_dict = {
                    "frontmatter": UseCaseFrontmatter(
                        id="uc-001",
                        version="1.0.0",
                        status="draft",
                        created=date(2026, 8, 5),
                        updated=date(2026, 8, 5),
                    ),
                    "title": "Buy Goods",
                    "characteristic_information": CharacteristicInformation(
                        goal_in_context="Goal",
                        scope="Scope",
                        level="Summary",
                        preconditions=["Precondition"],
                        success_end_condition=["Success"],
                        primary_actor="Actor",
                        trigger="Trigger",
                    ),
                    "main_success_scenario": MainSuccessScenario(steps=[Step(number=1, description="Step")]),
                }
                del uc_dict[section]
                with self.assertRaises(ValidationError):
                    UseCase(**uc_dict)

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            UseCase(
                frontmatter=UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                ),
                title="Buy Goods",
                characteristic_information=CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level="Summary",
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                ),
                main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step")]),
                extra_field="should fail",
            )

    def test_extension_step_reference_must_resolve_to_existing_step(self):
        """An extension referencing a non-existent main scenario step must be rejected."""
        with self.assertRaises(ValidationError):
            UseCase(
                frontmatter=UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                ),
                title="Buy Goods",
                characteristic_information=CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level="Summary",
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                ),
                main_success_scenario=MainSuccessScenario(
                    steps=[Step(number=1, description="Step 1"), Step(number=2, description="Step 2")]
                ),
                extensions=Extensions(
                    items=[
                        Extension(
                            step_reference="5a",  # step 5 does not exist
                            condition="Condition",
                            actions=[ExtensionAction(number="5a1", description="Action")],
                        )
                    ]
                ),
            )

    def test_extension_step_references_must_be_unique(self):
        """Duplicate step_reference values across extensions must be rejected."""
        with self.assertRaises(ValidationError):
            UseCase(
                frontmatter=UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                ),
                title="Buy Goods",
                characteristic_information=CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level="Summary",
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                ),
                main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step 1")]),
                extensions=Extensions(
                    items=[
                        Extension(
                            step_reference="1a",
                            condition="Condition A",
                            actions=[ExtensionAction(number="1a1", description="Action")],
                        ),
                        Extension(
                            step_reference="1a",
                            condition="Condition B",
                            actions=[ExtensionAction(number="1a1", description="Action")],
                        ),
                    ]
                ),
            )

    def test_sub_variation_step_reference_must_resolve_to_existing_step(self):
        """A sub-variation referencing a non-existent main scenario step must be rejected."""
        with self.assertRaises(ValidationError):
            UseCase(
                frontmatter=UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                ),
                title="Buy Goods",
                characteristic_information=CharacteristicInformation(
                    goal_in_context="Goal",
                    scope="Scope",
                    level="Summary",
                    preconditions=["Precondition"],
                    success_end_condition=["Success"],
                    primary_actor="Actor",
                    trigger="Trigger",
                ),
                main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Step 1")]),
                sub_variations=SubVariations(
                    items=[SubVariation(step_reference="7", variations=["Variation"])]  # step 7 does not exist
                ),
            )

    def test_valid_extensions_and_sub_variations_resolve_correctly(self):
        """Extensions/sub-variations with valid, resolvable, unique step references must succeed."""
        uc = UseCase(
            frontmatter=UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="draft",
                created=date(2026, 8, 5),
                updated=date(2026, 8, 5),
            ),
            title="Buy Goods",
            characteristic_information=CharacteristicInformation(
                goal_in_context="Goal",
                scope="Scope",
                level="Summary",
                preconditions=["Precondition"],
                success_end_condition=["Success"],
                primary_actor="Actor",
                trigger="Trigger",
            ),
            main_success_scenario=MainSuccessScenario(
                steps=[Step(number=1, description="Step 1"), Step(number=2, description="Step 2")]
            ),
            extensions=Extensions(
                items=[
                    Extension(
                        step_reference="1a",
                        condition="Condition",
                        actions=[ExtensionAction(number="1a1", description="Action")],
                    )
                ]
            ),
            sub_variations=SubVariations(items=[SubVariation(step_reference="2", variations=["Variation"])]),
        )
        self.assertEqual(len(uc.extensions.items), 1)
        self.assertEqual(len(uc.sub_variations.items), 1)


if __name__ == "__main__":
    unittest.main()
