"""Pydantic model for links between related use cases."""

from typing import Optional

from pydantic import BaseModel, Field


class RelatedUseCases(BaseModel):
    """Links to parent and child use cases.

    Attributes:
        superordinate: Name of use case that includes this one
        subordinate: List of use cases that are part of this one
    """

    superordinate: Optional[str] = Field(None, description="Name of use case that includes this one")
    subordinate: Optional[list[str]] = Field(None, description="List of subordinate use cases")

    model_config = {"extra": "forbid"}
