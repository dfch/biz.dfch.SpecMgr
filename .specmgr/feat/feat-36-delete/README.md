---
created: 2026-08-31 15:37:40.000000
id: feat-36-delete
status: planning
type: feat
updated: 2026-08-31 18:28:48.000000
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

- [ ] ACC-001: Verifies REQ-001 — `general/tools/delete.py` exists and registers `@mcp.tool(name="delete")` with the eleven-value `type` Literal; it dispatches through an `_ADAPTERS` table to eleven private `_delete_<d>` adapters; a live call `delete(id, type)` on a seeded document removes it and returns the deleted path as a `str`; `docs/MCP.md` (regenerated) lists exactly one `delete` tool and no `delete_<d>` tools.
- [ ] ACC-002: Verifies REQ-002 — the eleven `delete_<d>.py` source files, their `__init__.py` imports/`__all__`/docstring references, and the eleven `test_delete_<d>.py` files are all gone (`git status`/`grep -r "delete_<d>"` over `src/` and `tests/` returns nothing for a per-domain delete tool); `import biz.dfch.specmgr.<d>.tools` succeeds for every domain.
- [ ] ACC-003: Verifies REQ-003 — `general/tools/_path_safety.py` exposes `assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, and `assert_within`; `tests/general/tools/test__path_safety.py` passes; the functions are pure (no filesystem side effects) and importable by `get_<d>`/`update`/`set_status` without modification (i.e. no delete-specific coupling).
- [ ] ACC-004: Verifies REQ-004 — each of the eleven adapters acquires its domain's `<d>_lock(id_)` around the resolve-then-delete sequence (verified by a test that mocks/spies the lock, or a concurrency test showing a same-id `update` and `delete` do not interleave).
- [ ] ACC-005: Verifies REQ-005 — for a seeded document, `delete` with an unknown id raises that domain's `XNotFoundError`; with an injected id (`../x`, `a/b`, `a\b`, `..`, a non-UUID string for a UUID type, a non-`feat-NNN-slug` for `feat`) it raises `ValueError` and leaves the filesystem untouched; with a mocked `unlink`/`rmtree` that raises `OSError` it raises `DeleteError` whose message names the path.
- [ ] ACC-006: Verifies REQ-006 — for the ten flat domains the `*.md` file is removed and its directory is left intact; for `feat` the whole `<base>/<id>/` folder (including a seeded `history.md`) is removed.
- [ ] ACC-007: Verifies REQ-007 — a new accepted ADR exists in `docs/adr/` (listed in the regenerated `docs/adr/README.md`); `AGENTS.md`, `server.py`'s docstring, and `CHANGELOG.md` are updated per REQ-007; `specmgr docs`/`specmgr mcp-docs`/`specmgr adr-toc` all run clean (no drift) after the edits.
- [ ] ACC-008: Verifies REQ-008 — `tests/general/tools/test_delete.py` and `tests/general/tools/test__path_safety.py` exist and pass; the full `unittest` suite is green; `ruff format --check`, `ruff check`, and `vulture` are clean.

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

- [ ] Task 1.1: Add `general/tools/_path_safety.py` exactly per Design Notes §1 (`assert_no_traversal`, `assert_uuid`, `assert_feat_id`, `validate_id`, `assert_within`; `ValueError` on failure; no I/O) — depends on: Task 0.2 — status: not-started.
- [ ] Task 1.2: Add `tests/general/tools/test__path_safety.py` per Design Notes §9 — depends on: Task 1.1 — status: not-started.

#### Phase 2: The generic delete tool (Phase-Orchestrator)

- [ ] Task 2.1: Add `general/tools/delete.py` per Design Notes §2–§6 (`DeleteError`, eleven `_delete_<d>` adapters, `_ADAPTERS`, `@mcp.tool(name="delete")` public function calling `validate_id` then dispatching) and register it in `general/tools/__init__.py` (`from .delete import delete`, the `__all__` entry, and a sentence in the module docstring — the server registers tools purely via this package's import side effect) — depends on: Task 1.1 — status: not-started.
- [ ] Task 2.2: Add `tests/general/tools/test_delete.py` per Design Notes §9 — depends on: Task 2.1 — status: not-started.

#### Phase 3: Retire the eleven delete stubs (Phase-Orchestrator)

- [ ] Task 3.1: Delete the eleven `src/biz/dfch/specmgr/<d>/tools/delete_<d>.py` files — depends on: Task 2.1 — status: not-started.
- [ ] Task 3.2: In each of the eleven `<d>/tools/__init__.py`, remove the `from .delete_<d> import delete_<d>` line, the `delete_<d>` `__all__` entry, and the stub mention in the module docstring; **additionally** in each of the eleven domain-level `<d>/__init__.py` package docstrings, drop `delete_<d>` from the tool enumeration (required by ACC-002: `grep -r "delete_<d>"` over all of `src/` must return nothing) — depends on: Task 3.1 — status: not-started.
- [ ] Task 3.3: Delete the eleven `tests/<d>/tools/test_delete_<d>.py` stub-test files — depends on: Task 3.2 — status: not-started.

#### Phase 4: Decision and documentation propagation (Phase-Orchestrator)

- [ ] Task 4.1: Create the new ADR via the `create_adr` MCP tool per Design Notes §7 (requester-confirmed: the enabled specmgr MCP server resolves `docs/adr` relative to its CWD, i.e. this worktree — sanity-check with `git status` right after creation), set it `accepted`, run `specmgr adr-toc`, and ensure the new ADR file plus the regenerated `docs/adr/README.md` are `git add`ed into the Phase 4 commit — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.2: Update `AGENTS.md` per Design Notes §8 — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.3: Update `server.py`'s module docstring per Design Notes §8 — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.4: Add the `CHANGELOG.md` `[Unreleased]` entry per Design Notes §8 — depends on: Task 3.3 — status: not-started.
- [ ] Task 4.5: Regenerate `docs/` (`specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`), each run twice to confirm no drift — depends on: Tasks 4.1–4.4 — status: not-started.

#### Phase 5: Quality gate and sign-off (Phase-Orchestrator)

- [ ] Task 5.1: Run the full gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, the full `unittest` suite, and advisory `pylint`) and fix any failures — depends on: Task 4.5 — status: not-started.
- [ ] Task 5.2: Walk ACC-001..ACC-008, mark each `[x]` with a concrete justification (test file / tool / doc proving it), update Current Status, and bump this README's frontmatter `status`/`updated` — depends on: Task 5.1 — status: not-started.

## Progress

### Current Status

**As of 2026-08-31 (session handover)**: Design complete (Phase 0, including
Task 0.3). The `feat-36-delete` worktree/branch was cut from `dev` and this README
captures the full, implementer-ready design: the generic `delete` tool, the reusable
`_path_safety` module, the eleven stub removals, the locking/error contract, the new
ADR, and the documentation propagation. No feature source code has been written yet —
implementation (Phases 1–5) is delegated to the Phase-Orchestrator in a **fresh
session**; see the handover entry in Updates below for the agreed execution model,
commit policy, plan refinements, and environment caveats. Baseline is green: full
`unittest` suite OK (2704 tests), `ruff format --check` / `ruff check` / `vulture`
all clean.

### Blockers

- None currently.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-08-31 18:28:48.000Z — Session handover: Phase 0 complete, Phase 1 ready for a fresh session

The design session ended with Phase 0 complete. Implementation of Phases 1–5 resumes
in a **fresh session**, orchestrated from this README.

**Execution model (agreed with the requester):**

- Phase-by-phase: the main agent acts as Phase-Orchestrator and launches the
  `phase-implementer` subagent **once per phase** (1, then 2, …, 5). Each
  subagent implements its phase end-to-end (code, tests, phase-end quality gate,
  task-line status updates in this README) and reports back; the orchestrator
  verifies the gate results and commits before starting the next phase.
- Commit policy: **one commit per phase** on `feat-36-delete`. The orchestrator
  commits without asking for permission but does **NOT push**. The orchestrator
  stops and asks only when it needs a user decision or hits a wall.
- ADR (Task 4.1): the enabled specmgr MCP server (`uvx biz-dfch-specmgr[mcp]`)
  resolves `docs/adr` relative to its CWD — the requester confirmed `create_adr`
  lands the file in this worktree. The new ADR file must be committed together
  with the other Phase 4 files. Do NOT enable the disabled `specmgr-test` MCP
  server (it points at the main repo). Do NOT run `git pull` on this branch
  (no upstream tracking is set).

**Plan refinements agreed this session** (folded into the Task List above):

- Task 2.1 additionally registers `delete` in `general/tools/__init__.py`
  (import / `__all__` / docstring) — without it the tool would silently never
  register.
- Task 3.2 additionally drops `delete_<d>` from the eleven domain-level
  `<d>/__init__.py` package docstrings — otherwise ACC-002's grep-over-`src/`
  criterion would fail.

**Repo state at handover:**

- Worktree `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-36-delete`, branch
  `feat-36-delete`, working tree clean; tip is the Task 0.3 debug-print cleanup
  commit.
- Main repo on `dev` (`/home/user/src/biz.dfch.SpecMgr`) carries the byte-exact
  same cleanup commit (`9eb7e8a`); the maintainer pushes `dev`.
- Baseline verified green: full `unittest` suite (2704 tests, OK, noise-free
  output), `ruff format --check` (1487 files), `ruff check`, and `vulture` all
  clean.
- Pre-commit hooks are active in both checkouts. Known UX: when a hook (e.g.
  `ruff-format`) modifies a staged file, the first commit attempt fails with
  "Files were modified by this hook" — re-`git add` the file and commit again.
  The `unittest` hook (full suite, ~2 min) and `specmgr-coverage-badge` run on
  any `src`/`tests` change; the `specmgr docs`/`mcp-docs`/`adr-toc`/`schema`
  hooks are scoped to `src/` / `docs/adr` changes and will fire on the Phase
  3/4 commits.

**Next action:** launch `phase-implementer` for **Phase 1** (Tasks 1.1–1.2).

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
