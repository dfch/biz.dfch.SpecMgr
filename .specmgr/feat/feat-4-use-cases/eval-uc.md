# Plan: Evaluate and Formalize Use Case Tooling

## Overview

Build a complete use case (UC) document type for SpecMgr, following the established ADR tooling pattern. This plan evaluates design choices, validates the markdown schema through implementation, and delivers UC support alongside ADRs.

---

## Phase A: Schema & Pydantic Model (Weeks 1–2)

### A1. Finalize UC Schema
- Document the complete UC markdown structure in a formal schema specification
- Define all required and optional sections
- Establish naming conventions for actor references, step numbering, and alternative flow labels
- Output: `doc/uc-schema.md` (canonical reference, mirrors `adr-tool-plan.md` in scope)

### A2. Design Pydantic Models
Create `models/uc/v1/` package with full schema layer (no MCP dependency):
- **uc.py**: `UcFrontmatter`, `UcBody`, `UcStep`, `UcAlternativeFlow`, `Uc` models
- **frontmatter.py**: Parse YAML frontmatter with status, date, decision-makers, etc.
- **body.py**: Structured model for sections (Overview, Metadata, Main Success Scenario, Alternative Flows, Technology Variations)
- **parser.py**: Parse markdown → `Uc` model using `markdown-it-py` token stream
- **renderer.py**: Render `Uc` model → canonical markdown
- **mutations.py**: Pure functions for editing sections (update_section, update_alternative_flow, etc.)

### A3. Write Comprehensive Tests
- Unit tests for each Pydantic model (valid/invalid inputs)
- Parser tests: round-trip markdown → model → markdown for consistency
- Mutation tests: verify section updates, alternative flow edits, etc.
- Target: ≥90% coverage (matching ADR test density)

### A4. Validate Against Examples
- Parse the example use case (`doc/uc-example-for-plantuml.md`) with the new model
- Verify PlantUML code generation examples align with parsed model output
- Iterate schema if needed based on real-world example

---

## Phase B: MCP Tools and Resources (Weeks 2–3)

### B1. Create `uc/tools/` Package
Build 11 `@mcp.tool()` wrappers mirroring the ADR tool pattern:
- `create_uc` — Create new use case document
- `get_uc` — Read by id
- `update_frontmatter` — Update YAML metadata
- `update_section` — Update any body section (Overview, Metadata, Technology Variations)
- `update_alternative_flow` — Create/update/delete alternative flows
- `validate_uc` — Validate a UC by id
- **Shared infrastructure**: `_paths.py`, `_io.py` for id→path resolution and file I/O

### B2. Create `uc/resources/` Package
Expose read-only access via MCP resources:
- `specmgr://uc/list` — List all UC documents (resource)
- `specmgr://uc/{id}` — Read UC by id (template resource)

### B3. Write Tool Tests
- Unit tests for each tool (invalid input, file I/O, id resolution)
- Integration tests: create → update → read → validate workflows
- Target: ≥95% coverage (tools are critical user-facing surface)

### B4. Wire Into Server
- Import `uc.tools` and `uc.resources` at bottom of `server.py` (matching ADR pattern)
- Verify tools and resources register via `mcp list-tools` / `mcp list-resources`

---

## Phase C: MCP Prompts (Week 3)

### C1. Create Prompt Surface
Build `uc/prompts/` package with guided workflows:
- **`create_uc(scope, actors, trigger=None, decision_makers=None)`** → Returns instructional text for drafting a new UC
  - Guides user through: Overview → Metadata → Main Scenario → Alternatives → Technology Variations
  - Instructs LLM to check `specmgr://uc/list` for similar existing UCs
- **`update_uc(id, instructions=None)`** → Returns instructional text for revising an existing UC
  - Guides through the same sections, with change-mapping logic
  - Maps requested changes to the right tool (section update vs. alternative flow edit)

### C2. Step-Gated Test Variants (Optional)
- Create `create_uc_test` and `update_uc_test` with hard numbered `GATE 0..GATE N` blocks
- Same purpose as ADR test variants: A/B compare LLM compliance with narrated prompt

### C3. Write Prompt Tests
- Verify prompts return valid, readable instructional text
- Test with LLM to ensure tool sequence is followable

---

## Phase D: Parser for PlantUML Code Generation (Week 4)

### D1. Design PlantUML Extraction Helpers
Create utility functions in `models/uc/v1/` to extract diagram data:
- **extract_use_case_diagram()** → Returns dict with actors, use cases, relationships (include/extend based on alternative flows)
- **extract_activity_diagram()** → Returns dict with steps, swimlanes, decision branches, partitions
- **generate_plantuml_usecase()** → Template rendering for use case diagram PlantUML code
- **generate_plantuml_activity()** → Template rendering for activity diagram PlantUML code

### D2. Implement Parsing Logic
- Regex/parse Main Success Scenario steps: `^\d+\.\s+([A-Za-z]+)\s+(.+)$` → Extract actor and action
- Build swimlane map (actor → steps)
- Parse Alternative Flows: map step reference (5a) → decision diamonds
- Handle branching logic: "return to step X" → rejoins, "use case ends" → terminal

### D3. Write Extraction Tests
- Test extract_* functions on example UC
- Verify PlantUML code is syntactically valid (run through PlantUML renderer if available)
- Test round-trip: UC markdown → diagram data → PlantUML code

---

## Phase E: CLI Commands (Week 4)

### E1. Add UC Subcommands
Create `commands/uc.py` (or split into `commands/uc_*.py` per operation):
- `specmgr uc create --scope "Wiki System" --actors "Member,Admin"` — Prompt-driven creation
- `specmgr uc get <id>` — Display UC by id
- `specmgr uc list` — List all UCs
- `specmgr uc validate <id>` — Validate UC by id
- `specmgr uc diagram <id> [--type usecase|activity]` — Generate and print PlantUML code

### E2. Wire Into CLI App
- Register new commands in `cli.py` (Typer app)
- Ensure `specmgr uc --help` shows all subcommands

### E3. Write CLI Tests
- Test each command with valid and invalid inputs
- Test output formatting

---

## Phase F: Documentation & Examples (Week 5)

### F1. Formalize Schema Documentation
- Move/expand content from `doc/plantuml-analysis.md` and `doc/uc-example-for-plantuml.md` into a canonical spec
- Create `doc/uc-tool-plan.md` (mirroring `.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md`) with:
  - Complete schema and field definitions
  - Design rationale for each section
  - Next steps and per-item done/not-done tracking

### F2. Create Additional Examples
- Simple UC example (5 steps, no alternatives)
- Complex UC example (15+ steps, multiple branches)
- UC with subsections/swimlane-heavy activity diagram

### F3. Update AGENTS.md
- Document UC feature status (same section as ADR status)
- Identify what still needs to be done (CLI, CI/pre-commit for UCs, etc.)

---

## Phase G: Integration Tests & Validation (Week 5)

### G1. End-to-End Workflows
- Create UC via MCP tool → validate → read → generate diagrams
- Create UC via CLI command → verify file on disk → read via MCP resource
- Update UC via prompt/tool → verify changes persist

### G2. File Format & Roundtrip
- Verify markdown → model → markdown roundtrip is deterministic
- Test with hand-edited UC markdown (human edits don't break parser)

### G3. PlantUML Validation
- Generate PlantUML code for all example UCs
- Render diagrams (via online PlantUML or local renderer)
- Verify visual output matches intended flow

---

## Phase H: Pre-Commit Hook & CI (Week 6)

### H1. Extend Pre-Commit Configuration
- Add UC validation to `.pre-commit-config.yaml` (run `specmgr uc validate` on all UC files)
- Ensure lint/test scope includes new `uc/` package files

### H2. Extend CI Workflow
- CI matrix runs tests for UC package (same 3.11/3.12/3.13 matrix as ADRs)
- `specmgr docs` generation includes UC API docs
- Validate all UCs in repo before release

---

## Deliverables Checklist

### Code
- [ ] `models/uc/v1/` — Full Pydantic schema + parser + renderer + mutations
- [ ] `uc/tools/` — 7 MCP tools + shared infrastructure
- [ ] `uc/resources/` — 2 MCP resources (list, get-by-id)
- [ ] `uc/prompts/` — 2 prompt surfaces (create, update) + optional test variants
- [ ] `commands/uc.py` — CLI commands
- [ ] Extraction helpers in `models/uc/v1/` for PlantUML code generation

### Tests
- [ ] `tests/models/uc/` — ≥90% coverage (parser, models, mutations, extraction)
- [ ] `tests/uc/tools/` — ≥95% coverage (tool I/O, error handling)
- [ ] `tests/uc/resources/` — ≥95% coverage (resource access)
- [ ] `tests/uc/prompts/` — All prompts return valid text
- [ ] `tests/commands/uc.py` — All CLI commands tested

### Documentation
- [ ] `doc/uc-tool-plan.md` — Canonical schema + design rationale
- [ ] `doc/uc-schema.md` — Section-by-section field reference
- [ ] `doc/uc-example-simple.md` — Lightweight example
- [ ] `doc/uc-example-complex.md` — Feature-rich example
- [ ] Updated `AGENTS.md` with UC status
- [ ] Updated `doc/uc-plantuml-examples.md` with real generated PlantUML output

### Integration
- [ ] Pre-commit hook validates all UCs on commit
- [ ] CI pipeline runs UC tests + validation
- [ ] `specmgr docs` generates UC API docs
- [ ] Version bump and CHANGELOG entry (release as v0.3.0)

---

## Open Questions / Decisions

1. **Base Directory**: Where should UC files live by default?
   - Option A: `./docs/uc/` (mirroring `./docs/adr/`)
   - Option B: `./use-cases/` (more semantic)
   - Option C: Configurable via `SPECMGR_UC_DIR` env var (like `SPECMGR_ADR_DIR`)
   - **Decision**: (TBD)

2. **Frontmatter Fields**: Should UCs have the same frontmatter as ADRs (status, decision-makers, etc.)?
   - ADRs need `status` (proposed/accepted/rejected/etc.)
   - UCs are more descriptive (less of a "decision"), so may not need `status`
   - But might want `created_date`, `authors`, `reviewed_by` for traceability
   - **Decision**: (TBD)

3. **PlantUML Code Gen**: Should PlantUML code be:
   - A) Generated on-the-fly from UC markdown (parse + render templates) — more dynamic, always in sync
   - B) Stored alongside UC markdown (e.g., `uc-001-edit.md` + `uc-001-edit.puml`) — explicit, version-controlled
   - C) Both (option A as default, allow committing B for review)
   - **Decision**: (TBD)

4. **Alternative Flow Syntax**: Current format is `5a. Preview Changes` with **Trigger** + **Flow**.
   - Alternative: Should alternative flows be sub-sections under Main Scenario for tighter coupling?
   - Alternative: Should we support conditional expressions (e.g., `5a. [if preview_clicked]`) instead of natural language?
   - **Decision**: (TBD — current approach seems good, but document rationale)

5. **Stakeholder Tracking**: ADRs have `decision-makers`, `consulted`, `informed` fields.
   - Should UCs have analogous fields for traceability (e.g., `author`, `reviewed_by`, `stakeholders`)?
   - **Decision**: (TBD)

---

## Success Criteria

✅ All tests pass (model + tool + resource + prompt + CLI)  
✅ Example UCs parse → validate → generate PlantUML without errors  
✅ PlantUML diagrams render visually and match intended flows  
✅ LLM can create and update UCs via MCP tools following prompt guidance  
✅ Human developers can hand-edit UC markdown without breaking parser  
✅ Pre-commit hook catches validation errors locally  
✅ CLI `specmgr uc` subcommands work as expected  
✅ All code follows project style (ruff, pylint)  
✅ Documentation is complete and clear  

---

## Timeline

- **Week 1–2**: Schema + Models + Tests
- **Week 2–3**: MCP Tools + Resources
- **Week 3**: MCP Prompts
- **Week 4**: PlantUML Generation + CLI
- **Week 5**: Documentation + Examples + Integration Tests
- **Week 6**: Pre-Commit + CI + Release

**Total**: ~6 weeks (calendar time may vary based on parallel work)

---

## Notes

- This plan closely mirrors `.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md` in structure and scope — reuse ADR learnings where possible
- Resist the urge to add "nice to have" features (e.g., UC diagram generation, swimlane optimization) until Phase H is complete
- Keep mutations as pure functions in `models/uc/v1/mutations.py` (not Pydantic methods), matching ADR pattern
- Every tool call should re-read and re-parse current on-disk state (no in-memory cache), matching ADR pattern
- Test coverage targets: match or exceed ADR test density (186 passing ADR tests across models + tools + resources + prompts)
