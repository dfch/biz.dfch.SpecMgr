---
classification: null
created: '2026-09-03 10:00:47.481+02:00'
id: feat-84-specmgr-sysrs
status: done
type: feat
updated: '2026-10-07T06:21:40.953Z'
version: 1.0.0
---

# Feature: Create a SysRS for This Repo from the Existing Codebase and Features

## Plan

### Overview

biz.dfch.SpecMgr already ships a `sysrs` domain (feat-32-sysrs) that lets an
agent assemble a System Requirements Specification out of cross-references to
existing `gol`/`prb`/`qa`/`uc`/`req`/`rsk`/`dec`/`adr`/`vcr` artifacts, but no
SysRS document exists yet for this repository itself. GitHub issue #84 asks
for exactly that, built retrospectively: read and understand the existing
source code and every feature folder under `.specmgr/feat/`, extract whatever
requirements/decisions/scope information is already implicit there, ask the
user for anything missing, and then produce the SysRS document. This feature
also captures a short, repeatable procedure for refreshing that SysRS later
as new domains/features land, so the effort is not a one-off dead end.

### Requirements

- REQ-001: The agent must read and understand the source code under `src/` and `AGENTS.md` before drafting the SysRS.
- REQ-002: The agent must read and understand every existing feature folder under `.specmgr/feat/` to extract requirements, decisions, and scope already captured there.
- REQ-003: The agent must scan for existing `gol`/`req`/`uc`/`rsk`/`dec`/`adr`/`vcr` documents on disk (if any) and reuse their ids/titles as SysRS cross-reference bullets rather than re-deriving equivalent content from scratch.
- REQ-004: Where information needed for a mandatory SysRS section cannot be derived from existing artifacts, the agent must ask the user via the `question` tool rather than inventing content.
- REQ-005: The final output must be a schema-valid SYSRS document created via `create_sysrs`, whose cross-references cover the domain-package inventory listed in `AGENTS.md`'s Status section.
- REQ-006: The feature must produce a short, repeatable procedure (steps or a checklist) for regenerating/refreshing the SysRS later as new domains or features are added.

### Acceptance Criteria

- [x] ACC-001: `validate_sysrs(content, full=True)` passes with no errors on the drafted document before `create_sysrs` is called.
- [x] ACC-002: Every one of the 9 ISO/IEC 25010:2023 characteristic sections under `## Requirements` references at least one existing `REQ` id, or is explicitly left empty with a documented reason.
- [x] ACC-003: Every implemented domain package listed in `AGENTS.md`'s Status section is represented by at least one `REQ`/`GOL`/`DEC`/`UC` bullet somewhere in the SysRS.
- [x] ACC-004: Any information gaps identified during drafting were resolved by asking the user (via the `question` tool) and are reflected in the final document, not left as placeholders.
- [x] ACC-005: The regeneration workflow/checklist is written down (in this feature's Design Notes, added later) and can be followed without re-deriving it from scratch.

### Scope

#### Included

- Reading and analyzing `src/`, `AGENTS.md`, and every `.specmgr/feat/*/README.md`.
- Creating any missing prerequisite `GOL`/`REQ`/`DEC` documents needed so a SysRS cross-reference bullet points at a real id, using the appropriate `create_<d>` tool.
- Authoring the single SysRS document for this repo via `create_sysrs`, validated first with `validate_sysrs`.
- Documenting the regeneration workflow for refreshing the SysRS later.

#### Explicitly Out Of Scope

- Building or modifying any MCP tools, resources, or domain schemas -- this feature only produces documentation artifacts using existing tooling.
- Retroactively authoring full `VCR`/`UC` verification coverage for every `REQ` -- only cross-references what already exists or is minimally needed for the SysRS itself.
- Adding CI/pre-commit enforcement of SysRS freshness (tracked separately, similar to the existing "no `validate_*` in CI yet" gap noted in `AGENTS.md`).

### Design Notes

Regeneration/refresh checklist for keeping this SysRS current as the codebase evolves: (1) when a new domain package ships, create or verify at least one `REQ` document for it under the best-fit ISO/IEC 25010:2023 characteristic before referencing it from the SysRS; (2) when a new high-level business goal emerges, create a `GOL` document via `create_gol` before referencing it under `## Business Context and Goals`; (3) when a meaningful architectural or general decision accumulates, add an `ADR`/`DEC` cross-reference bullet to `## Decisions`, verifying the referenced document's exact current title first via `list_adr`/`get_adr` or `list_dec`/`get_dec`; (4) after any manual edit to the SysRS body, re-run `validate_sysrs(content, full=True)` and fix every reported issue before writing; (5) prefer the generic `update` tool's line-range `offset`/`limit` splice to append or insert a single new cross-reference bullet rather than re-authoring the whole document, mirroring how this very Design Notes section was itself inserted; (6) prepend a new dated entry to the SysRS's own `## Updates` section describing what changed and why, keeping the newest-first ordering that section's schema enforces.

### Task List

#### Phase 100: Discovery

- [x] Task 100.100: Read `AGENTS.md` and the source tree under `src/` to build a domain-package inventory.
- [x] Task 100.110: Read every `.specmgr/feat/*/README.md` and extract requirements, decisions, and scope already captured there.
- [x] Task 100.120: Enumerate any existing `gol`/`req`/`uc`/`rsk`/`dec`/`adr`/`vcr` documents on disk via their `list_<d>` tools and record their ids/titles.

#### Phase 110: Gap-Filling

- [x] Task 110.100: Identify SysRS sections (Goals, Decisions, Requirements per ISO 25010 characteristic, Other Characteristics) that have no corresponding existing artifact.
- [x] Task 110.110: Ask the user via the `question` tool to resolve each identified gap.
- [x] Task 110.120: Create any minimal prerequisite `GOL`/`REQ`/`DEC` documents needed to back a SysRS cross-reference bullet.

#### Phase 120: Draft and Create the SysRS

- [x] Task 120.100: Assemble the SysRS body per `specmgr://sysrs/template`/`specmgr://sysrs/example` and the `specmgr://sysrs/schema`.
- [x] Task 120.110: Run `validate_sysrs(content, full=True)` and fix any reported issues.
- [x] Task 120.120: Call `create_sysrs` to persist the document.
- [x] Task 120.130: Write down the regeneration workflow (e.g. in this feature's Design Notes via the `update` tool) for future refreshes.

## Progress

### Current Status

**As of 2026-09-03**: Phase 3 (Draft and Create the SysRS) is complete, closing out the feature. The retrospective System Requirements Specification for this repository was created via `create_sysrs` as SYSRS document `8d752304-b076-4bad-89af-f8032158dd21` ("System Requirements Specification: biz.dfch.SpecMgr"), preceded by a passing `validate_sysrs(content, full=True)` dry run and followed by a confirming `get_sysrs` round-trip. It cross-references both `gol` documents under `## Business Context and Goals`, all 10 Functional-Suitability and 4 Maintainability `req` documents under `## Requirements`, and 8 already-accepted, architecturally significant `adr` documents under `## Decisions`; the other 7 ISO/IEC 25010:2023 characteristics and several optional sections (`## Stakeholder Needs and Elicitation`, `### Problem Statement`, `## Operational Concept and Scenarios`, `## Risks`, `## Other Characteristics`, `## Verification`) are omitted with the documented reason recorded in the SysRS's own `## More Information` section, per the Phase 2 gap analysis. A new `### Design Notes` section (Task 3.4/ACC-005) was added to this feature plan, between `### Scope` and `### Task List`, spelling out the six-step regeneration/refresh checklist for keeping the SysRS current as new domains, goals, and decisions are added. All four Phase 3 tasks and all five acceptance criteria (ACC-001 through ACC-005) are checked off above.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 00:00:00.000Z - Phase 3 Draft and Create the SysRS complete

Completed Task 3.1 (assembled the SysRS body following `specmgr://sysrs/template`/`specmgr://sysrs/example`'s structure and the `specmgr://sysrs/schema`'s mandatory/optional rules), Task 3.2 (ran `validate_sysrs(content, full=True)` on the assembled document with placeholder frontmatter and it passed cleanly on the first attempt), Task 3.3 (called `create_sysrs`, which persisted SYSRS document `8d752304-b076-4bad-89af-f8032158dd21`, "System Requirements Specification: biz.dfch.SpecMgr", and a follow-up `get_sysrs` confirmed a clean round-trip), and Task 3.4 (added a new `### Design Notes` section to this feature plan, between `### Scope` and `### Task List`, documenting a six-step regeneration/refresh checklist for keeping the SysRS current). The finished SysRS cross-references both `gol` documents and all 14 `req` documents from Phase 2 under `## Business Context and Goals`/`## Requirements`, plus 8 already-accepted ADRs (domain-first hierarchy, filesystem-is-source-of-truth, id/addressing scheme, generic markdown parsing, generic dispatch tools, paged listing, tool-based id reads, and `.specmgr` feature-driven artifacts) under `## Decisions`; the 7 ISO/IEC 25010:2023 characteristics with no backing `REQ` and the six optional sections with no backing `qa`/`prb`/`uc`/`rsk`/`vcr` document are all omitted with the documented reason recorded in the SysRS's own `## More Information` section. All four Phase 3 tasks and all five acceptance criteria (ACC-001 through ACC-005) are now checked off; this closes the feature's task list, though the frontmatter `status` field is left for the orchestrator to change.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 00:00:00.000Z - Scope set to one-time SysRS plus reusable regeneration workflow

Decided the feature covers producing a single retrospective SysRS document for this repo AND documenting a short, repeatable procedure for refreshing it later, rather than a pure one-off deliverable.

#### 2026-09-03 00:00:00.000Z - Mine all existing domains as source material

Decided to mine `src/`, `AGENTS.md`, every `.specmgr/feat/*/README.md`, and any existing `gol`/`req`/`uc`/`rsk`/`dec`/`adr`/`vcr` documents on disk as source material, rather than limiting discovery to `.specmgr/feat` and code alone.

### Related PRs / Commits

- [Issue #84](https://github.com/dfch/biz.dfch.SpecMgr/issues/84): tracking issue for this feature.
