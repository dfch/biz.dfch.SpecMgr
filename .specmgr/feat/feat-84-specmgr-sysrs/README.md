---
classification: null
created: '2026-09-03 10:00:47.481+02:00'
id: feat-84-specmgr-sysrs
status: planning
type: feat
updated: '2026-09-03 10:29:55.382+02:00'
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

- [x] Task 2.1: Identify SysRS sections (Goals, Decisions, Requirements per ISO 25010 characteristic, Other Characteristics) that have no corresponding existing artifact.
- [x] Task 2.2: Ask the user via the `question` tool to resolve each identified gap.
- [x] Task 2.3: Create any minimal prerequisite `GOL`/`REQ`/`DEC` documents needed to back a SysRS cross-reference bullet.

#### Phase 3: Draft and Create the SysRS

- [ ] Task 3.1: Assemble the SysRS body per `specmgr://sysrs/template`/`specmgr://sysrs/example` and the `specmgr://sysrs/schema`.
- [ ] Task 3.2: Run `validate_sysrs(content, full=True)` and fix any reported issues.
- [ ] Task 3.3: Call `create_sysrs` to persist the document.
- [ ] Task 3.4: Write down the regeneration workflow (e.g. in this feature's Design Notes via the `update` tool) for future refreshes.

## Progress

### Current Status

**As of 2026-09-03**: Phase 2 (Gap-Filling) is complete. Recorded the gap analysis (Task 2.1): the `## Decisions` section will cross-reference existing ADRs directly (no new DEC documents needed); the optional `## Stakeholder Needs and Elicitation` (QA), `## Operational Concept and Scenarios` (UC), `## Risks` (RSK), `## Verification` (VCR), `### Problem Statement` (PRB), and `## Other Characteristics` sections will all be omitted from the SysRS with a documented reason, since no `qa`/`uc`/`rsk`/`vcr`/`prb` documents exist and none are needed to satisfy the acceptance criteria. No `question`-tool interactions were needed (Task 2.2): every GOL/REQ content gap was resolvable directly from `README.md`/`AGENTS.md`/`.specmgr/feat/*/README.md` without inventing content. Created (Task 2.3) 2 `GOL` documents (`08666592-a2d2-4309-95c6-3c94248ca342` "AI-Agent-Native Specification Artifact Management", `b663528e-08c5-426b-9f20-32192c0a3bdb` "Cross-Referenceable, Non-Duplicating Specification Artifacts") and 14 `REQ` documents, one per domain package listed in `AGENTS.md`'s Status section (adr, req, uc, tsk, qa, prb, gol, rsk, dec, feat -- Functional Suitability; sop, vcr, sysrs, general -- Maintainability), each validated with `validate_req`/`validate_gol` before `create_req`/`create_gol`. `list_gol`/`list_req` confirm exactly 2 and 14 documents on disk. Next step is Phase 3 (Draft and Create the SysRS).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 00:00:00.000Z - Phase 2 Gap-Filling complete

Completed Task 2.1 (recorded the gap analysis carried over from Phase 1 discovery/orchestrator decisions: the SysRS `## Decisions` section will cross-reference existing ADRs directly rather than creating new `dec` documents; the optional `## Stakeholder Needs and Elicitation`, `## Operational Concept and Scenarios`, `## Risks`, `## Verification`, `### Problem Statement`, and `## Other Characteristics` sections will all be omitted from the SysRS in Phase 3, with the reason -- no `qa`/`uc`/`rsk`/`vcr`/`prb` documents exist on disk and none are needed to satisfy ACC-001..ACC-005 -- documented here), Task 2.2 (no `question`-tool interaction was required: every GOL/REQ content gap encountered while drafting was resolvable directly from `README.md`'s stated project purpose and `AGENTS.md`'s per-domain Status section descriptions, without inventing unsupported content), and Task 2.3 (created the minimal prerequisite documents: 2 `GOL` documents via `create_gol`, each preceded by a passing `validate_gol` call -- `08666592-a2d2-4309-95c6-3c94248ca342` "AI-Agent-Native Specification Artifact Management" grounded in README.md's stated purpose ("An artifact manager for system specifications" / "an MCP server that you can use to manage different specification artifacts"), and `b663528e-08c5-426b-9f20-32192c0a3bdb` "Cross-Referenceable, Non-Duplicating Specification Artifacts" grounded in AGENTS.md's domain-first architecture description and the `sysrs` domain's cross-reference-only design; and 14 `REQ` documents via `create_req`, each preceded by a passing `validate_req` call, one per domain package in `AGENTS.md`'s Status section, each with a `## Related Artifacts` -> `### Goals` link back to whichever GOL above it serves -- Functional Suitability (10, linked to GOL `08666592-a2d2-4309-95c6-3c94248ca342`): `678319da-f8e6-4f65-8f98-1096024012af` "Architecture Decision Record Document Management" (adr), `64065cad-bb84-45c4-9e18-b2a8c5ce6865` "Requirement Document Management" (req), `594afce9-7166-47b2-8e8f-788b9ed68c8e` "Use Case Document Management" (uc), `c097fcb4-9bbd-41f8-b774-b2afdcb8ecb9` "Task List Document Management" (tsk), `152d608b-ea4c-463b-8183-33332fb41e50` "Requirements-Elicitation Question and Answer Document Management" (qa), `f4180953-9f1b-45a5-8474-8d15a5872d49` "Problem Statement Document Management" (prb), `7c0e56e2-3fa5-437e-b886-1be32b142292` "Goal Document Management" (gol), `bb018715-f9e6-4ae6-830c-58e40162ac70` "Risk Register Document Management" (rsk), `1b6975fb-f5c2-4a16-b9db-9f026b8e6912` "General Decision Document Management" (dec), `ccbf7ade-7d9e-4b2e-9868-0740bdc0e824` "Feature Folder Document Management" (feat); Maintainability (4, linked to GOL `b663528e-08c5-426b-9f20-32192c0a3bdb`): `3bbe6a0e-038c-4abb-987c-79d4db8abd51` "Standard Operating Procedure Document Management" (sop), `10b78b36-abad-4bfe-9281-f75677ff7d09` "Verification Case Record Document Management" (vcr), `26c37265-1a85-4b18-aada-c9e3db9574a8` "System Requirements Specification Aggregator Document Management" (sysrs), `bad7e9c7-f794-477b-b64f-ce04645c6ef3` "Generic Cross-Domain Document Dispatch Tools" (general)). `list_gol`/`list_req` were re-checked and confirm exactly 2 `GOL` and 14 `REQ` documents on disk, matching the intended counts. Next step is Phase 3 (Draft and Create the SysRS).

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
