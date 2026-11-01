---
created: '2026-08-31 07:25:24.241Z'
id: feat-33-vcr
status: done
type: feat
updated: '2026-10-07T06:21:40.934Z'
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

- REQ-001: (decided) `## Verifies` references **exactly one** REQ or UC -- modeled as a `Verifies(MarkdownSection2WithComment)` with a single mandatory `value: MarkdownParagraph` line ("`REQ|UC <uuid>: <title>`", `field_validator`-regex-checked) plus a **mandatory** `notes: MarkdownParagraph` paraphrase (in fixed declaration order, mirroring RSK's `Assessment.probability`/`.impact` two-mandatory-fields idiom) and an optional leading HTML `comment`. **Not** a bullet list -- no cardinality `model_validator` is needed, since a single-value field is structurally incapable of holding more than one reference; see the "single-value-field over list-of-one" decision in Design Notes and Decisions Made below (this supersedes the original `MarkdownListItemWithNotes` design). Resolves the previously-open "id is a real UUID, not a human code" gap shared with `sysrs`'s own REQ-003.
- REQ-002: (decided) `## Coverage` is a closed vocabulary paragraph -- `full` / `partial` / `none` -- mirroring `rsk`'s `## Strategy` pattern (`MarkdownParagraph` + `field_validator` regex).
- REQ-003: (decided) `## Acceptance Criteria` holds >= 1 repeating `### AC-NNN (Method): <criterion text>` sub-sections (3-digit zero-padded number, e.g. `AC-001`), DEC-Option-style (numbered H3, no per-item mutation tools). `Method` is parsed from the heading itself via regex (RSK `Probability`/`Impact` idiom) and is a closed **DTAIS** vocabulary: Demonstration, Test, Analysis, Inspection, Special. Each AC may optionally carry a `#### Test Steps` numbered procedure list. A `model_validator` rejects duplicate `AC-NNN` numbers.
- REQ-004: (decided) Frontmatter `status` is a closed, hyphen-free four-value lifecycle -- `draft` / `progress` / `complete` / `approved` -- grounded in INCOSE's Guide for Writing Requirements, Attribute A26 ("Need or Requirement Verification Status": "not started, in work, complete, and approved"; see `.specmgr/feat/feat-32-sysrs/incose-guide-writing-requirements-2019.md:1225`), reworded to this repo's hyphen-free style. No separate pass/fail/waived outcome field -- `## Coverage` is the only outcome signal.
- REQ-005: (not started) Everything else a from-scratch domain needs, patterned on `sop`'s precedent (`.specmgr/feat/feat-30-sop/README.md`): `vcr/models/v1/` schema + parser, 8 standard tools (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr(raw=False)`, `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub, `validate_vcr`), 3 resources (`schema`/`example`/`template`, no `/{id}`, no `/list`), prompts (`create_vcr`/`update_vcr`), generic `update`/`set_status` dispatch entries, packaged data, cross-cutting registration (`server.py`/`AGENTS.md`/`README.md`/CI/pre-commit).
- REQ-006: (decided) A cross-cutting `specmgr://dtais` resource explains the DTAIS verification-method vocabulary (what each of the 5 methods means and when/how to apply it), mirroring `sop`'s planned `specmgr://rasci` resource (`.specmgr/feat/feat-30-sop/README.md` REQ-011) and `rsk`'s existing `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` resources: a thin `general/resources/dtais.py` returning `read_packaged_text("general", "dtais")` verbatim, backed by `general/data/general_dtais.md`. Flat top-level URI (like `specmgr://iso25010`/the planned `specmgr://rasci`), not `specmgr://vcr/dtais`, since the vocabulary is domain-knowledge that other domains (e.g. `sysrs`) may want to reference too, not owned by `vcr`'s own schema. See the persisted sketch in Design Notes.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 -- `Verifies` (`vcr/models/v1/body.py`) is implemented exactly per the persisted class sketch (mandatory `value` regex-checked against `_VERIFIES_PATTERN`, mandatory `notes`, optional `comment`) and unit-tested end to end, including full-document round-trips, in `tests/vcr/models/v1/test_body.py`/`test_parser.py`.
- [x] ACC-002: Verifies REQ-002 -- `Coverage`'s closed `full`/`partial`/`none` vocabulary is implemented and unit-tested in `tests/vcr/models/v1/test_body.py`.
- [x] ACC-003: Verifies REQ-003 -- the `### AC-NNN (Method): ...` heading regex, closed DTAIS vocabulary (all 5 words), and the duplicate-`AC-NNN`- number `model_validator` are implemented in `vcr/models/v1/body.py`/`document.py` and unit-tested in `tests/vcr/models/v1/test_body.py`.
- [x] ACC-004: Verifies REQ-004 -- `VcrFrontmatter`'s closed `draft`/`progress`/`complete`/`approved` status vocabulary is implemented in `vcr/models/v1/frontmatter.py` and unit-tested in `tests/vcr/models/v1/test_frontmatter.py`.
- [x] ACC-005: Verifies REQ-005 -- the full domain now exists end to end: `vcr/models/v1/`, 8 tools (`vcr/tools/`), 3 resources (`vcr/resources/`), 2 prompts (`vcr/prompts/`), generic `update`/`set_status` dispatch (`type="vcr"` in `general/tools/`), packaged data (`vcr/data/`), and cross-cutting registration (`server.py`, `AGENTS.md`, `README.md`, `.pre-commit-config.yaml`), all covered by `tests/vcr/` (models, tools, resources, prompts) plus the new `vcr` cases in `tests/general/tools/test_update.py`/`test_set_status.py`; the full suite passes (2452 tests, `OK`).
- [x] ACC-006: Verifies REQ-006 -- `specmgr://dtais` exists (`general/resources/dtais.py`), is registered in `general/resources/__init__.py` and `server.py`'s docstring, is documented in `docs/MCP.md` (confirmed in the generated output), and its content (`general/data/general_dtais.md`) matches the persisted Design Notes sketch, with `tests/general/resources/test_dtais.py` confirming every documented method word round-trips through `AcceptanceCriterion.from_text`.

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

#### Phase 100: Empirical schema validation

- [x] Task 100.100: Draft `example.md`/`template.md` bodies exercising every section and validate against the `models/md` engine (mirroring `sop`'s/ `sysrs`'s discipline) before writing any Pydantic model code. - [x] `example.md` finalized as the **sole** draft (earlier `example.v2.md`/`example.v3.md` iterations merged into it and deleted): real frontmatter, single-value-field `## Verifies` (see Design Notes' `Verifies` class sketch), DTAIS/`Special` terminology, and every instructional/enforcement comment removed per the clean-example convention discovered in `dec`/`uc`/`req`'s shipped `*_example.md` files (see Design Notes) -- the only comment kept is `## Updates`' permanent "newest first" anchor, plus one new filled annotation exercising `Verifies`' optional `comment` field. Still not yet validated against `models/md`, since no `vcr` model code exists yet; see Task 1.1-1.3. - [x] `template.md` drafted (blind-text placeholder, mirroring `dec`/`rsk`/`prb`/`req`/`uc`'s shipped `*_template.md` shape): exercises the same section shape as `example.md` (frontmatter, `## Verifies` with optional `comment` + mandatory `value` + mandatory `notes`, `## Coverage`, `## Acceptance Criteria` with two `### AC-NNN (Method): ...` entries -- one with `#### Test Steps`, one without --, `## More Information`, `## Updates`), with placeholder ("blind text") content and a real-looking placeholder UUID (`deaddead-face-face-face-deaddeadface` for the frontmatter `id`, `c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee` for the `## Verifies` cross-reference). Restores the instructional guidance stripped from `example.md` per the clean-example convention, but only as an actual HTML comment where `example.md` itself already shows one is structurally valid (`## Verifies`' single leading-comment slot, and `## Updates`' permanent anchor) -- `## Coverage`, `## Acceptance Criteria`, and `#### Test Steps` carry no comment in the already- finalized `example.md` either (mirroring their precedent classes' lack of a `WithComment` variant: `rsk.Strategy`, `dec.ProsAndCons`, `dec.Option`, none of which support a leading comment), so adding one there would silently commit `template.md` to a schema shape Phase 1 has not decided and `example.md` already contradicts. Their guidance (Coverage's closed vocabulary; Method's closed DTAIS set; the `>= 1`/ unique-number rule; Test Steps' optionality) is instead folded into the free-form AC body prose as a trailing sentence, mirroring `prb_template.md`/`uc_template.md`'s established precedent of appending "Mandatory."/"Optional." notes directly into blind-text paragraph/list content rather than a comment; `## Coverage` itself (an exact-match `full`/`partial`/`none` value with no other content allowed, `re.fullmatch`-enforced) carries no note at all, matching `rsk_template.md`'s identical bare-value `## Strategy` precedent. `## More Information` uses the exact `dec_template.md`/ `feat_template.md` boilerplate sentence instead of a comment, for the same reason. Still not yet validated against `models/md`, since no `vcr` model code exists yet; see Task 1.1-1.3.
- [x] Task 100.110: Confirm the `### AC-NNN (Method): ...` heading regex and duplicate-number `model_validator` behave as expected on hand-written fixtures. Done via a throwaway `/tmp` scratch script (not committed, not a permanent test file), modeled on `dec`'s `_OPTION_HEADING_PATTERN`/`_validate_option_numbers_unique` precedent; see the new Updates entry below for the exact pattern, fixtures, and outcomes (all passed after fixing one bug in the first draft pattern -- missing literal escaped parentheses around the method group).

#### Phase 110: Models and parser

- [x] Task 110.100: `vcr/models/v1/frontmatter.py` (`VcrFrontmatter`, closed `status` vocabulary).
- [x] Task 110.110: `vcr/models/v1/body.py` (`Verifies`, `Coverage`, `AcceptanceCriterion`/`AcceptanceCriteria`, `MoreInformation`, reused `Updates`).
- [x] Task 110.120: `vcr/models/v1/document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`.
- [x] Task 110.130: Unit tests for every model class and the parser.

#### Phase 120: Tools

- [x] Task 120.100: `create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr` (with `raw` param), `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub, `validate_vcr`.
- [x] Task 120.110: Generic `update`/`set_status` dispatch entries (`type="vcr"`) in `general/tools/`.

#### Phase 130: Resources and prompts

- [x] Task 130.100: `specmgr://vcr/schema`, `.../example`, `.../template` resources.
- [x] Task 130.110: `create_vcr`/`update_vcr` prompts.
- [x] Task 130.120: `general/data/general_dtais.md` content (fill in the draft outline persisted in Design Notes), `general/resources/dtais.py` (`specmgr://dtais`), registered in `general/resources/__init__.py`; unit tests.

#### Phase 140: Cross-cutting registration

- [x] Task 140.100: `server.py` import line.
- [x] Task 140.110: `AGENTS.md` Status section bullet (mirroring the `sop`/`feat` bullets).
- [x] Task 140.120: `README.md`, CI/pre-commit updates as needed.
- [x] Task 140.130: `specmgr docs`/`specmgr adr-toc` regeneration, full test suite, ruff/vulture gates.

## Progress

### Current Status

**As of 2026-08-31 (post-merge, latest)**: Merged current `dev` into this
branch (PR #34 / `feat-30-sop`, which added the `sop` domain and the
cross-cutting `specmgr://rasci` resource, plus chore `03260fe`). Every
conflict was additive (`sop` and `vcr` register into the same generic
dispatch points) and was resolved by combining both sides; a missing
`vcr` packaged-schema CI step was added for parity with `sop`. All
generated artifacts were regenerated from the merged source and verified
drift-free; full gate green (2704 tests `OK`). The branch is now PR-ready
against `dev`. See the newest Updates entry below for the per-file
resolution log.

**As of 2026-08-31 (pre-merge)**: Feature complete end to end. Phase 4
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

#### 2026-08-31T16:26:00.000Z - Merged current `dev` (incl. PR #34 / SOP) into `feat-33-vcr`; resolved all conflicts additively; branch PR-ready
`origin/dev` had advanced past this branch's merge base (`4c7d976`) by PR
#34 ("feat(30): Add artifact type \"Standard Operating Procedure\" (SOP) —
complete", `ec3d644`) -- the new `sop` domain plus the cross-cutting
`specmgr://rasci` resource -- and by chore `03260fe` (a feat-7 README
backlog note; no file overlap). `git merge origin/dev` conflicted in 14
files; every conflict was additive (both `sop` and `vcr` register into the
same generic dispatch points) and was resolved by combining both sides:
`general/tools/update.py`: eleven whole-body domains
  (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`),
  both `_update_sop` and `_update_vcr` adapters, 11-way return union,
  11-value `type` enum; the `update` docstring was re-normalized to the
  base indentation the `sop` side had re-indented.
`general/tools/set_status.py`: twelve domains incl. `adr`, both
  adapters, 12-way union, 12-value enum; same docstring normalization.
`server.py`: module docstring gains both domains' resource lines,
  "no `{id}`/no `list`" sentences, tools/prompt paragraphs, and the count
  bumps (eleven whole-body / twelve incl. `adr`); the bottom import line
  is now `adr, dec, feat, general, gol, prb, qa, req, rsk, sop, tsk, uc,
  vcr`.
`general/resources/__init__.py`: imports/`__all__`/docstring carry
  `dtais`, `iso25010`, `rasci`, and `version`.
`commands/schema.py`: both `generate_sop_schema` and
  `generate_vcr_schema` plus both `_GENERATORS` entries (the registry
  itself auto-merged).
`.pre-commit-config.yaml`: all 11 `files:` regexes carry
  `sop/models/v1` and `vcr/models/v1`; both `specmgr-schema-sop-package`
  and `specmgr-schema-vcr-package` hooks present (12 schema hooks total).
`tests/general/tools/test_update.py` / `test_set_status.py`: both
  per-domain cases and fixtures (after the `dec` case, `sop` then
  `vcr`); `update`'s registration assertion now expects the 11-value
  enum; docstring counts updated to eleven/twelve -- the `sop` side had
  left `test_set_status`'s docstring stale at nine/eight, fixed as part
  of the union; `test_update`'s field-error note now names
  `dec`/`sop`/`vcr` (duplicated `### Option`/`### Step`/`### AC-NNN`
  numbers).
`AGENTS.md`: both `sop/` and `vcr/` Status bullets; `general/`
  paragraph unioned (eleven whole-body domains, twelve incl. `adr`,
  resources `version`/`iso25010`/`dtais`/`rasci`, eleven `get_<d>`
  tools); the "still missing" `validate_*`/`delete_*` lists, the
  registration summary, and the MCP-server import list all gain both.
`README.md` / `pyproject.toml`: auto-merged cleanly (SOP line after
  RSK, VCR line after UC; both `package-data` entries).
`.github/workflows/ci.yml`: an audit against the pre-commit hooks
  found all 11 packaged schema copies covered by hooks but only 10 by
  CI steps (`vcr` missing -- this branch had added the pre-commit hook
  but no CI step, unlike the `sop` PR). Added the
  `src/biz/dfch/specmgr/vcr/data/vcr_schema.json` packaged-copy drift
  step (after the `feat` step, before `docs/coverage.svg`) and added
  `vcr` to the all-types comment.
Generated artifacts (`docs/GENERATED.md`, `docs/api/**`,
  `docs/MCP.md`, `docs/*_schema.json`, packaged schema copies,
  `docs/adr/README.md`): conflict markers were dropped in favor of a
  full regeneration from the merged source -- `specmgr docs`,
  `specmgr mcp-docs`, `specmgr schema` (all 11 types `unchanged`),
  `specmgr schema --type {sop,vcr} --output-dir src/.../{sop,vcr}/data`
  (both `unchanged`), `specmgr adr-toc` -- then re-run as a fixed-point
  check with zero drift.
Quality gate after the merge: `ruff format --check` (1481 files),
`ruff check` (all passed), `vulture` (clean, no new whitelist entries
needed), full `unittest` suite (2704 tests, `OK`), `coverage run` +
`specmgr coverage-badge` (99%, `docs/coverage.svg` byte-unchanged),
advisory `pylint` (8.87/10, no new messages from the merge).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31T11:15:00.000Z - Corrected: `AcceptanceCriterion.description` added; `Updates` needs `WithComment`
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
#### 2026-08-31T10:30:00.000Z - `AcceptanceCriterion` carries no free-form description field; body is heading + optional `Test Steps` only
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
#### 2026-08-31T08:50:00.000Z - `example.md` is the sole draft; instructional comments removed
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
#### 2026-08-31T08:35:00.000Z - DTAIC's "Certification" renamed to "Special" (DTAIS)
Renamed the 5th verification method from "Certification" to "Special,"
changing the acronym from "DTAIC" to "DTAIS" throughout REQ-003, the
Overview, Scope, Acceptance Criteria, and Design Notes. User-directed
terminology choice; no additional rationale beyond preferring "Special"
as a broader term. `example.md`/`example.v2.md` (historical, superseded)
keep the original "Certification" wording; `example.v3.md` uses the
new term.
#### 2026-08-31T08:35:00.000Z - Cross-cutting `specmgr://dtais` resource (REQ-006)
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
#### 2026-08-31T08:15:00.000Z - `## Verifies` is a single-value field, not a list-of-one
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
#### 2026-08-31T07:25:24.241Z - Domain key `vcr`, not `ver`/`avc`
Chose `vcr` ("Verification Case Record") over `ver` (too easily confused
with the unrelated `version` frontmatter field) and `avc` (over-emphasizes
acceptance criteria over the verification record as a whole).
#### 2026-08-31T07:25:24.241Z - DTAIC is 5 methods, including Certification
Primary sources reviewed for `sysrs` (INCOSE Guide for Writing
Requirements, MITRE SE Guide) only document 4 verification methods
(Inspection, Analysis, Demonstration, Test). User explicitly chose a
5-method set adding Certification.
#### 2026-08-31T07:25:24.241Z - No separate pass/fail/waived outcome field
`## Coverage` (full/partial/none) is the only outcome signal; adding a
separate disposition field was considered and rejected as redundant.
#### 2026-08-31T07:25:24.241Z - Simple surface, no per-AC mutation tools
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
