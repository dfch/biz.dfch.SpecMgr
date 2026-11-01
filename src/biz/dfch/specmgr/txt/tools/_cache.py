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

"""Per-domain content-hash-validated read cache singleton for free-form text (feat-229-txt Phase 110).

1:1 port of ``vcr.tools._cache``'s shape for the ``txt`` domain -- see that
module's own docstring for the full circular-import rationale this module
also follows: ``txt.tools._io``'s ``load_by_id`` needs ``find_txt_path``
(from ``_paths.py``) to resolve an id to a path; with the cache wired in,
``_paths.py``'s ``find_txt_path`` needs a cache-backed ``read_fn`` to pass
to ``general.tools._doc_paths.find_doc_path_by_id`` -- and the only
cache-backed reader available is ``read_txt``. Pulling the cache singleton
and ``read_txt`` out into this standalone ``_cache.py`` module breaks the
``_io.py -> _paths.py -> _io.py`` cycle that would otherwise result: both
``_io.py`` and ``_paths.py`` depend *downward* on ``_cache.py``, and
``_cache.py`` depends on neither of them -- only on the generic
``general.tools._doc_cache.DocCache`` class and this domain's own
``txt.models.v1`` (TxtDocument/parse_txt).

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime -- the
same shape as ``_lock.py``'s per-id lock registry, just a single instance
here rather than one-per-id, since a domain only ever needs one cache. No
call site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below
(``read_txt``/``invalidate_txt_cache``/``reconcile_txt_cache``), and those
functions close over the module-level ``_cache`` singleton.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_txt_cache` exists purely so tests can clear every cached entry
in ``setUp``/``tearDown`` and never observe another test's cached state.
It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``txt`` domain.
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from pathlib import Path

from ...general.tools._doc_cache import DocCache
from ...general.tools._doc_paths import language_for_doc_path
from ..models.v1 import TxtDocument, parse_txt

__all__ = ["invalidate_txt_cache", "read_txt", "reconcile_txt_cache", "reset_txt_cache"]

#: Module-level singleton, one per process, for the lifetime of the process
#: (mirrors ``_lock.py``'s ``_locks`` registry). See the module docstring.
_cache: DocCache[TxtDocument] = DocCache()


def _parse(text: str, *, language: str | None = None) -> TxtDocument:
    """Parse ``text`` into a :class:`TxtDocument` (the cache's own ``parse_fn``).

    Receives the exact text :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.read`
    already read (and hashed) for this same call -- this function must not
    re-read the file itself (feat-107-doc-cache Phase 6, REQ-007: closes the
    hash/parse TOCTOU race the previous two-independent-reads shape had).
    The optional ``language`` (feat-197-i18n Phase 125) is the effective
    language of the file being parsed -- ``None``/omitted or ``"en"`` runs
    the canonical EN parse, any other value applies that language's
    heading-mapping table at ``parse_txt``'s own pre-pass.
    """
    assert isinstance(text, str), type(text)
    assert language is None or isinstance(language, str), type(language)

    result = parse_txt(text, language=language)
    return result


def read_txt(path: Path) -> TxtDocument:
    """Read and parse the free-form text document at ``path``, through the cache.

    A file is only ever re-parsed when its on-disk content hash no longer
    matches the hash recorded at the last read of ``path`` (ADR
    bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
    re-raised cached failure) is returned without re-invoking
    :func:`~biz.dfch.specmgr.txt.models.v1.parse_txt`.

    **Language-aware (feat-197-i18n Phase 125).** The effective language is
    derived from the file's own position relative to the free-form text base
    directory (``general.tools._doc_paths.language_for_doc_path`` -- a file
    directly in the flat ``docs/txt/`` directory parses canonical/EN, a file
    directly in ``docs/txt/{language}/`` parses in that language, anything
    else canonical), never from a caller argument: the location *is* the
    language encoding (ADR 38efdb66 item 1), so every consumer of this
    reader (``find_txt_path``'s scan, ``list_txt``'s rows, ``load_by_id``'s
    second read, the generic tools' own txt adapters) parses a variant file
    with its table without any signature change, and the ``DocCache``'s
    path-keyed entries keep EN and every language of one id independent
    (ADR item 9 -- no cache code change).

    Parameters
    ----------
    path:
        The filesystem path to the free-form text ``.md`` file.

    Returns
    -------
    TxtDocument
        The cached or freshly-parsed, validated document.
    """
    # Deferred past module import: ``_paths`` imports this module's own
    # ``read_txt``/``reconcile_txt_cache`` at module level (the
    # ``_io.py -> _paths.py -> _io.py`` cycle the module docstring describes),
    # so a module-level import back into it would be a circular import.
    from ._paths import txt_base_dir  # pylint: disable=import-outside-toplevel

    language = language_for_doc_path(txt_base_dir(), path)
    result = _cache.read(path, partial(_parse, language=language))
    return result


def invalidate_txt_cache(path: Path) -> None:
    """Drop ``path``'s cached entry, if present.

    Called by the generic ``delete`` tool's ``txt`` adapter immediately
    after a successful ``unlink()``, so a deleted document's
    stale cache entry is never served.

    Parameters
    ----------
    path:
        The filesystem path whose cache entry to drop.
    """
    _cache.invalidate(path)


def reconcile_txt_cache(live_paths: Iterable[Path]) -> None:
    """Drop every cached entry whose path is not in ``live_paths``.

    Called before any per-file work in both ``find_txt_path``'s scan (via
    ``general.tools._doc_paths.find_doc_path_by_id``'s ``reconcile_fn``
    parameter) and ``list_txt``, so a file deleted outside specmgr's own
    tooling does not leak in memory indefinitely.

    Parameters
    ----------
    live_paths:
        The current, live set of on-disk paths for the ``txt`` domain.
    """
    _cache.reconcile(live_paths)


def reset_txt_cache() -> None:
    """Clear every cached entry.

    Test-only: not for production use. See the module docstring's "Test
    isolation" section.
    """
    _cache.reset()
