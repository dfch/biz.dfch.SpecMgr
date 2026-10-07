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

"""The strict first-set-wins validation chain + the frozen result model (rulebook §3).

Selection is strict and configuration-driven over **exactly three** env vars
(§3.1 — no defaults, no PATH discovery, no opt-in flags): the first of
``SPECMGR_PLANTUML_JAR`` → ``SPECMGR_PLANTUML_BIN`` → ``SPECMGR_PLANTUML_URL``
that is **set** is the *only* source used. **No fall-through on
misconfiguration** (the privacy invariant, ADR 7a626b12): a set-but-unavailable
JAR with a set public URL never contacts the public URL — a typo'd local
source must never silently send diagram content to plantuml.com. A
set-but-unavailable source is a **hard validation failure** (``source_state``
= ``misconfigured``/``unavailable``/``inconclusive``, ``reason`` + ``fix_hint``
naming the exact problem, no write, no other source, no network); only the
all-unset state degrades — to the structure-only floor
(``source_state="none"``, ``available=False``).

The chain always runs the structure checker first; on structure red the
parser is **never called** (no subprocess, no network — the frozen
short-circuit, §3.7) and the result carries the structure errors with
``valid=None``/``rendered=None``/``checked_by="structure"`` (``None`` means
"not run", never "run and failed").

The result model (§3.6) is a non-raising structured result — the ADR 519d1206
chain precedent: :func:`validate_plantuml` never raises for validation
content; it returns a :class:`PlantumlValidationResult` carrying the verdict.
Import-free and stdlib-only (ADR 7a626b12).
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

from . import backends, structure, url
from .structure import Finding

__all__ = [
    "CHECKED_BY_STRUCTURE",
    "ENV_VAR_BIN",
    "ENV_VAR_JAR",
    "ENV_VAR_URL",
    "SOURCE_BIN",
    "SOURCE_JAR",
    "SOURCE_URL",
    "STATE_INCONCLUSIVE",
    "STATE_MISCONFIGURED",
    "STATE_NONE",
    "STATE_OK",
    "STATE_UNAVAILABLE",
    "PlantumlValidationResult",
    "SourceAvailability",
    "clear_probe_caches",
    "select_source",
    "source_availability",
    "validate_plantuml",
]

# --- the exactly-three source env vars (rulebook §3.1) -------------------------

ENV_VAR_JAR = "SPECMGR_PLANTUML_JAR"
ENV_VAR_BIN = "SPECMGR_PLANTUML_BIN"
ENV_VAR_URL = "SPECMGR_PLANTUML_URL"

#: The selection order (rulebook §3.2): JAR → BIN → URL; the first **set**
#: variable wins and is the only source used.
_SOURCE_ORDER: tuple[tuple[str, str], ...] = (
    ("jar", ENV_VAR_JAR),
    ("bin", ENV_VAR_BIN),
    ("url", ENV_VAR_URL),
)

SOURCE_JAR = "jar"
SOURCE_BIN = "bin"
SOURCE_URL = "url"

#: ``checked_by`` values (the §3.6 vocabulary).
CHECKED_BY_STRUCTURE = "structure"

#: ``source_state`` values (the §3.6 vocabulary).
STATE_OK = "ok"
STATE_MISCONFIGURED = "misconfigured"
STATE_UNAVAILABLE = "unavailable"
STATE_INCONCLUSIVE = "inconclusive"
STATE_NONE = "none"

#: The reason text for the all-unset floor (the structure-only state, §3.4).
_ALL_UNSET_REASON = (
    "no SPECMGR_PLANTUML_* source configured (SPECMGR_PLANTUML_JAR, SPECMGR_PLANTUML_BIN, and "
    "SPECMGR_PLANTUML_URL are all unset) — structure-only floor (rulebook §3.4)"
)


def select_source(env: Mapping[str, str] | None = None) -> tuple[str, str] | None:
    """Select the validation source: first SET of JAR → BIN → URL wins (§3.2).

    The returned ``(kind, value)`` is the **only** source the chain will ever
    use — there is no fall-through to any other variable. A variable that is
    present but empty is still *set* (it selects, and the probe then reports
    it as misconfigured — strictness over convenience).

    Parameters
    ----------
    env:
        The environment mapping to read (defaults to ``os.environ``); the
        parameter exists so tests can pin the configuration without touching
        the process environment.

    Returns
    -------
    tuple[str, str] | None
        ``(kind, value)`` for the first set variable, or ``None`` when all
        three are unset (the structure-only floor, §3.4).
    """
    source_env = os.environ if env is None else env
    for kind, var in _SOURCE_ORDER:
        value = source_env.get(var)
        if value is not None:
            result = (kind, value)
            return result
    return None


# --- the §3.6 result model (frozen shape — non-raising) ------------------------


@dataclass
class PlantumlValidationResult:
    """The non-raising validation result (rulebook §3.6 — the frozen shape).

    ``None`` on ``valid``/``rendered`` means **"not run"** — never "run and
    failed". On a structure-red short-circuit (§3.7) and on the all-unset
    floor, ``checked_by`` is ``"structure"``, ``valid``/``rendered`` are
    ``None``, and ``source_state``/``available`` report the source situation
    (``"none"`` + ``False`` when the source was never probed — all-unset, or
    the short-circuit with or without a configured source; the ``reason``
    text disambiguates the two).
    """

    structure_ok: bool
    valid: bool | None
    rendered: bool | None
    checked_by: str
    errors: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    source_state: str = STATE_NONE
    available: bool = False
    reason: str | None = None
    fix_hint: str | None = None


@dataclass(frozen=True)
class SourceAvailability:
    """The selected source's canary state (the env-gate helper, rulebook §3.5).

    Attributes:
        kind: ``"jar"``/``"bin"``/``"url"`` or ``None`` (all unset).
        value: the configured value (``None`` when all unset).
        available: the canary answered (``False`` for the all-unset floor and
            for every set-but-unavailable source).
        reason: why the source is not available (``None`` when available).
        fix_hint: the concrete fix (``None`` when available).
    """

    kind: str | None
    value: str | None
    available: bool
    reason: str | None = None
    fix_hint: str | None = None


def source_availability(env: Mapping[str, str] | None = None) -> SourceAvailability:
    """Select the source and probe its canary (memoised per process).

    The one entry point the test-suite env gate (:mod:`tests.conftest`) and
    the later ``specmgr://config`` plantuml section build on: selection per
    §3.2, then exactly one canary round-trip through the selected source
    (memoised — a second call in the same process costs nothing). No
    fall-through: only the selected source is ever probed.
    """
    selected = select_source(env)
    if selected is None:
        result = SourceAvailability(
            kind=None,
            value=None,
            available=False,
            reason=_ALL_UNSET_REASON,
            fix_hint=(
                "set exactly one of SPECMGR_PLANTUML_JAR (a plantuml.jar path), SPECMGR_PLANTUML_BIN "
                "(an executable speaking the §4 contract), or SPECMGR_PLANTUML_URL (a server base URL, "
                "prefix included) — rulebook §3.1"
            ),
        )
        return result
    kind, value = selected
    probe = url.probe_url(value) if kind == SOURCE_URL else backends.probe_local(kind, value)
    result = SourceAvailability(
        kind=kind,
        value=value,
        available=probe.ok,
        reason=None if probe.ok else probe.reason,
        fix_hint=None if probe.ok else probe.fix_hint,
    )
    return result


def clear_probe_caches() -> None:
    """Drop every memoised canary probe (test hook — the session gate re-probes).

    Clears both the jar/bin probe cache (:func:`backends.clear_probe_cache`)
    and the URL probe cache (:func:`url.clear_probe_cache`), so a changed
    environment is re-probed from scratch. Never called from ``src/``.
    """
    backends.clear_probe_cache()
    url.clear_probe_cache()


# --- the chain itself -----------------------------------------------------------


def validate_plantuml(text: str, env: Mapping[str, str] | None = None) -> PlantumlValidationResult:
    """Validate one diagram through the strict chain (rulebook §3).

    Always: the structure check first (preflight mode when a source is
    selected — the lenient set as warnings; standalone mode on the all-unset
    floor — the lenient set promoted to errors). On structure red: the frozen
    short-circuit (§3.7) — the parser is never called (no subprocess, no
    network) and the result carries the structure errors with
    ``valid=None``/``rendered=None``/``checked_by="structure"``. On structure
    green: the selected source's canary (memoised) gates the real check —
    set-but-unavailable is a hard failure (``source_state`` + ``reason`` +
    ``fix_hint``, no write, no other source, no network); available runs the
    authoritative check (+ render proof) and reports its verdict.

    Never raises for validation content (the non-raising structured-result
    precedent); configuration is read from ``env`` (default ``os.environ``).
    """
    assert isinstance(text, str), type(text)

    selected = select_source(env)
    check_mode = structure.MODE_PREFLIGHT if selected is not None else structure.MODE_STANDALONE
    structure_result = structure.check_structure(text, check_mode)

    if not structure_result.ok:
        # the frozen short-circuit (§3.7): no subprocess, no network, no
        # canary probe — 'none' here means "no source state was determined"
        result = PlantumlValidationResult(
            structure_ok=False,
            valid=None,
            rendered=None,
            checked_by=CHECKED_BY_STRUCTURE,
            errors=structure_result.errors,
            warnings=structure_result.warnings,
            source_state=STATE_NONE,
            available=False,
            reason="the structure check failed; no validation source was called (the frozen chain "
            "short-circuit — rulebook §3.7)",
        )
        return result

    if selected is None:
        # the all-unset floor (§3.4): the structure checker alone
        result = PlantumlValidationResult(
            structure_ok=True,
            valid=None,
            rendered=None,
            checked_by=CHECKED_BY_STRUCTURE,
            errors=[],
            warnings=structure_result.warnings,
            source_state=STATE_NONE,
            available=False,
            reason=_ALL_UNSET_REASON,
        )
        return result

    kind, value = selected
    if kind == SOURCE_URL:
        probe = url.probe_url(value)
    else:
        probe = backends.probe_local(kind, value)

    if not probe.ok:
        # set-but-unavailable = hard failure (§3.3): no other source, no
        # network, no write — the exact reason + fix hint naming the problem
        result = PlantumlValidationResult(
            structure_ok=True,
            valid=None,
            rendered=None,
            checked_by=kind,
            errors=[],
            warnings=structure_result.warnings,
            source_state=probe.source_state,
            available=False,
            reason=probe.reason,
            fix_hint=probe.fix_hint,
        )
        return result

    if kind == SOURCE_URL:
        verdict = url.validate_url(value, text)
        result = PlantumlValidationResult(
            structure_ok=True,
            valid=verdict.valid,
            rendered=verdict.rendered,
            checked_by=kind,
            errors=verdict.errors if verdict.errors is not None else [],
            warnings=structure_result.warnings,
            source_state=verdict.source_state,
            available=True,
            reason=verdict.reason,
            fix_hint=verdict.fix_hint,
        )
        return result

    assert probe.check_flag is not None  # an ok local probe always resolved its flag
    verdict = backends.validate_local(kind, value, text, probe.check_flag)
    result = PlantumlValidationResult(
        structure_ok=True,
        valid=verdict.valid,
        rendered=verdict.rendered,
        checked_by=kind,
        errors=verdict.errors,
        warnings=structure_result.warnings,
        source_state=STATE_OK,
        available=True,
        reason=verdict.reason,
        fix_hint=None,
    )
    return result
