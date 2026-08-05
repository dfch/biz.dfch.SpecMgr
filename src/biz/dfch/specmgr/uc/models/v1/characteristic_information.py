"""Pydantic model for the Use Case Characteristic Information section."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .related_use_cases import RelatedUseCases


class CharacteristicInformation(BaseModel):
    """All metadata and context about the use case.

    Attributes:
        goal_in_context: Longer statement of the goal in context
        scope: What system is being considered as a black box under design
        level: Scope level (Summary, Primary task, Subfunction)
        preconditions: What we expect is already the state of the world
        success_end_condition: The state of the world upon successful completion
        failed_end_condition: The state of the world if goal is abandoned
        primary_actor: A role name for the primary actor or description
        secondary_actors: List of other systems or actors needed
        trigger: The action upon the system that starts the use case
        frequency: How often it is expected to happen
        priority: How critical to the system/organization
        performance_target: The amount of time this use case should take
        channels_to_primary_actor: How the primary actor interacts with the system
        channels_to_secondary_actors: How secondary actors interact with the system
        related_use_cases: Links to parent and child use cases
    """

    goal_in_context: str = Field(..., description="Longer statement of the goal in context")
    scope: str = Field(..., description="What system is being considered as a black box")
    level: str = Field(
        ...,
        description="Scope level of the use case",
        json_schema_extra={"enum": ["Summary", "Primary task", "Subfunction"]},
    )
    preconditions: list[str] = Field(..., min_length=1, description="What we expect is already the state of the world")
    success_end_condition: list[str] = Field(..., min_length=1, description="The state of the world upon success")
    failed_end_condition: Optional[list[str]] = Field(None, description="The state of the world if goal is abandoned")
    primary_actor: str = Field(..., description="A role name for the primary actor or description")
    secondary_actors: Optional[list[str]] = Field(None, description="List of other systems or actors needed")
    trigger: str = Field(..., description="The action upon the system that starts the use case")
    frequency: Optional[str] = Field(None, description="How often it is expected to happen")
    priority: Optional[str] = Field(None, description="How critical to the system/organization")
    performance_target: Optional[str] = Field(None, description="The amount of time this use case should take")
    channels_to_primary_actor: Optional[list[str]] = Field(
        None, description="How the primary actor interacts with the system"
    )
    channels_to_secondary_actors: Optional[list[str]] = Field(
        None, description="How secondary actors interact with the system"
    )
    related_use_cases: Optional[RelatedUseCases] = Field(None, description="Links to parent and child use cases")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate level is one of the allowed values."""
        allowed = {"Summary", "Primary task", "Subfunction"}
        if v not in allowed:
            raise ValueError(f"level must be one of {allowed}, got {v}")
        return v

    model_config = {"extra": "forbid"}
