"""Pydantic model for a single action within a use case extension."""

from pydantic import BaseModel, Field


class ExtensionAction(BaseModel):
    """One numbered action within an :class:`Extension`.

    Cockburn's template numbers extension actions with a compound scheme
    derived from the extension's own ``step_reference`` (e.g. extension
    ``"3a"`` numbers its actions ``"3a1"``, ``"3a2"``, ``"3a3"``, ...). This
    class only enforces the *format* of that compound number (digits,
    optional letter, digits); whether an action's number actually shares its
    parent extension's ``step_reference`` prefix and is sequential is a
    cross-field concern validated on :class:`Extension` itself.

    Attributes:
        number: Compound action number (e.g. '3a1', '10b2')
        description: Action description
    """

    number: str = Field(..., pattern=r"^[0-9]+[a-z]?[0-9]+$", description="Compound action number, e.g. '3a1'")
    description: str = Field(..., min_length=1, description="Action description")

    model_config = {"extra": "forbid"}
