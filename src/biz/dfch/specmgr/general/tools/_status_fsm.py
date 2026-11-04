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

"""The generic ``set_status`` tool's own per-domain status state machine (feat-108-fsm, GitHub issue #108).

The cross-cutting half of feat-108-fsm's design (domain-owned ``_STATUS_TRANSITIONS`` tables plus
a central aggregation): :data:`_STATUS_TRANSITIONS_BY_TYPE` holds one entry per whole-body domain,
keyed to the shared ``general.tools._domains`` registry, and :func:`check_status_transition` is the
single pure check the whole-body ``_set_status_<d>`` adapters in ``set_status.py`` call --
immediately after their own unchanged-status no-op comparison and before the raw-body re-read and
``write_<d>_file`` -- to decide whether the transition from the document's current on-disk status
to the requested target is allowed by that domain's machine. A rejection is always pre-write:
nothing is persisted and ``updated`` is not bumped.

Two distinct error surfaces (the feature's own Design Notes): (A) the pre-existing pre-dispatch,
pre-load out-of-vocabulary check in ``set_status.py`` still returns
:class:`~biz.dfch.specmgr.general.models.invalid_status_result.InvalidStatusResult` (the domain's full
flat vocabulary) before any document is loaded -- no current state is known there, and this module
does not touch it; (B) this module's post-load transition check returns the non-raising
:class:`~biz.dfch.specmgr.general.models.invalid_status_transition_result.InvalidStatusTransitionResult`
(the targets allowed from the current state, sorted -- never the full vocabulary; an empty list
marks a terminal current state) -- case 6 of the ADR
519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result workaround chain, so the
current-state-relative detail survives MCP clients that truncate ``isError`` text.

Phased rollout (REQ-003's opt-in seam): an entry's value is ``None`` until the domain's own
``_STATUS_TRANSITIONS`` table lands (Phases 110/120, next to the domain's own ``_ALLOWED_STATUSES``
in its ``models/<v>/frontmatter.py``); a ``None`` entry is a passthrough -- :func:`check_status_transition`
returns ``None`` and the adapter proceeds exactly as before. As of Phase 110 the pilot domain
``req`` is enforced (its own table has landed) and every other whole-body domain is still a
passthrough until Phase 120 lands its table. ADR is excluded (REQ-006): it has no entry
and ``_set_status_adr`` never calls into this module.

**No ``mcp`` dependency here**, like every other private ``general/tools/`` support module: this
module is plain data plus pure functions (it imports the per-domain closed vocabularies from each
domain's own ``models/<v>/frontmatter.py`` exactly as ``set_status.py`` does for its own
``_ALLOWED_STATUSES_BY_TYPE`` -- no re-derived vocabulary), so importing it never registers or
touches a tool.
"""

from __future__ import annotations

from ...dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
from ...feat.models.v1.frontmatter import _ALLOWED_STATUSES as _FEAT_ALLOWED_STATUSES
from ...gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_ALLOWED_STATUSES
from ...prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_ALLOWED_STATUSES
from ...qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_ALLOWED_STATUSES
from ...req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_ALLOWED_STATUSES
from ...req.models.v1.frontmatter import _STATUS_TRANSITIONS as _REQ_STATUS_TRANSITIONS
from ...rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_ALLOWED_STATUSES
from ...set.models.v1.frontmatter import _ALLOWED_STATUSES as _SET_ALLOWED_STATUSES
from ...sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_ALLOWED_STATUSES
from ...sysrs.models.v1.frontmatter import _ALLOWED_STATUSES as _SYSRS_ALLOWED_STATUSES
from ...tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_ALLOWED_STATUSES
from ...txt.models.v1.frontmatter import _ALLOWED_STATUSES as _TXT_ALLOWED_STATUSES
from ...uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_ALLOWED_STATUSES
from ...vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_ALLOWED_STATUSES
from ..models import InvalidStatusTransitionResult
from ._domains import ADR, WHOLE_BODY_DOMAINS

__all__ = ["check_status_transition", "decide_transition"]

#: Each whole-body domain's own closed status vocabulary, keyed by ``type`` (REQ-003's per-entry
#: validity check): the same per-domain ``_ALLOWED_STATUSES`` constants ``set_status.py``'s own
#: ``_ALLOWED_STATUSES_BY_TYPE`` reuses -- no new duplicated list. ADR's fixed set is deliberately
#: absent: ADR is excluded from the state machine (REQ-006).
_STATUS_VOCABULARIES_BY_TYPE: dict[str, frozenset[str]] = {
    "req": _REQ_ALLOWED_STATUSES,
    "uc": _UC_ALLOWED_STATUSES,
    "tsk": _TSK_ALLOWED_STATUSES,
    "qa": _QA_ALLOWED_STATUSES,
    "prb": _PRB_ALLOWED_STATUSES,
    "gol": _GOL_ALLOWED_STATUSES,
    "rsk": _RSK_ALLOWED_STATUSES,
    "dec": _DEC_ALLOWED_STATUSES,
    "sop": _SOP_ALLOWED_STATUSES,
    "feat": _FEAT_ALLOWED_STATUSES,
    "vcr": _VCR_ALLOWED_STATUSES,
    "sysrs": _SYSRS_ALLOWED_STATUSES,
    "txt": _TXT_ALLOWED_STATUSES,
    "set": _SET_ALLOWED_STATUSES,
}

assert set(_STATUS_VOCABULARIES_BY_TYPE) == set(WHOLE_BODY_DOMAINS), (
    "_STATUS_VOCABULARIES_BY_TYPE keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- "
    "add or remove the domain in both places (feat-125-domain-lists, REQ-006; feat-108-fsm, REQ-003)"
)

#: The central aggregation of the per-domain status state machines (feat-108-fsm, REQ-003):
#: one entry per whole-body domain, keyed to the ``general.tools._domains`` registry. An entry's
#: value is the domain's own ``_STATUS_TRANSITIONS`` table (current status -> allowed target
#: statuses, set semantics) once it lands in Phases 110/120 (domain-owned, next to the domain's
#: own ``_ALLOWED_STATUSES``); ``None`` = no table yet (the opt-in passthrough seam). As of
#: Phase 110 ``req`` carries its own landed table and is enforced; every other whole-body
#: domain is still ``None`` (passthrough) until Phase 120. ADR has no entry (REQ-006).
_STATUS_TRANSITIONS_BY_TYPE: dict[str, dict[str, frozenset[str]] | None] = {
    "req": _REQ_STATUS_TRANSITIONS,
    "uc": None,
    "tsk": None,
    "qa": None,
    "prb": None,
    "gol": None,
    "rsk": None,
    "dec": None,
    "sop": None,
    "feat": None,
    "vcr": None,
    "sysrs": None,
    "txt": None,
    "set": None,
}

# Program invariants (import-time), the Phase 100 form of REQ-003/ACC-007's drift assert: the
# aggregation is keyed to the shared domain registry (every key a whole-body domain, ADR
# structurally absent -- tightened to full coverage of every whole-body domain in Phase 120,
# Task 120.120), and every non-None table names only statuses from its domain's own closed
# vocabulary (active for every landed table -- ``req`` since Phase 110 -- and the rest as
# Phase 120 lands its tables).
assert set(_STATUS_TRANSITIONS_BY_TYPE) <= set(WHOLE_BODY_DOMAINS), (
    "_STATUS_TRANSITIONS_BY_TYPE keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- "
    "add or remove the domain in both places (feat-125-domain-lists, REQ-006; feat-108-fsm, REQ-003)"
)
assert ADR not in _STATUS_TRANSITIONS_BY_TYPE, (
    "ADR is excluded from the status state machine (feat-108-fsm, REQ-006): it keeps its own "
    "flat-vocabulary behavior and gets no aggregation entry"
)
for _domain, _table in _STATUS_TRANSITIONS_BY_TYPE.items():
    if _table is None:
        continue
    _vocabulary = _STATUS_VOCABULARIES_BY_TYPE[_domain]
    for _current, _targets in _table.items():
        assert _current in _vocabulary, (
            f"_STATUS_TRANSITIONS_BY_TYPE[{_domain!r}] names current status {_current!r}, which is "
            f"outside the domain's own closed vocabulary (feat-108-fsm, REQ-001/REQ-003)"
        )
        assert isinstance(_targets, frozenset), type(_targets)
        assert _targets <= _vocabulary, (
            f"_STATUS_TRANSITIONS_BY_TYPE[{_domain!r}][{_current!r}] allows target status(es) "
            f"{sorted(_targets - _vocabulary)} outside the domain's own closed vocabulary "
            "(feat-108-fsm, REQ-001/REQ-003)"
        )


def decide_transition(
    table: dict[str, frozenset[str]] | None,
    type_: str,
    current: str,
    target: str,
) -> InvalidStatusTransitionResult | None:
    """The pure transition decision over one domain's own table (:func:`check_status_transition`'s core).

    Total and deterministic, with no module-state dependency (the testability seam): a ``None``
    table (a table-less domain, or a type with no aggregation entry such as ``adr``) is a
    passthrough; a ``target`` inside the current state's allowed set is allowed; everything else
    is a non-raising :class:`InvalidStatusTransitionResult` whose ``allowed_values`` are the
    current state's allowed targets, sorted (never the domain's full vocabulary). A ``current``
    status that is not a key of the table (structurally unreachable once a domain's table pins
    full vocabulary coverage, but the decision must stay total) is treated as a terminal state:
    empty ``allowed_values`` and the terminal message form.

    Parameters
    ----------
    table:
        The dispatched domain's own ``_STATUS_TRANSITIONS`` table (current status -> allowed
        target statuses), or ``None`` for a table-less (passthrough) domain.
    type_:
        The dispatched domain type, echoed verbatim into the result.
    current:
        The document's current on-disk status (already loaded by the adapter).
    target:
        The requested target status.

    Returns
    -------
    ``InvalidStatusTransitionResult | None``
        ``None`` when the call may proceed (passthrough or allowed transition); otherwise the
        non-raising structured rejection (never raises).
    """
    assert table is None or isinstance(table, dict), type(table)
    assert isinstance(type_, str), type(type_)
    assert isinstance(current, str), type(current)
    assert isinstance(target, str), type(target)

    if table is None:
        return None
    allowed = table.get(current, frozenset())
    if target in allowed:
        return None
    allowed_values = sorted(allowed)
    if allowed_values:
        message = (
            f"Invalid status transition '{current}' -> '{target}' for type '{type_}'. "
            f"Allowed from '{current}': {', '.join(allowed_values)}"
        )
    else:
        message = (
            f"Invalid status transition '{current}' -> '{target}' for type '{type_}'. "
            f"Status '{current}' is terminal (no outgoing transitions)."
        )
    result = InvalidStatusTransitionResult(
        valid=False,
        type=type_,
        from_status=current,
        to_status=target,
        allowed_values=allowed_values,
        message=message,
    )
    return result


def check_status_transition(type_: str, current: str, target: str) -> InvalidStatusTransitionResult | None:
    """The shared check the whole-body ``_set_status_<d>`` adapters call post-load/pre-write.

    Looks up the dispatched ``type_``'s own table in :data:`_STATUS_TRANSITIONS_BY_TYPE` and
    delegates to :func:`decide_transition`. A table-less domain (a ``None`` entry, or any type
    without an entry -- e.g. ``adr``, which never calls this) passes through (``None``), so the
    aggregation stays opt-in during the phased rollout (feat-108-fsm, REQ-003). The adapters call
    this inside their domain lock, after the unchanged-status no-op comparison and before the
    raw-body re-read -- a rejection is pre-write (nothing is persisted, ``updated`` is not
    bumped).

    Parameters
    ----------
    type_:
        The dispatched domain type (one of ``general.tools._domains.WHOLE_BODY_DOMAINS``).
    current:
        The document's current on-disk status (already loaded by the adapter).
    target:
        The requested target status.

    Returns
    -------
    ``InvalidStatusTransitionResult | None``
        ``None`` when the transition is allowed (or the domain is table-less); otherwise the
        non-raising structured rejection (never raises).
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(current, str), type(current)
    assert isinstance(target, str), type(target)

    table = _STATUS_TRANSITIONS_BY_TYPE.get(type_)
    result = decide_transition(table, type_, current, target)
    return result
