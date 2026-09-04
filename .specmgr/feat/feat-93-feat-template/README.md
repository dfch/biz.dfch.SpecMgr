---
classification: null
created: '2026-09-04 10:00:51.149+02:00'
id: feat-93-feat-template
status: done
type: feat
updated: '2026-09-04 11:15:00.000+02:00'
version: 1.0.0
---

# Feature: Consolidate Feature Templates/Examples onto the feat MCP Tools

## Plan

### Overview

Three diverging copies of the "feature template / example" concept exist in the repo, when the intended canonical source is the feature tools shipped as packaged, tested, versioned data: the embedded `src/biz/dfch/specmgr/feat/data/feat_template.md` skeleton, the orphaned on-disk `.specmgr/_template/v1/README.md` copy with zero consumers, and a verbatim fenced copy of the old bare template inside ADR e369ee2e. This feature removes the orphaned duplicates so there is exactly one canonical place to obtain a feature template/example: the `get_feat_template` / `get_feat_example` feature tools.

### Requirements

- REQ-001: Delete `.specmgr/_template/v1/README.md` and confirm no `src/` or `tests/` file references it.
- REQ-002: Remove the verbatim fenced template blocks from ADR e369ee2e (lines 77–191 and 233–344) and replace them with a pointer noting the up-to-date template lives at the `get_feat_template` / `get_feat_example` feature tools.
- REQ-003: Update the AGENTS.md `feat` template bullet so it points at `get_feat_template` / `get_feat_example` and states the tools are the canonical source (tools live in `data/`, no copied `_template` file).
- REQ-004: Regenerate `docs/MCP.md` and `docs/GENERATED.md` to reflect the AGENTS.md change.
- REQ-005: Keep both tools (`get_feat_template` as the structural skeleton, `get_feat_example` as the complete valid instance) and pass the full unit-test suite unchanged.

### Acceptance Criteria

- [ ] ACC-001: `validate_feat(content, full=True)` passes with no errors on the drafted document before `create_feat` is called.
- [ ] ACC-002: `.specmgr/_template/v1/README.md` is deleted; no `src/` or `tests/` file references it.
- [ ] ACC-003: ADR e369ee2e no longer embeds the fenced template blocks and ends with a pointer noting the up-to-date template lives at the `get_feat_template` / `get_feat_example` feature tools.
- [ ] ACC-004: AGENTS.md `feat` template bullet points at `get_feat_template` / `get_feat_example` and states the tools are the canonical source.
- [ ] ACC-005: `docs/MCP.md` / `docs/GENERATED.md` are regenerated and the full unit-test suite passes unchanged.

### Scope

#### Included

- Locating all diverging copies of the feature template/example concept (embedded `feat_template.md`, orphaned `.specmgr/_template/v1/README.md`, and the ADR e369ee2e fenced block).
- Deleting the orphaned on-disk `.specmgr/_template/v1/README.md` copy and verifying no `src/` or `tests/` file references it.
- Editing ADR e369ee2e to drop the verbatim fenced template blocks while keeping its folder-structure/prose decision content, and appending a pointer to the canonical tools.
- Updating the AGENTS.md `feat` template bullet to point at the canonical tools.
- Regenerating `docs/MCP.md` / `docs/GENERATED.md` and running the full unit-test suite.

#### Explicitly Out Of Scope

- Changing the behavior or content of the `get_feat_template` / `get_feat_example` tools themselves; both tools are kept as-is.
- Removing either feature tool or merging them into a single entry point.
- Any unrelated cleanup of `.specmgr/` or the docs tree.

### Dependencies

#### Depends On

- ADR e369ee2e (Organize development artifacts in `.specmgr`): the source of the orphaned on-disk template copy and the verbatim fenced block being removed.

#### Blocks

- Any future work that assumes `.specmgr/_template/v1/README.md` is a live, consumable template.

### Design Notes

The canonical source of truth for a feature template/example is the packaged data behind `get_feat_template` / `get_feat_example` (files under `src/biz/dfch/specmgr/feat/data/`). The on-disk `.specmgr/_template/v1/README.md` is a hand-copied artifact with no code consumer, and ADR e369ee2e embeds a verbatim fenced copy that drifts from the canonical tool output. Removing both keeps a single source of truth without touching the tools. The historical CHANGELOG reference in feat-38-39-41-43-44 is a historical record, not a live pointer, and is left intact.

### Related Decisions

- e369ee2e-xxxx-xxxx-xxxx-xxxxxxxxxxxx (ADR): Organize development artifacts in `.specmgr` — the ADR that introduced the on-disk template copy and now hosts the verbatim fenced block being removed.

### Task List

#### Phase 1: Discovery ✅ DONE

- [x] Task 1.1: Locate all diverging copies of the feature template/example concept and confirm the canonical `feat_template.md` / `feat_example.md` data files.
- [x] Task 1.2: Scan `src/` and `tests/` for any reference to `.specmgr/_template/v1/README.md`.
- [x] Task 1.3: Confirm the exact fenced template blocks and line ranges inside ADR e369ee2e.

#### Phase 2: Implementation

- [x] Task 2.1: Delete `.specmgr/_template/v1/README.md`.
- [x] Task 2.2: Edit ADR e369ee2e to drop the verbatim fenced template blocks and append a pointer to the canonical tools.
- [x] Task 2.3: Update the AGENTS.md `feat` template bullet to point at the canonical tools.

#### Phase 3: Verification

- [x] Task 3.1: Regenerate `docs/MCP.md` / `docs/GENERATED.md`.
- [x] Task 3.2: Run the full unit-test suite and confirm it passes unchanged.
- [x] Task 3.3: Dry-run `validate_feat(content, full=True)` on this feature's body.

## Progress

### Current Status

**As of 2026-09-04 10:15**: Phase 1 (Discovery) is complete. All three diverging copies located and confirmed; the orphaned `.specmgr/_template/v1/README.md` has zero `src/`/`tests/` consumers; ADR e369ee2e's fenced blocks mapped. No code changes made yet. Phase 2 (Implementation) is next.

**As of 2026-09-04 10:45**: Phase 2 (Implementation) is complete. Deleted `.specmgr/_template/v1/README.md`; removed the three verbatim fenced template blocks from ADR e369ee2e and updated its Option 1 "Template location" open question plus appended a pointer note to the canonical tools; updated the AGENTS.md `feat` template bullet and `.specmgr/` directory tree. Phase 3 (Verification) is next.

**As of 2026-09-04 11:15**: Phase 3 (Verification) is complete and the feature is **done**. Full unit-test suite: 3318 tests, OK (unchanged from baseline). `specmgr docs` + `specmgr adr-toc` ran clean with no changes to `docs/MCP.md`/`docs/GENERATED.md` (those are generated from source docstrings; Phase 2 only touched AGENTS.md, not source). `validate_feat(content, full=True)` on this feature's body parses cleanly. Note: the `### Decisions Made` section was migrated from markdown-rendered `- **[date]**:` bullets to the canonical `#### {timestamp} ( - | : ) {title}` H4 heading format required by the feat parser — without it `parse_feat` raised an `AssertionError` on `DecisionEntry`. `ruff format --check` + `ruff check` both pass.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 10:45:00.000+02:00 - Verification complete

Phase 3 (Verification) done. (1) Ran `specmgr docs` + `specadr adr-toc` — both exited cleanly and produced **no changes** to `docs/MCP.md`/`docs/GENERATED.md` (those files are generated from source docstrings; Phase 2 only edited AGENTS.md, not source, so no drift). (2) Full unit-test suite: **3318 tests, OK** (unchanged from baseline). (3) `validate_feat(content, full=True)` on this feature's body: **parses cleanly**. Note: the README's `### Decisions Made` section was migrated from markdown-rendered `- **[date]**:` bullets to the canonical `#### {timestamp} ( - | : ) {title}` H4 heading format required by `feat/models/v1` (matching `feat/data/feat_example.md`); without this the body failed `parse_feat` with an `AssertionError` on `DecisionEntry`. (4) `ruff format --check` + `ruff check` both pass.

#### 2026-09-04 10:45:00.000+02:00 - Implementation complete

Phase 2 (Implementation) done. (1) Deleted `.specmgr/_template/v1/README.md` (110 lines, zero consumers) via `git rm`. (2) ADR e369ee2e: removed the three verbatim fenced template blocks (Option 1 README.md block lines 77–190, Option 2 README.md block lines 233–292, Option 2 progress.md block lines 294–343), updated the Option 1 "Template location" open question to point at the canonical `get_feat_template`/`get_feat_example` tools, and appended a feat-93 pointer note at the end of the ADR. (3) AGENTS.md: rewrote the `feat` "Template" bullet to point at the canonical tools and dropped the `_template/v1/README.md` entry from the `.specmgr/` directory tree. `src/biz/dfch/specmgr/feat/data/` and the tools untouched. Phase 3 (Verification) is next.

#### 2026-09-04 10:15:00.000+02:00 - Discovery complete

Phase 1 (Discovery) done. Confirmed three diverging copies: (1) canonical `src/biz/dfch/specmgr/feat/data/feat_template.md` (1980 B) + `feat_example.md` (2423 B) under `feat/data/`; (2) orphaned `.specmgr/_template/v1/README.md` (110 lines, 2849 B, zero code consumers); (3) verbatim fenced template blocks inside ADR e369ee2e. `grep -rn "_template/v1" src/ tests/` returns no matches (exit 1). ADR e369ee2e fenced blocks: Option 1 README.md block lines 79–190; Option 2 README.md block lines 235–292 and progress.md block lines 296–343.

#### 2026-09-04 10:00:00.000+02:00 - Created

Feature scaffolded from GitHub issue #93 ("Consolidate feature templates/examples onto the feat MCP tools"). Scope, requirements, acceptance criteria, and a 3-phase task list were captured; discovery work has not started yet.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 10:45:00.000+02:00 : Canonical source is the packaged feat tools

Confirmed the canonical source is the packaged `feat/data/feat_template.md` + `feat_example.md` behind `get_feat_template`/`get_feat_example`; the `.specmgr/_template/v1/README.md` orphan and ADR e369ee2e fenced blocks are removable duplicates with zero `src/`/`tests/` consumers. Rationale: Phase 1 discovery (`grep -rn "_template/v1" src/ tests/` = no matches, exit 1) shows no code consumers, so removing them preserves the full unit-test suite unchanged.

#### 2026-09-04 10:45:00.000+02:00 : ADR e369ee2e keeps a pointer note, not a verbatim copy

Kept the removed template blocks in ADR e369ee2e as a historical-reference blockquote note (not deleted from the ADR body) so the ADR's decision narrative stays intact and traceable. Rationale: the ADR documents *why* the structure was chosen; the old bare templates are historical, not live references, so a short pointer note (not a verbatim fenced copy) is the right level of fidelity without re-introducing a drifting duplicate.
