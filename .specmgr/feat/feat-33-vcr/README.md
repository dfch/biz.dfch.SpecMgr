---
created: 2026-08-31 07:25:24.241609
id: feat-33-vcr
status: done
type: feat
updated: 2026-08-31 15:30:00
version: 1.1.0
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

- [x] ACC-001: Verifies REQ-001 -- `Verifies` (`vcr/models/v1/body.py`) is
  implemented exactly per the persisted class sketch (mandatory `value`
  regex-checked against `_VERIFIES_PATTERN`, mandatory `notes`, optional
  `comment`) and unit-tested end to end, including full-document
  round-trips, in `tests/vcr/models/v1/test_body.py`/`test_parser.py`.
- [x] ACC-002: Verifies REQ-002 -- `Coverage`'s closed
  `full`/`partial`/`none` vocabulary is implemented and unit-tested in
  `tests/vcr/models/v1/test_body.py`.
- [x] ACC-003: Verifies REQ-003 -- the `### AC-NNN (Method): ...` heading
  regex, closed DTAIS vocabulary (all 5 words), and the duplicate-`AC-NNN`-
  number `model_validator` are implemented in
  `vcr/models/v1/body.py`/`document.py` and unit-tested in
  `tests/vcr/models/v1/test_body.py`.
- [x] ACC-004: Verifies REQ-004 -- `VcrFrontmatter`'s closed
  `draft`/`progress`/`complete`/`approved` status vocabulary is
  implemented in `vcr/models/v1/frontmatter.py` and unit-tested in
  `tests/vcr/models/v1/test_frontmatter.py`.
- [x] ACC-005: Verifies REQ-005 -- the full domain now exists end to end:
  `vcr/models/v1/`, 8 tools (`vcr/tools/`), 3 resources (`vcr/resources/`),
  2 prompts (`vcr/prompts/`), generic `update`/`set_status` dispatch
  (`type="vcr"` in `general/tools/`), packaged data (`vcr/data/`), and
  cross-cutting registration (`server.py`, `AGENTS.md`, `README.md`,
  `.pre-commit-config.yaml`), all covered by `tests/vcr/` (models, tools,
  resources, prompts) plus the new `vcr` cases in
  `tests/general/tools/test_update.py`/`test_set_status.py`; the full
  suite passes (2452 tests, `OK`).
- [x] ACC-006: Verifies REQ-006 -- `specmgr://dtais` exists
  (`general/resources/dtais.py`), is registered in
  `general/resources/__init__.py` and `server.py`'s docstring, is
  documented in `docs/MCP.md` (confirmed in the generated output), and its
  content (`general/data/general_dtais.md`) matches the persisted Design
  Notes sketch, with `tests/general/resources/test_dtais.py` confirming
  every documented method word round-trips through
  `AcceptanceCriterion.from_text`.

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

- [x] Task 1.1: `vcr/models/v1/frontmatter.py` (`VcrFrontmatter`, closed
  `status` vocabulary).
- [x] Task 1.2: `vcr/models/v1/body.py` (`Verifies`, `Coverage`,
  `AcceptanceCriterion`/`AcceptanceCriteria`, `MoreInformation`, reused
  `Updates`).
- [x] Task 1.3: `vcr/models/v1/document.py`, `parser.py`, `summary.py`,
  `_util.py`, `__init__.py`.
- [x] Task 1.4: Unit tests for every model class and the parser.

#### Phase 2: Tools

- [x] Task 2.1: `create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr` (with
  `raw` param), `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub,
  `validate_vcr`.
- [x] Task 2.2: Generic `update`/`set_status` dispatch entries
  (`type="vcr"`) in `general/tools/`.

#### Phase 3: Resources and prompts

- [x] Task 3.1: `specmgr://vcr/schema`, `.../example`, `.../template`
  resources.
- [x] Task 3.2: `create_vcr`/`update_vcr` prompts.
- [x] Task 3.3: `general/data/general_dtais.md` content (fill in the
  draft outline persisted in Design Notes), `general/resources/dtais.py`
  (`specmgr://dtais`), registered in `general/resources/__init__.py`;
  unit tests.

#### Phase 4: Cross-cutting registration

- [x] Task 4.1: `server.py` import line.
- [x] Task 4.2: `AGENTS.md` Status section bullet (mirroring the
  `sop`/`feat` bullets).
- [x] Task 4.3: `README.md`, CI/pre-commit updates as needed.
- [x] Task 4.4: `specmgr docs`/`specmgr adr-toc` regeneration, full test
  suite, ruff/vulture gates.

## Progress

### Current Status

**As of 2026-08-31 (latest)**: Feature complete end to end. Phase 4
(Cross-cutting registration) wired `vcr/__init__.py` (now imports
`prompts`/`resources`/`tools`, mirroring `dec/__init__.py` exactly),
added `vcr` to `server.py`'s bottom import line and its full module
docstring (resources, the "no `{id}`/no `list`" paragraph, tools,
prompts, and the closing domain-enumeration paragraph -- all
domain-count language bumped from nine/ten to ten/eleven where it now
includes `vcr`), added a new `vcr/` bullet to `AGENTS.md`'s Status
section (positioned after `feat/`, before `general/`, mirroring `dec/`'s
shape) plus every other domain-enumeration spot in that file (`general/`'s
own resource list gains `specmgr://dtais`; the "still missing"
`validate_*`/`delete_*` lists gain `validate_vcr`/`delete_vcr`; the
tools/resources/prompts registration summary and the MCP-server-import
summary both gain `vcr`), added "Verification Case Record (VCR)" to root
`README.md`'s artifact list (alphabetically last, after "Use Case (UC)"),
added a `specmgr-schema-vcr-package` pre-commit hook (mirroring
`specmgr-schema-feat-package`) and inserted `vcr/models/v1` into every one
of the 10 existing `files:` regexes (the shared `specmgr-schema` hook plus
9 per-package hooks) and the `specmgr-schema` hook's own description, and
added a `CHANGELOG.md` `[Unreleased]` entry ("Twelfth domain feature").
Regenerated `docs/GENERATED.md`, `docs/api/`, `docs/MCP.md`,
`docs/adr/README.md` (no change -- confirmed empty diff, as expected since
this feature never touches `docs/adr/`), every `docs/*_schema.json`, and
the packaged `vcr/data/vcr_schema.json` copy -- each regeneration command
was run a second time afterward and confirmed stable (`unchanged`/
identical output, no further drift). Manually confirmed in the generated
`docs/MCP.md` that all 8 VCR tools, all 3 VCR resources, both VCR prompts,
and the standalone `specmgr://dtais` resource appear with correct
descriptions. Quality gate green: `ruff format --check` (1386 files
already formatted), `ruff check` (all checks passed), `vulture` (no
output, no new whitelist entries needed), and the full `unittest` suite
(2452 tests, `OK`, unchanged from Phase 3 -- Phase 4 added no new test
files, only cross-cutting registration/docs). All ACC-001..006 confirmed
and checked off. This feature is now fully implemented end to end,
matching every other already-shipped domain's registration shape.

**As of 2026-08-31 (earlier)**: Phase 3 (Resources and prompts) complete.
`vcr/resources/` (`vcr_schema`/`vcr_example`/`vcr_template`, mirroring
`dec/resources/` file-for-file) and `vcr/prompts/` (`create_vcr`/
`update_vcr`, mirroring `dec/prompts/` file-for-file, plus their packaged
`vcr_create_instructions.md`/`vcr_update_instructions.md`) now exist.
`commands/schema.py` gained `generate_vcr_schema`/a `"vcr"` `_GENERATORS`
entry, and both `docs/vcr_schema.json` and the packaged
`vcr/data/vcr_schema.json` copy are generated and drift-free. The
cross-cutting `specmgr://dtais` resource (REQ-006) now exists:
`general/data/general_dtais.md` (the five DTAIS method words, a "When to
apply each method" section, and a "Relationship to `## Coverage`"
section illustrating the `partial`-coverage/pending-`Special`-
certification scenario from `example.md`), `general/resources/dtais.py`,
registered in `general/resources/__init__.py`. 52 new unit tests
(`tests/vcr/resources/`, `tests/vcr/prompts/`,
`tests/general/resources/test_dtais.py`, bringing the full suite from
2400 to 2452). Neither `server.py` nor `vcr/__init__.py` was touched --
`vcr/__init__.py` deliberately still does not import
`tools`/`resources`/`prompts` (that domain-registration wiring is Phase
4's job).

**As of 2026-08-31 (earlier)**: Phase 2 (Tools) complete. `vcr/tools/` now exists in
full, mirroring `dec/tools/` file-for-file: `_paths.py`/`_lock.py`/`_io.py`/
`_write.py` plumbing, and the 8 standard tools (`create_vcr`, `parse_vcr`,
`get_vcr` with `raw`, `get_vcr_example`, `get_vcr_template`, `list_vcr`,
`delete_vcr` stub, `validate_vcr`). Packaged data
(`vcr/data/vcr_example.md`/`vcr_template.md`, copied byte-for-byte from
this feature's finalized planning drafts) backs `get_vcr_example`/
`get_vcr_template`, declared in `pyproject.toml`'s
`[tool.setuptools.package-data]`. The generic `update`/`set_status` tools
in `general/tools/` now dispatch `type="vcr"` to `_update_vcr`/
`_set_status_vcr`, ported verbatim from `_update_dec`/`_set_status_dec`.
64 new unit tests (`tests/vcr/tools/`, bringing the full suite from 2336 to
2400) plus new `vcr` cases in
`tests/general/tools/test_update.py`/`test_set_status.py` cover the full
create->get->list->update->set_status->validate->delete lifecycle. Neither
`server.py` nor `vcr/__init__.py` was touched -- `vcr/__init__.py`
deliberately still does not import `tools`/`resources`/`prompts` (that
domain-registration wiring, plus `vcr/resources`/`vcr/prompts` themselves,
is Phase 3/4's job). One noted, non-blocking fragility: running
`tests/vcr/tools/` in isolation (before Phase 4 wires `vcr/__init__.py`'s
own `tools` import) can hit a circular-import `ImportError` in
`test__io.py`/similar files that import `vcr.models.v1` directly, since
`general.tools.update`/`set_status` now import `vcr.tools._io` etc. at
module load time and `vcr.tools`'s own `__init__.py` eagerly imports
`list_vcr` (which needs `VcrSummary`) -- resolved automatically once Phase
4 makes `vcr/__init__.py` bootstrap `tools` first (mirroring every other
domain's own `__init__.py`); the full repo-wide test suite (the specified
quality gate) is unaffected and passes cleanly (2400 tests, `OK`).

**As of 2026-08-31 (earlier)**: Phase 1 (Models and parser) complete. `vcr/models/v1/`
now exists in full: `frontmatter.py` (`VcrFrontmatter`, closed
draft/progress/complete/approved status set), `body.py` (`Verifies`,
`Coverage`, `TestSteps`, `AcceptanceCriterion`/`AcceptanceCriteria`,
`MoreInformation`, `UpdateEntry`/`Updates`, and the top-level `Vcr` H1
container with its duplicate-AC-number `model_validator`), plus
`document.py`/`parser.py`/`summary.py`/`_util.py`/`__init__.py` mirroring
`dec/models/v1`'s shape exactly. 103 new unit tests (`tests/vcr/models/v1/`)
cover every heading alias, `Verifies`'/`Coverage`'s regex-enforced values,
the `AC-NNN (Method): ...` heading regex and computed `number`/`method`
fields, `TestSteps` presence/absence, mandatory/optional-section behavior,
misordering, the duplicate-AC-number after-validator, and full-document
round-trips through `parse_vcr`. REQ-001..004 (and their corresponding
ACC-001..004 schema-level acceptance criteria) are now implemented and
unit-tested end to end; ACC checkboxes themselves are left for sign-off
per this feature's own discipline. No `vcr` tool/resource/prompt code
exists yet, and `vcr/__init__.py` deliberately stays empty (no
`tools`/`resources`/`prompts` import) -- that domain-registration wiring
is Phase 2/3/4's job.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31T15:30:00.000000 — Phase 4 complete: cross-cutting registration; feature fully implemented end to end

Implemented Task 4.0 (the implicit prerequisite): wired `vcr/__init__.py`
to `from . import prompts, resources, tools`, mirroring `dec/__init__.py`
file-for-file (module docstring adapted to VCR's actual schema/tools/
resources/prompts, including the `specmgr://dtais` cross-reference). This
resolves the non-blocking circular-import fragility noted in the Phase
2/3 Updates entries (`tests/vcr/tools/`/`tests/vcr/resources/`/
`tests/vcr/prompts/` now import cleanly in isolation too, not just as
part of the full suite).

Implemented Task 4.1: added `vcr` to `server.py`'s bottom import line
(alphabetical position, after `uc`) and updated its module docstring in
full -- three new `specmgr://vcr/schema`/`.../example`/`.../template`
resource lines (after `feat`'s, before `iso25010`), a new
`specmgr://dtais` resource line (between `feat/template` and
`iso25010`), a new VCR sentence in the "no `{id}`/no `list`" paragraph, a
new "Verification case record tools (`vcr/tools/`)" paragraph (before
"General tools"), a new "Verification case record prompts
(`vcr/prompts/`)" paragraph (before "General prompts"), the `general`
tools paragraph's domain-count language bumped (`update`: nine -> ten
whole-body domains, list gains `vcr`; `set_status`: "all ten domains" ->
"all eleven domains", list gains `vcr` right before `adr`), and the
closing "Modules are grouped domain-first" paragraph's three
domain-enumeration spots (the domain list, the import-list sentence, and
the tools/resources/prompts registration sentence) all gain `vcr`. Re-read
the entire docstring end to end afterward to confirm every VCR mention is
internally consistent with what Phases 1-3 actually built.

Implemented Task 4.2: added a new `vcr/` bullet to `AGENTS.md`'s Status
section, positioned after `feat/` and before `general/` (mirroring
`dec/`'s bullet shape/depth), describing VCR's actual schema (`##
Verifies` single-value cross-reference, `## Coverage` closed vocabulary,
`## Acceptance Criteria` DTAIS-classified `### AC-NNN` entries), its 8
tools, 3 resources, 2 prompts, generic `update`/`set_status` dispatch, and
the cross-cutting `specmgr://dtais` resource. Also updated every other
domain-enumeration spot in the same file: the `general/` bullet's own
resource list (`specmgr://version`, `specmgr://iso25010` -> gains
`specmgr://dtais` with a one-line description), the `general/tools/`
`update` sub-bullet's domain count/list (nine -> ten, gains `vcr`), the
`set_status` sub-bullet's domain count (ten -> eleven), the "The nine
`get_<d>` tools" sentence (-> "The ten `get_<d>` tools"), the "Still
genuinely missing" bullets (`validate_vcr` added to the `validate_*` list,
`delete_vcr` added to the `delete_*` list), the "each register `tools`,
`resources`, and `prompts`" summary bullet (gains `vcr`), and the MCP
server section's "imports every domain package" sentence (gains `vcr`).
Did not touch the "Models location" paragraph (VCR has no exception to
document) or any unrelated `.specmgr/feat/` references.

Implemented Task 4.3: added "Verification Case Record (VCR)" to root
`README.md`'s artifact list (alphabetically last, after "Use Case (UC)"),
following the same precedent `feat-31-feature`'s own Phase 5 used to add
"Feature (FEAT)" to that same list -- confirmed the "Environment
Variables" section itself needed no change (it is already fully generic,
`SPECMGR_DOCS_DIR`-based, with no per-domain enumeration). Updated
`.pre-commit-config.yaml`: inserted `vcr/models/v1` into all 10 existing
occurrences of the shared `files:` regex (the `specmgr-schema` hook plus
the 9 per-package `specmgr-schema-<domain>-package` hooks), right after
`uc/models/v2` and before the always-last `models/md`, added a new
`specmgr-schema-vcr-package` hook block (appended after
`specmgr-schema-feat-package`, VCR-ified: `vcr/data/vcr_schema.json`,
`specmgr://vcr/schema`, `docs/vcr_schema.json`, `--type vcr
--output-dir src/biz/dfch/specmgr/vcr/data`) with the same updated regex,
and updated the `specmgr-schema` hook's own description text to list
`vcr` last. Added a `CHANGELOG.md` `[Unreleased]` `### Added` entry
("Twelfth domain feature (VCR/Verification Case Record tooling)"),
mirroring the FEAT entry's structure/depth (models, tools, resources +
prompts, the cross-cutting `specmgr://dtais` resource, cross-cutting
registration, test coverage).

Implemented Task 4.4: ran `specmgr docs`, `specmgr mcp-docs`,
`specmgr adr-toc`, `specmgr schema`, and
`specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`,
each exactly twice -- the first run wrote real changes (`docs/GENERATED.md`,
`docs/api/README.md`, `docs/api/biz.dfch.specmgr.server.md`,
`docs/api/biz.dfch.specmgr.vcr.md`, `docs/MCP.md`, `docs/adr/README.md`
regenerated with no diff, every `docs/*_schema.json` and the packaged
`vcr/data/vcr_schema.json` copy reported "unchanged"), the second run
confirmed byte-identical output (`md5sum` comparison before/after for the
docs-generation commands; "unchanged"/no-diff for every schema and the
adr-toc command) -- no residual drift from this phase's own edits.
Manually read the generated `docs/MCP.md` and confirmed all 8 VCR tools
(`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`, `get_vcr_example`,
`get_vcr_template`, `delete_vcr`, `validate_vcr`), all 3 VCR resources
(`specmgr://vcr/schema`/`.../example`/`.../template`), both VCR prompts
(`create_vcr`, `update_vcr`), and the standalone `specmgr://dtais`
resource appear with sensible, accurate descriptions. Quality gate green:
`ruff format --check` (1386 files already formatted), `ruff check` (all
checks passed), `vulture src/ whitelist.py --min-confidence 60` (no
output, no new whitelist entries needed), and the full `unittest` suite
(2452 tests, `OK` -- unchanged from Phase 3's count, since Phase 4 added
no new test files, only cross-cutting registration/docs). Updated the
Task List's Phase 4 checkboxes, walked every ACC-001..006 item and marked
all six `[x]` with a concrete justification citing the specific test
file/resource/tool proving each, and updated Current Status to reflect
the feature is now fully implemented end to end. Bumped this README's own
frontmatter `status` from `planning` to `done` and `version` from `1.0.0`
to `1.1.0`.

#### 2026-08-31T14:00:00.000000 — Phase 3 complete: `vcr/resources/`, `vcr/prompts/`, and the cross-cutting `specmgr://dtais` resource implemented

Implemented Task 3.1 (`vcr/resources/`): `vcr_schema.py`/`vcr_example.py`/
`vcr_template.py`, mirroring `dec/resources/`'s three files exactly
(rename `Dec`/`dec` -> `Vcr`/`vcr`, same URIs
`specmgr://vcr/schema`/`.../example`/`.../template`, same
`read_packaged_text` plumbing), plus `vcr/resources/__init__.py`. The
schema resource needed generator plumbing first: added
`generate_vcr_schema()` to `commands/schema.py` (mirroring
`generate_dec_schema` exactly) and a `"vcr"` entry to `_GENERATORS`
(alphabetically last, after `"uc"`), then ran
`specmgr schema --type vcr` (writes `docs/vcr_schema.json`) and
`specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`
(writes the packaged copy `vcr/data/vcr_schema.json`) -- both exited 1
on first generation (new file) and 0 (unchanged) on every subsequent run,
confirmed once more at the very end of the phase.

Implemented Task 3.2 (`vcr/prompts/`): `create_vcr.py`/`update_vcr.py`,
mirroring `dec/prompts/create_dec.py`/`update_dec.py` exactly (same
`string.Template`/`$topic`/`$id`/`$instructions` substitution shape,
`raw=True` for `update_vcr`'s line-range line numbers, narration-only
contract -- never calls `TodoWrite`/`question`/`list_vcr`/`create_vcr`/
`get_vcr`/`update`/`set_status` itself), plus `vcr/prompts/__init__.py`.
Their packaged instructions
(`vcr/data/vcr_create_instructions.md`/`vcr_update_instructions.md`)
adapt `dec`'s exact structure/tone to VCR's own schema (`## Verifies` ->
`## Coverage` -> `## Acceptance Criteria` -> `## More Information` ->
`## Updates` section recap, the closed DTAIS method vocabulary spelled
out verbatim, VCR's own four-value `draft`/`progress`/`complete`/
`approved` status set instead of DEC's six-value set, and references to
the new `specmgr://dtais` resource for method-word guidance) -- including
DEC's own step-0 "check `list_vcr` for a near-duplicate first" convention
and the same tool-call-sequence ending in `create_vcr(content)`/optional
`validate_vcr(content, full=False)`.

Implemented Task 3.3 (the cross-cutting `specmgr://dtais` resource,
REQ-006): `general/data/general_dtais.md` filled in every placeholder
from the Design Notes' persisted draft outline -- a closed-vocabulary
bullet list of the five DTAIS words (verbatim, in the same order as
`vcr.models.v1.body`'s `_AC_HEADING_PATTERN` method group, confirmed by a
new test), a "## When to apply each method" section with concrete
per-method guidance (informed by well-established V&V domain knowledge:
`Demonstration` for observable behavior without a quantitative
threshold, `Test` for a quantitative/measured threshold, `Analysis` for
calculation/modeling/simulation or pre-existence-of-system verification,
`Inspection` for artifact/source examination without operating the
system, and this feature's own addition `Special` for external
certification/compliance/supplier-conformance sign-off), and a
"## Relationship to `## Coverage`" section explaining that `## Coverage`
is a roll-up of every acceptance criterion's verification status (not an
independent field), concretely illustrated with `example.md`'s own
AC-004-pending-`Special`-certification `partial`-coverage scenario.
`general/resources/dtais.py` copies the plan's persisted sketch verbatim
(only the `..tools`/`...server` relative-import order was corrected to
match this codebase's actual isort convention, confirmed against
`general/resources/iso25010.py`'s own ordering), and
`general/resources/__init__.py` now imports/exports `dtais` alongside
`iso25010`/`version` (alphabetical).

Added 52 new unit tests across `tests/vcr/resources/`
(`test_vcr_schema.py`/`test_vcr_example.py`/`test_vcr_template.py`,
mirroring `tests/dec/resources/`'s three files), `tests/vcr/prompts/`
(`test_create_vcr.py`/`test_update_vcr.py`, mirroring
`tests/dec/prompts/`'s two files), and
`tests/general/resources/test_dtais.py` (mirroring
`tests/rsk/resources/test_tara.py`'s structure: a regex asserting the
five documented method-word bullets exactly match the model's closed
DTAIS set in order, a per-word round-trip through
`AcceptanceCriterion.from_text` confirming every documented word is
genuinely accepted end to end, and a rejected-word case using
`"Certification"` -- VCR's own retired 5th-method name -- which raises
`AssertionError` (an `AcceptanceCriterion` alias mismatch, not
`pydantic.ValidationError`, unlike RSK's `Strategy`-based rejected-word
test) since `AcceptanceCriterion` is a regex-`@alias`-matched heading
class, not a `field_validator`-checked value). Quality gate green: `ruff
format --check`, `ruff check`, `vulture` (no new whitelist entries
needed), and the full `unittest` suite (2452 tests, `OK`, up from 2400)
all pass. Did not touch `server.py`, `AGENTS.md`, top-level `README.md`,
or `.pre-commit-config.yaml` -- all reserved for Phase 4; `vcr/__init__.py`
also stays untouched (still no `tools`/`resources`/`prompts` import), so
the same non-blocking circular-import fragility noted in the Phase 2
Updates entry (isolated `vcr.models.v1` imports before `general` has
fully loaded) still applies identically to the new `vcr/resources`/
`vcr/prompts` modules in isolation -- unaffected in the full repo-wide
suite, which is the specified quality gate.

#### 2026-08-31T12:30:00.000000 — Phase 2 complete: `vcr/tools/` implemented, generic `update`/`set_status` dispatch wired for `type="vcr"`

Implemented the full `vcr/tools/` package, mirroring `dec/tools/` file-for-
file: `_paths.py` (`VCR_TYPE_NAME`, `VcrNotFoundError`, `vcr_base_dir`/
`ensure_vcr_base_dir`/`iter_vcr_paths`/`find_vcr_path`, built on the shared
`general.tools._doc_paths` helpers, not a new dependency), `_lock.py`
(`vcr_lock`), `_io.py` (`read_vcr`/`load_by_id`), `_write.py`
(`write_vcr_file`), and the 8 standard `@mcp.tool()` wrappers: `create_vcr`
(fresh `uuid.uuid4()` id, `type="vcr"`, `status="draft"` always on create,
filename `vcr-{id}-{slug}.md`), `parse_vcr`, `get_vcr` (with `raw: bool =
False`), `get_vcr_example`/`get_vcr_template` (reading new packaged data),
`list_vcr` (paged from day one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13),
`delete_vcr` (stub, always `NotImplementedError`), and `validate_vcr`
(disk-free/id-free dry run, `full: bool = False`). Copied the
already-finalized `example.md`/`template.md` planning drafts byte-for-byte
into `vcr/data/vcr_example.md`/`vcr_template.md`
(confirmed via `diff`: zero output) and declared the new
`"biz.dfch.specmgr.vcr"` package-data entry in `pyproject.toml`, inserted
after `"biz.dfch.specmgr.uc"` and before `"biz.dfch.specmgr.general"`,
matching every other domain's two-pattern (`data/*.md`, `data/*.json`)
shape even though no `vcr_schema.json` exists yet (Phase 3's job). Added
`vcr` as a tenth entry to the generic `update` tool's `_ADAPTERS` (new
`_update_vcr`, ported verbatim from `_update_dec`, appended last after
`feat`) and as an eleventh entry to `set_status`'s `_ADAPTERS` (new
`_set_status_vcr`, ported verbatim from `_set_status_dec` including the
`assert superseded_by is None` guard, inserted right after `feat` and
before the always-last `adr`), updating both tools' `Literal[...]`
parameter types, module/tool docstrings, and domain-count language
("nine"/"ten" -> "ten"/"eleven" as appropriate) throughout. Added 64 new
unit tests under `tests/vcr/tools/` (mirroring `tests/dec/tools/`'s 13
files file-for-file, using a minimal valid VCR body fixture: `## Verifies`
+ `## Coverage` + one `### AC-001 (Test): ...` entry, matching Phase 1's
own `test_parser.py` fixture shape) plus new `vcr` cases appended to the
table-driven `_CASES` lists in `tests/general/tools/test_update.py` (a
genuine duplicate-`### AC-001` `pydantic.ValidationError` field-error case,
mirroring DEC's own duplicate-`### Option` case) and
`test_set_status.py` (`valid_status="progress"`, `invalid_status="accepted"`
-- confirmed against `VcrFrontmatter`'s actual closed
`draft`/`progress`/`complete`/`approved` set before use), and updated both
files' registration/domain-count docstring language and the
`type` enum assertion in `test_update.py`'s
`test_update_registered_with_type_enum_and_optional_range`. Did not touch
`server.py`, did not create `vcr/resources`/`vcr/prompts`, and did not add
`vcr` to `server.py`'s import line -- all reserved for Phase 3/4;
`vcr/__init__.py` also stays untouched (still no `tools`/`resources`/
`prompts` import). Noted one non-blocking fragility for a future
implementer: since `vcr/__init__.py` does not yet bootstrap `vcr.tools`
(unlike every other already-registered domain's own `__init__.py`, which
bootstraps its `tools` package before anything else can reach its models
mid-import), running `tests/vcr/tools/` in isolation can hit a circular
import `ImportError` in files that import `vcr.models.v1` directly before
anything else has loaded `general.tools` (which now imports
`vcr.tools._io` et al., transitively re-entering `vcr.models.v1` while
it's still mid-import) -- resolved automatically once Phase 4 wires
`vcr/__init__.py` to import `tools`/`resources`/`prompts` the same way
`dec/__init__.py` already does; the full repo-wide suite (the specified
quality gate) is unaffected.
Quality gate green: `ruff format --check`, `ruff check`, `vulture` (no new
whitelist entries needed), and the full `unittest` suite (2400 tests,
`OK`, up from 2336) all pass.

#### 2026-08-31T11:15:00.000000 — Phase 1 correction: `AcceptanceCriterion.description` added; `example.md`/`template.md` now empirically validate end to end

Fixed a real specification error (not a genuine open design question) in
the schema landed by the previous Phase 1 entry: `AcceptanceCriterion` had
no field for the free-form descriptive paragraph that already-finalized
`example.md` demonstrates under 3 of its 4 `### AC-NNN (Method): ...`
headings (AC-001/002/004 each carry prose before/without `#### Test
Steps`; AC-003 has none). Added `description: MarkdownParagraph | None =
None` to `AcceptanceCriterion` in `vcr/models/v1/body.py`, declared before
`test_steps` (document order: heading -> optional description -> optional
`Test Steps`), both independently optional. While empirically re-validating
via a throwaway `/tmp` scratch script (per instruction) that called
`parse_vcr`/`Vcr.from_text` directly against `example.md`'s and
`template.md`'s actual body text, surfaced one more, closely-related gap
in scope of the same fix: `## Updates` in both drafts carries a permanent
leading "newest first" anchor `<!-- ... -->` comment (already noted as a
first-class, non-authoring-guidance structural anchor in this feature's
own Design Notes and clean-example-convention discussion), but `Updates`
was declared as a plain `MarkdownSection2` (DEC's own shape, whose
`dec_example.md` carries no such comment) instead of
`MarkdownSection2WithComment`. Changed `Updates` to
`MarkdownSection2WithComment` (mirroring `feat`'s own
`Updates(MarkdownSection3WithComment)` precedent) so this validates too.
After both fixes, the scratch script confirmed **both** `example.md` and
`template.md` now parse successfully end to end via `parse_vcr` (every
frontmatter field, `Verifies`, `Coverage`, all `AcceptanceCriterion`
entries' `description`/`test_steps` combinations, `More Information`, and
`Updates` with its comment) -- the only discrepancy from a byte-exact
round-trip is the pre-existing, already-documented `MarkdownListItem`
"tight numbered list renders as loose" quirk (unrelated to VCR, confirmed
via `difflib` diff: only blank lines inserted between numbered `Test
Steps` items), not a schema defect. The scratch script was deleted after
the run, never committed. Added 9 new `test_body.py` tests (all four
`description`/`test_steps` combinations plus `Updates`' leading comment)
and adjusted the reference-document fixtures in `test_body.py`/
`test_parser.py` to exercise AC-001 (both fields), AC-003 (description
only), and a new AC-004 (neither) -- mirroring `example.md`'s own shape --
plus the `Updates` comment. Quality gate re-run clean: `ruff format
--check`, `ruff check`, `vulture` (no new whitelist entries needed --
`description` is already a ubiquitous field/kwarg name used throughout the
codebase), and the full `unittest` suite (2336 tests, `OK`).

#### 2026-08-31T10:30:00.000000 — Phase 1 complete: `vcr/models/v1/` implemented and unit-tested

Implemented the full `vcr/models/v1/` schema and parser, mirroring `dec`'s
`models/v1` layout file-for-file (`frontmatter.py`, `body.py`,
`document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`, plus
`vcr/models/__init__.py` and an empty `vcr/__init__.py`). `VcrFrontmatter`
narrows `status` to the closed `draft`/`progress`/`complete`/`approved`
set (REQ-004). `body.py` implements `Verifies` verbatim from the Design
Notes' persisted class sketch (`MarkdownSection2WithComment`, regex-checked
`value`, mandatory `notes`), `Coverage` (RSK `Strategy`-style closed
3-value `full`/`partial`/`none` paragraph, REQ-002), `TestSteps` (`####
Test Steps`, a numbered procedure list, `min_length=1`), `AcceptanceCriterion`
(a regex-aliased `### AC-NNN (Method): <text>` heading with `number`/`method`
`@computed_field`s and an optional `test_steps` child), `AcceptanceCriteria`
(`>=1` entries), reused `MoreInformation`/`UpdateEntry`/`Updates` (DEC's
exact shape), and the top-level `Vcr` H1 container with a
`_validate_ac_numbers_unique` `model_validator` mirroring DEC's
`Decision._validate_option_numbers_unique` (mandatory `acceptance_criteria`,
so no `is not None` guard needed). `VcrSummary` is a plain `DocSummary`
subclass with no extra fields (DEC precedent, not RSK's enriched one).
Confirmed via a quick interactive sanity check before writing tests that
`AcceptanceCriterion` needed a different computed-field extraction
mechanic than DEC's `Option`/RSK's `Probability`/`Impact`: those are *leaf*
sections (zero other declared fields), so their own `.text` returns the
*complete* extent (heading marker + body) verbatim; `AcceptanceCriterion`
declares one other field (`test_steps`), making it *composite*, so its
`.text` returns only the heading's own inline content (marker already
stripped) -- the `number`/`method` regex therefore matches against
`self.text` directly, not `self.text.splitlines()[0]`. A consequence: an
`AcceptanceCriterion`'s body may contain nothing besides an optional
`#### Test Steps` -- there is no separate free-form description/notes
paragraph field, matching UC's `Extension`/`SubVariation` precedent
(condition/title info lives entirely in the heading, the declared field(s)
are the *only* body content) rather than DEC's leaf `Option` (which
absorbs arbitrary body prose since it declares no other field at all).
This means the already-finalized `example.md`'s AC-001/002/004 descriptive
paragraphs (prose directly under the heading, before/without `Test Steps`)
do **not** validate against this Phase 1 schema as literally written --
a known, deliberate gap flagged for Phase 3 (packaging `example.md`/
`template.md` as real package data) to resolve, either by revising
`example.md` or by reconsidering the schema then; Task 0.1 already noted
neither draft had been validated against `models/md` yet, and this phase's
own test fixtures (inline `textwrap.dedent`, per instructions) do not
depend on either draft file. Wrote 103 new tests across
`tests/vcr/models/v1/test_frontmatter.py`/`test_body.py`/`test_parser.py`,
covering every heading alias (including all 5 DTAIS method words and the
`AC-NNN` 3-digit/gap-allowed/duplicate-rejected number shape), `Verifies`'/
`Coverage`'s regex value validation, `TestSteps` presence/absence,
mandatory-vs-optional section behavior, misordering, and full-document
round-trips through `parse_vcr`. Added a `whitelist.py` entry
(`_validate_ac_numbers_unique`, `verifies`, `test_steps`) for three genuine
Pydantic-framework vulture false positives (mirroring the existing `dec
(feat-21 Phase 1)`/`_validate_option_numbers_unique` precedent exactly).
Quality gate green: `ruff format --check`, `ruff check`, `vulture` (with
the new whitelist entries), and the full `unittest` suite (2331 tests,
`OK`) all pass. Did not touch `server.py`, did not create
`vcr/tools`/`vcr/resources`/`vcr/prompts`, and `vcr/__init__.py` stays
empty (module docstring only, no `tools`/`resources`/`prompts` import) --
all reserved for Phase 2/3/4.

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

#### 2026-08-31T11:15:00.000000 — Corrected: `AcceptanceCriterion.description` added; `Updates` needs `WithComment`

Supersedes the decision immediately below (2026-08-31T10:30:00, "no
free-form description field"), which was a genuine specification error,
not a resolved design question: the plan's own Phase 0 discipline requires
the schema to match `example.md`'s empirically-validated content, and that
draft demonstrates a descriptive paragraph under 3 of its 4
`### AC-NNN (Method): ...` headings. Added `description: MarkdownParagraph
| None = None` to `AcceptanceCriterion`, declared before `test_steps`
(document order), both independently optional -- the composite-vs-leaf
reasoning in the superseded entry below still holds (that's *why* a
declared field, not absorbed body prose, was the right fix), it was just
missing the field itself. Also changed `Updates` from a plain
`MarkdownSection2` (DEC's shape) to `MarkdownSection2WithComment`
(`feat`'s shape) after the same empirical re-validation surfaced that
`example.md`/`template.md`'s permanent "newest first" anchor comment under
`## Updates` had no schema support either. Both `example.md` and
`template.md` now parse successfully end to end via `parse_vcr`,
confirmed via a throwaway, uncommitted `/tmp` scratch script (deleted
after the run).

#### 2026-08-31T10:30:00.000000 — `AcceptanceCriterion` carries no free-form description field; body is heading + optional `Test Steps` only

Phase 1's exact schema (declared `test_steps: TestSteps | None` plus
computed `number`/`method`) makes `AcceptanceCriterion` a *composite*
`MarkdownSection3` (it has one other declared field), unlike DEC's `Option`/
RSK's `Probability`/`Impact`, which are *leaf* sections with zero other
declared fields. A composite section's body must be fully consumed by its
declared field(s) (`MarkdownStr.from_text` asserts no text is left over),
so an `AcceptanceCriterion` with only `test_steps` declared cannot also
carry a free-form descriptive paragraph the way DEC's leaf `Option`
absorbs arbitrary body prose verbatim. Implemented per the phase's literal
instructions (no description/notes field), matching UC's `Extension`/
`SubVariation` precedent (heading carries all title/condition info, the
declared field(s) are the *only* body content) instead of DEC's `Option`.
Consequence: the already-finalized `example.md`'s AC-001/002/004
descriptive paragraphs do not validate against this schema as written --
left as a known, flagged gap for Phase 3 (packaging) to resolve (either by
revising `example.md`, or by adding a description field then), rather than
guessed at now, since Phase 1's instructions were explicit and this
phase's own tests deliberately do not depend on either draft file.

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
