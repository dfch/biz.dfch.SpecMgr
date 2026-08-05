"""Pydantic model for the complete Use Case document."""

from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .characteristic_information import CharacteristicInformation
from .extensions import Extensions
from .main_success_scenario import MainSuccessScenario
from .open_issues import OpenIssues
from .related_information import RelatedInformation
from .sub_variations import SubVariations
from .use_case_frontmatter import UseCaseFrontmatter


class UseCase(BaseModel):
    """A complete use case document based on Alistair Cockburn's template.

    This model represents a use case with YAML frontmatter and Markdown content sections.
    All required fields must be present; optional fields may be None.

    Attributes:
        frontmatter: YAML frontmatter metadata
        title: Use case name (from H1 heading, single line)
        characteristic_information: All metadata and context about the use case
        main_success_scenario: The happy path: steps from trigger to goal completion
        extensions: Alternative flows that still result in success
        sub_variations: Different technologies or methods for accomplishing steps
        open_issues: Questions and decisions awaiting resolution
        related_information: Additional context, notes, and assumptions
    """

    frontmatter: UseCaseFrontmatter = Field(..., description="YAML frontmatter metadata")
    title: str = Field(..., min_length=1, max_length=200, description="Use case name (from H1 heading)")
    characteristic_information: CharacteristicInformation = Field(
        ..., description="All metadata and context about the use case"
    )
    main_success_scenario: MainSuccessScenario = Field(
        ..., description="The happy path: steps from trigger to goal completion"
    )
    extensions: Optional[Extensions] = Field(None, description="Alternative flows that still result in success")
    sub_variations: Optional[SubVariations] = Field(
        None, description="Different technologies or methods for accomplishing steps"
    )
    open_issues: Optional[OpenIssues] = Field(None, description="Questions and decisions awaiting resolution")
    related_information: Optional[RelatedInformation] = Field(
        None, description="Additional context, notes, and assumptions"
    )

    @model_validator(mode="after")
    def validate_step_references_resolve_and_are_unique(self) -> "UseCase":
        """Extensions/sub_variations step_reference must resolve to a real step, with no duplicates.

        Neither JSON Schema (uc_schema.json) nor a single model's own fields can express this:
        it requires cross-checking ``Extension.step_reference``/``SubVariation.step_reference``
        against the sibling ``main_success_scenario.steps`` collection, and detecting duplicate
        references within each of ``extensions``/``sub_variations``. Unlike ADR's analogous
        Considered-Options/Option-section gap (deliberately left unenforced, per
        doc/adr-tool-plan.md §7), this check is explicitly in scope here (Task 1.3B).
        """
        step_numbers = {step.number for step in self.main_success_scenario.steps}

        if self.extensions is not None:
            _validate_unique_and_resolvable(
                references=[item.step_reference for item in self.extensions.items],
                step_numbers=step_numbers,
                section="extensions",
            )

        if self.sub_variations is not None:
            _validate_unique_and_resolvable(
                references=[item.step_reference for item in self.sub_variations.items],
                step_numbers=step_numbers,
                section="sub_variations",
            )

        return self

    model_config = {"extra": "forbid"}


def _validate_unique_and_resolvable(references: list[str], step_numbers: set[int], section: str) -> None:
    """Shared helper: every ``step_reference`` in ``references`` must resolve to an existing step
    number (its leading digits) and must not appear more than once within ``section``."""
    seen: set[str] = set()
    for reference in references:
        if reference in seen:
            raise ValueError(f"{section} has a duplicate step_reference {reference!r}")
        seen.add(reference)

        leading_digits = "".join(ch for ch in reference if ch.isdigit())
        if not leading_digits or int(leading_digits) not in step_numbers:
            raise ValueError(
                f"{section} step_reference {reference!r} does not resolve to any "
                f"main_success_scenario step number in {sorted(step_numbers)}"
            )
