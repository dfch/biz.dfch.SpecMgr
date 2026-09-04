---
classification: null
created: '2026-09-04 16:27:34.938+02:00'
id: feat-80-feat-id
status: planning
type: feat
updated: '2026-09-04 16:36:04.291+02:00'
version: 1.0.0
---

# Feature: Fix set_feat_id Return Shape to Match Other Write Tools

## Plan

### Overview

`set_feat_id(id, new_id)` currently returns the full `FeatDocument` (frontmatter + body) on a successful rename, unlike every other write tool converted to frontmatter-only returns in feat-69-update-context (the generic `update`/`set_status`/`set_classification` tools and all twelve per-domain `create_<d>` tools). `set_feat_id` is a bespoke, `feat`-only tool that predates and was never in scope for feat-69's enumerated tool list, so it was missed. This feature (1) fixes `set_feat_id` to return frontmatter-only, matching `create_feat`/`update`/`set_status`/`set_classification`'s shape, and (2) documents a reviewed inventory of every other MCP tool that can return a document or a piece of one (excluding `get_<d>`, which is expected to always return full documents), to confirm whether any other straggler exists beside `set_feat_id`.

### Requirements

- REQ-001: `set_feat_id` must return the domain's `FeatFrontmatter` object only (no `body`) on a successful rename, matching the return shape of `create_feat`/`update`/`set_status`/`set_classification`.

- REQ-002: `set_feat_id`'s own docstring/`description=` text must be updated to state it returns frontmatter-only, and instruct callers needing the body to call `get_feat` afterward (mirroring the other tools' existing wording).

- REQ-003: A reviewed, tool-by-tool inventory must confirm whether any other non-`get_<d>` MCP tool unintentionally returns a full document (or partial document content) where frontmatter-only would be the correct, consistent shape.

### Acceptance Criteria

- [ ] ACC-001: `set_feat_id`'s return type annotation changes from `FeatDocument` to `FeatFrontmatter`, and its implementation returns `new_frontmatter` directly (no `FeatDocument(...)` construction).

- [ ] ACC-002: `tests/feat/tools/test_set_feat_id.py` asserts `isinstance(result, FeatFrontmatter)`, `not isinstance(result, FeatDocument)`, and `not hasattr(result, "body")`, mirroring feat-69's test pattern for the other converted tools.

- [ ] ACC-003: AGENTS.md's `feat/` bullet is updated to state `set_feat_id` now returns frontmatter-only, consistent with the other write tools.

- [ ] ACC-004: `specmgr docs` is regenerated and `docs/MCP.md`/`docs/api/` reflect the new return type with no other drift.

- [ ] ACC-005: The Design Notes table below is reviewed and confirms `set_feat_id` is the only straggler among non-`get_<d>` tools; any additional straggler found is either fixed in this feature or explicitly logged as out of scope with a follow-up note.

### Scope

#### Included

- Changing `set_feat_id`'s return type/return statement in `src/biz/dfch/specmgr/feat/tools/set_feat_id.py`.

- Updating `set_feat_id`'s test assertions.

- Updating AGENTS.md's `feat/` bullet.

- Regenerating `specmgr docs` output.

- Reviewing (not necessarily changing) every other MCP tool that returns a document or part of one, to confirm no other unintentional full-document return exists.

#### Explicitly Out Of Scope

- Changing the deliberate, already-documented full-document returns: `create_adr`, `update_frontmatter`, `update_section`, the `adr` branch of `set_status`, and `get_<d>`/`get_adr` (all full-document by design, not stragglers).

- Changing `option_create`/`option_read`/`option_update`/`option_delete`/`option_list` (bare `str`/`list[str]`, not document-shaped, out of scope).

- Changing the generic `delete` tool (already returns a minimal path string, unaffected by feat-69, unaffected here).

- Publishing the tool-return-shape review as a new standalone `docs/` page or a formal AGENTS.md table -- the review lives in this feature's own Design Notes only.

### Design Notes

Tool-by-tool return-shape review (source-verified), confirming `set_feat_id` is the sole straggler:

| Tool | Current return shape | Verdict |
|---|---|---|
| `set_feat_id` | Full `FeatDocument` | **Bug -- fix in this feature** |
| `update` (12 domains) | `XxxFrontmatter` | Correct (feat-69) |
| `set_status` (12 non-adr) | `XxxFrontmatter` | Correct (feat-69) |
| `set_status` (adr branch) | Full `Adr` | Correct -- explicit design exclusion |
| `set_classification` (12 domains) | `XxxFrontmatter` | Correct (feat-69) |
| `create_<d>` (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) | `XxxFrontmatter` | Correct (feat-69) |
| `create_adr` | Full `Adr` | Correct -- explicit design exclusion |
| `get_<d>` (12) / `get_adr` | Full document (or raw str) | Correct -- always full by design, out of scope |
| `update_frontmatter` / `update_section` | Full `Adr` | Correct -- explicit design exclusion |
| `option_create` / `option_update` | Bare `str` | Correct -- not document-shaped |
| `option_read` | Bare `str` | Correct -- not document-shaped |
| `option_list` / `option_delete` | `list[str]` | Correct -- not document-shaped |
| `delete` | Path `str` | Correct -- already minimal |

The fix mirrors feat-69's mechanical recipe exactly: drop the `FeatDocument(...)` construction, change the annotation to `-> FeatFrontmatter`, `return new_frontmatter` directly, update the tool's `description=`/docstring, and add the same three-assertion test pattern (`isinstance`/`not isinstance`/`not hasattr(result, "body")`).

### Task List

#### Phase 1: Fix set_feat_id return shape

- [ ] Task 1.1: Change `set_feat_id`'s return type annotation from `FeatDocument` to `FeatFrontmatter` and return `new_frontmatter` directly in `src/biz/dfch/specmgr/feat/tools/set_feat_id.py`.

- [ ] Task 1.2: Update `set_feat_id`'s `description=`/docstring text to state the frontmatter-only return shape.

- [ ] Task 1.3: Update `tests/feat/tools/test_set_feat_id.py` with the three-assertion pattern (`isinstance(result, FeatFrontmatter)`, `not isinstance(result, FeatDocument)`, `not hasattr(result, "body")`).

- [ ] Task 1.4: Update AGENTS.md's `feat/` bullet to reflect the corrected return shape.

- [ ] Task 1.5: Run `uv run --frozen pytest -n auto`, `ruff format --check`, `ruff check`, `vulture`, and regenerate `specmgr docs`/`docs/MCP.md`; verify no drift.

## Progress

### Current Status

**As of 2026-09-04**: Feature drafted and scoped based on GitHub issue #80 and a source-code investigation confirming `set_feat_id` is the only tool with an unintentional full-document return; no implementation work has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 16:27:34.938+02:00 - Created

Feature drafted from GitHub issue #80, scoped after a source-verified review confirming `set_feat_id` as the sole straggler among non-`get_<d>` document-returning tools.

### Related PRs / Commits

- [Issue #80](https://github.com/dfch/biz.dfch.SpecMgr/issues/80): tracking issue for this feature.
