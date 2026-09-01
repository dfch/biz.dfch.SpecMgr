---
created: '2026-08-26 00:00:00.000Z'
id: feat-22-consolidate-mutation-tools
status: done
updated: '2026-08-27 00:00:00.000Z'
version: 1.0.0
---

# Feature: Consolidate update and set_status tools into generic type-dispatched tools

## Plan

### Overview

Replace the 15 near-duplicate per-domain mutation MCP tools with two generic,
cross-cutting tools that live in `general/tools/`: `update(id, type, content,
begin, end)` for whole-body (and now line-range) document replacement across
the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`),
and `set_status(id, type, status, superseded_by)` for status changes across
all eight domains including `adr`. The per-domain tools
(`update_req`/`update_uc`/`update_tsk`/`update_qa`/`update_prb`/`update_gol`/
`update_rsk`, `set_status_req`/`set_status_uc`/`set_status_tsk`/`set_status_qa`/
`set_status_prb`/`set_status_gol`/`set_status_rsk`, and ADR's own `set_status`)
are deleted outright (breaking; the package is 0.x and the MCP tool list is the
only contract). The generic `update` gains optional 1-based, inclusive
`begin`/`end` body-line parameters so a client can replace a line range
without re-sending the whole body — spliced into the current on-disk body and
validated as a *whole* document before anything is written (the
filesystem-is-source-of-truth and validate-before-write invariants are
untouched). To make line targeting reliable, the seven `get_<d>` tools gain an
optional `raw: bool = False` parameter returning the frontmatter-stripped body
text verbatim — the exact text `begin`/`end` index into (tool-first per ADR
ddfb1109; re-introducing `specmgr://<d>/{id}` resources was considered and
rejected). ADR keeps its section-level mutation surface
(`update_frontmatter`/`update_section`/`option_*`) unchanged — ADR is
deliberately *excluded* from `update` because it has no whole-body replace by
design (MADR contract), but is *included* in `set_status` with its
`superseded_by`-composition special case. A short ADR records the new
conventions so future domains (e.g. `ac`) add one dispatch entry instead of a
new tool. Expected end state: **71 tools / 25 resources / 19 prompts**
(today 84/25/19: −15 +2).

### Requirements

- REQ-001: A generic `update(id, type, content)` MCP tool in
  `general/tools/update.py` covering the seven whole-body domains
  (`type: Literal["req","uc","tsk","qa","prb","gol","rsk"]`), preserving each
  domain's existing whole-body semantics 1:1: body-only `content` (no
  frontmatter block) validated via the domain's own
  `X.from_text(format_text(content))` two-channel contract
  (`AssertionError` structural / `pydantic.ValidationError` field-level,
  nothing written on failure); under the domain's own lock, `load_by_id`,
  every frontmatter field preserved except `updated` (bumped to the current
  microsecond timestamp); `status` never settable through `update`; the
  caller's raw `content` persisted verbatim via the domain's `write_X_file`;
  unknown id raises the domain's own `XNotFoundError`.
- REQ-002: Optional `begin: int | None` / `end: int | None` parameters on
  `update`. When both are absent, behavior is exactly REQ-001 (backward-
  compatible default). When both are given, `content` is a replacement
  *fragment* for the current body's 1-based, inclusive line range
  `begin..end`, where `N` = number of lines of the current frontmatter-
  stripped body and `N+1` is a virtual position past the last line
  (`begin = end = N+1` → append at end of body; `end = N+1` → range extends
  through end of body). Misuse (exactly one of the two given, `begin < 1`,
  `begin > end`, `end > N+1`) raises `ValueError` with a clear message and
  writes nothing. The spliced *result* is validated as a whole body (REQ-001's
  validation contract) before writing; unchanged regions of the on-disk body
  remain byte-identical. An empty `content` fragment deletes the range (legal
  iff the result still validates). The YAML frontmatter is never addressable
  (coordinates are body-relative by construction).
- REQ-003: The seven `get_<d>` tools (`get_req`, `get_uc`, `get_tsk`,
  `get_qa`, `get_prb`, `get_gol`, `get_rsk`) gain an optional
  `raw: bool = False` parameter. `raw=False` (default) behaves exactly as
  today (returns the parsed `XDocument`). `raw=True` returns the
  frontmatter-stripped body text of the document verbatim as a plain string —
  produced by the *same* body-extraction helper the REQ-002 splice uses, so
  the text a client counts lines in is byte-for-byte the text the server
  splices against. Unknown id raises the domain's `XNotFoundError` in both
  modes. No `get_adr` change (ADR is not a `update` type).
- REQ-004: A generic `set_status(id, type, status, superseded_by=None)` MCP
  tool in `general/tools/set_status.py` covering all eight domains
  (`type: Literal["req","uc","tsk","qa","prb","gol","rsk","adr"]`). For the
  seven whole-body domains, semantics are preserved 1:1 from the deleted
  `set_status_<d>` tools: under the domain lock, `load_by_id`, the raw body
  re-read and re-persisted verbatim (body never touched), the frontmatter
  reconstructed through the domain's own `XFrontmatter` constructor so each
  domain's closed status vocabulary validates (invalid `status` →
  `pydantic.ValidationError`, nothing written), `updated` bumped, unknown id →
  domain `XNotFoundError`. For `type="adr"`, semantics are preserved 1:1 from
  the deleted ADR `set_status` tool: delegates to
  `models.adr.v1.mutations.set_status(adr, status, superseded_by)` (which
  composes `status` as `"superseded by {superseded_by}"` when
  `superseded_by` is given), `write_adr` render round-trip, `adr_lock`,
  `AdrNotFoundError`. `superseded_by` given with any `type` other than
  `"adr"` raises `ValueError` and writes nothing.
- REQ-005: The 15 superseded tools are removed from source and from MCP
  registration: `update_req`, `update_uc`, `update_tsk`, `update_qa`,
  `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
  `set_status_gol`, `set_status_rsk`, and ADR `set_status`. No deprecated
  wrappers are kept (user decision; 0.x breaking change, recorded in
  `CHANGELOG.md`).
- REQ-006: All prompt narration referencing the superseded tools is rewritten
  to the generic tools with correct signatures: the six domain
  `<d>_update_instructions.md` files (req, tsk, qa, rsk, prb, gol — `uc` has
  no prompts sub-package), `qa/data/qa_refine_instructions.md`, and the four
  ADR instruction files (`adr_create_instructions.md`,
  `adr_create_test_instructions.md`, `adr_update_instructions.md`,
  `adr_update_test_instructions.md` — their `set_status(id, …)` call sites
  gain `type="adr"`). The six domain update-instruction files additionally
  teach the REQ-002 range-update flow. Prompt Python module docstrings that
  name the superseded tools are corrected (6 domain `prompts/update_<d>.py`
  modules + 4 ADR prompt modules whose surface mentions become inaccurate).
  The 10 corresponding prompt test files (6 domain + 4 ADR) are updated to
  match the rewritten narration.
- REQ-007: Documentation and registration consistency: `server.py` module
  docstring (the authoritative tool/resource/prompt list) updated in the same
  phase that changes the surface it describes; `docs/MCP.md`, `docs/api/`,
  `docs/adr/README.md` regenerated with zero drift at every phase gate;
  `AGENTS.md` per-domain bullets and the `general/` bullet updated;
  `CHANGELOG.md` `[Unreleased]` carries the breaking-change and
  addition entries; a short ADR (Phase 1) records the conventions (explicit
  `type` over uuid-only resolution; ADR excluded from `update` but included
  in `set_status`; the REQ-002 range contract; the REQ-003 raw-read-over-
  resource decision; "future domains add one dispatch entry, not a new
  tool").

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — for every one of the seven types, `update`
  in whole-body mode (no `begin`/`end`) replaces the body, preserves
  `id`/`type`/`status`/`created`/`version`, bumps `updated` (microsecond
  timestamp), never sets `status`, propagates structural `AssertionError` /
  field `pydantic.ValidationError` with the file left byte-identical on disk,
  and raises the domain's own `XNotFoundError` for an unknown id. **PASS** —
  `tests/general/tools/test_update.py`'s `TestUpdateWholeBody` (5 test
  methods, each subTest-parameterized over all seven types, seeding a real,
  persisted document per type via the domain's own `create_<d>` tool in a
  temp `SPECMGR_DOCS_DIR`): `test_replaces_body_preserving_id_type_status_
  created_version` (body replaced; id/type/status/created/version
  preserved; `updated` bumped and matching the microsecond-timestamp shape),
  `test_status_not_settable_through_update` (a YAML frontmatter block
  smuggled into `content` → `AssertionError`, file untouched),
  `test_structural_failure_raises_and_leaves_file_byte_identical` (malformed
  body → `AssertionError`, file byte-identical),
  `test_field_validation_failure_raises_and_leaves_file_byte_identical`
  (out-of-vocabulary field value → `ValidationError` for req/uc/tsk/gol/rsk,
  structural `AssertionError` for qa/prb, file byte-identical in every case),
  and `test_raises_domain_not_found_for_unknown_id` (the domain's own
  `XNotFoundError`). Re-run live in the Phase-7 gate as part of **Ran 1779
  tests, OK**.
- [x] ACC-002: Verifies REQ-002 — for every one of the seven types: a middle-
  range replace leaves all out-of-range body lines byte-identical and inserts
  the fragment at the range; `begin = end = N+1` appends at end of body;
  `end = N+1` replaces through end of body; empty `content` deletes the range
  (verified with an optional-section deletion that yields a still-valid
  document); `begin = 1`, `end = N` produces the same file as whole-body mode
  with the identical text; each misuse case (one parameter only, `begin < 1`,
  `begin > end`, `end > N+1`, range deleting the H1, range producing an
  out-of-vocabulary field value) raises (`ValueError` / `AssertionError` /
  `ValidationError`) with the file left byte-identical on disk. **PASS** —
  the same file's `TestUpdateRange` (12 test methods, each subTest-
  parameterized over all seven types):
  `test_middle_range_replace_leaves_out_of_range_lines_byte_identical`,
  `test_n_plus_one_appends_at_end_of_body`,
  `test_end_n_plus_one_replaces_through_end_of_body`,
  `test_empty_content_deletes_an_optional_section` (deleting the appended
  optional section yields a still-valid document byte-equal to the minimal
  seed), `test_begin_one_end_n_equals_whole_body_mode` (byte-identical file
  to whole-body mode with the identical text, under a frozen microsecond
  clock), the four `ValueError` misuse tests —
  `test_exactly_one_of_begin_end_raises_value_error_before_file_access`
  (raised even for an unknown id, i.e. before any file access),
  `test_begin_below_one_raises_value_error_file_untouched`,
  `test_begin_above_end_raises_value_error_file_untouched`, and
  `test_end_above_n_plus_one_raises_value_error_file_untouched` (each error
  message names the offending value(s) and the allowed range; file
  byte-identical in every case) — plus
  `test_range_deleting_the_h1_raises_and_leaves_file_untouched`
  (`AssertionError`),
  `test_range_producing_out_of_vocabulary_value_raises_and_leaves_file_
  untouched` (per-type error: `ValidationError` for req/uc/tsk/gol/rsk,
  structural `AssertionError` for qa/prb — the documented nuance in the
  module docstring, lines 27–34: qa/prb bodies have no field-level
  validation), and `test_range_mode_raises_domain_not_found_for_unknown_id`.
  Re-run live in the Phase-7 gate as part of **Ran 1779 tests, OK**.
- [x] ACC-003: Verifies REQ-003 — for all seven domains, `get_<d>(id,
  raw=True)` returns the frontmatter-stripped body text byte-identical to the
  on-disk body (the text whose lines `begin`/`end` address — proven by a test
  that reads `raw`, picks a line range, calls `update` with that range, and
  confirms the splice landed exactly there); `get_<d>(id)` (`raw=False`)
  returns the parsed document exactly as before (regression); unknown id
  raises the domain `XNotFoundError` in both modes. **PASS** — each of the
  seven `tests/<d>/tools/test_get_<d>.py` files carries the same 4-test raw
  group (28 tests total): `test_raw_returns_body_text_via_shared_helper`
  (`raw=True` byte-identical to the on-disk body via the shared helper),
  `test_raw_line_coordinates_index_into_the_splice_target` (the coordinate
  invariant: read `raw`, pick the real line `k` of a marker, call `update`
  with `begin=k, end=k`, and confirm the splice landed exactly there with
  every other line unchanged), `test_raw_false_returns_parsed_document_as_
  before` (explicit `raw=False` equals the default parsed document —
  regression), and `test_raw_unknown_id_raises_not_found_in_both_modes` (the
  domain `XNotFoundError` in both modes). The shared body-extraction helper
  `body_text` lives in `general/tools/_splice.py` (line 55, no `mcp`
  dependency) — the single helper both the `update` splice and every
  `get_<d>(raw=True)` call go through, which *is* the "what the client
  counts is what the server splices" invariant. Re-run live in the Phase-7
  gate as part of **Ran 1779 tests, OK**.
- [x] ACC-004: Verifies REQ-004 — for all eight types, `set_status` changes
  `status`, bumps `updated`, and leaves the body untouched (seven domains: raw
  body byte-identical; ADR: re-render round-trip equal apart from
  status/updated); each domain's closed vocabulary is enforced (out-of-set
  value → `pydantic.ValidationError`, nothing written — including domain-
  distinct sets: `uc` 5-value, `tsk`/`qa` 4-value, `prb` 4-value, `rsk`
  6-value); ADR `superseded_by` composes `"superseded by X"`; `superseded_by`
  with a non-`adr` type raises `ValueError`, nothing written; unknown id
  raises the domain `XNotFoundError` / `AdrNotFoundError`. **PASS** —
  `tests/general/tools/test_set_status.py` (10 test methods covering all
  eight types — the seven whole-body domains subTest-parameterized, the ADR
  directly): `TestSetStatusWholeBodyDomains` —
  `test_changes_status_bumps_updated_leaves_body_untouched` (status changed
  on disk, `updated` bumped to the microsecond shape, id/type/created/
  version preserved, raw body byte-identical via the
  `frontmatter.loads(...).content` mechanism),
  `test_out_of_vocabulary_status_raises_validation_error_file_untouched`
  (cross-domain negative values — `open` against req/gol, `implemented`
  against uc/tsk/qa/prb/rsk — each a `pydantic.ValidationError` with the
  file byte-identical), `test_superseded_by_with_non_adr_type_raises_value_
  error_file_untouched` (the error names the offending type),
  `test_unknown_id_raises_domain_not_found` (the domain's own
  `XNotFoundError`), and `test_case_data_matches_the_domains_own_closed_sets`
  (the per-type valid/invalid pairs asserted against each domain's own
  imported `_ALLOWED_STATUSES`, so the distinct set sizes — req/gol 7, uc 5,
  tsk/qa 4, prb 4, rsk 6 — are verified, not trusted); `TestSetStatusAdr` —
  plain status with `superseded_by=None` (re-parsed render round-trip equal
  apart from status; ADR has no `updated` field), `superseded_by` composing
  `"superseded by X"` in the file, `implemented` → `ValidationError` with the
  file byte-identical, and unknown id → `AdrNotFoundError`; and
  `TestSetStatusSupersededByGuard` — the guard fires before any file access:
  `ValueError`, not the domain not-found, even for an unknown id. Re-run
  live in the Phase-7 gate as part of **Ran 1779 tests, OK**.
- [x] ACC-005: Verifies REQ-005 — the 15 superseded tools are absent from
  `src/` and from the live MCP registration; a grep over `src/` and `tests/`
  finds no code references to the removed tool names (any residual mention
  before Phase 5 is limited to the Phase-5-owned prompt narration files, and
  zero afterwards); `vulture` is clean. **PASS** — fresh Phase-7 run of
  `git grep -nE` over `src/` and `tests/` for all 15 removed tool names
  (word-boundary alternation of the seven `update_<d>` and the seven
  `set_status_<d>` names): 121 match lines in 28 files, every one kept by
  design — (a) 31 lines of prompt *function* names (the six domain
  `prompts/update_<d>.py` modules — tsk's is `update_task.py`, rsk's is
  `update_risk.py` — plus the four prompts `__init__.py` files and
  `qa/prompts/refine.py`), (b) 8 lines of kept prompt-name enumerations
  (`server.py`'s four per-domain PROMPT lines and one each in the
  `req`/`qa`/`prb`/`gol` package `__init__.py` files), (c) 8 lines in the
  four `*_create_instructions.md` data files (the "the `update_<d>` prompt"
  references — prompt names, not tool references), and (d) 74 lines in the
  16 prompt test files. Zero matches in any `tools/`, `models/`, or
  `general/` code; zero `set_status_<d>` matches anywhere; zero tool
  references in any `data/*.md`. Live registration: none of the 15 names is
  among the 71 tools returned by `asyncio.run(mcp.list_tools())`;
  `docs/MCP.md` carries none of the 15 removed `### Tool:` entries (0 of 15)
  and 71 `### Tool:` entries in total (the generic `set_status` at line 855,
  `update` at line 868). `vulture src/ whitelist.py --min-confidence 60`:
  clean, exit 0.
- [x] ACC-006: Verifies REQ-006 — all 11 instruction data files reference the
  generic tools with the correct signatures (`update(id, type="<d>", content
  [,...])`, `set_status(id, type=..., status[, superseded_by])`); the six
  domain update-instruction files teach the range-update flow (`get_<d>(id,
  raw=True)` → identify the 1-based range → `update(..., begin, end)`; whole-
  body for multi-section or uncertain changes); the 10 prompt test files pass
  against the rewritten narration. **PASS** — fresh Phase-7 greps over
  `src/biz/dfch/specmgr/*/data/*.md`: 18 data files carry the generic call
  shapes with zero superseded-tool call sites — `update(id, type="<d>",
  content[, begin=..., end=...])` in the 14 domain instruction files and
  `set_status(id, type="...", status[, superseded_by])` in the 16 domain +
  ADR files (the four ADR files use `set_status(id, type="adr", ...)`). Each
  of the six domain `<d>_update_instructions.md` files (req, tsk, qa, rsk,
  prb, gol) contains the range-update flow passage — verified in all six:
  `get_<d>(id, raw=True)` to see the exact body text → identify the 1-based,
  inclusive line range (`N+1` = end-of-body: `begin = end = N+1` appends
  after the last line, `end = N+1` extends the range through the last line)
  → `update(id, type="<d>", content, begin=..., end=...)` passing only the
  replacement lines (the server splices the fragment into the current on-
  disk body and validates the result as a whole document, so every out-of-
  range line stays byte-identical) → whole-body replace (no `begin`/`end`)
  for a multi-section change or whenever uncertain. The 16 prompt test files
  (6 domain update + 4 ADR + 4 domain create + `test_refine` +
  `test_implement_task`) re-run live in the Phase-7 gate: **Ran 186 tests,
  OK**.
- [x] ACC-007: Verifies REQ-007 — `specmgr docs`, `specmgr mcp-docs`,
  `specmgr adr-toc`, and `specmgr schema` all report zero drift;
  `docs/MCP.md` shows the two new general tools (with `type` rendered as a 7-
  / 8-value enum) and none of the 15 removed tools; `server.py`'s docstring
  lists exactly the post-feature surface; `AGENTS.md` and `CHANGELOG.md` are
  updated per REQ-007. **PASS** — fresh Phase-7 runs: `specmgr docs` (305
  module pages + `docs/GENERATED.md`), `specmgr mcp-docs` (`docs/MCP.md`),
  `specmgr adr-toc` (`docs/adr/README.md`), and `specmgr schema` (all seven
  domain schemas reported "unchanged") — all four byte-identical no-ops, and
  `git diff --exit-code -- docs/` exits 0. `docs/MCP.md` shows the two
  generic tools with `type` rendered as the enum — `update` (entry at line
  868): `| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk)` | Yes
  |` and `set_status` (entry at line 855): `| `type` | `string (enum: req,
  uc, tsk, qa, prb, gol, rsk, adr)` | Yes |` — and none of the 15 removed
  tools. `server.py`'s module docstring lists exactly the post-feature
  surface: the General-tools lines name `update` (7-value `type`, optional
  1-based inclusive `begin`/`end` body-line range with the `N+1` end-of-body
  sentinel, the spliced result validated as a whole document) and
  `set_status` (8-value `type`, `superseded_by` ADR-only, composing
  `"superseded by {superseded_by}"`); the ADR-tools line carries the 11
  wrappers (no `set_status`); each per-domain line names its `get_<d>` with
  the `raw=True` note and no `update_<d>`/`set_status_<d>`. `AGENTS.md` and
  `CHANGELOG.md` were updated per REQ-007 in the Phase-6 commit `c82abeb`.
- [x] ACC-008: Verifies REQ-001/002/004/005 — the Phase-1 ADR exists in
  `docs/adr/` with status `accepted` and is listed in `docs/adr/README.md`; a
  live, un-mocked end-to-end run in a temporary `SPECMGR_DOCS_DIR` passes for
  `req`, `rsk`, and `uc`: `create_<d>` → `get_<d>(id, raw=True)` →
  `update(id, type, content, begin, end)` (one middle-range replace, one
  `N+1` append) → `get_<d>` (content verified) → `set_status(id, type,
  status)` (domain-valid value) → `get_<d>` (status verified); for ADR:
  `create_adr` → `set_status(id, type="adr", status="superseded",
  superseded_by=…)` → status reads `"superseded by …"`;
  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real
  `server.mcp` instance reports **71 tools / 25 resources / 19 prompts**; a
  fresh subprocess import of `biz.dfch.specmgr.server` succeeds. **PASS** —
  (a) the Phase-1 ADR exists at `docs/adr/36905d5b-8057-4294-
  8665-c7eed5534db0-consolidate-whole-body-update-and-status-change-tools-
  into-g.md` with `status: accepted` and is listed in `docs/adr/README.md`
  (line 20: "Consolidate whole-body update and status-change tools into
  generic type-dispatched tools", with "- Id: 36905d5b-8057-
  4294-8665-c7eed5534db0" and "- Status: accepted" beneath it). (b) the
  live, un-mocked end-to-end run (throwaway script `/tmp/opencode/feat22_
  e2e.py` against a temp `SPECMGR_DOCS_DIR` + `SPECMGR_ADR_DIR`, driving the
  real tool functions; printed `E2E-OK`, exit 0) passed for all three whole-
  body domains and ADR — per domain: `create_<d>` → `get_<d>(id, raw=True)`
  (req N=20, rsk N=37, uc N=36 body lines) → one middle-range replace
  (changed line exactly the fragment, every out-of-range line byte-identical)
  → one `N+1` append (prior lines unchanged, new last lines exactly the
  fragment) → parsed `get_<d>` reflecting both edits (req `description` +
  `notes`, rsk `cause` + `owner`, uc `goal_in_context` + `open_issues`) →
  `set_status` with a domain-valid value (req `accepted`, rsk `mitigating`,
  uc `proposed`) → parsed status verified and `updated` bumped; for ADR:
  `create_adr` (initial status `proposed`) → `set_status(id, type="adr",
  status="superseded", superseded_by="00000000-0000-4000-8000-000000000000")`
  → `get_adr`'s frontmatter status reads exactly "superseded by
  00000000-0000-4000-8000-000000000000"; the temp dir was removed afterwards
  and `git status --short` shows no residue. (c)
  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the
  real `server.mcp` instance: "tools=71 resources=25 prompts=19" — none of
  the 15 removed tool names present, both generic tools present. (d) fresh-
  subprocess `uv run --frozen python -c "import biz.dfch.specmgr.server"`:
  exit 0.

### Scope

**Included in this feature:**

- `general/tools/update.py`, `general/tools/set_status.py`, and the shared
  body-text/splice helpers (private module under `general/tools/`), plus
  their registration in `general/tools/__init__.py`.
- The `raw` parameter on the seven `get_<d>` tools.
- Deletion of the 15 superseded tool modules, their test files, and all
  code/docstring references outside Phase-5-owned narration.
- The narration rewrite (11 instruction data files, prompt module
  docstrings, 10 prompt test files).
- The Phase-1 ADR, `AGENTS.md`, `CHANGELOG.md`, and all generated docs.

**Explicitly out of scope:**

- Any change to ADR's section-level mutation tools (`update_frontmatter`,
  `update_section`, `option_*`) or to ADR's `specmgr://adr/{id}` resource —
  ADR has no whole-body replace by design and is therefore not a `update`
  type; its `set_status` behavior moves to the generic tool unchanged.
- Re-introducing `specmgr://<d>/{id}` resources for the seven domains —
  rejected in the planning session on ADR ddfb1109's empirical reliability
  finding (agents invoke tools more reliably than parameterized resources);
  `get_<d>(raw=True)` serves the same need (recorded in the Phase-1 ADR).
- Consolidation of `create_*`, `get_*` (beyond the `raw` parameter),
  `list_*`, `validate_*`, `parse_*`, or the `delete_*` stubs.
- Any schema/model change: the per-domain status vocabularies, body schemas,
  and `specmgr schema` outputs are untouched.
- A version bump of `pyproject.toml` (release-time concern per `AGENTS.md`;
  the breaking change lands in `[Unreleased]`).
- The `ac` domain (does not exist yet) — but its *convention* is fixed by the
  ADR: it will add one dispatch entry to the two generic tools, not new
  tools.
- The pre-existing, already-documented AGENTS.md staleness items (e.g. the
  historical "REQ, UC, and TSK were built after that refactor" enumeration) —
  fixing unrelated stale text is not part of this feature.

### Dependencies

- Depends on: ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based reads are
  tool-first — the basis for `raw` on `get_<d>` instead of `/{id}`
  resources); ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
  hierarchy — the generic tools live in the cross-cutting `general/`
  package, reusing each domain's private helpers); ADR
  3bf0326f-065a-424c-a2b9-87e5d5bcfa99 (the `mcp` singleton lives in
  `server.py` — import-order consideration, see Design Notes); ADR
  71fd95d7-07f2-466f-81aa-d29b7e3ef34c (ADR's `update_section` contract —
  what `update` deliberately does *not* extend to ADR); ADR
  898bfcd0-85f9-462f-93a8-747bda4166c8 (ADRs are authored/edited only
  through the MCP structured tools — Phase 1 must use `specmgr_create_adr`);
  ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of
  truth — the splice re-reads the on-disk body and the validate-before-write
  invariant is preserved); the existing `general/tools/_doc_paths.py`/
  `_packaged_data.py` infrastructure and each domain's `_paths`/`_io`/
  `_write`/`_lock` private helpers (reused as-is, not modified).
- Blocks: none. Future domain work (e.g. `ac`) must follow the ADR's
  dispatch-entry convention.

### Design Notes

**Dispatch architecture.** Each of the two generic tools is a thin MCP
wrapper around a dispatch table `dict[str, Callable]` mapping the `type`
value to a private adapter function (`_update_<d>` / `_set_status_<d>`). Each
adapter is a **verbatim port** of the corresponding deleted tool's function
body (same lock, same `load_by_id`, same frontmatter carry-over / `updated`
bump, same `write_X_file`, same domain `XNotFoundError`) — for `update`, plus
the REQ-002 range branch; for `set_status`, the ADR adapter ports
`adr/tools/set_status.py` including its delegation to
`models.adr.v1.mutations.set_status`. Domain private helpers (`_paths`,
`_io`, `_write`, `_lock`) and domain models are **not modified** —
`create_*`/`get_*`/`validate_*`/`list_*` keep using them exactly as today,
and the new adapters import them the same way the old tools did. The adapters
and table live in `general/tools/` because the tools are cross-cutting (the
`general/` package is the documented home for non-domain-specific tools, per
`AGENTS.md`); no new shared *code* is added to the domain packages.

**`update` signature and return type.**

    @mcp.tool(
        name="update",
        title="Update document",
        description=(...),  # whole-body or line-range replace; type = domain;
    )                       # begin/end optional 1-based inclusive body-line range
    def update(
        id: str,
        type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk"],
        content: str,
        begin: int | None = None,
        end: int | None = None,
    ) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument:

The parameter is named `type` (matches the frontmatter field vocabulary the
client already knows; ruff's enabled rule set E/F/W has no builtin-shadowing
rule). The 7-way union return type is annotation-only — the MCP input schema
is built from the parameters, and the SDK serializes whichever concrete
document is returned. The `type` value must render as a 7-entry JSON-schema
`enum` in `docs/MCP.md` (verify in the Phase 2 gate).

**Range contract (REQ-002), precisely.** Let `N` be the number of lines of
the current frontmatter-stripped body (`len(body_text.splitlines())`).
Coordinates are 1-based and inclusive. `N+1` is a virtual position past the
last line:

- `begin = end = k` (1 ≤ k ≤ N) → replace line `k` only.
- `begin = k`, `end = m` (k ≤ m ≤ N) → replace lines `k..m`.
- `end = N+1` → the range extends through the last line (`k..N`).
- `begin = end = N+1` → the range is empty at end-of-body: pure append.
- `begin = 1`, `end = N` → whole-body replace, file-identical to whole-body
  mode with the same text (test this equivalence).
- Empty `content` → the range is deleted (legal iff the result validates).

Misuse → `ValueError` (client-controlled input, **not** `assert` — per
`.specmgr/conventions.md` Rule 3): exactly one of `begin`/`end` given;
`begin < 1`; `begin > end`; `end > N + 1`. The error message names the
offending value(s) and the allowed range. Splice algorithm: take the on-disk
body lines, drop lines `begin..min(end, N)`, insert `content.splitlines()` at
position `begin - 1`, rejoin with `"\n"` plus a single trailing `"\n"`. The
**result** is validated exactly like whole-body mode (`X.from_text(
format_text(spliced))`) and the spliced text (not the fragment) is persisted
verbatim via the domain `write_X_file` — so out-of-range regions are
byte-identical to disk and no renderer ever touches them. Frontmatter
addressing is impossible by construction: the body text is extracted with the
frontmatter block removed, and coordinates are defined relative to that text
only.

**Shared body extraction + `raw` invariant (REQ-003).** One private helper
(live in a new `general/tools/_splice.py` alongside the splice function, no
`mcp` dependency — plain file I/O, mirroring `_doc_paths.py`'s placement)
returns the frontmatter-stripped body text of a file using the established
`frontmatter.loads(path.read_text(encoding="utf-8")).content` mechanism (the
same one all seven `set_status_<d>` tools use today). Both the REQ-002 splice
and each `get_<d>(raw=True)` call go through this one helper, which *is* the
"what the client counts is what the server splices" invariant of ACC-003.
`get_<d>` with `raw=True` stays read-only: no lock, no directory creation —
matching every existing `get_<d>`.

**`set_status` signature and the `superseded_by` guard (REQ-004).**

    @mcp.tool(
        name="set_status",
        title="Set document status",
        description=(...),  # type = domain (8 values, incl. adr);
    )                       # superseded_by: adr only
    def set_status(
        id: str,
        type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "adr"],
        status: str,
        superseded_by: str | None = None,
    ) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr:

Per-domain closed status vocabularies (authoritative source: each domain's
`_ALLOWED_STATUSES` in `models/<v>/frontmatter.py` — re-read them when
implementing; the table below reflects 2026-08-26): `req` and `gol`:
`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
`implemented` (7); `uc`: `draft`/`proposed`/`accepted`/`deprecated`/
`superseded` (5); `tsk` and `qa`: `draft`/`active`/`done`/`cancelled` (4);
`prb`: `draft`/`active`/`resolved`/`cancelled` (4); `rsk`: `open`/
`mitigating`/`accepted`/`occurred`/`closed`/`dropped` (6); `adr`: 6 values
(`draft`/`proposed`/`rejected`/`accepted`/`deprecated`/`superseded`) plus the
`"superseded by X"` pattern. The guard `superseded_by is not None and type !=
"adr"` → `ValueError` runs **before** any file access.

**Import-order consideration.** `server.py` imports the domain packages in
one bottom-of-file line, with `general` second (`from . import adr, general,
gol, prb, qa, req, rsk, tsk, uc`). Once `general/tools/__init__.py` registers
the new tools, importing `general` pulls in **all** seven domain `tools` (and
`prompts`) packages earlier than today. This is safe by construction: every
domain tool module already does `from ...server import mcp` while
`server.py` is still executing its import line (the `mcp` name is bound at
`server.py:197`, before the import line at `server.py:211`), and every
`general.tools._packaged_data` import in domain prompts/resources uses the
submodule form (`from ...general.tools._packaged_data import read_packaged_
text`), which is safe mid-initialization. The Phase 2 gate's fresh-subprocess
import smoke test (ACC-008) proves it rather than assuming it.

**Docs discipline.** `server.py`'s module docstring is updated *inside* each
phase that changes the surface it describes (Phase 2 adds both tools' lines
as they are added; Phase 3 removes the `update_<d>` lines; Phase 4 removes
the `set_status_<d>` + ADR `set_status` lines). `docs/MCP.md` and
`docs/api/` are regenerated in every phase gate and must be drift-free
(`git diff --exit-code -- docs/`) at every phase commit — the pre-commit
hooks enforce this for any commit touching `src/`.

**Name-collision constraint.** ADR's existing tool is already named
`set_status`. Registering the generic `set_status` while `adr/tools/
set_status.py` still exists would double-register the name, which is why
Phase 4 adds the generic tool and deletes all eight old status tools in one
phase. (No such constraint exists for `update` — Phase 2 is purely additive,
Phase 3 deletes the seven `update_<d>` tools.)

**Phase-end quality gate (every phase).** Unless a phase task says otherwise:
`uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run
--frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen
python -m unittest discover -v -s tests -t . -p "test_*.py"`, plus the
`specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema`
regenerations the phase touches, then `git diff --exit-code -- docs/`. Fix
failures and re-run until green — a phase is not done with a red gate. Then
update this README: a dated entry in the **Recent Updates** section, Current
Status, and the phase's task lines flipped to done in place.

### Related ADRs

- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a
  tool (`get_<d>`), not a resource — the basis for `get_<d>(raw=True)`
  instead of re-introducing `specmgr://<d>/{id}` resources
- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-
  type domain — the generic tools live in the cross-cutting `general/`
  package, reusing domain-private helpers
- 3bf0326f-065a-424c-a2b9-87e5d5bcfa99: Extract the `mcp` singleton into its
  own module — the import-order consideration in Design Notes
- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` (ADR
  domain) — the section-level contract that `update` deliberately does not
  extend to ADR
- 898bfcd0-85f9-462f-93a8-747bda4166c8: Author and edit ADRs only through MCP
  structured tools — Phase 1 must use `specmgr_create_adr`, never a hand-
  written file
- 33c5ab08-ff58-4c73-8c32-23abaf3838e3: Filesystem is the sole source of
  truth — the splice re-reads the on-disk body; validate-before-write
- (Phase 1 creates the feature's own short ADR; its id is recorded in
  Decisions Made once created)

### Task List

Single, canonical breakdown of work phases and tasks. Status lives on the
task itself. Each phase ends with a mandatory phase-end quality-gate task
(full gate per Design Notes + this README's Progress update), and the
phase-orchestrator commits each accepted phase as one Conventional Commit.

#### Phase 1: ADR

- [x] Task 1.1: Create the feature's ADR with the `specmgr_create_adr` MCP
  tool (never hand-write the file — ADR 898bfcd0), status `accepted`, title
  "Consolidate whole-body update and status-change tools into generic type-
  dispatched tools": Context (15 near-duplicate mutation tools; LLM clients
  see 15 entries for 2 conceptual operations; each new domain would add
  more); Decision Drivers (simpler tool surface; no all-directories write-
  path scan and no per-domain v4-UUID-collision ambiguity — uuid-only
  resolution was rejected; the client already knows the domain; preserve the
  filesystem-source-of-truth and validate-before-write invariants);
  Considered Options (1: generic tools with explicit `type` — chosen; 2:
  uuid-only id resolution scanning all domain directories; 3: keep per-
  domain tools); Decision Outcome (Option 1) with Consequences (breaking: 14
  per-domain tools removed and ADR `set_status`'s signature gains a required
  `type`; ADR is excluded from `update` — its section-level MADR contract
  has no whole-body replace — but included in `set_status` with the
  `superseded_by` special case; the `update` line-range contract: 1-based
  inclusive `begin`/`end`, `N+1` EOF sentinel, splice-then-validate-whole,
  frontmatter never addressable; `get_<d>(raw=True)` as the line-number
  source — tool-first per ADR ddfb1109, re-introducing `specmgr://<d>/{id}`
  resources was considered and rejected; future domains add one dispatch
  entry per generic tool, not new tools) — depends on: none — status: done
- [x] Task 1.2: Validate the new ADR with `specmgr_validate_adr`; run `uv run
  --frozen specmgr adr-toc` and confirm the ADR appears in
  `docs/adr/README.md` — depends on: Task 1.1 — status: done
- [x] Task 1.3: Phase-end quality gate — full gate (ruff format --check, ruff
  check, vulture, full unittest suite; no `src/` changes are expected, so
  `docs/` drift checks cover `specmgr adr-toc` output only); set this
  README's frontmatter `status: planning` → `status: in-progress`; add a
  dated entry to the Recent Updates section, update Current Status, flip the
  phase's task lines to done in place; record the new ADR's id — depends on:
  Task 1.2 — status: done

#### Phase 2: Generic `update` tool + `raw` read parameter

- [x] Task 2.1: Create `general/tools/_splice.py` (no `mcp` dependency, plain
  file I/O + text manipulation, module docstring explaining the raw/splice
  invariant): `body_text(path: Path) -> str` (frontmatter-stripped body text
  via the established `frontmatter.loads(...).content` mechanism) and
  `splice_body(current_body: str, begin: int, end: int, content: str) -> str`
  (implements the Design-Notes range contract exactly: `N` = `len(
  current_body.splitlines())`; `ValueError` with a clear message for `begin <
  1`, `begin > end`, `end > N + 1`; drop lines `begin..min(end, N)`; insert
  `content.splitlines()` at position `begin - 1`; rejoin `"\n"` + single
  trailing `"\n"`; empty `content` = deletion) — depends on: none — status:
  done
- [x] Task 2.2: Create `general/tools/update.py`: seven private adapter
  functions `_update_<d>(id_, content, begin, end)` — verbatim ports of the
  current `update_<d>` function bodies (same `X_lock`, `load_by_id`,
  frontmatter carry-over + microsecond `updated` bump, `write_X_file`,
  domain `XNotFoundError`) with the range branch added (no `begin`/`end` →
  today's behavior: validate `X.from_text(format_text(content))`, persist
  `content` verbatim; both given → `body_text` + `splice_body`, validate the
  *result* via `X.from_text(format_text(spliced))`, persist the *spliced*
  text verbatim; the both-or-neither `ValueError` guard runs before any file
  access); a dispatch table; and `@mcp.tool(name="update", ...)` `def
  update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"],
  content: str, begin: int | None = None, end: int | None = None) ->
  ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
  GolDocument | RskDocument` with a full numpy-style docstring (including
  the range contract and the error types) — depends on: Task 2.1 — status:
  done
- [x] Task 2.3: Register `update` in `general/tools/__init__.py` (import,
  `__all__`, module docstring) — depends on: Task 2.2 — status: done
- [x] Task 2.4: Add the `raw: bool = False` parameter to the seven `get_<d>`
  tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`,
  `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`,
  `rsk/tools/get_rsk.py`): signature `get_<d>(id: str, raw: bool = False) ->
  XDocument | str`; `raw=True` resolves the id as today (no lock — read-only)
  and returns `body_text(path)` (the same helper the splice uses, per the
  Design-Notes invariant); `raw=False` returns the parsed document exactly as
  today; update each tool's `@mcp.tool` description and docstring Returns
  section — depends on: Task 2.1 — status: done
- [x] Task 2.5: Update `server.py`'s module docstring: add `update` to the
  General-tools lines (one line describing whole-body *and* line-range
  replace, the 7-value `type`, optional `begin`/`end`); note the `raw`
  parameter where the seven `get_<d>` tools are enumerated — depends on:
  Task 2.2, Task 2.4 — status: done
- [x] Task 2.6: `tests/general/tools/test_update.py` — parameterized over all
  seven types (seed a document per type, e.g. via the domain `create_<d>`
  tool in a temp `SPECMGR_DOCS_DIR`, mirroring the fixture strategy of the
  `tests/<d>/tools/test_update_<d>.py` files still on disk at this phase):
  whole-body mode (ACC-001 cases: body replaced; id/type/status/created/
  version preserved; `updated` bumped; status not settable; structural
  `AssertionError` and field `ValidationError` each leave the file
  byte-identical; unknown id → domain `XNotFoundError`); range mode (ACC-002
  cases: middle-range replace with out-of-range lines byte-identical; `N+1`
  append; `end=N+1` replace-through-EOF; empty-fragment deletion of an
  optional section yielding a valid document; `begin=1`/`end=N` ≡ whole-body;
  every `ValueError` misuse case; range deleting the H1 → `AssertionError`,
  file untouched; range producing an out-of-vocabulary field value →
  `ValidationError`, file untouched) — depends on: Task 2.2 — status: done
- [x] Task 2.7: Extend each domain's existing `tests/<d>/tools/test_get_<d>.py`
  (seven files) with `raw` coverage (ACC-003 cases): `raw=True` returns the
  body text byte-identical to the on-disk frontmatter-stripped body; the
  coordinate invariant (read `raw`, pick a real line range, `update` with it,
  assert the splice landed exactly there); `raw=False` regression (parsed
  document as before); unknown id → `XNotFoundError` in both modes — depends
  on: Task 2.4, Task 2.2 — status: done
- [x] Task 2.8: Registration smoke test: a unittest asserting
  `asyncio.run(mcp.list_tools())` contains `update` with `type` rendered as a
  7-value `enum` and optional integer `begin`/`end` in the input schema, plus
  a fresh-subprocess `uv run --frozen python -c "import biz.dfch.specmgr.
  server"` check run inside the phase gate (import-order proof, Design Notes)
  — depends on: Task 2.3 — status: done
- [x] Task 2.9: Phase-end quality gate — full gate including Tasks 2.6–2.8's
  new tests; `uv run --frozen specmgr mcp-docs` and `uv run --frozen specmgr
  docs` regeneration, then `git diff --exit-code -- docs/` zero drift;
  confirm `docs/MCP.md` shows the `update` entry (enum) and the `raw` note on
  the `get_<d>` entries; add a dated entry to the Recent Updates section,
  update Current Status, flip the phase's task lines to done in place —
  depends on: Tasks 2.3, 2.5, 2.8 — status: done

#### Phase 3: Retire the per-domain `update_*` tools

- [x] Task 3.1: Delete the seven tool modules: `req/tools/update_req.py`,
  `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`,
  `prb/tools/update_prb.py`, `gol/tools/update_gol.py`,
  `rsk/tools/update_rsk.py` — depends on: Phase 2 complete — status: done
- [x] Task 3.2: Delete the seven test files: `tests/req/tools/
  test_update_req.py`, `tests/uc/tools/test_update_uc.py`, `tests/tsk/tools/
  test_update_tsk.py`, `tests/qa/tools/test_update_qa.py`, `tests/prb/tools/
  test_update_prb.py`, `tests/gol/tools/test_update_gol.py`, `tests/rsk/
  tools/test_update_rsk.py` — depends on: Task 3.1 — status: done
- [x] Task 3.3: Update the seven domain `tools/__init__.py` files (remove the
  `update_<d>` import, `__all__` entry, and the module-docstring tool-list
  mention) and the seven domain `__init__.py` files (remove `update_<d>` from
  the docstring tool enumeration; note that whole-body updates go through the
  generic `update` tool in `general/tools/`) — depends on: Task 3.1 — status:
  done
- [x] Task 3.4: Update `server.py`'s module docstring: remove `update_<d>`
  from the seven per-domain Tools lines (the `set_status_<d>` entries stay
  until Phase 4) — depends on: Task 3.1 — status: done
- [x] Task 3.5: Grep verification: `grep -rn "update_req\|update_uc\|
  update_tsk\|update_qa\|update_prb\|update_gol\|update_rsk" src/ tests/`
  must return only prompt-narration matches (the six `prompts/update_<d>.py`
  module docstrings and their `data/*.md` files — Phase 5's ownership) and
  nothing in `tools/`, `models/`, or `general/`; record the residual match
  list in the Progress entry — depends on: Tasks 3.2, 3.3, 3.4 — status: done
- [x] Task 3.6: Phase-end quality gate — full gate; `specmgr mcp-docs` +
  `specmgr docs` regeneration, then `git diff --exit-code -- docs/` zero
  drift (`docs/MCP.md` loses the seven `update_<d>` entries; `docs/api/`
  loses the seven module pages); add a dated entry to the Recent Updates
  section, update Current Status, flip the phase's task lines to done in
  place — depends on: Task 3.5 — status: done

#### Phase 4: Generic `set_status` + retire the eight old status tools

- [x] Task 4.1: Create `general/tools/set_status.py`: eight private adapters
  `_set_status_<d>` — seven verbatim ports of the `set_status_<d>` bodies
  (lock, `load_by_id`, raw body re-read via the established
  `frontmatter.loads(...).content` mechanism, frontmatter reconstructed
  through the domain `XFrontmatter` constructor so the closed vocabulary
  validates, `updated` bump, body persisted verbatim, domain
  `XNotFoundError`) plus the ADR port (lock, `load_by_id`, delegation to
  `models.adr.v1.mutations.set_status(adr, status, superseded_by)`,
  `write_adr` render round-trip, `AdrNotFoundError`); the guard (`
  superseded_by is not None` and `type != "adr"` → `ValueError`, before any
  file access); a dispatch table; and `@mcp.tool(name="set_status", ...)`
  `def set_status(id: str, type: Literal["req","uc","tsk","qa","prb","gol",
  "rsk","adr"], status: str, superseded_by: str | None = None) ->
  ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
  GolDocument | RskDocument | Adr` with a full numpy-style docstring —
   depends on: Phase 3 complete (the `set_status` tool name must be free
   before this tool registers — see Design Notes, Name-collision constraint) —
   status: done
- [x] Task 4.2: Delete the eight superseded modules: `adr/tools/set_status.py`,
  `req/tools/set_status_req.py`, `uc/tools/set_status_uc.py`,
  `tsk/tools/set_status_tsk.py`, `qa/tools/set_status_qa.py`,
   `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`,
   `rsk/tools/set_status_rsk.py` — depends on: Task 4.1 — status: done
- [x] Task 4.3: Delete the eight test files: `tests/adr/tools/
  test_set_status.py`, `tests/req/tools/test_set_status_req.py`,
  `tests/uc/tools/test_set_status_uc.py`, `tests/tsk/tools/
  test_set_status_tsk.py`, `tests/qa/tools/test_set_status_qa.py`,
   `tests/prb/tools/test_set_status_prb.py`, `tests/gol/tools/
   test_set_status_gol.py`, `tests/rsk/tools/test_set_status_rsk.py` — depends
   on: Task 4.1 — status: done
- [x] Task 4.4: Register `set_status` in `general/tools/__init__.py` (import,
  `__all__`, module docstring); update `adr/tools/__init__.py` and the seven
  domain `tools/__init__.py` files (remove the `set_status*` imports,
  `__all__` entries, and docstring mentions; note status changes go through
  the generic `set_status` in `general/tools/`); update the eight domain
   `__init__.py` docstring enumerations likewise — depends on: Tasks 4.2, 4.3 —
   status: done
- [x] Task 4.5: Update `server.py`'s module docstring: remove `set_status`
  from the ADR tools line and `set_status_<d>` from the seven per-domain
  lines; add `set_status` to the General-tools lines (8-value `type`;
   `superseded_by` is ADR-only) — depends on: Tasks 4.1, 4.4 — status: done
- [x] Task 4.6: `tests/general/tools/test_set_status.py` — parameterized over
  all eight types (ACC-004 cases): status changed + `updated` bumped + body
  untouched (seven domains: raw body byte-identical; ADR: re-parsed document
  equal apart from status/updated); closed-vocabulary enforcement per domain
  (positive value from the domain's own set; negative value — re-read each
  domain's `_ALLOWED_STATUSES` and pick a value valid in one domain but
  invalid in the tested one, e.g. `implemented` against `rsk`/`uc`/`tsk`/`qa`/
  `prb`, `open` against `req` — each → `pydantic.ValidationError`, file
  untouched); ADR `superseded_by` composes `"superseded by X"` in the file;
  ADR plain `status` values work with `superseded_by=None`; `superseded_by`
  with any non-`adr` type → `ValueError`, file untouched; unknown id →
   domain `XNotFoundError` / `AdrNotFoundError` — depends on: Task 4.1 —
   status: done
- [x] Task 4.7: Phase-end quality gate — full gate including Task 4.6's new
  tests; `specmgr mcp-docs` + `specmgr docs` regeneration, then `git diff
  --exit-code -- docs/` zero drift; add a dated entry to the Recent Updates
  section, update Current Status, flip the phase's task lines to done in
   place — depends on: Tasks 4.5, 4.6 — status: done

#### Phase 5: Narration rewrite (prompts + instruction data)

- [x] Task 5.1: Grep-driven rewrite of every instruction data file naming a
  superseded tool (`grep -rn "update_req\|update_uc\|update_tsk\|update_qa\|
  update_prb\|update_gol\|update_rsk\|set_status_" src/biz/dfch/specmgr/
  */data/` plus bare `set_status(` in the ADR data files). Eleven files
  expected: the six `<d>_update_instructions.md` (req, tsk, qa, rsk, prb,
  gol — `uc` has no prompts sub-package): `update_<d>(id, content)` →
  `update(id, type="<d>", content)`; `set_status_<d>(id, status)` →
  `set_status(id, type="<d>", status)`; **add a range-update passage** — for
  a localized change (one paragraph/field/section), first call
  `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based
  line range (the `N+1` position is end-of-body), and call
  `update(id, type="<d>", content, begin=…, end=…)` passing only the
  replacement lines; for multi-section or uncertain changes, use the whole-
  body replace (no `begin`/`end`); correct each file's status-vocabulary
  prose where it differs per the Design-Notes table. `qa/data/
  qa_refine_instructions.md`: its `update_qa` call sites → `update(id,
  type="qa", …)` (refine appends — use the `N+1` append range for a clean
  append, else whole-body; keep the existing carry-forward guidance for the
  whole-body path). The four ADR instruction files: `set_status(id, status[,
  superseded_by])` → `set_status(id, type="adr", status[, superseded_by])` —
   depends on: Phase 4 complete — status: done
- [x] Task 5.2: Correct prompt Python module docstrings that name superseded
  tools: the six `prompts/update_<d>.py` modules (rsk's is `update_risk.py`,
  tsk's is `update_task.py`) — their module docstrings narrate the
  `update_<d>` / `set_status_<d>` surface; the four ADR prompt modules
  (`create_adr.py`, `create_adr_test.py`, `update_adr.py`,
  `update_adr_test.py`) — their surface mentions of `set_status` stay true
  (the tool still exists, now generic) but are made precise where they imply
  the old ADR-only signature. No behavioral change to any prompt function —
  depends on: Task 5.1 — status: done
- [x] Task 5.3: Update the ten prompt test files to assert the rewritten
  narration: `tests/req/prompts/test_update_req.py`, `tests/tsk/prompts/
  test_update_task.py`, `tests/qa/prompts/test_update_qa.py`, `tests/rsk/
  prompts/test_update_risk.py`, `tests/prb/prompts/test_update_prb.py`,
  `tests/gol/prompts/test_update_gol.py`, `tests/adr/prompts/
  test_create_adr.py`, `tests/adr/prompts/test_create_adr_test.py`,
  `tests/adr/prompts/test_update_adr.py`, `tests/adr/prompts/
  test_update_adr_test.py` — assertions must confirm the generic call shapes
   (and, for the six domain update prompts, the range-update passage) —
   depends on: Tasks 5.1, 5.2 — status: done
- [x] Task 5.4: Phase-end quality gate — full gate (the prompt data files are
  package data; `specmgr docs` regeneration covers Task 5.2's docstring
  changes), then `git diff --exit-code -- docs/` zero drift; add a dated
   entry to the Recent Updates section, update Current Status, flip the
   phase's task lines to done in place — depends on: Task 5.3 — status: done

#### Phase 6: Cross-cutting documentation and release notes

- [x] Task 6.1: Update `AGENTS.md`: the seven per-domain bullets — remove
  `update_<d>`/`set_status_<d>` from each tool enumeration and note that
  whole-body/line-range updates go through the generic `update` tool and
  status changes through the generic `set_status` tool (both in
  `general/tools/`); the ADR bullet — remove `set_status` from its 12-wrapper
  enumeration (11 remain); the `general/` bullet — add `update` (7-type;
  optional `begin`/`end` range with the `N+1` sentinel) and `set_status`
  (8-type; ADR-only `superseded_by`), and note the `raw` parameter on the
  seven `get_<d>` tools; the "Still genuinely missing / not yet done" list —
  add the convention note that future domains (e.g. `ac`) add one dispatch
  entry to the two generic tools (plus a `raw` getter parameter) instead of
  new `update_<d>`/`set_status_<d>` tools, citing the Phase-1 ADR id —
  depends on: Phase 5 complete — status: done
- [x] Task 6.2: Update `CHANGELOG.md`'s `[Unreleased]` section: **Breaking** —
  removed 14 MCP tools (`update_req`, `update_uc`, `update_tsk`,
  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,
  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,
  `set_status_gol`, `set_status_rsk`) and ADR `set_status`'s signature
  changes from `(id, status, superseded_by)` to `(id, type, status,
  superseded_by)` with `type="adr"` now required; **Added** — generic
  `update(id, type, content, begin, end)` (7 types; optional 1-based
  inclusive body-line range, `N+1` EOF sentinel, splice-then-validate-whole)
  and generic `set_status(id, type, status, superseded_by)` (8 types);
  optional `raw: bool = False` on the seven `get_<d>` tools (returns the
  frontmatter-stripped body text verbatim — the text `begin`/`end` index
  into); cite the Phase-1 ADR id — depends on: Phase 5 complete — status:
  done
- [x] Task 6.3: Final regeneration: `uv run --frozen specmgr docs`, `uv run
  --frozen specmgr mcp-docs`, `uv run --frozen specmgr adr-toc`, `uv run
  --frozen specmgr schema` (models are untouched — expect no schema
  changes); confirm `git diff --exit-code -- docs/` exits zero — depends on:
  Task 6.1, Task 6.2 — status: done
- [x] Task 6.4: Phase-end quality gate — full gate; add a dated entry to the
  Recent Updates section, update Current Status, flip the phase's task lines
  to done in place — depends on: Task 6.3 — status: done

#### Phase 7: Final cross-cutting verification

- [x] Task 7.1: Walk ACC-001…ACC-008 and confirm each with concrete evidence,
  annotating the Acceptance Criteria section inline in the style of
  feat-18-goal: live, un-mocked end-to-end in a temporary
  `SPECMGR_DOCS_DIR` — for `req`, `rsk`, and `uc`: `create_<d>` →
  `get_<d>(id, raw=True)` → `update(id, type, content, begin, end)` (one
  middle-range replace verified byte-exact, one `N+1` append) → `get_<d>`
  (content verified) → `set_status(id, type, status)` (domain-valid value
  from the Design-Notes table) → `get_<d>` (status verified); for ADR:
  `create_adr` → `set_status(id, type="adr", status="superseded",
  superseded_by=…)` → status reads `"superseded by …"`; confirm
  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the
  real `server.mcp` instance reports 71 tools / 25 resources / 19 prompts;
  fresh-subprocess import check; full quality gate (ruff format/check, pylint
  advisory, vulture, unittest, `specmgr docs`/`mcp-docs`/`adr-toc`/`schema`
  zero drift); remove the temporary docs directory and confirm `git status`
  shows no residue — depends on: Phases 1–6 complete — status: done
- [x] Task 7.2: Set this README's frontmatter `status: in-progress` →
  `status: done`; final Recent Updates entry and Current Status summary —
  depends on: Task 7.1 — status: done

#### Phase 8: dev integration — DEC domain conversion

The feature closed at Phase 7 against a pre-feat-21 `dev`. feat-21
(artifact type "Decision", DEC) was then completed, pushed, and merged
into `dev` (released as v0.12.0) while still on the old per-domain
mechanism — per-domain `update_dec`/`set_status_dec` tools, `get_dec`
without `raw`. Integrating feat-22 with `dev` therefore requires
converting the DEC domain to this feature's mechanism first, exactly as
the ADR's convention prescribes ("future domains add one dispatch entry
per generic tool (plus a `raw` getter parameter), not new tools").

- [x] Task 8.1: `git merge origin/dev` into `feat-22` (8 commits ahead of
  the merge-base `f9586e6`); resolve the 7 conflicting files — `AGENTS.md`,
  `CHANGELOG.md`, `src/biz/dfch/specmgr/server.py` (manual: dev's dec
  lines + our generic-tool lines, dec kept on its old-mechanism wording
  for the pure-union merge commit) and `docs/MCP.md`, `docs/GENERATED.md`,
  `docs/api/README.md`, `docs/api/biz.dfch.specmgr.server.md` (resolved by
  re-running `specmgr docs` + `specmgr mcp-docs`); verify the merge commit
  is green (full test suite + linters + generator idempotency) —
  status: done (merge commit `097b502`)
- [x] Task 8.2: Wire `dec` into the generic tools — `_update_dec`
  (verbatim port of the retired `update_dec` body plus the REQ-002 range
  branch) and `_set_status_dec` (verbatim port) in `general/tools/`,
  `"dec"` in both `_ADAPTERS` dispatch tables and `Literal` unions, both
  return unions, and the "seven/eight" → "eight/nine" count wording in
  module/tool/function docstrings — status: done
- [x] Task 8.3: Retire `dec/tools/update_dec.py` and
  `dec/tools/set_status_dec.py` (and their exports in
  `dec/tools/__init__.py`); add `raw: bool = False` to `get_dec`
  (shared `body_text` helper with the splice, mirroring `get_gol`);
  re-point the DEC package and private-helper docstrings
  (`dec/__init__.py`, `_io`, `_lock`, `_write`, `validate_dec`,
  `dec/tools/__init__.py`) and the `server.py` docstring (dec tools line,
  generic-tool counts, plus removal of a pre-existing duplicated
  ADR-prompts line) at the generic tools — status: done
- [x] Task 8.4: Narration rewrite — `dec/prompts/update_dec.py` module
  and function docstrings (mirroring the Phase-5 `update_gol` rewrite,
  dropping the now-obsolete tool-name-collision note),
  `dec/data/dec_update_instructions.md` (generic `update(id,
  type="dec", …)` incl. the new line-range subsection and
  `set_status(id, type="dec", status)`), `dec/data/dec_create_instructions.md`
  ("Later revisions" pointer) — status: done
- [x] Task 8.5: Tests — delete `tests/dec/tools/test_update_dec.py` and
  `test_set_status_dec.py`; add the dec `_Case` to
  `tests/general/tools/test_update.py` (duplicate `### Option 1:` heading
  appended at `N+1` as the field-level `ValidationError` trigger) and to
  `tests/general/tools/test_set_status.py` (`accepted` in / `implemented`
  out of dec's closed six-set, tied to `DecFrontmatter._ALLOWED_STATUSES`);
  the four `raw` tests in `tests/dec/tools/test_get_dec.py` (mirroring
  `test_get_gol`); `tests/dec/tools/test_integration.py` and
  `tests/dec/prompts/test_update_dec.py`/`test_create_dec.py` re-pointed
  at the generic call shapes (plus the new line-range-flow assertions) —
  status: done
- [x] Task 8.6: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`,
  `specmgr adr-toc`; delete the two stale API pages for the retired
  tools); update `AGENTS.md` (dec bullet on the generic wording, general
  counts eight/nine) and `CHANGELOG.md` (`[Unreleased]`: 16 removed
  per-domain tools incl. the v0.12.0-shipped `update_dec`/`set_status_dec`
  pair, generic tools cover the eight/nine domains, eight `raw` getters)
  — status: done
- [x] Task 8.7: Final quality gate (ruff format/check, vulture, pylint
  advisory — no new messages vs. the merge commit, full unittest, all
  four generators zero drift), push `feat-22`, open the PR to `dev` —
  status: done

**Note:** If a task's scope changes mid-flight, edit its description in
place; rely on git history (`git log -p` on this file) to recover what was
originally planned, rather than keeping a second copy of the task around.

## Progress

### Current Status

**As of 2026-08-27**: Feature complete — all seven phases done. The 15
near-duplicate per-domain mutation tools are replaced by two generic,
type-dispatched tools in `general/tools/` — `update` (whole-body and
line-range replace over the seven whole-body domains; optional 1-based
inclusive `begin`/`end` body-line range with the `N+1` end-of-body
sentinel; splice-then-validate-whole) and `set_status` (status change
over all eight domains; ADR-only `superseded_by` composing `"superseded
by X"`) — plus the `raw: bool = False` parameter on the seven `get_<d>`
tools (frontmatter-stripped body text as-is — the text `begin`/`end`
index into). All prompt narration, `server.py`'s docstring, `AGENTS.md`,
`CHANGELOG.md`, and the generated docs carry the post-feature surface.
Live registration: **71 tools / 25 resources / 19 prompts** — the
plan's target end state (from 84/25/19: −15 +2). Phase-7 final
verification: all eight acceptance criteria confirmed with fresh
evidence and annotated inline (`**PASS**`) in the Acceptance Criteria
section; the live, un-mocked end-to-end run passed for `req`, `rsk`, and
`uc` (create → raw read → middle-range replace → `N+1` append → parsed
verification → `set_status` → status verified) and for ADR
(`create_adr` → `set_status` with `superseded_by` → status reads
"superseded by …"); the full quality gate is green (ruff format/check,
vulture clean, **Ran 1779 tests, OK**, pylint advisory 8.94/10 with
zero messages in any file this feature touched, all four generators
no-ops with `git diff --exit-code -- docs/` exit 0). The feature's ADR
is 36905d5b-8057-4294-8665-c7eed5534db0 (accepted); the six phase
commits are listed under Related PRs / Commits.

**As of 2026-08-27 (Phase 8, post-merge with dev)**: feat-21 (the DEC
domain, released on dev as v0.12.0) merged into `feat-22` still on the
old per-domain mechanism and was converted to this feature's mechanism
per the ADR's convention for new domains. The two per-domain DEC
mutation tools (`update_dec`/`set_status_dec`) are gone; the generic
`update` and `set_status` tools now cover eight whole-body domains
(`type="dec"` added) and all nine domains respectively, and `get_dec`
gained `raw`. The plan/overview/acceptance-criteria text above describes
the feature as planned (seven whole-body domains, 71/25/19 end state —
correct at planning time, before DEC existed); the ADR is deliberately
left as the historical record of that planning state. Live registration
after the conversion: **79 tools / 28 resources / 21 prompts**
(71/25/19 from Phase 7 + feat-21's 10 dec tools / 3 dec resources / 2
dec prompts − the 2 converted dec tools). Phase-8 verification: full
quality gate green (ruff format/check, vulture clean, **Ran 2007 tests,
OK**, pylint advisory with no new messages vs. the merge commit —
cyclic-import −2, duplicate-code −2 — all four generators no-ops with
`git diff --exit-code -- docs/` exit 0).

### Blockers

None.

### Recent Updates

#### Update 2026-08-27 (Phase 8: dev integration and DEC conversion)

- Completed: Phase 8 (Tasks 8.1–8.7). `origin/dev` had moved on while
  this feature was in flight: feat-21 (artifact type "Decision", DEC —
  the tenth domain) was merged into `dev` (PR #23) and released as
  v0.12.0, still on the old per-domain mechanism (`update_dec` /
  `set_status_dec`, `get_dec` without `raw`). Merged `origin/dev` into
  `feat-22` (merge commit `097b502`; 7 conflicting files — `AGENTS.md`,
  `CHANGELOG.md`, `server.py` resolved manually, the four `docs/`
  files by regeneration) and converted the DEC domain to this
  feature's mechanism per ADR 36905d5b's convention for new domains
  (commit `5a7ddf3`): `_update_dec`/`_set_status_dec` adapters in the
  generic tools (`type="dec"`), the two per-domain tools deleted,
  `raw=True` on `get_dec`, DEC narration (prompt docstrings +
  `dec_update_instructions.md` incl. the new line-range flow,
  `dec_create_instructions.md`) re-pointed, tests re-pointed (dec cases
  added to the generic `update`/`set_status` parameterized suites —
  duplicate `### Option 1:` as the field-level failure trigger,
  `implemented` as the out-of-vocabulary status — plus the four `raw`
  tests on `get_dec`), and `AGENTS.md`/`CHANGELOG.md`/`server.py`/
  regenerated docs updated. Live registration: **79 tools / 28
  resources / 21 prompts**. Final quality gate green: ruff format/check
  clean, vulture   clean, **Ran 2007 tests, OK**, pylint advisory with no
  new messages vs. the merge commit (cyclic-import −2, duplicate-code
  −2), `specmgr docs`/`mcp-docs`/`adr-toc`/`schema` all no-ops
  (`git diff --exit-code -- docs/` exit 0).
- Done: pushed `feat-22` to origin and opened the PR to `dev`:
  https://github.com/dfch/biz.dfch.SpecMgr/pull/26.

#### Update 2026-08-27 (Phase 7: Final verification)

- Completed: Phase 7 (Tasks 7.1–7.2). Final cross-cutting verification —
  all eight acceptance criteria walked with fresh evidence and annotated
  inline (`**PASS**`) in the Acceptance Criteria section; frontmatter
  status `in-progress` → `done`; this Progress update closes the feature.
- Live, un-mocked end-to-end (throwaway script `/tmp/opencode/feat22_
  e2e.py`, temp `SPECMGR_DOCS_DIR` + `SPECMGR_ADR_DIR`, driving the real
  tool functions; printed `E2E-OK`, exit 0):
  - `req`: created id `594cd34e-5358-40f2-9a0b-e2b1f6f8d5a6` (raw body
    N=20) → middle-range replace line 7 (`begin=end=7`, the Description
    paragraph → "E2E-replaced description line."; the 19 out-of-range
    lines byte-identical) → `N+1` append (`begin=end=21`, `## Notes`
    section; the prior 20 lines unchanged) → parsed `get_req` reflecting
    both edits (`body.description`, `body.notes`) →
    `set_status(id, "req", "accepted")` → status verified, `updated`
    bumped `2026-08-27T15:21:16.920820` →
    `2026-08-27T15:21:17.376827`.
  - `rsk`: created id `7c70cc5e-1ce0-4cf1-a105-6ea45a40a248` (N=37) →
    middle-range replace line 5 (`## Cause` paragraph → "E2E-replaced
    root condition."; the 36 out-of-range lines byte-identical) → `N+1`
    append (`begin=end=38`, `## Owner` section) → parsed `get_rsk`
    reflecting both edits (`body.cause`, `body.owner`) →
    `set_status(id, "rsk", "mitigating")` → status verified, `updated`
    bumped.
  - `uc`: created id `151e0a6b-69f4-4fbe-ad08-c7b2e91b2a96` (N=36) →
    middle-range replace line 7 (`### Goal in Context` paragraph →
    "E2E-replaced goal-in-context line."; the 35 out-of-range lines byte-
    identical) → `N+1` append (`begin=end=37`, `## Open Issues` section)
    → parsed `get_uc` reflecting both edits
    (`body.characteristic_information.goal_in_context`,
    `body.open_issues`) → `set_status(id, "uc", "proposed")` → status
    verified, `updated` bumped.
  - `adr`: `create_adr` (id `6bd17f45-0c1a-43ac-84a3-104e08e58d95`,
    initial status `proposed`) → `set_status(id, "adr", "superseded",
    superseded_by="00000000-0000-4000-8000-000000000000")` →
    `get_adr`'s frontmatter status reads exactly "superseded by
    00000000-0000-4000-8000-000000000000".
  - Temp dir removed after the run (`exists=False`); `git status
    --short` in the repo shows no residue from the e2e.
- Live registration on the real `server.mcp` instance
  (`asyncio.run(mcp.list_tools()/list_resources()/list_prompts())`):
  **tools=71 resources=25 prompts=19** — none of the 15 removed tool
  names present, both generic tools present. Fresh-subprocess `uv run
  --frozen python -c "import biz.dfch.specmgr.server"`: exit 0.
- Quality gate (green): `ruff format --check` (1094 files already
  formatted), `ruff check` (all checks passed), `vulture src/
  whitelist.py --min-confidence 60` (clean, exit 0), full unittest suite
  (**Ran 1779 tests in 46.6s, OK**), pylint advisory (**8.94/10** — the
  105 E messages are all pre-existing false positives in the
  `req`/`gol`/`uc`/`rsk` `models/` packages and `models/md/`; zero in any
  file this feature touched and none in `general/tools/` or `server.py`),
  the four generators (`specmgr docs` — 305 module pages +
  `docs/GENERATED.md`, `specmgr mcp-docs`, `specmgr adr-toc`, `specmgr
  schema` — all seven domain schemas "unchanged") all byte-identical
  no-ops with `git diff --exit-code -- docs/` exit 0, the 16 prompt test
  files re-run live (**Ran 186 tests, OK**), and the ACC-005/006 greps
  re-run fresh (121 kept-by-design residual lines in 28 files; 18 data
  files carry the generic call shapes; zero superseded-tool call sites).
- Feature complete: all seven phases done; the eight acceptance criteria
  are checked and annotated in place; no code change in this phase.

#### Update 2026-08-27 (Phase 6: Cross-cutting documentation and release notes)

- Completed: Phase 6 (Tasks 6.1–6.4). Cross-cutting documentation and
  release notes for the consolidated mutation surface — `AGENTS.md`,
  `CHANGELOG.md`, the four final regenerations (all no-ops), and this
  Progress update. No code change in this phase.
  - `AGENTS.md` (Task 6.1): the seven per-domain bullets no longer
    enumerate `update_<d>`/`set_status_<d>` — each now says whole-body
    and line-range updates go through the generic `update` tool and
    status changes through the generic `set_status` tool (both in
    `general/tools/`, `type="<d>"`); the six bullets that enumerate
    `get_<d>` note its `raw: bool = False` parameter (`raw=True` returns
    the frontmatter-stripped body text as-is — the text `update`'s
    `begin`/`end` index into). The ADR bullet's `@mcp.tool()` wrapper
    count is 12 → 11 (`set_status` removed from the enumeration; ADR
    status changes go through the generic `set_status` tool in
    `general/tools/`, called with `type="adr"`, ADR-only
    `superseded_by`). The `general/` bullet adds `update` (the generic
    whole-body *and* line-range replace for the seven whole-body domains
    — 7-value `type`, optional 1-based inclusive `begin`/`end` with the
    `N+1` end-of-body sentinel, splice-then-validate-whole) and
    `set_status` (the generic status change for all eight domains incl.
    adr — ADR-only `superseded_by` composing `"superseded by X"`) to
    `general/tools/`, plus the `raw: bool = False` parameter on the
    seven `get_<d>` tools. The "Still genuinely missing / not yet done"
    list gains the future-domain convention: one dispatch entry to each
    of the two generic tools (`update`'s `type`, `set_status`'s `type`)
    plus a `raw` parameter on the new `get_<d>` tool — not new
    `update_<d>`/`set_status_<d>` tools — citing ADR
    36905d5b-8057-4294-8665-c7eed5534db0 (full UUID).
  - `CHANGELOG.md` (Task 6.2): `[Unreleased]` gains `### Removed`
    (**BREAKING**: the 14 per-domain mutation tools —
    `update_{req,uc,tsk,qa,prb,gol,rsk}` + `set_status_{req,uc,tsk,qa,
    prb,gol,rsk}` — deleted outright, no deprecated wrappers; ADR's own
    `set_status` removed, its signature changing from
    `(id, status, superseded_by)` to `(id, type, status,
    superseded_by)` with `type="adr"` now required) and `### Added`
    (generic `update(id, type, content, begin=None, end=None)` — 7
    types, 1-based inclusive body-line range, `N+1` EOF sentinel,
    splice-then-validate-whole; generic `set_status(id, type, status,
    superseded_by=None)` — 8 types, ADR-only `superseded_by`; optional
    `raw: bool = False` on the seven `get_<d>` tools) — citing ADR
    36905d5b-8057-4294-8665-c7eed5534db0. No `pyproject.toml` version
    bump (release-time concern — explicitly out of scope per the plan).
  - Task 6.3 (final regeneration): `specmgr docs` (305 module pages +
    `docs/GENERATED.md`), `specmgr mcp-docs` (`docs/MCP.md`), `specmgr
    adr-toc` (`docs/adr/README.md`), `specmgr schema` (all seven domain
    schemas reported "unchanged" — models untouched, clean exit) — all
    four byte-identical no-ops: `git diff --exit-code -- docs/` exits 0.
- Quality gate (green): `ruff format --check` (1094 files already
  formatted), `ruff check` (all checks passed), `vulture src/
  whitelist.py --min-confidence 60` (clean, exit 0), full unittest suite
  (**Ran 1779 tests, OK** — unchanged count: no code or tests touched
  in this phase).
- Next: Phase 7 (Final cross-cutting verification).

#### Update 2026-08-27 (Phase 5: Narration rewrite — prompts + instruction data)

- Completed: Phase 5 (Tasks 5.1–5.4). All prompt narration now names
  the generic tools with their exact call shapes — `update(id,
  type="<d>", content)` (whole-body), `update(id, type="<d>", content,
  begin=…, end=…)` (line-range), `set_status(id, type="<d>", status)`,
  and `set_status(id, type="adr", status[, superseded_by])` in the ADR
  files (`superseded_by` composing `"superseded by X"`). No prompt
  function signature or behavior changed anywhere — an AST comparison
  of HEAD vs. working tree confirms docstring-only edits in all
  touched prompt modules.
  - 18 instruction data files rewritten (the 11 files named by
    REQ-006, plus the six `*_create_instructions.md` and
    `tsk_implement_instructions.md` files whose "Later revisions" /
    persistence paragraphs also named the old tools): the six
    `<d>_update_instructions.md` (req, tsk, qa, rsk, prb, gol — `uc`
    has no prompts sub-package), `qa_refine_instructions.md`, the four
    ADR files, and `{req,tsk,qa,prb,gol,rsk}_create_instructions.md` +
    `tsk_implement_instructions.md`.
  - Range-update passage added to the six domain
    update-instruction files (REQ-002 flow, one passage per domain):
    for a localized change (one paragraph/field/section), first
    `get_<d>(id, raw=True)` to see the exact body text, identify the
    1-based, inclusive line range — `N+1` is end-of-body:
    `begin = end = N+1` appends after the last line, `end = N+1`
    extends the range through the last line — then
    `update(id, type="<d>", content, begin=…, end=…)` passing only the
    replacement lines (the server splices the fragment into the current
    on-disk body and validates the result as a whole document, so every
    out-of-range line stays byte-identical); for a multi-section
    change, or whenever uncertain about the line range, whole-body
    replace (no `begin`/`end`) with the carry-forward warning.
  - `qa_refine_instructions.md`: section 5 reworked from "Whole-body
    replace" to "Persist the appended questions" — the clean-append
    path uses the `N+1` append range (`get_qa(id, raw=True)` to count
    the body's lines, `update(id, type="qa", content, begin=N+1,
    end=N+1)` passing only the new pairs) when the new pairs all go at
    the very end of the body; otherwise the whole-body replace carries
    forward every section exactly as read (the existing carry-forward
    guidance, kept).
  - Status-vocabulary prose: all six update files verified against each
    domain's closed `_ALLOWED_STATUSES` in `models/<v>/frontmatter.py`
    (req/gol 7 values, tsk/qa 4, prb 4, rsk 6 — `uc`'s 5-value set has
    no narration; the ADR files carry the 6-value + `"superseded by X"`
    composition notes) — all match the Design-Notes table.
  - 11 prompt Python modules, docstrings only: the six domain
    `update_<d>.py` (tsk's `update_task.py`, rsk's `update_risk.py`)
    re-pointed from the `update_<d>`/`set_status_<d>` surface to the
    generic tools (with `get_<d>`'s `raw=True` noted as the line-range
    flow's line-number source); `qa/prompts/refine.py` likewise; three
    of the four ADR modules (`create_adr.py`, `create_adr_test.py`,
    `update_adr.py`) now name the generic `set_status` "always called
    with `type="adr"`" — `update_adr_test.py` needed no change (its
    surface mentions stay true).
  - `prb/prompts/__init__.py`: the stale "(the tool-name convention,
    like REQ/QA)" parenthetical — narrating the OLD tool-name origin,
    inaccurate once the `update_prb` tool was retired — reworded to
    "(the per-domain tool-name convention, like REQ/QA -- the prompt
    keeps its name, while the update/status tools are now the generic
    ``update``/``set_status`` in ``general/tools/``)".
    `qa/prompts/__init__.py`'s "``create_qa`` guides drafting…
    ``update_qa`` guides…" sentence kept: it describes the prompts
    (which keep their names by design), not the tools.
  - 16 prompt test files updated to assert the new narration (+11 new
    tests): the six `test_update_*.py` files switched to the generic
    call shapes and each gained `test_mentions_range_update_flow`
    (raw read → 1-based inclusive range → `N+1` sentinel →
    `begin=…/end=…` call → whole-body fallback → byte-identical); the
    four ADR `test_*.py` files each gained
    `test_mentions_generic_set_status_with_type_adr`; the four
    `test_create_{req,qa,prb,gol}.py` files assert the generic tool
    call shapes in "Later revisions"; `test_refine.py` gained
    `test_mentions_n_plus_one_append_range`; `test_implement_task.py`
    switched to `update(id, type="tsk", content)`.
- Quality-audit fixes to the previous (partially completed) session's
  work:
  - `prb/prompts/__init__.py`: stale tool-name-origin parenthetical
    (quoted above) — reworded.
  - `adr/data/adr_create_instructions.md` + `adr/data/
    adr_create_test_instructions.md`: the rewritten step-3 list item
    had gained a stray leading space (` 3.` with 5-space
    continuations), inconsistent with the surrounding column-0 items —
    restored to `3.` with 3-space continuations.
  - Everything else in the previous session's 54-file diff verified
    correct as-is (call shapes, range passages, vocabularies, ADR
    `type="adr"` sites, docstring-only prompt edits, test assertions).
- Final ACC-005 grep (`git grep -nE "\b(update_req|update_uc|update_
  tsk|update_qa|update_prb|update_gol|update_rsk|set_status_req|…|
  set_status_rsk)\b" -- src/ tests/`): 121 match lines in 28 files,
  every one kept by design:
  - (a) prompt function names — imports/`__all__`/
    `@mcp.prompt(name=…)`/`def`/module titles/cross-prompt references:
    `req/prompts/` (`update_req.py` 3, `__init__.py` 2), `qa/prompts/`
    (`update_qa.py` 4, `refine.py` 2, `__init__.py` 3), `prb/prompts/`
    (`update_prb.py` 4, `__init__.py` 3), `gol/prompts/`
    (`update_gol.py` 5, `__init__.py` 2), `tsk/prompts/update_task.py`
    2, `rsk/prompts/update_risk.py` 1 — 31 lines;
  - (b) `server.py`'s four per-domain PROMPT enumeration lines (159/
    165/170/174) + the prompt-enumeration sentences in `req`/`qa`/
    `prb`/`gol` `__init__.py` (1 each) — 8 lines;
  - (c) the four `*_create_instructions.md` files' "Later revisions" /
    duplicate-check prompt-name references (`the update_<d> prompt`) —
    8 lines;
  - (d) the 16 prompt test files (imports + prompt-function calls) —
    74 lines.
  - Zero `set_status_<d>` matches anywhere in `src/` or `tests/`; zero
    matches in `tools/`, `models/`, or `general/` code; **zero tool
    references in any `data/*.md`** (the only data-file matches are
    the class-(c) prompt names).
- Quality gate (green): `ruff format` (write run: 1094 files left
  unchanged — the previous session's formatting was already stable),
  `ruff format --check` (1094 files already formatted), `ruff check`
  (all checks passed), `vulture src/ whitelist.py --min-confidence 60`
  (clean, exit 0), full unittest suite (**Ran 1779 tests, OK** — up
  from 1768: +11 new narration tests). Regenerations: `coverage run -m
  unittest discover -s tests -t . -p "test_*.py"` (refreshed
  `.coverage`), `specmgr coverage-badge` (98% — unchanged rounded
  value, badge byte-identical, no diff), `specmgr docs` (305 module
  pages; 11 pages changed: the ten reworded prompt-module API pages +
  `docs/api/biz.dfch.specmgr.prb.prompts.md` for the `__init__`
  docstring fix), `specmgr mcp-docs` (no `docs/MCP.md` change — no MCP
  surface changed in this narration-only phase). Zero-drift proof: all
  three generators re-run; the second run was a byte-identical no-op
  (sha256 manifest diff empty). Fresh-subprocess `uv run --frozen
  python -c "import biz.dfch.specmgr.server"`: exit 0. Live
  registration unchanged at **71 tools / 25 resources / 19 prompts**
  (the feature's target end state, unchanged by this phase).
- Next: Phase 6 (Cross-cutting documentation and release notes).

#### Update 2026-08-27 (Phase 4: Generic `set_status` + retire the eight old status tools)

- Completed: Phase 4 (Tasks 4.1–4.7). The eight per-domain status tools
  (seven `set_status_<d>` + ADR's own `set_status`) are deleted from
  source and from MCP registration; status changes now go only through
  the generic `set_status` tool in `general/tools/`. **This is the
  phase where the plan's Name-collision constraint was honored
  atomically**: the generic tool (whose MCP name `set_status` was
  occupied by ADR's old tool) and the deletion of all eight old status
  tools landed in the same tree state, so the name `set_status` is never
  double-registered (verified: exactly one `set_status` in the live tool
  list). No schema changed.
  - New: `src/biz/dfch/specmgr/general/tools/set_status.py` —
    `@mcp.tool(name="set_status", title="Set document status")`
    `set_status(id, type, status, superseded_by=None)` over an 8-entry
    `dict[str, Callable]` dispatch table. The seven whole-body-domain
    adapters `_set_status_<d>` are verbatim ports of the deleted
    `set_status_<d>` bodies (same lock, `load_by_id`, raw body re-read
    via the established `frontmatter.loads(...).content` mechanism and
    re-persisted verbatim, frontmatter reconstructed through the
    domain's own `XFrontmatter` constructor so the closed vocabulary
    validates, microsecond `updated` bump, domain `XNotFoundError`);
    `_set_status_adr` ports ADR's old tool (same `adr_lock`,
    `load_by_id`, `write_adr` render round-trip, `AdrNotFoundError`)
    including its delegation to `models.adr.v1.mutations.set_status`
    (the model-layer *function* — kept by design, it is not an MCP
    tool). The `superseded_by` guard (`superseded_by is not None and
    type != "adr"` → `ValueError`) runs in the public function before
    any file access, mirroring `update.py`'s both-or-neither guard
    placement.
  - Deleted (8 tool modules): `adr/tools/set_status.py` and
    `{req,uc,tsk,qa,prb,gol,rsk}/tools/set_status_<d>.py`; deleted (8
    test files, 38 tests): `tests/adr/tools/test_set_status.py` (3) and
    `tests/{req,uc,tsk,qa,prb,gol,rsk}/tools/test_set_status_<d>.py`
    (5 each).
  - Registration: `general/tools/__init__.py` (import + `__all__` +
    docstring, next to `update`); `adr/tools/__init__.py` and the seven
    domain `tools/__init__.py` (removed the `set_status*` import /
    `__all__` entry / docstring mention; the narrating sentence
    rewritten to say status changes go through the generic `set_status`
    tool in `general.tools` (`type="<d>"`)); the seven domain
    `__init__.py` docstring tool enumerations likewise (`adr/__init__.py`
    names no tool and is unchanged).
  - `server.py`: `set_status` removed from the ADR tools line,
    `set_status_<d>` removed from the seven per-domain Tools lines;
    `set_status` added to the General-tools lines (8-value `type`;
    `superseded_by` ADR-only, composing `"superseded by X"`).
  - Re-pointed references (the orchestrator-verified residual set):
    `general/tools/update.py` (both status-path mentions → the generic
    `set_status` tool), `general/tools/_splice.py` (the two
    `set_status_<d>` mentions → "the same frontmatter-stripping
    mechanism the domain write paths use"), the seven domain
    `tools/_lock.py` + `adr/tools/_lock.py` (mutating-tool
    enumerations → the generic `set_status` tool), `gol/tools/_write.py`
    + `prb/tools/_write.py` (factor-out rationale),
    `tests/gol/tools/test_integration.py` +
    `tests/prb/tools/test_integration.py` (now
    `from biz.dfch.specmgr.general.tools.set_status import set_status`
    and `set_status(<d>_id, "<d>", ...)`; both still pass live).
  - `tests/commands/test_docs.py`: the `_count_mcp_features` known-count
    assertion for `adr/tools/` updated 12 → 11 modules (the ADR
    `set_status` module moved to `general/tools/`) — a direct
    consequence of Task 4.2's deletion, flagged here as the one test
    outside the phase's named scope that the deletion broke.
  - `docs/api/`: the eight `set_status*` module pages removed manually
    (the generator writes pages for existing modules but never deletes
    stale ones, as in Phase 3).
- Status-vocabulary source-of-truth check: re-read every domain's
  `_ALLOWED_STATUSES` (`req`/`tsk`/`prb`/`rsk` in `models/v1`,
  `uc`/`qa` in `models/v2`, ADR's `_FIXED_STATUSES` in
  `models/adr/v1/frontmatter.py`) — all match the Design-Notes table
  (req/gol 7, uc 5, tsk/qa 4, prb 4, rsk 6, adr 6 + the
  `"superseded by X"` pattern). The new tests import those private sets
  and assert the per-type valid/invalid pairs against them.
- New tests: `tests/general/tools/test_set_status.py` (10 tests,
  parameterized over all eight types — ACC-004): status changed +
  `updated` bumped (microsecond timestamp) + body untouched (seven
  domains: raw body byte-identical via the
  `frontmatter.loads(...).content` mechanism; ADR: re-parsed render
  round-trip equal apart from status — ADR has no `updated` field);
  closed-vocabulary enforcement per domain (positive value from the
  domain's own set; negative cross-domain values — `implemented`
  against uc/tsk/qa/prb/rsk, `open` against req/gol, `implemented`
  against adr — → `pydantic.ValidationError`, file byte-identical);
  ADR `superseded_by` composes `"superseded by X"` in the file (and
  plain values work with `superseded_by=None`); `superseded_by` with
  any non-`adr` type → `ValueError`, file untouched — including with an
  unknown id, proving the guard fires before file access (`ValueError`,
  not the domain not-found); unknown id → the domain's own
  `XNotFoundError` / `AdrNotFoundError`.
- ACC-005 grep (final, post-cleanup):
  `git grep -nE "\b(set_status_req|set_status_uc|set_status_tsk|
  set_status_qa|set_status_prb|set_status_gol|set_status_rsk)\b" -- src/
  tests/` matches only the Phase-5-owned prompt narration files
  (`*/data/*.md`, `*/prompts/*.py`, `tests/*/prompts/*`) — zero in
  `tools/`, `models/`, `general/`, or any `__init__.py`.
  `git grep -n "set_status" -- src/ tests/` otherwise matches only: the
  new `general/tools/set_status.py` + its registration in
  `general/tools/__init__.py`, the re-pointed references listed above,
  the ADR mutation model (`models/adr/v1/mutations.py` defines the
  model-layer **function** `set_status`, re-exported by
  `models/adr/__init__.py`/`models/adr/v1/__init__.py` and exercised by
  `tests/models/adr/v1/test_mutations.py` — kept by design, not a tool
  reference), and the Phase-5 ADR narration files.
- Quality gate (green): `ruff format` (initial write run changed nothing;
  `ruff format --check`: 1094 files already formatted — ruff 0.16
  formats md too, so the count moved 1101 → 1094 exactly by the 8
  deleted `docs/api/` `set_status*` pages minus the 1 new one),
  `ruff check` (all checks passed), `vulture src/ whitelist.py
  --min-confidence 60` (clean, exit 0), full unittest suite (**Ran 1768
  tests, OK** — down from 1796: −38, the eight deleted
  `test_set_status*.py` files (3 + 7×5); +10, the new
  `tests/general/tools/test_set_status.py`; the two re-pointed
  `gol`/`prb` integration tests still pass live). Regenerations:
  `coverage run -m unittest discover -s tests -t . -p "test_*.py"`
  (pre-commit's exact command, refreshed `.coverage`), `specmgr
  coverage-badge` (98% — unchanged rounded value, badge byte-identical,
  no diff), `specmgr mcp-docs` (header now "**71 tool(s)**"; the seven
  `set_status_<d>` entries and ADR's old `set_status` entry are gone;
  the new general `set_status` entry renders `type` as the 8-value enum
  `string (enum: req, uc, tsk, qa, prb, gol, rsk, adr)` with optional
  `string | None` `superseded_by`; the generic `update` entry intact),
  `specmgr docs` (305 module pages; new
  `docs/api/biz.dfch.specmgr.general.tools.set_status.md`; the eight
  old `set_status*` pages removed manually). Zero-drift proof: all three
  generators re-run and the whole `docs/` tree came back byte-identical
  (sha256 manifest diff empty). Fresh-subprocess
  `uv run --frozen python -c "import biz.dfch.specmgr.server"`: exit 0.
  Live registration confirmed at **71 tools / 25 resources / 19
  prompts** — the feature's target end state (−8 vs Phase 3's
  78/25/19: the eight old status tools out, the generic `set_status`
  in).
- Next: Phase 5 (Narration rewrite — prompts + instruction data).

#### Update 2026-08-27 (Phase 3: Retire the per-domain `update_*` tools)

- Completed: Phase 3 (Tasks 3.1–3.6). The seven `update_<d>` tools are
  deleted from source and from MCP registration; whole-body *and*
  line-range updates now go only through the generic `update` tool in
  `general/tools/` (Phase 2). Every non-narration code/docstring
  reference to the deleted tools was re-pointed:
  - Deleted (7 tool modules):
    `src/biz/dfch/specmgr/{req,uc,tsk,qa,prb,gol,rsk}/tools/update_<d>.py`;
    deleted (7 test files, 34 tests):
    `tests/{req,uc,tsk,qa,prb,gol,rsk}/tools/test_update_<d>.py`.
  - Seven domain `tools/__init__.py`: `update_<d>` import + `__all__`
    entry removed; the narrating sentence rewritten to say whole-body and
    line-range updates go through the generic `update` tool in
    `general.tools` (`type="<d>"`).
  - Seven domain `__init__.py`: `update_<d>` removed from the docstring
    tool enumeration, same generic-`update` pointer added. The prompt
    enumerations in `req`/`qa`/`prb`/`gol`'s `__init__.py` keep the
    prompt names `update_<d>` (the plan keeps the prompts).
  - `server.py`: `update_<d>` removed from the seven per-domain Tools
    lines; the `set_status_<d>` entries (Phase 4) and the per-domain
    prompt enumerations (kept prompt names) stay.
  - `general/tools/update.py`: the seven adapter docstrings reworded to
    name the historical port without the deleted tool names ("Verbatim
    port of the previous per-domain … update tool's function body … that
    per-domain tool was retired in feat-22 Phase 3"). The private
    adapter *function names* `_update_<d>` stay — they are this module's
    own names per the Design Notes' dispatch convention (Phase 4 mirrors
    it with `_set_status_<d>`), not references to the deleted tools.
  - Seven `_io.py`/`_lock.py`/`_write.py` helper pairs: docstrings
    re-pointed at the generic `update` tool; the live `set_status_<d>`
    mentions in the `_lock.py` modules kept.
  - `req/tools/create_req.py`, `uc/tools/create_uc.py`,
    `qa/tools/create_qa.py`: "shared with `update_<d>`" reworded to the
    generic `update` tool.
  - Seven `validate_<d>.py` and seven `set_status_<d>.py`: docstring
    mentions of the deleted tools reworded (the `set_status_<d>` modules
    themselves stay — Phase 4 deletes them).
  - `tsk/models/v1/body.py`: the `_validate_items_eagerly` docstring's
    `create_tsk`/`update_tsk`/`validate_tsk` mention reworded.
  - `tests/gol/tools/test_integration.py` +
    `tests/prb/tools/test_integration.py`: re-pointed from
    `update_gol`/`update_prb` to
    `from biz.dfch.specmgr.general.tools.update import update` and
    `update(<d>_id, "<d>", _REVISED_BODY)` (whole-body mode); docstring/
    step text updated; both still pass live.
- Task 3.5 residual match list — full
  `git grep -n "update_req\|update_uc\|update_tsk\|update_qa\|update_prb\|
  update_gol\|update_rsk" -- src/ tests/` after Tasks 3.1–3.5 (43 files,
  251 match lines), grouped:
  - Phase-5 prompt-narration files (left for Phase 5, per the plan's
    ownership): the prompt modules `req/prompts/update_req.py` (5),
    `qa/prompts/update_qa.py` (6), `qa/prompts/refine.py` (3),
    `prb/prompts/update_prb.py` (9), `gol/prompts/update_gol.py` (10),
    `tsk/prompts/update_task.py` (4), `rsk/prompts/update_risk.py` (3);
    the prompt `__init__.py` files `req/prompts/__init__.py` (2),
    `qa/prompts/__init__.py` (3), `prb/prompts/__init__.py` (3),
    `gol/prompts/__init__.py` (2) — tsk/rsk's `prompts/__init__.py`
    match nothing (their prompt functions are named `update_task`/
    `update_risk`); the 14 `*/data/*.md` instruction files
    (`req_create` 3, `req_update` 4, `tsk_create` 1, `tsk_implement` 1,
    `tsk_update` 4, `qa_create` 3, `qa_refine` 4, `qa_update` 4,
    `prb_create` 2, `prb_update` 4, `gol_create` 3, `gol_update` 4,
    `rsk_create` 1, `rsk_update` 4); and the 12 prompt test files under
    `tests/*/prompts/` (`test_update_req` 21, `test_update_qa` 24,
    `test_update_prb` 27, `test_update_gol` 24, `test_update_task` 8,
    `test_update_risk` 8, `test_create_req` 3, `test_create_qa` 3,
    `test_create_prb` 3, `test_create_gol` 3, `test_refine` 4,
    `test_implement_task` 3).
  - Kept-by-design prompt-name enumerations (not tool references — the
    plan keeps the prompt names): `server.py`'s four per-domain PROMPT
    enumeration lines (155/161/166/170: req, qa, prb, gol — tsk/rsk's
    prompt lines name `update_task`/`update_risk` and match nothing),
    and the prompt-enumeration sentence in `req/__init__.py`,
    `qa/__init__.py`, `prb/__init__.py`, `gol/__init__.py` (one match
    each).
  - Substring-only matches on the generic tool's own private adapter
    names (not references to deleted tools; see the adapter-name note
    above): `general/tools/update.py` (20 — the seven
    `def _update_<d>` lines, the six `:func:`_update_req``
    cross-references, and the seven dispatch-table entries).
  - Everything else: zero matches — in particular, no per-domain
    `tools/` file and no `models/` file names a deleted tool anymore
    (Task 3.5's plan wording anticipated nothing in `general/` either;
    the 20 adapter-name matches above are the single, documented
    exception — flagging for the orchestrator's confirmation).
- Quality gate (green): `ruff format --check` (1122 files already
  formatted, down from 1136 — the 14 deleted files), `ruff check` (all
  checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean,
  exit 0), full unittest suite (**Ran 1796 tests, OK** — down from 1830:
  −34, the seven deleted `test_update_<d>.py` files; the two re-pointed
  `gol`/`prb` integration tests still pass live). Regenerations:
  `specmgr coverage-badge` (98% — unchanged rounded value, badge
  byte-identical, no diff), `specmgr mcp-docs` (header now "78 tool(s)";
  the seven `update_<d>` tool table rows and `### Tool:` sections gone;
  the generic `update` entry and all eight `set_status*` entries intact;
  the `update_<d>` prompt rows untouched), `specmgr docs` (54 other
  `docs/api/` pages + `docs/api/README.md` + `docs/GENERATED.md`
  regenerated from the reworded docstrings; the seven
  `docs/api/biz.dfch.specmgr.<d>.tools.update_<d>.md` module pages
  deleted — the generator writes pages for existing modules but never
  deletes stale ones, so they were removed manually). Zero-drift proof:
  all three generators re-run and the whole `docs/` tree came back
  byte-identical (sha256 manifest diff empty). Fresh-subprocess
  `uv run --frozen python -c "import biz.dfch.specmgr.server"`: exit 0.
  Live registration confirmed at **78 tools / 25 resources / 19
  prompts** (−7 vs Phase 2's 85/25/19).
- Next: Phase 4 (Generic `set_status` + retire the eight old status
  tools).

#### Update 2026-08-27 (Phase 2: Generic `update` tool + `raw` read parameter)

- Completed: Phase 2 (Tasks 2.1–2.9). Purely additive — the seven
  `update_<d>` tools, all `set_status*` tools, and every `models/` package
  are untouched:
  - `general/tools/_splice.py` (no `mcp` dependency): `body_text(path)` —
    the single frontmatter-stripped body extraction via
    `frontmatter.loads(path.read_text(encoding="utf-8")).content` (the same
    mechanism every `set_status_<d>` tool uses) — and
    `splice_body(current_body, begin, end, content)` implementing the
    Design-Notes range contract exactly (`N` = line count; `ValueError` for
    `begin < 1` / `begin > end` / `end > N+1`, each message naming the
    offending value(s) and the allowed range; drop lines
    `begin..min(end, N)`, insert `content.splitlines()` at `begin - 1`,
    rejoin `"\n"` + one trailing `"\n"`; empty `content` = deletion; the
    `N+1` EOF sentinel falls out — `begin = end = N+1` is a pure append,
    `end = N+1` extends the range through the last line).
  - `general/tools/update.py`: `@mcp.tool(name="update")`
    `update(id, type, content, begin=None, end=None)` with a
    `dict[str, Callable]` dispatch table over seven private adapters
    `_update_<d>` — verbatim ports of the `update_<d>` function bodies
    (same `X_lock`, same `load_by_id`, same frontmatter carry-over with
    only `updated` bumped to the current microsecond timestamp, `status`
    never settable, same verbatim `write_X_file` persistence, same domain
    `XNotFoundError`) plus the range branch (no `begin`/`end` → today's
    behavior; both given → `body_text` + `splice_body`, validate the
    *spliced result* as a whole via `X.from_text(format_text(spliced))`,
    persist the *spliced* text verbatim; the both-or-neither `ValueError`
    guard runs in the public `update` before dispatch, i.e. before any file
    access). The parameter is intentionally named `type` (7-value
    `Literal` → 7-entry JSON-schema `enum` in the input schema); the
    7-way union return type is annotation-only.
  - `raw: bool = False` on the seven `get_<d>` tools: `raw=True` resolves
    the id as today (no lock — read-only) and returns `body_text(path)` —
    the *same* helper the splice uses (REQ-003's "what the client counts is
    what the server splices" invariant); `raw=False` behaves exactly as
    today (parsed `XDocument`). Each tool's `@mcp.tool` description and
    docstring updated.
  - Registration in `general/tools/__init__.py` (import, `__all__`, module
    docstring); `server.py`'s module docstring updated (`update` added to
    the General-tools lines; the `raw` parameter noted on each of the seven
    per-domain `get_<d>` lines).
- Deviation (additive renderer extension, recorded here per the plan's
  docs-discipline note): `docs/MCP.md` could not show the 7-value `type`
  enum — `commands/mcp_docs.py`'s `_schema_type_str` collapsed
  `{"type": "string", "enum": [...]}` to bare `string`. Added an enum
  branch rendering `string (enum: req, uc, tsk, qa, prb, gol, rsk)` (it
  fires only for properties declaring `enum` — no other current tool has
  one, so no pre-existing `docs/MCP.md` row changed) plus a
  `TestSchemaTypeStr` case. The Design Notes require the enum to be
  rendered in `docs/MCP.md` and verified in this phase's gate, which the
  untouched renderer could not satisfy.
- Test note (per-type out-of-vocabulary field-value cases): `req`/`uc`/
  `tsk`/`gol`/`rsk` each have a genuine body-level
  `pydantic.ValidationError` path (closed vocabularies or cross-field
  validators), but `qa`/`prb` bodies are free-form text with no closed
  vocabulary and no field constraint — their out-of-vocabulary input (an
  unrecognized section heading) fails structurally with `AssertionError`
  instead. The ACC-002 invariant (invalid input via a range → the file
  left byte-identical on disk) is verified for both error types, per type;
  the case data in `tests/general/tools/test_update.py` flags which each
  type raises.
- Quality gate (green): `ruff format` (initial run normalized the new
  files; subsequent `ruff format --check`: 1136 files already formatted),
  `ruff check` (all checks passed), `vulture src/ whitelist.py
  --min-confidence 60` (clean, exit 0), full unittest suite (**Ran 1830
  tests, OK** — up from 1783: +18 `tests/general/tools/test_update.py`
  (whole-body ACC-001, range ACC-002, and Task-2.8 registration, each
  parameterized over all seven types), +28 `raw`-coverage tests across the
  seven `tests/<d>/tools/test_get_<d>.py`, +1 `TestSchemaTypeStr` enum
  case); the seven pre-existing `update_<d>` test files (34 tests) still
  pass unchanged. Regenerations: `specmgr coverage-badge` (98% — the same
  rounded value as before, so the badge is byte-identical and left no
  diff), `specmgr mcp-docs` (header now "85 tool(s)"; `update` entry with
  the 7-value `type` enum and optional `integer | None` `begin`/`end`;
  `raw` note on all seven `get_<d>` entries), `specmgr docs` (new
  `docs/api/biz.dfch.specmgr.general.tools.update.md` / `._splice.md`
  pages; the seven `get_<d>` pages changed; `docs/api/README.md` +
  `docs/GENERATED.md` updated). Zero-drift proof: all three generators
  re-run and the whole `docs/` tree came back byte-identical (sha256
  manifest diff empty). `specmgr schema` re-run: all seven schemas
  unchanged (models untouched). Fresh-subprocess
  `uv run --frozen python -c "import biz.dfch.specmgr.server"`: exit 0
  (the import-order proof — `general` now pulls all seven domain tool
  packages earlier than before and still imports cleanly). Live
  registration confirmed at **85 tools / 25 resources / 19 prompts**.
- Next: Phase 3 (Retire the per-domain `update_*` tools).

#### Update 2026-08-27 (Phase 1: ADR)

- Completed: Phase 1 (Tasks 1.1–1.3). Created the feature's ADR via
  `specmgr_create_adr` (never hand-written — ADR 898bfcd0): id
  36905d5b-8057-4294-8665-c7eed5534db0, title "Consolidate whole-body update
  and status-change tools into generic type-dispatched tools", status
  `accepted`, date 2026-08-27, on disk at
  `docs/adr/36905d5b-8057-4294-8665-c7eed5534db0-consolidate-whole-body-
  update-and-status-change-tools-into-g.md`. `specmgr_validate_adr` passed;
  `specmgr adr-toc` regenerated `docs/adr/README.md` with the ADR row
  listed, and repeat runs are byte-identical no-ops (zero drift).
- Quality gate (green): `ruff format --check` (1131 files already
  formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py
  --min-confidence 60` (clean), full unittest suite (Ran 1783 tests, OK).
  No `src/` changes in this phase.
- Next: Phase 2 (Generic `update` tool + `raw` read parameter).

#### Update 2026-08-26 (planning session)

- Completed: Feature planned end to end with the user. Design locked:
  generic `update(id, type, content, begin, end)` for the seven whole-body
  domains (line-range contract with the `N+1` EOF sentinel, splice-then-
  validate-whole), generic `set_status(id, type, status, superseded_by)` for
  all eight domains (ADR-only `superseded_by`), `get_<d>(raw=True)` body-text
  read, outright deletion of the 15 superseded tools, per-domain prompts
  kept with rewritten narration, and a short ADR (Phase 1).
- Next: Phase 1 (ADR) via `/implement-feature feat-22-consolidate-mutation-
  tools`.
- Notes: Phase 4 is deliberately atomic (add generic `set_status` + delete
  all eight old status tools) because ADR's existing tool already occupies
  the `set_status` name. Target end state: 71 tools / 25 resources / 19
  prompts (from 84/25/19).

### Decisions Made

- **2026-08-26**: Explicit `type` parameter on both generic tools rather
  than bare-uuid resolution — per-domain v4 UUIDs are not *guaranteed*
  unique, uuid-only would force an all-domains directory scan (parsing every
  file) on the write path with cost growing per domain, and the calling
  client always already knows the domain.
- **2026-08-26**: ADR is excluded from `update` (its section-level MADR
  contract — `update_frontmatter`/`update_section`/`option_*` — has no
  whole-body replace by design) but included in `set_status` with the
  `superseded_by` special case.
- **2026-08-26**: The 15 superseded tools are deleted outright — no
  deprecated wrapper release; the package is 0.x and the MCP tool list is
  the only contract (breaking change recorded in `CHANGELOG.md`).
- **2026-08-26**: The per-domain `update_*` prompts are kept (domain-
  tailored interview guidance) and their narration text rewritten to the
  generic tools — rather than consolidating seven near-duplicate prompts
  into one generic prompt and losing domain-specific section names.
- **2026-08-26**: The decision is recorded as a short ADR (Phase 1) rather
  than README-only — it fixes a repo-wide convention future domains must
  follow (per AGENTS.md's "when in doubt, write the ADR").
- **2026-08-26**: `update` gains optional 1-based, inclusive `begin`/`end`
  body-line coordinates with an `N+1` EOF sentinel (append/through-EOF); the
  spliced result is always validated as a whole document before writing, and
  unchanged regions stay byte-identical to disk (user request: smaller,
  faster, safer targeted updates).
- **2026-08-26**: Line numbers are served by `get_<d>(raw=True)` (shared
  body-extraction helper with the splice) rather than re-introducing
  `specmgr://<d>/{id}` resources — ADR ddfb1109's empirical finding that
  agents invoke tools more reliably than parameterized resources, plus the
  maintenance cost of seven new resource templates, decided it.
- **2026-08-27**: The Phase-1 ADR was created with id
  36905d5b-8057-4294-8665-c7eed5534db0 ("Consolidate whole-body update and
  status-change tools into generic type-dispatched tools", status
  `accepted`) — it records the explicit-`type` dispatch convention (uuid-
  only resolution rejected), ADR's exclusion from `update` / inclusion in
  `set_status` with the `superseded_by` special case, the `update` line-
  range contract, and the `get_<d>(raw=True)` decision.

### Related PRs / Commits

- `2647649` — Phase 1: ADR (the feature's accepted ADR,
  36905d5b-8057-4294-8665-c7eed5534db0)
- `fc76490` — Phase 2: generic `update` tool + `raw` read parameter
- `971998f` — Phase 3: retire the seven per-domain `update_<d>` tools
- `d9f7a28` — Phase 4: generic `set_status` tool + retire the eight old
  status tools
- `db0fec5` — Phase 5: narration rewrite (prompts + instruction data)
- `c82abeb` — Phase 6: cross-cutting documentation and release notes
  (`AGENTS.md`, `CHANGELOG.md`)
- `097b502` — Phase 8: merge of `origin/dev` (feat-21 / DEC domain,
  v0.12.0) into `feat-22`
- `5a7ddf3` — Phase 8: convert the DEC domain to the generic
  `update`/`set_status` tools (code, narration, tests, `AGENTS.md`,
  `CHANGELOG.md`, regenerated docs)

One Conventional Commit per accepted phase, created by the phase-
orchestrator; Phase 8's two commits (merge + conversion) were created
directly when integrating the already-merged feat-21 branch from `dev`.

### Pull Request

- https://github.com/dfch/biz.dfch.SpecMgr/pull/26 — feat-22 → dev
  (includes the Phase-8 dev merge and DEC conversion).
