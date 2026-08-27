---
id: feat-21-decision
version: 1.0.0
status: done
created: 2026-08-26
updated: 2026-08-27
---

# Feature: Create artifact type "Decision" (DEC)

## Plan

### Overview

New `dec` domain: decisions **in general** (not architecture-only), keeping the ADR's general structure (MADR headings, `Options` collection) but built on the **generic `models/md` parser** with the **simple surface** used by GOL/RSK/QA — no fine-grained ADR mutation tools, no `specmgr://dec/{id}` resource, no renderer (writes persist the caller's raw validated body byte-for-byte).

### Requirements

- REQ-001: DEC schema + `parse_dec` on the generic `models/md` engine (`dec/models/v1/`: `frontmatter.py`, `body.py`, `document.py`, `parser.py`, `summary.py`, `_util.py` with `SCHEMA_COMMENT_VERSION = "v1"`)
- REQ-002: 10 MCP tools (`create_dec`, `update_dec`, `set_status_dec`, `parse_dec`, `list_dec`, `get_dec`, `get_dec_example`, `get_dec_template`, `delete_dec` stub, `validate_dec`) + private `_paths`/`_io`/`_lock`/`_write` helpers
- REQ-003: 3 MCP resources (`specmgr://dec/schema`, `specmgr://dec/example`, `specmgr://dec/template`); no `/{id}`, no `/list`
- REQ-004: 2 MCP prompts (`create_dec(topic)`, `update_dec(id, instructions?)`) + packaged instruction data
- REQ-005: `generate_dec_schema()` + `_GENERATORS["dec"]` in `commands/schema.py`; packaged `dec/data/dec_schema.json`
- REQ-006: Cross-cutting registration (server, pre-commit, CI, AGENTS.md, root README.md, regenerated docs)
- REQ-007: Full test coverage mirroring `tests/gol/`

### Acceptance Criteria

- [x] ACC-001 (REQ-001): packaged example **and** template parse via `parse_dec`; structural violations raise `AssertionError`: unknown H2; missing `## Context and Problem Statement` or `## Decision Outcome`; outcome without lead prose; `## Pros and Cons` present with zero options; `### Option 1` without `: title`; `## Updates` present with zero entries; update entry without lead paragraph; **misordering** (`## Updates` before `## More Information`, `## Related Artifacts` after `## Pros and Cons`, `### Consequences`/`### Confirmation` outside `## Decision Outcome`); the old ADR heading `## Pros and Cons of the Options` rejected; duplicate H2; non-blank leading content before H1; second H1 — evidence: tests/dec/models/v1/test_parser.py + test_body.py structural matrix, green in final gate.
- [x] ACC-002 (REQ-001): value violations raise `pydantic.ValidationError`: status ∉ 6-set, `type` ≠ `"dec"`, duplicate option number; `Option.number`/`Option.name` computed correctly; `Related Artifacts` sub-lists independently optional; `list_dec` paging clamps per `general.tools._paging` — evidence: tests/dec/models/v1/test_frontmatter.py + test_body.py (closed 6-set, `type` literal, option number/name) and tests/dec/tools/test_list_dec.py (paging clamp), green in final gate.
- [x] ACC-003 (REQ-002): create→get→list→update→set_status→validate round-trip against a temp `SPECMGR_DOCS_DIR`; `create_dec` fixes `status="draft"` and writes `dec-{id}-{slug}.md`; `update_dec` bumps only `updated` and preserves id/type/status/created/version; `set_status_dec` rejects out-of-set values; `delete_dec` raises `NotImplementedError`; `validate_dec` body-only/full semantics match `validate_gol` — evidence: tests/dec/tools/ (per-tool modules + test_integration.py create→get→list→update→set_status→validate round-trip on a temp SPECMGR_DOCS_DIR), green in final gate.
- [x] ACC-004 (REQ-003/005): `specmgr://dec/schema` equals fresh `generate_dec_schema()` output; example/template resources equal the packaged files byte-for-byte — evidence: tests/dec/resources/ (test_dec_schema.py vs fresh generate_dec_schema(); example/template byte-for-byte); docs/dec_schema.json cmp-identical to the packaged copy.
- [x] ACC-005 (REQ-004): both prompts return instruction text with `$topic`/`$id`/`$instructions` substituted from packaged data — evidence: tests/dec/prompts/ (both prompts substitute $topic/$id/$instructions from packaged data), green in final gate.
- [x] ACC-006 (REQ-006): after wiring, `specmgr docs`, `specmgr mcp-docs`, and `specmgr schema` are all idempotent (zero drift on a second run); `docs/dec_schema.json` and `src/biz/dfch/specmgr/dec/data/dec_schema.json` present and identical — evidence: second-run `specmgr mcp-docs`/`docs`/`schema` all report no changes (393-file docs tree byte-identical); both dec_schema.json copies cmp-identical.
- [x] ACC-007 (REQ-007): full unittest suite green; ruff format/check and vulture clean — evidence: full suite `Ran 2017 tests ... OK`; ruff format (1222 files)/check and vulture clean; `specmgr unused-code` clean.

### Scope

Included:

- `dec/` domain package (models, tools, resources, prompts, data) built on the existing `models/md` engine
- The 8 H2 sections + H1 + H3 sub-structure as in the Design Notes below
- Cross-cutting registration (server.py, schema command, pyproject, pre-commit, CI, AGENTS.md, root README.md, generated docs)
- Tests mirroring `tests/gol/`

Explicitly out of scope:

- No fine-grained mutation tools (`update_section`, `option_*`, `update_frontmatter`) — whole-body `update_dec` only
- No `render_dec` / deterministic re-render (raw-body persistence like GOL/RSK/QA)
- No `specmgr://dec/{id}` resource, no `specmgr://dec/list` resource
- No ADR frontmatter keys (`decision-makers`, `consulted`, `informed`, `date`), no `superseded by {ref}` status form
- No changes to the ADR domain or to the `models/md` engine (the engine already supports everything needed — if it does not, stop and report rather than patching the engine)

### Dependencies

- Depends on: `models/md` engine (feat-5, done), generic `_doc_paths`/`_packaged_data`/`_paging` in `general/tools/` (done)
- Blocks: nothing known

### Design Notes

**Document structure** (section order is binding — field declaration order = markdown order):

```markdown
---
id: <uuid>            # specmgr-assigned
type: dec             # Literal["dec"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft         # closed 6-set
version: 1.0.0
---

# {Free-form title}                          H1, @alias REGEX ".+"
## Context and Problem Statement             REQUIRED  (LITERAL alias, leaf)
## Decision Drivers                          OPTIONAL  (leaf)
## Considered Options                        OPTIONAL  (leaf)
## Decision Outcome                          REQUIRED  (composite)
    {mandatory lead prose}
  ### Consequences                           OPTIONAL  (leaf H3)
  ### Confirmation                           OPTIONAL  (leaf H3)
## Related Artifacts                         OPTIONAL  (composite, GOL shape)
  ### Requirements / ### Decisions /
  ### Goals / ### Acceptance Criteria        OPTIONAL  (bullet lists, >=1 if present)
## Pros and Cons                             OPTIONAL  (LITERAL alias, iff >=1 option)
  ### Option 1: {name}
  ### Option 2: {name}
## More Information                          OPTIONAL  (leaf)
## Updates                                   OPTIONAL, LAST (TSK shape)
  ### 2026-08-26 — Created
  {entry prose}
```

**Model classes** (all in `dec/models/v1/body.py`, one `MarkdownSection2`/`MarkdownSection3` subclass per heading; implicit SPACE_SEPARATED aliases unless noted):

- `Decision(MarkdownSection1)` — `@alias(value=".+", type=AliasType.REGEX)`; fields in order: `context`, `drivers | None`, `considered | None`, `outcome`, `related_artifacts | None`, `pros_and_cons | None`, `more_information | None`, `updates | None`; plus `model_validator(mode="after")` rejecting duplicate option numbers (raise `ValueError` → pydantic channel; only inspects `self.pros_and_cons` when not None)
- `Context(MarkdownSection2)` — `@alias(value="Context and Problem Statement", type=AliasType.LITERAL)`; leaf
- `DecisionDrivers`, `ConsideredOptions`, `MoreInformation` — leaves, implicit aliases
- `DecisionOutcome(MarkdownSection2)` — composite: `statement: MarkdownParagraph` (required; a bare list with no lead paragraph must be rejected), `consequences: Consequences | None`, `confirmation: Confirmation | None` (both leaf H3s)
- `RelatedArtifacts(MarkdownSection2)` + `Requirements`/`Decisions`/`Goals`/`AcceptanceCriteria(MarkdownSection3)` — **copy GOL's shape verbatim** (gol/models/v1/body.py:119-181): each child `items: list[MarkdownListItem] = Field(min_length=1)`, all four children optional on the container; adapt docstrings to DEC
- `ProsAndCons(MarkdownSection2)` — `@alias(value="Pros and Cons", type=AliasType.LITERAL)`; `options: list[Option] = Field(min_length=1)` (H2 present with zero options → structural error)
- `Option(MarkdownSection3)` — `@alias(value=r"^Option \d+: .+$", type=AliasType.REGEX)`; leaf; computed fields `number: int` and `name: str` extracted from the heading line of `self.text` (RSK `Probability.value` precedent, rsk/models/v1/assessment.py; extraction regex `^### Option (\d+): (.+)$`, `re.fullmatch`); leading zeros accepted, gaps allowed
- `Updates(MarkdownSection2)` — implicit alias "Updates"; `updates: list[UpdateEntry] = Field(min_length=1)`
- `UpdateEntry(MarkdownSection3)` — `@alias(value=".+", type=AliasType.REGEX)`; `content: MarkdownParagraph` (required); **copy TSK's shape verbatim** (tsk/models/v1/body.py:58-103); date-led entry titles are convention, not enforced

**Frontmatter**: `DecFrontmatter(MarkdownFrontmatter)` — `type: Literal["dec"] = "dec"`; closed status set `frozenset({"draft", "proposed", "accepted", "rejected", "deprecated", "superseded"})` with GOL's error-message pattern; default `"draft"` inherited (no RSK-style redeclaration needed since `"draft"` is in the set).

**Document/parser/summary**: `DecDocument(BaseModel)` (`frontmatter: DecFrontmatter`, `body: Decision`); `parse_dec(text)` is the 4-line glue (`frontmatter.loads` → `_stringify_metadata` → `Decision.from_text(format_text(post.content))`) exactly like `parse_gol`; `DecSummary(DocSummary)` plain (id/title/status/ref, no extras).

**Error channels** (codebase convention, no new exception types): structural → engine `AssertionError`; value → `pydantic.ValidationError`.

**Tools** (one module per tool, mirror `gol/tools/`): `create_dec` (fresh `uuid4`, `status="draft"` always, created/updated=now, `version=CURRENT_SCHEMA_VERSION`, filename `dec-{id}-{slugify(body.text)}.md`); `update_dec` (whole-body replace under `dec_lock(id)`, only `updated` bumped); `set_status_dec(id, status)` (closed set, raw body re-persisted verbatim); `parse_dec(path)`; `list_dec(max_results?, offset?)` (paged, inline `DecSummary`, skip-on-parse-failure); `get_dec(id)`; `get_dec_example()`/`get_dec_template()` (`read_packaged_text`); `delete_dec(id)` stub (`NotImplementedError`, `structured_output=False`); `validate_dec(content, full=False)`. Private helpers `_paths.py` (over `general.tools._doc_paths`, `DEC_TYPE_NAME = "dec"`, `DecNotFoundError`), `_io.py`, `_lock.py`, `_write.py` — identical shape to GOL's.

**Resources**: `specmgr://dec/schema` (JSON from packaged `dec/data/dec_schema.json`), `specmgr://dec/example`, `specmgr://dec/template` — identical to GOL's three; no `/{id}`, no `/list`.

**Prompts**: `create_dec(topic)` and `update_dec(id, instructions=None)` reading packaged `dec/data/dec_{create,update}_instructions.md` via `string.Template` (standard "(not given — ask the user before making any change)" fallback for `instructions`); mirror GOL/RSK.

**Packaged data**: `dec_example.md` — a **non-architectural** worked decision exercising every section (both outcome H3s, `## Related Artifacts` with ≥2 sub-lists, `## Pros and Cons` with 2 options, `## More Information`, 2 `## Updates` entries); must parse. `dec_template.md` — all-sections placeholder skeleton, `status: draft`, **must round-trip through `parse_dec`** (RSK precedent, stronger than GOL's).

**Cross-cutting wiring**:

- `server.py`: add `dec` to the final import line (`from . import adr, dec, general, gol, prb, qa, req, rsk, tsk, uc`) + module docstring (3 resources, 10 tools, 2 prompts, domain summary)
- `commands/schema.py`: `generate_dec_schema()` (mirror `generate_gol_schema`) + `_GENERATORS["dec"]`
- `pyproject.toml`: `"biz.dfch.specmgr.dec" = ["data/*.md", "data/*.json"]` under `[tool.setuptools.package-data]`
- `.pre-commit-config.yaml`: add `dec/models/v1` to the 8 existing `files:` globs (`specmgr-schema` + the 7 per-domain `specmgr-schema-*-package` hooks) + new `specmgr-schema-dec-package` hook (`--type dec --output-dir src/biz/dfch/specmgr/dec/data`)
- `.github/workflows/ci.yml`: one new step "Make sure `src/biz/dfch/specmgr/dec/data/dec_schema.json` is correct" mirroring the per-type packaged-copy steps (the all-types `docs/*_schema.json` step picks `dec` up automatically once registered in `_GENERATORS`)
- `AGENTS.md`: `dec/` bullet in the Status section (after `rsk/`); add `dec` to the "each register `tools`, `resources`, and `prompts`" enumeration and to the `delete_*` stub list; verify no other enumeration goes stale
- Root `README.md`: add `Decision (DEC)` to the "At this time, we have these artifact:" list (lines ~19-29), matching the existing entry style
- Regenerate: `docs/MCP.md` (`specmgr mcp-docs`), `docs/GENERATED.md` + `docs/api/` (`specmgr docs`), `docs/dec_schema.json` (`specmgr schema`)

**Precedents to copy** (do not re-derive): GOL = simple surface + `RelatedArtifacts` shape + frontmatter status pattern; TSK = `RecentUpdates`/`UpdateEntry` shape; RSK = computed fields from regex headings + template-must-round-trip guarantee.

**Commit discipline (binding for every phase)**: each phase ends with one commit (conventional-commit style, scope `dec`, e.g. `feat(dec): add models and parser`) and the short commit hash is added as a comment to GitHub issue #21 (`gh issue comment 21 --repo dfch/biz.dfch.SpecMgr --body "..."`). Include any hook-regenerated `docs/` files in the same commit (the `specmgr docs`/`mcp-docs` pre-commit hooks trigger on `src/` changes and regenerate `docs/GENERATED.md`+`docs/api/` by filesystem scan — from Phase 1 on, `dec` modules will appear there before `server.py` registers the domain; that is expected and correct).

### Related ADRs

- 832cd6c1-ef8a-4bfc-990e-a610823f61ae: Generic heading-mapped Markdown-to-Pydantic parsing (the `models/md` engine)
- bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model (`MarkdownFrontmatter`)
- ddfb1109-422d-4507-8dbc-dc5e4bec9614: No `/{id}` resources for id-based reads (tool-only)
- ec9f5262-9912-49d0-903f-fcfb54f28c13: Paged `list_*` tools instead of `/list` resources

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 0: Scaffolding
- [x] Task 0.1: Package skeleton — `dec/__init__.py` (`from . import prompts, resources, tools` + registration docstring), empty `dec/models/v1/`, `dec/tools/`, `dec/resources/`, `dec/prompts/`, `dec/data/` packages, and `tests/dec/` skeleton mirroring `tests/gol/` (`models/v1/`, `tools/`, `prompts/`, `resources/` + `__init__.py` files) — depends on: none — status: completed (2026-08-27)
- [x] Task 0.2: Commit Phase 0 + comment the commit hash on issue #21 — depends on: Task 0.1 — status: completed (2026-08-27, commit f1c7728, issue #21 comment posted by orchestrator)

#### Phase 1: Models + parser (`dec/models/v1/`)
- [x] Task 1.1: `_util.py` (`SCHEMA_COMMENT_VERSION = "v1"`) — depends on: Task 0.1 — status: completed (2026-08-27)
- [x] Task 1.2: `frontmatter.py` — `DecFrontmatter(MarkdownFrontmatter)`: `type: Literal["dec"] = "dec"`, closed 6-set status validator (GOL error-message pattern) — depends on: Task 1.1 — status: completed (2026-08-27)
- [x] Task 1.3: `body.py` — all section classes per Design Notes: `Decision` (root + duplicate-option-number after-validator), `Context` (LITERAL), `DecisionDrivers`, `ConsideredOptions`, `MoreInformation` (leaves), `DecisionOutcome` + `Consequences` + `Confirmation` (composite), `RelatedArtifacts` + 4 H3 list children (GOL shape), `ProsAndCons` (LITERAL "Pros and Cons") + `Option` (REGEX `^Option \d+: .+$`, computed `number`/`name`), `Updates` + `UpdateEntry` (TSK shape) — depends on: Task 1.2 — status: completed (2026-08-27)
- [x] Task 1.4: `document.py` (`DecDocument`), `parser.py` (`parse_dec` glue + `_stringify_metadata`), `summary.py` (`DecSummary`), `models/v1/__init__.py` + `models/__init__.py` exports — depends on: Task 1.3 — status: completed (2026-08-27)
- [x] Task 1.5: Tests `tests/dec/models/v1/` — `test_frontmatter.py`, `test_body.py` (alias acceptance/rejection, option regex incl. leading-zero acceptance + title-required rejection, number uniqueness, composite outcome, container-with-zero-options, Related Artifacts sub-list independence, Updates entry shape, misordering), `test_parser.py` (ACC-001/ACC-002 matrix + round-trip) — depends on: Task 1.4 — status: completed (2026-08-27)
- [x] Task 1.6: Phase-end quality gate (ruff format/check, vulture, full unittest) + commit + comment the commit hash on issue #21 — depends on: Task 1.5 — status: completed (2026-08-27, commit b889e4a, issue #21 comment posted by orchestrator)

#### Phase 2: Tools (`dec/tools/`)
- [x] Task 2.1: Private helpers `_paths.py` (`DEC_TYPE_NAME="dec"`, `DecNotFoundError`, wrappers over `general.tools._doc_paths`), `_io.py` (`read_dec`, `load_by_id`), `_lock.py` (`dec_lock`), `_write.py` (`write_dec_file`) — mirror GOL — depends on: Task 1.6 — status: completed (2026-08-27)
- [x] Task 2.2: The 10 tool modules + `tools/__init__.py` per Design Notes (`create_dec` fixes `status="draft"`, filename `dec-{id}-{slug}.md`; `delete_dec` stub `structured_output=False`) — depends on: Task 2.1 — status: completed (2026-08-27)
- [x] Task 2.3: Tests `tests/dec/tools/` — one module per tool + helper tests + `test_integration.py` (ACC-003) — depends on: Task 2.2 — status: completed (2026-08-27)
- [x] Task 2.4: Phase-end quality gate + commit + comment the commit hash on issue #21 — depends on: Task 2.3 — status: completed (2026-08-27, commit ff277a9, issue #21 comment posted by orchestrator)

#### Phase 3: Resources + packaged data + schema
- [x] Task 3.1: `dec/data/dec_example.md` — non-architectural worked decision exercising every section (Design Notes); must parse — depends on: Task 2.4 — status: completed (2026-08-27)
- [x] Task 3.2: `dec/data/dec_template.md` — all-sections placeholder skeleton, `status: draft`; must round-trip through `parse_dec` — depends on: Task 2.4 — status: completed (2026-08-27)
- [x] Task 3.3: `dec/data/dec_create_instructions.md` + `dec_update_instructions.md` (narrated flows, `$topic`/`$id`/`$instructions` placeholders) — depends on: Task 2.4 — status: completed (2026-08-27)
- [x] Task 3.4: `dec/resources/` — `dec_schema.py` (`specmgr://dec/schema`, JSON from packaged copy), `dec_example.py`, `dec_template.py`, `__init__.py` — depends on: Task 3.5 — status: completed (2026-08-27)
- [x] Task 3.5: `commands/schema.py` — `generate_dec_schema()` + `_GENERATORS["dec"]` (mirror `generate_gol_schema`); run `specmgr schema --type dec` (writes `docs/dec_schema.json`) and `specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data` (packaged copy) — depends on: Task 1.6 — status: completed (2026-08-27)
- [x] Task 3.6: Tests `tests/dec/resources/` (ACC-004) — depends on: Task 3.4 — status: completed (2026-08-27)
- [x] Task 3.7: Phase-end quality gate + commit + comment the commit hash on issue #21 — depends on: Task 3.6 — status: completed (2026-08-27, commit f8ba8b4, issue #21 comment posted by orchestrator)

#### Phase 4: Prompts
- [x] Task 4.1: `dec/prompts/` — `create_dec.py` (`create_dec(topic)`), `update_dec.py` (`update_dec(id, instructions=None)` with standard fallback), `__init__.py` — depends on: Task 3.3 — status: completed (2026-08-27)
- [x] Task 4.2: Tests `tests/dec/prompts/` (ACC-005) — depends on: Task 4.1 — status: completed (2026-08-27)
- [x] Task 4.3: Phase-end quality gate + commit + comment the commit hash on issue #21 — depends on: Task 4.2 — status: completed (2026-08-27, commit 754102c, issue #21 comment posted by orchestrator)

#### Phase 5: Cross-cutting registration
- [x] Task 5.1: `server.py` — add `dec` to the final import line (`adr, dec, general, gol, prb, qa, req, rsk, tsk, uc`) + module docstring (3 resources, 10 tools, 2 prompts, domain summary) — depends on: Task 4.3 — status: completed (2026-08-27)
- [x] Task 5.2: `pyproject.toml` — `"biz.dfch.specmgr.dec" = ["data/*.md", "data/*.json"]` package-data entry — depends on: Task 3.7 — status: completed (2026-08-27)
- [x] Task 5.3: `.pre-commit-config.yaml` — add `dec/models/v1` to the 8 existing `files:` globs + new `specmgr-schema-dec-package` hook — depends on: Task 3.5 — status: completed (2026-08-27)
- [x] Task 5.4: `.github/workflows/ci.yml` — new packaged-copy drift step for `dec/data/dec_schema.json` (all-types `docs/*_schema.json` step needs no change) — depends on: Task 3.5 — status: completed (2026-08-27)
- [x] Task 5.5: `AGENTS.md` — `dec/` bullet in Status (after `rsk/`); `dec` added to the tools/resources/prompts enumeration and the `delete_*` stub list; verify no other enumeration goes stale — depends on: Task 5.1 — status: completed (2026-08-27)
- [x] Task 5.6: Root `README.md` — add `Decision (DEC)` to the "At this time, we have these artifact:" list (lines ~19-29), matching the existing entry style — depends on: Task 5.1 — status: completed (2026-08-27)
- [x] Task 5.7: Regenerate `docs/MCP.md` (`specmgr mcp-docs`), `docs/GENERATED.md` + `docs/api/` (`specmgr docs`); verify all idempotent on a second run (ACC-006) — depends on: Task 5.1, 5.2 — status: completed (2026-08-27)
- [x] Task 5.8: Final quality gate (ruff format/check, vulture, full unittest, `specmgr unused-code`) + commit + comment the commit hash on issue #21 — depends on: Task 5.7 — status: completed (2026-08-27, final gate green; commit + issue #21 comment performed by orchestrator)
- [x] Task 5.9: Update this README's Progress (all tasks checked with dates, Current Status, Recent Updates, Related PRs/Commits) — depends on: Task 5.8 — status: completed (2026-08-27)

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-27**: Feature complete — all six phases (0–5) done, all seven
acceptance criteria verified PASS (see annotated Acceptance Criteria above), full
quality gate green (2017 tests, ruff format/check clean, vulture clean,
`specmgr unused-code` clean), `dec` registered in server.py (94 tools / 28
resources / 21 prompts live on the real `mcp` instance, of which 10 tools / 3
resources / 2 prompts are dec's — confirmed via `mcp.list_tools()/
list_resources()/list_prompts()` and matching docs/MCP.md's header line), docs
idempotent (ACC-006). GitHub issue #21 carries one comment per phase commit
(f1c7728, b889e4a, ff277a9, f8ba8b4, 754102c, and this phase's commit); ready
for review/merge, issue to be closed when the PR merges.

### Recent Updates

#### Update 2026-08-27 (post-merge note — tool-surface conversion by feat-22)

- This feature shipped on `dev` (v0.12.0) with per-domain `update_dec` /
  `set_status_dec` tools and a `get_dec` without `raw`. feat-22
  (consolidate mutation tools, ADR 36905d5b-8057-4294-8665-c7eed5534db0)
  merged `dev` into its branch and converted the DEC domain to the
  generic `update` / `set_status` tools (`type="dec"`) plus
  `get_dec(raw=True)`, retiring the two per-domain tools — see
  `.specmgr/feat/feat-22-consolidate-mutation-tools/README.md` Phase 8.
  The task lines above remain the historical record of this feature's
  own scope, which completed as planned at the time.

#### Update 2026-08-27 (Phase 5: Cross-cutting registration — feature complete)

- Completed Tasks 5.1–5.9, the final phase of the feature.
  - Task 5.1: `server.py` — `dec` added to the final import line
    (`adr, dec, general, gol, prb, qa, req, rsk, tsk, uc`) and to the module
    docstring (3 resources, 10 tools, 2 prompts, the no-`/{id}`/no-`/list`
    paragraph, and all three closing domain enumerations).
  - Task 5.2: `pyproject.toml` — `"biz.dfch.specmgr.dec" = ["data/*.md",
    "data/*.json"]` package-data entry (alphabetical slot after `adr`, before
    `gol`; the cross-cutting `general` entry stays last).
  - Task 5.3: `.pre-commit-config.yaml` — `dec/models/v1` added as the first
    alternative in all 8 schema-hook `files:` globs, new
    `specmgr-schema-dec-package` hook appended after the gol hook (mirrors it
    exactly), and `dec` added to the `specmgr-schema` hook description's
    registered-type list.
  - Task 5.4: `.github/workflows/ci.yml` — new packaged-copy drift step for
    `src/biz/dfch/specmgr/dec/data/dec_schema.json` (mirrors the gol step,
    `--python 3.13.13`); the all-types step picked `dec` up automatically via
    `_GENERATORS`, only its type-list comment gained `dec`.
  - Task 5.5: `AGENTS.md` — new `dec/` (Decision) bullet after `rsk/`; `dec`
    added to the "each register `tools`/`resources`/`prompts`" enumeration,
    the `delete_*` stub list, the `validate_*` not-yet-enforced parenthetical,
    and the `server.py` section's domain-package list.
  - Task 5.6: root `README.md` — `Decision (DEC)` added to the "At this time,
    we have these artifact:" list (alphabetical slot after ADR) and removed
    from the commented future list, per the feat-18 precedent.
  - Task 5.7: regenerated `docs/MCP.md` / `docs/api/` + `docs/GENERATED.md` /
    all `docs/*_schema.json`; `specmgr schema` reported all 8 types
    "(unchanged)" and only `docs/api/biz.dfch.specmgr.server.md` changed
    (docstring mirror); the second run of all three generators left the
    393-file docs tree byte-identical (ACC-006); `docs/dec_schema.json`
    cmp-identical to the packaged copy.
  - Task 5.8: final quality gate green — ruff format (1222 files) / ruff
    check / vulture (no new whitelist entries) / full unittest (**2017
    tests, OK**) / `specmgr unused-code` (no unused code). Live registration
    on the real `mcp` instance: 94 tools / 28 resources / 21 prompts, dec
    contributing 10/3/2. Commit + issue #21 comment performed by the
    orchestrator after verification.
  - Task 5.9: this Progress sweep — frontmatter `status: done`, all seven
    ACCs annotated with evidence, all task lines checked with dates.
- Next: feature complete — ready for review/merge; issue #21 to be closed
  when the PR merges.
- Notes: `docs/MCP.md` already carried the full dec registration since
  Phase 3 (the CLI imports `commands/schema.py`, whose module-level
  `dec.models.v1` import runs `dec/__init__.py` and registers dec on the
  shared `mcp` instance, so `specmgr mcp-docs` saw the dec entries before
  `server.py` listed the domain); Phase 5's regeneration confirms the file is
  byte-identical to what the now-registered `server.py` produces, and the
  header counts match the live introspection.

#### Update 2026-08-26 (handover)
- Completed: Structure walkthrough with user; all open decisions resolved (frontmatter, status set, option regex, uniqueness, outcome composite, Considered Options optionality, plus the three user adjustments: `## Pros and Cons` rename, `## Updates` last section in TSK shape, `## Related Artifacts` after Decision Outcome in GOL shape). Issue #21 created. Plan written here with per-phase commit+issue-comment tasks and the final-phase root-README.md task.
- Next: Phase orchestrator executes Phase 0 through Phase 5 in order; each phase ends with its quality gate, one commit, and an issue comment carrying the commit hash.
- Notes: Precedent modules to copy, not re-derive: `gol/` (surface + Related Artifacts), `tsk/models/v1/body.py:58-103` (Updates/UpdateEntry), `rsk/models/v1/assessment.py` (computed fields from regex headings). Do not modify `models/md` or the ADR domain.

### Decisions Made

- **2026-08-26**: Built on the generic `models/md` parser (not the ADR-specific `models/adr/v1` stack), with the GOL/RSK/QA simple surface — user requirement; no fine-grained ADR mutation tools for DEC.
- **2026-08-26**: Pure generic frontmatter (`id`/`type`/`created`/`updated`/`status`/`version`) — no ADR people keys or `date` (user chose "pure generic").
- **2026-08-26**: Closed 6-set status `draft`/`proposed`/`accepted`/`rejected`/`deprecated`/`superseded`, default `draft`, no `superseded by {ref}` form (user chose "closed 6-set only") — `set_status_dec` stays 2-arg.
- **2026-08-26**: Option heading regex `^Option \d+: .+$` — title required, leading zeros accepted (user choice); unique option numbers enforced via `Decision` after-validator → `ValidationError` channel (RSK-TARA precedent); gaps allowed, never renumbered.
- **2026-08-26**: `## Decision Outcome` composite — mandatory lead paragraph + optional `### Consequences`/`### Confirmation` (user chose "keep H3s").
- **2026-08-26**: `## Considered Options` optional, not mandatory (user chose optional — the `### Option N` sections carry the content).
- **2026-08-26** (user adjustment 1): Options container heading is `## Pros and Cons` (LITERAL alias), not ADR's `## Pros and Cons of the Options`; derived-presence semantics unchanged (H2 present only iff ≥1 option).
- **2026-08-26** (user adjustment 2): Optional `## Updates` section at the very end, TSK `RecentUpdates`/`UpdateEntry` shape (user chose TSK-style entries over a free-form leaf): `### {free-form title}` + mandatory lead paragraph, ≥1 entry if present.
- **2026-08-26** (user adjustment 3): Optional `## Related Artifacts` positioned after `## Considered Options` + `## Decision Outcome` (before `## Pros and Cons`), GOL shape copied verbatim (four all-optional H3 bullet lists). Position confirmed sensible: cross-references follow the outcome while the decision is in mind; Pros and Cons remain the trailing justification appendix.
- **2026-08-26**: Each implementation phase ends with one commit and a comment on issue #21 carrying the commit hash (user requirement).
- **2026-08-26**: Final-phase task adds `Decision (DEC)` to the root `README.md` artifact list (user requirement).

### Related PRs / Commits

- [Issue #21](https://github.com/dfch/biz.dfch.SpecMgr/issues/21): Create artifact type "Decision" (DEC)
- `f1c7728` feat(dec): add package and test scaffolding
- `b889e4a` feat(dec): add models and parser
- `ff277a9` feat(dec): add MCP tools
- `f8ba8b4` feat(dec): add packaged data, resources, and schema
- `754102c` feat(dec): add create/update prompts
- Phase 5 (Cross-cutting registration) — this commit; short hash recorded in the issue #21 comment
