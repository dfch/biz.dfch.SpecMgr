"""Pydantic model for a single use case sub-variation."""

from pydantic import BaseModel, Field


class SubVariation(BaseModel):
    """Different technologies or methods for accomplishing a step.

    Attributes:
        step_reference: Reference to main scenario step (e.g., '1', '7')
        variations: List of alternative ways to perform this step
    """

    step_reference: str = Field(..., pattern=r"^[0-9]+$", description="Reference to main scenario step")
    variations: list[str] = Field(..., min_length=1, description="List of alternative ways to perform this step")

    model_config = {"extra": "forbid"}
