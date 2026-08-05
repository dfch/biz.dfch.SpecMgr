---
id: feat-0-use-cases
version: 1.0.0
status: planning
created: 2026-08-05
updated: 2026-08-05
---

# Feature: Create Use Cases with tool support

## Plan

### Overview

Create a Markdown schema for use cases based on Alistair Cockburn's template, with tools to validate the schema and generate PlantUML diagrams (UC and Sequence diagrams). This enables specification of system behavior in a structured, machine-readable format that can be visualized and validated.

### Requirements

- REQ-001: Define a Markdown schema for use cases based on Cockburn's template (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Related Information)
- REQ-002: Validate Markdown use cases against the schema (structure, required fields, format)
- REQ-003: Generate PlantUML Use Case diagrams from validated use cases (showing actors and use case relationships)
- REQ-004: Generate PlantUML Sequence diagrams from use case scenarios (separate diagrams for main success path and each extension)
- REQ-005: Create MCP tools to support the workflow (parse, validate, generate diagrams)

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — Markdown schema defined with all Cockburn attributes; documented with examples
- [ ] ACC-002: Verifies REQ-002 — Validation tool checks required fields, format, and structure; rejects invalid use cases with clear error messages
- [ ] ACC-003: Verifies REQ-003 — UC diagram generator creates PlantUML code showing all actors and use cases with correct associations
- [ ] ACC-004: Verifies REQ-004 — Sequence diagram generator creates separate diagrams for main success path and each extension, showing actor-system interactions
- [ ] ACC-005: Verifies REQ-005 — MCP tools available for parse, validate, and generate operations; integrated into specmgr CLI/server

### Scope

**Included in this feature:**
- Markdown schema definition for use cases (based on Cockburn's template from https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm)
- Pydantic models for use case structure (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Related Information)
- Validation tool to check Markdown use cases against schema
- PlantUML UC diagram generator (actors and use case associations)
- PlantUML Sequence diagram generator (separate diagrams per scenario: main success + each extension)
- MCP tools for parse, validate, and generate operations
- CLI integration (specmgr uc-* commands)

**Explicitly out of scope:**
- Rendering PlantUML to PNG/SVG (PlantUML server/CLI is external dependency)
- Activity diagrams (Sequence diagrams chosen as primary flow visualization)
- Use case editing UI (Markdown is the source format)
- Automatic diagram layout optimization (PlantUML handles this)

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy)
- Blocks: None identified yet
- External: PlantUML (for diagram rendering, not included in this feature)

### Design Notes

**Formal Schema Specification:**
See `uc_schema.json` for the complete JSON Schema definition. This machine-readable schema defines all fields, types, constraints, and validation rules. Agents can parse this to understand the use case structure. See `uc_class.puml` for the class diagram and `uc_example.md` for a detailed example use case.

**Markdown Schema Design:**
- Use Cockburn's template attributes: Use Case name, Goal in Context, Scope, Level, Preconditions, Success End Condition, Failed End Condition, Primary Actor, Trigger, Main Success Scenario, Extensions, Sub-Variations, Related Information (Priority, Performance Target, Frequency, Channels, Secondary Actors, Open Issues, Schedule)
- Markdown structure: H2 for use case name, H3 for sections (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Related Information)
- Steps in scenarios numbered (1, 2, 3...) with optional sub-steps (1a, 1b, 2a, etc.)
- Extensions and Sub-Variations reference step numbers for clarity

**Diagram Generation Strategy:**
- UC diagrams: Parse all use cases, extract actors and use case names, generate PlantUML with actor-to-usecase associations
- Sequence diagrams: For each scenario (main success + each extension), generate separate diagram showing actor-system interactions as message exchanges
- Each diagram is a separate .puml file for modularity

**Validation:**
- Pydantic models enforce required fields and structure
- Custom validators check for valid step numbering, actor references, etc.
- Clear error messages guide users to fix schema violations

**MCP Surface (Tools, Prompts, Resources):**
- To be defined in Task 1.5 (specification phase)
- Expected tools: parse_uc, validate_uc, generate_uc_diagram, generate_sequence_diagram
- Expected resources: uc_list (list all use cases), uc_get (read specific use case)
- Expected prompts: create_uc (guided use case creation), update_uc (revise existing use case)
- Follows existing specmgr patterns (ADR tools/prompts/resources as reference)

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 1: Schema Definition & Validation
- [x] Task 1.1: Define Markdown schema for use cases (Cockburn attributes) — depends on: none — status: completed
- [ ] Task 1.2: Create Pydantic models for use case structure — depends on: Task 1.1 — status: in-progress
- [ ] Task 1.3: Implement validation tool (check required fields, format, step numbering) — depends on: Task 1.2 — status: not-started
- [ ] Task 1.4: Write schema documentation with examples — depends on: Task 1.1 — status: not-started

#### Phase 2: PlantUML Diagram Generation
- [ ] Task 2.1: Implement UC diagram generator (actors + use case associations) — depends on: Task 1.3 — status: not-started
- [ ] Task 2.2: Implement Sequence diagram generator (main success path) — depends on: Task 1.3 — status: not-started
- [ ] Task 2.3: Implement Sequence diagram generator (extensions) — depends on: Task 2.2 — status: not-started
- [ ] Task 2.4: Test diagram generation with sample use cases — depends on: Task 2.3 — status: not-started

#### Phase 3: MCP Tools & CLI Integration
- [ ] Task 3.1: Define MCP tools, prompts, and resources (specification) — depends on: Task 2.4 — status: not-started
- [ ] Task 3.2: Implement MCP tools per specification (Task 3.1) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.3: Implement MCP prompts per specification (Task 3.1) — depends on: Task 3.2 — status: not-started
- [ ] Task 3.4: Implement MCP resources per specification (Task 3.1) — depends on: Task 3.2 — status: not-started
- [ ] Task 3.5: Add CLI commands (specmgr uc-validate, specmgr uc-generate) — depends on: Task 3.2 — status: not-started
- [ ] Task 3.6: Integration tests for full workflow — depends on: Task 3.5 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-05**: Phase 1 (Schema Definition & Validation) substantially complete. Task 1.1 finished with formal JSON Schema, example use case, and class diagram. Now starting Task 1.2 (Pydantic models).

(No blockers identified at this time.)

### Recent Updates

If this section grows too long, move older entries to `history.md` in this
same folder and leave a pointer here, e.g.:
`See history.md for updates before YYYY-MM-DD.`

#### 2026-08-05 (continued)
- **Task 1.1 COMPLETED**: Markdown schema definition and formal specification
  - Created `uc_schema.json` — Complete JSON Schema with validation rules, constraints, and field types (312 lines)
  - Created `uc_example.md` — Detailed "Buy Goods" use case example with all sections
  - Created `uc_class.puml` — Class diagram showing schema structure
  - Frontmatter: `id`, `version`, `status`, `created`, `updated` (no title field; H1 is source of truth)
  - H1: Use case name
  - H2: Main sections (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Open Issues, Related Information)
  - H3: Subsections (Goal in Context, Scope, Level, Preconditions, Success End Condition, Failed End Condition, Primary Actor, Secondary Actors, Trigger, Frequency, Priority, Performance Target, Channels, Related Use Cases, step variations)
  - Max heading depth: H1-H3
  - Required sections: Characteristic Information, Goal in Context, Scope, Level, Preconditions, Success End Condition, Primary Actor, Trigger, Main Success Scenario
  - Optional sections: Failed End Condition, Secondary Actors, Frequency, Priority, Performance Target, Channels, Related Use Cases, Extensions, Sub-Variations, Open Issues, Related Information (Notes, Assumptions)
  - Generated PlantUML diagrams (activity and sequence diagrams for main success path and extensions)
- **Task 1.2 IN PROGRESS**: Create Pydantic models from JSON Schema
  - Next: Convert `uc_schema.json` into Python Pydantic models for validation
- **Housekeeping**: Moved Java reference implementation files to `playground/` subdirectory (not part of Python implementation)
- Notes: User confirmed preference for UC + Sequence diagrams (not Activity diagrams). Sequence diagrams will have separate diagrams for main success path and each extension. Reference: https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm

### Decisions Made

- **DEC-001** [2026-08-05]: Use UC + Sequence diagrams (not Activity diagrams) — Sequence diagrams better show interactions between actors and system; UC diagrams show the big picture. Together they provide overview + detail.
- **DEC-002** [2026-08-05]: Separate Sequence diagrams per scenario (main success + each extension) — Clearer visualization of different flows; easier to understand each scenario independently.
- **DEC-003** [2026-08-05]: Markdown as source format (not a UI) — Keeps use cases in version control, reviewable in PRs, and compatible with existing specmgr workflow.
- **DEC-004** [2026-08-05]: Create a new domain "uc" (use cases) — Following the domain-first hierarchy established in ADR ece4554b-725c-4f76-bc04-5d2b760363d2, create `uc/` as a top-level package alongside `adr/`, with sub-packages for `uc/models/`, `uc/tools/`, `uc/prompts/`, `uc/resources/`. This differs from current `adr/` structure (which has models in shared `models/adr/`) — see tech debt note below.
- **DEC-005** [2026-08-05]: Always include all optional section headings in use case documents — Even when empty, include Extensions, Sub-Variations, Open Issues, and Related Information sections. This ensures structural consistency across all use cases, makes it clear that these aspects were considered (even if empty), simplifies parsing/validation, and makes git diffs cleaner when content is added later. Empty sections can contain "(None identified)" or similar placeholder text.

### Related PRs / Commits

- [PR #NNN](link): [description]
- [Commit hash](link): [description]

## Technical Debt

### ADR models location refactoring (unrelated to this feature)

Currently, `adr/` domain has its schema models in the shared `models/adr/` folder (outside the domain package). This feature establishes a new pattern: `uc/models/` (models inside the domain package). For consistency, `adr/models/` should be moved into `adr/models/` to match the new pattern. This is a separate refactoring task, not part of this feature's scope, but should be tracked and prioritized.

**Impact**: Once completed, both `adr/` and `uc/` will have consistent internal structure with models co-located in their respective domain packages.

### Update `.specmgr/_template/v1/README.md` to include Tech Debt section

The feature template at `.specmgr/_template/v1/README.md` does not include a "Technical Debt" section. This section is useful for recording known issues, refactoring needs, and architectural inconsistencies discovered during feature work. The template should be updated to include an optional "## Technical Debt" section with guidance on when to use it.

**Impact**: Future features will have a consistent place to record tech debt, making it discoverable and prioritizable.
