"""Pydantic model for the Use Case main success scenario."""

from pydantic import BaseModel, Field, model_validator

from .step import Step


class MainSuccessScenario(BaseModel):
    """The happy path: steps from trigger to goal completion.

    Attributes:
        steps: Ordered list of steps in the main success scenario
    """

    steps: list[Step] = Field(..., min_length=1, description="Ordered list of steps")

    @model_validator(mode="after")
    def validate_steps_numbered_contiguously(self) -> "MainSuccessScenario":
        """Steps must be numbered 1, 2, 3, ... in ascending order, with no gaps or duplicates.

        JSON Schema (uc_schema.json) can only constrain each step's ``number`` individually
        (``minimum: 1``); this cross-item invariant across the whole list must be enforced here.
        """
        expected = list(range(1, len(self.steps) + 1))
        actual = [step.number for step in self.steps]
        if actual != expected:
            raise ValueError(f"steps must be numbered contiguously starting at 1 ({expected}), got {actual}")
        return self

    model_config = {"extra": "forbid"}
