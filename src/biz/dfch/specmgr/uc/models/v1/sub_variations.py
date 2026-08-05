"""Pydantic model for the collection of use case sub-variations."""

from pydantic import BaseModel, Field

from .sub_variation import SubVariation


class SubVariations(BaseModel):
    """Different technologies or methods for accomplishing steps.

    Attributes:
        items: List of sub-variations
    """

    items: list[SubVariation] = Field(..., description="List of sub-variations")

    model_config = {"extra": "forbid"}
