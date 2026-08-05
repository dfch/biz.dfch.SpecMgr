"""Pydantic model for the collection of use case extensions."""

from pydantic import BaseModel, Field

from .extension import Extension


class Extensions(BaseModel):
    """Alternative flows that still result in success.

    Attributes:
        items: List of extensions
    """

    items: list[Extension] = Field(..., description="List of extensions")

    model_config = {"extra": "forbid"}
