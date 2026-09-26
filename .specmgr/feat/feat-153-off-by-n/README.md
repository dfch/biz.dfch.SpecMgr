---
classification: null
created: '2026-09-26T18:33:23.901+02:00'
id: feat-153-off-by-n
status: planning
type: feat
updated: '2026-09-26T18:33:23.901+02:00'
version: 1.0.0
---

# Feature: Off-by-N line-offset corruption risk in the generic update tool

## Plan

### Overview

The generic `update` tool's line-range mode (`offset`/`limit`) addresses 1-based lines of the frontmatter-stripped body, sourced correctly only via `get_<d>(id, raw=True)`. GitHub issue #153 reports two independent gaps that let a wrong-but-in-bounds `offset` silently corrupt a document: (1) nothing warns that the on-disk file's YAML frontmatter block is variable-length, so computing a body-line offset as "raw file line number minus an assumed frontmatter length" is unsafe -- yet `feat`'s own AGENTS.md-sanctioned direct-file-editing workflow invites exactly that; and (2) `update` is "splice-then-validate-whole": a wrong offset that lands on a structurally similar line (e.g. a blank line instead of the intended list item) can still pass schema validation and is written with no feedback at all, leaving silent duplication/loss discoverable only by an unprompted manual re-read.

This feature closes issue #153 by adopting three of its four suggested fixes: (1) documenting the coordinate mismatch explicitly in `update`'s tool description and AGENTS.md's `feat` entry; (2) returning a small, bounded before/after snippet of the touched region on every successful `update` call, via a new `UpdateResult` wrapper return type; and (4) adding an opt-in `numbered` parameter to every `get_<d>(raw=True)` read so a caller can see 1-based body-line numbers without manually counting. The optional `dry_run` parameter (fix #3) is explicitly deferred -- not part of this feature.

### Requirements

- REQ-001: `update`'s tool description/docstring and AGENTS.md's `feat` entry state explicitly that a raw on-disk `.md` file's line numbers are never the same as `update`'s `offset`/`limit` body-line coordinates -- the YAML frontmatter block is variable-length -- and that the only safe source of coordinates is `get_<d>(id, raw=True)`, never a raw file read minus an assumed constant.

- REQ-002: In range mode (`offset` given), `update` returns a new wrapper result type (`UpdateResult` or similar) carrying the existing per-domain `frontmatter` plus a `snippet`: the exact lines dropped (before) and inserted (after) by the splice, plus 2 lines of unchanged context immediately above and below the touched range, each line labeled with its 1-based body-line number.

- REQ-003: In whole-body mode (no `offset`), `update` returns the same wrapper type with `snippet=None`, so the return shape is uniform across both modes and every whole-body domain.

- REQ-004: Every whole-body domain's `get_<d>` tool gains a new `numbered: bool = False` parameter, meaningful only combined with `raw=True`: when `True`, each line of the returned raw text is prefixed with its 1-based body-line number in `"<n>: "` form (mirroring this environment's own file-reading tool's convention); the default (`False`) preserves today's exact byte-verbatim `raw=True` output.

- REQ-005: `numbered=True` combined with `raw=False` raises `ValueError` before any file access, mirroring the existing rule that `offset`/`limit` combined with `raw=False` already raises `ValueError`.

- REQ-006: The tool descriptions for both `update` and every `get_<d>` explicitly warn that numbered output must never be fed back verbatim into `content` for `update`/`create_<d>` without first stripping the `"<n>: "` prefix from each line.

- REQ-007: Both changes (the REQ-002/REQ-003 snippet and the REQ-004/REQ-005 `numbered` parameter) apply uniformly across all 12 whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`); `adr` remains excluded, consistent with `update`'s existing scope.

- REQ-008: `server.py`'s module docstring, the regenerated `docs/MCP.md`, and `AGENTS.md` are updated to reflect the new `UpdateResult` return shape, the coordinate-mismatch warning, and the new `numbered` parameter.

### Acceptance Criteria

- [ ] ACC-001: `update`'s tool description text states, in prose, that the frontmatter block is variable-length and that raw on-disk file line numbers never equal `offset`/`limit` body-line coordinates; the corresponding bullet in AGENTS.md's `feat` entry carries the same warning.

- [ ] ACC-002: Calling `update(id, type, content, offset=k, limit=m)` on any of the 12 whole-body domains returns an object exposing both `frontmatter` and a non-`None` `snippet` string containing the before/after lines of the touched range plus 2 lines of context on each side, each line prefixed with its 1-based number.

- [ ] ACC-003: Calling `update(id, type, content)` with no `offset` returns the same object shape with `snippet=None`.

- [ ] ACC-004: `get_<d>(id, raw=True, numbered=True)` returns the body text with every line prefixed `"<n>: "` (1-based); `get_<d>(id, raw=True)` (default `numbered=False`) is unchanged and remains byte-identical to today's output.

- [ ] ACC-005: `get_<d>(id, raw=False, numbered=True)` raises `ValueError` before any file access, for every one of the 12 domains.

- [ ] ACC-006: The `update` and `get_<d>` tool descriptions each contain an explicit warning against feeding `numbered=True` output back as `content` without stripping the prefix.

- [ ] ACC-007: `server.py`'s docstring, `docs/MCP.md`, `docs/api/`, and AGENTS.md reflect every change above; the repo's own drift checks (`specmgr docs`) pass.

- [ ] ACC-008: The full test suite passes, including new unit tests for the snippet-window helper (boundary clamping at the start/end of the body, whole-body-mode `snippet=None`) and the numbered-line formatter, plus tool tests exercising both features across all 12 domains.

### Scope

#### Included

- An explicit coordinate-mismatch warning in `update`'s tool description and AGENTS.md's `feat` entry (fix #1).

- A new `UpdateResult`-style wrapper return type for `update`, carrying `frontmatter` + `snippet` (fix #2), with `snippet` populated in range mode only.

- A small, fixed-size (2-line) before/after snippet-window helper, shared by all 12 whole-body domain adapters.

- A new opt-in `numbered: bool = False` parameter on every domain's `get_<d>` tool, meaningful only combined with `raw=True` (fix #4).

- `ValueError` for `numbered=True` combined with `raw=False`.

- Explicit "don't feed numbered output back as content" warnings in both the `update` and `get_<d>` tool descriptions.

- `server.py` docstring, `docs/MCP.md`, `docs/api/`, and AGENTS.md updates.

- Unit and tool tests across all 12 whole-body domains.

#### Explicitly Out Of Scope

- The optional `dry_run: bool` parameter on `update` (fix #3) -- explicitly deferred, not part of this feature.

- Any change to `adr`'s own `update_section`/`option_*`/`update_frontmatter` tools (ADR stays excluded from the generic `update` tool).

- The separate generic `replace` tool proposed in feat-159-replace (a different, independent tool).

- Server-side enforcement that prevents direct raw-file hand-editing of `feat` READMEs -- the sanctioned workflow itself is unchanged; only the coordinate-computation guidance changes.

- A configurable snippet context-line count (fixed at 2 lines, not a new parameter).

### Design Notes

The snippet-window helper lives alongside `body_text`/`splice_body`/`window_body` in `general/tools/_splice.py` (or a new sibling module, e.g. `_snippet.py`, if `_splice.py` grows too large) and stays doc-type-agnostic like its neighbors. Given the pre-splice body, the `offset`/`limit` coordinates, and the post-splice body, it computes: the *before* window (the `offset..offset+limit-1` lines as they existed pre-splice, empty for a pure insert/`limit=0`), the *after* window (the lines the fragment actually occupies in the spliced result), and up to 2 lines of unchanged context immediately above and below the touched range in the *post-splice* body (clamped at the start/end of the body, mirroring `window_body`'s own clamp-not-error convention). Each returned line is labeled with its 1-based post-splice body-line number, e.g.:

```
   3: ## Some Heading
-  4: (old line that was replaced)
+  4: (new line that replaces it)
   5: (unchanged context line)
```

`update`'s return type changes from the current per-domain `FooFrontmatter` union to a new `UpdateResult` wrapper (exact name TBD during implementation) exposing `frontmatter: FooFrontmatter` and `snippet: str | None` (populated only in range mode); this is a deliberate, documented narrowing of ADR feat-69-update-context's "frontmatter-only" precedent, scoped to `update` alone -- `create_<d>`, `set_status`, and `set_classification` keep returning bare frontmatter, unchanged.

The `numbered` parameter reuses `window_body`'s existing line-splitting logic, adding an `f"{n}: "` prefix per returned line only when requested (mirroring the `<line>: <content>` convention this environment's own file-reading tool already uses) -- no change to `body_text`/`splice_body`, which stay numbering-agnostic since `update`'s range coordinates must keep addressing the *unprefixed* line count.

### Related Decisions

- ADR feat-69-update-context: established `update`'s current "frontmatter-only" return contract; this feature deliberately revises it for `update` specifically (adds a bounded `snippet` alongside `frontmatter`), without touching `create_<d>`/`set_status`/`set_classification`.

- feat-159-replace: an independent, unmerged proposal for a new exact-match `replace` tool; related in that it touches the same `general/tools/update.py`-shaped dispatch pattern, but not a dependency of this feature.

### Task List

#### Phase 1: Design

- [ ] Task 1.1: Finalize the `UpdateResult` wrapper shape and the snippet-window algorithm (before/after lines, 2-line context, boundary clamping) from this feature's Design Notes

- [ ] Task 1.2: Finalize the `numbered` parameter contract for `get_<d>` (opt-in, raw-only, `ValueError` when combined with `raw=False`) and the exact `"<n>: "` line-prefix format

#### Phase 2: Implementation -- update() snippet

- [ ] Task 2.1: Add a snippet-window helper (before/after lines + 2-line context) alongside `body_text`/`splice_body`/`window_body` in `general/tools/_splice.py`

- [ ] Task 2.2: Introduce the `UpdateResult` wrapper type and wire it through `update`'s public dispatcher and all 12 per-domain `_update_<d>` adapters (range mode populates `snippet`; whole-body mode sets `snippet=None`)

- [ ] Task 2.3: Update `update`'s tool description/docstring with the coordinate-mismatch warning (fix #1) and the "never feed a numbered read back as content" warning

#### Phase 3: Implementation -- numbered raw reads

- [ ] Task 3.1: Add the `numbered: bool = False` parameter to every one of the 12 domains' `get_<d>` tools, wired through the shared `window_body`/`body_text` helpers

- [ ] Task 3.2: Enforce `ValueError` for `numbered=True` combined with `raw=False`, before any file access

- [ ] Task 3.3: Update every `get_<d>` tool description/docstring with the numbered-format explanation and the "don't feed back verbatim" warning

#### Phase 4: Docs

- [ ] Task 4.1: Update AGENTS.md's `feat` entry (and the `general`/`update` bullet) with the coordinate-mismatch warning and the new `UpdateResult`/`numbered` capabilities

- [ ] Task 4.2: Regenerate `docs/MCP.md` and `docs/api/` via `specmgr docs`

#### Phase 5: Tests & Quality Gate

- [ ] Task 5.1: Unit tests for the snippet-window helper (before/after content, 2-line context, boundary clamping at body start/end, pure-insert/append cases)

- [ ] Task 5.2: Unit tests for the numbered-line formatter (format, default-off behavior, `ValueError` path)

- [ ] Task 5.3: Tool tests across all 12 whole-body domains for both features (happy path, whole-body-mode `snippet=None`, numbered on/off, `ValueError` paths)

- [ ] Task 5.4: Run ruff/pylint/vulture and the full test suite (phase-end quality gate)

## Progress

### Current Status

**As of 2026-09-26**: Feature drafted for GitHub issue #153; design decisions confirmed with the author (three of the issue's four suggested fixes adopted -- explicit documentation, a bounded before/after snippet via a new `UpdateResult` wrapper, and an opt-in `numbered` parameter on `get_<d>(raw=True)`; the optional `dry_run` parameter was explicitly deferred). Implementation has not started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26T12:00:00.000Z - Created

Feature drafted for GitHub issue #153 (off-by-N line-offset corruption risk in the generic `update` tool). Design decisions on which of the issue's four suggested fixes to adopt, the `UpdateResult` snippet shape, and the `numbered` raw-read parameter contract were confirmed with the author before drafting.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-26T12:00:00.000Z - Confirmed which suggested fixes to adopt and their exact shapes

Adopted fixes #1 (explicit documentation), #2 (bounded before/after snippet), and #4 (opt-in numbered raw reads) from GitHub issue #153; fix #3 (`dry_run` parameter) was explicitly deferred. The snippet is a before/after window with 2 lines of unchanged context on each side, populated only in `update`'s range mode; whole-body mode returns `snippet=None`. This requires a new `UpdateResult` wrapper return type for `update` (frontmatter + snippet), a deliberate, documented narrowing of ADR feat-69-update-context's "frontmatter-only" precedent scoped to `update` alone. The `numbered` parameter on `get_<d>` is opt-in (default `False`, preserving today's byte-verbatim `raw=True` output), meaningful only combined with `raw=True`; `numbered=True` with `raw=False` raises `ValueError`, mirroring the existing `offset`/`limit`-with-`raw=False` contract.

### Related PRs / Commits

- [Issue #153](https://github.com/dfch/biz.dfch.SpecMgr/issues/153): tracking issue for this feature.
