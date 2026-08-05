"""Pydantic model for the Use Case Related Information section."""

from typing import Optional

from pydantic import BaseModel, Field


class RelatedInformation(BaseModel):
    """Additional context, notes, and assumptions.

    Attributes:
        notes: Additional notes about the use case
        assumptions: Assumptions made in this use case
    """

    notes: Optional[list[str]] = Field(None, description="Additional notes about the use case")
    assumptions: Optional[list[str]] = Field(None, description="Assumptions made in this use case")

    model_config = {"extra": "forbid"}
