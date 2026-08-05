"""Pydantic model for a single scenario step."""

from pydantic import BaseModel, Field


class Step(BaseModel):
    """A single action or interaction in a scenario.

    Attributes:
        number: Step number (1, 2, 3, ...)
        description: Action description for this step
    """

    number: int = Field(..., ge=1, description="Step number")
    description: str = Field(..., min_length=1, description="Action description for this step")

    model_config = {"extra": "forbid"}
