---
status: accepted
decision-makers: dfch
id: 4c6119c9-532f-4629-8977-108e78304f48
version: 1.0.0
---

# Parse-validate-render pipeline: library choices, no AST-preserving round-trip

## Context and Problem Statement

The ADR system must parse YAML frontmatter, walk the markdown body to locate fixed headings and dynamic Option sections, validate against the Pydantic schema, and then render the entire file back to markdown. Multiple approaches exist: different YAML libraries, different markdown parsers, and different rendering strategies (template-based vs. AST-preserving round-trip).

## Decision Drivers

Correctness of parsing and rendering; ability to locate and extract fixed-heading sections and dynamic option numbering; long-term maintainability of the rendering pipeline.

## Considered Options

`pydantic` + `python-frontmatter` + `markdown-it-py` + deterministic template rendering vs. `PyYAML` directly + different markdown parser vs. `remark`-style AST-preserving round-trip.

## Decision Outcome

Use `pydantic` for Frontmatter and Body Pydantic models. Use `python-frontmatter` for splitting and parsing the YAML header (wraps PyYAML). Use `markdown-it-py` for walking the markdown token stream to locate fixed-heading sections (`## Context and Problem Statement`, etc.) and the dynamic `Option N` collection. Rendering is deterministic, template-based (not an AST serializer): the canonical form is defined entirely by the validator and renderer. Arbitrary human formatting nuances outside the schema (spacing, line wrapping, comment style) are not a preservation requirement, so AST round-trip preservation tooling (like `remark`) is not needed.

### Consequences

Lightweight, standard Python libraries with good maturity. `markdown-it-py` is purpose-built for token walking, avoiding the complexity of remark. Deterministic template rendering is simple, maintainable, and sufficient because the schema defines the canonical form. Trade-off: if a user adds custom formatting outside the schema (e.g., extra comments, unusual spacing), that formatting will be lost on the next tool-driven update. This is acceptable because the schema is the source of truth, and custom formatting is not a preserved artifact.

## More Information

Implementation: models/adr/v1/parser.py (parse_adr, uses markdown-it-py + python-frontmatter), models/adr/v1/renderer.py (render_adr, deterministic template), models/adr/v1/frontmatter.py (Pydantic AdrFrontmatter model), models/adr/v1/body.py (Pydantic AdrBody model).
