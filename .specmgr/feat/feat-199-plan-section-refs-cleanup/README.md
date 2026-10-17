---
classification: null
created: '2026-10-06T10:45:41.464+02:00'
id: feat-199-plan-section-refs-cleanup
status: progress
type: feat
updated: '2026-10-17T10:06:02.773+02:00'
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

- [ ] ACC-001: Verifies REQ-001 — a sweep for the bare `plan §` pattern across all of `src/` returns no results (the same pattern and scope Task 100.100's investigation uses, so the acceptance check and the investigation cannot diverge).
- [ ] ACC-002: Verifies REQ-002 — disposition table recorded in this file's Design Notes, one row per distinct reference site (or logical group).
- [ ] ACC-003: Verifies REQ-003 — `uc/models/v1/parser.py`'s hit is explicitly addressed (confirmed in/out) with rationale recorded.
- [ ] ACC-004: Verifies REQ-004 — `git diff` shows no changes under `.specmgr/feat/feat-9-doc-in-specmgr/`.

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

## Progress

### Current Status

**As of 2026-10-17**: Phase 110 (Implementation) is complete — status `progress`. All **124 citations** (the 122 bare-`plan §` hits across 27 `src/` files plus the 2 line-wrapped citations the bare pattern cannot see) were dropped per Task 100.100's disposition table — 0 ADR substitutions — with the two stale-in-content clauses handled per their rows: `models/adr/v1/adr.py`'s module docstring now states the resolved specmgr-assigned `{id}-{slug}.md` id/naming scheme (with a plain ADR 8cf940c5-3100-485c-a12d-14b59b631712 citation; the "still an open backlog item" clause is gone), and `models/adr/v1/summary.py` needed no rewrite (dropping its §8/§9a citations removes the stale surface enumeration; its existing `list_adr`/feat-13 history text stays byte-identical). The `uc/models/v1/parser.py` hit dropped exactly as the table specifies, and the out-of-pattern "Task 3.2" markers in `create_adr.py`/`validate_adr.py` are untouched. No test assertions broke (4668 passed / 17 skipped / 5662 subtests on the first run, 4668 passed / 17 skipped on the final run), the full quality gate is green (`ruff format --check` over 2062 files, `ruff check`, `vulture`, full suite), and `docs/api/` + `docs/GENERATED.md` + `docs/MCP.md` were regenerated so the pattern now survives in `docs/` only in the frozen ADR `docs/adr/7a626b12-….md`. ACC-001's sweep (`rg -n "plan §" src/`) returns no results and the feat-9 frozen directory is untouched (ACC-004); the `tests/` residue is 16 bare-shorthand hits in 15 files (no paths), and the I3 re-check found one pre-existing, out-of-scope by-path sibling citation (`uc/models/v2/__init__.py` → the stale `feat-4-use-cases/uc_model_v2_draft.py` path) reported for a separate follow-up. The feature is ready for the orchestrator's acceptance-criteria walk.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

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

### More Information

Originating discussion: feat-198-retire-adr-tool-plan-refs's scoping conversation (2026-10-06).
