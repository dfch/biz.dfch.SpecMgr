# History: Expose Frontmatter created/updated Date+Time Format in JSON Schema as a Pattern

#### 2026-09-04 09:00:00.000Z - Phase 3 (Verification and Closeout) quality gate complete
Ran Task 3.1's full quality gate on top of Phase 1 (commit `32ccc14`) and Phase 2 (commit
`b07809a`), starting from and ending with a fully clean working tree (`git status --porcelain`
empty before and after every command below):
`uv run --frozen ruff format --check`: `1652 files already formatted`.
`uv run --frozen ruff check`: `All checks passed!`.
`uv run --frozen vulture src/ whitelist.py --min-confidence 60`: no output (clean).
`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`: `Ran 3320 tests in
  127.626s` / `OK` -- same 3320-test count Phase 2 left behind (no regressions, no new failures).
`uv run --frozen specmgr docs`: regenerated `docs/api` + `docs/GENERATED.md`; `git status`
  confirmed zero diff (docs were already current from Phase 1/2).
`uv run --frozen specmgr schema` (all twelve registered types, `docs/` output): all twelve
  `docs/{type}_schema.json` files reported `(unchanged)` -- `dec`, `feat`, `gol`, `prb`, `qa`, `req`,
  `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`.
`uv run --frozen specmgr schema --type <t> --output-dir src/biz/dfch/specmgr/<t>/data` for each of
  the same twelve domains: all twelve packaged `{type}/data/{type}_schema.json` copies also reported
  `(unchanged)`.
Spot-checked `docs/req_schema.json`'s `$defs.ReqFrontmatter.properties.created`/`.updated`: both
  carry `"pattern": "^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}\\.\\d{3}(?:Z|[+-]\\d{2}:\\d{2})$"` as
  a sibling of the `anyOf` array, matching Design Notes' documented tradeoff exactly.
Confirmed `adr` has no registered schema type at all (`specmgr schema --help`'s `--type` list
  omits it, and no `docs/adr_schema.json`/`adr/data/adr_schema.json` file exists anywhere in the
  repo) -- ADR's schema is untouched, as REQ-001/Scope require.
Walked all seven acceptance criteria against this evidence plus the Phase 1/Phase 2 Updates
entries above; all seven (ACC-001 through ACC-007) are confirmed met. Task 3.2 (GitHub issue
comment + marking the feature `done`) is intentionally NOT done yet -- posting to GitHub and
flipping this document's frontmatter `status` are both held for explicit human confirmation, per
this phase's own instructions. No source, test, or schema files were touched during this
verification pass -- read-only quality-gate commands only, with only this README's Progress
section edited afterward.

#### 2026-09-04 09:00:00.000Z - Phase 2 (Regression Tests) complete
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

#### 2026-09-04 09:00:00.000Z - Phase 1 (Schema Exposure) complete
Implemented Tasks 1.1-1.3. In `src/biz/dfch/specmgr/models/md/frontmatter.py`, changed `created`/`updated` from plain `str | None = None` fields to `Field(default=None, json_schema_extra={"pattern": _DATE_TIME_PATTERN.pattern})`, confirmed this does NOT engage pydantic-core's own runtime `pattern` enforcement (verified end-to-end: a bad `created` value still raises the original actionable `@field_validator(mode="after")` message, not a generic pydantic pattern-mismatch dump), and updated both fields' docstrings per REQ-006 to mention the new schema-level `pattern` constraint. Regenerated `docs/{type}_schema.json` and each domain's packaged `{type}/data/{type}_schema.json` copy for all twelve affected domains (`dec`, `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `sop`, `sysrs`, `tsk`, `uc`, `vcr`) via `uv run --frozen specmgr schema` and `uv run --frozen specmgr schema --type <t> --output-dir src/biz/dfch/specmgr/<t>/data`; a second run of each produced `(unchanged)` for every file, confirming zero drift. Confirmed `adr`'s schema files show no diff. Full quality gate green: `ruff format --check`, `ruff check`, `vulture`, the full `unittest` suite (3318 tests), and `specmgr docs` (which regenerated only `docs/api/biz.dfch.specmgr.models.md.frontmatter.md` to reflect the docstring change, as expected).

#### 2026-09-04 08:22:35.000Z - Created
Created from GitHub issue #94 ("Expose frontmatter created/updated date+time format in JSON Schema as a pattern"). The issue itself was corrected in place before this feature was drafted: its original acceptance criteria prescribed `Field(pattern=...)` as the implementation mechanism, which a prototype build (during `feat-81-83-validation`'s own investigation) proved regresses `feat-27-validation`'s actionable validation-error messages; the issue's domain list was also missing `qa`. Both are reflected here as REQ-001/REQ-002 and the corrected domain list.
