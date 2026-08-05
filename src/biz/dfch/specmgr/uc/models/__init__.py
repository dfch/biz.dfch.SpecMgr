"""Use Case models — Pydantic schema for Cockburn-based use cases.

This package contains versioned model definitions. The current version is re-exported
as "current" for convenience.
"""

from .v1 import (
    CharacteristicInformation,
    Extension,
    ExtensionAction,
    Extensions,
    MainSuccessScenario,
    OpenIssues,
    RelatedInformation,
    RelatedUseCases,
    Step,
    SubVariation,
    SubVariations,
    UcParseError,
    UseCaseFrontmatter,
    UseCase,
    parse_uc,
)

# Re-export v1 as "current" for convenience
__all__ = [
    "UseCaseFrontmatter",
    "CharacteristicInformation",
    "RelatedUseCases",
    "Step",
    "MainSuccessScenario",
    "Extension",
    "ExtensionAction",
    "Extensions",
    "SubVariation",
    "SubVariations",
    "OpenIssues",
    "RelatedInformation",
    "UseCase",
    "parse_uc",
    "UcParseError",
]
