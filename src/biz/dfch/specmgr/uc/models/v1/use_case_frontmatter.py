"""Pydantic model for Use Case YAML frontmatter metadata."""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class UseCaseFrontmatter(BaseModel):
    """YAML frontmatter metadata for a use case document.

    Attributes:
        id: Unique identifier matching pattern 'uc-NNN' (e.g., 'uc-001')
        version: Semantic version (e.g., '1.0.0')
        status: Current status of the use case
        created: ISO 8601 date when created
        updated: ISO 8601 date when last updated
    """

    id: str = Field(..., pattern=r"^uc-[0-9]+$", description="Unique identifier for the use case")
    version: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Semantic version")
    status: str = Field(
        ...,
        description="Current status of the use case",
        json_schema_extra={"enum": ["draft", "proposed", "accepted", "deprecated", "superseded"]},
    )
    created: date = Field(..., description="ISO 8601 date when the use case was created")
    updated: date = Field(..., description="ISO 8601 date when the use case was last updated")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values."""
        allowed = {"draft", "proposed", "accepted", "deprecated", "superseded"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}, got {v}")
        return v

    model_config = {"extra": "forbid"}
