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

"""The unified MCP server startup warmup spawner (feat-187-list-feat-timeout, Task 110.120).

Replaces ``general.tools._similarity_search.start_similarity_warmup`` (now
removed) as the single entry point ``server.py``'s ``_lifespan`` calls at
startup. ``server.py``'s lifespan hook was never actually a no-op -- it
already started feat-134's similarity warmup -- and this module's own
addition (the ``feat`` two-stage cache warmup, GitHub issue #187) would
otherwise be a *second*, independently-scheduled background thread
competing for the GIL with the first one. ADR
3982712a-a46b-4b2b-809f-9c6925a49b44 instead unifies both into a single
daemon thread (``specmgr-startup-warmup``) running three phases, strictly
in order:

1. The ``feat`` frontmatter phase (cheap: frontmatter + H1 only).
2. The ``feat`` full-parse phase (expensive: the full corpus, sequentially).
3. The pre-existing, unchanged feat-134 similarity warmup body
   (:func:`~biz.dfch.specmgr.general.tools._similarity_search.warmup_similarity_cache`).

Both ``feat`` phases live in :func:`~biz.dfch.specmgr.feat.tools._warmup.warmup_feat_caches`,
a plain, synchronously runnable function this module merely calls -- this
module owns only the **gating** (per-phase opt-out flags) and the
**thread** (a single daemon, named and started here), never the phase
bodies themselves.

**Per-phase gating, not per-thread (REQ-007).** :data:`FEAT_WARMUP_DISABLED_ENV_VAR`
(``SPECMGR_FEAT_WARMUP_DISABLED``, new) gates phases 1-2; the pre-existing
``SPECMGR_SIMILARITY_DISABLED`` (:data:`~biz.dfch.specmgr.general.tools._embedding.SIMILARITY_DISABLED_ENV_VAR`)
gates phase 3 only, unchanged in meaning. When both flags are present, no
thread is started at all -- a true no-op, and the server behaves exactly as
it did before this feature shipped (one of the four flag-combination cases
the lifespan unit test asserts directly, ACC-009).

With the unified thread, at most one heavy, GIL-holding background phase
ever runs at a time during the warmup window (replacing the pre-refinement
design's two independent threads running in parallel) -- see the feature's
own Design Notes for the full GIL-contention analysis.
"""

from __future__ import annotations

import threading

from ... import _envregistry
from ...feat.tools._warmup import warmup_feat_caches
from ._embedding import SIMILARITY_DISABLED_ENV_VAR
from ._similarity_search import warmup_similarity_cache

__all__ = ["FEAT_WARMUP_DISABLED_ENV_VAR", "start_startup_warmup"]

#: Presence-based opt-out flag (any value) gating the ``feat`` frontmatter
#: and full-parse warmup phases only -- the repo's own env-flag convention
#: (mirrors ``SPECMGR_SIMILARITY_DISABLED``). Absent (the default): both
#: ``feat`` phases run.
FEAT_WARMUP_DISABLED_ENV_VAR = "SPECMGR_FEAT_WARMUP_DISABLED"

# The registry record for :data:`FEAT_WARMUP_DISABLED_ENV_VAR` (feat-208,
# Phase 110; the read sites migrated to the registry accessor in Phase
# 130): presence-based (no default -- a set-but-empty value still gates
# the phases: every gate reads the raw ``_envregistry.get(name) is not
# None``, never ``get_with_default``).
_envregistry.register(
    FEAT_WARMUP_DISABLED_ENV_VAR,
    description=(
        "Presence-based opt-out for the feat domain's two background cache-warming phases (frontmatter "
        "and full-parse) of the unified server-startup warmup thread: set to any value to skip both "
        "phases; when set together with SPECMGR_SIMILARITY_DISABLED, no warmup thread is started at "
        "all. Unset by default. Its resolved state is reported by the feat_warmup_disabled field of "
        "the specmgr://config resource."
    ),
    owner="general",
)

#: The unified warmup thread's own name (diagnostics: shows up as its own
#: thread in ``threading.enumerate()``/profilers; a daemon, so it dies with
#: the process -- no shutdown join logic by design, mirroring the
#: feat-134 ``specmgr-similarity-warmup`` thread's own precedent, which
#: this name replaces as the startup entry point).
_WARMUP_THREAD_NAME = "specmgr-startup-warmup"


def _run_all_phases() -> None:
    """The unified thread body: feat frontmatter phase -> feat full-parse phase -> similarity warmup.

    Each phase is independently crash-contained by its own body
    (:func:`~biz.dfch.specmgr.feat.tools._warmup.warmup_feat_caches` and
    :func:`~biz.dfch.specmgr.general.tools._similarity_search.warmup_similarity_cache`
    both already never raise) -- this function adds only the per-phase
    gating, strictly in order.
    """
    if _envregistry.get(FEAT_WARMUP_DISABLED_ENV_VAR) is None:
        warmup_feat_caches()
    if _envregistry.get(SIMILARITY_DISABLED_ENV_VAR) is None:
        warmup_similarity_cache()


def start_startup_warmup() -> threading.Thread | None:
    """Start the unified daemon warmup thread, unless both opt-out flags are set (REQ-007).

    The entry point ``server.py``'s ``_lifespan`` calls at startup (kept
    function-level-imported there, mirroring the predecessor
    ``start_similarity_warmup`` it replaces -- no circular import risk:
    this module's own ``feat.tools``/``general.tools`` imports resolve once
    ``server``'s ``mcp`` object already exists).

    Checks only the two lightweight, synchronous presence flags
    (:data:`FEAT_WARMUP_DISABLED_ENV_VAR`/``SPECMGR_SIMILARITY_DISABLED``):
    when *both* are present, no thread is started at all -- a true no-op,
    and the server runs exactly as it did before this feature shipped.
    Otherwise a single daemon thread is started running
    :func:`_run_all_phases` (which re-checks each flag independently, so a
    single flag disables only its own phase(s)) and returned **without
    joining it** -- server startup is never blocked by either warmup.

    Returns
    -------
    threading.Thread | None
        The started daemon thread, or ``None`` when both opt-out flags are
        present and no thread was started.
    """
    feat_disabled = _envregistry.get(FEAT_WARMUP_DISABLED_ENV_VAR) is not None
    similarity_disabled = _envregistry.get(SIMILARITY_DISABLED_ENV_VAR) is not None
    if feat_disabled and similarity_disabled:
        result: threading.Thread | None = None
        return result

    thread = threading.Thread(target=_run_all_phases, daemon=True, name=_WARMUP_THREAD_NAME)
    thread.start()
    result = thread
    return result
