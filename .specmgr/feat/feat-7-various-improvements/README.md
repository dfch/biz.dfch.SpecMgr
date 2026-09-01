---
created: 2026-08-15
id: feat-7-various-improvements
status: planning
updated: 2026-09-01
version: 1.0.0
---

# Feature: Various cross-cutting improvements

## Plan

### Overview

A rolling bucket for small, cross-cutting improvements that touch more than
one document domain (`adr`/`req`/`uc`/`general`) but are each too small to
justify their own `feat-NNN-slug` folder. Sections/tasks are added here as
new concerns come up; a concern gets split into its own feature folder if
it grows large enough to need dedicated requirements/acceptance criteria of
its own (see Design Notes).

The first tracked concern: standardizing the output format/contract of the
MCP `specmgr://*/list` resources (`adr_list`, `req_list`, and any future
`uc_list`/`ac_list`), and reviewing/optimizing the MCP `@mcp.prompt()`
modules (`adr/prompts/`, `req/prompts/`) for consistency and token
efficiency, including deciding the fate of the step-gated `_test` prompt
variants (`adr/prompts/create_adr_test.py`, `update_adr_test.py`) that
currently exist alongside the narrated originals for A/B comparison.

### Requirements

- REQ-001: All `specmgr://*/list` resources (`adr_list`, `req_list`, and
  future `uc_list`/`ac_list`) share a consistent, documented output
  contract (fields, sort order, skip-on-parse-failure semantics).
- REQ-002: A decision is made on whether/how list resources should support
  pagination or size limits as the number of documents in a base directory
  grows (both `adr_list` and `req_list` currently do a full, unbounded
  directory scan on every call).
- REQ-003: Every existing MCP prompt module (`create_adr`, `update_adr`,
  `create_adr_test`, `update_adr_test`, `create_req`, `update_req`) is
  reviewed against a documented set of prompt-quality criteria (length,
  redundancy, step-gating, clarity of the tool-call sequence it drives).
- REQ-004: A decision is recorded on the fate of the step-gated `_test`
  prompt variants — keep both narrated and step-gated variants long-term,
  consolidate into one style, or retire one — applied consistently across
  the `adr` and (if adopted) `req` domains.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 — `adr_list`/`req_list` (and any future
  `*_list` resource) share a common base summary shape/contract, checked
  by a shared test or an explicit side-by-side comparison. **Partially
  advanced by `feat-13-list-paging`** (2026-08-19): 4 of 5 domains
  (`ReqSummary`/`UcSummary`/`TskSummary`/`QaSummary`) now literally
  subclass the shared `general.models.DocSummary` base; `AdrSummary`
  shares the identical field set structurally but deliberately does
  **not** subclass it (dependency-graph reason: `models/adr` must stay
  free of the `mcp` extra — see feat-13's Decisions Made log and ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13), with equivalence enforced by a
  structural test instead of inheritance. Not marking this `[x]` yet since
  the contract is shared by convention/test, not uniformly by class
  hierarchy, across all five domains.
- [x] ACC-002: Verifies REQ-002 — a decision (ADR or an entry in this
  file's Decisions Made log, per the ADR-vs-feature-log tie-breaker in ADR
  e369ee2e) is recorded on list-resource pagination, with rationale even
  if the decision is "defer." **Done**: recorded in ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13 ("Expose `<domain>_list` as paged
  MCP tools (`list_<domain>`), not resources"), implemented in full by
  `feat-13-list-paging`.
- [ ] ACC-003: Verifies REQ-003 — each prompt module has a recorded
  review outcome (kept as-is / changed / retired) against the documented
  criteria.
- [ ] ACC-004: Verifies REQ-004 — an explicit decision on the `_test`
  variants is recorded and, if it implies code changes, those changes are
  made consistently in both domains that have prompts.

### Scope

**Included in this feature:**

- The output shape/contract of `specmgr://adr/list` and `specmgr://req/list`
- Design guidance for future `*_list` resources (`uc`, `ac`, ...)
- Review and optimization of existing `adr/prompts/` and `req/prompts/`
  modules
- The decision on keeping/consolidating/retiring the `_test` prompt
  variants

**Explicitly out of scope:**

- Net-new domains or document types (tracked separately, e.g. `uc`
  currently has no `prompts`/`resources` sub-package yet — adding one is
  its own feature, not this one)
- Other cross-cutting concerns not yet described (logging, error-handling
  conventions, config management, etc.) — these get their own section/task
  list added to this same file when they come up, or are split into a
  dedicated `feat-NNN-slug` folder if they turn out to be large

### Dependencies

- Depends on: ADR e369ee2e-3353-4f92-991c-6367d76d832e (`.specmgr`
  feature-folder structure), ADR ece4554b-725c-4f76-bc04-5d2b760363d2
  (domain-first hierarchy)
- Blocks: None identified yet

### Design Notes

- `adr_list` (`adr/resources/adr_list.py`) and `req_list`
  (`req/resources/req_list.py`) already follow the same general shape
  (id/title/status/filename, filename-sorted, skip-on-parse-failure) but
  catch different exception tuples per domain parser
  (`(AdrParseError, ValidationError)` vs. `(AssertionError, ValidationError)`) — worth confirming this divergence is intentional
  (domain-specific parser errors) rather than accidental drift.
- Neither list resource paginates; both differ from this project's own
  `asdste100` MCP tools (e.g. `word_list`, `rules_examples`), which
  already use a `max_results`/`offset` pattern — that pattern is a
  candidate model to reuse here rather than inventing a new one.
- `adr/prompts/create_adr_test.py`/`update_adr_test.py` are explicitly
  documented (AGENTS.md) as experimental, step-gated (`GATE 0`..`GATE N`)
  variants registered under distinct prompt names for side-by-side
  comparison against the narrated originals — this feature is where that
  comparison's outcome should get decided and recorded.

### Related ADRs

- e369ee2e-3353-4f92-991c-6367d76d832e: Organize development artifacts in
  `.specmgr` with feature-driven work units
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
  document-type domain (domain-first hierarchy)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself — there is no separate "planned" vs. "executed" list to keep in
sync; a task's line *is* its current status. Update it in place as work
progresses (edit, don't duplicate).

#### Phase 0: Housekeeping

- [x] Task 0.1: Create GitHub issue #7 for this feature and rename
  `feat-0-various-improvements` → `feat-7-various-improvements`, updating
  the frontmatter `id` to match — depends on: none — status: done
  (2026-08-15)

* [x] Task 0.2: Create and immediately close GitHub issue #8
  (`feat-0-coverage-badge`, already-completed feature) and rename the
  folder → `feat-8-coverage-badge`, updating the frontmatter `id` to match
  — depends on: none — status: done (2026-08-15)

- [x] Task 0.3: Create and immediately close GitHub issue #9
  (`feat-0-doc-in-specmgr`) and rename the folder →
  `feat-9-doc-in-specmgr`, updating the frontmatter `id` to match —
  depends on: none — status: done (2026-08-15)

- [x] Task 0.4: Fix all ~20 live cross-references to the old
  `feat-0-doc-in-specmgr` path across `AGENTS.md`, source docstrings
  (`server.py`, `adr/prompts/*.py`, `models/adr/__init__.py`,
  `models/adr/v1/__init__.py`, `uc/models/v1/use_case.py`), tests
  (`tests/adr/prompts/test_*.py`), and other feature docs
  (`feat-4-use-cases/README.md`, `v1/uc-schema.md`, `v1/eval-uc.md`) —
  deliberately left one reference untouched in an archived session
  transcript (`feat-9-doc-in-specmgr/history/session-ses_038f-adr-tool-plan.md`)
  since historical logs are point-in-time records, not live docs — depends
  on: Task 0.3 — status: done (2026-08-15)

- [x] Task 0.5: Regenerate `docs/api/` and `docs/GENERATED.md` via
  `uv run --frozen specmgr docs` (Python 3.13) to pick up the renamed
  path, then verify with `ruff format --check`, `ruff check`, and the full
  `unittest` suite (771 tests, all passing) — depends on: Task 0.4 —
  status: done (2026-08-15)

- [ ] Task 0.6: Review whether repeatedly referencing
  `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` (and its section
  numbers) inline in source docstrings (`server.py`, `adr/prompts/*.py`,
  `models/adr/__init__.py`, `models/adr/v1/__init__.py`,
  `uc/models/v1/use_case.py`) is genuinely useful or just redundant bloat
  that also creates a maintenance liability (as Task 0.4 just showed —
  ~20 references had to be fixed for a single folder rename). Decide a
  tighter convention (e.g. reference the plan once per module/file at
  most, or drop path+section references from docstrings entirely in
  favor of the plan file itself being the single source of truth) and
  apply it — depends on: Task 0.4 — status: not-started

- [ ] Task 0.7: Update ADR 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO
  8601 for all dates and times") to require timezone information on every
  timestamp — either an explicit offset (`±HHMM`) or `Z` for UTC — rather
  than treating it as optional, if this is not already stated; the current
  "Standard Format (Non-Filename Contexts)" section only shows `±HHMM` as
  an example under "With timezone" without mandating it — depends on: none
  — status: not-started

- [x] Task 0.8: Create a new `general` MCP resource that returns the main
  characteristics of ISO/IEC 25010:2023 (system/software quality model). Use this as input: `.specmgr/feat/feat-7-various-improvements/product-quality-model.md`. Name of resource: `iso25010`. Location: `src/general/resources`.
  with a description for each — depends on: none — status: done (2026-08-16,
  all 9 sub-tasks 0.8.1 through 0.8.9 complete)

  - [x] Task 0.8.1: Rewrite `product-quality-model.md`'s content into a new
    packaged data file, `general/data/general_iso25010.md` — drop each
    characteristic heading's leading `N. ` numbering (e.g. `## Functional Suitability`, not `## 1. Functional Suitability`; list order alone
    conveys the number) and convert every sub-characteristic bullet into
    its own nested `### ` heading directly under its characteristic's `##`
    heading (instead of a bullet list), so the generic `models.md` engine
    can parse names/descriptions as structured headings instead of
    regex-splitting bullet text. Also convert the trailing copyright/fair-use
    sentence into a leading HTML comment (`<!-- ... -->`) rather than a plain
    paragraph, so it maps onto `Iso25010.comment` below. The H1 title and the
    9-item bullet list of characteristic names are kept as-is (not dropped);
    the intro paragraph ("The product quality model consists of 9 main
    characteristics:") that originally sat between the H1 and the bullet
    list was later hand-edited out of `product-quality-model.md` (user
    edit, after this task's first pass), dropping `Iso25010.intro`
    accordingly (see Task 0.8.2) — `product-quality-model.md` itself was
    already hand-edited into this exact shape ahead of this task, so this
    step is a straight copy into the new packaged path plus an `mdformat`
    pass. Add a `"biz.dfch.specmgr.general" = ["data/*.md"]` entry to
    `pyproject.toml`'s `[tool.setuptools.package-data]` (none exists for
    `general` yet) — depends on: none — status: done (2026-08-16)
  - [x] Task 0.8.2: Add `models/iso25010.py` (flat, unversioned — this is
    static reference data, not a user-edited/versioned document type
    like ADR/REQ): `SubCharacteristic(MarkdownSection3)` and
    `Characteristic(MarkdownSection2)`, both
    `@alias(value=".+", type=AliasType.REGEX)` (free-form heading text,
    mirroring `req.models.v1.body.Requirement`'s own H1 precedent) with a
    `description: MarkdownParagraph` field each (plus
    `sub_characteristics: list[SubCharacteristic]` on `Characteristic`,
    `min_length=1`). `Iso25010(MarkdownSection1)` as the H1 container
    (mirroring `req.models.v1.body.Requirement`'s own H1 precedent), with
    fields in document order: `names: list[MarkdownListItem]`
    (`min_length=9, max_length=9` — exactly the 9 characteristic names, no
    lead-in `intro` field: the user hand-edited the source data to drop
    the intro sentence between the H1 and the bullet list), `comment: MarkdownComment | None` (the copyright/fair-use notice), and
    `characteristics: list[Characteristic]` (`min_length=9, max_length=9`
    — exactly the 9 main characteristics); and `parse_iso25010(text) -> Iso25010`, a thin `format_text` + `Iso25010.from_text` wrapper (no
    frontmatter to split off, unlike `parse_adr`/`parse_req`). Re-export
    `Iso25010`, `Characteristic`, `SubCharacteristic`, `parse_iso25010`
    from `models/__init__.py` — depends on: Task 0.8.1 — status:
    done (2026-08-16)
  - [x] Task 0.8.3: Add `general/resources/iso25010.py` —
    `@mcp.resource("specmgr://iso25010", name="iso25010", ..., mime_type="application/json")` wrapping
    `parse_iso25010(read_packaged_text("general", "iso25010", "md"))`,
    mirroring `req/resources/req_schema.py`'s packaged-data-read style;
    register in `general/resources/__init__.py` (import + `__all__`) —
    depends on: Task 0.8.2 — status: done (2026-08-16)
  - [x] Task 0.8.4: Update `general/__init__.py`'s and `server.py`'s module
    docstrings to list `specmgr://iso25010`; while in `server.py`, also
    fix its stale "top-level `resources` package" line (pre-existing
    drift left over from Task 0.12's move of `resources/` into
    `general/resources/`) — depends on: Task 0.8.3 — status: done (2026-08-16)
  - [x] Task 0.8.5: Add `tests/models/test_iso25010.py` — parse the
    packaged `general_iso25010.md` end-to-end via `parse_iso25010`,
    asserting 9 characteristics, spot-checking a couple of
    characteristic/sub-characteristic names and descriptions, and that
    the leading HTML comment is captured — depends on: Task 0.8.2 —
    status: done (2026-08-16)
  - [x] Task 0.8.6: Add `tests/general/resources/test_iso25010.py`,
    mirroring `tests/general/resources/test_version.py` — asserts the
    `iso25010` resource function returns an `Iso25010` instance with the
    expected characteristic count — depends on: Task 0.8.3 — status:
    done (2026-08-16)
  - [x] Task 0.8.7: Regenerate `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 — depends
    on: Task 0.8.4 — status: done (2026-08-16)
  - [x] Task 0.8.8: Verify — `ruff format --check`, `ruff check`,
    `vulture src/ whitelist.py --min-confidence 60`, and the full
    `unittest` suite — depends on: Task 0.8.1 through Task 0.8.7 —
    status: done (2026-08-16, 791 tests, all passing)
  - [x] Task 0.8.9: Update this feature's own Decisions Made / Recent
    Updates logs and mark Task 0.8 (and this sub-list) done — depends
    on: Task 0.8.1 through Task 0.8.8 — status: done (2026-08-16)

- [x] Task 0.9: Add an id-based `get_req` MCP **tool** (not just the
  existing `specmgr://req/{id}` resource) — reason: in practice, LLMs and
  agents fail to reliably use `specmgr://req/{id}` (a resource, not a
  tool) to retrieve an artifact by id, defeating the point of exposing it
  that way. This directly revisits `feat-6-requirement-artifact` Task
  3.17's design decision ("`specmgr://req/{id}` resource ... supersedes
  the earlier considered `get_req` tool — id-based single-document read is
  a resource only"); may also need the equivalent look at `get_adr` (which
  already exists as a tool, unlike REQ) and any future `uc`/`get_uc` for
  consistency — depends on: none — status: done (2026-08-15)

  - [x] Task 0.9.1: Write a new ADR recording the decision: add a `get_req`
    tool mirroring `get_adr`; remove `specmgr://req/{id}` (`req_get`)
    entirely so REQ is tool-only for id-based reads; explicitly leave
    `specmgr://adr/{id}` (`adr_get`) coexisting with `get_adr` as-is
    (accepted, deliberate cross-domain divergence, not silently ignored);
    note future `uc`/`get_uc` should follow the REQ (tool-only) precedent
    — depends on: none — status: done (2026-08-15)
  - [x] Task 0.9.2: Add `req/tools/get_req.py` — `@mcp.tool(name="get_req")`
    wrapper mirroring `adr/tools/get_adr.py`, using
    `req/tools/_io.py`/`_paths.py`'s `load_by_id(req_base_dir(), id)`,
    returning `ReqDocument` — depends on: Task 0.9.1 — status: done (2026-08-15)
  - [x] Task 0.9.3: Remove `req/resources/req_get.py` and drop its
    import/registration from `req/resources/__init__.py` (module
    docstring, the `from . import ...` line, and `__all__`) — depends on:
    Task 0.9.2 — status: done (2026-08-15)
  - [x] Task 0.9.4: Update `req/__init__.py`'s module docstring — drop
    `specmgr://req/{id}` from the resources list, add `get_req` to the
    tools list — depends on: Task 0.9.3 — status: done (2026-08-15)
  - [x] Task 0.9.5: Update `server.py`'s module docstring — remove the
    `specmgr://req/{id}` resource line, add `get_req` to the "Requirement
    tools" line — depends on: Task 0.9.3 — status: done (2026-08-15)
  - [x] Task 0.9.6: Update `req/prompts/update_req.py`'s `## 1. Read current state first` step to call `get_req(id)` instead of reading the
    now-removed `specmgr://req/{id}` resource (mirror `update_adr.py`'s
    phrasing style) — depends on: Task 0.9.2, Task 0.9.3 — status:
    done (2026-08-15)
  - [x] Task 0.9.7: Add `tests/req/tools/test_get_req.py`, mirroring
    `tests/adr/tools/test_get_adr.py`'s two cases
    (`test_returns_matching_document`, `test_raises_not_found_for_unknown_id`)
    — depends on: Task 0.9.2 — status: done (2026-08-15)
  - [x] Task 0.9.8: Remove `tests/req/resources/test_req_get.py` — depends
    on: Task 0.9.3 — status: done (2026-08-15)
  - [x] Task 0.9.9: Update `tests/req/prompts/test_update_req.py`'s
    assertions (currently asserting on the literal `"specmgr://req/{id}"`
    string) to assert on the new `get_req(id)` wording instead — depends
    on: Task 0.9.6 — status: done (2026-08-15)
  - [x] Task 0.9.10: Regenerate `docs/adr/README.md` (`specmgr adr-toc`)
    and `docs/api/`/`docs/GENERATED.md` (`specmgr docs`), Python 3.13 —
    depends on: Task 0.9.1, Task 0.9.4, Task 0.9.5 — status: done (2026-08-15)
  - [x] Task 0.9.11: Annotate `feat-6-requirement-artifact/README.md`'s
    Task 3.17 line with a short pointer note ("revisited/superseded by
    feat-7 Task 0.9 and ADR `<new-id>` — `get_req` tool added, resource
    removed"), without rewriting its existing history — depends on: Task
    0.9.1 — status: done (2026-08-15)
  - [x] Task 0.9.12: Update this feature's own Decisions Made / Recent
    Updates logs and mark Task 0.9 (and this sub-list) done — depends on:
    Task 0.9.1 through Task 0.9.11 — status: done (2026-08-15)
  - [x] Task 0.9.13: Verify — `ruff format --check`, `ruff check`,
    `vulture src/ whitelist.py --min-confidence 60` (catches the removed
    `req_get` file), and the full `unittest` suite — depends on: Task 0.9.2
    through Task 0.9.9 — status: done (2026-08-15)

- [x] Task 0.10: Create a new `general` MCP resource that returns the RFC
  2119\. This is an ad interim solution until we have a filter option in
  ASD-STE100 MCP by source. — depends on: none — status: cancelled

- [x] Task 0.11: Add CLI command "mdformat". This command formats a Markdown
  document with or without frontmatter in the same way that the MCP server
  formats documents when it reads and write artifacts (example: it uses
  numbering for ordered lists). This command does not perform a content
  validation — depends on: none — status: done (2026-08-16)

- [x] Task 0.12: Move src/resources to src/general/resources. Update refs to
  it — depends on: none — status: done (2026-08-16)

- [x] Task 0.13: Make the not-found error message easier to understand for
  `get_<type>` tools (`get_adr`, `get_req`, `get_uc`, `get_tsk`) — agents
  frequently pass a prefixed id (e.g. `"req-<uuid>"`) instead of the bare
  `<uuid>`, since the on-disk filename/slug carries that prefix; the id
  parameter must be the bare uuid only, with no domain prefix. Each
  domain's `<domain>/tools/_paths.py` raises its own `*NotFoundError`
  (`AdrNotFoundError`/`ReqNotFoundError`/`UcNotFoundError`/`TskNotFoundError`)
  with an `f"no {DOMAIN} found with id {id_!r}"`-style message that does
  not hint at this; `req`/`uc`/`tsk` funnel through the shared
  `general/tools/_doc_paths.py`'s `DocNotFoundError` before re-raising
  their own domain-specific message, while `adr/tools/_paths.py` raises
  `AdrNotFoundError` inline (no shared-module dependency); `tsk`'s message
  already carries a first-pass, not-yet-standardized hint ("Make sure,
  that you only use the 'id' without a prefix.") that needs grammar
  cleanup and alignment with whatever single wording gets decided. The
  detailed 9-step implementation breakdown lives in its own specmgr task
  list, TSK `266eb332-795b-48c4-9bc0-7115eb209378` ("Improve
  get_adr/get_req/get_uc/get_tsk Not-Found Error Messages") — retrieve it
  via the `get_tsk` MCP tool with id `266eb332-795b-48c4-9bc0-7115eb209378`
  — depends on: none — status: done (2026-08-16), all 9 sub-tasks
  complete: standardized wording decided (see Decisions Made) and applied
  to `AdrNotFoundError`/`ReqNotFoundError`/`UcNotFoundError`/
  `TskNotFoundError`/`DocNotFoundError`; tests extended to assert on
  message content in each domain's `test_paths.py`/`test__paths.py` and
  `test_get_<type>.py`; verified clean via `ruff format --check`/
  `ruff check`/`vulture src/ whitelist.py --min-confidence 60`/full
  `unittest` suite

- [x] Task 0.14: MCP tool: WebFetch with BearerToken and URL filter — a
  general, cross-cutting `webfetch` MCP tool for a Web Server
  instance (generic bearer-authenticated GET fetch, URL-filtered against a
  configured base URL). The full implementation plan and its per-task
  breakdown live in specmgr task list TSK
  `efb7d049-a222-4730-901f-6d57283b387c` ("Implement `webfetch` MCP Tool
  (Bearer-Authenticated, URL-Filtered Fetch for Web Server)") — retrieve it
  via the `get_tsk` MCP tool with id `efb7d049-a222-4730-901f-6d57283b387c`
  — depends on: none — status: done (2026-08-16)

- [x] Task 0.15: MCP tools `<domain>_list` must support paging — depends on:
  none — status: split out into `feat-13-list-paging` (GitHub issue #13,
  `.specmgr/feat/feat-13-list-paging/README.md`) on 2026-08-19; design
  agreed (resource→tool `list_<domain>`, `asdste100`-style `PagedResult`
  wrapper, shared `general/` infra, paging-only). **`feat-13-list-paging`
  is now complete** (all four phases done, decision recorded in ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13): closes REQ-002/ACC-002 and
  advances (but does not fully close) REQ-001/ACC-001 — see those entries
  below for the remaining ADR-outlier caveat.

- [ ] Task 0.16: MCP tools `<domain>_list` must support filtering — depends on: none — status: not-started

  we have to discuss the design first, before we can implement

- [x] Task 0.17: Add a `MarkdownListItemWithNotes` class to `markdown_list_item.py` that introduces a `notes: list[MarkdownParagraph] | None = None` field for captured continuation paragraphs inside list items — depends on: none — status: completed

  Background: `MarkdownListItem._value` correctly captures the full markdown content of each item (including indented continuation paragraphs after a blank line), but `_value` is a Pydantic private attribute so it does not appear in `model_dump()` / MCP JSON output. `ExtensionItem` solves this with an explicit `notes` field; REQ's `Characteristics.items` has no such field, so the `text` property only returns the leading-paragraph text and everything after the first blank line is dropped on serialization. The new base class adds `notes` to all list-item consumers (REQ characteristics, UC extensions, task lists, etc.) — items with no continuation paragraphs will serialize with `"notes": null` or a missing key; items with continuation paragraphs will carry the captured paragraphs in JSON.

  Full implementation plan: specmgr TSK `f581fb2f-9a82-11f1-9c57-fc4cea71c519`.

- [x] Task 0.18: Fix `MarkdownListItem.get_extent` for numbered lists — depends on: Task 0.17 — status: completed

  Background: `mdformat` renders loose numbered lists (`1.`, `2.`) differently from bullet lists (`-`): the `list_item_open` token's `.map` only spans the first paragraph, leaving continuation paragraphs as separate tokens outside the list item. This breaks `get_extent` for numbered lists with continuation paragraphs (e.g. REQ's `Characteristics` section). The fix detects single-item ordered lists (where `ordered_list_open.map[1] == list_item_open.map[1]`) and scans for trailing `paragraph_open` tokens after `ordered_list_close` but before the next `ordered_list_open`, extending the extent accordingly.

  Full implementation plan: specmgr TSK `602740af-0445-48d8-bcc3-18df541dad72`.

- [x] Task 0.19: Add a new `refine` QA prompt (`qa/prompts/refine.py`) that
  appends a batch of new, unanswered interview questions to an existing QA
  document, for one or more of the nine ISO/IEC 25010:2023 quality
  characteristics — resolves its target document via `specmgr://qa/list`
  (id or title lookup) plus `get_qa`, grounds each question in
  `specmgr://iso25010`'s actual characteristic definitions, asks the user
  via the `question` tool when the count/characteristics are ambiguous,
  appends `> {question}` / `_(awaiting response)_` placeholder pairs via a
  whole-body `update_qa` replace, and tells the user to answer the
  placeholders and then run the (separate, not-yet-implemented) `/resolve`
  command next. Registered in `qa/prompts/__init__.py` and `server.py`'s
  module docstring; 12 tests added in `tests/qa/prompts/test_refine.py` —
  depends on: none — status: done (2026-08-18)

  - [x] Task 0.19.1: Retrofit `refine`'s instructional text out of an
    inline `_INSTRUCTIONS_TEMPLATE` Python string (this codebase's
    universal convention for all 11 other prompt modules at the time) and
    into a new packaged data file, `qa/data/qa_refine_instructions.md`,
    read fresh on every call via
    `general.tools._packaged_data.read_packaged_text("qa", "refine_instructions", "md")`
    — the same packaging convention already used for
    `qa_example.md`/`qa_template.md`/`qa_schema.json`, applied to a
    prompt's instructional text for the first time in this codebase.
    Switched placeholder substitution from `str.format`
    (`{id_or_name}`/`{scope}`, requiring `{{`/`}}`-escaping of the
    template's own literal Q&A markdown placeholders like
    `{the question}`) to `string.Template`
    (`$id_or_name`/`$scope`), so the packaged `.md` file can use plain,
    unescaped `{...}` braces throughout. Added 2 more tests
    (`test_instructions_loaded_from_packaged_data_file`,
    `test_raises_file_not_found_when_instructions_missing`, mirroring
    `tests/uc/resources/test_uc_example.py`'s
    `mock.patch.object(_packaged_data, "packaged_data_path", ...)`
    pattern) — depends on: Task 0.19 — status: done (2026-08-18)
  - [x] Task 0.19.2: Regenerate `docs/api/`/`docs/GENERATED.md`
    (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); verify
    `ruff format --check`/`ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), and the full `unittest` suite — depends
    on: Task 0.19.1 — status: done (2026-08-18, 1158 tests, all passing,
    up from 1156)

- [x] Task 0.20: Apply the packaged-instructions-file pattern established
  by Task 0.19.1 to every remaining inline `_INSTRUCTIONS_TEMPLATE` prompt
  module in the codebase: `adr/prompts/create_adr.py`,
  `create_adr_test.py`, `update_adr.py`, `update_adr_test.py`;
  `req/prompts/create_req.py`, `update_req.py`; `tsk/prompts/create_task.py`,
  `update_task.py`, `implement_task.py`; `qa/prompts/create_qa.py`,
  `update_qa.py` (11 modules total). Each gets its own packaged
  `<domain>/data/<domain>_<kind>_instructions.md` file, loaded via
  `read_packaged_text` + `string.Template`, with any `str.format`-style
  `{...}`/`{{...}}` escaping unwound to plain `{...}` since
  `string.Template` needs none. Extend/add each module's test file with
  the same fresh-read/missing-file coverage `refine`'s Task 0.19.1 got —
  depends on: Task 0.19 — status: done (2026-08-18)

  - [x] Task 0.20.1 (ADR): `create_adr.py`/`create_adr_test.py`/
    `update_adr.py`/`update_adr_test.py` converted; new `adr/data/`
    package created (didn't exist before) with `adr_create_instructions.md`
    / `adr_create_test_instructions.md` / `adr_update_instructions.md` /
    `adr_update_test_instructions.md`; added
    `"biz.dfch.specmgr.adr" = ["data/*.md"]` to `pyproject.toml`'s
    `[tool.setuptools.package-data]` (ADR's package had none before, since
    its schema lives under top-level `models/adr/`, not `adr/models/`) —
    depends on: Task 0.19 — status: done (2026-08-18)
  - [x] Task 0.20.2 (REQ): `create_req.py`/`update_req.py` converted;
    `req_create_instructions.md`/`req_update_instructions.md` added to the
    already-existing `req/data/` — depends on: Task 0.19 — status: done
    (2026-08-18)
  - [x] Task 0.20.3 (TSK): `create_task.py`/`update_task.py`/
    `implement_task.py` converted; `tsk_create_instructions.md`/
    `tsk_update_instructions.md`/`tsk_implement_instructions.md` added to
    the already-existing `tsk/data/` — note the `tsk_*` file-name prefix
    (matching the domain/package name) even though the prompt names
    themselves are `create_task`/`update_task`/`implement_task` (with
    "task" not "tsk"), consistent with `tsk/data/tsk_example.md` already
    using that same prefix — depends on: Task 0.19 — status: done
    (2026-08-18)
  - [x] Task 0.20.4 (QA): `create_qa.py`/`update_qa.py` converted;
    `qa_create_instructions.md`/`qa_update_instructions.md` added
    alongside `qa_refine_instructions.md` in the already-existing
    `qa/data/` — depends on: Task 0.19 — status: done (2026-08-18)
  - [x] Task 0.20.5: Regenerated `docs/api/`/`docs/GENERATED.md`
    (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`); verified
    `ruff format --check`/`ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), and the full `unittest` suite — depends
    on: Task 0.20.1, Task 0.20.2, Task 0.20.3, Task 0.20.4 — status: done
    (2026-08-18, 1180 tests, all passing, up from 1158)

- [x] Task 0.21: Create a new, general-purpose MCP `@mcp.prompt()` (e.g.
  `general/prompts/compact_history.py`, prompt name `compact_history` —
  `general/` currently has `tools`/`resources` but no `prompts`
  sub-package yet, so this also stands up that new sub-package and its
  registration in `general/__init__.py`/`server.py`) that guides an LLM
  through compacting the "Recent Updates" section of *any* feature folder
  under `.specmgr/feat/<feature_id>/README.md`, not just this one — per
  ADR e369ee2e-3353-4f92-991c-6367d76d832e's chosen option, which
  documents an optional sibling `history.md` file for rotating out older
  `Recent Updates` entries once a feature's `README.md` section grows too
  long, leaving a pointer in its place (e.g. "See history.md for updates
  before YYYY-MM-DD."). Unlike `adr`/`req`/`uc`/`tsk`/`qa`, feature
  folders have no dedicated parser/get/update MCP tools of their own, so
  this prompt's instructions rely on the LLM's own file
  read/edit/write tools directly on `README.md`/`history.md`, not on any
  new specmgr tool. The prompt takes the feature id (e.g.
  `feat-7-various-improvements`) as a parameter; the exact rotation
  trigger/cutoff (entry count, age, line count, ...) is left for the
  prompt's instructions to ask the user about when ambiguous, per the
  ADR's own "Open Questions" note that this is deliberately not
  prescribed. This feature folder's own `Recent Updates` was already
  manually compacted (2026-08-18, ahead of this task), so no live demo
  run against it is planned here — coverage is unit tests only, using
  fixtures rather than re-running the prompt against this folder — but
  the prompt itself must not be specific to `feat-7-various-improvements`
  — depends on: none — status: done (2026-08-18), all 5 sub-tasks
  complete: 1192 tests, all passing, up from 1180

  - [x] Task 0.21.1: Add `general/prompts/__init__.py` and
    `general/prompts/compact_history.py`
    (`@mcp.prompt(name="compact_history")`, params `feature_id: str` and
    optional `cutoff_hint: str | None`), following the `refine` reference
    pattern exactly: instructional text lives in a packaged data file,
    `general/data/general_compact_history_instructions.md`, loaded via
    `read_packaged_text("general", "compact_history_instructions", "md")`
    - `string.Template` (`$feature_id`/`$cutoff_hint`). The instructions
      must: locate `.specmgr/feat/$feature_id/README.md` (and sibling
      `history.md` if present) via the LLM's own file tools; ask the user
      via the `question` tool for the rotation cutoff when `$cutoff_hint`
      is absent/ambiguous rather than guessing; move older `Recent Updates`
      entries verbatim into `history.md` (creating it if absent), preserve
      remaining entries and the `README.md` pointer line convention exactly
      as already used in this file; bump frontmatter `updated`; and verify
      every archived entry appears exactly once in `history.md` and nowhere
      else, mirroring the manual pass already performed on this folder —
      depends on: none — status: done (2026-08-18)
  - [x] Task 0.21.2: Register `compact_history` in
    `general/prompts/__init__.py`; add `prompts` to
    `general/__init__.py`'s imports/`__all__`/docstring; update
    `server.py`'s module docstring (`Prompts` section: add a "General
    prompts" line; package-shape paragraph: note `general` now also has a
    `prompts` sub-package) — depends on: Task 0.21.1 — status: done
    (2026-08-18)
  - [x] Task 0.21.3: Add `tests/general/prompts/__init__.py` and
    `tests/general/prompts/test_compact_history.py`, mirroring
    `tests/qa/prompts/test_refine.py`'s shape: parameter interpolation
    checks, key-instruction content checks (question tool, history.md,
    pointer line, frontmatter `updated`), plus the
    fresh-read-per-call/missing-file `FileNotFoundError` pair via
    `mock.patch.object(_packaged_data, "packaged_data_path", ...)` — no
    live run against this feature folder itself (already compacted) —
    depends on: Task 0.21.1 — status: done (2026-08-18, 12 tests added)
  - [x] Task 0.21.4: Regenerate `docs/api/`/`docs/GENERATED.md`
    (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13;
    verify `ruff format --check`/`ruff check` (clean),
    `vulture src/ whitelist.py --min-confidence 60` (clean), and the full
    `unittest` suite — depends on: Task 0.21.1, Task 0.21.2, Task 0.21.3
    — status: done (2026-08-18, 1192 tests, all passing, up from 1180)
  - [x] Task 0.21.5: Update this feature's own Decisions Made / Recent
    Updates logs and mark Task 0.21 (and this sub-list) done — depends
    on: Task 0.21.1 through Task 0.21.4 — status: done (2026-08-18)

- [x] Task 0.22: Examine cyclic dependency in `set_status.py` (qa) to server
  and mcp — depends on: none — status: documented (2026-08-19). Confirmed
  the cycle is real (`specmgr.server -> specmgr.qa -> specmgr.qa.tools -> specmgr.qa.tools.set_status_qa -> specmgr.server`) but architecture-wide,
  not qa-specific (~80 files across every domain follow the identical
  `from ...server import mcp` pattern; `pylint` R0401 flags ~90 equivalent
  warnings, already suppressed via `|| true`). Not currently breaking
  anything — safe only due to `server.py`'s fragile import-ordering
  convention (`mcp = MCPServer(...)` textually precedes its bottom-of-file
  domain imports). Decision recorded in ADR
  `3bf0326f-065a-424c-a2b9-87e5d5bcfa99` ("Extract MCP Singleton into Its
  Own Module to Break Domain/Server Cyclic Imports"): extract a new
  `mcp_instance.py` leaf module owning the `MCPServer` singleton, imported
  by both `server.py` and every domain file instead of `server.py` directly
  — implementation deferred to specmgr TSK
  `699432f5-6f95-498e-a269-8001e4afc0e5` ("Extract `mcp_instance.py` to
  Break Domain/Server Cyclic Imports"); no code changes made as part of
  this task

- [x] Task 0.23: Add the `mcp` SDK's `streamable-http` transport as a third
  `specmgr mcp --transport` option, alongside the existing `stdio`/`sse` —
  `mcp>=2.0.0` (already a dependency) exposes `run_streamable_http_async`
  symmetrically to the existing `run_sse_async` used for `sse`, so this is
  purely a transport-wiring change confined to `commands/mcp.py`, with no
  changes needed to `server.py`, tools, resources, or prompts (MCP
  transport is orthogonal to the legacy/modern protocol-era negotiation,
  which the SDK already handles automatically on every transport). `sse`
  is the legacy/deprecated MCP HTTP transport; `streamable-http` is its
  spec-current replacement. The detailed implementation breakdown lives in
  its own specmgr task list, TSK `aaf70093-8a7c-4565-9985-3beaa85e1d3d`
  ("Add `streamable-http` MCP Transport Option") — retrieve it via the
  `get_tsk` MCP tool with id `aaf70093-8a7c-4565-9985-3beaa85e1d3d` —
  depends on: none — status: done (2026-08-19)

- [x] Task 0.24: Clean up `AGENTS.md`'s stale `specmgr://<d>/list` resource
  mentions left over from `feat-13-list-paging`'s resource→tool conversion
  (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13) — found and flagged during
  `.specmgr/feat/feat-16-problem-statement/README.md`'s planning session
  (2026-08-25) while designing that new domain's own `list_prb` tool
  against the *current* code/ADR state rather than `AGENTS.md`'s
  (out-of-date) wording. Verification (2026-08-26) found the flagged drift
  already removed from `AGENTS.md` upstream — the
  `specmgr://req/list`/`specmgr://qa/list`/`specmgr://adr/list` strings
  were all gone as of feat-13's close-out commit `452e125` (2026-08-19,
  six days before the flag), and `specmgr://tsk/list` never appeared there
  at all — but still normalized every affected domain bullet (the five
  older ones, `adr`/`req`/`uc`/`tsk`/`qa`, now carry the explicit "no
  `specmgr://<d>/list` — listing is the `list_<d>` tool" note the newer
  `prb`/`gol`/`rsk` bullets already had), plus any other live
  `specmgr://<d>/list` mention: three model docstrings
  (`req/models/v1/summary.py`, `models/adr/v1/summary.py`,
  `tsk/models/v1/summary.py`) were fixed in the same pass per user
  instruction (2026-08-26), extending the task's originally AGENTS.md-only
  scope — depends on: none — status: done (2026-08-26)

- [x] Task 0.25: Update `AGENTS.md`'s "Models location" section so it
  states the *rule* instead of enumerating the post-refactor domains: ADR
  is the only document type whose schema is not in its own domain
  package (`models/adr/` at top level, because ADR predates the
  domain-first refactor); every other document type (`req`, `uc`, `tsk`,
  `qa`, `prb`, `gol`, and any future type) keeps its schema inside its
  own domain package (`<domain>/models/vN/`). This resolves the standing
  contradiction — the section currently names only "REQ, UC, and TSK" as
  built after the refactor, while AGENTS.md's own per-domain bullets name
  more (the `prb/` bullet says "same as REQ/UC/TSK/QA") — and
  future-proofs the section: building a new document type no longer
  requires editing AGENTS.md's "Models location" paragraph (as
  feat-18-goal Phase 4 had to do for `gol`). Secondary, decide at
  implementation time: the same per-type enumeration fragility exists in
  AGENTS.md's Status heading (count + domain list) and its closing
  "Don't assume any other domain package exists beyond …" paragraph —
  reword those as rules too where feasible, or keep them enumerated and
   record that decision in this file's Decisions Made — depends on: none —
   status: done (2026-08-26)

  Background: Found during feat-18-goal's (the new `gol` domain) Phase 4
  AGENTS.md update (2026-08-26): AGENTS.md's "Models location — a real,
  intentional divergence, not an oversight" paragraph (lines 108–116)
  reads "REQ, UC, and TSK were built *after* that refactor and each keep
  their schema inside their own domain package" — but `qa`
  (`qa/models/v2/`), `prb` (`prb/models/v1/`), and `gol` (`gol/models/v1/`)
  were also built after the domain-first refactor and likewise keep their
  schemas in their own domain packages, and the file's own `prb/` bullet
  already says "same as REQ/UC/TSK/QA" — the two sections contradict each
  other. The sentence also had to be extended for every new type (feat-18
  Phase 4 touched AGENTS.md in ~6 places for `gol` alone) even though the
  underlying fact is stable: ADR's schema is the single exception at
  top-level `models/adr/`. Stating the rule instead of enumerating the
  domains removes both the contradiction and the per-type maintenance.
  Note: the line numbers cited refer to AGENTS.md as of 2026-08-26 and
   will drift — locate the section by its heading when implementing.

- [x] Task 0.26: Document the one-time pre-commit hook install in
  `README.md`'s "Development" section for developers who want to develop
  this application — after `uv sync --all-extras` the hooks are still
  inactive, because `uv sync` only installs Python dependencies into the
  venv and never writes anything into `.git/hooks/`; the developer must
  additionally run `uv run --frozen pre-commit install` once per clone
  (this is already noted in `AGENTS.md`'s "Developer Commands" section,
  but not in the user-facing `README.md`). Add a short subsection there
  with the command and a one-line explanation of why `uv sync` alone is
  not enough — depends on: none — status: done (2026-08-26)

- [x] Task 0.27: Clean up the schema drift checks in `.github/workflows/ci.yml`
  and `.pre-commit-config.yaml` — (a) consolidate the five duplicated plain
  `specmgr schema` CI steps ("Make sure `docs/{req,uc,qa,prb,gol}_schema.json`
  is correct") into a single step: each invocation already regenerates/checks
  **all** registered types' `docs/*_schema.json` copies (no `--type` → full
  set, `commands/schema.py`), so one run covers req/uc/qa/prb/gol **and**
  `tsk`/`rsk`, which currently have no dedicated `docs/<t>_schema.json`
  step at all (their docs copies are only checked incidentally via the
  other five runs);
  keep the seven per-domain packaged-copy steps
  (`--type <t> --output-dir src/biz/dfch/specmgr/<t>/data`) unchanged —
  those are genuinely one artifact per step, matching the seven independent
  `specmgr-schema-*-package` pre-commit hooks; (b) confirm the
  `specmgr-schema` hook description in `.pre-commit-config.yaml` is current —
  it was stale ("currently `req` and `uc`" — predates tsk/qa/prb/gol; the
  `files:` patterns were updated when those domains landed, the prose was
  not) but was already fixed by feat-15's RSK work (Task 3.12) and now lists
  all seven registered types, so no change was needed;
  (c) verify the consolidated CI step locally (`uv run --frozen specmgr
  schema` exits 0 on a clean tree, 1 after deliberately drifting one file)
  — depends on: none — status: done (2026-08-26)

- [ ] Task 0.28: Clean up two pre-existing doc enumerations found while
  implementing feat-21-decision (the DEC domain, 2026-08-27) and
  deliberately left untouched there as out-of-scope: (a) the root
  `README.md`'s "At this time, we have these artifact:" list — promote the
  implemented `Risk (RSK)` domain into the active list (alphabetical slot
  between `- Requirement (REQ)` and `- Task List (TSK)`) and remove it from
  the commented-out future block below the list (the
  `feat-15-add-artifact-type-risk` work never promoted it; feat-18/feat-21
  each promoted their own entries); (b) `AGENTS.md`'s "Existing feature
  folders:" list (in the "Development Artifacts (`.specmgr/`)" section),
  which names only `feat-9-doc-in-specmgr/`/`feat-4-use-cases/`/
  `feat-5-md-model-parser/` while 14 feature folders now exist — either
  refresh the enumeration or reword it as a rule (per Task 0.25's
  precedent of stating the rule instead of enumerating), deciding at
  implementation time and recording the choice in this file's Decisions
  Made — depends on: none — status: not-started

  Background: Found during feat-21's Phase 5 (cross-cutting registration)
  when its AGENTS.md/root-README enumeration pass was scoped to DEC only;
  both items predate feat-21 (RSK's promotion gap dates to feat-15's
  close-out; the feature-folders list to the feat-9 migration era) and
  were flagged rather than fixed to keep feat-21's diff on-scope. No code
  impact — documentation-only staleness.

- [ ] Task 0.29: Fix silent/unhelpful validation failures when a
  `MarkdownParagraph`-typed field's prose wraps onto a line starting with
  `+`, `-`, or `*` — depends on: none — status: not-started

  Background: Found while closing out the "Finish persisting the OpenCode
  + MCP PlantUML sequence diagram" task list (TSK
  `952d39e5-3b79-4389-bc71-a4fe8ca85cd3`, 2026-08-29). A `Recent Updates`
  entry's paragraph in a TSK document wrapped onto a line starting with
  `+ group-block style as final...`; both the generic `update` tool
  (`general/tools/update.py`) and the domain `validate_tsk` tool
  (`tsk/tools/validate_tsk.py`) failed with an opaque, generic
  MCP-SDK-generated `"Error executing tool <name>: ..."` message that gave
  no actionable hint about the cause. Root-caused via investigation:

  - `models/md/_markdown.py`'s `format_text()` (mdformat/markdown-it,
    CommonMark) correctly-but-surprisingly treats a `+`/`-`/`*`-prefixed
    line following a paragraph as the start of a NEW bullet list, not lazy
    paragraph continuation — splitting one logical paragraph into two
    separate token blocks (`paragraph_open`/... plus
    `bullet_list_open`/...).
  - `models/md/markdown_paragraph.py`'s `MarkdownParagraph.get_extent`
    (leaf case) only captures the first `paragraph_open`'s own line span,
    so the resulting stray bullet-list block is never absorbed into the
    field's extent.
  - `models/md/markdown_str.py:382`'s generic `MarkdownStr.from_text`
    "text left over after processing all fields" `AssertionError` fires
    because no other declared field consumes the leftover bullet-list
    text — reproduced concretely against `tsk/models/v1/body.py`'s
    `UpdateEntry.content: MarkdownParagraph` field, but the exposure is
    generic to `models/md` (`MarkdownParagraph` is used the same way by
    every other whole-body domain: req/uc/qa/prb/gol/rsk/dec), not
    TSK-specific.
  - The generic "Error executing tool X: {e}" wording is produced by the
    third-party `mcp` SDK (`mcp/server/mcpserver/tools/base.py`/
    `server.py`), not by this repo's own code — the underlying
    `AssertionError`/`ValidationError` message IS interpolated into `{e}`
    server-side; any further truncation to a bare "Error executing tool X"
    happens client-side (outside this repo's control). This repo could
    still make the underlying message clearer/more actionable on its own
    side (see below).
   - Confirmed test gap: no test in `tests/models/md/` or any domain's
     tests covers a paragraph continuation line starting with `+`/`-`/`*`.

   Sibling trigger (GitHub issue #27, 2026-08-27): a bare `<word>`-style
   token in prose (e.g. `<domain>` — not backticked, not inside an HTML
   comment) is parsed as a raw HTML tag by markdown-it and reaches the
   same "text left over" assertion with the same opaque
   "Error executing tool <name>" surface — same failure class and fix
   scope, different repro.

   Candidate fix directions to evaluate at implementation time (not decided
   yet):

  1. In `models/md/_markdown.py`/`markdown_paragraph.py`: teach
     `MarkdownParagraph` (or `format_text`) to absorb an immediately-
     following stray `bullet_list`/`ordered_list` block back into a leaf
     paragraph's extent, OR pre-escape non-list-intended leading
     `+`/`-`/`*` characters before formatting.
  2. In `general/tools/update.py` and each domain's `validate_<d>.py`
     (currently zero exception handling anywhere in the tool layer, by
     design — see their docstrings): add a
     `try/except (AssertionError, pydantic.ValidationError)` wrapper that
     re-raises a `ValueError` with a clearer, targeted message when this
     specific "text left over" pattern is detected, so the SDK's `{e}`
     interpolation carries a genuinely actionable hint instead of a raw
     assertion string.
  3. Add regression tests: `tests/models/md/test_markdown_paragraph.py` (a
     paragraph whose second line starts with `+`/`-`/`*`) and at least one
     domain-level test (e.g. `tests/tsk/models/v1/test_body.py` or
     `tests/tsk/tools/test_validate_tsk.py`) reproducing the exact failure
     end-to-end.

- [ ] Task 0.30: Consolidate "Recent Updates" and "Updates" across
  artifact types — depends on: none — status: not-started

  Background: Found while planning `feat-30-sop` (2026-08-30). Different
  document-type domains use different heading text and different section
  shapes for their own "what changed over time" section: `tsk`'s
  `RecentUpdates`/`## Recent Updates` (free-form `@alias(value=".+",
  type=AliasType.REGEX)` H3 heading, mandatory lead `MarkdownParagraph`
  content, no timestamp format enforced structurally); `dec`'s
  `Updates`/`## Updates` (implicit-alias heading, `UpdateEntry` H3s). `sop`
  (feat-30, not yet implemented) is about to add a **third** variant,
  `Updates`/`## Updates` with a structurally-enforced ISO8601 timestamp +
  " — " + title heading regex
  (`^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}) — .+$`)
  — a stricter shape than either `tsk` or `dec` currently has. `feat`
  (feat-31, formalizing the `.specmgr/feat/` artifact type itself, also not
  yet implemented) adds a **fourth** variant: the same ISO8601-enforced
  `Updates`/`UpdateEntry` shape as `sop`, but one heading level deeper
  (`### Updates`/`#### {timestamp} — {title}`, since it sits under
  `## Progress` rather than directly under the document's H1) — copied
  from `sop`'s planned shape rather than `sop`'s code (which does not exist
  yet). None of `req`/`uc`/`qa`/`prb`/`gol`/`rsk` have any such section at
  all today. Decide: (a) whether a single canonical heading name/shape
  (`## Updates` vs `## Recent Updates`, timestamp format enforced or not,
  and at which heading depth) should be retrofitted across every domain
  that has one, or whether the divergence is intentional/acceptable
  per-domain; (b) if consolidating, whether this warrants a shared
  `models/md` mixin/base class (e.g. a generic `UpdatesSection`/
  `UpdateEntry` pair domains can subclass) rather than each domain
  hand-rolling its own `Updates`/`UpdateEntry` pair; (c) whether `sop`'s/
  `feat`'s ISO8601-with-offset timestamp format for `Updates` entry
  headings should become the new cross-domain standard (superseding
  `tsk`'s free-form heading and `dec`'s implicit-alias heading), be
  retrofitted onto `tsk`/`dec`, or stay `sop`/`feat`-only as a deliberate
  divergence; record whichever decision is made, with rationale, in this
  file's Decisions Made log (or a full ADR if it turns out to affect the
  parser engine itself, per the ADR-vs-feature-log tie-breaker in ADR
  e369ee2e-3353-4f92-991c-6367d76d832e). Out of scope for `feat-30-sop`/
  `feat-31-feature` themselves — both features proceed with their own
  `Updates` shape as designed; this task is only about whether a later,
  separate consolidation pass should retrofit `tsk`/`dec` (and any future
  domain) onto one shared shape.

- [ ] Task 0.31: Migrate the 17 pre-existing `.specmgr/feat/*/README.md`
  files into the new `feat` artifact-type schema (`type: feat` frontmatter
  field, closed 4-set `status` with no hyphens, `### Updates`
  restructuring per whatever Task 0.30 decides) — depends on:
  `feat-31-feature` (the `feat` artifact type feature) being implemented
  and merged, Task 0.30 (consolidation decision) — status: not-started

  Background: `feat-31-feature` (formalizing the Feature artifact type)
  deliberately does **not** migrate existing feature folders — they stay
  unparseable by `parse_feat`/`get_feat` (silently skipped by `list_feat`)
  until this follow-up task migrates them by hand/script once the schema
   and its `### Updates` shape are both settled (user-directed decision,
   recorded in `feat-31-feature`'s own Decisions Made log).

- [x] Task 0.32: Per GitHub issue #28 ("specmgr_get and specmgr_update
   must both support offset and limit"): change the generic `update`
   tool's (`general/tools/update.py`) 1-based inclusive `begin`/`end`
   body-line range to `offset`/`limit` (matching the `read` tool's
   parameter names), and add `offset`/`limit` paging to the ten
   `get_<d>` tools (alongside their existing `raw` parameter) so a
   caller can read a body window without fetching the whole document —
   depends on: none — status: split out into `feat-28-get-update`
   (GitHub issue #28, `.specmgr/feat/feat-28-get-update/README.md`) on
   2026-09-01; the revised contract (`offset`/`limit` for the generic
   `update` tool + windowed `get_<d>` reads, hard rename, ADR draft
   created in this feature) is recorded in the feat-28 plan.

   Background: Both requests date from 2026-08-27, before/around
   feat-22's consolidation, when the tools were still named
   `specmgr_get`/`specmgr_update`; they now map to the generic `update`
   tool (which kept `begin`/`end`) and the per-domain `get_<d>` tools
   (which have `raw` only — verified on `dev`, 2026-08-31). Note the
   semantic difference to resolve at implementation time: `update`'s
   `begin`/`end` is a *splice range* (replace lines begin..end with
   `content`), whereas `read`'s `offset`/`limit` is a *read window* —
   the rename must decide whether `update` keeps splice semantics under
   the new names (e.g. "start at offset, replace up to limit lines") or
   whether the issue intended something else. The issue explicitly asked
   for this to be tracked here; it was never recorded in this task list
   (found during the 2026-08-31 stale-issue review).

- [ ] Task 0.33: Per GitHub issue #29 ("Artifact type 'Decision' (DEC)
   need additional attributes from ADR frontmatter"): extend
   `DecFrontmatter` (`dec/models/v1/frontmatter.py`) with the ADR-style
   attributes a decision in general is missing, e.g. `source` or
   `owner` — depends on: none — status: not-started

   Background: `DecFrontmatter` currently narrows only `type`
   (`Literal["dec"]`) and `status` (closed six-value set) on top of the
   generic `MarkdownFrontmatter` (`id`/`created`/`updated`/`version`),
   verified on `dev` (2026-08-31) — no `source`/`owner` or other
   ADR-style fields exist yet. The exact attribute set to add is open:
   the issue names `source` and `owner` as examples, but the ADR
   frontmatter (`AdrFrontmatter`) itself defines `date`/`decision-makers`/
   `consulted`/`informed` beyond the shared base, so decide at
   implementation time which of these (plus any DEC-specific ones like
   `source`/`owner`) `DecFrontmatter` should gain, and keep the
   whole-object-replace frontmatter contract. The issue explicitly asked
   for this to be tracked here; it was never recorded in this task list
   (found during the 2026-08-31 stale-issue review).

- [ ] Task 1.1: Inventory current `specmgr://*/list` resources and diff
  their output shape/behavior (`adr_list` vs. `req_list`) — depends on:
  none — status: not-started

- [ ] Task 1.2: Inventory current MCP prompt modules and their
  structure/length/gating style (`create_adr`, `update_adr`,
  `create_adr_test`, `update_adr_test`, `create_req`, `update_req`) —
  depends on: none — status: not-started

#### Phase 2: Decide

- [ ] Task 2.1: Decide the standardized list-resource contract (shared
  base summary model, pagination yes/no and shape if yes) — depends on:
  Task 1.1 — status: in-progress — one piece already decided directly
  (2026-08-15, ahead of the formal audit): the fallback identifier field is
  named `ref`, not `filename`, and holds the extensionless base name, not
  the raw on-disk filename (see Decisions Made). Pagination is now
  **completed** via `feat-13-list-paging` (resource→tool `list_<domain>` +
  `asdste100`-style `PagedResult` wrapper, recorded in ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13); the shared-base-summary piece was
  also carried into and completed by that feature (`general.models. DocSummary`, subclassed by 4 of 5 domains — see ACC-001).
- [ ] Task 2.2: Decide the fate of the `_test` prompt variants and the
  criteria used for the prompt-quality review — depends on: Task 1.2 —
  status: not-started

#### Phase 3: Implement

- [x] Task 3.1a: Rename `AdrSummary.filename`/`ReqSummary.filename` to
  `ref`, changing its value from `path.name` (e.g. `"<uuid>-a-title.md"`)
  to the extensionless `path.stem` (e.g. `"<uuid>-a-title"`), and update
  the `adr_list`/`req_list` resource descriptions accordingly — done to
  stop steering the calling LLM toward reading the file off disk directly
  instead of using `get_adr`/`get_req`/`specmgr://{adr,req}/{id}` — depends
  on: none — status: done (2026-08-15)
- [x] Task 3.1b: Apply the remaining piece of the standardized
  list-resource contract (pagination) to `adr_list`/`req_list` (and
  document the full contract for future `*_list` resources) — depends on:
  Task 2.1 — status: **completed via `feat-13-list-paging`** (GitHub issue
  #13); implemented there as the resource→tool + `PagedResult` conversion
  across all five domains, not just `adr`/`req` — decision recorded in ADR
  ec9f5262-9912-49d0-903f-fcfb54f28c13.
- [ ] Task 3.2: Apply prompt optimizations and the `_test`-variant decision
  — depends on: Task 2.2 — status: not-started

#### Phase 4: Verify

- [ ] Task 4.1: Update/extend tests covering the list resources and
  prompts affected by Phase 3 — depends on: Task 3.1, Task 3.2 — status:
  not-started
- [ ] Task 4.2: Update `AGENTS.md`/`docs/GENERATED.md` (via `specmgr docs`)
  to reflect the final state — depends on: Task 4.1 — status: not-started

**Note:** If a task's scope changes mid-flight, edit its description in place;
rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-16**: Feature folder created with the first tracked
concern (MCP list-resource format + prompt optimizations) scoped. Phase 0
housekeeping (backfilling GitHub issue numbers for `feat-0-*` folders,
including this one) is complete. The `filename` → `ref` field rename
(Task 3.1a) is implemented ahead of the formal Phase 1/2 audit/decision;
the rest of Phase 1 (audit) and the pagination question are not started.
Task 0.9 (`get_req` tool, all 13 sub-tasks) is now complete: `get_req` was
added, `specmgr://req/{id}` was removed, `specmgr://adr/{id}` was
deliberately left untouched, and the decision is recorded in ADR
`ddfb1109-422d-4507-8dbc-dc5e4bec9614`. Task 0.11 (`mdformat` CLI command)
is now complete: the formatting logic previously inlined in the `mdformat`
MCP tool was extracted into a shared, disk-free
`models.md._markdown.format_markdown_document()` helper, which both the MCP
tool and the new `specmgr mdformat` CLI command now call. Task 0.12 (move
`src/resources` to `src/general/resources`) is now complete: the top-level
`resources` package (the `specmgr://version` resource) was folded into
`general/` alongside `general/tools/`, since it is itself a cross-cutting,
not domain-specific, concern. Task 0.8 (`specmgr://iso25010` resource, all
9 sub-tasks) is now complete: `general/resources/iso25010.py` wraps
`parse_iso25010(read_packaged_text("general", "iso25010", "md"))`, is
registered in `general/resources/__init__.py`, and `general/__init__.py`/
`server.py`'s module docstrings (the latter's stale "top-level `resources`
package" line also fixed) list it; new tests
(`tests/models/test_iso25010.py`, `tests/general/resources/test_iso25010.py`)
and regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md` are in place.
Task 0.13 (standardized not-found error message across `get_adr`/`get_req`/
`get_uc`/`get_tsk`, all 9 sub-tasks from TSK
`266eb332-795b-48c4-9bc0-7115eb209378`) is now complete: one wording
template is applied identically across all four `*NotFoundError` classes
plus the shared `DocNotFoundError`, and tests assert on the message content.
Task 0.19 (new `refine` QA prompt, both sub-tasks) is now complete: the
prompt itself was added and registered, then its instructional text was
retrofitted out of an inline Python string into a packaged data file
(`qa/data/qa_refine_instructions.md`) read via `read_packaged_text` +
`string.Template` — the first time this codebase has moved a prompt's
instructions out of an inline `_INSTRUCTIONS_TEMPLATE` constant. Task 0.20
(applying that same pattern to the remaining 11 prompt modules across
`adr`/`req`/`tsk`/`qa`, all five sub-tasks) is now complete: every prompt
module that previously carried an inline `_INSTRUCTIONS_TEMPLATE` now
loads its instructions from a packaged `<domain>/data/<domain>_<kind>.md`
file via `read_packaged_text` + `string.Template`, including a brand-new
`adr/data/` package (registered in `pyproject.toml`) since ADR had none
before. This feature folder's own `Recent Updates` section was also
compacted (manually, ahead of Task 0.21): entries older than 2026-08-18
now live in a sibling `history.md`, per ADR
e369ee2e-3353-4f92-991c-6367d76d832e. Task 0.21 (a new, general-purpose
`compact_history` MCP prompt, all 5 sub-tasks) is now complete: `general/`
gained its first `prompts` sub-package (`general/prompts/`), registered
alongside its existing `tools`/`resources` in `general/__init__.py` and
`server.py`'s module docstring; the prompt guides an LLM through rotating
older `### Recent Updates` entries out of any `.specmgr` feature folder's
`README.md` into an optional sibling `history.md`, using the LLM's own
file tools directly (no dedicated specmgr tool exists for feature
folders) and the `question` tool to resolve an ambiguous rotation cutoff.
Covered by 12 new unit tests (fixtures only, no live re-run against this
already-compacted folder).

### Recent Updates

See `history.md` for updates before 2026-08-18 (rotated out per ADR
e369ee2e-3353-4f92-991c-6367d76d832e once this section grew too long).

#### Update 2026-09-01 (Task 0.32 split out)

- Split out: Task 0.32 (GitHub issue #28 — rename the generic `update`
  tool's `begin`/`end` splice range to `offset`/`limit` and add
  `offset`/`limit` windowed reads to the `get_<d>` tools) is now tracked
  in `feat-28-get-update` (`.specmgr/feat/feat-28-get-update/README.md`),
  created 2026-09-01. The revised contract (hard rename with no
  compatibility alias, strict `update` splice validation, raw-only
  clamping windowed reads) is recorded in that plan, and the new ADR
  recording it lands in `docs/adr/` as a draft in Phase 0.

#### Update 2026-08-31 (Task 0.29 extended)

- Extended: Task 0.29's background now also covers GitHub issue #27's
  bare `<word>`-style token repro (parsed as a raw HTML tag by
  markdown-it) as a sibling trigger of the same failure class — same
  "text left over" assertion, same opaque "Error executing tool <name>"
  surface. Noted on issue #27 itself.

#### Update 2026-08-31 (Tasks 0.32, 0.33 recorded)

- Recorded: Task 0.32 (GitHub issue #28 — rename the generic `update`
  tool's `begin`/`end` splice range to `offset`/`limit` and add
  `offset`/`limit` paging to the `get_<d>` tools) and Task 0.33 (GitHub
  issue #29 — extend `DecFrontmatter` with ADR-style attributes such as
  `source`/`owner`). Both issues explicitly asked to be tracked as
  feat-7 tasks but were never recorded in this task list; found during
  the 2026-08-31 stale-issue review (which also closed stale issues
  #31 and #1, per TSK `75beb26c-89ab-4b82-be96-e5e522a07e90`). Both
  tasks are not-started.

#### Update 2026-08-30 (Task 0.31 recorded; Task 0.30 extended)

- Recorded: Task 0.31 (migrate the 17 pre-existing `.specmgr/feat/*/
  README.md` files into the new `feat` artifact-type schema once
  `feat-31-feature` ships and Task 0.30's consolidation decision is made)
  — found while planning `feat-31-feature` (formalizing the Feature
  artifact type itself), which deliberately excludes this migration from
  its own scope per user direction.
- Extended: Task 0.30's background note now also cites `feat-31-feature`'s
  planned `### Updates`/`UpdateEntry` shape (same ISO8601 regex as `sop`,
  one heading level deeper) as a fourth divergent variant, alongside
  `tsk`/`dec`/`sop`.

#### Update 2026-08-30 (Task 0.30 recorded)

- Recorded: Task 0.30 (consolidate "Recent Updates"/"Updates" across
  artifact types — found while planning `feat-30-sop`, which is about to
  introduce a third divergent `## Updates` shape alongside `tsk`'s
  `## Recent Updates` and `dec`'s `## Updates`). Decision deferred; task
  is not-started.

#### Update 2026-08-29 (Task 0.29 recorded)

- Recorded: Task 0.29 (silent/unhelpful validation failures when a
  `MarkdownParagraph`-typed field's prose wraps onto a line starting with
  `+`, `-`, or `*` — found while closing out TSK
  `952d39e5-3b79-4389-bc71-a4fe8ca85cd3`). Root cause investigated and
  documented (mdformat/CommonMark list-splitting, `MarkdownParagraph`'s
  leaf-extent logic, and the generic `"text left over"` assertion in
  `models/md/markdown_str.py`, confirmed generic to every whole-body
  domain, not TSK-specific); candidate fix directions recorded but not
  implemented. Task is not-started.

#### Update 2026-08-27 (Task 0.28 recorded)

- Recorded: Task 0.28 (two pre-existing documentation enumerations found
  during feat-21's DEC implementation — the root `README.md`'s missing
  `Risk (RSK)` promotion, and `AGENTS.md`'s stale "Existing feature
  folders" list); documentation-only, no code changes, task is
  not-started.

#### Update 2026-08-26T17:51:33Z (Task 0.25)

- Completed: Task 0.25 (AGENTS.md now states the rule instead of
  enumerating the post-refactor domains in its "Models location"
  section), including the secondary rewording decided at implementation
  time (see Decisions Made):

  - Rewrote the "Models location" paragraph rule-first: every document
    type keeps its schema in its own domain package
    (`<domain>/models/vN/`), ADR is the single exception (top-level
    `models/adr/`, predates the domain-first refactor, no `mcp`
    dependency), and building a new document type requires no edit to
    the paragraph. The sentence enumerating what top-level `models/`
    holds (`adr/` + shared cross-domain modules `iso25010.py`/`md/`/
    `version_info.py`) is kept — it lists shared modules, not doc
    types.
  - Trimmed the now-redundant "X is a new domain built after the
    domain-first refactor, same as REQ/UC/TSK/QA[...]" tails from the
    `prb`/`gol`/`rsk` bullets; each bullet's domain-specific
    schema-location fact (e.g. `qa/models/v2/`-only) is untouched.
  - Reworded the Status heading (dropped the "nine … (ADR, REQ, …)"
    count+list duplicate — the per-domain bullets are now named as the
    live enumeration) and the closing "Don't assume any other domain
    package exists beyond …" paragraph (now points at the bullets
    instead of carrying a second copy of the list).
  - Incidental one-line fix: the `general/` bullet's stale "No
    `general/prompts/` yet." (left behind by Task 0.21, which added
    `general/prompts/` + `compact_history`) now lists
    `general/prompts/` (`compact_history`), since the reworded closing
    paragraph points at the bullets as the exceptions list.
  - Deliberately left enumerated (recorded in Decisions Made): the
    `MCP server (server.py)` paragraph's domain-import list (it
    documents the actual code line a new domain must touch) and the
    "Still genuinely missing / not yet done" list (a dynamic gap
    tracker, not a package inventory).
  - Pure doc edit (AGENTS.md + this file): no code, test, or generated
    doc changes; grep confirmed nothing in `tests/`/`src/` asserts on
    AGENTS.md content.

#### Update 2026-08-26T17:06:30Z (Task 0.24)

- Completed: Task 0.24 (clean up `AGENTS.md`'s stale `specmgr://<d>/list`
  resource mentions), with a verification-first outcome and a small scope
  extension:

  - Verification found the flagged drift no longer present in
    `AGENTS.md`: git pickaxe (`git log -S`) shows the
    `specmgr://req/list`/`specmgr://qa/list`/`specmgr://adr/list` strings
    were all removed by feat-13's close-out commit `452e125` (2026-08-19)
    — six days before the feat-16 planning session flagged them on
    2026-08-25 — and `specmgr://tsk/list` never appeared in `AGENTS.md`
    at all. Cross-checked against the live MCP surface: `server.py`'s
    module docstring (no `*_list` resources; all eight `list_<d>` tools
    under Tools), the code (no `resources/*list*.py` in any domain; eight
    `tools/list_<d>.py`), `docs/MCP.md`, and the packaged data files
    (incl. the `refine` prompt's instructions) — no stale mentions
    anywhere.
  - Normalized the five older-domain bullets (`adr`/`req`/`uc`/`tsk`/
    `qa`) to carry the explicit "no `specmgr://<d>/list` — listing is the
    `list_<d>` tool, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13" note that
    the `prb`/`gol`/`rsk` bullets already had, so the ambiguity that
    caused the false flag can't silently recur.
  - Fixed the same stale names in three model docstrings (scope
    extension, per user instruction): `req/models/v1/summary.py`
    (`specmgr://req/list` → `list_req`), `models/adr/v1/summary.py`
    (`list_adrs`/`specmgr://adr/list` → `list_adr`), and
    `tsk/models/v1/summary.py` (module + class docstring,
    `specmgr://tsk/list` → `list_tsk`, incl. the stale "(Phase-3,
    not-yet-built)" clause).
  - Annotated the two `feat-16-problem-statement` README references to
    this task as closed (append-only pointers, no history rewritten).
  - Regenerated `docs/api/`/`docs/GENERATED.md` (`specmgr docs`);
    `specmgr schema` reports no drift; `ruff format --check`/`ruff
    check`/`vulture src/ whitelist.py --min-confidence 60` clean; full
    `unittest` suite passing (1783 tests).

#### Update 2026-08-19T06:49:34Z (Task 0.22)

- Completed (documented only, no code changes): Task 0.22 (examine the
  `qa/tools/set_status_qa.py` \<-> `server.py` cyclic dependency):

  - Confirmed the import cycle is real: `specmgr.server -> specmgr.qa -> specmgr.qa.tools -> specmgr.qa.tools.set_status_qa -> specmgr.server`,
    via `qa/tools/set_status_qa.py`'s `from ...server import mcp`. Confirmed
    via `pylint`'s R0401 check and by tracing `server.py`'s own bottom-of-file
    `from . import adr, general, qa, req, tsk, uc` registration imports.
  - Confirmed this is **not** qa-specific: identical
    `from ...server import mcp` imports exist in ~80 tool/resource/prompt
    files across every domain (`adr`, `general`, `qa`, `req`, `tsk`, `uc`),
    all flagged by the same ~90 R0401 warnings, already permanently
    suppressed in CI via `|| true`.
  - Confirmed it is not currently breaking anything: the cycle resolves
    safely today only because `server.py` constructs
    `mcp = MCPServer(...)` textually before its own domain-package
    registration imports — a fragile ordering convention, not an enforced
    invariant.
  - Wrote ADR `3bf0326f-065a-424c-a2b9-87e5d5bcfa99` ("Extract MCP Singleton
    into Its Own Module to Break Domain/Server Cyclic Imports"), recording
    the decision to extract a new `mcp_instance.py` leaf module owning the
    `MCPServer` singleton, imported by both `server.py` and every domain
    file instead of reaching into `server.py` directly.
  - Created specmgr TSK `699432f5-6f95-498e-a269-8001e4afc0e5` ("Extract
    `mcp_instance.py` to Break Domain/Server Cyclic Imports") with the
    7-task implementation breakdown for executing the ADR's decision
    (new module, `server.py`/domain-file import updates, test/docs/lint
    verification), referenced from both the ADR's "More Information" and
    this task's line. Implementation deliberately not started as part of
    this task.

#### Update 2026-08-19T06:24:46Z (Task 0.23)

- Completed: Task 0.23 (add the `mcp` SDK's `streamable-http` transport as
  a third `specmgr mcp --transport` option), all 8 sub-tasks from TSK
  `aaf70093-8a7c-4565-9985-3beaa85e1d3d`:

  - Extended `commands/mcp.py`'s `--transport`/`-t` Typer option (help
    text, `show_default`, `SPECMGR_MCP_TRANSPORT` envvar description) to
    accept `"streamable-http"` alongside the existing `"stdio"`/`"sse"`.
  - Added a `streamable-http` branch in the `mcp()` command function,
    calling `_warn_on_public_binding(host)` (same as the `sse` branch)
    then `mcp_server.run(transport="streamable-http", host=host, port=port, stateless_http=True)` — `stateless_http=True` set
    explicitly to match this server's already-stateless `_lifespan`.
  - Updated `commands/mcp.py`'s module docstring with a third
    `streamable-http` bullet and usage example, and `README.md`'s MCP
    section (`--transport` table row + a short usage example mirroring
    the existing `sse` one).
  - Extended `tests/commands/test_mcp.py` with a new `TestMcpCommand`
    class asserting `mcp_server.run` is called correctly for all three
    branches (`stdio`, `sse`, `streamable-http`) — no prior test exercised
    the `mcp()` command function's branches directly, so symmetric
    coverage was added for all three, not just the new one.
  - Regenerated `docs/api/`/`docs/GENERATED.md`; verified
    `ruff format --check`/`ruff check`/
    `vulture src/ whitelist.py --min-confidence 60` (all clean) and the
    full `unittest` suite (1195 tests, all passing, up from 1192).
  - Purely a transport-wiring change confined to `commands/mcp.py` (plus
    its tests/docs) — no changes to `server.py`, tools, resources, or
    prompts, since MCP transport is orthogonal to protocol-era/tool logic.

#### Update 2026-08-18T21:32:28Z (Task 0.21)

- Completed: Task 0.21 (new `compact_history` MCP prompt), all 5
  sub-tasks:

  - Added `general/prompts/__init__.py` and
    `general/prompts/compact_history.py`
    (`@mcp.prompt(name="compact_history")`, params `feature_id: str` and
    optional `cutoff_hint: str | None`), the first prompt under `general/`
    (which previously had `tools`/`resources` only). Instructional text
    lives in a new packaged data file,
    `general/data/general_compact_history_instructions.md`, loaded via
    `read_packaged_text("general", "compact_history_instructions", "md")`
    - `string.Template` (`$feature_id`/`$cutoff_hint`), following the
      `refine` reference pattern exactly.
  - The instructions guide the LLM through: locating
    `.specmgr/feat/<feature_id>/README.md` (and sibling `history.md` if
    present) via its own file tools (no dedicated specmgr tool exists for
    feature folders); asking the user via the `question` tool for the
    rotation cutoff when ambiguous; moving older `#### YYYY-MM-DD` entries
    verbatim into `history.md` (creating it if absent); updating the
    `README.md` pointer line (`See \`history.md\` for updates before
    YYYY-MM-DD.`); bumping frontmatter `updated`; and verifying each moved entry appears exactly once in `history.md\` and nowhere else.
  - Registered `compact_history` in `general/__init__.py`'s
    imports/`__all__`/docstring and `server.py`'s module docstring
    (`Prompts` section plus the package-shape paragraph, now noting
    `general` registers `tools`/`resources`/`prompts` like `req`/`tsk`/
    `qa`).
  - Added `tests/general/prompts/test_compact_history.py` (12 tests),
    mirroring `tests/qa/prompts/test_refine.py`'s shape: parameter
    interpolation, key-instruction content checks, and the
    fresh-read-per-call/missing-file `FileNotFoundError` pair via
    `mock.patch.object(_packaged_data, "packaged_data_path", ...)`. No
    live run against this feature folder itself, since it was already
    manually compacted on 2026-08-18 ahead of this task — there was
    nothing left to rotate.
  - Regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`; verified
    `ruff format --check`/`ruff check`/
    `vulture src/ whitelist.py --min-confidence 60` (all clean) and the
    full `unittest` suite (1192 tests, all passing, up from 1180).

- Completed: Task 0.18 (Fix `MarkdownListItem.get_extent` for numbered lists), TSK `602740af-0445-48d8-bcc3-18df541dad72`:

  - Fixed `MarkdownListItem.get_extent` in `markdown_list_item.py` to correctly handle continuation paragraphs in loose numbered lists by detecting single-item ordered lists (where `ordered_list_open.map[1] == list_item_open.map[1]`) and scanning for `paragraph_open` tokens between `ordered_list_close` and the next `ordered_list_open`.
  - Added 6 new test cases to `tests/models/md/test_markdown_list_item_with_notes.py` covering tight/loose numbered items with 0-2 continuation paragraphs (parsing verification; loose numbered lists don't round-trip byte-exact due to mdformat stripping indentation — documented as accepted limitation).
  - Verified REQ domain integration: `tests/req/tools/test_get_req.py::test_returns_matching_document` passes with original fixture containing numbered list with continuation paragraph.
  - All 1013 tests pass; `ruff format --check`, `ruff check`, `vulture` clean; no regressions in REQ/UC/TSK domains.

- Completed: Task 0.19 (new `refine` QA prompt), both sub-tasks:

  - Added `qa/prompts/refine.py` (`@mcp.prompt(name="refine")`): appends a
    requested count of new, unanswered `> {question}` /
    `_(awaiting response)_` Q&A pairs to one or more of the nine ISO/IEC
    25010:2023 characteristic sections of an existing QA document.
    Resolves its target via `specmgr://qa/list` (id or title) + `get_qa`;
    grounds each question in `specmgr://iso25010`'s real characteristic
    definitions; uses the `question` tool when the count/characteristics
    are ambiguous; whole-body-replaces via `update_qa`; tells the user to
    fill in the placeholders and then run the separate, not-yet-built
    `/resolve` command next (this prompt never runs it itself). Registered
    in `qa/prompts/__init__.py` and `server.py`'s module docstring; 12
    tests added in `tests/qa/prompts/test_refine.py`.
  - Task 0.19.1: retrofitted `refine`'s instructional text out of an
    inline `_INSTRUCTIONS_TEMPLATE` string (matching every other prompt
    module at the time) into a new packaged data file,
    `qa/data/qa_refine_instructions.md`, loaded via
    `read_packaged_text("qa", "refine_instructions", "md")` — reusing the
    `qa_example.md`/`qa_template.md`/`qa_schema.json` packaging
    convention for prompt instructions for the first time. Switched
    placeholder substitution from `str.format` to `string.Template`
    (`$id_or_name`/`$scope`) so the packaged file needs no `{{`/`}}`
    brace-escaping for its own literal Q&A placeholders. Added 2 more
    tests (fresh-read-per-call, missing-file `FileNotFoundError`),
    mirroring `tests/uc/resources/test_uc_example.py`'s
    `mock.patch.object(_packaged_data, "packaged_data_path", ...)`
    pattern.
  - Task 0.19.2: regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`;
    verified `ruff format --check`/`ruff check`/
    `vulture src/ whitelist.py --min-confidence 60` (all clean) and the
    full `unittest` suite (1158 tests, all passing, up from 1156).
  - Added Task 0.20 (not started) to track applying this same
    packaged-instructions-file pattern to the remaining 11 prompt modules
    across `adr`/`req`/`tsk`/`qa`.

- Completed: Compacted this file's own `Recent Updates` history ahead of
  Task 0.21 (manually, since the `compact_history` prompt it will add
  doesn't exist yet): moved the 2026-08-17/2026-08-16/2026-08-15 entries
  verbatim into a new sibling `history.md`, per ADR
  e369ee2e-3353-4f92-991c-6367d76d832e's rotation mechanism, and left this
  section holding only the 2026-08-18 entry plus a pointer note. Verified
  every archived entry appears exactly once in `history.md` and nowhere
  in this file (grep spot-checks on unique fragments); `README.md` shrank
  from 923 to 654 lines.

- Completed: Task 0.20 (packaged-instructions-file retrofit for the
  remaining 11 prompt modules), all five sub-tasks, delegated as four
  parallel per-domain batches (ADR/REQ/TSK/QA) each following the
  `refine`/`qa_refine_instructions.md` reference pattern exactly:

  - Task 0.20.1 (ADR): converted `create_adr`/`create_adr_test`/
    `update_adr`/`update_adr_test`; created a brand-new `adr/data/`
    package (ADR previously had none, since its schema lives at
    top-level `models/adr/`) and registered
    `"biz.dfch.specmgr.adr" = ["data/*.md"]` in `pyproject.toml`.
  - Task 0.20.2 (REQ): converted `create_req`/`update_req` into the
    already-existing `req/data/`.
  - Task 0.20.3 (TSK): converted `create_task`/`update_task`/
    `implement_task` into the already-existing `tsk/data/`, keeping the
    `tsk_*` file prefix (not `task_*`) consistent with
    `tsk/data/tsk_example.md`.
  - Task 0.20.4 (QA): converted `create_qa`/`update_qa` into the
    already-existing `qa/data/`, alongside `qa_refine_instructions.md`.
  - Task 0.20.5: regenerated `docs/api/`/`docs/GENERATED.md`/`docs/MCP.md`;
    verified `ruff format --check`/`ruff check`/
    `vulture src/ whitelist.py --min-confidence 60` (all clean) and the
    full `unittest` suite (1180 tests, all passing, up from 1158 — 22 new
    tests: 2 per converted module).
  - Every module's public `@mcp.prompt()` signature, decorator arguments,
    and docstring Parameters/Returns sections were left unchanged; only
    the internal instruction-loading mechanism and each module's
    docstring gained a short explanatory paragraph.

### Decisions Made

- **2026-08-15**: Use a shared feature folder (`feat-0-various-improvements`,
  later renamed to `feat-7-various-improvements` once issue #7 was opened)
  as a home for small cross-cutting concerns rather than one folder per
  concern — rationale: per-concern folders would be disproportionately
  small relative to the ADR's per-feature template overhead; this can be
  split later if any tracked concern grows.
- **2026-08-15**: `AdrSummary`/`ReqSummary`'s fallback identifier field is
  named `ref`, not `filename`, and holds the extensionless base name
  (`path.stem`), not the raw on-disk filename (`path.name`) — rationale:
  a field literally called `filename` invites an LLM caller to go read the
  file directly off disk instead of calling `get_adr`/`get_req`/
  `specmgr://{adr,req}/{id}`, which is the whole point of exposing these
  as MCP resources in the first place.
- **2026-08-15**: Recorded as ADR `ddfb1109-422d-4507-8dbc-dc5e4bec9614` —
  add a `get_req` tool and remove `specmgr://req/{id}` entirely (REQ
  becomes tool-only for id-based reads), while deliberately leaving
  `specmgr://adr/{id}` coexisting with `get_adr` untouched. Future document
  domains (`uc`/`get_uc`, `ac`/`get_ac`, ...) should follow the REQ
  (tool-only) precedent rather than the older ADR one, absent a specific
  reason to add a resource counterpart.
- **2026-08-16**: Standardized the not-found error message (Task 0.13) as
  one template applied identically across `AdrNotFoundError`/
  `ReqNotFoundError`/`UcNotFoundError`/`TskNotFoundError`/`DocNotFoundError`:
  `f"no {noun} found with id {id_!r}. The id must be the bare document UUID, without a domain prefix (use '<uuid>', not '{prefix}-<uuid>')."`,
  with `noun`/`prefix` = ADR/adr, requirement/req, use case/uc, task
  list/tsk; the shared, domain-agnostic `DocNotFoundError` keeps the same
  closing sentence minus the prefix example, since
  `find_doc_path_by_id` has no `type_name` to derive one from. Rationale:
  a single wording, decided once and reused everywhere, is easier to keep
  consistent than one bespoke message per domain, and explicitly naming
  the bare-uuid-no-prefix requirement addresses the actual agent mistake
  (passing `"req-<uuid>"`/`"tsk-<uuid>"` etc. instead of the bare id) this
  task was opened to fix.
- **2026-08-16**: For Task 0.14's `webfetch` MCP tool: implement it as a
  *generic* bearer-authenticated GET fetch (caller supplies the full target
  URL) rather than Web Server-page-ID-specific logic like the existing
  `Web Server` agent skill; use `httpx` (promoted from a transitive to a
  direct dependency in the `mcp` extra) rather than stdlib `urllib.request`,
  since `httpx` is already pulled in transitively by the `mcp` package;
  return the raw response body text with no HTML-to-markdown/JSON parsing;
  match the configured `SPECMGR_WEBFETCH_BASE_URL` prefix case-
  insensitively; raise custom typed exceptions
  (`WebfetchNotConfiguredError`, `WebfetchUrlNotAllowedError`) on
  misconfiguration or a disallowed URL, matching this repo's house style of
  typed exceptions over error-dict returns; place it at
  `general/tools/webfetch.py` (cross-cutting, not domain-specific),
  registered as MCP tool `webfetch`. Rationale: keeps the tool minimal and
  reusable beyond Web Server, avoids adding an HTML-to-markdown dependency,
  and follows existing conventions (`_paths.py`-style env-var handling,
  typed exceptions, `general/` for cross-cutting tools) rather than
  inventing new ones.
- **2026-08-18**: For Task 0.21's `compact_history` prompt: it operates
  purely via the LLM's own file read/edit/write tools directly on
  `README.md`/`history.md`, not through any new specmgr tool, since
  feature folders (unlike ADR/REQ/UC/TSK/QA) have no dedicated
  parser/get/update MCP tool of their own and adding one was judged out
  of scope for this task; the exact rotation trigger/cutoff is resolved
  at prompt-run time via the `question` tool (per ADR
  e369ee2e-3353-4f92-991c-6367d76d832e's own "Open Questions" note that
  this is deliberately not prescribed), not hardcoded into the prompt.
  Verification for this task is unit tests only (fixtures), not a live
  re-run against this feature folder, since its own `Recent Updates` was
  already manually compacted on 2026-08-18 ahead of this task and there
  was nothing left to rotate.
- **2026-08-19**: For Task 0.23's `streamable-http` transport: set
  `stateless_http=True` explicitly on the new branch's `mcp_server.run(...)`
  call, rather than leaving it at the SDK's own default — rationale:
  matches this server's already-stateless `_lifespan` (`server.py`) and
  aligns with the modern MCP protocol era's stateless-per-request session
  model, so a caller never accidentally depends on session state that
  `stdio`/`sse` never provided either.
- **2026-08-19**: For Task 0.22's cyclic-import investigation: the
  `set_status_qa.py` -> `server.py` cycle is real but universal across every
  domain, not qa-specific, and currently benign only due to `server.py`'s
  import ordering; recorded ADR `3bf0326f-065a-424c-a2b9-87e5d5bcfa99`
  choosing to extract a new `mcp_instance.py` leaf module as the fix
  (`server.py` and every domain file import the `MCPServer` singleton from
  there instead of from `server.py`), with the ~80-file mechanical refactor
  itself deferred to TSK `699432f5-6f95-498e-a269-8001e4afc0e5` rather than
  performed now — rationale: keeps this housekeeping task small (examine +
  decide) and lets the refactor be scheduled/executed independently.
- **2026-08-26**: For Task 0.24, close with verification + normalization
  rather than as a no-op: the flagged `AGENTS.md` drift was found already
  removed upstream (feat-13's close-out commit `452e125`, 2026-08-19 —
  before the 2026-08-25 flag), but the five older-domain bullets were
  normalized to the explicit "no `specmgr://<d>/list` — listing is the
  `list_<d>` tool" convention the newer `prb`/`gol`/`rsk` bullets already
  carry — rationale: `AGENTS.md` is a quick-reference doc whose job is to
  stop agents from assuming a `specmgr://<d>/list` resource exists, and
  "not mentioned" is weaker than "explicitly noted absent" for that
  purpose (the false flag itself shows how easily the assumption creeps
   back). The three model-docstring stragglers were fixed in the same pass
   (user instruction, 2026-08-26) rather than filed as a follow-up task.
- **2026-08-26**: For Task 0.25, reworded AGENTS.md's remaining per-type
  enumerations as rules instead of keeping them: the "Models location"
  paragraph now states the rule (every doc type's schema lives in
  `<domain>/models/vN/`; ADR is the single exception at top-level
  `models/adr/`), the Status heading drops its count+domain-list
  duplicate, and the closing "Don't assume …" paragraph points at the
  per-domain bullets instead of carrying a second copy of the list —
  rationale: the per-domain bullets are the one enumeration that must
  exist anyway (each carries domain-specific facts: tool/resource/prompt
  names, schema version, sub-package exceptions), so the other three
  lists were pure duplicates, and their drift cost is what feat-18
  Phase 4 just demonstrated (~6 AGENTS.md edits for `gol` alone). Two
  spots deliberately left enumerated: the `MCP server (server.py)`
  paragraph's domain-import list (it documents the actual code line a
  new domain must touch — its "drift" is the instruction itself) and
  the "Still genuinely missing / not yet done" list (a dynamic gap
  tracker, not a package inventory).

### Related PRs / Commits

None yet.
