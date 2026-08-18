---
created: 2026-08-18
id: feat-12-qa-artifact
status: planning
updated: 2026-08-18
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

- [ ] Task 0.1: Delete stray untracked scaffolding from an earlier session
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
  contradiction — depends on: none — status: not-started.

- [ ] Task 0.2: Phase-end check (lightweight — no code/tests affected by a
  pure directory deletion) — confirm `git status` and `git status --ignored` show no residue from the deleted paths; update this README's
  Progress section (Current Status, a dated Recent Updates entry) noting
  Phase 0 complete — depends on: Task 0.1 — status: not-started.

#### Phase 1: `models/md` engine enhancement

Standalone, reusable addition to the shared engine; `qa` is its first real
consumer but not the motivating point on its own.

- [ ] Task 1.1: Change `@markdown(...)` to merge into any inherited
  `_metadata` rather than fully replacing it — depends on: none — status:
  not-started.

- [ ] Task 1.2: Add `end_marker: type[MarkdownStr] | None = None` parameter
  to `@markdown` — depends on: Task 1.1 — status: not-started.

- [ ] Task 1.3: `MarkdownSection.get_extent` — add a depth-aware (via
  `Token.nesting`) stop condition for `cls._metadata.get("end_marker")`'s
  `type`/`tag`, alongside the existing heading-level check; only a depth-0
  occurrence stops the scan — depends on: Task 1.2 — status: not-started.

  Note on "depth-0": A real correctness nuance for Phase 1's depth-aware end_marker check. `Token.nesting` itself is already used across `models/md` (see Design Notes), so the primitive is not new — the new part is applying it as a depth counter inside `get_extent`'s stop scan. The plan says "depth-0 occurrence" via Token.nesting, which is correct in principle, but it's worth being explicit now: the depth counter must track every nesting open/close pair in the token stream (list items, other block quotes, etc.), not just the end_marker type's own open/close tokens. Otherwise, e.g., a bullet list legitimately nested inside requirement's own body would throw off the depth count, and a block quote appearing after it could be misjudged as depth-0 when it's actually still nested one level deep — or vice versa. This is exactly the kind of easy-to-get-subtly-wrong logic Task 1.4's edge-case test needs to specifically exercise (a nested list and a nested block quote both inside requirement's own valid content, not just one or the other).

- [ ] Task 1.4: Unit tests — merge-semantics regression (all existing
  `models/md` classes unaffected), new `end_marker` stop behavior, and the
  nested/legitimate-occurrence edge case (an end-marker-type token
  appearing one level deeper inside otherwise-valid content must not
  truncate) — depends on: Task 1.3 — status: not-started.

- [ ] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite covering Task
  1.4's new tests plus the full existing suite for regressions); update
  this README's Progress section (Current Status, a dated Recent Updates
  entry, Decisions Made if applicable); commit as one Conventional Commit
  — depends on: Task 1.4 — status: not-started.

#### Phase 2: Specification

- [ ] Task 2.1: Write a full reference `qa_reference.md` exercising every
  field — depends on: Phase 1 complete — status: not-started.

  **Plan correction (2026-08-18, see Decisions Made):** the former Task
  2.2 ("Draft `qa_schema.json`") has moved to Phase 3 as Task 3.1.1 —
  schema generation needs `QaDocument` to exist
  (`QaDocument.model_json_schema()`), which isn't defined until Task 3.1,
  not just the reference markdown file this phase produces (same bug
  feat-10 hit and fixed in its own Decisions Made log, moving its
  equivalent task from Phase 1 to Phase 2 as Task 2.5). Task numbering is
  intentionally left with a gap at 2.2 rather than renumbering Task 2.3
  or any later task.

- [ ] Task 2.3: Phase-end check — no Pydantic models exist yet in this
  phase, so no unit-test suite applies; instead confirm `qa_reference.md`
  is well-formed (`specmgr mdformat` clean) and run the general
  pre-commit/quality gate (ruff format/check, vulture) over any changed
  files; update this README's Progress section (Current Status, a dated
  Recent Updates entry) noting Phase 2 complete — depends on: Task 2.1 —
  status: not-started.

#### Phase 3: Pydantic Models & Parser

- [ ] Task 3.1: `qa/models/v1/{frontmatter,body,document,parser,summary, _util}.py`, including `Requirement`'s `end_marker` wiring (leaf class,
  deliberately unspecified/arbitrary agent-authored content -- see Design
  Notes) and resolving the 9-category class-sharing question (see Design
  Notes) — depends on: Task 2.1 — status: not-started.

- [ ] Task 3.1.1 (moved from former Phase 2 Task 2.2, folded together with
  former Phase 5 Task 5.2, see Decisions Made): Implement
  `generate_qa_schema()` in `commands/schema.py` (mirroring
  `generate_req_schema`/`generate_uc_schema`/`generate_tsk_schema`, via
  `QaDocument.model_json_schema()`, JSON Schema 2020-12) and register
  `"qa"` in the `specmgr schema` doc-type generator registry
  (`_GENERATORS`); draft `docs/qa_schema.json` by running it — mirrors
  feat-10's own Task 2.5 exactly (generator + registry + draft, as one
  task, right after the document model exists) — depends on: Task 3.1 —
  status: not-started.

- [ ] Task 3.2: Unit tests + full parser round-trip against
  `qa_reference.md` — depends on: Task 3.1 — status: not-started.

- [ ] Task 3.3: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite including Task
  3.2's new tests); update this README's Progress section (Current
  Status, a dated Recent Updates entry, Decisions Made if applicable);
  commit as one Conventional Commit — depends on: Task 3.1.1, Task 3.2 —
  status: not-started.

#### Phase 4: MCP Surface

- [ ] Task 4.1: `qa/tools/{_paths,_io,_lock,_write,parse_qa,get_qa, get_qa_example,get_qa_template,create_qa,update_qa,set_status_qa, delete_qa,validate_qa}.py` — 1:1 port of REQ's tool plumbing — depends
  on: Task 3.1 — status: not-started.

- [ ] Task 4.2: `qa/resources/{qa_schema,qa_example,qa_template, qa_list}.py` — depends on: Task 4.1 — status: not-started.

- [ ] Task 4.3: `qa/prompts/{create_qa,update_qa}.py` — depends on: Task
  4.1 — status: not-started.

- [ ] Task 4.4: `qa/data/{qa_example.md,qa_template.md,qa_schema.json}` +
  `qa/__init__.py` — depends on: Tasks 4.1-4.3 — status: not-started.

- [ ] Task 4.5: `tests/qa/{tools,resources,prompts}/` mirroring
  `tests/req/{tools,resources,prompts}/`'s layout and coverage — depends
  on: Tasks 4.1-4.4 — status: not-started.

- [ ] Task 4.6: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite including Task
  4.5's new tests); update this README's Progress section (Current
  Status, a dated Recent Updates entry, Decisions Made if applicable);
  commit as one Conventional Commit — depends on: Task 4.5 — status:
  not-started.

#### Phase 5: Cross-cutting registration

- [ ] Task 5.1: `server.py` — add `qa` to the bottom import line, update
  the module docstring — depends on: Phase 4 complete — status:
  not-started.

  **Plan correction (2026-08-18, see Decisions Made):** the former Task
  5.2 (`generate_qa_schema()` + registry entry) has been folded into
  Phase 3's Task 3.1.1 instead, right after `QaDocument` is defined,
  mirroring feat-10's own Task 2.5. Task numbering is intentionally left
  with a gap at 5.2 rather than renumbering Tasks 5.3-5.8.

- [ ] Task 5.3: `pyproject.toml` — `"biz.dfch.specmgr.qa" = ["data/*.md", "data/*.json"]` package-data entry — depends on: Task 4.4 — status:
  not-started.

- [ ] Task 5.4: `.pre-commit-config.yaml` — widen the shared schema-hook
  glob to include `qa/models/v1`; add a `specmgr-schema-qa-package` hook —
  depends on: Task 3.1.1 — status: not-started.

- [ ] Task 5.5: `.github/workflows/ci.yml` — add the `docs/qa_schema.json`
  check + packaged-copy check steps — depends on: Task 3.1.1 — status:
  not-started.

- [ ] Task 5.6: `AGENTS.md` — update to six domain/cross-cutting packages
  — depends on: Phase 5 complete — status: not-started.

- [ ] Task 5.7: `specmgr docs` / `specmgr mcp-docs` regeneration, `specmgr schema --type qa` — confirm the `qa` domain appears correctly and all
  three commands report zero drift now that registration (Task 3.1.1,
  Tasks 5.1, 5.3-5.6) is complete — depends on: Task 3.1.1, Task 5.1,
  Tasks 5.3-5.6 — status: not-started.

- [ ] Task 5.8: Phase-end quality gate — run the full pre-commit/quality
  gate (ruff format/check, vulture, full `unittest` suite); update this
  README's Progress section (Current Status, a dated Recent Updates
  entry, Decisions Made if applicable); commit as one Conventional Commit
  — depends on: Task 5.7 — status: not-started.

#### Phase 6: Final cross-cutting verification

- [ ] Task 6.1: Final verification pass — walk every ACC-001..006 and
  confirm each is satisfied with concrete evidence; run the full quality
  gate (ruff format/check, pylint advisory, vulture, unittest, `specmgr docs`, `specmgr mcp-docs`, `specmgr schema --type qa` drift checks) one
  last time end-to-end; update this README's Progress section (Current
  Status, a dated Recent Updates entry) and set feature status to `done`
  — depends on: Phase 0-5 complete — status: not-started.

## Progress

### Current Status

**As of 2026-08-18**: Planning complete. Schema design, the `end_marker`
engine enhancement, and the full task breakdown are agreed. Implementation
has not started (deliberately deferred per explicit instruction — plan-only
so far).

### Blockers

None currently.

### Recent Updates

Older entries (2026-08-18T11:15:00Z and earlier) are archived in
[`history.md`](history.md).

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

### Related PRs / Commits

None yet.
