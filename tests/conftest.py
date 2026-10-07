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

Three responsibilities (feat-185-uc-diagrams, Phase 110 / Task 110.100; the
render-proof helpers added in Phase 145):

1. **``.env`` loading** — the gitignored repo-root ``.env`` (the local
   configuration surface for ``SPECMGR_PLANTUML_*``; never committed) is
   loaded at collection time, mirroring ``cli.py:_load_default_dotenv``'s
   **dual lookup**: walk upward from this file's own location first (so a
   checkout with a root ``.env`` works from any pytest invocation
   directory), then from CWD as the fallback. The load is explicit
   ``override=False``: a developer's real environment always wins over
   ``.env`` (e.g. a targeted ``SPECMGR_PLANTUML_BIN=... pytest ...`` run
   overrides the ``.env``'s URL). The load is skipped entirely when the
   ``SPECMGR_TESTS_NO_DOTENV`` sentinel env var is set (the
   ``specmgr coverage-badge`` pre-commit hook's CI source-less re-run,
   feat-185-uc-diagrams Phase 145 — the committed coverage badge must match
   the CI condition where no ``SPECMGR_PLANTUML_*`` is configured, so that
   re-run must not pick the source up from the local ``.env``).

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

3. **Render-proof helpers** (Phase 145, the user-approved 2026-10-06
   amendment B): :func:`assert_rendered_svg` is the render-proof contract —
   every "rendered" assertion in this feature's tests checks the SVG **body**
   for the expected diagram text and the absence of the crash markers, never
   ``is_real_svg`` alone (the pre-amendment classifier accepted a PlantUML
   crash page as a real render); :func:`render_proof_body` runs the selected
   source's own render proof and returns the body bytes for that assertion.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv

from biz.dfch.specmgr.plantuml import backends, chain, url

# ---------------------------------------------------------------------------
# .env loading (mirrors cli.py:_load_default_dotenv's dual lookup)
# ---------------------------------------------------------------------------


#: Sentinel env var: when set, the ``.env`` load below is skipped entirely —
#: the suite runs under the CI (source-less) condition whatever the local
#: ``.env`` configures. Used by the ``specmgr coverage-badge`` pre-commit
#: hook's source-less re-run (feat-185-uc-diagrams Phase 145 — the committed
#: badge matches the CI condition where no ``SPECMGR_PLANTUML_*`` is set).
#: ``cli.py`` carries its own copy of the same sentinel (``cli
#: .NO_DOTENV_SENTINEL``) because its module-level ``.env`` load runs in
#: every test process that imports it — the two names are drift-pinned in
#: ``tests/plantuml/test_source_gate.py``.
NO_DOTENV_SENTINEL = "SPECMGR_TESTS_NO_DOTENV"


def _load_default_dotenv() -> None:
    """Load ``.env`` walking upward from this file, then from CWD as fallback.

    ``override=False`` is explicit (``load_dotenv``'s default, pinned here so
    a future signature change cannot silently invert it): the developer's
    real environment always wins over the gitignored ``.env``. The load is
    skipped entirely when the :data:`NO_DOTENV_SENTINEL` env var is set (the
    CI source-less condition, see its docstring).
    """
    if os.environ.get(NO_DOTENV_SENTINEL):
        return
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


# ---------------------------------------------------------------------------
# render-proof helpers (feat-185-uc-diagrams Phase 145, 2026-10-06 amendment)
# ---------------------------------------------------------------------------


def assert_rendered_svg(body: bytes, expected_text: str) -> None:
    """Assert ``body`` is a TRUE render of the diagram carrying ``expected_text``.

    The Phase 145 render-proof contract (the user-approved 2026-10-06
    amendment B): every "rendered" assertion in this feature's tests checks
    the SVG **body** for the expected diagram text **and** the absence of the
    crash markers — never ``is_real_svg`` alone. (The pre-amendment
    classifier accepted PlantUML's crash page — 200 + "…has crashed." + the
    embedded exception trace — as a real render, so a shape-crash read as
    green; rulebook §5.2 crash line.)
    """
    text = body.decode("utf-8", errors="replace")
    assert "has crashed" not in text, "the SVG body is a PlantUML crash page (rulebook §5.2)"
    assert "ClassCastException" not in text, "the SVG body carries a crash exception trace"
    assert expected_text in text, (
        f"expected diagram text {expected_text!r} is not present in the rendered SVG body "
        "(the render did not draw the diagram)"
    )


def render_proof_body(kind: str, value: str, diagram: str) -> bytes:
    """The selected source's render-proof SVG body for a valid diagram.

    Runs the source's own render proof (the URL backend's ``/svg/`` body /
    the jar/bin ``--svg`` temp file) and returns the bytes for
    :func:`assert_rendered_svg`. Raises ``AssertionError`` when the proof was
    not rendered (the test's expectation is already wrong then).
    """
    if kind == "url":
        verdict = url.validate_url(value, diagram)
        assert verdict.rendered is True and verdict.proof_path, f"the URL proof did not render: {verdict}"
        assert verdict.proof_path is not None
        return Path(verdict.proof_path).read_bytes()
    assert kind in ("jar", "bin"), kind
    probe = backends.probe_local(kind, value)
    assert probe.ok and probe.check_flag, f"the {kind} source is not available: {probe}"
    verdict = backends.validate_local(kind, value, diagram, probe.check_flag)
    assert verdict.rendered is True and verdict.proof_path, f"the {kind} proof did not render: {verdict}"
    assert verdict.proof_path is not None
    return Path(verdict.proof_path).read_bytes()
