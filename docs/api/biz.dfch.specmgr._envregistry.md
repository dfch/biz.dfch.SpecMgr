# `biz.dfch.specmgr._envregistry`

Central, stdlib-only environment-variable registry (feat-208).

Every environment variable this package reads is registered here by its
owning domain/feature with its name, default (or a presence-based
marker), description, and owner, making this module the single source of
truth for env-var names and defaults. The registry-backed completeness
and documentation-coverage tests (feat-208 Phase 150/160) check against
it, and every read site in ``src/`` (except the import-free ``plantuml/``
package, see the feature plan's Design Notes) goes through ``get``/
``get_with_default`` below.

Placement and import constraints (feat-208, Design Notes "Registry
placement"): this module is top-level, a sibling of ``_paths.py``, and
imports nothing beyond the standard library (``os``, ``dataclasses``).
``cli.py`` and ``commands/mcp.py`` import it at module level (import-time
registration of their own vars, Typer option defaults sourced from it)
in a ``[cli]``-only install where the ``mcp`` extra is absent, so its
import chain must never reach ``server``/the third-party ``mcp`` package
-- which is exactly what the originally drafted ``general/tools/`` home
would do (that package's ``__init__.py`` eagerly imports every
``@mcp.tool()`` module). The top-level ``__init__.py`` carries no imports
of its own, so this module's import chain is just itself.
``tests/test_envregistry.py`` pins the stdlib-only import graph with an
AST walk (mirroring ``plantuml/``'s import-free pin in
``tests/plantuml/test_structure.py``).

Registration happens at import time of each owning module (feat-208
Phase 110), so the registry is complete by the time any server/CLI
entry point runs; the read sites migrate onto ``get``/
``get_with_default`` in Phase 120-140. The environment is always read
at call time (``get``/``get_with_default``), never at registration
time.

## Classes

### `EnvVar`

One registered environment variable (feat-208, Phase 100).

Attributes:
    name: The environment variable name (e.g. ``SPECMGR_ADR_DIR``).
    default: The value to insert when the variable is unset, or
        ``None`` for a presence-based variable that carries no default.
    description: Non-empty, human-readable purpose of the variable.
    owner: The registering domain/feature (e.g. ``adr``, ``general``).
    format: The ``server.json`` manifest ``format`` for the variable
        (e.g. ``number``/``filepath``), or ``None`` when the manifest
        carries none.
    choices: The ``server.json`` manifest ``choices`` for the variable
        (empty when the manifest carries none).
    empty_falls_back_to_default: Whether a set-but-empty value falls
        back to ``default`` -- ``True`` for the four empty-or-unset-to-
        default read sites (``SPECMGR_ADR_DIR``, ``SPECMGR_DOCS_DIR``,
        ``SPECMGR_FEAT_DIR`` -- whose read code is
        ``Path(value) if value else DEFAULT`` -- and
        ``FASTEMBED_CACHE_PATH``, whose read code is
        ``value or default``); ``False`` for every other variable
        (set-but-empty stays set there). The four-variable set is the
        user-approved Option A decision recorded in the feat-208 plan
        (2026-10-10 update entry), which supersedes the plan's original
        single-variable wording.


## Functions

### `_conflict_detail(stored: 'EnvVar', entry: 'EnvVar') -> 'str'`

Render the field-level diff of two conflicting records (feat-208, Phase 100).


### `_entry_or_fail(name: 'str') -> 'EnvVar'`

Return the stored record for ``name``, failing loudly when absent (feat-208, Phase 100).


### `all_vars() -> 'tuple[EnvVar, ...]'`

Return every registered record in registration order (feat-208, Phase 100).

The read surface for the registry-backed completeness and
documentation-coverage tests (feat-208 Phase 150/160).

Returns:
    A snapshot tuple of the current registry contents.


### `get(name: 'str') -> 'str | None'`

Read one registered variable raw from the process environment (feat-208, Phase 100).

The environment is read at call time; no default is inserted. This is
the accessor for presence-based variables (``default is None``), which
must be able to distinguish "unset" (``None``) from "set".

Args:
    name: A registered environment variable name.

Returns:
    The variable's current environment value, or ``None`` when unset.


### `get_with_default(name: 'str') -> 'str'`

Read one registered variable with its default inserted (feat-208, Phase 100).

The environment is read at call time: a set value (including a
set-but-empty one) is returned as-is, except that a set-but-empty
value falls back to the registered default when the entry's
``empty_falls_back_to_default`` flag is set -- the four empty-fallback
variables (``SPECMGR_ADR_DIR``, ``SPECMGR_DOCS_DIR``,
``SPECMGR_FEAT_DIR``, ``FASTEMBED_CACHE_PATH``; the user-approved
Option A decision, feat-208 Phase 110). An unset variable yields the
registered default.

Args:
    name: A registered environment variable name carrying a default.

Returns:
    The variable's current environment value, or its registered
    default when the value is absent (or empty with the flag set).


### `register(name: 'str', *, default: 'str | None' = None, description: 'str', owner: 'str', format: 'str | None' = None, choices: 'tuple[str, ...]' = (), empty_falls_back_to_default: 'bool' = False) -> 'EnvVar'`

Register one environment variable (feat-208, Phase 100).

Idempotent for identical metadata: re-registering the same ``name``
with identical values returns the stored record. Re-registering the
same ``name`` with conflicting metadata fails loudly, naming the
variable and every conflicting field.

Args:
    name: The environment variable name.
    default: The value to insert when the variable is unset, or
        ``None`` for a presence-based variable.
    description: Non-empty, human-readable purpose of the variable.
    owner: The registering domain/feature.
    format: The ``server.json`` manifest ``format`` for the variable, if any.
    choices: The ``server.json`` manifest ``choices`` for the variable, if any.
    empty_falls_back_to_default: Whether a set-but-empty value falls
        back to ``default``.

Returns:
    The stored record for ``name``.

