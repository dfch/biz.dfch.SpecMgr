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

"""Per-domain content-hash-validated read cache singleton for verification case records (feat-107-doc-cache Phase 4).

1:1 port of ``req.tools._cache``'s shape (feat-107-doc-cache Phase 3, the
pilot domain) for the ``vcr`` domain -- see that module's own docstring for
the full circular-import rationale this module also follows: ``vcr.tools._io``'s
``load_by_id`` needs ``find_vcr_path`` (from ``_paths.py``) to resolve an id to
a path; with the cache wired in, ``_paths.py``'s ``find_vcr_path`` needs a
cache-backed ``read_fn`` to pass to
``general.tools._doc_paths.find_doc_path_by_id`` -- and the only cache-backed
reader available is ``read_vcr``. Pulling the cache singleton and ``read_vcr``
out into this standalone ``_cache.py`` module breaks the
``_io.py -> _paths.py -> _io.py`` cycle that would otherwise result: both
``_io.py`` and ``_paths.py`` depend *downward* on ``_cache.py``, and
``_cache.py`` depends on neither of them -- only on the generic
``general.tools._doc_cache.DocCache`` class and this domain's own
``vcr.models.v1`` (VcrDocument/parse_vcr).

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime -- the
same shape as ``_lock.py``'s per-id lock registry, just a single instance
here rather than one-per-id, since a domain only ever needs one cache. No
call site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below
(``read_vcr``/``invalidate_vcr_cache``/``reconcile_vcr_cache``), and those
functions close over the module-level ``_cache`` singleton.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_vcr_cache` exists purely so tests can clear every cached entry
in ``setUp``/``tearDown`` and never observe another test's cached state.
It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``vcr`` domain, and
``.specmgr/feat/feat-107-doc-cache/README.md`` for the feature plan this
implements (Phase 4, mechanically repeating Phase 3's ``req`` template).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ...general.tools._doc_cache import DocCache
from ..models.v1 import VcrDocument, parse_vcr

__all__ = ["invalidate_vcr_cache", "read_vcr", "reconcile_vcr_cache", "reset_vcr_cache"]

#: Module-level singleton, one per process, for the lifetime of the process
#: (mirrors ``_lock.py``'s ``_locks`` registry). See the module docstring.
_cache: DocCache[VcrDocument] = DocCache()


def _parse(path: Path) -> VcrDocument:
    """Read and parse ``path``'s full text into a :class:`VcrDocument` (the cache's own ``parse_fn``)."""
    assert isinstance(path, Path), type(path)

    result = parse_vcr(path.read_text(encoding="utf-8"))
    return result


def read_vcr(path: Path) -> VcrDocument:
    """Read and parse the verification case record at ``path``, through the cache.

    A file is only ever re-parsed when its on-disk content hash no longer
    matches the hash recorded at the last read of ``path`` (ADR
    bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
    re-raised cached failure) is returned without re-invoking
    :func:`~biz.dfch.specmgr.vcr.models.v1.parse_vcr`.

    Parameters
    ----------
    path:
        The filesystem path to the verification case record ``.md`` file.

    Returns
    -------
    VcrDocument
        The cached or freshly-parsed, validated document.
    """
    result = _cache.read(path, _parse)
    return result


def invalidate_vcr_cache(path: Path) -> None:
    """Drop ``path``'s cached entry, if present.

    Called by the generic ``delete`` tool's ``vcr`` adapter immediately
    after a successful ``unlink()`` (REQ-004), so a deleted document's
    stale cache entry is never served.

    Parameters
    ----------
    path:
        The filesystem path whose cache entry to drop.
    """
    _cache.invalidate(path)


def reconcile_vcr_cache(live_paths: Iterable[Path]) -> None:
    """Drop every cached entry whose path is not in ``live_paths`` (REQ-005).

    Called before any per-file work in both ``find_vcr_path``'s scan (via
    ``general.tools._doc_paths.find_doc_path_by_id``'s ``reconcile_fn``
    parameter) and ``list_vcr``, so a file deleted outside specmgr's own
    tooling does not leak in memory indefinitely.

    Parameters
    ----------
    live_paths:
        The current, live set of on-disk paths for the ``vcr`` domain.
    """
    _cache.reconcile(live_paths)


def reset_vcr_cache() -> None:
    """Clear every cached entry.

    Test-only: not for production use. See the module docstring's "Test
    isolation" section.
    """
    _cache.reset()
