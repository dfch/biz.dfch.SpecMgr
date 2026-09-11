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

"""Requirement base directory resolution and id -> path lookup (Task 3.11).

A thin, requirement-specific layer over the generic
``general.tools._doc_paths`` module (Task 3.10), rather than a second
hand-written copy of ``adr.tools._paths`` -- the base-directory/id-lookup
plumbing is identical in shape, only the parsed document type and its id
accessor differ.

Mirrors ``adr.tools._paths``'s read-only/write split: :func:`req_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_req_base_dir` does, for the eventual
``create_req`` tool (Task 3.12).

**Cache-backed scan (feat-107-doc-cache Phase 3).** :func:`find_req_path`
now scans through the content-hash-validated per-domain cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s own
``read_req`` (not ``parse_req``) as ``find_doc_path_by_id``'s ``read_fn``,
so a file whose on-disk content hash is unchanged since its last read is
not re-parsed, and it passes ``._cache``'s ``reconcile_req_cache`` as
``reconcile_fn`` so an orphaned cache entry (a file deleted outside
specmgr's own tooling) is dropped before any per-file work on every scan.
``read_req``/``reconcile_req_cache`` are imported from ``._cache``, not
``._io``, to avoid a circular import -- see ``._cache``'s own module
docstring for the full rationale. The filesystem remains the sole source
of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache entry is only
ever a memoization keyed by validated content hash, never an independent
fact about what exists on disk.
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
from ..models.v1 import ReqDocument
from ._cache import read_req, reconcile_req_cache

__all__ = [
    "REQ_TYPE_NAME",
    "ReqNotFoundError",
    "ensure_req_base_dir",
    "find_req_path",
    "iter_req_paths",
    "req_base_dir",
]

#: The doc-type subdirectory name passed to ``general.tools._doc_paths``
#: (``{docs root}/req/``, e.g. ``docs/req``).
REQ_TYPE_NAME = "req"


class ReqNotFoundError(LookupError):
    """No requirement file found matching the given id.

    A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
    a subclass of it -- the same relationship ``adr.tools._paths.AdrNotFoundError``
    has to nothing generic, so callers can keep catching a requirement-specific
    exception type without depending on the generic module's own exception.
    """


def req_base_dir() -> Path:
    """Return the configured requirement base directory, without creating it.

    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(REQ_TYPE_NAME)``
    -- see that function's own docstring for the env var/default it reads.

    Returns
    -------
    Path
        The resolved requirement base directory.
    """
    result = doc_base_dir(REQ_TYPE_NAME)
    return result


def ensure_req_base_dir() -> Path:
    """Return the configured requirement base directory, creating it if missing.

    Only ``create_req`` (Task 3.12) should call this -- every other
    tool/resource uses the read-only :func:`req_base_dir` instead.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist requirement base directory.
    """
    result = ensure_doc_base_dir(REQ_TYPE_NAME)
    return result


def iter_req_paths() -> Iterator[Path]:
    """Yield every requirement ``*.md`` file under :func:`req_base_dir`, sorted by name.

    Yields nothing (rather than raising) if the base directory does not exist.

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    result = iter_doc_paths(req_base_dir())
    return result


def _get_req_id(doc: ReqDocument) -> str | None:
    """Extract the id from a parsed :class:`ReqDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
    result = doc.frontmatter.id
    return result


def find_req_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path under ``base_dir``.

    Scans every ``*.md`` file under ``base_dir``, reading each through the
    cache-backed :func:`~._cache.read_req` (feat-107-doc-cache Phase 3) and
    comparing ``frontmatter.id`` against ``id_`` -- a file whose on-disk
    content hash is unchanged since its last read is not re-parsed. A file
    that fails to parse (``AssertionError``/``pydantic.ValidationError``) is
    silently skipped -- one broken file must not prevent lookup of a
    different, valid id. Mirrors ``adr.tools._paths.find_adr_path``'s own
    skip-on-parse-failure rule. Before scanning, the cache is reconciled
    against the freshly materialized live path listing
    (:func:`~._cache.reconcile_req_cache`), dropping any cached entry for a
    file deleted outside specmgr's own tooling (REQ-005).

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
    ReqNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    try:
        result = find_doc_path_by_id(base_dir, id_, read_req, _get_req_id, reconcile_fn=reconcile_req_cache)
    except DocNotFoundError as ex:
        raise ReqNotFoundError(
            f"no requirement found with id {id_!r}. The id must be the bare document UUID, without a domain "
            f"prefix (use '<uuid>', not 'req-<uuid>')."
        ) from ex
    return result
