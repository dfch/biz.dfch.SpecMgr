---
classification: null
created: '2026-09-04 08:22:35.000Z'
id: feat-94-frontmatter-schema
status: planning
type: feat
updated: '2026-09-04 08:22:35.000Z'
version: 1.0.0
---

# Feature: Expose Frontmatter created/updated Date+Time Format in JSON Schema as a Pattern

## Plan

### Overview

GitHub issue #94 reports that every whole-body document type's frontmatter `created`/`updated` fields are validated at runtime by `frontmatter._DATE_TIME_PATTERN` (`src/biz/dfch/specmgr/models/md/frontmatter.py`), but the format is lost entirely when the JSON Schema is generated: `created`/`updated` serialize as a plain `string | null` in both `docs/{type}_schema.json` and each domain's packaged copy `src/biz/dfch/specmgr/{type}/data/{type}_schema.json` (both generated via `XDocument.model_json_schema()`, see `src/biz/dfch/specmgr/commands/schema.py`), so schema consumers cannot tell that any format constraint was ever required. This feature makes the `yyyy-MM-dd HH:mm:ss.fff` + `Z`/`±HH:mm` constraint part of every whole-body document's JSON Schema, keeping the regex as a single source of truth, without changing the runtime validator's behavior or error-message content. A prototype implementation (built and reviewed during `feat-81-83-validation`'s own investigation, then discarded per that feature's "do not implement" scope) found that a naive `Field(pattern=...)` annotation regresses `feat-27-validation`'s actionable validation-error messages: pydantic-core enforces `pattern` as a genuine runtime constraint that fires before the existing hand-written `@field_validator(mode="after")`, replacing the actionable message with a generic, unhelpful `String should match pattern '...'` dump. This feature's design must avoid that regression.

### Requirements

- REQ-001: Add a `pattern` (derived from the shared `frontmatter._DATE_TIME_PATTERN.pattern`, no duplicated regex literal) to every whole-body domain's generated JSON Schema for `created`/`updated`, across all twelve domains whose frontmatter subclasses `MarkdownFrontmatter` (`dec`, `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`); `adr`'s distinct `AdrFrontmatter` (no `created`/`updated` fields, does not inherit `MarkdownFrontmatter`) is out of scope.

- REQ-002: The chosen mechanism must not add pydantic-core runtime enforcement beyond the existing `@field_validator(mode="after")` on `created`/`updated`. A prototyped `Field(pattern=...)` was found to violate this (see Overview); `Field(json_schema_extra={"pattern": _DATE_TIME_PATTERN.pattern})` was verified as a working alternative that avoids pydantic-core's own enforcement while still documenting the constraint in the schema.

- REQ-003: Add a regression test asserting that a non-conforming `created`/`updated` value still surfaces the existing actionable message (e.g. "must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset") through `validate_<d>` or equivalent, not a raw pydantic pattern-mismatch message, for at least one domain.

- REQ-004: Add a test asserting the generated JSON Schema for `created`/`updated` actually carries the `pattern` key, for at least one domain (ideally parametrized/looped across all twelve) -- this is currently unverified by any existing test.

- REQ-005: Regenerate both `docs/{type}_schema.json` and each domain's packaged copy `src/biz/dfch/specmgr/{type}/data/{type}_schema.json`, for all twelve affected domains, with zero drift on a second run.

- REQ-006: Update `MarkdownFrontmatter`'s `created`/`updated` docstring text to mention the new schema-level pattern constraint (it currently says only "Free-form date/timestamp").

- REQ-007: Full pre-commit/CI quality gate green: `ruff format`/`ruff check`, `vulture`, the full `unittest` suite, `specmgr docs`, and `specmgr schema` drift detection for both the `docs/` copies and the package-data copies. No test breakage from the schema-shape change.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 -- all twelve affected domains' generated schemas show `pattern` for `created`/`updated`, derived from `frontmatter._DATE_TIME_PATTERN.pattern` with no duplicated regex literal; `adr`'s schema is unchanged.

- [ ] ACC-002: Verifies REQ-002 -- Design Notes records the `Field(pattern=...)` regression finding and the chosen mechanism, with a demonstrated before/after message comparison confirming no runtime behavior change.

- [ ] ACC-003: Verifies REQ-003 -- the regression test described exists and passes.

- [ ] ACC-004: Verifies REQ-004 -- the schema-shape test described exists and passes.

- [ ] ACC-005: Verifies REQ-005 -- both `docs/*_schema.json` and package `*/data/*_schema.json` for all twelve domains regenerate with zero drift.

- [ ] ACC-006: Verifies REQ-006 -- the docstring is updated.

- [ ] ACC-007: Verifies REQ-007 -- the full quality gate is green.

### Scope

#### Included

- Adding schema-level `pattern` documentation for `created`/`updated` across all twelve whole-body domains (`dec`, `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`).

- New regression tests protecting both the message-quality constraint (REQ-002/REQ-003) and the new schema behavior (REQ-004).

- The `MarkdownFrontmatter` docstring update (REQ-006).

- Regenerating both the `docs/` and package-data copies of all twelve affected schemas (REQ-005).

#### Explicitly Out Of Scope

- Any change to the on-disk timestamp format (`yyyy-MM-dd HH:mm:ss.fff`, space-separated) -- existing documents and fixtures stay valid; a `T`-separator (ISO 8601 `T`) migration was considered and explicitly dropped (no parsing benefit on Python 3.11+, and it would break every existing document and require updating ~60 test fixtures for no material gain).

- Any change to `AdrFrontmatter` -- a distinct model with no `created`/`updated` fields, not inheriting `MarkdownFrontmatter`.

- Any change to the runtime validator's error-raising behavior or message content, beyond what is needed to avoid the regression identified in REQ-002 (i.e. the existing actionable message must be preserved verbatim).

### Dependencies

#### Depends On

- `feat-27-validation` (done) -- supplies the actionable validation-error message this feature's REQ-002/REQ-003 constraint exists to protect from regression.

### Design Notes

**The `Field(pattern=...)` regression, and the chosen alternative.** Prototyping `Field(pattern=...)` on `MarkdownFrontmatter.created`/`updated` (during `feat-81-83-validation`'s own investigation) was found to trigger pydantic-core's own runtime `pattern` enforcement, which fires *before* the existing `@field_validator(mode="after")` and replaces the actionable message with a generic `String should match pattern '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$'` dump -- demonstrated end-to-end through `validate_req`. This is exactly the class of opaque-validation-error problem `feat-27-validation` (and `feat-81-83-validation`) exist to eliminate, and no existing test caught it, because every "reject" test for this field only asserts `assertRaises(ValidationError)`, never message content.

`Field(json_schema_extra={"pattern": _DATE_TIME_PATTERN.pattern})` was verified as a safe alternative: it adds the `pattern` key to the generated schema without engaging pydantic-core's own enforcement, so the hand-written validator remains the sole runtime authority. Its only tradeoff is schema shape: the `pattern` key ends up as a sibling of the field's `anyOf` array (informationally covering the whole `str | None` union) rather than nested inside the `anyOf`'s `string` branch the way `Field(pattern=...)` naturally places it. This is a minor imprecision, not a functional problem -- a spec-conforming JSON Schema validator only applies `pattern` to string-typed instances regardless of where the keyword sits, and `null` is never subject to it either way. This tradeoff is accepted given REQ-002's constraint.

**Two generated artifacts per domain.** Each domain has *two* generated schema files that must both regenerate: `docs/{type}_schema.json` (the default `specmgr schema` output directory) and a packaged copy `src/biz/dfch/specmgr/{type}/data/{type}_schema.json` (read by the `specmgr://{type}/schema` MCP resource via `importlib.resources`, so it works from a real, non-editable install). Each has its own dedicated pre-commit hook (`specmgr-schema` for the `docs/` copies, `specmgr-schema-{type}-package` per domain for the package copy) -- both must be checked for drift, not just `docs/`.

**Single source of truth for the regex.** All twelve affected domains' frontmatter subclasses inherit `created`/`updated` unchanged from the shared `MarkdownFrontmatter` base (`models/md/frontmatter.py`), so a single edit to that base class propagates to every domain's generated schema via `XDocument.model_json_schema()`. `adr`'s `AdrFrontmatter` is a separate model with no shared base and is unaffected.

### Task List

#### Phase 1: Schema Exposure

- [x] Task 1.1: Implement the schema-exposure mechanism satisfying REQ-002's constraint (e.g. `Field(json_schema_extra={"pattern": _DATE_TIME_PATTERN.pattern})`) on `MarkdownFrontmatter.created`/`updated`.

- [x] Task 1.2: Update the `created`/`updated` docstring per REQ-006.

- [x] Task 1.3: Regenerate `docs/{type}_schema.json` and each domain's packaged copy for all twelve affected domains; confirm zero drift on a second run.

#### Phase 2: Regression Tests

- [x] Task 2.1: Add a test asserting the generated schema carries `pattern` for `created`/`updated` (REQ-004).

- [x] Task 2.2: Add a test asserting the actionable validator message still surfaces through `validate_<d>` for a non-conforming value, not a raw pydantic pattern-mismatch dump (REQ-003).

#### Phase 3: Verification and Closeout

- [x] Task 3.1: Full quality gate (`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite, `specmgr docs`, `specmgr schema` drift check for both `docs/` and package copies).

- [ ] Task 3.2: Comment on GitHub issue #94 with the outcome; mark this feature done.

## Progress

### Current Status

**As of 2026-09-04**: Phase 1 (Schema Exposure), Phase 2 (Regression Tests), and Phase 3's
quality-gate verification (Task 3.1) are all complete. `MarkdownFrontmatter.created`/`updated` now
carry `Field(json_schema_extra={"pattern": _DATE_TIME_PATTERN.pattern})`, and all twelve affected
domains' `docs/{type}_schema.json` and packaged `src/biz/dfch/specmgr/{type}/data/{type}_schema.json`
copies regenerate with zero drift; `adr`'s schema files are untouched (ADR has no registered schema
type at all). REQ-003/REQ-004 are covered by regression tests. All seven acceptance criteria
(ACC-001 through ACC-007) have been walked through with concrete evidence and are confirmed met.
Only Task 3.2 remains: posting a summary comment on GitHub issue #94 and marking this feature
`done` -- both held pending explicit human confirmation, so the frontmatter `status` here stays
`planning` for now.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 - Phase 3 (Verification and Closeout) quality gate complete

Ran Task 3.1's full quality gate on top of Phase 1 (commit `32ccc14`) and Phase 2 (commit
`b07809a`), starting from and ending with a fully clean working tree (`git status --porcelain`
empty before and after every command below):

- `uv run --frozen ruff format --check`: `1652 files already formatted`.
- `uv run --frozen ruff check`: `All checks passed!`.
- `uv run --frozen vulture src/ whitelist.py --min-confidence 60`: no output (clean).
- `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`: `Ran 3320 tests in
  127.626s` / `OK` -- same 3320-test count Phase 2 left behind (no regressions, no new failures).
- `uv run --frozen specmgr docs`: regenerated `docs/api` + `docs/GENERATED.md`; `git status`
  confirmed zero diff (docs were already current from Phase 1/2).
- `uv run --frozen specmgr schema` (all twelve registered types, `docs/` output): all twelve
  `docs/{type}_schema.json` files reported `(unchanged)` -- `dec`, `feat`, `gol`, `prb`, `qa`, `req`,
  `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`.
- `uv run --frozen specmgr schema --type <t> --output-dir src/biz/dfch/specmgr/<t>/data` for each of
  the same twelve domains: all twelve packaged `{type}/data/{type}_schema.json` copies also reported
  `(unchanged)`.
- Spot-checked `docs/req_schema.json`'s `$defs.ReqFrontmatter.properties.created`/`.updated`: both
  carry `"pattern": "^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}(?:Z|[+-]\\d{2}:\\d{2})$"` as
  a sibling of the `anyOf` array, matching Design Notes' documented tradeoff exactly.
- Confirmed `adr` has no registered schema type at all (`specmgr schema --help`'s `--type` list
  omits it, and no `docs/adr_schema.json`/`adr/data/adr_schema.json` file exists anywhere in the
  repo) -- ADR's schema is untouched, as REQ-001/Scope require.

Walked all seven acceptance criteria against this evidence plus the Phase 1/Phase 2 Updates
entries above; all seven (ACC-001 through ACC-007) are confirmed met. Task 3.2 (GitHub issue
comment + marking the feature `done`) is intentionally NOT done yet -- posting to GitHub and
flipping this document's frontmatter `status` are both held for explicit human confirmation, per
this phase's own instructions. No source, test, or schema files were touched during this
verification pass -- read-only quality-gate commands only, with only this README's Progress
section edited afterward.

#### 2026-09-04 - Phase 2 (Regression Tests) complete

Implemented Tasks 2.1-2.2. Added `TestGeneratedSchemaCreatedUpdatedPattern` to
`tests/commands/test_schema.py` (REQ-004): a single test method loops (via `subTest`) over every
entry in `commands.schema._GENERATORS` (all twelve affected domains: `dec`, `feat`, `gol`, `prb`,
`qa`, `req`, `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`), generates each domain's schema, locates its
`{Domain}Frontmatter` entry under `$defs`, and asserts both `created["pattern"]` and
`updated["pattern"]` equal `frontmatter._DATE_TIME_PATTERN.pattern` exactly -- this was previously
unverified by any existing test. Added
`test_bad_created_value_surfaces_actionable_message_not_raw_pattern_dump` to
`tests/req/tools/test_validate_req.py` (REQ-003): calls `validate_req(..., full=True)` with a
`T`-separated (non-conforming) `created` value and asserts the raised `pydantic.ValidationError`'s
message contains the existing actionable text ("must be the date+time variant 'yyyy-MM-dd
HH:mm:ss.fff' followed by 'Z' or a signed '+HH:mm'/'-HH:mm' offset") and does NOT contain the raw
pydantic pattern-mismatch phrase "String should match pattern" -- guarding specifically against the
`Field(pattern=...)` regression this feature's Design Notes records. No source files or schema JSON
files were touched -- test-only change. Full quality gate green: `ruff format --check`, `ruff
check`, `vulture`, the full `unittest` suite (3320 tests, up from 3318), and `specmgr docs` (no
drift -- no docstrings changed in this phase).

#### 2026-09-04 - Phase 1 (Schema Exposure) complete

Implemented Tasks 1.1-1.3. In `src/biz/dfch/specmgr/models/md/frontmatter.py`, changed `created`/`updated` from plain `str | None = None` fields to `Field(default=None, json_schema_extra={"pattern": _DATE_TIME_PATTERN.pattern})`, confirmed this does NOT engage pydantic-core's own runtime `pattern` enforcement (verified end-to-end: a bad `created` value still raises the original actionable `@field_validator(mode="after")` message, not a generic pydantic pattern-mismatch dump), and updated both fields' docstrings per REQ-006 to mention the new schema-level `pattern` constraint. Regenerated `docs/{type}_schema.json` and each domain's packaged `{type}/data/{type}_schema.json` copy for all twelve affected domains (`dec`, `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`) via `uv run --frozen specmgr schema` and `uv run --frozen specmgr schema --type <t> --output-dir src/biz/dfch/specmgr/<t>/data`; a second run of each produced `(unchanged)` for every file, confirming zero drift. Confirmed `adr`'s schema files show no diff. Full quality gate green: `ruff format --check`, `ruff check`, `vulture`, the full `unittest` suite (3318 tests), and `specmgr docs` (which regenerated only `docs/api/biz.dfch.specmgr.models.md.frontmatter.md` to reflect the docstring change, as expected).

#### 2026-09-04 08:22:35.000Z - Created

Created from GitHub issue #94 ("Expose frontmatter created/updated date+time format in JSON Schema as a pattern"). The issue itself was corrected in place before this feature was drafted: its original acceptance criteria prescribed `Field(pattern=...)` as the implementation mechanism, which a prototype build (during `feat-81-83-validation`'s own investigation) proved regresses `feat-27-validation`'s actionable validation-error messages; the issue's domain list was also missing `qa`. Both are reflected here as REQ-001/REQ-002 and the corrected domain list.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 - Chose `req` for REQ-003 and a parametrized `subTest` loop for REQ-004

REQ-003 ("at least one domain") was satisfied via `req`/`validate_req`, following the plan's own
suggestion and matching an established test pattern already in `tests/req/tools/test_validate_req.py`
(a full-document fixture with a single field swapped, then asserted against via
`assertRaises(...) as ctx` + message inspection) rather than adding a new test file. REQ-004
("ideally parametrized/looped across all twelve") was implemented as a single `subTest`-looped test
method in `tests/commands/test_schema.py` iterating `commands.schema._GENERATORS`, since that module
already owns the one canonical `{domain: generate_fn}` mapping across all twelve affected domains --
avoiding a hand-maintained duplicate list of domain names/`Frontmatter` classes elsewhere, and
`domain.capitalize()` reliably reconstructs each `{Domain}Frontmatter` `$defs` key for every current
single-word domain name.

#### 2026-09-04 08:22:35.000Z - Require the schema-exposure mechanism not to change runtime validation behavior

Decided the feature's Requirements/Acceptance Criteria state a *constraint* (no pydantic-core runtime enforcement beyond the existing validator) rather than prescribing a specific mechanism, since the original GitHub issue's literal `Field(pattern=...)` prescription was demonstrated to violate that constraint. `Field(json_schema_extra={"pattern": ...})` is recorded in Design Notes as a verified-working option, not mandated as the only acceptable one.
