---
status: accepted
decision-makers: dfch
id: e11421d3-cc1d-487b-af32-ee4093422712
version: 1.0.0
---

# Use Architecture Decision Records (ADRs) to document design decisions

## Context and Problem Statement

As the project evolves, significant design and architectural decisions are made (e.g., domain-first package layout, filesystem-as-source-of-truth, ISO 8601 date usage, development artifact organization). Without a consistent, discoverable record of these decisions, the reasoning behind them is lost over time, gets re-litigated, or is only recoverable by archaeology through git history and chat logs. The project needs a lightweight, standardized way to capture the context, options considered, and rationale behind each significant decision, in a format that is both human-readable and machine-parseable (since specmgr itself provides tooling to create/read/update ADRs).

## Decision Drivers

- Decisions and their rationale must be discoverable by future contributors and agents, not just recoverable from commit history
- The format must be simple enough to write by hand, yet structured enough for specmgr's own tooling (`adr` domain package) to parse, validate, and render
- The format should be a widely recognized standard rather than a bespoke one, to lower the learning curve for contributors and to allow reuse of existing tooling/conventions
- ADRs must be version-controlled alongside the code they describe

## Considered Options

- MADR (Markdown Architecture Decision Records) 4.0.0, as implemented by this project's own `models/adr/v1` schema and `adr/tools/` MCP surface

## Decision Outcome

Adopt Architecture Decision Records (ADRs) as the standard way to document significant design and architectural decisions for this project, stored as Markdown files under `docs/adr/`. Each ADR is authored and maintained using specmgr's own `adr` domain tooling (`models/adr/v1`, `adr/tools/`), which implements the MADR 4.0.0 format. This is a deliberately reflexive choice: specmgr, a tool for managing specification artifacts, uses its own ADR feature to document its own decisions.

### Consequences

**Positive:**
- Design decisions, their context, and their rationale are preserved in a durable, version-controlled, and discoverable location (`docs/adr/`)
- specmgr's own ADR tooling gets continuous real-world exercise ("dogfooding"), surfacing usability gaps early
- The MADR format is a recognized industry standard, so new contributors familiar with it need no onboarding
- `docs/adr/README.md` (generated via `specmgr adr-toc`) gives a single table-of-contents entry point to all decisions

**Negative:**
- Adds process overhead: every significant decision now requires an ADR rather than being made informally
- Requires discipline to keep ADR status (`proposed`/`accepted`/`superseded`/...) up to date as decisions evolve

## Pros and Cons of the Options

### Option 1: MADR 4.0.0 via specmgr's ADR tooling

Each ADR is a single Markdown file under `docs/adr/`, named `{id}-{slug}.md`, consisting of:

- **YAML frontmatter**: `id` (server-assigned UUID), `version` (schema version), `status` (`draft` | `proposed` | `accepted` | `rejected` | `deprecated` | `superseded` | `superseded by ...`), `date`, `decision-makers`, `consulted`, `informed`
- **Body** (Markdown, MADR 4.0.0 structure):
  - `# {title}` (H1)
  - `## Context and Problem Statement` (mandatory)
  - `## Decision Drivers` (optional)
  - `## Considered Options` (mandatory)
  - `## Decision Outcome` (mandatory), with optional `### Consequences` and `### Confirmation` sub-sections
  - `## Pros and Cons of the Options` (derived; rendered only if one or more `### Option N: {title}` entries exist)
  - `## More Information` (optional, always last)

This is not a hand-rolled convention: it is exactly what this project's `models/adr/v1` Pydantic schema, parser, and renderer implement, and exactly what the `adr/tools/` MCP tools (`create_adr`, `update_section`, `set_status`, `option_*`, `validate_adr`, ...) operate on. A separate `specmgr adr-toc` CLI command regenerates `docs/adr/README.md` as a table of contents over all ADRs, and `pre-commit`/CI hooks keep both the docs and the ADR set consistent.
