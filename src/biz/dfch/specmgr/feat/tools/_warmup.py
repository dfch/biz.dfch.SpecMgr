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

"""The ``feat`` domain's own two-phase cache warmup (feat-187-list-feat-timeout, Task 110.120).

Fixes GitHub issue #187's ``list_feat`` cold-scan timeout (ADR
3982712a-a46b-4b2b-809f-9c6925a49b44) from the background: :func:`warmup_feat_caches`
is a plain, synchronously runnable function -- independent of any thread --
that runs two phases over the live ``feat`` corpus, in order:

1. **Frontmatter phase** -- every live ``*/README.md`` read through the
   dirty (frontmatter-stage) cache (:func:`~biz.dfch.specmgr.feat.tools._cache.read_feat_dirty`).
   Cheap: a PyYAML frontmatter parse plus a plain-text H1 line scan, no
   markdown-it body tokenizing. Completes in well under a second for this
   repo's own corpus (measured at ADR-authoring time).
2. **Full-parse phase** -- the same live paths, this time through the
   clean (full-parse) cache (:func:`~biz.dfch.specmgr.feat.tools._cache.read_feat`).
   Expensive (on the order of several minutes for this repo's own corpus),
   entirely in the background, off ``list_feat``'s/``get_feat``'s own
   request paths.

Both phases are **crash-contained**: a cacheable parse failure
(:data:`~biz.dfch.specmgr.general.tools._doc_cache.CACHEABLE_ERROR_TYPES`)
is the normal, expected outcome for a file that fails to parse -- it is
stored by the cache exactly like any on-demand read would store it, counted
in the phase's own result, and never logged as a warning. Any other,
genuinely unexpected exception (e.g. a file vanishing mid-warmup, a
transient ``OSError``) is logged via the standard library ``logging``
module at ``WARNING`` (the path plus ``exc_info=True``, mirroring the
feat-134 ``specmgr-similarity-warmup`` thread's own precedent) and
swallowed -- it never stops the phase from reaching the remaining paths,
and never propagates out of :func:`warmup_feat_caches` at all.

:func:`warmup_feat_caches` is deliberately **not** itself a thread -- the
thread that runs it (named ``specmgr-startup-warmup``) is spawned by the
cross-cutting ``general.tools._startup_warmup.start_startup_warmup``
spawner, which sequences this function's two phases ahead of the
pre-existing feat-134 similarity warmup (``general.tools._similarity_search.warmup_similarity_cache``).
Being a plain function lets tests (and any future caller) drive both
phases directly and synchronously, without a real background thread.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from ...general.tools._doc_cache import CACHEABLE_ERROR_TYPES
from ._cache import read_feat, read_feat_dirty, reconcile_feat_cache, reconcile_feat_dirty_cache
from ._paths import feat_base_dir, iter_feat_paths

__all__ = ["FeatWarmupResult", "WarmupPhaseResult", "warmup_feat_caches"]

_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WarmupPhaseResult:
    """One warmup phase's own small summary (Task 110.120, REQ-007).

    Attributes:
        paths_warmed: The number of candidate paths that ended up with a
            cache entry -- a successful parse or one of
            :data:`~biz.dfch.specmgr.general.tools._doc_cache.CACHEABLE_ERROR_TYPES`
            stored as a cacheable failure. Does NOT count a path skipped
            due to an unexpected, non-cacheable exception (logged and
            swallowed instead).
        parse_failures: The subset of ``paths_warmed`` that were a
            cacheable parse failure rather than a success.
    """

    paths_warmed: int
    parse_failures: int


@dataclass(frozen=True)
class FeatWarmupResult:
    """The full :func:`warmup_feat_caches` return value: one result per phase (Task 110.120, REQ-007)."""

    frontmatter_phase: WarmupPhaseResult
    full_parse_phase: WarmupPhaseResult


def _run_phase(paths: Iterable[Path], read: Callable[[Path], object], phase_name: str) -> WarmupPhaseResult:
    """Run one warmup phase's own ``read`` callback over ``paths``, crash-contained.

    Parameters
    ----------
    paths:
        The live paths to warm.
    read:
        The phase's own cache-backed reader (:func:`~biz.dfch.specmgr.feat.tools._cache.read_feat_dirty`
        for the frontmatter phase, :func:`~biz.dfch.specmgr.feat.tools._cache.read_feat`
        for the full-parse phase).
    phase_name:
        A short, human-readable phase name for the warning log line.

    Returns
    -------
    WarmupPhaseResult
        This phase's own summary.
    """
    paths_warmed = 0
    parse_failures = 0
    for path in paths:
        try:
            read(path)
        except CACHEABLE_ERROR_TYPES:
            # The normal, expected outcome for a file that fails to parse -- already stored by
            # the cache exactly like any on-demand read would store it. Not a crash.
            paths_warmed += 1
            parse_failures += 1
        except Exception:  # pylint: disable=broad-except -- crash containment (REQ-007): never stops the phase.
            _logger.warning("%s: unexpected failure warming %s", phase_name, path, exc_info=True)
            continue
        else:
            paths_warmed += 1
    result = WarmupPhaseResult(paths_warmed=paths_warmed, parse_failures=parse_failures)
    return result


def warmup_feat_caches() -> FeatWarmupResult:
    """Run both ``feat`` warmup phases synchronously, crash-contained, over the live corpus.

    Scans the live ``feat`` base directory once (:func:`~biz.dfch.specmgr.feat.tools._paths.iter_feat_paths`),
    reconciles both cache stages against that live listing (so a folder
    deleted outside specmgr's own tooling does not leak in memory
    indefinitely in either stage, mirroring ``list_feat``'s own
    reconcile-on-scan, REQ-005), then runs the frontmatter phase followed
    by the full-parse phase over the same path list -- never raising, and
    never blocking on anything other than the two phases' own (bounded,
    cache-backed) reads.

    Returns
    -------
    FeatWarmupResult
        Both phases' own small summaries, for the phase-finish log lines
        and test assertions.
    """
    paths = list(iter_feat_paths(feat_base_dir()))
    reconcile_feat_dirty_cache(paths)
    reconcile_feat_cache(paths)

    _logger.info("feat frontmatter warmup phase starting: %d candidate path(s)", len(paths))
    frontmatter_result = _run_phase(paths, read_feat_dirty, "feat frontmatter warmup phase")
    _logger.info(
        "feat frontmatter warmup phase finished: %d path(s) warmed, %d parse failure(s)",
        frontmatter_result.paths_warmed,
        frontmatter_result.parse_failures,
    )

    _logger.info("feat full-parse warmup phase starting: %d candidate path(s)", len(paths))
    full_parse_result = _run_phase(paths, read_feat, "feat full-parse warmup phase")
    _logger.info(
        "feat full-parse warmup phase finished: %d path(s) warmed, %d parse failure(s)",
        full_parse_result.paths_warmed,
        full_parse_result.parse_failures,
    )

    result = FeatWarmupResult(frontmatter_phase=frontmatter_result, full_parse_phase=full_parse_result)
    return result
