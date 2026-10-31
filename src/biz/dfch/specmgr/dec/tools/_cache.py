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

"""Per-domain content-hash-validated read cache singleton for decisions (feat-107-doc-cache Phase 4).

1:1 port of ``req.tools._cache``'s shape (feat-107-doc-cache Phase 3, the
pilot domain) for the ``dec`` domain -- see that module's own docstring for
the full circular-import rationale this module also follows: ``dec.tools._io``'s
``load_by_id`` needs ``find_dec_path`` (from ``_paths.py``) to resolve an id to
a path; with the cache wired in, ``_paths.py``'s ``find_dec_path`` needs a
cache-backed ``read_fn`` to pass to
``general.tools._doc_paths.find_doc_path_by_id`` -- and the only cache-backed
reader available is ``read_dec``. Pulling the cache singleton and ``read_dec``
out into this standalone ``_cache.py`` module breaks the
``_io.py -> _paths.py -> _io.py`` cycle that would otherwise result: both
``_io.py`` and ``_paths.py`` depend *downward* on ``_cache.py``, and
``_cache.py`` depends on neither of them -- only on the generic
``general.tools._doc_cache.DocCache`` class, the generic
``general.tools._doc_paths.language_for_doc_path`` helper (the
file-position -> language derivation, feat-197-i18n Phase 110), and this
domain's own ``dec.models.v1`` (DecDocument/parse_dec). Its one
``_paths`` import (``dec_base_dir``) is deferred inside ``read_dec`` for
the same circular-import reason this module exists (see the function's
own comment).

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime -- the
same shape as ``_lock.py``'s per-id lock registry, just a single instance
here rather than one-per-id, since a domain only ever needs one cache. No
call site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below
(``read_dec``/``invalidate_dec_cache``/``reconcile_dec_cache``), and those
functions close over the module-level ``_cache`` singleton.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_dec_cache` exists purely so tests can clear every cached entry
in ``setUp``/``tearDown`` and never observe another test's cached state.
It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``dec`` domain, and
``.specmgr/feat/feat-107-doc-cache/README.md`` for the feature plan this
implements (Phase 4, mechanically repeating Phase 3's ``req`` template).
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import partial
from pathlib import Path

from ...general.tools._doc_cache import DocCache
from ...general.tools._doc_paths import language_for_doc_path
from ..models.v1 import DecDocument, parse_dec

__all__ = ["invalidate_dec_cache", "read_dec", "reconcile_dec_cache", "reset_dec_cache"]

#: Module-level singleton, one per process, for the lifetime of the process
#: (mirrors ``_lock.py``'s ``_locks`` registry). See the module docstring.
_cache: DocCache[DecDocument] = DocCache()


def _parse(text: str, *, language: str | None = None) -> DecDocument:
    """Parse ``text`` into a :class:`DecDocument` (the cache's own ``parse_fn`` -- Phase 6: text in, not ``Path``).

    Receives the exact text :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.read`
    already read (and hashed) for this same call -- this function must not
    re-read the file itself (feat-107-doc-cache Phase 6, REQ-007: closes the
    hash/parse TOCTOU race the previous two-independent-reads shape had).
    The optional ``language`` (feat-197-i18n Phase 110) is the effective
    language of the file being parsed -- ``None``/omitted or ``"en"`` runs
    the canonical EN parse, any other value applies that language's
    heading-mapping table at ``parse_dec``'s own pre-pass.
    """
    assert isinstance(text, str), type(text)
    assert language is None or isinstance(language, str), type(language)

    result = parse_dec(text, language=language)
    return result


def read_dec(path: Path) -> DecDocument:
    """Read and parse the decision at ``path``, through the cache.

    A file is only ever re-parsed when its on-disk content hash no longer
    matches the hash recorded at the last read of ``path`` (ADR
    bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
    re-raised cached failure) is returned without re-invoking
    :func:`~biz.dfch.specmgr.dec.models.v1.parse_dec`.

    **Language-aware (feat-197-i18n Phase 110).** The effective language is
    derived from the file's own position relative to the decision base
    directory (``general.tools._doc_paths.language_for_doc_path`` -- a file
    directly in the flat ``docs/dec/`` directory parses canonical/EN, a file
    directly in ``docs/dec/{language}/`` parses in that language, anything
    else canonical), never from a caller argument: the location *is* the
    language encoding (ADR 38efdb66 item 1), so every consumer of this
    reader (``find_dec_path``'s scan, ``list_dec``'s rows, ``load_by_id``'s
    second read, the generic tools' own dec adapters) parses a variant file
    with its table without any signature change, and the ``DocCache``'s
    path-keyed entries keep EN and every language of one id independent
    (ADR item 9 -- no cache code change).

    Parameters
    ----------
    path:
        The filesystem path to the decision ``.md`` file.

    Returns
    -------
    DecDocument
        The cached or freshly-parsed, validated document (canonical heading
        text; for a language variant, that language's table applied).
    """
    # Deferred past module import: ``_paths`` imports this module's own
    # ``read_dec``/``reconcile_dec_cache`` at module level (the
    # ``_io.py -> _paths.py -> _io.py`` cycle the module docstring describes),
    # so a module-level import back into it would be a circular import --
    # the same deferred-import discipline ``general.tools._path_safety``
    # applies to its own ``_domains`` import.
    from ._paths import dec_base_dir  # pylint: disable=import-outside-toplevel

    language = language_for_doc_path(dec_base_dir(), path)
    result = _cache.read(path, partial(_parse, language=language))
    return result


def invalidate_dec_cache(path: Path) -> None:
    """Drop ``path``'s cached entry, if present.

    Called by the generic ``delete`` tool's ``dec`` adapter immediately
    after a successful ``unlink()`` (REQ-004), so a deleted document's
    stale cache entry is never served.

    Parameters
    ----------
    path:
        The filesystem path whose cache entry to drop.
    """
    _cache.invalidate(path)


def reconcile_dec_cache(live_paths: Iterable[Path]) -> None:
    """Drop every cached entry whose path is not in ``live_paths`` (REQ-005).

    Called before any per-file work in both ``find_dec_path``'s scan (via
    ``general.tools._doc_paths.find_doc_path_by_id``'s ``reconcile_fn``
    parameter) and ``list_dec``, so a file deleted outside specmgr's own
    tooling does not leak in memory indefinitely.

    Parameters
    ----------
    live_paths:
        The current, live set of on-disk paths for the ``dec`` domain.
    """
    _cache.reconcile(live_paths)


def reset_dec_cache() -> None:
    """Clear every cached entry.

    Test-only: not for production use. See the module docstring's "Test
    isolation" section.
    """
    _cache.reset()
