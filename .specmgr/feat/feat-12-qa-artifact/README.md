---
created: '2026-08-18 00:00:00.000Z'
id: feat-12-qa-artifact
status: done
updated: '2026-08-18 00:00:00.000Z'
version: 1.0.0
---

# Feature: Question and Answer (QA) artifact type

## Plan

### Overview

A new `qa` document-type domain: a requirements-elicitation interview structured
around the fixed ISO/IEC 25010:2023 quality-characteristic categories (plus
`General` and `More Information`), each holding a repeating list of
question/answer pairs, with an optional embedded `Requirement` callout per
answer holding arbitrary, deliberately unspecified agent-authored content.
Follows the domain-first hierarchy (ADR
ece4554b-725c-4f76-bc04-5d2b760363d2) and is modeled most closely on `req/`
(single artifact per file, no ADR-style dynamic option tooling, no UC-style
dual schema versions). Introduces the project's first real domain use of
`MarkdownBlockQuote`, and a new, generalized `@markdown(end_marker=...)`
mechanism in the shared `models/md` engine.

### Requirements

- REQ-001: Generalize `models/md`'s `@markdown` decorator and
  `MarkdownSection.get_extent` with a depth-aware `end_marker` stop
  condition — a standalone, reusable engine capability, not `qa`-specific,
  needed so a composite section (e.g. an embedded `Requirement` H4) can stop
  at the next block quote instead of only at the next heading.
- REQ-002: Define the `qa` markdown schema (frontmatter + body) — H1 title;
  fixed H2s (`General`, the 9 ISO 25010:2023 characteristics, `More Information`); repeating `QaSection` (H3) Q&A pairs inside each
  ISO-characteristic H2; special fixed `Introduction`/`Raw Requirements` H3s
  inside `General`.
- REQ-003: Pydantic models under `qa/models/v1/` (frontmatter, body,
  document, parser, summary), status set reused from TSK
  (`draft`/`active`/`done`/`cancelled`).
- REQ-004: Parse/validate `qa` documents from markdown, mirroring
  `parse_req`/`parse_tsk`'s two-error-channel convention
  (`AssertionError`/`pydantic.ValidationError`).
- REQ-005: MCP tools/resources/prompts mirroring REQ's surface: `parse_qa`,
  `get_qa`, `get_qa_example`, `get_qa_template`, `create_qa`, `update_qa`,
  `set_status_qa`, `delete_qa` (stub), `validate_qa`; resources
  `specmgr://qa/schema`, `/example`, `/template`, `/list` (no `/{id}`, per
  ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614); prompts `create_qa`,
  `update_qa`.
- REQ-006: Full cross-cutting registration (`server.py`,
  `commands/schema.py`, `pyproject.toml`, `.pre-commit-config.yaml`, CI,
  `AGENTS.md`) and test coverage mirroring `tests/req/`'s layout.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — `@markdown(...)` merges into any inherited
  `_metadata` instead of replacing it (regression-tested against all
  existing `models/md` classes); a class declaring `end_marker=X` stops
  `MarkdownSection.get_extent`'s scan at the first *depth-0* occurrence of
  `X`'s token type, not the first occurrence anywhere (nested/legitimate
  occurrences one level deeper do not truncate).
- [ ] ACC-002: Verifies REQ-002 — a full reference `qa_reference.md`
  document exercising every field (including `General`'s special structure,
  every ISO characteristic category, an embedded `Requirement` callout, and
  `More Information`) parses successfully.
- [ ] ACC-003: Verifies REQ-003 — Pydantic models validate required/optional
  fields correctly; `QaFrontmatter.status` rejects any value outside the
  four-value set.
- [ ] ACC-004: Verifies REQ-004 — parser produces a valid object tree for a
  well-formed document; malformed structure raises `AssertionError`; invalid
  field values raise `pydantic.ValidationError`.
- [ ] ACC-005: Verifies REQ-005 — every listed tool/resource/prompt is
  registered and callable via the MCP server.
- [ ] ACC-006: Verifies REQ-006 — `specmgr docs`, `specmgr mcp-docs`, and
  `specmgr schema --type qa` all run clean with no drift; CI/pre-commit
  hooks cover the new domain.

### Scope

**Included in this feature:**

- The `@markdown(end_marker=...)` engine enhancement in `models/md`
  (Phase 1) — a standalone, reusable addition, exercised for the first time
  by `qa`'s embedded `Requirement` callout.
- The `qa` markdown schema, Pydantic models, parser, and summary.
- MCP tools, resources, and prompts, in the same shape as REQ.
- Example/template packaged data files, generated JSON Schema.
- Full test suite mirroring `tests/req/`'s layout, plus new `models/md`
  tests for Phase 1.
- Cleanup of stray, untracked, empty scaffold directories left over from an
  earlier session (see Decisions Made).

**Explicitly out of scope (for v1):**

- Cross-document validation of an embedded `requirement` callout's content
  against real REQ documents (e.g. checking it against an actual
  `req-*.md` file, or promoting it into one).
- Characteristic-based filtering/search over `qa` documents (same
  deferral REQ made for its own `characteristics`).
- Any rendering/exporting of `qa` documents to non-markdown formats.

### Dependencies

- Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy), ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure),
  ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (tool-only id-based reads);
  the existing, already-tested `MarkdownBlockQuote` class
  (`models/md/markdown_block_quote.py`); the existing `Iso25010`/
  `parse_iso25010` model and `specmgr://iso25010` resource
  (`models/iso25010.py`), whose 9 characteristic names are the canonical
  source for `qa`'s fixed H2 set.
- Blocks: None identified yet.

### Design Notes

**Schema (finalized during planning discussion):**

```
QaFrontmatter(MarkdownFrontmatter): type: Literal["qa"];
  status in {draft, active, done, cancelled} (reused from TSK's set)

Qa(MarkdownSection1)                          # H1, free-form title (alias ".+")
├── general: General                           # always present
├── functional_suitability: <QaCategory>        # always present, items may be empty
├── performance_efficiency: <QaCategory>
├── compatibility: <QaCategory>
├── interaction_capability: <QaCategory>
├── reliability: <QaCategory>
├── security: <QaCategory>
├── maintainability: <QaCategory>
├── flexibility: <QaCategory>
├── safety: <QaCategory>
└── more_information: MoreInformation | None    # leaf, opaque raw text (mirrors REQ's MoreInformation)

General(MarkdownSection2WithComment)              # inherited `comment: MarkdownComment | None`, not redeclared
├── introduction: Introduction                  # always present
└── raw_requirements: RawRequirements            # always present

Introduction(MarkdownSection3WithComment)         # inherited `comment: MarkdownComment | None`, not redeclared
└── body: list[MarkdownParagraph] | None

RawRequirements(MarkdownSection3)                # leaf, opaque raw text (mirrors MoreInformation/Notes)

<QaCategory>(MarkdownSection2)                   # one of the 9 ISO characteristic H2s; fixed, exact heading name (not free-form)
└── items: list[QaSection] | None                # repeating Q&A pairs; category may be empty

QaSection(MarkdownSection3WithComment)            # one Q&A pair, free-form H3 heading (alias ".+"); inherited `comment`, not redeclared
├── requirement: Requirement | None              # @markdown(end_marker=MarkdownBlockQuote) -- new mechanism
├── question: MarkdownBlockQuote | None
└── answer: QaAnswer | None                      # leaf, opaque raw text (mirrors MoreInformation/Notes)
```

All fields on `QaSection` (`requirement`/`question`/`answer`), plus the
inherited `comment`, are fully optional.

**`requirement`'s content is deliberately unspecified.** Unlike
`RawRequirements`/`MoreInformation`/`QaAnswer` (which are leaf classes for
the *same* reason -- capturing free-form markdown verbatim), `requirement`
is called out separately here because its purpose differs: it exists to
hold whatever an *agent* (not a human author) chooses to write when it
determines a given Q&A answer implies a concrete requirement, with no
enforced shape (not REQ's own `statement`/`level`/etc. fields, not any
other structure). This is intentional -- the field's value is exactly
"arbitrary agent-authored content," not a gap to close later.

**The `end_marker` engine problem this schema exposed, and its resolution:**
placing `requirement` (an H4 section) before `question` (a block quote) in
field-declaration order only parses correctly if `requirement`'s own
`get_extent` knows to stop *before* the next block quote, not just the next
heading — `MarkdownSection.get_extent`'s existing stop condition only ever
checks heading tokens (verified against its actual implementation), so a
block quote following a `requirement` section would otherwise be silently
absorbed into it. Resolved by adding a generalized, declarative
`end_marker` parameter to `@markdown(...)` rather than a one-off
`get_extent` override on a single class — but only after confirming (a) the
existing decorator does a full, unconditional `_metadata` replace with no
merge against inherited data (verified: every one of the 11 existing
`@markdown(...)` call sites in `models/md/` applies the decorator exactly
once — the `*WithComment` classes inherit it rather than re-applying it —
so this exact drift risk has no precedent yet, but would be hit
immediately by a further subclass adding `end_marker` on top of
`MarkdownSection4`), so the decorator itself must switch to merge-into-
inherited semantics first (Task 1.1, verified 100% backward compatible
against all existing call sites); and (b) a block quote has no notion of
heading "levels", so the stop condition must be depth-aware (via
`Token.nesting`, tracking open/close pairs — already an established idiom in
`models/md`, used by `markdown_section`/`markdown_block_quote`/
`markdown_comment`/`markdown_code_block`/`markdown_paragraph`/
`markdown_list_item`, so this reuses an existing pattern rather than
introducing one) rather than "stop at the first occurrence anywhere" —
otherwise a legitimately nested block quote inside `requirement`'s own valid
content would cause premature truncation.

**Deliberately deferred to Phase 3 (not blocking this plan):** whether the 9
`<QaCategory>` H2 sections share one parameterized base class (9 distinct
final subclasses, each deriving its own fixed heading name from its class
name via the existing implicit `AliasType.SPACE_SEPARATED` convention) or
need a more bespoke approach; `models/iso25010.py::Characteristic` was
checked as a possible reuse candidate but its field shape (`description` +
`sub_characteristics`) doesn't match `qa`'s `items: list[QaSection]` need,
so it is a naming/pattern precedent only, not directly reusable.

**ISO 25010:2023 characteristic names, verified exact wording:** fetched
directly via the `specmgr://iso25010` MCP resource (not just read from the
packaged `.md` file) to confirm the canonical spelling/casing each
`<QaCategory>` heading must match: `Functional Suitability`, `Performance Efficiency`, `Compatibility`, `Interaction Capability`, `Reliability`,
`Security`, `Maintainability`, `Flexibility`, `Safety`. The schema's
snake_case field names above (`functional_suitability`,
`performance_efficiency`, etc.) already correspond 1:1 to this exact
wording.

**`Introduction`/`RawRequirements`'s implicit alias derivation is kept as
relying on `AliasType.SPACE_SEPARATED` class-name derivation (no explicit
`@alias`), intentionally** -- not changed to an explicit `@alias`
declaration, per direct instruction.

**`answer`/`raw_requirements`/`more_information` as opaque raw text:**
verified against the actual `MarkdownStr.from_text`/`get_extent`
implementation that a class with no declared `MarkdownStr`-typed fields
already captures "any remaining markdown text" verbatim in `_value` — this
is exactly how REQ's existing `MoreInformation`/`Notes` classes already
work (bare `MarkdownSection2` subclasses with no further fields). No new
engine mechanism is needed for this part; it is only the `requirement`
field's placement *before* `question` that required the `end_marker` work
above.

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

**Execution approach** (decided 2026-08-18, see Decisions Made): because
implementation is likely to span multiple sessions (context-size
constrained), each phase below ends with a mandatory phase-end task —
extend/run that phase's unit tests, run the full pre-commit/quality gate
(ruff format/check, vulture, full `unittest` suite), and update this
README's Progress section (Current Status, a dated Recent Updates entry,
and Decisions Made if applicable) — before the phase is considered done or
a session ends. Each phase is committed as one Conventional Commit,
mirroring feat-10's per-phase test-and-commit discipline
(`.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md`), adopted
here explicitly so a fresh-context session can resume correctly from this
file alone. Phase 4 and Phase 5 each gain their own dedicated test task
(new task numbers, not renumbered into the existing sequence) rather than
deferring all MCP-surface/cross-cutting testing to a terminal phase; Phase
6 is repurposed accordingly to a final cross-cutting verification pass
only (mirroring feat-10's own Phase 4), not where tests get written for
the first time.

#### Phase 0: Cleanup

- [x] Task 0.1: Delete stray untracked scaffolding from an earlier session
  — `src/qa/` (wrong namespace, missing `biz/dfch/specmgr/` prefix),
  `src/biz/dfch/specmgr/qa/{tools,resources,prompts}/` (empty, no
  `models/`), `tests/qa/` (empty), and `biz/dfch/specmgr/qa/` (top-level,
  wrong -- missing `src/` prefix entirely). All confirmed empty
  directories, untracked by git (git does not track empty directories, so
  none of these show up in `git status`). Do not reuse any of these. Note:
  a previously-listed `models/qa/v1/` path does **not** exist on disk
  (verified) — there is nothing to delete there. Note: `tests/qa/` is
  deliberately deleted here and re-created later by Task 4.5 as the real
  test location (mirroring `tests/req/`); this is intentional, not a
  contradiction — depends on: none — status: done.

- [x] Task 0.2: Phase-end check (lightweight — no code/tests affected by a
  pure directory deletion) — confirm `git status` and `git status --ignored` show no residue from the deleted paths; update this README's
  Progress section (Current Status, a dated Recent Updates entry) noting
  Phase 0 complete — depends on: Task 0.1 — status: done.

#### Phase 1: `models/md` engine enhancement

Standalone, reusable addition to the shared engine; `qa` is its first real
consumer but not the motivating point on its own.

- [x] Task 1.1: Change `@markdown(...)` to merge into any inherited
  `_metadata` rather than fully replacing it — depends on: none — status:
  done.

- [x] Task 1.2: Add `end_marker: type[MarkdownStr] | None = None` parameter
  to `@markdown` — depends on: Task 1.1 — status: done.

- [x] Task 1.3: `MarkdownSection.get_extent` — add a depth-aware (via
  `Token.nesting`) stop condition for `cls._metadata.get("end_marker")`'s
  `type`/`tag`, alongside the existing heading-level check; only a depth-0
  occurrence stops the scan — depends on: Task 1.2 — status: done.

  Note on "depth-0": A real correctness nuance for Phase 1's depth-aware end_marker check. `Token.nesting` itself is already used across `models/md` (see Design Notes), so the primitive is not new — the new part is applying it as a depth counter inside `get_extent`'s stop scan. The plan says "depth-0 occurrence" via Token.nesting, which is correct in principle, but it's worth being explicit now: the depth counter must track every nesting open/close pair in the token stream (list items, other block quotes, etc.), not just the end_marker type's own open/close tokens. Otherwise, e.g., a bullet list legitimately nested inside requirement's own body would throw off the depth count, and a block quote appearing after it could be misjudged as depth-0 when it's actually still nested one level deep — or vice versa. This is exactly the kind of easy-to-get-subtly-wrong logic Task 1.4's edge-case test needs to specifically exercise (a nested list and a nested block quote both inside requirement's own valid content, not just one or the other).

- [x] Task 1.4: Unit tests — merge-semantics regression (all existing
  `models/md` classes unaffected), new `end_marker` stop behavior, and the
  nested/legitimate-occurrence edge case (an end-marker-type token
  appearing one level deeper inside otherwise-valid content must not
  truncate) — depends on: Task 1.3 — status: done.

- [x] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite covering Task
  1.4's new tests plus the full existing suite for regressions); update
  this README's Progress section (Current Status, a dated Recent Updates
  entry, Decisions Made if applicable); commit as one Conventional Commit
  — depends on: Task 1.4 — status: done (commit itself left to the
  orchestrator, per this session's instructions).

#### Phase 2: Specification

- [x] Task 2.1: Write a full reference `qa_reference.md` exercising every
  field — depends on: Phase 1 complete — status: done.

  **Plan correction (2026-08-18, see Decisions Made):** the former Task
  2.2 ("Draft `qa_schema.json`") has moved to Phase 3 as Task 3.1.1 —
  schema generation needs `QaDocument` to exist
  (`QaDocument.model_json_schema()`), which isn't defined until Task 3.1,
  not just the reference markdown file this phase produces (same bug
  feat-10 hit and fixed in its own Decisions Made log, moving its
  equivalent task from Phase 1 to Phase 2 as Task 2.5). Task numbering is
  intentionally left with a gap at 2.2 rather than renumbering Task 2.3
  or any later task.

- [x] Task 2.3: Phase-end check — no Pydantic models exist yet in this
  phase, so no unit-test suite applies; instead confirm `qa_reference.md`
  is well-formed (`specmgr mdformat` clean) and run the general
  pre-commit/quality gate (ruff format/check, vulture) over any changed
  files; update this README's Progress section (Current Status, a dated
  Recent Updates entry) noting Phase 2 complete — depends on: Task 2.1 —
  status: done.

#### Phase 3: Pydantic Models & Parser

- [x] Task 3.1: `qa/models/v1/{frontmatter,body,document,parser,summary, _util}.py`, including `Requirement`'s `end_marker` wiring (leaf class,
  deliberately unspecified/arbitrary agent-authored content -- see Design
  Notes) and resolving the 9-category class-sharing question (see Design
  Notes) — depends on: Task 2.1 — status: done.

- [x] Task 3.1.1 (moved from former Phase 2 Task 2.2, folded together with
  former Phase 5 Task 5.2, see Decisions Made): Implement
  `generate_qa_schema()` in `commands/schema.py` (mirroring
  `generate_req_schema`/`generate_uc_schema`/`generate_tsk_schema`, via
  `QaDocument.model_json_schema()`, JSON Schema 2020-12) and register
  `"qa"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`); draft `docs/qa_schema.json` by running it — mirrors
  feat-10's own Task 2.5 exactly (generator + registry + draft, as one
  task, right after the document model exists) — depends on: Task 3.1 —
  status: done.

- [x] Task 3.2: Unit tests + full parser round-trip against
  `qa_reference.md` — depends on: Task 3.1 — status: done.

- [x] Task 3.3: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite including Task
  3.2's new tests); update this README's Progress section (Current
  Status, a dated Recent Updates entry, Decisions Made if applicable);
  commit as one Conventional Commit — depends on: Task 3.1.1, Task 3.2 —
  status: done (commit itself left to the orchestrator, per this
  session's instructions).

#### Phase 4: MCP Surface

- [x] Task 4.1: `qa/tools/{_paths,_io,_lock,_write,parse_qa,get_qa, get_qa_example,get_qa_template,create_qa,update_qa,set_status_qa, delete_qa,validate_qa}.py` — 1:1 port of REQ's tool plumbing — depends
  on: Task 3.1 — status: done.

- [x] Task 4.2: `qa/resources/{qa_schema,qa_example,qa_template, qa_list}.py` — depends on: Task 4.1 — status: done.

- [x] Task 4.3: `qa/prompts/{create_qa,update_qa}.py` — depends on: Task
  4.1 — status: done.

- [x] Task 4.4: `qa/data/{qa_example.md,qa_template.md,qa_schema.json}` +
  `qa/__init__.py` — depends on: Tasks 4.1-4.3 — status: done.

- [x] Task 4.5: `tests/qa/{tools,resources,prompts}/` mirroring
  `tests/req/{tools,resources,prompts}/`'s layout and coverage — depends
  on: Tasks 4.1-4.4 — status: done.

- [x] Task 4.6: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite including Task
  4.5's new tests); update this README's Progress section (Current
  Status, a dated Recent Updates entry, Decisions Made if applicable);
  commit as one Conventional Commit — depends on: Task 4.5 — status:
  done (commit itself left to the orchestrator, per this session's
  instructions).

#### Phase 5: Cross-cutting registration

- [x] Task 5.1: `server.py` — add `qa` to the bottom import line, update
  the module docstring — depends on: Phase 4 complete — status: done.

  **Plan correction (2026-08-18, see Decisions Made):** the former Task
  5.2 (`generate_qa_schema()` + registry entry) has been folded into
  Phase 3's Task 3.1.1 instead, right after `QaDocument` is defined,
  mirroring feat-10's own Task 2.5. Task numbering is intentionally left
  with a gap at 5.2 rather than renumbering Tasks 5.3-5.8.

- [x] Task 5.3: `pyproject.toml` — `"biz.dfch.specmgr.qa" = ["data/*.md", "data/*.json"]` package-data entry — depends on: Task 4.4 — status:
  done.

- [x] Task 5.4: `.pre-commit-config.yaml` — widen the shared schema-hook
  glob to include `qa/models/v1`; add a `specmgr-schema-qa-package` hook —
  depends on: Task 3.1.1 — status: done.

- [x] Task 5.5: `.github/workflows/ci.yml` — add the `docs/qa_schema.json`
  check + packaged-copy check steps — depends on: Task 3.1.1 — status:
  done.

- [x] Task 5.6: `AGENTS.md` — update to six domain/cross-cutting packages
  — depends on: Phase 5 complete — status: done.

- [x] Task 5.7: `specmgr docs` / `specmgr mcp-docs` regeneration, `specmgr schema --type qa` — confirm the `qa` domain appears correctly and all
  three commands report zero drift now that registration (Task 3.1.1,
  Tasks 5.1, 5.3-5.6) is complete — depends on: Task 3.1.1, Task 5.1,
  Tasks 5.3-5.6 — status: done.

- [x] Task 5.8: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite); update this
  README's Progress section (Current Status, a dated Recent Updates
  entry, Decisions Made if applicable); commit as one Conventional Commit
  — depends on: Task 5.7 — status: done (commit itself left to the
  orchestrator, per this session's instructions).

#### Phase 6: Final cross-cutting verification

- [x] Task 6.1: Final verification pass — walk every ACC-001..006 and
  confirm each is satisfied with concrete evidence; run the full quality
  gate (ruff format/check, pylint advisory, vulture, unittest, `specmgr docs`, `specmgr mcp-docs`, `specmgr schema --type qa` drift checks) one
  last time end-to-end; update this README's Progress section (Current
  Status, a dated Recent Updates entry) and set feature status to `done`
  — depends on: Phase 0-5 complete — status: done.

## Progress

### Current Status

**As of 2026-08-18**: Feature complete — all 6 phases done, Task 6.1 (Final
verification pass) confirmed all six acceptance criteria satisfied with
concrete evidence and the full quality gate green end-to-end. Feature
status set to `done`. Phase 0 (Cleanup), Phase 1 (`models/md` engine
enhancement), Phase 2 (Specification), Phase 3 (Pydantic Models & Parser),
Phase 4 (MCP Surface), Phase 5 (Cross-cutting registration), and Phase 6
(Final cross-cutting verification) complete — Tasks 1.1-1.5, 2.1/2.3,
3.1/3.1.1/3.2/3.3, 4.1-4.6, 5.1/5.3-5.8, and 6.1 done (intentional gap at
5.2, folded into Task 3.1.1 earlier in the plan). ACC-001 (merge-semantics
regression + depth-0 `end_marker` stop condition, 18 tests in
`tests/models/md/test_markdown.py`/`test_markdown_section_end_marker.py`),
ACC-002 (`qa_reference.md` re-verified to parse successfully via
`parse_qa` on the current committed state), ACC-003 (35 tests in
`tests/qa/models/v1/test_frontmatter.py`/`test_body.py` covering
required/optional field validation and the four-value `status` closed
set), ACC-004 (`tests/qa/models/v1/test_parser.py` covering a valid
object tree, `AssertionError` on malformed structure, and
`pydantic.ValidationError` on invalid field values), ACC-005 (live
`biz.dfch.specmgr.server.mcp` introspection confirming all 9 tools, 4
resources, and 2 prompts registered and callable), and ACC-006 (fresh
`specmgr docs`/`specmgr mcp-docs`/`specmgr schema --type qa` runs, all
reporting zero drift) were each independently re-verified this phase, not
just trusted from earlier phase reports. The
`qa` domain is now fully registered end-to-end: `server.py`'s bottom-of-file
import line reads `from . import adr, general, qa, req, tsk, uc`, and its
module docstring documents `qa`'s four resources (`specmgr://qa/schema`,
`/example`, `/template`, `/list`, no `/{id}`), nine tools, and two prompts
alongside the other domains. `pyproject.toml` packages `qa/data/*.md` and
`*.json`; `.pre-commit-config.yaml`'s shared schema-hook glob now matches
`qa/models/v1` and a new `specmgr-schema-qa-package` hook keeps
`qa/data/qa_schema.json` in sync; `.github/workflows/ci.yml` gained a
`docs/qa_schema.json` + packaged-copy check pair mirroring REQ/UC's. Note:
as already established at the end of Phase 4, this registration wiring was
*functionally* redundant with the transitive import `commands/schema.py`
already causes via `qa.models.v1` (so `docs/MCP.md` and `docs/GENERATED.md`
already listed all of `qa`'s tools/resources/prompts before this phase and
needed no regeneration here beyond `docs/api/biz.dfch.specmgr.server.md`,
which changed solely due to the docstring edit) -- Task 5.1 was still done
for documented-convention clarity/correctness, per `AGENTS.md`'s own
"add its import to that same last line" instruction. `AGENTS.md` now reads
"six domain/cross-cutting packages implemented (ADR, REQ, UC, TSK, QA,
general)" with a `qa/` bullet (mirroring REQ's/TSK's bullet shape) inserted
after the `tsk/` bullet, its "Still genuinely missing" list updated
(`delete_qa` stub, `validate_qa` omitted from pre-commit/CI enforcement,
`qa` added to the tools/resources/prompts registration summary), and every
other domain-enumeration spot in the file (the closing "don't assume any
other domain package exists" paragraph, and the "MCP server (`server.py`)"
section's own import-list mention) updated to include `qa` too. Ran
`specmgr docs`/`specmgr mcp-docs`/`specmgr schema --type qa` (both
`docs/qa_schema.json` and the packaged `qa/data/qa_schema.json` copy) twice
each and confirmed the second run of every command reports zero further
drift (`(unchanged)` for both schema outputs, identical `git diff` for
`docs/`/`docs/MCP.md` across both runs). Full quality gate green: `ruff
format --check` (766 files already formatted), `ruff check` (all checks
passed), `vulture` (no output, clean), and the full `unittest` suite (1144
tests, OK -- unchanged from Phase 4's count, no regressions, as expected
since this phase touched no `src/`/`tests/` Python logic). Commit for Phase
5 intentionally left to the orchestrator. Phase 6 (Final cross-cutting
verification) subsequently completed Task 6.1: see the dated Recent
Updates entry below for the full evidence trail. Commit for Phase 6
intentionally left to the orchestrator as well. No further phases remain.

### Blockers

None currently.

### Recent Updates

Older entries (2026-08-18T11:15:00Z and earlier) are archived in
[`history.md`](history.md).

#### Update 2026-08-18T23:45:00Z

- Completed: Phase 6 (Final cross-cutting verification) — Task 6.1 (Final
  verification pass). Re-read the plan's Acceptance Criteria section and
  Phase 6 verbatim first, per the orchestrator's instructions, then walked
  every ACC-001..006 independently with fresh, concrete evidence (not
  trusting earlier phase reports):
  - **ACC-001**: Ran `tests/models/md/test_markdown.py` (12 tests —
    merge-semantics regression, including
    `test_reapplying_with_no_arguments_keeps_every_inherited_key`,
    `test_explicitly_passing_none_clears_an_inherited_value`,
    `test_end_marker_is_merged_the_same_way`) and
    `tests/models/md/test_markdown_section_end_marker.py` (6 tests —
    depth-0 stop condition, including
    `test_extent_stops_before_the_first_depth_zero_block_quote` and the
    nested-list-and-nested-block-quote edge case
    `test_nested_list_and_nested_block_quote_do_not_truncate`/
    `test_from_text_retains_the_nested_list_and_quote_but_not_the_end_marker`)
    — 18/18 passed.
  - **ACC-002**: Called
    `parse_qa('.specmgr/feat/feat-12-qa-artifact/qa_reference.md')`
    directly against the current committed state (not just re-reading a
    prior phase's claim): confirmed `frontmatter.id`, `frontmatter.status`,
    `body.text`, `compatibility.items is None`, `functional_suitability`'s
    2 Q&A pairs, and `more_information` all round-trip correctly.
  - **ACC-003**: Ran `tests/qa/models/v1/test_frontmatter.py` (9 tests,
    including `test_accepts_all_four_statuses`/
    `test_rejects_unknown_status`) and `tests/qa/models/v1/test_body.py`
    (17 tests, including `TestQaRequiredVsOptionalFields`'s
    missing-mandatory-field checks) — 26/26 passed.
  - **ACC-004**: Ran `tests/qa/models/v1/test_parser.py` (6 tests —
    `test_parses_minimal_document`/`test_parses_full_reference_document`
    for a valid object tree,
    `test_missing_general_section_raises_assertion_error`/
    `test_missing_iso_characteristic_section_raises_assertion_error` for
    `AssertionError`, `test_invalid_status_raises_validation_error` for
    `pydantic.ValidationError`) — 6/6 passed.
  - **ACC-005**: Imported `biz.dfch.specmgr.server` live and introspected
    `server.mcp` via `list_tools()`/`list_resources()`/`list_prompts()`
    (async): confirmed all 9 tools (`parse_qa`, `get_qa`, `get_qa_example`,
    `get_qa_template`, `create_qa`, `update_qa`, `set_status_qa`,
    `delete_qa`, `validate_qa`), all 4 resources (`specmgr://qa/schema`,
    `/example`, `/template`, `/list`), and both prompts (`create_qa`,
    `update_qa`) present among the server's 49 total tools / 19 total
    resources / 11 total prompts (matching `docs/MCP.md`'s documented
    counts). Went further than mere registration: actually called
    `mcp.call_tool('get_qa_template', {})`,
    `mcp.read_resource('specmgr://qa/schema')`,
    `mcp.get_prompt('create_qa', {'topic': ...})`, and
    `mcp.get_prompt('update_qa', {'id': 'x'})` live and confirmed each
    returns successfully — proving callable, not just registered.
  - **ACC-006**: Re-ran `specmgr docs`, `specmgr mcp-docs`,
    `specmgr schema --type qa`, and `specmgr schema --type qa --output-dir
    src/biz/dfch/specmgr/qa/data` fresh against the current committed
    state: `specmgr docs`/`specmgr mcp-docs` produced no
    `git status --short` changes under `docs/`, and both schema commands
    reported `(unchanged)` — zero drift confirmed independently of Phase
    5's own claim.
  - Ran the full quality gate end-to-end: `uv run --frozen ruff format
    --check` (766 files already formatted), `uv run --frozen ruff check`
    (all checks passed), `uv run --frozen pylint $(git ls-files '*.py')`
    (9.01/10, advisory only — the only findings are pre-existing `R0401`
    cyclic-import warnings following the same domain-package/`server.py`
    import pattern already present for every other domain (`adr`, `req`,
    `tsk`, `uc`), not a `qa`-specific regression, so not treated as a
    blocker), `uv run --frozen vulture src/ whitelist.py
    --min-confidence 60` (no output, clean), and `uv run --frozen python
    -m unittest discover -v -s tests -t . -p "test_*.py"` (1144 tests, OK
    — identical count to Phase 5's end, no regressions, as expected for a
    verification-only phase). Found no genuine regression or surprise;
    nothing required fixing.
- Next: None — feature complete.
- Notes: Set frontmatter `status: done` (from `planning`); `version`
  intentionally left at `1.0.0` per the orchestrator's explicit
  instruction. Left staging/committing to the orchestrator per this
  session's instructions; no `src/`/`tests/` files were touched this
  phase (verification-and-documentation only), so the working tree has
  only this README's edits, unstaged.

#### Update 2026-08-18T22:45:00Z

- Completed: Phase 5 (Cross-cutting registration) — Tasks 5.1, 5.3, 5.4,
  5.5, 5.6, 5.7, 5.8 (intentional gap at 5.2, folded into Task 3.1.1 earlier
  in the plan). Read `server.py`, `pyproject.toml`'s
  `[tool.setuptools.package-data]`, `.pre-commit-config.yaml`,
  `.github/workflows/ci.yml`, and `AGENTS.md` in full first, per the
  orchestrator's instructions, confirming the already-established fact
  that `qa`'s MCP surface was already transitively registered (via
  `commands/schema.py` importing `qa.models.v1`, which triggers
  `qa/__init__.py`'s own `tools`/`resources`/`prompts` import) before this
  phase started, so `docs/MCP.md`/`docs/GENERATED.md` needed no
  regeneration here.
  - **Task 5.1**: Changed `server.py`'s bottom import line to
    `from . import adr, general, qa, req, tsk, uc  # noqa: E402, F401`
    (alphabetical order). Updated the module docstring: added a
    `specmgr://qa/schema`/`/example`/`/template`/`/list` resources block
    (placed after the `tsk` block and before `specmgr://iso25010`, matching
    the existing chronological-addition-order convention, not strict
    alphabetical), a sentence extending the existing REQ/UC/TSK
    no-`/{id}`-resource note to cover QA, a "QA tools (`qa/tools/`): ..."
    line listing all 9 tools (placed after the Task list tools line, before
    General tools), a "QA prompts (`qa/prompts/`): `create_qa`,
    `update_qa`" line (after Task list prompts), and updated the "Modules
    are grouped domain-first" paragraph's domain list
    (`adr`, `uc`, `req`, `tsk`, `qa`, and later `ac`), its import-list
    mention (`adr`/`general`/`qa`/`req`/`tsk`/`uc`, alphabetical), and its
    closing sentence (`req`, `tsk`, and `qa` each register `tools`,
    `resources`, and `prompts`; `uc` registers `tools` and `resources`
    only).
  - **Task 5.3**: Added `"biz.dfch.specmgr.qa" = ["data/*.md", "data/*.json"]`
    to `pyproject.toml`'s `[tool.setuptools.package-data]`, placed
    alphabetically among the domain packages (`qa` before `req`, `req`
    before `tsk`, `tsk` before `uc`), with `general` kept last as the
    existing convention already has it (not alphabetical -- `general`
    would otherwise sort before `qa`/`req`/`tsk`/`uc`).
  - **Task 5.4**: Widened the shared `files:` glob on all four existing
    schema hooks (`specmgr-schema`, `specmgr-schema-req-package`,
    `specmgr-schema-uc-package`, `specmgr-schema-tsk-package`) from
    `^src/biz/dfch/specmgr/(req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$`
    to
    `^src/biz/dfch/specmgr/(qa/models/v1|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$`
    (alphabetical inside the group). Added a new `specmgr-schema-qa-package`
    hook, a 1:1 mirror of `specmgr-schema-tsk-package`'s shape/wording
    (`entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`,
    same widened glob).
  - **Task 5.5**: Added two new CI steps to `.github/workflows/ci.yml`,
    placed immediately after the existing
    `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` step and before the
    `docs/coverage.svg` step: "Make sure `docs/qa_schema.json` is correct"
    (bare `specmgr schema`, same `if: matrix.python-version == '3.13'`
    guard and `::error::` failure-message pattern as the existing
    `docs/req_schema.json`/`docs/uc_schema.json` steps) and "Make sure
    `src/biz/dfch/specmgr/qa/data/qa_schema.json` is correct"
    (`specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`).
  - **Task 5.6**: Updated `AGENTS.md`'s heading to "six domain/cross-cutting
    packages implemented (ADR, REQ, UC, TSK, QA, general)" and its lead-in
    sentence to "Five document-type domains plus one cross-cutting package".
    Added a `qa/` bullet after the `tsk/` bullet (matching the existing
    chronological-order convention the other bullets already use, not
    alphabetical), mirroring REQ's/TSK's own bullet depth (tools list,
    resources list, prompts list, no-`/{id}`-resource note citing ADR
    ddfb1109-422d-4507-8dbc-dc5e4bec9614). Updated the "Still genuinely
    missing" list: added `validate_qa` to the pre-commit/CI enforcement
    bullet (for consistency -- `qa` has the identical gap REQ/UC/TSK
    already have), added `delete_qa` to the stubs bullet, and added `qa` to
    the tools/resources/prompts registration-summary bullet. Updated the
    closing "don't assume any other domain package exists beyond..."
    paragraph and, since it also enumerates all five prior domains and
    would otherwise be factually wrong by omission, the "MCP server
    (`server.py`)" section's own "imports every domain package (...)"
    sentence -- the one specific case the hard-rule carve-out ("unless it
    specifically enumerates the 5 domains and would now be factually wrong
    by omitting `qa`") applies to; no other section was touched.
  - **Task 5.7**: Ran `specmgr docs`, `specmgr mcp-docs`, `specmgr schema
    --type qa`, and `specmgr schema --type qa --output-dir
    src/biz/dfch/specmgr/qa/data`, each twice. First run: `specmgr docs`
    regenerated only `docs/api/biz.dfch.specmgr.server.md` (the docstring
    changes from Task 5.1); `specmgr mcp-docs` produced no `git diff` at
    all (confirming the orchestrator's stated fact that `docs/MCP.md`
    already reflected `qa`'s full surface from the Phase-4-era transitive
    import); both `specmgr schema --type qa` invocations reported
    `(unchanged)` since Task 3.1.1/4.4 already drafted both files
    correctly. Second run of every command: identical `(unchanged)`
    results and an identical `git diff --stat docs/` to the first run --
    all four commands confirmed idempotent, no further drift introduced by
    Task 5.1's docstring edit or Task 5.6's `AGENTS.md` edit (which
    `specmgr docs`/`mcp-docs` don't even read, since `AGENTS.md` isn't a
    `src/` docstring source).
  - **Task 5.8**: Ran the full phase-end quality gate:
    `uv run --frozen ruff format --check` (766 files already formatted),
    `uv run --frozen ruff check` (all checks passed),
    `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no
    output, clean), and
    `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
    (1144 tests, OK -- identical count to Phase 4's end, no regressions, as
    expected since Phase 5 is pure cross-cutting registration/config with
    no new `src/`/`tests/` Python logic). Left staging/committing to the
    orchestrator per this session's instructions; working tree has the
    edited `server.py`, `pyproject.toml`, `.pre-commit-config.yaml`,
    `.github/workflows/ci.yml`, `AGENTS.md`, and the regenerated
    `docs/api/biz.dfch.specmgr.server.md`, all unstaged.
- Next: Phase 6 (Final cross-cutting verification) — Task 6.1.
- Notes: `qa` is now identically wired into every cross-cutting mechanism
  REQ/UC/TSK already have (server registration, packaging, pre-commit
  schema hooks, CI schema-drift checks, `AGENTS.md`). Phase 6 is a
  verification-only pass (walk ACC-001..006, run the full quality gate
  including pylint-advisory/`specmgr docs`/`specmgr mcp-docs`/`specmgr
  schema --type qa` end-to-end one more time) and setting the feature
  status to `done` -- no new implementation is expected there.

#### Update 2026-08-18T21:10:00Z

- Completed: Phase 4 (MCP Surface) — Tasks 4.1, 4.2, 4.3, 4.4, 4.5, 4.6.
  Read every REQ file the plan named (`req/tools/*.py`, `req/resources/*.py`,
  `req/prompts/*.py`, `req/data/*`, `req/__init__.py`,
  `general/tools/_packaged_data.py`, `general/tools/_doc_paths.py`) plus
  `qa_reference.md` and `qa/models/v1/*.py` before writing anything, per the
  orchestrator's instructions.
  - **Task 4.1**: Created `qa/tools/{__init__,_paths,_io,_lock,_write,
    parse_qa,get_qa,get_qa_example,get_qa_template,create_qa,update_qa,
    set_status_qa,delete_qa,validate_qa}.py`, a 1:1 port of every
    corresponding `req.tools` module with every `Req`/`req` identifier
    substituted for `Qa`/`qa` (`ReqDocument` -> `QaDocument`,
    `ReqFrontmatter` -> `QaFrontmatter`, `Requirement` -> `Qa` -- the `qa`
    domain's own body class, not to be confused with `qa`'s *own*,
    differently-shaped `Requirement` callout class from Phase 3 --
    `ReqNotFoundError` -> `QaNotFoundError`, `req_lock`/`req_base_dir` ->
    `qa_lock`/`qa_base_dir`, `REQ_TYPE_NAME` -> `QA_TYPE_NAME`). Every
    design-rationale docstring (error-channel split, lock rationale,
    no-render-just-persist-verbatim design, read-only/write directory
    split, id -> path skip-on-parse-failure rule) was preserved and
    reworded for QA, not stripped. `create_qa`'s filename convention is
    `qa-{id}-{slugify(body.text)}.md`. `set_status_qa` reconstructs
    `QaFrontmatter` via its own constructor (not `model_copy`) so the
    four-value closed-set `status` validator (`draft`/`active`/`done`/
    `cancelled`) actually runs. `delete_qa` is a registered
    `structured_output=False` stub, always raising `NotImplementedError`.
    `validate_qa` mirrors `validate_req`'s disk-free/id-free dry-run shape
    exactly.
  - **Task 4.2**: Created `qa/resources/{__init__,qa_schema,qa_example,
    qa_template,qa_list}.py`, 1:1 ports of REQ's four resources at the
    same four URIs (`specmgr://qa/schema`, `/example`, `/template`,
    `/list`, no `/{id}`). `qa_list` builds `QaSummary` entries
    (`id`/`title`=`doc.body.text`/`status`/`ref`=`path.stem`), silently
    skipping any file that fails to parse
    (`AssertionError`/`pydantic.ValidationError`), identical to
    `req_list`'s own skip rule.
  - **Task 4.3**: Created `qa/prompts/{__init__,create_qa,update_qa}.py`,
    matching `req/prompts/`'s instructional-text-returning `@mcp.prompt()`
    shape exactly, but with the instructional content fully rewritten for
    QA's own schema: the `create_qa` prompt recaps `# {title}`, `##
    General` (`### Introduction`/`### Raw Requirements`), the nine fixed
    ISO/IEC 25010:2023 characteristic H2s in their canonical order/wording,
    the free-form `### {question}` `QaSection` pattern (optional
    `comment`/`requirement`/`question`/`answer`), and optional `##
    More Information`; it tells the LLM to check `specmgr://qa/list`
    first, elicit characteristic-relevant answers per category (noting a
    category may legitimately stay empty), and reference
    `specmgr://qa/template`/`/example`/`/schema` before calling
    `create_qa`/`validate_qa`. The `update_qa` prompt maps body changes to
    `update_qa(id, content)` (whole-body replace, explicitly warning that
    all nine fixed category headings must be carried forward even when
    empty) and status changes to `set_status_qa(id, status)`
    (draft/active/done/cancelled), mirroring `update_req`'s prompt
    structure/tone.
  - **Task 4.4**: Created `qa/data/qa_example.md` by reusing Phase 2's
    `qa_reference.md` verbatim (mirroring REQ's own reference-is-example
    precedent named as an explicit option in this task) -- verified via a
    throwaway `parse_qa(...)` call that it round-trips successfully
    (`frontmatter.id`, `body.text`, `compatibility.items is None`, and
    `functional_suitability`'s two Q&A pairs all came back correctly; see
    Decisions Made for why no TSK-style light adaptation was needed).
    Created `qa/data/qa_template.md` from scratch (not adapted from
    `qa_reference.md`) with every fixed H2 present, both `## General`
    sub-sections, one Q&A pair with all four optional fields filled with
    short placeholder text (`comment`/`#### Requirement`/`question`/
    `answer`), and `## More Information` -- verified it happens to parse
    successfully end-to-end too (a stronger guarantee than the task
    required, which only asked for structural completeness). Copied
    `docs/qa_schema.json` byte-for-byte to `qa/data/qa_schema.json`
    (confirmed via `diff`). Edited (not recreated) `qa/__init__.py`,
    replacing its Phase-3-only docstring with one mirroring
    `req/__init__.py`'s exact shape/wording, and added
    `from . import prompts, resources, tools  # noqa: F401` plus the
    matching `__all__`; explicitly noted `server.py`'s own import list
    still excludes `qa` (Phase 5's Task 5.1).
  - **Task 4.5**: Read every file under `tests/req/{tools,resources,
    prompts}/` first, then created the mirrored `tests/qa/{tools,
    resources,prompts}/` suites (`__init__.py` markers plus 19 test
    files, 83 tests total: 53 in `tools/`, 15 in `resources/`, 15 in
    `prompts/`), all isolated from the real filesystem via
    `mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: ...})` against a
    `tempfile.TemporaryDirectory()`, the same pattern `tests/req/` uses.
    Coverage mirrors REQ's own depth/shape per file (base-dir resolution,
    id lookup and its skip-on-parse-failure rule, lock serialization,
    write-and-round-trip, create/update/get/set-status/delete/validate/
    parse tool behavior including every error channel, packaged-data
    example/template reads with cache-freshness and missing-file checks,
    the `qa_list` resource's skip-malformed-file behavior, and prompt
    content/ordering assertions) -- adapted only where QA's own schema
    differs from REQ's (see Decisions Made for the one genuine coverage
    gap this surfaced).
  - **Task 4.6**: Ran the full phase-end quality gate:
    `uv run --frozen ruff format --check` (744 files already formatted),
    `uv run --frozen ruff check` (all checks passed),
    `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no
    output, clean -- no new dead-code flags this phase, unlike Phase 3),
    and `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
    (1144 tests, OK -- up from 1061, i.e. exactly the 83 new `qa` tests,
    no regressions). Also ran `uv run --frozen specmgr docs` (regenerated
    `docs/api/*.md` for 20 new `qa` modules plus `docs/GENERATED.md`'s
    test-file count 156 -> 175) and confirmed a second run produces an
    identical `git status --short docs/` (idempotent). Left
    staging/committing to the orchestrator per this session's
    instructions; working tree has the new `qa/{tools,resources,prompts,
    data}/`/`tests/qa/{tools,resources,prompts}/` trees, the edited
    `qa/__init__.py`, and the regenerated docs, all unstaged.
- Next: Phase 5 (Cross-cutting registration) — Task 5.1 (`server.py` --
  add `qa` to the bottom import line, update the module docstring).
- Notes: `qa`'s tools/resources/prompts are fully built, importable, and
  unit-tested standalone (each test imports the specific function directly,
  e.g. `from biz.dfch.specmgr.qa.tools.create_qa import create_qa`, mirroring
  how `tests/req/` itself never round-trips through a live MCP server), but
  are not yet registered against the live MCP server -- `server.py`'s
  bottom-of-file import list still only imports `adr`, `general`, `req`,
  `tsk`, `uc`, not `qa`. That wiring, plus `pyproject.toml` package-data,
  the pre-commit schema-hook glob, and the CI schema-drift check, are all
  Phase 5 work and were deliberately left untouched this phase.

#### Update 2026-08-18T19:30:00Z

- Completed: Phase 3 (Pydantic Models & Parser) — Tasks 3.1, 3.1.1, 3.2, 3.3.
  - **Task 3.1**: Created the `qa` domain package:
    `src/biz/dfch/specmgr/qa/__init__.py` (docstring-only for now, since
    `tools`/`resources`/`prompts` don't exist until Phase 4 -- it does not
    import them yet, unlike `req`/`tsk`'s own `__init__.py`), plus
    `qa/models/__init__.py` and `qa/models/v1/{__init__,_util,frontmatter,
    body,document,parser,summary}.py`, all inside the domain package per
    the domain-first layout (ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
    mirroring `req`/`tsk`'s exact file shapes read directly from disk
    first. `QaFrontmatter` reuses `TskFrontmatter`'s `_ALLOWED_STATUSES`
    pattern verbatim (`draft`/`active`/`done`/`cancelled`). `body.py`
    implements the full schema from Design Notes: `Qa(MarkdownSection1)`,
    `General(MarkdownSection2WithComment)` with `Introduction
    (MarkdownSection3WithComment)`/`RawRequirements(MarkdownSection3)`,
    `QaSection(MarkdownSection3WithComment)` with `requirement`/`question`/
    `answer`, `Requirement(MarkdownSection4)` decorated
    `@markdown(end_marker=MarkdownBlockQuote)`, and the 9 ISO/IEC
    25010:2023 `<QaCategory>` classes. Resolved the plan's deferred
    9-category class-sharing question by empirically verifying (via a
    throwaway script, then codified in `tests/qa/models/v1/test_body.py`)
    that approach (a) -- one shared, private `_QaCategory(MarkdownSection2)`
    intermediate base declaring `items` once, with 9 final subclasses each
    relying on implicit `AliasType.SPACE_SEPARATED` alias derivation from
    their own class names -- carries no heading-detection risk: confirmed
    that `MarkdownSection.get_extent`/`from_text`'s `match_alias` call
    always passes the actual runtime subclass (e.g. `FunctionalSuitability`),
    not the shared base, as `cls`, so `cls.__name__` (not `_QaCategory`'s)
    is what the implicit alias derivation keys off; also confirmed
    `_get_field_names()` correctly resolves the inherited `items` field
    through the extra inheritance level, and that `@markdown`'s
    `_metadata` (`heading_open`/`h2`) is inherited transparently with no
    per-subclass re-application needed. Discovered mid-implementation that
    `QaAnswer` cannot be heading-anchored like `MoreInformation`/
    `RawRequirements`/`Notes` (all bare `MarkdownSectionN` subclasses) --
    re-reading `qa_reference.md` closely showed every `answer` is trailing
    prose immediately after `question`'s block quote with **no heading of
    its own** anywhere in the document. Implemented `QaAnswer` as a bare
    `MarkdownStr` subclass instead (no `@markdown` metadata at all), whose
    inherited `get_extent` already captures "everything remaining" with no
    heading-level stop condition, plus an explicit `text` computed property
    (mirroring `MarkdownParagraph.text`/`MarkdownSection.text`/
    `MarkdownCodeBlock.text`'s established pattern) so `_value` is
    reachable through `model_dump()`. Verified `Requirement`'s
    `@markdown(end_marker=MarkdownBlockQuote)` merges into
    `MarkdownSection4`'s already-inherited `type="heading_open"`/`tag="h4"`
    without needing to re-pass them, and that its heading text is fixed
    (`"Requirement"`, matching the implicit `AliasType.SPACE_SEPARATED`
    derivation), confirmed against `qa_reference.md`'s literal
    `#### Requirement` heading. Round-tripped the full `qa_reference.md`
    through the assembled `Qa`/`QaFrontmatter` models via a throwaway
    script before writing `parser.py`, confirming byte-exact round-trip
    including the `Compatibility`-is-empty case and the `end_marker`
    scenario.
  - **Task 3.1.1**: Read `commands/schema.py` in full, added
    `generate_qa_schema()` mirroring `generate_req_schema`/
    `generate_tsk_schema`/`generate_uc_schema` exactly (imports
    `SCHEMA_COMMENT_VERSION as QA_SCHEMA_COMMENT_VERSION` from
    `qa.models.v1`, `QaDocument` from `qa.models.v1.document`, injects
    `$schema`/`$comment`, serializes with `indent=2, sort_keys=True` plus
    trailing newline), registered `"qa": generate_qa_schema` in
    `_GENERATORS`, and ran `uv run --frozen specmgr schema --type qa` to
    draft `docs/qa_schema.json` (`$comment: "v1"`, top-level `$schema`
    pointing at the 2020-12 dialect, `$defs` holding all 9 category
    classes plus `Qa`/`QaSection`/`QaAnswer`/`Requirement`/`General`/
    `Introduction`/`RawRequirements`/`MoreInformation`/`QaFrontmatter`/
    the shared `models/md` leaf types it references).
  - **Task 3.2**: Added `tests/qa/{__init__,models/__init__,models/v1/
    __init__}.py` (empty namespace markers, matching `tests/tsk/`'s exact
    convention) and `tests/qa/models/v1/{test_frontmatter,test_body,
    test_parser}.py` (35 tests total), mirroring `tests/tsk/models/v1/`'s
    style/depth. `test_frontmatter.py` covers `type`/`version`/`status`
    defaults and rejection of any status outside the four-value set
    (ACC-003). `test_body.py` covers required-vs-optional field validation
    on `Qa`/`<QaCategory>`/`QaSection` via direct construction (ACC-003),
    an explicit "all 9 categories resolve their own, distinct, correct
    heading alias" regression test for the class-sharing decision above,
    the `Requirement` `end_marker` wiring (metadata, fixed heading, and a
    from-text round-trip proving it does not absorb a following block
    quote), and `QaAnswer`'s heading-free, multi-paragraph-capturing
    behavior. `test_parser.py` mirrors `tests/tsk/models/v1/test_parser.py`'s
    exact structure (`_REFERENCE_PATH` pointing at this feature's own
    `qa_reference.md`): a minimal valid document parses correctly
    (ACC-004); the full reference document round-trips with specific
    assertions on `compatibility.items is None`, every other category's
    item count, and the first `Functional Suitability` Q&A pair's
    `requirement`/`question`/`answer` content proving the `end_marker`
    scenario works end-to-end (ACC-002/ACC-004); a missing `## General` or
    a missing ISO-characteristic H2 (`## Safety`) each raise
    `AssertionError`; an invalid frontmatter `status` raises
    `pydantic.ValidationError` (ACC-004). Fixed three initial test
    failures caused by `QaAnswer.text` retaining a trailing `"\n"` (its
    `_value` is the verbatim remaining extent, not a stripped paragraph
    text) by asserting `.strip()` equality/`assertIn` instead of exact
    equality where appropriate.
  - **Task 3.3**: Ran the full phase-end quality gate:
    `uv run --frozen ruff format --check` (698 files already formatted),
    `uv run --frozen ruff check` (all checks passed),
    `uv run --frozen vulture src/ whitelist.py --min-confidence 60` --
    initially flagged 15 new Pydantic field names as unused (`introduction`,
    `raw_requirements`, `requirement`, `question`, `answer`, and the 9
    category field names on `Qa` plus `general`), added them to
    `whitelist.py`'s existing "Pydantic model fields read only via
    (de)serialization/rendering" section (same rationale as its existing
    entries: these fields aren't accessed as plain Python attributes
    anywhere in `src/` yet, only via markdown round-tripping and, later,
    Phase 4's MCP tools), then re-ran vulture clean. Ran
    `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
    (1061 tests, OK -- up from 1026 before this phase, i.e. exactly the 35
    new `qa` tests, no regressions). Also ran `uv run --frozen specmgr docs`
    (regenerated `docs/api/*.md` for 9 new `qa` modules plus
    `docs/GENERATED.md`'s test-file count 153 -> 156) and confirmed a
    second run produces an identical `git status --short docs/` (idempotent).
    `docs/qa_schema.json` (drafted in Task 3.1.1) was left as-is, unchanged
    since Task 3.1.1. Left staging/committing to the orchestrator per this
    session's instructions; working tree has the new `qa/`/`tests/qa/`
    trees, the `commands/schema.py`/`whitelist.py` edits, and the
    regenerated docs, all unstaged.
- Next: Phase 4 (MCP Surface) — Task 4.1
  (`qa/tools/{_paths,_io,_lock,_write,parse_qa,get_qa,...}.py`).
- Notes: `qa`'s own `tools`/`resources`/`prompts` (and therefore
  `qa/__init__.py`'s eventual `from . import prompts, resources, tools`
  line) remain Phase 4 work; nothing in Phase 3 registers `qa` against the
  MCP server yet.

#### Update 2026-08-18T17:40:00Z

- Completed: Phase 2 (Specification) — Task 2.1 and Task 2.3.
  - **Task 2.1**: Wrote
    `.specmgr/feat/feat-12-qa-artifact/qa_reference.md`, a pure
    markdown-authoring reference exercising every field of the schema
    shape pinned down in Design Notes (no Pydantic models exist yet — that
    is Phase 3's Task 3.1). Read `req_reference.md`, `tsk_reference.md`,
    and `uc_reference.md` first for style precedent, and reused
    `tsk_reference.md`'s "Migrate Widgets to the New Registry" theme so
    this document reads as the requirements-elicitation interview that
    would plausibly precede that task list. Frontmatter uses
    `id: deaddead-feed-feed-feed-deaddeadfeed`, `status: active`,
    `type: qa` (see Decisions Made). Structure: a single H1, then `##
    General` (H3 `### Introduction` with two body paragraphs, H3 `### Raw
    Requirements` as opaque prose), then the 9 ISO/IEC 25010:2023
    characteristic H2s in exact canonical order/wording (verified earlier
    against the `specmgr://iso25010` resource per the plan's own Design
    Notes, re-confirmed here against
    `general/data/general_iso25010.md`'s own H2 order), then `## More
    Information`. Q&A (H3) coverage across categories: `Functional
    Suitability` has two H3s — the first exercises all four `QaSection`
    fields at once (an HTML `comment` immediately after its heading, a
    `#### Requirement` callout whose own body contains both a nested
    bullet list *and* a nested block quote inside one of that list's
    items, mirroring Task 1.3/1.4's own edge-case fixture almost verbatim,
    immediately followed by its `question` block quote — exercising the
    exact `end_marker` scenario Phase 1 was built for — then a prose
    `answer`), the second has only `question`+`answer` (no
    `comment`/`requirement`), exercising "all four fields fully optional".
    `Safety` has one more full-combo H3 (`comment` + `Requirement` +
    immediately-following `question` + `answer`, this one without nested
    list/quote content, as a second, simpler `end_marker` occurrence).
    `Performance Efficiency`, `Interaction Capability`, `Reliability`,
    `Security`, `Maintainability`, and `Flexibility` each get exactly one
    `question`+`answer`-only H3. `Compatibility` is the one category
    deliberately left with **no** H3 children at all (empty `items`),
    per the plan's explicit "pick which one(s) are empty" instruction —
    rationale (a purely internal migration raising no external
    interoperability/co-existence concerns yet) is documented both in this
    entry and inline in the reference doc's own `More Information`
    section. Ran `uv run --frozen specmgr mdformat
    .specmgr/feat/feat-12-qa-artifact/qa_reference.md` (exit code `0` —
    already canonical, no rewrite) and confirmed with `--dry-run` too.
  - **Task 2.3**: Ran `uv run --frozen ruff format --check` (674 files
    already formatted), `uv run --frozen ruff check` (all checks passed),
    and `uv run --frozen vulture src/ whitelist.py --min-confidence 60`
    (no output, clean) — unaffected, as expected, since this phase only
    added one markdown file outside `src/`/`tests/`. No unit-test suite
    applies (no Pydantic models exist yet).
- Next: Phase 3 (Pydantic Models & Parser) — Task 3.1 (`qa/models/v1/...`).
- Notes: Phase 2 added no `src/`/`tests/` code and made no commits (left
  to the orchestrator, per this session's instructions).

#### Update 2026-08-18T16:05:00Z

- Completed: Phase 1 (`models/md` engine enhancement) — Tasks 1.1 through
  1.5.
  - **Task 1.1**: `markdown()` in `src/biz/dfch/specmgr/models/md/markdown.py`
    now merges into `getattr(cls, "_metadata", {})` instead of
    unconditionally replacing it. `type`/`tag` (and the new `end_marker`,
    see Task 1.2) became keyword-only parameters defaulting to a private
    module-level sentinel `_UNSET = object()` rather than `None`, so "this
    keyword was not passed" (leave any inherited value alone) is
    distinguishable from "this keyword was explicitly passed as `None`"
    (a real, honored value that overwrites/clears an inherited entry).
    Verified 100% backward compatible against all 11 existing
    `@markdown(...)` call sites (`markdown_section.py`,
    `markdown_section1.py`-`markdown_section6.py`, `markdown_paragraph.py`,
    `markdown_code_block.py`, `markdown_block_quote.py`,
    `markdown_comment.py`) — every one still passes both `type`/`tag`
    explicitly, so merge-vs-replace is unobservable for them; the
    `*_with_comment.py` classes were left untouched (they inherit
    `_metadata`, never re-apply `@markdown`).
  - **Task 1.2**: Added `end_marker: type[MarkdownStr] | None = _UNSET`
    to `markdown()`, stored under `_metadata["end_marker"]` via the same
    merge/sentinel mechanism as `type`/`tag`. Decorator docstring/examples
    updated accordingly (including a new example showing a subclass
    re-applying `@markdown` and keeping an inherited `end_marker`).
  - **Task 1.3**: `MarkdownSection.get_extent`
    (`src/biz/dfch/specmgr/models/md/markdown_section.py`) now also stops
    at the first token matching `cls._metadata.get("end_marker")`'s own
    `type`/`tag`, but only when that token occurs at nesting depth 0. A
    running `depth` counter is updated by every token's own `Token.nesting`
    across the *entire* token stream (not just tokens matching the
    end_marker's type), checked *before* applying that token's own delta —
    verified by tracing real token streams via `parse()` for a fixture H4
    section with a nested bullet list, a nested block quote *inside a list
    item*, and a real depth-0 block quote following: the nested
    occurrences correctly report depth 2/3 (not 0) and are not mistaken for
    the end marker, while the real end-marker block quote reports depth 0
    and stops the scan there.
  - **Task 1.4**: Added `tests/models/md/test_markdown.py` (11-call-site
    backward-compatibility regression for Task 1.1, plus new
    merge/sentinel/`end_marker` unit tests for the decorator itself) and
    `tests/models/md/test_markdown_section_end_marker.py` (a fixture
    `_RequirementLikeSection(MarkdownSection4)` declaring
    `@markdown(end_marker=MarkdownBlockQuote)`, exercising: a depth-0 block
    quote stopping the scan; no end marker following still reaching the
    end of the text; and the nested-list-and-nested-block-quote edge case
    from Task 1.3's note, both `get_extent` and `from_text` verified). 18
    new tests total.
  - **Task 1.5**: Ran the full phase-end quality gate:
    `uv run --frozen ruff format --check` (673 files already formatted),
    `uv run --frozen ruff check` (all checks passed),
    `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no
    output, clean), and
    `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
    (1026 tests, OK — up from 1008 before this phase, i.e. exactly the 18
    new tests, no regressions). Also ran `uv run --frozen specmgr docs`
    since Phase 1 changed docstrings inherited by several downstream
    subclasses (`Characteristic` in `models/iso25010.py`, TSK's `Task`,
    UC's `Assumptions`) — regenerated `docs/api/*.md` and
    `docs/GENERATED.md` (test-file count 151 -> 153) to keep them
    drift-free for the eventual commit; re-ran it a second time to confirm
    it is now idempotent (no further changes). Left staging/committing to
    the orchestrator per this session's explicit instructions; working
    tree has the two modified source files
    (`models/md/markdown.py`, `models/md/markdown_section.py`), the two
    new test files, and the regenerated docs, all unstaged.
- Next: Phase 2 (Specification) — Task 2.1 (write a full reference
  `qa_reference.md`).
- Notes: Phase 1 is the first and only `models/md` engine change in this
  feature; Phase 2 onward builds the `qa` domain itself on top of it.

#### Update 2026-08-18T14:20:00Z

- Completed: Phase 0 (Cleanup) — Task 0.1 and Task 0.2. Re-verified from
  the repo root (`ls`, `find . -type d -iname "qa"`, `git status`,
  `git status --ignored`) that all four previously-flagged stray
  scaffold paths (`src/qa/`, `src/biz/dfch/specmgr/qa/{tools,resources,
  prompts}/`, `tests/qa/`, `biz/dfch/specmgr/qa/`) are **already absent**
  from disk — no directory of any of these four paths exists, and
  neither `git status` nor `git status --ignored` shows any `qa`-related
  residue (tracked, untracked, or ignored). No deletion was actually
  performed as a result — confirming their absence *is* the completion
  of Task 0.1 (the scaffolding was evidently already removed in an
  earlier, unrecorded step or never actually landed on this checkout),
  not a skipped task. Task 0.2's phase-end check (`git status` /
  `git status --ignored` clean of residue) is satisfied by the same
  verification. This closes Phase 0.
- Next: Phase 1 (`models/md` engine enhancement) — Task 1.1 (merge
  `@markdown(...)` into inherited `_metadata` instead of full replace).
- Notes: Implementation of Phase 1 onward has not started yet.

#### Update 2026-08-18T13:50:58Z

- Completed: Resolved the Task 5.2 duplication flagged (but left
  unresolved) at the end of the previous update. Folded the former Phase
  5 Task 5.2 (`generate_qa_schema()` + `specmgr schema` registry entry)
  into Phase 3's **Task 3.1.1** — which now implements the generator
  function, registers it, *and* drafts `docs/qa_schema.json` by running
  it, all in one task, right after `QaDocument` (Task 3.1) exists. This
  mirrors feat-10's own Task 2.5 exactly (generator + registry + draft,
  as a single task), rather than REQ's older, more fragmented "draft
  first (Task 1.2), formalize later (Tasks 2.7-2.9)" history that the
  previous update had matched by mistake. Phase 5 now has an intentional
  numbering gap at `5.2` (same leave-a-gap convention as Phase 2's `2.2`
  gap), and Tasks 5.4/5.5 (pre-commit hook, CI step) now depend on Task
  3.1.1 instead of the removed Task 5.2. Task 5.7 (docs/schema drift
  check)'s dependency list updated from the stale "Tasks 5.1-5.6" range
  to the precise `Task 3.1.1, Task 5.1, Tasks 5.3-5.6`.
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation still intentionally not started — this remains a
  plan-only commit.

#### Update 2026-08-18T12:40:00Z

- Completed: Fixed the Task 2.2 schema-generation sequencing bug flagged
  (but deliberately left unresolved) in the previous update, following
  feat-10's exact precedent (its own Task 1.3 → Task 2.5 move). Moved the
  "draft `qa_schema.json`" task out of Phase 2 (Specification) — where it
  incorrectly depended only on the reference markdown file (Task 2.1) —
  into Phase 3 (Pydantic Models & Parser) as a new **Task 3.1.1**, placed
  right after Task 3.1 (which defines `QaDocument`) and depending on it,
  since `QaDocument.model_json_schema()` cannot run before that class
  exists. Used a sub-numbered task id (`3.1.1`) specifically so no other
  task in Phase 3 onward needed renumbering. Phase 2 now has an
  intentional numbering gap at `2.2` (Task 2.3's dependency updated from
  Task 2.2 to Task 2.1 accordingly) — left as a gap rather than
  renumbering Task 2.3, consistent with this project's existing
  leave-a-gap convention for numbered sub-items (e.g. `AdrOption`
  deletion). Task 3.1.1 is explicitly scoped as a one-off draft via a
  direct `QaDocument.model_json_schema()` call, not yet wired into the
  reusable `specmgr schema` CLI registry — that generic
  `generate_qa_schema()` + registry entry remains Phase 5's Task 5.2,
  matching REQ's own historical Task 1.2 (draft) → Tasks 2.7-2.9
  (formalize) sequencing. Phase 3's phase-end task (3.3) now also depends
  on Task 3.1.1.
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation still intentionally not started — this remains a
  plan-only commit.

### Decisions Made

- **2026-08-18**: Reuse TSK's 4-value status set (`draft`/`active`/`done`/
  `cancelled`) for `QaFrontmatter.status` rather than REQ's 7-value set —
  a Q&A document's lifecycle doesn't map naturally to
  proposed/accepted/rejected/implemented.
- **2026-08-18**: Each Q&A pair (`QaSection`) is an H3 section with a
  free-form heading (alias `.+`), not a flat bullet-list item — allows a
  nested `requirement` H4 callout and full-fidelity blockquote/answer
  content, which a flat list item cannot express.
- **2026-08-18**: `answer`/`raw_requirements`/`more_information` are all
  represented as opaque, unstructured leaf classes (no declared
  sub-fields) rather than a structured `list[MarkdownParagraph]` — verified
  this is already exactly how REQ's `MoreInformation`/`Notes` work today,
  so no new engine mechanism was needed for this part.
- **2026-08-18**: Introduce a new `@markdown(end_marker=...)` parameter in
  `models/md` (Phase 1, its own dedicated phase) rather than a one-off
  `get_extent` override on a single class — chosen for reusability and
  consistency with the project's existing declarative-decorator idiom,
  after confirming (a) the decorator must switch from full-replace to
  merge-into-inherited semantics first (verified 100% backward compatible
  against all 11 existing call sites), and (b) the stop condition must be
  depth-aware via `Token.nesting`, not first-match-wins, since block quotes
  have no heading-style "level" to disambiguate legitimate nested
  occurrences from a field boundary.
- **2026-08-18**: All four `QaSection` fields (`comment`/`requirement`/
  `question`/`answer`) are fully optional.
- **2026-08-18**: All fixed H2 category headings (`General`, the 9 ISO
  characteristics, `More Information`) are always present in every `qa`
  document; only their internal content (e.g. a category's `items` list)
  may be empty/absent.
- **2026-08-18**: Confirmed four stray, untracked, empty scaffold
  directories from an earlier session must be deleted, not reused: `src/ qa/` (wrong namespace), `src/biz/dfch/specmgr/qa/{tools,resources, prompts}/` (no `models/`), `tests/qa/`, and `biz/dfch/specmgr/qa/`
  (top-level, wrong -- missing `src/` prefix entirely). A fifth path,
  `models/qa/v1/`, was previously listed here but does **not** exist on
  disk (re-verified) — dropped from the delete list. A stale editor/LSP
  diagnostic referenced further `.py` files (`v1.py`, `cli.py`,
  `__init__.py`) supposedly inside these paths; verified directly on disk
  and via `git status --ignored` that none of these files actually exist --
  the diagnostics were phantom/stale, not real content to account for.
- **2026-08-18**: Renamed `Requirement4` -> `Requirement` (naming typo
  fix). Its content is deliberately left unspecified: it holds arbitrary
  agent-authored data (not human-authored, not shaped like REQ's own
  `Requirement` fields), by design, not as a placeholder for future
  structure.
- **2026-08-18**: `General`/`QaSection` inherit `comment` from
  `MarkdownSection2WithComment`/`MarkdownSection3WithComment` instead of
  hand-declaring their own `comment: MarkdownComment | None` field —
  matches existing precedent (TSK's `Task`, REQ's `Level`/`Priority`).
- **2026-08-18**: ISO 25010:2023 characteristic wording verified directly
  via the `specmgr://iso25010` MCP resource (`Functional Suitability`,
  `Performance Efficiency`, `Compatibility`, `Interaction Capability`,
  `Reliability`, `Security`, `Maintainability`, `Flexibility`, `Safety`) —
  confirms the schema's snake_case field names already line up 1:1; no
  renaming needed.
- **2026-08-18**: `Introduction`/`RawRequirements` keep their implicit
  `AliasType.SPACE_SEPARATED` alias derivation (no explicit `@alias`) —
  intentional, not changed.
- **2026-08-18**: Adopted feat-10's per-phase test-and-commit execution
  model (one Conventional Commit per phase, gated by a mandatory
  phase-end task covering unit tests, the full pre-commit/quality gate,
  and a Progress-section update) rather than a single terminal test
  phase. Rationale: implementation is expected to span multiple sessions
  due to context-size limits; without a forced per-phase checkpoint, a
  session could end mid-phase with no reliable test/quality/documentation
  signal for the next session to resume from. New test tasks for Phase 4
  (Task 4.5) and Phase 5 (Task 5.7) were appended as new task numbers
  (not renumbered into the existing sequence), and Phase 6 was repurposed
  to a final cross-cutting verification pass only, mirroring feat-10's
  own Phase 4. Task 2.2's schema-generation sequencing issue (an
  identical bug feat-10 hit and fixed in its own Decisions Made log) was
  deliberately left unresolved here, to be addressed in a separate pass.
- **2026-08-18**: Schema generation lives in **Task 3.1.1** (Phase 3),
  right after Task 3.1 defines `QaDocument`, and does all three of:
  implement `generate_qa_schema()`, register `"qa"` in the `specmgr schema` `_GENERATORS` registry, and draft `docs/qa_schema.json` by
  running it — mirroring feat-10's own Task 2.5. Rationale: schema
  generation calls `QaDocument.model_json_schema()`, so it cannot precede
  `QaDocument`; keeping generator + registry + draft as one task (rather
  than splitting draft-now/formalize-later across Phase 3 and Phase 5)
  follows feat-10's recent, domain-first precedent and avoids a broken
  dependency where a Phase 5 pre-commit/CI wiring task would reference a
  schema task that cannot run before 3.1.1's draft already exists. Phase
  2 keeps an intentional gap at `2.2` and Phase 5 an intentional gap at
  `5.2` (this project leaves numbering gaps rather than renumbering, e.g.
  `AdrOption` deletion); Tasks 5.4/5.5/5.7 depend on Task 3.1.1.
  (History: this originally sat in Phase 2 as Task 2.2, was moved to Phase
  3 as Task 3.1.1 to fix the sequencing bug, then had the former Phase 5
  Task 5.2 generator/registry step folded in — two superseded intermediate
  decisions collapsed here into their final state.)
- **2026-08-18**: Task 1.1's "keyword-only params defaulting to a sentinel"
  hint was implemented as a private module-level `_UNSET = object()` in
  `models/md/markdown.py`, with `type`/`tag`/`end_marker` all becoming
  keyword-only parameters defaulting to `_UNSET` (never compared for
  equality, only identity via `is`/`is not`). Rationale: a plain `None`
  default cannot distinguish "caller omitted this keyword" (leave any
  inherited `_metadata` value alone) from "caller explicitly passed
  `None`" (a real value that overwrites/clears an inherited entry) --
  `None` is itself a legitimate explicit value for all three parameters
  (e.g. `MarkdownSection`'s own bare `tag`-less declaration, or explicitly
  clearing an inherited `end_marker`). Making the parameters keyword-only
  was a deliberate, compatible tightening: all 11 existing call sites
  already pass `type=`/`tag=` as keywords, so nothing broke, and it rules
  out a future positional-argument use that the sentinel-based merge logic
  could not otherwise distinguish from omission.
- **2026-08-18**: `qa_reference.md`'s frontmatter uses
  `id: deaddead-feed-feed-feed-deaddeadfeed` and `status: active` —
  neither was pinned down by the plan itself. `id` follows
  `req_reference.md`/`tsk_reference.md`'s existing "deaddead-...-dead..."
  placeholder-UUID convention with a distinct themed hex word (`feed`,
  valid hex, pairs with `dead`) so it's visually distinguishable from
  REQ's/TSK's own reference docs at a glance; `status: active` was picked
  (over `draft`/`done`/`cancelled`) to reflect an interview that has been
  conducted and answered but not yet formally closed out. Of the 9 ISO
  25010:2023 categories, `Compatibility` was chosen as the one
  deliberately left with no Q&A pairs (exercising the "category's `items`
  may be empty/absent" case) — rationale: the widget-registry migration
  theme this reference doc reuses from `tsk_reference.md` is purely
  internal, so external interoperability/co-existence questions were
  judged the most natural category to have nothing elicited for yet,
  compared to the other 8 which all have at least one plausible internal
  question. Both choices are documented inline in the reference doc
  itself (frontmatter comment-free, but the empty-category rationale is
  spelled out in its own `More Information` section) as well as here.
- **2026-08-18**: Phase 1's `get_extent` depth counter for the new
  `end_marker` stop condition (Task 1.3) considers a token "at depth 0"
  when the running depth *going into* it (i.e. before applying that
  token's own `Token.nesting` delta) is 0 -- verified against real token
  streams via `parse()` (see `test_markdown_section_end_marker.py`) rather
  than assumed, per the plan's explicit instruction not to guess this.
  The depth counter increments/decrements on *every* token's `.nesting`
  across the whole stream (list items, other block quotes, the section's
  own heading triple, ...), not just tokens matching the `end_marker`'s
  own type -- confirmed necessary by tracing a fixture with a block quote
  nested *inside* a list item: tracking only the end marker's own
  open/close pairs would have reported that nested quote as depth 0 (no
  prior same-type token to offset it), causing a false-positive stop.
- **2026-08-18 (Task 3.1)**: Resolved the plan's deliberately-deferred
  9-category class-sharing question in favor of **option (a)**: one
  private, shared `_QaCategory(MarkdownSection2)` intermediate base
  declaring `items: list[QaSection] | None = None` exactly once, with all
  9 final subclasses (`FunctionalSuitability`, ..., `Safety`) as bare,
  field-free subclasses of it, each relying on the implicit
  `AliasType.SPACE_SEPARATED` derivation of its *own* class name for its
  heading match. Rejected option (b) (9 fully independent
  `MarkdownSection2` subclasses, each redeclaring `items` itself) as pure
  duplication with no offsetting benefit once (a) was confirmed safe.
  Verified empirically (via a throwaway script exercising
  `_metadata`/`_get_field_names()`/`match_alias`/`from_text` directly,
  later codified into `tests/qa/models/v1/test_body.py`'s
  `TestQaCategoryAliasesAreDistinct`) that sharing the base introduces no
  ambiguity: `MarkdownSection.get_extent`/`from_text` always call
  `match_alias(cls, ...)` with `cls` bound to the actual leaf subclass
  (e.g. `FunctionalSuitability`), never `_QaCategory`, so
  `AliasType.SPACE_SEPARATED`'s `cls.__name__`-based derivation resolves
  correctly and distinctly per category; `@markdown`'s `_metadata`
  (`type="heading_open"`, `tag="h2"`, inherited from `MarkdownSection2`
  through the extra `_QaCategory` level) and `_get_field_names()`'s
  `model_fields` introspection (which already walks the full MRO) are
  both unaffected by the added inheritance depth. This mirrors the
  project's own established "`*WithComment` inherit rather than
  redeclare" idiom (Task 1.1's own Decisions Made entry), just one level
  deeper and privately scoped (`_QaCategory` is not exported from
  `qa/models/v1/__init__.py`).
- **2026-08-18 (Task 3.1)**: `QaAnswer` is a bare `MarkdownStr` subclass
  (no `@markdown` metadata at all), **not** a heading-anchored
  `MarkdownSectionN` subclass like `RawRequirements`/`MoreInformation`/
  `Notes` -- a genuine, plan-unresolved implementation decision, not a
  simple mirroring of those three. Discovered while wiring up `QaSection`
  that `qa_reference.md`'s `answer` content is always the free-form prose
  trailing directly after `question`'s block quote, with **no heading of
  its own** anywhere in the reference document (no `#### Answer`/similar).
  A heading-anchored class would therefore never match. The base
  `MarkdownStr.get_extent`'s own "no heading-level stop condition, consume
  everything remaining" behavior is exactly what an un-headed trailing
  field needs, so `QaAnswer(MarkdownStr)` (no decorator) was used
  directly, with an explicit `text` computed property added (mirroring
  `MarkdownParagraph.text`/`MarkdownSection.text`/`MarkdownCodeBlock.text`'s
  established pattern) so its otherwise-private `_value` remains reachable
  through `model_dump()`/`model_dump_json()`, consistent with every other
  leaf class in the project.
- **2026-08-18 (Task 3.1)**: `qa/__init__.py` was created now (Task 3.1),
  ahead of Task 4.4's own listed `qa/__init__.py` deliverable, as a
  docstring-only placeholder with no `tools`/`resources`/`prompts` import
  (none exist yet) -- unlike `req`/`tsk/__init__.py`'s
  `from . import prompts, resources, tools`. This satisfies the
  orchestrator's Task 3.1 instruction to create the file now while leaving
  its eventual MCP-registration import line to Phase 4, when those
  sub-packages actually exist; Task 4.4 will edit (not recreate) this same
  file.
- **2026-08-18 (Task 3.3)**: 15 new Pydantic field names introduced by
  `qa/models/v1/body.py` (`introduction`, `raw_requirements`,
  `requirement`, `question`, `answer`, `general`, and the 9 category
  fields on `Qa`) were added to `whitelist.py`'s existing "Pydantic model
  fields read only via (de)serialization/rendering" section -- the same
  category as REQ's/TSK's/UC's own pre-existing entries there, since none
  of these new field names are accessed as a plain Python attribute
  anywhere in `src/` yet (only through markdown round-tripping today, and,
  from Phase 4 onward, through MCP tool/resource code that doesn't exist
  yet). `items` needed no such entry: it was already kept alive by
  `tsk/models/v1/body.py`'s `Task._validate_items_eagerly`/
  `uc/models/v1/use_case.py`'s existing `self.items`/`self.extensions.items`
  accesses.
- **2026-08-18 (Task 4.4)**: `qa/data/qa_example.md` reuses Phase 2's
  `qa_reference.md` verbatim (byte-identical copy), rather than lightly
  adapting it the way TSK's `tsk_example.md` differs from
  `tsk_reference.md`. Rationale: `qa_reference.md` was already written to
  exercise every field of the schema (both `General` sub-sections, all
  nine categories including one deliberately empty one, a `Requirement`
  callout with a nested list/block-quote edge case, and `More
  Information`) and was already verified, in Phase 3, to round-trip
  byte-exactly through `parse_qa`/`Qa`/`QaFrontmatter` -- there was no
  wording/numbering awkwardness of the kind TSK's own adaptation fixed
  (TSK's reference lacked task numbers a real task list would want), so
  introducing any divergence between the two documents would only be
  extra unforced maintenance surface with no benefit. Re-verified the
  round-trip independently in this phase via a throwaway script before
  relying on it in `get_qa_example`/`specmgr://qa/example`'s tests.
- **2026-08-18 (Task 4.4)**: `qa/data/qa_template.md` was written from
  scratch rather than derived from `qa_reference.md`/`qa_example.md`,
  since a template's job (short, generic placeholder prose signaling
  "fill this in") is different in kind from a reference/example's job
  (a complete, realistic scenario) -- mirrors why `req_template.md`/
  `tsk_template.md` are also hand-written distinct files, not trimmed
  copies of their own examples. It happens to also satisfy every
  `parse_qa` validator (verified), which is a stronger guarantee than
  the task required (only "structurally complete" was mandated) -- this
  is incidental, not a design goal, since a real template's placeholder
  text is explicitly allowed to fail field-level validation.
- **2026-08-18 (Phase 5)**: Placement choices left unpinned by the plan
  text, resolved by following each file's own existing convention rather
  than defaulting to strict alphabetical order everywhere:
  `server.py`'s docstring resources/tools/prompts blocks for `qa` were
  placed after the `tsk` blocks (chronological addition order, matching
  how `req`/`uc`/`tsk` are already ordered relative to each other, not
  alphabetically -- `uc` sorts after `req` there too); `AGENTS.md`'s new
  `qa/` bullet was placed after the `tsk/` bullet for the same reason;
  `pyproject.toml`'s new `"biz.dfch.specmgr.qa"` package-data entry, by
  contrast, was placed alphabetically (`qa` before `req`/`tsk`/`uc`) since
  that table's existing `req`/`tsk`/`uc` ordering already *is* alphabetical
  (with `general` kept last regardless, as a cross-cutting non-domain
  entry, not part of that ordering). `.pre-commit-config.yaml`'s widened
  glob group and the new `specmgr-schema-qa-package` hook's own glob use
  alphabetical order inside the parenthesized group
  (`qa/models/v1|req/models/v1|tsk/models/v1|uc/models/v2|models/md`), per
  the task's own explicit instruction. `.github/workflows/ci.yml`'s two new
  `qa` steps were placed immediately after the existing `tsk` packaged-copy
  step and before `docs/coverage.svg`, alongside the other doc-type schema
  step pairs rather than at the end of the file, matching the task's
  explicit placement instruction.
- **2026-08-18 (Phase 5)**: `AGENTS.md`'s pre-commit/CI enforcement gap
  bullet ("No `validate_adr` (or `validate_req`/.../`validate_tsk`) tool
  runs...") was extended to also mention `validate_qa`, for consistency --
  `qa` has the exact same gap (no pre-commit/CI hook runs `validate_qa`
  over the repo's own `qa` documents) that REQ/UC/TSK already have listed
  there, so omitting it would have been an inconsistent, arbitrary gap in
  an otherwise now-six-domain-wide list.
- **2026-08-18 (Task 4.5)**: `qa`'s tool/resource test suites have no
  `test_raises_validation_error_for_bad_field_value`-equivalent test (the
  one REQ's own `test_create_req.py`/`test_update_req.py`/
  `test_validate_req.py` each carry, exercising a bad `## Level` value).
  Unlike REQ's body, `qa`'s body has no caller-controllable field with its
  own closed-set/pattern validator -- every fixed category heading is a
  *structural* match (fixed heading text via `AliasType.SPACE_SEPARATED`,
  raising `AssertionError` on mismatch, not `pydantic.ValidationError`),
  and every other body field is fully optional free-form prose. The only
  genuine `pydantic.ValidationError` channel in the whole QA lifecycle
  surface is `QaFrontmatter.status`'s four-value closed set, already
  covered by `test_set_status_qa.py`/`test_validate_qa.py`'s "full=True"
  path -- so this is a real, schema-driven asymmetry versus REQ, not a
  coverage gap to fill later.

### Related PRs / Commits

None yet.
