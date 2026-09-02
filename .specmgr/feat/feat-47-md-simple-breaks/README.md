---
classification: null
created: '2026-09-02 16:10:31.726+02:00'
id: feat-47-md-simple-breaks
status: planning
type: feat
updated: '2026-09-02 16:29:30.863+02:00'
version: 1.0.0
---

# Feature: Preserve `---` Thematic Breaks in `mdformat` via `mdformat-simple-breaks`

## Plan

### Overview

GitHub issue #47: `specmgr mdformat` (and, transitively, `format_text()` in `models/md/_markdown.py`, which every domain's `parse_<d>`/`create_<d>`/`validate_<d>`/`update` path also calls) currently converts a `---` thematic break into a 70-character line of underscores. This is `mdformat`'s own hardcoded, non-configurable `hr` renderer (an explicit, permanent upstream style decision -- executablebooks/mdformat#69 -- not exposed as an option). We want plain `---` preserved/normalized instead, since that is the form most Markdown authors actually type.

Research (see issue #47 discussion) confirmed this is only achievable via `mdformat`'s `parser_extension` plugin mechanism, and that the third-party package `mdformat-simple-breaks` (MIT, single-file, renders `hr` as a literal `---`) already does exactly this, registered under the `mdformat.parser_extension` entry point group as `simple_breaks`. It was verified end-to-end against this repo's actual `format_markdown_document`/`format_text` pipeline (including combined with the existing `number=True` option and with YAML frontmatter present) and against the full 3056-test suite with zero regressions.

### Requirements

- REQ-001: `format_text()` (`models/md/_markdown.py`) must render any thematic break (`---`, `***`, `___`, or any CommonMark-valid variant) as `---`, not as a 70-character line of underscores.

- REQ-002: The `mdformat-simple-breaks` dependency must be pinned to an exact version (no `^`/`~=`/`>=` range) so it never silently updates via `uv sync`/`uv lock --upgrade`; bumping it is a deliberate, reviewed change.

### Acceptance Criteria

- [x] ACC-001: A markdown body containing `---` as a thematic break, run through `specmgr mdformat` (CLI) or the `mdformat` MCP tool, keeps `---` in the output instead of a 70-underscore line.

- [x] ACC-002: `pyproject.toml` pins `mdformat-simple-breaks` with `==` (exact version), and `uv.lock` is regenerated to match.

- [x] ACC-003: A regression test, added to the existing `tests/models/md/test__markdown.py` (not a new file -- it already targets this exact module), asserts `format_text(...)`/`format_markdown_document(...)` renders `---`, `***`, and `___` thematic breaks as `---`, not underscores.

- [x] ACC-004: The full existing test suite still passes.

### Scope

#### Included

- Adding `mdformat-simple-breaks` as an exact-pinned dependency in `pyproject.toml` and `uv.lock`.

- Wiring `extensions={"simple_breaks"}` into the single shared `mdformat.text(...)` call in `format_text()` (`src/biz/dfch/specmgr/models/md/_markdown.py`).

- A regression test covering the new thematic-break rendering.

#### Explicitly Out Of Scope

- Reformatting/touching any existing repository markdown content that already contains a 70-underscore thematic break (any such diff happens naturally, later, the next time that specific document is parsed/created/validated/updated -- not as part of this feature).

- Any other `mdformat` styling/option change unrelated to thematic breaks.

- Writing an in-house thematic-break renderer plugin (an existing, small, MIT-licensed package already does this correctly; see Design Notes).

### Dependencies

#### Depends On

- None.

#### Blocks

- None.

### Design Notes

`mdformat`'s `hr` renderer is hardcoded in `mdformat/renderer/_context.py` (`"_" * 70`); there is no CLI flag or `options=` key for it, confirmed by reading upstream source and the linked upstream issue.

`mdformat` supports per-syntax-node renderer overrides via the `mdformat.parser_extension` entry-point group (`ParserExtensionInterface` -- a `RENDERERS` mapping merged into `mdformat.renderer.DEFAULT_RENDERERS`). This is the same, fully public mechanism the wider `mdformat` plugin ecosystem (`mdformat-gfm`, `mdformat-tables`, etc.) uses.

`mdformat-simple-breaks` (<https://github.com/csala/mdformat-simple-breaks>, PyPI `mdformat-simple-breaks`) implements exactly one `hr` override returning a literal `---`, registered under entry-point name `simple_breaks`. Its `0.1.0` release (2025-10-28) targets `mdformat~=1.0.0`, matching this repo's own `mdformat>=1.0.0` pin.

Verified side effects: no conflict with YAML-frontmatter delimiter parsing (a body-leading `---` round-trips correctly through `frontmatter.loads`/`dumps`); no new setext-heading ambiguity (that ambiguity already exists in plain CommonMark, independent of this change); the full test suite passes with the plugin actually wired in.

Pinning `mdformat-simple-breaks` to an exact version (`==0.1.0`), per explicit request, rather than an open-ended range: this is a single-maintainer, low-adoption package, so we intentionally do not want it to silently pick up future releases via `uv sync`/`uv lock --upgrade` -- any version bump is a deliberate, reviewed change to this one line in `pyproject.toml`.

PyPI reachability from the implementation environment was confirmed directly (fetched `https://pypi.org/pypi/mdformat-simple-breaks/json`, got `200`): the package has published exactly two releases ever, `0.0.1` and `0.1.0`, so `0.1.0` is indeed latest, matching this plan's pin. Its own `requires_dist` is `mdformat~=1.0.0` -- compatible with this repo's `mdformat>=1.0.0` pin today, but a latent constraint worth remembering if this repo's `mdformat` pin is ever bumped to `2.x`: `mdformat-simple-breaks` would need its own upstream release supporting that major version first, or this plugin becomes a blocker on that future bump. Also confirmed empirically: `mdformat.text` accepts `extensions: Iterable[str] = ()` as a keyword (via `inspect.signature`), and before the dependency is installed, `mdformat.plugins.PARSER_EXTENSIONS` is empty (entry points are discovered at import time from installed packages) -- i.e. Task 1.3's `extensions={"simple_breaks"}` wiring is inert/a no-op until Tasks 1.1/1.2 actually add and lock the dependency.

### Related Decisions

- None (implementation-detail-scoped; logged in this feature's own Decisions Made log instead, per `AGENTS.md`'s ADR-vs-feature-log guidance).

### Task List

#### Phase 1: Implementation

- [x] Task 1.1: Add `mdformat-simple-breaks==0.1.0` (exact pin) as a dependency in `pyproject.toml`.

- [x] Task 1.2: Regenerate `uv.lock` (`uv lock`).

- [x] Task 1.3: Wire `extensions={"simple_breaks"}` into the shared `mdformat.text(...)` call in `format_text()` (`src/biz/dfch/specmgr/models/md/_markdown.py`).

- [x] Task 1.4: Add regression test case(s) to the existing `tests/models/md/test__markdown.py` covering `---`/`***`/`___` thematic-break rendering (extend, don't add a new file).

- [x] Task 1.5: Run the full test suite and confirm no regressions.

- [x] Task 1.6: Add a `### Fixed` entry (Keep a Changelog's own standard category for a bug fix, per this repo's existing `CHANGELOG.md` section headers) under `[Unreleased]`, describing the GitHub issue #47 fix.

## Progress

### Current Status

**As of 2026-09-02**: Implementation complete. `mdformat-simple-breaks==0.1.0` is pinned in `pyproject.toml`/`uv.lock`, wired into `format_text()` via `extensions={"simple_breaks"}`, a regression test was added, the full test suite (3060 tests) passes, and the CHANGELOG `[Unreleased]` `### Fixed` entry is in place. All tasks and acceptance criteria are checked off. Ready for orchestrator review/commit.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 00:00:00.000Z - Implementation complete

Completed Phase 1 (the plan's only phase). `uv add "mdformat-simple-breaks==0.1.0"` added the dependency to `pyproject.toml` with an exact `==` pin (verified) and regenerated `uv.lock` in the same step (Tasks 1.1/1.2). Added a module-level `_MDFORMAT_EXTENSIONS = {"simple_breaks"}` constant and wired it into the single `mdformat.text(...)` call in `format_text()` (`src/biz/dfch/specmgr/models/md/_markdown.py`, Task 1.3). Extended `tests/models/md/test__markdown.py` with four new regression tests covering `---`/`***`/`___` via `format_text` and a combined frontmatter+body case via `format_markdown_document` (Task 1.4). Ran the full suite: 3060 tests, all passing, no regressions (Task 1.5). Added a `### Fixed` entry under `[Unreleased]` in `CHANGELOG.md` referencing GitHub issue #47 (Task 1.6). Manually verified ACC-001 end-to-end via `specmgr mdformat` CLI on a scratch file containing `___`, confirming the on-disk output uses `---`. Quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, full `unittest discover`) all green. No deviations from the plan.

#### 2026-09-02 00:00:00.000Z - Plan refined ahead of implementation

Resolved three open items surfaced during pre-implementation review: (1) the CHANGELOG entry (Task 1.6) uses `### Fixed`, matching Keep a Changelog's standard category for a bug fix and this repo's own existing section headers; (2) the regression test (ACC-003/Task 1.4) extends the existing `tests/models/md/test__markdown.py` rather than adding a new file, since that file already targets this exact module; (3) PyPI reachability and `mdformat-simple-breaks` package metadata (exactly two releases, `0.0.1`/`0.1.0`; `requires_dist: mdformat~=1.0.0`) were verified directly from the implementation environment -- see Design Notes for the latent `mdformat` 2.x compatibility caveat this uncovered. No requirements/scope changes; implementation still not started.

#### 2026-09-02 00:00:00.000Z - Created

Feature folder created to track fixing GitHub issue #47 (`specmgr mdformat` converts `---` to a 70-underscore thematic break) via the `mdformat-simple-breaks` plugin, pinned to an exact version.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 00:00:00.000Z - Use `mdformat-simple-breaks` instead of an in-house plugin

`mdformat` has no built-in option for this (upstream explicitly refuses to add one); a tiny, MIT-licensed, single-purpose plugin already exists and targets our exact `mdformat` major version, so building/maintaining our own `parser_extension` plugin for the same one-line `hr` override was rejected as unnecessary duplication.

#### 2026-09-02 00:00:00.000Z - Pin `mdformat-simple-breaks` to an exact version

Per explicit request: this is a low-adoption, single-maintainer dependency, so version bumps must be deliberate/reviewed, not automatic via `uv sync`/`uv lock --upgrade`.

### Related PRs / Commits

- None yet.

### More Information

None.
