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

"""Per-domain content-hash-validated read cache singleton for features (feat-107-doc-cache Phase 4, Task 4.1a).

``feat`` is the one domain whose cache integration is necessarily bespoke
(the feature plan's own Design Notes, and ADR bfd76370-b59b-4d65-b550-a969f6c93c9d):
``feat.tools._paths``/``feat.tools.set_feat_id`` never route through the
shared ``general.tools._doc_paths`` module every other whole-body
domain's ``_cache.py`` module plugs into (Phase 4's mechanical rollout) --
``feat`` is folder-per-document (``<base>/<id>/README.md``) and its own
``find_feat_path_by_id`` shortcuts directly to that path instead of scanning
and comparing parsed ids. This module still follows every other
domain's *shape* as closely as that difference allows: a module-level
:class:`DocCache` singleton (mirroring ``_lock.py``'s ``_locks`` registry),
``read_feat``/``invalidate_feat_cache``/``reconcile_feat_cache``/
``reset_feat_cache`` -- plus one function unique to this domain,
:func:`move_feat_cache_entry`, wrapping :meth:`DocCache.move` for
``set_feat_id``'s rename case (no other domain in this codebase ever
renames a document's own on-disk path in place; every other rename-shaped
operation is actually a delete+create instead).

**Why this is its own module, not folded into ``_io.py``/``_paths.py``
directly.** Same circular-import rationale as every other domain's own
``_cache.py`` (see e.g. ``req.tools._cache``'s module docstring): ``_io.py``
imports ``find_feat_path_by_id`` from ``_paths.py``; with the cache wired
in, ``_paths.py``'s ``find_feat_path_by_id`` needs a cache-backed
``read_feat`` to avoid re-parsing the same file twice per ``get_feat`` call
(the same double-parse bug ADR bfd76370-b59b-4d65-b550-a969f6c93c9d fixes
for every other domain) -- and the only cache-backed reader available is
``read_feat``. Pulling the cache singleton and ``read_feat`` out into this
standalone ``_cache.py`` module breaks the ``_io.py -> _paths.py -> _io.py``
cycle that would otherwise result.

**Module-level singleton, mirroring ``_lock.py``'s ``_locks`` registry.**
Exactly one :class:`DocCache` instance exists per process for this domain,
created once at import time and reused for the process's lifetime. No call
site threads an explicit cache instance through function signatures;
callers simply import and call the plain functions below.

**Test isolation.** Because ``_cache`` is a module-level singleton, it
would otherwise persist across every test case that runs in the same
process (this codebase's test suite runs under ``pytest-xdist``/``-n
auto``: each worker is its own process, so cross-worker leakage is not a
concern, but cross-*test*-within-the-same-worker leakage very much is).
:func:`reset_feat_cache` exists purely so tests can clear every cached
entry in ``setUp``/``tearDown`` and never observe another test's cached
state. It is not for production use.

See ADR bfd76370-b59b-4d65-b550-a969f6c93c9d for the full cache design this
module wires up for the ``feat`` domain, and
``.specmgr/feat/feat-107-doc-cache/README.md`` for the feature plan this
implements (Phase 4, Task 4.1a).

**feat-187-list-feat-timeout, Task 110.100: a second, "dirty" (frontmatter-
stage) ``DocCache`` instance alongside the pre-existing "clean" (full-parse)
one.** Added to fix GitHub issue #187's ``list_feat`` cold-scan timeout (ADR
3982712a-a46b-4b2b-809f-9c6925a49b44): a cold ``list_feat`` call must never
run a full body parse on its request path, but must still surface a
document's frontmatter + H1 (``id``/``title``/``status``) immediately, so
``total`` is complete from call one. The dirty stage's own ``parse_fn``
(:func:`_parse_frontmatter_summary`) is deliberately *not* a full
``parse_feat`` call: it runs the identical two-step frontmatter derivation
``parse_feat`` itself runs (:func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`
against :class:`~biz.dfch.specmgr.feat.models.v1.FeatFrontmatter`, reusing
``parse_feat``'s own ``_stringify_metadata`` helper so tier-1 YAML/frontmatter-
schema error text is byte-identical to ``parse_feat``'s by construction),
followed by a cheap, non-full-parsing H1 scan
(:func:`~biz.dfch.specmgr.general.tools._similarity_text.first_h1`) plus the
``^Feature: .+$`` alias check every ``Feature`` body also enforces -- never a
call into ``models.md`` body-parsing machinery. A missing or wrong-shape H1
raises a dirty-stage-specific ``AssertionError`` (one of
:data:`~biz.dfch.specmgr.general.tools._doc_cache.CACHEABLE_ERROR_TYPES`), so
it is cached and surfaced exactly like any other parse failure -- just
with text that does not (yet) match ``parse_feat``'s own body-aware error
message (the documented tier-2 limitation; see
``feat.tools.list_feat``'s own docstring for the three-tier contract this
feeds).

Both ``DocCache`` instances get the same reconcile/invalidate/move/reset
wiring -- the dirty-stage wrapper functions below
(:func:`read_feat_dirty`/:func:`peek_feat`/:func:`read_feat_dirty_preloaded`/
:func:`invalidate_feat_dirty_cache`/:func:`reconcile_feat_dirty_cache`/
:func:`move_feat_dirty_cache_entry`/:func:`reset_feat_dirty_cache`) mirror the
clean stage's own shape one-for-one, so every write-path call site that
warms/invalidates/moves the clean cache does the same for the dirty one
(Task 110.130).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ...general.tools._doc_cache import DocCache
from ...general.tools._similarity_text import first_h1
from ...models.md._frontmatter_parse import parse_frontmatter
from ..models.v1 import FeatDocument, FeatFrontmatter, parse_feat
from ..models.v1.parser import _stringify_metadata

__all__ = [
    "FeatFrontmatterSummary",
    "invalidate_feat_cache",
    "invalidate_feat_dirty_cache",
    "move_feat_cache_entry",
    "move_feat_dirty_cache_entry",
    "peek_feat",
    "read_feat",
    "read_feat_dirty",
    "read_feat_dirty_preloaded",
    "reconcile_feat_cache",
    "reconcile_feat_dirty_cache",
    "reset_feat_cache",
    "reset_feat_dirty_cache",
]

#: Module-level singleton, one per process, for the lifetime of the process
#: (mirrors ``_lock.py``'s ``_locks`` registry). See the module docstring.
_cache: DocCache[FeatDocument] = DocCache()

#: The "dirty" (frontmatter-stage) singleton (feat-187-list-feat-timeout,
#: Task 110.100) -- a second, independent :class:`DocCache` instance keyed
#: by the same ``README.md`` paths as :data:`_cache`, but caching only the
#: cheap :class:`FeatFrontmatterSummary` payload, never a full
#: :class:`FeatDocument`.
_dirty_cache: DocCache[FeatFrontmatterSummary] = DocCache()

#: The literal alias every well-formed ``Feature`` H1 heading line must
#: match (mirrors ``Feature``'s own ``@alias(value="^Feature: .+$",
#: type=AliasType.REGEX)`` in ``feat/models/v1/body.py`` -- a plain
#: ``re.match`` here is sufficient and avoids importing the body model's
#: alias machinery/a circular import).
_FEATURE_H1_ALIAS_PATTERN = re.compile(r"^Feature: .+$")


@dataclass(frozen=True)
class FeatFrontmatterSummary:
    """The dirty stage's own frozen frontmatter+H1 payload (feat-187-list-feat-timeout, Task 110.100).

    Deliberately minimal: only what a frontmatter-plus-H1 scan can produce
    without ever touching the body's deeper structure. ``ref``/``path`` are
    NOT part of this payload -- those are folder-derived facts
    ``list_feat`` already has independently of either cache stage.

    Attributes:
        id: The document's frontmatter ``id`` (``None`` for the rare
            document whose frontmatter omits it entirely -- mirrors
            ``MarkdownFrontmatter.id``'s own ``str | None`` type).
        status: The document's frontmatter ``status``.
        title: The scanned H1's *full* heading text (e.g. ``"Feature: My
            Title"``) -- mirrors ``Feature.text``'s own contract (the whole
            heading line, not just the free-form title after the colon);
            callers needing just the free-form part call
            :func:`~biz.dfch.specmgr.feat.tools._paths.feature_title` on it,
            exactly as a clean-stage ``FeatDocument.body.text`` read would.
    """

    id: str | None
    status: str
    title: str


def _parse(text: str) -> FeatDocument:
    """Parse ``text`` into a :class:`FeatDocument` (the clean cache's own ``parse_fn``).

    Phase 6: text in, not ``Path``. Receives the exact text
    :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.read`
    already read (and hashed) for this same call -- this function must not
    re-read the file itself (feat-107-doc-cache Phase 6, REQ-007: closes the
    hash/parse TOCTOU race the previous two-independent-reads shape had).
    """
    assert isinstance(text, str), type(text)

    result = parse_feat(text)
    return result


def _parse_frontmatter_summary(text: str) -> FeatFrontmatterSummary:
    """Parse ``text`` into a :class:`FeatFrontmatterSummary` (the dirty cache's own ``parse_fn``, Task 110.100).

    Runs the exact same :func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`
    call :func:`~biz.dfch.specmgr.feat.models.v1.parse_feat` itself makes
    (reusing its own ``_stringify_metadata`` helper, so tier-1 YAML/
    frontmatter-schema error text is byte-identical by construction), then a
    cheap, non-full-parsing H1 scan (:func:`~biz.dfch.specmgr.general.tools._similarity_text.first_h1`)
    plus the ``^Feature: .+$`` alias check -- never a call into
    ``models.md`` body-parsing machinery.

    Parameters
    ----------
    text:
        The complete file content, exactly as read from disk.

    Returns
    -------
    FeatFrontmatterSummary
        The derived frontmatter+H1 summary payload.

    Raises
    ------
    yaml.YAMLError
        For malformed frontmatter YAML (tier 1) -- propagated unchanged
        from :func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`.
    pydantic.ValidationError
        For a frontmatter schema violation (tier 1) -- propagated unchanged.
    AssertionError
        For a missing or wrong-shape H1 (tier 2) -- a dirty-stage-specific
        message that does not (yet) match ``parse_feat``'s own body-aware
        error text for the same defect (the documented tier-2 limitation).
    """
    assert isinstance(text, str), type(text)

    fm, body = parse_frontmatter(text, FeatFrontmatter, domain="feat", stringify_metadata=_stringify_metadata)
    heading = first_h1(body)
    assert heading is not None, (
        "feat dirty-stage scan: the body carries no level-1 heading (ATX or setext) at all -- "
        "a feature document's H1 must be `# Feature: <title>`."
    )
    assert _FEATURE_H1_ALIAS_PATTERN.match(heading) is not None, (
        f"feat dirty-stage scan: the body's first level-1 heading {heading!r} does not match "
        f"the required `^Feature: .+$` shape."
    )
    result = FeatFrontmatterSummary(id=fm.id, status=fm.status, title=heading)
    return result


def read_feat(path: Path) -> FeatDocument:
    """Read and parse the feature document at ``path``, through the cache.

    A file is only ever re-parsed when its on-disk content hash no longer
    matches the hash recorded at the last read of ``path`` (ADR
    bfd76370-b59b-4d65-b550-a969f6c93c9d); otherwise the cached result (or
    re-raised cached failure) is returned without re-invoking
    :func:`~biz.dfch.specmgr.feat.models.v1.parse_feat`.

    Parameters
    ----------
    path:
        The filesystem path to the feature's ``README.md`` file.

    Returns
    -------
    FeatDocument
        The cached or freshly-parsed, validated document.
    """
    result = _cache.read(path, _parse)
    return result


def invalidate_feat_cache(path: Path) -> None:
    """Drop ``path``'s cached entry, if present.

    Called by the generic ``delete`` tool's ``feat`` adapter immediately
    after a successful ``shutil.rmtree(folder)`` (REQ-004), so a deleted
    document's stale cache entry is never served. ``path`` is the cached
    ``README.md`` file path (the cache's own key), not the containing
    folder ``rmtree`` actually removed.

    Parameters
    ----------
    path:
        The filesystem path whose cache entry to drop (the feature's
        ``README.md`` file, not its containing folder).
    """
    _cache.invalidate(path)


def reconcile_feat_cache(live_paths: Iterable[Path]) -> None:
    """Drop every cached entry whose path is not in ``live_paths`` (REQ-005).

    Called before any per-file work in ``list_feat`` (there is no directory
    scan in ``find_feat_path_by_id`` itself to reconcile against -- see this
    domain's own ``_paths.py`` docstring for why: the shortcut-only lookup
    never scans), so a folder deleted outside specmgr's own tooling does
    not leak in memory indefinitely.

    Parameters
    ----------
    live_paths:
        The current, live set of on-disk ``README.md`` paths for the
        ``feat`` domain.
    """
    _cache.reconcile(live_paths)


def move_feat_cache_entry(old_path: Path, new_path: Path) -> None:
    """Relocate ``old_path``'s cache entry (if present) to ``new_path``.

    Called by ``set_feat_id`` as the *last* step, only after
    ``write_feat_file(new_path, ...)`` has already succeeded -- never at the
    earlier ``old_path.parent.rename(new_path.parent)`` step -- so a failure
    between the rename and the write never leaves a cache entry addressing
    a file that was never actually written (REQ-004). Thin wrapper over
    :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.move`.

    Parameters
    ----------
    old_path:
        The feature's previous ``README.md`` path (the cache's old key).
    new_path:
        The feature's new ``README.md`` path (the cache's new key).
    """
    _cache.move(old_path, new_path)


def reset_feat_cache() -> None:
    """Clear every cached entry.

    Test-only: not for production use. See the module docstring's "Test
    isolation" section.
    """
    _cache.reset()


def peek_feat(path: Path, text: str) -> FeatDocument | Exception | None:
    """Peek the clean (full-parse) cache for ``path`` against already-read ``text``, without parsing.

    Thin wrapper over :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.peek_preloaded`
    on the clean :data:`_cache` singleton (feat-187-list-feat-timeout, Task
    110.105/110.110) -- ``list_feat``'s request path calls this first, with
    the one ``text`` it already read for ``path``, before falling back to
    :func:`read_feat_dirty_preloaded` on a miss (``None``).

    Parameters
    ----------
    path:
        The feature's ``README.md`` path.
    text:
        The exact text already read from ``path`` -- never re-read here.

    Returns
    -------
    FeatDocument | Exception | None
        A fresh copy of the cached document, a fresh reconstruction of a
        cached parse-failure exception (returned, not raised), or ``None``
        on a miss (no entry yet, or ``text``'s hash does not match the
        entry's own).
    """
    result = _cache.peek_preloaded(path, text)
    return result


def read_feat_dirty(path: Path) -> FeatFrontmatterSummary:
    """Read and derive the frontmatter+H1 summary at ``path``, through the dirty-stage cache.

    Reads ``path`` itself (one file read) and parses through
    :data:`_dirty_cache` via :func:`_parse_frontmatter_summary` -- the
    warmup's own frontmatter phase (``feat.tools._warmup.warmup_feat_caches``)
    and every write-path call site (Task 110.130) call this to warm the
    dirty stage for a path whose text they have not already read in hand.

    Parameters
    ----------
    path:
        The filesystem path to the feature's ``README.md`` file.

    Returns
    -------
    FeatFrontmatterSummary
        The cached or freshly-derived frontmatter+H1 summary.
    """
    result = _dirty_cache.read(path, _parse_frontmatter_summary)
    return result


def read_feat_dirty_preloaded(path: Path, text: str) -> FeatFrontmatterSummary:
    """Read-or-derive the dirty-stage summary for ``path``, given already-read ``text``.

    Thin wrapper over :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.read_preloaded`
    on :data:`_dirty_cache` (feat-187-list-feat-timeout, Task 110.105/110.110)
    -- ``list_feat``'s request path calls this on a clean-stage miss
    (:func:`peek_feat` returned ``None``), passing the same ``text`` it
    already read for ``path`` -- never a second, independent file read.

    Parameters
    ----------
    path:
        The feature's ``README.md`` path.
    text:
        The exact text already read from ``path``.

    Returns
    -------
    FeatFrontmatterSummary
        The cached or freshly-derived frontmatter+H1 summary.

    Raises
    ------
    yaml.YAMLError
        For malformed frontmatter YAML (tier 1).
    pydantic.ValidationError
        For a frontmatter schema violation (tier 1).
    AssertionError
        For a missing or wrong-shape H1 (tier 2).
    """
    result = _dirty_cache.read_preloaded(path, text, _parse_frontmatter_summary)
    return result


def invalidate_feat_dirty_cache(path: Path) -> None:
    """Drop ``path``'s cached dirty-stage entry, if present.

    Called alongside :func:`invalidate_feat_cache` from every write-path
    call site that invalidates the clean cache (Task 110.130), so a
    deleted document's stale dirty-stage entry is never served either.

    Parameters
    ----------
    path:
        The filesystem path whose dirty-stage cache entry to drop (the
        feature's ``README.md`` file, not its containing folder).
    """
    _dirty_cache.invalidate(path)


def reconcile_feat_dirty_cache(live_paths: Iterable[Path]) -> None:
    """Drop every cached dirty-stage entry whose path is not in ``live_paths``.

    Called alongside :func:`reconcile_feat_cache` -- both ``list_feat`` and
    the warmup's own frontmatter phase call this before any per-file work,
    so a folder deleted outside specmgr's own tooling does not leak in
    memory indefinitely in either cache stage.

    Parameters
    ----------
    live_paths:
        The current, live set of on-disk ``README.md`` paths for the
        ``feat`` domain.
    """
    _dirty_cache.reconcile(live_paths)


def move_feat_dirty_cache_entry(old_path: Path, new_path: Path) -> None:
    """Relocate ``old_path``'s dirty-stage cache entry (if present) to ``new_path``.

    Called alongside :func:`move_feat_cache_entry` from ``set_feat_id``,
    only after ``write_feat_file(new_path, ...)`` has already succeeded
    (Task 110.130) -- thin wrapper over
    :meth:`~biz.dfch.specmgr.general.tools._doc_cache.DocCache.move`.

    Parameters
    ----------
    old_path:
        The feature's previous ``README.md`` path (the dirty cache's old
        key).
    new_path:
        The feature's new ``README.md`` path (the dirty cache's new key).
    """
    _dirty_cache.move(old_path, new_path)


def reset_feat_dirty_cache() -> None:
    """Clear every cached dirty-stage entry.

    Test-only: not for production use. See the module docstring's "Test
    isolation" section.
    """
    _dirty_cache.reset()
