---
classification: null
created: '2026-10-03T07:27:21.033+02:00'
id: feat-152-ref-skill
status: planning
type: feat
updated: '2026-10-03T08:33:39.296+02:00'
version: 1.0.0
---

# Feature: Agent-Initiated Cross-Reference Retrieval via opencode Skill (specmgr-refs)

## Plan

### Overview

feat-144-ref-artifact shipped the specmgr cross-reference retrieval stack: the generic `list_references` MCP tool, the project-local `/refs` opencode command, and the read-only `ref-finder` subagent. Two gaps remain for agents that need to retrieve references while working: (1) trigger asymmetry — `/refs` is user-initiated and only fires when a human types the command, so an agent mid-task has no context-triggered way to discover the convention and the tool; an opencode skill, whose description is always present in the agent's system prompt and loads itself when the task matches, closes exactly this gap. (2) single-document scope — the command and subagent only answer "what does document X reference?"; workflows that compose `list_references` (multi-hop graph traversal, batch resolution validation across the registry, reverse lookup of "which documents reference X") are codified nowhere, so an agent asked any of these improvises the loops, pagination, dedup, and presentation every time. This feature adds a thin project-local opencode skill (`.opencode/skills/specmgr-refs/SKILL.md`) that acts as a router, not a re-implementation: single-document requests go to `list_references` directly (or delegate to `ref-finder` / `/refs`), graph/batch/reverse requests follow codified composition workflows, and the skill keeps the read-only posture and reporting conventions of the existing `ref-finder` agent.

### Requirements

- REQ-001: A new project-local opencode skill `.opencode/skills/specmgr-refs/SKILL.md` exists, with a description matching specmgr cross-reference retrieval task phrasings so the agent loads it mid-task without user initiation.
- REQ-002: The skill acts as a router, not a re-implementation: single-document reference retrieval is delegated to the existing `list_references` tool (or the `ref-finder` subagent / `/refs` command), and the skill body never copies `ref-finder`'s workflow narrative (pointer, not duplication).
- REQ-003: The skill codifies a multi-hop graph traversal workflow (e.g. "show me this sysrs's reference graph, two levels deep"): per-level `list_references` calls, seen-set dedup, pagination while `truncated`, **NOT FOUND** flagging, and tabular reporting.
- REQ-004: The skill codifies a batch resolution validation workflow (e.g. "do all cross-references across the registry resolve on disk?"): iterate `list_<d>` over the whole-body domains (the `list_references` source-domain enum additionally accepts `adr` — deliberately excluded here, see Design Notes), run `list_references` per document, aggregate per-domain and overall `total`/`error_count`, and flag every unresolvable reference.
- REQ-005: The skill codifies a reverse lookup workflow (e.g. "which documents reference REQ `<uuid>`?"): scan candidate documents via paged `list_<d>` plus per-document `list_references`, match on the target `(type, id)`, and report the referencing documents with `type`/`id`/`title`/`path`.
- REQ-006: The skill preserves `ref-finder`'s read-only posture (no edit/write/commit) and reporting conventions (`type`/`id`/`title`/`path` per reference, **NOT FOUND** prefix for unresolvable references, stated `total` and `error_count`).
- REQ-007: Registration and documentation: `AGENTS.md` registers the skill in its `list_references` tool entry (following the existing `repair`-skill registration pattern), the root `README.md` documents it in its `## Referencing Artifacts` section alongside the `/refs` command and the `ref-finder` subagent, `CHANGELOG.md` records the addition, and the skill file conforms to the project-local `.opencode` skill conventions (same shape as the existing `repair` and `feat-numbering` skills).
- REQ-008: A drift-guard consistency test `tests/opencode/test_skill_specmgr_refs.py` (structure per `tests/opencode/test_skill_feat_numbering.py`) pins the skill's load-bearing wording so it cannot silently drift from the feat-144 contract: the file location; frontmatter exactly `name`/`description` with `name` equal to the containing folder and a third-person `description` carrying the trigger keywords; the inherited reporting vocabulary (**NOT FOUND** prefix, `type`/`id`/`title`/`path` row fields, stated `total`/`error_count`/`truncated`); and the single-document delegation pointer naming `list_references`/`ref-finder`/`/refs`.

### Acceptance Criteria

- [ ] ACC-001: The skill's description matches reference-retrieval phrasings (e.g. "which documents reference X", "show me the reference graph", "do all cross-references resolve") well enough that the agent loads the skill unprompted in matching mid-task contexts.
- [ ] ACC-002: The single-document, graph, batch, and reverse workflows are each covered by exactly one codified path in the skill, with no overlapping or contradictory instructions.
- [ ] ACC-003: The skill body contains no narrative duplication of `ref-finder`'s workflow — single-document handling is a pointer/delegation, not a copy.
- [ ] ACC-004: All four workflows execute successfully against live specmgr documents in this repository (smoke exercise), reporting expected rows with **NOT FOUND** flagging.
- [ ] ACC-005: The REQ-008 consistency test exists, pins the location, frontmatter, trigger keywords, reporting vocabulary, and delegation pointer as listed, and passes under the repository quality gate's `pytest` run (the mechanical counterpart of REQ-002/REQ-006).

### Scope

#### Included

- The skill file `.opencode/skills/specmgr-refs/SKILL.md` (description + router body)
- The codified workflows: single-document, multi-hop graph traversal, batch resolution validation, reverse lookup
- Read-only posture and `ref-finder` reporting conventions preserved in the skill
- The drift-guard consistency test `tests/opencode/test_skill_specmgr_refs.py`
- Documentation: `AGENTS.md` registration + root `README.md` `## Referencing Artifacts` mention + `CHANGELOG.md` entry
- This feature's plan folder (`.specmgr/feat/feat-152-ref-skill/`)

#### Explicitly Out Of Scope

- New MCP capabilities (e.g. `reverse`/`depth` parameters on `list_references`) — client-agnostic feature work, its own issue if pursued
- Changes to the `list_references` tool, the `/refs` command, or the `ref-finder` subagent (beyond pure pointer/reference fixes)
- Packaging or distribution outside the repository (the skill lives in the project-local `.opencode` tree; no PyPI impact)
- Non-opencode client support (the skill is opencode-specific; the MCP tools remain the client-agnostic surface)
- ADR-inclusive batch validation (iterating `list_adr` for the REQ-004 workflow) — recorded deliberate scoping decision, see Design Notes

### Dependencies

#### Depends On

- feat-144-ref-artifact (done) — the skill routes to its `list_references` tool, `/refs` command, and `ref-finder` subagent

#### Blocks

- none

### Design Notes

- Router, not re-implementation: the skill's body is a decision table over task shape. Single-document retrieval is a pointer to the existing `list_references` tool / `ref-finder` subagent / `/refs` command (no narrative copy, so the two do not drift apart). Graph, batch, and reverse are the only three compositions codified, each as one numbered workflow (loops + seen-set dedup + pagination while `truncated` + **NOT FOUND** flagging + tabular reporting with stated `total`/`error_count`).
- Trigger mechanism: the skill's description is the always-present surface (opencode lists it in the agent's system prompt and loads the skill when the task matches); it is written to match reference-retrieval phrasings, not implementation vocabulary.
- Layering: project-local `.opencode` tree (like feat-144's command + agent), config not `src/` — no packaging, no PyPI, no CI impact; the client-agnostic surface stays the MCP tools.
- Read-only posture: the skill instructs retrieval and reporting only — no edit/write/commit — consistent with `ref-finder`'s denied-permission model.
- Directory choice: the skill lives at the plural `.opencode/skills/specmgr-refs/` path, following the `feat-numbering` precedent (the repo's newest skill, feat-163); OpenCode discovers both singular and plural project skill directories, and the first skill (`repair`, feat-150) uses the singular `.opencode/skill/` — the newest-skill precedent wins.
- Batch workflow scoping (REQ-004): the batch validation iterates the 12 whole-body domains only. The `list_references` source-domain enum additionally accepts `adr`, and ADR documents can carry outbound `<TYPE> <uuid>` references — the exclusion is deliberate, since `adr` is slated for removal (GitHub issue #46) and the workflow targets the whole-body registry; an ADR-inclusive registry-wide check would add a `list_adr` iteration and is out of scope here.
- Reverse lookup cost (REQ-005): the reverse lookup is an O(registry-size) scan — paged `list_<d>` over the 12 whole-body domains plus one `list_references` call per document — and no domain can be pre-filtered, because the extractor regex-scans every body for the 10-tag reference vocabulary. The skill body states this cost expectation so an implementer does not "optimize" the scan by skipping domains.

### Related Decisions

- ADR e369ee2e-3353-4f92-991c-6367d76d832e: development artifacts in `.specmgr` with feature-driven work units (this plan folder follows it)
- feat-144-ref-artifact planning decision: opencode-specific surface (command + agent) lives under the project-local `.opencode` tree — this skill adopts the same layering

### Task List

#### Phase 100: Design

- [ ] Task 100.100: Lock the skill description wording against reference-retrieval phrasings (trigger match)
- [ ] Task 100.110: Draft the router body: single-document delegation + the codified graph, batch, and reverse workflows
- [ ] Task 100.120: Cross-check the draft against `ref-finder` conventions (pointer not copy; reporting vocabulary)
- [ ] Task 100.130: Draft the consistency-test pin list (location, frontmatter, trigger keywords, reporting vocabulary, delegation pointer)

#### Phase 110: Implementation

- [ ] Task 110.100: Create `.opencode/skills/specmgr-refs/SKILL.md`
- [ ] Task 110.110: Register the skill in `AGENTS.md` and the root `README.md` `## Referencing Artifacts` section, and record it in `CHANGELOG.md`
- [ ] Task 110.120: Create `tests/opencode/test_skill_specmgr_refs.py` per the Task 100.130 pin list

#### Phase 120: Verification

- [ ] Task 120.100: Smoke-exercise the single-document, graph, batch, and reverse workflows against live documents
- [ ] Task 120.110: Verify the skill loads unprompted in a matching context (description match check)
- [ ] Task 120.120: Run the repository quality gate (`ruff format --check`, `ruff check`, `vulture`, `pytest -n auto`, doc drift checks)

#### Phase 130: Closeout

- [ ] Task 130.100: Update this feature's Progress (check off ACCs, advance status via the generic `set_status`)

## Progress

### Current Status

**As of 2026-10-03**: Planning. Issue #152 analyzed; the upstream feat-144 stack (`list_references` tool, `/refs` command, `ref-finder` subagent) is shipped and available to route to. No skill file exists yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-03T06:30:34.899Z - Plan revised after review pass

Plan review pass (feat-reviewer) findings folded in: REQ-004 records the deliberate `adr` source-domain exclusion (new Out-Of-Scope bullet + Design Note); REQ-007's registration anchors corrected — `AGENTS.md`'s `list_references` entry per the existing `repair`-skill pattern, and the root `README.md` `## Referencing Artifacts` section added to the doc scope (the "alongside `/refs` and `ref-finder` in `AGENTS.md`" premise was inaccurate); ACC-004 trimmed of its trivially-true plan-folder clause; new REQ-008/ACC-005 + Tasks 100.130/110.120 add the drift-guard consistency test `tests/opencode/test_skill_specmgr_refs.py` (feat-163 precedent); Design Notes record the directory-choice and reverse-lookup-cost rationale; the Created entry heading re-synced to the frontmatter `created` timestamp.

#### 2026-10-03T05:27:21.033Z - Created

Feature plan created for GitHub issue #152 (agent-initiated specmgr cross-reference retrieval via an opencode skill), routing on the feat-144-ref-artifact stack.

### Related PRs / Commits

- GitHub issue #152 — https://github.com/dfch/biz.dfch.SpecMgr/issues/152 (the feature request this plan tracks)
