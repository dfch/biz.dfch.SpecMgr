---
created: 2026-08-31 07:25:24.241609
id: feat-33-vcr
status: planning
type: feat
updated: 2026-08-31 08:50:00
version: 1.0.0
---

# Feature: Add artifact type "Verification Case Record" (VCR)

## Plan

### Overview

New document-type domain, `vcr` ("Verification Case Record"), that captures
how a single requirement or use case is verified: a coverage assessment plus
a list of acceptance criteria, each with its own DTAIS verification method.
Fills a gap identified during `feat-32-sysrs` (System Specification)
planning -- see that feature's README, Design Notes, "Domain-to-source
mapping" table and "Not yet decided" list: no existing specmgr domain
models ISO/IEC/IEEE 29148's / MITRE SE Guide's "Verification / Test and
Evaluation" concept. Tracked by GitHub issue #33. Follows the domain-first
hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and lands on the
"simple surface" from day one (generic `update`/`set_status` dispatch, per
ADR 36905d5b-8057-4294-8665-c7eed5534db0 -- no per-domain mutation tools,
including no per-AC create/read/update/delete tools).

Domain key: `vcr`.

### Requirements

- REQ-001 (decided): `## Verifies` references **exactly one** REQ or UC --
  modeled as a `Verifies(MarkdownSection2WithComment)` with a single
  mandatory `value: MarkdownParagraph` line ("`REQ|UC <uuid>: <title>`",
  `field_validator`-regex-checked) plus a **mandatory** `notes: MarkdownParagraph` paraphrase (in fixed declaration order, mirroring
  RSK's `Assessment.probability`/`.impact` two-mandatory-fields idiom) and
  an optional leading HTML `comment`. **Not** a bullet list -- no
  cardinality `model_validator` is needed, since a single-value field is
  structurally incapable of holding more than one reference; see the
  "single-value-field over list-of-one" decision in Design Notes and
  Decisions Made below (this supersedes the original
  `MarkdownListItemWithNotes` design). Resolves the previously-open "id is
  a real UUID, not a human code" gap shared with `sysrs`'s own REQ-003.
- REQ-002 (decided): `## Coverage` is a closed vocabulary paragraph --
  `full` / `partial` / `none` -- mirroring `rsk`'s `## Strategy` pattern
  (`MarkdownParagraph` + `field_validator` regex).
- REQ-003 (decided): `## Acceptance Criteria` holds >= 1 repeating
  `### AC-NNN (Method): <criterion text>` sub-sections (3-digit
  zero-padded number, e.g. `AC-001`), DEC-Option-style (numbered H3, no
  per-item mutation tools). `Method` is parsed from the heading itself via
  regex (RSK `Probability`/`Impact` idiom) and is a closed **DTAIS**
  vocabulary: Demonstration, Test, Analysis, Inspection, Special.
  Each AC may optionally carry a `#### Test Steps` numbered procedure
  list. A `model_validator` rejects duplicate `AC-NNN` numbers.
- REQ-004 (decided): Frontmatter `status` is a closed, hyphen-free
  four-value lifecycle -- `draft` / `progress` / `complete` / `approved` --
  grounded in INCOSE's Guide for Writing Requirements, Attribute A26
  ("Need or Requirement Verification Status": "not started, in work,
  complete, and approved"; see
  `.specmgr/feat/feat-32-sysrs/incose-guide-writing-requirements-2019.md:1225`),
  reworded to this repo's hyphen-free style. No separate pass/fail/waived
  outcome field -- `## Coverage` is the only outcome signal.
- REQ-005 (not started): Everything else a from-scratch domain needs,
  patterned on `sop`'s precedent (`.specmgr/feat/feat-30-sop/README.md`):
  `vcr/models/v1/` schema + parser, 8 standard tools (`create_vcr`,
  `parse_vcr`, `list_vcr`, `get_vcr(raw=False)`, `get_vcr_example`,
  `get_vcr_template`, `delete_vcr` stub, `validate_vcr`), 3 resources
  (`schema`/`example`/`template`, no `/{id}`, no `/list`), prompts
  (`create_vcr`/`update_vcr`), generic `update`/`set_status` dispatch
  entries, packaged data, cross-cutting registration
  (`server.py`/`AGENTS.md`/`README.md`/CI/pre-commit).
- REQ-006 (decided): A cross-cutting `specmgr://dtais` resource explains
  the DTAIS verification-method vocabulary (what each of the 5 methods
  means and when/how to apply it), mirroring `sop`'s planned
  `specmgr://rasci` resource (`.specmgr/feat/feat-30-sop/README.md`
  REQ-011) and `rsk`'s existing `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix`
  resources: a thin `general/resources/dtais.py` returning
  `read_packaged_text("general", "dtais")` verbatim, backed by
  `general/data/general_dtais.md`. Flat top-level URI (like
  `specmgr://iso25010`/the planned `specmgr://rasci`), not
  `specmgr://vcr/dtais`, since the vocabulary is domain-knowledge that
  other domains (e.g. `sysrs`) may want to reference too, not owned by
  `vcr`'s own schema. See the persisted sketch in Design Notes.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 -- an `example.md`/draft body demonstrates
  the `## Verifies` shape and validates against the `models/md` engine
  (mirroring `sop`'s/`sysrs`'s pre-implementation empirical-verification
  discipline) before Phase 1 starts.
- [ ] ACC-002: Verifies REQ-002 -- `## Coverage`'s closed vocabulary is
  validated the same way.
- [ ] ACC-003: Verifies REQ-003 -- the `### AC-NNN (Method): ...` heading
  regex, DTAIS closed vocabulary, and duplicate-number rejection are
  validated against the `models/md` engine.
- [ ] ACC-004: Verifies REQ-004 -- the frontmatter `status` closed
  vocabulary is implemented and unit-tested.
- [ ] ACC-005: Verifies REQ-005 -- full domain implementation, once
  REQ-001..004 are locked, following `sop`'s task-list shape.
- [ ] ACC-006: Verifies REQ-006 -- `specmgr://dtais` exists, is registered
  in `general/resources/__init__.py` and `server.py`'s docstring, and its
  content is reviewed against the persisted Design Notes sketch.

### Scope

#### Included

- Schema design and empirical validation for `## Verifies`, `## Coverage`,
  `## Acceptance Criteria` (incl. DTAIS method + optional `#### Test Steps`), `## More Information`, `## Updates`.
- Full domain build: models, parser, 8 tools, 3 resources, prompts,
  generic dispatch registration, cross-cutting registration.
- The cross-cutting `specmgr://dtais` resource (REQ-006), even though it
  lives in `general/`, not `vcr/`, since it exists to support this
  feature's `## Acceptance Criteria` method vocabulary.

#### Explicitly Out Of Scope

- Per-AC mutation tools (`ac_create`/`ac_read`/`ac_update`/`ac_delete`) --
  deliberately deferred/rejected in favor of the "simple surface" default;
  may be revisited later if agents need to target one AC without
  resending the whole document.
- A separate pass/fail/waived outcome field -- `## Coverage`
  (full/partial/none) is the only outcome signal for now.
- Any change to `sysrs`'s own schema (this feature is a sibling domain
  `sysrs` will cross-reference once both exist, not a section inside
  `sysrs` itself).

### Dependencies

#### Depends On

- ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy).
- ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic `update`/`set_status`
  dispatch -- new domains use it from day one).
- ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads).
- ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 (paged `list_<d>` tool, not a
  resource).
- `.specmgr/feat/feat-30-sop/README.md` as the most recent
  from-scratch-domain precedent to copy tooling/registration shape from,
  including its planned (not yet implemented) `specmgr://rasci`
  cross-cutting resource design (REQ-011, Task 3.4/3.5/3.8), the direct
  precedent for `specmgr://dtais` (REQ-006).
- `rsk`'s existing `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix`
  resources, the closest *implemented* precedent for a raw-markdown
  domain-knowledge resource (`read_packaged_text` passthrough, no
  Pydantic parsing).
- `req`/`uc` domains, for the real (UUID) ids `## Verifies`
  cross-references.

#### Blocks

- `sysrs`'s own "Verification / Test and Evaluation" open design question
  (`.specmgr/feat/feat-32-sysrs/README.md`, "Not yet decided") -- once
  `vcr` exists, `sysrs` can cross-reference it instead of inventing a
  `## Verification` section of its own.

### Design Notes

Full design was worked out interactively in a planning session conducted
on the `feat-32-sysrs` branch/worktree (before this feature got its own
branch); see that session's transcript for the complete rationale,
including:

- Why the "REQ-9687"-style ids seen elsewhere in the codebase
  (`req`/`gol`/`dec`'s `## Related Artifacts`) are illustrative only, not
  the real (UUID) id format -- and why `## Verifies` therefore needs an
  explicit `REQ`/`UC` literal type tag alongside the real id, rather than
  relying on an id-prefix regex.
- Why `## Verifies` ended up a single-value field, not a
  cardinality-1-constrained list: an explore-agent survey of every
  "exactly one X" relationship in the codebase found **zero** precedent
  for a list constrained to `len == 1` via `model_validator` anywhere,
  and equally zero precedent for baking a foreign id/title into a section's
  own heading (RSK's `### Probability {1..5}`/DEC's `### Option N: title`
  idiom is only ever used for repeatable *sibling* elements, never to
  collapse a whole section into its H2). The actual precedent for a
  true 1:1 relationship is a single non-list `value: MarkdownParagraph`
  field directly under the H2 -- SOP's `Accountable` (RASCI "exactly one
  owner"), RSK's `Strategy`/`Owner`, REQ/GOL's `Source` -- so `## Verifies`
  follows that shape instead, with `notes` made mandatory (unlike
  `MarkdownListItemWithNotes.notes`, which is optional) since a paraphrase
  is always expected. See the class sketch below.
- Why DTAIS's 5 methods (Demonstration, Test, Analysis, Inspection,
  Special) were chosen over the 4-method set (Inspection, Analysis,
  Demonstration, Test) found in the primary sources reviewed for `sysrs`
  (INCOSE Guide for Writing Requirements, MITRE SE Guide) -- a deliberate
  user choice to add a 5th method. Originally named "Certification"
  (hence the initial "DTAIC" acronym); renamed to "Special" (yielding
  "DTAIS") since it reads as broader than formal certification-body
  sign-off alone -- see Decisions Made below.
- Why frontmatter `status` uses INCOSE's A26 attribute's
  workflow-progress values (reworded hyphen-free:
  `draft`/`progress`/`complete`/`approved`) rather than an invented
  pass/fail/waived lifecycle.
- Why the acceptance-criteria list needed its own numbered-H3 sub-section
  per entry (DEC-`Option`-style) rather than a flat bullet list: each
  entry has structurally distinct fields (method, optional test steps),
  which a flat `MarkdownListItem` cannot carry.
- Why `specmgr://dtais` is a cross-cutting `general/` resource, not a
  `vcr/`-scoped one: it documents a vocabulary (the 5 DTAIS methods) that
  is conceptually independent of `vcr`'s own schema -- the same reasoning
  `sop`'s still-unimplemented `specmgr://rasci` design used for RASCI
  (`.specmgr/feat/feat-30-sop/README.md` REQ-011) -- and the raw-markdown
  passthrough shape (no Pydantic parsing) mirrors `rsk`'s already-shipped
  `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` rather than
  `specmgr://iso25010`'s structured-parse approach, since the audience is
  an LLM agent reading guidance prose, not code consuming structured
  data.
- **Clean-example convention** (discovered while finalizing `example.md`
  as the sole draft): a survey of every already-implemented domain's
  shipped `<domain>_example.md` vs. `<domain>_template.md` found that
  `dec`/`uc`/`req` ship fully comment-free examples (instructional
  comments like "mandatory", "enforced via regex", closed-vocabulary
  hints live only in the template, or as plain descriptive prose in the
  body, never as an HTML comment in the finished example); `rsk`/`prb`
  *replace* a template's generic instructional comment with a realistic
  filled-in annotation (e.g. RSK's H1 comment naming the real risk
  entry) rather than leaving instructional text in place; and `feat`/`qa`
  comments are permanent structural anchors or first-class schema fields
  (e.g. `## Updates`' "newest first" note), not authoring guidance, so
  they appear unchanged in both example and template. `gol`/`tsk` show
  this isn't universally enforced (they leak leftover instructional text
  into their examples) -- an anti-pattern this feature avoids. `vcr`'s
  `example.md` now follows the `dec`/`uc`/`req`/`rsk`/`prb` pattern:
  every instructional comment was removed (they belong in the
  not-yet-drafted `template.md` instead), `## Updates`' anchor comment
  was kept as-is, and `## Verifies`' optional `comment` field is now
  exercised with one realistic filled annotation instead of staying
  empty.

**Candidate `Verifies` class sketch** (for `vcr/models/v1/body.py`, Phase
1 -- not yet implemented; persisted here so a future implementer can start
from this instead of re-deriving it):

```python
import re

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownParagraph, MarkdownSection2WithComment

_VERIFIES_PATTERN = r"^(REQ|UC) [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$"


class Verifies(MarkdownSection2WithComment):
    """`## Verifies` -- exactly one REQ or UC cross-reference. Mandatory.

    Modeled as a single non-list value field (SOP's `Accountable` / RSK's
    `Strategy`&`Owner` / REQ&GOL's `Source` precedent), not a bullet list
    -- a single-value field is structurally incapable of holding more than
    one reference, so no cardinality `model_validator` is needed. `value`
    and `notes` are two mandatory fields in fixed declaration order,
    mirroring RSK's `Assessment.probability`/`.impact` two-mandatory-
    fields-in-sequence idiom (just `MarkdownParagraph` instead of
    `Probability`/`Impact`).

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`). Inherited from
        `MarkdownSection2WithComment`.
    value:
        Single-line `"REQ|UC <uuid>: <title>"`. Mandatory.
        `field_validator`-regex-checked against `_VERIFIES_PATTERN`
        (standard 8-4-4-4-12 hex UUID shape -- no UUID-format precedent
        existed elsewhere in the codebase to reuse, so this introduces
        one).
    notes:
        One-paragraph paraphrase of why this REQ/UC is verified here.
        Mandatory (unlike `MarkdownListItemWithNotes.notes`, which is
        optional).
    """

    value: MarkdownParagraph = Field(description='Single-line value: "REQ|UC <uuid>: <title>".')
    notes: MarkdownParagraph = Field(description="Mandatory one-paragraph paraphrase.")

    @field_validator("value")
    @classmethod
    def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
        """Enforce `_VERIFIES_PATTERN` against `value.text` (mirrors `req.Level`/`rsk.Strategy`)."""
        if not re.fullmatch(_VERIFIES_PATTERN, value.text):
            raise ValueError(f"value must match pattern {_VERIFIES_PATTERN!r}, got {value.text!r}")
        return value
```

**Candidate `specmgr://dtais` resource sketch** (for `general/resources/dtais.py` +
`general/data/general_dtais.md`, Phase 3 -- not yet implemented; persisted
here so a future implementer can start from this instead of re-deriving
it. Mirrors `rsk/resources/tara.py` + `rsk/data/rsk_tara.md` exactly,
just cross-cutting instead of `rsk`-scoped):

```python
"""Resource: specmgr://dtais -- the DTAIS verification-method vocabulary."""

from __future__ import annotations

from ..tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://dtais",
    name="dtais",
    title="DTAIS Verification Method Vocabulary",
    description=(
        "What DTAIS is (Demonstration, Test, Analysis, Inspection, Special), the five valid "
        "`### AC-NNN (Method): ...` method words, and when and how to apply each, as raw "
        "markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def dtais() -> str:
    """Return the packaged DTAIS guidance's full markdown text, verbatim."""
    return read_packaged_text("general", "dtais")
```

Registered in `general/resources/__init__.py` alongside `iso25010`/`version`
(and, once built, `rasci`):

```python
from . import dtais, iso25010, version  # noqa: F401

__all__ = [
    "dtais",
    "iso25010",
    "version",
]
```

Draft content outline for `general/data/general_dtais.md` (mirroring
`rsk_tara.md`'s shape -- closed-vocabulary list, then a "when to apply
each" section per method):

```markdown
# DTAIS Verification Methods

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria` (and any other domain that needs to describe how
a criterion is verified):

- `Demonstration` -- observing the system in operation, without
  instrumented measurement, to confirm a qualitative or operational
  characteristic.
- `Test` -- exercising the system under controlled, instrumented
  conditions and comparing measured results against a quantitative
  threshold.
- `Analysis` -- using calculation, modeling, or simulation (not direct
  observation of the built system) to show a requirement is met.
- `Inspection` -- visual or procedural examination of the system,
  design artifacts, or source code, without operating the system.
- `Special` -- any other verification approach not covered by the four
  methods above, e.g. a formal third-party certification/compliance
  sign-off, a supplier's certificate of conformance, or another
  contractually-mandated special process.

## When to apply each method

...(guidance per method, mirroring `rsk_tara.md`'s "## When to apply each
strategy" section -- to be filled in during Phase 3, informed by
INCOSE's Guide for Writing Requirements / MITRE SE Guide's own
Demonstration/Test/Analysis/Inspection definitions).

## Relationship to `## Coverage`

... (how an AC's method interacts with the overall `full`/`partial`/`none`
coverage signal -- see `vcr`'s REQ-002).
```

**Candidate H1/body outline** (not yet empirically validated against
`models/md` -- Phase 0 task):

```markdown
# Feature: <free text, unconstrained like RSK/GOL/DEC/SOP>

## Verifies

<!-- Optional context comment. -->

REQ <uuid>: <title>

<one-line paraphrase>

## Coverage

full

## Acceptance Criteria

### AC-001 (Test): <criterion text>

#### Test Steps

1. ...
2. ...

### AC-002 (Analysis): <criterion text>

## More Information

...

## Updates

<!-- Newest entry first -->

### <timestamp> — Created

...
```

(Note: `### {timestamp} — {title}`, one level shallower than `feat`'s own
`## Progress` → `### Updates` → `#### {timestamp} — {title}`, since `vcr`
has no Plan/Progress split -- same reasoning `sysrs` used for its own
`## Updates` section.)

### Related Decisions

- No dedicated ADR yet -- design decisions recorded above and in this
  feature's own Decisions Made log below, per the "scoped entirely to
  this feature's implementation details" rule in AGENTS.md.

### Task List

#### Phase 0: Empirical schema validation

- [x] Task 0.1: Draft `example.md`/`template.md` bodies exercising every
  section and validate against the `models/md` engine (mirroring `sop`'s/
  `sysrs`'s discipline) before writing any Pydantic model code.
  - [x] `example.md` finalized as the **sole** draft (earlier
    `example.v2.md`/`example.v3.md` iterations merged into it and
    deleted): real frontmatter, single-value-field `## Verifies` (see
    Design Notes' `Verifies` class sketch), DTAIS/`Special` terminology,
    and every instructional/enforcement comment removed per the
    clean-example convention discovered in `dec`/`uc`/`req`'s shipped
    `*_example.md` files (see Design Notes) -- the only comment kept is
    `## Updates`' permanent "newest first" anchor, plus one new filled
    annotation exercising `Verifies`' optional `comment` field. Still not
    yet validated against `models/md`, since no `vcr` model code exists
    yet; see Task 1.1-1.3.
  - [x] `template.md` drafted (blind-text placeholder, mirroring
    `dec`/`rsk`/`prb`/`req`/`uc`'s shipped `*_template.md` shape): exercises
    the same section shape as `example.md` (frontmatter, `## Verifies`
    with optional `comment` + mandatory `value` + mandatory `notes`,
    `## Coverage`, `## Acceptance Criteria` with two `### AC-NNN (Method):
    ...` entries -- one with `#### Test Steps`, one without --,
    `## More Information`, `## Updates`), with placeholder ("blind text")
    content and a real-looking placeholder UUID
    (`deaddead-face-face-face-deaddeadface` for the frontmatter `id`,
    `c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee` for the `## Verifies`
    cross-reference). Restores the instructional guidance stripped from
    `example.md` per the clean-example convention, but only as an actual
    HTML comment where `example.md` itself already shows one is
    structurally valid (`## Verifies`' single leading-comment slot, and
    `## Updates`' permanent anchor) -- `## Coverage`, `## Acceptance
    Criteria`, and `#### Test Steps` carry no comment in the already-
    finalized `example.md` either (mirroring their precedent classes'
    lack of a `WithComment` variant: `rsk.Strategy`, `dec.ProsAndCons`,
    `dec.Option`, none of which support a leading comment), so adding one
    there would silently commit `template.md` to a schema shape Phase 1
    has not decided and `example.md` already contradicts. Their guidance
    (Coverage's closed vocabulary; Method's closed DTAIS set; the `>= 1`/
    unique-number rule; Test Steps' optionality) is instead folded into
    the free-form AC body prose as a trailing sentence, mirroring
    `prb_template.md`/`uc_template.md`'s established precedent of
    appending "Mandatory."/"Optional." notes directly into blind-text
    paragraph/list content rather than a comment; `## Coverage` itself
    (an exact-match `full`/`partial`/`none` value with no other content
    allowed, `re.fullmatch`-enforced) carries no note at all, matching
    `rsk_template.md`'s identical bare-value `## Strategy` precedent.
    `## More Information` uses the exact `dec_template.md`/
    `feat_template.md` boilerplate sentence instead of a comment, for the
    same reason. Still not yet validated against `models/md`, since no
    `vcr` model code exists yet; see Task 1.1-1.3.
- [x] Task 0.2: Confirm the `### AC-NNN (Method): ...` heading regex and
  duplicate-number `model_validator` behave as expected on hand-written
  fixtures. Done via a throwaway `/tmp` scratch script (not committed, not
  a permanent test file), modeled on `dec`'s
  `_OPTION_HEADING_PATTERN`/`_validate_option_numbers_unique` precedent;
  see the new Updates entry below for the exact pattern, fixtures, and
  outcomes (all passed after fixing one bug in the first draft pattern --
  missing literal escaped parentheses around the method group).

#### Phase 1: Models and parser

- [ ] Task 1.1: `vcr/models/v1/frontmatter.py` (`VcrFrontmatter`, closed
  `status` vocabulary).
- [ ] Task 1.2: `vcr/models/v1/body.py` (`Verifies`, `Coverage`,
  `AcceptanceCriterion`/`AcceptanceCriteria`, `MoreInformation`, reused
  `Updates`).
- [ ] Task 1.3: `vcr/models/v1/document.py`, `parser.py`, `summary.py`,
  `_util.py`, `__init__.py`.
- [ ] Task 1.4: Unit tests for every model class and the parser.

#### Phase 2: Tools

- [ ] Task 2.1: `create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr` (with
  `raw` param), `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub,
  `validate_vcr`.
- [ ] Task 2.2: Generic `update`/`set_status` dispatch entries
  (`type="vcr"`) in `general/tools/`.

#### Phase 3: Resources and prompts

- [ ] Task 3.1: `specmgr://vcr/schema`, `.../example`, `.../template`
  resources.
- [ ] Task 3.2: `create_vcr`/`update_vcr` prompts.
- [ ] Task 3.3: `general/data/general_dtais.md` content (fill in the
  draft outline persisted in Design Notes), `general/resources/dtais.py`
  (`specmgr://dtais`), registered in `general/resources/__init__.py`;
  unit tests.

#### Phase 4: Cross-cutting registration

- [ ] Task 4.1: `server.py` import line.
- [ ] Task 4.2: `AGENTS.md` Status section bullet (mirroring the
  `sop`/`feat` bullets).
- [ ] Task 4.3: `README.md`, CI/pre-commit updates as needed.
- [ ] Task 4.4: `specmgr docs`/`specmgr adr-toc` regeneration, full test
  suite, ruff/vulture gates.

## Progress

### Current Status

**As of 2026-08-31**: Phase 0 (Empirical schema validation) complete.
`example.md` finalized as the **sole** draft (the intermediate
`example.v2.md`/`example.v3.md` iterations were merged into it and
deleted -- real frontmatter, single-value-field `## Verifies`,
DTAIS/`Special` terminology, and every instructional comment stripped per
the clean-example convention); `template.md` now drafted alongside it
(blind-text placeholders, instructional comments restored, mirroring
`dec`/`rsk`/`prb`/`req`/`uc`'s shipped `*_template.md` files); the
`### AC-NNN (Method): ...` heading regex and a duplicate-AC-number
`model_validator` idea (modeled on `dec`'s `Option`/
`_validate_option_numbers_unique` precedent) both confirmed against
hand-written fixtures via a throwaway `/tmp` scratch script (Task 0.2).
The `Verifies` class sketch and the `specmgr://dtais` resource sketch
(REQ-006) remain persisted in Design Notes for Phases 1/3. Still no
`vcr` model/tool/resource code written -- neither `example.md` nor
`template.md` has been validated against the actual `models/md` engine
yet, since that engine doesn't have a `vcr` schema to validate against
until Phase 1 exists.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31T09:10:00.000000 — Phase 0 complete: drafted template.md, confirmed AC-NNN regex/duplicate check

Drafted `template.md` (Task 0.1's remaining sub-bullet), reading
`example.md` plus `dec_template.md`/`rsk_template.md`/`prb_template.md`/
`req_template.md`/`uc_template.md` (`src/biz/dfch/specmgr/<domain>/data/`)
first to confirm the codebase's actual `*_template.md` conventions: short
"blind text" placeholder prose (`prb`/`uc` precedent), an HTML comment
restoring authoring/enforcement guidance on fields whose precedent class
is a `*WithComment` variant (`req_template.md`'s `## Level`/`## Priority`),
and appending "Mandatory."/"Optional."/cardinality notes as trailing prose
directly inside free-form blind-text content otherwise (`prb_template.md`/
`uc_template.md`). Cross-checked every comment placement against the
already-finalized `example.md` before adding one: `## Verifies` is the
document's *only* comment-bearing section (`Verifies` is sketched as
`MarkdownSection2WithComment` in Design Notes, and `example.md` itself
already exercises the slot) plus `## Updates`' permanent anchor;
`## Coverage`, `## Acceptance Criteria`, and `#### Test Steps` show no
comment in `example.md` either, matching their precedent classes'
lack of comment support (`rsk.Strategy`, `dec.ProsAndCons`, `dec.Option`)
-- adding one there would have committed `template.md` to a schema shape
Phase 1 hasn't decided and `example.md` already contradicts. So
`template.md` exercises every section from `example.md`'s shape
(frontmatter with placeholder id `deaddead-face-face-face-deaddeadface`;
`## Verifies` with one leading comment bundling both the "optional
context" convention and the enforced value/notes shape, a placeholder
`REQ <uuid>: <title>` value using a second, distinct placeholder UUID
`c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee`, and a mandatory `notes`
paraphrase; a bare `## Coverage` value with no note at all, matching
`rsk_template.md`'s identical `## Strategy` precedent (an exact-match
`re.fullmatch` value has no room for trailing text either); `## Acceptance
Criteria` with two `### AC-NNN (Method): ...` entries -- the first
carrying the `>= 1`/DTAIS-closed-set/unique-number guidance as a trailing
prose sentence in its own free-form body paragraph, and an optional
`#### Test Steps` list; the second with no `#### Test Steps`, and a
trailing note explaining why -- `## More Information` using the exact
`dec_template.md`/`feat_template.md` boilerplate sentence instead of a
comment; `## Updates` with its permanent "newest first" anchor). Then ran
Task 0.2: a throwaway `/tmp/vcr_scratch_task02.py` script (deleted after
the run, never committed) tested `_AC_HEADING_PATTERN = re.compile(r"###
AC-(\d{3}) \((Demonstration|Test|Analysis|Inspection|Special)\): (.+)")`
against 6 valid headings (all 5 DTAIS words plus a 3-digit boundary case
`AC-999`) and 8 invalid headings (2-digit/4-digit number, an unknown
method word `Certification`, missing parentheses, missing colon, missing
criterion text, a non-digit number, and wrong case) via `re.fullmatch`,
and a `dec`-`_validate_option_numbers_unique`-style seen-set duplicate
check against 6 number-list fixtures (no duplicates, two different
allowed-gap cases, an exact duplicate, a duplicate at opposite ends of the
list, and a single-entry list). First draft of the pattern omitted the
literal escaped parentheses around the method group, which the script
caught immediately (valid cases wrongly failed to match, and the
"missing parentheses" invalid case wrongly matched); fixed and re-ran --
all 14 heading cases and all 6 duplicate-check cases passed on the second
run. Confirmed the corrected pattern also matches all four real
`### AC-NNN (Method): ...` headings in the already-finalized
`example.md` verbatim. `example.md` itself was read-only throughout --
left byte-for-byte unchanged (`git status`/`git diff` confirm no
modification). Updated Task 0.1/0.2 checkboxes and Current Status
accordingly; no Decisions Made entry needed (no open design question was
settled here, just an empirical confirmation of already-decided
REQ-003/Design Notes text).

#### 2026-08-31T08:50:00.000000 — Merged example.v2.md/example.v3.md into a single, cleaned example.md

Reviewed `example.v2.md` (concurrently edited by the user: DTAIS/`Special`
rename applied directly, plus two comment tweaks) against `example.v3.md`
(my own DTAIS-rename pass, created before noticing the user's edit) --
confirmed the two had converged on the same content, with the user's `v2`
slightly ahead (refined comment wording). Then reviewed every HTML
comment in the document for whether it helps a future *using* agent
(authoring a new `vcr` document) vs. a future *implementing* agent
(building the Pydantic models) -- surveyed `dec`/`uc`/`req`/`rsk`/`prb`/
`feat`/`qa`'s already-shipped `*_example.md`/`*_template.md` files to
find the actual codebase convention (see new Design Notes bullet).
Result: removed every instructional/enforcement comment (`## Coverage`'s
vocabulary hint, AC-001's regex/resource-discovery hint, the `## Acceptance Criteria` comment that wrongly said the list "may be empty" -- contradicting
already-decided REQ-003's `>= 1` -- `#### Test Steps`'s and `## More Information`'s optionality notes, and the Updates entry's "enforced via
REGEX" note, none of which correspond to an actual designed comment-slot);
kept `## Updates`' "newest first" anchor (a permanent structural comment,
not authoring guidance, per `feat`'s identical convention); removed the
top meta/changelog comment block entirely (that history now lives only in
this README); and added one new realistic filled-in comment under
`## Verifies` to exercise its designed optional `comment` field (mirroring
RSK's/PRB's H1-comment pattern), since it had never been demonstrated.
Deleted `example.v2.md` and `example.v3.md`; `example.md` is now the
feature's single, definitive draft, intended for a future implementer to
build against directly. Updated Task 0.1, Current Status, and Design
Notes (candidate outline + new clean-example-convention bullet)
accordingly.

#### 2026-08-31T08:35:00.000000 — Renamed DTAIC/Certification to DTAIS/Special; added `specmgr://dtais` resource plan

Renamed the "Certification" verification method to "Special" (acronym
DTAIC -> DTAIS) throughout the current-design text (REQ-003, ACC-003,
Overview, Scope, Design Notes) -- past dated Updates/Decisions log entries
left unchanged as historical record. Added REQ-006/ACC-006: a new
cross-cutting `specmgr://dtais` resource explaining the DTAIS vocabulary,
mirroring `sop`'s still-unimplemented `specmgr://rasci` design and `rsk`'s
shipped `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` raw-markdown
resources. Persisted a full sketch (`general/resources/dtais.py`,
`general/resources/__init__.py` registration, and a draft
`general/data/general_dtais.md` content outline covering all 5 methods)
in Design Notes for Phase 3 (Task 3.3, new). Added `example.v3.md`
(supersedes `example.v2.md`) with AC-004 renamed to `(Special)`.

#### 2026-08-31T08:15:00.000000 — Added example.v2.md, redesigned `## Verifies`

Redesigned `## Verifies` from a cardinality-1-constrained
`MarkdownListItemWithNotes` bullet list to a single-value field
(`Verifies(MarkdownSection2WithComment)`: mandatory `value` line +
mandatory `notes` paraphrase + optional leading `comment`), after an
explore-agent survey found no codebase precedent for either the
list-of-one design or a heading-embedded-id alternative, but did find a
direct precedent for true 1:1 relationships (SOP's `Accountable`, RSK's
`Strategy`/`Owner`, REQ/GOL's `Source`). Persisted the resulting
`Verifies` class sketch (regex, field_validator, docstring) in Design
Notes for Phase 1. Added `example.v2.md` -- same scenario as `example.md`
but with the new `## Verifies` shape and a real YAML frontmatter block
(`id`/`status`/`type`/`created`/`updated`/`version`), so it is usable
directly once `vcr/models/v1/` exists rather than staying body-only.
Updated REQ-001, the candidate H1/body outline, and Task 0.1 to match.

#### 2026-08-31T07:52:00.000000 — Added discussion-draft example.md

Added `example.md` (API key revocation latency scenario, thematically
continuing `feat-32-sysrs/example.v4.md`'s partner-API-key story) for
user review -- illustrates `## Verifies`/`## Coverage`/
`## Acceptance Criteria` (all four DTAIC methods, with and without
optional `#### Test Steps`)/`## More Information`/`## Updates`. Not yet
validated against `models/md` (no `vcr` model code exists). Also
corrected the `## Updates` entry nesting in this README's own candidate
body outline (Design Notes) from `####` to `###`, matching `sysrs`'s own
"no Plan/Progress split -> one level shallower than `feat`" reasoning,
which applies identically to `vcr`.

#### 2026-08-31T07:25:24.241609 — Created

Feature folder created after an interactive planning session (conducted
on the `feat-32-sysrs` branch/worktree) settled the `vcr` schema shape,
DTAIC vocabulary, frontmatter status lifecycle, and simple-surface
tooling scope. GitHub issue #33 opened with a short overview as its
description; branch/worktree `feat-33-vcr` created off `origin/dev`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31T08:50:00.000000 — `example.md` is the sole draft; instructional comments removed

Consolidated `example.md`/`example.v2.md`/`example.v3.md` into a single
`example.md`, deleting the other two. Adopted the "clean example" convention
already used by `dec`/`uc`/`req`/`rsk`/`prb`/`feat` (see Design Notes):
instructional/enforcement comments (closed-vocabulary hints, "mandatory/
optional" notes, regex-enforcement notes, resource-discovery hints) do not
belong in a finished example -- they belong in the not-yet-drafted
`template.md`, or nowhere, since the real content already demonstrates the
shape. Only `## Updates`' permanent "newest first" anchor comment was kept
(a structural anchor, not authoring guidance). Also fixed a latent bug:
the removed `## Acceptance Criteria` comment claimed the list "may be
empty," contradicting already-decided REQ-003 (`>= 1` mandatory) -- no
longer an issue once the comment is gone, since the example's own 4 ACs
already satisfy it. Added a new filled annotation under `## Verifies` to
exercise its designed optional `comment` field for the first time.

#### 2026-08-31T08:35:00.000000 — DTAIC's "Certification" renamed to "Special" (DTAIS)

Renamed the 5th verification method from "Certification" to "Special,"
changing the acronym from "DTAIC" to "DTAIS" throughout REQ-003, the
Overview, Scope, Acceptance Criteria, and Design Notes. User-directed
terminology choice; no additional rationale beyond preferring "Special"
as a broader term. `example.md`/`example.v2.md` (historical, superseded)
keep the original "Certification" wording; `example.v3.md` uses the
new term.

#### 2026-08-31T08:35:00.000000 — Cross-cutting `specmgr://dtais` resource (REQ-006)

Added a new requirement for a `specmgr://dtais` resource explaining the
DTAIS method vocabulary, mirroring `sop`'s planned (not yet built)
`specmgr://rasci` resource and `rsk`'s shipped `specmgr://rsk/tara`/
`specmgr://rsk/risk-matrix` raw-markdown domain-knowledge resources.
Deliberately placed in `general/resources/` (flat `specmgr://dtais` URI),
not `vcr/resources/` (which would have been `specmgr://vcr/dtais`),
since the vocabulary is domain-knowledge other domains (e.g. `sysrs`)
may also want to reference, not something owned by `vcr`'s own schema --
same reasoning as `sop`'s RASCI design. Scheduled as Phase 3, Task 3.3,
not implemented yet.

#### 2026-08-31T08:15:00.000000 — `## Verifies` is a single-value field, not a list-of-one

Replaced the original `MarkdownListItemWithNotes` + cardinality-1
`model_validator` design for `## Verifies` with a single non-list
`Verifies(MarkdownSection2WithComment)` (mandatory `value` line +
mandatory `notes` paraphrase + optional leading `comment`). A
heading-embedded alternative (`## Verifies: REQ <uuid>: <title>`) was also
considered and rejected -- neither the list-of-one nor the
heading-embedded shape has any precedent in the codebase, while the
single-value-field shape directly matches SOP's `Accountable`, RSK's
`Strategy`/`Owner`, and REQ/GOL's `Source` (all genuine 1:1
relationships). `notes` is mandatory here (unlike the optional `notes` on
`MarkdownListItemWithNotes`), since a paraphrase is always expected.

#### 2026-08-31T07:25:24.241609 — Domain key `vcr`, not `ver`/`avc`

Chose `vcr` ("Verification Case Record") over `ver` (too easily confused
with the unrelated `version` frontmatter field) and `avc` (over-emphasizes
acceptance criteria over the verification record as a whole).

#### 2026-08-31T07:25:24.241609 — DTAIC is 5 methods, including Certification

Primary sources reviewed for `sysrs` (INCOSE Guide for Writing
Requirements, MITRE SE Guide) only document 4 verification methods
(Inspection, Analysis, Demonstration, Test). User explicitly chose a
5-method set adding Certification.

#### 2026-08-31T07:25:24.241609 — No separate pass/fail/waived outcome field

`## Coverage` (full/partial/none) is the only outcome signal; adding a
separate disposition field was considered and rejected as redundant.

#### 2026-08-31T07:25:24.241609 — Simple surface, no per-AC mutation tools

Follows every domain since `sop`'s default (ADR
36905d5b-8057-4294-8665-c7eed5534db0): no per-domain mutation tools.
Per-AC `ac_create`/`ac_read`/`ac_update`/`ac_delete` tools
(ADR-`Option`-style) were considered and explicitly deferred/rejected for
the initial build.

### Related PRs / Commits

- [Issue #33](https://github.com/dfch/biz.dfch.SpecMgr/issues/33):
  tracking issue for this feature.

### More Information

None yet.
