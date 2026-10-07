# Archived history — feat-12-qa-artifact

Older "Recent Updates" entries moved out of `README.md` to keep the live
Progress section focused on current state. Newest archived entry first.

#### 2026-08-18T22:45:00.000Z - Update

Completed: Phase 5 (Cross-cutting registration) — Tasks 5.1, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8 (intentional gap at 5.2,
folded into Task 3.1.1 earlier in the plan). Read `server.py`, `pyproject.toml`'s `[tool.setuptools.package-data]`,
`.pre-commit-config.yaml`, `.github/workflows/ci.yml`, and `AGENTS.md` in full first, per the orchestrator's
instructions, confirming the already-established fact that `qa`'s MCP surface was already transitively registered (via
`commands/schema.py` importing `qa.models.v1`, which triggers `qa/__init__.py`'s own `tools`/`resources`/`prompts`
import) before this phase started, so `docs/MCP.md`/`docs/GENERATED.md` needed no regeneration here. **Task 5.1**:
Changed `server.py`'s bottom import line to `from . import adr, general, qa, req, tsk, uc  # noqa: E402, F401`
(alphabetical order). Updated the module docstring: added a `specmgr://qa/schema`/`/example`/`/template`/`/list`
resources block (placed after the `tsk` block and before `specmgr://iso25010`, matching the existing
chronological-addition-order convention, not strict alphabetical), a sentence extending the existing REQ/UC/TSK
no-`/{id}`-resource note to cover QA, a "QA tools (`qa/tools/`): ..." line listing all 9 tools (placed after the Task
list tools line, before General tools), a "QA prompts (`qa/prompts/`): `create_qa`, `update_qa`" line (after Task list
prompts), and updated the "Modules are grouped domain-first" paragraph's domain list (`adr`, `uc`, `req`, `tsk`, `qa`,
and later `ac`), its import-list mention (`adr`/`general`/`qa`/`req`/`tsk`/`uc`, alphabetical), and its closing sentence
(`req`, `tsk`, and `qa` each register `tools`, `resources`, and `prompts`; `uc` registers `tools` and `resources` only).
**Task 5.3**: Added `"biz.dfch.specmgr.qa" = ["data/*.md", "data/*.json"]` to `pyproject.toml`'s
`[tool.setuptools.package-data]`, placed alphabetically among the domain packages (`qa` before `req`, `req` before
`tsk`, `tsk` before `uc`), with `general` kept last as the existing convention already has it (not alphabetical --
`general` would otherwise sort before `qa`/`req`/`tsk`/`uc`). **Task 5.4**: Widened the shared `files:` glob on all four
existing schema hooks (`specmgr-schema`, `specmgr-schema-req-package`, `specmgr-schema-uc-package`,
`specmgr-schema-tsk-package`) from `^src/biz/dfch/specmgr/(req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$`
to `^src/biz/dfch/specmgr/(qa/models/v1|req/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$` (alphabetical
inside the group). Added a new `specmgr-schema-qa-package` hook, a 1:1 mirror of `specmgr-schema-tsk-package`'s
shape/wording (`entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`, same widened
glob). **Task 5.5**: Added two new CI steps to `.github/workflows/ci.yml`, placed immediately after the existing
`src/biz/dfch/specmgr/tsk/data/tsk_schema.json` step and before the `docs/coverage.svg` step: "Make sure
`docs/qa_schema.json` is correct" (bare `specmgr schema`, same `if: matrix.python-version == '3.13'` guard and
`::error::` failure-message pattern as the existing `docs/req_schema.json`/`docs/uc_schema.json` steps) and "Make sure
`src/biz/dfch/specmgr/qa/data/qa_schema.json` is correct" (`specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`). **Task 5.6**: Updated `AGENTS.md`'s heading to "six domain/cross-cutting packages
implemented (ADR, REQ, UC, TSK, QA, general)" and its lead-in sentence to "Five document-type domains plus one
cross-cutting package". Added a `qa/` bullet after the `tsk/` bullet (matching the existing chronological-order
convention the other bullets already use, not alphabetical), mirroring REQ's/TSK's own bullet depth (tools list,
resources list, prompts list, no-`/{id}`-resource note citing ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Updated the
"Still genuinely missing" list: added `validate_qa` to the pre-commit/CI enforcement bullet (for consistency -- `qa` has
the identical gap REQ/UC/TSK already have), added `delete_qa` to the stubs bullet, and added `qa` to the
tools/resources/prompts registration-summary bullet. Updated the closing "don't assume any other domain package exists
beyond..." paragraph and, since it also enumerates all five prior domains and would otherwise be factually wrong by
omission, the "MCP server (`server.py`)" section's own "imports every domain package (...)" sentence -- the one specific
case the hard-rule carve-out ("unless it specifically enumerates the 5 domains and would now be factually wrong by
omitting `qa`") applies to; no other section was touched. **Task 5.7**: Ran `specmgr docs`, `specmgr mcp-docs`, `specmgr schema --type qa`, and `specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`, each twice. First run:
`specmgr docs` regenerated only `docs/api/biz.dfch.specmgr.server.md` (the docstring changes from Task 5.1); `specmgr mcp-docs` produced no `git diff` at all (confirming the orchestrator's stated fact that `docs/MCP.md` already reflected
`qa`'s full surface from the Phase-4-era transitive import); both `specmgr schema --type qa` invocations reported
`(unchanged)` since Task 3.1.1/4.4 already drafted both files correctly. Second run of every command: identical
`(unchanged)` results and an identical `git diff --stat docs/` to the first run -- all four commands confirmed
idempotent, no further drift introduced by Task 5.1's docstring edit or Task 5.6's `AGENTS.md` edit (which `specmgr docs`/`mcp-docs` don't even read, since `AGENTS.md` isn't a `src/` docstring source). **Task 5.8**: Ran the full
phase-end quality gate: `uv run --frozen ruff format --check` (766 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no output, clean), and `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (1144 tests, OK -- identical count to Phase
4's end, no regressions, as expected since Phase 5 is pure cross-cutting registration/config with no new `src/`/`tests/`
Python logic). Left staging/committing to the orchestrator per this session's instructions; working tree has the edited
`server.py`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `AGENTS.md`, and the regenerated
`docs/api/biz.dfch.specmgr.server.md`, all unstaged. Next: Phase 6 (Final cross-cutting verification) — Task 6.1. Notes:
`qa` is now identically wired into every cross-cutting mechanism REQ/UC/TSK already have (server registration,
packaging, pre-commit schema hooks, CI schema-drift checks, `AGENTS.md`). Phase 6 is a verification-only pass (walk
ACC-001..006, run the full quality gate including pylint-advisory/`specmgr docs`/`specmgr mcp-docs`/`specmgr schema --type qa` end-to-end one more time) and setting the feature status to `done` -- no new implementation is expected
there.


#### 2026-08-18T21:10:00.000Z - Update

Completed: Phase 4 (MCP Surface) — Tasks 4.1, 4.2, 4.3, 4.4, 4.5, 4.6. Read every REQ file the plan named
(`req/tools/*.py`, `req/resources/*.py`, `req/prompts/*.py`, `req/data/*`, `req/__init__.py`,
`general/tools/_packaged_data.py`, `general/tools/_doc_paths.py`) plus `qa_reference.md` and `qa/models/v1/*.py` before
writing anything, per the orchestrator's instructions. **Task 4.1**: Created
`qa/tools/{__init__,_paths,_io,_lock,_write, parse_qa,get_qa,get_qa_example,get_qa_template,create_qa,update_qa, set_status_qa,delete_qa,validate_qa}.py`, a 1:1 port of every corresponding `req.tools` module with every `Req`/`req`
identifier substituted for `Qa`/`qa` (`ReqDocument` -> `QaDocument`, `ReqFrontmatter` -> `QaFrontmatter`, `Requirement`
-> `Qa` -- the `qa` domain's own body class, not to be confused with `qa`'s *own*, differently-shaped `Requirement`
callout class from Phase 3 -- `ReqNotFoundError` -> `QaNotFoundError`, `req_lock`/`req_base_dir` ->
`qa_lock`/`qa_base_dir`, `REQ_TYPE_NAME` -> `QA_TYPE_NAME`). Every design-rationale docstring (error-channel split, lock
rationale, no-render-just-persist-verbatim design, read-only/write directory split, id -> path skip-on-parse-failure
rule) was preserved and reworded for QA, not stripped. `create_qa`'s filename convention is
`qa-{id}-{slugify(body.text)}.md`. `set_status_qa` reconstructs `QaFrontmatter` via its own constructor (not
`model_copy`) so the four-value closed-set `status` validator (`draft`/`active`/`done`/`cancelled`) actually runs.
`delete_qa` is a registered `structured_output=False` stub, always raising `NotImplementedError`. `validate_qa` mirrors
`validate_req`'s disk-free/id-free dry-run shape exactly. **Task 4.2**: Created
`qa/resources/{__init__,qa_schema,qa_example, qa_template,qa_list}.py`, 1:1 ports of REQ's four resources at the same
four URIs (`specmgr://qa/schema`, `/example`, `/template`, `/list`, no `/{id}`). `qa_list` builds `QaSummary` entries
(`id`/`title`=`doc.body.text`/`status`/`ref`=`path.stem`), silently skipping any file that fails to parse
(`AssertionError`/`pydantic.ValidationError`), identical to `req_list`'s own skip rule. **Task 4.3**: Created
`qa/prompts/{__init__,create_qa,update_qa}.py`, matching `req/prompts/`'s instructional-text-returning `@mcp.prompt()`
shape exactly, but with the instructional content fully rewritten for QA's own schema: the `create_qa` prompt recaps `# {title}`, `## General` (`### Introduction`/`### Raw Requirements`), the nine fixed ISO/IEC 25010:2023 characteristic H2s
in their canonical order/wording, the free-form `### {question}` `QaSection` pattern (optional
`comment`/`requirement`/`question`/`answer`), and optional `## More Information`; it tells the LLM to check
`specmgr://qa/list` first, elicit characteristic-relevant answers per category (noting a category may legitimately stay
empty), and reference `specmgr://qa/template`/`/example`/`/schema` before calling `create_qa`/`validate_qa`. The
`update_qa` prompt maps body changes to `update_qa(id, content)` (whole-body replace, explicitly warning that all nine
fixed category headings must be carried forward even when empty) and status changes to `set_status_qa(id, status)`
(draft/active/done/cancelled), mirroring `update_req`'s prompt structure/tone. **Task 4.4**: Created
`qa/data/qa_example.md` by reusing Phase 2's `qa_reference.md` verbatim (mirroring REQ's own reference-is-example
precedent named as an explicit option in this task) -- verified via a throwaway `parse_qa(...)` call that it round-trips
successfully (`frontmatter.id`, `body.text`, `compatibility.items is None`, and `functional_suitability`'s two Q&A pairs
all came back correctly; see Decisions Made for why no TSK-style light adaptation was needed). Created
`qa/data/qa_template.md` from scratch (not adapted from `qa_reference.md`) with every fixed H2 present, both `## General` sub-sections, one Q&A pair with all four optional fields filled with short placeholder text (`comment`/`#### Requirement`/`question`/`answer`), and `## More Information` -- verified it happens to parse successfully end-to-end too
(a stronger guarantee than the task required, which only asked for structural completeness). Copied
`docs/qa_schema.json` byte-for-byte to `qa/data/qa_schema.json` (confirmed via `diff`). Edited (not recreated)
`qa/__init__.py`, replacing its Phase-3-only docstring with one mirroring `req/__init__.py`'s exact shape/wording, and
added `from . import prompts, resources, tools  # noqa: F401` plus the matching `__all__`; explicitly noted
`server.py`'s own import list still excludes `qa` (Phase 5's Task 5.1). **Task 4.5**: Read every file under
`tests/req/{tools,resources, prompts}/` first, then created the mirrored `tests/qa/{tools, resources,prompts}/` suites
(`__init__.py` markers plus 19 test files, 83 tests total: 53 in `tools/`, 15 in `resources/`, 15 in `prompts/`), all
isolated from the real filesystem via `mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: ...})` against a
`tempfile.TemporaryDirectory()`, the same pattern `tests/req/` uses. Coverage mirrors REQ's own depth/shape per file
(base-dir resolution, id lookup and its skip-on-parse-failure rule, lock serialization, write-and-round-trip,
create/update/get/set-status/delete/validate/parse tool behavior including every error channel, packaged-data
example/template reads with cache-freshness and missing-file checks, the `qa_list` resource's skip-malformed-file
behavior, and prompt content/ordering assertions) -- adapted only where QA's own schema differs from REQ's (see
Decisions Made for the one genuine coverage gap this surfaced). **Task 4.6**: Ran the full phase-end quality gate: `uv run --frozen ruff format --check` (744 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no output, clean -- no new dead-code flags this phase,
unlike Phase 3), and `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (1144 tests, OK -- up
from 1061, i.e. exactly the 83 new `qa` tests, no regressions). Also ran `uv run --frozen specmgr docs` (regenerated
`docs/api/*.md` for 20 new `qa` modules plus `docs/GENERATED.md`'s test-file count 156 -> 175) and confirmed a second
run produces an identical `git status --short docs/` (idempotent). Left staging/committing to the orchestrator per this
session's instructions; working tree has the new `qa/{tools,resources,prompts, data}/`/`tests/qa/{tools,resources,prompts}/` trees, the edited `qa/__init__.py`, and the regenerated docs, all
unstaged. Next: Phase 5 (Cross-cutting registration) — Task 5.1 (`server.py` -- add `qa` to the bottom import line,
update the module docstring). Notes: `qa`'s tools/resources/prompts are fully built, importable, and unit-tested
standalone (each test imports the specific function directly, e.g. `from biz.dfch.specmgr.qa.tools.create_qa import create_qa`, mirroring how `tests/req/` itself never round-trips through a live MCP server), but are not yet registered
against the live MCP server -- `server.py`'s bottom-of-file import list still only imports `adr`, `general`, `req`,
`tsk`, `uc`, not `qa`. That wiring, plus `pyproject.toml` package-data, the pre-commit schema-hook glob, and the CI
schema-drift check, are all Phase 5 work and were deliberately left untouched this phase.


#### 2026-08-18T19:30:00.000Z - Update

Completed: Phase 3 (Pydantic Models & Parser) — Tasks 3.1, 3.1.1, 3.2, 3.3. **Task 3.1**: Created the `qa` domain
package: `src/biz/dfch/specmgr/qa/__init__.py` (docstring-only for now, since `tools`/`resources`/`prompts` don't exist
until Phase 4 -- it does not import them yet, unlike `req`/`tsk`'s own `__init__.py`), plus `qa/models/__init__.py` and
`qa/models/v1/{__init__,_util,frontmatter, body,document,parser,summary}.py`, all inside the domain package per the
domain-first layout (ADR ece4554b-725c-4f76-bc04-5d2b760363d2), mirroring `req`/`tsk`'s exact file shapes read directly
from disk first. `QaFrontmatter` reuses `TskFrontmatter`'s `_ALLOWED_STATUSES` pattern verbatim
(`draft`/`active`/`done`/`cancelled`). `body.py` implements the full schema from Design Notes: `Qa(MarkdownSection1)`,
`General(MarkdownSection2WithComment)` with `Introduction (MarkdownSection3WithComment)`/`RawRequirements(MarkdownSection3)`, `QaSection(MarkdownSection3WithComment)` with
`requirement`/`question`/`answer`, `Requirement(MarkdownSection4)` decorated `@markdown(end_marker=MarkdownBlockQuote)`,
and the 9 ISO/IEC 25010:2023 `<QaCategory>` classes. Resolved the plan's deferred 9-category class-sharing question by
empirically verifying (via a throwaway script, then codified in `tests/qa/models/v1/test_body.py`) that approach (a) --
one shared, private `_QaCategory(MarkdownSection2)` intermediate base declaring `items` once, with 9 final subclasses
each relying on implicit `AliasType.SPACE_SEPARATED` alias derivation from their own class names -- carries no
heading-detection risk: confirmed that `MarkdownSection.get_extent`/`from_text`'s `match_alias` call always passes the
actual runtime subclass (e.g. `FunctionalSuitability`), not the shared base, as `cls`, so `cls.__name__` (not
`_QaCategory`'s) is what the implicit alias derivation keys off; also confirmed `_get_field_names()` correctly resolves
the inherited `items` field through the extra inheritance level, and that `@markdown`'s `_metadata`
(`heading_open`/`h2`) is inherited transparently with no per-subclass re-application needed. Discovered
mid-implementation that `QaAnswer` cannot be heading-anchored like `MoreInformation`/`RawRequirements`/`Notes` (all bare
`MarkdownSectionN` subclasses) -- re-reading `qa_reference.md` closely showed every `answer` is trailing prose
immediately after `question`'s block quote with **no heading of its own** anywhere in the document. Implemented
`QaAnswer` as a bare `MarkdownStr` subclass instead (no `@markdown` metadata at all), whose inherited `get_extent`
already captures "everything remaining" with no heading-level stop condition, plus an explicit `text` computed property
(mirroring `MarkdownParagraph.text`/`MarkdownSection.text`/`MarkdownCodeBlock.text`'s established pattern) so `_value`
is reachable through `model_dump()`. Verified `Requirement`'s `@markdown(end_marker=MarkdownBlockQuote)` merges into
`MarkdownSection4`'s already-inherited `type="heading_open"`/`tag="h4"` without needing to re-pass them, and that its
heading text is fixed (`"Requirement"`, matching the implicit `AliasType.SPACE_SEPARATED` derivation), confirmed against
`qa_reference.md`'s literal `#### Requirement` heading. Round-tripped the full `qa_reference.md` through the assembled
`Qa`/`QaFrontmatter` models via a throwaway script before writing `parser.py`, confirming byte-exact round-trip
including the `Compatibility`-is-empty case and the `end_marker` scenario. **Task 3.1.1**: Read `commands/schema.py` in
full, added `generate_qa_schema()` mirroring `generate_req_schema`/`generate_tsk_schema`/`generate_uc_schema` exactly
(imports `SCHEMA_COMMENT_VERSION as QA_SCHEMA_COMMENT_VERSION` from `qa.models.v1`, `QaDocument` from
`qa.models.v1.document`, injects `$schema`/`$comment`, serializes with `indent=2, sort_keys=True` plus trailing
newline), registered `"qa": generate_qa_schema` in `_GENERATORS`, and ran `uv run --frozen specmgr schema --type qa` to
draft `docs/qa_schema.json` (`$comment: "v1"`, top-level `$schema` pointing at the 2020-12 dialect, `$defs` holding all
9 category classes plus
`Qa`/`QaSection`/`QaAnswer`/`Requirement`/`General`/`Introduction`/`RawRequirements`/`MoreInformation`/`QaFrontmatter`/the
shared `models/md` leaf types it references). **Task 3.2**: Added
`tests/qa/{__init__,models/__init__,models/v1/__init__}.py` (empty namespace markers, matching `tests/tsk/`'s exact
convention) and `tests/qa/models/v1/{test_frontmatter,test_body, test_parser}.py` (35 tests total), mirroring
`tests/tsk/models/v1/`'s style/depth. `test_frontmatter.py` covers `type`/`version`/`status` defaults and rejection of
any status outside the four-value set (ACC-003). `test_body.py` covers required-vs-optional field validation on
`Qa`/`<QaCategory>`/`QaSection` via direct construction (ACC-003), an explicit "all 9 categories resolve their own,
distinct, correct heading alias" regression test for the class-sharing decision above, the `Requirement` `end_marker`
wiring (metadata, fixed heading, and a from-text round-trip proving it does not absorb a following block quote), and
`QaAnswer`'s heading-free, multi-paragraph-capturing behavior. `test_parser.py` mirrors
`tests/tsk/models/v1/test_parser.py`'s exact structure (`_REFERENCE_PATH` pointing at this feature's own
`qa_reference.md`): a minimal valid document parses correctly (ACC-004); the full reference document round-trips with
specific assertions on `compatibility.items is None`, every other category's item count, and the first `Functional Suitability` Q&A pair's `requirement`/`question`/`answer` content proving the `end_marker` scenario works end-to-end
(ACC-002/ACC-004); a missing `## General` or a missing ISO-characteristic H2 (`## Safety`) each raise `AssertionError`;
an invalid frontmatter `status` raises `pydantic.ValidationError` (ACC-004). Fixed three initial test failures caused by
`QaAnswer.text` retaining a trailing `"\n"` (its `_value` is the verbatim remaining extent, not a stripped paragraph
text) by asserting `.strip()` equality/`assertIn` instead of exact equality where appropriate. **Task 3.3**: Ran the
full phase-end quality gate: `uv run --frozen ruff format --check` (698 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` -- initially flagged 15 new
Pydantic field names as unused (`introduction`, `raw_requirements`, `requirement`, `question`, `answer`, and the 9
category field names on `Qa` plus `general`), added them to `whitelist.py`'s existing "Pydantic model fields read only
via (de)serialization/rendering" section (same rationale as its existing entries: these fields aren't accessed as plain
Python attributes anywhere in `src/` yet, only via markdown round-tripping and, later, Phase 4's MCP tools), then re-ran
vulture clean. Ran `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (1061 tests, OK -- up
from 1026 before this phase, i.e. exactly the 35 new `qa` tests, no regressions). Also ran `uv run --frozen specmgr docs` (regenerated `docs/api/*.md` for 9 new `qa` modules plus `docs/GENERATED.md`'s test-file count 153 -> 156) and
confirmed a second run produces an identical `git status --short docs/` (idempotent). `docs/qa_schema.json` (drafted in
Task 3.1.1) was left as-is, unchanged since Task 3.1.1. Left staging/committing to the orchestrator per this session's
instructions; working tree has the new `qa/`/`tests/qa/` trees, the `commands/schema.py`/`whitelist.py` edits, and the
regenerated docs, all unstaged. Next: Phase 4 (MCP Surface) — Task 4.1
(`qa/tools/{_paths,_io,_lock,_write,parse_qa,get_qa,...}.py`). Notes: `qa`'s own `tools`/`resources`/`prompts` (and
therefore `qa/__init__.py`'s eventual `from . import prompts, resources, tools` line) remain Phase 4 work; nothing in
Phase 3 registers `qa` against the MCP server yet.


#### 2026-08-18T17:40:00.000Z - Update

Completed: Phase 2 (Specification) — Task 2.1 and Task 2.3. **Task 2.1**: Wrote
`.specmgr/feat/feat-12-qa-artifact/qa_reference.md`, a pure markdown-authoring reference exercising every field of the
schema shape pinned down in Design Notes (no Pydantic models exist yet — that is Phase 3's Task 3.1). Read
`req_reference.md`, `tsk_reference.md`, and `uc_reference.md` first for style precedent, and reused `tsk_reference.md`'s
"Migrate Widgets to the New Registry" theme so this document reads as the requirements-elicitation interview that would
plausibly precede that task list. Frontmatter uses `id: deaddead-feed-feed-feed-deaddeadfeed`, `status: active`, `type: qa` (see Decisions Made). Structure: a single H1, then `## General` (H3 `### Introduction` with two body paragraphs, H3
`### Raw Requirements` as opaque prose), then the 9 ISO/IEC 25010:2023 characteristic H2s in exact canonical
order/wording (verified earlier against the `specmgr://iso25010` resource per the plan's own Design Notes, re-confirmed
here against `general/data/general_iso25010.md`'s own H2 order), then `## More Information`. Q&A (H3) coverage across
categories: `Functional Suitability` has two H3s — the first exercises all four `QaSection` fields at once (an HTML
`comment` immediately after its heading, a `#### Requirement` callout whose own body contains both a nested bullet list
*and* a nested block quote inside one of that list's items, mirroring Task 1.3/1.4's own edge-case fixture almost
verbatim, immediately followed by its `question` block quote — exercising the exact `end_marker` scenario Phase 1 was
built for — then a prose `answer`), the second has only `question`+`answer` (no `comment`/`requirement`), exercising
"all four fields fully optional". `Safety` has one more full-combo H3 (`comment` + `Requirement` + immediately-following
`question` + `answer`, this one without nested list/quote content, as a second, simpler `end_marker` occurrence).
`Performance Efficiency`, `Interaction Capability`, `Reliability`, `Security`, `Maintainability`, and `Flexibility` each
get exactly one `question`+`answer`-only H3. `Compatibility` is the one category deliberately left with **no** H3
children at all (empty `items`), per the plan's explicit "pick which one(s) are empty" instruction — rationale (a purely
internal migration raising no external interoperability/co-existence concerns yet) is documented both in this entry and
inline in the reference doc's own `More Information` section. Ran `uv run --frozen specmgr mdformat .specmgr/feat/feat-12-qa-artifact/qa_reference.md` (exit code `0` — already canonical, no rewrite) and confirmed with
`--dry-run` too. **Task 2.3**: Ran `uv run --frozen ruff format --check` (674 files already formatted), `uv run --frozen ruff check` (all checks passed), and `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no output, clean)
— unaffected, as expected, since this phase only added one markdown file outside `src/`/`tests/`. No unit-test suite
applies (no Pydantic models exist yet). Next: Phase 3 (Pydantic Models & Parser) — Task 3.1 (`qa/models/v1/...`). Notes:
Phase 2 added no `src/`/`tests/` code and made no commits (left to the orchestrator, per this session's instructions).


#### 2026-08-18T16:05:00.000Z - Update

Completed: Phase 1 (`models/md` engine enhancement) — Tasks 1.1 through 1.5. **Task 1.1**: `markdown()` in
`src/biz/dfch/specmgr/models/md/markdown.py` now merges into `getattr(cls, "_metadata", {})` instead of unconditionally
replacing it. `type`/`tag` (and the new `end_marker`, see Task 1.2) became keyword-only parameters defaulting to a
private module-level sentinel `_UNSET = object()` rather than `None`, so "this keyword was not passed" (leave any
inherited value alone) is distinguishable from "this keyword was explicitly passed as `None`" (a real, honored value
that overwrites/clears an inherited entry). Verified 100% backward compatible against all 11 existing `@markdown(...)`
call sites (`markdown_section.py`, `markdown_section1.py`-`markdown_section6.py`, `markdown_paragraph.py`,
`markdown_code_block.py`, `markdown_block_quote.py`, `markdown_comment.py`) — every one still passes both `type`/`tag`
explicitly, so merge-vs-replace is unobservable for them; the `*_with_comment.py` classes were left untouched (they
inherit `_metadata`, never re-apply `@markdown`). **Task 1.2**: Added `end_marker: type[MarkdownStr] | None = _UNSET` to
`markdown()`, stored under `_metadata["end_marker"]` via the same merge/sentinel mechanism as `type`/`tag`. Decorator
docstring/examples updated accordingly (including a new example showing a subclass re-applying `@markdown` and keeping
an inherited `end_marker`). **Task 1.3**: `MarkdownSection.get_extent`
(`src/biz/dfch/specmgr/models/md/markdown_section.py`) now also stops at the first token matching
`cls._metadata.get("end_marker")`'s own `type`/`tag`, but only when that token occurs at nesting depth 0. A running
`depth` counter is updated by every token's own `Token.nesting` across the *entire* token stream (not just tokens
matching the end_marker's type), checked *before* applying that token's own delta — verified by tracing real token
streams via `parse()` for a fixture H4 section with a nested bullet list, a nested block quote *inside a list item*, and
a real depth-0 block quote following: the nested occurrences correctly report depth 2/3 (not 0) and are not mistaken for
the end marker, while the real end-marker block quote reports depth 0 and stops the scan there. **Task 1.4**: Added
`tests/models/md/test_markdown.py` (11-call-site backward-compatibility regression for Task 1.1, plus new
merge/sentinel/`end_marker` unit tests for the decorator itself) and
`tests/models/md/test_markdown_section_end_marker.py` (a fixture `_RequirementLikeSection(MarkdownSection4)` declaring
`@markdown(end_marker=MarkdownBlockQuote)`, exercising: a depth-0 block quote stopping the scan; no end marker following
still reaching the end of the text; and the nested-list-and-nested-block-quote edge case from Task 1.3's note, both
`get_extent` and `from_text` verified). 18 new tests total. **Task 1.5**: Ran the full phase-end quality gate: `uv run --frozen ruff format --check` (673 files already formatted), `uv run --frozen ruff check` (all checks passed), `uv run --frozen vulture src/ whitelist.py --min-confidence 60` (no output, clean), and `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` (1026 tests, OK — up from 1008 before this phase, i.e. exactly the 18 new
tests, no regressions). Also ran `uv run --frozen specmgr docs` since Phase 1 changed docstrings inherited by several
downstream subclasses (`Characteristic` in `models/iso25010.py`, TSK's `Task`, UC's `Assumptions`) — regenerated
`docs/api/*.md` and `docs/GENERATED.md` (test-file count 151 -> 153) to keep them drift-free for the eventual commit;
re-ran it a second time to confirm it is now idempotent (no further changes). Left staging/committing to the
orchestrator per this session's explicit instructions; working tree has the two modified source files
(`models/md/markdown.py`, `models/md/markdown_section.py`), the two new test files, and the regenerated docs, all
unstaged. Next: Phase 2 (Specification) — Task 2.1 (write a full reference `qa_reference.md`). Notes: Phase 1 is the
first and only `models/md` engine change in this feature; Phase 2 onward builds the `qa` domain itself on top of it.


#### 2026-08-18T14:20:00.000Z - Update

Completed: Phase 0 (Cleanup) — Task 0.1 and Task 0.2. Re-verified from the repo root (`ls`, `find . -type d -iname "qa"`, `git status`, `git status --ignored`) that all four previously-flagged stray scaffold paths (`src/qa/`,
`src/biz/dfch/specmgr/qa/{tools,resources, prompts}/`, `tests/qa/`, `biz/dfch/specmgr/qa/`) are **already absent** from
disk — no directory of any of these four paths exists, and neither `git status` nor `git status --ignored` shows any
`qa`-related residue (tracked, untracked, or ignored). No deletion was actually performed as a result — confirming their
absence *is* the completion of Task 0.1 (the scaffolding was evidently already removed in an earlier, unrecorded step or
never actually landed on this checkout), not a skipped task. Task 0.2's phase-end check (`git status` / `git status --ignored` clean of residue) is satisfied by the same verification. This closes Phase 0. Next: Phase 1 (`models/md`
engine enhancement) — Task 1.1 (merge `@markdown(...)` into inherited `_metadata` instead of full replace). Notes:
Implementation of Phase 1 onward has not started yet.


#### 2026-08-18T13:50:58.000Z - Update

Completed: Resolved the Task 5.2 duplication flagged (but left unresolved) at the end of the previous update. Folded the
former Phase 5 Task 5.2 (`generate_qa_schema()` + `specmgr schema` registry entry) into Phase 3's **Task 3.1.1** — which
now implements the generator function, registers it, *and* drafts `docs/qa_schema.json` by running it, all in one task,
right after `QaDocument` (Task 3.1) exists. This mirrors feat-10's own Task 2.5 exactly (generator + registry + draft,
as a single task), rather than REQ's older, more fragmented "draft first (Task 1.2), formalize later (Tasks 2.7-2.9)"
history that the previous update had matched by mistake. Phase 5 now has an intentional numbering gap at `5.2` (same
leave-a-gap convention as Phase 2's `2.2` gap), and Tasks 5.4/5.5 (pre-commit hook, CI step) now depend on Task 3.1.1
instead of the removed Task 5.2. Task 5.7 (docs/schema drift check)'s dependency list updated from the stale "Tasks
5.1-5.6" range to the precise `Task 3.1.1, Task 5.1, Tasks 5.3-5.6`. Next: Phase 0 cleanup, then Phase 1 (`models/md`
engine enhancement). Notes: Implementation still intentionally not started — this remains a plan-only commit.


#### 2026-08-18T12:40:00.000Z - Update

Completed: Fixed the Task 2.2 schema-generation sequencing bug flagged (but deliberately left unresolved) in the
previous update, following feat-10's exact precedent (its own Task 1.3 → Task 2.5 move). Moved the "draft
`qa_schema.json`" task out of Phase 2 (Specification) — where it incorrectly depended only on the reference markdown
file (Task 2.1) — into Phase 3 (Pydantic Models & Parser) as a new **Task 3.1.1**, placed right after Task 3.1 (which
defines `QaDocument`) and depending on it, since `QaDocument.model_json_schema()` cannot run before that class exists.
Used a sub-numbered task id (`3.1.1`) specifically so no other task in Phase 3 onward needed renumbering. Phase 2 now
has an intentional numbering gap at `2.2` (Task 2.3's dependency updated from Task 2.2 to Task 2.1 accordingly) — left
as a gap rather than renumbering Task 2.3, consistent with this project's existing leave-a-gap convention for numbered
sub-items (e.g. `AdrOption` deletion). Task 3.1.1 is explicitly scoped as a one-off draft via a direct
`QaDocument.model_json_schema()` call, not yet wired into the reusable `specmgr schema` CLI registry — that generic
`generate_qa_schema()` + registry entry remains Phase 5's Task 5.2, matching REQ's own historical Task 1.2 (draft) →
Tasks 2.7-2.9 (formalize) sequencing. Phase 3's phase-end task (3.3) now also depends on Task 3.1.1. Next: Phase 0
cleanup, then Phase 1 (`models/md` engine enhancement). Notes: Implementation still intentionally not started — this
remains a plan-only commit.

#### Update 2026-08-18T11:15:00Z

- Completed: Restructured the Task List's execution model, modeled on
  feat-10's per-phase test-and-commit discipline
  (`.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md`) — added
  an explicit "Execution approach" note plus a mandatory phase-end task
  to every phase (0-6): extend/run that phase's unit tests, run the full
  pre-commit/quality gate, and update this README's Progress section,
  before a phase (or session) is considered done. This directly addresses
  the risk that implementation spans multiple sessions due to context
  size — a fresh-context session must be able to resume correctly from
  this file alone. Filled the two gaps where MCP-surface/cross-cutting
  testing was previously deferred to a terminal phase: Phase 4 gained a
  new Task 4.5 (`tests/qa/{tools,resources,prompts}/`) and Phase 5 gained
  a new Task 5.7 (`specmgr docs`/`mcp-docs`/`schema` drift check), each
  followed by its own phase-end task (4.6, 5.8). Phase 6 was repurposed
  from "Tests & Docs" to "Final cross-cutting verification" only
  (mirroring feat-10's own Phase 4), since per-phase testing now covers
  what Phase 6 previously deferred everything to. New tasks were appended
  with new numbers rather than renumbering existing tasks. Deliberately
  left Task 2.2's schema-generation sequencing (drafting `qa_schema.json`
  before any Pydantic model exists) unresolved for a separate pass, per
  explicit instruction, despite feat-10's own Decisions Made log
  recording an identical sequencing bug it had to fix (moved from its
  Phase 1 to Phase 2 as Task 2.5).
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation still intentionally not started — this remains a
  plan-only commit.

#### Update 2026-08-18T09:30:00Z

- Completed: Post-write review pass raised four loose ends, all resolved:
  (1) fixed a naming typo (`Requirement4` -> `Requirement`) and explicitly
  documented that its content is deliberately unspecified, arbitrary
  agent-authored data, not a gap to close later; (2) replaced `General`'s
  and `QaSection`'s hand-declared `comment: MarkdownComment | None` fields
  with inherited `MarkdownSection2WithComment`/`MarkdownSection3WithComment`
  mixins, matching TSK's/REQ's existing precedent; (3) verified the exact
  ISO 25010:2023 characteristic wording directly via the `specmgr:// iso25010` MCP resource (not just the packaged `.md` file) -- confirmed
  the schema's snake_case field names already correspond 1:1; (4) confirmed
  `Introduction`/`RawRequirements`'s implicit `AliasType.SPACE_SEPARATED`
  alias derivation is being kept as-is, intentionally, not changed.
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation still intentionally not started — this remains a
  plan-only commit.

#### Update 2026-08-18T08:00:00Z

- Completed: Full planning/design discussion — schema shape iterated
  through several rounds (blockquote-as-question feasibility check,
  answer-content representation, `QaSection` field ordering, the
  `end_marker` generalization and its decorator-merge prerequisite), this
  `README.md` written.
- Next: Phase 0 cleanup, then Phase 1 (`models/md` engine enhancement).
- Notes: Implementation intentionally not started yet per explicit
  instruction — this commit is plan-only.
