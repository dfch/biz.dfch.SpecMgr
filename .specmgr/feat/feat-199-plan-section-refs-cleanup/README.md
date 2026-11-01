---
classification: null
created: '2026-10-06T10:45:41.464+02:00'
id: feat-199-plan-section-refs-cleanup
status: done
type: feat
updated: '2026-10-18T19:58:13.848+02:00'
version: 1.0.0
---

# Feature: Clean Up Bare `(plan §N)` Shorthand Citations of adr-tool-plan.md

## Plan

### Overview

Follow-up to feat-198-retire-adr-tool-plan-refs / GitHub issue #198. That
feature scopes only the 14 citations that spell out `adr-tool-plan.md` by
literal path. A broader sweep (done while scoping feat-198) found a much
larger, separate pattern: **~120 bare `(plan §N)`-style shorthand references
across ~25 files** in `src/biz/dfch/specmgr/adr/tools/`, `adr/resources/`,
and `models/adr/v1/` (plus one stray hit in `uc/models/v1/parser.py` to
double-check and one in `server.py`'s module docstring; exact counts
re-measured by Task 100.100 against the current tree) — e.g.
`"""``@mcp.tool()`` wrapper: get_adr (plan §8, §9a, §10 item 4)."""`.

These never spell out the filename `adr-tool-plan.md` at all — they rely on
the reader inferring from context that "plan" means that specific file and
its section numbering (§2 heading layout, §3 frontmatter, §4 body,
§5 options, §6 module layout, §7 cross-cutting decisions, §8 tool surface,
§9/§9a id-scheme, §10 next-steps, §11 prompts).

**Confirmed, not assumed, before filing this**: spot-checked via `git
blame`/`git log --follow` across four independent files
(`adr/tools/_paths.py`, `adr/tools/update_section.py`,
`models/adr/v1/body.py`, `adr/resources/adr_get.py`) — all "plan §N" lines
were introduced on 2026-08-03, the exact day `doc/adr-tool-plan.md`
(pre-`.specmgr`-migration path) was being actively authored; one commit
(`9e844dbc`) even touched both `doc/adr-tool-plan.md` and the citing
`_paths.py` line in the same commit. This is a genuinely different usage
from the many `docs(feat-NNN): update plan` commits in this repo's history,
which refer to an individual feature's own `README.md` "## Plan" section (no
`§N` sub-numbering at all) — unrelated and not to be confused with this.

This feature is deliberately left at `planning` status with a shallow task
list: it needs its own dedicated investigation/mapping pass (per-reference
disposition, mirroring feat-198's Design Notes table) before a real task
breakdown can be written, since it touches the most mature, heavily-tested
domain in the repo (ADR tooling).

### Requirements

- REQ-001: No file under `src/` carries a bare `(plan §N)`-style citation referring to `adr-tool-plan.md` after this feature closes.
- REQ-002: Every citation removed per REQ-001 has a recorded disposition (ADR substitution, drop, or other), mirroring feat-198's per-citation Design Notes approach.
- REQ-003: The one stray `uc/models/v1/parser.py` hit is explicitly confirmed (or ruled out) as the same `adr-tool-plan.md` referent before being lumped into this cleanup.
- REQ-004: `adr-tool-plan.md` itself remains untouched (same disposition as feat-198 — frozen historical record).

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — a sweep for the bare `plan §` pattern across all of `src/` returns no results (the same pattern and scope Task 100.100's investigation uses, so the acceptance check and the investigation cannot diverge).
- [x] ACC-002: Verifies REQ-002 — disposition table recorded in this file's Design Notes, one row per distinct reference site (or logical group).
- [x] ACC-003: Verifies REQ-003 — `uc/models/v1/parser.py`'s hit is explicitly addressed (confirmed in/out) with rationale recorded.
- [x] ACC-004: Verifies REQ-004 — `git diff` shows no changes under `.specmgr/feat/feat-9-doc-in-specmgr/`.

### Scope

#### Included

- All bare `plan §` shorthand references in `src/biz/dfch/specmgr/adr/tools/`, `adr/resources/`, and `models/adr/` — `__init__.py` included (0 hits at filing, its 7 removed by feat-198, but the package stays whole so the sweep scope matches REQ-001) — plus `server.py` (one module-docstring hit).
- The one stray `uc/models/v1/parser.py` reference (confirm/address per REQ-003).
- A fresh per-reference investigation/mapping pass (not yet done) before any edits — this is the first task once this feature moves out of `planning`.

#### Explicitly Out Of Scope

- The 14 literal-path citations already covered by feat-198-retire-adr-tool-plan-refs (do not duplicate that work here).
- Editing `adr-tool-plan.md` itself or any of its feat-9 siblings.
- Any changes to the 17 other feature folders' stray sibling files (separate, already-deferred concern per feat-198's own Scope section).
- The ~19 same-pattern hits in `tests/` (module docstrings/comments in `tests/adr/tools/` and `tests/models/adr/v1/`; nothing asserts on the pattern, so no `tests/` change is required by the `src/` edits) — out of scope per REQ-001's `src/`-only wording; Task 110.130 records the residue and re-checks AGENTS.md's no-live-citations clause against it (feat-198's post-review follow-up I3).
- Non-`src/` artifacts carrying the pattern: `docs/MCP.md`, `docs/GENERATED.md`, and `docs/api/*.md` are auto-generated and clear via Task 110.120's regeneration (never hand-edited); `CHANGELOG.md` (2 hits) and `docs/adr/7a626b12-….md` (1 hit) are frozen historical records, untouched (same disposition as REQ-004).

### Dependencies

#### Depends On

- FEAT feat-198-retire-adr-tool-plan-refs (establishes the per-citation disposition pattern — ADR substitution vs. drop — this feature should reuse).

#### Blocks

- None identified.

### Design Notes

Per-reference disposition table for the bare `plan §` shorthand citations
(Task 100.100; sweep of 2026-10-17: **122 hits in 27 files** under
`src/biz/dfch/specmgr/` via the ACC-001 pattern `rg -n "plan §" src/`,
byte-identical to the orchestrator baseline measured moments before this
phase and consistent with the at-filing estimate of ~120 hits / ~25 files).
Every hit is an `adr-tool-plan.md` citation — the referent was confirmed at
filing by `git blame`/`git log --follow` across four independent files (see
Overview), and the cited §N at every site was verified on 2026-10-17 to match
that file's actual sections. The `Cited §` column names the plan section(s)
a group cites, with the formal ADR(s) that govern that section: the plan file
itself names these ADRs at the top of each section, and all nine were re-read
in full on 2026-10-17 and confirmed to govern the cited content. §9 (open
backlog) and §10 (next steps) carry no ADR — they are the plan's own progress
sections. All 122 dispositions are Drop (per-site rationale in the `Fix`
column): every citing docstring states the cited design verbatim, so no ADR
substitution is needed; the governing ADR is recorded per row in case Phase
110 or review wants a citation at any site.

| Location(s) | Cited § | Fix |
|---|---|---|
| `server.py` — module docstring, registry lead-in (line 22) | §8, §9a (7531106b, 8cf940c5) | Drop: the exhaustive registry list that follows is self-evident, and its scope (all 13 domains) has long outgrown the plan's ADR-only §8/§9a enumeration. |
| `models/adr/v1/summary.py` — module docstring, class docstring, `id` parameter (lines 18, 41, 48) | §8, §9a (7531106b, 8cf940c5) | Drop: the docstrings describe the `list_adr` output shape and the `id`/`None` semantics inline; the cited §8/§9a surface enumeration is stale (listing became the `list_adr` tool in feat-13, which the same docstring records). |
| `models/adr/v1/_util.py` — `SCHEMA_MAJOR_VERSION`/`CURRENT_SCHEMA_VERSION` comments, `validate_schema_version` docstring (lines 25, 33, 79) | §3, §6 (bbf412a7, ece4554b) | Drop: the vN versioning rule (major matches the folder name; non-breaking → bump minor/patch in place; breaking → new sibling package) is stated verbatim in the same comments. |
| `models/adr/v1/adr.py` — module + class docstrings (lines 21, 41, 44, 46) | §3, §7, §8, §9 (bbf412a7, 33c5ab08, 7531106b; §9 has no ADR) | Drop (with staleness note): line 21's "still an open backlog item (plan §9)" is stale — §9 was resolved in §9a (ADR 8cf940c5) — and the model's own two fields make the no-path scope self-evident; Phase 110 should drop the citation together with that stale clause. Lines 41/44/46 state the tool-exchange shape and the version-on-frontmatter round-trip rationale inline. |
| `models/adr/v1/frontmatter.py` — module + class + `id`/`version` parameter docstrings (lines 18, 38, 46, 55, 58) | §3, §6, §7, §9a (bbf412a7, ece4554b, 4c6119c9, 8cf940c5) | Drop: the whole-object full-replace contract, the system-owned `id`, the specmgr-only extension keys, and the vN-dispatch rationale are all stated verbatim in the same docstrings. |
| `models/adr/v1/body.py` — module docstring, field-constant comments, class docstring (lines 19, 31, 38, 44, 46, 49, 56, 74, 84) | §4, §5 (71fd95d7, d54abe50) | Drop: the mandatory/optional split, the deletion-sentinel rejection, the Considered-Options/Option drift acceptance, and the derived-container-iff-non-empty rule are each stated in the very sentence that cites them. |
| `models/adr/v1/option.py` — module + class docstrings (lines 18, 30, 32) | §4, §5, §8 (71fd95d7, d54abe50, 7531106b) | Drop: the no-sentinel-for-options rule and the option_delete-only removal are stated inline. |
| `models/adr/v1/parser.py` — module docstring (lines 18, 20, 23–24, 25, 30, 34, 42) | §2, §7, §8, §10 (c73e4f9d, 33c5ab08, 4c6119c9, 7531106b; §10 has no ADR) | Drop: the parse/validate/render split, the MADR-derived heading layout, the "no separate validation pass" design, and the quoted §7 validator wording are all in the same docstring; the §10 item 2 marker is self-evident (this module is that item). Lines 23–24 carry one **line-wrapped** citation ("plan" / "§7/§8" across the break) the bare sweep does not see — drop it with the sentence. |
| `models/adr/v1/parser.py` — heading-table comments, `_Node`/`_stringify_metadata` docstrings (lines 62, 67, 78, 82, 88, 96, 126, 185) | §3, §4, §5 (bbf412a7, 71fd95d7, d54abe50) | Drop: the comments restate the §4 field table and §5 option-heading rules inline (the dict literals *are* the table), and line 185 quotes §3's date-not-enforced wording verbatim. |
| `models/adr/v1/renderer.py` — module docstring, `_FRONTMATTER_KEYS` comment (lines 18, 20, 24, 38, 41, 44, 59, 61) | §3, §4, §5, §7, §9a, §10 (bbf412a7, 71fd95d7, d54abe50, 4c6119c9, 8cf940c5; §10 has no ADR) | Drop: the pipeline stage split, the no-AST-round-trip rationale, the fixed emission order, and the §4/§5 render rules are all stated in the same docstrings. |
| `models/adr/v1/mutations.py` — module docstring + every exception/function docstring (lines 18, 21, 27, 36, 44, 70, 79, 85, 89, 95, 101, 132, 158, 170, 178, 182, 206, 224, 227) | §4, §5, §7, §8 (71fd95d7, d54abe50, 33c5ab08, 7531106b) | Drop: each function docstring states its own semantics (deletion sentinel, mandatory-section rejection, never-reused numbering, gaps-on-delete, full-content replace) verbatim, and the module docstring states the purity + no-file-I/O + re-read-cycle design inline, including the quoted §7 wording. |
| `adr/tools/_paths.py` — module docstring + constant/function docstrings (lines 19, 27, 29–30, 55, 87, 122, 147) | §7, §9a (33c5ab08, 8cf940c5) | Drop: the module docstring states the no-cache fresh-scan design, the `SPECMGR_ADR_DIR` default, the slug rules, and the staleness rationale verbatim, and each function docstring repeats the scheme inline. Lines 29–30 carry one **line-wrapped** citation ("(plan" / "§7)" across the break) inside the same sentence — drop it together with line 27's "(plan §9a)". |
| `adr/tools/_lock.py` — module docstring (lines 18, 27) | §7, §9a (33c5ab08, 8cf940c5) | Drop: the docstring states the no-cache premise and the full lost-update-race rationale the lock exists to guard inline. |
| `adr/tools/_io.py` — module docstring + `read_adr`/`write_adr` docstrings (lines 18, 36, 41) | §7, §9a (33c5ab08, 8cf940c5) | Drop: the quoted "re-read, re-parse" / "re-render, re-write" phrases are inline and the module identity is self-evident. |
| `adr/tools/__init__.py` — package docstring (line 18) | §6, §8, §10 (ece4554b, 7531106b; §10 has no ADR) | Drop: self-evident package lead-in; the docstring continues with the one-module-per-tool layout and the side-effecting-import convention. |
| The 10 tool-wrapper module lead-ins — `get_adr.py` (line 20), `create_adr.py` (18), `update_frontmatter.py` (20), `update_section.py` (20), `option_create.py` (20), `option_update.py` (20), `option_read.py` (20), `option_delete.py` (20), `option_list.py` (20), `validate_adr.py` (20) | §4, §5, §7, §8, §9a, §10 (71fd95d7, d54abe50, 33c5ab08, 7531106b, 8cf940c5; §10 has no ADR) | Drop: the wrapper identity is the module's own name, and §10 item 4 is a stale progress marker. The "Task 3.2" marks in `create_adr.py`/`validate_adr.py` cite feat-9's own README task list (a different document, a different citation shape, outside this feature's pattern) — leave them. |
| The 10 tool-wrapper "no in-memory cache" sentences — `get_adr.py` (line 24), `create_adr.py` (21), `update_frontmatter.py` (24), `update_section.py` (25), `option_create.py` (25), `option_update.py` (25), `option_read.py` (24), `option_list.py` (24), `option_delete.py` (25), `validate_adr.py` (24) | §7, §9a (33c5ab08, 8cf940c5) | Drop: each sentence states the no-cache, file-is-source-of-truth design verbatim (ADR 33c5ab08 is the governing decision if a citation is wanted; `_lock.py`'s docstring carries the most complete statement of its rationale). |
| `update_frontmatter.py` — `@mcp.tool` description (line 42) + function docstring (lines 47, 52) | §3, §9a (bbf412a7, 8cf940c5) | Drop: the whole-object full-replace semantics and the system-managed `id` re-injection exception are stated in the same docstring. |
| `update_section.py` — `@mcp.tool` description (line 48) + function docstring (line 53) | §4 (71fd95d7) | Drop: the sentinel semantics (blank/`"REMOVE"` case-insensitive, mandatory-field rejection, nothing written on error) are stated inline. |
| The 5 `option_*` `@mcp.tool` descriptions — `option_create.py` (line 47), `option_update.py` (47), `option_read.py` (43), `option_delete.py` (47), `option_list.py` (43) | §5 (d54abe50) | Drop: each one-line description is complete without the citation; the function docstrings carry the semantics. |
| `option_delete.py` — function docstring (line 53) | §5 (d54abe50) | Drop: the no-renumbering, gaps-on-delete rule is stated inline. |
| `get_adr.py` — `id` parameter docstring (line 52) | §9a (8cf940c5) | Drop: "specmgr-assigned identifier" states what the `id` is inline. |
| `create_adr.py` — function docstring (lines 58, 61) | §9a (8cf940c5) | Drop: the fresh-UUID, assigned-once, `{id}-{slug}.md` filename, and slug-derived-from-title scheme are all stated in the same docstring. |
| `validate_adr.py` — function docstring (line 55) | §7 (4c6119c9) | Drop: "validate" = the Pydantic validators running during parsing, "no separate validation pass" — stated inline. |
| `adr/resources/__init__.py` — package docstring (line 18) | §8, §9a (7531106b, 8cf940c5) | Drop: self-evident package lead-in; the docstring already explains the `adr_list` → `list_adr` history with a live feat-13 citation. |
| `adr/resources/adr_get.py` — module + function docstrings (lines 20, 22, 49, 57) | §7, §8, §9a (33c5ab08, 7531106b, 8cf940c5) | Drop: the resource-instead-of-tool decision and its rationale (context attachment without a tool round-trip, same id-resolution, no cache) are stated verbatim (ADR 7531106b is the governing decision if a citation is wanted). |
| `uc/models/v1/parser.py` — module docstring (line 4) | §7 (4c6119c9) | Drop (referent **confirmed**, see note below): the sentence already names ``models/adr/v1/parser.py`` as the source of the mirrored "parse -> validate -> render" split; "ADR's plan §7" is redundant provenance. |

**`uc/models/v1/parser.py` (REQ-003) — referent confirmed: same `adr-tool-plan.md`, in scope.**
The hit reads: 'mirrors ``models/adr/v1/parser.py``'s "parse -> validate -> render"
split, ADR's plan §7'. It was introduced with the module in commit `0544d2bb`
(2026-08-05, "feat(uc): add use case domain with models and parser"), two days
after the 2026-08-03 ADR-tooling authoring window that introduced every other
hit. The referent is `adr-tool-plan.md` §7 (cross-cutting design decisions), for
four converging reasons: (a) the sentence names the ADR domain's parser module
as what is being mirrored, and that module cites the identical pipeline split
as "(plan §7)"; (b) §7's actual content — "Pipeline: parse → validate →
render" plus "one schema-driven validate_adr check", i.e. no separate
validation pass — is exactly the design the docstring describes; (c) the same
author/feature (feat-4-use-cases) writes the identical "ADR's … §7" framing
explicitly as `adr-tool-plan.md` §7 in that README's DEC-008 entry; (d) the UC
feature plan — the document line 1 of the same docstring calls "feature plan"
(Task 1.3A) — has no `§N` sub-numbering anywhere in its `## Plan` section, so
it cannot be the referent. REQ-003 is resolved as **confirmed in**; the
disposition is the Drop in the table row above.

**Line-wrapped citations (invisible to the bare sweep):** two of the 124
actual citations wrap across a line break ("plan" ends a line, "§N" starts the
next) and so do not match `plan §`: `models/adr/v1/parser.py` lines 23–24
("plan" / "§7/§8)") and `adr/tools/_paths.py` lines 29–30 ("(plan" / "§7)").
Both are already covered by their rows above; Phase 110 must drop them
together with the same-line citation in the same sentence.

**Out-of-pattern markers recorded for Phase 110's awareness (not dispositioned
here):** the "Task 3.2" marks in the `create_adr.py`/`validate_adr.py` module
leads cite feat-9's own README task list — a different document and a different
citation shape; they do not match the `plan §` pattern and are untouched by
this feature.

### Related Decisions

- ADR e369ee2e-3353-4f92-991c-6367d76d832e: governs `.specmgr/feat/` file layout; same frozen-historical-record disposition as feat-198 applies to `adr-tool-plan.md` itself here too.

### Task List

#### Phase 100: Investigation

- [x] Task 100.100: Re-run the `plan §` sweep against the current tree (counts may have shifted since this feature was filed) and produce the per-reference disposition table in this file's Design Notes, one row per distinct citation site — depends on: none — status: done

- [x] Task 100.110: Confirm or rule out the `uc/models/v1/parser.py` stray hit (REQ-003) — depends on: none — status: done

#### Phase 110: Implementation

- [x] Task 110.100: Apply the dispositions from Task 100.100's table — depends on: Task 100.100, Task 100.110 — status: done

- [x] Task 110.110: Update any test assertions affected by the docstring changes — depends on: Task 110.100 — status: done

- [x] Task 110.120: Regenerate `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`; verify `ruff format --check`/`ruff check`/`vulture`/full test suite — depends on: Task 110.100, Task 110.110 — status: done

- [x] Task 110.130: Final verification — re-run the `plan §` sweep across `src/` (must return no results, ACC-001), confirm `git diff` shows no changes under `.specmgr/feat/feat-9-doc-in-specmgr/` (ACC-004), re-run the sweep over `tests/` and record the residue, then re-check AGENTS.md's no-live-citations clause against that post-cleanup residue state (feat-198's post-review follow-up I3) — depends on: Task 110.120 — status: done

#### Phase 120: Post-Review Improvements

- [x] Task 120.100: Apply the src/ rewordings per the feat-reviewer's I1–I3 — I2 (drop the referent-less "(second half)" in `models/adr/v1/parser.py`'s module docstring), I1 (reword the `adr/resources/adr_get.py` noqa comment's possessive "the plan's" reference to a self-contained statement), I3 (correct the six pre-existing stale-wording sites in the touched files: the nonexistent `tools.py` citations in `adr/tools/_paths.py` (module docstring + `ensure_adr_base_dir`) and `adr/tools/_io.py` (module docstring), and the "future parser" phrasing in `models/adr/v1/adr.py`, the "future validate_adr MCP tool" phrasing in `models/adr/v1/parser.py`, and the "future MCP tool surface"/"future tools/ package" phrasings in `models/adr/v1/mutations.py` — each rewording verified against the current tree) — depends on: none — status: done

- [x] Task 120.110: Remove the by-path sibling citation in `uc/models/v2/__init__.py` (the feat-reviewer's I4 — the one remaining no-live-citations-clause violation in `src/`): the sentence cites `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py` (a stale path — the file lives at `v1/uc_model_v2_draft.py`); correcting the path would still violate the clause, so drop the citation clause and make the sentence self-contained — depends on: none — status: done

- [x] Task 120.120: Drop the 16 recorded `tests/` `plan §` residue hits in 15 files (the Phase 110 record) with the same minimal drop mechanics — depends on: none — status: done

- [x] Task 120.130: Regenerate `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`; verify `ruff format --check`/`ruff check`/`vulture`/full test suite — depends on: Task 120.100, Task 120.110, Task 120.120 — status: done

- [x] Task 120.140: Final verification — repo-wide `plan §` residue = exactly the two frozen historical artifacts (`CHANGELOG.md`, `docs/adr/7a626b12-….md`), `tests/` and `src/` clean, `.specmgr/feat/feat-9-doc-in-specmgr/` still untouched, no by-path sibling citation left in `src/`, progress records updated — depends on: Task 120.130 — status: done

- [x] Task 120.150: Fix the last stale "future (existing component)" phrasing in the ADR model package — `models/adr/v1/body.py`'s "the future ``update_section(key, value)`` MCP tool" (the tool exists now, `adr/tools/update_section.py`); found during the Phase 120 verification review — drop "future" (one word), regenerate the module's docs/api page, re-verify the "the future" sweep over the ADR package (only the legitimate `frontmatter.py:58` schema-dispatch mention may remain), and run the gate — depends on: Task 120.140 — status: done

- [x] Task 120.160: TSK-domain follow-up (user-directed 2026-10-18; outside feat-199's own requirements — found by the repo-wide "the future" sweep run while verifying Phase 120): fix the last stale same-class phrasing, `tsk/models/v1/body.py`'s "a future `create_tsk` tool" (`tsk/tools/create_tsk.py` exists; the same docstring already refers to it in the present tense at line 257) — "a future" → "the" — then regenerate its three generated mirrors (`docs/tsk_schema.json` via `specmgr schema`, the package copy `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` via `specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data`, `docs/api/biz.dfch.specmgr.tsk.models.v1.body.md` via `specmgr docs`) and run the gate — depends on: Task 120.150 — status: done

- [x] Task 120.170: Fix the four remaining pre-existing "a future (existing component)" phrasings recorded in Current Status after Task 120.160 (user-directed 2026-10-18, second follow-up extension): `models/md/frontmatter.py`'s module docstring "(e.g. a future ``uc``/``req``)" (both domains exist), `general/resources/dtais.py`'s module docstring "(e.g. a future `sysrs`)" (exists), and `general/tools/_packaged_data.py`'s module docstring "so a future artifact domain (UC, goal, acc, ...) never needs its own copy" (UC and goal exist and use the module; acc does not) plus "(e.g. ``req/data/req_example.md``, a future ``uc/data/uc_example.md``)" (the file exists) — each rewording verified against the current tree and grammatical; regenerate the affected generated mirrors (`specmgr docs`, `specmgr mcp-docs`, `specmgr schema` — report which actually change) and run the gate — depends on: Task 120.160 — status: done

## Progress

### Current Status

**As of 2026-10-18**: implementation complete (Phase 100 `ca8f3a8`, Phase 110 `d36ae69`) — all four acceptance criteria verified with concrete evidence and ticked; status `done`. A user-directed Phase 120 (Post-Review Improvements) was added for the feat-reviewer's I1–I4 and the recorded tests/-residue follow-up — see Decisions Made. All **124 citations** (the 122 bare-`plan §` hits across 27 `src/` files plus the 2 line-wrapped citations the bare pattern cannot see) were dropped per Task 100.100's disposition table — 0 ADR substitutions — with the two stale-in-content clauses handled per their rows: `models/adr/v1/adr.py`'s module docstring now states the resolved specmgr-assigned `{id}-{slug}.md` id/naming scheme (with a plain ADR 8cf940c5-3100-485c-a12d-14b59b631712 citation; the "still an open backlog item" clause is gone), and `models/adr/v1/summary.py` needed no rewrite (dropping its §8/§9a citations removes the stale surface enumeration; its existing `list_adr`/feat-13 history text stays byte-identical). The `uc/models/v1/parser.py` hit dropped exactly as the table specifies, and the out-of-pattern "Task 3.2" markers in `create_adr.py`/`validate_adr.py` are untouched. No test assertions broke (4668 passed / 17 skipped / 5662 subtests on the first run, 4668 passed / 17 skipped on the final run), the full quality gate is green (`ruff format --check` over 2062 files, `ruff check`, `vulture`, full suite), and `docs/api/` + `docs/GENERATED.md` + `docs/MCP.md` were regenerated so the pattern now survives in `docs/` only in the frozen ADR `docs/adr/7a626b12-….md`. ACC-001's sweep (`rg -n "plan §" src/`) returns no results and the feat-9 frozen directory is untouched (ACC-004). Phase 120 (Post-Review Improvements, user-directed — see Decisions Made) is complete: the feat-reviewer's I1 (the `adr_get.py` noqa comment is now a self-contained statement), I2 (the referent-less "(second half)" fragment dropped), I3 (the six pre-existing stale-wording sites in the touched files corrected against the current tree), and I4 (the `uc/models/v2/__init__.py` by-path sibling citation removed, the sentence made self-contained) are applied, the recorded `tests/` residue — the 16 bare `plan §` hits in 15 files — is dropped with the same minimal mechanics, and the repo-wide `plan §` residue is now exactly the two frozen historical artifacts (`CHANGELOG.md`, `docs/adr/7a626b12-….md`) with `src/` + `tests/` clean and the full gate green (4668 passed / 17 skipped / 5662 subtests). Review-correction Task 120.150 is complete: the ADR model package carries no remaining stale "future (existing component)" phrasing. Task 120.160 (the user-directed TSK follow-up) is complete: the TSK stale phrasing (`tsk/models/v1/body.py`'s "a future `create_tsk` tool" — the tool exists) is fixed, its three generated mirrors regenerated, and `rg "a future .create_tsk"` over `src/` + `docs/` is clean. The orchestrator's adjudication of the remaining repo-wide "the future"/"a future" sweep hits (read-verified 2026-10-18) found four further pre-existing same-class sites in other domains — `models/md/frontmatter.py:23` ("a future `uc`/`req`"), `general/resources/dtais.py:36` ("a future `sysrs`"), `general/tools/_packaged_data.py:19` ("a future artifact domain (UC, goal, acc, ...)") and :24 ("a future `uc/data/uc_example.md`") — each named component exists; the user then directed (2026-10-18) that they be fixed as Task 120.170, a second follow-up extension of this feature — now complete. PR #217 merged into `dev` at `4195a9d` (2026-10-18) and the Task 120.170 follow-up in PR #219, merged at `095db60` (2026-10-18) — all work merged, status `done`, issue #199 closed.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-18 19:45:48.224+02:00 - Status set to done; PR #219 recorded; issue #199 closed

All work merged: PR #217 (Phases 100–120, Tasks 120.150/120.160) at
`4195a9d` and the second follow-up PR #219 (Task 120.170 — the four
remaining stale "a future (existing component)" phrasings) at `095db60`,
both into `dev` on 2026-10-18, CI green on each final HEAD, and both
`feat-199-plan-section-refs-cleanup` branches (upstream + local) kept per
user direction. Status moves `review` → `done`; GitHub issue #199 closed.
Final state of the repo: no bare `plan §` shorthand citation of
`adr-tool-plan.md` in `src/` or `tests/`, no by-path feature-folder-sibling
citation in `src/`, the repo-wide `plan §` residue limited to the two
frozen historical artifacts (`CHANGELOG.md`, `docs/adr/7a626b12-….md`), and
zero stale "future (existing component)" phrasings in `src/` (only
legitimate hypotheticals remain, incl. the not-yet-built `acc` domain and
the vN schema dispatch at `models/adr/v1/frontmatter.py:58`).

#### 2026-10-18 12:10:52.919+02:00 - Task 120.170 complete (four remaining stale sites)

The four pre-existing same-class stale phrasings recorded in Current Status after Task 120.160 are fixed (no commit — the orchestrator owns that). Each site was re-read and verified against the current tree before writing; per-site before → after:
1. `models/md/frontmatter.py:23` — before: (e.g. a future `uc`/`req`), after: (e.g. `uc`/`req`). Both domains exist and subclass `MarkdownFrontmatter` (`uc/models/v2/frontmatter.py` `UcFrontmatter`, `req/models/v1/frontmatter.py` `ReqFrontmatter`).
2. `general/resources/dtais.py:36` — before: (e.g. a future `sysrs`), after: (e.g. `sysrs`). The `sysrs` domain package exists.
3. `general/tools/_packaged_data.py:20` — before: "so a future artifact domain (UC, goal, acc, ...) never needs its own copy", after: "so a new artifact domain (UC, goal, acc, ...) never needs its own copy" (one word, "future" → "new": a bare drop would be ungrammatical — "a artifact" — and UC and goal have already arrived, so "new" reads as "any artifact domain arriving, as UC and goal did and acc will"). Verified: all 13 domain packages import the module and no private `_data.py` file remains anywhere under `src/`; `acc` genuinely does not exist yet and stays as the hypothetical example.
4. `general/tools/_packaged_data.py:24` — before: (e.g. `req/data/req_example.md`, a future `uc/data/uc_example.md`), after: (e.g. `req/data/req_example.md`, `uc/data/uc_example.md`). Both files exist on disk.
Regeneration: `specmgr docs` changed exactly three `docs/api/` pages — `biz.dfch.specmgr.models.md.frontmatter.md`, `biz.dfch.specmgr.general.resources.dtais.md`, `biz.dfch.specmgr.general.tools._packaged_data.md` (1/1/2 lines each; `docs/GENERATED.md` rewritten byte-identical); `specmgr mcp-docs` returned `docs/MCP.md` byte-identical (no diff); `specmgr schema` reported every schema unchanged (module docstrings do not feed the JSON schemas) and `git status --short -- src/biz/dfch/specmgr/*/data/` shows nothing (no package copy changed).
Gate: `ruff format --check` (2062 files already formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings) all pass; `pytest -n auto --cov=src --cov-report= -q` → 4668 passed, 17 skipped, 5662 subtests passed in 73.61 s.
Full stale-class adjudication `rg -n "the future|a future" src/` → 12 hits, zero stale "future (existing component)" phrasings. Each remaining hit, with its legitimacy: the six "avoids a future collision" lines in the `get_*_example.py` tools (`dec`, `req`, `sop`, `sysrs`, `vcr`, `gol` — hypothetical collision); `models/adr/v1/frontmatter.py:58` "lets a future parser dispatch" (the vN schema-dispatch code does not exist yet); `general/resources/config.py` "a future fastembed version" (hypothetical); `general/tools/_domains.py` "a future unregistered name" (hypothetical); `general/tools/_similarity_search.py` "a future demand-path cache hit" (hypothetical); `general/tools/_path_safety.py` "a future id-validation gap" (hypothetical); `general/tools/_doc_cache.py` "a future accidental in-place mutation by caller code" (hypothetical event, not a component — the one hit outside the orchestrator's expected list).
Site 3's `acc` example remains in the docstring (the `acc` domain genuinely does not exist yet); it no longer carries the word "future", so it sits outside the pattern's sweep.

#### 2026-10-18 08:52:15.685+02:00 - Task 120.160 complete (user-directed TSK follow-up)

One-word-class fix in `tsk/models/v1/body.py` (the `RecentUpdates`
class docstring's `updates:` parameter block, line 198): "a future
`create_tsk` tool" is now "the `create_tsk` tool" — the tool exists
at `tsk/tools/create_tsk.py`, and the same docstring already refers
to it in the present tense at line 257. Regenerated the three
generated mirrors (exactly one changed line in each, the same
wording): `docs/tsk_schema.json` (via `specmgr schema`), the package
copy `src/biz/dfch/specmgr/tsk/data/tsk_schema.json` (via
`specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data`),
and `docs/api/biz.dfch.specmgr.tsk.models.v1.body.md` (via
`specmgr docs`); `specmgr mcp-docs` ran too and `docs/MCP.md` came
back byte-identical (no diff). `rg -n "a future .create_tsk" docs/
src/` returns nothing (exit 1). Gate: `ruff format --check` (2062
files already formatted), `ruff check` (all checks passed),
`vulture src/ whitelist.py --min-confidence 60` (no findings) all
pass; pytest `-n auto --cov=src --cov-report= -q` → 4668 passed,
17 skipped, 5662 subtests passed in 73.76 s.

#### 2026-10-17 21:41:17.812+02:00 - Phase 120 review correction (Task 120.150)

The verification review of Phase 120 (resumed feat-reviewer session)
found one last same-class stale phrasing at `models/adr/v1/body.py:46`
("the future ``update_section`` MCP tool" — the tool exists now, at
`adr/tools/update_section.py`); fixed by dropping "future" (one word),
regenerating `docs/api/biz.dfch.specmgr.models.adr.v1.body.md` (the only
docs file changed — `docs/MCP.md` and `docs/GENERATED.md` rewritten but
byte-identical), and re-running the ADR-package "the future" sweep, which
now leaves only the legitimate `models/adr/v1/frontmatter.py:58`
schema-dispatch mention ("lets a future parser dispatch" — no
version-dispatch code exists in the tree). The full gate is green:
`ruff format --check` (2062 files), `ruff check`, `vulture` pass;
pytest 4668 passed, 17 skipped, 5662 subtests.

#### 2026-10-17 18:57:56.185+02:00 - Phase 120 complete (post-review improvements)

Implemented Task 120.100, Task 120.110, Task 120.120, Task 120.130, Task
120.140 (no commit — the orchestrator owns that). **Task 120.100** (the
src/ rewordings per the feat-reviewer's I1–I3, every named component
fact-checked against the current tree before writing): I2 — the
`models/adr/v1/parser.py` module docstring, before →
`there is no separate validation pass here. "render" is a later, separate module (second half).`
after → `there is no separate validation pass here. "render" is a later, separate module.`
(the referent-less "(second half)" fragment left by Phase 110's disclosed
drop of "(plan §10 item 2, second half)" — strictly this feature's own
defect). I1 — `adr/resources/adr_get.py` line 45, before →
`# noqa: A002 -- "id" matches the plan's tool/resource parameter name throughout`
after → `# noqa: A002 -- "id" matches the parameter name used across the ADR tool/resource surface`
(self-contained, does not name the frozen plan; the `# noqa: A002`
directive itself kept — it silences a real flake8-name check). I3 — the
six pre-existing stale-wording sites, exact before → after per site:
(1) the `adr/tools/_paths.py` module docstring, before →
`only ``create_adr`` (in ``tools.py``) calls it.` after →
`only the ``create_adr`` tool calls it.` (`tools.py` does not exist —
`adr/tools/` is one module per tool, the tool lives at
`adr/tools/create_adr.py`); (2) the same file's `ensure_adr_base_dir`
docstring, before → `Only ``create_adr`` (``tools.py``) calls this -- every other tool uses`
after → `Only the ``create_adr`` tool calls this -- every other tool uses`;
(3) the `adr/tools/_io.py` module docstring, before →
`kept separate from the ``@mcp.tool()``-decorated functions in ``tools.py`` `
after → `kept separate from the ``@mcp.tool()``-decorated functions in ``adr/tools/`` `
(the decorated functions live in `adr/tools/`, one module each);
(4) the `models/adr/v1/adr.py` `Adr` class docstring, before →
`This is the structured object the future parser produces from an on-disk ``.md`` file and the renderer consumes to produce one, and the shape ``get_adr``/``create_adr`` are expected to exchange with the LLM instead of raw markdown text.`
after → `This is the structured object the parser produces from an on-disk ``.md`` file and the renderer consumes to produce one, and the shape ``get_adr``/``create_adr`` exchange with the LLM instead of raw markdown text.`
(the parser `models/adr/v1/parser.py`, the renderer
`models/adr/v1/renderer.py`, and both tools all exist now, so present
tense); (5) the `models/adr/v1/mutations.py` module docstring, before →
`This is the model-layer half of the future MCP tool surface's ``update_section``/``option_*``/``set_status`` tools: it implements their semantics against an in-memory :class:`Adr`, deliberately excluding any file I/O (reading/writing/finding a document by id) -- that belongs to a future ``tools/`` package, not here.`
after → `This is the model-layer half of the ``update_section``/``option_*`` ADR tools and the generic ``set_status`` tool (called with ``type="adr"``): it implements their semantics against an in-memory :class:`Adr`, deliberately excluding any file I/O (reading/writing/finding a document by id) -- that belongs to the ``adr/tools/`` package, not here.`
(every named component verified: `adr/tools/update_section.py` + the
five `option_*` modules, `general/tools/set_status.py` with its ADR
branch, the `adr/tools/` package); (6) the `models/adr/v1/parser.py`
module docstring (the "future validate_adr MCP tool" phrasing, grouped
under I3), before → `the same schema-driven check the future ``validate_adr`` MCP tool uses`
after → `the same schema-driven check the ``validate_adr`` MCP tool uses`
(`adr/tools/validate_adr.py` exists). **Task 120.110** (I4): the
`uc/models/v2/__init__.py` module docstring, before →
`See `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py` for the design sketch this package implements, and `uc/models/v1/` for the original custom-parser implementation this package supersedes.`
after → `The original custom-parser implementation this package supersedes lives in `uc/models/v1/`.`
(the by-path sibling citation clause dropped — a corrected path would
still violate AGENTS.md's no-live-citations clause, so the sentence is
self-contained with the `uc/models/v1/` half kept; the sibling file
itself under `.specmgr/feat/feat-4-use-cases/` untouched).
**Task 120.120** (the recorded tests/ residue): all 16 bare `plan §` hits
in 15 files dropped with the same minimal drop mechanics (drop the
citation text, fix resulting punctuation/whitespace, all other characters
byte-identical, no re-wrapping): `tests/adr/tools/` — 10 files × 1 at
line 18, the whole-parenthetical citation in each module docstring
dropped (`test_get_adr.py`/`test_create_adr.py`/`test_update_frontmatter.py`:
` (plan §8, §9a)`; `test_update_section.py`: ` (plan §4, §8, §9a)`; the
five `test_option_*.py`: ` (plan §5, §8, §9a)`; `test_validate_adr.py`:
` (plan §7, §8, §9a)`), each docstring now
`"""Tests for the ``X`` ``@mcp.tool()`` wrapper."""`;
`tests/models/adr/v1/` — `test_parser.py` line 18, before →
`"""Tests for :func:`parse_adr` (plan §7/§10 item 2)."""` after →
`"""Tests for :func:`parse_adr`."""`; `test_mutations.py` line 18,
before → `"""Tests for the structured edit operations in :mod:`mutations` (plan §4, §5, §8)."""`
after → `"""Tests for the structured edit operations in :mod:`mutations`."""`;
`test_renderer.py` line 18, before → `(plan §7/§10 item 2, the render half of the`
after → `(the render half of the` (the parenthetical's own content kept)
and line 207, before → `(plan §10 item 4) -- not byte-identical` after →
`-- not byte-identical` (the whole-parenthetical citation dropped);
`test_examples.py` line 22, before → `-- plan §2's source document, not hand-written`
after → `-- the source document, not hand-written` (possessive citation →
determiner substitution, the Phase 110 mechanics); plus
`tests/models/adr/v1/examples/README.md` line 4, before →
`(plan §2's source document), used as parser fixtures in` after →
`used as parser fixtures in` (the packaged-example provenance note —
verified no test loads that file's content; the full suite is the
proof). **Task 120.130** (regeneration + gate): `uv run --frozen specmgr docs`
rewrote 515 module files + `docs/GENERATED.md`, `uv run --frozen specmgr mcp-docs`
rewrote `docs/MCP.md`; `git diff --stat -- docs/` → 6 files changed, 16
insertions(+), 16 deletions(-) — exactly the API pages of the six
modules whose docstrings changed (`adr/tools/_io`, `adr/tools/_paths`,
`models/adr/v1/adr`, `models/adr/v1/mutations`, `models/adr/v1/parser`,
`uc/models/v2`); the `adr/resources/adr_get.py` page is unchanged because
only its trailing `# noqa` line comment (not a docstring) moved. Gate
evidence: (1) `uv run --frozen ruff format --check` → "2062 files already
formatted" (pass); (2) `uv run --frozen ruff check` → "All checks
passed!" (pass); (3) `uv run --frozen vulture src/ whitelist.py --min-confidence 60`
→ no findings, exit 0 (pass); (4) `uv run --frozen pytest -n auto --cov=src --cov-report= -q`
→ 4668 passed, 17 skipped, 5662 subtests passed in 62.49 s (pass, the
final run after all code edits). **Task 120.140** (final verification,
all six results): (1) `rg -n "plan §" src/` → no results, exit 1 (pass);
(2) `rg -n "plan §" tests/` → no results, exit 1 (pass); (3) repo-wide
`rg -n "plan §" .` (the rg-default scan, which excludes `.git` and
hidden directories such as `.specmgr/`) → exactly 3 hits in the two
frozen historical artifacts: `CHANGELOG.md` lines 2443–2444 (2 hits) and
`docs/adr/7a626b12-….md` line 22 (1 hit) (pass); (4)
`git diff 5d2450a -- .specmgr/feat/feat-9-doc-in-specmgr/` → empty,
0 bytes (pass); (5) `rg -n "\.specmgr/feat/" src/` → every remaining hit
cites only a `README.md`, a `history.md`, a feature directory
(`.specmgr/feat/` itself, or a `feat-NNN-slug` folder name), or a
template string (`.specmgr/feat/<id>/README.md`,
`.specmgr/feat/<feature_id>/`, `.specmgr/feat/$feature_id/README.md`) —
no hit cites any other file type, the I4 violation is gone (pass); (6)
`git status --short`/`git diff --stat` footprint → the 7 changed `src/`
files, the 15 changed `tests/` files, the 6 regenerated `docs/api/*`
pages, and this README (plus the pre-existing orchestrator README
edits) — no frozen file touched. This README re-parses cleanly via the
`get_feat` MCP tool (structured body returned, no ParseFailureResult) —
each of the edits above went through that tool's own post-edit
validation.

#### 2026-10-17 11:19:36.680+02:00 - Status set to review; all acceptance criteria verified and ticked

Implementation complete (Phase 100: `ca8f3a8`, Phase 110: `d36ae69`). All
four acceptance criteria verified by the orchestrator against the committed
tree with concrete evidence: ACC-001 (`rg -n "plan §" src/` → no results,
exit 1 — the 124 dropped citations comprise the 122 bare-pattern hits plus
the 2 line-wrapped ones the bare pattern cannot see; the wrapped-residue
check confirms no `plan`/`§N` split citations remain), ACC-002 (the 27-row
per-reference disposition table recorded in Design Notes — all-Drop, with
the governing formal ADR for each cited plan § recorded per row), ACC-003
(the `uc/models/v1/parser.py` hit confirmed as the same `adr-tool-plan.md`
referent — §7, cross-cutting design decisions — with four converging lines
of evidence in Design Notes, and dropped in Phase 110), ACC-004 (`git diff
5d2450a -- .specmgr/feat/feat-9-doc-in-specmgr/` → empty; nothing under that
path touched). Recorded for separate follow-up (out of scope here): the
`tests/` residue of 16 bare-shorthand hits in 15 files (no paths, nothing
asserts on the pattern) and one pre-existing by-path sibling citation with a
stale path (`uc/models/v2/__init__.py` →
`.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py`, which in fact lives at
`v1/uc_model_v2_draft.py`) — the I3 re-check confirms AGENTS.md's
no-live-citations clause is otherwise intact against the post-cleanup state.
Status moves `progress` → `review`; a PR against `dev` follows.

#### 2026-10-17 10:06:02.773+02:00 - Phase 110 complete (implementation)

Implemented Task 110.100, Task 110.110, Task 110.120, Task 110.130 (no
commit — the orchestrator owns that). **Task 110.100**: all 124 citations
dropped across the 27 table files, worked in table order (per-file drop
counts: `mutations.py` 19, `parser.py` 15 (14 bare + the line-wrapped
citation of its lines 23–24), `body.py` 9, `renderer.py` 8, `_paths.py` 7
(6 bare + the line-wrapped citation of its lines 29–30), `frontmatter.py`
5, `update_frontmatter.py` 5; `adr.py`, `update_section.py`,
`option_delete.py`, `create_adr.py`, `adr_get.py` 4 each; 10 files ×3
(`_util.py`, `summary.py`, `option.py`, `validate_adr.py`,
`option_update.py`, `option_read.py`, `option_list.py`, `option_create.py`,
`_io.py`, `get_adr.py`); `_lock.py` 2; and 1 each in
`uc/models/v1/parser.py`, `server.py`, `adr/tools/__init__.py`,
`adr/resources/__init__.py` — the two wrapped citations dropped together
with the same-sentence bare citation, as their rows instruct). Both
stale-in-content clauses handled per their rows: (1)
`models/adr/v1/adr.py`'s module docstring, before → "the file/directory
naming and id-assignment scheme is still an open backlog item (plan §9)
and is out of scope for this schema." after → "the file/directory naming
and id-assignment scheme is the specmgr-assigned ``{id}-{slug}.md`` scheme
(ADR 8cf940c5-3100-485c-a12d-14b59b631712), implemented in ``adr/tools/``
and out of scope for this schema." — the plain formal-ADR-UUID citation was
chosen over a citation-free statement because the governing decision is the
content of the corrected sentence, and every other design fact in these
docstrings cites its formal ADR the same way; (2)
`models/adr/v1/summary.py` needed no rewrite — dropping its §8/§9a
citations removes the stale surface enumeration outright, while the same
docstrings' existing `list_adr`/feat-13 history text stays byte-identical.
The `uc/models/v1/parser.py` line-4 hit dropped exactly as specified:
before → '... "parse -> validate -> render" split, ADR's plan §7).' after
→ '... "parse -> validate -> render" split).' (the sentence already names
the mirrored module). Where a dropped possessive or referent citation left
a sentence ungrammatical or dangling, the repair was minimal (content
unchanged, disclosed): determiner substitution for possessive citations
("mirrors plan §4's rule" → "mirrors the rule", "(plan §8's narrow
convenience wrapper)" → "(a narrow convenience wrapper)",
"(plan §4/§5's H2 sections other" → "(the H2 sections other"), deletion of
now-referent-less phrases ("the table's" in body.py, "from plan §4" in
option.py), and citation-within-parenthetical drops that keep the
parenthetical's own content ("(plan §5, likewise" → "(likewise",
"(plan §10 item 2, second half)" → "(second half)", "(plan §9a's filename
scheme)" → parenthetical gone, the quoted design wordings in
`_io.py`/`mutations.py`/`parser.py` kept verbatim with only the "plan
§N's"/"plan §N:" citation dropped). The "Task 3.2" markers in
`create_adr.py`/`validate_adr.py` left untouched as instructed. One line
break inside `models/adr/v1/parser.py`'s module docstring moved (to after
"uses) --"): the byte-level drop of the line-wrapped citation joined its
two lines into a 134-character line, which ruff's E501 (line-length 120)
rejects — prose otherwise byte-identical. **Task 110.110**: no test
assertions broke — the MCP tool description strings these docstrings feed
are pinned by no assertion (feat-198's precedent); pytest evidence:
4668 passed, 17 skipped, 5662 subtests passed in 69.26 s (first run,
immediately after the src/ edits) and 4668 passed, 17 skipped in 69.20 s
(final run, after docs regeneration) — zero test files edited.
**Task 110.120**: `specmgr docs` regenerated 515 module files +
`docs/GENERATED.md`, `specmgr mcp-docs` regenerated `docs/MCP.md`;
`rg -c "plan §" docs/` now returns hits ONLY in the frozen
`docs/adr/7a626b12-….md` (1 hit). Gate evidence: (1) `uv run --frozen ruff
format --check` → "2062 files already formatted" (pass); (2) `uv run
--frozen ruff check` → "All checks passed!" (pass); (3) `uv run --frozen
vulture src/ whitelist.py --min-confidence 60` → no findings (pass); (4)
`uv run --frozen pytest -n auto --cov=src --cov-report=` → 4668 passed,
17 skipped (pass); (5) `git diff --stat -- docs/` → 30 files changed, 167
insertions(+), 168 deletions(-), exclusively `docs/api/*` +
`docs/GENERATED.md` + `docs/MCP.md` (no frozen doc touched).
**Task 110.130** (all five results): (1) ACC-001 sweep
`rg -n "plan §" src/` → no results, exit status 1 (pass); (2)
wrapped-residue check `rg -n "plan$|^\s*§" src/` → no `plan`/`§N` split
citations remain (both known wrapped sites gone; every remaining hit is a
pre-existing legitimate line — rulebook § continuations, ISO/IEC 25010
§9.5.x references, the "feat-208 plan" update-entry mention, the "plan
Overview layer 3" feature-plan mention in `commands/diagram.py`); (3)
ACC-004 `git diff 5d2450a -- .specmgr/feat/feat-9-doc-in-specmgr/` → empty
(0 bytes) and `git status --short` shows nothing under that path (pass);
(4) tests/ residue `rg -c "plan §" tests/` → 16 hits in 15 files
(`tests/adr/tools/` 10 files ×1: `test_get_adr.py`, `test_create_adr.py`,
`test_update_frontmatter.py`, `test_update_section.py`,
`test_option_create.py`, `test_option_update.py`, `test_option_read.py`,
`test_option_delete.py`, `test_option_list.py`, `test_validate_adr.py`;
`tests/models/adr/v1/`: `test_examples.py` 1, `test_parser.py` 1,
`test_mutations.py` 1, `test_renderer.py` 2; plus
`tests/models/adr/v1/examples/README.md` 1) — all bare `plan §` shorthand
in module docstrings/comments, nothing asserts on the pattern, the
at-filing estimate was ~19; (5) I3 re-check against AGENTS.md's
no-live-citations clause (which forbids citing feature-folder sibling
files — anything other than `README.md`/`history.md` — BY PATH from
src/, tests/, or AGENTS.md): (a) the src/ tree contains ONE by-path
sibling citation, found by the sweep but pre-existing and out of scope —
`uc/models/v2/__init__.py` line 20 cites
`.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py`, a file that in fact
lives one level down at `v1/uc_model_v2_draft.py` (stale path; no
`plan §` hit, not in the disposition table) — left untouched and reported
to the orchestrator for a separate follow-up; (b) the tests/ residue does
not violate the clause — every one of its 16 hits is bare `plan §`
shorthand with no path; (c) AGENTS.md itself cites no sibling file by
path (its `.specmgr/feat/` mentions are all README.md, directory, or
feature-id references — consistent with feat-198's fix).

#### 2026-10-17 06:33:49.568+02:00 - Phase 100 complete (investigation)

Implemented Task 100.100 and Task 100.110 (investigation only — no `src/` or
`tests/` edits; the only file written is this README). Final sweep:
`rg -n "plan §" src/` → **122 hits in 27 files**, per-file counts byte-identical
to the orchestrator baseline measured moments earlier (`mutations.py` 19,
`parser.py` 14, `body.py` 9, `renderer.py` 8, `_paths.py` 6, `frontmatter.py`
5, `update_frontmatter.py` 5; `adr.py`, `update_section.py`, `option_delete.py`,
`create_adr.py`, `adr_get.py` 4 each; 10 files ×3 (`models/adr/v1/_util.py`,
`models/adr/v1/summary.py`, `models/adr/v1/option.py`, `adr/tools/validate_adr.py`,
`adr/tools/option_update.py`, `adr/tools/option_read.py`, `adr/tools/option_list.py`,
`adr/tools/option_create.py`, `adr/tools/_io.py`, `adr/tools/get_adr.py`);
`adr/tools/_lock.py` 2; and 1 each in `uc/models/v1/parser.py`, `server.py`,
`adr/tools/__init__.py`, `adr/resources/__init__.py`). Disposition
table written to Design Notes: 27 rows covering all 27 files (group rows
enumerate their member files), **all 122 dispositions are Drop** — each citing
docstring states the cited design verbatim, so no ADR substitution is needed;
the governing ADR for every cited plan § is recorded in the table's `Cited §`
column (nine formal ADRs re-read in full and confirmed: 33c5ab08, 4c6119c9,
8cf940c5, 7531106b, bbf412a7, 71fd95d7, d54abe50, c73e4f9d, ece4554b). Also
recorded in Design Notes: 2 **line-wrapped** citations invisible to the bare
pattern (`models/adr/v1/parser.py` lines 23–24 "plan"/"§7/§8)" and
`adr/tools/_paths.py` lines 29–30 "(plan"/"§7)") that Phase 110 must drop with
their sentences; 2 stale-content flags (`adr.py` line 21 "still an open
backlog item (plan §9)" — §9 was resolved in §9a; `summary.py`'s §8/§9a
enumeration — listing became the `list_adr` tool in feat-13); 2 out-of-pattern
"Task 3.2" markers (`create_adr.py`/`validate_adr.py`, citing feat-9's README
task list — left untouched). Task 100.110 (REQ-003): the
`uc/models/v1/parser.py` line-4 hit is **confirmed in** — "ADR's plan §7" is
`adr-tool-plan.md` §7 (cross-cutting decisions: parse→validate→render pipeline,
no separate validation pass): the sentence names the ADR parser module as what
is mirrored (which cites the identical split as "(plan §7)"), the module dates
from commit `0544d2bb` (2026-08-05, two days after the ADR-tooling authoring
window), feat-4-use-cases's own DEC-008 entry uses the identical "ADR's … §7"
framing for `adr-tool-plan.md` §7, and the UC feature plan's `## Plan` section
has no `§N` sub-numbering at all; disposition is Drop (the sentence already
names the mirrored module). Gate evidence: per-file `rg -c "plan §" src/`
counts sum to 122 = `rg -n "plan §" src/ | wc -l`; all 27 files enumerated in
the table rows; this README re-parses cleanly via the `get_feat` MCP tool
(structured body returned, no ParseFailureResult).

#### 2026-10-17 02:25:57.000Z - Refinement pass

Applied the feat-refiner findings (G1–G4, D1–D4, I1–I4; positives P1–P6 left as-is): the Overview/Scope/ACC-001 site enumeration now includes the `server.py` module-docstring hit and the at-filing counts are corrected (~120 hits / ~25 files in the three named packages — the file count was right, the occurrence count ~30 low); ACC-001's sweep is redefined as the bare `plan §` pattern across all of `src/`, aligned with Task 100.100 and REQ-001; the section legend gains §2; `Included` annotates `models/adr/__init__.py`'s 0-hit state; Out Of Scope records the `tests/` residue and the non-`src/` artifact dispositions (auto-generated docs vs. frozen `CHANGELOG.md`/ADR); Depends On and Related Decisions are in machine-resolvable reference-tag form; new Task 110.130 verifies ACC-001/ACC-004 and closes feat-198's post-review follow-up I3; Current Status notes feat-198 is `done` (2026-10-07) and this feature is unblocked.

#### 2026-10-06 00:00:00.000Z - Created

Split out from feat-198-retire-adr-tool-plan-refs's scoping discussion (GitHub issue #199) after discovering ~90 bare `(plan §N)` shorthand citations across ~25 files, confirmed via `git blame`/`git log --follow` to refer to `adr-tool-plan.md`. Deliberately kept separate from feat-198 to avoid expanding an already-scoped, already-filed issue; deliberately left at a shallow planning depth pending its own investigation pass.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-18 11:22:43.592+02:00 - User-directed fix of the four remaining stale sites (Task 120.170)

The user directed (2026-10-18) that the four pre-existing same-class
"a future (existing component)" phrasings recorded in Current Status after
Task 120.160 (`models/md/frontmatter.py`, `general/resources/dtais.py`,
`general/tools/_packaged_data.py` ×2) be fixed on this branch as well — a
second user-directed follow-up extension of this feature (after Phase 120
and Tasks 120.150/120.160), same rationale: same-class corrections found by
this feature's own sweeps, kept auditable in one place. Scope: the four
phrasings plus regeneration of any affected generated mirrors and the gate.
After Task 120.170, the full "the future"/"a future" adjudication over
`src/` must show zero stale "future (existing component)" phrasings
(remaining hits legitimate: hypothetical future versions/gaps/collisions,
the genuinely-not-yet-built `acc` domain, and the not-yet-existing vN
schema-dispatch mention at `models/adr/v1/frontmatter.py:58`). This work
ships in a second PR against `dev` (PR #217 already merged at `4195a9d`);
the feat branch is kept, per user direction, in both rounds.

#### 2026-10-18 08:33:44.534+02:00 - User-directed TSK follow-up (Task 120.160)

While verifying Phase 120, the orchestrator's repo-wide "the future" sweep
found one last stale same-class phrasing outside feat-199's own
requirements: `tsk/models/v1/body.py`'s "a future `create_tsk` tool"
although `tsk/tools/create_tsk.py` exists (the same docstring's line 257
already refers to it in the present tense). It was disclosed in the final
report and the PR body as an out-of-scope observation; the user directed
(2026-10-18) that it be fixed on this branch before the merge, so Task
120.160 records the fix here rather than in a separate feature — same
rationale as the Phase 120 user-directed extension: a same-class
correction found by this feature's own sweep, kept auditable in one place.
Scope of the fix: the single phrasing in `body.py` plus regeneration of
its three generated mirrors (`docs/tsk_schema.json`, the package copy
`src/biz/dfch/specmgr/tsk/data/tsk_schema.json`, the `docs/api` module
page) — no other TSK change.

#### 2026-10-17 19:59:30.739+02:00 - Phase 120 wording: self-contained rewordings, no new citations

Phase 120's judgment calls: (a) every I1–I4 rewording is
self-contained — no replacement cites the frozen `adr-tool-plan.md` in
any form (not "plan", not "(plan §N)", not "the plan's"), and no new
by-path feature-folder-sibling citation is introduced; where a stale
clause named a component that exists now, the rewording names that
component (`the ``create_adr`` tool`, `adr/tools/`, the
``validate_adr`` MCP tool, the parser/renderer, the generic
``set_status`` tool called with ``type="adr"``) rather than inventing a
citation. (b) The `mutations.py` rewording splits the old lumped
``update_section``/``option_*``/``set_status`` triple into what the
tree actually holds: the ADR-domain `update_section`/`option_*` tools
versus the generic `set_status` tool (ADR status changes route through
`general/tools/set_status.py` with `type="adr"`, never an ADR-local
`set_status`), and the file-I/O clause now points at the existing
`adr/tools/` package. (c) The tests/ drops follow the Phase 110 minimal
mechanics exactly: whole-parenthetical citations dropped with their
preceding space, citation-within-parenthetical drops keeping the
parenthetical's own content, possessive citations ("plan §2's source
document") → determiner substitution ("the source document"); no test
assertion needed changing (the 4668-passed final run is the proof), and
`tests/models/adr/v1/examples/README.md` is packaged provenance that no
test loads. (d) The repo-wide check (Task 120.140 item 3) is the
rg-default scan `rg -n "plan §" .`, which excludes `.git` and hidden
directories (including `.specmgr/`); it returns exactly the two frozen
historical artifacts. The `.specmgr/` tree (feature READMEs, session
transcripts, evidence files — this feature's own README included, which
documents the pattern name) carries further `plan §` occurrences as
planning text, not code residue; those documents are historical records
outside this feature's sweep scope (REQ-001/REQ-004). (e) The Updates
entry's long before→after quotes are wrapped so no backtick code span
is left dangling at a line break (the shared markdown-it instance pairs
code spans across line breaks within a paragraph, so a fused
triple-backtick run — a quoted line ending in double backticks plus the
quoting span's own closing backtick — shifts the pairing of every later
span in the paragraph and can leave a `<…>` sequence raw, which the
feat body parser rejects as html_inline); a space before the quoting
span's closing backtick keeps the runs separate.

#### 2026-10-17 18:09:15.261+02:00 - User-directed post-review scope extension (Phase 120)

After the feat-reviewer pass (2026-10-17; verdict: no Errors/Gaps/
Discrepancies, improvements I1–I4), the user directed that the improvements
and the recorded follow-ups be fixed in this feature rather than deferred to
separate issues. Phase 120 therefore extends this feature's work to: (a) I2
— the referent-less "(second half)" fragment left by this feature's own
disclosed Phase 110 repair (strictly this feature's defect); (b) I1 — the
possessive "the plan's" reference to the frozen `adr-tool-plan.md` in
`adr/resources/adr_get.py`'s noqa comment (out of REQ-001's bare `plan §`
pattern, but within the feature's intent); (c) I3 — six pre-existing
stale-wording sites in the files this feature touched (nonexistent
`tools.py` citations, "future parser/validate_adr/tool surface" phrasings) —
the same class as the two stale clauses Phase 110 fixed per its table; (d)
I4 — the stale by-path sibling citation in `uc/models/v2/__init__.py`
(surfaced by Task 110.130's re-check; the one remaining
no-live-citations-clause violation in `src/`; resolved by dropping the citation clause, since a corrected path would still violate the clause); and (e) the recorded `tests/`
residue (16 bare `plan §` hits in 15 files, previously out of scope per
REQ-001's `src/`-only wording — the same user-decision-extension precedent as
feat-198's Task 110.100). The historical scope text (REQ-001, the Explicitly
Out Of Scope bullets) is left unchanged as the record of the requirement as
accepted; this entry and Phase 120 are the disclosure of the widening
(feat-198's I2 precedent). Frozen artifacts (`CHANGELOG.md`,
`docs/adr/7a626b12-….md`) remain untouched: after Phase 120 the repo-wide
`plan §` residue is exactly those two historical records, and `src/` +
`tests/` carry neither a `plan §` hit nor a by-path sibling citation.

#### 2026-10-17 10:06:02.773+02:00 - Stale-clause rewrite wording and minimal grammar-repair policy

Phase 110's judgment calls: (a) For the `adr.py` stale clause (the id/naming
scheme "still an open backlog item"), the rewrite states the now-true fact
WITH a plain formal-ADR-UUID citation (ADR 8cf940c5-3100-485c-a12d-14b59b631712)
rather than a citation-free statement — the governing decision is the content
of the corrected sentence, not provenance for the dropped citation, and every
other design fact in these docstrings cites its formal ADR the same way; the
`summary.py` stale flag needed no wording change, since dropping its citations
removes the stale §8/§9a surface enumeration outright and the docstrings'
existing `list_adr`/feat-13 history text already records the correct account.
(b) Where a dropped possessive or referent citation ("plan §N's X", "the
table's") left a sentence ungrammatical or dangling, the minimal repair was a
determiner substitution ("the rule", "a narrow convenience wrapper", "the H2
sections other") or deletion of the now referent-less phrase — no wording
improved beyond that, per the phase's byte-identity instruction. (c) One line
break inside `models/adr/v1/parser.py`'s module docstring moved (to after
"uses) --") because the byte-level drop of the line-wrapped citation joined
its two lines into a 134-character line and ruff's E501 (line-length 120)
rejects it; the prose is otherwise byte-identical. (d) The I3 re-check found
one pre-existing by-path sibling citation in src/ (`uc/models/v2/__init__.py`
→ `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py`, the file actually
living at `v1/uc_model_v2_draft.py`): out of this feature's scope (no
`plan §` hit, not in the table) — left untouched, reported for a separate
follow-up.

#### 2026-10-17 06:33:49.568+02:00 - All 122 citations Drop-disposed; per-§ ADR governance map recorded

Non-obvious judgment calls from Phase 100: (a) Unlike feat-198 (4 of its 14
sites were ADR substitutions), **every** site here is Drop — the ADR-tooling
docstrings were written in the same 2026-08-03 authoring session as
`adr-tool-plan.md` and quote its wording verbatim, so each citing prose is
already self-contained; a substitution would add a pointer without adding
content. The governing formal ADR for every cited plan § is nevertheless
recorded in the table's `Cited §` column (all nine re-read in full on
2026-10-17 and confirmed to govern: 33c5ab08 filesystem-is-the-sole-source-of-
truth, 4c6119c9 parse-validate-render pipeline, 8cf940c5
id/filename/addressing scheme, 7531106b listing/by-id reads as resources,
bbf412a7 frontmatter extension fields + full-replace contract, 71fd95d7
generic update_section + deletion sentinel, d54abe50 derived Options container
with a dedicated Option sub-API, c73e4f9d MADR 4.0.0 template, ece4554b
domain-first layout + vN versioning), so Phase 110 or a reviewer can cite one
at any site without re-deriving it. (b) Two citations are flagged as stale **in content**, not
just form: `adr.py` line 21's "still an open backlog item (plan §9)" (§9 was
resolved in §9a / ADR 8cf940c5) and `summary.py`'s §8/§9a surface enumeration
(listing became the `list_adr` tool in feat-13) — both rows instruct Phase 110
to drop the citation together with the stale clause. (c) Two line-wrapped
citations the bare `plan §` pattern cannot see (`models/adr/v1/parser.py`
lines 23–24, `adr/tools/_paths.py` lines 29–30) are explicitly recorded so
they get dropped with their sentences. (d) No "other" disposition was needed:
every cited plan section that carries content has a formal ADR, and the two
ADR-less sections (§9 open backlog, §10 next steps) appear only in
self-evident or stale sites that are dropped. (e) The `uc/models/v1/parser.py`
referent was confirmed as `adr-tool-plan.md` §7 (in scope, Drop) rather than
ruled out — see the Design Notes note for the four converging lines of
evidence.

#### 2026-10-06 00:00:00.000Z - Kept separate from feat-198

Decided not to fold this into feat-198-retire-adr-tool-plan-refs despite the overlapping root cause (both are about fragile, redundant citations of `adr-tool-plan.md`). Rationale: feat-198 was already scoped and its GitHub issue (#198) already filed against the narrower 14-citation set before this larger pattern was found; the ~90-reference, 25+-file scale across the most mature domain in the repo deserves its own dedicated investigation and review rather than a late, silent scope expansion.

### Related PRs / Commits

- [Issue #199](https://github.com/dfch/biz.dfch.SpecMgr/issues/199): tracking issue for this feature.
- [Issue #198](https://github.com/dfch/biz.dfch.SpecMgr/issues/198): the narrower, already-scoped sibling this was split out of.
- [PR #217](https://github.com/dfch/biz.dfch.SpecMgr/pull/217): this feature's PR against `dev` — merged 2026-10-18 at `4195a9d`.
- [PR #219](https://github.com/dfch/biz.dfch.SpecMgr/pull/219): second follow-up PR (Task 120.170) against `dev` — merged 2026-10-18 at `095db60`.

### More Information

Originating discussion: feat-198-retire-adr-tool-plan-refs's scoping conversation (2026-10-06).
