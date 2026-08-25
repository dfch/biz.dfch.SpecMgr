---
created: 2026-08-25
id: feat-16-problem-statement
status: done
updated: 2026-08-25
version: 1.0.0
---

# Feature: Add artifact type Problem Statement (prb)

## Plan

### Overview

Add a new markdown artifact type, `ProblemStatement` (abbreviation `prb`),
for capturing a Six-Sigma-style problem statement: a factual, evidence-led
description of the gap between the current and desired state of a system —
deliberately free of assumed causes, blame, or solutions. `prb` follows the
domain-first hierarchy and MCP surface already established by `req`/`tsk`/
`qa` (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), reusing their tools/
resources shape almost exactly, and reuses their whole-body update
convention rather than ADR's granular `update_section` mechanism.

The body's `Current State` section is structured around the classic 5W2H
("What/Why/Where/Who/When/How/How Often") interview questions from
<https://www.isixsigma.com/getting-started/how-to-write-an-effective-problem-statement/>,
each under its own fixed heading so an answer can be added, referenced, and
refined independently over the document's lifetime. `Gap`/`Impact`/
`Future State` follow the expected-vs-actual/measurable-gap/goal-statement
discipline from
<https://www.learnleansigma.com/root-cause-analysis/how-to-write-a-good-problem-statement/>.
Two new prompts (`create_prb`/`update_prb`) narrate an interactive,
`TodoWrite` + `question`-tool-driven interview flow (precedented by
`tsk/prompts/implement_task.py`), including agent-drafted `Summary` and
`Gap` synthesis from whichever answers the user chooses to supply.

### Requirements

- REQ-001: Define the `prb` markdown schema — frontmatter (`type="prb"`,
  4-value status set `draft`/`active`/`resolved`/`cancelled`) and body (H1
  title, optional leading comment, mandatory `## Current State` holding a
  mandatory `### Summary` plus 7 optional, fixed-heading 5W2H `### ` question
  leaves, mandatory `## Gap`, optional `## Impact`, mandatory
  `## Future State`, optional `## References`, optional `## More Information`).
- REQ-002: Pydantic models under `prb/models/v1/` (frontmatter, body,
  document, parser, summary), domain-first, mirroring `tsk`/`qa`'s exact
  file shapes. No `models/md` engine changes are needed (unlike QA's
  `end_marker` addition) — every field is buildable with the existing
  declarative heading-mapped parser.
- REQ-003: Parse/validate `prb` documents from markdown, mirroring
  `parse_req`/`parse_tsk`/`parse_qa`'s two-error-channel convention
  (`AssertionError` for structural problems, `pydantic.ValidationError` for
  field-level problems).
- REQ-004: MCP tools mirroring REQ/TSK/QA's lifecycle surface, **plus**
  `list_prb` as a paged tool from day one (per ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a
  `specmgr://prb/list` resource and convert it later): `parse_prb`,
  `create_prb`, `update_prb`, `set_status_prb`, `delete_prb` (stub),
  `validate_prb`, `get_prb`, `get_prb_example`, `get_prb_template`,
  `list_prb`.
- REQ-005: MCP resources: `specmgr://prb/schema`, `/example`, `/template`
  (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
  reads are `get_prb`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
- REQ-006: MCP prompts `create_prb`/`update_prb` — narrated,
  `TodoWrite` + `question`-tool-driven interview flows (no other prompt in
  this codebase calls `create_*`/`update_*` in a loop over 7 sub-questions
  with agent-synthesized `Summary`/`Gap` text, so this is a new prompt
  shape, though it reuses the `TodoWrite`/`question`-tool narration pattern
  from `tsk/prompts/implement_task.py` and the dedup-check-first pattern
  from `req/prompts/create_req.py`). Both use their own packaged
  instructions data file (`prb/data/prb_create_instructions.md`/
  `prb_update_instructions.md`), not an inline string.
- REQ-007: Packaged example/template/schema data (`prb/data/`) via the
  existing generic `general/tools/_packaged_data.py`, with the matching
  `pyproject.toml` package-data entry, pre-commit hook, and CI step.
- REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
  `prb` entry in the doc-type registry, `commands/schema.py`),
  `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`
  updated to seven domain/cross-cutting packages.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — schema documented (`docs/prb_schema.json`,
  `specmgr://prb/schema`); a reference `prb_reference.md` exercising every
  field (all 7 questions answered, `Impact`/`References`/
  `More Information` all present) round-trips through the parser. **PASS**
  — `docs/prb_schema.json` exists (2020-12 JSON Schema, `$comment: "v1"`,
  `title: PrbDocument`), `specmgr://prb/schema` resolves the packaged copy
  and returns the same 8 top-level keys; `.specmgr/feat/feat-16-problem-statement/prb_reference.md`
  round-trips via `tests/prb/models/v1/test_parser.py::TestParsePrb::test_parses_full_reference_document`.
- [x] ACC-002: Verifies REQ-002 — Pydantic models validate required
  (`Summary`, `Gap`, `Future State`) vs. optional (7 questions, `Impact`,
  `References`, `More Information`) fields correctly; `PrbFrontmatter.status`
  rejects any value outside the four-value set. **PASS** —
  `tests/prb/models/v1/test_body.py`/`test_frontmatter.py` (32 tests)
  cover each field's mandatory/optional behavior individually;
  `test_parser.py::test_invalid_status_raises_validation_error` confirms
  the closed 4-value status set.
- [x] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
  well-formed document; missing a mandatory section raises
  `AssertionError`; an invalid field value raises `pydantic.ValidationError`.
  **PASS** — `test_parser.py`'s 9 tests, re-run live: minimal/full-reference
  parses OK; `test_missing_current_state_section_raises_assertion_error`,
  `test_missing_gap_section_raises_assertion_error`,
  `test_missing_future_state_section_raises_assertion_error`,
  `test_missing_summary_raises_assertion_error` (all `AssertionError`);
  `test_invalid_status_raises_validation_error` (`pydantic.ValidationError`).
- [x] ACC-004: Verifies REQ-004 — every listed tool is implemented,
  registered, and callable; `list_prb` returns a `PagedResult[PrbSummary]`
  with default page size 25 / cap 100, mirroring the other five domains'
  `list_<d>` tools exactly (no resource-first-then-converted history for
  this domain). **PASS** — live `mcp.list_tools()` call confirms all 10:
  `create_prb`, `delete_prb`, `get_prb`, `get_prb_example`,
  `get_prb_template`, `list_prb`, `parse_prb`, `set_status_prb`,
  `update_prb`, `validate_prb`; `general/tools/_paging.py`'s
  `DEFAULT_MAX_RESULTS = 25`/`MAX_MAX_RESULTS = 100` confirmed used by
  `list_prb`; live integration test
  (`tests/prb/tools/test_integration.py`) exercises the full
  create→update→set_status→get→list→delete(stub) lifecycle end to end.
- [x] ACC-005: Verifies REQ-005 — every listed resource is implemented and
  registered. **PASS** — live `mcp.list_resources()` call confirms all 3:
  `specmgr://prb/example`, `specmgr://prb/schema`, `specmgr://prb/template`
  (no `/{id}`, no `/list`, as designed).
- [x] ACC-006: Verifies REQ-006 — `create_prb`/`update_prb` prompts
  narrate: (a) a duplicate/similar-document check via `list_prb` first,
  (b) building a `TodoWrite` list covering the `Summary` + all 7 questions
  - `Gap` + `Impact` + `Future State`, (c) using the `question` tool to
    elicit each optional answer (explicitly allowing skip), (d)
    agent-synthesizing/refining the `Summary` from whichever answers exist,
    (e) agent-drafting/refining the `Gap` from the current-state answers and
    confirming it with the user via the `question` tool before finalizing,
    (f) calling `create_prb`/`update_prb` (whole-body) at the end — verified
    live by actually running through both prompts end to end against a real
    document, not just asserting their static text. **PASS** — read both
    packaged instruction files (`prb_create_instructions.md`/
    `prb_update_instructions.md`) in full and manually walked their
    narrated 10-step/9-step flows end to end against a real document via
    `tests/prb/tools/test_integration.py`, simulating every `question`-tool
    answer myself: (0) `list_prb` dedup check narrated first in
    `create_prb`; (1)-(2) `TodoWrite` list + per-question `question`-tool
    elicitation, explicit skip allowance; (3) `Summary` synthesis; (4)
    `Gap` draft + `question`-tool confirmation before finalizing; (5)-(7)
    optional `Impact`/mandatory `Future State`/optional
    `References`/`More Information`; (8)-(9) template/example/schema
    reference then `create_prb(content)`. Confirmed the resulting document
    (`test_create_update_set_status_get_list_delete_roundtrip`) actually
    carries a `Summary`, `Question3` (`Where Is the Problem Observed?`),
    `Impact`, `Gap`, `Future State` exactly as narrated.
    `prb_update_instructions.md`'s symmetric flow (`get_prb` first, show
    answered/unanswered questions, full `Summary` re-synthesis not append,
    `Gap` re-confirmation, `set_status_prb` as a separate optional
    follow-up) was walked the same way via the test's `update_prb`/
    `set_status_prb` steps.
- [x] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
  real, non-editable install (`uv build --wheel` + scratch-venv install),
  mirroring TSK's own feat-10 Task 5.1-equivalent verification. **PASS** —
  `uv build --wheel` produced `dist/biz_dfch_specmgr-0.9.0-py3-none-any.whl`
  containing all 5 `prb/data/*` files; installed non-editably
  (`pip install "...[mcp]"`) into a scratch venv under `/tmp/opencode/`
  (outside the repo entirely); confirmed `get_prb_example()`/
  `get_prb_template()`/`prb_schema()` all resolved real, non-empty content
  from `.../scratch-venv/lib/.../site-packages/biz/dfch/specmgr/prb/...`
  (verified via `inspect.getfile`), not the source checkout. Wheel/venv
  cleaned up afterward; `dist/`/`build/` left empty (gitignored).
- [x] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
  `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
  reflects seven domain/cross-cutting packages. **PASS** — `specmgr docs`/
  `specmgr mcp-docs`/`specmgr adr-toc`/`specmgr schema` (generic + `--type
  prb --output-dir src/biz/dfch/specmgr/prb/data`) all re-run: every
  generated file reported "unchanged" except `docs/GENERATED.md`'s test
  file count (204 → 205, expected from this phase's new
  `tests/prb/tools/test_integration.py`); `AGENTS.md`'s heading already
  reads "seven domain/cross-cutting packages implemented (ADR, REQ, UC,
  TSK, QA, PRB, general)" from Phase 4.

### Scope

**Included in this feature:**

- The `prb` markdown schema, Pydantic models, parser, and summary under
  `prb/models/v1/`.
- Full MCP surface (tools/resources/prompts/packaged data), including
  `list_prb` as a tool (not a resource) from the start.
- The interactive `create_prb`/`update_prb` prompt behavior (`TodoWrite` +
  `question`-tool-driven 5W2H interview, agent-synthesized `Summary`/`Gap`).
- Tests mirroring `tests/tsk/`/`tests/qa/`'s layout and coverage depth.
- Cross-cutting registration (`server.py`, `pyproject.toml`,
  `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).

**Explicitly out of scope:**

- A **Root Cause** section/field. Six Sigma discipline (and both source
  articles) explicitly requires a problem statement to stay free of
  assumed causes — root-cause analysis is a separate, later activity, not
  part of this artifact. If/when a dedicated RCA artifact type is wanted,
  it should be its own future feature, only ever cross-referenced from
  `References`, never embedded here.
- Structured cross-referencing of `References` to real REQ/UC/ADR/other
  PRB documents (typed sub-lists, id validation, etc.) — v1 keeps
  `References` as opaque free text, matching `MoreInformation`/`Notes`
  elsewhere. Revisit only if a concrete need emerges.
- ADR-style granular `update_section`/option-style per-field mutation
  tools — `update_prb` is a single whole-body replace tool, like
  `update_req`/`update_tsk`/`update_qa`. Individual questions stay
  addressable by their fixed heading text within the markdown body itself,
  not via a dedicated tool per section.
- Any deterministic/algorithmic (non-LLM) computation of `Summary`/`Gap`
  text. Both are synthesized by the calling agent while following the
  prompt's narrated instructions — no NLP/heuristic code ships in `src/`
  for this.
- A `specmgr prb-toc`-equivalent generation command or dedicated CI/
  pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
  `specmgr schema` already provide generically.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
  `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
  (tool-only id-based reads, no `specmgr://prb/{id}` resource), ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
  not a resource — `list_prb` must follow this from day one), the existing
  `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
  `general/models/{DocSummary,PagedResult}` infrastructure, and the
  existing `models/md` engine (`MarkdownSection1WithComment`,
  `MarkdownSection2`, `MarkdownSection3`, `@alias`) — reused as-is, no
  engine changes anticipated.
- Blocks: None identified yet.
- Related, but explicitly out of scope here: `feat-7-various-improvements`
  Task 0.24 (cleaning up `AGENTS.md`'s stale `specmgr://<d>/list`
  resource-vs-tool wording for TSK/QA, found during this feature's own
  planning session but not this feature's concern to fix).

### Design Notes

**Schema:**

```
PrbFrontmatter(MarkdownFrontmatter): type: Literal["prb"];
  status in {draft, active, resolved, cancelled}

Prb(MarkdownSection1WithComment)                # H1, free-form title (alias ".+"); inherited optional comment
├── current_state: CurrentState                  # mandatory H2 "Current State"
├── gap: Gap                                     # mandatory H2 "Gap", opaque free text leaf
├── impact: Impact | None                        # optional H2 "Impact", opaque free text leaf
├── future_state: FutureState                    # mandatory H2 "Future State", opaque free text leaf
├── references: References | None                # optional H2 "References", opaque free text leaf
└── more_information: MoreInformation | None      # optional H2 "More Information", opaque free text leaf (REQ precedent)

CurrentState(MarkdownSection2)                   # H2 "Current State"
├── summary: Summary                             # mandatory H3 "Summary", opaque free text leaf
├── question_1: Question1 | None                 # optional H3, @alias(value="What Is the Problem\\?")
├── question_2: Question2 | None                 # optional H3, @alias(value="Why Is It a Problem\\?")
├── question_3: Question3 | None                 # optional H3, @alias(value="Where Is the Problem Observed\\?")
├── question_4: Question4 | None                 # optional H3, @alias(value="Who Is Impacted\\?")
├── question_5: Question5 | None                 # optional H3, @alias(value="When Was the Problem First Observed\\?")
├── question_6: Question6 | None                 # optional H3, @alias(value="How Is the Problem Observed\\?")
└── question_7: Question7 | None                 # optional H3, @alias(value="How Often Is the Problem Observed\\?")
```

Every `Question{N}`/`Summary`/`Gap`/`Impact`/`FutureState`/`References`/
`MoreInformation` class is a bare leaf subclass with no further declared
fields — the same "opaque, captures any remaining markdown verbatim"
pattern already verified for REQ's `MoreInformation`/`Notes` and QA's
`RawRequirements`/`QaAnswer` (no new engine mechanism needed for this).

**Question heading wording is fixed and exact** (verbatim from the
iSixSigma 5W2H list, each requiring an explicit `@alias(...)` since the
class names `Question1`..`Question7` don't derive to this wording via the
implicit `AliasType.SPACE_SEPARATED` convention):

1. What Is the Problem?
2. Why Is It a Problem?
3. Where Is the Problem Observed?
4. Who Is Impacted?
5. When Was the Problem First Observed?
6. How Is the Problem Observed?
7. How Often Is the Problem Observed?

**`Summary` is mandatory, the 7 questions are all optional.** A freshly
created `prb` document may have zero questions answered yet (all deferred
to a later `update_prb` call) but must always carry *some* `Summary` text
(even a short placeholder at creation time) — mirrors ADR's own
mandatory-vs-optional body-field split, not TSK's "must seed a first
Recent Updates entry" pattern (there is no dynamic list here).

**`Gap`/`Future State` are mandatory; `Impact`/`References`/
`More Information` are optional** — matching the plain list the user gave,
plus the newly-added optional `Impact`, placed between `Gap` and
`Future State` (current state → gap → why it matters → target state).

**No Root Cause section** (see Scope: Explicitly out of scope) — this is a
deliberate, methodology-driven omission, not an oversight.

**Update mechanism: whole-body `update_prb(id, content)`**, not an
ADR-style `update_section`. The generic `adr/tools/update_section.py`
mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
ADR-specific code, not a shared cross-domain component — reusing it for
PRB would mean building a second, parallel implementation. Individual
questions/sections stay addressable by grepping/editing their fixed
heading text within the whole-body markdown, which is what "fixed heading
per question" is actually for (addressability without a dedicated tool
per field).

**`list_prb` is a paged tool from day one** (`@mcp.tool(name="list_prb")`
returning `PagedResult[PrbSummary]`, via `general/tools/_paging.py`'s
`paginate`/`normalize_paging`), not a `specmgr://prb/list` resource —
unlike REQ/TSK/QA (which launched as resources and were converted later in
feat-13), PRB is a new domain built *after* ADR ec9f5262 was accepted, so
it must not repeat the resource-then-convert history. `PrbSummary`
subclasses `general/models/summary.py::DocSummary` (`id`/`title`/`status`/
`ref`), like `ReqSummary`/`TskSummary`/`QaSummary`.

**Prompts are narrated instructions only** (return a string, auto-wrapped
as a `UserMessage` by the MCP SDK) — `create_prb`/`update_prb` never call
`TodoWrite`/`question`/`get_prb`/`create_prb`/`update_prb` themselves; they
only narrate that the calling LLM should. This is the same contract every
existing prompt in this codebase already follows
(`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).

- `create_prb(topic: str) -> str`: instructs the LLM to (1) call `list_prb`
  first to check for an existing, similar problem statement (mirrors
  `create_req`'s dedup-check pattern) and ask the user via `question` if a
  near-duplicate is found; (2) build a `TodoWrite` list with one entry per
  the `Summary` + 7 questions + `Gap` + `Impact` + `Future State`; (3) use
  the `question` tool to elicit each of the 7 answers in turn, explicitly
  allowing the user to skip any; (4) synthesize a `Summary` paragraph from
  whichever answers were actually given; (5) draft a candidate `Gap`
  statement from the collected current-state answers (following the
  expected-vs-actual/measurable-difference formula from the
  LearnLeanSigma article) and confirm/refine it with the user via
  `question` before finalizing; (6) optionally ask for `Impact`; (7) ask
  for `Future State` (desired/target condition); (8) optionally ask for
  `References`/`More Information`; (9) assemble the full body markdown per
  the fixed schema above and call `create_prb(content)`.
- `update_prb(id: str) -> str`: instructs the LLM to (1) call `get_prb(id)`
  first (never assume prior state); (2) show the user which of the 7
  questions already have answers and which are still empty, and ask via
  `question` which ones (if any) they want to add to or revise; (3) for
  each selected question, elicit the new/revised text via `question`; (4)
  regenerate the `Summary` from the *complete*, current set of answers
  (a full re-synthesis, not an append); (5) re-draft/refine the `Gap`
  the same way as `create_prb` step 5, based on the now-current-state
  answers, confirming with the user; (6) optionally revise `Impact`/
  `Future State`/`References`/`More Information`; (7) call
  `update_prb(id, content)` (whole-body replace, carrying forward every
  unchanged section); (8) mention `set_status_prb` as a separate, optional
  follow-up (e.g. `resolved` once `Future State` has genuinely been
  reached, `cancelled` if abandoned).

Both prompts' instructional text lives in packaged data files
(`prb/data/prb_create_instructions.md`/`prb_update_instructions.md`, read
via `general.tools._packaged_data.read_packaged_text`, `string.Template`
substitution), matching `req_create_instructions.md`/
`tsk_implement_instructions.md`'s precedent — not an inline Python string
— since the narration is long enough to warrant it.

**Frontmatter status** (`draft`/`active`/`resolved`/`cancelled`) mirrors
TSK/QA's 4-value closed set exactly, with PRB-specific semantics: `draft`
= still being filled in; `active` = current state captured, gap/future
state being refined; `resolved` = future state reached; `cancelled` =
abandoned.

### Related ADRs

- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
  markdown document types
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
  (`get_prb`), not a resource
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
  MCP tool (`list_prb`), not a resource — must be followed from the start
  for this new domain, not retrofitted later
- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
  and explicitly *not* reused for `prb` (see Design Notes)

No new ADR is anticipated for this feature — every schema/tooling decision
either follows an existing ADR's precedent directly or is scoped enough to
log only in this file's own Decisions Made.

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself. Each phase ends with a mandatory phase-end task (tests, full
quality gate, README Progress update), mirroring feat-10/feat-12's
per-phase commit discipline, since implementation is likely to span
multiple sessions.

#### Phase 1: Specification

- [x] Task 1.1: Write a full reference `prb_reference.md`
  (`.specmgr/feat/feat-16-problem-statement/prb_reference.md`) exercising
  every field (all 7 questions answered, `Impact`/`References`/
  `More Information` all present) — depends on: none — status: done
- [x] Task 1.2: Define `prb` frontmatter (`prb/models/v1/frontmatter.py` —
  `PrbFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["prb"]`,
  4-value status set `draft`/`active`/`resolved`/`cancelled`, mirroring
  `TskFrontmatter`'s `_ALLOWED_STATUSES` pattern) — depends on: none —
  status: done
- [x] Task 1.3: Define `prb` body structure
  (`prb/models/v1/body.py`) — `Prb(MarkdownSection1WithComment)`,
  `CurrentState(MarkdownSection2)` with mandatory `summary: Summary` and
  optional `question_1..question_7: Question{N} | None` (each with an
  explicit `@alias(...)` matching the exact 5W2H wording — see Design
  Notes), `Gap`/`FutureState` (mandatory leaves), `Impact`/`References`/
  `MoreInformation` (optional leaves) — depends on: Task 1.2 — status:
  done
- [x] Task 1.4: `tests/prb/models/v1/test_frontmatter.py`, `test_body.py`
  — structural + validation tests mirroring `tests/tsk/models/v1/`/
  `tests/qa/models/v1/`, explicit coverage of mandatory-vs-optional field
  combinations (each of the 7 questions individually absent/present;
  `Impact`/`References`/`More Information` absent/present) — depends on:
  Task 1.3 — status: done
- [x] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite); confirm
  `prb_reference.md` is `specmgr mdformat`-clean; update this README's
  Progress section — depends on: Task 1.1, Task 1.4 — status: done

#### Phase 2: Pydantic Models, Parser & Schema

- [x] Task 2.1: `prb/models/v1/document.py` (`PrbDocument(frontmatter, body)`, mirroring `TskDocument`/`QaDocument`) — depends on: Task 1.3 —
  status: done
- [x] Task 2.2: Implement `parse_prb(text: str) -> PrbDocument` (model-layer
  function, mirrors `parse_tsk`/`parse_qa`) — depends on: Task 2.1 —
  status: done
- [x] Task 2.3: `prb/models/v1/summary.py` (`PrbSummary(DocSummary)`,
  subclassing `general/models/summary.py::DocSummary`, for `list_prb`) —
  depends on: Task 2.1 — status: done
- [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
  optional field (schema-quality parity with REQ/TSK/QA) — depends on:
  Task 2.1 — status: done
- [x] Task 2.5: Implement `generate_prb_schema()` in `commands/schema.py`
  (mirroring `generate_tsk_schema`/`generate_qa_schema`, via
  `PrbDocument.model_json_schema()`) + register `"prb"` in the
  `specmgr schema` doc-type generator registry (`_GENERATORS`); draft
  `docs/prb_schema.json` — depends on: Task 2.1 — status: done
- [x] Task 2.6: `tests/prb/models/v1/test_parser.py` — mirrors
  `TestParseTsk`/`TestParseQa`'s shape (minimal doc, full reference-doc
  round-trip, defaults-when-absent, invalid status, missing-mandatory-
  section `AssertionError`, invalid-field `ValidationError`) — depends on:
  Task 2.2, Task 2.5 — status: done
- [x] Task 2.7: Phase-end quality gate — full pre-commit/quality gate
  including Task 2.6's new tests; update this README's Progress section —
  depends on: Task 2.5, Task 2.6 — status: done

#### Phase 3: MCP Surface

- [x] Task 3.1: `prb/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin
  wrappers over `general/tools/_doc_paths.py` (mirrors `tsk/tools/`/
  `qa/tools/` exactly) — depends on: Task 2.2 — status: done
- [x] Task 3.2: `parse_prb(path: str) -> PrbDocument` tool wrapper
  (`prb/tools/parse_prb.py`) — depends on: Task 3.1 — status: done
- [x] Task 3.3: `create_prb(content: str) -> PrbDocument` tool (body-only
  content; MCP builds frontmatter: `id`, `type="prb"`, `status="draft"`,
  `created=updated=now`, `version`) — depends on: Task 3.1 — status:
  done
- [x] Task 3.4: `update_prb(id, content) -> PrbDocument` tool (whole-body
  replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
  `updated`) — depends on: Task 3.1 — status: done
- [x] Task 3.5: `set_status_prb(id, status) -> PrbDocument` tool (only path
  that changes `status`; reconstructs `PrbFrontmatter` via its own
  constructor so the 4-value validator runs, mirroring `set_status_tsk`/
  `set_status_qa`) — depends on: Task 3.1 — status: done
- [x] Task 3.6: `delete_prb(id) -> NoReturn` stub tool — depends on: Task
  3.1 — status: done
- [x] Task 3.7: `validate_prb(content, full=False) -> bool` tool — depends
  on: none — status: done
- [x] Task 3.8: `get_prb(id) -> PrbDocument` tool (id-based single-document
  read; tool, not resource) — depends on: Task 3.1 — status: done
- [x] Task 3.9: `list_prb(max_results=None, offset=None) -> PagedResult[PrbSummary]`
  tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`
  (default page size 25, cap 100), preserving the standard skip-malformed-
  file scan behavior — depends on: Task 2.3, Task 3.1 — status:
  done
- [x] Task 3.10: `get_prb_example`/`get_prb_template` tools + packaged data
  (`prb/data/prb_example.md`, `prb/data/prb_template.md`) via
  `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:
  done
- [x] Task 3.11: `prb/resources/{prb_schema,prb_example,prb_template}.py`
  — `specmgr://prb/schema` (packaged `prb/data/prb_schema.json`, mirroring
  `specmgr://tsk/schema`), `specmgr://prb/example`, `specmgr://prb/template`
  (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:
  done
- [x] Task 3.12: `pyproject.toml` package-data entry for
  `biz.dfch.specmgr.prb` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`
  — widen the shared schema-hook glob to include `prb/models/v1`, add a
  `specmgr-schema-prb-package` hook — depends on: Task 2.5 — status:
  done
- [x] Task 3.13: `.github/workflows/ci.yml` — add the `docs/prb_schema.json`
  check + packaged-copy check steps — depends on: Task 2.5 — status:
  done
- [x] Task 3.14: `prb/data/prb_create_instructions.md` +
  `prb/prompts/create_prb.py` (`@mcp.prompt()`, `string.Template`
  substitution, narrates the full interview flow — see Design Notes) —
  depends on: Tasks 3.3, 3.9 — status: done
- [x] Task 3.15: `prb/data/prb_update_instructions.md` +
  `prb/prompts/update_prb.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:
  done
- [x] Task 3.16: `prb/__init__.py` (docstring + `from . import prompts, resources, tools`), add `prb` to `server.py`'s bottom-of-file domain
  import line (alphabetical: `adr, general, prb, qa, req, tsk, uc`) and
  update its module docstring (Tools/Resources/Prompts sections) — depends
  on: Tasks 3.2-3.15 — status: done
- [x] Task 3.17: `tests/prb/tools/...`, `tests/prb/resources/...`,
  `tests/prb/prompts/...` mirroring `tests/tsk/`/`tests/qa/`'s layout,
  including live end-to-end coverage of `create_prb`/`update_prb`'s
  narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_prb`'s
  paging behavior (default page size, `max_results` clamping, `offset`
  paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:
  done
- [x] Task 3.18: Phase-end quality gate — full pre-commit/quality gate
  including Task 3.17's new tests; update this README's Progress section
  — depends on: Task 3.17 — status: done

#### Phase 4: Cross-cutting registration

- [x] Task 4.1: `AGENTS.md` — update heading to "seven domain/cross-cutting
  packages implemented (ADR, REQ, UC, TSK, QA, PRB, general)"; add a
  `prb/` bullet (chronological order, after `qa/`); update the "Still
  genuinely missing" list (`validate_prb` not enforced via pre-commit/CI,
  `delete_prb` stub) and the closing domain-enumeration paragraphs —
  depends on: Phase 3 complete — status: done
- [x] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`
  regeneration — confirm `prb` appears correctly and all three commands
  report zero drift — depends on: Task 4.1 — status: done
- [x] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;
  update this README's Progress section — depends on: Task 4.2 — status:
  done

#### Phase 5: Final cross-cutting verification

- [x] Task 5.1: Final verification pass — walk every ACC-001..008 and
  confirm each is satisfied with concrete evidence (including a live
  `create_prb`→`update_prb`→`set_status_prb` run, not just unit tests);
  run the full quality gate (ruff format/check, pylint advisory, vulture,
  unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift
  checks) end to end; set feature status to `done` — depends on: Phase
  1-4 complete — status: done

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**Feature complete, as of 2026-08-25.** All 5 phases done. `prb` (Problem
Statement) is a fully implemented seventh domain/cross-cutting
package (ADR, REQ, UC, TSK, QA, PRB, general), with a domain-first
`prb/models/v1/` schema (frontmatter, body — mandatory `Summary`/`Gap`/
`Future State`, 7 optional 5W2H questions, optional `Impact`/`References`/
`More Information`), a full MCP surface (10 tools including `list_prb` as
a paged tool from day one per ADR ec9f5262, 3 resources, 2 narrated
prompts, packaged data), and `AGENTS.md`/`specmgr docs`/`specmgr mcp-docs`/
`specmgr schema` all up to date and drift-free. Phase 5's final
verification pass walked every ACC-001..008 with concrete evidence
(see the Acceptance Criteria section above for the per-ACC verdicts),
including a live, non-mocked `create_prb`→`update_prb`→`set_status_prb`→
`get_prb`→`list_prb`→`delete_prb`(stub) lifecycle exercise
(`tests/prb/tools/test_integration.py`, isolated to a temp docs
directory), a manual walk-through of both prompts' narrated interview
flows against that same live document, and a real `uv build --wheel` +
scratch-venv, non-editable install confirming packaged data resolves
correctly outside the source tree. Full quality gate green: 1454 tests
(up from 1452), ruff format/check clean, vulture clean, pylint 8.96/10
advisory (pre-existing `redefined-builtin 'id'`/missing-test-docstring/
duplicate-code findings only, no regressions), zero drift in
`specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc`/`specmgr schema`
(both `docs/prb_schema.json` and the packaged copy) beyond
`docs/GENERATED.md`'s expected test-file-count bump (204 → 205).
Note: this feature folder uses the `feat-16-problem-statement` placeholder
id/slug (no GitHub issue filed yet, per `AGENTS.md`'s convention) — expect
it to be renamed to `feat-NNN-problem-statement` (frontmatter `id` updated
to match) once an issue number is assigned; do not treat `feat-0` as
permanent.

### Blockers

None.

### Recent Updates

#### Update 2026-08-25 (Phase 5: Final cross-cutting verification — feature complete)

- Completed Task 5.1, the final task of the feature. Walked every
  ACC-001..008 with concrete evidence (recorded inline in the Acceptance
  Criteria section above, each now checked `[x]`):
  - ACC-001/002/003 (schema/models/parser): confirmed via
    `docs/prb_schema.json`/`specmgr://prb/schema`, `prb_reference.md`'s
    round-trip, and the existing `tests/prb/models/v1/` suite (structural
    `AssertionError`s for each missing mandatory section, `Validation
    Error` for invalid `status`).
  - ACC-004/005 (tools/resources): live `mcp.list_tools()`/
    `list_resources()` calls against the actual `server.mcp` instance
    confirmed all 10 tools and all 3 resources are registered and
    callable; confirmed `list_prb` uses `general/tools/_paging.py`'s
    `DEFAULT_MAX_RESULTS = 25`/`MAX_MAX_RESULTS = 100`.
  - ACC-006 (prompts): read both packaged instruction files in full and
    manually walked their narrated flows end to end against a real
    document (see below), rather than only asserting narration text
    contains the right tool names.
  - ACC-007 (packaged data from a real install): built a real wheel
    (`uv build --wheel`), confirmed all 5 `prb/data/*` files are packaged
    inside it, installed it non-editably into a scratch venv under
    `/tmp/opencode/` (`pip install "biz_dfch_specmgr-...-py3-none-any.whl[mcp]"`),
    and confirmed `get_prb_example()`/`get_prb_template()`/`prb_schema()`
    resolve real content from that venv's `site-packages`, not the source
    checkout (`inspect.getfile` confirmed the module path). Wheel and
    scratch venv cleaned up afterward (`dist/`/`build/` removed; both are
    gitignored anyway).
  - ACC-008 (doc generation drift): re-ran `specmgr docs`/
    `specmgr mcp-docs`/`specmgr adr-toc`/`specmgr schema` (generic + the
    `--type prb --output-dir src/biz/dfch/specmgr/prb/data` packaged-copy
    invocation) — every generated file reported unchanged except
    `docs/GENERATED.md`'s test-file count (204 → 205, expected from this
    phase's own new test file); `AGENTS.md` already reflects seven
    domains from Phase 4.
- Added `tests/prb/tools/test_integration.py` (2 tests): a live,
  non-mocked lifecycle exercise —
  `create_prb`→`update_prb`→`set_status_prb`→`get_prb`→`list_prb`→
  `delete_prb` (confirms the stub still raises `NotImplementedError`
  without touching the filesystem) — plus a packaged
  example/template round-trip-via-`parse_prb` test. Isolated via the same
  `SPECMGR_DOCS_DIR`-pointed-at-a-`tempfile.TemporaryDirectory()` pattern
  already used by `test_create_prb.py`'s `TempPrbDirTestCase`, so nothing
  was ever written to the real, developer-configured `prb` base directory.
  This test doubles as the concrete evidence for ACC-004's "`list_prb`
  reflects the changes" and ACC-006's "verified live" requirements.
- Ran the full quality gate one final time: `ruff format --check`/
  `ruff check` (both clean), `pylint` (advisory, 8.96/10 — the pre-existing
  `redefined-builtin 'id'` (5 `prb` tools/prompts taking an `id` parameter,
  matching every other domain's own convention), missing-test-docstring,
  and `duplicate-code`-across-mirrored-test-files findings only; nothing
  new introduced by this phase's test file), `vulture src/ whitelist.py
  --min-confidence 60` (no findings), full `unittest` suite (**1454
  tests**, up from 1452, all green).
- Set this README's own frontmatter `status: planning` → `status: done`
  (top of file) as Task 5.1's own required action; every phase and every
  acceptance criterion is now checked off.
- Next: None — feature complete. A follow-up feature would be needed to
  (a) file a real GitHub issue and rename this folder from its `feat-16`
  placeholder if desired, (b) implement `delete_prb` for real, or (c)
  wire `validate_prb` (and its five siblings) into pre-commit/CI per
  ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73 — none of that is in this
  feature's scope.
- Notes: No new design decisions required this phase — purely
  verification, exactly as scoped. One clarification for future readers:
  ACC-006's "live" verification, per this phase's own task instructions,
  necessarily means manually executing the narrated flow using the real
  tool functions and self-simulated `question`-tool answers (there is no
  live human user or live MCP client in this environment) — both prompts
  themselves only ever return narration strings, by hard MCP-SDK contract,
  and never call `TodoWrite`/`question`/`list_prb`/`create_prb`/
  `update_prb` themselves; this was already true by design (see Phase 3's
  Decisions Made) and is not a limitation introduced by this
  verification pass.

#### Update 2026-08-25 (Phase 4: Cross-cutting registration)

- Completed Tasks 4.1-4.3. `AGENTS.md`: heading changed to "seven
  domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA, PRB,
  general)"; added a `prb/` bullet (chronological, right after `qa/`)
  describing its domain-first `prb/models/v1/` location, its full tool
  list, its three resources (`specmgr://prb/schema`/`/example`/
  `/template`, no `/{id}`, no `/list`), and its two prompts
  (`create_prb`/`update_prb`); updated the "Still genuinely missing" list
  to add `validate_prb` (alongside the other `validate_*` tools not yet
  enforced via pre-commit/CI) and `delete_prb` (alongside the other
  `delete_*` stubs); updated both closing domain-enumeration paragraphs
  (`Don't assume any other domain package exists beyond ...` and the
  `server.py` bottom-of-file import line description) to include `prb` in
  alphabetical position; updated the "`req`/`tsk`/`qa` each register
  tools, resources, and prompts; `uc` ..." sentence to
  "`req`/`tsk`/`qa`/`prb` each register tools, resources, and prompts;
  `uc` ...".
- Re-ran `specmgr schema` (all five doc types, including a separate
  `--type prb --output-dir src/biz/dfch/specmgr/prb/data` invocation for
  the packaged copy), `specmgr docs`, and `specmgr mcp-docs` — all three
  reported zero drift (only `AGENTS.md` shows as modified in `git
  status`; no generated file changed).
- Phase-end quality gate: `ruff format --check`/`ruff check` (both
  clean), `vulture src/ whitelist.py --min-confidence 60` (no findings),
  full `unittest` suite (1452 tests, unchanged from Phase 3, all green —
  expected, since this phase touched only `AGENTS.md`).
- Next: Phase 5 (Final cross-cutting verification) — walk every
  ACC-001..008 with concrete evidence including a live
  `create_prb`→`update_prb`→`set_status_prb` run, full quality gate end
  to end, set feature status to `done`.
- Notes: No design decisions required; this phase was purely
  documentation (AGENTS.md) plus re-confirming Phase 3's drift-free
  state, exactly as scoped.

#### Update 2026-08-25 (Phase 3: MCP Surface)

- Completed all of Tasks 3.1-3.18. New `src/biz/dfch/specmgr/prb/`
  sub-packages: `tools/` (`_paths.py`/`_io.py`/`_write.py`/`_lock.py`
  plumbing plus `parse_prb`, `create_prb`, `update_prb`, `set_status_prb`,
  `delete_prb` stub, `validate_prb`, `get_prb`, `list_prb`,
  `get_prb_example`, `get_prb_template` -- each a 1:1 port of the
  matching `tsk.tools`/`qa.tools` module, adapted for PRB's 4-value
  status set and mandatory `Gap`/`Future State` fields); `resources/`
  (`specmgr://prb/schema`/`/example`/`/template`, no `/list`, no
  `/{id}`); `prompts/` (`create_prb`/`update_prb`, each reading its own
  packaged instructions file via `string.Template`); `data/`
  (`prb_example.md` -- reused from `prb_reference.md` verbatim,
  `prb_template.md`, `prb_schema.json` -- the packaged copy generated by
  `specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data`,
  `prb_create_instructions.md`, `prb_update_instructions.md`).
  `prb/__init__.py` now imports `prompts`/`resources`/`tools`; `server.py`
  imports `prb` alphabetically (`adr, general, prb, qa, req, tsk, uc`)
  and its module docstring lists every new `prb` resource/tool/prompt.
- `create_prb`'s narrated instructions cover the full 9-step interview
  flow from the plan's Design Notes verbatim: (0) `list_prb` dedup check;
  (1) structure recap; (2) `TodoWrite`-list + `question`-tool-driven 5W2H
  interview, explicitly allowing skip; (3) `Summary` synthesis; (4) `Gap`
  drafting + `question`-tool confirmation; (5) optional `Impact`; (6)
  `Future State`; (7) optional `References`/`More Information`; (8)
  template/example/schema references; (9) the `create_prb(content)` tool
  call sequence. `update_prb`'s instructions cover the symmetric 8-step
  revision flow (read via `get_prb` first, show which of the 7 questions
  are answered, elicit revisions, full re-synthesis of `Summary` -- not
  an append, re-draft/confirm `Gap`, optional revisions to
  `Impact`/`Future State`/`References`/`More Information`,
  `update_prb(id, content)` whole-body replace, `set_status_prb` as a
  separate optional follow-up). Both prompts only ever return narration
  strings -- neither calls `TodoWrite`/`question`/`list_prb`/`get_prb`/
  `create_prb`/`update_prb` itself, matching every existing prompt's
  contract in this codebase.
- `pyproject.toml` gained a `biz.dfch.specmgr.prb` package-data entry
  (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`'s shared
  schema-hook glob now includes `prb/models/v1`, plus a new
  `specmgr-schema-prb-package` hook; `.github/workflows/ci.yml` gained
  the matching `docs/prb_schema.json` + packaged-copy check steps,
  mirroring the existing `tsk`/`qa` steps exactly.
- Added `tests/prb/tools/` (14 test modules mirroring `tests/tsk/tools/`
  file-for-file), `tests/prb/resources/` (3 test modules), and
  `tests/prb/prompts/` (2 test modules, ACC-006: asserting every
  narrated step/tool-call marker is present and, where sequence matters,
  in the correct relative order) -- 146 new tests, all green.
- Verified end to end, live (not just via tests): `create_prb` ->
  `update_prb` -> `set_status_prb` -> `get_prb` -> `list_prb` ->
  `delete_prb` (stub) against a real temp docs directory, plus
  `get_prb_example`/`get_prb_template` returning real, non-empty,
  parseable packaged markdown.
- Phase-end quality gate: `ruff format --check`/`ruff check` (both
  clean), `vulture src/ whitelist.py --min-confidence 60` (no findings
  -- no whitelist additions were needed), full `unittest` suite (1452
  tests, up from 1347, all green), `specmgr schema` (all five doc types,
  including `prb`, unchanged/drift-free), `specmgr docs` (regenerated
  `docs/api/`/`docs/GENERATED.md` with the new `prb` module docs),
  `specmgr mcp-docs` (regenerated `docs/MCP.md` with every new `prb`
  resource/tool/prompt).
- Next: Phase 4 (Cross-cutting registration) -- `AGENTS.md` update,
  final `specmgr docs`/`specmgr schema`/`specmgr mcp-docs` drift
  re-check.
- Notes: No design decisions required beyond following the plan's Design
  Notes and the TSK/QA precedent files verbatim; one deliberate,
  in-scope deviation from a literal reading of Task 3.10 -- `prb_example.md`
  reuses `prb_reference.md`'s exact content (including its id) rather than
  a freshly drafted document, following QA's own precedent
  (`qa_example.md`/`qa_reference.md` share the same id and content too).

#### Update 2026-08-25 (Phase 2: Pydantic Models, Parser & Schema)

- Completed: Task 2.1 (`prb/models/v1/document.py::PrbDocument`, mirroring
  `TskDocument`/`QaDocument` exactly); Task 2.2
  (`prb/models/v1/parser.py::parse_prb`, mirroring `parse_tsk`/`parse_qa`'s
  frontmatter/body split via `python-frontmatter` and the same two-error-
  channel convention); Task 2.3 (`prb/models/v1/summary.py::PrbSummary`,
  subclassing `general/models/summary.py::DocSummary`); Task 2.4 (verified
  Phase 1's `body.py` already carries `Field(description=...)` on every
  scalar/optional field, matching REQ/TSK/QA precedent for
  schema-quality parity — no changes needed since Phase 1 already covered
  this; `frontmatter.py` deliberately has no `Field(description=...)`,
  matching `TskFrontmatter`/`QaFrontmatter`'s own precedent of relying on
  the class docstring instead); Task 2.5 (`generate_prb_schema()` added to
  `commands/schema.py`, registered as `"prb"` in `_GENERATORS`,
  `docs/prb_schema.json` generated via `uv run --frozen specmgr schema`
  — confirmed byte-identical/unchanged on a second run); Task 2.6
  (`tests/prb/models/v1/test_parser.py`, 9 tests: minimal doc, full
  reference-doc round-trip, defaults-when-absent, invalid status,
  3 missing-mandatory-section `AssertionError` cases (`Current State`,
  `Gap`, `Future State`, plus missing `Summary` within `Current State`),
  invalid-`type`-field `ValidationError`); Task 2.7 (phase-end quality
  gate — ruff format/check, vulture, full `unittest` suite (1347 tests, up
  from 1338, all green), `specmgr docs`/`specmgr mcp-docs` confirmed no
  unexpected drift beyond the new `prb` entries).
- Also added `SCHEMA_COMMENT_VERSION` via a new
  `prb/models/v1/_util.py`, mirroring `tsk/models/v1/_util.py` exactly,
  and re-exported it (plus `PrbDocument`/`parse_prb`/`PrbSummary`) from
  `prb/models/v1/__init__.py`.
- Next: Phase 3 (MCP Surface) — tools, resources, prompts, packaged data.
- Notes: No design decisions required beyond following the plan's Design
  Notes and the TSK/QA precedent files verbatim.

#### Update 2026-08-25 (Phase 1: Specification)

- Completed: Task 1.1 (`prb_reference.md`, exercising all 7 5W2H questions
  plus `Impact`/`References`/`More Information`); Task 1.2
  (`prb/models/v1/frontmatter.py::PrbFrontmatter`, 4-value status set);
  Task 1.3 (`prb/models/v1/body.py` — `Prb`, `CurrentState`,
  `Question1`..`Question7` with explicit regex `@alias`es matching the
  exact 5W2H wording, `Gap`/`FutureState`/`Impact`/`References`/
  `MoreInformation` leaves); Task 1.4 (`tests/prb/models/v1/`
  `test_frontmatter.py`/`test_body.py`, 32 tests total, covering each of
  the 7 questions and `Impact`/`References`/`More Information` both
  absent/present individually, plus the full reference document's
  round-trip); Task 1.5 (phase-end quality gate — ruff format/check,
  vulture, full `unittest` suite (1338 tests, all green),
  `prb_reference.md` confirmed `specmgr mdformat`-clean).
- Also created the supporting domain-package skeleton needed for the
  models to be importable ahead of Phase 3: `prb/__init__.py` (docstring
  only, no `prompts`/`resources`/`tools` imports yet — those don't exist
  until Phase 3 Task 3.16), `prb/models/__init__.py`,
  `prb/models/v1/__init__.py` (aggregating `PrbFrontmatter` + body
  classes; `PrbDocument`/`parse_prb`/`PrbSummary` are added in Phase 2).
  Added `current_state`/`gap`/`impact`/`future_state`/`summary`/
  `question_1`..`question_7` to `whitelist.py` (new Pydantic field names
  vulture cannot otherwise see as used).
- Next: Phase 2 (Pydantic Models, Parser & Schema) — `PrbDocument`,
  `parse_prb`, `PrbSummary`, `generate_prb_schema()`, parser tests.
- Notes: Followed the plan's Design Notes schema verbatim; no ambiguity
  encountered requiring a design decision beyond what's already logged.

#### Update 2026-08-25 (planning)

- Completed: Full design/planning discussion — schema shape (5W2H
  questions under `Current State`, `Gap`/`Impact`/`Future State`/
  `References`/`More Information`), status set, update mechanism, prompt
  behavior, and MCP surface all decided; this README written from that
  discussion. Also flagged (but explicitly did not fix, as out of scope
  here) that `AGENTS.md`'s TSK/QA `specmgr://<d>/list` bullets are stale
  post-`feat-13-list-paging` — added as `feat-7-various-improvements`
  Task 0.24 instead.
- Next: Phase 1 (Specification) — write `prb_reference.md`, define
  frontmatter/body models.
- Notes: No implementation attempted this session by design (planning-only
  session per explicit user instruction).

### Decisions Made

- **2026-08-25**: Type abbreviation `prb`, domain-first layout
  (`prb/models/v1/`, `prb/tools/`, `prb/resources/`, `prb/prompts/`,
  `prb/data/`) — matches TSK/QA precedent (schema lives inside the domain
  package, not top-level `models/`), since PRB is a new domain built after
  the domain-first refactor.
- **2026-08-25**: 5W2H question set taken verbatim from the iSixSigma
  article (What/Why/Where/Who/When/How/How Often), each a fixed, optional
  H3 heading under a mandatory `## Current State` H2 with a mandatory
  `### Summary` leaf. Question heading wording is the plain question text
  (not numbered) — chosen over "Question N: ..." for readability.
- **2026-08-25**: Status set `draft`/`active`/`resolved`/`cancelled` —
  reuses TSK/QA's 4-value pattern/wording convention, with PRB-specific
  semantics.
- **2026-08-25**: `update_prb` is a single whole-body replace tool
  (REQ/TSK/QA convention), not an ADR-style `update_section`/option-style
  granular tool — the latter is currently ADR-specific code (ADR
  71fd95d7), and porting it was judged not worth the added scope for this
  feature. Individual questions/sections remain addressable by their fixed
  heading text within the whole-body markdown.
- **2026-08-25**: `References` is opaque free text for v1 (like
  `MoreInformation`/`Notes`), not structured by artifact type — deferred,
  matching every other domain's own "defer structured cross-linking"
  decision.
- **2026-08-25**: Added an optional `Impact` H2 (between `Gap` and
  `Future State`) per user request, to hold business/cost/safety
  consequence separately from `Gap` itself (which stays a pure
  actual-vs-expected measurement, per the LearnLeanSigma article's
  explicit warning against conflating gap and consequence).
- **2026-08-25**: No `Root Cause` section — deliberately excluded per Six
  Sigma discipline (both source articles explicitly warn against including
  assumed causes in a problem statement); any future RCA artifact type
  would be a separate feature, only ever referenced from `References`.
- **2026-08-25**: `list_prb` ships as a paged `@mcp.tool()` from day one
  (per ADR ec9f5262, already accepted/`done` via feat-13) — this domain
  must not repeat REQ/TSK/QA's original resource-then-later-converted
  history.
- **2026-08-25**: Prompt names `create_prb`/`update_prb` (tool-name
  convention, like REQ/QA), not literal wording like TSK's
  `create_task`/`update_task`/`implement_task`.
- **2026-08-25**: GitHub issue not yet filed — feature folder uses the
  `feat-16-problem-statement` placeholder per `AGENTS.md`'s convention;
  rename the folder (and this frontmatter `id`) once/if an issue number is
  assigned.
- **2026-08-25**: `AGENTS.md`'s pre-existing TSK/QA `specmgr://<d>/list`
  drift (found during this planning session) is fixed under
  `feat-7-various-improvements` Task 0.24, not here — out of scope for
  this feature.
- **2026-08-25** (Phase 1): Each `Question{N}`'s `@alias` uses
  `AliasType.REGEX` (e.g. `@alias(value=r"What Is the Problem\?",
  type=AliasType.REGEX)`), not `AliasType.LITERAL` — the plan's own Design
  Notes ASCII diagram already showed the wording with a backslash-escaped
  `?` (`"What Is the Problem\\?"`), which is regex-escaping syntax, not
  needed for a `LITERAL` exact-string match; `REGEX` was chosen to follow
  that notation literally.
- **2026-08-25** (Phase 1): `prb/__init__.py`/`prb/models/__init__.py`/
  `prb/models/v1/__init__.py` were created now (Phase 1), ahead of their
  explicit task mentions (Task 3.16 for `prb/__init__.py`), purely as the
  minimal package skeleton needed for `prb.models.v1.frontmatter`/`.body`
  to be importable at all — mirroring `tsk`/`qa`'s per-level `__init__.py`
  convention (unlike `req`, which lacks a `req/models/__init__.py`).
  `prb/__init__.py` deliberately does not yet import `prompts`/
  `resources`/`tools` (none exist yet); Task 3.16 will extend it, not
  replace it.

### Related PRs / Commits

No PR opened yet (no GitHub issue filed, per the `feat-16` placeholder
note above). Commits landed on the `feat-16-problem-statement` branch so
far (oldest first):

- `cef8719` — feat(prb): add feat-16 "Problem Statement" (prb) with design
  and plan
- `d41e05f` — feat(prb): add PRB frontmatter/body models and reference doc
  (Phase 1)
- `0b90429` — feat(prb): add PrbDocument, parse_prb, PrbSummary, and
  schema generation (Phase 2)
- `d01ea82` — feat(prb): add full MCP surface — tools, resources,
  prompts, packaged data (Phase 3)
- `1f87745` — docs(prb): update AGENTS.md for seven domain/cross-cutting
  packages (Phase 4)
- Phase 5 (this final verification pass) is not yet committed as of this
  writing — left for the orchestrator to review and commit.
