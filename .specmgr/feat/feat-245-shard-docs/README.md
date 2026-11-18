---
classification: null
created: '2026-10-31T17:51:01.215+01:00'
id: feat-245-shard-docs
status: planning
type: feat
updated: '2026-11-18T15:42:54.619+01:00'
version: 1.0.0
---

# Feature: Shard document storage by uuid prefix

## Plan

### Overview

Per-type document directories (`docs/<type>/`) currently hold every document of the type flat in one directory. As corpora grow this bounds nothing: a cold per-id resolution parses every file of the domain before it finds the target (the same cold-scan class feat-187 fixed for `list_feat`), and directory-level operations (git, glob, OS) degrade with file count. This feature shards all thirteen UUID whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs, txt, set — `feat` is the only non-UUID whole-body domain and stays excluded; ADR is no longer a domain at all, removed per issue #46) into 256 shard subdirectories under a per-language directory, using one uniform layout for every language including English: `docs/<type>/<lang>/<id[:2]>/<uuid>-<slug>.md` (English files move from the flat `docs/<type>/` to `docs/<type>/en/<shard>/`, retiring the flat-EN location of DEC 38efdb66-8025-45c5-bbe8-45b25fc7a772 item 1, whose compatibility argument sharding already voids). File names drop the `<type>-` prefix, extending DEC's existing `<uuid>-<slug>.md` convention to the other twelve sharded domains. Every MCP read path is restricted to the sharded layout (hard cut-over); the `specmgr-lint` gate recognizes the new layout with misplaced files becoming a blocking layout violation; the 76 in-repo documents are migrated in the same change. It is a breaking change for downstream users with pre-existing flat trees, documented as such. Implements issue #245.

### Requirements

- REQ-001: Documents of the thirteen UUID whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs, txt, set) are stored one per shard subdirectory under the domain's per-language directory, for every language including EN: `docs/<type>/<lang>/<id[:2]>/<uuid>-<slug>.md`, the shard named by the first two hex digits of the document's uuid.
- REQ-002: Document file names carry no type prefix: a file is named `<uuid>-<slug>.md` (slug derived from the H1 title by the existing slugify rules), extending DEC's existing `<uuid>-<slug>.md` convention to the other twelve sharded domains.
- REQ-003: The MCP read path is shard-only for every language: a language's scan yields files exactly one subdirectory level below the language directory (`docs/<type>/<lang>/*/*.md`); files directly under `docs/<type>/` (missing language dir) or directly under `docs/<type>/<lang>/` (missing shard dir) are invisible to `list_<d>`, `get_<d>`, id resolution, `list_languages`, and the similarity corpus.
- REQ-004: Id resolution first scans the shard derived from the id (`id[:2]`) within the language's own directory (EN = the `en/` directory); a document whose placement disagrees with its id is still found by the full sharded-listing fallback of that language (the filesystem remains the sole source of truth).
- REQ-005: Every `create_<d>` tool (the thirteen domains, every language including EN) writes through the single shared `sharded_doc_path(base_dir, id_, slug)` helper in `general/tools/_doc_paths.py` over `doc_base_dir(type, language)` — which now resolves every language, EN included, to `docs/<type>/<lang>/` — and creates the shard directory; no per-domain filename line and no flat-EN base resolution remain.
- REQ-006: The `specmgr-lint` gate recognizes the sharded layout (anchored pattern + `_infer_type`, all three drift-pinned copies): the one valid file shape is `docs/<type>/<lang>/<2-hex-shard>/<file>.md`; a file that misses the language dir, misses the shard dir, carries a non-hex shard, or sits deeper than one shard level is a layout violation failing with exit 2 naming the correct path; a language dir without a packaged heading table is placement-valid but its files take the existing no-table content error; non-domain dirs (e.g. `docs/archive/`, depth ≥ 3) keep today's skip behavior.
- REQ-007: The 76 existing in-repo documents (48 dec, 14 req, 4 tsk, 3 qa, 3 sop, 2 gol, 1 sysrs, 1 txt) are moved into `docs/<type>/en/<shard>/` in the same change as the code (`git mv`; the 48 dec files are already prefix-less and move only, the remaining 28 drop the `<type>-` prefix — move + rename, 100% similarity, history preserved).
- REQ-008: `list_<d>` result order and `ref` semantics are preserved in the thirteen domains (EN and every language): order equals lexicographic file-name order within a language's sharded listing and `ref = path.stem = <uuid>-<slug>` for documents carrying a frontmatter `id`; id-less documents keep author-chosen stems (no uuid prefix) and remain list-visible only when placed inside a shard dir (see the Id-less documents design note).
- REQ-009: The breaking change is documented: CHANGELOG `[Unreleased]` (pre-existing flat trees invisible until moved under `<lang>/<shard>/`; file names lose the `<type>-` prefix; `ref` values change; English moves into `en/`), README, AGENTS.md (including the feat-197-i18n layout paragraph), and the `specmgr://i18n` guidance all describe the uniform layout, and a new DEC records the decision.

### Acceptance Criteria

- [ ] ACC-001: `create_<d>` places the file at `docs/<type>/en/<id[:2]>/<uuid>-<slug>.md` and leaves nothing directly under `docs/<type>/` or `docs/<type>/en/`, asserted for all thirteen domains (REQ-001, REQ-002, REQ-005).
- [ ] ACC-002: every `ref` reported by `list_<d>` (EN or a language variant) in the thirteen domains starts with the document uuid (no `<type>-` prefix) for documents carrying a frontmatter `id` (id-less documents keep author-chosen stems, no uuid prefix) and `list` order equals lexicographic file-name order (REQ-002, REQ-008).
- [ ] ACC-003: a file hand-placed directly under `docs/<type>/` or directly under `docs/<type>/<lang>/` appears in no `list_<d>` result and is unresolvable by `get_<d>` or `list_languages` (REQ-003).
- [ ] ACC-004: a document moved to a wrong shard dir (EN or variant) resolves by id with byte-identical content via the fallback scan (REQ-004).
- [ ] ACC-005: staging `docs/req/foo.md` (missing language dir), `docs/req/en/foo.md` (missing shard dir), `docs/req/en/zz/x.md` (non-hex shard), and `docs/req/en/10/20/x.md` (deeper than one shard level) each fails the lint gate with exit 2 and the correct path in the message; a valid EN shard file, a valid variant shard file, and non-domain dirs (e.g. `docs/archive/`, depth ≥ 3) lint clean (REQ-006).
- [ ] ACC-006: after migration, `git ls-files` over the thirteen domain dirs matches only `en/<2-hex>/<uuid>-<slug>.md` paths, `git log --follow` shows preserved history, and `specmgr lint --all` exits 0 (REQ-007).
- [ ] ACC-007: CHANGELOG `[Unreleased]`, README, AGENTS.md (including the i18n layout paragraph), the `specmgr://i18n` guidance, and the new DEC all describe the uniform layout, and the breaking note names the flat-tree visibility loss, the English `en/` move, and the `ref`/file-name change (REQ-009).
- [ ] ACC-008: `list_languages` still probes every shape-valid two-letter base-level dir (a dir without a packaged heading table yields its existing no-table/unparseable entries), the EN-only consumers (`list_references`, `find_related`, `find_similar_text`, `get_reference_diagram(_all)`) are re-rooted at the `en/` dir and see EN files only, never variant files, and `get_<d>(language=…)`/`create_<d>(language=…)` round-trip a sharded variant (REQ-003, REQ-005; DEC 38efdb66-8025-45c5-bbe8-45b25fc7a772).
- [ ] ACC-009: `parse_<d>` derives the language from the path's first subdirectory under the domain base (shape-valid two letters; `en` ⇒ canonical) and parses sharded files under any language dir; a file at any other position parses canonical and is caught by the placement gate — asserted for all thirteen `parse_<d>` tools (REQ-003, REQ-006).

### Scope

#### Included

- Sharded layout core in `general/tools/_doc_paths.py`: `SHARD_DIGITS`, `shard_token`, `sharded_doc_path`, `doc_base_dir`/`ensure_doc_base_dir` resolving every language (EN included) to `docs/<type>/<lang>/`, the shard-only per-language scan (`<lang-dir>/*/*.md`), first-subdirectory language derivation, shard-narrowed id resolution with full per-language fallback
- Wiring the thirteen `create_<d>` tools (every language including EN) through the shared helper
- `specmgr-lint` layout recognition + the single-shape placement validator, and the anchored artifact pattern in the three drift-pinned copies (pre-commit hook, CI workflow, test constant)
- One-off in-repo migration of the 76 documents into `en/<shard>/` (`git mv`; 48 dec move-only, 28 move + rename)
- Test sweep across the suite for the new layout, including the feat-197-i18n suites (`test_i18n_*`, `test_language_guard`, `test_list_languages`, `test_check_translation_drift`, the EN-only-consumer pinning tests) re-seeded to `en/<shard>/` + `<lang>/<shard>/`
- Documentation: README, AGENTS.md (per-domain layout bullets + the feat-197-i18n paragraph), the `specmgr://i18n` guidance data file, `SPECMGR_DOCS_DIR` registry description, CHANGELOG `[Unreleased]`, new DEC

#### Explicitly Out Of Scope

- `feat` (folder-per-document, non-uuid ids) sharding — ADR is no longer a domain (removed per issue #46), so no ADR scope remains
- A migration CLI or any dual-layout read compatibility
- Env-var-configurable shard size (fixed constant `SHARD_DIGITS = 2`)
- Version bump / release (release SOP at ship time)
- Any new MCP tool/resource/prompt surface

### Design Notes

Key invariants and rationale:

- **One uniform layout for every language**: `docs/<type>/<lang>/<shard>/<file>` with `en` a normal language dir. EN's flat location (DEC 38efdb66 item 1) existed solely so pre-existing English files kept their exact path; sharding already moves every English file, so the compatibility argument is void and the flat special case is retired. Every scan, resolution, parse-derivation, and lint rule is then language-agnostic — the same code runs for `en` and for any variant.
- **Why this kills the shard/language collision**: a two-letter language code can be a valid two-hex shard name (`de`); in a mixed layout (flat EN shards beside language dirs) that makes one directory hold two kinds of files and forces depth- or table-based disambiguation. In the uniform layout languages and shards sit at different path levels, so no directory ever plays two roles and no disambiguation heuristic exists.
- **Order preservation**: sorting a language's sharded listing by (shard dir, file name) equals today's lexicographic file-name sort because the shard is the two-hex prefix of the uuid and the file name now starts with the uuid — so `list_<d>` order and `ref` values stay stable except the intended prefix removal (REQ-008).
- **Why 2 digits**: 256 shards bound any dir to ~N/256 files; no two-hex string can equal a domain name (every two-char domain name contains a non-hex letter: `u`, `q`), whereas 3 digits could (`dec` is three pure-hex chars, producing `docs/dec/dec/` and confusing layout inference).
- **Why shard-only reads**: hard cut-over per plan review; downstream flat trees are invisible until moved — the accepted, documented breaking change (REQ-003, REQ-009).
- **Why a violation instead of skip or content-lint**: a misplaced document is invisible to every MCP read tool; a passing gate would commit a dead document. The gate fails loudly with the correct path in the message (feat-218 ethos; REQ-006). Placement checking stays purely shape-based (language dir present, shard dir two-hex, exactly one shard level) because the uniform layout makes every path unambiguous; language validity (packaged heading table) stays with the existing content/parse error path.
- **EN-only consumers (DEC 38efdb66 REQ-013/ACC-014)**: the invariant "never see a variant" is preserved by construction — the EN scan is re-rooted at the `en/` dir, so no glob-shape argument is needed; the pinning test is re-asserted in that form (Phase 130).
- **`ref` churn**: `ref = path.stem` changes from `<type>-<uuid>-<slug>` to `<uuid>-<slug>`; `ref` is documented as opaque and is never an input to `get_<d>` (bare uuid only), so this is documentation churn, not a functional break.
- **Id-less documents**: hand-authored docs with `id: None` in the frontmatter (list-only today) stay list-visible iff placed inside a shard dir (any shard, e.g. `en/00/`), EN or variant — their stems keep the author-chosen name (no uuid prefix), so the uuid-prefix invariant of REQ-008/ACC-002 applies only to documents carrying a frontmatter `id` (the in-repo corpus contains no id-less documents).
- **Cold per-id resolution** drops from O(N-domain) to O(N/256) parses via the shard-narrowed scan, per language (REQ-004).
- **dec moves only**: the 48 in-repo dec files already carry the prefix-less name REQ-002 extends; their migration is a pure `git mv` into `en/<shard>/`, the other 28 files move + rename.

### Related Decisions

- DEC 38efdb66-8025-45c5-bbe8-45b25fc7a772 (multi-language artifact variants: directory layout + heading mapping) — refined by this feature: the language-location rule extends to EN (a uniform `docs/<type>/<lang>/<shard>/` for every language), retiring item 1's flat-EN special case.
- The DEC recording the sharded layout decision is created under `docs/dec/` during Phase 140; its id is added here once it exists.

### Task List

#### Phase 100: Core sharded layout in general/tools/_doc_paths.py

- [ ] Task 100.100: Add `SHARD_DIGITS = 2`, `shard_token(id_)`, and `sharded_doc_path(base_dir, id_, slug)` (prefix-less name, creates the shard dir) (REQ-001, REQ-002, REQ-005).
- [ ] Task 100.110: Make `iter_doc_paths` yield the sharded listing of its base dir (`<base>/*/*.md`, sorted by relative path; flat files and any deeper nesting excluded) — the per-language scan primitive, called with each language's own base dir (REQ-003).
- [ ] Task 100.120: Shard-narrow `find_doc_path_by_id` within a language's base dir (EN = the `en/` dir) with the full sharded-listing fallback per language; reconcile semantics unchanged (REQ-004).
- [ ] Task 100.130: Shard-narrow `find_parse_failure` with the full fallback (REQ-004).
- [ ] Task 100.140: Update `_doc_paths` module and function docstrings for the sharded, prefix-less naming and the uniform per-language layout, and the per-domain `tools/_paths.py` wrapper module/function docstrings of all thirteen sharded domains (e.g. `req/tools/_paths.py`, where `req_base_dir`/`iter_req_paths` document "the flat `docs/req/` directory exactly as before / exactly today's listing") — the wrapper files need no code change, docstrings only, otherwise `docs/api/` (regenerated in 140.110) ships wrong layout documentation (REQ-002, REQ-003).
- [ ] Task 100.150: Unit tests for the layout core: order identity, flat/too-deep not yielded, fast path, wrong-shard fallback (EN + variant), id-less doc in `en/00/` (ACC-003, ACC-004).
- [ ] Task 100.160: Rework `doc_base_dir`/`ensure_doc_base_dir` to resolve every language — `en` included, no flat special case — to `docs/<type>/<lang>/`; `language=None` (omitted) resolves to the `en/` directory — every EN-only call site (the per-domain `iter_<d>_paths()`, `find_<d>_path()`, `config_info()`) passes `None`, and the "EN-only consumers never see a variant" invariant holds only if `None` maps to `en/` rather than raising or returning the domain root (REQ-003, REQ-005).
- [ ] Task 100.170: Rework `language_for_doc_path` (language = the path's first subdirectory under the domain base, shape-valid two letters; any other position ⇒ canonical) and `iter_doc_paths_all_languages` (union of the sharded listings of `en/` + every shape-valid language dir); `iter_language_dirs` keeps its shape-valid discovery semantics (REQ-003).
- [ ] Task 100.180: Unit test for the re-rooted EN-only scan: the EN-only consumers re-rooted at the `en/` dir see EN files only, never variant files (ACC-008, ACC-009).

#### Phase 110: Write path

- [ ] Task 110.100: Wire all thirteen `create_<d>` tools through `sharded_doc_path` over the per-language `doc_base_dir` (every language including EN), removing the per-domain filename lines and the flat-EN base resolution (REQ-002, REQ-005).
- [ ] Task 110.110: Per-domain create tests asserting `docs/<type>/en/<id[:2]>/<uuid>-<slug>.md` and no flat file (EN), plus one table-closed language's variant create asserting `docs/<type>/<lang>/<id[:2]>/<uuid>-<slug>.md` (ACC-001, ACC-002, ACC-008).

#### Phase 120: Lint gate

- [ ] Task 120.100: `_infer_type` sharded recognition (the valid shape is `docs/<type>/<lang>/<2-hex>/<file>.md`) plus the placement validator (missing language dir, missing shard dir, non-hex shard, deeper than one shard level — all violations, exit 2 naming the correct path; a no-table language dir stays placement-valid, its files take the existing no-table content error) (REQ-006).
- [ ] Task 120.110: Update the anchored artifact pattern in `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, and `tests/commands/test_lint.py` (open-depth match under `docs/<dir>/` so misplaced depths are selected for the validator; non-domain dirs keep the skip behavior) and extend the drift test (REQ-006).
- [ ] Task 120.120: Lint tests: valid EN shard, valid variant shard, the four violation shapes, the non-domain-dir skip at every depth pinned against the repo's real archive tree (real files, depth ≥ 3 — e.g. `docs/archive/adr/<uuid>-<slug>.md` and `docs/archive/sop/` — non-domain dir → skip, exit 0), `_derive_id` and repair pointer on sharded paths (ACC-005).

#### Phase 130: Test sweep and in-repo migration

- [ ] Task 130.100: Update the flat-glob `_doc_path()` test helpers and hand-seeded broken/variant files across the ~30 affected test files — including the feat-197-i18n suites (`tests/general/tools/test_i18n_*`, `tests/dec/tools/test_i18n_*`, `test_language_guard`, `test_list_languages`, `test_check_translation_drift`, the EN-only-consumer pinning tests) and the `specmgr://config` surface (`tests/general/resources/test_config.py`: the per-domain `base_dir` assertion `assertEqual(…, DEFAULT_DOCS_ROOT / domain)` becomes `DEFAULT_DOCS_ROOT / domain / "en"` for the thirteen sharded domains — `config_info()` calls each domain's base-dir function with no language, and after Task 100.160 the omitted-language resolution targets `docs/<type>/en/`; plus the golden fixture `tests/fixtures/config-golden/specmgr-config.pre-migration.json`, regenerated per that fixture's own capture-README procedure) — to the uniform `en/<shard>/` + `<lang>/<shard>/` layout (REQ-002, REQ-003).
- [ ] Task 130.110: `git mv` the 76 in-repo docs into `docs/<type>/en/<shard>/` (48 dec move-only, the remaining 28 with the type prefix dropped; throwaway loop, not committed as tooling) (REQ-007).
- [ ] Task 130.120: Verify `specmgr lint --all` and the full test suite are green on the migrated tree (ACC-002, ACC-006).

#### Phase 140: Docs and verification

- [ ] Task 140.100: Update README, AGENTS.md (per-domain layout bullets + the feat-197-i18n paragraph), the `specmgr://i18n` guidance data file, and the `SPECMGR_DOCS_DIR` registry description; CHANGELOG `[Unreleased]` with the breaking note; create the DEC under `docs/dec/` (REQ-009).
- [ ] Task 140.110: Regenerate `docs/MCP.md`, `docs/api/`, and `docs/GENERATED.md` if any docstring changed.
- [ ] Task 140.120: Run ruff format/check, vulture, pylint, the full pytest suite, and the pre-commit hooks end-to-end.
- [ ] Task 140.130: Add the DEC reference to Related Decisions; update the feat status and Recent Updates (REQ-009).

## Progress

### Current Status

**As of 2026-11-18**: Plan revised against current dev — the ADR artifact type is removed from dev (issue #46), the scope covers all thirteen UUID whole-body domains, and the layout is uniform for every language including English (`docs/<type>/<lang>/<shard>/`, the flat-EN location retired). Not started — awaiting implementation.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-18 14:31:36.772Z - Plan refined after feat-refiner pass (G1, G2, D1, D3, I1, I2)

Seven user-approved fixes from the feat-refiner pass applied to the plan:

- G1: Task 130.100 now also covers the two config items no task owned — `tests/general/resources/test_config.py` (its per-domain `base_dir` assertion `assertEqual(…, DEFAULT_DOCS_ROOT / domain)` becomes `DEFAULT_DOCS_ROOT / domain / "en"` for the thirteen sharded domains, since `config_info()` calls each domain's base-dir function with no language and the omitted-language resolution targets `docs/<type>/en/` after Task 100.160) and the `specmgr://config` golden `tests/fixtures/config-golden/specmgr-config.pre-migration.json` (regenerated per that fixture's own capture-README procedure) — so the 130.120/140.120 green-suite gates own every affected item.
- G2: Task 100.140 now also updates the per-domain `tools/_paths.py` wrapper module/function docstrings of all thirteen sharded domains (e.g. `req/tools/_paths.py`, "the flat `docs/req/` directory exactly as before / exactly today's listing") — docstrings only, no code change, so `docs/api/` (regenerated in 140.110) does not ship wrong layout documentation.
- D1: REQ-008, ACC-002, and the Id-less documents design note now carry the explicit exception — the uuid-prefix invariant applies to documents carrying a frontmatter `id`; id-less documents keep author-chosen stems (no uuid prefix) and stay list-visible only when placed inside a shard dir (the in-repo corpus contains no id-less documents — a text-clarity fix, not a behavior change).
- D2: The 2026-10-31 Decisions Made entry is amended so the 2026-11-18 "Every ADR reference is re-pointed to DEC" claim holds — "unifies with ADR's convention" now reads "(ADR removed per issue #46; the convention is now DEC's — see the 2026-11-18 Updates entry)".
- D3: The "EN-only scan re-rooted at `en/`" test case moves out of Task 100.150 into a new Task 100.180 appended after 100.170 — the behavior is introduced by Tasks 100.160/100.170, so every task's tests are satisfiable in list order (100.150 now cites ACC-003/ACC-004 only).
- I1: Task 120.120 pins the lint skip behavior against the repo's real non-domain tree `docs/archive/` (real files, depth ≥ 3), and REQ-006/ACC-005 use `docs/archive/` (depth ≥ 3) as the concrete example instead of the non-existent `docs/appendix/`.
- I2: Task 100.160 now states explicitly that `language=None` (omitted) resolves to the `en/` directory — every EN-only call site (the per-domain `iter_<d>_paths()`, `find_<d>_path()`, `config_info()`) passes `None`, and the "EN-only consumers never see a variant" invariant holds only if `None` maps to `en/` rather than raising or returning the domain root.

#### 2026-11-18 07:06:21.000Z - Plan revised for ADR removal, thirteen-domain scope, and the uniform per-language sharded layout

The plan was revised against current dev, settled with the requester:

- Every ADR reference is re-pointed to DEC — the ADR artifact type is removed from dev (issue #46 closed, feat-46-remove-adr done, PR #258); this feature's own decision record becomes a DEC under `docs/dec/`, and REQ-002's naming rationale now extends DEC's existing prefix-less convention.
- Scope extended from eleven to all thirteen UUID whole-body domains: `txt` (merged 2026-10-28, before the original settlement) and `set` (merged 2026-11-02) were missing from the original "eleven".
- The layout is uniform for every language, English included: `docs/<type>/<lang>/<shard>/<file>` with `en` a normal language dir. Keeping EN flat would leave one directory (`de`) that is both an EN shard and a language dir, forcing depth- and table-based disambiguation in the scans, the parse derivation, and the lint gate; the uniform layout removes that whole class because languages and shards sit at different path levels. EN's flat location (DEC 38efdb66 item 1) existed only to keep pre-existing English paths stable — an argument sharding already voids, since every English file moves.
- In-repo migration count updated 27 → 76 (the ADR→DEC conversion added 47 dec files; the 48 dec files already prefix-less move only, the remaining 28 move + rename, all into `en/<shard>/`).
- New ACC-008/ACC-009 (the uniform-layout read/parse behavior) and Tasks 100.160/100.170 (`doc_base_dir` + language-derivation rework).

#### 2026-10-31 16:48:12.000Z - Created

Feature plan created for issue #245 after plan review: sharded layout (two-hex-digit uuid prefix, 256 shards), prefix-less file names, shard-only reads, the lint layout-violation gate, the one-off in-repo migration, and the documented breaking change.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-18 07:06:21.000Z - All thirteen UUID domains in scope; one uniform sharded layout for every language including en

Settled with the requester in the plan revision:

- Scope is every UUID whole-body domain (the thirteen: req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/txt/set); `feat` stays excluded (folder-per-document), ADR is no longer a domain (removed per issue #46).
- Every language — English included — uses `docs/<type>/<lang>/<shard>/<file>`: the flat-EN location is retired (DEC 38efdb66 item 1 refined), a language dir without a packaged heading table is placement-valid but its files take the existing no-table content error, and no path is ever ambiguous between an EN shard and a language dir.
- The sharded layout's decision record is a DEC — the ADR type no longer exists in dev.

#### 2026-10-31 16:30:00.000Z - Shard size, naming, reads, migration, and gate semantics settled in plan review

The layout was decided in iterative plan review with the requester:

- Two hex digits (256 shards), bare-hex dir names, fixed constant (no env var) — a two-hex shard cannot collide with a domain name, unlike three digits (`dec` is three pure-hex chars).
- File names drop the `<type>-` prefix (REQ-002) — unifies with ADR's convention (ADR removed per issue #46; the convention is now DEC's — see the 2026-11-18 Updates entry) and removes the "`req-<uuid>`" not-found error class at the root.
- No dual-layout reads and no migration CLI (REQ-003, REQ-007) — breaking for downstream flat trees, accepted and documented (REQ-009).
- A misplaced file is a lint layout violation that blocks the commit (exit 2), not a silent skip or a content-only lint (REQ-006).
- The GitHub issue is created before the feature folder; the feature id carries the issue number.
