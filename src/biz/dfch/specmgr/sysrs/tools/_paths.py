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

"""System Requirements Specification (SYSRS) base directory resolution and id -> path lookup (Task 3.1).

A thin, SYSRS-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``vcr.tools._paths``/``sop.tools._paths`` file-for-file.

Mirrors ``gol.tools._paths``'s read-only/write split: :func:`sysrs_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_sysrs_base_dir` does, for ``create_sysrs``. There
is deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ...general.tools._doc_paths import (
    DocNotFoundError,
    doc_base_dir,
    ensure_doc_base_dir,
    find_doc_path_by_id,
    iter_doc_paths,
)
from ..models.v1 import SysrsDocument, parse_sysrs

__all__ = [
    "SYSRS_TYPE_NAME",
    "SysrsNotFoundError",
    "sysrs_base_dir",
    "ensure_sysrs_base_dir",
    "find_sysrs_path",
    "iter_sysrs_paths",
]

#: The doc-type subdirectory name passed to ``general.tools._doc_paths``
#: (``{docs root}/sysrs/``, e.g. ``docs/sysrs``).
SYSRS_TYPE_NAME = "sysrs"


class SysrsNotFoundError(LookupError):
    """No System Requirements Specification file found matching the given id.

    A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
    a subclass of it -- the same relationship ``gol.tools._paths.GolNotFoundError``
    has to nothing generic, so callers can keep catching a SYSRS-specific
    exception type without depending on the generic module's own exception.
    """


def sysrs_base_dir() -> Path:
    """Return the configured System Requirements Specification base directory, without creating it.

    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(SYSRS_TYPE_NAME)``
    -- see that function's own docstring for the env var/default it reads.

    Returns
    -------
    Path
        The resolved System Requirements Specification base directory.
    """
    result = doc_base_dir(SYSRS_TYPE_NAME)
    return result


def ensure_sysrs_base_dir() -> Path:
    """Return the configured System Requirements Specification base directory, creating it if missing.

    Only ``create_sysrs`` should call this -- every other tool/resource uses
    the read-only :func:`sysrs_base_dir` instead.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist System Requirements Specification base directory.
    """
    result = ensure_doc_base_dir(SYSRS_TYPE_NAME)
    return result


def iter_sysrs_paths() -> Iterator[Path]:
    """Yield every System Requirements Specification ``*.md`` file under :func:`sysrs_base_dir`, sorted by name.

    Yields nothing (rather than raising) if the base directory does not exist.

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    result = iter_doc_paths(sysrs_base_dir())
    return result


def _get_sysrs_id(doc: SysrsDocument) -> str | None:
    """Extract the id from a parsed :class:`SysrsDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
    result = doc.frontmatter.id
    return result


def find_sysrs_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path under ``base_dir``.

    Scans every ``*.md`` file under ``base_dir``, parsing each via
    :func:`~biz.dfch.specmgr.sysrs.models.v1.parse_sysrs` and comparing
    ``frontmatter.id`` against ``id_``. A file that fails to parse
    (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
    one broken file must not prevent lookup of a different, valid id.
    Mirrors ``gol.tools._paths.find_gol_path``'s own skip-on-parse-failure
    rule.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    Path
        The resolved file path.

    Raises
    ------
    SysrsNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    try:
        result = find_doc_path_by_id(base_dir, id_, parse_sysrs, _get_sysrs_id)
    except DocNotFoundError as ex:
        raise SysrsNotFoundError(
            f"no System Requirements Specification found with id {id_!r}. The id must be the bare document "
            f"UUID, without a domain prefix (use '<uuid>', not 'sysrs-<uuid>')."
        ) from ex
    return result
