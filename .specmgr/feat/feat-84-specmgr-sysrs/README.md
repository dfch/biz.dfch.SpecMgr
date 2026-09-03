---
classification: null
created: '2026-09-03 10:00:47.481+02:00'
id: feat-84-specmgr-sysrs
status: planning
type: feat
updated: '2026-09-03 10:04:36.472+02:00'
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

- [ ] ACC-001: `validate_sysrs(content, full=True)` passes with no errors on the drafted document before `create_sysrs` is called.
- [ ] ACC-002: Every one of the 9 ISO/IEC 25010:2023 characteristic sections under `## Requirements` references at least one existing `REQ` id, or is explicitly left empty with a documented reason.
- [ ] ACC-003: Every implemented domain package listed in `AGENTS.md`'s Status section is represented by at least one `REQ`/`GOL`/`DEC`/`UC` bullet somewhere in the SysRS.
- [ ] ACC-004: Any information gaps identified during drafting were resolved by asking the user (via the `question` tool) and are reflected in the final document, not left as placeholders.
- [ ] ACC-005: The regeneration workflow/checklist is written down (in this feature's Design Notes, added later) and can be followed without re-deriving it from scratch.

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

### Task List

#### Phase 1: Discovery

- [x] Task 1.1: Read `AGENTS.md` and the source tree under `src/` to build a domain-package inventory.
- [x] Task 1.2: Read every `.specmgr/feat/*/README.md` and extract requirements, decisions, and scope already captured there.
- [x] Task 1.3: Enumerate any existing `gol`/`req`/`uc`/`rsk`/`dec`/`adr`/`vcr` documents on disk via their `list_<d>` tools and record their ids/titles.

#### Phase 2: Gap-Filling

- [ ] Task 2.1: Identify SysRS sections (Goals, Decisions, Requirements per ISO 25010 characteristic, Other Characteristics) that have no corresponding existing artifact.
- [ ] Task 2.2: Ask the user via the `question` tool to resolve each identified gap.
- [ ] Task 2.3: Create any minimal prerequisite `GOL`/`REQ`/`DEC` documents needed to back a SysRS cross-reference bullet.

#### Phase 3: Draft and Create the SysRS

- [ ] Task 3.1: Assemble the SysRS body per `specmgr://sysrs/template`/`specmgr://sysrs/example` and the `specmgr://sysrs/schema`.
- [ ] Task 3.2: Run `validate_sysrs(content, full=True)` and fix any reported issues.
- [ ] Task 3.3: Call `create_sysrs` to persist the document.
- [ ] Task 3.4: Write down the regeneration workflow (e.g. in this feature's Design Notes via the `update` tool) for future refreshes.

## Progress

### Current Status

**As of 2026-09-03**: Phase 1 (Discovery) is complete. Read `AGENTS.md` in full and confirmed the domain-package inventory it documents (13 domain/cross-cutting packages: adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs, plus the cross-cutting `general` package). Read all 33 other `.specmgr/feat/*/README.md` feature folders in full (34 total including this one) and extracted their requirements/decisions/scope. Enumerated existing domain documents on disk via `list_gol`/`list_req`/`list_uc`/`list_rsk`/`list_dec`/`list_adr`/`list_vcr`: only `adr` has documents (28 accepted ADRs); `gol`/`req`/`uc`/`rsk`/`dec`/`vcr` all have zero documents on disk. This confirms Phase 2 (Gap-Filling) will need to create prerequisite `GOL`/`REQ`/`DEC` documents from scratch, since no reusable cross-reference targets exist yet for those six domains. Next step is Phase 2 (Gap-Filling).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 00:00:00.000Z - Phase 1 Discovery complete

Completed Task 1.1 (read `AGENTS.md` and confirmed the `src/` domain-package inventory: 13 domain/cross-cutting packages -- adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs -- plus the cross-cutting `general` package), Task 1.2 (read all 33 other feature folders under `.specmgr/feat/` in full and extracted their requirements/decisions/scope -- notable prior art: feat-32-sysrs designed the `sysrs` schema itself; feat-18-goal/feat-6-requirement-artifact/feat-21-decision designed the `gol`/`req`/`dec` domains this feature will need to create documents in), and Task 1.3 (enumerated existing documents via `list_gol`/`list_req`/`list_uc`/`list_rsk`/`list_dec`/`list_adr`/`list_vcr`: `gol`=0, `req`=0, `uc`=0, `rsk`=0, `dec`=0, `vcr`=0, `adr`=28 accepted ADRs). No documents currently exist for `gol`/`req`/`uc`/`rsk`/`dec`/`vcr` on disk, so Phase 2 will need to create minimal prerequisite documents from scratch rather than reusing existing ids.

#### 2026-09-03 00:00:00.000Z - Created

Feature scaffolded from GitHub issue #84 ("Create SysRS from existing code base and features"). Scope, requirements, acceptance criteria, and a 3-phase task list were captured; discovery work has not started yet.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 00:00:00.000Z - Scope set to one-time SysRS plus reusable regeneration workflow

Decided the feature covers producing a single retrospective SysRS document for this repo AND documenting a short, repeatable procedure for refreshing it later, rather than a pure one-off deliverable.

#### 2026-09-03 00:00:00.000Z - Mine all existing domains as source material

Decided to mine `src/`, `AGENTS.md`, every `.specmgr/feat/*/README.md`, and any existing `gol`/`req`/`uc`/`rsk`/`dec`/`adr`/`vcr` documents on disk as source material, rather than limiting discovery to `.specmgr/feat` and code alone.

### Related PRs / Commits

- [Issue #84](https://github.com/dfch/biz.dfch.SpecMgr/issues/84): tracking issue for this feature.
