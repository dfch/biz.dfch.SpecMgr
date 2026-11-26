---
status: accepted
decision-makers: dfch
id: ece4554b-725c-4f76-bc04-5d2b760363d2
version: 1.0.0
---

# Organize the codebase by document-type domain: domain-first hierarchy for tools/prompts/resources, shared versioned models

## Context and Problem Statement

As the SpecMgr project grows to support multiple document types (initially ADR, later req, uc, ac, etc.), the code organization must scale. Two patterns exist: (1) interface-layer-first (top-level tools/, prompts/, resources/ packages, each with domain sub-packages like tools/adr/, prompts/adr/), or (2) domain-first (top-level adr/, req/, uc/ packages, each containing its own tools/, prompts/, resources/ sub-packages). Interface-layer-first scatters each domain across three locations; domain-first co-locates all code for one document type. The schema layer (Pydantic models, parser, renderer, mutations) must also have a clear home.

## Decision Drivers

Maintainability and discoverability: developers working on ADR functionality should find all ADR code in one place; future document types (req, uc, ac) should follow the same pattern; schema mutations (update_section, option_create, etc.) need a consistent, domain-agnostic location; schema versioning must support long-term evolution (v1, v2, etc.) without code duplication.

## Considered Options

Interface-layer-first (tools/adr/, prompts/adr/, resources/adr_*) vs. domain-first (adr/tools/, adr/prompts/, adr/resources/); mutations as Pydantic model methods vs. pure free functions; full wholesale vN duplication per major schema version vs. minimal diff (only changed classes in vN, import unchanged classes from vN-1).

## Decision Outcome

Adopt a domain-first hierarchy. Create top-level domain packages (adr/, and later req/, uc/, ac/) each containing tools/, prompts/, resources/ sub-packages. Keep models/ as a shared, top-level package organized internally by domain (models/adr/, models/req/, etc.) with major-version sub-packages (models/adr/v1/, models/adr/v2/, etc.). Mutations (update_section, set_status, option_*, etc.) live as pure free functions in models/adr/v1/mutations.py (not as Pydantic model methods), taking whole Adr objects and returning new Adr objects or read-only data, never mutating their arguments. For major schema version upgrades, create a minimal vN package containing only the classes that changed; unchanged classes are imported from vN-1. This avoids a full N-parsers-times-N-renderers maintenance matrix and prevents drift from unrelated bugfixes.

### Consequences

All ADR-related code is co-located under adr/; future domains (req/, uc/, ac/) will follow the identical structure, making the codebase predictable and maintainable. Shared models/ reduces duplication and keeps schema validation centralized. Free-function mutations are stateless and composable. Minimal vN duplication (only changed classes) keeps migration code simple and maintainable. Trade-off: domain packages are now top-level, adding one level of nesting compared to interface-layer-first; developers unfamiliar with the convention must learn the pattern once.

### Confirmation

Verify that adr/, models/adr/, tests/adr/, tests/models/adr/ follow the documented structure; verify that mutations are pure functions with no side effects; verify no Pydantic model classes define their own mutation methods.
