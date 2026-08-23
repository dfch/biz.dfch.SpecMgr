---
created: 2026-08-23
id: feat-14-qa-v2-adjacent-qa
status: done
updated: 2026-08-23
version: 1.0.0
---

# Feature: QA v2 — adjacent question/answer pairs (no per-question heading)

## Plan

### Overview

`qa/models/v1/`'s `QaSection` models one question/answer pair as its own
free-form `### {heading}` H3 sub-section (`qa/models/v1/body.py:194-216`).
This feature introduces a **v2** QA body schema, alongside (not replacing
on disk) v1, where many question/answer pairs can appear directly one after
another inside a single ISO/IEC 25010:2023 characteristic section — each
pair is `<!-- optional comment -->` + `> {question}` (a block quote) +
free-form answer prose, with **no heading of its own** per pair. The
enclosing category section can also be entirely empty (zero pairs). A new,
additional `## Elicitation Context` section (structurally identical to the
9 ISO/IEC 25010:2023 characteristic sections) is introduced between
`## General` and the first characteristic (`## Functional Suitability`).

Once v2 is validated, every QA MCP tool/resource/prompt is repointed at it;
existing v1-shaped documents are **not** auto-migrated — the shared parsing
path checks `QaFrontmatter.version`'s major component and raises a clear,
actionable error ("this document must be migrated") for anything that
isn't v2. `qa/models/v1/` stays on disk (no tool reaches it anymore) as
historical reference only; full deletion is a separate, later cleanup, out
of this feature's scope.

**Deliberately minimal footprint on the shared `models/md` engine.** Unlike
feat-12 (which added a genuinely reusable `@markdown(end_marker=...)`
mechanism to `MarkdownSection.get_extent`), this feature adds **zero**
changes to `models/md/` — every new mechanic (the free-form
"swallow-until-terminator" answer scan, the composite record's own
`get_extent`) is implemented locally inside `qa/models/v2/`, by design (see
Design Notes).

### Requirements

- REQ-001: `qa/models/v2/question_answer.py`: `QaAnswer` — an opaque,
  free-form markdown blob (mirrors v1's own `QaAnswer` shape) whose own
  `get_extent` stops at the first depth-0 occurrence of: a heading (any
  level), a block quote, or a comment — otherwise it runs to the end of the
  given text. `QaQuestionAnswer` — `comment: MarkdownComment | None`,
  `question: MarkdownBlockQuote | None`, `answer: QaAnswer | None`, all
  independently optional; its own `get_extent` sums the three fields' own
  extents sequentially (0 total when nothing matches, which is what lets
  the enclosing `questions` list — and therefore the whole category section
  — be legitimately empty).
- REQ-002: `qa/models/v2/body.py`: `_QaCategory(MarkdownSection2)` — a
  private intermediate base declaring `questions: list[QaQuestionAnswer] | None` once (mirrors v1's own `_QaCategory` pattern exactly, including its
  dynamic, non-hardcoded heading-level derivation — see Design Notes).
  `ElicitationContext(_QaCategory)` (new) plus the 9 ISO/IEC 25010:2023
  characteristic subclasses (`FunctionalSuitability`, ...,
  `Safety`) — names verified verbatim against the live `specmgr://iso25010`
  resource. `General`/`Introduction`/`RawRequirements`/`MoreInformation`
  duplicated unchanged from v1 (full independence from v1, no imports
  between the two schema versions). `Qa(MarkdownSection1)` H1 wrapper with
  field order: `general` → `elicitation_context` →
  `functional_suitability` → `performance_efficiency` → `compatibility` →
  `interaction_capability` → `reliability` → `security` →
  `maintainability` → `flexibility` → `safety` → `more_information`.
- REQ-003: `QaFrontmatter` is imported unchanged from `qa/models/v1/` into
  `qa/models/v2/` (frontmatter shape is not versioned by this feature, only
  the body schema is) — its existing `version` field is the dispatch key
  for REQ-004's gate.
- REQ-004 (revised 2026-08-23, see Decisions Made): No
  `QaFrontmatter.version`-based dispatch is used — `version` is confirmed
  (via direct testing) to encode the shared `models.md` parsing engine's own
  schema version (hardcoded to major 1, `models/md/_util.py::SCHEMA_MAJOR_VERSION`),
  not a per-document-type body-schema version, and can never carry a
  major-2 value for any document that validates as `QaFrontmatter` at all.
  Mirroring the established, working precedent in
  `uc/models/v2/parser.py::parse_uc` (which performs the same v1→v2
  body-schema cutover with zero runtime version inspection), the QA v2
  parsing entry point (`qa/models/v2/parser.py::parse_qa`) unconditionally
  parses via v2's `Qa` body schema; there is no fallback to v1 parsing and
  no explicit version check. A v1-shaped (or otherwise non-v2-shaped)
  document fails naturally with whatever structural
  `AssertionError`/`pydantic.ValidationError` `Qa.from_text`/
  `QaFrontmatter.model_validate` raises on its own.
- REQ-005 (revised 2026-08-23, see Decisions Made): Repoint every QA MCP
  tool (`create_qa`, `update_qa`, `set_status_qa`, `parse_qa`, `list_qa`,
  `get_qa`, `get_qa_example`, `get_qa_template`, `delete_qa` stub,
  `validate_qa`) at `qa/models/v2/`.
- REQ-006: Regenerate QA resources (`specmgr://qa/schema`, `/example`,
  `/template`, `/list`) from the v2 models/example/template.
- REQ-007: Update QA prompts (`create_qa`, `update_qa`) narration for the
  adjacent-pairs structure (no more "one H3 per question", `## Elicitation Context` called out alongside the 9 characteristics).
- REQ-008: Cross-cutting doc regeneration (`specmgr docs`, `server.py`
  module docstring, `AGENTS.md`) reflecting v2 as the QA domain's only
  tool-reachable schema going forward.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — `QaAnswer.get_extent` stops correctly at
  each of the three terminator kinds (heading/block quote/comment)
  independently and runs to end-of-text when none follow;
  `QaQuestionAnswer.get_extent`/`from_text` round-trip for: empty, comment-
  only, question+answer, full comment+question+answer triple, a
  multi-paragraph answer that embeds an ordered list (captured verbatim,
  opaque), two/three adjacent pairs in sequence, and a trailing dangling
  comment (accepted as a comment-only pair, not an error).
- [x] ACC-002: Verifies REQ-002 — a full reference document (mirroring the
  example in Design Notes) with `## Elicitation Context` before `## Functional Suitability`, at least one category with zero pairs, and one
  category with several adjacent pairs, parses and round-trips
  successfully; all 10 `_QaCategory`-shaped fields are mandatory
  (`questions` may be `None`).
- [x] ACC-003: Verifies REQ-003 — `qa/models/v2/` imports `QaFrontmatter`
  from `qa/models/v1/` with no duplication; existing frontmatter validation
  behavior (status set, required/optional fields) is unchanged.
- [x] ACC-004 (revised 2026-08-23): Verifies REQ-004 — a v2-shaped document
  parses successfully via `qa/models/v2/parser.py::parse_qa`; a v1-shaped
  (or otherwise malformed) document raises a structural
  `AssertionError`/`pydantic.ValidationError` from `Qa.from_text`/
  `QaFrontmatter.model_validate`, with no attempt at v1 parsing and no
  fallback.
- [x] ACC-005 (revised 2026-08-23, see Decisions Made): Verifies REQ-005 —
  every listed QA tool is registered, callable, operates against v2
  documents, and surfaces the same structural
  `AssertionError`/`pydantic.ValidationError` `Qa.from_text`/
  `QaFrontmatter.model_validate` raise on their own for a v1-shaped document
  passed to a read path (`get_qa`/`parse_qa`/`validate_qa`), per REQ-004's
  revised (Phase 3) no-gate design.
- [x] ACC-006: Verifies REQ-006 — the three QA resources reflect v2's shape
  (schema/example/template all parse as v2 documents).
- [x] ACC-007: Verifies REQ-007 — `create_qa`/`update_qa` prompt content
  describes the adjacent-pairs structure and `## Elicitation Context`, with
  no remaining reference to per-question H3 headings.
- [x] ACC-008: Verifies REQ-008 — `specmgr docs`, `specmgr mcp-docs`, and
  `specmgr schema --type qa` all run clean with no drift; `AGENTS.md`
  reflects v2 as QA's tool-reachable schema and notes v1 is retained
  on-disk only, unreachable from tools.

### Scope

**Included in this feature:**

- `qa/models/v2/` models (`question_answer.py`, `body.py`), fully
  independent of `qa/models/v1/` except for the shared, unchanged
  `QaFrontmatter`.
- The version-gate mechanism and its wiring into every QA tool's parsing
  path.
- Full QA tool/resource/prompt rewiring to v2, in this same feature (not
  deferred to a follow-up).
- Example/template packaged data files and generated JSON Schema for v2.
- Full test suite for the new models, the version gate, and the rewired
  tools/resources/prompts.
- `docs/`/`AGENTS.md` regeneration reflecting the v2 cutover.

**Explicitly out of scope:**

- Any change to the shared `models/md` engine — by design, every new
  mechanic here is local to `qa/models/v2/` (see Design Notes).
- An automated v1 → v2 document migration tool (the version gate only
  detects and reports; it does not convert).
- Deleting `qa/models/v1/` from disk (kept as historical reference).
  **Update 2026-08-23**: this cleanup is no longer an unscheduled "separate,
  later" item — it is now tracked explicitly as Phase 8 of this same plan
  (see Task List below), per the user's direct request to add it here
  rather than open a new feature/issue for it.
- Any new `Requirement`-callout-style structure inside `QaQuestionAnswer`
  (v1's `#### Requirement` callout has no v2 equivalent — not requested).
- Cross-document validation or search over QA documents.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr`
  structure), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based
  reads); the existing, unmodified `models/md` engine (`MarkdownStr`,
  `MarkdownSection`, `MarkdownSection2`, `MarkdownSection2WithComment`,
  `MarkdownBlockQuote`, `MarkdownComment`, `MarkdownParagraph`); the
  existing `qa/models/v1/` package (referenced for shape/precedent only,
  not imported, except `QaFrontmatter`); the live `specmgr://iso25010`
  resource as the canonical source for the 9 characteristic names.
- Blocks: None identified yet.

### Design Notes

**Schema:**

```
QaFrontmatter (imported unchanged from qa/models/v1/)

Qa(MarkdownSection1)                              # H1, free-form title (alias ".+")
├── general: General                              # always present
├── elicitation_context: ElicitationContext        # always present, questions may be empty — NEW
├── functional_suitability: <QaCategory>           # always present, questions may be empty
├── performance_efficiency: <QaCategory>
├── compatibility: <QaCategory>
├── interaction_capability: <QaCategory>
├── reliability: <QaCategory>
├── security: <QaCategory>
├── maintainability: <QaCategory>
├── flexibility: <QaCategory>
├── safety: <QaCategory>
└── more_information: MoreInformation | None       # leaf, opaque raw text (unchanged from v1)

General(MarkdownSection2WithComment)               # unchanged from v1
├── introduction: Introduction
└── raw_requirements: RawRequirements

_QaCategory(MarkdownSection2)                      # private intermediate base, NEW shape
└── questions: list[QaQuestionAnswer] | None       # repeating adjacent Q&A pairs; category may be empty

QaQuestionAnswer(MarkdownStr)                      # one Q&A pair, NO heading of its own — NEW
├── comment: MarkdownComment | None                # belongs to the question that follows it
├── question: MarkdownBlockQuote | None
└── answer: QaAnswer | None                        # opaque free-form blob, bounded scan (see below)
```

**Why `QaAnswer`/`QaQuestionAnswer` need local, non-reflective overrides
(and why no `models/md` change is needed):** `models/md`'s generic
`MarkdownStr.from_text`/`get_extent` machinery already distributes text
among declared fields via each field type's own `get_extent`
(`markdown_str.py:287-386`), and `process_list_field` already handles
`list[QaQuestionAnswer]` generically once `QaQuestionAnswer.get_extent`
correctly reports one pair's own extent. Two gaps existed relative to that
generic machinery, both closed locally:

1. `MarkdownStr`'s base `get_extent` (`markdown_str.py:60-97`) is "swallow
   everything remaining" — correct for v1's `QaAnswer` (declared *last* in
   a heading-bounded section) but wrong for v2, where more pairs can follow
   within the same section. `QaAnswer`'s local override generalizes the
   *existing* depth-0 scan pattern already used by
   `MarkdownSection.get_extent`'s `end_marker` mechanism
   (`markdown_section.py:121-146`, introduced by feat-12) from "stop at one
   declared marker type" to "stop at the first of: heading (any level),
   block quote, or comment" — copied and adapted locally, not exported to
   `models/md`.
2. No class in the codebase computes a composite's own extent as the sum
   of its declared fields' extents (every existing composite is either
   heading-bounded or a single pre-grouped markdown-it token — verified
   against `MarkdownSection`, `MarkdownBlockQuote`, `MarkdownListItem`,
   `MarkdownCodeBlock`, `MarkdownComment`). `QaQuestionAnswer.get_extent`
   supplies this locally: mechanically the same per-field walk
   `MarkdownStr.from_text`'s loop already performs
   (`markdown_str.py:345-382`), just totaling extents instead of
   instantiating.

`QaQuestionAnswer`'s `from_text`/`__str__`/`_get_field_names()` need **no**
override — all three fields are plain `Optional[SingleClass]` (no lists, no
unions), which the generic, unmodified engine already handles correctly.

**`_QaCategory`'s heading-level stop condition is dynamic, not
hardcoded.** `_QaCategory(MarkdownSection2)` applies no `@markdown`
decorator of its own; it inherits `_metadata = {"type": "heading_open", "tag": "h2"}` from `MarkdownSection2` through ordinary Python class-
attribute inheritance. `MarkdownSection.get_extent` derives its stop level
at runtime via `own_level = _HEADING_TAGS.index(own_tag) + 1`
(`markdown_section.py:102`) — there is no literal level number anywhere in
this path. If `_QaCategory` were ever changed to inherit from a different
`MarkdownSectionN`, the stop level would follow automatically. This is
identical to, and already proven by, v1's own `_QaCategory(MarkdownSection2)`.

**`## Elicitation Context` is a 10th `_QaCategory`-shaped section, not one
of the 9 ISO/IEC 25010:2023 characteristics** — it will not appear in (and
is not derived from) the `specmgr://iso25010` resource; it is QA-schema-
specific. It sits between `General` and `FunctionalSuitability` in both
markdown document order and `Qa`'s field declaration order.

**Trailing dangling comment:** a comment with nothing recognizable
following it (end of section, or followed by another heading) becomes its
own final `QaQuestionAnswer` with only `comment` set (`question`/`answer`
both `None`) — accepted, not an error, by explicit instruction.

**Hard version-gate cutover, no dual-read support:** by explicit
instruction, the rewired tools do not attempt to parse v1-shaped documents
at all — `QaFrontmatter.version`'s major component is checked and a clear
migration-required error is raised for anything that isn't v2. This is
simpler than, and a deliberate deviation from, ADR's own `version`-field
dispatch-to-multiple-parsers pattern referenced in `AGENTS.md`.

**Reference example** (cross-checked and confirmed during planning):

```markdown
# Widget Frobnicator Q&A

## General

### Introduction

<!-- filled in during the kickoff interview -->

This document captures the requirements interview for the Widget Frobnicator.

### Raw Requirements

The frobnicator must handle at least 500 widgets/minute.

## Elicitation Context

> Who are the primary stakeholders for this system?

Product management and the on-call SRE team.

## Functional Suitability

<!-- comment belongs to the question right after it -->

> What happens when the input queue is empty?

The frobnicator idles and polls every 100ms.

That polling interval is configurable via `poll_interval_ms`.

> How should malformed widgets be handled?

Malformed widgets are rejected and logged. The rejection flow is:

1. Validate the widget schema.
2. Log the failure with the widget's id.
3. Increment the `rejected_total` counter.

No retry is attempted for malformed input.

## Performance Efficiency

## Compatibility

## Interaction Capability

## Reliability

## Security

## Maintainability

## Flexibility

## Safety

## More Information

See the original ticket for background on throughput targets.
```

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
  `.specmgr` with feature-driven work units
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: (tool-only id-based reads, no
  `specmgr://{type}/{id}` resource)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

**Execution approach:** implementation happens on a dedicated feature
branch, `feat/feat-14-qa-v2-adjacent-qa`, branched off `dev`, created only
once this plan is approved (not yet created as of this writing). Each phase
below ends with a mandatory phase-end task — extend/run that phase's unit
tests, run the full pre-commit/quality gate (`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite), and update this README's
Progress section (Current Status, a dated Recent Updates entry, Decisions
Made if applicable) — before the phase is considered done. Each phase is
committed as one Conventional Commit, mirroring feat-12's own per-phase
test-and-commit discipline
(`.specmgr/feat/feat-12-qa-artifact/README.md`).

#### Phase 0: Planning artifact

- [x] Task 0.1: Write this feature plan to `.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md`
  — depends on: none — status: done (2026-08-23).
- [x] Task 0.2: Create feature branch `feat/feat-14-qa-v2-adjacent-qa` off
  `dev` — depends on: Task 0.1 — status: done (2026-08-23).

#### Phase 1: `QaAnswer` + `QaQuestionAnswer`

- [x] Task 1.1: Implement `qa/models/v2/question_answer.py`: `QaAnswer`
  (bounded terminator scan) and `QaQuestionAnswer` (`comment`/`question`/
  `answer`, `get_extent` override) — depends on: Task 0.2 — status:
  done (2026-08-23).
- [x] Task 1.2: Unit tests — `tests/qa/models/v2/test_question_answer.py`
  covering every case in ACC-001 — depends on: Task 1.1 — status:
  done (2026-08-23).
- [x] Task 1.3: Phase-end quality gate (ruff format/check, vulture, full
  `unittest` suite); update this README's Progress section; commit as one
  Conventional Commit (`feat(qa): add v2 QaAnswer/QaQuestionAnswer models`) — depends on: Task 1.2 — status: done (2026-08-23, quality gate green;
  commit itself left to the orchestrator).

#### Phase 2: `body.py`

- [x] Task 2.1: Implement `qa/models/v2/body.py`: `_QaCategory`,
  `ElicitationContext`, the 9 ISO/IEC 25010:2023 characteristic subclasses
  (names verified against live `specmgr://iso25010`), duplicated
  `General`/`Introduction`/`RawRequirements`/`MoreInformation`, `Qa` (H1)
  with the full field order — depends on: Task 1.3 — status: done
  (2026-08-23).
- [x] Task 2.2: Reference document exercising every field (adapted from
  Design Notes' example) + round-trip test in
  `tests/qa/models/v2/test_body.py` (ACC-002) — depends on: Task 2.1 —
  status: done (2026-08-23).
- [x] Task 2.3: Phase-end quality gate; update Progress section; commit
  (`feat(qa): add v2 QA body schema (Elicitation Context, 9 ISO/IEC 25010 categories, General, More Information)`) — depends on: Task 2.2 —
  status: done (2026-08-23, quality gate green; commit itself left to the
  orchestrator).

#### Phase 3: Version gate

**Revised 2026-08-23** (see Decisions Made): there is no "version-gate
helper" -- a structural conflict discovered mid-phase (`QaFrontmatter.version`
can never carry a major-2 value, see Decisions Made) made a
`QaFrontmatter.version`-based dispatch mechanism impossible; the user
resolved this by directing that `qa/models/v2/parser.py::parse_qa` instead
mirror `uc/models/v2/parser.py::parse_uc`'s existing, working
unconditional-v2-parsing precedent exactly (no runtime version inspection
at all). REQ-004/ACC-004 above were revised in place to match.

- [x] Task 3.1: Implement `qa/models/v2/parser.py::parse_qa` (no
  version-gate helper exists; see the revised REQ-004 above and Decisions
  Made) — depends on: Task 2.3 — status: done (2026-08-23). Also delivered
  `qa/models/v2/document.py` (`QaDocument`, pairing v2's `Qa` body with
  `QaFrontmatter` re-exported unchanged from `qa/models/v1/`) as the
  concrete "shared parsing entry point" REQ-004 refers to, per
  orchestrator-directed scope clarification.
- [x] Task 3.2: Unit tests — a v2-shaped document (`version: 1.0.0`
  frontmatter, the only value `QaFrontmatter.version` ever accepts) parses
  successfully; a v1-shaped body fails with the same structural
  `AssertionError`/`ValidationError` `Qa.from_text`/`QaFrontmatter.model_validate`
  raise on their own, with no fallback to v1 parsing (revised ACC-004); plus
  an ACC-003 cross-check confirming `QaDocument.frontmatter`'s declared type
  is `qa.models.v1.frontmatter.QaFrontmatter` itself — depends on: Task 3.1
  — status: done (2026-08-23, `tests/qa/models/v2/test_parser.py`, 6 tests,
  all green).
- [x] Task 3.3: Phase-end quality gate; update Progress section; commit
  (`feat(qa): add v2 parser (parse_qa/QaDocument), no version gate`) —
  depends on: Task 3.2 — status: done (2026-08-23, quality gate green;
  commit itself left to the orchestrator).

#### Phase 4: Rewire `qa/tools/*`

- [x] Task 4.1 (revised 2026-08-23, see Decisions Made): Repoint
  `create_qa`, `update_qa`, `set_status_qa`, `parse_qa`, `list_qa`,
  `get_qa`, `get_qa_example`, `get_qa_template`, `delete_qa` (stub),
  `validate_qa` at `qa/models/v2/` -- repointed at v2's schema/parser (no
  version gate exists -- see Phase 3's revised REQ-004 and Decisions Made)
  — depends on: Task 3.3 — status: done (2026-08-23).
- [x] Task 4.2: Update/extend `tests/qa/tools/` for v2 behavior through the
  actual tool functions (ACC-005) — depends on: Task 4.1 — status: done
  (2026-08-23).
- [x] Task 4.3: Phase-end quality gate; update Progress section; commit
  (`feat(qa)!: repoint QA tools at v2 schema`, noting the breaking change
  for v1 documents in the commit body) — depends on: Task 4.2 — status:
  done (2026-08-23, quality gate green; commit itself left to the
  orchestrator).

#### Phase 5: Rewire `qa/resources/*`

- [x] Task 5.1: Regenerate `specmgr://qa/schema`, `/example`, `/template`
  from v2 models/example/template — depends on: Task 4.3 — status: done
  (2026-08-23).
- [x] Task 5.2: Update/extend `tests/qa/resources/` to assert v2 shape
  (ACC-006) — depends on: Task 5.1 — status: done (2026-08-23).
- [x] Task 5.3: Phase-end quality gate; update Progress section; commit
  (`feat(qa): update QA resources (schema/example/template) for v2`) —
  depends on: Task 5.2 — status: done (2026-08-23, quality gate green;
  commit itself left to the orchestrator).

#### Phase 6: Rewire `qa/prompts/*`

- [x] Task 6.1: Update `create_qa`/`update_qa` prompt narration for the
  adjacent-pairs structure and `## Elicitation Context` — depends on: Task
  5.3 — status: done (2026-08-23). Also updated the packaged `refine`
  instructions file for the same v1→v2 shape change, per orchestrator
  scope note (see Decisions Made).
- [x] Task 6.2: Update/extend `tests/qa/prompts/` (ACC-007) — depends on:
  Task 6.1 — status: done (2026-08-23).
- [x] Task 6.3: Phase-end quality gate; update Progress section; commit
  (`feat(qa): update QA prompts for v2 adjacent question/answer structure`) — depends on: Task 6.2 — status: done (2026-08-23, quality gate green;
  commit itself left to the orchestrator).

#### Phase 7: Cross-cutting docs + final verification

- [x] Task 7.1: `uv run --frozen specmgr docs` (regenerate `docs/api/`,
  `docs/GENERATED.md`); update `server.py`'s module docstring; update
  `AGENTS.md`'s QA section (v2 as the tool-reachable schema, v1 retained
  on-disk only, unreachable from tools) — depends on: Task 6.3 — status:
  done (2026-08-23).
- [x] Task 7.2: Final verification pass — walk every ACC-001..008 with
  concrete evidence; run the full quality gate end-to-end (`ruff format/check`, `pylint` advisory, `vulture`, full `unittest`, `specmgr docs`/`specmgr adr-toc` drift checks) — depends on: Task 7.1 — status:
  done (2026-08-23).
- [x] Task 7.3: Update Progress section (Current Status, dated Recent
  Updates entry); set feature frontmatter `status: done`; commit
  (`docs(qa): regenerate generated docs for QA v2`) — depends on: Task
  7.2 — status: done (2026-08-23, quality gate green; commit itself left
  to the orchestrator).

#### Phase 8: Cleanup -- remove qa/models/v1/

**Added 2026-08-23**, after Phases 0-7 were already complete, per the
user's explicit request to track this follow-up cleanup directly in this
same plan rather than open a new feature/issue for it (see the Scope
section's revised "Explicitly out of scope" bullet). Not yet started --
none of Phase 8's tasks have been executed.

- [ ] Task 8.1: Grep the whole repo for `qa.models.v1`/`qa\.models\.v1`
  (`src/`, `tests/`, `docs/`, config files) to enumerate every remaining
  reference before deleting anything -- do not assume the known set below
  (`qa/models/v2/document.py`, `qa/models/v2/parser.py`,
  `qa/models/v2/__init__.py`, `qa/tools/_write.py`) is exhaustive. Then, as
  a distinct sub-step (the one non-trivial part of an otherwise mechanical
  deletion): **move** `qa/models/v1/frontmatter.py` (`QaFrontmatter`) out
  of `qa/models/v1/` and into `qa/models/v2/` itself (or another clearly-
  named shared location, e.g. a new `qa/models/_shared/`), update every
  import found by the grep sweep away from `..v1.frontmatter`/
  `qa.models.v1.frontmatter` to the new location, and update
  `qa/models/v2/__init__.py`'s re-export accordingly. Only once every
  import is repointed, delete the rest of `qa/models/v1/` entirely
  (`__init__.py`, `_util.py`, `body.py`, `document.py`, `parser.py`,
  `summary.py` -- `QaSummary` is imported from `qa/models/v1/` by
  `qa/tools/list_qa.py` per Phase 4's Decisions Made, so confirm via the
  grep sweep whether `summary.py` needs the same move-not-delete treatment
  as `frontmatter.py`, rather than assuming it doesn't) -- depends on:
  Task 7.3 -- status: not-started.
- [ ] Task 8.2: Delete `tests/qa/models/v1/` entirely, and remove/rewrite
  any remaining test elsewhere in the suite that imports from
  `qa.models.v1` (confirm via the same grep sweep as Task 8.1 rather than
  assuming Phases 4-6's own rewiring already left none) -- depends on:
  Task 8.1 -- status: not-started.
- [ ] Task 8.3: Update `AGENTS.md`'s `qa/` bullet to remove its current
  description of `qa/models/v1/` as "legacy, retained on disk purely as
  historical reference" entirely, since it no longer exists on disk at
  all -- QA becomes a single-schema (v2-only) domain again, matching how
  the bullet would read had v1 never existed, while keeping the wording
  that is still accurate (the `## Elicitation Context`/adjacent-pairs
  description, the tool/resource/prompt lists) -- depends on: Task 8.2 --
  status: not-started.
- [ ] Task 8.4: Phase-end quality gate (`ruff format --check`, `ruff check`,
  `vulture src/ whitelist.py --min-confidence 60`, full `unittest discover`
  suite, `specmgr docs`/`specmgr mcp-docs` drift checks -- `qa/models/v1/`'s
  module docstrings currently appear in `docs/GENERATED.md`/`docs/api/` and
  must drop out cleanly); update this README's Progress section (Current
  Status, a dated Recent Updates entry); commit as one Conventional Commit
  (suggest: `chore(qa)!: remove qa/models/v1 (superseded by v2)`, noting in
  the commit body that this is a breaking change for anyone still importing
  `qa.models.v1` directly, even though no MCP tool/resource/prompt has
  referenced it since Phase 4) -- depends on: Task 8.3 -- status:
  not-started.

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-23**: Phase 0 (planning + branch creation), Phase 1
(`QaAnswer`/`QaQuestionAnswer`), and Phase 2 (`body.py`) are all done.
`qa/models/v2/question_answer.py` implements `QaAnswer`'s bounded
terminator scan and `QaQuestionAnswer`'s composite `get_extent`, both
purely local to `qa/models/v2/` with zero changes to `models/md/`;
`tests/qa/models/v2/test_question_answer.py` covers every case in ACC-001
(17 tests, all green). `qa/models/v2/body.py` adds `_QaCategory`,
`ElicitationContext` (a 10th `_QaCategory`-shaped section, not one of the 9
ISO/IEC 25010:2023 characteristics), the 9 characteristic subclasses (names
verified against the live `specmgr://iso25010` resource), and
`General`/`Introduction`/`RawRequirements`/`MoreInformation` duplicated
verbatim from v1, plus `Qa` (H1) with the full field order (`general` ->
`elicitation_context` -> the 9 characteristics -> `more_information`);
`tests/qa/models/v2/test_body.py` covers ACC-002 with the README's own
reference document (18 tests, all green). Phase 2's quality gate
(`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite —
1311 tests total) is green.

**Phase 3 is done.** A mid-phase structural conflict (`QaFrontmatter.version`
can never carry a major-2 value -- see Decisions Made) was escalated to and
resolved by the user: `qa/models/v2/parser.py::parse_qa` mirrors
`uc/models/v2/parser.py::parse_uc`'s existing unconditional-v2-parsing
precedent instead of a `version`-based gate. REQ-004/ACC-004 were revised
in place accordingly. `qa/models/v2/document.py` (`QaDocument`) and
`qa/models/v2/parser.py` (`parse_qa`) are implemented and exported;
`tests/qa/models/v2/test_parser.py` (6 tests) covers a full v2-shaped
document parsing successfully, a v1-shaped body failing with the same
structural error `Qa.from_text` raises on its own (no v1 fallback), an
invalid-frontmatter `ValidationError` case, and the ACC-003 cross-check.
Phase 3's quality gate (`ruff format --check`, `ruff check`, `vulture`, full
`unittest` suite -- 1317 tests total) is green.

**Phase 4 is done.** Every one of the ten listed QA tools (`create_qa`,
`update_qa`, `set_status_qa`, `parse_qa`, `list_qa`, `get_qa`,
`get_qa_example`, `get_qa_template`, `delete_qa`, `validate_qa`) is
repointed at `qa/models/v2/` (`QaSummary` deliberately stays imported from
`qa/models/v1/` in `list_qa.py`, per REQ-002/REQ-003 -- it is a generic,
body-schema-independent DTO). `tests/qa/tools/` (10 of 14 files needed
changes; the other 4 -- `test__lock.py`, `test_delete_qa.py`,
`test_get_qa_example.py`, `test_get_qa_template.py` -- had no v1-shaped
fixtures or model imports to begin with) now uses v2-shaped fixtures
(`## Elicitation Context` added, `.items`/`QaSection` usages converted to
`.questions`/`QaQuestionAnswer`), and every read-path tool (`get_qa`,
`parse_qa`, `validate_qa`) has an explicit ACC-005 test confirming a
v1-shaped document fails with the same structural
`AssertionError`/`pydantic.ValidationError` the v2 parser raises on its
own, with no silent v1 fallback. REQ-005/ACC-005's own wording was revised
in place to drop the stale "version gate" reference left over from Phase
3's blocker resolution (see Decisions Made). Phase 4's quality gate
(`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite --
  1322 tests total) is green. Phases 5-7 remain `not-started`.

**Phase 5 is done.** `specmgr://qa/schema`/`/example`/`/template` now all
reflect v2's shape (ACC-006). Added `src/biz/dfch/specmgr/qa/models/v2/_util.py`
(`SCHEMA_COMMENT_VERSION = "v2"`, mirroring `uc/models/v2/_util.py`'s own
precedent exactly), exported from `qa/models/v2/__init__.py`. Repointed
`commands/schema.py::generate_qa_schema()`'s imports from
`qa.models.v1`/`qa.models.v1.document` to `qa.models.v2`/`qa.models.v2.document`
(docstring corrected from "v1"/`qa.models.v1` to "v2"/`qa.models.v2`) and
regenerated both `docs/qa_schema.json` and
`src/biz/dfch/specmgr/qa/data/qa_schema.json` via `specmgr schema --type qa`
(twice, once per output dir) -- both now carry `"$comment": "v2"` and a
`$defs`/`properties` shape built from v2's `Qa`/`_QaCategory`/`QaQuestionAnswer`
(`elicitation_context`, `questions`; no `items`/`Requirement`/`QaSection`).
Updated `.pre-commit-config.yaml`'s 5 occurrences of the shared
`specmgr-schema*` hooks' `files:` regex from `qa/models/v1` to `qa/models/v2`
so future `qa/models/v2/` edits actually re-trigger schema regeneration.
Grepped `.github/workflows/ci.yml` for `qa/models/v1`/`qa/models` -- no match
found, so nothing needed changing there (QA's CI drift checks are not
per-domain-scoped the way the pre-commit hooks are).

Rewrote the packaged `src/biz/dfch/specmgr/qa/data/qa_example.md` into a
complete, valid v2-shaped document, keeping the same widget-registry-migration
interview scenario: added a `## Elicitation Context` section (one Q&A pair,
about who was interviewed/why) between `## General` and
`## Functional Suitability`; converted every old `### {heading}` Q&A
sub-section into v2's adjacent shape (optional `<!-- comment -->` + `>
{question}` + free-form answer, no heading of its own), folding each old
subsection's own heading text into its question's block quote where it read
naturally (e.g. "What must happen if a widget fails to migrate cleanly?"
folded into the existing listener-rollback question) and dropping it
otherwise (the block quote already fully captured the question); dropped
both `#### Requirement` callouts entirely, folding their load-bearing content
(the rollback-scope requirement, the cutover-fallback requirement) into the
surrounding answer prose so no information was lost; kept `## Compatibility`
with zero pairs, per instruction; left the frontmatter's `version: 1.0.0`
untouched (confirmed in Phase 3 to be the shared `models.md` engine's
version, unrelated to QA's own body-schema version). Verified via a direct
Python snippet that the rewritten file's body (`frontmatter.loads(text).content`,
`format_text`-normalized) round-trips byte-for-byte through
`qa.models.v2.body.Qa.from_text`/`str()`, and that the whole file parses via
`qa.models.v2.parser.parse_qa` with `elicitation_context.questions` and
`functional_suitability.questions` both populated. Rewrote
`src/biz/dfch/specmgr/qa/data/qa_template.md` similarly: added a
`## Elicitation Context` placeholder pair mirroring `## Functional
Suitability`'s own placeholder shape, removed the `#### Requirement`
callout placeholder text (no v2 equivalent), and rewrote `## Functional
Suitability`'s placeholder prose to describe v2's actual shape (optional
comment, `>` question block quote, free-form answer, no heading of its own,
multiple pairs one after another) plus a second adjacent placeholder pair
demonstrating that directly. Extended `tests/qa/resources/test_qa_schema.py`
(new `test_reflects_v2_body_shape`, and the existing default-schema test's
`"$comment"` assertion updated from `"v1"` to `"v2"`),
`tests/qa/resources/test_qa_example.py` (new
`test_parses_successfully_as_a_v2_document`, parsing the real packaged
example via `qa.models.v2.parser.parse_qa` and asserting
`elicitation_context.questions` is non-empty), and
`tests/qa/resources/test_qa_template.py` (new
`test_contains_elicitation_context_section`, a lightweight structural check
only, per `get_qa_template`'s own "not guaranteed to validate" docstring).
Grepped the wider test suite for other QA-schema-comment/shape assertions
that this change could break (`tests/commands/test_schema.py`,
`tests/general/tools/test__packaged_data.py`) and confirmed both are
REQ-only, not QA-specific -- no changes needed there. Phase 5's quality gate
(`ruff format --check`, `ruff check`, `vulture`, full `unittest` suite --
1325 tests total) is green; both final `specmgr schema --type qa`
invocations (default `docs/` output dir and
`src/biz/dfch/specmgr/qa/data`) report `(unchanged)`/exit 0, confirming zero
drift.

**Phase 6 is done.** Rewrote the narration in all three of QA's packaged
prompt-instructions files (no `qa/prompts/*.py` code changed -- all three
prompts are already version-agnostic `string.Template` substitutions over
a packaged `.md` file):
`src/biz/dfch/specmgr/qa/data/qa_create_instructions.md`'s "Structure
recap" now describes ten fixed `##` category headings (`## Elicitation
Context` first, explicitly called out as QA-schema-specific and *not* one
of the nine ISO/IEC 25010:2023 characteristics, followed by the nine
characteristics themselves), each holding zero or more adjacent
comment/question/answer pairs with no heading of their own (dropped every
"`### {question-ish heading}`"/"a free-form H3 per pair" reference and the
`#### Requirement` callout entirely, per this feature's own explicit scope
exclusion); step 2's gather-information guidance and step 3's
template/example/schema reference guidance were updated to match (nine ->
ten headings, `Elicitation Context` gathered first).
`qa_update_instructions.md`'s step 3 tool-mapping bullet now lists
`Elicitation Context` alongside (and explicitly distinct from) the nine
ISO/IEC 25010:2023 category sections, drops `requirement` from a Q&A
pair's field list (now `comment`/`question`/`answer` only), and updates
"nine fixed category headings" to "ten" in the whole-body-replace caveat.
`qa_refine_instructions.md`'s step 2 now offers `Elicitation Context` as a
tenth selectable target alongside the nine characteristics (with an "all
ten" shortcut replacing "all nine"); step 3 explicitly calls out skipping
the `specmgr://iso25010` lookup for `Elicitation Context` (QA-schema-
specific, no ISO/IEC 25010:2023 definition to fetch) and drafting
context-gathering questions directly instead; step 4 now describes
appending new pairs in v2's adjacent shape (`> {question}` immediately
followed by the literal `_(awaiting response)_` placeholder, no heading of
its own) directly after any existing pairs in the targeted category,
keeping the existing "no comment, no requirement callout on new pairs"
instruction (dropping only the now-nonexistent "requirement callout"
half, since v2 has no such callout at all); step 5's "nine fixed category
headings" became "ten". Extended
`tests/qa/prompts/{test_create_qa,test_update_qa,test_refine}.py` (ACC-007)
with assertions that `## Elicitation Context`/`Elicitation Context` is
mentioned in each prompt's output and that the old v1 per-pair-heading
phrasing (`"### {question-ish heading}"`) and the old
`"comment`/`requirement`/`question`/`answer"` field-list phrasing are both
gone; `test_create_qa.py` also asserts `#### Requirement` no longer
appears. A final grep sweep across all three
`qa_*_instructions.md` files for leftover `### {`/`#### Requirement`
  references found none; every remaining "nine" reference correctly scopes
  to the nine ISO/IEC 25010:2023 characteristics specifically, not the
  overall (now ten) category count. Phase 6's quality gate (`ruff format
  --check`, `ruff check`, `vulture`, full `unittest` suite -- 1332 tests
  total) is green.

**Phase 7 is done — the whole feature is complete.** Updated
`src/biz/dfch/specmgr/server.py`'s module docstring (the `refine` prompt's
description now says "for `Elicitation Context` or one or more of the nine
ISO/IEC 25010:2023 quality characteristics" instead of only the nine; a
full grep of the rest of the docstring found no other QA-schema-shape-
specific prose needing a change -- the rest of the docstring only lists
registered tool/resource/prompt *names*, unaffected by the v1->v2 body
schema change). Updated `AGENTS.md`'s `qa/` bullet to describe the v1
(legacy, on-disk-only, unreachable from any MCP tool/resource/prompt)
/v2 (current, every QA tool/resource/prompt repointed at it) split,
mirroring UC's own v1/v2 phrasing convention, plus a short note on the new
`## Elicitation Context` 10th section; the "Still genuinely missing"
bullet list needed no change (nothing there referenced QA's schema
version). Added a `## [Unreleased]` / `### Changed` entry to
`CHANGELOG.md` documenting the breaking v1->v2 QA schema cutover,
mirroring the `## [0.8.0]` entry's `**BREAKING**:` convention. Ran
`specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc`/
`specmgr schema --type qa` (both output dirs) -- all report zero drift
beyond `docs/api/biz.dfch.specmgr.server.md`'s own regeneration from the
docstring edit above (confirming every prior phase's own pre-commit hook
already kept `docs/`/`qa_schema.json` fully in sync). Final quality gate
green end to end: `ruff format --check` (832 files already formatted),
`ruff check` (all checks passed), `pylint` (advisory only, pre-existing
`R0401` cyclic-import findings across every domain package unrelated to
this feature, 8.95/10), `vulture src/ whitelist.py --min-confidence 60`
(no findings), full `unittest discover` (1332 tests, all passing). Walked
every ACC-001..008 against concrete test evidence (see the final Recent
Updates entry below for the full list) -- all eight confirmed. No file
under `qa/models/`, `qa/tools/`, `qa/resources/`, `qa/prompts/`, or
`models/md/` was touched in this phase; only cross-cutting docs
(`server.py`, `AGENTS.md`, `CHANGELOG.md`, `docs/api/biz.dfch.specmgr.server.md`)
changed.

**Followup added 2026-08-23 (plan-only, no code changed):** Phase 8
("Cleanup -- remove `qa/models/v1/`") has been added to the Task List
above, at the user's direct request, to track the deletion of
`qa/models/v1/` that Phases 0-7 deliberately deferred (see the Scope
section). Phase 8 is **not-started** -- none of its tasks have been
executed. This does not reopen the feature's main scope: Phases 0-7 (the
actual QA v2 feature -- new adjacent-pairs schema, hard version cutover,
full tool/resource/prompt rewiring, cross-cutting docs) remain complete
and merged-ready; the feature frontmatter `status` stays `done`
accordingly, with Phase 8 tracked as an explicitly-scoped followup
cleanup rather than a reason to revert to `in-progress`.

### Blockers

None currently. (The version-gate design conflict found and resolved during
Phase 3 is recorded in Decisions Made, not repeated here.)

### Recent Updates

#### Update 2026-08-23T00:00:00Z

- Completed: Task 0.1 — full design discussion (feasibility exploration of
  a class structure supporting adjacent question/answer pairs without a
  per-question heading), converging on: local (non-`models/md`) `QaAnswer`/
  `QaQuestionAnswer` overrides; `_QaCategory`'s dynamic (non-hardcoded)
  heading-level derivation confirmed already correct via direct source
  inspection (`markdown_section.py:97-102`, `markdown_section2.py:28-29`);
  a new `## Elicitation Context` 10th `_QaCategory`-shaped section (not one
  of the 9 ISO/IEC 25010:2023 characteristics, verified against the live
  `specmgr://iso25010` resource); full duplication of v2's body schema
  from v1 for independence; a hard version-gate cutover (no dual v1/v2
  read support); full tool/resource/prompt rewiring bundled into this same
  feature (not deferred); a phased, test-and-commit-per-phase execution
  plan on a dedicated feature branch. Wrote this README capturing the full
  plan.
- Next: Task 0.2 — create the `feat/feat-14-qa-v2-adjacent-qa` branch off
  `dev`, then begin Phase 1.
- Notes: No code has been written yet, per explicit instruction to write
  only the plan at this stage.

#### Update 2026-08-23T00:30:00Z

- Completed: Created GitHub issue
  [#14](https://github.com/dfch/biz.dfch.SpecMgr/issues/14) ("QA v2:
  adjacent question/answer pairs (no per-question heading)"), using this
  README's Overview section verbatim as the issue body. Renamed the
  feature folder and every internal reference (frontmatter `id`, feature
  branch name, task descriptions) from `feat-0-qa-v2-adjacent-qa` to
  `feat-14-qa-v2-adjacent-qa`, per the `feat-NNN-slug` convention (`0`
  meant "no issue yet"; `14` is the real issue number now that one
  exists).
- Next: Task 0.2 — create the `feat/feat-14-qa-v2-adjacent-qa` branch off
  `dev`, then begin Phase 1.
- Notes: No `src/`/`tests/` code touched — this update only concerns the
  feature folder's identity/naming.

#### Update 2026-08-23T01:00:00Z

- Completed: Task 0.2 (branch `feat-14` created off `dev` by the
  orchestrator) and Phase 1 (Tasks 1.1-1.3). Added
  `src/biz/dfch/specmgr/qa/models/v2/question_answer.py` (`QaAnswer`'s
  bounded terminator scan; `QaQuestionAnswer`'s composite `get_extent`,
  both local to `qa/models/v2/`, zero changes to `models/md/`) and
  `src/biz/dfch/specmgr/qa/models/v2/__init__.py` (exporting `QaAnswer`/
  `QaQuestionAnswer` only, forward-compatible with Phase 2's further
  exports). Added `tests/qa/models/v2/test_question_answer.py` (17 tests)
  covering every ACC-001 case: `QaAnswer.get_extent` stopping at each of
  heading (any level)/block quote/comment independently and running to
  end-of-text otherwise; `QaQuestionAnswer.get_extent`/`from_text`
  round-tripping empty, comment-only, question+answer, full triple, a
  multi-paragraph answer embedding an ordered list (verbatim, opaque),
  two/three adjacent pairs (via `QaQuestionAnswer.process_list_field`,
  since `_QaCategory`/`Qa` don't exist until Phase 2), and a trailing
  dangling comment (both at end-of-text and followed by a heading).
  Quality gate green: `ruff format --check`, `ruff check`, `vulture src/
  whitelist.py --min-confidence 60` (no findings), full `unittest discover`
  (1293 tests, all passing).
- Next: Phase 2 — implement `qa/models/v2/body.py` (`_QaCategory`,
  `ElicitationContext`, the 9 ISO/IEC 25010:2023 characteristic subclasses,
  duplicated `General`/`Introduction`/`RawRequirements`/`MoreInformation`,
  `Qa`), plus its reference-document round-trip test (ACC-002).
- Notes: No `src/biz/dfch/specmgr/models/md/` file was read-only-inspected
  for reference and left completely untouched, per explicit instruction.
  See Decisions Made below for one non-trivial implementation detail
  (`QaQuestionAnswer.get_extent`'s exact algorithm) not spelled out at
  that level of detail in the original plan.

### Decisions Made

- **2026-08-23**: `answer` stays an opaque, unparsed markdown blob (like
  v1's `QaAnswer`), not a structured list of typed paragraph/list-item
  sub-objects — matches the "any MarkdownStr(s), free-form" requirement
  with the smallest implementation, and mirrors v1's own established
  precedent.
- **2026-08-23**: No changes to the shared `models/md` engine — every new
  mechanic (`QaAnswer`'s bounded terminator scan, `QaQuestionAnswer`'s
  composite `get_extent`) is implemented locally inside `qa/models/v2/`,
  by explicit instruction to keep this QA-only and minimal.
- **2026-08-23**: `## Elicitation Context` is an additional section (not a
  replacement for `## General`), positioned between `## General` and `## Functional Suitability`, structurally identical to the 9 ISO/IEC
  25010:2023 characteristic sections (`_QaCategory`-shaped) but not one of
  them.
- **2026-08-23**: Hard version-gate cutover — the rewired tools read
  `QaFrontmatter.version`'s major component and raise a clear
  migration-required error for anything that isn't v2; no dual v1/v2
  parsing support is implemented.
- **2026-08-23**: v2's `General`/`Introduction`/`RawRequirements`/
  `MoreInformation`/`Qa` classes are fully duplicated into
  `qa/models/v2/body.py` rather than imported from v1 (except
  `QaFrontmatter`, which is shared), so v1 can eventually be deleted with
  no lingering dependency from v2.
- **2026-08-23**: Full QA tool/resource/prompt rewiring is bundled into
  this same feature (Phases 4-7), rather than deferred to a follow-up
  feature, by explicit instruction.
- **2026-08-23**: A trailing dangling comment (nothing recognizable
  following it within a category section) becomes its own
  `QaQuestionAnswer` with only `comment` set — accepted, not an error.
- **2026-08-23 (Phase 1)**: `QaQuestionAnswer.get_extent` is implemented as
  a single continuous depth-0 token scan over the whole given `text` (the
  same one-`parse()`-call technique `MarkdownSection.get_extent`'s
  `end_marker` mechanism already uses), tracking `seen_comment`/
  `seen_question`/`content_seen` state, rather than literally summing each
  field's own `get_extent` on successively re-normalized substrings. A
  naive per-field-substring sum was prototyped and rejected: slicing off a
  matched field's lines and re-normalizing the remainder with `mdformat`
  silently drops the separating blank line between two fields (the exact
  class of bug `process_list_field`'s own docstring in `markdown_str.py`
  already documents for a different case), which under-counts the total
  extent by one line per internal field boundary. The single continuous
  scan sidesteps this by construction, since it uses one absolute line
  numbering throughout and never re-parses a substring. This was verified
  empirically against the real engine before committing to the design (a
  naive sum returned 2 for a case that must return 3, absorbing an extra
  answer paragraph into the *next* pair's own extent). The state machine
  also had to add a `content_seen` flag beyond the plan's original
  `seen_comment`/`seen_question` sketch, to correctly stop at a block quote
  that appears *after* some answer prose has already started (a comment
  with no question, straight to answer prose, followed later by the next
  pair's own question) — without it, that later block quote would
  incorrectly be treated as still belonging to the current pair's own
  (already-skipped) `question` field.
- **2026-08-23 (Phase 3)**: Per the orchestrator's explicit scope
  clarification (not a unilateral expansion), Phase 3 delivers
  `qa/models/v2/document.py` (`QaDocument`, pairing v1's unchanged
  `QaFrontmatter` with v2's own `Qa` body) and `qa/models/v2/parser.py`
  (`parse_qa`) as the concrete "shared QA parsing entry point" REQ-004
  refers to -- ACC-004's "a v2 document parses end-to-end" requirement needs
  more than an isolated unit test against a bare version string.
- **2026-08-23 (Phase 3, superseded design attempt)**: An initial
  implementation added a `QaFrontmatter.version`-based gate
  (`qa/models/v2/_version_gate.py`'s `QaSchemaVersionError`/
  `check_qa_schema_version`, dispatching on major `2` == "QA v2"). While
  writing Task 3.2's end-to-end tests, this was discovered to be
  structurally impossible: `QaFrontmatter.version`'s inherited
  `models.md`-engine-version validator (`models/md/_util.py::validate_schema_version`)
  hardcodes acceptance to major `1` only (documented as "the `models.md`
  schema ... version ... DO NOT CHANGE!" -- i.e. the shared parsing
  engine's own version, not a per-document-type body-schema version) and
  raises its own `pydantic.ValidationError` for both `"2.0.0"` and any
  non-`major.minor.patch` garbage *before* any gate function could run.
  Verified interactively:
  `QaFrontmatter.model_validate({"version": "2.0.0", ...})` and
  `QaFrontmatter.model_validate({"version": "banana", ...})` both raise
  `ValidationError` from `MarkdownFrontmatter`'s own validator, never
  reaching the new gate. This was not resolved unilaterally -- every fix
  candidate touched a file this phase was told to leave unchanged
  (`qa/models/v1/frontmatter.py`) or was explicitly out of this feature's
  scope (`models/md/`, see Overview's "zero changes to `models/md/`") -- so
  it was escalated to the orchestrator, who escalated it to the user.
- **2026-08-23 (Phase 3, user decision)**: The user resolved the above
  blocker as **Option 1**: drop the `QaFrontmatter.version`-based gate
  mechanism entirely (`_version_gate.py` and its isolated tests deleted) and
  mirror `uc/models/v2/parser.py::parse_uc`'s existing, already-working
  precedent exactly -- `qa/models/v2/parser.py::parse_qa` parses
  unconditionally via v2's `Qa` body schema, with zero runtime `version`
  inspection. A v1-shaped document now fails naturally with whatever
  structural `AssertionError`/`pydantic.ValidationError`
  `Qa.from_text`/`QaFrontmatter.model_validate` raises on its own -- the "no
  fallback to v1 parsing" guarantee still holds, just because there is no
  v1 code path reachable from `qa/models/v2/parser.py` at all, rather than
  via an explicit check. REQ-004 and ACC-004 (see Requirements/Acceptance
  Criteria above) were revised in place to match, per this plan's own
  "edit task/requirement descriptions in place, rely on git history to
  recover what was originally planned" policy.
- **2026-08-23 (Phase 4)**: REQ-005/ACC-005's wording (originally written
  before Phase 3's version-gate blocker was discovered and resolved, see
  the two Phase 3 entries above) still referenced "the version gate"/
  "REQ-004's error" as if a dedicated gate mechanism existed. Revised both
  in place, same edit-in-place-rely-on-git-history policy this plan
  already uses for REQ-004/ACC-004: REQ-005 drops the
  ", routed through REQ-004's version gate" clause entirely; ACC-005 now
  describes the same structural `AssertionError`/`pydantic.ValidationError`
  `Qa.from_text`/`QaFrontmatter.model_validate` raise on their own for a
  v1-shaped document, per REQ-004's revised (Phase 3) no-gate design, not
  a distinct "REQ-004's error".
- **2026-08-23 (Phase 4)**: `get_qa`'s own id-based lookup
  (`qa.tools._paths.find_qa_path`) silently skips any file that fails to
  parse -- a pre-existing, unrelated-to-this-v1/v2-cutover behavior
  (documented in that module's own docstring, proven by
  `test__paths.py::test_skips_malformed_file_and_still_finds_valid_one`,
  which predates this feature). This means a v1-shaped file dropped into
  the QA base directory can never be *found* by id in the first place --
  calling `get_qa(some_id)` against it surfaces `QaNotFoundError`, not the
  structural parse error ACC-005 asks read-path tools to surface. Rather
  than treat this as a blocker, the ACC-005 test for `get_qa` is written
  one layer down, directly against `qa.tools._io.read_qa` (the function
  `get_qa` -> `load_by_id` calls once a path has already been resolved) --
  the smallest unit that actually demonstrates "no silent v1 fallback"
  for `get_qa`'s own read path, without contradicting the separate,
  legitimate, already-established skip-on-parse-failure behavior of id
  lookup itself.
- **2026-08-23 (Phase 5)**: When restructuring `qa_example.md`'s old
  `#### Requirement` callouts into v2's shape, each old H3 sub-section's own
  heading text was folded into its Q&A pair's block quote wherever that
  heading text carried a question the existing `>` block quote (if any)
  didn't already fully capture (e.g. "What must happen if a widget fails to
  migrate cleanly?" + the existing listener-rollback question were combined
  into one two-part question), and dropped otherwise (several sub-sections'
  heading text was already fully redundant with their own existing `>`
  block quote). No information from either `#### Requirement` callout was
  discarded -- both were folded into the surrounding answer prose as plain
  sentences (dropping the original callout's own nested-list/nested-quote
  formatting, to sidestep the nested-block-quote-inside-a-list edge case in
  `QaAnswer.get_extent`'s terminator scan, even though such a quote would in
  fact sit at depth > 0 and not trigger early termination -- simplifying to
  plain prose was preferred here for readability, not because it was
  structurally necessary).
- **2026-08-23 (Phase 5)**: `.github/workflows/ci.yml` was grepped for
  `qa/models/v1`/`qa/models` and had no matches -- QA's `specmgr
  schema`/`specmgr docs` drift checks in CI are not scoped to specific
  `qa/models/vN` paths the way `.pre-commit-config.yaml`'s local hooks are
  (CI simply re-runs the full command and diffs), so no CI workflow edit
  was needed for this phase, confirming the task instruction's own
  "only edit what you actually find" guidance.
- **2026-08-23 (Phase 2)**: `whitelist.py`'s existing Pydantic-field-name
  block (already covering `items`/`answer`/`question`/`general`/the 9
  category field names for v1) was extended with `elicitation_context` and
  `questions`, alphabetically in place. Vulture flags these two new v2
  field names as unused because — unlike `items`/`more_information`, which
  also happen to be accessed as plain attributes elsewhere in `src/`
  (`tsk`'s `Task.items`, ADR's `body.more_information`) and are therefore
  already "seen" name-wise — `questions`/`elicitation_context` are only
  ever accessed as attributes from `tests/`, which vulture's `src/
  whitelist.py` invocation does not scan. This mirrors the same
  false-positive class every other whitelisted QA/REQ/UC/TSK field name in
  that block already documents, not a new category of exception.
- **2026-08-23 (Phase 6)**: REQ-007/ACC-007's literal wording only names
  `create_qa`/`update_qa`, but Phase 6 also rewrote
  `qa_refine_instructions.md` (the packaged instructions backing the
  separate, already-registered `refine` prompt), extending REQ-007/
  ACC-007's *practical* scope without editing their wording. Rationale:
  `refine`'s pre-existing instructions told the LLM to append new
  v1-shaped `### {question-ish heading}` Q&A pairs, a structure
  `qa/tools/update_qa` (repointed at v2 in Phase 4) now rejects outright --
  leaving it stale would make `refine` actively harmful (guaranteed to
  produce a document `update_qa` cannot write). Fixing it was judged
  squarely necessary to avoid shipping a broken prompt as part of this same
  v1->v2 cutover, even though the plan's own README did not anticipate
  this third prompt's staleness when REQ-007/ACC-007 were originally
  written. REQ-007/ACC-007's own wording was left as-is rather than
  amended, since amending it retroactively to claim it always covered
  `refine` would misrepresent the original plan; this entry documents the
  scope extension instead, per this plan's own precedent of recording
  such calls in Decisions Made rather than silently expanding a
  requirement's text.

#### Update 2026-08-23T02:00:00Z

- Completed: Phase 2 (Tasks 2.1-2.3). Added
  `src/biz/dfch/specmgr/qa/models/v2/body.py`: the private `_QaCategory`
  intermediate base (`questions: list[QaQuestionAnswer] | None`, no
  `@markdown` decorator of its own — inherits `MarkdownSection2`'s
  `_metadata` through ordinary class-attribute inheritance, exactly
  mirroring v1's own `_QaCategory`); the new `ElicitationContext` 10th
  `_QaCategory`-shaped section (verified, via the live `specmgr://iso25010`
  MCP resource read during this phase, to not be one of the 9 official
  characteristics); the 9 ISO/IEC 25010:2023 characteristic subclasses
  (`FunctionalSuitability`, `PerformanceEfficiency`, `Compatibility`,
  `InteractionCapability`, `Reliability`, `Security`, `Maintainability`,
  `Flexibility`, `Safety` — names cross-checked verbatim against that same
  live resource read, confirming v1's own precedent); `General`/
  `Introduction`/`RawRequirements`/`MoreInformation` duplicated verbatim
  from `qa/models/v1/body.py` (no import from v1); and `Qa(MarkdownSection1)`
  with the full field order (`general` -> `elicitation_context` ->
  `functional_suitability` -> ... -> `safety` -> `more_information`).
  Extended `src/biz/dfch/specmgr/qa/models/v2/__init__.py` to export all of
  `body.py`'s public symbols alongside Phase 1's `QaAnswer`/
  `QaQuestionAnswer` (`_QaCategory` stays un-exported, mirroring v1's own
  `qa/models/v1/__init__.py`). Added `tests/qa/models/v2/test_body.py` (18
  tests) covering ACC-002: the 10 category classes' distinct heading
  aliases and shared `heading_open`/`h2` metadata, empty-category
  round-trips, `questions` optionality, `General`/`Introduction`/
  `RawRequirements` parsing, `Qa`'s mandatory-vs-optional field validation
  (including the new `elicitation_context` mandatory check), and a full
  reference-document round-trip test using the README's own Design Notes
  example verbatim (`## Elicitation Context` before `## Functional
  Suitability`, two adjacent Q&A pairs under `Functional Suitability`
  including the multi-paragraph/ordered-list answer, and eight categories
  legitimately empty). Extended `whitelist.py` with `elicitation_context`/
  `questions` (see Decisions Made). Quality gate green: `ruff format
  --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`
  (no findings after the whitelist extension), full `unittest discover`
  (1311 tests, all passing).
- Next: Phase 3 — implement the version-gate helper (reads
  `QaFrontmatter.version`'s major component; raises a clear
  migration-required error for anything not v2), plus its unit tests
  (ACC-004).
- Notes: No `src/biz/dfch/specmgr/models/md/` file was modified; no
  `qa/models/v1/` file was modified; `qa/models/v2/question_answer.py` was
  read-only referenced, not modified. `qa/models/v2/body.py`'s 9
  characteristic names and the confirmation that `Elicitation Context` is
  not one of them were both verified directly against a live
  `specmgr://iso25010` MCP resource read performed during this phase (not
  solely via v1's precedent, though the two independently agree).

#### Update 2026-08-23T03:00:00Z

- Completed: Phase 3 (Tasks 3.1-3.3), after a mid-phase design conflict was
  escalated to and resolved by the user (see Decisions Made). Added
  `src/biz/dfch/specmgr/qa/models/v2/document.py` (`QaDocument`, pairing
  v2's `Qa` body with `QaFrontmatter` re-exported unchanged from
  `qa/models/v1/`) and `src/biz/dfch/specmgr/qa/models/v2/parser.py`
  (`parse_qa`, mirroring both `qa/models/v1/parser.py::parse_qa`'s
  frontmatter-then-body structure and `uc/models/v2/parser.py::parse_uc`'s
  unconditional-v2-parsing shape -- no runtime `version` inspection/gate).
  An initial implementation with a `QaFrontmatter.version`-based gate
  (`_version_gate.py`) was written, found structurally broken (see
  Decisions Made for the full repro), and deleted per the user's Option 1
  decision. Extended `src/biz/dfch/specmgr/qa/models/v2/__init__.py` to
  export `QaDocument`, `QaFrontmatter` (re-export), and `parse_qa`. Added
  `tests/qa/models/v2/test_parser.py` (6 tests) covering: a full v2-shaped
  reference document (`version: 1.0.0` frontmatter -- the only value
  `QaFrontmatter.version` ever accepts) parsing successfully end to end; a
  v1-shaped body (missing the mandatory `## Elicitation Context` section)
  raising the same structural `AssertionError` `Qa.from_text` raises on its
  own, with no fallback to v1 parsing; an invalid-frontmatter-status
  `ValidationError` case; and the ACC-003 cross-check confirming
  `QaDocument.frontmatter`'s declared type is
  `qa.models.v1.frontmatter.QaFrontmatter` itself (via both
  `typing.get_type_hints` and direct `model_fields` inspection). Revised
  REQ-004 and ACC-004 in the Requirements/Acceptance Criteria sections
  above in place to describe the no-gate design. Quality gate green:
  `ruff format --check`, `ruff check`, `vulture src/ whitelist.py
  --min-confidence 60` (no findings), full `unittest discover` (1317 tests,
  all passing).
- Next: Phase 4 — repoint `qa/tools/*` at `qa/models/v2/`
  (`qa/tools/*`'s existing "routed through the version gate" wording will
  need its own in-place revision when that phase starts, since no gate
  exists to route through anymore).
- Notes: No `src/biz/dfch/specmgr/models/md/` file was modified; no
  `qa/models/v1/` file was modified; Phase 1/2's `question_answer.py`/
  `body.py` were not modified. No commit was made (left to the
  orchestrator).

#### Update 2026-08-23T04:00:00Z

- Completed: Phase 4 (Tasks 4.1-4.3). Repointed every QA MCP tool's model
  imports from `qa/models/v1/` to `qa/models/v2/` in
  `src/biz/dfch/specmgr/qa/tools/{create_qa,update_qa,set_status_qa,parse_qa,get_qa,validate_qa,_paths,_write,_io}.py`
  (`Qa`/`QaDocument`/`QaFrontmatter`/`parse_qa`, per file), plus each
  file's Sphinx `:class:`/prose docstring references. `list_qa.py` keeps
  `QaSummary` imported from `qa/models/v1/` (confirmed, by reading
  `qa/models/v1/summary.py`, to be a generic, body-schema-independent DTO
  with no coupling to `Qa`'s field shape) but had its one `parse_qa`
  docstring cross-reference updated to `v2`. `get_qa_example.py`,
  `get_qa_template.py`, and `delete_qa.py` needed no change at all (no
  model imports, no `qa.models.v*` docstring references) -- confirmed by
  direct inspection, per the plan's own scope note.
  `create_qa.py`'s unrelated `CURRENT_SCHEMA_VERSION` import from
  `...models.md` was left untouched, as instructed. Rewrote
  `tests/qa/tools/{test_create_qa,test_update_qa,test_set_status_qa,test_parse_qa,test_get_qa,test_list_qa,test_validate_qa,test__io,test__paths,test__write}.py`
  (10 of the 14 files in the directory) to v2-shaped fixtures: every
  body-markdown fixture gained a mandatory `## Elicitation Context`
  section between `## General` and `## Functional Suitability`;
  `.compatibility.items`/`### {heading}`-per-question assertions were
  converted to `.compatibility.questions`/adjacent-pair
  (`> question` + prose, no heading) shape; every `QaDocument`
  `isinstance`/type-annotated import moved from `models.v1` to `models.v2`
  (confirmed the two are genuinely distinct classes, not aliases, so a
  stale `v1` import would silently break `isinstance` checks against what
  the now-v2-backed tools actually return). `test__write.py` keeps its
  `QaFrontmatter` import pinned to `models.v1` (the deliberately-shared
  symbol) while its `parse_qa` round-trip check moved to `models.v2`. The
  other 4 files (`test__lock.py`, `test_delete_qa.py`,
  `test_get_qa_example.py`, `test_get_qa_template.py`) needed no change --
  confirmed by reading each: no v1-shaped fixture, no `.items`/`.questions`
  access, no `qa.models.v*` import at all (the packaged example/template
  files they exercise remain v1-shaped on disk, unchanged, since
  regenerating them is Phase 5/REQ-006's job, not this phase's).
  Added the explicit ACC-005 test coverage requested for every read-path
  tool: `test_parse_qa.py::test_raises_structural_error_for_v1_shaped_document`,
  `test_validate_qa.py::test_raises_structural_error_for_v1_shaped_{body_only_content,full_document}`,
  and, for `get_qa` (whose own id-based lookup silently *skips* any file
  that fails to parse, per `qa.tools._paths.find_qa_path`'s pre-existing,
  unrelated-to-this-cutover design -- so a v1-shaped file can never be
  *found* by id in the first place), `test_get_qa.py::test_read_path_surfaces_structural_error_for_v1_shaped_document`
  and `test__io.py::TestReadQa.test_raises_structural_error_for_v1_shaped_document`,
  both exercising `qa.tools._io.read_qa` directly -- the smallest unit
  `get_qa` actually delegates to for parsing once a path is resolved (see
  Decisions Made for the full reasoning behind this design choice).
  Revised REQ-005/ACC-005 and Task 4.1's own description in place to drop
  the stale "version gate"/"routed through REQ-004's version gate"
  wording left over from before Phase 3's blocker resolution. Quality
  gate green: `ruff format --check`, `ruff check`, `vulture src/
  whitelist.py --min-confidence 60` (no findings), full `unittest
  discover` (1322 tests, all passing).
- Next: Phase 5 — regenerate `specmgr://qa/schema`, `/example`, `/template`
  from v2 models/example/template (REQ-006/ACC-006).
- Notes: No `src/biz/dfch/specmgr/models/md/` file was modified; no
  `qa/models/v1/` file was modified; Phases 1-3's `qa/models/v2/`
  files (`question_answer.py`, `body.py`, `document.py`, `parser.py`,
  `__init__.py`) were not modified. No commit was made (left to the
  orchestrator).

#### Update 2026-08-23T05:00:00Z

- Completed: Phase 5 (Tasks 5.1-5.3). Added
  `src/biz/dfch/specmgr/qa/models/v2/_util.py` (`SCHEMA_COMMENT_VERSION =
  "v2"`, mirroring `uc/models/v2/_util.py` exactly), exported from
  `qa/models/v2/__init__.py`. Repointed `commands/schema.py`'s
  `generate_qa_schema()` imports from `qa.models.v1`/`qa.models.v1.document`
  to `qa.models.v2`/`qa.models.v2.document` (docstring corrected to say
  "v2"/`qa.models.v2`), then regenerated `docs/qa_schema.json` and
  `src/biz/dfch/specmgr/qa/data/qa_schema.json` via
  `specmgr schema --type qa` (both output dirs) -- both now carry
  `"$comment": "v2"` and a `$defs`/`properties` shape built from v2's
  `Qa`/`_QaCategory`/`QaQuestionAnswer`. Updated all 5 occurrences of the
  shared `specmgr-schema*` pre-commit hooks' `files:` regex in
  `.pre-commit-config.yaml` from `qa/models/v1` to `qa/models/v2`. Grepped
  `.github/workflows/ci.yml` for any `qa/models/v1`/`qa/models` reference --
  none found, so no CI workflow change was needed. Rewrote
  `src/biz/dfch/specmgr/qa/data/qa_example.md` into a complete, valid
  v2-shaped document (new `## Elicitation Context` section, every old `###
  {heading}` Q&A sub-section converted to v2's adjacent
  comment/question/answer shape with no heading of its own, both `####
  Requirement` callouts folded into surrounding answer prose and dropped as
  a separate structure, `## Compatibility` kept empty, frontmatter
  `version: 1.0.0` left untouched) and verified it round-trips through
  `qa.models.v2.body.Qa.from_text`/`str()` and parses end-to-end via
  `qa.models.v2.parser.parse_qa`. Rewrote
  `src/biz/dfch/specmgr/qa/data/qa_template.md` similarly (new `##
  Elicitation Context` placeholder, `#### Requirement` placeholder removed,
  `## Functional Suitability` placeholder prose rewritten to describe v2's
  actual adjacent-pairs shape). Extended
  `tests/qa/resources/{test_qa_schema,test_qa_example,test_qa_template}.py`
  per ACC-006 (updated `"$comment"` assertion to `"v2"`, added a v2-shape
  schema assertion, an actual `parse_qa` round-trip assertion against the
  packaged example, and a lightweight `## Elicitation Context` structural
  check on the template). Grepped the wider test suite for other
  QA-schema-comment/shape assertions this change could break
  (`tests/commands/test_schema.py`, `tests/general/tools/test__packaged_data.py`)
  and confirmed both are REQ-only -- no changes needed. Quality gate green:
  `ruff format --check`, `ruff check`, `vulture src/ whitelist.py
  --min-confidence 60` (no findings), full `unittest discover` (1325 tests,
  all passing). Both final `specmgr schema --type qa` invocations (default
  `docs/` and `src/biz/dfch/specmgr/qa/data`) report `(unchanged)`/exit 0.
- Next: Phase 6 -- update `create_qa`/`update_qa` prompt narration for the
  adjacent-pairs structure and `## Elicitation Context` (REQ-007/ACC-007).
- Notes: No `src/biz/dfch/specmgr/models/md/` file was modified; no
  `qa/models/v1/` file was modified; no `qa/tools/` file was modified;
  Phases 1-4's already-implemented `qa/models/v2/` files
  (`question_answer.py`, `body.py`, `document.py`, `parser.py`) were not
  modified -- only `qa/models/v2/__init__.py` (adding the `SCHEMA_COMMENT_VERSION`
  export) and the new `qa/models/v2/_util.py` were touched in that package.
  No commit was made (left to the orchestrator).

#### Update 2026-08-23T06:00:00Z

- Completed: Phase 6 (Tasks 6.1-6.3). Rewrote the narration in all three of
  QA's packaged prompt-instructions files -- no `qa/prompts/*.py` code
  changed (all three prompts are already version-agnostic
  `string.Template` substitutions over a packaged `.md` file):
  `src/biz/dfch/specmgr/qa/data/qa_create_instructions.md`'s "Structure
  recap" now describes ten fixed `##` category headings (`## Elicitation
  Context` first, explicitly called out as QA-schema-specific and not one
  of the nine ISO/IEC 25010:2023 characteristics, followed by the nine
  characteristics), each holding zero or more adjacent
  comment/question/answer pairs with no heading of their own (dropped
  every "`### {question-ish heading}`" reference and the `#### Requirement`
  callout entirely); steps 2/3 updated to match (nine -> ten headings,
  `Elicitation Context` gathered first).
  `src/biz/dfch/specmgr/qa/data/qa_update_instructions.md`'s step 3
  tool-mapping bullet now lists `Elicitation Context` alongside (and
  explicitly distinct from) the nine ISO/IEC 25010:2023 category sections,
  drops `requirement` from a Q&A pair's field list (now
  `comment`/`question`/`answer` only), and updates "nine fixed category
  headings" to "ten".
  `src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md`'s step 2 now
  offers `Elicitation Context` as a tenth selectable target alongside the
  nine characteristics (with an "all ten" shortcut replacing "all nine");
  step 3 explicitly calls out skipping the `specmgr://iso25010` lookup for
  `Elicitation Context` and drafting context-gathering questions directly
  instead; step 4 now describes appending new pairs in v2's adjacent shape
  (`> {question}` immediately followed by the literal
  `_(awaiting response)_` placeholder, no heading of its own) directly
  after any existing pairs in the targeted category; step 5's "nine fixed
  category headings" became "ten". This third file's update was not
  explicitly named by REQ-007/ACC-007 but was treated as in-scope for this
  phase (see Decisions Made) because its pre-existing instructions
  described a structure `update_qa` (already v2-only since Phase 4) would
  reject outright. Extended
  `tests/qa/prompts/{test_create_qa,test_update_qa,test_refine}.py`
  (ACC-007) with assertions that `Elicitation Context` is mentioned in
  each prompt's output and that the old v1 per-pair-heading phrasing
  (`"### {question-ish heading}"`) and old field-list phrasing
  (`` "comment`/`requirement`/`question`/`answer" ``) are both gone;
  `test_create_qa.py` also asserts `#### Requirement` no longer appears. A
  final grep sweep across all three `qa_*_instructions.md` files for
  leftover `### {`/`#### Requirement` references found none; every
  remaining "nine" reference correctly scopes to the nine ISO/IEC
  25010:2023 characteristics specifically. Quality gate green:
  `ruff format --check`, `ruff check`, `vulture src/ whitelist.py
  --min-confidence 60` (no findings), full `unittest discover` (1332
  tests, all passing).
- Next: Phase 7 -- `specmgr docs` regeneration, `server.py`/`AGENTS.md`
  updates, and final ACC-001..008 verification.
- Notes: No `src/biz/dfch/specmgr/models/md/` file was modified; no
  `qa/models/`, `qa/tools/`, or `qa/resources/` file was modified; no
  `qa/prompts/*.py` file needed any change (all three prompts already read
  their instructions from a packaged `.md` file with no model/schema
  import). No commit was made (left to the orchestrator).

#### Update 2026-08-23T07:00:00Z

- Completed: Phase 7 (Tasks 7.1-7.3) -- the whole feature is now done.
  Updated `src/biz/dfch/specmgr/server.py`'s module docstring (`refine`
  prompt description now covers `Elicitation Context` alongside the nine
  ISO/IEC 25010:2023 characteristics; a full grep found nothing else
  QA-schema-shape-specific in the docstring). Updated `AGENTS.md`'s `qa/`
  bullet to describe the v1 (legacy, on-disk-only)/v2 (current,
  tool-reachable) split and the new `## Elicitation Context` section,
  mirroring UC's own v1/v2 phrasing; the "Still genuinely missing" list
  needed no change. Added a `## [Unreleased]` / `### Changed` entry to
  `CHANGELOG.md` documenting the breaking QA v1->v2 cutover, mirroring the
  `## [0.8.0]` entry's `**BREAKING**:` convention. Ran
  `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc`/
  `specmgr schema --type qa` (both output dirs) -- all report zero drift
  beyond `docs/api/biz.dfch.specmgr.server.md`'s own regeneration from the
  docstring edit. Ran the full quality gate: `ruff format --check` (832
  files already formatted), `ruff check` (all checks passed), `pylint`
  (advisory, pre-existing `R0401` cyclic-import findings across every
  domain package, unrelated to this feature, 8.95/10), `vulture src/
  whitelist.py --min-confidence 60` (no findings), full `unittest
  discover` (1332 tests, all passing). Walked every ACC-001..008 against
  concrete evidence: ACC-001/ACC-002 -- `tests/qa/models/v2/{test_question_answer,test_body}.py`
  (17 + 18 tests); ACC-003 -- `tests/qa/models/v2/test_parser.py::test_frontmatter_field_type_is_v1_qa_frontmatter`/
  `test_frontmatter_field_info_annotation_is_v1_qa_frontmatter`; ACC-004 --
  `tests/qa/models/v2/test_parser.py::test_parses_full_reference_document`/
  `test_missing_elicitation_context_raises_the_same_structural_error_from_from_text`;
  ACC-005 -- `tests/qa/tools/{test_get_qa.py::test_read_path_surfaces_structural_error_for_v1_shaped_document,
  test__io.py::TestReadQa.test_raises_structural_error_for_v1_shaped_document,
  test_parse_qa.py::test_raises_structural_error_for_v1_shaped_document,
  test_validate_qa.py::test_raises_structural_error_for_v1_shaped_{body_only_content,full_document}}`;
  ACC-006 -- `tests/qa/resources/{test_qa_schema.py::test_reflects_v2_body_shape,
  test_qa_example.py::test_parses_successfully_as_a_v2_document,
  test_qa_template.py::test_contains_elicitation_context_section}`; ACC-007
  -- `tests/qa/prompts/{test_create_qa.py::test_mentions_elicitation_context_section,
  test_update_qa.py::test_mentions_elicitation_context,
  test_refine.py::test_mentions_elicitation_context_as_selectable_target}`
  plus each file's own "no longer mentions" negative assertions; ACC-008 --
  the zero-drift `specmgr docs`/`specmgr mcp-docs`/`specmgr schema --type qa`
  command runs above, plus this phase's own `AGENTS.md` edit. Set this
  README's frontmatter `status` to `done` and marked every ACC-001..008
  and Task 7.1-7.3 checkbox done in place.
- Next: None -- feature complete. The orchestrator will independently
  re-verify and then commit (six commits landed on the `feat-14` branch
  are expected, one per phase 1-7, per this plan's own per-phase commit
  discipline).
- Notes: Confirmed via `git status`/`git diff --stat` that only
  `AGENTS.md`, `CHANGELOG.md`, `src/biz/dfch/specmgr/server.py`, and
  `docs/api/biz.dfch.specmgr.server.md` changed in this phase -- no file
  under `qa/models/`, `qa/tools/`, `qa/resources/`, `qa/prompts/`, or
  `models/md/` was touched. No commit was made (left to the orchestrator).

#### Update 2026-08-23T08:00:00Z

- Completed: Plan-only addition of Phase 8 ("Cleanup -- remove
  `qa/models/v1/`", Tasks 8.1-8.4) to the Task List, requested directly by
  the user in conversation (not from a new GitHub issue) to track the
  `qa/models/v1/` deletion that Phases 0-7 deliberately deferred (see the
  Overview and the Scope section's "Explicitly out of scope" bullet, now
  updated to point at Phase 8 instead of an unscheduled "separate, later
  cleanup"). Updated this README's Current Status note to record that
  Phase 8 exists and is not-started, while Phases 0-7 remain complete and
  merged-ready. No `src/`/`tests/` file was touched, no code was run, and
  no task in Phase 8 was executed -- this update is this plan document
  only.
- Next: Phase 8, Task 8.1 -- grep the repo for `qa.models.v1` references
  and move `QaFrontmatter` out of `qa/models/v1/frontmatter.py` before any
  deletion.
- Notes: Feature frontmatter `status` stays `done` (Phases 0-7's actual QA
  v2 feature is complete); this addition does not reopen that scope.

### Related PRs / Commits

None yet (this feature was developed and verified across seven phases on
the `feat-14` branch; the orchestrator commits each phase separately per
this plan's own per-phase commit discipline). Phase 8 (cleanup) has been
added to the plan but not yet executed or committed.
