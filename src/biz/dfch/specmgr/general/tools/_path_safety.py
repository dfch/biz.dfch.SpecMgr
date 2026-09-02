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

"""Reusable, doc-type-agnostic path-safety assertions for document ids and
resolved paths (feat-36-delete, Phase 1).

Prevents path injection through a generic, type-dispatched document
tool's ``type``/``id`` inputs and confines a resolved path to the domain's
own base directory. A private, cross-domain helper in the same package
and in the same style as :mod:`_doc_paths`, :mod:`_splice`, and
:mod:`_paging`: it has **no** ``mcp`` dependency and performs **no
filesystem mutation** -- the functions only inspect ``str`` and
:class:`~pathlib.Path` values and raise :class:`ValueError` on failure,
naming the offending value. (:func:`assert_within`'s read-only
``Path.resolve()`` calls are the module's single, sanctioned filesystem
touch.)

The generic ``delete`` tool (``.specmgr/feat/feat-36-delete/README.md``,
Design Notes sections 2-6) was the first caller. The five functions are
now also called by the thirteen ``get_<d>`` tools (including ``get_adr``,
and ``get_sysrs`` since feat-32-sysrs Phase 3)
and by the generic ``update`` and ``set_status`` tools
(``.specmgr/feat/feat-38-39-41-43-44/README.md``, Phase 4, REQ-009): they
take only plain ``str``/``Path`` inputs, return ``None`` (raise on
failure), and carry no delete-specific state, argument, or return value --
in particular the delete-specific ``DeleteError`` wrapper (REQ-005)
deliberately lives in ``delete.py``, not here, because it is a
delete-specific concern, not a reusable safety primitive.
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "assert_feat_id",
    "assert_no_traversal",
    "assert_uuid",
    "assert_within",
    "validate_id",
]

#: The twelve UUID domains whose ``id`` is a server-generated v4 UUID: the
#: eleven whole-body domains plus ``adr`` (feat-38-39-41-43-44 Phase 4,
#: REQ-009; ``sysrs`` added feat-32-sysrs Phase 3) -- ADR ids are canonical
#: lowercase-hex UUIDs of the exact same
#: shape (see ``adr.tools._paths.find_adr_path``/any ``docs/adr/*.md``
#: frontmatter ``id`` value). ``delete``'s own ``Literal`` type still
#: excludes ``"adr"`` (its behavior is unchanged, D-Phase-4) -- this
#: addition is purely for use by ``get_<d>``/``update``/``set_status``.
_UUID_TYPES = frozenset({"req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs", "adr"})

#: The ``feat`` document type: the one whole-body domain whose ``id`` is a
#: chosen ``feat-NNN-slug`` folder name, not a server-generated UUID.
_TYPE_FEAT = "feat"

#: Canonical 8-4-4-4-12 lowercase-hex UUID shape (the form ``uuid.uuid4().str`` produces,
#: which is what every ``create_<d>`` tool writes into the frontmatter ``id``).
_UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

#: The ``feat`` folder-name shape (ADR 8cf940c5): ``feat-NNN-slug``, lowercase alnum + hyphen.
_FEAT_ID_PATTERN = re.compile(r"^feat-[0-9]+-[a-z0-9-]+$")

#: The path-separator characters an id must never contain.
_PATH_SEPARATORS = ("/", "\\")

#: The relative-parent traversal sequence an id must never contain.
_TRAVERSAL_SEQUENCE = ".."


def assert_no_traversal(id_: str) -> None:
    """Reject any id that could contribute a relative path.

    Universal guard, independent of domain: the value must be a non-empty
    ``str`` and must contain no ``/``, no ``\\``, and no ``..``. This alone
    makes it impossible for the id to escape its base directory when joined
    into a path.

    Parameters
    ----------
    id_:
        The id to check.

    Raises
    ------
    ValueError
        The value is empty (or whitespace-only), or it contains a path
        separator (``/`` or ``\\``) or the ``..`` traversal sequence; the
        message names the offending value.
    """
    assert isinstance(id_, str), type(id_)

    if not id_.strip():
        raise ValueError(f"id {id_!r} is empty; a non-empty id is required")
    if _TRAVERSAL_SEQUENCE in id_ or any(separator in id_ for separator in _PATH_SEPARATORS):
        raise ValueError(f"id {id_!r} contains a path separator or a '..' traversal sequence; a bare id is expected")


def assert_uuid(id_: str) -> None:
    """Reject any id that is not a canonical lowercase-hex v4-shaped UUID.

    Enforced for the ten :data:`_UUID_TYPES` domains. (Subsumes
    :func:`assert_no_traversal` for well-formed input, but both are applied
    so the error message is precise.)

    Parameters
    ----------
    id_:
        The id to check.

    Raises
    ------
    ValueError
        The value does not match the canonical 8-4-4-4-12 lowercase-hex
        UUID shape; the message names the offending value.
    """
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    if not _UUID_PATTERN.match(id_):
        raise ValueError(
            f"id {id_!r} is not a canonical lowercase-hex UUID (8-4-4-4-12); a server-generated UUID is expected"
        )


def assert_feat_id(id_: str) -> None:
    """Reject any id that is not a well-formed ``feat-NNN-slug`` folder name.

    Enforced for the ``feat`` domain (folder-per-document, ADR 8cf940c5):
    ``feat-``, one or more digits, ``-``, then a non-empty run of lowercase
    alnum and hyphen.

    Parameters
    ----------
    id_:
        The id to check.

    Raises
    ------
    ValueError
        The value does not match the ``feat-NNN-slug`` shape; the message
        names the offending value.
    """
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    if not _FEAT_ID_PATTERN.match(id_):
        raise ValueError(f"id {id_!r} is not a well-formed feat-NNN-slug folder name (e.g. 'feat-36-delete')")


def validate_id(type_: str, id_: str) -> None:
    """Convenience dispatcher: :func:`assert_no_traversal` plus the type's format check.

    ``type_`` in :data:`_UUID_TYPES` -> :func:`assert_uuid`;
    ``type_ == "feat"`` -> :func:`assert_feat_id`; any other ``type_`` ->
    ``ValueError`` (unknown type). This is the single entry point the
    generic ``delete``, ``update``, ``set_status``, and every ``get_<d>``
    tool (including ``get_adr``) call before any filesystem access.

    Parameters
    ----------
    type_:
        The document type name: one of the thirteen document types (the
        twelve whole-body domains, or ``adr``).
    id_:
        The id to check.

    Raises
    ------
    ValueError
        ``type_`` is not one of the thirteen document type names, or the
        id fails :func:`assert_no_traversal` or the type's own format
        check; the message names the offending value.
    """
    assert isinstance(type_, str), type(type_)
    assert type_.strip()
    assert isinstance(id_, str), type(id_)

    assert_no_traversal(id_)
    if type_ in _UUID_TYPES:
        assert_uuid(id_)
    elif type_ == _TYPE_FEAT:
        assert_feat_id(id_)
    else:
        raise ValueError(
            f"unknown document type {type_!r}; expected 'feat' or one of the twelve UUID domains "
            f"(req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/adr)"
        )


def assert_within(base_dir: Path, candidate: Path) -> None:
    """Defense-in-depth: ``candidate.resolve()`` must be ``is_relative_to(base_dir.resolve())``.

    Type-agnostic. Called by the adapters *after* id -> path resolution,
    so that even if a future id-validation gap existed, a resolved path
    could never point outside the domain's own base directory.

    Parameters
    ----------
    base_dir:
        The domain's own base directory.
    candidate:
        The resolved candidate path to check.

    Raises
    ------
    ValueError
        ``candidate``, once resolved, lies outside ``base_dir`` once
        resolved; the message names both paths.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(candidate, Path), type(candidate)

    if not candidate.resolve().is_relative_to(base_dir.resolve()):
        raise ValueError(f"path {candidate!r} resolves outside base directory {base_dir!r}")
