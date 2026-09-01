---
created: '2026-09-01T15:14:00.000000'
id: feat-38-39-41-43-44
status: planning
type: feat
updated: '2026-09-01T16:14:12.000000'
version: 1.0.0
---

# Feature: Update-entry formats, newest-first ordering, path safety, and unified timestamps (issues 38/39/41/43/44)

## Plan

### Overview

This feature bundles five open issues into one sequential effort: #38 (drop the enforced em-dash from update-entry headings in favor of ` - ` or ` : `), #39 (SOP `## Updates` must be newest-first, generalized to parse-enforced ordering across DEC/VCR/TSK as well), #41 (remove the pylint W0622 redefined-builtin warnings for the intentional `id`/`type` parameter names), #43 (extend feat-36-delete's `_path_safety` guards to `get_<d>`, `update`, and `set_status`), and #44 (unify every artifact timestamp into exactly two variants, `yyyy-MM-dd` and `yyyy-MM-dd HH:mm:ss.fff` + (`Z` or `±HH:mm`), with frontmatter `created`/`updated` strictly enforced as date+time). Each issue is its own phase (Phases 1 to 5). Phases 1 to 3 share the update-entry surface and are strictly ordered; Phases 4 and 5 are independent of each other and slot in after Phase 3. No phase implements another phase's scope.

### Requirements

- REQ-001: The SOP `UpdateEntry` and the FEAT `UpdateEntry`/`DecisionEntry` heading regexes accept exactly ` - ` or ` : ` as the separator between timestamp and title and reject the em-dash `—` (strictly: em-dash entries fail to parse).
- REQ-002: No packaged template, example, or instructions file (sop/feat/dec/vcr; tsk already conforms) uses an em-dash in update-entry headings or heading-convention text.
- REQ-003: Every repo-owned artifact carrying em-dash update entries is migrated to the new separator (the docs/sop SOP entries, the feat-36 README entries, and this feature README's own entries).
- REQ-004: The SOP `## Updates`, DEC `## Updates`, VCR `## Updates`, and TSK `## Recent Updates` sections enforce newest-first ordering at parse time; the DEC/VCR/TSK entries become timestamp-led (`yyyy-MM-dd` or the full date+time variant, then ` - ` or ` : `, then a title) so ordering can be validated; SOP/FEAT entries stay date+time-only.
- REQ-005: The SOP/DEC/TSK update containers gain leading-HTML-comment support (the `MarkdownSection2WithComment` shape), the packaged templates carry a "newest first, prepend" ordering hint, and the create/update instructions of all four domains direct prepending instead of appending.
- REQ-006: The shared `MarkdownFrontmatter` fields `created`/`updated` accept only the date+time variant `yyyy-MM-dd HH:mm:ss.fff` + (`Z` or `±HH:mm`) at parse time (date-only is rejected; blank/absent stays `None`); the fields remain system-owned (no tool parameter exposes them).
- REQ-007: Every tool-written `created`/`updated` value (the 11 `create_<d>` tools, the 22 `update` adapter sites, and the 11 `set_status` adapter sites) is produced by one shared helper that emits the date+time variant from `datetime.now().astimezone()`, with `Z` when the UTC offset is zero and `±HH:mm` otherwise, and milliseconds truncated to exactly three digits.
- REQ-008: All legacy repo timestamps (frontmatter of the five parseable documents plus the twenty-one legacy feat READMEs, and non-conforming packaged body-entry values) are migrated under the D7 rules: date-only becomes midnight UTC `00:00:00.000Z`, partial times are padded and assumed UTC, microsecond values are truncated to milliseconds and assumed UTC `Z`, and literal placeholders take the containing folder's first git-commit timestamp (UTC); `created:`/`updated:` lines inside code fences are excluded; all test-fixture `created`/`updated` values (~49 files) are normalized to the conforming date+time shape.
- REQ-009: The twelve `get_<d>` tools (including `get_adr`), the generic `update`, and the generic `set_status` validate `id` via `_path_safety.validate_id` before any filesystem access and confine the resolved path with `_path_safety.assert_within` after resolution; `validate_id` additionally accepts `adr` (a UUID domain); `delete` behavior is unchanged.
- REQ-010: The pylint W0622 (redefined-builtin) count drops to zero via one explicit module-level `# pylint: disable=redefined-builtin` line with a rationale comment in each of the 39 affected files; no global pylint config change, so a future file shadowing `id`/`type` without the comment keeps warning.

### Acceptance Criteria

- [ ] ACC-001: Verifies REQ-001 - a SOP/FEAT update entry with an em-dash separator fails to parse (eagerly, with a validation/alias error); entries using ` - ` and ` : ` parse and expose correct computed `timestamp`/`title`.
- [ ] ACC-002: Verifies REQ-002 - a repo-wide grep finds no em-dash in any update-entry heading or heading-convention text in the sop/feat/dec/vcr/tsk packaged data; schema JSONs and docs regenerate drift-free via the pre-commit hooks.
- [ ] ACC-003: Verifies REQ-003 - the docs/sop SOP, the feat-36 README, and this feature README all parse under the post-migration model, with only separators (and, per ACC-004, ordering) changed.
- [ ] ACC-004: Verifies REQ-004/REQ-005 - in all four domains, older-before-newer entries fail to parse; newest-first, equal timestamps, and same-day date-only/date+time pairs parse; DEC/VCR/TSK entries without a timestamp-led heading fail to parse; the templates carry the ordering-hint comment; the repo's own docs parse.
- [ ] ACC-005: Verifies REQ-006 - the parser rejects frontmatter `created`/`updated` values that are date-only, six-digit fraction, `T`-separated, timezone-less, or otherwise non-conforming; it accepts the `Z` and `±HH:mm` date+time variants; blank/absent stays `None`.
- [ ] ACC-006: Verifies REQ-007 - a freshly created/updated/status-changed document carries `created`/`updated` values matching `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2})$` (three-digit milliseconds, timezone information present).
- [ ] ACC-007: Verifies REQ-008 - after migration, every repo frontmatter `created`/`updated` value and every test fixture is conforming, and the full unittest suite is green.
- [ ] ACC-008: Verifies REQ-009 - injection ids (`../x`, `a/b`, `..`, malformed UUID/feat ids) against `get_<d>`/`update`/`set_status` raise `ValueError` before any filesystem access (seeds untouched); `assert_within` is spy-verified inside each adapter's lock; valid flows stay byte-identical; `delete` is unchanged.
- [ ] ACC-009: Verifies REQ-010 - `uv run --frozen pylint $(git ls-files '*.py')` reports zero W0622 with all other baseline findings unchanged; `pyproject.toml` is untouched.

### Scope

#### Included

- SOP/FEAT update-entry separator regexes, computed fields, and docstrings (Phase 1)
- SOP/DEC/VCR/TSK packaged templates, examples, and create/update instruction data (Phases 1 to 3)
- Migration of the repo's own artifacts: docs/sop x1, docs/tsk x2 (verification only), `.specmgr/feat/feat-36-delete`, and this feature README (Phases 1 to 3)
- Newest-first ordering validation, timestamp-led DEC/VCR/TSK headings, `WithComment` promotion, and ordering-hint templates (Phase 2)
- Shared timestamp helper, all 44 generator sites, the frontmatter format validator, test-fixture normalization, and data/template alignment (Phase 3)
- `_path_safety` extension (`adr`), wiring into the twelve `get_<d>` tools plus `update` and `set_status`, and injection tests (Phase 4)
- The 39 per-file pylint disable lines plus baseline verification (Phase 5)
- CHANGELOG `[Unreleased]` entries (BREAKING markers for Phases 1 to 3), AGENTS.md propagation (Phase 4), and the `server.py` docstring, `docs/MCP.md`, and schema JSONs (via pre-commit hooks)

#### Explicitly Out Of Scope

- Body migration of the twenty-one legacy feat READMEs (they predate the feat-31 schema and fail to parse for unrelated structural reasons; frontmatter only, per REQ-008)
- ADR frontmatter: it has no `created`/`updated` fields, and the MADR `date` stays free-form (D9)
- Prose em-dashes outside artifact formats (AGENTS.md, docstrings, `rsk_tara.md`/`rsk_risk_matrix.md` prose, the qa_example title)
- The twelve pre-existing W0611 unused-import findings in `server.py` (intentional side-effect imports; a different warning class than W0622)
- Migration of downstream users' documents (the D10 break is accepted; their documents migrate naturally or via a user-side pass)
- Renaming the branch `feat-38-39-31-43-44` (the folder/README id is authoritative, per D1)
- Any tool parameter exposing `created`/`updated` (the system-owned invariant is preserved)

### Dependencies

#### Depends On

- feat-36-delete (done): the reusable `general/tools/_path_safety.py` module, Phase 4's only code dependency
- `origin/dev` at or after `8c13e16`: the branch was fast-forwarded before the design concluded and is merged again before implementation starts

### Design Notes

The canonical timestamp variants (D4/D7): date `^\d{4}-\d{2}-\d{2}$`; date+time `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2})$` (space separator, exactly three millisecond digits, `Z` for UTC or a signed `±HH:mm` offset). Tool-produced values use local time with the actual offset and `Z` when the offset is zero (deterministic under CI). The Phase 1/2 entry heading shape is `{date+time or date}` + `( - | : )` + `{title}`: the SOP/FEAT alias becomes `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2})(?: - | : ) .+$` and the new DEC/VCR/TSK alias `^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(Z|[+-]\d{2}:\d{2}))?(?: - | : ) .+$`; the separator group is non-capturing, so the computed `timestamp`/`title` fields are unchanged.

The Phase 3 validator lives on the shared `MarkdownFrontmatter` (`models/md/frontmatter.py`) as a `mode="after"` field validator over `created`/`updated` (it runs after the inherited blank-to-None normalization): `None` passes, and any other value must fullmatch the date+time regex; date-only is rejected for these two fields (D5). One base class covers all eleven whole-body domains; the ADR frontmatter (`models/adr/v1/frontmatter.py`) carries no such fields and stays untouched (D9). No tool exposes `created`/`updated` as a parameter (the `create_<d>` tools seed both, `update`/`set_status` bump only `updated`), so the format is system-controlled end to end (the D5 invariant).

Phase 2 adds a shared pure helper `models/md/_ordering.py` (no `mcp` dependency, mirroring the `models/md/_util.py` precedent): `validate_newest_first(timestamps, label)` compares consecutive entries with `datetime.fromisoformat` (aware comparison; `Z` is supported on 3.11+), with the mixed-granularity rule that when either side is date-only the comparison happens at day granularity, and equal values (same day, or identical timestamps) are allowed. The four domains' validators (`sop.Updates` new, `dec.Updates` new, `vcr.Updates` new, `tsk.RecentUpdates` new) delegate to it, sharing one implementation with the untouched FEAT precedent. The SOP/DEC/TSK update containers are promoted from `MarkdownSection2` to `MarkdownSection2WithComment` (VCR already is) purely to carry the FEAT-style `<!-- Newest entry first -- prepend ... -->` hint in templates; the added `comment` field is optional, so direct construction is unaffected.

The D7 migration is mechanical per value: date-only becomes ` 00:00:00.000Z` appended (midnight UTC); partial times (e.g. `05:42`) are padded to `HH:mm:ss.fff` and assumed UTC `Z`; microsecond values (`T`- or space-separated) become space-separated, the fraction is truncated to three digits, and UTC is assumed `Z` (no timezone conversion: the original instant is deliberately reinterpreted as UTC per the requester); literal `YYYY-MM-DD` placeholders take the containing folder's first git-commit timestamp (UTC, `Z`). Scope: real frontmatter blocks only, so `created:`/`updated:` lines inside code fences of the legacy READMEs (prose) are excluded (D8). The five parseable repo documents (docs/sop x1, docs/tsk x2, the feat-36 README, and this feature README) must migrate in Phase 3 or the tools stop working on them; the twenty-one legacy feat READMEs get frontmatter-only normalization so a later body-migration effort does not have to re-derive the rule.

Phase 4 mirrors the `delete` contract (`general/tools/delete.py`): the public `update`/`set_status` call `validate_id(type, id)` before dispatch (a `ValueError` before any filesystem access), and every adapter calls `assert_within(base_dir, path)` after `load_by_id` inside the domain lock; the twelve `get_<d>` tools apply the same two guards without a lock (reads do not mutate). `_path_safety._UUID_TYPES` gains `"adr"` (eleven UUID domains; `delete`'s `Literal` still excludes `adr`, so its behavior is unchanged), and the `validate_id` docstring/error text are updated accordingly.

Phase 5 adds one module-level `# pylint: disable=redefined-builtin` line with a one-line rationale (e.g. "`id`/`type` intentionally shadow the builtins: public tool API, issue #41") after the license header of each of the 39 baseline files (38 x `id` shadows across the `get_<d>` tools, the per-domain update/implement prompts, the ADR tools/resources/prompts, and the `update`/`set_status`/`delete` public functions; 4 x `type` shadows in those same three generic tools plus `models/md/markdown.py`/`alias.py`). No `pyproject.toml` change (D6): the tripwire stays effective for any future file.

Each phase ends gate-green: `ruff format --check` + `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full unittest suite (baseline 2713 tests at `8c13e16`), advisory pylint with no new findings against the captured baseline (42 x W0622, 12 x W0611, score 9.34/10), and the pre-commit regenerations (`specmgr schema` into `docs/` plus each domain's `data/`, `specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`) drift-free. Phases 1, 2, and 3 each record a CHANGELOG `[Unreleased]` entry with a BREAKING marker (em-dash rejection; newly constrained TSK/DEC/VCR headings; frontmatter format enforcement). This README's own entries are written in the currently enforced shapes (em-dash headings, `T`+microsecond frontmatter) so the Phase 1 and Phase 3 migration rules are exercised on it too; its frontmatter `updated` is bumped and a `### Updates` entry is prepended at every phase end.

### Related Decisions

- ADR 1af6787b-eaab-4e8f-888f-531c1e76c19d (feat-36): path-safety guards for the generic delete, Phase 4's direct precedent
- ADR 36905d5b-8057-4294-8665-c7eed5534db0: dispatch-only generic-tool convention (the adapter shape Phase 4 extends)
- ADR 8cf940c5-3100-485c-a12d-14b59b631712: feat folder-per-document addressing (`assert_feat_id` in Phase 4; this folder's own id)
- ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614: id-based reads are `get_<d>`-only (Phase 4 covers every `get_<d>`)
- ADR 9c687bb1-8ee7-41c8-84ec-07606356bc73: pre-commit enforcement of docs/schema drift (the per-phase gate)

### Task List

#### Phase 1: Em-dash out of update entries (issue 38)

- [ ] Task 1.1: Change the SOP `UpdateEntry` alias and `_UPDATE_ENTRY_HEADING_PATTERN` to `(?: - | : )`; update docstrings - depends on: none - status: not-started
- [ ] Task 1.2: Change the FEAT `_ENTRY_HEADING_ALIAS`/`_ENTRY_HEADING_PATTERN` (covers `UpdateEntry` and `DecisionEntry`); update docstrings - depends on: none - status: not-started
- [ ] Task 1.3: Rewrite the SOP packaged data (template/example/create-instructions) to the new separators - depends on: Task 1.1 - status: not-started
- [ ] Task 1.4: Rewrite the FEAT packaged data (template/example/create-instructions) - depends on: Task 1.2 - status: not-started
- [ ] Task 1.5: Rewrite the DEC/VCR convention text (model docstrings + template/example/create-instructions) - depends on: none - status: not-started
- [ ] Task 1.6: Migrate repo artifacts (docs/sop entries, feat-36 README entries, this README's entries) - depends on: Tasks 1.1-1.2 - status: not-started
- [ ] Task 1.7: Update the SOP/FEAT/DEC/VCR test fixtures (parser + body tests) - depends on: Tasks 1.1-1.5 - status: not-started
- [ ] Task 1.8: Phase gate (schema/docs/mcp-docs regen, suite, pylint, CHANGELOG BREAKING entry, this README's Updates) - depends on: Tasks 1.6-1.7 - status: not-started

#### Phase 2: Newest-first ordering enforced in SOP/DEC/VCR/TSK (issue 39)

- [ ] Task 2.1: Shared `models/md/_ordering.py` helper + unit tests (aware comparison, day-granularity rule, equals allowed) - depends on: Phase 1 - status: not-started
- [ ] Task 2.2: SOP `Updates._validate_newest_first` (delegates to the helper) + out-of-order parse tests - depends on: Task 2.1 - status: not-started
- [ ] Task 2.3: DEC/VCR/TSK timestamp-led `UpdateEntry` alias + `timestamp` computed field + section validators + tests - depends on: Task 2.1 - status: not-started
- [ ] Task 2.4: Promote SOP/DEC/TSK containers to `MarkdownSection2WithComment`; ordering-hint comments in templates; reword all four domains' create/update instructions to prepend - depends on: Tasks 2.2-2.3 - status: not-started
- [ ] Task 2.5: Re-order the docs/sop entries newest-first; verify the docs/tsk entries against the new alias - depends on: Tasks 2.2-2.3 - status: not-started
- [ ] Task 2.6: Phase gate (regens, suite, pylint, CHANGELOG BREAKING entry, this README's Updates) - depends on: Tasks 2.4-2.5 - status: not-started

#### Phase 3: Unified timestamp format (issue 44)

- [ ] Task 3.1: `general/tools/_timestamps.py` helper (`now_timestamp`, `format_timestamp`, `format_date`; `Z` for zero offset; three-digit ms) + unit tests - depends on: Phase 2 - status: not-started
- [ ] Task 3.2: `MarkdownFrontmatter.created`/`updated` date+time-only validator (D5) + tests (reject date-only/microseconds/`T`/timezone-less; accept `Z`/offset) - depends on: none - status: not-started
- [ ] Task 3.3: Replace all 44 generator sites (11 create, 22 update, 11 set_status) with the helper - depends on: Tasks 3.1-3.2 - status: not-started
- [ ] Task 3.4: Migrate repo documents per D7/D8 (five parseable docs mandatory; twenty-one legacy feat READMEs frontmatter-only; placeholders to first-commit timestamp) - depends on: Task 3.2 - status: not-started
- [ ] Task 3.5: Normalize every test-fixture `created`/`updated` value (~49 files) to conforming date+time - depends on: Task 3.2 - status: not-started
- [ ] Task 3.6: Normalize packaged body-entry values (vcr_template seconds; tsk_template/tsk_example `05:42` times) and align `.specmgr/_template/v1/README.md` with the enforced feat convention - depends on: Phase 2 - status: not-started
- [ ] Task 3.7: Reword the "microsecond timestamp" docstrings (`update.py`, `set_status.py`, feat models) - depends on: Task 3.3 - status: not-started
- [ ] Task 3.8: Phase gate (regens, suite, pylint, CHANGELOG BREAKING entry, this README's Updates + its own frontmatter/entry migration) - depends on: Tasks 3.3-3.7 - status: not-started

#### Phase 4: `_path_safety` in `get_<d>`/`update`/`set_status` (issue 43)

- [ ] Task 4.1: `_path_safety` gains `"adr"` (`_UUID_TYPES` + docstring/error text) + `test__path_safety` updates - depends on: Phase 3 - status: not-started
- [ ] Task 4.2: Public `update` calls `validate_id` before dispatch + `assert_within` in the eleven adapters + injection/defense-in-depth tests modeled on `test_delete.py` - depends on: Task 4.1 - status: not-started
- [ ] Task 4.3: Same for public `set_status` (twelve adapters incl. adr) + tests - depends on: Task 4.1 - status: not-started
- [ ] Task 4.4: Same for the twelve `get_<d>` tools (incl. `get_adr` via `find_adr_path`) + parameterized injection tests - depends on: Task 4.1 - status: not-started
- [ ] Task 4.5: Update tool docstrings/descriptions with the ValueError contract; propagate the AGENTS.md `general/` bullet; `server.py` docstring + `docs/MCP.md` via hooks - depends on: Tasks 4.2-4.4 - status: not-started
- [ ] Task 4.6: Phase gate (regens, suite, pylint, CHANGELOG entry, this README's Updates) - depends on: Task 4.5 - status: not-started

#### Phase 5: Pylint W0622 per-file disables (issue 41)

- [ ] Task 5.1: Add the module-level `# pylint: disable=redefined-builtin` line with rationale to the 39 baseline files - depends on: Phase 4 - status: not-started
- [ ] Task 5.2: Verify the full pylint run: zero W0622, all other findings unchanged against the captured baseline - depends on: Task 5.1 - status: not-started
- [ ] Task 5.3: Record in this README's Decisions Made + CHANGELOG entry + phase gate (regens, suite, this README's Updates) - depends on: Task 5.2 - status: not-started

## Progress

### Current Status

As of 2026-09-01: the design phase is complete. All five issues were examined against the codebase at `origin/dev` `8c13e16` (baseline: 2713 tests green; pylint 42 x W0622 across 39 files; after the post-plan merge of `8e07594`, 2720 tests green and only two of the twenty-two repo feat READMEs parse under the feat model: `feat-36-delete` and this one). Decisions D1 to D10 are locked with the requester and logged under `### Decisions Made`; nothing is implemented yet. Next: start Phase 1 (issue #38).

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 16:14:12.000+02:00 — Design session wrap-up: issue links recorded, pylint baseline re-verified

Closed out the design session: added the `### Related PRs / Commits` section with the five source-issue URLs (one phase each) and the design-session commits, and re-ran the advisory pylint baseline on the post-merge tree to confirm Phase 5's inventory is still exact (42 x W0622 in the same 39 files, score 9.34/10, unchanged by the `8e07594` merge). Nothing else outstanding; the branch is pushed and ready for Phase 1.

#### 2026-09-01 15:42:48.000+02:00 — Merged origin/dev (8e07594) after the plan commit; counts updated

After committing the plan, upstream dev had gained one commit, `8e07594` (feat-40 docs pruning: `specmgr docs` now prunes stale `docs/api` pages; it also brought the `feat-32-sysrs` and `feat-40-docs-prune` folders and a CHANGELOG entry). It was merged into this branch (merge commit on top of the plan commit, not pushed). The feat parse inventory was re-verified on the merged tree: twenty-two feat READMEs, only `feat-36-delete` and this one parse, so the plan's migration counts were updated in place (REQ-008, Scope, Design Notes, Task 3.4, and decision D8: nineteen legacy READMEs becomes twenty-one; four parseable mandatory-migration documents becomes five, counting this README). The full unittest suite is green on the merged tree (2720 tests). No code changes.

#### 2026-09-01 15:14:00.000+02:00 — Feature planned from issues 38, 39, 41, 43, 44 (design phase complete)

The plan was written after fetching the five GitHub issues and examining the affected surfaces: the SOP/FEAT em-dash-enforced entry regexes (`sop/models/v1/body.py` line 421, `feat/models/v1/body.py` line 425), the DEC/VCR free-form conventions, the FEAT `_validate_newest_first` precedent, the feat-36 `_path_safety` module, the 44 `datetime.now().isoformat(timespec="microseconds")` generator sites, the free-form `MarkdownFrontmatter.created`/`updated`, and the captured pylint baseline (42 x W0622 in 39 files, 12 x W0611 in `server.py`, score 9.34/10). The branch was fast-forwarded to `origin/dev` `8c13e16`, uv synced with all extras on Python 3.13.13, and pre-commit installed, with the full suite (2713 tests) green as the baseline. No code changes yet.

### Decisions Made

#### 2026-09-01 15:14:00.000+02:00 — D7/D5 refinements: frontmatter is date+time-only and system-owned; migration assumes UTC

The requester confirmed that frontmatter `created`/`updated` must enforce date+time (date-only rejected) and that these fields are system-owned: the MCP tools always write them, and no tool parameter lets an agent set them manually (the existing invariant is preserved). The migration rule for legacy values was fixed (D7): date-only values become midnight UTC `00:00:00.000Z`; values with microseconds are truncated to milliseconds, use no timezone, and assume UTC (`Z`); partial times are padded and assumed UTC; literal `YYYY-MM-DD` placeholders take the containing folder's first git-commit timestamp (UTC, `Z`).

#### 2026-09-01 15:05:00.000+02:00 — D5/D8/D10: frontmatter format enforced strictly at parse; repo documents migrate in Phase 3

Chosen over "tools only produce it": the shared `MarkdownFrontmatter` gains a date+time-only validator for `created`/`updated`, so a non-conforming document fails to parse (it appears missing from `get`/`list`/`update`/`set_status`/`delete`). Migrating the repo's own artifacts is part of Phase 3 (D8): the five parseable documents (docs/sop x1, docs/tsk x2, the feat-36 README, and this feature README) are mandatory, the twenty-one legacy feat READMEs get frontmatter-only normalization, and code-fence `created:`/`updated:` prose lines are excluded. ADR frontmatter is untouched (D9: no created/updated fields; the MADR `date` stays free-form). The hard break for downstream documents was accepted (D10).

#### 2026-09-01 14:50:00.000+02:00 — D1/D2/D3/D4/D6: folder name, separators, ordering scope, timezone, pylint style

The folder/README id is `feat-38-39-41-43-44` (D1; the `31` in the branch name is a typo for issue 41, and the branch keeps its name). Update-entry headings accept both ` - ` and ` : ` separators, and the em-dash is strictly rejected with in-phase migration of the repo's artifacts (D2). Newest-first ordering is enforced at parse time across SOP, DEC, VCR, and TSK (not SOP-only), which requires the DEC/VCR/TSK entries to become timestamp-led (D3). Date+time values carry local time with the actual offset, or `Z` for UTC (D4; the issue's example was acknowledged as sloppy, the intent is "use tz info", and `Z` is allowed as well). The W0622 elimination uses explicit per-file pylint disable comments instead of a global config, so the shadowing stays visibly intentional in every affected file (D6).

### Related PRs / Commits

Source issues (one phase each):

- [Issue #38](https://github.com/dfch/biz.dfch.SpecMgr/issues/38): Replace "em-dash" in Sop.Updates section with "colon" or "dash" (Phase 1)
- [Issue #39](https://github.com/dfch/biz.dfch.SpecMgr/issues/39): Sop.Updates are ascending and not descending (Phase 2)
- [Issue #41](https://github.com/dfch/biz.dfch.SpecMgr/issues/41): Examine pylint W0622 id/type (Phase 5)
- [Issue #43](https://github.com/dfch/biz.dfch.SpecMgr/issues/43): `get_<d>`, `update`, `set_status` must use `_path_safety` (Phase 4)
- [Issue #44](https://github.com/dfch/biz.dfch.SpecMgr/issues/44): Timestamps in artifact must use the same format (Phase 3)

Design-session commits on `feat-38-39-31-43-44`:

- `4f88880`: plan created
- `019a49b`: merged `origin/dev` (`8e07594`, feat-40 docs pruning)
- `1958c11`: plan counts updated for the post-merge parse inventory
