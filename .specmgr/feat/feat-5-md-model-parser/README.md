---
created: '2026-08-08 00:00:00.000Z'
id: feat-5-md-model-parser
status: done
updated: '2026-10-07T06:21:40.940Z'
version: 1.0.0
---

# Feature: Generic heading-mapped Markdown-to-Pydantic document parser

## Plan

### Overview

A generic, document-type-agnostic engine that parses a whole Markdown document
(YAML frontmatter + nested heading structure) into a typed Pydantic model tree,
and renders it back to Markdown. Fields declare which heading they correspond
to via `Annotated[SomeMarkdownStr, Heading(tag=..., alias=...)]` metadata; the
parser recurses into any field whose type itself declares further
`Heading`-annotated fields, so a document's nesting depth (e.g. an `##`
section containing several `###` sub-sections) is fully represented as typed,
individually-validated fields rather than an opaque text blob. Content
constraints (allowed tags, length, no-raw-HTML, opt-in round-trip fidelity)
are expressed as composable `Annotated` markers evaluated by one shared
validator, instead of a hand-written `model_validator` per model class.

This is a **sibling, not a superset or replacement**, of
`feat-3-md-str-constraints` (a separate, regex-based `MdStr` type for
constraining a single plain-string field's inline Markdown, e.g. a `name` or
`description` field). The two solve different-shaped problems: feat-3
constrains one string field's permitted inline syntax; this feature parses
and validates the structure of an entire multi-section document. They are
tracked independently and neither blocks the other.

### Requirements

- REQ-001: Define a `@markdown(type=, tag=)` class decorator (`markdown.py`) attaching a `_metadata` dict (markdown-it token `type`/HTML `tag`) to a `MarkdownStr` subclass, and six concrete `MarkdownSection1`..`MarkdownSection6` base classes (`markdown_section1.py`..`markdown_section6.py`) that each pin `tag` to `h1`..`h6` respectively — heading level is expressed as which base class is inherited, not as `Annotated` field metadata. Separately, an opt-in `@alias(value=, type=)` class decorator (`alias.py`, `alias_type.py`'s `AliasType.LITERAL`/`SPACE_SEPARATED`/`REGEX`) attaches `_alias_metadata` used only for identity matching at parse time (`alias_match.match_alias`), never for rendering; a class with no `@alias` at all defaults to `AliasType.SPACE_SEPARATED`'s derivation of its own class name (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0), not "accept any heading text". `LITERAL` matching is exact and case-sensitive (no normalization, no trailing-parenthetical stripping) — a heading like `"Extensions (optional)"` must be declared verbatim, since `SPACE_SEPARATED`'s automatic class-name-derived alias cannot express such suffixes. Field optionality (`X | None`) is driven only by the Python type (`MarkdownStr._unwrap_optional`), never by heading text.
- REQ-002: Define `MarkdownStr` (`markdown_str.py`), a Pydantic base model storing its rendered text verbatim in a private `_value: str` attribute (not parsed `markdown-it-py` tokens retained on the instance), exposing `__str__`/`__repr__` that return `_value` unchanged for a leaf class (no nested `MarkdownStr` fields) or the `mdformat`-normalized concatenation of every nested field's own `__str__()` for a composite class.
- REQ-003: Implement a recursive parser, `MarkdownStr.from_text(text) -> MarkdownStr` (overridden by `MarkdownSection.from_text` for heading-bearing classes), that tokenizes `text` once per recursion step via a shared module-level `MarkdownIt` instance (`_markdown.py`), and recursively slices it into one block per declared nested field (in declaration order) using that field type's own `get_extent(text)` to determine the block boundary, to arbitrary nesting depth. Frontmatter splitting is explicitly **not** this engine's responsibility (see REQ-006) — callers strip it before calling `from_text`.
- REQ-004: Implement the inverse `MarkdownStr.__str__`/`MarkdownSection.__str__`, producing Markdown text from a populated model instance. Because every leaf `_value` retains its complete heading+body extent verbatim (not just inline content), `str(instance)` reproduces the exact `mdformat`-normalized text `from_text` consumed — a byte-exact round-trip by construction, not merely a structural one. **Accepted exception (2026-08-11, Task 1.6.3):** `list[MarkdownListItem]` content is the one case where this is only structural, not byte-exact — a genuinely *tight* source list round-trips to an equivalent *loose* list (see `markdown_list_item.py`'s class docstring); loose lists are unaffected. This matches this feature's own founding ADR, which already treats list-rendering variance as out of scope for byte-exact fidelity.
- REQ-005: *(done, rescoped 2026-08-11)* Reject raw HTML (both HTML blocks and inline HTML tags) anywhere in a parsed document. Landed as one choke point, `_markdown.py`'s `parse(text) -> list[Token]` (wrapping `md.parse(text)` plus a recursive `_assert_no_raw_html` walk that also descends into every `"inline"` token's `.children`, since `html_inline` tokens only ever appear there, never in the top-level token list — verified empirically), which every `get_extent`/`from_text` in `markdown_str.py`/`markdown_section.py`/`markdown_paragraph.py`/`markdown_list_item.py`/`markdown_code_block.py`/`markdown_block_quote.py` now calls instead of `md.parse(text)` directly — the same "one shared call site" convention `format_text` already established for `mdformat` options. `MarkdownStr.from_text`'s leaf branch (the one place that previously stored `_value` without ever tokenizing it) gained an explicit `parse(text)` call so a leaf class reached directly, not just via a composite parent's `get_extent`, is still checked. This also covers `MarkdownParagraph`/`MarkdownListItem`/`MarkdownCodeBlock`/`MarkdownBlockQuote`, not only the two classes this REQ's own wording names. **Superseded scope note:** the previously-planned generic, composable `Annotated`-based constraint-marker framework (`AllowedTags(tags)`, `LengthConstraint(min_length=, max_length=)`, a generic `NoRawHtml()` marker, all evaluated by one shared validator, plus a `constraints.py` module) was dropped as speculative — only `@markdown`/`@alias` exist and are actually planned as class-level decorators; no `AllowedTags`/`LengthConstraint` mechanism is planned. Raw-HTML rejection is the one concrete, decided need and is tracked directly as this REQ, not as an instance of a generic marker framework. If another concrete constraint need arises later (e.g. a length limit), it should be scoped as its own fresh requirement then, not slotted into a speculative framework revived for the occasion. The previously-noted opt-in `RoundTrip()` marker remains moot regardless: REQ-004's byte-exact round-trip is already the engine's unconditional default behavior, not an opt-in feature to gate.
- REQ-006: *(done, 2026-08-11)* Per ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29, added `MarkdownFrontmatter` (`models/md/frontmatter.py`), a base Pydantic model with the core fields `id`, `type`, `created`, `updated`, `status`, `version` shared by every markdown-backed document type. `type` is mandatory on the base with no default (non-blank, enforced) — a concrete document type (e.g. a future `uc`/`req`) subclasses `MarkdownFrontmatter` and narrows `type` to a fixed `Literal["..."]` value with a default, acting as a discriminator a generic loader could read before knowing which concrete subclass to validate the rest of the block against. `status` defaults to `"draft"` (blank/`None` normalizes to it too) but, unlike `AdrFrontmatter.status`'s closed six-value enum, is deliberately left free-form here — different document types may want different status vocabularies, and a subclass can add its own stricter validator. `version` is validated against this package's own `SCHEMA_MAJOR_VERSION`/`CURRENT_SCHEMA_VERSION` (`models/md/_util.py`), independent of `models.adr.v1._util`'s equivalent constants — no shared validator module was introduced (per repo-owner direction: `AdrFrontmatter` stays untouched/unconverted for now; a future convergence remains possible but undecided). Frontmatter *stripping* itself is still not this engine's job (unchanged from the original REQ-006 note) — `frontmatter.loads(text).content`/`.metadata` (`python-frontmatter`) remains the caller's responsibility; `MarkdownFrontmatter` only validates `.metadata` once stripped, it does not touch `.content`.
- REQ-007: Provide a fixture model reproducing the full nested structure of `tests/feat-5-md-model-parser/uc_example.md` (all three heading levels: `# Buy Goods` → nine `##` sections → all `###` children under `## Characteristic Information`/`## Related Information`), proving the recursive engine end-to-end, including a mix of required and `Optional[...]` fields. Landed as `UseCase`/`CharacteristicInformation`/etc. in `tests/models/md/test_uc_example.py` (distinct from the smaller, earlier `tests/models/md/various_models.py` fixture, which stays as a minimal unit-test double, not a superset of this one). This fixture is a proof of the generic engine, not the official use-case domain model (that ownership stays with `feat-4-use-cases`, if/when it chooses to adopt this engine). `Extensions`/`Sub-Variations`/`Open Issues` are modelled as leaf `MarkdownSection2`s (their dynamically-named, per-use-case h3 sub-headings are inert text) since the engine has no "repeated/list section" concept yet.
- REQ-008: Add unit tests per building block (`@markdown`/`@alias`/`match_alias` behavior, `MarkdownStr.get_extent`/`from_text`/`__str__`, `MarkdownSection.get_extent`/`from_text`/`__str__`, `Optional[...]` field handling) plus an integration test that round-trips `MarkdownSection1.from_text`/`__str__` against both fixtures end-to-end.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — `MarkdownSection.from_text` rejects a heading whose `(type, tag)` doesn't match the class's own `@markdown` metadata (e.g. a class declaring `h2` fails against an `h3` heading at that position — `test_markdown_section.py`), and, independently, rejects a heading whose text doesn't satisfy a declared `@alias` while a class with no `@alias` matches the `AliasType.SPACE_SEPARATED` derivation of its own class name, not any heading text (`test_alias_match.py`, `TestMarkdownSectionAliasEnforcement`). `LITERAL` matching is exact/case-sensitive by design (not case-insensitive, no parenthetical stripping) — covered by `test_literal_is_case_sensitive_with_no_normalization`.
- [x] ACC-002: Verifies REQ-002 — `MarkdownStr.from_text(text).__str__()` round-trips at least: a single leaf paragraph (`test_leaf_class_stores_value_verbatim`), a multi-field composite document (`test_distributes_lines_across_fields_using_get_extent`), and inline-formatted content (heading text containing `*emphasis*`/`**strong**`, `test_leaf_section_preserves_inline_formatting_in_heading`).
- [x] ACC-003: Verifies REQ-003 — `MarkdownSection1.from_text` on both the `various_models.py` fixture (two levels: `MainDocument` → `CharacteristicInformation`/`RelatedInformation` → h3 leaves) and the full `uc_example.md` fixture (three levels, ~15 h3 fields under `Characteristic Information`) populates every declared field, with a mandatory trailing-completeness assertion (`remaining_text == ""`) that fails loudly on any leftover unclaimed heading (`test_main_document_from_text`, `test_parses_title_and_top_level_sections`, `test_parses_all_characteristic_information_fields`).
- [x] ACC-004: Verifies REQ-004 — `str(MarkdownSection1.from_text(text)) == text` holds exactly (byte-exact, not just structural) for both fixtures (`various_models.py`'s `MainDocument`, `uc_example.md`'s `UseCase` — `test_round_trip_reproduces_the_source_document`).
- [x] ACC-005: Verifies REQ-005 — `tests/models/md/test_markdown_html_rejection.py` (12 cases): `_markdown.parse` raises on an `html_block`, on `html_inline` nested inside a paragraph's or a heading's `inline` children, and stays unaffected by plain Markdown formatting (`**strong**`/`*emphasis*`) and by HTML-looking text inside a fenced code block (opaque code, not raw HTML); plus end-to-end cases through `MarkdownStr.from_text` (leaf) and `MarkdownSection.from_text` (leaf, `html_block` in body / `html_inline` in heading) confirming both raise loudly and both stay unaffected by plain formatting. No `AllowedTags`/`LengthConstraint` cases are planned (see REQ-005's superseded-scope note); the `RoundTrip()`-inactive-by-default half of the original criterion no longer applies either.
- [x] ACC-006: Verifies REQ-006 — `tests/models/md/test_frontmatter.py` (19 cases): `MarkdownFrontmatter` rejects a missing/blank `type`, defaults `status`/`version` correctly (including blank-normalizes-to-default), rejects a mismatched-major/malformed `version`, normalizes blank `created`/`updated` to `None`; plus `TestMarkdownFrontmatterSubclassing` proving a document-type subclass can narrow `type` to a fixed `Literal[...]` (default applies with no explicit `type=`, a mismatched value is rejected), inherits the base's `status`/`version` defaults, and may add its own further fields. `test_uc_example.py::setUpClass` is unchanged — it still only strips via `python-frontmatter` and never constructs a `MarkdownFrontmatter`, since wiring a concrete `uc` frontmatter subclass into that fixture is out of scope for this feature (fixture proves the generic engine, not the official use-case domain model).
- [x] ACC-007: Verifies REQ-007 — `UseCase.from_text` (`tests/models/md/test_uc_example.py`) successfully parses the entirety of `tests/feat-5-md-model-parser/uc_example.md`'s body (post frontmatter-stripping) without falling back to an untyped/opaque blob for any `##`/`###` section — every field down to `RelatedUseCases`/`Assumptions` is a typed `MarkdownSection3`, not a dict or raw string.
- [x] ACC-008: Verifies REQ-008 — Full suite passes under `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (374 tests as of this reconciliation, all for this feature's modules under `tests/models/md/` passing, none skipped).

### Scope

#### Included

- `src/biz/dfch/specmgr/models/md/markdown_str.py` — `MarkdownStr` base
  model: `get_extent()` (generic, non-heading-aware fallback), `from_text()`
  (recursive field-by-field slicing via `process_field()`), `__str__`
- `src/biz/dfch/specmgr/models/md/markdown_section.py` — `MarkdownSection`
  abstract base: `get_extent()` override (heading-level-aware: stops at any
  sibling/ancestor heading, i.e. level `<= own_level`; nested deeper headings
  are included), `from_text()` (validates the heading triple against
  `@markdown`'s `_metadata` and, via `match_alias`, against any declared
  `@alias`; delegates body population to `MarkdownStr.from_text`), `__str__`
  (heading re-emission for composite sections), `name` computed field
- `src/biz/dfch/specmgr/models/md/markdown_section1.py` .. `markdown_section6.py`
  — concrete `MarkdownSection` subclasses for h1..h6, each just supplying
  `@markdown(type="heading_open", tag="hN")`
- `src/biz/dfch/specmgr/models/md/markdown.py` — `@markdown(type=, tag=)`
  class decorator attaching `_metadata`
- `src/biz/dfch/specmgr/models/md/alias.py` / `alias_type.py` — `@alias`
  decorator attaching `_alias_metadata` (display naming, independent of
  `@markdown`)
- `src/biz/dfch/specmgr/models/md/alias_match.py` — `match_alias(cls, heading_text)`, enforcing that a parsed heading's actual text satisfies
  the class's declared `@alias` (`LITERAL`/`SPACE_SEPARATED`/`REGEX`), used
  by `MarkdownSection.from_text`; a class with no `@alias` at all always
  matches (opt-in, not mandatory)
- `src/biz/dfch/specmgr/models/md/_markdown.py` — shared module-level
  `MarkdownIt` instance (`md`)
- `src/biz/dfch/specmgr/models/md/frontmatter.py` — `MarkdownFrontmatter`,
  the base frontmatter model (`id`/`type`/`created`/`updated`/`status`/
  `version`) every document type's own frontmatter model subclasses,
  per ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (REQ-006)
- `src/biz/dfch/specmgr/models/md/_util.py` — private validator helpers
  (`blank_to_none`, `default_if_blank`, `validate_schema_version`) and
  `SCHEMA_MAJOR_VERSION`/`CURRENT_SCHEMA_VERSION` for `MarkdownFrontmatter`,
  deliberately independent of `models/adr/v1/_util.py`'s equivalents
- `tests/models/md/various_models.py` — the smaller, hand-built fixture
  model tree (`MainDocument`, `CharacteristicInformation`, `GoalInContext`,
  `Scope`, `RelatedInformation`, `Notes`, `Assumptions`), each inheriting
  its heading tag from the appropriate `MarkdownSectionN` base rather than
  redeclaring `@markdown(...)` itself. Lives under `tests/`, not `src/`,
  since it is a test-only fixture proving out the recursive `from_text`
  mechanics, not production code (moved there after initially landing
  under `src/`).
- `tests/models/md/test_uc_example.py` — a second, larger fixture model
  tree (`UseCase`, `CharacteristicInformation`, `MainSuccessScenario`,
  `Extensions`, `SubVariations`, `OpenIssues`, `RelatedInformation`, and all
  ~15 `###` leaves under `Characteristic Information`) that reproduces the
  full structure of `tests/feat-5-md-model-parser/uc_example.md` end-to-end
  (REQ-007/ACC-007), including required vs. `Optional[...]` fields and
  frontmatter stripped externally via `python-frontmatter` (not by this
  engine — see REQ-006).
- Tests under `tests/models/md/` (`test_markdown_str.py`,
  `test_markdown_section.py`, `test_alias_match.py`, `test_uc_example.py`,
  `test_frontmatter.py`)

**Reconciled with actual implementation (2026-08-11):** the original plan's
`heading.py` (`Annotated[Heading(...)]` metadata), `constraints.py`,
`frontmatter.py`, and `parser.py`/`render_document` never landed under those
names, and are not expected to — the class-hierarchy approach
(`MarkdownSection1`..`6` + `@markdown`/`@alias`) permanently replaced the
annotation-metadata approach originally described in REQ-001/003 (see ADR
832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.1.0). The Requirements/Acceptance
Criteria/Task List sections now describe this actual design; a typed
frontmatter model (REQ-006) remains genuinely not-started work, not stale
documentation.

**Rescoped (2026-08-11, later same day):** REQ-005 no longer plans a generic,
composable `Annotated`-based content-constraint-marker framework
(`AllowedTags`/`LengthConstraint`/a generic `NoRawHtml()` marker/
`constraints.py`) — that was speculative and never actually decided beyond
`@markdown`/`@alias`. REQ-005 is now the one concrete, decided need instead:
reject raw HTML anywhere in a parsed document. See REQ-005 for the
superseded-scope rationale.

#### Explicitly Out Of Scope

- Migrating the existing ADR parser/renderer (`models/adr/v1/parser.py`, `renderer.py`) onto this engine — ADR 4c6119c9 stays as-is
- The regex-based `MdStr`/`MdStrConstraints` single-field string type — owned by `feat-3-md-str-constraints`, a different mechanism for a different problem shape
- Defining the official use-case (`uc`) domain model/schema — owned by `feat-4-use-cases`; this feature only proves the generic engine via a fixture
- A generic, composable content-constraint-marker framework (`AllowedTags`/`LengthConstraint`, a `constraints.py` module, a shared validator reading opt-in markers) — dropped as speculative (see REQ-005's rescoping note above); only the concrete raw-HTML rejection in REQ-005 is planned. The engine's byte-exact round-trip (REQ-004) remains unconditional/always-on by construction, not an opt-in `RoundTrip()` marker as originally scoped
- Any `tools`/`prompts`/`resources` MCP surface for a new document type — this feature is schema/engine only, following the `models/adr/v1` precedent of landing the schema layer before any domain package

### Dependencies

#### Depends On

- ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy, shared versioned `models/`), ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae (this feature's own heading-recursion engine design decision), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (this feature's frontmatter model design decision, REQ-006/Task 4.1)
- Related, not blocking: `feat-3-md-str-constraints` (separate regex-based string constraint type), `feat-4-use-cases` (may evaluate adopting this engine for its UC schema later; not assumed here)
- External: adds `markdown-it-py` (+ a YAML frontmatter parsing dependency) to the library's **base** dependencies, since parsing is core library behavior, not CLI/MCP-only

### Design Notes

Single, canonical breakdown of work phases and tasks in the Task List below.
Status lives on the task itself — there is no separate "planned" vs.
"executed" list to keep in sync; a task's line *is* its current status.
Update it in place as work progresses (edit, don't duplicate).

**Note (2026-08-11 reconciliation, Task List):** phases/tasks in the Task
List below replace the original `heading.py`/`constraints.py`/
`frontmatter.py`/`parser.py`-shaped breakdown (superseded design, see
Requirements above) with the actual `models/md/` module layout. Task
numbering restarts at Phase 0 but no history is lost — the original phase
text remains recoverable via `git log -p` on this file. If a task's scope
changes mid-flight, edit its description in place; rely on git history
(`git log -p` on this file) to recover what was originally planned, rather
than keeping a second copy of the task around.

**Note (2026-08-11 reconciliation):** the list in Requirements above replaces
the original `Annotated[Heading(...)]`/`parse_document`/`render_document`/
`constraints.py`/`frontmatter.py`-shaped requirements (see prior revisions in
`git log -p` on this file) with what `src/biz/dfch/specmgr/models/md/` and
`tests/models/md/` actually implement, per ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae
v1.1.0's superseding design (class hierarchy + class-level alias + cursor-
based recursive descent, not field-level `Annotated` metadata).

See ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae (v1.5.0) for the full rationale,
considered alternatives (imperative class decorator; convention-only field
name matching), and the actual-vs.-originally-sketched implementation
reconciliation. Key points carried over here for quick reference (updated
2026-08-11 to match that reconciliation — see git history for the earlier,
now-superseded bullets this replaced):

- Recursive slicing algorithm: for a field's own extent (from its
  `heading_open` line through just before the next sibling/ancestor heading,
  i.e. level `<=` its own — `MarkdownSection.get_extent`), any child field
  whose type itself declares nested `MarkdownStr` fields is parsed from that
  slice at the next heading level down (`MarkdownStr.from_text`'s recursion).
  A leaf field's complete extent (heading + body, or just the body for a
  non-heading leaf) is stored verbatim in its own private `_value: str`
  (not retained `markdown-it-py` tokens), so `__str__` at any level
  reproduces that whole subtree by concatenating its children's own
  `__str__()`.
- No constraint-marker mechanism is planned as opt-in composables on
  `MarkdownStr` fields — that generic framework (`AllowedTags`/
  `LengthConstraint`/a generic `NoRawHtml()` marker) was dropped as
  speculative (see REQ-005's 2026-08-11 rescoping above). The only content
  constraint currently planned is REQ-005's concrete raw-HTML rejection,
  which is not field-opt-in — it applies unconditionally to every
  `MarkdownStr.from_text`/`MarkdownSection.from_text` call once implemented.
- Originating sketch and fixture: `tests/feat-5-md-model-parser/req_parser.py`,
  `tests/feat-5-md-model-parser/uc_example.md` (fixture file is reused
  as-is; this feature's own model/tests live under `tests/models/md/`, not
  `tests/models/markdown/v1/` as originally sketched here).

### Related Decisions

- 832cd6c1-ef8a-4bfc-990e-a610823f61ae: Generic heading-mapped markdown-to-Pydantic parsing with declarative Heading metadata and opt-in constraints
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for markdown document types (`models/md/frontmatter.py`)
- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)
- 4c6119c9-532f-4629-8977-108e78304f48: Parse-validate-render pipeline for ADRs (related, not superseded — this feature does not migrate the ADR pipeline)

### Task List

#### Phase 100: Preparation

- [x] Task 100.100: Create module level md parser instance in `src/biz/dfch/specmgr/models/md/_markdown.py` (shared `MarkdownIt` instance, `md`)
- [x] Task 100.110: Create `class MarkdownStr(BaseModel)` (`markdown_str.py`) — landed as a plain Pydantic `BaseModel` with a private `_value: str` attribute, not a `StrictStr` subclass as originally sketched

#### Phase 110: Metadata/identity decorators

- [x] Task 110.100: Create `markdown.py` — `@markdown(type=, tag=)` class decorator attaching `_metadata` (markdown-it token `type`/HTML `tag`) — depends on: none — status: done
- [x] Task 110.110: Create `alias_type.py` — `AliasType` (`LITERAL`/`SPACE_SEPARATED`/`REGEX`) and `alias.py` — `@alias(value=, type=)` class decorator attaching `_alias_metadata` (opt-in, parse-time identity only, never used for rendering) — depends on: none — status: done
- [x] Task 110.120: Create `alias_match.py` — `space_separated_name(class_name)` and `match_alias(cls, heading_text)`, enforcing a declared `@alias` (or always matching if none declared) — depends on: Task 1.2 — status: done
- [x] Task 110.130: Create `markdown_section1.py`..`markdown_section6.py` — concrete `MarkdownSection` subclasses for h1..h6, each just supplying `@markdown(type="heading_open", tag="hN")` — depends on: Task 2.1 (below) — status: done. h4/h5/h6 additionally needed a bugfix (a live, always-crashing `_tokens`-based assertion left over from before `_value` replaced `_tokens`, see Recent Updates) and dedicated test coverage (`tests/models/md/test_markdown_section_levels.py`), neither of which existed until this reconciliation.
- [x] Task 100.120: ~~Create `metadata_utils.py`~~ — **removed 2026-08-11**: `_metadata` introspection helpers (`get_direct_metadata`, `get_inherited_metadata`, `find_metadata_source`, `get_metadata_chain`, `has_metadata`) were dead code — never called by the core recursion path, never re-exercised by any test, and its own docstring examples referenced a nonexistent `@annotate` decorator (the real one is `@markdown`). Deleted the module, its `docs/api/` page, and its `models/md/__init__.py` re-exports rather than backfilling tests for unused code — depends on: Task 1.1 — status: removed
- [x] Task 110.140: Unit tests for Tasks 1.1–1.5 (`test_alias_match.py`: `space_separated_name` conversion cases, every `match_alias` branch including no-alias-always-matches and `LITERAL`'s case-sensitivity) — depends on: Task 1.3 — status: done
- [x] Task 110.150: Support `list[MarkdownStr]` (or `list[SomeMarkdownStrSubclass]`) fields in `markdown_str.py`'s `_get_field_names`/`from_text`/`__str__`. Detection: `_unwrap_list(annotation) -> tuple[type, bool]` (sibling to `_unwrap_optional`, plain `list[X]` only via `typing.get_origin(annotation) is list` — no `Sequence`/`tuple` support), applied after `_unwrap_optional` so `list[X] | None` unwraps to `(X, optional=True, is_list=True)`. Consumption: `process_list_field(name, item_type, text, *, optional=False) -> tuple[str, list[MarkdownStr] | None]` — deliberately **not** mirroring `process_field`'s `(extent, value)` contract (an earlier draft did and was wrong: summing per-item extents against a locally-renormalized string silently loses lines dropped by `mdformat.text()` between items, e.g. a separating blank line, causing `from_text`'s generic `remaining_text.splitlines()[extent:]` slice to misalign against the caller's *original*, not-yet-renormalized `remaining_text` — the exact class of bug `from_text` itself already moved off a line-index `cursor` to avoid). Instead it loops `item_type.get_extent`/slice/`mdformat`-renormalize/`item_type.from_text` while extent `> 0` and returns the already-fully-reduced `remaining_text` string directly, which `from_text` adopts as-is for list fields (bypassing the generic extent-slicing step used for scalar fields). No item found on the *first* iteration is an absence (mandatory `list[X]` -> assertion error, matching today's missing-mandatory-scalar-field behavior; `list[X] | None` -> field left `None`, `text` returned unchanged) while no item found on any *subsequent* iteration just ends the list normally (items 2+ are implicitly optional without needing `Optional[X]` themselves). Rendering: `__str__` iterates the list and appends `str(item)` per element, same as today's single-field append, skipping a `None` list exactly like an absent optional scalar field — depends on: Task 2.1 — status: done
- [x] Task 110.160: Support base object `MarkdownParagraph` (`markdown_paragraph.py`) — a single class (`@markdown(type="paragraph_open", tag="p")`, no level spectrum, no `@alias` enforcement — a paragraph's text is free-form content, not a title). Leaf case (no declared fields): `get_extent`/`from_text` claim exactly the paragraph's own line span, nothing more — content that follows (even a sibling paragraph) is left untouched, unlike a leaf `MarkdownSection`'s greedy-to-next-heading behavior. Composite case (has declared `MarkdownStr`/`list[MarkdownStr]` fields): `_value` holds only the paragraph's own inline text; the remainder is delegated to `super().from_text()` (`MarkdownStr.from_text`) for field population, exactly like `MarkdownSection.from_text` delegates its post-heading body — bounded, in `get_extent`, only by the next heading of *any* level (h1-h6), since a paragraph has no level of its own and can never itself contain a heading. `__str__` mirrors `MarkdownSection.__str__` minus the heading-marker reconstruction — depends on: Task 2.1 — status: done
- [x] Task 110.170: Support `MarkdownListItem` (`markdown_list_item.py`), a single, subclassable, leaf-or-composite class shared by bullet and ordered lists, used only as `items: list[MarkdownListItem]`/`list[MarkdownListItem] | None` on whatever `MarkdownSection`/`MarkdownParagraph`/`MarkdownListItem` wants a list-shaped field — deliberately **not** a dedicated `MarkdownList`/`MarkdownBulletList`/`MarkdownOrderedList` container class (an earlier-drafted design, discarded before implementation once the container turned out to add no capability the existing `list[MarkdownStr]` machinery didn't already provide). Leaf case (no declared fields): `_value` = the item's complete extent verbatim, marker and any un-modelled nested content included. Composite case (a subclass declares fields, e.g. a nested `list[MarkdownListItem]` for a sub-list): `_value` = the item's own leading paragraph verbatim *including its marker* (not marker-free like `MarkdownParagraph`'s `_value`, since a list item's marker cannot be reconstructed from class metadata alone — it depends on bullet-vs-ordered and, for ordered lists, final position); `__str__` re-indents the declared fields' rendered output by the marker's own width before recombining. A computed `text` field (mirroring `MarkdownSection.name`) exposes the leading paragraph's marker/indent-free text. Required a cross-cutting fix, `_markdown.py`'s new `format_text()` (`mdformat.text(text, options={"number": True})`), adopted by every normalization call site in `markdown_str.py`/`markdown_section.py`/`markdown_paragraph.py`/`test_uc_example.py` — `mdformat`'s default option collapses every ordered-list item to `"1."` on each normalization pass (only the first number is CommonMark-semantically meaningful), which would otherwise make real sequential numbering unrepresentable. Accepted, documented exception to REQ-004: a genuinely *tight* source list currently round-trips to a structurally-equivalent *loose* list (loose lists round-trip byte-exact) — see `markdown_list_item.py`'s class docstring — since each item is independently `mdformat`-renormalized in isolation before the parent's existing `list[MarkdownStr]` `__str__` rejoins them, which is where the tight/loose distinction (a property of the gap *between* items) is unavoidably lost. Restriction: `MarkdownListItem` can only be used inside `list[MarkdownListItem]`, never as a bare top-level/scalar field, since `get_extent`/`from_text` require the enclosing `bullet_list_open`/`ordered_list_open` wrapper token — depends on: Task 2.1 — status: done
- [x] Task 110.180: Create `MarkdownCodeBlock` (`markdown_code_block.py`) — renamed from the originally-scoped `MarkdownCodeFence` once the design settled on handling only fenced (```` ``` ````) code blocks, never indented (4-space) ones — a single, **leaf-only** class (no composite/subclassing case, unlike `MarkdownParagraph`/`MarkdownListItem`), `@markdown(type="fence", tag="code")`. markdown-it tokenizes a fenced block as one self-closing token (`nesting == 0`), not an open/mid/close triple, whose own `.map` already spans exactly the fence markers + content, so `get_extent` is just `tokens[0].map[1]` (or `0` if the first token doesn't match `type`/`tag`) — no stop-condition scan needed. `from_text` asserts the single-token match (`type`/`tag`/`nesting == 0`) and stores the *complete extent verbatim* in `_value` (fence markers, info string if any, and code content) — same "leaf stores its full extent" convention as `MarkdownParagraph`/`MarkdownSection`'s leaf case. New computed field `text` (mirrors `MarkdownSection.name`/`MarkdownListItem.text`) re-parses and returns the fence token's own `.content` unchanged, trailing `"\n"` included (left as-is since `mdformat` re-normalizes on render anyway). No language/info-string handling or restriction — any (or no) info string after the opening fence matches; `~~~`-style fences are moot since `mdformat.text()` already normalizes them to ```` ``` ```` before this class ever sees the text (verified: `mdformat.text("~~~\n...\n~~~\n")` → ```` ``` ````-fenced), so no separate `markup` assertion is needed. Leaf-only is actively enforced, not just documented: both `get_extent` and `from_text` `assert not cls._get_field_names()`, failing loudly if ever subclassed with declared fields. No `__str__` override — the inherited `MarkdownStr.__str__` already returns `_value` unchanged when there are no declared fields, which is always true here. Implemented 2026-08-11 with `tests/models/md/test_markdown_code_block.py` (17 cases: `get_extent` no-extent/whole-fence/multi-line/stops-before-following-content/info-string/empty-fence/leaf-only-guard cases, `from_text`/`__str__` round-trip cases for plain/info-string/multi-line/empty fences plus rejection/leaf-only-guard cases, and `text` computed-field cases for inner-content-only/info-string-excluded/empty/multi-line-preserved) — registered in `models/md/__init__.py`; full suite green (447 passed), `ruff format --check`/`ruff check`/`vulture` clean, `specmgr docs` regenerated with no drift on re-run — depends on: Task 2.1 — status: done
- [x] Task 110.190: Create `MarkdownBlockQuote` (`markdown_block_quote.py`), `@markdown(type="blockquote_open", tag="blockquote")`, no `@alias` enforcement (quoted content is free-form, not a title). markdown-it already groups every *consecutive* `>` line -- including internal blank `>` continuation lines (a "loose" quote with several paragraphs) and any more deeply nested quote (`> > ...`) -- into one `blockquote_open`/`blockquote_close` pair whose own `.map` already spans the whole thing (two quotes separated by a real blank line are two separate pairs, already exactly "consecutive `>` = one instance"), so `get_extent` needs no stop-condition scan -- `tokens[0].map[1]` directly, same situation as `MarkdownListItem`/`MarkdownCodeBlock`. Unlike `MarkdownListItem` (which always assumes a leading paragraph), a quote's content can start with *any* block type (heading, list, nested quote, ...), so `from_text` validates only `tokens[0]` itself (`type`/`tag`/`nesting == 1`), nothing about what follows. Deliberately **not leaf-only** (unlike `MarkdownCodeBlock`) -- future typed fields (e.g. `emphasis`/`strong` as separate objects) are meant to nest inside it -- but a quote has no separate "own text" line the way a heading/paragraph/list item does, since *every* line carries the `>` marker regardless of that line's own block type. So the composite split differs from `MarkdownSection`/`MarkdownParagraph`: leaf case stores the complete extent verbatim (marker included on every line), same as any other leaf; composite case strips the marker from **every** line of the extent (`_dedent_quote_lines`, not just a leading line), re-`format_text`s the result, and delegates it *whole* to `super().from_text()` -- since the entire extent is body this way, `_value` is set to `""` (nothing left to keep, unlike Section's heading-inline-text or Paragraph's lead-sentence). `__str__`'s composite branch re-applies the marker to every line of `super().__str__()`'s output (`_indent_quote_lines`) rather than reconstructing a single heading/lead-sentence line. New computed field `text` mirrors `MarkdownSection.name`/`MarkdownListItem.text`'s "own source, markers stripped" semantics (nested markdown syntax like `*emphasis*` preserved as-is, not rendered to plain text) but applied line-by-line: leaf dedents `_value`; composite returns `super().__str__()` directly, since that's already marker-free by construction. Confirmed via a manual dedent/reindent round-trip check before implementing that a composite quote containing a nested `MarkdownBlockQuote` field round-trips byte-exact. Implemented 2026-08-11 with `tests/models/md/test_markdown_block_quote.py` (20 cases: `get_extent` no-extent/single-line/multi-line/loose-multi-paragraph/stops-at-real-blank-line/two-blank-separated-quotes-are-separate/nested-deeper-quote-included/heading-and-list-inside-quote cases; leaf `from_text`/`__str__`/`text` round-trip, inline-formatting-preserved, loose-quote round-trip, rejection, and marker-stripping cases; composite `from_text`/`__str__`/`text` field-split, round-trip, dedented-text, nested-quote-field round-trip, and full-document sibling-field cases) — registered in `models/md/__init__.py`; full suite green (467 passed), `ruff format --check`/`ruff check`/`vulture` clean, `specmgr docs` regenerated (85 module files) with no drift on re-run — depends on: Task 2.1 — status: done
- [x] Task 110.200: Exercise `@alias`'s `REGEX` branch end-to-end through a real `MarkdownSection.from_text` call — depends on: Task 1.6 — status: done (2026-08-11 reconciliation: already covered, not newly implemented — `tests/models/md/test_markdown_section.py::TestMarkdownSectionAliasEnforcement::test_regex_alias_accepts_any_non_empty_heading_text` calls `_AnyHeadingLeafSection.from_text` on an `@alias(value=".+", type=AliasType.REGEX)`-decorated `MarkdownSection3` subclass, and `various_models.py`'s `MainDocument` fixture — used throughout ACC-003/ACC-004's round-trip tests — is itself `REGEX`-aliased the same way, as are fixtures added since in `test_markdown_paragraph.py`, `test_markdown_str.py`, `test_uc_example.py`, and `test_markdown_list_item.py`. The task's original "no fixture class declares `AliasType.REGEX` yet" premise had already gone stale by the time this was checked)

#### Phase 120: Recursive engine (`MarkdownStr`/`MarkdownSection`)

- [x] Task 120.100: Implement `markdown_str.py`'s `MarkdownStr.get_extent`/`_unwrap_optional`/`process_field`/`from_text`/`__str__`/`__repr__`/`_get_field_names` — generic (non-heading-aware) leaf/composite slicing and rendering, including `Optional[X]`/`X | None` field support (an absent optional field consumes `0` lines and is left unset rather than raising) — depends on: Task 0.2 — status: done
- [x] Task 120.110: Implement `markdown_section.py`'s `MarkdownSection.get_extent` (heading-level-aware: stops at any sibling/ancestor heading, i.e. level `<= own_level`; nested deeper headings are included) and `from_text` (validates the heading triple against `@markdown`'s `_metadata` and, via `match_alias`, against any declared `@alias`; delegates body population to `MarkdownStr.from_text`) — depends on: Task 2.1, Task 1.3 — status: done. **Amended 2026-08-12**: `get_extent` originally checked heading *level* only, not `@alias` -- see Recent Updates' 2026-08-12 entry for the bug this caused and its fix (`get_extent` now also calls `match_alias`, matching `from_text`'s own check).
- [x] Task 120.120: Implement `MarkdownSection.__str__` (re-emits the section's own heading for a composite section; a leaf section's `_value` already holds its full extent verbatim) and the `name` computed field — depends on: Task 2.2 — status: done
- [x] Task 120.130: Unit tests for Tasks 2.1–2.3 — `test_markdown_str.py` (leaf/composite `from_text`, missing-extent/leftover-text error cases, three `Optional[...]` field cases, `get_extent` line-count contract) and `test_markdown_section.py` (no-extent/end-of-input/nested-deeper/sibling-stops/ancestor-stops `get_extent` cases parametrized across h1–h6, plus `__str__` round-trip and `@alias`-enforcement cases) — depends on: Task 2.3 — status: done

#### Phase 130: Reject raw HTML *(done, rescoped 2026-08-11)*

- [x] Task 130.100: Make `MarkdownStr.from_text`/`MarkdownSection.from_text` reject raw HTML (`html_block`/`html_inline` tokens) anywhere in the tokenized text — depends on: Task 2.1 — status: done. Implemented as a single choke point rather than per-class special-casing: `_markdown.py` gained `parse(text) -> list[Token]` (wraps `md.parse(text)`, then a recursive `_assert_no_raw_html` walk that also descends into every `"inline"` token's `.children`, since `html_inline` only ever nests there) and `_RAW_HTML_TOKEN_TYPES = ("html_block", "html_inline")`. Every `md.parse(text)` call site across `markdown_str.py`/`markdown_section.py`/`markdown_paragraph.py`/`markdown_list_item.py`/`markdown_code_block.py`/`markdown_block_quote.py` (14 sites) now calls `parse(text)` instead — disabling markdown-it's `html_block`/`html_inline` rules outright (the plan's other originally-sketched option) was rejected because that would make raw HTML silently parse as something else (e.g. plain text), not raise, which contradicts "reject". `MarkdownStr.from_text`'s leaf branch also gained an explicit `parse(text)` call it previously lacked entirely (it stored `_value` unchecked), so a leaf class reached directly — not only via a composite parent's `get_extent` — is still guarded.
- [x] Task 130.110: Unit tests for Task 3.1 — depends on: Task 3.1 — status: done. `tests/models/md/test_markdown_html_rejection.py` (12 cases): `_markdown.parse` raising on `html_block`/on `html_inline` nested in a paragraph's or heading's `inline` children, staying unaffected by plain Markdown formatting (`**strong**`/`*emphasis*`) and by HTML-looking text inside a fenced code block; plus end-to-end `MarkdownStr.from_text`/`MarkdownSection.from_text` (leaf) pass/fail cases per ACC-005. **Note (rescoped 2026-08-11):** this phase no longer plans a generic `constraints.py` module with composable `AllowedTags`/`LengthConstraint`/`NoRawHtml` marker classes plus a shared validator — that framework was speculative and dropped; only `@markdown`/`@alias` exist as class-level decorators, and raw-HTML rejection above is the one concrete, decided need. The previously-noted opt-in `RoundTrip()` marker remains dropped too — REQ-004's byte-exact round-trip is already the engine's unconditional default (see Requirements/Scope above), so there is nothing left for such a marker to gate.

#### Phase 140: Frontmatter *(done, 2026-08-11)*

- [x] Task 140.100: Decide whether/how a typed frontmatter model (`id`, `version`, `status`, `created`, `updated`) layers on top of the already-working `python-frontmatter`-based stripping (`frontmatter.loads(text).content`/`.metadata`, proven in `test_uc_example.py`) — depends on: none — status: done. Decided via ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29: a base `MarkdownFrontmatter` (`models/md/frontmatter.py`) with core fields `id`/`type`/`created`/`updated`/`status`/`version` (`type` added beyond the task's original field list, as a mandatory document-type discriminator with no default), subclassed per document type (narrowing `type` to a fixed `Literal[...]`). `AdrFrontmatter` stays independent/unconverted; `models/md/_util.py` owns its own validator helpers rather than depending on `models/adr/v1/_util.py`.
- [x] Task 140.110: Unit tests for Task 4.1 — depends on: Task 4.1 — status: done. `tests/models/md/test_frontmatter.py` (19 cases): base-model field defaults/validation (`type` mandatory/non-blank, `status`/`version` defaults and blank-normalization, `version` major-mismatch/malformed rejection, `created`/`updated` blank-to-`None`), plus a `TestMarkdownFrontmatterSubclassing` suite covering the `Literal`-narrowed `type` discriminator pattern end-to-end.

#### Phase 150: Fixtures + integration

- [x] Task 150.100: Define `tests/models/md/various_models.py` — a small, two-level-nested fixture (`MainDocument` → `CharacteristicInformation`/`RelatedInformation` → h3 leaves) proving the recursive mechanics — depends on: Task 2.3 — status: done
- [x] Task 150.110: Define `tests/models/md/test_uc_example.py`'s model tree (`UseCase`, all `##`/`###` sections of `uc_example.md`, mixed required/`Optional[...]` fields) reproducing the fixture's full nested structure — depends on: Task 5.1 — status: done
- [x] Task 150.120: Integration test: `UseCase.from_text` on `uc_example.md` (frontmatter stripped via `python-frontmatter`), assert every field populated, then assert `str(instance) == body` (byte-exact round-trip) — depends on: Task 5.2 — status: done

#### Phase 160: Docs

- [x] Task 160.100: Module docstrings for every file under `src/biz/dfch/specmgr/models/md/` per `.specmgr/conventions.md` — depends on: Task 5.3 — status: done
- [x] Task 160.110: Run `specmgr docs` to regenerate `docs/api/`/`docs/GENERATED.md` — depends on: Task 6.1 — status: done (`docs/api/biz.dfch.specmgr.models.md.*.md` staged; confirmed no drift on re-run during this reconciliation)

## Progress

### Current Status

**Done, as of 2026-08-11.** Every phase in the Task List (0–6, including
Phase 4/REQ-006's typed frontmatter model, the last item to land) is
complete. The generic engine lives under
`src/biz/dfch/specmgr/models/md/` (`MarkdownStr`/`MarkdownSection` +
`MarkdownSection1`..`6`, `@markdown`/`@alias` identity decorators,
`MarkdownParagraph`/`MarkdownListItem`/`MarkdownCodeBlock`/
`MarkdownBlockQuote` content classes, raw-HTML rejection, and the
`MarkdownFrontmatter` base frontmatter model), proven end-to-end against
both `tests/models/md/various_models.py` (small, hand-built fixture) and
`tests/models/md/test_uc_example.py` (the full `uc_example.md` fixture, all
three heading levels). All work is committed and pushed — `git log`'s most
recent commits for this feature are `8d99dd3` ("feat(models/md): add
MarkdownFrontmatter Pydantic model with validation helpers"), `e243386`
("feat(md): add HTML rejection to the Markdown parser"), and `8aec612`
("chore(doc): align feature and ADR documentation with implementation");
nothing under `src/biz/dfch/specmgr/models/md/`/`tests/models/md/` is
untracked or uncommitted. GitHub issue #5 is **closed**.

Test baseline as of this update:

```
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"
# Ran 498 tests. OK.
```

`ruff format --check` / `ruff check` / `vulture src/ whitelist.py --min-confidence 60` are all clean on every file this feature touched — the
`F841` warning on an unused `tokens` local in
`MarkdownSection.validate_heading_structure`'s mostly-commented-out body,
previously noted here as a pre-existing exception, no longer reproduces.
`specmgr docs`/`specmgr adr-toc` are up to date with no drift.

See "Follow-ups" below for the small number of optional, explicitly
non-blocking items intentionally left open when this feature was closed.

### Blockers

- [ ] None identified at this time.

**Follow-ups:** This feature is closed (status `done`, GitHub issue #5
closed) — the items below are optional, explicitly non-blocking, and were
left open on purpose when the feature was closed. They are not "next steps
required to finish this feature"; pick any of them up as its own future work
(a new `feat-N-slug`, or folded into whichever feature first needs it)
if/when it becomes relevant. Earlier, now-resolved "Next" entries from this
feature's active development are not repeated here — see git history
(`git log -p` on this file) or the Updates log below for that record.

1. `validate_heading_structure` (`MarkdownSection`, `model_validator(mode="after")`)
   and the docstring `Example` under `name` are effectively inert (all
   assertions commented out). Revisit and add real assertions now that
   `str(self)` inside them actually contains the heading again (this
   feature never got around to it, since the equivalent protection is
   already delivered structurally by `MarkdownSection.get_extent`'s own
   stop condition plus `from_text`'s trailing-completeness check — see ADR
   832cd6c1-ef8a-4bfc-990e-a610823f61ae's Consequences).
2. The engine's byte-exact round-trip guarantee (REQ-004) has only been
   exercised against the two fixtures' actual content shapes, not every
   structural combination (e.g. a leaf section with multiple paragraphs,
   an embedded list, or a code block all together). Worth a dedicated test
   with structurally richer leaf body content once a real (non-fixture)
   document type starts adopting this engine.
3. `test_uc_example.py`'s `Assumptions`/`OpenIssues`/`MainSuccessScenario`/
   `Extensions`/`SubVariations` still stay leaf `MarkdownSection2`/`3`s (see
   REQ-007's note) rather than adopting the `items: list[MarkdownListItem]`
   shape from Task 1.6.3. Not required by this feature — that fixture
   proves the generic engine, not the official use-case domain model — but
   worth revisiting if/when `feat-4-use-cases` evaluates adopting this
   engine for its own `uc` schema.
4. `AdrFrontmatter` (`models/adr/v1/frontmatter.py`) was deliberately left
   independent of the new `MarkdownFrontmatter` base (ADR
   bc5e18ad-6bbf-4265-bae4-3e34984a2d29) rather than converted to subclass
   it. A future decision may converge the two once there is appetite to
   touch the ADR pipeline; not scheduled here.

### Updates

#### 2026-08-15T12:00:00.000Z - post-closure addition: new `MarkdownComment` class + `_assert_no_raw_html` inline-comment permission

Requested by `feat-6-requirement-artifact`'s Task 3.20, since both changes
land in this feature's own `models/md/` module (`markdown_comment.py`
new, `_markdown.py` modified) — same "downstream feature triggers a
change in the closed engine" pattern as this file's other post-closure
entries below, this time an addition rather than a bug fix or docstring
trim.

- **New `models/md/markdown_comment.py`**: `MarkdownComment`, a leaf-only
  `MarkdownStr` subclass matching a single self-closing `"html_block"`
  token whose content starts with `<!--` (an HTML comment) — mirrors
  `MarkdownCodeBlock`'s established single-token (`nesting == 0`) leaf
  pattern exactly (`get_extent`/`from_text`/`text`). Lets any
  `MarkdownStr` subclass declare an optional `comment: MarkdownComment | None` field wherever an explanatory comment may precede/follow a real
  value, without that comment breaking the class's own structural field
  matching — the generic `MarkdownStr.from_text` field-distribution loop
  already supports an `Optional[X]` field anywhere in declaration order,
  so no engine change was needed to make the new class usable this way.
  Registered in `models/md/__init__.py`. Class docstring kept short
  (~400 chars) from the start, per the docstring-length lesson from this
  file's own 2026-08-14 entry below (inlined into every schema `$defs`
  entry that references it).
- **`_markdown.py`'s `_assert_no_raw_html`** now also permits an
  `"html_inline"` token whose content starts with `<!--` — previously only
  `"html_block"` had this exception. A shared `_ALLOWED_RAW_HTML_PREFIX = "<!--"` constant backs both checks now. A non-comment inline tag (e.g.
  `<b>bold</b>`) is still rejected exactly as before.
- Both changes are independent of each other: `MarkdownComment` only ever
  matches the already-permitted `"html_block"` shape, so it needed no new
  engine permission; the `"html_inline"` change is a parallel, standalone
  extension. `feat-6-requirement-artifact` used the former to fix
  `req_template.md`'s actual (block-form) parse-validity break; the latter
  was implemented alongside it since it was the literal ask in that
  feature's Task 3.20, and is independently useful (e.g. a future
  same-line inline annotation elsewhere).
- Tests: `tests/models/md/test_markdown_comment.py` (8 new cases,
  mirroring `test_markdown_code_block.py`'s structure) and two new cases
  in `tests/models/md/test_markdown_html_rejection.py` (inline comment
  permitted; non-comment inline tag still rejected). Full project suite
  green (769 tests), `ruff format --check`/`ruff check`/`vulture` clean.

### Decisions Made

#### 2026-08-08T16:00:00.000Z - Superseded the Annotated field-metadata mechanism

Superseded the `Annotated[Heading(tag=, alias=)]` field
metadata mechanism with a `MarkdownHeading1`..`MarkdownHeading6` class
hierarchy + class-level alias + sequential cursor-based recursive-descent
parser (see ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.1.0 for full
rationale) — level is now a type, not metadata; alias is parse-time-only
identity, never used for rendering; heading tokens are stored and replayed
verbatim instead of resynthesized, so inline formatting round-trips.

#### 2026-08-08T15:00:00.000Z - RoundTrip() fidelity is opt-in

`RoundTrip()` fidelity checking is opt-in per field/class,
never a default constraint, since Markdown has many equally valid
renderings of the same semantic content.

#### 2026-08-08T14:30:00.000Z - Kept as a separate feature from feat-3

Kept this generic AST/`markdown-it-py`-based engine as a
separate feature from `feat-3-md-str-constraints`'s regex-based `MdStr`,
rather than superseding it or merging the two — they address different
problem shapes (whole-document structural parsing vs. single-field inline
constraint checking) and neither blocks the other.

### Related PRs / Commits

- [Issue #5](https://github.com/dfch/biz.dfch.SpecMgr/issues/5): Generic heading-mapped Markdown-to-Pydantic document parser

### More Information

(No technical debt identified yet for this feature.)
