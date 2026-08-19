# History: feat-7-various-improvements

Archived older `Recent Updates` entries for
`.specmgr/feat/feat-7-various-improvements/README.md`, rotated out per ADR
e369ee2e-3353-4f92-991c-6367d76d832e ("Organize development artifacts in
`.specmgr` with feature-driven work units"), which documents this optional
sibling file as the destination for entries once a feature's own `Recent Updates` section grows too long. This file holds every entry from before
2026-08-18; `README.md`'s own `Recent Updates` section keeps 2026-08-18
onward and links back here.

## Recent Updates

#### 2026-08-17T21:17:58Z

- Completed: Task 0.17 (MarkdownListItemWithNotes for captured continuation paragraphs), TSK `f581fb2f-9a82-11f1-9c57-fc4cea71c519`:
  - Added `MarkdownListItemWithNotes` class to `markdown_list_item.py` with `notes: list[MarkdownParagraph] | None = None` field; docstring mirrors `ExtensionItem`; delegated `get_extent`/`from_text`/`__str__`.
  - Updated `req/models/v1/body.py`'s `Characteristics.items` to use `MarkdownListItemWithNotes`; created fixture `docs/req/test-loose-list-with-continuation.md`.
  - Updated `uc/models/v2/use_case.py`'s `ExtensionItem` to derive from `MarkdownListItemWithNotes` (replacing inline `notes` field with inheritance).
  - Added `tests/models/md/test_markdown_list_item_with_notes.py` with 16 tests covering parsing, serialization/JSON, round-trips for tight/loose items (0-2 continuation paragraphs), compact items, and REQ-domain `Characteristics.items` integration. All 16 pass; full suite 1004 tests all passing — no regressions in REQ/UC/TSK domains.
  - Verified clean: ruff format/check (0 issues), vulture (unused code), pre-commit hook schema regen (req+uc schemas updated for new model type).

#### 2026-08-16T21:23:33Z

- In progress: Task 0.14 (`webfetch` MCP tool for Web Server). Clarified
  scope with the user (generic bearer-authenticated GET fetch, not
  Web Server-page-ID-specific; `httpx` over stdlib `urllib`; raw response
  body returned; custom typed exceptions on misconfiguration/disallowed
  URL; case-insensitive base-URL prefix match; `general/tools/webfetch.py`,
  tool name `webfetch`) and created the implementation-plan task list, TSK
  `efb7d049-a222-4730-901f-6d57283b387c` ("Implement `webfetch` MCP Tool
  (Bearer-Authenticated, URL-Filtered Fetch for Web Server)", 10 tasks).
  Task 0.14's own line above updated to remove the original inline
  instructions and point at this TSK id. Implementation itself has not
  started yet.
- Completed: Task 0.14 (`webfetch` MCP tool for Web Server), all 11 tasks
  from TSK `efb7d049-a222-4730-901f-6d57283b387c`: `httpx` promoted to a
  direct dependency in the `mcp` extra; `general/tools/webfetch.py` added
  (`SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER` env vars,
  `WebfetchNotConfiguredError`/`WebfetchUrlNotAllowedError`, the `webfetch`
  MCP tool itself using `httpx.get(..., follow_redirects=True)`); registered
  in `general/tools/__init__.py` with docstrings updated in
  `general/__init__.py` and `server.py`; 8 mocked tests added in
  `tests/general/tools/test_webfetch.py` (URL-filter rejection, case-
  insensitive base-URL matching on both sides, missing-config errors,
  successful bearer-header fetch, non-2xx raise); `docs/api/`,
  `docs/GENERATED.md`, and `docs/MCP.md` regenerated; `README.md`'s
  Environment Variables section documents the two new env vars; verified
  clean via `ruff format --check`/`ruff check`/
  `vulture src/ whitelist.py --min-confidence 60`/full `unittest` suite (988
  tests). TSK `efb7d049-a222-4730-901f-6d57283b387c` itself updated to
  `status: done`, and Task 0.14's line above updated to point at it with
  `status: done`.
- Completed: Task 0.13 (standardize the not-found error message across
  `get_adr`/`get_req`/`get_uc`/`get_tsk`), all 9 sub-tasks from TSK
  `266eb332-795b-48c4-9bc0-7115eb209378`:
  - Decided and recorded the standardized wording template (see Decisions
    Made) — explicitly tells the caller the id must be the bare document
    UUID, without a domain prefix, and shows the offending-vs-correct
    shape via a `'<uuid>'`/`'{prefix}-<uuid>'` example.
  - Applied it to `adr/tools/_paths.py`'s `AdrNotFoundError`,
    `req/tools/_paths.py`'s `ReqNotFoundError`,
    `uc/tools/_paths.py`'s `UcNotFoundError`, and
    `tsk/tools/_paths.py`'s `TskNotFoundError` (replacing its earlier,
    grammatically rough first-pass hint), plus the shared
    `general/tools/_doc_paths.py`'s `DocNotFoundError` for consistency.
  - Extended `tests/adr/tools/test_paths.py`,
    `tests/req/tools/test__paths.py`, `tests/uc/tools/test__paths.py`,
    `tests/tsk/tools/test__paths.py`,
    `tests/general/tools/test__doc_paths.py`, and each domain's
    `tests/<domain>/tools/test_get_<type>.py` to assert on the new
    message content, not just the raised exception type.
  - Verified: `ruff format --check`/`ruff check` (clean),
    `vulture src/ whitelist.py --min-confidence 60` (clean), and the full
    `unittest` suite (all passing).
- Completed: Task 0.8 (`specmgr://iso25010` resource) end to end, via
  sub-tasks 0.8.3-0.8.9 (0.8.1/0.8.2 were already done in an earlier
  session, see below):
  - Added `general/resources/iso25010.py` (`@mcp.resource("specmgr://iso25010", name="iso25010", ..., mime_type="application/json")`), wrapping
    `parse_iso25010(read_packaged_text("general", "iso25010", "md"))`,
    mirroring `req/resources/req_schema.py`'s packaged-data-read style; registered
    it in `general/resources/__init__.py` (import + `__all__`).
  - Updated `general/__init__.py`'s module docstring to mention `iso25010`
    alongside `version`; updated `server.py`'s Resources list with
    `specmgr://iso25010` and fixed its stale "top-level `resources` package"
    wording left over from Task 0.12's move of `resources/` into
    `general/resources/`.
  - Added `tests/models/test_iso25010.py` (5 tests: instance type, 9
    names/9 characteristics, leading-comment capture, and two
    characteristic/sub-characteristic spot-checks — Functional Suitability
    and Safety) and `tests/general/resources/test_iso25010.py` (2 tests,
    mirroring `tests/general/resources/test_version.py`).
  - Regenerated `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and
    `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13 — now 7 resources (up
    from 6).
  - Verified: `ruff format --check`/`ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), and the full `unittest`
    suite (791 tests, all passing, up from 784).
- Corrected: User hand-edited both `product-quality-model.md` (dropped the
  intro sentence "The product quality model consists of 9 main
  characteristics:" between the H1 and the bullet list) and
  `models/iso25010.py` (dropped the `intro: MarkdownParagraph` field
  entirely; changed `names`/`characteristics` from `min_length=1` to
  `min_length=9, max_length=9`, enforcing the exact expected count) after
  Task 0.8.1/0.8.2 were first marked done above. Re-synced
  `general/data/general_iso25010.md` from the updated source (straight
  copy, `mdformat` reports no change needed) and re-verified end-to-end:
  `parse_iso25010` still parses 9 characteristics/9 names correctly, the
  copyright comment is still captured, `ruff format` (the edited model
  file needed one collapse-to-one-line fix, now clean), `ruff check`,
  `vulture src/ whitelist.py --min-confidence 60` (clean), and the full
  `unittest` suite (784 tests, all passing). Task 0.8.1/0.8.2's
  descriptions above updated in place to match the corrected design.
- Completed: Task 0.8.2 — added `src/biz/dfch/specmgr/models/iso25010.py`
  (flat, unversioned): `SubCharacteristic(MarkdownSection3)` and
  `Characteristic(MarkdownSection2)` (both `@alias(value=".+", type=AliasType.REGEX)`, each with a `description: MarkdownParagraph`
  field, plus `sub_characteristics: list[SubCharacteristic]` (`min_length=1`)
  on `Characteristic`); `Iso25010(MarkdownSection1)` as the H1 container
  with `intro: MarkdownParagraph`, `names: list[MarkdownListItem]`
  (`min_length=1`), `comment: MarkdownComment | None`, and
  `characteristics: list[Characteristic]` (`min_length=1`), in document
  order; and `parse_iso25010(text) -> Iso25010`, a thin `format_text` +
  `Iso25010.from_text` wrapper. Re-exported `Iso25010`, `Characteristic`,
  `SubCharacteristic`, `parse_iso25010` from `models/__init__.py`. Added
  `sub_characteristics` to `whitelist.py` (vulture false positive — a
  Pydantic field only read via (de)serialization). Verified end-to-end by
  parsing the packaged `general_iso25010.md` (9 characteristics, 9 names,
  intro text as expected); `ruff format --check`/`ruff check` (clean),
  `vulture src/ whitelist.py --min-confidence 60` (clean), and the full
  `unittest` suite (784 tests, all passing, unchanged — no new tests added
  yet; that is Task 0.8.5). Per Task 0.8.2's note, pausing here for the
  user before starting Task 0.8.3 (`general/resources/iso25010.py`).
- Completed: Task 0.8.1 — copied
  `.specmgr/feat/feat-7-various-improvements/product-quality-model.md`
  verbatim to the new packaged data file
  `src/biz/dfch/specmgr/general/data/general_iso25010.md` (source file was
  already hand-edited into the target shape ahead of this task: no `N. `
  numbering on `##` characteristic headings, every sub-characteristic
  already a nested `###` heading, and the copyright/fair-use sentence
  already a leading HTML comment) — `diff` confirms byte-for-byte identity
  and `mdformat` reports no change needed (already canonical). Added a
  `"biz.dfch.specmgr.general" = ["data/*.md"]` entry to `pyproject.toml`'s
  `[tool.setuptools.package-data]`. Per Task 0.8.2's note, pausing here for
  the user before starting `models/iso25010.py`.
- Completed: Task 0.12 — moved the top-level `resources/` package into
  `general/resources/`.
  - `src/biz/dfch/specmgr/resources/{__init__.py,version.py}` (the
    `specmgr://version` resource) moved to
    `src/biz/dfch/specmgr/general/resources/{__init__.py,version.py}` via
    `git mv`, since it is itself a cross-cutting, not domain-specific,
    concern, consistent with `general/tools/`.
  - `general/resources/version.py`'s relative imports adjusted for the new
    nesting depth (`..models`/`..server` → `...models`/`...server`).
  - `general/__init__.py` updated to import/re-export `resources` alongside
    `tools`, with its module docstring rewritten to describe both.
  - `server.py`'s registration import simplified from
    `from . import adr, general, req, resources, uc` to
    `from . import adr, general, req, uc`, since `general` now pulls in its
    own `resources` sub-package.
  - `tests/resources/` moved to `tests/general/resources/`
    (`test_version.py`'s import updated to
    `biz.dfch.specmgr.general.resources.version`).
  - Updated `tests/commands/test_docs.py`'s
    `test_collect_module_docs_finds_domains` (asserted on the now-gone
    top-level `"resources"` domain key; now asserts `"general"`, which
    subsumes it) and `AGENTS.md`'s description of `general/` and its
    "check first" caveat.
  - Deleted the now-orphaned `docs/api/biz.dfch.specmgr.resources.md`/
    `biz.dfch.specmgr.resources.version.md` and regenerated
    `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md`
    (`specmgr mcp-docs`, no diff — tool/resource registration unchanged).
  - Added a `CHANGELOG.md` entry under `[Unreleased]`.
  - Verified: `ruff format --check`/`ruff check` (clean),
    `vulture src/ whitelist.py --min-confidence 60` (clean), and the full
    `unittest` suite (784 tests, all passing).
- Completed: Task 0.11 — added the `specmgr mdformat <path>` CLI command.
  - Extracted the frontmatter-aware formatting logic out of
    `general/tools/mdformat.py` into a new, pure (disk-free)
    `format_markdown_document(text) -> tuple[bool, str]` helper in
    `models/md/_markdown.py` — the single shared implementation now used by
    both the `mdformat` MCP tool and the new CLI command.
  - Refactored `general/tools/mdformat.py` to call the shared helper;
    its own behavior/signature/tests are unchanged.
  - Added `commands/mdformat.py`: `specmgr mdformat <path>` formats a file
    in place by default; `--dry-run`/`-d` prints the formatted result via
    `rich.markdown.Markdown` instead of writing to disk. Both modes compare
    original vs. formatted content in memory and use the same exit-code
    contract: `0` = no change (already canonical), `1` = a change was
    detected (written to disk unless `--dry-run`). No content validation is
    performed; a missing/unreadable file is not caught and propagates as an
    uncaught exception (consistent with the MCP tool's own behavior).
  - Registered the command in `commands/__init__.py` and `cli.py`.
  - Added `tests/models/md/test__markdown.py` (7 tests) for the new shared
    helper and `tests/commands/test_mdformat.py` (6 tests) for the CLI
    command; all pre-existing `tests/general/tools/test_mdformat.py` tests
    still pass unchanged (behavior preserved).
  - Verified: `ruff format --check`/`ruff check` (clean),
    `vulture src/ whitelist.py --min-confidence 60` (clean), full
    `unittest` suite (784 tests, all passing, up from 771), and
    regenerated `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) plus
    `docs/MCP.md` (`specmgr mcp-docs`, no diff — tool description text
    unchanged).
- Next: Phase 1 audit — inventory current list resources and prompt
  modules; Task 3.1b (pagination) still open; Task 0.6/0.7/0.10 also
  still not started.

#### 2026-08-15T08:39:25Z

- Completed: Created `feat-0-various-improvements` with initial scope
  (list-resource format standardization + prompt optimizations, including
  the `_test` prompt-variant decision).
- Completed: Opened [GitHub issue #7](https://github.com/dfch/biz.dfch.SpecMgr/issues/7)
  and renamed the folder to `feat-7-various-improvements` accordingly
  (frontmatter `id` updated to match).
- Completed: Phase 0 housekeeping — backfilled GitHub issue numbers for
  the two other `feat-0-*` folders (`feat-0-coverage-badge` → issue #8 →
  `feat-8-coverage-badge`; `feat-0-doc-in-specmgr` → issue #9 →
  `feat-9-doc-in-specmgr`), including fixing ~20 live cross-references to
  the renamed path and regenerating `docs/api/`/`docs/GENERATED.md`. See
  Phase 0 in the Task List for the full breakdown.
- Completed: Renamed `AdrSummary.filename`/`ReqSummary.filename` to `ref`
  and changed its value to the extensionless base name (`path.stem`
  instead of `path.name`) in `adr_list`/`req_list`, with matching resource
  description/docstring updates and new test coverage
  (`tests/adr/resources/test_adr.py`, `tests/req/resources/test_req_list.py`).
  Verified with `ruff format --check`/`ruff check` (clean) and the full
  `unittest` suite (771 tests, all passing), and regenerated `docs/api/`.
- Corrected: The `filename` → `ref` change above was implemented directly
  from a request that only asked for it to be logged as a task — user
  flagged this as jumping ahead without confirmation. Reverted all of it
  (`git checkout --` on the touched source/test files, then re-ran
  `specmgr docs` to bring `docs/api/` back in sync).
- Completed: User then clarified the implementation should in fact be
  kept, not reverted — re-applied the identical `filename` → `ref` change
  (models, resources, tests, docstrings) by hand, re-verified with
  `ruff format --check`/`ruff check` (clean) and the full `unittest` suite
  (771 tests, all passing), and regenerated `docs/api/` again. Net effect
  matches the entry above; recorded here for the process lesson: confirm
  scope (log-only vs. implement) before writing code on an ambiguously
  worded request.
- Completed: Task 0.9 (`get_req` MCP tool) end to end, via sub-tasks
  0.9.1-0.9.13:
  - Wrote ADR `ddfb1109-422d-4507-8dbc-dc5e4bec9614` ("Expose id-based REQ
    document reads as a tool (get_req), not a resource") recording the
    decision and its rationale.
  - Added `req/tools/get_req.py` (`@mcp.tool(name="get_req")`), mirroring
    `adr/tools/get_adr.py`, and registered it in `req/tools/__init__.py`.
  - Removed `req/resources/req_get.py` (the `specmgr://req/{id}` resource)
    and its registration/docstring in `req/resources/__init__.py`; deleted
    the now-orphaned `docs/api/biz.dfch.specmgr.req.resources.req_get.md`.
  - Updated `req/__init__.py` and `server.py`'s module docstrings to match
    the new tool/resource surface.
  - Updated `req/prompts/update_req.py`'s "read current state first" step
    to call `get_req(id)` instead of reading the removed resource.
  - Added `tests/req/tools/test_get_req.py` (mirrors
    `tests/adr/tools/test_get_adr.py`); removed
    `tests/req/resources/test_req_get.py`; updated
    `tests/req/prompts/test_update_req.py`'s assertions accordingly.
  - Regenerated `docs/api/`/`docs/GENERATED.md` (`specmgr docs`) and
    `docs/adr/README.md` (`specmgr adr-toc`).
  - Annotated `feat-6-requirement-artifact/README.md` Task 3.17 with a
    pointer to this decision, without rewriting its existing history.
  - Verified: `ruff format --check`/`ruff check` (clean, after also fixing
    unrelated pre-existing trailing-whitespace in
    `req/prompts/create_req.py` that was blocking a clean `ruff check`),
    and the full `unittest` suite (771 tests, all passing). `specmgr://adr/{id}`
    (`adr_get`) was deliberately left coexisting with `get_adr`, unchanged.
- Notes: Found the working tree already carrying unrelated, uncommitted
  changes predating this session (the `filename` → `ref` rename touching
  `adr_list`/`req_list`/`AdrSummary`/`ReqSummary`, plus three new
  `docs/req/*.md` requirement documents and an unrelated edit to
  `req/prompts/create_req.py`) — left as-is, out of scope for Task 0.9.
  `vulture` also flags two pre-existing `unused variable 'ref'` warnings
  from that same rename in `whitelist.py`-adjacent files; confirmed via
  `git stash` that these predate Task 0.9's changes and are not caused by
  `get_req`. Not fixed here — candidate follow-up task if this feature's
  Phase 3.1b/pagination work revisits the same files.
- Next: Phase 1 audit — inventory current list resources and prompt
  modules; Task 3.1b (pagination) still open.
- Notes: This folder is a rolling bucket for cross-cutting concerns; split
  any single concern into its own `feat-NNN-slug` folder if it grows large
  enough to need its own dedicated requirements/acceptance criteria.
