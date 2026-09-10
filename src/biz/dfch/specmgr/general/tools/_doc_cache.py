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

"""Generic, doc-type-agnostic content-hash-validated in-memory read cache (feat-107-doc-cache, Phase 2).

``get_*``/``list_*`` MCP tool calls currently re-scan and fully re-parse an
entire domain directory on every single invocation
(``general.tools._doc_paths.find_doc_path_by_id``,
``general.tools._listing.build_summaries``), paying full markdown-it
tokenizing plus nested Pydantic validation cost on every call, for every
candidate file scanned -- CPU-bound work that holds the GIL and therefore
serializes regardless of how many threads/cores are available. This module
supplies :class:`DocCache`, a reusable, domain-agnostic cache class that
eliminates that redundant re-parsing: a file is only ever re-parsed when its
on-disk content actually changed.

**Process-local, one instance per domain.** This module supplies only the
reusable :class:`DocCache` class itself -- it is Phase 3/4's job to
instantiate one module-level singleton per domain (mirroring the existing
per-domain ``threading.Lock`` registries in each domain's own ``_lock.py``)
and route that domain's ``read_<domain>``/``find_doc_path_by_id`` scan/
``list_<domain>`` summary-building callback through it. **ADR
(``models/adr/v1``) is deliberately excluded from this cache mechanism
entirely** -- it is expected to be phased out later and does not justify
its own independently-implemented cache module, since it has no dependency
on ``general`` to begin with.

**Content-hash validation guarantee.** Every :meth:`DocCache.read` call
re-hashes ``path``'s full on-disk text (``hashlib.blake2b``) and compares it
against the hash recorded at the last successful/failed read of that path
*before* deciding whether to skip re-parsing -- a stale entry is
structurally impossible, it can only ever cost one extra parse. This
refines, rather than violates, ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3's
"the filesystem is the sole source of truth" invariant. See ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d for the full design this module
implements, including its relationship to ADR 33c5ab08 and the explicit
ADR-domain exclusion above.

**Lock-ordering rule.** :class:`DocCache`'s own internal ``threading.Lock``
guards *only* its dict get/set/pop bookkeeping -- never the file read, never
the caller-supplied ``parse_fn`` call itself, and never held across any
domain-level per-id lock (e.g. ``req_lock``, ``feat_create_lock``/
``feat_lock``). Per ADR bfd76370-b59b-4d65-b550-a969f6c93c9d, this cache's
lock is always the *innermost* lock acquired in any call stack: a caller
holding a domain lock may acquire this cache's lock, but this cache never
acquires a domain lock itself, and never holds its own lock across a call
back into caller code (the file read or ``parse_fn``) that could itself
attempt to acquire another lock.

**Explicitly out of scope** (mirroring the feature's own Scope section): no
TTL/size-based eviction, and no ``stat()``-based (mtime/size) pre-check fast
path -- content-hash-only for this first version.
"""

from __future__ import annotations

import hashlib
import threading
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import ValidationError

__all__ = ["CACHEABLE_ERROR_TYPES", "DocCache"]

#: The exact failure channel every ``parse_<domain>`` function in this
#: codebase can raise (mirrors ``general.tools._listing.DEFAULT_ERROR_TYPES``):
#: structural (``AssertionError``), field/cross-field
#: (``pydantic.ValidationError``), and malformed frontmatter YAML
#: (``yaml.YAMLError``, raised unwrapped by ``parse_<domain>``). Only a
#: ``parse_fn`` failure of one of these types is cached as a "failure" --
#: anything else (a bug, an unexpected exception type) propagates
#: uncaught and is never stored, so a genuine bug stays immediately visible
#: instead of being silently pinned into the cache.
CACHEABLE_ERROR_TYPES: tuple[type[Exception], ...] = (AssertionError, ValidationError, yaml.YAMLError)

#: Parsed-document type produced by a caller-supplied ``parse_fn``.
_DocT = TypeVar("_DocT")


class DocCache(Generic[_DocT]):
    """A process-local, content-hash-validated in-memory read cache for one domain.

    Shaped as ``dict[Path, tuple[content_hash, result]]`` (ADR
    bfd76370-b59b-4d65-b550-a969f6c93c9d), where ``result`` is either the
    successfully parsed document or the exception a prior parse attempt
    raised. One :class:`DocCache` instance is intended per domain, created
    once as a module-level singleton (Phase 3/4's job, not this module's) --
    this class carries no assumption about which domain it caches for
    beyond the generic ``_DocT`` type parameter.

    Not thread-hostile, but not a full cross-file synchronization
    primitive either: the internal lock (``threading.Lock``) guards only
    this instance's dict bookkeeping, so concurrent :meth:`read` calls for
    *different* paths never block each other on that bookkeeping. A
    concurrent cold-start race for the *same* path may still invoke
    ``parse_fn`` more than once (allowed for by ACC-006, a Phase 3 concern);
    this class does not attempt to de-duplicate in-flight parses.
    """

    def __init__(self) -> None:
        """Initialize an empty cache."""
        self._lock = threading.Lock()
        #: Maps a path to its ``(content_hash, result)`` entry, where
        #: ``result`` is either the successfully parsed document or the
        #: exception a failed parse raised.
        self._entries: dict[Path, tuple[bytes, _DocT | Exception]] = {}

    def read(self, path: Path, parse_fn: Callable[[Path], _DocT]) -> _DocT:
        """Return the cached or freshly-parsed result for ``path``.

        Reads ``path``'s full on-disk text and computes its content hash on
        every call, regardless of hit/miss. When the computed hash matches
        the hash stored for ``path`` at its last read, the stored result is
        returned without invoking ``parse_fn`` again -- re-raising the
        stored exception if that prior read had failed. On a hash mismatch
        or cache miss, ``parse_fn(path)`` is called fresh, and the new
        ``(hash, result)`` pair (or ``(hash, exception)`` for one of
        :data:`CACHEABLE_ERROR_TYPES`) is stored before returning/re-raising.

        Only the dict get/set around ``parse_fn`` is guarded by this
        instance's lock; the file read and the ``parse_fn`` call itself
        happen outside the lock, so a slow parse of one path never blocks a
        concurrent read of a different path.

        Parameters
        ----------
        path:
            The filesystem path to read and, if needed, parse.
        parse_fn:
            Parses ``path`` into a document object on a cache miss (e.g. a
            domain's own ``read_<domain>``, or ``lambda p: parse_req(p.read_text(encoding="utf-8"))``).
            Typically re-reads ``path``'s text itself -- this is expected
            and not a redundant read to avoid, since it only happens on an
            actual cache miss.

        Returns
        -------
        _DocT
            The cached or freshly-parsed document.

        Raises
        ------
        Exception
            Re-raises a cached parse failure (one of
            :data:`CACHEABLE_ERROR_TYPES`) on a hash match, or propagates a
            fresh ``parse_fn`` failure of one of those types after caching
            it. Any other exception (including a failure to even read
            ``path``, e.g. ``OSError``/``FileNotFoundError``) propagates
            uncaught and is never cached.
        """
        assert isinstance(path, Path), type(path)
        assert callable(parse_fn), type(parse_fn)

        text = path.read_text(encoding="utf-8")
        content_hash = hashlib.blake2b(text.encode("utf-8")).digest()

        with self._lock:
            cached = self._entries.get(path)
        if cached is not None and cached[0] == content_hash:
            cached_result = cached[1]
            if isinstance(cached_result, Exception):
                raise cached_result
            return cached_result

        try:
            result: _DocT = parse_fn(path)
        except CACHEABLE_ERROR_TYPES as exc:
            with self._lock:
                self._entries[path] = (content_hash, exc)
            raise

        with self._lock:
            self._entries[path] = (content_hash, result)
        return result

    def invalidate(self, path: Path) -> None:
        """Drop ``path``'s cache entry, if present.

        A no-op if ``path`` has no cached entry.

        Parameters
        ----------
        path:
            The filesystem path whose cache entry to drop.
        """
        assert isinstance(path, Path), type(path)

        with self._lock:
            self._entries.pop(path, None)

    def reconcile(self, live_paths: Iterable[Path]) -> None:
        """Drop every cached entry whose path is not in ``live_paths``.

        A pure set-difference operation against the given, already
        materialized live path listing (e.g. from a cheap directory glob
        via ``iter_doc_paths``) -- performs no file I/O of its own.

        Parameters
        ----------
        live_paths:
            The current, live set of on-disk paths for this domain.
        """
        live_set = set(live_paths)

        with self._lock:
            stale_paths = [cached_path for cached_path in self._entries if cached_path not in live_set]
            for stale_path in stale_paths:
                del self._entries[stale_path]

    def move(self, old_path: Path, new_path: Path) -> None:
        """Relocate ``old_path``'s cache entry (if present) to ``new_path``.

        For a rename case (e.g. ``set_feat_id``'s folder rename): a no-op if
        ``old_path`` has no cached entry. Otherwise, moves the entry's
        stored ``(hash, result)`` pair as-is, without re-validating it
        against ``new_path``'s actual on-disk content -- the next
        :meth:`read` of ``new_path`` re-hashes its current content and
        naturally hits (if ``old_path``'s and ``new_path``'s content are
        byte-for-byte identical, the realistic case for a plain rename) or
        misses and reparses (if not) exactly like any other :meth:`read`
        call.

        Parameters
        ----------
        old_path:
            The cache entry's current key.
        new_path:
            The cache entry's new key.
        """
        assert isinstance(old_path, Path), type(old_path)
        assert isinstance(new_path, Path), type(new_path)

        with self._lock:
            entry = self._entries.pop(old_path, None)
            if entry is not None:
                self._entries[new_path] = entry

    def reset(self) -> None:
        """Clear every cached entry.

        Test-only: not for production use. Exists so tests do not leak
        cached entries across test cases within the same process, since a
        domain's cache instance is otherwise a module-level singleton that
        persists for the whole test process's lifetime.
        """
        with self._lock:
            self._entries.clear()
