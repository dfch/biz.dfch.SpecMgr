---
classification: null
created: '2026-09-04 00:00:00.000Z'
id: feat-92-resources
status: done
type: feat
updated: '2026-10-07T06:21:40.954Z'
version: 1.0.0
---

# Feature: Expose Cross-Cutting Reference Resources as Markdown with Model-Backed Drift-Guard Tests, Add EARS

## Plan

### Overview

Change how the cross-cutting reference resources (`specmgr://iso25010`,
`specmgr://dtais`, `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`,
`specmgr://rasci`) are exposed and validated, and add a new one
(`specmgr://ears`). Every current consumer of these resources is an LLM
reading prose via an MCP prompt instruction, never programmatic code
indexing into a parsed structure -- so validation moves from "structured
JSON returned on every call" (`iso25010` today) or "ad hoc regex
cross-check in the resource's own test" (`dtais`/`tara`/`risk-matrix`
today) to a uniform pattern: raw markdown output, backed by a dedicated
internal Pydantic model that is (a) parsed on every resource call purely
to fail fast on structural drift, with the parsed result discarded and
the raw text returned, and (b) covered by its own
`tests/models/test_*.py` drift-guard suite. See GitHub issue #92.

### Requirements

- REQ-001: `specmgr://iso25010` returns raw markdown (`text/markdown`) instead of a structured `Iso25010` JSON object, and still calls `parse_iso25010()` on every read to fail fast on structural drift.
- REQ-002: A dedicated `general/models/dtais.py` model parses the DTAIS guidance document's structure (5 method words, matching "when to apply" list, 3-value coverage list).
- REQ-003: A dedicated `rsk/models/v1/tara.py` model parses the TARA guidance document's structure (4 strategy words, "when to apply" quadrant list, mitigation-interaction list, 6-value status list).
- REQ-004: A dedicated `rsk/models/v1/risk_matrix.py` model parses only the "Product thresholds" list (4 entries), leaving the visual 5x5 table unmodeled.
- REQ-005: A dedicated `general/models/rasci.py` model parses the 5 RASCI roles and their descriptions.
- REQ-006: A new `specmgr://ears` resource documents the EARS requirement-phrasing templates, backed by a `general/models/ears.py` model and a new packaged `general/data/general_ears.md`.
- REQ-007: An ADR documents the repo-wide convention established here (reference resource = markdown + model-backed unittest, not structured JSON).

### Acceptance Criteria

- [x] ACC-001: `specmgr://iso25010`'s `mime_type` is `text/markdown` and its test asserts fail-fast behavior on a malformed packaged file.
- [x] ACC-002: `tests/models/test_dtais.py` fails if `general_dtais.md`'s 5+3-item structure is broken.
- [x] ACC-003: `tests/models/test_tara.py` fails if `rsk_tara.md`'s 4+4+6-item structure is broken.
- [x] ACC-004: `tests/models/test_risk_matrix.py` fails if `rsk_risk_matrix.md`'s 4-item threshold list is broken.
- [x] ACC-005: `tests/models/test_rasci.py` fails if `general_rasci.md`'s 5-role structure is broken.
- [x] ACC-006: `specmgr://ears` is registered, documented in `server.py`'s module docstring, and covered by a model + resource test.
- [x] ACC-007: An ADR exists documenting the convention.

### Scope

#### Included

- The five existing resources' output-shape/validation changes.
- One new resource (`ears`) and its packaged data, authored from scratch.
- New models, each with dedicated structural tests.
- One ADR.

#### Explicitly Out Of Scope

- Any change to how `req`/`gol`/`sysrs`/`vcr` *consume* EARS/ISO25010
  guidance (no prompt rewiring beyond what already references these
  resources).
- Adding a general-purpose markdown-table parsing primitive to
  `models/md` (deliberately avoided per Design Notes below).

### Dependencies

#### Depends On

- None.

#### Blocks

- None known yet.

### Design Notes

- **List-item modeling pattern**: `dtais`/`tara`/`ears`'s closed-vocabulary
  bullets are modeled as `MarkdownListItem` subclasses with a
  `@computed_field` that regex-extracts the leading keyword from `.text`,
  reusing the exact precedent already established by
  `feat.RequirementItem`/`tsk.TaskItem` -- no new shared `models/md`
  primitive is needed.
- **`risk_matrix` avoids table parsing entirely**: the visual 5x5 table
  and the "Product thresholds" list encode the same information; only the
  4-item threshold list is modeled. The visual table stays unvalidated
  prose (residual drift risk accepted, optionally covered by a
  lightweight regex-only test assertion, not a model field).
- **Model placement**: `general/models/` for `dtais`/`rasci`/`ears`
  (cross-cutting, same domain-first precedent as `paged_result.py`/
  `summary.py`); `rsk/models/v1/` for `tara`/`risk_matrix` (RSK-owned,
  alongside `Strategy`/`level_from_product`).
- **`iso25010` validation timing**: parse-and-discard at request time
  (fail fast in production) *and* a CI-time drift-guard test -- not
  test-only validation.

### Related Decisions

- ADR (to be created in Phase 0): formalizes this feature's central
  convention repo-wide.


Cross-checked against the original paper (`Mavin_A_Rolls_Royce_EARS_RE09_Paperaccepted.pdf`,
kept in this feature folder): the packaged `general_ears.md` authored in Phase 6 used
invented pattern names/order/template wording instead of the paper's own §4.1-4.6
terminology, omitted the paper's §4.1 generic syntax entirely, and had no worked
examples in `## When to use each pattern`. This phase corrects REQ-006's realized
content to match the source paper; no new requirement/acceptance-criterion is added
since REQ-006/ACC-006 already cover "documents the EARS requirement-phrasing
templates" -- this is a content-accuracy fix, not new scope. Lands as additional
commits on the still-open PR #95 (branch `feat-92-resources` -> `dev`), not a new PR.

**Source material, verbatim from the paper (§4.1-4.6), needed for Tasks 8.1-8.4 --
recorded here because the PDF is a personal reference kept in this feature folder
only, not a repo artifact, and will not be available at implementation time:**

- **Generic syntax (§4.1)**: `` `<optional preconditions> <optional trigger> the <system name> shall <system response>` `` -- goes into `general_ears.md`'s intro paragraph (Task 8.2).
- **Pattern order and names, in this exact order** (§4.1's specialization list and the
  §4.2-4.6 section headings agree): `Ubiquitous requirements`, `Event-driven
  requirements`, `Unwanted behaviours`, `State-driven requirements`, `Optional
  features` -- this is the new `_PATTERN_NAMES` value for Task 8.1, and the bullet
  order for both lists in `general_ears.md` (Task 8.2).
- **Templates, one per pattern (§4.2-4.6), each a backticked sentence template
  followed by the existing hand-written explanation (kept as-is per the "leave
  explanatory text as-is" decision)**:
  - Ubiquitous requirements -- `` `The <system name> shall <system response>.` ``
  - Event-driven requirements -- `` `WHEN <optional preconditions> <trigger> the <system name> shall <system response>.` ``
  - Unwanted behaviours -- `` `IF <optional preconditions> <trigger>, THEN the <system name> shall <system response>.` ``
  - State-driven requirements -- `` `WHILE <in a specific state> the <system name> shall <system response>.` ``
  - Optional features -- `` `WHERE <feature is included> the <system name> shall <system response>.` ``
- **First worked example per pattern (§4.2-4.6's own "For example: ..." sentence --
  the paper's §4.5 gives State-driven a second, alternate "During" example too, not
  used here), to append to each `## When to use each pattern` bullet (Task 8.2)**:
  - Ubiquitous requirements: "The control system shall prevent engine overspeed."
  - Event-driven requirements: "When continuous ignition is commanded by the aircraft, the control system shall switch on continuous ignition."
  - Unwanted behaviours: "If the computed airspeed fault flag is set, then the control system shall use modelled airspeed."
  - State-driven requirements: "While the aircraft is in-flight, the control system shall maintain engine fuel flow above XXlbs/sec."
  - Optional features: "Where the control system includes an overspeed protection function, the control system shall test the availability of the overspeed protection function prior to aircraft dispatch."
- The paper's `## Combining patterns`-equivalent (§4.7) still uses lowercase
  `when`/`while`/`where` keywords in its own prose; this phase deliberately does
  NOT touch `general_ears.md`'s existing `## Combining patterns` section (out of
  the six items requested), so it will read inconsistently (lowercase keywords)
  next to the newly upper-cased templates above it -- known, accepted, not a bug.


### Task List

#### Phase 100: ADR

- [x] Task 100.100: Write and merge the ADR (REQ-007).

#### Phase 110: `iso25010`

- [x] Task 110.100: Switch `general/resources/iso25010.py` to markdown output with parse-and-discard validation.
- [x] Task 110.110: Update `dtais.py`'s stale docstring cross-reference.
- [x] Task 110.120: Broaden `tests/models/test_iso25010.py`; rewrite `tests/general/resources/test_iso25010.py`.

#### Phase 120: `dtais` model

- [x] Task 120.100: Add `general/models/dtais.py` and `tests/models/test_dtais.py`.

#### Phase 130: `tara` model

- [x] Task 130.100: Add `rsk/models/v1/tara.py` and `tests/models/test_tara.py`.

#### Phase 140: `risk_matrix` model

- [x] Task 140.100: Add `rsk/models/v1/risk_matrix.py` and `tests/models/test_risk_matrix.py`. Scope extended per the user's explicit "follow the ADR" decision to also include wiring `rsk/resources/risk_matrix.py` to `parse_risk_matrix` on every call, not deferred to a later follow-up.

#### Phase 150: `rasci` model

- [x] Task 150.100: Add `general/models/rasci.py` and `tests/models/test_rasci.py`.

#### Phase 160: `ears` resource

- [x] Task 160.100: Author `general/data/general_ears.md`.
- [x] Task 160.110: Add `general/models/ears.py`, `general/resources/ears.py`, and tests.

#### Phase 170: Wrap-up

- [x] Task 170.100: Regenerate docs, update `server.py`'s docstring, add a CHANGELOG entry, run the full lint/test pass.

#### Phase 180: Align EARS content with the source paper (Mavin et al., RE'09)
- [x] Task 180.100: Discard the stray uncommitted partial edit to `general/data/general_ears.md` (`git checkout --` it) before starting.
- [x] Task 180.110: Update `general/models/ears.py`'s `_PATTERN_NAMES` constant to the paper's exact ordered vocabulary (`["Ubiquitous requirements", "Event-driven requirements", "Unwanted behaviours", "State-driven requirements", "Optional features"]`); update stale name/order mentions in its module and class docstrings. No structural/field changes needed.
- [x] Task 180.120: Rewrite `general/data/general_ears.md` per the source paper: append the generic EARS syntax to the existing intro paragraph (same block, no blank line); reorder/rename/reword `## The five requirement patterns`'s five bullets to the paper's exact names and templates (keep each bullet's existing hand-written explanatory sentence); reorder `## When to use each pattern` to match, and append the paper's first worked example per pattern to each bullet.
- [x] Task 180.130: Update `tests/models/test_ears.py`: `_EXPECTED_PATTERN_NAMES` and all 3 malformed fixtures (`_MISSING_PATTERN_TEXT`, `_MISMATCHED_WHEN_TO_USE_TEXT`, `_WRONG_PATTERN_NAME_TEXT`) to the new names/order/templates.
- [x] Task 180.140: Update `tests/general/resources/test_ears.py`: `_EXPECTED_PATTERN_NAMES` and `_valid_ears_text()`'s fixture to the new names/order/templates.
- [x] Task 180.150: Update stale old-name/order mentions in `general/resources/ears.py` (module docstring + `@mcp.resource(...)` description) and `server.py`'s module docstring (~line 120-122).
- [x] Task 180.160: Wrap-up: regenerate docs (`specmgr docs`), extend the existing CHANGELOG `[Unreleased]` entry, run the full lint/test pass, commit, and push to `origin/feat-92-resources` (lands on the existing open PR #95 -- no new PR).

## Progress

### Current Status

**As of 2026-09-04**: Phase 0 (ADR), Phase 1 (`iso25010`), Phase 2
(`dtais` model), Phase 3 (`tara` model), Phase 4 (`risk_matrix` model),
Phase 5 (`rasci` model), and Phase 6 (`ears` resource) done. ADR
356d8781-e446-4c26-917a-eda85648ce9d accepted, documenting the repo-wide
convention; `specmgr://iso25010` now follows it (raw markdown,
parse-and-discard). `general/models/dtais.py`'s `Dtais` model and
`rsk/models/v1/tara.py`'s `Tara` model both exist and are covered by
`tests/models/test_dtais.py`/`tests/models/test_tara.py`. A follow-up
unit of work (not a numbered phase of its own) has now wired
`general/resources/dtais.py`/`rsk/resources/tara.py` to call
`parse_dtais`/`parse_tara` on every resource call, per the ADR's literal
Decision Outcome -- see the dated Updates entry below. Phase 4
(`risk_matrix`) and Phase 5 (`rasci`) both followed the user's "follow
the ADR literally" decision from the start: `rsk/models/v1/risk_matrix.py`'s
`RiskMatrix` model was added together with `rsk/resources/risk_matrix.py`'s
wiring to `parse_risk_matrix` in the same phase, and
`general/models/rasci.py`'s `Rasci` model was added together with
`general/resources/rasci.py`'s wiring to `parse_rasci`, neither as a
separately-deferred follow-up -- see the dated Updates entries below.
Phase 6 (`ears`) authored the brand-new `general/data/general_ears.md`
guidance file from scratch AND built `general/models/ears.py`/
`general/resources/ears.py`'s request-time parse-and-discard wiring in
the same phase, from day one -- no "later wiring" follow-up was needed
for this one, unlike `dtais`/`tara`'s original narrower Phase 2/3 task
scoping. Phase 7 (wrap-up) is now also done: a final consistency pass
found `server.py`'s module docstring, every touched resource's own
docstring, `README.md`, and `AGENTS.md` already accurate (no stale
"structured JSON"/"no dedicated model" claims for any of the six
resources), added a `CHANGELOG.md` `[Unreleased]` entry (GitHub issue
#92), and re-ran `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc`
with zero resulting diff -- confirming every prior phase's own
doc-regeneration step already left the repo fully in sync.

**Phase 8 (align EARS content with the source paper, Mavin et al.,
RE'09) is now also done**: cross-checking Phase 6's freshly-authored
`general_ears.md` against the actual source paper found its pattern
names/order/templates were invented rather than transcribed, so this
phase replaced `general/models/ears.py`'s `_PATTERN_NAMES` and every
stale docstring mention with the paper's own §4.1-4.6 vocabulary
(`Ubiquitous requirements`, `Event-driven requirements`, `Unwanted
behaviours`, `State-driven requirements`, `Optional features`, in that
order), rewrote `general/data/general_ears.md` to use the paper's exact
generic syntax and per-pattern templates, and appended the paper's own
worked example sentence to each `## When to use each pattern` bullet;
`## Combining patterns` was deliberately left untouched. **The feature
is now fully complete**: all 8 phases plus the dtais/tara follow-up are
done, every REQ-001..007 is implemented, and every ACC-001..007 remains
satisfied (see the dated Updates entries below).

### Blockers

None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 23:59:59.000Z - Phase 8 (align EARS content with the source paper) complete -- feature done
Cross-checked Phase 6's from-scratch `general/data/general_ears.md`
against the actual source paper (Mavin et al., "Easy Approach to
Requirements Syntax (EARS)", RE'09, sections 4.1-4.6, kept as a personal
reference PDF in this feature folder, not a repo artifact) and found it
had used invented pattern names/order/wording instead of transcribing
the paper's own terminology, omitted the paper's §4.1 generic syntax
sentence entirely, and had no worked examples under `## When to use each
pattern`.
Task 8.0: confirmed via `git status`/`git diff` that there was no stray
uncommitted edit to `general_ears.md` to discard -- nothing to do.
Task 8.1: updated `general/models/ears.py`'s `_PATTERN_NAMES` to the
paper's exact ordered vocabulary (`["Ubiquitous requirements",
"Event-driven requirements", "Unwanted behaviours", "State-driven
requirements", "Optional features"]`) and every stale name/order mention
in the module docstring and the `PatternItem`/`WhenToUseItem`/`Patterns`
docstrings. Verified (see Decisions Made below) that the existing `_NAME`
regex fragment (`` [A-Za-z]+(?:[- ][A-Za-z]+)* ``) already matches a
3-token name like `Event-driven requirements` without modification, so
no regex widening was needed.
Task 8.2: rewrote `general/data/general_ears.md`: appended the paper's
generic syntax (`` `<optional preconditions> <optional trigger> the
<system name> shall <system response>` ``) as a trailing clause of the
existing intro paragraph (same block, no new paragraph); reordered/
renamed/re-templated `## The five requirement patterns`'s five bullets to
the paper's exact names and backticked templates, in the paper's exact
order, keeping each bullet's pre-existing hand-written explanatory
sentence untouched; reordered `## When to use each pattern` to match and
appended the paper's own first worked example sentence, verbatim, to each
bullet. Left `## Combining patterns` completely untouched, per the task's
explicit instruction (its lowercase `when`/`while`/`where` keywords now
read inconsistently against the newly upper-cased `WHEN`/`WHILE`/`WHERE`
templates above it -- known, accepted, not fixed). Ran the file through
`specmgr_mdformat` and adopted its normalized wrapping as the committed
form.
Task 8.3: updated `tests/models/test_ears.py`'s `_EXPECTED_PATTERN_NAMES`
and all three malformed fixtures (`_MISSING_PATTERN_TEXT`,
`_MISMATCHED_WHEN_TO_USE_TEXT`, `_WRONG_PATTERN_NAME_TEXT`) to the new
names/order/templates, each still exercising the exact same failure mode
as before (missing one pattern bullet; mismatched order between the two
lists; an out-of-vocabulary pattern name).
Task 8.4: updated `tests/general/resources/test_ears.py`'s
`_EXPECTED_PATTERN_NAMES` and `_valid_ears_text()`'s fixture to the new
names/order/templates; confirmed it remains a well-formed,
`parse_ears`-accepted document.
Task 8.5: updated the stale name/order mentions in
`general/resources/ears.py`'s module docstring and its
`@mcp.resource(...)` `description=` string, and in `server.py`'s module
docstring's `specmgr://ears --` bullet.
Task 8.6: regenerated `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md`
via `specmgr docs`/`specmgr mcp-docs` (both produced real diffs, since
`ears.py`'s docstrings and `general_ears.md`'s content changed); `specmgr
adr-toc` produced zero diff, as expected (no ADR touched by this phase).
Extended the existing `CHANGELOG.md` `[Unreleased]` `### Added` bullet
(rather than adding a new bullet) with a clause noting the `specmgr://ears`
content was aligned with the source paper's exact pattern names/order/
templates and now includes its worked examples.
Full quality gate, all green: `ruff format --check` (1672 files already
formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py
--min-confidence 60` (no findings), full `unittest` suite (**3377
tests**, all passing -- identical count to Phase 7's own last run, since
this phase only changed existing fixtures/docstrings, not test/src
structure), and `specmgr unused-code` ("No unused code found").
The feature is now fully complete: all 8 phases plus the dtais/tara
follow-up are done, REQ-001 through REQ-007 remain implemented, and
ACC-001 through ACC-007 remain satisfied -- REQ-006/ACC-006 are unchanged
in scope by this phase, only corrected in content accuracy. No new
REQ-*/ACC-* item was added. No blockers. Per this phase's own explicit
instructions, this work was NOT committed or pushed -- it lands as
additional commits on the still-open PR #95 at the orchestrator's/user's
discretion.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 23:59:59.000Z - Phase 8 implementation calls: no regex widening needed; CHANGELOG bullet extended in place
Two small calls made while implementing Phase 8: (1) Task 8.1 asked to
verify whether `general/models/ears.py`'s shared `_NAME` regex fragment
(`` [A-Za-z]+(?:[- ][A-Za-z]+)* ``) needed widening to match a 2-3-token
name like `Event-driven requirements`/`Unwanted behaviours` -- a quick
standalone regex check (`re.fullmatch` against all five new names)
confirmed the existing fragment already matches an unbounded number of
`[- ]`-separated letter-groups, so `Event-driven requirements` (three
groups: `Event`, `-driven`, ` requirements`) and every other new name
match without any change; no widening was made, since the fragment's `*`
repetition was never actually bounded to one extra group in the first
place. (2) The CHANGELOG instructions offered either extending the
existing `specmgr://ears` bullet or adding a small new one -- chose to
extend the existing `### Added` bullet in place with one more clause,
since the correction is a content-accuracy refinement of the exact same
resource already announced there, not a separate change worth its own
bullet.
#### 2026-09-04 00:00:00.000Z - `ears` model design calls (Phase 6)
Two non-obvious calls made while implementing `general/models/ears.py`:
(1) the phase's own design guidance suggested declaring `patterns:
list[PatternItem]` as a bare field directly on `Ears`, mirroring `Dtais.
methods`'s bare-list shape -- but the authored `general/data/
general_ears.md` content itself (fixed verbatim per REQ-006's own "Content
to author" section) puts `## The five requirement patterns` under its
own H2 heading, unlike `Dtais.methods`'s heading-less intro list. A bare
list field cannot skip an intervening heading (confirmed by an
`AssertionError` from `models.md`'s own parser when first attempted), so
`patterns` is instead a composite `Patterns(MarkdownSection2)` section
(`patterns: Patterns`, with the 5-item list living at `patterns.items`),
mirroring `WhenToUse`'s own composite shape one section earlier than the
original design sketch called for. This is a straightforward adaptation
to the parser's actual heading-consumption rules, not a deferred-to-user
ambiguity -- the fixed content and the parser's own constraints left only
one workable model shape. (2) Unlike `tara`'s three lists (which
genuinely disagree on order across the document, forcing set-based
cross-checks), `general_ears.md`'s two closed-vocabulary lists were
authored from scratch with the SAME pattern-name order deliberately kept
in both, so `Ears._validate_when_to_use_matches_patterns` is a simple,
strict ordered-list equality (`patterns.items` names == `when_to_use.
items` names, in order) -- simpler and stricter than `tara`'s set-based
comparison, and possible only because this document's author (this
phase) controlled both lists' ordering from the start, unlike `tara`'s
pre-existing, reverse-engineered file.
#### 2026-09-04 00:00:00.000Z - `rasci` model design calls (Phase 5)
Two non-obvious calls made while implementing `general/models/rasci.py`:
(1) `RoleItem` exposes two `@computed_field`s (`role`/`description`)
rather than one, mirroring `tsk.models.v1.task_item.TaskItem`'s
`checked`/`description` precedent instead of `dtais`'s/`risk_matrix`'s
single-computed-field `MethodItem`/`ThresholdItem` style -- REQ-005's own
wording ("the 5 RASCI roles **and their descriptions**") explicitly calls
out the description as part of what must be modeled, unlike REQ-002's "5
method words" (no "and their descriptions" clause). (2) REQ-005's "5
RASCI roles" is read strictly, pinning the closed, ordered 5-value
vocabulary (`["Responsible", "Accountable", "Support", "Consulted",
"Informed"]`) in `Roles._validate_roles`, not just a `Field(min_length=5,
max_length=5)` count -- mirroring `CoverageRelationship`/
`ProductThresholds`'s strict-reading precedent from Phases 2/4, and
matching ACC-005's own "fails if ... 5-role **structure** is broken"
wording (a renamed/reordered role is a structural break, not merely a
count mismatch). Unlike `dtais`'s two 5-word lists, RASCI has only the one
role list in the whole document (no second list to cross-check against),
so there is no analogous "matching" cross-check to add here.
#### 2026-09-04 00:00:00.000Z - `risk_matrix` model design calls (Phase 4)
Two non-obvious calls made while implementing `rsk/models/v1/risk_matrix.py`:
(1) the `level_from_product` cross-check the phase instructions "strongly
encouraged" (rather than mandated) was implemented: `ProductThresholds.
_validate_thresholds` asserts `level_from_product(low) == zone` and
`level_from_product(high) == zone` for every one of the 4 threshold
bands, in addition to pinning the closed, ordered 4-value zone vocabulary
and the contiguous-bounds-spanning-1..25 check. This ties the packaged
prose directly to the schema's own executable zone-derivation logic
(`rsk.models.v1.assessment.level_from_product`), giving REQ-004's
drift-guard real teeth against the same class of "documentation quietly
diverges from code" drift the existing (and still-present)
`tests/rsk/resources/test_risk_matrix.py` ad hoc regex checks already
guarded against for the visual table, but now enforced at request time
via the model, not just in a resource-level test. (2) `ThresholdItem`
exposes its three pieces (`low: int`, `high: int`, `zone: str`) as three
separate `@computed_field`s rather than one combined tuple-returning
field, since `ProductThresholds._validate_thresholds` needs to read each
piece independently (for the order check, the contiguity check, and the
`level_from_product` cross-check) and three plain `int`/`str`-typed
properties are simpler to consume there than unpacking a tuple three
times; this also matches `assessment.Probability.value`/`Impact.value`'s
own "one computed field per meaningfully-distinct piece of data" style
already established in this same package.
#### 2026-09-04 00:00:00.000Z - Follow the ADR literally: every reference resource is wired to parse-and-discard at request time, not just `iso25010`
Phase 2's Task 2.1 and Phase 3's Task 3.1 task descriptions were scoped
too narrowly -- "add the model + its `tests/models/test_*.py` suite"
only -- leaving `general/resources/dtais.py`/`rsk/resources/tara.py`
themselves un-wired to call `parse_dtais`/`parse_tara` at request time,
which contradicted ADR 356d8781-e446-4c26-917a-eda85648ce9d's Decision
Outcome ("That model is parsed on every resource call purely to fail
fast on structural drift at request time... the parsed result is
discarded and the original raw text returned unchanged" -- stated for
every reference resource, not `iso25010` alone). The orchestrator
surfaced this task-list-vs-ADR gap to the user, who decided explicitly:
follow the ADR literally -- every reference resource (not just
`iso25010`) is wired to parse-and-discard at request time. This was
implemented immediately as a follow-up for `dtais`/`tara` (see the
Updates entry above); Phases 4/5/6 (`risk_matrix`, `rasci`, `ears`) will
include this same request-time parse-and-discard wiring as part of
their own scope, not as separately-deferred follow-up work, so no
similar gap should recur for those three.
#### 2026-09-04 00:00:00.000Z - `tara` model's cross-list "matching" checks compare by set, not by order (Phase 3)
Unlike `dtais`'s two 5-word lists (which happen to share the same order,
so `Dtais._validate_when_to_apply_matches_methods` could -- and does --
compare them as ordered lists), the real `rsk_tara.md`'s TARA strategy
word appears in three lists with three genuinely *different* orders:
`transfer`/`accept`/`reduce`/`avoid` (the intro list, organized
alphabetically-ish by the TARA acronym), `transfer`/`avoid`/`reduce`/
`accept` (the "When to apply each strategy" quadrant list, organized by
probability/impact quadrant), and `reduce`/`transfer`/`avoid`/`accept`
(the "Interaction with `## Mitigation`" list, organized by how much
`## Mitigation` prose each strategy needs). Verified directly against the
real, `mdformat`-normalized file (not just the plan's own hint) before
writing the validators. Given this, `Tara._validate_quadrant_matches_
strategies`/`Tara._validate_mitigation_matches_strategies` compare the
three lists' strategy words as Python `set`s, not as ordered lists --
REQ-003's "matching 'when to apply' quadrant list"/"mitigation-interaction
list" is read as "names the same four words", not "in the same order".
The intro list itself still gets a strict, ordered check
(`Tara._validate_strategies` pins `["transfer", "accept", "reduce",
"avoid"]` exactly, mirroring `CoverageRelationship._validate_
coverage_values`'s strict-reading precedent for a list with no competing
alternate order elsewhere in the same document) -- it is the one list with
no other list to disagree with about ordering, so pinning its order costs
nothing and still catches a renamed/reordered canonical vocabulary. The
independent 6-value frontmatter `status` list gets the same strict,
ordered treatment for the same reason (no other list mentions it at all).
Tests mirror this exactly: happy-path assertions compare the quadrant/
mitigation lists' words as sets (`self.assertEqual(quadrant_words,
strategy_words)` on `set` values), never asserting a specific order for
those two lists, so a future test edit cannot silently regress back to an
order-sensitive (and therefore wrong, given the real file) comparison.
#### 2026-09-04 00:00:00.000Z - `dtais` model design calls (Phase 2)
Three non-obvious calls made while implementing `general/models/dtais.py`:
(1) `` ## Relationship to `## Coverage` ``'s heading is pinned via
`@alias(value="Relationship to `## Coverage`", type=AliasType.LITERAL)`
rather than `AliasType.REGEX` -- an exact literal comparison is simpler
and just as correct as a regex here, since the heading text (backticks
and nested `##` included) is a fixed literal string, not a pattern to
match; mirrors `feat.RelatedPrsCommits`'s existing `LITERAL`-for-
special-punctuation precedent. (2) REQ-002's "3-value coverage list" is
read strictly: `CoverageRelationship._validate_coverage_values` asserts
the actual ordered values (`["full", "partial", "none"]`), not just a
`Field(min_length=3, max_length=3)` count -- giving ACC-002 real
drift-detection teeth against a renamed/reordered coverage value, not
just a missing/extra bullet. (3) The DTAIS method-word vocabulary itself
(`Demonstration`/`Test`/`Analysis`/`Inspection`/`Special`) is NOT pinned
as a closed literal set on `Dtais.methods` -- only the count (`min_length=
5, max_length=5`) and the cross-list "matching" guarantee against
`when_to_apply.items` are enforced, mirroring `Iso25010.names`'s existing
"count only, no fixed vocabulary" precedent; REQ-002 asks for "5 method
words, matching 'when to apply' list", not a fixed vocabulary check, and
`vcr.models.v1.body._AC_HEADING_PATTERN` already separately owns the
authoritative closed DTAIS set.
#### 2026-09-04 00:00:00.000Z - EARS resource placement
`specmgr://ears` lives under `general/resources/` (cross-cutting), not
`req/resources/`, mirroring `dtais`'s cross-domain placement rationale.
#### 2026-09-04 00:00:00.000Z - Model scope for regex-cross-checked resources
Dedicated models are added for all three of `dtais`, `tara`, and
`risk_matrix` (not just `risk_matrix`), replacing their existing ad hoc
regex-based drift-guard tests.
#### 2026-09-04 00:00:00.000Z - iso25010 validation approach
Kept runtime validate-then-discard (parse via `parse_iso25010` to fail
fast, return raw text) rather than test-only validation.
### Related PRs / Commits

- GitHub issue #92: https://github.com/dfch/biz.dfch.SpecMgr/issues/92

### More Information

None.
