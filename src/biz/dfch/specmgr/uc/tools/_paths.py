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

"""Use-case base directory resolution and id -> path lookup (Task 3.1.5).

A thin, use-case-specific layer over the generic
``general.tools._doc_paths`` module, mirroring ``req.tools._paths`` exactly.

Mirrors ``req.tools._paths``'s read-only/write split: :func:`uc_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_uc_base_dir` does, for ``create_uc``.

**Cache-backed scan (feat-107-doc-cache Phase 4).** :func:`find_uc_path`
now scans through the content-hash-validated per-domain cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d): it passes ``._cache``'s own
``read_uc`` (not ``parse_uc``) as ``find_doc_path_by_id``'s ``read_fn``,
so a file whose on-disk content hash is unchanged since its last read is
not re-parsed, and it passes ``._cache``'s ``reconcile_uc_cache`` as
``reconcile_fn`` so an orphaned cache entry (a file deleted outside
specmgr's own tooling) is dropped before any per-file work on every scan.
``read_uc``/``reconcile_uc_cache`` are imported from ``._cache``, not
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
from ..models.v2 import UcDocument
from ._cache import read_uc, reconcile_uc_cache

__all__ = [
    "UC_TYPE_NAME",
    "UcNotFoundError",
    "ensure_uc_base_dir",
    "find_uc_path",
    "iter_uc_paths",
    "uc_base_dir",
]

#: The doc-type subdirectory name passed to ``general.tools._doc_paths``
#: (``{docs root}/uc/``, e.g. ``docs/uc``).
UC_TYPE_NAME = "uc"


class UcNotFoundError(LookupError):
    """No use-case file found matching the given id.

    A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
    a subclass of it -- mirrors ``req.tools._paths.ReqNotFoundError``'s own
    relationship, so callers can keep catching a use-case-specific exception
    type without depending on the generic module's own exception.
    """


def uc_base_dir(language: str | None = None) -> Path:
    """Return the configured use-case base directory, without creating it.

    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(UC_TYPE_NAME)``
    -- see that function's own docstring for the env var/default it reads.

    The optional ``language`` (feat-197-i18n Phase 125) selects the flat-vs-subdirectory
    resolution: ``None``/omitted or ``"en"`` = the flat ``docs/uc/`` directory exactly
    as before; any other shape-validated code = its ``docs/uc/{language}/``
    subdirectory.

    Parameters
    ----------
    language:
        The document language to resolve -- see
        :func:`general.tools._doc_paths.doc_base_dir`.

    Returns
    -------
    Path
        The resolved use-case base directory.
    """
    result = doc_base_dir(UC_TYPE_NAME, language)
    return result


def ensure_uc_base_dir(language: str | None = None) -> Path:
    """Return the configured use-case base directory, creating it if missing.

    Only ``create_uc`` should call this -- every other tool/resource uses
    the read-only :func:`uc_base_dir` instead.

    The optional ``language`` parameter selects the same flat-vs-subdirectory resolution as
    :func:`uc_base_dir` (feat-197-i18n Phase 125) before the directory is created.

    Parameters
    ----------
    language:
        The document language to resolve -- see
        :func:`general.tools._doc_paths.ensure_doc_base_dir`.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist use-case base directory.
    """
    result = ensure_doc_base_dir(UC_TYPE_NAME, language)
    return result


def iter_uc_paths(language: str | None = None) -> Iterator[Path]:
    """Yield every use-case ``*.md`` file under :func:`uc_base_dir`, sorted by name.

    Yields nothing (rather than raising) if the base directory does not exist.

    The optional ``language`` (feat-197-i18n Phase 125) selects the scanned directory:
    ``None``/omitted or ``"en"`` = the flat ``docs/uc/`` directory (exactly today's
    listing); any other shape-validated code = its ``docs/uc/{language}/``
    subdirectory (non-recursive; never descends further).

    Parameters
    ----------
    language:
        The document language whose directory to scan -- see
        :func:`uc_base_dir`.

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    result = iter_doc_paths(uc_base_dir(language))
    return result


def _get_uc_id(doc: UcDocument) -> str | None:
    """Extract the id from a parsed :class:`UcDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
    result = doc.frontmatter.id
    return result


def _reconcile_uc_scan(scan_paths: Iterable[Path]) -> None:  # pylint: disable=unused-argument
    """Reconcile the ``uc`` cache against the domain-wide live listing (the ``find_uc_path`` ``reconcile_fn``).

    The ``reconcile_fn`` :func:`find_doc_path_by_id` calls once, before any
    per-file work, with the scanned directory's own materialized path
    listing. With the ``{language}`` subfolder layout (feat-197-i18n
    Phase 125, ADR 38efdb66 item 9), a scan of one language directory no
    longer covers the whole domain -- reconciling against ``scan_paths``
    alone would evict every other language's cached entries -- so this
    wrapper instead hands :func:`~._cache.reconcile_uc_cache` the
    domain-wide union (the flat EN files plus every file in every
    shape-valid ``{language}`` subdirectory,
    ``general.tools._doc_paths.iter_doc_paths_all_languages``).
    ``scan_paths`` is intentionally unused: the union is a superset of it.
    With no language subdirectory present the union is the scanned listing
    itself (the pre-i18n behavior, byte-identical).
    """
    reconcile_uc_cache(list(iter_doc_paths_all_languages(uc_base_dir())))


def find_uc_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path under ``base_dir``.

    Scans every ``*.md`` file under ``base_dir``, reading each through the
    cache-backed :func:`~._cache.read_uc` (feat-107-doc-cache Phase 4) and
    comparing ``frontmatter.id`` against ``id_`` -- a file whose on-disk
    content hash is unchanged since its last read is not re-parsed. A file
    that fails to parse
    (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
    one broken file must not prevent lookup of a different, valid id.
    Mirrors ``req.tools._paths.find_req_path``'s own skip-on-parse-failure
    rule. Before scanning, the cache is reconciled
    against the freshly materialized live path listing
    (:func:`~._cache.reconcile_uc_cache`, against the domain-wide live listing of every language
    -- a scan of one language must not evict the other languages' entries, feat-197-i18n
    Phase 125), dropping any cached entry for a
    file deleted outside specmgr's own tooling (REQ-005).

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
    UcNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    try:
        result = find_doc_path_by_id(base_dir, id_, read_uc, _get_uc_id, reconcile_fn=_reconcile_uc_scan)
    except DocNotFoundError as ex:
        raise UcNotFoundError(
            f"no use case found with id {id_!r}. The id must be the bare document UUID, without a domain "
            f"prefix (use '<uuid>', not 'uc-<uuid>')."
        ) from ex
    return result
