"""Pydantic model for the Use Case Open Issues section."""

from pydantic import BaseModel, Field


class OpenIssues(BaseModel):
    """Questions and decisions awaiting resolution.

    Attributes:
        items: List of open issues
    """

    items: list[str] = Field(..., description="List of open issues")

    model_config = {"extra": "forbid"}
