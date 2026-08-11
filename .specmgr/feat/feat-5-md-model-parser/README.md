---
id: feat-5-md-model-parser
version: 1.9.0
status: in-progress
created: 2026-08-08
updated: 2026-08-11
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

**Note (2026-08-11 reconciliation):** the list below replaces the original
`Annotated[Heading(...)]`/`parse_document`/`render_document`/`constraints.py`/
`frontmatter.py`-shaped requirements (see prior revisions in `git log -p` on
this file) with what `src/biz/dfch/specmgr/models/md/` and
`tests/models/md/` actually implement, per ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae
v1.1.0's superseding design (class hierarchy + class-level alias + cursor-
based recursive descent, not field-level `Annotated` metadata).

- REQ-001: Define a `@markdown(type=, tag=)` class decorator (`markdown.py`) attaching a `_metadata` dict (markdown-it token `type`/HTML `tag`) to a `MarkdownStr` subclass, and six concrete `MarkdownSection1`..`MarkdownSection6` base classes (`markdown_section1.py`..`markdown_section6.py`) that each pin `tag` to `h1`..`h6` respectively — heading level is expressed as which base class is inherited, not as `Annotated` field metadata. Separately, an opt-in `@alias(value=, type=)` class decorator (`alias.py`, `alias_type.py`'s `AliasType.LITERAL`/`SPACE_SEPARATED`/`REGEX`) attaches `_alias_metadata` used only for identity matching at parse time (`alias_match.match_alias`), never for rendering; a class with no `@alias` at all defaults to `AliasType.SPACE_SEPARATED`'s derivation of its own class name (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0), not "accept any heading text". `LITERAL` matching is exact and case-sensitive (no normalization, no trailing-parenthetical stripping) — a heading like `"Extensions (optional)"` must be declared verbatim, since `SPACE_SEPARATED`'s automatic class-name-derived alias cannot express such suffixes. Field optionality (`X | None`) is driven only by the Python type (`MarkdownStr._unwrap_optional`), never by heading text.
- REQ-002: Define `MarkdownStr` (`markdown_str.py`), a Pydantic base model storing its rendered text verbatim in a private `_value: str` attribute (not parsed `markdown-it-py` tokens retained on the instance), exposing `__str__`/`__repr__` that return `_value` unchanged for a leaf class (no nested `MarkdownStr` fields) or the `mdformat`-normalized concatenation of every nested field's own `__str__()` for a composite class.
- REQ-003: Implement a recursive parser, `MarkdownStr.from_text(text) -> MarkdownStr` (overridden by `MarkdownSection.from_text` for heading-bearing classes), that tokenizes `text` once per recursion step via a shared module-level `MarkdownIt` instance (`_markdown.py`), and recursively slices it into one block per declared nested field (in declaration order) using that field type's own `get_extent(text)` to determine the block boundary, to arbitrary nesting depth. Frontmatter splitting is explicitly **not** this engine's responsibility (see REQ-006) — callers strip it before calling `from_text`.
- REQ-004: Implement the inverse `MarkdownStr.__str__`/`MarkdownSection.__str__`, producing Markdown text from a populated model instance. Because every leaf `_value` retains its complete heading+body extent verbatim (not just inline content), `str(instance)` reproduces the exact `mdformat`-normalized text `from_text` consumed — a byte-exact round-trip by construction, not merely a structural one.
- REQ-005 *(not started)*: Provide composable, `Annotated`-based content constraint markers — `AllowedTags(tags)`, `LengthConstraint(min_length=, max_length=)`, `NoRawHtml()` — evaluated by a shared validator on `MarkdownStr`. No `constraints.py` module or any such marker exists yet; content is currently unconstrained beyond basic Markdown parseability. A separate opt-in `RoundTrip()` marker, as originally scoped, is now moot: REQ-004's byte-exact round-trip is already the engine's unconditional default behavior, not an opt-in feature to gate.
- REQ-006 *(not started, design changed)*: The originally-scoped typed `DocumentFrontMatter` Pydantic base (`id`, `version`, `status`, `created`, `updated`) does not exist. The proven approach instead (`tests/models/md/test_uc_example.py`) delegates frontmatter stripping entirely to the `python-frontmatter` package — already a project dependency, already used the same way by `models.adr.v1.parser` — via `frontmatter.loads(text).content`, since `mdformat.text()` is CommonMark-only and mangles a `---\n...\n---` block. Whether/how a typed frontmatter model gets layered on top of `.metadata` remains open.
- REQ-007: Provide a fixture model reproducing the full nested structure of `tests/feat-5-md-model-parser/uc_example.md` (all three heading levels: `# Buy Goods` → nine `##` sections → all `###` children under `## Characteristic Information`/`## Related Information`), proving the recursive engine end-to-end, including a mix of required and `Optional[...]` fields. Landed as `UseCase`/`CharacteristicInformation`/etc. in `tests/models/md/test_uc_example.py` (distinct from the smaller, earlier `tests/models/md/various_models.py` fixture, which stays as a minimal unit-test double, not a superset of this one). This fixture is a proof of the generic engine, not the official use-case domain model (that ownership stays with `feat-4-use-cases`, if/when it chooses to adopt this engine). `Extensions`/`Sub-Variations`/`Open Issues` are modelled as leaf `MarkdownSection2`s (their dynamically-named, per-use-case h3 sub-headings are inert text) since the engine has no "repeated/list section" concept yet.
- REQ-008: Add unit tests per building block (`@markdown`/`@alias`/`match_alias` behavior, `MarkdownStr.get_extent`/`from_text`/`__str__`, `MarkdownSection.get_extent`/`from_text`/`__str__`, `Optional[...]` field handling) plus an integration test that round-trips `MarkdownSection1.from_text`/`__str__` against both fixtures end-to-end.

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — `MarkdownSection.from_text` rejects a heading whose `(type, tag)` doesn't match the class's own `@markdown` metadata (e.g. a class declaring `h2` fails against an `h3` heading at that position — `test_markdown_section.py`), and, independently, rejects a heading whose text doesn't satisfy a declared `@alias` while a class with no `@alias` matches the `AliasType.SPACE_SEPARATED` derivation of its own class name, not any heading text (`test_alias_match.py`, `TestMarkdownSectionAliasEnforcement`). `LITERAL` matching is exact/case-sensitive by design (not case-insensitive, no parenthetical stripping) — covered by `test_literal_is_case_sensitive_with_no_normalization`.
- [x] ACC-002: Verifies REQ-002 — `MarkdownStr.from_text(text).__str__()` round-trips at least: a single leaf paragraph (`test_leaf_class_stores_value_verbatim`), a multi-field composite document (`test_distributes_lines_across_fields_using_get_extent`), and inline-formatted content (heading text containing `*emphasis*`/`**strong**`, `test_leaf_section_preserves_inline_formatting_in_heading`).
- [x] ACC-003: Verifies REQ-003 — `MarkdownSection1.from_text` on both the `various_models.py` fixture (two levels: `MainDocument` → `CharacteristicInformation`/`RelatedInformation` → h3 leaves) and the full `uc_example.md` fixture (three levels, ~15 h3 fields under `Characteristic Information`) populates every declared field, with a mandatory trailing-completeness assertion (`remaining_text == ""`) that fails loudly on any leftover unclaimed heading (`test_main_document_from_text`, `test_parses_title_and_top_level_sections`, `test_parses_all_characteristic_information_fields`).
- [x] ACC-004: Verifies REQ-004 — `str(MarkdownSection1.from_text(text)) == text` holds exactly (byte-exact, not just structural) for both fixtures (`various_models.py`'s `MainDocument`, `uc_example.md`'s `UseCase` — `test_round_trip_reproduces_the_source_document`).
- [ ] ACC-005 *(blocked — REQ-005 not started)*: No constraint marker exists yet to test; `AllowedTags`/`LengthConstraint`/`NoRawHtml` pass/fail cases remain to be written once `constraints.py` lands. The `RoundTrip()`-inactive-by-default half of the original criterion no longer applies (see REQ-005).
- [ ] ACC-006 *(blocked — REQ-006 not started)*: No `DocumentFrontMatter` model exists yet to reject an invalid frontmatter block; current tests only strip frontmatter via `python-frontmatter` before parsing (`test_uc_example.py::setUpClass`), performing no validation on `.metadata`.
- [x] ACC-007: Verifies REQ-007 — `UseCase.from_text` (`tests/models/md/test_uc_example.py`) successfully parses the entirety of `tests/feat-5-md-model-parser/uc_example.md`'s body (post frontmatter-stripping) without falling back to an untyped/opaque blob for any `##`/`###` section — every field down to `RelatedUseCases`/`Assumptions` is a typed `MarkdownSection3`, not a dict or raw string.
- [x] ACC-008: Verifies REQ-008 — Full suite passes under `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (374 tests as of this reconciliation, all for this feature's modules under `tests/models/md/` passing, none skipped).

### Scope

**Included in this feature:**
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
- `src/biz/dfch/specmgr/models/md/alias_match.py` — `match_alias(cls,
  heading_text)`, enforcing that a parsed heading's actual text satisfies
  the class's declared `@alias` (`LITERAL`/`SPACE_SEPARATED`/`REGEX`), used
  by `MarkdownSection.from_text`; a class with no `@alias` at all always
  matches (opt-in, not mandatory)
- `src/biz/dfch/specmgr/models/md/_markdown.py` — shared module-level
  `MarkdownIt` instance (`md`)
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
  `test_markdown_section.py`, `test_alias_match.py`, `test_uc_example.py`)

**Reconciled with actual implementation (2026-08-11):** the original plan's
`heading.py` (`Annotated[Heading(...)]` metadata), `constraints.py`,
`frontmatter.py`, and `parser.py`/`render_document` never landed under those
names, and are not expected to — the class-hierarchy approach
(`MarkdownSection1`..`6` + `@markdown`/`@alias`) permanently replaced the
annotation-metadata approach originally described in REQ-001/003 (see ADR
832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.1.0). The Requirements/Acceptance
Criteria/Task List sections now describe this actual design; `constraints.py`
(REQ-005) and a typed frontmatter model (REQ-006) remain genuinely
not-started work, not stale documentation.

**Explicitly out of scope:**
- Migrating the existing ADR parser/renderer (`models/adr/v1/parser.py`, `renderer.py`) onto this engine — ADR 4c6119c9 stays as-is
- The regex-based `MdStr`/`MdStrConstraints` single-field string type — owned by `feat-3-md-str-constraints`, a different mechanism for a different problem shape
- Defining the official use-case (`uc`) domain model/schema — owned by `feat-4-use-cases`; this feature only proves the generic engine via a fixture
- Content constraint checking (`AllowedTags`/`LengthConstraint`/`NoRawHtml`) — not yet implemented (REQ-005); note the engine's byte-exact round-trip (REQ-004) is unconditional/always-on by construction, not an opt-in `RoundTrip()` marker as originally scoped
- Any `tools`/`prompts`/`resources` MCP surface for a new document type — this feature is schema/engine only, following the `models/adr/v1` precedent of landing the schema layer before any domain package

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr` structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first hierarchy, shared versioned `models/`), ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae (this feature's own design decision)
- Related, not blocking: `feat-3-md-str-constraints` (separate regex-based string constraint type), `feat-4-use-cases` (may evaluate adopting this engine for its UC schema later; not assumed here)
- External: adds `markdown-it-py` (+ a YAML frontmatter parsing dependency) to the library's **base** dependencies, since parsing is core library behavior, not CLI/MCP-only

### Design Notes

See ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae for the full rationale and
considered alternatives (imperative class decorator; convention-only field
name matching). Key points carried over here for quick reference:

- Recursive slicing algorithm: for a field's token range (from its
  `heading_open` to just before the next `heading_open` of `<=` its own
  level), any child field whose type itself declares `Heading`-annotated
  fields is parsed from that slice at the next heading level down. The full
  slice (heading + all nested content) is retained as the field's own
  `_tokens`, so rendering at any level reproduces that whole subtree.
- Constraint markers are opt-in composables, not required on every field;
  a bare `MarkdownStr` field with no constraint metadata is valid and
  unconstrained beyond basic Markdown parseability.
- Originating sketch and fixture: `tests/feat-5-md-model-parser/req_parser.py`,
  `tests/feat-5-md-model-parser/uc_example.md` (fixture file is reused
  as-is; this feature's own model/tests live under `tests/models/markdown/v1/`).

### Related ADRs

- 832cd6c1-ef8a-4bfc-990e-a610823f61ae: Generic heading-mapped markdown-to-Pydantic parsing with declarative Heading metadata and opt-in constraints
- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-type domain (domain-first hierarchy)
- 4c6119c9-532f-4629-8977-108e78304f48: Parse-validate-render pipeline for ADRs (related, not superseded — this feature does not migrate the ADR pipeline)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

**Note (2026-08-11 reconciliation):** phases/tasks below replace the
original `heading.py`/`constraints.py`/`frontmatter.py`/`parser.py`-shaped
breakdown (superseded design, see Requirements above) with the actual
`models/md/` module layout. Task numbering restarts at Phase 0 but no
history is lost — the original phase text remains recoverable via `git log
-p` on this file.

#### Phase 0: Preparation
- [x] Task 0.1: Create module level md parser instance in `src/biz/dfch/specmgr/models/md/_markdown.py` (shared `MarkdownIt` instance, `md`)
- [x] Task 0.2: Create `class MarkdownStr(BaseModel)` (`markdown_str.py`) — landed as a plain Pydantic `BaseModel` with a private `_value: str` attribute, not a `StrictStr` subclass as originally sketched

#### Phase 1: Metadata/identity decorators
- [x] Task 1.1: Create `markdown.py` — `@markdown(type=, tag=)` class decorator attaching `_metadata` (markdown-it token `type`/HTML `tag`) — depends on: none — status: done
- [x] Task 1.2: Create `alias_type.py` — `AliasType` (`LITERAL`/`SPACE_SEPARATED`/`REGEX`) and `alias.py` — `@alias(value=, type=)` class decorator attaching `_alias_metadata` (opt-in, parse-time identity only, never used for rendering) — depends on: none — status: done
- [x] Task 1.3: Create `alias_match.py` — `space_separated_name(class_name)` and `match_alias(cls, heading_text)`, enforcing a declared `@alias` (or always matching if none declared) — depends on: Task 1.2 — status: done
- [x] Task 1.4: Create `markdown_section1.py`..`markdown_section6.py` — concrete `MarkdownSection` subclasses for h1..h6, each just supplying `@markdown(type="heading_open", tag="hN")` — depends on: Task 2.1 (below) — status: done. h4/h5/h6 additionally needed a bugfix (a live, always-crashing `_tokens`-based assertion left over from before `_value` replaced `_tokens`, see Recent Updates) and dedicated test coverage (`tests/models/md/test_markdown_section_levels.py`), neither of which existed until this reconciliation.
- [x] ~~Task 1.5: Create `metadata_utils.py`~~ — **removed 2026-08-11**: `_metadata` introspection helpers (`get_direct_metadata`, `get_inherited_metadata`, `find_metadata_source`, `get_metadata_chain`, `has_metadata`) were dead code — never called by the core recursion path, never re-exercised by any test, and its own docstring examples referenced a nonexistent `@annotate` decorator (the real one is `@markdown`). Deleted the module, its `docs/api/` page, and its `models/md/__init__.py` re-exports rather than backfilling tests for unused code — depends on: Task 1.1 — status: removed
- [x] Task 1.6: Unit tests for Tasks 1.1–1.5 (`test_alias_match.py`: `space_separated_name` conversion cases, every `match_alias` branch including no-alias-always-matches and `LITERAL`'s case-sensitivity) — depends on: Task 1.3 — status: done
- [x] Task 1.6.1: Support `list[MarkdownStr]` (or `list[SomeMarkdownStrSubclass]`) fields in `markdown_str.py`'s `_get_field_names`/`from_text`/`__str__`. Detection: `_unwrap_list(annotation) -> tuple[type, bool]` (sibling to `_unwrap_optional`, plain `list[X]` only via `typing.get_origin(annotation) is list` — no `Sequence`/`tuple` support), applied after `_unwrap_optional` so `list[X] | None` unwraps to `(X, optional=True, is_list=True)`. Consumption: `process_list_field(name, item_type, text, *, optional=False) -> tuple[str, list[MarkdownStr] | None]` — deliberately **not** mirroring `process_field`'s `(extent, value)` contract (an earlier draft did and was wrong: summing per-item extents against a locally-renormalized string silently loses lines dropped by `mdformat.text()` between items, e.g. a separating blank line, causing `from_text`'s generic `remaining_text.splitlines()[extent:]` slice to misalign against the caller's *original*, not-yet-renormalized `remaining_text` — the exact class of bug `from_text` itself already moved off a line-index `cursor` to avoid). Instead it loops `item_type.get_extent`/slice/`mdformat`-renormalize/`item_type.from_text` while extent `> 0` and returns the already-fully-reduced `remaining_text` string directly, which `from_text` adopts as-is for list fields (bypassing the generic extent-slicing step used for scalar fields). No item found on the *first* iteration is an absence (mandatory `list[X]` -> assertion error, matching today's missing-mandatory-scalar-field behavior; `list[X] | None` -> field left `None`, `text` returned unchanged) while no item found on any *subsequent* iteration just ends the list normally (items 2+ are implicitly optional without needing `Optional[X]` themselves). Rendering: `__str__` iterates the list and appends `str(item)` per element, same as today's single-field append, skipping a `None` list exactly like an absent optional scalar field — depends on: Task 2.1 — status: done
- [x] Task 1.6.2: Support base object `MarkdownParagraph` (`markdown_paragraph.py`) — a single class (`@markdown(type="paragraph_open", tag="p")`, no level spectrum, no `@alias` enforcement — a paragraph's text is free-form content, not a title). Leaf case (no declared fields): `get_extent`/`from_text` claim exactly the paragraph's own line span, nothing more — content that follows (even a sibling paragraph) is left untouched, unlike a leaf `MarkdownSection`'s greedy-to-next-heading behavior. Composite case (has declared `MarkdownStr`/`list[MarkdownStr]` fields): `_value` holds only the paragraph's own inline text; the remainder is delegated to `super().from_text()` (`MarkdownStr.from_text`) for field population, exactly like `MarkdownSection.from_text` delegates its post-heading body — bounded, in `get_extent`, only by the next heading of *any* level (h1-h6), since a paragraph has no level of its own and can never itself contain a heading. `__str__` mirrors `MarkdownSection.__str__` minus the heading-marker reconstruction — depends on: Task 2.1 — status: done
- [ ] Task 1.6.3: Support `MarkdownList` — depends on: TBD — status: not-started
- [ ] Task 1.7: Exercise `@alias`'s `REGEX` branch end-to-end through a real `MarkdownSection.from_text` call (currently only unit-tested in isolation; no fixture class declares `AliasType.REGEX` yet) — depends on: Task 1.6 — status: not-started (low priority; `@alias`'s mechanism may itself be revisited later)

#### Phase 2: Recursive engine (`MarkdownStr`/`MarkdownSection`)
- [x] Task 2.1: Implement `markdown_str.py`'s `MarkdownStr.get_extent`/`_unwrap_optional`/`process_field`/`from_text`/`__str__`/`__repr__`/`_get_field_names` — generic (non-heading-aware) leaf/composite slicing and rendering, including `Optional[X]`/`X | None` field support (an absent optional field consumes `0` lines and is left unset rather than raising) — depends on: Task 0.2 — status: done
- [x] Task 2.2: Implement `markdown_section.py`'s `MarkdownSection.get_extent` (heading-level-aware: stops at any sibling/ancestor heading, i.e. level `<= own_level`; nested deeper headings are included) and `from_text` (validates the heading triple against `@markdown`'s `_metadata` and, via `match_alias`, against any declared `@alias`; delegates body population to `MarkdownStr.from_text`) — depends on: Task 2.1, Task 1.3 — status: done
- [x] Task 2.3: Implement `MarkdownSection.__str__` (re-emits the section's own heading for a composite section; a leaf section's `_value` already holds its full extent verbatim) and the `name` computed field — depends on: Task 2.2 — status: done
- [x] Task 2.4: Unit tests for Tasks 2.1–2.3 — `test_markdown_str.py` (leaf/composite `from_text`, missing-extent/leftover-text error cases, three `Optional[...]` field cases, `get_extent` line-count contract) and `test_markdown_section.py` (no-extent/end-of-input/nested-deeper/sibling-stops/ancestor-stops `get_extent` cases parametrized across h1–h6, plus `__str__` round-trip and `@alias`-enforcement cases) — depends on: Task 2.3 — status: done

#### Phase 3: Content constraints *(not started)*
- [ ] Task 3.1: Create `constraints.py` — `AllowedTags`, `LengthConstraint`, `NoRawHtml` marker classes plus a shared validator on `MarkdownStr` that reads and applies whichever markers are present — depends on: Task 2.1 — status: not-started
- [ ] Task 3.2: Unit tests for Task 3.1 (each constraint's pass/fail case) — depends on: Task 3.1 — status: not-started
- **Note:** the originally-scoped opt-in `RoundTrip()` marker is dropped from this phase — REQ-004's byte-exact round-trip is already the engine's unconditional default (see Requirements/Scope above), so there is nothing left for such a marker to gate.

#### Phase 4: Frontmatter *(not started; design changed)*
- [ ] Task 4.1: Decide whether/how a typed frontmatter model (`id`, `version`, `status`, `created`, `updated`) layers on top of the already-working `python-frontmatter`-based stripping (`frontmatter.loads(text).content`/`.metadata`, proven in `test_uc_example.py`) — depends on: none — status: not-started
- [ ] Task 4.2: Unit tests for Task 4.1, once scoped — depends on: Task 4.1 — status: not-started

#### Phase 5: Fixtures + integration
- [x] Task 5.1: Define `tests/models/md/various_models.py` — a small, two-level-nested fixture (`MainDocument` → `CharacteristicInformation`/`RelatedInformation` → h3 leaves) proving the recursive mechanics — depends on: Task 2.3 — status: done
- [x] Task 5.2: Define `tests/models/md/test_uc_example.py`'s model tree (`UseCase`, all `##`/`###` sections of `uc_example.md`, mixed required/`Optional[...]` fields) reproducing the fixture's full nested structure — depends on: Task 5.1 — status: done
- [x] Task 5.3: Integration test: `UseCase.from_text` on `uc_example.md` (frontmatter stripped via `python-frontmatter`), assert every field populated, then assert `str(instance) == body` (byte-exact round-trip) — depends on: Task 5.2 — status: done

#### Phase 6: Docs
- [x] Task 6.1: Module docstrings for every file under `src/biz/dfch/specmgr/models/md/` per `.specmgr/conventions.md` — depends on: Task 5.3 — status: done
- [x] Task 6.2: Run `specmgr docs` to regenerate `docs/api/`/`docs/GENERATED.md` — depends on: Task 6.1 — status: done (`docs/api/biz.dfch.specmgr.models.md.*.md` staged; confirmed no drift on re-run during this reconciliation)

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-10**: Implementation is underway directly under
`src/biz/dfch/specmgr/models/md/` (superseding the originally-planned
`models/markdown/` path and the `Annotated[Heading(...)]` mechanism — see
Scope above). `MarkdownStr.get_extent`/`from_text`/`process_field` and
`MarkdownSection.get_extent`/`from_text`/`__str__` are all now implemented
and unit-tested, including with real nested-heading content (not just the
fixed-extent test doubles) — see Recent Updates below for the fixes this
required. `MarkdownSection._value` semantics (corrected this session, see
Recent Updates): a **leaf** section (no nested fields) stores its complete
extent verbatim (heading and body), exactly like the base
`MarkdownStr.from_text` leaf case, since nothing else will ever retain that
text. A **composite** section (has nested fields) stores only its own
heading's inline content, since the body is already fully represented,
recursively, by its nested fields (down to whichever leaf(ves) ultimately
hold it in full) — storing the full extent there too would just duplicate
what the children already carry. `MarkdownSection.__str__` mirrors this:
leaf sections defer to `super().__str__()` (returns `_value` verbatim,
already the full extent); composite sections reconstruct
`"#" * level + " " + self._value` from `cls._metadata['tag']` and prepend
it to `super().__str__()`'s children output. Net effect: `str(instance)`
is now a full, byte-exact round-trip of whatever `from_text` consumed, for
both leaf and composite sections — the previous session's "leaf body text
is silently dropped" trade-off is resolved, not just documented. As a side
effect this also fixed `MarkdownSection.name` (a `computed_field` that
re-parses `str(self)` to extract the heading text) for composite sections,
which previously found no heading to extract since `str(self)` didn't
contain one.

`MarkdownSection.from_text` now also enforces `@alias`, via the new
`alias_match.py` module's `match_alias(cls, heading_text)`: previously
`_alias_metadata` (set by `@alias`) was inert class data that nothing ever
checked against the actual parsed heading text. A class with no `@alias` at
all always matches (opt-in, not mandatory) — see Recent Updates for the
`various_models.py` fixture aliases this uncovered as already wrong
(`GoalInContext`'s `"Goats in Coats"`, `CharacteristicInformation`'s
`"characteristic_information"`), now corrected to match the fixture
documents' actual heading text.

**All of `src/biz/dfch/specmgr/models/md/` and `tests/models/md/` are
currently untracked in git** (`git status` shows `??`, not staged) — nothing
here has been committed yet. A new session should run `git status` first to
confirm this is still the case before doing anything else.

Test baseline as of this update:
```
uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"
# Ran 367 tests. OK.
```
`ruff format --check` / `ruff check` are clean on all files touched in this
feature except one **pre-existing, unrelated** warning (`F841` on an unused
`tokens` local in `MarkdownSection.validate_heading_structure`'s
mostly-commented-out body — not introduced by this feature's recent work,
left as-is).

### Blockers

- [ ] None identified at this time.

### Next (exact resumption point for a new session)

1. ~~Revisit Requirements/Acceptance Criteria/Task List below~~ — **done
   2026-08-11**: reconciled to describe the actual
   `MarkdownSection1..6`/`get_extent`/`from_text`/`__str__`/`alias_match`
   implementation (see Recent Updates below); no longer stale.
2. `validate_heading_structure` (`MarkdownSection`, `model_validator(mode="after")`)
   and the docstring `Example` under `name` are effectively inert (all
   assertions commented out); revisit now that `str(self)` inside them
   actually contains the heading again and real assertions have become
   meaningful to add.
3. The current byte-exact round-trip only holds for the `various_models.py`
   fixture's flat leaf content (single paragraph per leaf, no lists/code
   blocks/etc.). Worth a dedicated test with structurally richer leaf body
   content (lists, nested headings inside a "leaf" in the domain-model
   sense, multiple paragraphs) once a real (non-fixture) document type
   starts adopting this engine, per the still-unverified `mdformat`
   reformatting/line-count caveat noted earlier this session.
4. `match_alias`'s `REGEX` branch (`alias_match.py`) is unit-tested in
   isolation (`test_alias_match.py`) but not yet exercised end-to-end
   through `MarkdownSection.from_text`/`various_models.py` — none of the
   fixture classes currently declare `AliasType.REGEX`. Per explicit
   repo-owner direction this session, `@alias`'s whole mechanism may be
   short-lived/superseded later, so this is a minor gap, not a priority.

### Recent Updates

#### 2026-08-11 (continued, part 6)
- Completed: Task 1.6.2 -- `MarkdownParagraph` (`markdown_paragraph.py`), a
  single class (no `MarkdownParagraph1..6` spectrum -- a paragraph has no
  level) pinned to `@markdown(type="paragraph_open", tag="p")`, with no
  `@alias` enforcement of its own text (agreed via clarifying questions this
  session: a paragraph's content is free-form prose, not a title to match
  against a class-name-derived alias, unlike a heading).
  - `get_extent`/`from_text`: leaf case (no declared fields) claims exactly
    the paragraph's own line span (`paragraph_open.map[1]`), nothing more --
    unlike a leaf `MarkdownSection`, which greedily claims everything up to
    the next sibling/ancestor heading since "nothing else will retain that
    text." A leaf `MarkdownParagraph` deliberately does *not* mirror that:
    content following it (even a sibling paragraph) is left untouched.
  - Composite case (has declared `MarkdownStr`/`list[MarkdownStr]` fields):
    `_value` holds only the paragraph's own inline text; the remainder is
    delegated to `super().from_text()` for field population, exactly like
    `MarkdownSection.from_text`'s post-heading body delegation. `get_extent`
    bounds this delegation only by the next heading of *any* level (h1-h6)
    -- not some paragraph-specific level, since a paragraph has none and,
    per repo-owner clarification, can never itself contain a heading. A
    following sibling paragraph does *not* stop it; only a heading does.
    `__str__` mirrors `MarkdownSection.__str__`'s composite branch minus the
    heading-marker (`"#" * level`) reconstruction, since a paragraph has
    none to reconstruct.
  - Design converged via clarifying questions before implementation (leaf
    extent = own block only; no `@alias` check; composite stop condition =
    any heading level, with the child fields' own `get_extent`/`from_text`
    determining the real boundary within that window) -- see this session's
    Q&A for the reasoning `git log -p` doesn't otherwise capture.
  - New tests: `tests/models/md/test_markdown_paragraph.py` (12 cases) --
    `get_extent` (no-extent, leaf-own-span-only including multi-line and
    trailing-sibling-paragraph cases, composite-to-end-of-input,
    composite-not-stopped-by-a-sibling-paragraph, composite-stops-before-any-
    heading-level parametrized h1-h6) and `from_text`/`__str__` (leaf
    round-trip, leaf inline-formatting preservation, leaf rejects
    non-paragraph text, composite splits intro text from its delegated
    field, composite round-trips exactly, composite leaves a following
    heading available for a sibling field in a larger document).
  - Registered in `models/md/__init__.py`'s imports/`__all__`.
  - Full suite: 402 passed, 0 failed (390 -> 402, 12 new). `ruff format
    --check`/`ruff check`/`vulture` clean.
  - Task 1.6.3 (`MarkdownList`) remains not-started.

#### 2026-08-11 (continued, part 5)
- Completed: Task 1.6.1 -- `list[MarkdownStr]`/`list[MarkdownStr] | None` field
  support in `markdown_str.py`, added ad hoc (not part of the original task
  list; repo-owner requested it directly this session):
  - `_unwrap_list(annotation) -> tuple[type, bool]`: new sibling to
    `_unwrap_optional`, recognizing plain `list[X]` only (no
    `Sequence`/`tuple` support by explicit decision).
    `_get_field_names`/`from_text` apply `_unwrap_optional` then
    `_unwrap_list` in that order, so `list[X] | None` resolves to
    `(X, optional=True, is_list=True)` -- the two axes are independent.
  - `process_list_field(name, item_type, text, *, optional=False) ->
    tuple[str, list[MarkdownStr] | None]`: loops `item_type.get_extent`/
    slice/`mdformat`-renormalize/`item_type.from_text` while an item
    matches. A first draft mirrored `process_field`'s `(extent, value)`
    contract (matching the initial design discussion) but this was found to
    be **incorrect**, not just a style choice: summing per-item extents
    computed against a locally-renormalized string silently loses lines
    `mdformat.text()` drops between items (e.g. a separating blank line),
    so a caller-side `remaining_text.splitlines()[extent:]` computed from
    that sum no longer lines up with the caller's actual `remaining_text`
    -- exactly the class of bug `from_text` itself already moved off an
    integer line-index `cursor` to avoid (see 2026-08-10 entry below).
    Fixed by having `process_list_field` return the already-fully-reduced
    `remaining_text` string directly; `from_text`'s per-field loop adopts it
    as-is for list fields, bypassing the generic extent-based slicing step
    used for scalar fields.
  - Semantics: no item found on the list's *first* iteration is an absence
    -- an assertion error for a mandatory `list[X]` field, or `(text,
    None)` (untouched) for `list[X] | None`. No item found on any
    *subsequent* iteration just ends the list normally, i.e. items 2+ are
    implicitly optional without needing `Optional[X]` on `item_type`
    itself.
  - `__str__`: a list field renders every item in declaration order via
    `str(item)`, appended the same way a scalar field's single rendered
    string is today; a `None` list is skipped exactly like an absent
    optional scalar field.
  - Also removed a leftover debug `print(f"_get_field_names: ...")` from
    `_get_field_names` while touching that method (unrelated cleanup, not
    gated behind its own task).
  - New tests in `tests/models/md/test_markdown_str.py`
    (`_MarkerItemField`/`_RequiredListContainer`/
    `_TrailingOptionalListContainer`/`_PresentOptionalListContainer`/
    `_ListThenTrailingContainer` fixtures): mandatory list collects all
    matching items and round-trips, mandatory list with zero items raises,
    optional list absent when remaining text is empty, optional list
    populated when items are found, and a list stopping at the first
    non-matching item so a subsequent scalar field can still consume the
    remainder. `_MarkerItemField` deliberately uses a plain-text marker
    (`"item: "`), not real list syntax (`"- "`) -- joining several
    pre-rendered leaf blocks with a blank line (`MarkdownStr.__str__`'s
    normal behavior) turns a *tight* markdown list back into a *loose* one,
    which would fail a round-trip assertion for a reason unrelated to
    list-field support itself.
  - Full suite: 389 passed, 0 failed (384 -> 389, 5 new).
    `ruff format --check`/`ruff check`/`vulture` clean.
  - Task 1.6.2 (`MarkdownParagraph`) and Task 1.6.3 (`MarkdownList`) remain
    not-started -- their descriptions are still pending from the
    repo-owner, deliberately deferred to a later session per explicit
    instruction this session.

#### 2026-08-11 (continued, part 4)
- Completed: Corrected an error in ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae
  (now v1.4.0) and in `alias_match.py`'s actual code, per explicit
  repo-owner direction: a class declaring no `@alias` at all must default
  to `AliasType.SPACE_SEPARATED`'s derivation of `cls.__name__` (the same
  default `@alias` itself already uses), not a literal match against the
  raw class name -- the part 3 entry below incorrectly documented the
  latter as intended/shipped behavior.
  - `alias_match.py`: `match_alias`'s no-`_alias_metadata` branch now
    returns `heading_text == space_separated_name(cls.__name__)` instead of
    `heading_text == cls.__name__`; updated its docstring accordingly.
    `markdown_section.py`'s `from_text` docstring and `alias_type.py`'s
    stale "`LITERAL`... is the default alias type" docstring line (already
    inconsistent with `alias.py`'s real `SPACE_SEPARATED` decorator
    default, independent of this bug) were also corrected.
  - Removed the now-superfluous explicit annotations that part 3 (wrongly)
    added or kept to satisfy the incorrect literal default:
    `various_models.py`'s `CharacteristicInformation` lost its
    `@alias(value="Characteristic Information", type=AliasType.LITERAL)`;
    `test_markdown_section_levels.py`'s `TopLevel`..`SixthLevel` (six
    classes) lost their `@alias(type=AliasType.SPACE_SEPARATED)`. Both are
    now exactly what the corrected default produces automatically.
  - `various_models.py`'s `RelatedInformation` needed no change -- it was
    already (correctly) left undecorated, but the previous incorrect
    default made it fail to match its `"Related Information"` heading; two
    tests were failing before this fix
    (`test_markdown_section.TestMarkdownSectionStr.test_composite_document_reemits_every_heading_and_body`,
    `test_markdown_str.TestFromText.test_main_document_from_text`) and pass
    after it, with no fixture change.
  - `test_alias_match.py`/`test_markdown_section.py`: renamed and rewrote
    the no-`@alias`-default tests
    (`test_class_with_no_alias_defaults_to_literal_class_name_match` ->
    `..._space_separated_class_name_match`) to assert the corrected
    behavior; `test_alias_match.py` also gained a fixture without a leading
    underscore (`NoAliasMultiWord`) since `space_separated_name` applied to
    an underscore-prefixed name (the previous `_NoAlias`) produces an odd
    `"_ No Alias"` result, irrelevant to what the test demonstrates.
  - Full suite green (see next full-suite run for the exact count);
    `ruff format --check`/`ruff check` clean; `specmgr docs`/`specmgr
    adr-toc` regenerated.
  - REQ-001/ACC-001 above updated to stop claiming "a class with no `@alias`
    at all always matches any heading text", stale since before v1.2.0.

#### 2026-08-11 (continued, part 3)
- Completed: Brought `alias_match.py`/`markdown_section.py` in line with
  ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.2.0/v1.3.1 (previously
  documentation-only revisions -- this entry is the code catching up):
  - `match_alias`: a class with no `@alias` metadata at all now defaults to
    a literal match against `cls.__name__`, instead of unconditionally
    returning `True`. Updated its and `space_separated_name`'s docstrings
    accordingly; updated `MarkdownSection.from_text`'s docstring to stop
    claiming `_alias_metadata` is "otherwise never checked against
    anything."
  - Reconciled every fixture that relied on the old "no alias = accept
    anything" default (ADR v1.2.0's open item (1)): `various_models.py`'s
    `MainDocument` (H1, document-specific title) now declares
    `@alias(value=".+", type=AliasType.REGEX)`; its `RelatedInformation`
    (multi-word class name, space-separated heading) now declares
    `@alias(type=AliasType.SPACE_SEPARATED)`; `test_uc_example.py`'s
    `UseCase` (H1) likewise gained the `.+` regex alias. `Scope`/`Notes`/
    `Assumptions` needed no change -- their single-word class names already
    equal their fixture headings literally, matching the new default by
    coincidence. `test_markdown_section_levels.py`'s `TopLevel`..
    `SixthLevel` (multi-word class names, space-separated headings) all
    gained `@alias(type=AliasType.SPACE_SEPARATED)`.
  - Fixed 4 tests in `tests/models/md/test_markdown_section.py` that called
    `MarkdownSection3.from_text` directly with arbitrary heading text
    (`"Sec3"`, `"Anything Goes"`, `"Leaf H3"`) that no longer matches the
    literal-class-name default: introduced `_AnyHeadingLeafSection`
    (`@alias(value=".+", type=AliasType.REGEX)`) for tests where the
    heading text is incidental to what's actually being tested (extent/
    round-trip mechanics), and rewrote `test_class_with_no_alias_accepts_
    any_heading_text` into two tests demonstrating the new default
    directly: `test_class_with_no_alias_defaults_to_literal_class_name_
    match` (heading equal to class name succeeds) and
    `test_class_with_no_alias_rejects_a_different_heading` (anything else
    fails).
  - `test_alias_match.py`: renamed/split `test_class_with_no_alias_
    metadata_always_matches` into
    `test_class_with_no_alias_defaults_to_literal_class_name_match` and
    `test_class_with_no_alias_rejects_a_different_heading`; added
    `test_regex_alias_accepts_any_non_empty_heading_text` (positive cases
    plus the empty-string rejection, per ADR v1.3.1's `.+` vs `.*` decision).
  - Full suite: 372 passed, 0 failed (368 -> 372: 4 fixed by rewrite/split,
    net 4 new). `ruff format --check`/`ruff check` clean (same pre-existing,
    unrelated `F841`). `specmgr docs` regenerated, no drift beyond the
    docstring content changes above (still 80 modules).

#### 2026-08-11 (continued, part 2)
- Completed: `markdown_section4.py`/`5.py`/`6.py` were also flagged as
  unreferenced (no import anywhere outside their own file, no test
  instantiated them), but unlike `metadata_utils.py` these are real,
  needed pieces of the h1-h6 spectrum, not dead code to remove. Kept them
  and instead:
  - Found, while investigating, that they weren't merely unused but
    actively broken: their `validate_headings` `model_validator` still had
    a *live* `assert self._tokens[0].tag == "h4"` (etc.) — `_tokens`
    (`markdown_section.py`) is declared but never populated by `from_text`
    (only `_value` is), so it's permanently `[]`, and this assertion would
    raise `IndexError` on construction of any `MarkdownSection4`/`5`/`6`
    instance. `markdown_section1.py`/`2.py`/`3.py` already have this same
    dead assertion fully commented out; `4`/`5`/`6` did not. Commented it
    out the same way in all three, matching `1`–`3`.
  - Added `tests/models/md/test_markdown_section_levels.py`: a six-level
    fixture (`TopLevel` h1 down to `SixthLevel` h6, one nested field per
    level) exercised through `TopLevel.from_text`, asserting every level
    down to `SixthLevel` is populated, the h6 leaf retains its full
    extent, `str(instance)` round-trips the source text exactly, and
    `get_extent` agrees across h4/h5/h6. This is the first test coverage
    that reaches h4-h6 at all (previous h1-h3-only fixtures never
    exercised these three classes or the bug above).
  - Full suite: 378 passed, 0 failed (374 -> 378). `specmgr docs` re-run
    clean (same 81 modules, only content diffs). `ruff format --check`/
    `ruff check` clean (same pre-existing, unrelated `F841`).

#### 2026-08-11 (continued)
- Completed: Deleted `src/biz/dfch/specmgr/models/md/metadata_utils.py`
  (`get_direct_metadata`/`get_inherited_metadata`/`find_metadata_source`/
  `get_metadata_chain`/`has_metadata`) after confirming, per repo-owner
  question, that it was unused dead code: no call site anywhere in
  `src/`/`tests/` besides its own definitions, no test file exercised it,
  and its `@annotate`-decorator docstring examples didn't even match the
  real `@markdown` decorator name — a sign it drifted from the rest of the
  module rather than being actively maintained. Removed its
  `models/md/__init__.py` re-exports and its `docs/api/` page, then
  re-ran `specmgr docs` (clean, 81 module files instead of 82) and the
  full suite (374 tests, unchanged — confirming nothing depended on it).
  Updated Scope/Task List above (Task 1.5 struck through as removed rather
  than done).

#### 2026-08-11
- Completed: Reconciled the Requirements/Acceptance Criteria/Task List
  sections above with the actual `src/biz/dfch/specmgr/models/md/`
  implementation (Next item 1 from 2026-08-10), replacing the superseded
  `Annotated[Heading(...)]`/`heading.py`/`parser.py`/`constraints.py`/
  `frontmatter.py`-shaped text with descriptions of the real
  `@markdown`/`@alias`/`alias_match`/`MarkdownStr`/`MarkdownSection1..6`
  design (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.1.0).
  - Investigation ahead of the rewrite surfaced that considerably more had
    already landed than the 2026-08-10 entries below describe, all staged
    (`git add`ed) but never logged here: `metadata_utils.py` (`_metadata`
    introspection helpers), `Optional[X]`/`X | None` field support in
    `MarkdownStr.from_text`/`process_field` (3 new test cases), and —most
    notably — `tests/models/md/test_uc_example.py`, a full second fixture
    model tree (`UseCase` + every `##`/`###` section) that parses the real
    `tests/feat-5-md-model-parser/uc_example.md` end-to-end (frontmatter
    stripped via `python-frontmatter`, matching `models.adr.v1.parser`'s
    convention) and byte-exact round-trips it — i.e. REQ-007/ACC-007 (the
    full-fixture proof) is now satisfied, not still pending. Full suite:
    374 tests passing (up from 367), confirmed via `unittest discover`;
    `specmgr docs` re-run confirms `docs/api/`/`docs/GENERATED.md` have no
    drift (already regenerated and staged).
  - REQ-005 (content constraints: `AllowedTags`/`LengthConstraint`/
    `NoRawHtml`) and REQ-006 (typed `DocumentFrontMatter`) remain genuinely
    not-started, not just undocumented — no `constraints.py`/`frontmatter.py`
    module exists. REQ-005's originally-scoped opt-in `RoundTrip()` marker
    is dropped as moot: the engine's byte-exact round-trip (REQ-004) is
    already unconditional/always-on by construction (every leaf `_value`
    retains its full extent verbatim), so there is nothing left for such a
    marker to gate.
  - Scope, per explicit instruction: this entry touches only the
    Requirements/Acceptance Criteria/Task List/Scope reconciliation and
    logging it here; it does not implement Phase 3/4 (constraints,
    frontmatter typing) or revisit `validate_heading_structure`/`REGEX`
    end-to-end coverage (Next items 2–4 below, left as-is/unstarted).
  - Left untouched at the time, out of scope for this feature and not
    investigated further: `src/biz/dfch/specmgr/models/generic_md_parser.py`
    and `tests/test_generic_md_parser.py` (also staged, `@annotate_structure`/
    `MarkdownModel`-based) — an orphaned module not referenced by this or
    any other feature's README. **Update, same day:** subsequent
    investigation (prompted by a repo-owner question) traced it to a
    committed session transcript (`session-ses_01e6-md-pydantic-parser.md`,
    git-ignored) showing it pre-dated ADR 832cd6c1/this feature entirely — a
    prior, independent prototype an earlier session found already
    uncommitted in the working tree and was explicitly told to leave alone
    ("Leave it, ADR/plan stand as target design"). Confirmed it had zero
    production callers (only its own two test files: `tests/test_generic_md_parser.py`,
    `tests/feat-3-md-str-constraints/test_modelvalidator.py`), so, per
    repo-owner decision, it and both consumer test files (plus
    `GENERIC_MD_PARSER.md` and its `docs/api/` page) were deleted outright
    rather than integrated or further investigated. `tests/feat-3-md-str-constraints/`'s
    remaining, unrelated spike files (`test_token_tree_sample_markdown1.py`,
    `test_uc_example_tokens.py`, fixtures) and `.specmgr/feat/feat-3-md-str-constraints/`
    itself were explicitly left in place, not part of this deletion. Suite:
    380 -> 370 tests (10 removed, all belonging to the deleted files); `specmgr
    docs` re-run clean (80 modules, down from 81).
- Next: unchanged — see Next items 2–4 above (item 1 is now struck through
  as done; items 2–4 were not investigated or touched this session, so
  item 3's premise may itself now be partly stale given `uc_example.md`'s
  richer content — left for a future session to re-check, not assumed
  either way here).

#### 2026-08-10
- Completed (this session): Implemented and unit-tested the core recursive
  extraction mechanics under `src/biz/dfch/specmgr/models/md/`:
  - `MarkdownStr.get_extent(text) -> int`: generic fallback extent
    calculation (max `token.map[1]` across all tokens with a map); returns a
    **line count** (not a 0-based index) so `0` unambiguously means "no
    extent" and `text.splitlines()[:get_extent(text)]` is the idiomatic
    slice — deliberately chosen over a last-line-index return to avoid an
    index/no-extent collision at line 0.
  - `MarkdownSection.get_extent(text) -> int`: heading-level-aware override.
    A level-N section's extent spans its own heading through any nested
    *deeper* heading, stopping at (excluding) the next heading whose level
    is `<= N` (sibling or ancestor) — confirmed correct for h1..h6 via
    parametrized `subTest` cases in `test_markdown_section.py`. Returns `0`
    if the text's first token isn't this class's own heading.
  - `MarkdownStr.process_field(name, type_, text) -> tuple[int, MarkdownStr]`:
    encapsulates one field's extent lookup + `mdformat`-normalized slicing +
    recursive `from_text` construction, extracted out of `from_text`'s loop
    body for testability/overridability. Fixed a `SyntaxError`
    (`type_: type of MarkdownStr` → `type_: type[MarkdownStr]`) introduced
    while drafting this.
  - `MarkdownStr.from_text(text) -> MarkdownStr`: replaced the hardcoded
    `field_type.from_text("abc")` placeholder with real cursor-based
    line distribution across declared fields (in declaration order), each
    field's share determined by `process_field`. Added a trailing assertion
    that the whole loop consumed every line (`cursor == len(lines)`), so
    leftover/unclaimed text after the last field fails loudly instead of
    being silently dropped.
  - Fixed a real, `mdformat`-precondition-driven bug surfaced by the above:
    `process_field`'s line-rejoin (`"\n".join(lines[:extent])`) drops the
    trailing newline that `from_text`'s `text == mdformat.text(text)`
    precondition requires; fixed by normalizing via `mdformat.text(...)`
    before the recursive `from_text` call.
  - `various_models.py` cleanup (done by repo owner mid-session): removed
    redundant/incorrect `@markdown(...)` redecoration on classes that
    already inherit correct `_metadata` from their `MarkdownSection1/2/3`
    base (the redecoration was overwriting, not merging, `_metadata`,
    silently breaking tag validation for `CharacteristicInformation`
    et al.); kept `@alias` where still needed.
  - New tests: `tests/models/md/test_markdown_section.py` (7 cases: no-extent,
    end-of-input fallback, nested-deeper-heading inclusion, sibling-stops,
    ancestor-stops, plus parametrized h1/h2/h3-stop and h4/h5/h6-don't-stop);
    `tests/models/md/test_markdown_str.py` expanded with `get_extent`
    line-count-contract tests and `from_text`/`process_field` tests using
    fixed-extent test doubles (`_FixedExtentField`/`_TwoLineField`/
    `_OneLineField`) to isolate the cursor/distribution logic from real
    markdown-heading parsing.
- Next (superseded by the entry below — kept for history): fix
  `MarkdownSection.from_text` (delegate to `MarkdownStr.from_text` after
  heading-triple validation), then rewrite `test_main_document_from_text`
  against realistic multi-heading input.

#### 2026-08-10 (continued)
- Completed: Fixed the two items from the "Next" list above, plus a bug
  discovered while prototyping the first fix:
  - `MarkdownStr.from_text`: the not-yet-consumed remainder was tracked as
    an integer `cursor` into the *original* `text.splitlines()`, and the raw
    (un-normalized) substring `"\n".join(lines[cursor:])` was passed straight
    into `process_field`/`get_extent`. A raw substring of an
    already-`mdformat`-compliant document is not itself guaranteed to be
    `mdformat`-compliant (e.g. it can start with a blank line `mdformat`
    would strip), which broke `get_extent`'s precondition assertion as soon
    as real nested-heading content (not the fixed-extent test doubles) was
    exercised — this was exactly the "known caveat" flagged in the previous
    entry, confirmed as a real blocker, not a hypothetical one. Fixed by
    replacing `cursor` with a `remaining_text` **string** that is
    re-normalized via `mdformat.text(...)` after every field consumes its
    `extent` lines, so it is always `mdformat`-compliant by construction
    before the next field's `get_extent` call. The trailing completeness
    check changed from `cursor == len(lines)` to `remaining_text == ""`.
  - `MarkdownSection.from_text`: replaced the
    `field_type.from_text("TODO : text from 4th token")` placeholder.
    Resolved the previously-open design question (whether child fields
    should only see the body after the heading) as **yes**: after
    validating the heading triple against `cls._metadata`, the heading's own
    line span (`tokens[0].map[1]`) is stripped off, the remainder is
    `mdformat`-normalized, and delegated to `super().from_text(body)` (i.e.
    `MarkdownStr.from_text`, resolved via cooperative `super()` with `cls`
    still bound to the concrete subclass) for the actual recursive field
    population. Renamed the parameter `v` -> `text` for consistency with
    `MarkdownStr.from_text`.
  - Per explicit repo-owner request, `_value` is now set to the heading's
    **inline content** (`tokens[1].content.strip()`, i.e. the raw markdown
    source between the heading markers) rather than the section's full raw
    text, for both the leaf and composite branches — this is what will let
    a future `__str__` override re-emit `"## " + self._value` instead of
    re-deriving the heading from nested fields. Verified empirically that
    `.content` preserves inline formatting markup verbatim (e.g.
    `"This is a *heading* with **strong** formatting"` round-trips through
    `_value` unchanged, since markdown-it's `inline` token keeps the raw
    source in `.content` and only its `.children` holds the structurally
    parsed form) — added a regression assertion for this
    (`### *Goal* In Context`) in the rewritten test below. Note this is a
    deliberate trade-off for leaf sections: any body text after a leaf
    section's heading is no longer retained anywhere by `from_text` (full
    round-trip fidelity stays opt-in/out of scope per this feature's Scope
    section).
  - Rewrote `tests/models/md/test_markdown_str.py::test_main_document_from_text`
    to use a realistic, `mdformat`-compliant, two-level-nested document
    (`MainDocument` h1 -> `CharacteristicInformation`/`RelatedInformation`
    h2 -> their h3 leaf children) instead of the stale hardcoded
    `"abc"`/single-line-input assertions, checking each `_value` against the
    section's actual heading title.
  - Moved `various_models.py` from
    `src/biz/dfch/specmgr/models/md/various_models.py` to
    `tests/models/md/various_models.py` (repo-owner request): it is a
    test-only fixture model tree, not production code. Updated its internal
    imports to absolute (`biz.dfch.specmgr.models.md....`) since it no
    longer lives inside that package, and updated
    `test_markdown_str.py`'s import to a relative `from .various_models
    import ...`.
  - Full suite: 349 passed, 0 failed (previously 349 passed, 1 known
    failure). `ruff format --check`/`ruff check` clean on every file touched
    this entry.
- Next (superseded by the entry below — kept for history): fix
  `MarkdownSection`/`MarkdownStr` rendering (`__str__`) so a composite
  section re-emits its own heading, not just its children's text.

#### 2026-08-10 (continued, part 2)
- Completed: Added `MarkdownSection.__str__`, overriding
  `MarkdownStr.__str__`. Derives the heading level from `cls._metadata['tag']`
  (`_HEADING_TAGS.index(tag) + 1`), reconstructs `"#" * level + " " +
  self._value`, and — only if the section declares nested fields — appends
  `super().__str__()` (the children's already-`mdformat`-normalized
  concatenation) after a blank line, then re-normalizes the whole thing with
  `mdformat.text(...)`. A leaf section (no nested fields) renders just its
  reconstructed heading line, per the trade-off already made in
  `from_text` (see previous entry) — deliberately not attempting to recover
  body text that `from_text` never retained.
  - Confirmed as a side effect that `MarkdownSection.name` (the
    `computed_field` that re-parses `str(self)` looking for a heading) now
    also works correctly for composite sections — it previously found no
    heading in `str(self)` and effectively couldn't have worked, though no
    test exercised it before now.
  - New tests: `tests/models/md/test_markdown_section.py::TestMarkdownSectionStr`
    (3 cases) — a leaf section re-emits its own heading; inline formatting
    markup inside a leaf heading (`*Emphasized*`) round-trips through
    `__str__` verbatim; a full `MainDocument` fixture's `str()` reproduces
    every descendant heading (h1 through both h2/h3 branches), not just the
    leaf headings `MarkdownStr.__str__` alone would have produced.
  - Full suite: 352 passed, 0 failed (349 -> 352 with the new tests).
    `ruff format --check`/`ruff check` clean on every file touched this
    entry (same pre-existing, unrelated `F841` as before).
- Next (superseded by the entry below — kept for history): reconcile
  Requirements/Acceptance Criteria/Task List with the actual
  implementation, and decide whether leaf sections need a second field to
  retain body content.

#### 2026-08-10 (continued, part 3)
- Completed: Corrected a design error in the previous two entries, caught
  by the repo owner: `MarkdownSection._value` was being set to the
  heading's inline content for **every** section, leaf and composite alike
  — which meant a leaf section's body text (there being no nested field to
  hold it) was silently and permanently dropped by `from_text`, something
  the previous entries flagged as a "deliberate trade-off" rather than
  recognizing as a straightforward bug. Fixed:
  - `MarkdownSection.from_text`: the leaf branch (`not field_names`) now
    sets `instance._value = text` — the complete extent `from_text`
    received, heading and body verbatim — exactly like the base
    `MarkdownStr.from_text` leaf case. The composite branch is unchanged
    (still stores only the heading's inline content), since a composite
    section's body is already fully represented, recursively, by its
    nested fields all the way down to whichever leaf(ves) ultimately hold
    it in full; storing the full extent on the composite too would just
    duplicate what its children already carry.
  - `MarkdownSection.__str__`: the leaf branch now defers to
    `super().__str__()` (`MarkdownStr.__str__`'s leaf case, which returns
    `_value` unchanged) instead of reconstructing `"#" * level + " " +
    self._value` — since `_value` already *is* the full rendered section
    now, reconstructing the heading on top of it would have doubled it up.
    The composite branch is unchanged.
  - Net effect: `str(instance)` is now a full, byte-exact round-trip of
    whatever `from_text` consumed, verified end-to-end against the
    `various_models.py` fixture (`str(MainDocument.from_text(text)) ==
    text`, exactly). This resolves the "leaf body text is silently
    dropped"/"round-trip fidelity" caveat from the previous two entries —
    it was a bug in this session's own work, not an inherent, pre-existing
    limitation of the engine.
  - Updated the 4 now-incorrect assertions this design error had baked
    into: `test_main_document_from_text`
    (`tests/models/md/test_markdown_str.py`) now checks each leaf field's
    `_value` against its full heading+body text and adds a
    `str(doc) == text` round-trip assertion; the 3
    `TestMarkdownSectionStr` cases (`tests/models/md/test_markdown_section.py`)
    now assert full-extent round-trips instead of heading-only output
    (renamed accordingly:
    `test_leaf_section_reemits_its_complete_extent_verbatim`,
    `test_composite_document_reemits_every_heading_and_body`).
  - Full suite: 352 passed, 0 failed (same count as before — this was a
    correction, not new coverage). `ruff format --check`/`ruff check`
    clean on every file touched this entry (same pre-existing, unrelated
    `F841` as before).
- Next (superseded by the entry below — kept for history): reconcile
  Requirements/Acceptance Criteria/Task List with the actual
  implementation; the leaf-body-text question from previous entries is now
  resolved and removed from "Next".

#### 2026-08-10 (continued, part 4)
- Completed: Per repo-owner request, `MarkdownSection.from_text` now
  honours `@alias` (previously `_alias_metadata`, set by `@alias`, was
  inert class data — nothing ever checked it against the actual parsed
  heading text):
  - Added `src/biz/dfch/specmgr/models/md/alias_match.py`: `match_alias(cls,
    heading_text) -> bool`, encapsulating the three `AliasType` comparisons
    (`LITERAL`: exact string equality, case-sensitive, no normalization,
    per explicit repo-owner direction — "LITERAL means LITERAL";
    `SPACE_SEPARATED`: equality against `space_separated_name(cls.__name__)`,
    a new PascalCase -> title-case-with-spaces helper; `REGEX`: `re.
    fullmatch` against the declared pattern), plus the policy that a class
    with **no** `@alias` metadata at all always matches — `@alias` is
    opt-in per class, not mandatory on every `MarkdownSection` subclass.
  - Wired it into `MarkdownSection.from_text`: right after the existing
    `@markdown` type/tag heading-triple validation (as requested, so the
    two checks read as one contiguous block), asserts `match_alias(cls,
    heading_text)` before branching on leaf vs. composite. Moved the
    `heading_text = t_mid.content.strip()` computation earlier so it is
    available to this assertion in both branches (previously only computed
    in the composite branch).
  - This immediately surfaced two already-wrong `@alias` values in
    `tests/models/md/various_models.py` that had never been checked against
    anything: `GoalInContext`'s `@alias(value="Goats in Coats", ...)` and
    `CharacteristicInformation`'s `@alias(value="characteristic_information",
    ...)`, neither of which matched the fixture documents' actual heading
    text used throughout `test_markdown_str.py`/`test_markdown_section.py`
    (`"*Goal* In Context"` and `"Characteristic Information"` respectively).
    Corrected both literal values to match (per repo-owner direction:
    "fix the alias, but make new tests that verify it is working").
    `Scope`/`Notes`/`Assumptions`/`RelatedInformation`/`MainDocument` declare
    no `@alias` at all and were therefore unaffected (nothing to honour).
  - New tests: `tests/models/md/test_alias_match.py` (11 cases) — unit tests
    for `space_separated_name` and every `match_alias` branch (no-alias
    always matches; `LITERAL` match/mismatch/case-sensitivity/no-trailing-
    parenthetical-stripping; `SPACE_SEPARATED` match/mismatch; `REGEX`
    match/mismatch). `tests/models/md/test_markdown_section.py::
    TestMarkdownSectionAliasEnforcement` (4 cases) — `from_text` accepts a
    heading matching a declared `@alias`, rejects one that doesn't, accepts
    any heading text for a class with no `@alias`, and (end-to-end) rejects
    a `MainDocument` fixture document whose `CharacteristicInformation`
    heading doesn't match its `@alias`.
  - Full suite: 367 passed, 0 failed (352 -> 367 with the 15 new tests).
    `ruff format --check`/`ruff check` clean on every file touched this
    entry (same pre-existing, unrelated `F841` as before).
- Next: see "Next" above — reconcile Requirements/Acceptance
  Criteria/Task List with the actual implementation (now including
  `alias_match.py`); the leaf-body-text question is resolved; `@alias`'s
  `REGEX` branch is unit-tested but not yet exercised end-to-end through
  the fixture (added as a new, low-priority "Next" item).
- Notes: This session's work happened interactively/incrementally (small
  scoped diffs, test-driven at each step) rather than against a pre-written
  task list — the Task List below has drifted from what's actually
  implemented and needs reconciliation (see "Next" item 1).

#### 2026-08-08 (even later)
- Completed: Added a committed, standalone spike-test suite under
  `tests/feat-5-md-model-parser/` proving out several of the design
  primitives from `req_parser.py`'s continuation notes and the PARSING
  STRATEGY, ahead of any real Phase 1 implementation:
  - `test_field_declaration_order.py` — pins down (as a committed test
    rather than an ad hoc chat check) that `pydantic.BaseModel.model_fields`
    preserves field declaration order, including fields inherited from a
    base class.
  - `test_parse_heading.py` / `test_annotations.py` — a `get_section(token,
    tokens)` helper (plus its `walk_token_tree` depth-first token-tree
    walker building block) that slices a heading's own span out of a flat
    `markdown-it-py` token list. Iterated twice: first only stopped at an
    exact `(type, tag)` match; then fixed, per explicit request, so any
    same-or-shallower heading level terminates the span (an `h1` now
    correctly terminates a preceding `h2`'s section, not just another
    `h2`) — this directly matches the PARSING STRATEGY's step 2b span
    definition ("everything up to the next same-or-shallower-level
    heading").
  - `test_walk_attributes.py` — a `walk_attributes(cls)` generalization of
    the declaration-order guarantee to any plain class (not just
    `pydantic.BaseModel`): walks `cls.__mro__` base-to-derived and merges
    each class's own (non-inherited) `__annotations__`, correctly keeping a
    redeclared attribute at its original position rather than moving it to
    the end. Written because `cls.__annotations__` via attribute lookup, in
    Python ≥3.10, no longer transparently falls back to a base class's
    annotations dict when a subclass declares none of its own — each class
    now gets its own (possibly empty) dict, so a naive walker would
    silently lose inherited attributes without this MRO-merging approach.
  - All 18 tests pass; `ruff format`/`ruff check` clean.
- Next: unchanged from the entry below — formalize `alias` as a real class
  attribute, implement class-name-derived default alias, write
  `parse_document`/`render_document`, generalize `Document`'s remaining
  fields, decide `DocumentFrontMatter`'s typed shape, then start Phase 1 in
  earnest (after revising its task list, which still reflects the
  superseded `Heading`-annotation mechanism).
- Notes: None of this spike work touches `feat-3-md-str-constraints` or
  `feat-4-use-cases`.

#### 2026-08-08 (later)
- Completed: Revised the design (and ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae,
  now v1.1.0) after further review of `req_parser.py`: replaced the
  `Annotated[Heading(tag=, alias=)]` field-metadata mechanism with a
  `MarkdownHeading1`..`MarkdownHeading6` base-class hierarchy (level encoded
  structurally, each with a default "no same-or-higher-level heading nested
  beneath me" validator) plus a class-level `alias` for identity matching
  only; every heading-bearing instance now stores its own heading token
  triple verbatim (no more render-time heading resynthesis from metadata),
  so inline formatting inside a heading round-trips for free; settled on a
  sequential cursor-based recursive-descent parsing algorithm (fields walked
  in declaration order, matched by `(tag, alias)`, with a mandatory trailing
  completeness check per nesting level to catch out-of-order/unrecognized
  sections). Applied the resulting fixes to `req_parser.py` and added a
  continuation-notes block at the top of that file for session handoff.
- Next: Formalize the `alias` mechanism as a real class attribute (not a
  comment placeholder); implement class-name-derived default alias; write
  the actual `parse_document`/`render_document` functions; generalize
  `Document`'s remaining fields (`main_success_scenario`, `extensions`,
  `sub_variants`, `open_issues`, `related_information`) to dedicated
  `MarkdownHeading2` subclasses; add `CharacteristicInformation`'s nested h3
  fields; decide `DocumentFrontMatter`'s typed shape; then begin Phase 1
  tasks below in earnest (the task list still reflects the superseded
  `Heading`-annotation mechanism and needs a pass before work starts).
- Notes: This feature intentionally does not touch `feat-3-md-str-constraints`
  or `feat-4-use-cases` content. See `tests/feat-5-md-model-parser/req_parser.py`'s
  top-of-file notes block for the fullest up-to-date design detail.

#### 2026-08-08
- Completed: Examined `tests/feat-5-md-model-parser/req_parser.py` and
  `uc_example.md`; clarified design (declarative `Heading` metadata, opt-in
  constraints, recursive nesting, typed frontmatter) via Q&A; wrote ADR
  832cd6c1-ef8a-4bfc-990e-a610823f61ae; discovered and resolved a conflict
  with the pre-existing (uncommitted) regex-based plan in
  `feat-3-md-str-constraints/README.md` by keeping the two as separate,
  non-blocking features; created this feature folder.
- Next: Begin Phase 1 (core primitives).
- Notes: This feature intentionally does not touch `feat-3-md-str-constraints`
  or `feat-4-use-cases` content.

### Decisions Made

- **[2026-08-08]**: Kept this generic AST/`markdown-it-py`-based engine as a
  separate feature from `feat-3-md-str-constraints`'s regex-based `MdStr`,
  rather than superseding it or merging the two — they address different
  problem shapes (whole-document structural parsing vs. single-field inline
  constraint checking) and neither blocks the other.
- **[2026-08-08]**: `RoundTrip()` fidelity checking is opt-in per field/class,
  never a default constraint, since Markdown has many equally valid
  renderings of the same semantic content.
- **[2026-08-08]**: Superseded the `Annotated[Heading(tag=, alias=)]` field
  metadata mechanism with a `MarkdownHeading1`..`MarkdownHeading6` class
  hierarchy + class-level alias + sequential cursor-based recursive-descent
  parser (see ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.1.0 for full
  rationale) — level is now a type, not metadata; alias is parse-time-only
  identity, never used for rendering; heading tokens are stored and replayed
  verbatim instead of resynthesized, so inline formatting round-trips.

### Related PRs / Commits

- [Issue #5](https://github.com/dfch/biz.dfch.SpecMgr/issues/5): Generic heading-mapped Markdown-to-Pydantic document parser

## Technical Debt

(No technical debt identified yet for this feature.)
