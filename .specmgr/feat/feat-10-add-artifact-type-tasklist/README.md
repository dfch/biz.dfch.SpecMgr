---
created: 2026-08-16
id: feat-10-add-artifact-type-tasklist
status: in-progress
updated: 2026-08-16
version: 1.0.0
---

# Feature: Add artifact type TaskList (tsk)

## Plan

### Overview

Add a new markdown artifact type, `TaskList` (abbreviation `tsk`), for specifying
task/todo lists. Whenever an agent creates a "procedure" or step-based plan, it
should be able to use a `TaskList` document instead of a full `feat-N-slug`
feature file — keeping the list out of the main feature file's context and
providing a lightweight vehicle for small procedures where a complete feature
is too much. `tsk` follows the domain-first hierarchy and MCP surface already
established by `req` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing its
tools/resources shape almost exactly (per GitHub issue #10).

### Requirements

- [ ] REQ-001: Define the `tsk` markdown schema — frontmatter (`type="tsk"`,
  4-value status set: `draft`/`active`/`done`/`cancelled`) and body (H1 title,
  optional leading comment, flat checklist of items, mandatory `## Recent Updates` section holding a dynamic list of H3 update entries)
- [ ] REQ-002: Pydantic models for `tsk` documents (`tsk/models/v1/` —
  domain-first path, mirroring `req/models/v1/`)
- [ ] REQ-003: Parse and validate `tsk` documents from markdown
  (`parse_tsk`, mirroring `parse_req`)
- [ ] REQ-004: MCP tools mirroring `req`'s lifecycle surface: `parse_tsk`,
  `get_tsk_example`, `get_tsk_template`, `create_tsk`, `update_tsk`,
  `set_status_tsk`, `delete_tsk` (stub), `validate_tsk`, `get_tsk`
- [ ] REQ-005: MCP resources mirroring `req`: `specmgr://tsk/list`,
  `/example`, `/schema`, `/template`
- [ ] REQ-006: MCP prompts — `create_task`, `update_task` (narrated tool
  sequences, mirroring `req/prompts/create_req.py`/`update_req.py`), and a new
  `implement_task` prompt: reads an existing `tsk` document (via `get_tsk`),
  builds an actual `TodoWrite` list from its items, and uses the `question`
  tool to resolve ambiguity before proceeding
- [ ] REQ-007: Packaged example/template/schema data (`tsk/data/`) via the
  existing generic `general/tools/_packaged_data.py`, with the matching
  `pyproject.toml` package-data entry, pre-commit hook, and CI step
- [ ] REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema`
  (new `tsk` entry in the doc-type registry), `specmgr mcp-docs`, all kept
  drift-free via pre-commit/CI

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — schema documented, reference `tsk`
  document (`tsk_reference.md`) round-trips through the parser
- [ ] ACC-002: Verifies REQ-002 — Pydantic models validate required/optional
  fields correctly, including the `TaskItem` checked/description split
- [ ] ACC-003: Verifies REQ-003 — parser produces a valid object tree;
  malformed input raises (structural `AssertionError` / field-level
  `pydantic.ValidationError`, matching `req`/`uc`'s error-channel convention)
- [ ] ACC-004: Verifies REQ-004 — every listed tool implemented and
  registered, with `create_tsk`/`update_tsk` validating body-only content the
  same way `create_req`/`update_req` do
- [ ] ACC-005: Verifies REQ-005 — every listed resource implemented and
  registered
- [ ] ACC-006: Verifies REQ-006 — `create_task`/`update_task` prompts
  narrate the correct tool sequence; `implement_task` demonstrably drives a
  `TodoWrite` list from a real `tsk` document and asks a clarifying question
  via the `question` tool when an item's intent is ambiguous
- [ ] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
  real, non-editable install (wheel build + scratch venv), mirroring `req`'s
  own verification (feat-6 Task 5.1)
- [ ] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
  `specmgr mcp-docs` all report no drift after implementation

### Scope

**Included in this feature:**

- Specification of the `tsk` markdown schema (frontmatter + body)
- Pydantic models, parser, and schema generation under `tsk/models/v1/`
- Full MCP surface (tools/resources/prompts/packaged data) mirroring `req`
- `implement_task` prompt behavior (TodoWrite + `question`-tool clarification)
- Tests mirroring `tests/req/`'s layout and coverage

**Explicitly out of scope:**

- Phases, per-item `depends on`/`status` metadata, or any other structure
  beyond a flat checklist (explicit decision — see Design Notes)
- Granular, ADR-style section-mutation tools (e.g. an `option_*`-style
  surface for `## Recent Updates` entries) — entries are appended via a
  whole-body `update_tsk` call, same conclusion `req` reached in its own
  Task 3.9 design discussion
- Cross-referencing/linking `tsk` documents to other artifact types
  (REQ/UC/ADR) — not part of this feature
- A `specmgr tsk-toc`-equivalent generation command or its own CI/pre-commit
  drift check beyond what `specmgr docs`/`specmgr mcp-docs`/`specmgr schema`
  already provide generically

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), `general/tools/_doc_paths.py` and
  `_packaged_data.py` (generalized past REQ specifically for this kind of
  reuse, `feat-6-requirement-artifact` Tasks 3.10/5.2/5.3), the existing
  `models/md` engine — in particular `MarkdownSection1WithComment` and
  `MarkdownListItem` (reused as-is) and `MarkdownComment` (feat-6 Task 3.20)
- Blocks: None identified yet

### Design Notes

- **Body shape** — `Task` (the body's H1 class) subclasses the already-
  existing `MarkdownSection1WithComment` mixin (`models/md/`), reusing it
  as-is (no new mixin needed):

  ```
  # {H1 title}
  <!-- optional leading comment -->        comment: MarkdownComment | None
  - [ ] flat checklist item                items: list[TaskItem]  (>=1)
  - [x] another item
  ...

  ## Recent Updates                        recent_updates: RecentUpdates
  ### {free-form title}
  {update text}
  ### {another entry}
  {update text}
  ```

  Order is enforced by the model: title -> optional comment -> items (>=1)
  -> mandatory `## Recent Updates` heading, whose own `updates` list also
  requires `>=1` entry (`min_length=1`, corrected during Phase 2 — see
  Decisions Made: a freshly created `tsk` document must seed a first update
  entry, e.g. "Created", since the underlying parsing engine already
  rejected an empty `## Recent Updates` section and direct construction is
  now made consistent with it rather than silently diverging).

- **`TaskItem`** (new leaf, `tsk/models/v1/task_item.py`, subclass of
  `MarkdownListItem`) parses a literal `- [ ] text` / `- [x] text` marker
  into `checked: bool` + `description: str` computed fields. This is
  necessary because the project's markdown parser (`MarkdownIt("commonmark")`,
  `models/md/_markdown.py`) has no GFM task-list plugin enabled — `[ ]`/`[x]`
  is otherwise just literal inline text, not a distinct AST node.

- **`RecentUpdates`** — an H2 section holding a dynamic list of H3 entries
  (free-form title + content each), structurally similar to `AdrBody`'s
  `## Pros and Cons of the Options` / `AdrOption` collection, but with no
  dedicated per-entry tools (no `option_create`/`option_list` equivalent).
  Entries are appended by editing the whole body and calling
  `update_tsk(id, content)`. Requires `>=1` entry at all times (see body
  shape note above) — Phase 3's `create_tsk`/`get_tsk_template`/
  `get_tsk_example` must seed a first entry (e.g. "Created").

- **Frontmatter status** — `draft`/`active`/`done`/`cancelled`: a small,
  purpose-fit set matching how a task list is actually used (start it, work
  it, finish it, or drop it), rather than reusing REQ's 7-value ADR-like set,
  most of which doesn't map naturally onto a todo list.

- **Prompt naming** — the three prompts use the issue's literal wording
  (`create_task`/`update_task`/`implement_task`), not the `tsk`-prefixed
  convention the tools/resources use, matching GitHub issue #10 verbatim.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types

No new ADR is anticipated for this feature — the `TaskItem` checkbox-parsing
approach and the `RecentUpdates` dynamic-section design are scoped enough to
log only in this file's own Decisions Made, not a full ADR.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

**Execution approach** (decided 2026-08-16, see Decisions Made): each phase
below is delegated to the `implementation-specialist` subagent as one unit
(implementation + its own mirrored tests together, not a separate later test
phase), reviewed and quality-gated (ruff format/check, vulture, full
`unittest` suite) by the orchestrator, then committed as one Conventional
Commit per phase. The original standalone "Phase 5: Tests" has been folded
into Phases 1–3 below (each phase now carries its own test tasks); Phase 4
absorbs a final cross-cutting verification pass instead. This collapses the
original 5 phases into **4 commits**.

#### Phase 1: Specification (commit 1) — done

- [x] Task 1.1: Define `tsk` frontmatter (`tsk/models/v1/frontmatter.py` —
  `TskFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["tsk"]`,
  4-value status set `draft`/`active`/`done`/`cancelled`) — depends on: none
  — status: done
- [x] Task 1.2: Define `tsk` body structure (`tsk/models/v1/body.py`,
  `tsk/models/v1/task_item.py`) — `Task(MarkdownSection1WithComment)` with
  `items: list[TaskItem]` and `recent_updates: RecentUpdates`; `TaskItem`
  (checked/description computed fields, new `MarkdownListItem` subclass);
  `RecentUpdates(MarkdownSection2)` holding `updates: list[UpdateEntry]`
  built on `models/md`'s generic `list[MarkdownStr]` engine
  (`process_list_field`), with `UpdateEntry` a free-form-title H3 leaf via
  `@alias(value=".+", type=AliasType.REGEX)` — not ADR's numbered-option
  pattern — depends on: Task 1.1 — status: done
- [x] Task 1.3 (renumbered; was 1.4): Create a reference `tsk` document
  (`tsk_reference.md`) exercising every field, used as the parser's
  round-trip test fixture — depends on: Task 1.2 — status: done (placed at
  `.specmgr/feat/feat-10-add-artifact-type-tasklist/tsk_reference.md`,
  mirroring `req`'s own reference-fixture location convention, not
  `tsk/data/` — see Recent Updates)
- [x] Task 1.4 (renumbered; was 1.5, folded from former Task 5.1):
  `tests/tsk/models/v1/test_frontmatter.py`, `test_body.py`/`test_task_item.py`
  — structural + validation tests mirroring `tests/req/models/v1/`, with
  explicit coverage of `MarkdownSection1WithComment`'s comment-present/
  comment-absent cases (its first real production consumer — no prior test
  coverage outside `models/md`'s own unit tests) — depends on: Task 1.3 —
  status: done

**Plan correction (2026-08-16, see Decisions Made)**: the former Task 1.3
("draft `tsk_schema.json` + register in the schema generator") has moved to
Phase 2 as Task 2.5 — `generate_req_schema`/`generate_uc_schema`
(`commands/schema.py`) both call the full `XDocument.model_json_schema()`,
not just the body model, so schema generation cannot happen before
`TskDocument` (Task 2.1) exists.

#### Phase 2: Pydantic Models & Parser (commit 2) — done

- [x] Task 2.1: `tsk/models/v1/document.py` (`TskDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:
  done
- [x] Task 2.2: Implement `parse_tsk(text: str) -> TskDocument` (mirrors
  `parse_req`/`parse_uc`) — depends on: Task 2.1 — status: done
- [x] Task 2.3: `tsk/models/v1/summary.py` (`TskSummary`, mirroring
  `ReqSummary`/`AdrSummary`, for the `specmgr://tsk/list` resource) —
  depends on: Task 2.1 — status: done
- [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ's Task 2.4/2.5/2.6) —
  depends on: Task 2.1 — status: done (audited; Phase 1 already met the bar,
  no gaps found)
- [x] Task 2.5 (moved from Phase 1's former Task 1.3): Draft `tsk_schema.json`
  via `generate_tsk_schema()` (mirroring `generate_req_schema`/
  `generate_uc_schema` in `commands/schema.py`, calling
  `TskDocument.model_json_schema()`) + register `"tsk"` in the `specmgr
  schema` doc-type generator registry (`_GENERATORS`) — depends on: Task
  2.1 — status: done (`docs/tsk_schema.json` generated, mirroring
  `docs/req_schema.json`/`docs/uc_schema.json`'s own precedent)
- [x] Task 2.6 (folded from former Task 5.1): `tests/tsk/models/v1/test_parser.py`
  — mirrors `TestParseReq`'s 8-case shape (minimal doc, full
  reference-doc round-trip, defaults-when-absent, invalid status, malformed
  structure, etc.), plus round-trip coverage of the new
  `RecentUpdates`/`UpdateEntry` dynamic-list combo — depends on: Task 2.2,
  Task 2.5 — status: done

#### Phase 3: MCP Surface (commit 3)

- [ ] Task 3.1: `tsk/tools/_paths.py` + `_io.py` + `_write.py` + `_lock.py`,
  thin wrappers over `general/tools/_doc_paths.py` (mirrors
  `req/tools/_paths.py` etc. exactly) — depends on: Task 2.2 — status:
  not-started
- [ ] Task 3.2: `create_tsk(content: str) -> TskDocument` tool (body-only
  content, MCP builds frontmatter: `id`, `type="tsk"`, `status="draft"`,
  `created=updated=now`, `version`) — depends on: Task 3.1 — status:
  not-started
- [ ] Task 3.3: `update_tsk(id, content) -> TskDocument` tool (whole-body
  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
  `updated`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.4: `set_status_tsk(id, status) -> TskDocument` tool (only path
  that changes `status`) — depends on: Task 3.1 — status: not-started
- [ ] Task 3.5: `delete_tsk(id) -> NoReturn` stub tool — depends on: Task
  3.1 — status: not-started
- [ ] Task 3.6: `validate_tsk(content, full=False) -> bool` tool — depends
  on: none — status: not-started
- [ ] Task 3.7: `get_tsk(id) -> TskDocument` tool (id-based single-document
  read; tool, not resource — matches REQ's revisited Task 3.17 conclusion)
  — depends on: Task 3.1 — status: not-started
- [ ] Task 3.8: `get_tsk_example`/`get_tsk_template` tools + packaged data
  (`tsk/data/tsk_example.md`, `tsk/data/tsk_template.md`) via
  `general/tools/_packaged_data.py` — depends on: Task 1.4 — status:
  not-started
- [ ] Task 3.9: `specmgr://tsk/list` and `specmgr://tsk/schema` resources
  (packaged `tsk/data/tsk_schema.json`, mirroring `specmgr://req/schema`) —
  depends on: Task 3.1, Task 2.5 — status: not-started
- [ ] Task 3.10: `specmgr://tsk/example` and `specmgr://tsk/template`
  resources — depends on: Task 3.8 — status: not-started
- [ ] Task 3.11: `pyproject.toml` package-data entry for
  `biz.dfch.specmgr.tsk` (`data/*.md`, `data/*.json`), pre-commit hook + CI
  step for the packaged `tsk_schema.json` copy (mirroring
  `specmgr-schema-req-package`) — depends on: Task 2.5 — status: not-started
- [ ] Task 3.12: `tsk/prompts/create_task.py` + `update_task.py` — narrate
  the tool sequence (mirroring `req/prompts/create_req.py`/`update_req.py`)
  — depends on: Tasks 3.2, 3.3, 3.4, 3.7, 3.9 — status: not-started
- [ ] Task 3.13: `tsk/prompts/implement_task.py` — reads an existing `tsk`
  document via `get_tsk`, builds a `TodoWrite` list from its `items`, and
  uses the `question` tool to resolve ambiguity for any item before
  proceeding — depends on: Task 3.7 — status: not-started
- [ ] Task 3.14: add `tsk` to `server.py`'s domain import line (last-line
  import convention — easily forgotten, silently means nothing registers)
  — depends on: Tasks 3.2-3.13 — status: not-started
- [ ] Task 3.15 (folded from former Tasks 5.2/5.3): `tests/tsk/tools/...`,
  `tests/tsk/resources/...`, `tests/tsk/prompts/...` mirroring
  `tests/req/tools/`/`tests/req/resources/` layout, plus dedicated tests for
  `implement_task`'s `TodoWrite`/`question`-tool driven behavior — depends
  on: Tasks 3.1-3.14 — status: not-started

#### Phase 4: Docs, CI wiring & final verification (commit 4)

- [ ] Task 4.1: `specmgr docs` regeneration (new `tsk` modules picked up) —
  depends on: Phase 1-3 complete — status: not-started
- [ ] Task 4.2: `specmgr mcp-docs` regeneration (new tools/resources/
  prompts appear in `docs/MCP.md`) — depends on: Phase 3 complete — status:
  not-started
- [ ] Task 4.3: CI wiring — confirm the Python-3.13-only `specmgr schema`/
  `specmgr docs`/`specmgr mcp-docs` steps in `.github/workflows/ci.yml`
  cover `tsk` with no separate per-type step needed (registry-driven,
  mirroring `req`'s own wiring) — depends on: Task 4.1, Task 4.2 — status:
  not-started
- [ ] Task 4.4: Final verification pass — walk every ACC-001..008 below and
  confirm each is actually satisfied; run the full quality gate (ruff
  format/check, pylint advisory, vulture, unittest, `specmgr docs`,
  `specmgr schema`, `specmgr mcp-docs` drift checks) once more end-to-end —
  depends on: Tasks 4.1-4.3 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-16**: Phases 1-2 done. Phase 1 committed (`9ace8dd`); Phase 2
(`TskDocument`, `parse_tsk`, `TskSummary`, `generate_tsk_schema()`, parser
tests) implemented and quality-gated, about to be committed. Along the way,
corrected `RecentUpdates.updates` to require `min_length=1` (was
inconsistent — parsing already rejected zero entries, direct construction
didn't). 885 tests passing, ruff/vulture clean, `docs/tsk_schema.json`
generated. Proceeding to Phase 3 (MCP Surface).

### Blockers

None.

### Recent Updates

#### 2026-08-16

- Completed: Resolved a GitHub issue-number discrepancy — the branch
  `feat-11-add-artifact-type-tasklist` already existed locally, but GitHub
  issue #11 does not exist; issue #10 ("Add artifact type TaskList") is the
  actual matching issue. Per user decision, renamed the branch to
  `feat-10-add-artifact-type-tasklist` (via `git branch -m`) rather than
  creating a new issue or leaving the mismatched name. Merged `dev` into the
  branch first (fast-forward; brought in the now-complete UC MCP surface).
  Wrote this feature's plan, covering schema, models, MCP tools/resources/
  prompts, packaged data, docs/CI wiring, and tests — mirroring the `req`
  domain per the issue's own instructions, with two explicit design
  decisions: (1) the body is a flat checklist only (no phases/dependencies/
  per-item status), and (2) the body carries an optional leading comment
  before the checklist and a mandatory `## Recent Updates` H2 section (H3
  entries) after it.
- Next: Begin Phase 1 (Specification) — define `TskFrontmatter`, the
  `Task`/`TaskItem`/`RecentUpdates` body classes, and the `tsk_reference.md`
  fixture.
- Notes: No implementation code has been written yet; this session was
  planning and branch setup only, per explicit instruction not to start
  implementation.

#### 2026-08-16 (continued)

- Completed: Explored the existing `req`/`uc` domains and shared
  `models/md`/`general/tools` building blocks in depth to validate the
  plan's feasibility before coding. Confirmed two nontrivial points: (1)
  `MarkdownSection1WithComment` (which `Task`'s body subclasses) has zero
  prior production consumers — only exercised in `models/md`'s own unit
  tests — so Phase 1 needs explicit comment-present/absent test coverage as
  its first real-world use; (2) `RecentUpdates` should be built on
  `models/md`'s existing generic `list[MarkdownStr]` engine
  (`process_list_field` + a free-form-title H3 leaf via
  `@alias(value=".+", type=AliasType.REGEX)`), not adapted from ADR's
  `AdrOption`/`_OPTION_HEADING_PATTERN`, which bakes in mandatory
  sequential numbering that doesn't fit free-form update entries. Finalized
  execution approach with the user (see Decisions Made) and restructured
  the Task List above accordingly (Phase 5 folded into Phases 1-3, 4
  commits instead of 5).
- Next: Execute Phase 1 (Specification) via the `implementation-specialist`
  subagent.
- Notes: Still no implementation code written as of this update; this
  entry only records the finalized plan restructuring.

#### 2026-08-16 (further continued)

- Completed: **Phase 1 (Specification)**, committed as `9ace8dd`
  (`feat(tsk): add tsk (TaskList) frontmatter and body models`).
  `tsk/models/v1/frontmatter.py` (`TskFrontmatter`), `tsk/models/v1/body.py`
  (`Task`, `RecentUpdates`, `UpdateEntry`), `tsk/models/v1/task_item.py`
  (`TaskItem`), the `tsk_reference.md` round-trip fixture (placed at
  `.specmgr/feat/feat-10-add-artifact-type-tasklist/tsk_reference.md`,
  mirroring `req`'s established reference-fixture location rather than
  `tsk/data/`), and their tests (`tests/tsk/models/v1/`) are all in place.
  877 tests passing total; ruff format/check and vulture clean; `specmgr
  docs`/`specmgr mcp-docs` regenerated. Delegated to
  `implementation-specialist`, reviewed and quality-gated by the
  orchestrator before committing.
- Also completed: caught and fixed a dependency-ordering bug in the
  original Task List before starting — schema generation (former Task 1.3)
  requires the full `TskDocument` model (`XDocument.model_json_schema()`
  pattern confirmed in `commands/schema.py`), so it was moved to Phase 2 as
  Task 2.5 (see Decisions Made).
- Next: Execute Phase 2 (Pydantic Models & Parser) — `TskDocument`,
  `parse_tsk`, `TskSummary`, field descriptions, `generate_tsk_schema()` +
  registry entry, and parser round-trip tests against `tsk_reference.md`.
- Notes: `RecentUpdates.updates` is mandatory (non-`Optional`) per the
  Design Notes' "may start empty **on creation**" wording, but the
  underlying `models/md` list-parsing engine will raise if a *persisted*
  document's `## Recent Updates` section has zero `### ` entries — flagged
  by the implementation-specialist as consistent with `req.Characteristics`'
  existing behavior (not a regression), but worth keeping in mind if Phase
  2's `parse_tsk` round-trip tests need a Recent Updates section with at
  least one entry.

#### 2026-08-16 (yet further continued)

- Completed: **Phase 2 (Pydantic Models & Parser)**. `tsk/models/v1/document.py`
  (`TskDocument`), `parser.py` (`parse_tsk`), `summary.py` (`TskSummary`),
  `_util.py` (`SCHEMA_COMMENT_VERSION`), `generate_tsk_schema()` +
  `_GENERATORS["tsk"]` in `commands/schema.py`, and
  `tests/tsk/models/v1/test_parser.py` (8 tests, mirroring `TestParseReq`)
  all implemented. `docs/tsk_schema.json` generated, mirroring
  `docs/req_schema.json`/`docs/uc_schema.json`'s own precedent. Delegated to
  `implementation-specialist`, reviewed by the orchestrator.
- Also completed: resolved the `RecentUpdates.updates` empty-list
  inconsistency flagged as a Phase 1 risk — confirmed empirically that
  `from_text` parsing already rejected zero entries while direct
  construction (`RecentUpdates(updates=[])`) silently succeeded. Added
  `min_length=1` to make both paths consistent (see Decisions Made), and
  updated the two Phase 1 tests that exercised the old (now-superseded)
  behavior (`TestRecentUpdatesEmpty`, `TestTaskItemsValidation`) to match.
- Next: Execute Phase 3 (MCP Surface) — tools, resources, prompts, packaged
  data, `server.py` wiring, and their tests. Phase 3's `create_tsk`/
  `get_tsk_template`/`get_tsk_example` must each seed a first Recent Updates
  entry (e.g. "Created") given the `min_length=1` constraint above.
- Notes: 885 tests passing (877 + 8 new); ruff format/check and vulture
  clean.

### Decisions Made

- **2026-08-16**: Target GitHub issue #10, not #11 — issue #11 does not
  exist; #10 ("Add artifact type TaskList") matches the pre-existing local
  branch's slug. Rationale: avoid creating a redundant new issue when an
  existing one already describes the same feature.
- **2026-08-16**: Rename the local branch from `feat-11-...` to
  `feat-10-...` rather than keep the mismatched number or leave a new issue
  to be filed — rationale: keeps the `feat-NNN-slug` convention
  (AGENTS.md) accurate and avoids a second `.specmgr/feat/` folder later
  needing a rename too.
- **2026-08-16**: `tsk` body is a flat checklist (H1 + optional comment +
  `items: list[TaskItem]` + mandatory `## Recent Updates`) — no phases, no
  per-item `depends on`/`status` metadata. Rationale: keeps the artifact
  genuinely lightweight, distinct from the heavier `.specmgr/feat/*`
  Task List format it is meant to be a smaller alternative to.
- **2026-08-16**: `tsk` frontmatter `status` is `draft`/`active`/`done`/
  `cancelled`, not REQ's 7-value set. Rationale: purpose-fit to how a task
  list is actually used, rather than maximizing schema consistency with an
  artifact type (REQ) whose lifecycle semantics don't map naturally onto a
  todo list.
- **2026-08-16**: No dedicated per-entry tools for `## Recent Updates`
  (no `option_create`/`option_list` equivalent) — entries are appended via
  whole-body `update_tsk` calls. Rationale: mirrors REQ's own Task 3.9
  conclusion that granular, ADR-style section-mutation tooling isn't worth
  building for an artifact this small.
- **2026-08-16**: Execution strategy — delegate each phase to the
  `implementation-specialist` subagent (implementation + its own mirrored
  tests together, not a separate later test phase); one Conventional Commit
  per completed phase; orchestrator quality-gates (ruff/vulture/unittest)
  before each commit. Rationale: user-selected approach; keeps the original
  5-phase plan's dependency ordering intact while avoiding a large,
  disconnected final test-writing pass.
- **2026-08-16**: `RecentUpdates`/its H3 entries are built on `models/md`'s
  generic `list[MarkdownStr]` engine (`process_list_field`) with a
  free-form-title H3 leaf via `@alias(value=".+", type=AliasType.REGEX)`,
  not adapted from ADR's `AdrOption`/`_OPTION_HEADING_PATTERN`. Rationale:
  ADR's option model bakes in mandatory sequential numbering and a fixed
  `"Option {number}: "` render format that free-form update entries don't
  want; the declarative `models/md` engine already provides the needed
  "H2 with dynamic H3 children" shape generically (confirmed by
  exploration), matching how `req`'s own `Requirement` H1 already uses the
  same free-form-title alias mechanism.
- **2026-08-16**: Moved schema generation (`generate_tsk_schema()` +
  `specmgr schema` registry entry) from Phase 1 to Phase 2, as Task 2.5.
  Rationale: verified `commands/schema.py`'s `generate_req_schema`/
  `generate_uc_schema` both call the full `XDocument.model_json_schema()`
  (frontmatter + body combined), not the body model alone — so it cannot
  run before `TskDocument` (Task 2.1) exists. The original Task List had
  this as Task 1.3, before `TskDocument` was even defined; corrected before
  starting implementation to avoid building against a broken dependency
  order.
- **2026-08-16**: Added `min_length=1` to `RecentUpdates.updates`,
  superseding the original Design Notes wording ("its own `updates` list may
  start empty on creation"). Rationale: Phase 2 empirically confirmed
  `models/md`'s generic list-parsing engine already rejects a `## Recent
  Updates` section with zero `### ` entries during `from_text` for any
  non-`Optional` `list[X]` field (regardless of `min_length`) — but direct
  Python construction (`RecentUpdates(updates=[])`) still silently
  succeeded, an inconsistency that would have surfaced confusingly in
  Phase 3's `create_tsk`. Making the constraint explicit and consistent
  means a freshly created `tsk` document must seed a first Recent Updates
  entry (e.g. "Created") — `create_tsk`/`get_tsk_template`/`get_tsk_example`
  in Phase 3 must account for this, same as `Task.items`' own `min_length=1`
  already requires at least one checklist item.

### Related PRs / Commits

None yet.
