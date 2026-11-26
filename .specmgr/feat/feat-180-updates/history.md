# History: Allow Any Markdown Content in Updates/Decisions Made Entries

#### 2026-10-03T10:32:42.000Z - Phase 140 (Upstream dev merge) completed; CHANGELOG pure-union verified, PR #182 CLEAN

Implemented Tasks 140.100-140.170. The merge parent was 818a2e9
(`docs(feat-185): add plan`) -- exactly one docs-only commit past
the plan's stated 8e23fed, adding only the new file
`.specmgr/feat/feat-185-uc-diagrams/README.md` that this branch
never touches; no design impact. `uv sync --all-extras --frozen` ran
before the merge (Task 140.100) and again after the merge commit, so
the phase-end gate ran under the post-merge lockfile environment
(dev's 776c13d uv-group bump landed).

`git merge origin/dev` (Task 140.110) stopped with exactly one
conflict, `CHANGELOG.md` -- the only file both sides touched
(confirmed via `git diff --name-only --diff-filter=U`); everything
else auto-merged. Resolved (Task 140.120) in `[Unreleased]` ->
`### Changed` as the pure union per the feat-153 merge precedent:
our 13-line #180 entry first, dev's 7-line #177 `FEAT`-tag entry
after, then one blank line, then `### Removed` -- nothing else in
the file touched. Committed (Task 140.140) as merge commit 48c0a74
with the default merge message.

ACC-011 verification (Task 140.130): `git diff HEAD^1 HEAD --
CHANGELOG.md` and `git diff HEAD^2 HEAD -- CHANGELOG.md` each show
zero deletion lines (every content line is a `+` line carrying the
other parent's entry), and both entries extract byte-identical from
the committed tree against their respective parents (the 13-line /
7-line spans sed-extracted from each parent and from HEAD, `diff`
clean).

Pre-commit at the merge commit: the hook IS installed (in the
shared common git dir, which all worktrees share) -- the plan's
"no pre-commit hooks are installed in this worktree" parenthetical
was stale. As predicted, for a conflicted-merge commit it checked
only the merge-conflict file: "Checking merge-conflict files
only.", `ruff format` Passed on `CHANGELOG.md`, every other hook
Skipped (no files to check).

Docs regeneration to a fixed point (Task 140.150): `specmgr docs`
(485 `docs/api/` module files + `docs/GENERATED.md`), `specmgr
mcp-docs` (`docs/MCP.md`), `specmgr adr-toc` (`docs/adr/README.md`)
-- `git status --short` empty afterwards: zero drift (feat-180
touched no tool docstrings), no docs commit needed.

Phase-end gate (Task 140.160), post-merge environment: `uv run
--frozen ruff format --check` green (1788 files already formatted),
`uv run --frozen ruff check` green (all checks passed), `uv run
--frozen vulture src/ whitelist.py --min-confidence 60` green (exit
0, no output), full suite green: **4052 passed in 75.69s (0:01:15),
0 failed**.

Push (Task 140.170): `git push origin feat-180-updates` carried the
merge commit (`9cf04b0..48c0a74`). GitHub cleared the conflict
shortly after: `gh pr view 182 --json mergeable,mergeStateStatus`
polls (no `--watch`, 30-120s apart) reported `UNSTABLE`/`MERGEABLE`
while the post-merge CI ran, then
`{"mergeStateStatus":"CLEAN","mergeable":"MERGEABLE"}` -- the
`CONFLICTING` state recorded in the 2026-10-03T08:48:14.000Z entry
is gone. This bookkeeping commit is pushed after that verification,
and the PR's final state is re-confirmed CLEAN by the poll
following this push.


#### 2026-10-03T08:48:14.000Z - Plan extended with Phase 140 (upstream dev merge) and Phase 150 (review); no implementation started

While PR #182 sat open, upstream `dev` advanced 6 commits past this
branch's merge base (fac70948): feat-153 (issue #153, PR #164 --
numbered raw reads + the `update` `UpdateResult` return), feat-177
(issue #177, PR #181 -- `list_references` FEAT tag), the feat-135/
162/163 closeouts, a uv dependency bump, and two feat-plan repairs --
so GitHub now reports the PR `mergeable: CONFLICTING`. A read-only
`git merge-tree` of `origin/dev` (8e23fed, confirmed current via
`git ls-remote`) against this branch shows exactly one conflict:
`CHANGELOG.md`, the only file both sides touched (our 37 changed
files intersect their 197 in one). The conflict sits in
`[Unreleased]` -> `### Changed`, where this feature's #180 entry and
dev's #177 `FEAT`-tag entry both appended at the tail of the bullet
list. Also confirmed: no review of this feature has actually happened
-- the status had been set to `review` (c096158) and the PR opened,
but GitHub carries zero reviews and an empty `reviewDecision`, no
`feat-reviewer` pass is recorded anywhere in this README (the only
"review" mention before this one is the 2026-10-02T15:00:00 plan
refinement), and all 10 original ACC boxes were still unchecked.

Per user direction, the plan was extended in place only (no
implementation started): new `Phase 140: Upstream dev merge
(CHANGELOG conflict)` (Tasks 140.100-140.170: resync the uv.lock,
`git merge origin/dev`, resolve the `CHANGELOG.md` conflict as a
pure union -- our #180 entry first, dev's #177 entry after, each
byte-verbatim against its parent, following the feat-153 merge
precedent recorded in `.specmgr/feat/feat-153-off-by-n/README.md` --
verify the union, regenerate the derived docs to a fixed point, full
gate, push, and poll PR #182 to `CLEAN`) and new `Phase 150: Review
and closeout` (Tasks 150.100-150.130: the `feat-reviewer` subagent
pass against REQ-001..006/ACC-001..011, fix + re-gate any findings,
check off the met ACC boxes, dated review entry, commit + push).
ACC-008 and the Scope's "4 phases" references updated to 6; two new
acceptance criteria added (ACC-011: merge is a pure union and the PR
becomes mergeable; ACC-012: review pass completed and ACCs checked).
Status stays `review`.


#### 2026-10-02T22:12:05.000Z - Phase 130 (CHANGELOG and final verification) completed; implementation finished

Implemented Tasks 130.100-130.130. Task 130.100 added one entry under
`[Unreleased]` -> `### Changed` in `CHANGELOG.md` (appended at the end
of the subsection, after the `update`/`edit` `ValidateResult` entry and
before `### Removed`): the timestamped entries' `content` field
(`UpdateEntry.content` -- `## Updates` in `vcr`/`dec`/`sop`/`sysrs`,
`## Recent Updates` in `tsk`, `### Updates` in `feat` -- and `feat`'s
own `DecisionEntry.content` in `### Decisions Made`) now accepts any
markdown content (multiple paragraphs, lists, code blocks, block
quotes), not just a single CommonMark paragraph, retyped from
`MarkdownParagraph` to the per-domain `UpdateEntryContent`/
`DecisionEntryContent` `MarkdownStr` leaves following the `qa`
`### Introduction` precedent (GitHub issue #114) -- backward-compatible
strict superset, `content` still mandatory, blank/whitespace-only
bodies still failing (GitHub issue #180). Nothing else in
`CHANGELOG.md` touched (no other entries, no `[Unreleased]` header
change, no version bump); `ruff format CHANGELOG.md` reported the file
already formatted.

Phase-end gate (Tasks 130.110-130.130): `uv run --frozen ruff format
--check` green (1782 files already formatted), `uv run --frozen ruff
check` green (all checks passed), `uv run --frozen vulture src/
whitelist.py --min-confidence 60` green (exit 0, no output), final
full suite `uv run --frozen pytest -n auto --cov=src --cov-report=`
green: **3939 passed in 68.84s (0:01:08), 0 failed** -- unchanged from
the Phase 120 baseline (as recorded for Phases 110/120, xdist drops
the unittest-subtest counter from the distributed summary; the last
serial confirmation there reported 2698 subtests).

All four phases (100/110/120/130) are now complete, each with its own
passing-gate commit: b6492cd (Phase 100), ebf4f17 (Phase 110), f6c9f9b
(Phase 120), and this phase's commit for Phase 130 (carrying
`CHANGELOG.md` + this bookkeeping only). Task 130.140: the
orchestrator commits this phase immediately after this entry, then
sets the feature status to `review` and opens the PR.


#### 2026-10-02T21:02:17.000Z - Phase 120 (Regenerate build artifacts) completed as a verification pass; zero drift

Implemented Tasks 120.100-120.120 as a verification pass, not a
regeneration: Phase 100's approved fix-up (Task 100.165, committed in
b6492cd) had already landed every affected artifact -- the 6 domains'
`docs/<d>_schema.json` + packaged
`src/biz/dfch/specmgr/<d>/data/<d>_schema.json` copies
(dec/feat/sop/sysrs/tsk/vcr) and `docs/api/` for the 6 changed
`body.py` modules -- because ACC-008 required the full gate green
before Phase 100's commit and the commit-time pre-commit hooks would
otherwise have forced the same regeneration.

Regeneration confirmation: all 13 `specmgr schema` invocations -- the
12 per-domain pairs (`--output-dir docs/` + `--output-dir
src/biz/dfch/specmgr/<d>/data`, one pair each for dec/feat/sop/sysrs/
tsk/vcr) plus 1 all-types run (no args, all 12 registered types to
`docs/`) -- reported `✓ Wrote ... (unchanged)` and exited 0: the 6
affected and the other 6 `docs/` schemas both agree with the committed
copies, and all 6 packaged copies agree as well. `specmgr docs`
(484 `docs/api/` module files + `docs/GENERATED.md`) and `specmgr
mcp-docs` (`docs/MCP.md`) also reported no drift; `git status --short`
was empty after every regeneration command.

Phase-end gate (Task 120.120): `uv run --frozen ruff format --check`
green (1782 files already formatted), `uv run --frozen ruff check`
green (all checks passed), `uv run --frozen vulture src/ whitelist.py
--min-confidence 60` green (no output), full suite `uv run --frozen
pytest -n auto --cov=src --cov-report=` green: **3939 passed in
72.76s, 0 failed**. As recorded for Phase 110, xdist drops the
unittest-subtest counter from the distributed summary, so the count
was re-confirmed with a serial run: **`3939 passed, 3 deselected,
2698 subtests passed in 296.54s`** -- unchanged from Phase 110's
result, as expected for a no-content-change phase. Task 120.130: the
orchestrator commits this phase immediately after this entry (the
commit carries only this bookkeeping, since the regeneration pass
changed no file).

Anomaly surfaced during bookkeeping (reported during the verification
pass; resolved in this phase's own commit per orchestrator approval):
`parse_feat` of this README with THIS worktree's own feat-180 code
was failing the
`_validate_newest_first` check in BOTH `### Updates` and `###
Decisions Made` -- the 14:30:00 entry in each section sat above the
16:30:00/15:00:00 (Updates) and 16:00:00 (Decisions Made) entries.
That ordering violation was introduced by Phase 100's bookkeeping
(b6492cd) and stayed latent, because under the pre-feat-180
`MarkdownParagraph`-based `UpdateEntry.content` the parse of the
multi-paragraph Phase 100/110 entries failed earlier with "text left
over" and never reached the ordering validator; the feat-180
relaxation is what lets parsing get that far. This entry itself is
valid: a `/tmp` copy with only the two misplaced 14:30 entries
re-sorted to their newest-first positions parses cleanly under this
worktree's code (7 Updates + 6 Decisions entries, this entry's
multi-paragraph content fully captured as `UpdateEntryContent`), so
the re-sort was a mechanical, content-preserving fix. Separately,
this session's MCP
`specmgr_get_feat` still reports the old "text left over" error for
the file because the server process runs pre-feat-180 code from
another checkout -- a restart from a post-feat-180 checkout is needed
to serve the new schema; no tool signatures changed, so `specmgr
mcp-docs` is unaffected (confirmed above).

Resolution: this phase additionally re-ordered the two
`14:30:00.000Z` entries (one in `### Updates`, one in `### Decisions
Made`) that Phase 100's bookkeeping had prepended above newer entries
-- a newest-first violation that stayed latent under the pre-feat-180
model (parsing died earlier with "text left over" on the
multi-paragraph entries) and is now enforced-and-detected because
feat-180's own relaxation lets `parse_feat` reach the ordering
validator. Whole entry blocks were moved byte-for-byte with no
rewording; `parse_feat` on this README now succeeds (`OK 7 6`: 7
Updates + 6 Decisions entries).


#### 2026-10-02T19:52:53.000Z - Phase 110 (New test coverage) completed; full gate green

Implemented Tasks 110.100-110.170; the phase is purely additive as
scoped (test files only, `src/` untouched). Per-domain additions, each a
new test class placed beside the domain's own `UpdateEntry` tests,
mirroring each file's local conventions (`format_text` fixtures,
`str(sut) == text` entry-level round-trips, `assertRaises` negatives,
module docstring extended with a feat-180 coverage line):

- `tests/vcr/models/v1/test_body.py` -- new
  `TestUpdateEntryAcceptsNonParagraphContent` (7 tests: multi-paragraph,
  bullet list, numbered list, fenced code block, block quote -- each
  asserting parse + byte-identical round-trip + raw `.content.text`
  including the trailing `"\n"`; blank-content `AssertionError` negative
  (ACC-005, none existed for vcr before); `model_dump(mode="json")`
  surfaces `- item one\n\n- item two\n` at
  `dump["updates"]["updates"][0]["content"]["text"]` (ACC-006)).
- `tests/feat/models/v1/test_body.py` -- new
  `TestUpdateEntryAndDecisionEntryAcceptsNonParagraphContent` (6 tests;
  the 5 shape tests loop `UpdateEntry`/`DecisionEntry` under their own
  `####` headings via subTest, so both entry classes are covered per
  shape; `model_dump` asserts both
  `dump["progress"]["updates"]["updates"][0]["content"]["text"]` and
  `dump["progress"]["decisions_made"]["decisions"][0]["content"]["text"]`
  on a `Feature` body built from the file's own `_minimal_plan()`
  helper). Blank-content negatives already existed
  (`test_entry_without_lead_paragraph_raises_assertion_error`) --
  confirmed unmodified, not duplicated.
- `tests/dec/models/v1/test_body.py` -- new
  `TestUpdateEntryAcceptsNonParagraphContent` (6 tests: the 5 shapes +
  `model_dump` at `dump["updates"]["updates"][0]["content"]["text"]`;
  the existing blank-content negative confirmed unmodified).
- `tests/sop/models/v1/test_body.py` -- new
  `TestUpdateEntryAcceptsNonParagraphContent` (6 tests, same shape;
  existing blank-content negative confirmed unmodified).
- `tests/sysrs/models/v1/test_body.py` -- new
  `TestUpdateEntryAcceptsNonParagraphContent` (7 tests, including the
  blank-content negative -- none existed for sysrs before -- and
  `model_dump` at `dump["updates"]["updates"][0]["content"]["text"]`).
- `tests/tsk/models/v1/test_body.py` -- new
  `TestUpdateEntryAcceptsNonParagraphContent` (7 tests, including the
  blank-content negative -- none existed for tsk before -- and
  `model_dump` at `dump["recent_updates"]["updates"][0]["content"]["text"]`
  on a full `Task` body, the exact key path
  `tests/tsk/tools/test_parse_tsk.py` pins at document level).

Fixture stability: every body used in a round-trip assertion is
mdformat-stable under the engine's own options (`{"number": True}` +
`simple_breaks`), verified by running `format_text` over each candidate
and by a pre-write scratch run through every domain's real
`UpdateEntry`/`DecisionEntry` (all 5 shapes x all 6 domains parsed,
round-tripped byte-identically, and exposed the expected raw
`.content.text`; blank and whitespace-only bodies raised the engine's
mandatory-field `AssertionError`; a `+`-bullet confirmed to normalize
to `-`). Block-quote coverage was included in all 6 domains (the plan
required at least 3).

`test_parser.py` check (Tasks 110.130/110.140/110.150/110.155): all 6
domains' `tests/<d>/models/v1/test_parser.py` read in full -- every
Updates/Decisions Made fixture in those files is a single-paragraph
entry (still valid, REQ-005), and the exact-value `.content.text`
assertions (vcr:193-194, dec:268-269, tsk:81/105-109/193) already carry
the trailing `"\n"` form from Phase 100's fix-up; no paragraph-specific
assumption breaks or under-tests the new capability, so NO change was
needed in any of the 6 files. `tests/tsk/tools/test_create_tsk.py`
confirmed passing unmodified (its only `## Recent Updates` fixture is a
single paragraph). All existing bare-`assertRaises` negatives
(heading-only entries, zero-entry containers, out-of-order entries)
pass unmodified -- ACC-005/REQ-003 semantics preserved.

Phase-end gate (Task 110.170): `uv run --frozen ruff format --check`
green (1782 files already formatted), `uv run --frozen ruff check` green
(all checks passed), `uv run --frozen vulture src/ whitelist.py
--min-confidence 60` green (no output), full suite
`uv run --frozen pytest -n auto --cov=src --cov-report=` green:
**3939 passed, 0 failed** (Phase 100's 3900 + 39 new tests). On this
120-core box `-n auto` (120 workers) drops the unittest-subtest counter
from xdist's summary line, so the count was re-confirmed with `-n 4`:
**`3939 passed, 2698 subtests passed in 139.34s`** (Phase 100's 2688
subtests + the 10 new ones from feat's 5x2-class shape loops). Task
110.180: the orchestrator commits this phase immediately after this
entry.


#### 2026-10-02T17:40:00.000Z - Phase 100 fix-up completed per user-approved resolution; full gate green

Implemented Task 100.165 per the user-approved resolution of the
29-failure analysis above (see the Decisions Made entry of the same
timestamp): (a) updated the 21 scalar (+10 tuple) pre-existing expected
values across the 6
domains' `test_body.py`/`test_parser.py` files plus
`tests/tsk/tools/test_parse_tsk.py` -- the exact-value `.content.text` /
`model_dump()` assertions that pinned the old `MarkdownParagraph.text`
stripped form now expect the new leaf type's raw form (old string +
trailing `"\n"`, the same shape qa's own `IntroductionBody` test asserts
at `tests/qa/models/v2/test_body.py:230`); mechanical expected-value
changes only, no test logic touched. (b) Deleted
`tests/regression/test_issue_27.py`'s
`TestFeat7Task029StrayListMarkerRegression` (3 tests) together with its
trigger-2 fixtures (`_FEAT_7_TASK_0_29_BODY`,
`_FEAT_7_TASK_0_29_VALID_SEED_BODY`, `_FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS`,
`_FEAT_7_TASK_0_29_EXPECTED_SUBSTRINGS_VIA_VALIDATE`) and section banner:
the pinned trigger (a `+`-prefixed continuation line inside a
`## Recent Updates` entry) is now valid any-markdown content by design
(issue #180, ACC-003); `TestIssue27BareDomainTokenRegression` is
untouched, no import became unused, and the module docstring now records
the supersession, pointing to the remaining engine-level pin in
`tests/models/md/test_validation_error_baseline.py`
(`test_list_field_leaves_a_stray_list_marker_line_unconsumed`).
(c) Regenerated the stale artifacts: `specmgr schema` (6 of 12 `docs/`
schemas changed -- dec/feat/sop/sysrs/tsk/vcr; the other 6 unchanged),
the 6 packaged `<d>/data/<d>_schema.json` copies (all changed, including
`tsk`'s, whose drift test does not exist -- pre-existing asymmetry left
untouched, the pre-commit `specmgr-schema-tsk-package` hook still
enforces it), `specmgr docs` (the 6 changed domains' `docs/api/...body.md`
exports refreshed; `docs/GENERATED.md` unchanged), and `specmgr mcp-docs`
(confirmed no drift -- tool signatures unchanged). Final gate (Task
100.170): `ruff format --check` green (1782 files already formatted),
`ruff check` green (all checks passed), `vulture` green, full suite
`3900 passed, 2688 subtests passed in 74.84s` -- 0 failed (the previous
3874 passed + 29 failed minus the 3 deleted regression tests). Task
100.180: the orchestrator commits this phase immediately after this
entry.


#### 2026-10-02T16:30:00.000Z - Clarified why the manual phase-end gate isn't redundant with pre-commit hooks

Added a Design Notes paragraph explaining that each phase's manual
quality-gate task (ruff format/check, ruff check, vulture, full test
suite) is not duplicate busywork even though this repo's installed
pre-commit hooks already re-enforce the identical checks -- plus
schema/docs drift -- automatically on every `git commit` touching
`src/**/*.py`/`tests/**/*.py`: the manual run is purely for fast local
feedback, catching a failure before attempting the commit rather than
discovering it mid-commit and having to fix-then-retry.


#### 2026-10-02T15:00:00.000Z - Plan refined after codebase-verification review

Reviewed the plan against the actual codebase (per-domain `body.py` files,
the `feat-114` `IntroductionBody` precedent, `models/md/markdown_str.py`
internals, existing tests, schema files, and `CHANGELOG.md`) and corrected
several issues: (1) Phase 110's premise that existing tests need
`MarkdownParagraph`-specific error-message fixes was false -- no such
assertions exist in any of the 6 domains; reworded all Phase 110 tasks to
be purely additive and added an explanatory paragraph to Design Notes;
(2) Tasks 100.100 (`vcr`) and 100.130 (`dec`) incorrectly implied
`MarkdownParagraph` might be dropped -- it stays in use elsewhere in both
files (`CrossReference`/`Coverage`/`AcceptanceCriterion` in `vcr`,
`DecisionOutcome.statement` in `dec`), now stated explicitly; (3) resolved
an inconsistency where only `tsk`'s `test_create_tsk.py` was singled out
for an edit it doesn't need, and only `sop`/`tsk` called out `test_parser.py`
checks -- added Task 110.155 for `vcr`/`feat`/`dec` parity and clarified
`test_create_tsk.py` needs no change; (4) Task 120.100 now spells out the
two separate `specmgr schema` invocations per domain; (5) Task 130.100 now
specifies the `### Changed` CHANGELOG subsection; (6) Design Notes now
notes that this extends the `feat-114` `IntroductionBody` idiom into new
(mandatory-field) territory rather than being a pure mirror, and that
`.text` is also required for existing call-site compatibility, not just
`model_dump()`.


#### 2026-10-02T14:30:00.000Z - Phase 100 (Model change) implemented; full suite shows 29 pre-existing-test failures for Phase 110 to correct

Implemented Tasks 100.100-100.160: added the per-domain
`UpdateEntryContent(MarkdownStr)` leaf class (plus `feat`'s
`DecisionEntryContent`) with a `text` computed property
(`return self._value`, mirroring `qa`'s `IntroductionBody.text` from
feat-114), and retyped `UpdateEntry.content` (all 6 domains) and
`DecisionEntry.content` (feat) from `MarkdownParagraph` to the new leaf
type, in `vcr`/`feat`/`dec`/`sop`/`sysrs`/`tsk`'s own
`models/v1/body.py`. Imports: `MarkdownStr` added in all 6;
`MarkdownParagraph` kept in `vcr` (still used by
`CrossReference.value`/`.notes`, `Coverage.value`,
`AcceptanceCriterion.description`) and `dec` (still used by
`DecisionOutcome.statement`), dropped in `feat`/`sop`/`sysrs`/`tsk`
(verified unused after the retypes); the module docstrings of the 4
drop-import files that listed `MarkdownParagraph` among the engine
components now name the new leaf class(es) instead; the "lead paragraph"
wording in each `UpdateEntry`/`DecisionEntry` docstring/Field description
now says the entry's own update/decision text (any markdown content) --
the "Mandatory" claim is kept. No `models/md` engine changes, no new
validator code, no `__init__.py` export changes (the feat-114
`IntroductionBody` precedent is also un-exported), and heading structure /
`@alias` timestamp pattern / `min_length=1` / newest-first check all
untouched.

Phase-end gate (Task 100.170) run: `ruff format --check` green (1782
files already formatted), `ruff check` green (all checks passed),
`vulture src/ whitelist.py --min-confidence 60` green (no whitelist
change needed -- the `text` name is already marked used by existing
`self.text` accesses in `src/`, exactly as for the `IntroductionBody`
precedent, which carries no whitelist entry either); full suite
**red**: `29 failed, 3874 passed in 74.66s`. All 29 are pre-existing
tests the plan predicted would pass unmodified; they fall in three
groups: (1) 21 scalar (+10 tuple) exact-value assertions on
`.content.text` /
`model_dump()` values in the 6 domains' `test_body.py`/`test_parser.py`
/ `tests/tsk/tools/test_parse_tsk.py` that pin the OLD
`MarkdownParagraph.text` behavior (re-parse + `.strip()`, no trailing
newline) -- the new leaf type exposes `_value` raw, which carries
mdformat's canonical single trailing newline; qa's own shipped test for
the precedent idiom asserts exactly that trailing newline
(`tests/qa/models/v2/test_body.py:230`:
`assertEqual(sut.introduction.body.text, "Some intro text.\n")`);
single-paragraph round-trips were verified byte-identical and
blank/whitespace-only content still fails with the engine's
mandatory-field zero-extent check, so the model change itself is correct
per the plan's Design Rules -- these 21 scalar (+10 tuple) assertions
need the trailing
`"\n"` added; (2) 3 `tests/regression/test_issue_27.py`
`TestFeat7Task029StrayListMarkerRegression` tests whose fixture puts a
`+`-prefixed line inside a `## Recent Updates` entry -- that content is
now legitimate any-markdown (ACC-003) and parses instead of raising,
which is precisely the semantic change issue #180 requests; the plan's
Design Notes analyzed only the blank-content negative path ("the new
leaf type's `get_extent` returns `0` for blank text exactly like
`MarkdownParagraph.get_extent`") and missed this now-valid list path, so
those 3 regression tests need re-scoping (the feat-7 stray-list-marker
trigger no longer applies inside update entries); (3) 5
`test_matches_fresh_generate_{feat,dec,sop,sysrs,vcr}_schema_output`
schema-drift tests whose packaged `schema.json` copies predate the model
change -- regenerated by Phase 120 (or the commit-time
`specmgr-schema`/`specmgr-schema-<domain>-package` pre-commit hooks,
which run before the commit-time test hook). Tasks 100.170/100.180 stay
open until groups (1)+(2) are corrected (Phase 110's scope -- its tasks
were planned as purely additive on a premise this run proved false) and
group (3) by Phase 120 / the commit hook.


#### 2026-10-02T14:15:00.000Z - Created

Feature folder created from GitHub issue #180, following a plan-mode
design discussion that: (1) confirmed scope as all 6 domains (`vcr`,
`feat`, `dec`, `sop`, `sysrs`, `tsk`) including `feat`'s `DecisionEntry`;
(2) confirmed a new per-domain `UpdateEntryContent`/`DecisionEntryContent`
leaf class (mirroring `feat-114`'s `IntroductionBody(MarkdownStr)` idiom)
replaces `MarkdownParagraph` as the field type; (3) confirmed `content`
stays mandatory and non-blank is enforced for free by the engine's
existing mandatory-field zero-extent check, with no new validator code
required; (4) confirmed example/template markdown files are left
unchanged, since the relaxation is a strict superset and existing
single-paragraph examples remain valid.
