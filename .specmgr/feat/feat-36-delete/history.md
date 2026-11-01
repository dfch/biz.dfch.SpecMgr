# History: Replace per-domain delete stubs with a generic type-dispatched delete tool

#### 2026-08-31 23:20:24.000Z - Phase 4 (Tasks 4.2–4.4): AGENTS.md, server.py docstring, CHANGELOG.md updated

Implemented Tasks 4.2–4.4 strictly per Design Notes §8 — the three documentation-propagation file edits of Phase 4; Task 4.1 (the new ADR, created via the `specmgr` MCP structured tools per ADR 898bfcd0 and set `accepted`) and Task 4.5 (docs regeneration, `specmgr docs`/`mcp-docs`/`adr-toc` each run twice to a fixed point) remain for the orchestrator. In `AGENTS.md` (Task 4.2), each of the eleven per-domain Status bullets (`req/`, `uc/`, `tsk/`, `qa/`, `prb/`, `gol/`, `rsk/`, `dec/`, `sop/`, `feat/`, `vcr/`) drops its `delete_<d>` stub mention from the tool enumeration (with `feat`'s "All 8 tools" count corrected to "All 7 tools") and gains a deletion note worded consistently with the generic `update`/`set_status` phrasing already in each bullet ("deletions through the generic `delete` tool (`type="<d>"`)"); the "Still genuinely missing / not yet done" stubs bullet ("`delete_req`/…/`delete_vcr` are stubs, not yet implemented") is removed, leaving the heading and the other three bullets intact; the `general/` bullet's `general/tools/` enumeration gains `delete` — the generic type-dispatched hard-delete for the eleven whole-body domains (`adr` excluded), with a note that all eleven domains implement a `delete` adapter in that one tool (a future domain adds its own adapter there, never a per-domain `delete_<d>` tool), resolving by `id`, taking the domain's own lock, and returning the deleted path; and the `ac` "future domain" convention note now reads "one dispatch entry to each of the two generic tools in `general/tools/` (`update`'s `type`, `set_status`'s `type`), one `delete` adapter in the generic `delete` tool, plus a `raw` parameter on the new `get_<d>` tool — not new `update_<d>`/`set_status_<d>`/`delete_<d>` tools". In `server.py`'s module docstring (Task 4.3 — the authoritative registration list; docstring text only, no code touched), the eleven per-domain `delete_<d>` stub mentions are removed from the domain tool paragraphs, keeping every other tool name and the surrounding sentence structure, and the "General tools" paragraph gains a `delete` entry on the same `name -- description` pattern: the generic type-dispatched hard-delete for the eleven whole-body domains (`type` one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr, `adr` not supported), resolves by `id`, takes the domain lock, and returns the deleted path, with a `ValueError` for injection/wrong-format ids before any file access, the domain's `XNotFoundError` for missing documents, and a `DeleteError` for I/O failures. In `CHANGELOG.md` (Task 4.4), the previously empty `[Unreleased]` section gains a `### Removed` entry (**BREAKING** 0.x: the eleven `delete_<d>` stub MCP tools deleted outright, no deprecated wrappers, with the caller switch to `delete` plus the explicit `type` parameter) and an `### Added` entry (the generic `delete(id, type)` MCP tool in `general/tools/` with its full dispatch, locking, and `ValueError`/`XNotFoundError`/`DeleteError` error contract, and the reusable, doc-type-agnostic `general/tools/_path_safety.py` module with its five pure, no-I/O guards, wired into `delete` now and adoptable later by `get_<d>`/`update`/`set_status` with zero rework) — both sub-headings following the file's existing Keep-a-Changelog convention and the 0.13.0 `### Removed`/`### Added` precedent. Phase-end quality gate all green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full `unittest` suite (2713 tests OK — the Phase-3 baseline, unchanged since this phase is doc-only), `python -c "import biz.dfch.specmgr.server"` (SERVER IMPORT OK), and the verification grep `grep -nE 'delete_(req|uc|tsk|qa|prb|gol|rsk|dec|sop|feat|vcr)' AGENTS.md src/biz/dfch/specmgr/server.py` returning zero matches in both files (all eleven stub mentions gone; the remaining matches elsewhere — `general/tools/delete.py`'s private `_delete_<d>` adapter names and the `docs/` mirrors — are expected and will be reconciled by the orchestrator-owned Task 4.5 docs regeneration).


#### 2026-08-31 21:32:55.000Z - Phase 3 complete: eleven delete stubs retired

Implemented Tasks 3.1–3.3 per the plan, plus the orchestrator-resolved plan gap. Deleted the eleven
`src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` stub modules, the eleven
`tests/<d>/tools/test_delete_<d>.py` stub-test files (22 files, `git rm`), and — after the
orchestrator's post-phase `specmgr docs` regeneration, which rewrites existing pages but does not prune
stale ones — the eleven now-stale `docs/api/biz.dfch.specmgr.<d>.tools.delete_<d>.md` stub-API pages the
same way (11 more `git rm`'s); in each of the eleven `<d>/tools/__init__.py` removed the `from
.delete_<d> import delete_<d>` line, the `__all__` entry, and the stub sentence from the module
docstring — replaced, where the sentence structure allowed, with a single pointer line ("Deletion of
`<d>` documents goes through the generic ``delete`` tool in ``general.tools`` (``type="<d>"``)", with
`sop`'s pointer living inside its existing generic-dispatch paragraph, `feat`'s "eight lifecycle tools"
count corrected to "seven", and the other ten domains taking the pointer in the standard position) — and
in each of the eleven domain-level `<d>/__init__.py` dropped `delete_<d>` from the tool enumeration
(`sop`'s "(8 tools, …)" count corrected to "(7 tools, …)", and `feat`'s generic-surface sentence now
reading "the generic ``update``/``set_status``/``delete`` tools"). Per the orchestrator's resolution of
the plan gap, the six integration-test modules that used to end their lifecycle by asserting the stub
raises `NotImplementedError` (`tests/{dec,feat,gol,prb,sop,vcr}/tools/test_integration.py`) now perform
a REAL delete through the generic tool: `delete(<id>, type="<d>")`, asserting the returned `str` is the
seeded path (the `*.md` file path for the flat domains — resolved via the domain's own `find_<d>_path`
where the test previously tracked no path (`gol`/`prb`) — and the `<base>/<id>/` folder path for
`feat`), that the file/folder no longer exists, and that a follow-up `get_<d>` raises the domain's own
`XNotFoundError` (`DecNotFoundError`, `FeatNotFoundError`, `GolNotFoundError`, `PrbNotFoundError`,
`SopNotFoundError`, `VcrNotFoundError`); the module and method docstring lifecycle descriptions were
updated accordingly, no other test structure or earlier lifecycle step was changed. Phase-end quality
gate all green: `ruff format --check` (1472 files already formatted), `ruff check` (All checks passed),
and `vulture src/ whitelist.py --min-confidence 60` clean (no whitelist change needed); the ACC-002 grep
(`grep -rnE 'delete_(req|uc|tsk|qa|prb|gol|rsk|dec|sop|feat|vcr)' src/ tests/`) returns nothing under
`tests/` and, under `src/`, only the two hard-constraint-protected files — `server.py`'s module
docstring (Task 4.3's job) and `general/tools/delete.py`'s private `_delete_<d>` adapter functions
(Phase 2 work; internal dispatch-table names, not tools — plus a gitignored `egg-info` build artifact) —
and, after the pruning, the same grep over `docs/` returns no per-domain stub mentions outside those two
protected content mirrors (`docs/api/biz.dfch.specmgr.general.tools.delete.md`'s private `_delete_<d>`
adapter headings, and `docs/api/biz.dfch.specmgr.server.md`, which still mirrors `server.py`'s
Task-4.3-pending docstring; `docs/MCP.md` carries zero matches) — and `import
biz.dfch.specmgr.<d>.tools` succeeds for every domain (`IMPORTS OK`, including `server`); after
importing `server`, `mcp.list_tools()` shows `delete` exactly once and zero `delete_<d>` tools (93 total
= 104 − 11); the six updated integration modules pass (18 tests OK, ~15 s); full `unittest` suite OK
(2713 tests = 2735 Phase-2 baseline − 22 removed stub tests, ~119 s). Phase 4 (decision and
documentation propagation, Tasks 4.1–4.5) is next.


#### 2026-08-31 20:21:21.000Z - Phase 2 complete: generic delete tool

Implemented Tasks 2.1–2.2 strictly per Design Notes §2–§6/§9. Added `src/biz/dfch/specmgr/general/tools/delete.py`, the generic `delete` MCP tool: `@mcp.tool(name="delete", title="Delete document")` with the pinned `def delete(id: str, type: Literal[...eleven values...]) -> str` body (`validate_id(type, id)` before any filesystem access per REQ-003, then `_ADAPTERS[type](id)` and return the result); `DeleteError(OSError)` per REQ-005; `_DELETE_TYPES` with the pinned comment; and the eleven private `_delete_<d>` adapters — the ten flat domains in the canonical pinned form (`<d>_base_dir()` → `<d>_lock(id_)` → `load_<d>_by_id(base_dir, id_)` with the parsed document discarded → `assert_within(base_dir, path)` → `path.unlink()` in a try/except re-raising `DeleteError(f"failed to delete {path}: {ex}") from ex` → `return str(path)` after the lock) and the `feat` adapter diverging exactly per §3 (`folder = path.parent`, `assert_within(base_dir, folder)`, `shutil.rmtree(folder)` in the same try/except, `return str(folder)`); the domain's own `XNotFoundError` propagates unchanged from `load_by_id`, and `shutil` is the only new stdlib import. Each adapter follows `set_status.py`'s qualified per-domain import pattern (`<d>_lock`, `load_by_id as load_<d>_by_id`, `<d>_base_dir`), and the tool is registered in `general/tools/__init__.py` (`from .delete import delete`, the `__all__` entry, and a module-docstring sentence). Added `tests/general/tools/test_delete.py` — 8 test methods parameterized over all eleven types, mirroring `test_set_status.py`'s fixture strategy (seeding a real document per type via the domain's own `create_<d>` into temp `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`): success (the returned `str` is the deleted file path for the flat domains / the deleted folder path for `feat`, the file/folder is gone, a follow-up `load_by_id` raises the domain's `XNotFoundError`); the `feat` folder-per-document delete including a seeded `history.md`; every pinned injection shape (`../x`, `a/b`, `a\b`, `..`) plus each type's wrong-format id raising `ValueError` with the seeded document left intact; a well-formed unknown id raising the domain's `XNotFoundError`; a mocked `Path.unlink` (ten flat domains) / `shutil.rmtree` (`feat`) `OSError` surfacing as `DeleteError` (an `OSError`, the exact instance as `__cause__`, the path in the message, target left in place); the domain's own per-id lock entered around the delete for all eleven types (an event-ordered spy wrapping each `<d>_lock`); and a registration smoke test (mirroring `test_update.py`'s) verifying the live `mcp` registration carries `delete` exactly once with the 11-value `type` enum and required `id`/`type`. Phase-end quality gate all green: `ruff format --check` (1493 files), `ruff check` (All checks passed), and `vulture src/ whitelist.py --min-confidence 60` clean (no whitelist change needed — `_DELETE_TYPES` is a private module constant, which vulture ignores by name convention); target test module OK (8 tests); full `unittest` suite OK (2735 tests = 2727 baseline + 8 new, ~114 s); `import biz.dfch.specmgr.server` OK (104 tools registered; `delete` present exactly once; the eleven `delete_<d>` stubs still registered, as expected — Phase 3 retires them). Phase 3 (retire the eleven delete stubs, Tasks 3.1–3.3) is next.


#### 2026-08-31 19:09:41.000Z - Phase 1 complete: reusable path-safety module

Implemented Tasks 1.1–1.2 strictly per Design Notes §1/§9. Added `src/biz/dfch/specmgr/general/tools/_path_safety.py`, the reusable, doc-type-agnostic path-safety module: `__all__` with the five public functions (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`), `_UUID_TYPES` (the ten UUID domains), the canonical 8-4-4-4-12 lowercase-hex `_UUID_PATTERN`, the `_FEAT_ID_PATTERN` (`^feat-[0-9]+-[a-z0-9-]+$`), and comparison constants for the `feat` type name, the path separators, and the `..` sequence; no `mcp` dependency, no filesystem mutation (the sanctioned touch is `assert_within`'s read-only `Path.resolve()` calls), no `DeleteError` (it lives in the Phase 2 `delete.py`, per §1's reusability contract); every function starts with the standard input guards and raises `ValueError` with a message naming the offending value, and `validate_id` is the single before-filesystem-access entry point (rejecting unknown `type_` values). Added `tests/general/tools/test__path_safety.py` with 23 pure unit tests covering every §9 case (the six pinned `assert_no_traversal` rejection shapes; the `assert_uuid` and `assert_feat_id` accept/reject sets; `validate_id` over all ten UUID domains, `feat`, an unknown type, and a traversal id; `assert_within` child/base/sibling/ancestor containment). Phase-end quality gate all green: `ruff format --check` (1490 files), `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` clean; target test module OK (23 tests); full `unittest` suite OK (2727 tests = 2704 baseline + 23 new, ~105 s). Phase 2 (the generic `delete` tool, Tasks 2.1–2.2) is next.


#### 2026-08-31 18:28:48.000Z - Session handover: Phase 0 complete, Phase 1 ready for a fresh session

The design session ended with Phase 0 complete. Implementation of Phases 1–5 resumes in a **fresh session**, orchestrated from this README, with the main agent acting as Phase-Orchestrator and launching the `phase-implementer` subagent **once per phase** (1, then 2, …, 5): each subagent implements its phase end-to-end (code, tests, phase-end quality gate, task-line status updates in this README) and reports back, and the orchestrator verifies the gate results and commits before starting the next phase. The agreed commit policy is **one commit per phase** on `feat-36-delete`: the orchestrator commits without asking for permission but does **NOT push**, and stops and asks only when it needs a user decision or hits a wall. For Task 4.1's ADR, the enabled specmgr MCP server (`uvx biz-dfch-specmgr[mcp]`) resolves `docs/adr` relative to its CWD — the requester confirmed `create_adr` lands the file in this worktree — and the new ADR file must be committed together with the other Phase 4 files; the disabled `specmgr-test` MCP server must NOT be enabled (it points at the main repo), and `git pull` must NOT be run on this branch (no upstream tracking is set). Two plan refinements agreed this session (folded into the Task List above): Task 2.1 additionally registers `delete` in `general/tools/__init__.py` (import / `__all__` / docstring) — without it the tool would silently never register — and Task 3.2 additionally drops `delete_<d>` from the eleven domain-level `<d>/__init__.py` package docstrings — otherwise ACC-002's grep-over-`src/` criterion would fail. Repo state at handover: worktree `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`, branch `feat-36-delete`, working tree clean, tip the Task 0.3 debug-print cleanup commit; the main repo on `dev` (`/home/user/src/biz.dfch.SpecMgr`) carries the byte-exact same cleanup commit (`9eb7e8a`), which the maintainer pushes; the baseline is verified green — full `unittest` suite (2704 tests, OK, noise-free output), `ruff format --check` (1487 files), `ruff check`, and `vulture` all clean. Pre-commit hooks are active in both checkouts, with one known UX: when a hook (e.g. `ruff-format`) modifies a staged file, the first commit attempt fails with "Files were modified by this hook" — re-`git add` the file and commit again — and the `unittest` hook (full suite, ~2 min) and `specmgr-coverage-badge` run on any `src`/`tests` change, while the `specmgr docs`/`mcp-docs`/`adr-toc`/`schema` hooks are scoped to `src/` / `docs/adr` changes and will fire on the Phase 3/4 commits. **Next action:** launch `phase-implementer` for **Phase 1** (Tasks 1.1–1.2).


#### 2026-08-31 18:10:22.000Z - Leftover debug prints stripped from the md model tests (Task 0.3)

Removed 17 debug `print()` calls — plus the `lines = ...`/`result = ...`
assignments and one loop that became dead with them — from
`tests/models/md/test_markdown_section.py` (`TestAnyHeadingLeafSectionExtent`),
`tests/models/md/test_markdown_str.py` (`TestGetExtent`), and
`tests/models/md/test_markdown_list_item.py` (`test_nested_list`). The
byte-exact change was committed to `dev` (maintainer pushes) and to this
branch separately, so the feature's later merge into `dev` is
conflict-free. No behavior change: the three test modules pass (64 tests),
`ruff` is clean, and the `unittest` output is noise-free again.


#### 2026-08-31 15:37:40.000Z - Feature designed; worktree and plan authored (Phase 0 complete)

Completed the design for issue #36. Created the `feat-36-delete` git worktree/branch
from `dev` (leaving `dev` untouched) and authored this README as the full,
implementer-ready plan. Key design decisions, confirmed with the requester: (1) the
generic `delete` tool covers the eleven whole-body domains and excludes ADR; (2) `feat`
hard-deletes its entire `<base>/<id>/` folder; (3) the tool returns the deleted path as
a `str`; and (4) the path/file injection-prevention logic lives in a new **reusable**
module `general/tools/_path_safety.py` so the `get`/`update`/`set_status` tools can
adopt it later with zero rework (they are not modified in this feature). No
implementation code has been written; Phases 1–5 are delegated to the Phase-Orchestrator.
