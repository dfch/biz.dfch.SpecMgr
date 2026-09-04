---
created: '2026-09-04 00:00:00.000Z'
id: feat-92-resources
status: review
type: feat
updated: '2026-09-04 12:00:00.000Z'
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

### Task List

#### Phase 0: ADR

- [x] Task 0.1: Write and merge the ADR (REQ-007).

#### Phase 1: `iso25010`

- [x] Task 1.1: Switch `general/resources/iso25010.py` to markdown output with parse-and-discard validation.
- [x] Task 1.2: Update `dtais.py`'s stale docstring cross-reference.
- [x] Task 1.3: Broaden `tests/models/test_iso25010.py`; rewrite `tests/general/resources/test_iso25010.py`.

#### Phase 2: `dtais` model

- [x] Task 2.1: Add `general/models/dtais.py` and `tests/models/test_dtais.py`.

#### Phase 3: `tara` model

- [x] Task 3.1: Add `rsk/models/v1/tara.py` and `tests/models/test_tara.py`.

#### Phase 4: `risk_matrix` model

- [x] Task 4.1: Add `rsk/models/v1/risk_matrix.py` and `tests/models/test_risk_matrix.py`. Scope extended per the
  user's explicit "follow the ADR" decision to also include wiring `rsk/resources/risk_matrix.py` to
  `parse_risk_matrix` on every call, not deferred to a later follow-up.

#### Phase 5: `rasci` model

- [x] Task 5.1: Add `general/models/rasci.py` and `tests/models/test_rasci.py`.

#### Phase 6: `ears` resource

- [x] Task 6.1: Author `general/data/general_ears.md`.
- [x] Task 6.2: Add `general/models/ears.py`, `general/resources/ears.py`, and tests.

#### Phase 7: Wrap-up

- [x] Task 7.1: Regenerate docs, update `server.py`'s docstring, add a CHANGELOG entry, run the full lint/test pass.

#### Phase 8: Align EARS content with the source paper (Mavin et al., RE'09)

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

- [ ] Task 8.0: Discard the stray uncommitted partial edit to
  `general/data/general_ears.md` (`git checkout --` it) before starting.
- [ ] Task 8.1: Update `general/models/ears.py`'s `_PATTERN_NAMES` constant to the
  paper's exact ordered vocabulary (`["Ubiquitous requirements", "Event-driven
  requirements", "Unwanted behaviours", "State-driven requirements", "Optional
  features"]`); update stale name/order mentions in its module and class
  docstrings. No structural/field changes needed.
- [ ] Task 8.2: Rewrite `general/data/general_ears.md` per the source paper: append
  the generic EARS syntax to the existing intro paragraph (same block, no blank
  line); reorder/rename/reword `## The five requirement patterns`'s five bullets
  to the paper's exact names and templates (keep each bullet's existing
  hand-written explanatory sentence); reorder `## When to use each pattern` to
  match, and append the paper's first worked example per pattern to each bullet.
- [ ] Task 8.3: Update `tests/models/test_ears.py`: `_EXPECTED_PATTERN_NAMES` and
  all 3 malformed fixtures (`_MISSING_PATTERN_TEXT`, `_MISMATCHED_WHEN_TO_USE_TEXT`,
  `_WRONG_PATTERN_NAME_TEXT`) to the new names/order/templates.
- [ ] Task 8.4: Update `tests/general/resources/test_ears.py`:
  `_EXPECTED_PATTERN_NAMES` and `_valid_ears_text()`'s fixture to the new
  names/order/templates.
- [ ] Task 8.5: Update stale old-name/order mentions in `general/resources/ears.py`
  (module docstring + `@mcp.resource(...)` description) and `server.py`'s module
  docstring (~line 120-122).
- [ ] Task 8.6: Wrap-up: regenerate docs (`specmgr docs`), extend the existing
  CHANGELOG `[Unreleased]` entry, run the full lint/test pass, commit, and push
  to `origin/feat-92-resources` (lands on the existing open PR #95 -- no new PR).

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
doc-regeneration step already left the repo fully in sync. **The feature
is now complete**: all 7 phases plus the dtais/tara follow-up are done,
every REQ-001..007 is implemented, and every ACC-001..007 was
individually re-verified against the current repo state (see the dated
Updates entry below).

### Blockers

None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 00:00:00.000Z - Phase 7 (wrap-up) complete -- feature done

Ran the final consistency/verification pass (Task 7.1). Cross-checked
every `server.py` module-docstring line mentioning `specmgr://iso25010`,
`specmgr://dtais`, `specmgr://rsk/tara`, `specmgr://rsk/risk-matrix`,
`specmgr://rasci`, and `specmgr://ears` against what each resource
actually does now: all six bullets already describe the current
raw-markdown behavior correctly (`iso25010`'s own bullet never claimed a
JSON/MIME shape to begin with, confirmed by direct inspection rather
than trusting Phase 1's own self-report). Searched the whole `src/` tree
for "structured"/"no dedicated model"/"parsed into a structured" near
these six resource names: every hit found is either a model's own
docstring correctly describing its *own* structured internal
representation, or a resource docstring correctly stating what the
resource is now, per ADR 356d8781-e446-4c26-917a-eda85648ce9d ("not
structured JSON") -- no stale claim survived from before this feature.
Checked the repo-root `README.md` and `AGENTS.md` for the same six
resource names: no claim about output shape (JSON vs. markdown) is made
in either file for any of the six, so nothing needed fixing there;
`AGENTS.md`'s own `general/` bullet and "Still genuinely missing"
section were inspected too and found to have a pre-existing, unrelated
staleness (they don't enumerate every resource under `general/resources/`,
e.g. `dtais`/`rasci` predate this feature and were already unlisted, and
the new `ears` resource is likewise not listed) -- left untouched since
it predates this feature and is a listing-completeness gap, not an
output-shape claim this feature's ADR is about; fixing it would be scope
creep beyond Task 7.1's own instructions.

Ran `uv run --frozen specmgr docs`, `specmgr mcp-docs`, and `specmgr
adr-toc`: all three produced **zero** `git status` diff, confirming every
prior phase's own doc-regeneration step already left `docs/api/`,
`docs/GENERATED.md`, `docs/MCP.md`, and `docs/adr/README.md` fully in
sync -- no missed regeneration step from Phases 0-6.

Added a `CHANGELOG.md` `[Unreleased]` entry (GitHub issue #92): one
`### Changed` bullet for `specmgr://iso25010`'s breaking output-shape
change (raw markdown instead of structured JSON, still parse-and-discard
validated), and one `### Added` bullet for the four new drift-guarded
models (`dtais`/`tara`/`risk-matrix`/`rasci`), the new `specmgr://ears`
resource, and the new ADR.

Full lint/test pass, all green: `ruff format --check` (1672 files already
formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py
--min-confidence 60` (no findings), `pylint $(git ls-files '*.py')`
(advisory-only, 8.91/10, same pre-existing `R0401` cyclic-import noise as
every prior phase, `|| true` in CI, not a regression), full `unittest`
suite (**3377 tests**, all passing -- identical count to Phase 6's own
last run, confirming Phase 7 added no new src/test code of its own, only
docs/CHANGELOG/this README), and `specmgr unused-code` ("No unused code
found").

Re-walked every acceptance criterion (ACC-001..007) against the current
repo state rather than trusting the existing checkboxes: ACC-001
(`general/resources/iso25010.py`'s `mime_type="text/markdown"` confirmed
directly, `tests/models/test_iso25010.py::test_raises_on_malformed_text`
and `tests/general/resources/test_iso25010.py::test_raises_on_structural_drift`
both exist), ACC-002..005 (`tests/models/test_dtais.py`/`test_tara.py`/
`test_risk_matrix.py`/`test_rasci.py` all exist with 10/11/10/7 tests
each, including 4/5/4/3 distinct malformed-fixture drift-guard assertions
respectively), ACC-006 (`specmgr://ears` registered in
`general/resources/ears.py`, imported/exported from
`general/resources/__init__.py`, documented in `server.py`'s module
docstring, and covered by `tests/models/test_ears.py` (8 tests) plus a
resource-level test), ACC-007 (the ADR file exists on disk with
`status: accepted`) -- all seven confirmed genuinely satisfied, not just
checkbox-ticked.

The feature is complete: all 7 phases plus the dtais/tara follow-up are
done, REQ-001 through REQ-007 are all implemented, and ACC-001 through
ACC-007 are all independently re-verified in this entry. No blockers.

#### 2026-09-04 00:00:00.000Z - Phase 6 (`ears` resource) complete

Authored `general/data/general_ears.md` from scratch (REQ-006, Task
6.1): an EARS (Easy Approach to Requirements Syntax) guidance document
with an intro paragraph, `## The five requirement patterns` (5 bolded,
backtick-templated bullets: `Ubiquitous`, `Event-driven`, `State-driven`,
`Unwanted behavior`, `Optional feature`), `## When to use each pattern`
(5 bolded-and-backticked bullets naming the same 5 pattern names, in the
SAME order as the first list, deliberately, since this content was
authored fresh rather than reverse-engineered from a pre-existing file),
and `## Combining patterns` (prose about "complex" multi-keyword EARS
sentences, left unmodeled). Ran the content through `specmgr_mdformat`
while iterating and adopted its normalized wrapping (inline code spans
are never broken across lines by `mdformat`, so several bullets ended up
single-line rather than soft-wrapped) as the committed, canonical form,
so a future `mdformat` pass produces no diff.

Added `general/models/ears.py` (REQ-006, Task 6.2): an `Ears
(MarkdownSection1)` document model mirroring `general.models.dtais.
Dtais`'s shape closely, with one structural deviation forced by the
authored content itself (see Decisions Made below): unlike `Dtais.
methods` (a bare `list[MethodItem]` field directly under the H1, no
heading of its own), `general_ears.md`'s first closed-vocabulary list
lives under its own `## The five requirement patterns` H2 heading, so it
is wrapped in a composite `Patterns(MarkdownSection2)` section (`items:
list[PatternItem]`, `min_length=5, max_length=5`) rather than declared as
a bare list field on `Ears` itself. `PatternItem` exposes two
`@computed_field`s (`name: str`, `template: str`) via
`_PATTERN_ITEM_PATTERN` (`` ^\*\*(?P<name>NAME)\*\* -- (?P<template>`[^`]+`).*$ ``,
`re.DOTALL`) -- the pattern name is bolded plain text, the template
itself IS backticked; the shared `_NAME` regex fragment
(`` [A-Za-z]+(?:[- ][A-Za-z]+)* ``) handles a name containing an internal
hyphen (`Event-driven`) or space (`Unwanted behavior`, `Optional
feature`). `WhenToUseItem` exposes one `@computed_field` (`name: str`)
via `_WHEN_TO_USE_ITEM_PATTERN` (bolded AND backticked variant, same
shape as `general.models.dtais.WhenToApplyItem`). `Patterns.
_validate_patterns` forces eager evaluation of every item's
`.name`/`.template` AND pins the closed, ordered 5-value vocabulary
(`_PATTERN_NAMES = ["Ubiquitous", "Event-driven", "State-driven",
"Unwanted behavior", "Optional feature"]`), mirroring `general.models.
rasci.Roles._validate_roles`'s strict-reading precedent. `WhenToUse.
_validate_items_eagerly` forces eager evaluation only (mirroring
`WhenToApply._validate_items_eagerly`). `## Combining patterns` is a
**leaf** `CombiningPatterns(MarkdownSection2)` subclass (no nested
fields), out of REQ-006's narrow scope, mirroring `RasciVsRaci`/
`ScaleAnchors`'s leaf-section precedent. `Ears.
_validate_when_to_use_matches_patterns` is REQ-006's "matching"
cross-check: `patterns.items`' names and `when_to_use.items`' names must
be equal, in the same order -- a **simple, strict ordered-list
equality**, not the set-based comparison `rsk.models.v1.tara.Tara` needed
(see Decisions Made below for why). `parse_ears()` mirrors
`parse_dtais()`'s exact `format_text` + `from_text` + `isinstance` shape.
Exported from `general/models/__init__.py` alongside `Dtais`/`Rasci`, per
that package's existing style. Added `tests/models/test_ears.py` (8
tests) mirroring `test_dtais.py`'s structure: 5 happy-path assertions
against the real packaged file (instance type, 5/5 counts, exact pattern
names/order, non-empty backticked templates, when-to-use names matching
in order) plus 3 distinct malformed-fixture drift-guard tests (ACC-006)
-- a patterns list with only 4 of the 5 required entries, a when-to-use
list whose order doesn't match the patterns list, and a patterns list
with a name (`Guard clause`) not in the closed vocabulary -- each
asserting `parse_ears` raises `AssertionError`/`pydantic.ValidationError`.

Added `general/resources/ears.py` (Task 6.2, built dispatch-ready and
wired from day one, unlike `dtais`/`tara`'s original Phase 2/3 scoping):
`@mcp.resource("specmgr://ears", ..., mime_type="text/markdown")`
decorating an `ears() -> str` function that reads the packaged text via
`read_packaged_text("general", "ears")`, calls `parse_ears(text)` to
validate (discarding the result), and returns the raw text unchanged --
mirroring `general/resources/dtais.py`'s already-wired shape exactly,
module/function docstrings included (`Raises` section:
`FileNotFoundError`/`AssertionError`/`pydantic.ValidationError`). Added
`ears` to `general/resources/__init__.py`'s import list, `__all__`, and
module docstring bullet. Added a `specmgr://ears` bullet to `server.py`'s
module docstring `Resources` section, in the same format as the
`specmgr://dtais`/`specmgr://iso25010`/`specmgr://rasci` bullets
(ACC-006's explicit requirement for this phase, not deferred to Phase
7). Added `tests/general/resources/test_ears.py` (5 tests) mirroring
`tests/general/resources/test_dtais.py`'s structure exactly, built in
full immediately (no retrofit needed, since this resource was wired from
day one): real packaged content assertions, fresh-read-per-call
(`mock.patch.object(_packaged_data, "packaged_data_path", ...)` with a
`_valid_ears_text(marker)` builder function mirroring `_valid_dtais_text`'s
precedent), `FileNotFoundError` propagation on a missing file, and a
`test_raises_on_structural_drift` fail-fast test (ACC-006's "resource
test" requirement).

Added `_._validate_patterns`/`_._validate_when_to_use_matches_patterns`
to `whitelist.py`'s Pydantic-validator group, and `combining_patterns` to
its (de)serialization-only-field group (`Ears.patterns`/`.when_to_use`
are both read by `_validate_when_to_use_matches_patterns`, so they needed
no entry; only the leaf `combining_patterns` field is never read as a
plain attribute). Regenerated `docs/api/`/`docs/GENERATED.md` via
`specmgr docs` (new `docs/api/biz.dfch.specmgr.general.models.ears.md`/
`docs/api/biz.dfch.specmgr.general.resources.ears.md` module pages, plus
the expected cross-reference updates in `docs/api/README.md`/
`docs/api/biz.dfch.specmgr.general.models.md`/
`docs/api/biz.dfch.specmgr.general.resources.md`/
`docs/api/biz.dfch.specmgr.server.md`/`docs/GENERATED.md`); `specmgr
mcp-docs` DID produce a `docs/MCP.md` diff this time (unlike prior
phases), as expected -- the resource count bumped from 43 to 44 and a new
`### Resource: ears` entry/TOC row appeared, since this is a brand-new
resource registration, not a re-wiring of an existing one. Full quality
gate (ruff format --check, ruff check, vulture, full unittest suite: 3377
tests) passed.

#### 2026-09-04 00:00:00.000Z - Phase 5 (`rasci` model, scope extended to include resource wiring) complete

Added `general/models/rasci.py` (REQ-005): a `Rasci(MarkdownSection1)`
document model for `general/data/general_rasci.md`, mirroring
`general.models.dtais.Dtais`'s shape (H1-rooted, leading `MarkdownParagraph`
intro -- confirmed against the real file that lines 3-9 form a single
paragraph, not two -- followed by an H2-nested section, not a leading bare
list directly under the H1 like `Dtais.methods`/`Tara.strategies`, since
the real file's role list lives under `## The five roles`, not the intro).
`RoleItem` (a leaf `MarkdownListItem`) recovers a bullet's role name and
description via two separate `@computed_field`s (`role: str`,
`description: str`), mirroring `tsk.models.v1.task_item.TaskItem`'s
`checked`/`description` two-computed-field precedent rather than
`dtais`'s/`risk_matrix`'s single-computed-field pattern, since REQ-005
explicitly asks for "the 5 RASCI roles **and their descriptions**", not
just the role words; the regex (`^\*\*(?P<role>[A-Za-z]+)\*\* -- ...$`,
`re.DOTALL`) matches RASCI's bolded-plain-text role names
(`**Responsible**`), confirmed against the real, `mdformat`-normalized
file to differ from DTAIS/TARA's backticked (`` `Word` ``) style. `## The
five roles` (`Roles`, `@alias(..., type=AliasType.LITERAL)` since the
heading text doesn't match the implicit `SPACE_SEPARATED` derivation of
the class name) declares `items: list[RoleItem]` (`min_length=5,
max_length=5`), with `_validate_roles` forcing eager evaluation of every
item's `.role`/`.description` AND pinning the closed, ordered 5-value
vocabulary (`["Responsible", "Accountable", "Support", "Consulted",
"Informed"]`) -- REQ-005's "5 RASCI roles" read strictly, per
ACC-005's own "fails if ... structure is broken" wording, mirroring
`CoverageRelationship`/`ProductThresholds`'s strict-reading precedent.
`## RASCI vs. plain RACI` (`RasciVsRaci`, also `@alias(...,
type=AliasType.LITERAL)`) is a **leaf** `MarkdownSection2` subclass with no
nested fields, storing the comparison section verbatim -- out of REQ-005's
narrow scope, same reasoning as `risk_matrix.py`'s `ScaleAnchors`/
`ZoneTable`/`ReadingTogether` leaf sections. `parse_rasci()` mirrors
`parse_dtais()`'s exact `format_text` + `from_text` + `isinstance` shape.
Exported from `general/models/__init__.py` alongside `Dtais`/`parse_dtais`,
per that package's existing style. Added `tests/models/test_rasci.py` (7
tests) mirroring `test_dtais.py`'s structure: 4 happy-path assertions
against the real packaged file (instance type, 5-item count, exact role
names/order, non-empty descriptions) plus 3 distinct malformed-fixture
drift-guard tests (ACC-005) -- a role list with only 4 of the 5 required
entries, a role list with two roles swapped out of order, and a role list
with a role name (`Owner`) not in the closed vocabulary -- each asserting
`parse_rasci` raises `AssertionError`/`pydantic.ValidationError`.

Per the user's "follow the ADR literally" decision (see this feature's
Decisions Made log), and per this phase's own explicitly-extended scope
(not deferred, unlike Phases 2/3's original narrower task wording), this
phase also wired `general/resources/rasci.py`'s `rasci()` to
`parse_rasci` on every call from the start: imports `parse_rasci` from
`..models` and calls it (discarding the result) right after
`read_packaged_text`, before returning the raw text; the module and
function docstrings were updated to describe the parse-and-discard
behavior and a `Raises` section (`FileNotFoundError`/`AssertionError`/
`pydantic.ValidationError`), mirroring `iso25010.py`/`dtais.py`'s
wording, and the stale "unlike `iso25010` ... this is a raw passthrough
with no dedicated model yet" line was removed. Added a
`test_raises_on_structural_drift` test to the EXISTING
`tests/general/resources/test_rasci.py` (left every other test in that
file untouched, per this phase's own instructions -- in particular
`test_content_is_generic_no_sop_specific_rules`, ACC-010, unrelated to
this phase). Also had to fix that file's pre-existing
`test_reads_fresh_on_every_call` test: it previously wrote bare
`"first"`/`"second"` strings to the temp packaged file, which is not
valid RASCI-shaped markdown and would now fail the new parse-and-discard
call -- replaced with a `_valid_rasci_text(marker)` builder function
(mirroring `test_dtais.py`'s own `_valid_dtais_text(marker)` precedent)
that produces a minimal, well-formed, `parse_rasci`-accepted document
tagged with a marker in the title, so the fresh-read-per-call assertion
still holds. Added `_._validate_roles` to `whitelist.py`'s
Pydantic-validator group, and `roles`/`rasci_vs_raci` to its
(de)serialization-only-field group (these two `Rasci` fields are never
read as plain attributes anywhere in `src/`). Regenerated
`docs/api/`/`docs/GENERATED.md` via `specmgr docs` (new
`docs/api/biz.dfch.specmgr.general.models.rasci.md` module page, plus the
expected cross-reference updates in `docs/api/README.md`/
`docs/api/biz.dfch.specmgr.general.models.md`/
`docs/api/biz.dfch.specmgr.general.resources.rasci.md`/
`docs/GENERATED.md`); `specmgr mcp-docs` produced no `docs/MCP.md` diff,
as expected, since the resource's `mime_type`/URI/name did not change.
Full quality gate (ruff format --check, ruff check, vulture, full
unittest suite: 3364 tests) passed.

#### 2026-09-04 00:00:00.000Z - Phase 4 (`risk_matrix` model, scope extended to include resource wiring) complete

Added `rsk/models/v1/risk_matrix.py` (REQ-004): a `RiskMatrix(MarkdownSection1)`
document model for `rsk/data/rsk_risk_matrix.md`, following REQ-004's
narrow scope literally -- only the "Product thresholds" 4-item list is
modeled. `## Scale anchors`, `## Zone table`, and `## Reading initial and
residual together` are each a **leaf** `MarkdownSection2` subclass
(`ScaleAnchors`/`ZoneTable`/`ReadingTogether`, no nested fields of their
own), so `models/md`'s engine stores each one's entire extent (heading +
full body, verbatim) without attempting to parse its internal
bullets/table/paragraphs -- this still satisfies the parser's
every-line-consumed-by-some-field requirement while leaving the visual
5x5 table and the two scale-anchor lists genuinely unmodeled, exactly as
this feature's Design Notes call for. All three leaf sections needed an
explicit `@alias(..., type=AliasType.LITERAL)` (their headings'
second-word-lowercase wording -- "Scale anchors", "Zone table", "Reading
initial and residual together" -- does not match the implicit
`SPACE_SEPARATED` derivation of a PascalCase class name). `ThresholdItem`
(a leaf `MarkdownListItem`) recovers a `` `low-high` → `zone` `` bullet's
three pieces via three separate `@computed_field`s (`low: int`,
`high: int`, `zone: str`), reusing `feat.RequirementItem`/`tsk.TaskItem`'s
established regex precedent; the zone regex group allows an internal
space (`"very high"`). `ProductThresholds.items` is `Field(min_length=4,
max_length=4)`, and its `_validate_thresholds` `model_validator` gives
REQ-004's drift-guard real teeth (per this module's own Decisions Made
entry below): beyond the count, it pins the 4 zone names' exact order
(`["low", "medium", "high", "very high"]`), asserts the 4 bands are
contiguous and span 1..25 exactly, and cross-checks every band's bounds
against `rsk.models.v1.assessment.level_from_product`'s own executable
zone-derivation logic (`level_from_product(low) == zone` and
`level_from_product(high) == zone`) -- tying the packaged prose directly
to the schema's actual computed-field logic, not just an independently
maintained copy of the same four numbers. `parse_risk_matrix()` mirrors
`parse_tara()`'s exact `format_text` + `from_text` + `isinstance` shape.
Exported from `rsk/models/v1/__init__.py` alongside `Tara`/`parse_tara`,
per that package's existing style. Added `tests/models/test_risk_matrix.py`
(10 tests) mirroring `test_tara.py`'s structure: 6 happy-path assertions
against the real packaged file (instance type, 4-item count, exact zone
names/order, exact bounds, and the `level_from_product` cross-check),
1 "does the hand-built minimal fixture even parse" sanity check backing
the malformed fixtures below, and 4 distinct malformed-fixture drift-guard
tests (ACC-004) -- a threshold list with only 3 of the 4 required entries,
a threshold list with two zone names swapped out of order, a threshold
list with a gap in its bounds (non-contiguous), and a threshold entry
whose stated zone doesn't match what `level_from_product` would actually
derive for its bounds -- each asserting `parse_risk_matrix` raises
`AssertionError`/`pydantic.ValidationError`.

Per the user's "follow the ADR literally" decision (see this feature's
Decisions Made log), this phase's scope was extended beyond Task 4.1's
literal "model + test" wording to also wire `rsk/resources/
risk_matrix.py`'s `risk_matrix()` to `parse_risk_matrix` on every call,
mirroring the `dtais`/`tara` follow-up's exact pattern from the start
rather than deferring it: imports `parse_risk_matrix` from `..models.v1`
and calls it (discarding the result) right after `read_packaged_text`,
before returning the raw text; the module and function docstrings were
updated to describe the parse-and-discard behavior and a `Raises` section
(`FileNotFoundError`/`AssertionError`/`pydantic.ValidationError`),
mirroring `iso25010.py`/`tara.py`'s wording. Added a
`test_raises_on_structural_drift` test to the EXISTING
`tests/rsk/resources/test_risk_matrix.py` (left every other test in that
file untouched, per this phase's own instructions -- in particular the
ACC-005 drift-guard tests `test_documented_product_thresholds_match_the_model`/
`test_documented_zone_table_matches_the_model`, which stay as their own
ad hoc regex-based check against the visual table, since REQ-004
deliberately leaves that table unmodeled). Also had to fix that file's
pre-existing `test_reads_fresh_on_every_call` test: it previously wrote
bare `"first"`/`"second"` strings to the temp packaged file, which is not
valid risk-matrix-shaped markdown and would now fail the new
parse-and-discard call -- replaced with a `_valid_risk_matrix_text(marker)`
builder function (mirroring `test_tara.py`'s own `_valid_tara_text(marker)`
precedent) that produces a minimal, well-formed, `parse_risk_matrix`-accepted
document tagged with a marker in the title, so the fresh-read-per-call
assertion still holds. Added `_._validate_thresholds` to `whitelist.py`'s
Pydantic-validator group, and `scale_anchors`/`zone_table`/
`product_thresholds`/`reading_together` to its
(de)serialization-only-field group (these four `RiskMatrix` fields are
never touched by any `model_validator`, unlike `dtais`/`tara`'s own
fields, since REQ-004 deliberately leaves their content unvalidated).
Regenerated `docs/api/`/`docs/GENERATED.md` via `specmgr docs` (new
`docs/api/biz.dfch.specmgr.rsk.models.v1.risk_matrix.md` module page,
plus the expected cross-reference updates in `docs/api/README.md`/
`docs/api/biz.dfch.specmgr.rsk.models.v1.md`/
`docs/api/biz.dfch.specmgr.rsk.resources.risk_matrix.md`/
`docs/GENERATED.md`); `specmgr mcp-docs` produced no `docs/MCP.md` diff,
as expected, since the resource's `mime_type`/URI/name did not change.
Full quality gate (ruff format --check, ruff check, vulture, full
unittest suite: 3356 tests) passed.

#### 2026-09-04 00:00:00.000Z - Follow-up: wired `dtais`/`tara` resources to parse-and-discard at request time

Phase 2's Task 2.1 and Phase 3's Task 3.1 were scoped, by their own task
text, to "add the model and its `tests/models/test_*.py` drift-guard
suite" only, deliberately leaving `general/resources/dtais.py`'s
`dtais()` and `rsk/resources/tara.py`'s `tara()` as plain
`read_packaged_text` passthroughs with no request-time parse call. That
narrower task scoping left a gap against the ADR's own Decision Outcome,
which states plainly that the backing model "is parsed on every resource
call purely to fail fast on structural drift at request time... the
parsed result is discarded and the original raw text returned
unchanged" for every reference resource, not just `iso25010`. The user
was asked to resolve this task-list-vs-ADR gap explicitly and chose to
follow the ADR literally (see the new Decisions Made entry below) rather
than leave Phases 2/3 as model-only forever. This follow-up (not itself
a numbered phase or task) implements that resolution for `dtais`/`tara`,
mirroring Phase 1's exact `iso25010.py` precedent: `general/resources/
dtais.py`'s `dtais()` now imports `parse_dtais` from `..models` and
calls it (discarding the result) right after `read_packaged_text`,
before returning the raw text; `rsk/resources/tara.py`'s `tara()`
does the same with `parse_tara` from `..models.v1`. Both modules' module
and function docstrings were updated to describe the parse-and-discard
behavior and its `Raises` section (`FileNotFoundError`/`AssertionError`/
`pydantic.ValidationError`), word-for-word mirroring `iso25010.py`'s
wording. Added a `test_raises_on_structural_drift` test to both
`tests/general/resources/test_dtais.py` and `tests/rsk/resources/
test_tara.py`, mirroring `test_iso25010.py`'s pattern exactly
(`tempfile.TemporaryDirectory()` + `mock.patch.object(_packaged_data,
"packaged_data_path", ...)` pointing at a minimal malformed document,
asserting `(AssertionError, ValueError)` -- `pydantic.ValidationError`
is a `ValueError` subclass, so this covers both failure shapes exactly
like `test_iso25010.py`'s own assertion). Also had to fix both files'
pre-existing `test_reads_fresh_on_every_call` tests: they previously
wrote bare `"first"`/`"second"` strings to the temp packaged file, which
is not valid DTAIS-/TARA-shaped markdown and would now fail the new
parse-and-discard call -- replaced with `_valid_dtais_text(marker)`/
`_valid_tara_text(marker)` builder functions (mirroring `test_iso25010.
py`'s own `_valid_iso25010_text(marker)` precedent) that produce
minimal, well-formed, `parse_dtais`/`parse_tara`-accepted documents
tagged with a marker in the title, so the fresh-read-per-call assertion
still holds. `_valid_tara_text` had to reproduce the real file's exact
arrow (`→`) and em-dash (`—`) characters in the quadrant/mitigation/
status bullets, since `Tara`'s `_QUADRANT_ITEM_PATTERN`/
`_STATUS_ITEM_PATTERN` regexes match those literal Unicode characters,
not an ASCII `->`/`--` substitute. Did NOT touch `general/data/
general_dtais.md`, `rsk/data/rsk_tara.md`, or the `Dtais`/`Tara` model
classes themselves -- all already correct from Phases 2/3. Did NOT check
off any Task List items or ACC boxes for this follow-up: Task 2.1/
ACC-002 and Task 3.1/ACC-003 already correctly describe "model + test"
only and remain checked; this wiring gap is closed by this Updates entry
plus the Decisions Made entry, not by a new/retroactively-edited task.
Full quality gate (ruff format --check, ruff check, vulture, full
unittest suite: 3345 tests) passed. Regenerated `docs/api/` via
`specmgr docs` (docstring-only diffs in
`docs/api/biz.dfch.specmgr.general.resources.dtais.md`/
`docs/api/biz.dfch.specmgr.rsk.resources.tara.md`); `specmgr mcp-docs`
produced no `docs/MCP.md` diff, as expected, since neither resource's
`mime_type`/URI/name changed.

#### 2026-09-04 00:00:00.000Z - Phase 3 (`tara` model) complete

Added `rsk/models/v1/tara.py` (REQ-003): a `Tara(MarkdownSection1)`
document model for `rsk/data/rsk_tara.md`, mirroring
`general.models.dtais.Dtais`'s shape (H1-rooted, leading `MarkdownParagraph`
intro -- confirmed against the real file that lines 3-8 form a single
paragraph, not two, so no `list[MarkdownParagraph]` intro field was
needed -- followed by a leading `list[StrategyItem]` field directly under
the H1 before any H2). Four leaf `MarkdownListItem` subclasses recover the
distinct bullet shapes via `@computed_field` regex extraction:
`StrategyItem.strategy` (the bare `` `word` `` intro list, single-line, no
`re.DOTALL`), `QuadrantItem.strategy` (the bolded
`` **{quadrant} -> `word`**\n{explanation} `` list under `## When to apply
each strategy`), `MitigationItem.strategy` (the `` `word`: {explanation} ``
list under `` ## Interaction with `## Mitigation` ``), and
`StatusItem.status` (the `` `word` -- {explanation} `` list under
`` ## Interaction with the frontmatter `status` ``, using the real file's
em dash character, not a hyphen). The latter three regexes use
`re.DOTALL`, same reasoning as `dtais`. Confirmed via direct token
inspection of the real, `mdformat`-normalized file that
`` ## Interaction with `## Mitigation` `` has an intro paragraph and items
but deliberately **no** closing paragraph (its bullet list is followed
directly by the next `##` heading), unlike `WhenToApply`/
`StatusInteraction`, which both have one -- `MitigationInteraction`
therefore declares no `closing` field. All three H2 section classes use
`@alias(..., type=AliasType.LITERAL)` since their headings contain
backticks/nested `##`/inline code, mirroring `dtais`'s established
precedent. `Tara.strategies`/`WhenToApply.items`/`MitigationInteraction.
items` are each `Field(min_length=4, max_length=4)`;
`StatusInteraction.items` is `Field(min_length=6, max_length=6)`. Five
`model_validator(mode="after")`s: `WhenToApply._validate_items_eagerly`/
`MitigationInteraction._validate_items_eagerly` (reusing the already-
whitelisted generic name, no new `whitelist.py` entry needed for these
two) force eager per-item computed-field evaluation only;
`StatusInteraction._validate_status_values` forces eager evaluation AND
pins the closed, ordered 6-value vocabulary (`["open", "mitigating",
"accepted", "occurred", "closed", "dropped"]`); `Tara._validate_strategies`
forces eager evaluation AND pins the intro list's own order as the one
canonical, fixed 4-value vocabulary (`["transfer", "accept", "reduce",
"avoid"]`); `Tara._validate_quadrant_matches_strategies`/`Tara.
_validate_mitigation_matches_strategies` are REQ-003's "matching"
cross-checks -- **by set, not by order** (see Decisions Made below).
`parse_tara()` mirrors `parse_dtais()`'s exact `format_text` + `from_text`
+ `isinstance` shape. Exported from `rsk/models/v1/__init__.py` alongside
`Strategy`/`level_from_product`, per that package's existing style. Added
`tests/models/test_tara.py` (11 tests) mirroring `test_dtais.py`'s
structure: 6 happy-path assertions against the real packaged file
(instance type, 4/4/4/6 counts, the exact strategy/status word lists, and
set-equality assertions -- not order assertions -- for the quadrant/
mitigation lists, matching the model's own validator logic) plus 5
distinct malformed-fixture drift-guard tests (ACC-003) -- a missing intro
strategy bullet (3 of 4), a quadrant list whose *set* no longer matches
(drops `accept`, duplicates `avoid`), a mitigation list whose *set* no
longer matches (drops `accept`, duplicates `reduce`), a short-by-one
status list (5 of 6, `occurred` dropped), and a status list with an
out-of-vocabulary value (`unknown` instead of `occurred`) -- each
asserting `parse_tara` raises `AssertionError`/`pydantic.ValidationError`.
Deliberately did NOT touch `rsk/resources/tara.py` (the resource function
itself) or `rsk/data/rsk_tara.md` -- wiring the resource to call
`parse_tara` for parse-and-discard validation is a later phase's task, per
the plan's own Task 3.1 note. Added
`_._validate_status_values`/`_._validate_strategies`/
`_._validate_quadrant_matches_strategies`/
`_._validate_mitigation_matches_strategies` to `whitelist.py`'s
Pydantic-validator group (the two `_validate_items_eagerly` methods
needed no new entry, reusing the name `dtais`'s Phase 2 addition already
whitelisted). Regenerated `docs/api/`/`docs/GENERATED.md` via
`specmgr docs` (new `docs/api/biz.dfch.specmgr.rsk.models.v1.tara.md`
module page, plus the expected cross-reference updates in
`docs/api/README.md`/`docs/api/biz.dfch.specmgr.rsk.models.v1.md`/
`docs/GENERATED.md`). Full quality gate (ruff format --check, ruff check,
vulture, full unittest suite: 3343 tests) passed.

#### 2026-09-04 00:00:00.000Z - Phase 2 (`dtais` model) complete

Added `general/models/dtais.py` (REQ-002): a `Dtais(MarkdownSection1)`
document model for `general/data/general_dtais.md`, mirroring
`models.iso25010.Iso25010`'s shape (H1-rooted, leading `MarkdownParagraph`
intro, a leading `list[MethodItem]` field directly under the H1 before any
H2). Two leaf `MarkdownListItem` subclasses recover the closed
vocabularies via `@computed_field` regex extraction, mirroring
`feat.RequirementItem`/`tsk.TaskItem`'s precedent: `MethodItem.method`
(the un-bolded `` `Word` -- ... `` intro list) and `WhenToApplyItem.method`/
`CoverageItem.value` (the bolded-and-backticked `` **`Word`** -- ... ``
lists under `## When to apply each method`/`` ## Relationship to `##
Coverage` ``, the latter's heading pinned via `@alias(..., type=AliasType.
LITERAL)` since it literally contains backticks and a nested `##`). Both
regexes use `re.DOTALL` (a soft-wrapped bullet's `.text` keeps its
continuation lines' embedded newline), mirroring
`sysrs.models.v1.body._validate_cross_reference_items`'s established
reasoning. `Dtais.methods`/`WhenToApply.items` are each `Field(min_length=5,
max_length=5)`; `CoverageRelationship.items` is `Field(min_length=3,
max_length=3)`. Three `model_validator(mode="after")`s extend
`tsk.Task._validate_items_eagerly`'s pattern: `WhenToApply.
_validate_items_eagerly` forces every item's `.method` eagerly;
`CoverageRelationship._validate_coverage_values` forces every item's
`.value` eagerly AND pins the closed, ordered 3-value vocabulary
(`["full", "partial", "none"]`) -- REQ-002's "3-value coverage list" read
strictly (actual values, not just count); `Dtais.
_validate_when_to_apply_matches_methods` is REQ-002's explicit "matching"
cross-check: the intro 5-item method list and the "when to apply" 5-item
list must name the same 5 words in the same order. `parse_dtais()` mirrors
`parse_iso25010()`'s exact `format_text` + `from_text` + `isinstance`
shape. Exported from `general/models/__init__.py` alongside `DocSummary`/
`PagedResult`, per that package's existing style. Added `tests/models/
test_dtais.py` (10 tests) mirroring `test_iso25010.py`'s structure: 6
happy-path assertions against the real packaged file (instance type,
5/5/3 counts, the exact method/when-to-apply/coverage word lists) plus 4
distinct malformed-fixture drift-guard tests (ACC-002) -- a missing intro
method bullet (4 of 5), a mismatched "when to apply" word, a
short-by-one coverage list (2 of 3), and a coverage list with an
out-of-vocabulary value (`unknown` instead of `none`) -- each asserting
`parse_dtais` raises `AssertionError`/`pydantic.ValidationError`.
Deliberately did NOT touch `general/resources/dtais.py` (the resource
function itself) or `general/data/general_dtais.md` -- wiring the
resource to call `parse_dtais` for parse-and-discard validation is a
later phase's task, per the plan's own Task 2.1 note. Added
`_._validate_coverage_values`/`_._validate_when_to_apply_matches_methods`
to `whitelist.py`'s Pydantic-validator group, and `methods`/
`when_to_apply`/`coverage`/`closing` to its (de)serialization-only-field
group (the new model's fields aren't read as plain attributes by any
`src/` code yet, same as every other domain's Phase-1-style model
addition). Regenerated `docs/api/`/`docs/GENERATED.md` via `specmgr docs`
(new `docs/api/biz.dfch.specmgr.general.models.dtais.md` module page,
plus the expected cross-reference updates in `docs/api/README.md`/
`docs/api/biz.dfch.specmgr.general.models.md`/`docs/GENERATED.md`). Full
quality gate (ruff format --check, ruff check, vulture, full unittest
suite: 3332 tests) passed.

#### 2026-09-04 00:00:00.000Z - Phase 1 (`iso25010`) complete

Switched `general/resources/iso25010.py`'s `iso25010()` resource function
from returning a structured `Iso25010` JSON object (`mime_type="application/json"`)
to returning the packaged `general/data/general_iso25010.md` raw markdown
text (`mime_type="text/markdown"`), per ADR
356d8781-e446-4c26-917a-eda85648ce9d: it still
calls `parse_iso25010()` on every call to fail fast on structural drift,
discarding the parsed result and returning the original raw text. Fixed
stale "`specmgr://iso25010`'s structured parse is the precedent for
machine-readable reference data" cross-references in
`general/resources/dtais.py`, `general/resources/rasci.py`, and
`rsk/resources/tara.py`'s docstrings (Task 1.2), and one similarly stale
"unlike `iso25010` (parsed into a structured model)" line in `rasci.py`'s
function docstring. Broadened `tests/models/test_iso25010.py` with a new
`test_raises_on_malformed_text` fail-fast/drift-guard test (a
deliberately-truncated 2-of-9-characteristic document). Rewrote
`tests/general/resources/test_iso25010.py` to match the new raw-markdown
contract, mirroring `tests/general/resources/test_dtais.py`/
`tests/rsk/resources/test_tara.py`'s established pattern: real packaged
content assertions, fresh-read-per-call
(`mock.patch.object(_packaged_data, "packaged_data_path", ...)`),
`FileNotFoundError` propagation on a missing file, and (ACC-001) a new
`test_raises_on_structural_drift` test that patches the packaged file to
malformed content and asserts the resource raises. Regenerated
`docs/api/`/`docs/GENERATED.md` via `specmgr docs` (docstring-only diff,
`server.py`'s own module docstring intentionally left describing the old
JSON behavior for now -- that's Phase 7's Task 7.1). Full quality gate
(ruff format --check, ruff check, vulture, full unittest suite: 3322
tests) passed.

#### 2026-09-04 00:00:00.000Z - Phase 0 (ADR) complete

Created and accepted ADR
`docs/adr/356d8781-e446-4c26-917a-eda85648ce9d-expose-cross-cutting-reference-resources-as-raw-markdown-wit.md`
("Expose cross-cutting reference resources as raw markdown with
model-backed drift-guard tests, not structured JSON") via the `create_adr`
MCP tool, covering all three considered options (chosen: uniform raw
markdown + model-backed drift-guard tests; rejected: uniform structured
JSON; rejected: uniform raw markdown with ad hoc regex tests only) and
cross-referencing `specmgr://iso25010`/`dtais`/`rsk/tara`/`rsk/risk-matrix`/
`rasci`/the new `ears`, plus GitHub issue #92 and this feature's README in
"More Information". Regenerated `docs/adr/README.md` via
`specmgr adr-toc`. Full quality gate (ruff format --check, ruff check,
vulture, full unittest suite: 3318 tests) passed.

#### 2026-09-04 00:00:00.000Z - Created

Feature folder created for GitHub issue #92, capturing the plan discussed
and agreed with the user.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
