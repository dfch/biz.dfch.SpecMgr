# History: Create Use Cases with tool support

#### 2026-08-16 Task 3.1 closed out; its Task 2.4 dependency corrected

- **Task 3.1 marked COMPLETED**, with its dependency corrected: it previously
  listed `depends on: Task 2.4` (Phase 2 diagram generation), but that was a
  planning-time error — defining/implementing the MCP tool/resource/prompt
  surface has no actual dependency on diagram generation being finished
  first. Changed to `depends on: none`. No standalone specification document
  was ever written (as already noted, mirroring `parse_uc`'s own precedent);
  the task's real scope was instead fulfilled directly via Task
  3.1.1-3.1.7 (schema/example/template/list resources, full CRUD+validate
  tool set, `parse_uc`'s path-based shape confirmed, class-hierarchy
  docstrings). Phase 2 (Task 2.2-2.4) remains not-started and unrelated to
  this change. Documentation-only edit — no code/test changes.

#### 2026-08-16 Task 3.1.7 completed: docstrings on the UseCase class hierarchy

- **Task 3.1.7 COMPLETED**: Added a brief, purpose-focused docstring to every
  one of the ~25 classes in `uc/models/v2/use_case.py` (`GoalInContext`,
  `Scope`, `Level`, `Preconditions`, `SuccessEndCondition`,
  `FailedEndCondition`, `PrimaryActor`, `SecondaryActors`, `Trigger`,
  `Frequency`, `Priority`, `PerformanceTarget`, `ChannelsToPrimaryActor`,
  `ChannelsToSecondaryActors`, `RelatedUseCases`, `CharacteristicInformation`,
  `MainSuccessScenario`, `ExtensionItem`, `Extension`, `Extensions`,
  `SubVariation`, `SubVariations`, `OpenIssues`, `Notes`, `Assumptions`,
  `RelatedInformation`, `UseCase`) — the file previously had none. Each
  docstring is two sentences: what the section means/is for in a use case,
  then its shape (free-form prose vs. bullet list vs. ordered list vs.
  composed-of-sub-sections) — deliberately no reference to task numbers or
  implementation history, per the task's own instruction. `document.py`
  (`UcDocument`), `frontmatter.py` (`UcFrontmatter`), and `summary.py`
  (`UcSummary`) were reviewed too but already carried purpose-focused
  docstrings and needed no changes.
- Documentation-only change (no field/behavior changes): `ruff format`/
  `ruff check`/`vulture` clean, all 856 tests still passing.

#### 2026-08-16 Tasks 3.1.1-3.1.6 completed: full uc MCP tool/resource surface

- **Tasks 3.1.1-3.1.6 COMPLETED**, mirroring `req/`'s existing MCP surface
  file-by-file (see Task List entries for the per-task breakdown):
  - **Resources** (`uc/resources/`, new package): `uc_schema`
    (`specmgr://uc/schema`, code-generated via a new `generate_uc_schema()` in
    `commands/schema.py` from `UcDocument.model_json_schema()`, packaged at
    `uc/data/uc_schema.json`), `uc_example` (`specmgr://uc/example`, packaged
    `uc/data/uc_example.md` — a verbatim copy of this feature's own
    `v2/uc_reference.md`), `uc_template` (`specmgr://uc/template`, a newly
    authored `uc/data/uc_template.md`), `uc_list` (`specmgr://uc/list`, backed
    by a new `UcSummary` model, `uc/models/v2/summary.py`).
  - **Tools** (`uc/tools/`): `get_uc_example`, `get_uc_template`, `get_uc`,
    `create_uc`, `update_uc`, `delete_uc` (stub), `set_status_uc`,
    `validate_uc` — all built on a new id-based storage layer
    (`uc/tools/_paths.py`/`_io.py`/`_lock.py`/`_write.py`), reusing the
    already-generic `general.tools._doc_paths` the same way `req/tools/_paths.py`
    does. `parse_uc` stays path-based, unchanged (Task 3.1.6 — confirmed this
    matches `parse_req`'s own shape; `get_req`/`get_uc` are the id-based ones,
    not `parse_req`/`parse_uc`).
  - **Infra**: `pyproject.toml` package-data entry for `biz.dfch.specmgr.uc`;
    `.pre-commit-config.yaml`/CI updated with a `specmgr-schema-uc-package`
    hook/step mirroring req's, and the shared `specmgr-schema` hook's file
    glob widened to include `uc/models/v2`.
  - Deliberately **not** done: no `uc/prompts/` package (Task 3.3 stays
    genuinely open), no `uc/models/v3` (stayed entirely within `uc/models/v2`
    — only additive `summary.py`/`_util.py`), `parse_uc`'s signature untouched.
- 856 tests total (up from prior count), `ruff format`/`ruff check`/`vulture`
  clean, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` all regenerated
  and clean.

#### 2026-08-13 `parse_uc` MCP tool signature changed: text → path parameter

- **`parse_uc` MCP tool signature changed** (`uc/tools/parse_uc.py`): the
  `@mcp.tool()` wrapper now accepts a file path (`path: str`) instead of raw
  markdown text (`text: str`), and reads the file from disk before parsing.
  Breaking change — not a storage-layer addition (no id-based UC file storage
  exists yet), just a convenience shift from "parse text you pass directly" to
  "parse text read from a file you reference". File-access errors propagate
  naturally as `FileNotFoundError`/`PermissionError`/`OSError`, mirroring the
  existing "let parse/validation failures propagate uncaught" convention from
  `adr/tools/` — no wrapping or custom error types introduced.
- **Model-layer `parse_uc` unchanged** (`uc/models/v2/parser.py`): the free
  function `parse_uc(text: str) -> UcDocument` stays as-is — it's still the
  file-existence-agnostic entry point used by model tests and non-MCP code.
  Only the thin `@mcp.tool()` wrapper in `uc/tools/parse_uc.py` changed.
- **Tests fully rewritten** (`tests/uc/tools/test_parse_uc.py`): each test now
  writes its test document to a `tempfile.TemporaryDirectory`, passes the path
  string to `parse_uc`, and verifies the result. Added a new case:
  nonexistent path → `FileNotFoundError`. Same three validation scenarios
  (valid document, invalid frontmatter, malformed structure) covered, now
  through file-based input. 4 tests → 4 tests (no net addition), all passing.
- **Module and tool docstrings updated** to reflect path-based operation, with
  explicit callout on file-access error propagation.
- 555 tests total (554 prior + 1 new FileNotFoundError case), all passing.
  `ruff format`/`ruff check`/`vulture` clean, `specmgr docs` regenerated.

#### 2026-08-12 Task 1.7 completed; Task 1.5 fully closed

- **Task 1.7 COMPLETED**: Resolved the two open decisions its own task text
  had flagged (promote-vs-duplicate the JSON Schema; what to do about
  `v1/uc-schema.md`):
  - **Duplicated, not promoted**: `v2/uc_reference_mdformat_schema.json`
    (scoped to, and named after, one specific worked example) is left
    untouched. A new `v2/uc_schema.json` is a generalized duplicate of it —
    identical field shape/nesting, but with every reference-document-specific
    comment (literal `id`/`created`/`updated` values, "derived directly from
    `uc_reference_mdformat.md`/`.ast`" framing) rewritten to be
    document-agnostic. `v2/uc_schema.json` is now *the* canonical v2 schema;
    validated via `jsonschema.Draft7Validator.check_schema()`.
  - **Wrote `v2/uc-schema.md` from scratch** (not a port of `v1/uc-schema.md`)
    — a narrative walkthrough of the current `uc/models/v2` shape: heading
    structure (now with `Extensions`/`Sub-Variations`/`Open Issues`/
    `Related Information` genuinely optional, not v1's always-present
    DEC-005 convention), frontmatter, each H2 section, and a brief callout
    (§6/§7) on why 2 of the original 3 Task 1.3B cross-field validators are
    now structurally unnecessary versus the one (§9) that still applies and
    how it's implemented (`UseCase.validate_step_references_resolve_and_are_unique`).
  - **`v1/uc_schema.json`/`v1/uc-schema.md` marked superseded**: not edited
    themselves (kept as an unmodified historical record), but the feature
    README's own Design Notes section now explicitly calls out all `v1/`
    schema artifacts as superseded/historical-only, and repoints the
    "canonical schema" pointer at the `v2/` artifacts.
  - No re-diff of the schema against `uc/models/v2` code was needed — Task
    1.8 (added after the original `uc_reference_mdformat_schema.json` was
    written) only added a parser function, no model/field changes.
- **Task 1.5 marked COMPLETED**: its last remaining gate (Task 1.7) is now
  closed, so the whole "rebuild `uc` on `models/md`" task is done. Phase 2's
  Task 2.2 (blocked on Task 1.5) is now unblocked (still not-started, but
  no longer waiting on a model-shape decision) — see the Phase 2 Task List
  note.
- No test/code changes this session (documentation/schema-artifact task
  only); `ruff format`/`ruff check`/`vulture` untouched, no new tests added
  (554 tests remains current).

#### 2026-08-12 Task 1.8 completed (`parse_uc`); `parse_uc` MCP tool added ahead of Phase 3

- **Task 1.8 COMPLETED**: `uc/models/v2/parser.py::parse_uc(text: str) -> UcDocument`,
  a free function mirroring `models.adr.v1.parser.parse_adr`'s split (frontmatter via
  `frontmatter.loads`/`UcFrontmatter.model_validate` with the same YAML-date
  `_stringify_metadata` coercion `parse_adr` needed; body via
  `UseCase.from_text(format_text(post.content))`). No dedicated `UcParseError`
  introduced — structural failures surface as the generic engine's own
  `AssertionError`, field/cross-field failures as `pydantic.ValidationError`,
  both left uncaught like `parse_adr`. Re-exported from `uc/models/v2/__init__.py`.
  6 new tests in `tests/uc/models/v2/test_parser.py`, including a full round-trip
  of the feature's own `v2/uc_reference.md` reference document.
- **`parse_uc` MCP tool ADDED** (`uc/tools/parse_uc.py`, `uc/tools/__init__.py`),
  per repo-owner request, ahead of Task 3.1's specification/Task 3.2's full
  implementation: a thin `@mcp.tool()` wrapper over the parser function above,
  taking raw markdown text directly since no id-based use-case file storage
  layer exists yet (unlike `adr/tools/`'s `_paths.py`/`_io.py`). Registered by
  `uc/__init__.py` (new, previously empty) and wired into `server.py`'s
  domain-package import list, mirroring `adr`'s own self-registration
  pattern. 3 new tests in `tests/uc/tools/test_parse_uc.py`. Explicitly scoped
  as a single tool, not a claim that Phase 3 is done — see the Task List's
  Phase 3 note.
- 554 tests total (545 prior + 6 + 3 new), `ruff format`/`ruff check`/`vulture`
  clean, `specmgr docs` regenerated.

#### 2026-08-12 New `v2/uc_reference*` artifacts; `uc_reference_mdformat_schema.json` written; 3 model/document discrepancies resolved

- Repo owner renamed `v2/uc_example.md` to `v2/uc_reference.md`, and added
  `v2/uc_reference.ast` (its raw CommonMark AST dump), plus an mdformat-
  normalized pair (`v2/uc_reference_mdformat.md`/`.ast`) and two `.puml`
  diagrams. Old top-level exploration docs (`eval-uc.md`, `uc-schema.md`,
  `uc_schema.json`, `uc_example.md`/`.ast`, etc.) were moved into a new
  `v1/` subfolder for the same reason `v2/` exists — separating the
  original hand-written-parser-era artifacts from the `models/md`-engine-era
  ones. `tests/uc/models/v1/test_parser.py`/`test_uc_diagram.py`'s hardcoded
  `_EXAMPLE_PATH` was updated to the new `v1/uc_example-v1.md` location (a
  path-only fix, no behavior change) — this had silently broken 2 tests
  until caught by this session's full-suite run.
- **Wrote `v2/uc_reference_mdformat_schema.json`**: a JSON Schema (draft-07)
  for `uc_reference_mdformat.md`, built by cross-referencing its AST against
  `uc/models/v2/use_case.py`/`frontmatter.py`/`document.py`, mirroring those
  Pydantic classes' property names/nesting (including the
  `extensions.extensions`/`sub_variations.sub_variations` double-naming and
  the extra `related_information.notes.items`/`.assumptions.items` nesting
  level vs. v1's flatter shape). Validated via
  `jsonschema.Draft7Validator.check_schema()` plus a hand-built instance
  from the reference document's actual content.
- **Found, then fixed, 3 discrepancies** between the reference document and
  the then-current `uc/models/v2` code (surfaced while writing the schema
  above — `UseCase.from_text()` would have failed on this exact reference
  document before this fix):
  1. `### Preconditions` (doc, plural) vs. `Precondition`'s auto-derived
     singular heading — **resolved by renaming the class/field**
     `Precondition`/`precondition` to `Preconditions`/`preconditions`
     (matches the doc without needing an explicit `@alias`, same as every
     other plain-name h3 field).
  2. `### Channels to Primary/Secondary Actors` (doc, lowercase "to") vs.
     `ChannelsToPrimaryActor`/`ChannelsToSecondaryActors`'s
     `space_separated_name`-derived title-cased heading ("Channels **To**
     ...") — **resolved by adding an explicit `@alias(..., AliasType.LITERAL)`**
     to both classes, matching the document's exact casing.
  3. Frontmatter `type: doc-uc` (doc) vs. `UcFrontmatter.type: Literal["uc"]`
     (code) — **resolved in the document's favor of the code**: updated
     `v2/uc_reference.md`'s frontmatter to `type: uc`. `uc_reference_mdformat.md`
     itself carries no `type` field in its (AST-mangled, unstripped)
     frontmatter heading, so nothing needed changing there.
     `uc_reference_mdformat_schema.json` updated to drop its `x-discrepancy`
     notes now that all three are resolved (`type` is `const: "uc"`, no
     remaining code/document mismatch). `uc/models/v2/__init__.py`'s exports
     updated for the `Preconditions` rename. 4 existing tests updated for the
     heading-text rename (`test_use_case.py`, `test_document.py`) plus the
     `_EXAMPLE_PATH` fixes above; 545 tests still passing, `ruff format`/
     `ruff check`/`vulture` clean, `specmgr docs` regenerated.

#### 2026-08-12 Task 1.6 completed; Task 1.7/1.8 added to close out Task 1.5

- **Task 1.6 COMPLETED**: Ported the one still-applicable Task 1.3B cross-field
  `model_validator` onto `uc/models/v2/use_case.py`:
  `UseCase.validate_step_references_resolve_and_are_unique`, checking that every
  `Extension`/`SubVariation` heading's `{ref}`/`{N}` resolves to an existing
  1-based position in `main_success_scenario.steps`, with no duplicate
  references within either collection — same invariant as v1's
  `_validate_unique_and_resolvable`, adapted to extract the reference from the
  heading's `.text` (via `_EXTENSION_HEADING_PATTERN`/`_SUB_VARIATION_HEADING_PATTERN`)
  instead of a dedicated `step_reference` field, since v2 has no such field.
  The other two original Task 1.3B validators were confirmed (not re-written)
  as structurally unnecessary now that `steps`/`Extension.items` are real
  CommonMark ordered lists — including a dedicated test proving
  `ExtensionItem.notes` (new vs. v1) introduces no numbering invariant of its
  own. `ruff format`/`ruff check` clean.
- **Task 1.7/1.8 ADDED**: splitting the "remaining work before Task 1.5 can be
  marked done" prose (previously only in Current Status, not the Task List)
  into two tracked tasks — Task 1.7 (`uc_schema.json`/`uc-schema.md` updates
  for DEC-010's schema change) and Task 1.8 (a `from_text`/parser entry point
  for `UcDocument`) — per repo-owner request, so Task 1.5's remaining scope is
  enumerated the same way every other task is, rather than living only as
  Current-Status narrative.
- 545 tests total (538 prior + 7 new: `tests/uc/models/v2/test_use_case.py`).

#### 2026-08-12 Task 1.5 substantially implemented; full-rebuild finding superseded (DEC-010); framework bug found+fixed in feat-5

- **Task 1.5 (rebuild on `models/md`) substantially implemented**, correcting the
  2026-08-11 finding that a "full rebuild" wasn't achievable. Built out, in
  `src/biz/dfch/specmgr/uc/models/v2/`: `use_case.py` (`CharacteristicInformation`
  and its ~15 h3 fields, `MainSuccessScenario.steps: list[MarkdownListItem]`,
  `Extensions`/`Extension`/`ExtensionItem`, `SubVariations`/`SubVariation`,
  `OpenIssues`, `RelatedInformation`/`Notes`/`Assumptions`, root `UseCase`),
  `frontmatter.py` (`UcFrontmatter`, narrowing `MarkdownFrontmatter`'s `type`/
  `status`, dropping v1's `uc-NNN` `id` pattern in favor of `AdrFrontmatter.id`'s
  specmgr-assigned-identifier convention), and `document.py` (`UcDocument`,
  pairing `UcFrontmatter`+`UseCase`, mirroring `models.adr.v1.Adr`). 39 new
  tests in `tests/uc/models/v2/` (full repo suite: 538 passing).
- **Finding superseded (DEC-010)**: proved empirically
  (`tests/uc/models/v2/test_extensions_parsing.py`/`test_sub_variations_parsing.py`)
  that the generic engine's regex `@alias` *does* support a dynamically-named,
  repeated h3 sub-heading under a fixed h2 parent — the exact capability the
  2026-08-11 finding claimed didn't exist. The other half of that finding
  (Cockburn's compound action numbering, e.g. `"3a1."`, is not valid CommonMark
  list syntax) still holds, but was resolved by changing the on-disk schema
  instead of building a hybrid parser (DEC-010): `Extension` actions are now a
  plain ordered list (`ExtensionItem` under `Extension.items`), with
  cross-references expressed as prose ("Return to step 4."), matching how
  `MainSuccessScenario.steps` already worked. `ExtensionItem` additionally
  supports an optional `notes: list[MarkdownParagraph]` field for a loose-list
  continuation paragraph (a v1 gap this happens to close, not something v1 had).
  No hybrid two-pass parser / `parsed_items()` escape hatch from the original
  draft sketch was needed in the end.
- **Framework bug found and fixed in the (closed) feat-5-md-model-parser
  feature**, discovered while integrating: `MarkdownSection.get_extent` only
  ever checked heading *level*, never the declared `@alias`, unlike
  `from_text`. This broke `process_field`'s optional-field "absence" detection
  whenever an absent optional heading-section field was immediately followed
  by a *different*, same-level sibling heading (reproduced independently
  against this feature's own `RelatedInformation.notes`/`assumptions` and the
  pre-existing `CharacteristicInformation.failed_end_condition`/
  `secondary_actors`). Fixed in `models/md/markdown_section.py`
  (`get_extent` now also calls `match_alias`); feat-5's own
  `test_markdown_section.py` updated in place (7 tests switched from the bare,
  unaliased `MarkdownSection3` to its own pre-existing `_AnyHeadingLeafSection`
  fixture, plus 1 new regression test) — see
  `.specmgr/feat/feat-5-md-model-parser/README.md`'s matching 2026-08-12 entry
  for the full writeup and rationale for why this was treated as a bugfix on a
  closed feature, not a reopening of its design.
- **Task 1.6 ADDED**: port/re-verify the three Task 1.3B cross-field
  `model_validator`s onto the v2 model tree -- see the Task List entry for the
  per-validator breakdown (one now structurally obsolete thanks to real
  CommonMark lists, one needs re-confirming now `ExtensionItem` has a new
  `notes` field v1 never had, one -- `UseCase`-level step-reference resolution
  -- still genuinely needs writing). Not started this session; left for a
  fresh session per repo-owner request (context budget).

#### 2026-08-11 Task 1.5 draft sketch — full-rebuild feasibility finding

- **Task 1.5 draft**: Wrote `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py`, a design-review-only sketch (not wired into `src/`, not tested) of the rebuilt model tree. Found, and verified empirically via `MarkdownIt().parse(...)`, that a literal full rebuild is not achievable as scoped: Cockburn's compound extension-action numbering (`"3a1. ..."`) is not valid CommonMark ordered-list syntax (letters after the leading digits disqualify it) — it tokenizes as one plain paragraph, not a list — unlike Main Success Scenario's steps (`"1. ..."`, `"2. ..."`), which *are* a real `ordered_list_open`/`list_item_open` list. Worse, `Extensions`/`SubVariations`'s own per-item h3 headings (`"### 3a. ..."`, `"### Step 1: ..."`) are dynamically named per document, which `MarkdownStr.from_text`'s statically-declared-field model cannot decompose at all yet — feat-5's own REQ-007 note already flagged this same gap for its fixture. The draft sketch adopts a hybrid instead: the generic engine owns frontmatter, top-level sections, Characteristic Information's ~15 h3 fields (via a new `BulletListSection`/`ProseSection` convenience pair, an improvement over the fixture's opaque-leaf shape), and Main Success Scenario's real ordered list (`Step(MarkdownListItem)`, `MainSuccessScenario.steps: list[Step]` — as a bonus, Task 1.3B's step-numbering-contiguity validator becomes structurally unnecessary under this shape, not just ported forward); `Extensions`/`SubVariations` stay leaf `MarkdownSection2`s with a second, dedicated regex-based parse pass (reusing `uc/models/v1/parser.py`'s existing patterns and the existing `Extension`/`ExtensionAction`/`SubVariation` models unchanged) recovering typed structure from the leaf's raw text. Left `parsed_items()`/the cross-reference re-validation as `NotImplementedError` in the sketch (routine porting, not a design question). Three open decisions block finalizing Task 1.5 (see the sketch's trailing comment block): accept the hybrid as final; change the on-disk schema to forbid compound numbering (option 2 from that block, recommended if full rebuild proves necessary); or raise a primitive against feat-5 for "repeated section" support (option 3, would unblock other future multipart headings).

#### 2026-08-11 Task 1.5 added (Phase 1 reopened)

- **Task 1.5 ADDED**: Rebuild the uc schema/models on feat-5-md-model-parser's now-closed generic `models/md` Markdown-to-Pydantic engine (`MarkdownStr`, `MarkdownSection1`..`6`, `MarkdownParagraph`, `MarkdownListItem`, `MarkdownFrontmatter`), replacing the hand-written `uc/models/v1` Pydantic models and the custom `parse_uc` parser/renderer. Directly actions feat-5's own Follow-up #3 ("worth revisiting if/when `feat-4-use-cases` evaluates adopting this engine for its own `uc` schema"). Scoped as a full rebuild (DEC-009), not an evaluation-only spike. Reopens Phase 1 (previously marked complete on 2026-08-05); the three cross-field `model_validator`s from Task 1.3B must be preserved on the rebuilt model tree, since the generic engine has no equivalent built-in check. Task 2.1 (UC diagram generator, done) is flagged as possibly needing rework once Task 1.5 lands; Task 2.2 (Sequence diagram generator, main success path) is now explicitly blocked on Task 1.5 rather than started against a model shape that may be replaced. Dependencies section updated to record feat-5-md-model-parser as a completed dependency for this task.

#### 2026-08-05 (continued)

- **Task 1.1 COMPLETED**: Markdown schema definition and formal specification
  - Created `uc_schema.json` — Complete JSON Schema with validation rules, constraints, and field types (312 lines)
  - Created `uc_reference_mdformat.md` — Detailed "Buy Goods" use case example with all sections
  - Created `uc_class.puml` — Class diagram showing schema structure
  - Frontmatter: `id`, `version`, `status`, `created`, `updated` (no title field; H1 is source of truth)
  - H1: Use case name
  - H2: Main sections (Characteristic Information, Main Success Scenario, Extensions, Sub-Variations, Open Issues, Related Information)
  - H3: Subsections (Goal in Context, Scope, Level, Preconditions, Success End Condition, Failed End Condition, Primary Actor, Secondary Actors, Trigger, Frequency, Priority, Performance Target, Channels, Related Use Cases, step variations)
  - Max heading depth: H1-H3
  - Required sections: Characteristic Information, Goal in Context, Scope, Level, Preconditions, Success End Condition, Primary Actor, Trigger, Main Success Scenario
  - Optional sections: Failed End Condition, Secondary Actors, Frequency, Priority, Performance Target, Channels, Related Use Cases, Extensions, Sub-Variations, Open Issues, Related Information (Notes, Assumptions)
  - Generated PlantUML diagrams (activity and sequence diagrams for main success path and extensions)
- **Task 1.2 COMPLETED**: Create Pydantic models from JSON Schema
  - Created 5 model files in `src/biz/dfch/specmgr/uc/models/v1/`:
    - `frontmatter.py` — `UseCaseFrontmatter`
    - `characteristic_information.py` — `CharacteristicInformation`, `RelatedUseCases`
    - `scenario.py` — `Step`, `MainSuccessScenario`, `Extension`, `Extensions`, `SubVariation`, `SubVariations`
    - `related_information.py` — `OpenIssues`, `RelatedInformation`
    - `usecase.py` — `UseCase` (root model)
  - 12 Pydantic model classes total, matching class diagram exactly
  - Full validation with pattern matching, enum validation, min/max constraints, required/optional field enforcement
  - Created comprehensive test suite: 55 tests across 5 test files covering all models and validation rules (tests/uc/models/v1/)
  - All tests passing (257 total tests in project: 186 ADR + 55 UC + 16 other)
  - Package structure follows DEC-004: models inside domain package (`uc/models/` not shared `models/uc/`)
  - One class per file policy enforced (with logical grouping for tightly coupled classes)
  - Class names aligned with class diagram: `UseCaseFrontmatter` (not `UcFrontmatter`), `Step` (not `MainSuccessScenarioStep`)
- **Housekeeping**: Moved Java reference implementation files to `playground/` subdirectory (not part of Python implementation)
- Notes: User confirmed preference for UC + Sequence diagrams (not Activity diagrams). Sequence diagrams will have separate diagrams for main success path and each extension. Reference: https://www.cs.otago.ac.nz/coursework/cosc461/uctempla.htm

#### 2026-08-05 Task 1.3 split into 1.3A/1.3B

- **Task 1.3 split**: Originally a single task ("Implement validation tool"), split into Task 1.3A (Markdown parser) and Task 1.3B (cross-field validators) since a `parse_uc` parser didn't yet exist — a prerequisite for any file-based validation, unlike ADR where `parse_adr` predates its `validate_adr` tool. Kept the dotted sub-numbering so the overall task numbering (Task 2.x, 3.x) didn't need renumbering. See DEC-006/DEC-007.
- **Task 1.3A COMPLETED**: Fixed `Extension.actions` (previously `list[str]`) to `list[ExtensionAction]`, modeling the compound sub-numbering (`3a1`, `3a2`, ...) already present in `uc_reference_mdformat.md` but not yet in the Pydantic schema. Updated `uc_schema.json` to match. Implemented `parse_uc` (`uc/models/v1/parser.py`), mirroring ADR's `parse_adr` heading-outline-tree approach (`models/adr/v1/parser.py`) but extended with numbered/bulleted Markdown list parsing (Main Success Scenario steps, Extension actions, most `list[str]` fields) and compound-heading parsing (`### {stepRef}. {condition}` for Extensions, `### Step N: {label}` for Sub-Variations). Raises a dedicated `UcParseError` for structural problems, distinct from `pydantic.ValidationError` for field-content/invariant problems — same two-channel split as ADR's parser. Round-trips the full `uc_reference_mdformat.md` file correctly. 14 new parser tests (structural-error cases + full-document + minimal-document round trips), plus 1 new `ExtensionAction` test file and updated `Extension`/`Extensions`/`UseCase` model tests for the new `actions` shape.
- **Task 1.3B COMPLETED**: Added three `model_validator`s not expressible in JSON Schema draft-07 (cross-item/cross-field invariants): (1) `MainSuccessScenario.steps` must be numbered contiguously 1, 2, 3, ... ascending, no gaps/duplicates/out-of-order; (2) `Extension.actions` must be numbered `{step_reference}1`, `{step_reference}2`, ... sequentially; (3) `UseCase`-level check that every `Extension`/`SubVariation` `step_reference` resolves to an existing `main_success_scenario` step number, with no duplicate references within either collection. Unlike ADR's analogous Considered-Options/Option-section gap (deliberately left unenforced per `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §7), this cross-reference check is explicitly enforced here since Task 1.3's original title named "step numbering" as in-scope. 12 new tests across `test_main_success_scenario.py`, `test_extension.py`, `test_use_case.py`.
- All 292 tests passing (186 ADR + 90 UC + 16 other), `ruff format`/`ruff check` clean, `specmgr docs` regenerated.

#### 2026-08-05 Task 1.4 completed

- **Task 1.4 COMPLETED**: Wrote `uc-schema.md` — a narrative walkthrough of the Cockburn-based use case schema (heading structure, frontmatter, each H2 section, the three cross-field `model_validator` invariants and where each constraint lives across `uc_schema.json`/Pydantic field declarations/`model_validator`s, and how `parse_uc` maps Markdown onto it). References rather than duplicates `uc_schema.json` (exact field constraints) and `uc_reference_mdformat.md` (full worked example), mirroring how `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` explains MADR sections without restating the whole template. Placed at `.specmgr/feat/feat-4-use-cases/uc-schema.md` (feature-local, not top-level `doc/`) since the feature is still mid-flight. Phase 1 now fully complete.

#### 2026-08-05 Task 2.1 completed

- **Task 2.1 COMPLETED**: Implemented `render_uc_diagram(use_case: UseCase) -> str` (`uc/models/v1/uc_diagram.py`), a pure function (no file I/O, no multi-document resolution — parses/renders exactly one `UseCase` at a time, mirroring `models/adr/v1/renderer.py`'s style) that generates a PlantUML Use Case diagram: one `usecase` node for the document itself, one `actor` node per distinct label derived from `primary_actor`/`secondary_actors`, and one association edge per actor. Sub-use-case mentions in actor/extension text (e.g. "(UC-044)") are left as plain text, never resolved into separate nodes, since no id→document listing/resolution layer exists yet (Phase 3). Actor label extraction rule: use the contents of the first double-quoted substring if present (taking priority over any parenthetical), otherwise strip everything from the first `" ("` onward, otherwise use the text as-is. A label that is already a bare PlantUML identifier (e.g. `"Buyer"`, `"Bank"`) is reused as its own alias unquoted; otherwise a generated `actorN` alias is used with the label quoted. 12 new tests in `tests/uc/models/v1/test_uc_diagram.py` (label-extraction cases, diagram structure, full `uc_reference_mdformat.md` round-trip). 304 tests total (292 prior + 12 new), `ruff format`/`ruff check` clean, `specmgr docs` regenerated.
