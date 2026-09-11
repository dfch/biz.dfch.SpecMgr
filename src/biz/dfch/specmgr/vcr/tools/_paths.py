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

"""Verification case record base directory resolution and id -> path lookup (Task 2.1).

A thin, VCR-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``dec.tools._paths`` file-for-file.

Mirrors ``gol.tools._paths``'s read-only/write split: :func:`vcr_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_vcr_base_dir` does, for ``create_vcr``.

**Cache-backed scan (feat-107-doc-cache Phase 4).** :func:`find_vcr_path`
now scans through the content-hash-validated per-domain cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s own
``read_vcr`` (not ``parse_vcr``) as ``find_doc_path_by_id``'s ``read_fn``,
so a file whose on-disk content hash is unchanged since its last read is
not re-parsed, and it passes ``._cache``'s ``reconcile_vcr_cache`` as
``reconcile_fn`` so an orphaned cache entry (a file deleted outside
specmgr's own tooling) is dropped before any per-file work on every scan.
``read_vcr``/``reconcile_vcr_cache`` are imported from ``._cache``, not
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
from ..models.v1 import VcrDocument
from ._cache import read_vcr, reconcile_vcr_cache

__all__ = [
    "VCR_TYPE_NAME",
    "VcrNotFoundError",
    "vcr_base_dir",
    "ensure_vcr_base_dir",
    "find_vcr_path",
    "iter_vcr_paths",
]

#: The doc-type subdirectory name passed to ``general.tools._doc_paths``
#: (``{docs root}/vcr/``, e.g. ``docs/vcr``).
VCR_TYPE_NAME = "vcr"


class VcrNotFoundError(LookupError):
    """No verification case record file found matching the given id.

    A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
    a subclass of it -- the same relationship ``gol.tools._paths.GolNotFoundError``
    has to nothing generic, so callers can keep catching a VCR-specific
    exception type without depending on the generic module's own exception.
    """


def vcr_base_dir() -> Path:
    """Return the configured verification case record base directory, without creating it.

    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(VCR_TYPE_NAME)``
    -- see that function's own docstring for the env var/default it reads.

    Returns
    -------
    Path
        The resolved verification case record base directory.
    """
    result = doc_base_dir(VCR_TYPE_NAME)
    return result


def ensure_vcr_base_dir() -> Path:
    """Return the configured verification case record base directory, creating it if missing.

    Only ``create_vcr`` should call this -- every other tool/resource uses
    the read-only :func:`vcr_base_dir` instead.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist verification case record base directory.
    """
    result = ensure_doc_base_dir(VCR_TYPE_NAME)
    return result


def iter_vcr_paths() -> Iterator[Path]:
    """Yield every verification case record ``*.md`` file under :func:`vcr_base_dir`, sorted by name.

    Yields nothing (rather than raising) if the base directory does not exist.

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    result = iter_doc_paths(vcr_base_dir())
    return result


def _get_vcr_id(doc: VcrDocument) -> str | None:
    """Extract the id from a parsed :class:`VcrDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
    result = doc.frontmatter.id
    return result


def find_vcr_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path under ``base_dir``.

    Scans every ``*.md`` file under ``base_dir``, reading each through the
    cache-backed :func:`~._cache.read_vcr` (feat-107-doc-cache Phase 4) and
    comparing ``frontmatter.id`` against ``id_`` -- a file whose on-disk
    content hash is unchanged since its last read is not re-parsed. A file
    that fails to parse
    (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
    one broken file must not prevent lookup of a different, valid id.
    Mirrors ``gol.tools._paths.find_gol_path``'s own skip-on-parse-failure
    rule. Before scanning, the cache is reconciled
    against the freshly materialized live path listing
    (:func:`~._cache.reconcile_vcr_cache`), dropping any cached entry for a
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
    VcrNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    try:
        result = find_doc_path_by_id(base_dir, id_, read_vcr, _get_vcr_id, reconcile_fn=reconcile_vcr_cache)
    except DocNotFoundError as ex:
        raise VcrNotFoundError(
            f"no verification case record found with id {id_!r}. The id must be the bare document "
            f"UUID, without a domain prefix (use '<uuid>', not 'vcr-<uuid>')."
        ) from ex
    return result
