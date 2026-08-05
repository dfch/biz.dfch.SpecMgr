"""Pydantic model for a single use case extension."""

from pydantic import BaseModel, Field, model_validator

from .extension_action import ExtensionAction


class Extension(BaseModel):
    """An alternative flow that still results in success.

    Attributes:
        step_reference: Reference to main scenario step (e.g., '3a', '4b')
        condition: Condition that triggers this extension
        actions: Ordered list of compound-numbered actions or sub-use cases to perform
    """

    step_reference: str = Field(..., pattern=r"^[0-9]+[a-z]?$", description="Reference to main scenario step")
    condition: str = Field(..., min_length=1, description="Condition that triggers this extension")
    actions: list[ExtensionAction] = Field(
        ..., min_length=1, description="Ordered list of compound-numbered actions or sub-use cases to perform"
    )

    @model_validator(mode="after")
    def validate_actions_numbered_sequentially(self) -> "Extension":
        """Each action's number must be '{step_reference}{n}' for n = 1, 2, 3, ... in order.

        E.g. extension '3a' must number its actions '3a1', '3a2', '3a3', ... with no gaps,
        duplicates, or out-of-order entries. This cross-item invariant (action number prefix
        matching the parent step_reference, sequential suffix) cannot be expressed per-item in
        JSON Schema (uc_schema.json), so it is enforced here instead.
        """
        expected = [f"{self.step_reference}{n}" for n in range(1, len(self.actions) + 1)]
        actual = [action.number for action in self.actions]
        if actual != expected:
            raise ValueError(
                f"actions must be numbered {expected} for step_reference {self.step_reference!r}, got {actual}"
            )
        return self

    model_config = {"extra": "forbid"}
