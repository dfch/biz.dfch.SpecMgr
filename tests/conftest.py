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

"""Repo-root pytest configuration: ``.env`` loading + the PlantUML source-availability gate.

Two responsibilities (feat-185-uc-diagrams, Phase 110 / Task 110.100):

1. **``.env`` loading** — the gitignored repo-root ``.env`` (the local
   configuration surface for ``SPECMGR_PLANTUML_*``; never committed) is
   loaded at collection time, mirroring ``cli.py:_load_default_dotenv``'s
   **dual lookup**: walk upward from this file's own location first (so a
   checkout with a root ``.env`` works from any pytest invocation
   directory), then from CWD as the fallback. The load is explicit
   ``override=False``: a developer's real environment always wins over
   ``.env`` (e.g. a targeted ``SPECMGR_PLANTUML_BIN=... pytest ...`` run
   overrides the ``.env``'s URL).

2. **The source-availability gate** — :func:`plantuml_source` determines the
   selected source per the rulebook §3.2 order (JAR → BIN → URL) and probes
   it ONCE per pytest session (the canary round-trip is memoised per process
   inside the ``plantuml`` package, so every test in the session shares one
   probe; a dead source fails the probe fast — named timeouts on every
   subprocess/HTTP call — and never hangs collection). Test modules gate their
   real-parser tests with :func:`require_plantuml_source`, which skips with a
   reason (ACC-007: ``pytest -rs`` reports it — e.g. "no SPECMGR_PLANTUML_*
   source configured" vs "the canary round-trip through the bin source
   failed: …"), so a checkout with nothing configured skips cleanly while a
   configured dev machine runs the real-parser tests.
"""

from __future__ import annotations

from typing import Any

from dotenv import find_dotenv, load_dotenv

from biz.dfch.specmgr.plantuml import chain

# ---------------------------------------------------------------------------
# .env loading (mirrors cli.py:_load_default_dotenv's dual lookup)
# ---------------------------------------------------------------------------


def _load_default_dotenv() -> None:
    """Load ``.env`` walking upward from this file, then from CWD as fallback.

    ``override=False`` is explicit (``load_dotenv``'s default, pinned here so
    a future signature change cannot silently invert it): the developer's
    real environment always wins over the gitignored ``.env``.
    """
    dotenv_path = find_dotenv(usecwd=False) or find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, verbose=False, override=False)


_load_default_dotenv()

# ---------------------------------------------------------------------------
# the PlantUML source-availability gate (one canary probe per session)
# ---------------------------------------------------------------------------

#: The session memo for :func:`plantuml_source` — one probe per pytest
#: session (per xdist worker process); the probe itself is also memoised
#: inside the ``plantuml`` package per (kind, value), so the two layers agree.
_SOURCE_INFO_CACHE: dict[str, chain.SourceAvailability] = {}


def plantuml_source() -> chain.SourceAvailability:
    """Return the selected validation source's canary state (memoised).

    Selection per rulebook §3.2 (first SET of JAR → BIN → URL; no
    fall-through), then exactly one canary round-trip through the selected
    source. On a checkout with nothing configured this costs a pure
    environment read (no probe at all).
    """
    if "info" not in _SOURCE_INFO_CACHE:
        _SOURCE_INFO_CACHE["info"] = chain.source_availability()
    result: chain.SourceAvailability = _SOURCE_INFO_CACHE["info"]
    return result


def reset_source_gate() -> None:
    """Clear the session memo (test hook — lets a test re-probe a changed env)."""
    _SOURCE_INFO_CACHE.clear()
    chain.clear_probe_caches()


def require_plantuml_source(testcase: Any) -> chain.SourceAvailability:
    """Gate one test on source availability, skipping with a reason when absent.

    The ``skipif``-style helper for real-parser tests (ACC-007): when the
    selected source does not answer its canary, ``testcase.skipTest(...)``
    fires with the exact reason — ``pytest -rs`` reports it. Returns the
    availability info (kind + value) for the test to use.
    """
    info = plantuml_source()
    if not info.available:
        testcase.skipTest(f"PlantUML source gate: {info.reason}")
    return info
