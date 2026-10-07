# History: Uniform Full ISO 8601 Date+Time Timestamps (T-Canonical Frontmatter, Both Separators Accepted)

#### 2026-09-24 18:26:19.805Z - Phase 4 complete: 8 previous-feature supersession notes, CHANGELOG/AGENTS.md closeout, ADR accepted + TOC regenerated, issue #146 commented, full gate green

Task 4.1: added one brief supersession blockquote (each citing ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf) to 8 of the 11 previous feature READMEs -- the 5
unconditional ones (feat-38-39-41-43-44, feat-32-sysrs, feat-67-70-71,
feat-104-109-set-status-noop-dec-docs, feat-94-frontmatter-schema) plus 3 of the 6
verify-by-grep candidates that carry timestamp-format decisions: feat-31-feature (its pinned
`### Updates`/`### Decisions Made` heading regex and its frontmatter plain-`YYYY-MM-DD`-to-
microsecond-timestamp decision), feat-10-add-artifact-type-tasklist (its free-form `## Recent
Updates` entry-heading decision), and feat-21-decision (its TSK-style free-form `## Updates`
entry decision plus its date-only `created`/`updated: YYYY-MM-DD` frontmatter wording). The
other 3 candidates carry no format decisions and got no note (grep evidence: feat-33-vcr has
only `{timestamp}` placeholders describing heading nesting, no format pinned; feat-5-md-model-
parser only self-referential "Recent Updates" mentions of its own progress log; feat-93-feat-
template only feat-parser-compliance wording about the canonical heading format it migrated
to). Per-file `parse_feat` before/after status: OK→OK for feat-38-39-41-43-44, feat-67-70-71,
feat-104-109 (the 3 parseable files, verified by re-parsing after the edit); FAIL→FAIL with
the same pre-existing error for feat-32-sysrs, feat-94-frontmatter-schema, feat-31-feature,
feat-10-add-artifact-type-tasklist, feat-21-decision (line numbers shifted +4 only);
feat-33-vcr/feat-5/feat-93 untouched. Note placement: directly below the H1 is structurally
impossible in the 3 parseable READMEs (the feat parser requires `## Plan` as the first token
after the H1 -- verified empirically before any edit), so per the plan's adjust clause all 8
notes were placed at the end of the `### Overview` section instead, consistently (see
Decisions Made). No doc repair of those READMEs per the plan (pre-existing parse failures stay
out of scope, tracked by `docs/tsk/tsk-2687d267`).
Task 4.2: `CHANGELOG.md` gained a `### Breaking Changes` entry under `[Unreleased]`
(uniform full date+time contract: frontmatter `created`/`updated` of all twelve whole-body
domains now written `T`-separated (machine canonical) and accepting `T` or space; tsk/dec/vcr/
sysrs dated entry headings tightened from date-or-full to full date+time only, with the
repo-owned inventory migrated in the same change; feat/sop entry headings additionally accept
`T`; newest-first ordering now compares full timestamps as aware datetimes), citing the ADR +
GitHub issue #146 (feat-146-date-time); AGENTS.md's feature-frontmatter convention line was
updated from (`YYYY-MM-DD`, ...) to the new full date+time contract with the ADR cited -- only
that wording touched.
Task 4.3: the ADR was set to `accepted` via the generic `set_status` (`type="adr"`,
`id="8c889262-152b-4b8e-ae2c-75371f7a9edf"`); `get_adr` confirms `status: accepted` and the
on-disk ADR file diffed to exactly one line (`status: draft` → `status: accepted` -- ADR
frontmatter has no `created`/`updated`, only the free-form `date`, left untouched).
Regenerations: `specmgr adr-toc` changed `docs/adr/README.md` (the 8c889262 entry's
"Status: draft" → "Status: accepted", the only diff); `specmgr docs` (470 api files +
GENERATED.md) and `specmgr mcp-docs` (docs/MCP.md) were both no-ops with zero working-tree
changes (no src/ docstring changes and no new tools/resources/prompts this feature). Posted
the closeout comment on GitHub issue #146
(https://github.com/dfch/biz.dfch.SpecMgr/issues/146#issuecomment-5819537651, comment id
5819537651, posted 2026-09-24T18:09:45Z): fix summary + branch `feat-146-date-time` (PR
pending) + ADR reference; deliberately no "fixes #146" (that belongs in the PR body) and the
issue was left open.
Task 4.4: full quality gate green -- `ruff format --check` (1715 files already formatted) +
`ruff check` (All checks passed), vulture clean (no output), `pytest -n auto --cov=src
--cov-report=` **3440 passed** (exact Phase 3 baseline), `coverage report -m` TOTAL
**10551/122 = 99%** (`docs/coverage.svg` byte-identical, no changes), pylint **8.92/10
(+0.00)** (src untouched this phase), `specmgr schema` 12/12 `(unchanged)`. Files changed by
Phase 4 overall: the 8 supersession notes, CHANGELOG.md, AGENTS.md, the ADR frontmatter line,
docs/adr/README.md, and this plan README; everything left uncommitted for the orchestrator.


#### 2026-09-24 16:56:53.646Z - Phase 3 complete: 3 docs/ headings migrated to midnight UTC, parse gate green (sysrs appendix excluded per user ruling)

Per the orchestrator-relayed user ruling (final), `docs/sysrs/sysrs-8d752304-...-appendix.md`
is **not** a real sysrs document (it is a manual feat-84 concatenation of all referenced
artifacts, commit bca1a87) and is excluded from the Task 3.2 parse gate -- its raw-HTML H1
issue is out of scope and was left unrepaired (recorded in Decisions Made). With the
exclusion in place, the throwaway gate script re-ran clean: **57 parsed OK, 0 FAIL, 1
excluded** -- per-domain tally: adr=36 (`models.adr.v1.parse_adr`), gol=2, req=14, sop=1,
sysrs=1 (the real sysrs document; the 3 migrated `docs/tsk` x2 + `docs/sysrs` x1 headings
all parse), tsk=3; `docs/adr/README.md` (generated TOC) and the generated/binary artifacts
(`docs/api/`, `docs/GENERATED.md`, `docs/coverage.svg`, `docs/MCP.md`, `docs/*_schema.json`,
2 `.pdf` files) skipped as non-documents. Phase-end full quality gate re-run on the finished
tree, all green: `ruff format --check` (1715 files already formatted) + `ruff check` (All
checks passed), vulture clean, `pytest -n auto --cov=src --cov-report=` **3440 passed**
(exact Phase 2 baseline), `coverage report -m` TOTAL **10551/122 = 99%** (`docs/coverage.svg`
byte-identical, no `coverage-badge` re-run needed), pylint **8.92/10 (+0.00)** (src untouched
this phase), `specmgr schema` 12/12 `(unchanged)` + `specmgr docs` (470 api files +
GENERATED.md) with zero working-tree changes (drift-free). Task 3.2 marked `[x]`; the earlier
"Phase 3 blocked" entry stands as history. Files changed by Phase 3 overall: the 3 `docs/`
heading lines (Task 3.1) + this plan README; everything left uncommitted for the orchestrator.


#### 2026-09-24 09:57:29.222Z - Phase 3 blocked: docs/ 3-heading migration done (Task 3.1); parse gate 57/58 pass with one pre-existing unrelated failure (Task 3.2)

Task 3.1: migrated the 3 and only 3 date-only entry headings in `docs/` (verified
by grep `^#{2,4} \d{4}-\d{2}-\d{2} -` returning exactly these 3 before the change) to
space-form midnight UTC, preserving date, separator glyph, and title:
`docs/tsk/tsk-699432f5-...-extract-mcp-instance-py-to-break-domain-server-cyclic-import.md:24`
`### 2026-08-19 - Created` → `### 2026-08-19 00:00:00.000Z - Created`;
`docs/tsk/tsk-602740af-...-fix-markdownlistitem-get-extent-for-numbered-lists.md:36`
`### 2026-08-18 - Created` → `### 2026-08-18 00:00:00.000Z - Created`;
`docs/sysrs/sysrs-8d752304-...-system-requirements-specification-biz-dfch-specmgr.md:213`
`### 2026-09-03 - Created` → `### 2026-09-03 00:00:00.000Z - Created`. No other
bytes changed (frontmatter mass-migration explicitly out of scope; `git diff --stat`:
3 files, +3/-3). Task 3.2 (parse gate): no existing test or script walks `docs/`
(checked `tests/`), so a throwaway script parsed every `docs/<domain>/*.md` through
its own domain's model parser (`gol/req/sop/sysrs/tsk.models.v1.parser.parse_<d>`)
plus `docs/adr/*.md` (36 ADRs, README.md skipped as generated TOC) through
`models.adr.v1.parse_adr` -- 58 files total: **57 OK, 1 FAIL**. The 3 migrated
documents all parse. The one failure is pre-existing and unrelated to timestamps
(both the file and `src/` are unmodified at HEAD b526c21):
`docs/sysrs/sysrs-8d752304-...-appendix.md` fails with ```AssertionError: raw HTML is
not permitted in a parsed document at line 362 (relative to this text's own
numbering): html_inline '<domain>'; fix: wrap it in a code span (e.g. `<domain>`) or
write it as an HTML comment (e.g. `<!-- <domain> -->`) instead``` -- the appendix
(manual feat-84 concatenation, commit bca1a87) embeds ADR ec9f5262's own H1 heading
verbatim (`# Expose <domain>_list as paged MCP tools (list_<domain>), not
resources`) into sysrs body text, which the sysrs body parser rejects while
`parse_adr` accepts it fine as an ADR H1. This file is not tracked by the
`.specmgr/feat` README failure list `docs/tsk/tsk-2687d267` either. Per the plan's
hard-constraint hazard clause ("if any `docs/` document fails for a reason unrelated
to timestamps (a pre-existing failure), STOP and report it with the error instead of
fixing it"), the failure is reported and Task 3.2 left open for orchestrator triage;
fixing it (wrapping the bare `<domain>` tokens in code spans/HTML comments) would be
a one-line content repair to a file outside this phase's allowed change set. Quality
gate on the migrated tree (all green): `ruff format --check` (1715 files already
formatted) + `ruff check` (all checks passed), vulture (clean), `pytest -n auto
--cov` **3440 passed** (exact Phase 2 baseline; `test_issue_67.py` -- whose narrow
midnight-migration-heading exclusion exists precisely so the 3 migrated headings
don't trip it -- passes in the suite), `coverage report` TOTAL **10551/122 = 99%**
(`docs/coverage.svg` byte-unchanged, no `coverage-badge` re-run needed), pylint
**8.92/10 (+0.00)** (src untouched this phase), `specmgr docs` (470 api files +
GENERATED.md, zero working-tree changes) and `specmgr schema` (12/12 `(unchanged)`)
drift-free. Files changed by this phase so far: the 3 `docs/` heading lines + this
plan README.


#### 2026-09-24 09:18:11.741Z - Phase 2 complete: six entry-heading domains on the shared full date+time fragment ([T ] accepted, date-only rejected), _ordering mixed-granularity branch deleted, packaged data + 10 instruction files + test suite migrated

Implemented Tasks 2.1-2.7. Entry headings: `feat` (`UpdateEntry`/`DecisionEntry` alias +
pattern) and `sop` (`UpdateEntry` alias + pattern) widened to `[T ]`; `tsk`
(`RecentUpdates`), `dec`/`vcr`/`sysrs` (`Updates`) tightened to the mandatory full form with
`[T ]` -- all six sites now accept exactly the shared fragment
`\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})`, the same fragment as
Phase 1's frontmatter pattern (verbatim, per the plan's Design Notes). `models/md/_ordering.py`
dropped `_DATE_ONLY_LENGTH` and its mixed date-only/date+time day-granularity branch (now a
plain aware `datetime.fromisoformat` comparison; module + function docstrings updated), and the
five `Updates`/`RecentUpdates` `_validate_newest_first` delegate docstrings plus the six body
docstrings' leniency wording (REQ-004 / "locked post-sibling shape" / "deliberately not the
same format as frontmatter") were rewritten to cite ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf; `models/md/frontmatter.py`'s now-stale "until feat-146
Phase 2 tightens those too" note was updated to state all six entry-heading aliases enforce the
same full fragment. Packaged data: the 8 date-only entry headings
(`dec_example:136`, `sysrs_example:535/541`, `sysrs_template:236`, `tsk_example:25/29`,
`tsk_template:22`, `vcr_template:54`) became space-form midnight UTC
(`### {date} 00:00:00.000Z - {title}`), and all 12 of the six domains' example/template files
still parse through their own parsers. The 8 tsk/dec/vcr/sysrs instruction files were rewritten
to describe the full form only with space-form examples (the 4 update instructions gained an
explicit heading-format note where they previously had none), and the feat/sop create
instructions' format wording was aligned (both separators accepted; the sop "different format
from the frontmatter dates" claim dropped -- it is the same full format now); `tsk_implement`/
`feat_update`/`sop_update` were checked and carry no format wording. Tests: the 4 domain test
files (tsk/dec/vcr/sysrs `test_body.py`) flipped date-only accept→reject (alias `match_alias`
rejections + `from_text` `AssertionError` rejections, mirroring the existing rejection-test
style), every date-only entry-heading fixture in the suite (21 files, incl. the
tsk/tools + general/tools + regression fixtures) migrated to full form, `test__ordering.py`
dropped its 7 date-only/mixed-granularity cases and gained same-day `T`-vs-space ordering cases,
`T`-accept tests were added for all six domains (11 new tests net, suite now 3440 passed), and
`test_issue_67.py`'s date-only-heading exclusion (moot per the ADR's consequences) was replaced
by a narrow exclusion of the documented midnight-UTC migration heading shape, which the
migrated packaged headings would otherwise trip (see Decisions Made). Gate: `specmgr schema`
regenerated 6 of 12 `docs/*_schema.json` (dec/feat/sop/sysrs/tsk/vcr -- the six entry-heading
domains) + their packaged `data/` copies (the other 6 unchanged), `specmgr docs` regenerated 7
`docs/api/` files, `specmgr adr-toc`/`specmgr schema`/`specmgr docs` all drift-free on re-run,
ruff format/check + vulture clean, coverage TOTAL 10551 stmts / 122 missed = 99% (down from
10557/126 -- the deleted `_ordering` branch removed covered statements; `docs/coverage.svg`
still reads 99%, byte-identical), pylint 8.92/10 unchanged with only pre-existing types'
numeric counters shifted (+11 C0116 from the new docstring-less tests matching file convention,
+1 C0301 long string-literal line, +1 R0801 duplicate-code pair). Note: the 3 `docs/` entry
headings (`docs/tsk` x2, `docs/sysrs` x1) now fail to parse -- expected at Phase 2 end,
migrated in Phase 3.


#### 2026-09-24 06:09:11.544Z - Phase 1 fix: coverage-badge regression repaired (12 parser-level unquoted-timestamp tests; badge back to 99%)

Orchestrator verification of the Phase 1 commit found the pre-commit `specmgr coverage-badge`
hook failing: the Phase 1 `_stringify_metadata` rewrite added 3 previously-uncovered lines per
whole-body-domain parser (the `datetime`-coercion branch and the `str()` else branch of the new
loop, 36 lines total) -- no per-domain parser test ever fed an unquoted full timestamp through
PyYAML, so suite coverage dropped to 162 missed (98.46%) and the hook rewrote
`docs/coverage.svg` to 98%. Fix (no design change -- Phase 1's `Decisions Made` entry stands
unchanged): one new focused test per domain in each of the twelve `tests/<d>/models/v*/
test_parser.py` (`TestUnquotedTimestampNormalization.test_unquoted_timestamps_converges_to_t_canonical_form`,
12 new tests total, mirroring each file's own minimal-document fixture style and reusing its
existing `ValidationError` import): it parses the domain's minimal document with `created`
unquoted `T`-form and `updated` unquoted space-form (both PyYAML-coerced to `datetime`), asserts
both converge to the `T`-canonical form (REQ-006), and asserts an unquoted date-only `created`
still raises `ValidationError` (REQ-003 -- that failing parse is what covers the `str()` else
branch). Result: all 12 whole-body parsers back to 100% (22/22 statements, 0 missed), TOTAL back
to exactly the pre-Phase-1 126 missed (10557 statements, 99%), `docs/coverage.svg` regenerated
to 99%. Full gate re-run green: ruff format/check (1715 files), vulture (clean), `specmgr
schema` 12/12 `(unchanged)` + `specmgr docs` drift-free (no working-tree changes),
`pytest -n auto --cov` 3429 passed (3417 + 12), pylint 1837 findings / 8.92 -- identical to the
pre-change baseline apart from the three Phase-1 numeric shifts already noted below. The `qa`
file (the only one without a `_MINIMAL_DOC` constant) uses its own `_VALID_DOC` fixture.


#### 2026-09-24 04:45:51.954Z - Phase 1 complete: T-canonical frontmatter write/read core, [T ] pattern, 53-file test sweep, schemas/docs regenerated, full gate green

Implemented Tasks 1.1-1.5. Write side: `general/tools/_timestamps.py`'s `format_timestamp`/
`now_timestamp` now emit `yyyy-MM-ddTHH:mm:ss.fff` + (`Z`|`±HH:mm`) (delegating to the new shared
core), `format_date` removed (its only callers were its own two tests). Read side:
`MarkdownFrontmatter._DATE_TIME_PATTERN` widened to `[T ]` (date-only, six-digit-fraction, and
timezone-less values still rejected; the D5 validator message/docstrings updated), and all twelve
whole-body domain parsers' `_stringify_metadata` copies now normalize PyYAML-coerced `datetime`
values to the `T`-canonical form via the new shared `models/md/_timestamps.py`
(`format_timestamp` + `normalize_yaml_datetime` with a sub-millisecond guard so an unquoted
six-digit fraction is left for the pattern's actionable rejection rather than silently truncated
into an accepted shape). Sweep: 24 packaged template/example frontmatters +
`tests/feat/models/v1/data/feat_reference.md` (byte-identical to `feat_example.md`, verified) +
`rsk/tools/_sentinel.py`'s own fixture to `T`; 53 test files' space-form frontmatter fixtures/
writer-output assertions to `T` (explicit space-acceptance tests kept in
`tests/models/md/test_frontmatter.py` -- `reject_t_separator` flipped to `accept_t_separator`,
new `accept_space_separator`), `tests/general/tools/test__timestamps.py` rewritten to the `T`
form (12 tests kept: two `format_date` tests replaced by two `T`-separator tests), new
`tests/models/md/test__timestamps.py` (14 tests) covering the shared core + the unquoted-value
matrix (T/space/Z/second-precision accepted; six-digit, date-only, naive rejected). `specmgr
schema` regenerated all twelve `docs/*_schema.json` + their packaged `data/` copies (the
pre-commit hook's `--output-dir` syncs), `specmgr docs` regenerated 470 `docs/api/` files +
`docs/GENERATED.md`. Full quality gate green: ruff format/check (1715 files), vulture (clean),
`pytest -n auto --cov` 3417 passed (baseline 3402: +14 new shared-module tests, +1 new
space-acceptance test, +2 new `T`-separator tests, -2 removed `format_date` tests), pylint 1837
findings before and after with only three pre-existing findings' numeric counters shifted (no new
findings). Phases 2-4 remain.


#### 2026-09-23 20:40:25.711Z - Phase 0 complete: adr-toc regenerated, full quality gate green

Created the ADR (8c889262-152b-4b8e-ae2c-75371f7a9edf, `draft`), created this feature folder,
regenerated `docs/adr/README.md` via `specmgr adr-toc`, and ran the phase-end full quality gate
green (ruff format/check, vulture, `pytest -n auto --cov` -- 3402 passed). Implementation
(Phases 1-4) is deliberately not started yet.


#### 2026-09-23 20:31:28.001Z - Created

Feature created for GitHub issue #146 (`create_feat` fails on date-only `Updates`/`Decisions Made`
timestamps, inconsistent with `create_tsk`); plan finalized after the format decisions were
confirmed with the requester, and the ADR (8c889262-152b-4b8e-ae2c-75371f7a9edf) was created as
`draft` ahead of this folder.
