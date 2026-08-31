---
created: 2026-08-31 07:25:24.241609
id: feat-33-vcr
status: planning
type: feat
updated: 2026-08-31 07:25:24.241609
version: 1.0.0
---

# Feature: Add artifact type "Verification Case Record" (VCR)

## Plan

### Overview

New document-type domain, `vcr` ("Verification Case Record"), that captures
how a single requirement or use case is verified: a coverage assessment plus
a list of acceptance criteria, each with its own DTAIC verification method.
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
  a single cross-reference bullet holding a literal `REQ`/`UC` tag, the
  real (UUID) id, and the title, plus a short agent-generated paraphrase
  as an indented notes paragraph (`MarkdownListItemWithNotes`). A
  `model_validator` enforces cardinality = 1 and tag in {REQ, UC}. Resolves
  the previously-open "id is a real UUID, not a human code" gap shared
  with `sysrs`'s own REQ-003.
- REQ-002 (decided): `## Coverage` is a closed vocabulary paragraph --
  `full` / `partial` / `none` -- mirroring `rsk`'s `## Strategy` pattern
  (`MarkdownParagraph` + `field_validator` regex).
- REQ-003 (decided): `## Acceptance Criteria` holds >= 1 repeating
  `### AC-NNN (Method): <criterion text>` sub-sections (3-digit
  zero-padded number, e.g. `AC-001`), DEC-Option-style (numbered H3, no
  per-item mutation tools). `Method` is parsed from the heading itself via
  regex (RSK `Probability`/`Impact` idiom) and is a closed **DTAIC**
  vocabulary: Demonstration, Test, Analysis, Inspection, Certification.
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

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 -- an `example.md`/draft body demonstrates
  the `## Verifies` shape and validates against the `models/md` engine
  (mirroring `sop`'s/`sysrs`'s pre-implementation empirical-verification
  discipline) before Phase 1 starts.
- [ ] ACC-002: Verifies REQ-002 -- `## Coverage`'s closed vocabulary is
  validated the same way.
- [ ] ACC-003: Verifies REQ-003 -- the `### AC-NNN (Method): ...` heading
  regex, DTAIC closed vocabulary, and duplicate-number rejection are
  validated against the `models/md` engine.
- [ ] ACC-004: Verifies REQ-004 -- the frontmatter `status` closed
  vocabulary is implemented and unit-tested.
- [ ] ACC-005: Verifies REQ-005 -- full domain implementation, once
  REQ-001..004 are locked, following `sop`'s task-list shape.

### Scope

#### Included

- Schema design and empirical validation for `## Verifies`, `## Coverage`,
  `## Acceptance Criteria` (incl. DTAIC method + optional `#### Test Steps`), `## More Information`, `## Updates`.
- Full domain build: models, parser, 8 tools, 3 resources, prompts,
  generic dispatch registration, cross-cutting registration.

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
  from-scratch-domain precedent to copy tooling/registration shape from.
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
- Why DTAIC's 5 methods (Demonstration, Test, Analysis, Inspection,
  Certification) were chosen over the 4-method set (Inspection, Analysis,
  Demonstration, Test) found in the primary sources reviewed for `sysrs`
  (INCOSE Guide for Writing Requirements, MITRE SE Guide) -- a deliberate
  user choice to include Certification as a 5th method.
- Why frontmatter `status` uses INCOSE's A26 attribute's
  workflow-progress values (reworded hyphen-free:
  `draft`/`progress`/`complete`/`approved`) rather than an invented
  pass/fail/waived lifecycle.
- Why the acceptance-criteria list needed its own numbered-H3 sub-section
  per entry (DEC-`Option`-style) rather than a flat bullet list: each
  entry has structurally distinct fields (method, optional test steps),
  which a flat `MarkdownListItem` cannot carry.

**Candidate H1/body outline** (not yet empirically validated against
`models/md` -- Phase 0 task):

```markdown
# Feature: <free text, unconstrained like RSK/GOL/DEC/SOP>

## Verifies

- REQ <uuid>: <title>

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

- [ ] Task 0.1: Draft `example.md`/`template.md` bodies exercising every
  section and validate against the `models/md` engine (mirroring `sop`'s/
  `sysrs`'s discipline) before writing any Pydantic model code.
- [ ] Task 0.2: Confirm the `### AC-NNN (Method): ...` heading regex and
  duplicate-number `model_validator` behave as expected on hand-written
  fixtures.

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

#### Phase 4: Cross-cutting registration

- [ ] Task 4.1: `server.py` import line.
- [ ] Task 4.2: `AGENTS.md` Status section bullet (mirroring the
  `sop`/`feat` bullets).
- [ ] Task 4.3: `README.md`, CI/pre-commit updates as needed.
- [ ] Task 4.4: `specmgr docs`/`specmgr adr-toc` regeneration, full test
  suite, ruff/vulture gates.

## Progress

### Current Status

**As of 2026-08-31**: Planning complete -- design agreed interactively
(see Design Notes); GitHub issue #33 opened; dedicated branch/worktree
`feat-33-vcr` created off `origin/dev`. No code written yet.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31T07:25:24.241609 — Created

Feature folder created after an interactive planning session (conducted
on the `feat-32-sysrs` branch/worktree) settled the `vcr` schema shape,
DTAIC vocabulary, frontmatter status lifecycle, and simple-surface
tooling scope. GitHub issue #33 opened with a short overview as its
description; branch/worktree `feat-33-vcr` created off `origin/dev`.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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
