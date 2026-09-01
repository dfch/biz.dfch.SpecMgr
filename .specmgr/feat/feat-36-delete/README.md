---
created: 2026-08-31 15:37:40.000000
id: feat-36-delete
status: done
type: feat
updated: 2026-09-01 01:28:41.000000
version: 1.0.0
---

# Feature: Replace per-domain delete stubs with a generic type-dispatched delete tool

## Plan

### Overview

Every document domain except ADR currently ships an unimplemented `delete_<domain>`
MCP tool (a registered stub that always raises `NotImplementedError`). This feature
replaces those eleven near-duplicate stubs with a single generic, type-dispatched
`delete(id, type)` tool in `general/tools/delete.py` — the exact analog of the
existing generic `update` and `set_status` tools (ADR
36905d5b-8057-4294-8665-c7eed5534db0). The new tool dispatches on an explicit
`type` parameter (one of the eleven whole-body domains `req`/`uc`/`tsk`/`qa`/`prb`/
`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`; **ADR is deliberately excluded**) to a private
per-domain adapter that resolves the document, takes the domain's own lock, and hard-
deletes it from disk, returning the deleted path as a `str`.

The feature's second, load-bearing contribution is a **new, reusable path-safety
module** (`general/tools/_path_safety.py`) that prevents path-injection through the
`type` or `id` inputs and confines resolved paths to their base directory. No such
guard exists anywhere in the codebase today. It is wired into `delete` in this
feature, but is designed so the `get_<d>`, `update`, and `set_status` tools can adopt
it later with zero rework (they are **not** modified here). The convention "every
domain implements a `delete` adapter in the generic tool, never a per-domain
`delete_<d>` tool" is recorded in a new ADR and propagated to `AGENTS.md`, the
`server.py` docstring, and `CHANGELOG.md`.

Tracked by GitHub issue #36. Branch/worktree: `feat-36-delete`.

### Requirements

- REQ-001: Add a generic `@mcp.tool(name="delete")` in `general/tools/delete.py` with signature `def delete(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","dec","sop","feat","vcr"]) -> str`; eleven private adapters `_delete_<d>(id_) -> str`; a shared `_ADAPTERS: dict[str, Callable[[str], str]]` dispatch table — mirroring `set_status.py`'s structure. On success it returns the deleted path as a `str` (the file path for the ten flat domains, the folder path for `feat`).
- REQ-002: Remove all eleven existing `delete_<domain>` stub tools: the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files, their `from .delete_<d> import delete_<d>` / `__all__` / module-docstring references in each `<d>/tools/__init__.py`, and the eleven `tests/<d>/tools/test_delete_<d>.py` stub test files.
- REQ-003: Add a **reusable** path-safety module `general/tools/_path_safety.py` providing `assert_no_traversal(id_)`, `assert_uuid(id_)`, `assert_feat_id(id_)`, `validate_id(type_, id_)`, and `assert_within(base_dir, candidate)` (all raising `ValueError` with a meaningful message). It must prevent path-injection via `type` or `id`, and it must be callable unchanged by the `get_<d>`, `update`, and `set_status` tools in the future. This feature wires it into `delete` only; it does not modify `get`/`update`/`set_status`.
- REQ-004: Locking — each adapter wraps its resolve-then-delete sequence in the domain's existing `<d>_lock(id_)` context manager (the same lock `update`/`set_status` already use), so a concurrent same-id mutation cannot interleave with the delete.
- REQ-005: Graceful error handling — a missing document raises the domain's own `XNotFoundError` (unchanged); an invalid `id` (non-str, traversal character, or wrong format for the type) raises `ValueError` before any filesystem access; an I/O failure during the actual `unlink`/`rmtree` (`OSError`/`PermissionError`/race) is caught and re-raised as a new `DeleteError` (defined in `delete.py`, subclassing `OSError`) carrying the path and the underlying cause.
- REQ-006: Delete mechanics — the ten flat-file domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`vcr`) remove the single `*.md` file via `Path.unlink()`; `feat` (folder-per-document, ADR 8cf940c5) removes the entire `<base>/<id>/` folder via `shutil.rmtree(folder)`, deleting `README.md`, any `history.md`, and any session transcripts in that folder.
- REQ-007: Record and propagate the decision — create a new ADR titled "Replace domain-specific delete tools with a generic type-dispatched delete tool" (via the `create_adr` MCP tool, then `specmgr adr-toc`); update `AGENTS.md` (each of the eleven per-domain Status bullets drops the `delete_<d> stub` mention and the "Still genuinely missing" `delete_*` stubs bullet is removed/rewritten; the `general/` bullet gains the `delete` tool and a note that all domains now implement a `delete` adapter there); update `server.py`'s module docstring (the authoritative tool list — remove the eleven `delete_<d>` stub mentions, add `delete` to the General tools paragraph); add a `CHANGELOG.md` `[Unreleased]` breaking-change entry; regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`).
- REQ-008: Tests — add `tests/general/tools/test_delete.py` (parameterized over all eleven types: seed a real persisted document per type, then assert delete succeeds, returns the right path, the file/folder is gone, and a subsequent `get_<d>`/`load_by_id` raises the domain `XNotFoundError`; assert every path-injection attempt raises `ValueError` before any filesystem access; assert an unknown id raises the domain `XNotFoundError`; assert an I/O failure raises `DeleteError`; assert the domain lock is acquired) and `tests/general/tools/test__path_safety.py` (unit tests for every `_path_safety` function, including the UUID and feat-format regexes, the traversal-character rejections, and the containment check).

### Acceptance Criteria

- [x] ACC-001: Verifies REQ-001 — `general/tools/delete.py` exists and registers `@mcp.tool(name="delete")` with the eleven-value `type` Literal; it dispatches through an `_ADAPTERS` table to eleven private `_delete_<d>` adapters; a live call `delete(id, type)` on a seeded document removes it and returns the deleted path as a `str`; `docs/MCP.md` (regenerated) lists exactly one `delete` tool and no `delete_<d>` tools. — evidence: `tests.general.tools.test_delete.TestDeleteRegistration::test_delete_registered_with_11_value_type_enum` (live `mcp.list_tools()` after importing `server`: 93 tools, exactly one `delete`, zero `delete_<d>`, 11-value `type` enum, `required` `["id", "type"]`) and `TestDeleteWholeBodyDomains::test_delete_returns_deleted_path_and_removes_the_document` (live `delete()` call on a seeded document returns the deleted path `str`, file/folder gone); `docs/MCP.md` lists exactly one `delete` tool row (`### Tool: delete`) and zero `delete_<d>` rows (grep counts 1/0).
- [x] ACC-002: Verifies REQ-002 — the eleven `delete_<d>.py` source files, their `__init__.py` imports/`__all__`/docstring references, and the eleven `test_delete_<d>.py` files are all gone (`git status`/`grep -r "delete_<d>"` over `src/` and `tests/` returns nothing for a per-domain delete tool); `import biz.dfch.specmgr.<d>.tools` succeeds for every domain. — evidence: `git ls-files | grep -E 'delete_(req|uc|tsk|qa|prb|gol|rsk|dec|sop|feat|vcr)'` returns zero files; `grep -rnE 'delete_(req|uc|tsk|qa|prb|gol|rsk|dec|sop|feat|vcr)' src/ tests/` returns nothing under `tests/` and, under `src/`, only the private `_delete_<d>` adapter names (def lines, the `_ADAPTERS` table, and docstring `:func:` references) inside `general/tools/delete.py` — the protected, by-design mirror of REQ-001's pinned adapter names, plus gitignored untracked build artifacts (`*.egg-info/`, `__pycache__/`); `import biz.dfch.specmgr.<d>.tools` → `IMPORTS OK` for all eleven domains.
- [x] ACC-003: Verifies REQ-003 — `general/tools/_path_safety.py` exposes `assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, and `assert_within`; `tests/general/tools/test__path_safety.py` passes; the functions are pure (no filesystem side effects) and importable by `get_<d>`/`update`/`set_status` without modification (i.e. no delete-specific coupling). — evidence: `__all__` exposes all five functions and `general/tools/delete.py:105` imports `assert_within, validate_id` from `._path_safety`; `tests.general.tools.test__path_safety` passes (23 tests, OK); purity grep: the module imports only `__future__`/`re`/`pathlib.Path` (no `mcp`, no delete-specific imports, no I/O beyond the sanctioned read-only `Path.resolve()` calls in `assert_within`) — its eight `delete`/`DeleteError` mentions are docstring/example text only, so `get_<d>`/`update`/`set_status` can import it unchanged.
- [x] ACC-004: Verifies REQ-004 — each of the eleven adapters acquires its domain's `<d>_lock(id_)` around the resolve-then-delete sequence (verified by a test that mocks/spies the lock, or a concurrency test showing a same-id `update` and `delete` do not interleave). — evidence: `tests.general.tools.test_delete.TestDeleteLocking::test_the_domain_lock_is_entered_around_the_delete` (parameterized over all eleven types) spies each domain's `<d>_lock` on the `delete` module via `mock.patch.object` with an event-recording `spy_lock` and asserts the events equal `["acquire:<id>", "release"]` with the delete having completed inside the lock — OK.
- [x] ACC-005: Verifies REQ-005 — for a seeded document, `delete` with an unknown id raises that domain's `XNotFoundError`; with an injected id (`../x`, `a/b`, `a\b`, `..`, a non-UUID string for a UUID type, a non-`feat-NNN-slug` for `feat`) it raises `ValueError` and leaves the filesystem untouched; with a mocked `unlink`/`rmtree` that raises `OSError` it raises `DeleteError` whose message names the path. — evidence: `tests.general.tools.test_delete.TestDeleteInjection::test_injection_ids_raise_value_error_and_leave_filesystem_untouched` (every pinned traversal shape plus each type's wrong-format id raises `ValueError`, seeded document left intact), `TestDeleteWholeBodyDomains::test_unknown_id_raises_domain_not_found_and_leaves_the_seed_intact` (well-formed unknown id raises the domain's own `XNotFoundError`), and `TestDeleteIoFailure::test_unlink_failure_raises_delete_error_with_cause_and_path` / `::test_rmtree_failure_raises_delete_error_with_cause_and_path` (mocked `Path.unlink`/`shutil.rmtree` raising `OSError` surface as `DeleteError` with the exact `OSError` as `__cause__` and the path in the message) — all OK.
- [x] ACC-006: Verifies REQ-006 — for the ten flat domains the `*.md` file is removed and its directory is left intact; for `feat` the whole `<base>/<id>/` folder (including a seeded `history.md`) is removed. — evidence: `tests.general.tools.test_delete.TestDeleteWholeBodyDomains::test_delete_returns_deleted_path_and_removes_the_document` (for all eleven types the returned `str` is exactly the seeded `*.md` file path for the flat domains / the folder path for `feat`, the target no longer exists, the containing directory is left intact, and a follow-up `load_by_id` raises the domain `XNotFoundError`) and `::test_feat_delete_removes_the_whole_folder_including_history_md` (the entire `<base>/<id>/` folder, including a seeded `history.md`, is removed via `shutil.rmtree`) — both OK.
- [x] ACC-007: Verifies REQ-007 — a new accepted ADR exists in `docs/adr/` (listed in the regenerated `docs/adr/README.md`); `AGENTS.md`, `server.py`'s docstring, and `CHANGELOG.md` are updated per REQ-007; `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` all run clean (no drift) after the edits. — evidence: `docs/adr/1af6787b-eaab-4e8f-888f-531c1e76c19d-replace-domain-specific-delete-tools-with-a-generic-type-dis.md` exists with frontmatter `status: accepted` and is listed in `docs/adr/README.md` (grep hit); `grep -cE 'delete_(req|uc|tsk|qa|prb|gol|rsk|dec|sop|feat|vcr)'` → 0 in `AGENTS.md` and 0 in `server.py` (`CHANGELOG.md`'s `[Unreleased]` entry is the pinned removal/added note per Design Notes §8, not a stub mention); `specmgr adr-toc` + `specmgr docs` + `specmgr mcp-docs` re-ran drift-free — each wrote byte-identical content and `git status` was clean afterwards (no `docs/` changes).
- [x] ACC-008: Verifies REQ-008 — `tests/general/tools/test_delete.py` and `tests/general/tools/test__path_safety.py` exist and pass; the full `unittest` suite is green; `ruff format --check`, `ruff check`, and `vulture` are clean. — evidence: both files are git-tracked (`git ls-files`) and pass — `tests.general.tools.test_delete` (8 tests, all eleven types parameterized, OK) and `tests.general.tools.test__path_safety` (23 tests, OK); full `unittest` suite green (2713 tests, OK) and `ruff format --check` (1462 files) / `ruff check` / `vulture src/ whitelist.py --min-confidence 60` clean per the Task 5.1 post-fix gate re-run.

### Scope

#### Included

- The generic `delete` MCP tool (`general/tools/delete.py`) with eleven type-dispatched adapters and an `_ADAPTERS` table.
- The reusable path-safety module (`general/tools/_path_safety.py`) and its unit tests.
- Removal of the eleven `delete_<d>` stub tools (source, registration, docstrings, stub tests).
- Per-domain locking and graceful error handling (`ValueError` for bad ids, `XNotFoundError` for missing docs, `DeleteError` for I/O failures).
- The `feat` folder-per-document hard delete (`shutil.rmtree`).
- Decision/documentation propagation: new ADR, `AGENTS.md`, `server.py` docstring, `CHANGELOG.md`, and `docs/` regeneration.
- New test files `tests/general/tools/test_delete.py` and `tests/general/tools/test__path_safety.py`.

#### Explicitly Out Of Scope

- Any change to ADR deletion — ADR has no `delete_adr` today and gets none; the generic `delete` covers only the eleven whole-body domains.
- Modifying the `get_<d>`, `update`, or `set_status` tools to call the new `_path_safety` module — the module is built to be reusable by them, but they are left untouched here (adoption is a future, separate decision).
- Soft-delete, archival, or status-based "deleted" semantics — the issue specifies a hard delete from disk.
- Re-introducing any per-domain `delete_<d>` tool, or any `specmgr://<d>/{id}` resource.
- A `delete` prompt (no `create_<d>`/`update_<d>`-style narrated prompt is added for deletion).

### Dependencies

#### Depends On

- ADR 36905d5b-8057-4294-8665-c7eed5534db0 (generic type-dispatched `update`/`set_status` tools — the structural precedent this feature copies for `delete`, including the `Literal` `type` parameter, the private-adapter-per-domain pattern, and the `_ADAPTERS` dispatch table).
- ADR 8cf940c5-3100-485c-a12d-14b59b631712 (`feat`'s folder-per-document, `feat-NNN-slug` addressing — the reason `feat`'s adapter and id format differ from the ten UUID domains).
- Each domain's existing `<d>/tools/_lock.py` (`<d>_lock`), `<d>/tools/_io.py` (`load_by_id`), and `<d>/tools/_paths.py` (`<d>_base_dir`, `XNotFoundError`) — the adapters reuse all of these rather than introducing new plumbing.
- ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of truth) and ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 (author/edit ADRs only through MCP structured tools — governs how the new ADR for this decision is created).

#### Blocks

- Nothing. This feature is self-contained; it removes a long-standing "still missing" item from `AGENTS.md` and is a prerequisite for any future domain that would otherwise be expected to ship its own `delete_<d>` stub (the new convention is that they instead add one adapter to the generic `delete` tool).

### Design Notes

This design is the complete, implementer-ready specification. The Phase-Orchestrator
should execute the Task List below against these notes; every file, function, and
behavior is pinned here so no design work remains at implementation time.

#### 1. The reusable path-safety module (`general/tools/_path_safety.py`)

This is the feature's most important new artifact and the one the user explicitly
required to be reusable by `get`/`update` later. It is a private, cross-domain helper
in the same package and in the same style as the existing `general/tools/_doc_paths.py`,
`_splice.py`, and `_paging.py`. It has **no** `mcp`/file-write dependency and performs
**no filesystem mutation** — it only inspects strings and `Path` objects — so it is
trivially safe to import from any read tool as well.

Public API (every function raises `ValueError` with a message that names the offending
value; every function starts with the codebase-standard `assert isinstance(...)` /
`assert value.strip()` input guards per `.specmgr/conventions.md`):

```python
__all__ = [
    "assert_feat_id",
    "assert_no_traversal",
    "assert_uuid",
    "assert_within",
    "validate_id",
]

#: The ten whole-body domains whose `id` is a server-generated v4 UUID.
_UUID_TYPES = frozenset({"req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr"})

#: Canonical 8-4-4-4-12 lowercase-hex UUID shape (the form `uuid.uuid4().str` produces,
#: which is what every `create_<d>` tool writes into the frontmatter `id`).
_UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

#: The `feat` folder-name shape (ADR 8cf940c5): `feat-NNN-slug`, lowercase alnum + hyphen.
_FEAT_ID_PATTERN = re.compile(r"^feat-[0-9]+-[a-z0-9-]+$")


def assert_no_traversal(id_: str) -> None:
    """Reject any id that could contribute a relative path.

    Universal guard, independent of domain: the value must be a non-empty `str`
    and must contain no `/`, no `\\`, and no `..`. This alone makes it impossible
    for the id to escape its base directory when joined into a path.
    """


def assert_uuid(id_: str) -> None:
    """Reject any id that is not a canonical lowercase-hex v4-shaped UUID.

    Enforced for the ten `_UUID_TYPES` domains. (Subsumes `assert_no_traversal`
    for well-formed input, but both are applied so the error message is precise.)
    """


def assert_feat_id(id_: str) -> None:
    """Reject any id that is not a well-formed `feat-NNN-slug` folder name."""


def validate_id(type_: str, id_: str) -> None:
    """Convenience dispatcher: `assert_no_traversal` plus the type's format check.

    `type_` in `_UUID_TYPES` -> `assert_uuid`; `type_ == "feat"` ->
    `assert_feat_id`; any other `type_` -> `ValueError` (unknown type). This is the
    single entry point the generic `delete` (and, later, `update`/`set_status`)
    calls before any filesystem access.
    """


def assert_within(base_dir: Path, candidate: Path) -> None:
    """Defense-in-depth: `candidate.resolve()` must be `is_relative_to(base_dir.resolve())`.

    Type-agnostic. Called by the adapters *after* id -> path resolution, so that even
    if a future id-validation gap existed, a resolved path could never point outside
    the domain's own base directory.
    """
```

Reusability contract (why `get`/`update` can adopt this later with zero rework):
the five functions take only plain `str`/`Path`/`type` inputs, perform no I/O, and
return `None` (raise on failure). A future `get_<d>` would call
`assert_no_traversal(id)` + the domain's format assert + `assert_within(base_dir, path)`;
a future `update`/`set_status` would call `validate_id(type, id)` + `assert_within(...)`.
No delete-specific state, argument, or return value leaks into this module. `DeleteError`
(RQ-005's I/O wrapper) deliberately lives in `delete.py`, **not** here, for the same
reason — it is a delete-specific concern, not a reusable safety primitive.

#### 2. The generic tool (`general/tools/delete.py`)

Structure mirrors `general/tools/set_status.py` file-for-file: a long module docstring
(explaining the dispatch, the safety, the error contract, and that ADR is excluded),
the per-domain private adapters, the `_ADAPTERS` table, and the single
`@mcp.tool(name="delete")`-decorated public function. Imports follow the same
qualified, per-domain `from ...<d>.tools._lock import <d>_lock` / `from ...<d>.tools._io
import load_by_id as load_<d>_by_id` / `from ...<d>.tools._paths import <d>_base_dir`
pattern `set_status.py` uses.

Public function (parameter intentionally named `type`, matching `set_status`/`update`):

```python
#: The eleven whole-body domains the generic delete tool covers (ADR excluded).
_DELETE_TYPES = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr")


class DeleteError(OSError):
    """A delete failed at the filesystem layer (I/O error, permission, or race).

    Carries the resolved path and the underlying `OSError` as `__cause__` so the
    MCP host can surface a meaningful message to the caller (REQ-005).
    """


@mcp.tool(
    name="delete",
    title="Delete document",
    description=(
        "Permanently delete an existing document from disk across the eleven whole-body "
        "domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr; "
        "`adr` is not supported). Resolves the document by `id`, takes the domain lock, "
        "and removes it: the single `*.md` file for the ten flat domains, or the entire "
        "`<base>/<id>/` folder for `feat`. Returns the deleted path as a string. "
        "An invalid `id` (path-injection attempt or wrong format) is a `ValueError` "
        "raised before any file access; a missing document is the domain's own "
        "`XNotFoundError`; an I/O failure is a `DeleteError`. This is the sole "
        "delete entry point -- the former per-domain `delete_<d>` tools are removed."
    ),
)
def delete(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr"],
) -> str:
    """..."""
    # REQ-003: validate before any filesystem access (injection prevention).
    validate_id(type, id)
    result = _ADAPTERS[type](id)
    return result
```

`_ADAPTERS` is `dict[str, Callable[[str], str]]` mapping each of the eleven `type`
strings to its `_delete_<d>` adapter.

#### 3. The per-domain adapters

Ten of the eleven are byte-for-byte the same shape, differing only in the domain's
lock / `load_by_id` / `base_dir` / `XNotFoundError` names. The canonical form (shown
for `req`):

```python
def _delete_req(id_: str) -> str:
    """Hard-delete the requirement `id_` from disk (REQ-001/004/005/006)."""
    base_dir = req_base_dir()
    with req_lock(id_):  # REQ-004
        path, _existing = load_req_by_id(base_dir, id_)  # resolves + ReqNotFoundError
        assert_within(base_dir, path)  # REQ-003 defense-in-depth
        try:
            path.unlink()  # REQ-006
        except OSError as ex:
            raise DeleteError(f"failed to delete {path}: {ex}") from ex  # REQ-005
    return str(path)  # REQ-001
```

Notes on the adapter contract:
- `load_by_id` is used (not a raw `find_*_path`) for consistency with `set_status`/
  `update`; the returned parsed document is discarded (`_existing`) — only the `path`
  is needed. This also guarantees the target is a valid, parseable document of that
  domain with that exact `id` before anything is removed.
- The domain's own `XNotFoundError` (e.g. `ReqNotFoundError`) propagates unchanged
  from `load_by_id` — the adapter does not catch it (REQ-005).
- `validate_id` is **not** repeated inside each adapter; it is called once in the
  public `delete` before dispatch. The `assert_within` **is** repeated per adapter
  because it needs the resolved `path` (available only inside the lock).

The `feat` adapter diverges in exactly two ways (folder-per-document, ADR 8cf940c5):
it removes the containing folder, not the `README.md` file, and it returns the folder
path.

```python
def _delete_feat(id_: str) -> str:
    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, _existing = load_feat_by_id(base_dir, id_)  # <base>/<id>/README.md
        folder = path.parent
        assert_within(base_dir, folder)
        try:
            shutil.rmtree(folder)  # REQ-006: whole folder
        except OSError as ex:
            raise DeleteError(f"failed to delete {folder}: {ex}") from ex
    return str(folder)
```

`delete.py` therefore imports `shutil` (the only new stdlib import) and, for `feat`,
uses `path.parent` as the deletion target.

#### 4. Locking (REQ-004)

No new lock is introduced. Each adapter re-uses the domain's existing
`<d>/tools/_lock.py::<d>_lock(id_)` — the very lock the generic `update` and
`set_status` adapters already take for the same id. Because `delete`'s
resolve-then-delete runs under that same per-id lock, a concurrent `update`/
`set_status`/`delete` targeting the same id is serialized, satisfying the issue's
"we have a lock in place when we find the file and delete it."

#### 5. Path-injection threat model (REQ-003)

- `type`: a closed `Literal` of eleven strings — structurally incapable of carrying
  a path. No check needed beyond the `Literal` itself (and `validate_id` rejecting an
  unknown type string at the Python level, for callers that bypass the schema).
- `id`: the only free-form input. Two independent layers stop injection:
  1. **Format validation** (`validate_id`, before any I/O): no `/`, `\`, or `..`
     (`assert_no_traversal`), plus a strict domain format (canonical UUID for the ten
     UUID domains; `feat-NNN-slug` for `feat`). A value like `../../etc/passwd` fails
     both the traversal and the format checks and is rejected with a `ValueError`
     before the filesystem is touched.
  2. **Containment** (`assert_within`, after resolution, inside the lock): the resolved
     path must be `is_relative_to` the domain's base directory. This is defense-in-depth
     against any future gap in layer 1 (e.g. a domain whose resolver builds a path from
     the id, as `feat` does).
- The ten flat domains' resolvers (`find_<d>_path`) scan and compare parsed ids rather
  than joining the id into a path, so they are already injection-safe; the `feat`
  resolver (`find_feat_path_by_id`) *does* join `base_dir / id / README.md`, which is
  precisely why the two-layer guard matters and is why `assert_feat_id` +
  `assert_within` are both applied for `feat`.

#### 6. Error contract (REQ-005)

| Condition | Raised | Where | Filesystem touched? |
|---|---|---|---|
| `id` has `/`, `\`, `..`, or wrong format for `type` | `ValueError` | public `delete`, via `validate_id` | No (before dispatch) |
| unknown `type` string (Python-level) | `ValueError` | `validate_id` | No |
| no document with `id` in `type`'s domain | domain `XNotFoundError` | adapter, via `load_by_id` | No (read-only scan) |
| resolved path escapes base dir | `ValueError` | adapter, via `assert_within` | No |
| `unlink`/`rmtree` I/O failure | `DeleteError` (wraps `OSError`) | adapter | Partial at most |

#### 7. The new ADR (REQ-007)

Created via the `create_adr` MCP tool (per ADR 898bfcd0, ADRs are authored only
through structured tools), then `specmgr adr-toc`. Title: **"Replace domain-specific
delete tools with a generic type-dispatched delete tool"**. Suggested body:
- *Context and Problem Statement*: eleven unimplemented `delete_<d>` stubs inflate the
  tool surface; no delete path-safety exists; the issue (#36) asks for one generic,
  safe, locked delete.
- *Decision Drivers*: minimal tool surface; explicit `type` keeps id resolution
  single-domain; injection safety; reuse of existing per-domain locks/resolvers;
  filesystem-is-source-of-truth.
- *Considered Options*: (1) generic `delete(id, type)` with per-domain adapters + a
  reusable `_path_safety` module (chosen); (2) implement each `delete_<d>` stub
  independently (rejected: eleven near-duplicates, no shared safety); (3) uuid-only
  id resolution scanning all domains (rejected: cross-domain UUID ambiguity, full-dir
  scan on the write path — same reasons ADR 36905d5b rejected it for `update`).
- *Decision Outcome*: Option 1; ADR excluded (no `delete_adr` ever existed; deleting an
  ADR risks breaking other ADRs' "superseded by X" references); convention — every
  current and future domain implements a `delete` adapter in the generic tool, never a
  per-domain `delete_<d>` tool.
- *Consequences*: breaking (eleven tools removed, one added — the 0.x MCP tool list is
  the only client contract, recorded in `CHANGELOG.md`); `get`/`update`/`set_status`
  can now adopt `_path_safety` for their own injection protection in a future change.
- *More Information*: this feature plan; related ADRs 36905d5b, 8cf940c5, 33c5ab08,
  898bfcd0.

#### 8. Documentation propagation (REQ-007)

- `AGENTS.md`: in each of the eleven per-domain Status bullets, replace the
  "`delete_<d>` stub" / "`delete_<d>` (stub, not yet implemented)" mention with a note
  that deletion goes through the generic `delete` tool (`type="<d>"`); delete the
  "Still genuinely missing" bullet "`delete_req`/…/`delete_vcr` are stubs, not yet
  implemented"; in the `general/` bullet, add `delete` to the `general/tools/` list and
  add a sentence that all eleven whole-body domains implement a `delete` adapter there
  (ADR-excluded). Keep the `ac` "future domain" convention note in sync (a future domain
  adds a `delete` adapter too).
- `server.py` module docstring: remove the eleven per-domain `delete_<d>` stub mentions
  from the domain tool paragraphs; add `delete` to the "General tools
  (`general/tools/`)" paragraph describing it (eleven whole-body domains, ADR excluded,
  returns the deleted path, safety/lock/error contract in one line).
- `CHANGELOG.md`: under `[Unreleased]`, a `### Changed`/`### Removed` entry: removed the
  eleven `delete_<d>` stub tools; added the generic `delete` tool; added reusable
  `general/tools/_path_safety.py`. Mark breaking (0.x).
- Regenerate `docs/`: `specmgr docs` (API docs + `docs/GENERATED.md`), `specmgr
  mcp-docs` (`docs/MCP.md`), `specmgr adr-toc` (`docs/adr/README.md`) — each run twice
  to confirm a stable fixed point (no drift).

#### 9. Test design (REQ-008)

`tests/general/tools/test__path_safety.py` — pure unit tests, no filesystem:
- `assert_no_traversal`: accepts a plain id; rejects `""`, `"../x"`, `"a/b"`, `"a\b"`,
  `".."`, `"a/../b"` (each a `ValueError`).
- `assert_uuid`: accepts a canonical lowercase UUID; rejects uppercase, a 31-char
  string, a string with `/`, and a `feat-1-x` string.
- `assert_feat_id`: accepts `"feat-36-delete"`; rejects `"feat-36"` (no slug),
  `"feature-36-x"`, `"feat-36/../x"`, and a UUID.
- `validate_id`: for each of the ten UUID types a UUID passes and a `feat` id fails;
  for `feat` a `feat` id passes and a UUID fails; an unknown `type_` raises.
- `assert_within`: a child path of the base passes; a sibling/ancestor path raises.

`tests/general/tools/test_delete.py` — parameterized over all eleven types (mirroring
`test_set_status.py`'s fixture strategy: seed a real document per type via the domain's
own `create_<d>` into a temp `SPECMGR_DOCS_DIR` / `SPECMGR_FEAT_DIR`):
- success: record the returned `str`; assert the file (or `feat` folder) no longer
  exists; assert a follow-up `get_<d>`/`load_by_id` raises the domain `XNotFoundError`.
- `feat` specifically: seed a `history.md` in the folder; assert the whole folder (and
  the `history.md`) is gone.
- injection: for each type, call `delete` with `../x`, `a/b`, `a\b`, `..`, and a
  wrong-format id; assert `ValueError` and that the seeded document still exists.
- unknown id: assert the domain `XNotFoundError`.
- I/O failure: mock `Path.unlink` (or `shutil.rmtree` for `feat`) to raise `OSError`;
  assert `DeleteError` is raised and its message contains the path.
- locking: spy/mock the domain `<d>_lock` and assert it is entered for the delete.

The eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files are deleted (REQ-002);
no replacement per-domain delete tests are added — coverage moves entirely to
`tests/general/tools/test_delete.py`.

### Related Decisions

- New ADR (created in Phase 4, REQ-007): "Replace domain-specific delete tools with a
  generic type-dispatched delete tool" — the architecture-level record of this feature's
  decision and of the forward convention that every domain implements a `delete` adapter
  in the generic tool.
- ADR 36905d5b-8057-4294-8665-c7eed5534db0 — the `update`/`set_status` generic-tool
  precedent this feature extends with `delete`.
- ADR 8cf940c5-3100-485c-a12d-14b59b631712 — `feat`'s folder-per-document addressing,
  which drives `feat`'s distinct adapter and id format.
- ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 — filesystem is the sole source of truth
  (delete removes the on-disk file; there is no separate deletion record).
- ADR 898bfcd0-85f9-462f-93a8-747bda4166c8 — ADRs are authored/edited only through MCP
  structured tools (governs Phase 4's `create_adr` step).

### Task List

#### Phase 0: Worktree, branch, and design plan (designer)

- [x] Task 0.1: Create the `feat-36-delete` git worktree/branch from `dev` at `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete` (`dev` left untouched) — status: done (2026-08-31).
- [x] Task 0.2: Author this feature README (the full design) — status: done (2026-08-31).
- [x] Task 0.3: Strip leftover debug `print()` calls (and the assignments/loops that become dead with them) from `tests/models/md/test_markdown_section.py`, `tests/models/md/test_markdown_str.py`, and `tests/models/md/test_markdown_list_item.py` — applied byte-exact to `dev` (separate commit there, pushed by the maintainer) and to this branch so the later feature merge stays conflict-free; makes the `unittest` output (and the pre-commit hook's) noise-free — depends on: Task 0.2 — status: done (2026-08-31).

#### Phase 1: Reusable path-safety module (Phase-Orchestrator)

- [x] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1 (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 — status: done (2026-08-31).
- [x] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 — depends on: Task 1.1 — status: done (2026-08-31).

#### Phase 2: The generic delete tool (Phase-Orchestrator)

- [x] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`, eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name="delete")` public function calling `validate_id` then dispatching) and register it in `general/tools/__init__.py` (`from .delete import delete`, the `__all__` entry, and a sentence in the module docstring — the server registers tools purely via this package's import side effect) — depends on: Task 1.1 — status: done (2026-08-31).
- [x] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 — depends on: Task 2.1 — status: done (2026-08-31).

#### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)

- [x] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files — depends on: Task 2.1 — status: done (2026-08-31).
- [x] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the stub mention in the module docstring; **additionally** in each of the eleven domain-level `<d>/__init__.py` package docstrings, drop `delete_<d>` from the tool enumeration (required by ACC-002: `grep -r "delete_<d>"` over all of `src/` must return nothing) — depends on: Task 3.1 — status: done (2026-08-31).
- [x] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files — depends on: Task 3.2 — status: done (2026-08-31).

#### Phase 4: Decision and documentation propagation (Phase-Orchestrator)

- [x] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7 (requester-confirmed: the enabled specmgr MCP server resolves `docs/adr` relative to its CWD, i.e. this worktree — sanity-check with `git status` right after creation), set it `accepted`, run `specmgr adr-toc`, and ensure the new ADR file plus the regenerated `docs/adr/README.md` are `git add`ed into the Phase 4 commit — depends on: Task 3.3 — status: done (2026-09-01).
- [x] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 — status: done (2026-08-31).
- [x] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on: Task 3.3 — status: done (2026-08-31).
- [x] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 — depends on: Task 3.3 — status: done (2026-08-31).
- [x] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 — status: done (2026-09-01).

#### Phase 5: Quality gate and sign-off (Phase-Orchestrator)

- [x] Task 5.1: Run the full gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory `pylint`) and fix any failures — depends on: Task 4.5 — status: done (2026-09-01).
- [x] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification (test file / tool / doc proving it), update Current Status, and bump this README's frontmatter `status`/`updated` — depends on: Task 5.1 — status: done (2026-09-01).

## Progress

### Current Status

**As of 2026-09-01 (Phase 5 complete — feature signed off, done)**: all five
phases are complete. Phase 0 (design, including Task 0.3), Phase 1 (the
reusable path-safety module), Phase 2 (the generic `delete` tool), Phase 3
(retire the eleven delete stubs), and Phase 4 (the accepted ADR
`1af6787b-eaab-4e8f-888f-531c1e76c19d` in `docs/adr/`, propagation to
`AGENTS.md`/`server.py`/`CHANGELOG.md`, and `docs/` regeneration to a
verified fixed point) delivered: `general/tools/_path_safety.py` provides
the five pinned, pure, non-I/O assertions, and `general/tools/delete.py`
registers the single generic `delete(id, type)` MCP tool for the eleven
whole-body domains (ADR excluded) — `validate_id` before any filesystem
access (REQ-003), per-domain private `_delete_<d>` adapters that resolve via
the domain's own `load_by_id` under the domain's own per-id lock (REQ-004),
`assert_within` containment, and a hard delete via `Path.unlink()` (the ten
flat domains) or `shutil.rmtree` on the whole `<base>/<id>/` folder (`feat`);
the domain's own `XNotFoundError` propagates unchanged and an I/O failure
surfaces as `DeleteError` (an `OSError` subclass, REQ-005). The eleven
`delete_<d>` stub tools are fully retired (modules, `__init__.py`
references, stub tests, and stale API pages all removed, with a pointer line
to the generic `delete` tool in each `<d>/tools/__init__.py`), the six
integration-test modules now end their lifecycle with a real generic delete,
and the live MCP surface is 93 tools — exactly one `delete` and zero
`delete_<d>`. Phase 5's full quality gate is green: `ruff format --check`
(1462 files already formatted), `ruff check` (All checks passed), `vulture
src/ whitelist.py --min-confidence 60` clean, full `unittest` suite OK
(2713 tests), and the advisory `pylint` at the known 8.89/10 repo baseline —
the only feature-file findings beyond the pinned `delete.py` W0622 (identical
findings at `set_status.py`/`update.py`), the pre-existing `server.py:337`
C0413/W0611, and the 160 pre-existing `cyclic-import` R0401 findings were in
`tests/general/tools/test_delete.py` and are resolved: the five C0301
line-too-long docstrings are wrapped without changing test semantics and the
lock-spy test is restructured into a per-case helper so its closure captures
no loop-defined cell variables (W0640 gone), while the two R1732 and one
C0415 findings are left with sibling precedent (the identical patterns in
`test_set_status.py`/`test_update.py`, which pylint flags the same way); a
repo-wide pylint re-run confirms zero new findings. ACC-001..ACC-008 are all
verified, each criterion line marked `[x]` with concrete evidence appended;
this feature is done.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-01 01:28:41.000Z — Phase 5 complete: full gate green, ACC-001..ACC-008 verified, feature signed off

Ran the Phase 5 full quality gate (Task 5.1) and the ACC sign-off walk (Task 5.2). Gate results before any fix: `ruff format --check` (1462 files already formatted), `ruff check` (All checks passed), `vulture src/ whitelist.py --min-confidence 60` (clean, exit 0), the full `unittest` suite (2713 tests, OK), and advisory `pylint` at the known repo baseline 8.89/10 — whose only feature-file findings, beyond the pinned `delete.py` W0622 redefined-builtin `id`/`type` (identical findings at `set_status.py:503-504` and `update.py:610-611`, intentional per the plan), the pre-existing `server.py:337` C0413/W0611, and the 160 pre-existing `cyclic-import` R0401 findings, were in `tests/general/tools/test_delete.py`: five C0301 line-too-long, three W0640 cell-var-from-loop (the lock-spy test), two R1732 consider-using-with, and one C0415 import-outside-toplevel. Applied exactly the pinned disposition: the five overlong docstrings (the `TempDeleteDirTestCase` class docstring, the `TestDeleteWholeBodyDomains` class docstring, and the injection/rmtree/lock-spy method docstrings) are wrapped without changing any test semantics, and the lock-spy test is restructured by extracting its per-case body into a `_assert_lock_entered(case)` helper method — the original `spy_lock` closure body is kept byte-identical, but its captured `events`/`real_lock` are now plain function locals rather than loop-defined cell variables, which removes all three W0640 findings (an intermediate default-argument capture variant was tried first and abandoned because it introduced a new W0102 dangerous-default-value finding). Left in place, with the sibling precedent: the two R1732 findings on the `setUp` temp-dir allocations are lifecycle-managed by `unittest.TestCase.enterContext` (not unmanaged) and match the byte-identical `Path(self.enterContext(tempfile.TemporaryDirectory()))` pattern at `test_set_status.py:460` and `test_update.py:798`, which pylint flags the same way, and the C0415 finding on the registration smoke test matches `test_update.py:1082` (`setUpClass` importing `server.mcp` to defer the server import out of module load). Every other feature-file finding (the six `test_integration.py` modules and the eleven `<d>/tools/__init__.py` files, all zero findings on `__init__.py`) was verified pre-existing by running pylint on the pre-feature base revision of those files — no finding sits on a feature-authored line, only line shifts. After the fix, the full gate was re-run: `ruff format --check` / `ruff check` / `vulture` clean, full `unittest` suite OK (2713 tests), and a repo-wide pylint re-run shows exactly the five C0301 + three W0640 findings gone, the three pinned leave-in-place findings (two R1732, one C0415) still present, and zero new findings anywhere. The ACC walk then verified each criterion with freshly-run evidence (each criterion line is now `[x]` with the concrete justification appended on the same line): ACC-001 the live `mcp.list_tools()` after importing `server` shows 93 tools, exactly one `delete` with the 11-value `type` enum and `required` `["id", "type"]`, zero `delete_<d>`, the live delete call on a seeded document returns the deleted path, and `docs/MCP.md` lists exactly one `delete` tool row and zero `delete_<d>` rows; ACC-002 `git ls-files` shows no `delete_<d>.py` file and the repo-wide grep returns nothing under `tests/` and, under `src/`, only the protected private `_delete_<d>` adapter names inside `general/tools/delete.py` (a by-design mirror of REQ-001's pinned adapter names, plus gitignored egg-info/pycache build artifacts) while `import biz.dfch.specmgr.<d>.tools` succeeds for all eleven domains; ACC-003 the five `_path_safety` functions are exposed and imported by `delete.py`, `tests/general/tools/test__path_safety` passes (23 tests), and the module is pure (imports only `__future__`/`re`/`pathlib`, no I/O beyond the sanctioned read-only `Path.resolve()` in `assert_within`, no delete-specific imports — its eight `delete` mentions are docstring/example text); ACC-004 `TestDeleteLocking.test_the_domain_lock_is_entered_around_the_delete` spies each of the eleven `<d>_lock`s and asserts `["acquire:<id>", "release"]` bracket the delete; ACC-005 `TestDeleteInjection`, `TestDeleteWholeBodyDomains.test_unknown_id_raises_domain_not_found_and_leaves_the_seed_intact`, and both `TestDeleteIoFailure` tests prove `ValueError` (seed untouched), the domain `XNotFoundError`, and `DeleteError` (with `__cause__` and the path in the message); ACC-006 `TestDeleteWholeBodyDomains` proves the flat-file delete (file gone, directory intact) and the `feat` whole-folder delete including a seeded `history.md`; ACC-007 ADR `1af6787b-eaab-4e8f-888f-531c1e76c19d` exists in `docs/adr/` with frontmatter `status: accepted`, is listed in `docs/adr/README.md`, `AGENTS.md` and `server.py` carry zero `delete_<d>` stub mentions (the `CHANGELOG.md` `[Unreleased]` entry is the pinned removal/added note per Design Notes §8), and `specmgr adr-toc`/`specmgr docs`/`specmgr mcp-docs` re-ran drift-free (byte-identical output, `git status` clean afterwards); ACC-008 both new test files are tracked and pass (8 + 23 tests), the full suite is green (2713 tests), and `ruff format --check`/`ruff check`/`vulture` are clean per the Task 5.1 re-run. Also normalized the pre-existing schema defect in the 2026-08-31 18:28:48 session-handover entry below: its bullet lists violated the feat v1 `UpdateEntry` schema (exactly one paragraph per entry) and made `parse_feat` of this README fail at HEAD — it is now a single flowing prose paragraph with the heading/timestamp byte-identical and every fact preserved, and `parse_feat` of the whole document now succeeds. With all five phases complete, the gate green, and ACC-001..ACC-008 verified, this feature is signed off: frontmatter `status` set to `done`.

#### 2026-08-31 23:20:24.000Z — Phase 4 (Tasks 4.2–4.4): AGENTS.md, server.py docstring, CHANGELOG.md updated

Implemented Tasks 4.2–4.4 strictly per Design Notes §8 — the three documentation-propagation file edits of Phase 4; Task 4.1 (the new ADR, created via the `specmgr` MCP structured tools per ADR 898bfcd0 and set `accepted`) and Task 4.5 (docs regeneration, `specmgr docs`/`mcp-docs`/`adr-toc` each run twice to a fixed point) remain for the orchestrator. In `AGENTS.md` (Task 4.2), each of the eleven per-domain Status bullets (`req/`, `uc/`, `tsk/`, `qa/`, `prb/`, `gol/`, `rsk/`, `dec/`, `sop/`, `feat/`, `vcr/`) drops its `delete_<d>` stub mention from the tool enumeration (with `feat`'s "All 8 tools" count corrected to "All 7 tools") and gains a deletion note worded consistently with the generic `update`/`set_status` phrasing already in each bullet ("deletions through the generic `delete` tool (`type="<d>"`)"); the "Still genuinely missing / not yet done" stubs bullet ("`delete_req`/…/`delete_vcr` are stubs, not yet implemented") is removed, leaving the heading and the other three bullets intact; the `general/` bullet's `general/tools/` enumeration gains `delete` — the generic type-dispatched hard-delete for the eleven whole-body domains (`adr` excluded), with a note that all eleven domains implement a `delete` adapter in that one tool (a future domain adds its own adapter there, never a per-domain `delete_<d>` tool), resolving by `id`, taking the domain's own lock, and returning the deleted path; and the `ac` "future domain" convention note now reads "one dispatch entry to each of the two generic tools in `general/tools/` (`update`'s `type`, `set_status`'s `type`), one `delete` adapter in the generic `delete` tool, plus a `raw` parameter on the new `get_<d>` tool — not new `update_<d>`/`set_status_<d>`/`delete_<d>` tools". In `server.py`'s module docstring (Task 4.3 — the authoritative registration list; docstring text only, no code touched), the eleven per-domain `delete_<d>` stub mentions are removed from the domain tool paragraphs, keeping every other tool name and the surrounding sentence structure, and the "General tools" paragraph gains a `delete` entry on the same `name -- description` pattern: the generic type-dispatched hard-delete for the eleven whole-body domains (`type` one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr, `adr` not supported), resolves by `id`, takes the domain lock, and returns the deleted path, with a `ValueError` for injection/wrong-format ids before any file access, the domain's `XNotFoundError` for missing documents, and a `DeleteError` for I/O failures. In `CHANGELOG.md` (Task 4.4), the previously empty `[Unreleased]` section gains a `### Removed` entry (**BREAKING** 0.x: the eleven `delete_<d>` stub MCP tools deleted outright, no deprecated wrappers, with the caller switch to `delete` plus the explicit `type` parameter) and an `### Added` entry (the generic `delete(id, type)` MCP tool in `general/tools/` with its full dispatch, locking, and `ValueError`/`XNotFoundError`/`DeleteError` error contract, and the reusable, doc-type-agnostic `general/tools/_path_safety.py` module with its five pure, no-I/O guards, wired into `delete` now and adoptable later by `get_<d>`/`update`/`set_status` with zero rework) — both sub-headings following the file's existing Keep-a-Changelog convention and the 0.13.0 `### Removed`/`### Added` precedent. Phase-end quality gate all green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full `unittest` suite (2713 tests OK — the Phase-3 baseline, unchanged since this phase is doc-only), `python -c "import biz.dfch.specmgr.server"` (SERVER IMPORT OK), and the verification grep `grep -nE 'delete_(req|uc|tsk|qa|prb|gol|rsk|dec|sop|feat|vcr)' AGENTS.md src/biz/dfch/specmgr/server.py` returning zero matches in both files (all eleven stub mentions gone; the remaining matches elsewhere — `general/tools/delete.py`'s private `_delete_<d>` adapter names and the `docs/` mirrors — are expected and will be reconciled by the orchestrator-owned Task 4.5 docs regeneration).

#### 2026-08-31 21:32:55.000Z — Phase 3 complete: eleven delete stubs retired

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

#### 2026-08-31 20:21:21.000Z — Phase 2 complete: generic delete tool

Implemented Tasks 2.1–2.2 strictly per Design Notes §2–§6/§9. Added `src/biz/dfch/specmgr/general/tools/delete.py`, the generic `delete` MCP tool: `@mcp.tool(name="delete", title="Delete document")` with the pinned `def delete(id: str, type: Literal[...eleven values...]) -> str` body (`validate_id(type, id)` before any filesystem access per REQ-003, then `_ADAPTERS[type](id)` and return the result); `DeleteError(OSError)` per REQ-005; `_DELETE_TYPES` with the pinned comment; and the eleven private `_delete_<d>` adapters — the ten flat domains in the canonical pinned form (`<d>_base_dir()` → `<d>_lock(id_)` → `load_<d>_by_id(base_dir, id_)` with the parsed document discarded → `assert_within(base_dir, path)` → `path.unlink()` in a try/except re-raising `DeleteError(f"failed to delete {path}: {ex}") from ex` → `return str(path)` after the lock) and the `feat` adapter diverging exactly per §3 (`folder = path.parent`, `assert_within(base_dir, folder)`, `shutil.rmtree(folder)` in the same try/except, `return str(folder)`); the domain's own `XNotFoundError` propagates unchanged from `load_by_id`, and `shutil` is the only new stdlib import. Each adapter follows `set_status.py`'s qualified per-domain import pattern (`<d>_lock`, `load_by_id as load_<d>_by_id`, `<d>_base_dir`), and the tool is registered in `general/tools/__init__.py` (`from .delete import delete`, the `__all__` entry, and a module-docstring sentence). Added `tests/general/tools/test_delete.py` — 8 test methods parameterized over all eleven types, mirroring `test_set_status.py`'s fixture strategy (seeding a real document per type via the domain's own `create_<d>` into temp `SPECMGR_DOCS_DIR`/`SPECMGR_FEAT_DIR`): success (the returned `str` is the deleted file path for the flat domains / the deleted folder path for `feat`, the file/folder is gone, a follow-up `load_by_id` raises the domain's `XNotFoundError`); the `feat` folder-per-document delete including a seeded `history.md`; every pinned injection shape (`../x`, `a/b`, `a\b`, `..`) plus each type's wrong-format id raising `ValueError` with the seeded document left intact; a well-formed unknown id raising the domain's `XNotFoundError`; a mocked `Path.unlink` (ten flat domains) / `shutil.rmtree` (`feat`) `OSError` surfacing as `DeleteError` (an `OSError`, the exact instance as `__cause__`, the path in the message, target left in place); the domain's own per-id lock entered around the delete for all eleven types (an event-ordered spy wrapping each `<d>_lock`); and a registration smoke test (mirroring `test_update.py`'s) verifying the live `mcp` registration carries `delete` exactly once with the 11-value `type` enum and required `id`/`type`. Phase-end quality gate all green: `ruff format --check` (1493 files), `ruff check` (All checks passed), and `vulture src/ whitelist.py --min-confidence 60` clean (no whitelist change needed — `_DELETE_TYPES` is a private module constant, which vulture ignores by name convention); target test module OK (8 tests); full `unittest` suite OK (2735 tests = 2727 baseline + 8 new, ~114 s); `import biz.dfch.specmgr.server` OK (104 tools registered; `delete` present exactly once; the eleven `delete_<d>` stubs still registered, as expected — Phase 3 retires them). Phase 3 (retire the eleven delete stubs, Tasks 3.1–3.3) is next.

#### 2026-08-31 19:09:41.000Z — Phase 1 complete: reusable path-safety module

Implemented Tasks 1.1–1.2 strictly per Design Notes §1/§9. Added `src/biz/dfch/specmgr/general/tools/_path_safety.py`, the reusable, doc-type-agnostic path-safety module: `__all__` with the five public functions (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`), `_UUID_TYPES` (the ten UUID domains), the canonical 8-4-4-4-12 lowercase-hex `_UUID_PATTERN`, the `_FEAT_ID_PATTERN` (`^feat-[0-9]+-[a-z0-9-]+$`), and comparison constants for the `feat` type name, the path separators, and the `..` sequence; no `mcp` dependency, no filesystem mutation (the sanctioned touch is `assert_within`'s read-only `Path.resolve()` calls), no `DeleteError` (it lives in the Phase 2 `delete.py`, per §1's reusability contract); every function starts with the standard input guards and raises `ValueError` with a message naming the offending value, and `validate_id` is the single before-filesystem-access entry point (rejecting unknown `type_` values). Added `tests/general/tools/test__path_safety.py` with 23 pure unit tests covering every §9 case (the six pinned `assert_no_traversal` rejection shapes; the `assert_uuid` and `assert_feat_id` accept/reject sets; `validate_id` over all ten UUID domains, `feat`, an unknown type, and a traversal id; `assert_within` child/base/sibling/ancestor containment). Phase-end quality gate all green: `ruff format --check` (1490 files), `ruff check`, and `vulture src/ whitelist.py --min-confidence 60` clean; target test module OK (23 tests); full `unittest` suite OK (2727 tests = 2704 baseline + 23 new, ~105 s). Phase 2 (the generic `delete` tool, Tasks 2.1–2.2) is next.

#### 2026-08-31 18:28:48.000Z — Session handover: Phase 0 complete, Phase 1 ready for a fresh session

The design session ended with Phase 0 complete. Implementation of Phases 1–5 resumes in a **fresh session**, orchestrated from this README, with the main agent acting as Phase-Orchestrator and launching the `phase-implementer` subagent **once per phase** (1, then 2, …, 5): each subagent implements its phase end-to-end (code, tests, phase-end quality gate, task-line status updates in this README) and reports back, and the orchestrator verifies the gate results and commits before starting the next phase. The agreed commit policy is **one commit per phase** on `feat-36-delete`: the orchestrator commits without asking for permission but does **NOT push**, and stops and asks only when it needs a user decision or hits a wall. For Task 4.1's ADR, the enabled specmgr MCP server (`uvx biz-dfch-specmgr[mcp]`) resolves `docs/adr` relative to its CWD — the requester confirmed `create_adr` lands the file in this worktree — and the new ADR file must be committed together with the other Phase 4 files; the disabled `specmgr-test` MCP server must NOT be enabled (it points at the main repo), and `git pull` must NOT be run on this branch (no upstream tracking is set). Two plan refinements agreed this session (folded into the Task List above): Task 2.1 additionally registers `delete` in `general/tools/__init__.py` (import / `__all__` / docstring) — without it the tool would silently never register — and Task 3.2 additionally drops `delete_<d>` from the eleven domain-level `<d>/__init__.py` package docstrings — otherwise ACC-002's grep-over-`src/` criterion would fail. Repo state at handover: worktree `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`, branch `feat-36-delete`, working tree clean, tip the Task 0.3 debug-print cleanup commit; the main repo on `dev` (`/home/user/src/biz.dfch.SpecMgr`) carries the byte-exact same cleanup commit (`9eb7e8a`), which the maintainer pushes; the baseline is verified green — full `unittest` suite (2704 tests, OK, noise-free output), `ruff format --check` (1487 files), `ruff check`, and `vulture` all clean. Pre-commit hooks are active in both checkouts, with one known UX: when a hook (e.g. `ruff-format`) modifies a staged file, the first commit attempt fails with "Files were modified by this hook" — re-`git add` the file and commit again — and the `unittest` hook (full suite, ~2 min) and `specmgr-coverage-badge` run on any `src`/`tests` change, while the `specmgr docs`/`mcp-docs`/`adr-toc`/`schema` hooks are scoped to `src/` / `docs/adr` changes and will fire on the Phase 3/4 commits. **Next action:** launch `phase-implementer` for **Phase 1** (Tasks 1.1–1.2).

#### 2026-08-31 18:10:22.000Z — Leftover debug prints stripped from the md model tests (Task 0.3)

Removed 17 debug `print()` calls — plus the `lines = ...`/`result = ...`
assignments and one loop that became dead with them — from
`tests/models/md/test_markdown_section.py` (`TestAnyHeadingLeafSectionExtent`),
`tests/models/md/test_markdown_str.py` (`TestGetExtent`), and
`tests/models/md/test_markdown_list_item.py` (`test_nested_list`). The
byte-exact change was committed to `dev` (maintainer pushes) and to this
branch separately, so the feature's later merge into `dev` is
conflict-free. No behavior change: the three test modules pass (64 tests),
`ruff` is clean, and the `unittest` output is noise-free again.

#### 2026-08-31 15:37:40.000Z — Feature designed; worktree and plan authored (Phase 0 complete)

Completed the design for issue #36. Created the `feat-36-delete` git worktree/branch
from `dev` (leaving `dev` untouched) and authored this README as the full,
implementer-ready plan. Key design decisions, confirmed with the requester: (1) the
generic `delete` tool covers the eleven whole-body domains and excludes ADR; (2) `feat`
hard-deletes its entire `<base>/<id>/` folder; (3) the tool returns the deleted path as
a `str`; and (4) the path/file injection-prevention logic lives in a new **reusable**
module `general/tools/_path_safety.py` so the `get`/`update`/`set_status` tools can
adopt it later with zero rework (they are not modified in this feature). No
implementation code has been written; Phases 1–5 are delegated to the Phase-Orchestrator.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31 15:37:40.000Z — ADR excluded from the generic delete tool

The generic `delete` covers only the eleven whole-body domains (`req`/`uc`/`tsk`/`qa`/
`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr`), not ADR. Rationale: ADR has never had a
`delete_adr` stub, it is treated specially (render round-trip, schema under shared
`models/adr/`), and hard-deleting an ADR could break other ADRs' "superseded by X"
cross-references. This mirrors the `update` tool's precedent of excluding ADR.

#### 2026-08-31 15:37:40.000Z — Injection prevention is a reusable, non-I/O module

The path/file validation that prevents injection is implemented in
`general/tools/_path_safety.py` as pure functions (string/`Path` inspection only, no
filesystem mutation), deliberately separate from the delete-specific `DeleteError` and
from `_doc_paths.py`. This makes it directly reusable by the `get_<d>`, `update`, and
`set_status` tools in a future change without rework, per the requester's requirement.
`delete` is the only tool wired to it in this feature.

#### 2026-08-31 15:37:40.000Z — `feat` deletes its whole folder; the tool returns the deleted path

Because `feat` is folder-per-document (ADR 8cf940c5), its adapter removes the entire
`<base>/<id>/` folder via `shutil.rmtree` (including any `history.md`/session files),
while the ten flat domains remove their single `*.md` file via `Path.unlink()`. The
public `delete` tool returns the deleted path as a `str` (file path for the flat
domains, folder path for `feat`).
