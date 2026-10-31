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

"""Decision base directory resolution and id -> path lookup (Task 2.1).

A thin, decision-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``gol.tools._paths`` file-for-file.

Mirrors ``gol.tools._paths``'s read-only/write split: :func:`dec_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_dec_base_dir` does, for ``create_dec``.

**Cache-backed scan (feat-107-doc-cache Phase 4).** :func:`find_dec_path`
now scans through the content-hash-validated per-domain cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s own
``read_dec`` (not ``parse_dec``) as ``find_doc_path_by_id``'s ``read_fn``,
so a file whose on-disk content hash is unchanged since its last read is
not re-parsed, and it passes ``._cache``'s ``reconcile_dec_cache`` as
``reconcile_fn`` so an orphaned cache entry (a file deleted outside
specmgr's own tooling) is dropped before any per-file work on every scan.
``read_dec``/``reconcile_dec_cache`` are imported from ``._cache``, not
``._io``, to avoid a circular import -- see ``._cache``'s own module
docstring for the full rationale. The filesystem remains the sole source
of truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache entry is only
ever a memoization keyed by validated content hash, never an independent
fact about what exists on disk.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from ...general.tools._doc_paths import (
    DocNotFoundError,
    doc_base_dir,
    ensure_doc_base_dir,
    find_doc_path_by_id,
    iter_doc_paths,
    iter_doc_paths_all_languages,
)
from ..models.v1 import DecDocument
from ._cache import read_dec, reconcile_dec_cache

__all__ = [
    "DEC_TYPE_NAME",
    "DecNotFoundError",
    "dec_base_dir",
    "ensure_dec_base_dir",
    "find_dec_path",
    "iter_dec_paths",
]

#: The doc-type subdirectory name passed to ``general.tools._doc_paths``
#: (``{docs root}/dec/``, e.g. ``docs/dec``).
DEC_TYPE_NAME = "dec"


class DecNotFoundError(LookupError):
    """No decision file found matching the given id.

    A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
    a subclass of it -- the same relationship ``gol.tools._paths.GolNotFoundError``
    has to nothing generic, so callers can keep catching a decision-specific
    exception type without depending on the generic module's own exception.
    """


def dec_base_dir(language: str | None = None) -> Path:
    """Return the configured decision base directory, without creating it.

    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(DEC_TYPE_NAME)``
    -- see that function's own docstring for the env var/default it reads
    and for the optional ``language`` resolution (feat-197-i18n Phase 110):
    ``None``/omitted or ``"en"`` = the flat ``docs/dec/`` directory exactly
    as before; any other shape-validated code = its ``docs/dec/{language}/``
    subdirectory.

    Parameters
    ----------
    language:
        The document language to resolve -- see
        :func:`general.tools._doc_paths.doc_base_dir`.

    Returns
    -------
    Path
        The resolved decision base directory (in the given language).
    """
    result = doc_base_dir(DEC_TYPE_NAME, language)
    return result


def ensure_dec_base_dir(language: str | None = None) -> Path:
    """Return the configured decision base directory, creating it if missing.

    Only ``create_dec`` should call this -- every other tool/resource uses
    the read-only :func:`dec_base_dir` instead. The optional ``language``
    parameter selects the same flat-vs-subdirectory resolution as
    :func:`dec_base_dir` (feat-197-i18n Phase 110) before the directory is
    created.

    Parameters
    ----------
    language:
        The document language to resolve -- see
        :func:`general.tools._doc_paths.ensure_doc_base_dir`.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist decision base directory (in
        the given language).
    """
    result = ensure_doc_base_dir(DEC_TYPE_NAME, language)
    return result


def iter_dec_paths(language: str | None = None) -> Iterator[Path]:
    """Yield every decision ``*.md`` file in one language's directory, sorted by name.

    The optional ``language`` (feat-197-i18n Phase 110) selects the scanned
    directory: ``None``/omitted or ``"en"`` = the flat ``docs/dec/``
    directory (exactly today's listing); any other shape-validated code =
    its ``docs/dec/{language}/`` subdirectory. Yields nothing (rather than
    raising) if the selected directory does not exist.

    Parameters
    ----------
    language:
        The document language whose directory to scan -- see
        :func:`dec_base_dir`.

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    result = iter_doc_paths(dec_base_dir(language))
    return result


def _get_dec_id(doc: DecDocument) -> str | None:
    """Extract the id from a parsed :class:`DecDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
    result = doc.frontmatter.id
    return result


def _reconcile_dec_scan(scan_paths: Iterable[Path]) -> None:  # pylint: disable=unused-argument
    """Reconcile the decision cache against the domain-wide live listing (the ``find_dec_path`` ``reconcile_fn``).

    The ``reconcile_fn`` :func:`find_doc_path_by_id` calls once, before any
    per-file work, with the scanned directory's own materialized path
    listing. With the ``{language}`` subfolder layout (feat-197-i18n
    Phase 110, ADR 38efdb66 item 9), a scan of one language directory no
    longer covers the whole domain -- reconciling against ``scan_paths``
    alone would evict every other language's cached entries -- so this
    wrapper instead hands :func:`~._cache.reconcile_dec_cache` the
    domain-wide union (the flat EN files plus every file in every
    shape-valid ``{language}`` subdirectory,
    ``general.tools._doc_paths.iter_doc_paths_all_languages``).
    ``scan_paths`` is intentionally unused: the union is a superset of it,
    and recomputing it from the directory listing keeps this one helper
    correct regardless of which language's directory was scanned. With no
    language subdirectory present the union is the scanned listing itself
    (the pre-i18n behavior, byte-identical).
    """
    reconcile_dec_cache(list(iter_doc_paths_all_languages(dec_base_dir())))


def find_dec_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path under ``base_dir``.

    Scans every ``*.md`` file under ``base_dir``, reading each through the
    cache-backed :func:`~._cache.read_dec` (feat-107-doc-cache Phase 4) and
    comparing ``frontmatter.id`` against ``id_`` -- a file whose on-disk
    content hash is unchanged since its last read is not re-parsed. A file
    that fails to parse
    (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
    one broken file must not prevent lookup of a different, valid id.
    Mirrors ``gol.tools._paths.find_gol_path``'s own skip-on-parse-failure
    rule. Before scanning, the cache is reconciled
    (:func:`~._cache.reconcile_dec_cache`) against the freshly
    materialized domain-wide live path listing (the flat EN files plus
    every ``{language}`` subdirectory's files -- a scan of one language
    must not evict the other languages' entries, feat-197-i18n Phase 110),
    dropping any cached entry for a file deleted outside specmgr's own
    tooling (REQ-005).

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files (the flat EN directory,
        or one ``{language}`` subdirectory).
    id_:
        The id to look up.

    Returns
    -------
    Path
        The resolved file path.

    Raises
    ------
    DecNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    try:
        result = find_doc_path_by_id(base_dir, id_, read_dec, _get_dec_id, reconcile_fn=_reconcile_dec_scan)
    except DocNotFoundError as ex:
        raise DecNotFoundError(
            f"no decision found with id {id_!r}. The id must be the bare document UUID, without a "
            f"domain prefix (use '<uuid>', not 'dec-<uuid>')."
        ) from ex
    return result
