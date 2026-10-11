# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Central, stdlib-only environment-variable registry (feat-208).

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
"""

from __future__ import annotations

import os
from dataclasses import dataclass

__all__ = ["EnvVar", "all_vars", "get", "get_with_default", "register"]


@dataclass(frozen=True, slots=True)
class EnvVar:
    """One registered environment variable (feat-208, Phase 100).

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
    """

    name: str
    default: str | None
    description: str
    owner: str
    format: str | None = None
    choices: tuple[str, ...] = ()
    empty_falls_back_to_default: bool = False

    def __post_init__(self) -> None:
        """Validate the record's own invariants (feat-208, Phase 100)."""
        assert self.name, "EnvVar.name must be a non-empty string"
        assert self.description.strip(), f"EnvVar.description for {self.name!r} must be non-empty"
        assert self.owner, f"EnvVar.owner for {self.name!r} must be a non-empty string"
        assert not self.empty_falls_back_to_default or self.default is not None, (
            f"EnvVar.empty_falls_back_to_default for {self.name!r} requires a non-None default"
        )


#: The registry itself: env-var name -> record. Registration happens at
#: import time of each owning module (feat-208 Phase 110+), so this grows
#: as the process imports more of the package; reads always go through
#: ``get``/``get_with_default`` (or ``all_vars`` for the full snapshot).
_REGISTRY: dict[str, EnvVar] = {}


def register(
    name: str,
    *,
    default: str | None = None,
    description: str,
    owner: str,
    format: str | None = None,
    choices: tuple[str, ...] = (),
    empty_falls_back_to_default: bool = False,
) -> EnvVar:
    """Register one environment variable (feat-208, Phase 100).

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
    """
    entry = EnvVar(
        name=name,
        default=default,
        description=description,
        owner=owner,
        format=format,
        choices=choices,
        empty_falls_back_to_default=empty_falls_back_to_default,
    )
    stored = _REGISTRY.get(name)
    if stored is not None:
        assert stored == entry, (
            f"conflicting re-registration of environment variable {name!r} (stored owner "
            f"{stored.owner!r}); conflicting fields:\n{_conflict_detail(stored, entry)}"
        )
        result = stored
        return result
    _REGISTRY[name] = entry
    result = entry
    return result


def _conflict_detail(stored: EnvVar, entry: EnvVar) -> str:
    """Render the field-level diff of two conflicting records (feat-208, Phase 100)."""
    pairs: list[tuple[str, object, object]] = [
        ("default", stored.default, entry.default),
        ("description", stored.description, entry.description),
        ("owner", stored.owner, entry.owner),
        ("format", stored.format, entry.format),
        ("choices", stored.choices, entry.choices),
        ("empty_falls_back_to_default", stored.empty_falls_back_to_default, entry.empty_falls_back_to_default),
    ]
    result = "\n".join(f"  {field}: stored {old!r}, new {new!r}" for field, old, new in pairs if old != new)
    return result


def _entry_or_fail(name: str) -> EnvVar:
    """Return the stored record for ``name``, failing loudly when absent (feat-208, Phase 100)."""
    entry = _REGISTRY.get(name)
    assert entry is not None, f"unknown environment variable {name!r}: it is not registered"
    result = entry
    return result


def get(name: str) -> str | None:
    """Read one registered variable raw from the process environment (feat-208, Phase 100).

    The environment is read at call time; no default is inserted. This is
    the accessor for presence-based variables (``default is None``), which
    must be able to distinguish "unset" (``None``) from "set".

    Args:
        name: A registered environment variable name.

    Returns:
        The variable's current environment value, or ``None`` when unset.
    """
    entry = _entry_or_fail(name)
    result = os.environ.get(entry.name)
    return result


def get_with_default(name: str) -> str:
    """Read one registered variable with its default inserted (feat-208, Phase 100).

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
    """
    entry = _entry_or_fail(name)
    value = os.environ.get(entry.name)
    if value is None:
        assert entry.default is not None, (
            f"{name!r} is registered as presence-based (no default) and is unset: read it via get(), "
            "which returns None for the unset case, not get_with_default()"
        )
        result = entry.default
    elif value == "" and entry.empty_falls_back_to_default:
        # ``empty_falls_back_to_default`` requires a non-None default
        # (``EnvVar.__post_init__``), so this assert never fires; it exists
        # to narrow the type for static checkers.
        assert entry.default is not None, (
            f"{name!r} has empty_falls_back_to_default set but no default (invalid record -- see EnvVar.__post_init__)"
        )
        result = entry.default
    else:
        result = value
    return result


def all_vars() -> tuple[EnvVar, ...]:
    """Return every registered record in registration order (feat-208, Phase 100).

    The read surface for the registry-backed completeness and
    documentation-coverage tests (feat-208 Phase 150/160).

    Returns:
        A snapshot tuple of the current registry contents.
    """
    result = tuple(_REGISTRY.values())
    return result
