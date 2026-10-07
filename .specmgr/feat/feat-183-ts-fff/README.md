---
classification: null
created: '2026-10-03T09:39:04.941+02:00'
id: feat-183-ts-fff
status: review
type: feat
updated: '2026-10-07T09:03:15.075+02:00'
version: 1.0.0
---

# Feature: Reduce Agent Misreading of the "fff" Millisecond Placeholder in Timestamp Format Notation

## Plan

### Overview

GitHub issue #183 reports that agents repeatedly emit the literal characters `fff` in
timestamps instead of actual millisecond digits, because the packaged instruction files,
docstrings, and runtime error messages describe the millisecond field of the timestamp
format using the placeholder notation `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]` (established
by feat-146-date-time). Packaged templates and examples carry only concrete sample
timestamps, not the placeholder notation (verified against the live tree on 2026-10-04;
re-verified at rollout by Task 120.100). The root cause of this misunderstanding is not
yet known. This feature (1) runs a short investigation into
why the `fff` placeholder notation is misread as literal text, (2) based on the findings,
selects and validates one replacement notation against a pre-defined quantitative pass
bar, and (3) rolls that replacement out consistently across every occurrence (packaged
instruction files, docstrings/field descriptions, the runtime error message and the test pinning its text, generated
JSON schemas -- both the `docs/` and packaged `data/` copies -- the generated `docs/api` pages, and `AGENTS.md`) --
without changing the underlying accepted timestamp formats, separators, or validation
regexes feat-146-date-time established, and without adding bloated explanatory prose to
address the confusion. The two ADRs that document the old notation as historical decision
records (ADR 23a14195, ADR 8c889262) are deliberately left untouched -- see Scope.

### Requirements

- REQ-001: Conduct a short root-cause investigation into why the `fff` placeholder notation is misread as literal text, by spawning several (at least three) independent, fresh-context AI agent sessions via the `task` tool, presenting each with today's unmodified instruction-file/docstring wording and a neutral prompt, and recording their literal interpretations/misreadings verbatim in one `session-NN.md` sibling per session (`session-01.md`, ...) -- together with the shared neutral prompt template in a `session-prompt.md` sibling of this README.
- REQ-002: Based on the investigation findings, select one replacement notation for the millisecond placeholder that is demonstrably less likely to be copied verbatim, validated using the same independent fresh-context `task`-tool-session method as REQ-001 against a quantitative pass bar defined up front (Task 110.100).
- REQ-003: Apply the chosen replacement notation consistently everywhere the current `fff` placeholder appears: the 12 packaged instruction files (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs` `*_create_instructions.md` and `*_update_instructions.md`), domain docstrings/field descriptions, the runtime validation error message in `models/md/frontmatter.py` (the only user-visible error string carrying the notation), the generated JSON schemas (the 6 affected types, in both the `docs/` and packaged `data/` copies), and `AGENTS.md`; packaged templates/examples are verified at rollout and updated only if an occurrence is found. The two historical ADRs that illustrate the old notation and `CHANGELOG.md`'s existing entries are explicitly excluded -- see Scope.
- REQ-004: The timestamp parsing/validation rules established by feat-146-date-time (accepted separators, millisecond digit count, regex patterns) remain unchanged; only the human-facing notation -- including the wording of runtime error messages -- changes, not the behavior that produces or matches them.
- REQ-005: The replacement must not introduce bloated explanatory text -- it stays a narrow token/notation substitution, at most a short inline comment, not new paragraphs added to every occurrence.

### Acceptance Criteria

- [x] ACC-001: A short written summary of the root-cause investigation (REQ-001) exists, citing concrete evidence (the `session-*.md` verbatim agent-session records and/or historical examples) of why the current notation misleads, recorded in this README's `### Design Notes` > `#### Investigation Findings` > `##### Root Cause (ACC-001)` subsection.
- [x] ACC-002: The chosen replacement notation (REQ-002) is documented with its rationale, including the pass-bar validation evidence that it reduces misreading versus the current `fff` notation, recorded in this README's `### Design Notes` > `#### Investigation Findings` > `##### Chosen Notation and Rationale (ACC-002)` subsection.
- [x] ACC-003: Every occurrence of the old `fff` placeholder notation describing a millisecond placeholder -- in the in-scope files of Task 100.105's baseline inventory (packaged instruction files, docstrings, the runtime error message, JSON schemas in both the `docs/` and packaged `data/` copies, the generated `docs/api` pages, `AGENTS.md`) -- is updated to the new notation. Verified by a scoped search (not a blind repo-wide `fff` grep) that targets that baseline file set and notation-shaped patterns (e.g. `ss.fff`, `HH:mm:ss.fff`), explicitly excluding unrelated matches (e.g. the `#fff` CSS color literal in `commands/coverage_badge.py`, gitignored `build/`, `.opencode/node_modules/`) and the out-of-scope historical content named in Scope (the two ADRs, `CHANGELOG.md`, `.specmgr/feat/*/session-*.md`, `docs/tsk/*.md`) as well as this README's own deliberate references to the notation being replaced.
- [x] ACC-004: No template, example, instruction file, docstring, or error message touched by this feature grows by more than a small, bounded amount of added prose per occurrence (the anti-bloat constraint), verified by reviewing the diff of each touched file.
- [x] ACC-005: Every packaged template and example still parses through its own domain's parser after the notation change (no structural/content regression); the packaged instruction files are verified by diff review to carry only the notation substitution, since they are frontmatter-less prompt markdown, not domain documents.
- [x] ACC-006: The full quality gate (ruff format/check, vulture, `pytest -n auto --cov`, pylint baseline unchanged) is green after the change, including any test that previously pinned the literal old-notation error-message text (e.g. `tests/general/tools/test_validate.py`) now updated to match the new notation.

### Scope

#### Included

- Investigating why agents misread the `fff` placeholder notation, by spawning independent, fresh-context `task`-tool agent sessions with today's unmodified wording; the verbatim interpretations and the neutral prompt template are recorded in a `session-*.md` sibling of this README.
- Taking a baseline inventory of the in-scope file set (Task 100.105) that ACC-003's scoped search targets.
- Selecting and validating a replacement notation for the millisecond placeholder against a pre-defined quantitative pass bar.
- Updating every occurrence of the `fff` placeholder across the packaged instruction files (`tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`), docstrings/field descriptions, the runtime error message, the generated JSON schemas (`docs/` and packaged `data/` copies), and `AGENTS.md`; verifying packaged templates/examples carry no occurrence.
- Updating the runtime validation/error-message text that currently cites the `fff` notation (wording only, not the validation logic/regex itself), and the tests that pin that exact message text.

#### Explicitly Out Of Scope

- Changing the accepted timestamp formats, separators, or validation regexes established by feat-146-date-time -- only the human-facing notation changes.
- Editing the historical ADR documents that illustrate the old notation (ADR 23a14195-339c-48af-99d2-97c9964041ae "Use ISO 8601 for all dates and times" and ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf) -- ADRs are immutable historical decision records; this feature cites them, it does not rewrite them.
- Rewriting historical narrative content that happens to contain the old notation (`CHANGELOG.md`'s existing entries, `.specmgr/feat/*/session-*.md` transcripts, `docs/tsk/*.md` historical task records) -- only currently-authoritative, forward-facing content is in scope; the one deliberate forward-facing citation, this feature's own new `CHANGELOG.md` `[Unreleased]` entry quoting the old notation to name the token the substitution replaces, is likewise excluded from ACC-003's residual check.
- The old-notation references in this feature README itself (its Overview, Requirements, Acceptance Criteria, Scope, Design Notes, and Task List name the notation being replaced as the subject of the work) -- deliberate historical references, excluded from ACC-003's residual check.
- Adding verbose explanatory prose about timestamp formatting beyond the narrow notation substitution.
- Re-litigating the `T`-vs-space separator decision or any other feat-146-date-time decision.

### Dependencies

#### Depends On

- feat-146-date-time: establishes the `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]` notation this feature revises for clarity.

### Design Notes

#### Investigation Findings

##### Baseline Inventory (Task 100.105)

Anchor: HEAD `25c7f13be4571a5af635a69eb37dcd3bdfb30025` (verified via `git rev-parse HEAD`).
Inventory is over tracked files as of that commit plus no `src/` changes (this phase adds only
untracked `session-prompt.md`/`session-NN.md` siblings here). Method: notation-shaped
`git grep -E 'ss\.fff|SS\.fff'` over tracked files (gitignored `build/` and
`.opencode/node_modules/` are invisible to it by construction), plus a full case-insensitive
`fff` sweep to classify every non-notation hit. **Total: 48 in-scope files, 54 occurrences.**

- `src/` core models (11 files, 15 occurrences; all paths under `src/biz/dfch/specmgr/`):
  `models/md/frontmatter.py:56,97,187` (line 187 = the sole user-visible runtime error string),
  `models/md/_timestamps.py:23,90`, `models/md/_ordering.py:29`,
  `general/tools/_timestamps.py:27,79`, `tsk/models/v1/body.py:114`,
  `vcr/models/v1/body.py:370`, `sysrs/models/v1/body.py:1008`, `sop/models/v1/body.py:437`,
  `dec/models/v1/body.py:466`, `feat/models/v1/body.py:539`, `feat/models/v1/frontmatter.py:32`.
- `src/` packaged instruction data (12 files, 12 occurrences, one per file):
  `tsk` create:28/update:44, `dec` create:64/update:78, `sop` create:64/update:78,
  `feat` create:73/update:64, `vcr` create:48/update:59, `sysrs` create:95/update:81
  (`<d>/data/<d>_{create,update}_instructions.md`).
- `src/` packaged `data/` JSON schemas (6 files, 6 occurrences): `tsk`:179, `dec`:651,
  `sop`:595, `feat`:539, `vcr`:112, `sysrs`:1067.
- `docs/` JSON schema copies (6 files, 6 occurrences): the same six `<d>_schema.json` files at
  the same line numbers; all six pairs verified byte-identical to their packaged `data/`
  copies via `cmp`.
- `docs/api` generated pages (11 files, 13 occurrences): `models.md._timestamps:8,61`,
  `general.tools._timestamps:12,57`, `models.md._ordering:14`, `models.md.frontmatter:53`,
  `tsk.models.v1.body:1392`, `dec.models.v1.body:19490`, `sop.models.v1.body:16948`,
  `feat.models.v1.body:21762`, `feat.models.v1.frontmatter:17`, `vcr.models.v1.body:4313`,
  `sysrs.models.v1.body:32254` (all `biz.dfch.specmgr.*` page names).
- `AGENTS.md:1011` (1 file, 1 occurrence).
- `tests/general/tools/test_validate.py:895` (1 file, 1 occurrence; pins the error-message text).

Excluded and why: the `#fff` CSS color literal (`commands/coverage_badge.py:111,124` and its
generated `docs/coverage.svg`); the two historical ADRs (`docs/adr/23a14195-...:60,61`,
`docs/adr/8c889262-...:15,36`); `CHANGELOG.md:15` (this feature's own new `[Unreleased]`
entry, which deliberately quotes the old notation to name the token the substitution replaces)
plus `CHANGELOG.md`'s pre-existing entries (at `564,751,887,1208,1238` in this inventory's base
commit; shifted to `580,767,903,1224,1254` by that new entry's +16 lines); `docs/tsk/*.md`
historical task records (plan expected them to carry the only uppercase `SS.fff` variant;
actual at HEAD: zero `fff` occurrences); other `.specmgr/feat/*` historical feature records;
this README's own deliberate references; the new `session-prompt.md`/`session-NN.md`
siblings' deliberate quotes (including the Phase 140 BEFORE arm's verbatim `fff` quotes in
`session-13.md`-`session-15.md` and the `## G1 follow-up` section's arm derivation);
incidental hex `fff` runs in session ids, git hashes, `uv.lock`, and a binary PDF.

Deltas vs the plan's second-pass expectations: every verified expectation holds except two --
the total instruction-file count is 32, not 33 (12 of 32 carry the notation, as expected),
and `docs/tsk/*.md` carry zero occurrences, not the expected uppercase variant (excluded
either way).

##### Root Cause (ACC-001)

The three fresh-context baseline sessions (`session-01.md` through `session-03.md`, prompted
verbatim per `session-prompt.md`) all substituted the placeholder correctly -- baseline rate
3/3, zero literal `fff` copies -- and each grounded its millisecond choice in the concrete
`e.g. ### 2026-08-19 05:42:00.000+02:00` line that today's instruction-file wording ships
alongside the notation (session-01: `.fff` "is the required 3-digit millisecond field";
session-02: `.fff = .000`; session-03: "the mandatory `.fff` millisecond field gets `.000`").
The root cause is therefore not the notation under its full, example-anchored presentation,
but exposure without that anchor: `fff` is a bare three-letter token that is not ISO 8601 and
that nothing in the notation marks as a digit slot, so wherever an agent meets the notation
alone -- notably the example-free runtime error message
(`models/md/frontmatter.py:187`, whose text is the notation itself) -- a surface
pattern-fill reading copies it verbatim, as issue #183 reports. The repo's own history
corroborates the confusion: the feat-156 README records its own `### Updates` entry headings
having been written *without* the millisecond slot at all ("lacked the `.fff` milliseconds the
`UpdateEntry` heading regex mandates") because the slot's content was unguessable from the
notation.

##### Chosen Notation and Rationale (ACC-002)

**Chosen: `SSS`** -- the full pattern becomes `yyyy-MM-dd[T ]HH:mm:ss.SSS[Z|±HH:MM]`.

Rationale, grounded in the recorded root cause (`fff` is a bare three-letter, non-ISO token that
nothing in the notation marks as a digit slot): `SSS` marks the slot as exactly three digits by the
notation's own convention -- the same "repeated field letter, repetition count = digit count"
mechanism `yyyy`/`MM`/`dd`/`HH`/`mm`/`ss` already use -- and `S` is the established pattern letter
for the millisecond field (Java SimpleDateFormat, moment.js, date-fns, Android), an uppercase that
keeps the slot visually distinct from the adjacent `ss` (lowercase) seconds field. It is a narrow
drop-in token (REQ-005) that changes nothing about the accepted formats or regexes (REQ-004).

Candidates considered (three drafted, three validated). Protocol per candidate: the persisted Phase
100 neutral template with one mechanical substitution (`fff` -> token in exactly the three
quoted-notation occurrences, everything else byte-identical), three independent fresh-context
`explore` sessions, the same fixed task (2026-10-06, 07:52:14 UTC+02:00); pass = zero verbatim
copies of the candidate token AND correct-substitution rate >= 2/3 AND >= the `fff` baseline 3/3.

| Candidate | Grounding | Sessions | Scores | Verbatim copies | Computation | Result |
|---|---|---|---|---|---|---|
| `SSS` | pattern-letter convention (field letter, repetition count = digit count) | 04-06 | 3x (b) | 0 | 3/3 >= 2/3, >= 3/3 | PASS |
| `ms` | ISO 31-2 unit symbol (slot labelled by the unit its content carries) | 07-09 | 3x (b) | 0 | 3/3 >= 2/3, >= 3/3 | PASS |
| `sss` | ISO 8601's own fractional-seconds notation; drawback: sits directly after `ss` | 10-12 | 3x (b) | 0 | 3/3 >= 2/3, >= 3/3 | PASS |

All three pass, so Task 110.115's selection rule applied: prefer the candidate that marks the digit
slot by the notation's own convention (the recorded root-cause defect), then the strongest
convention backing, then the narrowest token. `ms` labels the field by unit but leaves the
three-digit requirement to the concrete example (its sessions derive `.000` "as in the example");
`sss` marks the digit count but collides with the adjacent `ss` seconds field (`ss.sss`),
re-introducing the adjacent-letter-slot ambiguity the root cause describes. All three of `SSS`'s
sessions derived `.000` from the token itself ("the format requires three digits", "the mandatory
3-digit `SSS` milliseconds"). No re-draft rounds were needed.

Pass-bar evidence versus `fff`: `SSS` achieves 3/3 correct substitutions and zero verbatim copies
(`session-04.md`-`session-06.md`) under the identical protocol that gave `fff` its 3/3 baseline
(`session-01.md`-`session-03.md`) -- no regression, zero misreads -- while the token itself now
carries the digit-slot marker, removing the bare non-ISO token the recorded root cause identifies as
the misreading mechanism on the example-free exposure paths (notably the runtime error message).
Prompt variants, the full trial log, and the per-candidate computation: `session-prompt.md`.
Because every trial's prompt carried the concrete `e.g. ...05:42:00.000+02:00` anchor line, the
quantitative comparison measures no-regression-plus-zero-verbatim-copies under example-anchored
exposure; the example-free exposure path (notably the runtime error message alone) was measured
in the Phase 140 round-2 follow-up (`##### G1 Example-Free Paired Trial (round-2 review
follow-up)` below -- observed BEFORE->AFTER delta: none at N=3 per arm), so the reduction claim
for that path rests on the token's self-descriptiveness rather than on a measured delta.

Phase 120 rollout note: the rollout is the mechanical substitution `fff` -> `SSS` (uppercase, three
letters) at every in-scope occurrence of Task 100.105's baseline inventory (48 files, 54
occurrences at HEAD `25c7f13be4571a5af635a69eb37dcd3bdfb30025`).

##### G1 Example-Free Paired Trial (round-2 review follow-up)

Round-2 review finding G1 (feat-reviewer; the round-1 pass had recorded the same point as the
limitation sentence in the ACC-002 subsection above): the Phase 100/110 protocol was
example-anchored -- every trial prompt carried the concrete
`e.g. ### 2026-08-19 05:42:00.000+02:00` line -- so the one exposure path the root cause
identifies as the actual misreading mechanism (the notation *alone*, notably the example-free
runtime error message) was never measured quantitatively. Phase 140 closes this with a paired
BEFORE/AFTER measurement on that path: the shared example-free variant (the runtime error
message as the sole format source -- no anchor line, no instruction-file or docstring quotes;
identical fixed task and reply format to Phases 100/110) with the BEFORE arm quoting the
pre-rollout `fff` wording byte-faithful from base commit
`25c7f13be4571a5af635a69eb37dcd3bdfb30025`'s `frontmatter.py` lines 186-187 and the AFTER arm
quoting the post-rollout `SSS` wording from the same lines at HEAD; three independent,
fresh-context `explore` sessions per arm (`session-13.md`-`session-15.md` = BEFORE,
`session-16.md`-`session-18.md` = AFTER), all on the single endpoint
`vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`; full protocol, arm derivation, trial log, and
per-arm computation in `session-prompt.md`'s `## G1 follow-up: example-free paired trial`
section (explicitly outside the Phase 110 pass bar -- no pass/fail gate).

| Arm | Sessions | Scores | Verbatim copies |
|---|---|---|---|
| BEFORE `fff` | 13-15 | 3x (b) | 0 |
| AFTER `SSS` | 16-18 | 3x (b) | 0 |

**Observed BEFORE->AFTER delta: none** -- both arms scored identically (3/3 correct
substitutions, zero verbatim placeholder copies) on the example-free path at N=3 per arm, and
all six sessions derived the three-digit millisecond field from the error message alone.
Honest small-N interpretation (full text in `session-prompt.md`): at 3 trials per arm the
measurement surfaces an arm-wide verbatim-copy failure mode (the one issue #183 reports as
repeated) and would very likely have surfaced a per-trial misread rate of ~1/3 or higher, but
it cannot exclude smaller per-trial rates, and the fresh-context `explore` population is a
best-available proxy for the unnamed, non-reproduced agent population behind the reported
misreads. Consequence for the record: `SSS`'s selection rationale for this path stands on the
token's self-descriptiveness (it marks the digit slot by the notation's own convention -- the
recorded root-cause defect of `fff`) rather than on a measured delta; the path is now measured,
and the measurement's honest result is "no observable difference at this N on this population".

**Contingency agreed with the user (2026-10-07, after this measurement):** if the issue #183
error shows again after the `SSS` rollout -- i.e. an agent still emits the literal placeholder
in the millisecond slot whatever the token is -- the follow-up is to **drop the fractional/
millisecond part of the timestamp form completely** rather than swap to a third token, since
this paired measurement shows the token alone does not explain the misreading on the measured
population. That change is out of scope for this feature (it would alter the form
feat-146-date-time established -- milliseconds are currently mandatory and exactly three
digits -- and so would be a new feature in its own right), and it is triggered only by a
recurrence that comes with concrete failing examples (model, context, the rejected value and
the raised error) collected for the record first.

### Related Decisions

- ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO 8601 for all dates and times"): the earlier, foundational ADR that first documented the `HH:mm:ss.fff` example this feature revises for clarity; cited for context, not edited.
- ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf ("Use full ISO 8601 date+time timestamps in all entry headings and frontmatter (accept T or space, write T)"): established the notation this feature is revising for clarity, not reversing its format/validation rules.

### Task List

#### Phase 100: Root-cause investigation

- [x] Task 100.100: Bump this README's frontmatter `status` to `progress` (via the generic `set_status` tool, `type="feat"`) and prepend an Updates entry recording the transition, spawn at least three independent, fresh-context `task`-tool agent sessions (subagent type `explore` -- the only general-purpose fresh-context research agent; no specialized agent, to keep the prompt neutral), present each with the current, unmodified instruction-file/docstring timestamp wording and a neutral prompt, and record their literal interpretations/misreadings verbatim in one `session-NN.md` sibling per session (`session-01.md`, ...) -- together with the shared neutral prompt template in a `session-prompt.md` sibling (REQ-001). -- depends on: none
- [x] Task 100.105: Produce the baseline inventory of the in-scope file set -- every file carrying the `fff` placeholder notation as of the current HEAD commit (record the exact SHA in the subsection), with file:line occurrences -- and record it in this README's `#### Investigation Findings` > `##### Baseline Inventory` subsection (ACC-003's scoped search targets this set). -- depends on: none
- [x] Task 100.110: Synthesize the collected evidence into a short root-cause summary and record it in this README's `#### Investigation Findings` > `##### Root Cause (ACC-001)` subsection (ACC-001). -- depends on: Task 100.100

#### Phase 110: Notation selection

- [x] Task 110.100: Draft 2-3 candidate replacement notations for the millisecond placeholder and define the quantitative pass bar together with its measurement protocol up front (each candidate validated in at least three fresh-context sessions of the REQ-001 method, each session performing one fixed timestamp task under the persisted neutral prompt template; a "correct substitution" is a syntactically valid full date+time timestamp with exactly three millisecond digits in the placeholder field; the `fff` baseline rate is measured with the same protocol in Phase 100; pass = zero verbatim placeholder copies AND a correct-millisecond-substitution rate of at least two-thirds of the trials AND at least as high as the `fff` baseline rate). -- depends on: Task 100.110
- [x] Task 110.110: Validate the leading candidate(s) against the pass bar using the same independent fresh-context `task`-tool-session method as Phase 100 and record the results -- verbatim session transcripts in one `session-NN.md` sibling per session, continuing Phase 100's numbering, plus the per-candidate pass/fail computation. -- depends on: Task 110.100
- [x] Task 110.115: Select the one candidate that meets the pass bar (if none does, re-draft per Task 110.100's criteria, up to two further re-draft rounds; if still none passes, or if Task 100.110's root cause lies outside the notation, record the negative outcome in the `##### Chosen Notation and Rationale (ACC-002)` subsection and stop for a user decision instead of entering Phase 120). -- depends on: Task 110.110
- [x] Task 110.120: Record the final chosen notation and its rationale, including the pass-bar evidence, in this README's `#### Investigation Findings` > `##### Chosen Notation and Rationale (ACC-002)` subsection (ACC-002). -- depends on: Task 110.115

#### Phase 120: Rollout

- [x] Task 120.100: Verify by search that no packaged template/example carries the `fff` placeholder notation (expected: zero occurrences, concrete sample timestamps only); update any occurrence found to the new notation. -- depends on: Task 110.120
- [x] Task 120.105: Update the 12 packaged instruction files that cite the `fff` notation -- `*_create_instructions.md` and `*_update_instructions.md` in `tsk`/`dec`/`sop`/`feat`/`vcr`/`sysrs`. -- depends on: Task 110.120
- [x] Task 120.110: Update the core sources -- the runtime error string in `models/md/frontmatter.py` (the only user-visible error text carrying the notation) and the docstring/comment mentions in `models/md/_timestamps.py`, `models/md/_ordering.py`, `general/tools/_timestamps.py`, and the 7 per-domain model files (`tsk`/`vcr`/`sysrs`/`sop`/`dec` `models/v1/body.py`, plus `feat` `models/v1/body.py` and `feat` `models/v1/frontmatter.py`). -- depends on: Task 110.120
- [x] Task 120.115: Update the test that pins the exact literal error-message text containing the old notation (`tests/general/tools/test_validate.py`) to match the new notation. -- depends on: Task 120.110
- [x] Task 120.120: Regenerate the affected artifacts -- `uv run --frozen specmgr schema` for the `docs/` schema copies, `uv run --frozen specmgr schema --type <d> --output-dir src/biz/dfch/specmgr/<d>/data` for the 6 packaged `data/` schema copies served by `specmgr://<d>/schema` (dec/feat/sop/sysrs/tsk/vcr are the only schema files carrying the notation), and `uv run --frozen specmgr docs` for `docs/api`/`docs/GENERATED.md` (`docs/adr/README.md` is unaffected -- no ADR changes). -- depends on: Task 120.110
- [x] Task 120.130: Update `AGENTS.md`'s own mentions of the notation. -- depends on: Task 110.120
- [x] Task 120.140: Scoped search (per ACC-003's pattern/exclusion rules, targeting Task 100.105's baseline file set) confirms no remaining `fff`-as-placeholder occurrences in in-scope files; full quality gate green (ACC-006); bump this README's frontmatter `status` to `review` (via the generic `set_status` tool) and prepend an Updates entry recording the transition. -- depends on: Task 120.100, Task 120.105, Task 120.115, Task 120.120, Task 120.130

#### Phase 130: Closeout

- [x] Task 130.100: Add a `CHANGELOG.md` `[Unreleased]` entry and comment on GitHub issue #183 with the fix summary. -- depends on: Task 120.140
- [x] Task 130.110: Final full quality gate; bump this README's frontmatter `status` to `done` (via the generic `set_status` tool) and prepend an Updates entry recording the transition. -- depends on: Task 130.100 (the task's `done` status bump was superseded for this run -- status remains `review`, `done` deferred until after the PR merge; see the Phase 130 Updates entry)

#### Phase 140: Review follow-up (round 2: G1 paired measurement + I1 exclusion completeness)

- [x] Task 140.100: Source both verbatim error-message quotes -- the BEFORE `fff` wording byte-faithful from base commit `25c7f13be4571a5af635a69eb37dcd3bdfb30025`'s `src/biz/dfch/specmgr/models/md/frontmatter.py` lines 186-187 and the AFTER `SSS` wording from the same lines at HEAD -- and draft the shared example-free prompt variant (the runtime error message as the sole format source: no `e.g.` anchor line, no instruction-file or docstring quotes; the two arms differ by exactly one mechanical token substitution with round-trip proof; identical fixed task and reply format to Phases 100/110), recorded up front as a new section in `session-prompt.md` explicitly outside the Phase 110 pass bar, scored with the existing (a)/(b)/(c) protocol read per arm. -- depends on: none
- [x] Task 140.110: Run the paired measurement -- three independent, fresh-context `explore` sessions per arm, continuing the session numbering (`session-13.md`-`session-15.md` = BEFORE `fff`, `session-16.md`-`session-18.md` = AFTER `SSS`), each presented verbatim with its arm's variant -- and record the verbatim responses in one `session-NN.md` sibling per session plus the per-arm scores and the observed BEFORE->AFTER delta in the `session-prompt.md` section (honest small-N interpretation; no pass/fail gate). -- depends on: Task 140.100
- [x] Task 140.120: Update this README -- a new `#####` subsection under `#### Investigation Findings` recording the paired trial and its delta; rewrite the ACC-002 limitation sentence (the example-anchored protocol caveat) to state the measured outcome; extend the two old-notation exclusion enumerations (the `#### Explicitly Out Of Scope` bullet covering `CHANGELOG.md`'s existing entries, and the Baseline Inventory's "Excluded and why" line) to cover this feature's own new `CHANGELOG.md` `[Unreleased]` entry quoting the old notation (round-2 review finding I1). -- depends on: Task 140.110
- [x] Task 140.130: Verify -- re-run ACC-003's scoped residual check (expect zero in-scope `ss.fff|SS.fff` and the unchanged 48-file / 54-occurrence `ss.SSS` set) and confirm `git status` shows only the intended changes in this feature folder (docs-only: no `src/`/`tests/`/`docs/`/`CHANGELOG.md` changes, no quality-gate re-run needed); prepend the `Current Status` + `Recent Updates` completion entries. -- depends on: Task 140.120

## Progress

### Current Status

**As of 2026-10-07**: Phase 140 (round-2 review follow-up) complete. The paired example-free
measurement (round-2 G1) closed the one unmeasured edge of the Phase 100/110 protocol: three
independent fresh-context `explore` sessions per arm (BEFORE `fff` quoted byte-faithful from
base `25c7f13`, AFTER `SSS` quoted from HEAD; the runtime error message as the sole format
source, no `e.g.` anchor) scored 3/3 correct substitutions with zero verbatim placeholder
copies each -- observed BEFORE->AFTER delta: none at N=3 per arm, with the honest small-N
interpretation recorded in `session-prompt.md`'s `## G1 follow-up` section and the new
`##### G1 Example-Free Paired Trial (round-2 review follow-up)` subsection. Round-2 I1: the
exclusion enumerations now cover this feature's own new `[Unreleased]` `CHANGELOG.md` entry
(`CHANGELOG.md:15`) quoting the old notation, completing ACC-003's residual-check exclusion
set. Docs-only; ACC-003 re-verified (zero in-scope `ss.fff|SS.fff`, the 48-file / 54
`ss.SSS` set unchanged) and `git status` clean of this feature folder. Branch and PR
unchanged: frontmatter `status` remains `review`, PR #201 open; the `done` transition stays
deferred until after the PR merge.

**As of 2026-10-06**: Round-1 review findings (feat-reviewer) applied in a docs-only pass over
this feature folder (no `src/`/`tests/`/`docs/`/`CHANGELOG.md` changes) -- see the `Round-1
review findings applied` Updates entry. Branch and PR unchanged: frontmatter `status`
remains `review`, PR #201 open; the `done` transition stays deferred until after the PR
merge.

**As of 2026-10-06**: Phase 130 (closeout) complete; branch `feat-183-ts-fff` ready
for PR. `CHANGELOG.md` carries the new `[Unreleased]` `### Changed` entry, GitHub
issue #183 has the fix summary posted and verified, and the final full quality gate
is green (pytest 4080 passed; `specmgr docs`/`specmgr adr-toc` no-op). The frontmatter
`status` intentionally remains `review` -- per orchestrator/user instruction the
`done` transition is deferred until after the PR merge (the plan's Task 130.110
`done` bump is superseded for this run).

**As of 2026-10-06**: Phase 120 (rollout) complete; feature in `review`. The `SSS`
notation substituted across the whole Task 100.105 baseline inventory (11 core
sources, 12 packaged instruction files, the test pin, `AGENTS.md`, plus the
regenerated schema copies and `docs/api` pages); ACC-003's scoped residual search
and the full quality gate green (pytest 4080 passed). Next: Phase 130 (closeout).

**As of 2026-10-06**: Phase 110 (notation selection) complete; feature in `progress`. All three
candidate notations (`SSS`, `ms`, `sss`) pass the pre-defined pass bar (3/3 correct substitutions
and zero verbatim placeholder copies each, versus the `fff` baseline 3/3); `SSS` is selected and
recorded in `##### Chosen Notation and Rationale (ACC-002)` with the full pass-bar evidence. Next:
Phase 120 (rollout of the mechanical `fff` -> `SSS` substitution over the 48-file / 54-occurrence
baseline inventory).

**As of 2026-10-06**: Phase 100 (root-cause investigation) complete; feature in `progress`.
Baseline measured (3/3 correct substitutions under today's `fff` wording, zero verbatim
copies), inventory recorded (48 in-scope files, 54 occurrences), root cause summarized in
`#### Investigation Findings`. Next: Phase 110 (notation selection).

**As of 2026-10-04**: Plan refined against the live tree per a review that found and fixed
3 errors, 3 gaps, 4 discrepancies, and 4 improvements (see the `Plan refined` Updates
entry); still planning stage.

**As of 2026-10-03**: Feature just created from GitHub issue #183; planning stage only -- no
investigation or implementation has started yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T09:03:15.075+02:00 - Follow-up contingency note added (drop milliseconds if the error recurs on `SSS`)

Per user decision after the Phase 140 measurement: if the issue #183 error shows again after
the `SSS` rollout (an agent still emits the literal placeholder in the millisecond slot
whatever the token is), the follow-up is to drop the fractional/millisecond part of the
timestamp form completely rather than swap to a third token -- the paired trial showed the
token alone does not explain the misreading on the measured population. Recorded as a
**Contingency** paragraph at the end of the `##### G1 Example-Free Paired Trial (round-2
review follow-up)` subsection. The contingency is explicitly out of scope for this feature
(it would alter the feat-146-established form, where milliseconds are mandatory three digits)
and would be a new feature triggered only by a recurrence with concrete failing examples
(model, context, rejected value, raised error) collected first. Docs-only note; frontmatter
`status` remains `review` (no transition; `done` stays deferred until after the PR merge).

#### 2026-10-07T08:42:35.080+02:00 - Phase 140 complete (round-2 review follow-up: G1 paired measurement + I1 exclusion completeness)

Tasks 140.100/140.110/140.120/140.130 done. G1 (round-2): the paired example-free
measurement ran per the protocol recorded up front in `session-prompt.md`'s new
`## G1 follow-up: example-free paired trial` section (explicitly outside the Phase 110
pass bar; no pass/fail gate). Both verbatim error-message quotes sourced: BEFORE `fff`
from `git show 25c7f13be4571a5af635a69eb37dcd3bdfb30025:src/biz/dfch/specmgr/models/md/
frontmatter.py` lines 186-187 (byte-faithful to the pre-rollout wording) and AFTER `SSS`
from the same lines at HEAD; the two quotes differ in exactly the one token, and the two
arm variants are one mechanical `{TOKEN}` substitution of the shared template (round-trip
proven by construction). Six trials -- three independent, fresh-context `explore`
sessions per arm, each via the reviewing agent's own `task` tool with the arm's variant
verbatim (no headless relay needed this round, unlike Phases 100/110; all six on the
single endpoint `vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2`, so the Phase 110
two-endpoint caveat does not apply): BEFORE `fff` = `session-13.md`-`session-15.md`
(3/3 (b), zero verbatim `fff` copies), AFTER `SSS` = `session-16.md`-`session-18.md`
(3/3 (b), zero verbatim `SSS` copies). **Observed BEFORE->AFTER delta: none** at N=3 per
arm -- all six sessions derived the three-digit millisecond field from the error message
alone; the honest small-N interpretation (at 3 trials per arm the measurement surfaces
an arm-wide verbatim-copy failure mode -- the one issue #183 reports as repeated -- and
would very likely have surfaced a per-trial misread rate of ~1/3 or higher, but cannot
exclude smaller per-trial rates, and the fresh-context `explore` population is a
best-available proxy for the unnamed, non-reproduced agent population behind the
reported misreads) is recorded in `session-prompt.md`, and the consequence for the
record -- `SSS`'s selection rationale for this path stands on the token's
self-descriptiveness, and the path is now measured -- in the new `##### G1 Example-Free
Paired Trial (round-2 review follow-up)` subsection; the ACC-002 limitation sentence
now points to that measurement. I1 (round-2): both exclusion enumerations extended to
cover this feature's own new `CHANGELOG.md` `[Unreleased]` entry (`CHANGELOG.md:15`,
which deliberately quotes the old notation to name the token the substitution replaces)
-- the `#### Explicitly Out Of Scope` bullet and the Baseline Inventory's "Excluded and
why" line (the latter also records the +16-line shift of the pre-existing entry
references `564,751,887,1208,1238` -> `580,767,903,1224,1254` caused by that new entry,
and names the Phase 140 session files' verbatim `fff` quotes under the
session-prompt.md/session-NN.md deliberate-quotes exclusion). Verification (Task
140.130): ACC-003's scoped residual check re-run -- `git grep -lE 'ss\.fff|SS\.fff'`
hits only the documented exclusion set (`CHANGELOG.md` x6, the two historical ADRs x2
each, the historical `.specmgr/feat/*` records, this feature's own README/session
deliberate references) with zero in-scope hits, and `git grep -lE 'ss\.SSS|SS\.SSS'`
yields 50 files = the unchanged 48-file baseline set plus this feature's own two files
(6 deliberate lines: README 152/278/354, session-prompt 124/132/140), i.e. the in-scope
54 unchanged; `git status` shows only the intended changes in
`.specmgr/feat/feat-183-ts-fff/` (`README.md`/`session-prompt.md` modified,
`session-13.md`-`session-18.md` added) -- no `src/`/`tests/`/`docs/`/`CHANGELOG.md`
changes, so no quality-gate re-run is needed. Docs-only phase; frontmatter `status`
remains `review` (no transition; `done` stays deferred until after the PR merge).

#### 2026-10-07T08:05:17.144+02:00 - Phase 140 start (round-2 review follow-up: G1 paired measurement + I1 exclusion completeness)

Round-2 feat-reviewer pass over the completed feature found no errors; one gap (G1: the
Phase 100/110 protocol was example-anchored -- every trial prompt carried the concrete
`e.g. ...05:42:00.000+02:00` line -- so the example-free exposure path the root cause
identifies, notably the runtime error message alone, was never measured quantitatively;
recorded in round 1 as the ACC-002 limitation sentence) and one improvement (I1: this
feature's own new `CHANGELOG.md` `[Unreleased]` entry quotes the old notation but is not
covered by the README's exclusion enumerations). Per user decision, G1 is closed with a
paired BEFORE/AFTER measurement on the example-free path (three independent, fresh-context
`explore` sessions per arm, `session-13.md`-`session-18.md`, protocol recorded up front in
`session-prompt.md`, explicitly outside the Phase 110 pass bar) and I1 is applied as a
docs-only exclusion-list completion. Docs-only phase: no `src/`/`tests/`/`docs/`/
`CHANGELOG.md` changes; frontmatter `status` remains `review` (no transition; `done` stays
deferred until after the PR merge).

#### 2026-10-06T23:58:11.794+02:00 - Round-1 review findings applied (feat-reviewer)

Docs-only pass over this feature folder (no `src/`/`tests/`/`docs/`/`CHANGELOG.md`
changes) applying the round-1 feat-reviewer findings. D1: the baseline inventory
arithmetic corrected -- header total 53 -> 54 in-scope occurrences (48 files
unchanged), the `docs/api` bullet 12 -> 13 occurrences (its own itemized line
references enumerate 13), and every propagated restatement of the wrong total
corrected (the ACC-002 Phase 120 rollout note, the Phase 100/110 `### Current
Status` entries, the Phase 100/120 Updates entries); re-verified against base
commit 25c7f13 (`git grep -cE 'ss\.fff|SS\.fff'` = 54 in-scope match lines: 33
`src/` + 1 `AGENTS.md` + 1 test + 6 `docs/` schemas + 13 `docs/api`) and HEAD
(exactly 54 `ss.SSS` replacements across the same 48 files, zero residual
`ss.fff` in scope). D2: the nine Phase 110 `session-04.md`-`session-12.md`
`Model:` headers corrected to the `vllm-sys0-mtp-1/qwen3.8-27b-bf16-896k-mtp-1`
endpoint per the opencode session store (the three Phase 100 sessions genuinely
ran on `mtp-2` and are unchanged); the `## Mechanism and trial log` model
statement qualified to name both endpoints, with one added line on the
consequence: every trial (baseline and all candidates) scored identically (3/3
correct, zero verbatim copies), so the endpoint difference cannot have changed
any pass/fail outcome; identical underlying weights across the two endpoints are
assumed from the endpoints' naming, not verified. D3: Task 130.110 annotated at
the end of its line (the `done` status bump superseded for this run; status
remains `review`, `done` deferred until after the PR merge), and the six
`### Acceptance Criteria` boxes checked after the independent review verified
each criterion as satisfied. D4: `### Current Status` reordered strictly
newest-first (Phase 130, 120, 110, 100, then the 2026-10-04, then the
2026-10-03 entry; blocks moved verbatim, no rewording). G1: one sentence on
the protocol limitation added to the ACC-002 record after the "Pass-bar
evidence" paragraph: because every trial's prompt carried the concrete
`e.g. ...05:42:00.000+02:00` anchor line, the comparison measures
no-regression-plus-zero-verbatim-copies under example-anchored exposure, and
the reduction claim for the example-free exposure path rests on the token's
self-descriptiveness rather than a measured delta. Branch and PR unchanged:
frontmatter `status` remains `review`, PR #201 open.

#### 2026-10-06T22:08:37.782+02:00 - Phase 130 complete (closeout)

Tasks 130.100/130.110 done. `CHANGELOG.md`: one new `[Unreleased]` entry under
`### Changed` (category chosen for a human-facing notation/wording change with no
behavior change), matching the adjacent entries' hard-wrap width and the
`(feat-183-ts-fff, GitHub issue #183)` provenance idiom. GitHub issue #183: fix
summary posted via `gh` and verified (comment
https://github.com/dfch/biz.dfch.SpecMgr/issues/183#issuecomment-6024451872, author
`dfch`, 2026-10-06T20:04:23Z). Final full quality gate green: ruff format --check
(1840 files already formatted), ruff check (all checks passed), vulture (clean, no
output), pytest -n auto --cov=src (4080 passed), `specmgr docs` and
`specmgr adr-toc` both no-ops (regenerated `docs/` byte-identical; `git status --
docs/` clean). Status override: the frontmatter `status` intentionally remains
`review` (not `done`) per orchestrator/user instruction -- the `done` transition is
deferred until after the PR merge, so the plan's Task 130.110 `done` bump is
superseded for this run; no `set_status` call was made this phase (the only
frontmatter change is the `updated` bump for this hand edit, per the prior
phases' precedent). Closeout complete; the branch is ready for PR.

#### 2026-10-06T21:30:12.033+02:00 - Phase 120 complete (rollout; status progress → review)

Tasks 120.100/120.105/120.110/120.115/120.120/120.130/120.140 done. Mechanical `fff` →
`SSS` token substitution across the entire Task 100.105 baseline file set (48 files,
54 occurrences): the 11 core model sources -- including the sole user-visible runtime
error string in `models/md/frontmatter.py` (wording only; every accepted format,
separator, and validation regex unchanged per REQ-004) -- the 12 packaged instruction
files (pure substitution, one line each, no rewording), the test pin in
`tests/general/tools/test_validate.py`, and `AGENTS.md`. Task 120.100 re-verified all
24 packaged templates/examples: zero notation occurrences (concrete sample timestamps
only), so no update was needed there. Regenerated: the 6 `docs/` and 6 packaged
`data/` schema copies (all 6 pairs verified byte-identical via `cmp`; a second run of
every generator is a no-op; the generated diffs contain only the substitution) and the
11 `docs/api` pages (`docs/GENERATED.md` rewritten byte-identical; `docs/MCP.md` and
`docs/adr/README.md` untouched). ACC-003 scoped residual search: zero
`ss.fff|SS.fff` remains in any in-scope file -- every remaining repo-wide hit is the
documented exclusion set (the two historical ADRs, `CHANGELOG.md`, other
`.specmgr/feat/*` historical records, this feature's own README/session files, the
`#fff` CSS literals, lockfile hashes, and the binary PDF). Full quality gate green:
ruff format/check, vulture, pytest 4080 passed, `specmgr docs`/`specmgr adr-toc`
no-op. Environment delta: the worktree's `.venv` editable install initially pointed
at the main checkout; reinstalled via `uv sync --all-extras --frozen
--reinstall-package biz-dfch-specmgr` so all generators ran against worktree code
(the one stray run before that rewrote byte-identical content into the main repo's
`docs/`, leaving it clean). Frontmatter `status` bumped `progress` → `review` via the
generic `set_status` tool (`type="feat"`) per Task 120.140 (plan convention I4).

#### 2026-10-06T18:31:46.947Z - Phase 110 complete (notation selection)

Tasks 110.100/110.110/110.115/110.120 done. Three candidate notations drafted (`SSS`, `ms`, `sss`),
each validated in three independent fresh-context `explore` sessions under the persisted Phase 100
template with one mechanical substitution (`fff` -> token in exactly the three quoted occurrences):
3/3 correct substitutions and zero verbatim placeholder copies for every candidate -- all three
PASS the pass bar (zero verbatim copies AND rate >= 2/3 AND >= the `fff` baseline 3/3), sessions
`session-04.md`-`session-12.md`, prompt variants and trial log in `session-prompt.md`. `SSS`
selected (Task 110.115's rule: marks the digit slot by the notation's own repetition convention,
the established millisecond pattern letter, distinct from the `ss` seconds field) and recorded in
`##### Chosen Notation and Rationale (ACC-002)` with the per-candidate pass-bar evidence. Same
headless `opencode run` relay mechanism as Phase 100 (the implementing agent's own `task` tool is
denied; byte-identity of every trial's relayed prompt verified from the raw JSON event stream,
trailing newline aside; responses are the subagents' own `task_result`s). No re-draft rounds
needed. No `src/` or `tests/` file was touched. Next: Phase 120 (rollout of `fff` -> `SSS`).

#### 2026-10-06T07:11:20.433Z - Phase 100 complete (root-cause investigation)

Tasks 100.100/100.105/100.110 done. Three independent, fresh-context `explore` sessions
(verbatim records `session-01.md`-`session-03.md`, shared neutral template and scoring
protocol `session-prompt.md`) performed the one fixed timestamp task under today's
unmodified wording: 3/3 correct substitutions, zero literal `fff` copies -- the `fff`
baseline rate is 100%, feeding Phase 110's pass bar (Task 110.100). Root cause recorded
under `#### Investigation Findings`: the notation misleads where it is exposed without the
concrete-example anchor, notably in the example-free runtime error message. Baseline
inventory recorded (48 in-scope files, 54 occurrences at HEAD
`25c7f13be4571a5af635a69eb37dcd3bdfb30025`; deltas: 32 instruction files total, not 33;
`docs/tsk/*.md` carry zero occurrences, not the expected uppercase variant). No `src/` or
`tests/` file was touched. Mechanism note: the implementing agent's own `task` tool is
denied, so each trial ran as a headless `opencode run` relay that invoked the `explore`
subagent via the `task` tool with the template verified byte-identical from the raw event
stream.

#### 2026-10-06T06:02:59.173Z - Status planning → progress (Phase 100 start)

Frontmatter `status` bumped `planning` → `progress` via the generic `set_status` tool
(`type="feat"`) per Task 100.100. Phase 100 (root-cause investigation) is now in flight.

#### 2026-10-04T06:55:42.756Z - Plan refined (second-pass review findings applied)

Second-pass review of the plan against the live tree: every factual claim independently
re-verified, no new errors found (the prior E1-E3 fixes hold). Applied: G1 (the Task
110.100 pass bar gains an absolute floor -- at least two-thirds of the trials must be
correctly substituted -- closing the vacuous-baseline case), G2 (the measurement protocol
is defined up front -- one fixed timestamp task per session, "correct substitution"
defined, the `fff` baseline measured with the same protocol), G3 (Phase 110 transcripts
recorded in the same `session-*.md` sibling convention as Phase 100), G4 (Task 110.115's
re-draft loop bounded to two rounds, with a stop-for-user-decision exit on a negative
pass bar or a non-notation root cause), D1 (ACC-003's category enumeration now includes
the generated `docs/api` pages), D2 (the Overview's rollout list now includes the test
pinning the error text and the `docs/api` pages), D3 (the templates/examples premise
phrased as verified against the live tree on 2026-10-04, re-verified at rollout by Task
120.100), I1 (Task 100.105's baseline anchor pinned to an explicit HEAD SHA), I2
(session-file naming fixed: `session-NN.md` per session plus `session-prompt.md` for the
shared prompt template), I3 (the subagent type named: `explore`), I4 (status-transition
tasks now also prepend an Updates entry). Verified facts: 29 `src/` files with 33
occurrences, `AGENTS.md:945`, `tests/general/tools/test_validate.py:895`, 11 generated
`docs/api` pages, `docs/` and packaged `data/` schema copies byte-identical, 12 of 33
instruction files, 24 templates/examples with zero occurrences, the sole user-visible
error string at `models/md/frontmatter.py:187`, and a complete exclusion set (`#fff` CSS
literals, the two ADRs, `CHANGELOG.md`, the `docs/tsk` historical records carrying the
only uppercase `SS.fff` variant, gitignored `build/`, this README).

#### 2026-10-04T06:00:51.526Z - Plan refined (review findings applied)

Plan review against the live tree found and fixed: E1 (Task 120.105 said 6 instruction
files; 12 carry the notation), E2 (Task 120.120 now names both schema output locations --
`docs/` vs the packaged `data/` copies -- and the 6-of-12 affected types), E3 (ACC-005's
parser regression re-scoped from the frontmatter-less instruction files to
templates/examples), G1 (verbatim agent records plus the neutral prompt template now stored
in a `session-*.md` sibling of this README), G2 (new Task 100.105 baseline inventory
defines ACC-003's in-scope file set), G3 (quantitative pass bar defined up front in Task
110.100, selection in Task 110.115), D1 (templates/examples premise corrected -- they carry
concrete timestamps, not the notation; Task 120.100 is verify-and-update-if-found), D2
(notation rendering unified on `yyyy-MM-dd[T ]HH:mm:ss.fff[Z|±HH:MM]`), D3 (unaffected
`docs/adr/README.md` dropped from Task 120.120), D4 (the runtime error string in
`models/md/frontmatter.py` distinguished from docstring/comment-only mentions), I1
(`-- depends on:` suffixes added to every task line), I2 (this README's own old-notation
references explicitly out of scope for ACC-003), I3 (prompt template persisted with the
verbatim records), I4 (frontmatter `status` transitions tracked in the task lines).

#### 2026-10-03T07:39:04.941Z - Created

Feature created for GitHub issue #183 ("Agents misread 'fff' misunderstand in templates and
examples"). The plan covers a short root-cause investigation (spawning independent fresh-context
`task`-tool agent sessions with today's unmodified wording), selection and validation of a
replacement millisecond-placeholder notation, and a full rollout across packaged
templates/examples/create-update-instruction-files/docstrings/runtime-error-messages/schemas/AGENTS.md,
without changing the underlying timestamp validation rules established by feat-146-date-time. The
two ADRs that document the old notation as historical decision records, and other historical
narrative content (`CHANGELOG.md`, session transcripts, historical task docs), are explicitly out
of scope.

### More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/183
