# History: Add artifact type TaskList (tsk)

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
