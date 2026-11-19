---
classification: null
created: '2026-10-31T17:51:01.215+01:00'
id: feat-245-shard-docs
status: planning
type: feat
updated: '2026-10-31T17:51:01.215+01:00'
version: 1.0.0
---

# Feature: Shard document storage by uuid prefix

## Plan

### Overview

Per-type document directories (`docs/<type>/`) currently hold every document of the type flat in one directory. As corpora grow this bounds nothing: a cold per-id resolution parses every file of the domain before it finds the target (the same cold-scan class feat-187 fixed for `list_feat`), and directory-level operations (git, glob, OS) degrade with file count. This feature shards the eleven whole-body UUID domains into 256 subdirectories named by the first two hex digits of the document's uuid, drops the `<type>-` prefix from file names, restricts every MCP read path to the sharded layout (hard cut-over), extends the `specmgr-lint` gate to recognize the new layout with misplaced files becoming a blocking layout violation, and migrates the 27 in-repo documents in the same change. It is a breaking change for downstream users with pre-existing flat trees, documented as such. Implements issue #245.

### Requirements

- REQ-001: Documents of the eleven whole-body UUID domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs) are stored one per shard subdirectory under the domain's base directory, the shard named by the first two hex digits of the document's uuid (`docs/<type>/<id[:2]>`).
- REQ-002: Document file names carry no type prefix: a file is named `<uuid>-<slug>.md` (slug derived from the H1 title by the existing slugify rules), unifying the eleven sharded domains with ADR's existing `<uuid>-<slug>.md` convention.
- REQ-003: The MCP read path is shard-only: `iter_doc_paths` yields exactly one subdirectory level (`*/*.md`); files directly under `docs/<type>/` are invisible to `list_<d>`, `get_<d>`, id resolution, and the similarity corpus.
- REQ-004: Id resolution first scans the shard derived from the id (`id[:2]`); a document whose placement disagrees with its id is still found by the full sharded-listing fallback (the filesystem remains the sole source of truth).
- REQ-005: Every `create_<d>` tool writes through the single shared `sharded_doc_path(base_dir, id_, slug)` helper in `general/tools/_doc_paths.py`, which creates the shard directory; no per-domain filename line remains.
- REQ-006: The `specmgr-lint` gate recognizes the sharded layout (anchored pattern + `_infer_type`, all three drift-pinned copies) and fails with exit 2 naming the correct path when a file is misplaced: flat in a sharded domain, in a non-hex subdirectory, or at subdirectory depth under `docs/adr/`; flat ADR files and non-domain dirs (e.g. `docs/appendix/`) keep today's behavior.
- REQ-007: The 27 existing in-repo documents are moved into shards with the type prefix dropped (`git mv`, 100% similarity, history preserved) in the same change as the code.
- REQ-008: `list_<d>` result order and `ref` semantics are preserved: order equals lexicographic file-name order and `ref = path.stem = <uuid>-<slug>`.
- REQ-009: The breaking change is documented: CHANGELOG `[Unreleased]` (pre-existing flat trees invisible until moved; file names lose the `<type>-` prefix; `ref` values change), README and AGENTS.md describe the sharded layout, and a new ADR records the decision.

### Acceptance Criteria

- [ ] ACC-001: `create_<d>` places the file at `docs/<type>/<id[:2]>/<uuid>-<slug>.md` and leaves nothing directly under `docs/<type>/`, asserted for all eleven domains (REQ-001, REQ-002, REQ-005).
- [ ] ACC-002: every `ref` reported by `list_<d>` in the eleven domains starts with the document uuid (no `<type>-` prefix) and `list` order equals lexicographic file-name order (REQ-002, REQ-008).
- [ ] ACC-003: a flat file hand-placed under `docs/<type>/` appears in no `list_<d>` result and is unresolvable by `get_<d>` (REQ-003).
- [ ] ACC-004: a document moved to a wrong shard dir resolves by id with byte-identical content via the fallback scan (REQ-004).
- [ ] ACC-005: staging `docs/req/foo.md`, `docs/req/foo/x.md`, and `docs/adr/x/y.md` each fails the lint gate with exit 2 and the correct path in the message; a valid sharded file and a flat ADR file lint clean (REQ-006).
- [ ] ACC-006: after migration, `git ls-files` over the eleven domain dirs matches only sharded prefix-less paths, `git log --follow` shows preserved history, and `specmgr lint --all` exits 0 (REQ-007).
- [ ] ACC-007: CHANGELOG `[Unreleased]`, README, AGENTS.md, and the new ADR all describe the sharded layout, and the breaking note names the flat-tree visibility loss and the `ref`/file-name change (REQ-009).

### Scope

#### Included

- Sharded layout core in `general/tools/_doc_paths.py`: `SHARD_DIGITS`, `shard_token`, `sharded_doc_path`, shard-only `iter_doc_paths`, shard-narrowed id resolution with full fallback
- Wiring the eleven `create_<d>` tools through the shared helper
- `specmgr-lint` layout recognition + placement-violation check, and the anchored artifact pattern in the three drift-pinned copies (pre-commit hook, CI workflow, test constant)
- One-off in-repo migration of the 27 documents (`git mv`, move + rename)
- Test sweep across the suite for the new layout
- Documentation: README, AGENTS.md, `SPECMGR_DOCS_DIR` registry description, CHANGELOG `[Unreleased]`, new ADR

#### Explicitly Out Of Scope

- ADR (bespoke module, being removed per issue #46) and `feat` (folder-per-document, non-uuid ids) sharding
- A migration CLI or any dual-layout read compatibility
- Env-var-configurable shard size (fixed constant `SHARD_DIGITS = 2`)
- Version bump / release (release SOP at ship time)
- Any new MCP tool/resource/prompt surface

### Design Notes

Key invariants and rationale:

- **Order preservation**: sorting the sharded listing by (shard dir, file name) equals today's lexicographic file-name sort because the shard is the two-hex prefix of the uuid and the file name now starts with the uuid — so `list_<d>` order and `ref` values stay stable except the intended prefix removal (REQ-008).
- **Why 2 digits**: 256 shards bound any dir to ~N/256 files; no two-hex string can equal a domain name (every two-char domain name contains a non-hex letter: `u`, `q`), whereas 3 digits could (`dec` is three pure-hex chars, producing `docs/dec/dec/` and confusing layout inference).
- **Why shard-only reads**: hard cut-over per plan review; downstream flat trees are invisible until moved — the accepted, documented breaking change (REQ-003, REQ-009).
- **Why a violation instead of skip or content-lint**: a misplaced document is invisible to every MCP read tool; a passing gate would commit a dead document. The gate fails loudly with the correct path in the message (feat-218 ethos; REQ-006).
- **`ref` churn**: `ref = path.stem` changes from `<type>-<uuid>-<slug>` to `<uuid>-<slug>`; `ref` is documented as opaque and is never an input to `get_<d>` (bare uuid only), so this is documentation churn, not a functional break.
- **Id-less documents**: hand-authored docs with `id: None` in the frontmatter (list-only today) stay list-visible iff placed inside a shard dir (any shard, e.g. `00/`).
- **Cold per-id resolution** drops from O(N-domain) to O(N/256) parses via the shard-narrowed scan (REQ-004).

### Related Decisions

- The ADR recording the sharded layout decision is created under `docs/adr/` during Phase 140; its id is added here once it exists.

### Task List

#### Phase 100: Core sharded layout in general/tools/_doc_paths.py

- [ ] Task 100.100: Add `SHARD_DIGITS = 2`, `shard_token(id_)`, and `sharded_doc_path(base_dir, id_, slug)` (prefix-less name, creates the shard dir) (REQ-001, REQ-002, REQ-005).
- [ ] Task 100.110: Make `iter_doc_paths` yield sharded-only paths (`*/*.md`, sorted by relative path, depth-2+ excluded) (REQ-003).
- [ ] Task 100.120: Shard-narrow `find_doc_path_by_id` with the full sharded-listing fallback; reconcile semantics unchanged (REQ-004).
- [ ] Task 100.130: Shard-narrow `find_parse_failure` with the full fallback (REQ-004).
- [ ] Task 100.140: Update `_doc_paths` module and function docstrings for the sharded, prefix-less naming (REQ-002, REQ-003).
- [ ] Task 100.150: Unit tests for the layout core: order identity, flat/depth-2+ not yielded, fast path, wrong-shard fallback, id-less doc in `00/` (ACC-003, ACC-004).

#### Phase 110: Write path

- [ ] Task 110.100: Wire all eleven `create_<d>` tools through `sharded_doc_path`, removing the per-domain filename lines (REQ-002, REQ-005).
- [ ] Task 110.110: Per-domain create tests asserting the sharded prefix-less path and no flat file (ACC-001, ACC-002).

#### Phase 120: Lint gate

- [ ] Task 120.100: `_infer_type` sharded recognition (grandparent in domains) plus the placement validator (flat in a sharded domain, non-hex subdir, depth under `adr` are violations, exit 2 naming the correct path) (REQ-006).
- [ ] Task 120.110: Update the anchored artifact pattern in `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, and `tests/commands/test_lint.py` (depth-3 branch added; flat branch kept for ADR + violation selection) and extend the drift test (REQ-006).
- [ ] Task 120.120: Lint tests: valid sharded, flat ADR, the three violation shapes, `appendix` skip, `_derive_id` and repair pointer on sharded paths (ACC-005).

#### Phase 130: Test sweep and in-repo migration

- [ ] Task 130.100: Update the flat-glob `_doc_path()` test helpers and hand-seeded broken files across the ~25 affected test files to the sharded prefix-less layout (REQ-002, REQ-003).
- [ ] Task 130.110: `git mv` the 27 in-repo docs into shards with the type prefix dropped (throwaway loop, not committed as tooling) (REQ-007).
- [ ] Task 130.120: Verify `specmgr lint --all` and the full test suite are green on the migrated tree (ACC-002, ACC-006).

#### Phase 140: Docs and verification

- [ ] Task 140.100: Update README, AGENTS.md, and the `SPECMGR_DOCS_DIR` registry description; CHANGELOG `[Unreleased]` with the breaking note; create the ADR under `docs/adr/` (REQ-009).
- [ ] Task 140.110: Regenerate `docs/MCP.md`, `docs/api/`, and `docs/GENERATED.md` if any docstring changed.
- [ ] Task 140.120: Run ruff format/check, vulture, pylint, the full pytest suite, and the pre-commit hooks end-to-end.
- [ ] Task 140.130: Add the ADR reference to Related Decisions; update the feat status and Recent Updates (REQ-009).

## Progress

### Current Status

**As of 2026-10-31**: Plan settled in review with the requester (issue #245). Not started — awaiting implementation.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-31 16:48:12.000Z - Created

Feature plan created for issue #245 after plan review: sharded layout (two-hex-digit uuid prefix, 256 shards), prefix-less file names, shard-only reads, the lint layout-violation gate, the one-off in-repo migration, and the documented breaking change.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-31 16:30:00.000Z - Shard size, naming, reads, migration, and gate semantics settled in plan review

The layout was decided in iterative plan review with the requester:

- Two hex digits (256 shards), bare-hex dir names, fixed constant (no env var) — a two-hex shard cannot collide with a domain name, unlike three digits (`dec` is three pure-hex chars).
- File names drop the `<type>-` prefix (REQ-002) — unifies with ADR's convention and removes the "`req-<uuid>`" not-found error class at the root.
- No dual-layout reads and no migration CLI (REQ-003, REQ-007) — breaking for downstream flat trees, accepted and documented (REQ-009).
- A misplaced file is a lint layout violation that blocks the commit (exit 2), not a silent skip or a content-only lint (REQ-006).
- The GitHub issue is created before the feature folder; the feature id carries the issue number.
