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
marks a terminal current state) -- case 6 of the DEC
519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result workaround chain, so the
current-state-relative detail survives MCP clients that truncate ``isError`` text.

Rollout complete (REQ-003/ACC-007): every whole-body domain's own ``_STATUS_TRANSITIONS`` table
has landed (next to the domain's own ``_ALLOWED_STATUSES`` in its ``models/<v>/frontmatter.py``)
and is enforced -- ``req`` as the Phase 110 pilot, the remaining whole-body domains as of Phase
120. The import-time drift assert below is the full-coverage form: keys equal the shared
``general.tools._domains`` registry (the 14 whole-body domains), and no entry is ``None``. The
pure core :func:`decide_transition` still treats a ``None`` table as a passthrough (the
total-decision seam, exercised by tests with temporary tables and by unregistered types).

**No ``mcp`` dependency here**, like every other private ``general/tools/`` support module: this
module is plain data plus pure functions (it imports the per-domain closed vocabularies and the
per-domain state machines from each domain's own ``models/<v>/frontmatter.py`` exactly as
``set_status.py`` does for its own ``_ALLOWED_STATUSES_BY_TYPE`` -- no re-derived vocabulary,
no re-derived table), so importing it never registers or touches a tool.
"""

from __future__ import annotations

from ...dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
from ...dec.models.v1.frontmatter import _STATUS_TRANSITIONS as _DEC_STATUS_TRANSITIONS
from ...feat.models.v1.frontmatter import _ALLOWED_STATUSES as _FEAT_ALLOWED_STATUSES
from ...feat.models.v1.frontmatter import _STATUS_TRANSITIONS as _FEAT_STATUS_TRANSITIONS
from ...gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_ALLOWED_STATUSES
from ...gol.models.v1.frontmatter import _STATUS_TRANSITIONS as _GOL_STATUS_TRANSITIONS
from ...prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_ALLOWED_STATUSES
from ...prb.models.v1.frontmatter import _STATUS_TRANSITIONS as _PRB_STATUS_TRANSITIONS
from ...qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_ALLOWED_STATUSES
from ...qa.models.v2.frontmatter import _STATUS_TRANSITIONS as _QA_STATUS_TRANSITIONS
from ...req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_ALLOWED_STATUSES
from ...req.models.v1.frontmatter import _STATUS_TRANSITIONS as _REQ_STATUS_TRANSITIONS
from ...rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_ALLOWED_STATUSES
from ...rsk.models.v1.frontmatter import _STATUS_TRANSITIONS as _RSK_STATUS_TRANSITIONS
from ...set.models.v1.frontmatter import _ALLOWED_STATUSES as _SET_ALLOWED_STATUSES
from ...set.models.v1.frontmatter import _STATUS_TRANSITIONS as _SET_STATUS_TRANSITIONS
from ...sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_ALLOWED_STATUSES
from ...sop.models.v1.frontmatter import _STATUS_TRANSITIONS as _SOP_STATUS_TRANSITIONS
from ...sysrs.models.v1.frontmatter import _ALLOWED_STATUSES as _SYSRS_ALLOWED_STATUSES
from ...sysrs.models.v1.frontmatter import _STATUS_TRANSITIONS as _SYSRS_STATUS_TRANSITIONS
from ...tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_ALLOWED_STATUSES
from ...tsk.models.v1.frontmatter import _STATUS_TRANSITIONS as _TSK_STATUS_TRANSITIONS
from ...txt.models.v1.frontmatter import _ALLOWED_STATUSES as _TXT_ALLOWED_STATUSES
from ...txt.models.v1.frontmatter import _STATUS_TRANSITIONS as _TXT_STATUS_TRANSITIONS
from ...uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_ALLOWED_STATUSES
from ...uc.models.v2.frontmatter import _STATUS_TRANSITIONS as _UC_STATUS_TRANSITIONS
from ...vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_ALLOWED_STATUSES
from ...vcr.models.v1.frontmatter import _STATUS_TRANSITIONS as _VCR_STATUS_TRANSITIONS
from ..models import InvalidStatusTransitionResult
from ._domains import WHOLE_BODY_DOMAINS

__all__ = ["check_status_transition", "decide_transition"]

#: Each whole-body domain's own closed status vocabulary, keyed by ``type`` (REQ-003's per-entry
#: validity check): the same per-domain ``_ALLOWED_STATUSES`` constants ``set_status.py``'s own
#: ``_ALLOWED_STATUSES_BY_TYPE`` reuses -- no new duplicated list.
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
#: one entry per whole-body domain, keyed to the ``general.tools._domains`` registry. Every
#: entry's value is the domain's own ``_STATUS_TRANSITIONS`` table (current status -> allowed
#: target statuses, set semantics; domain-owned, next to the domain's own
#: ``_ALLOWED_STATUSES`` in its ``models/<v>/frontmatter.py``), carried by identity -- ``req``
#: since Phase 110, every remaining whole-body domain since Phase 120 (rollout complete: no
#: entry is ``None`` any more, and no whole-body domain is a passthrough).
_STATUS_TRANSITIONS_BY_TYPE: dict[str, dict[str, frozenset[str]]] = {
    "req": _REQ_STATUS_TRANSITIONS,
    "uc": _UC_STATUS_TRANSITIONS,
    "tsk": _TSK_STATUS_TRANSITIONS,
    "qa": _QA_STATUS_TRANSITIONS,
    "prb": _PRB_STATUS_TRANSITIONS,
    "gol": _GOL_STATUS_TRANSITIONS,
    "rsk": _RSK_STATUS_TRANSITIONS,
    "dec": _DEC_STATUS_TRANSITIONS,
    "sop": _SOP_STATUS_TRANSITIONS,
    "feat": _FEAT_STATUS_TRANSITIONS,
    "vcr": _VCR_STATUS_TRANSITIONS,
    "sysrs": _SYSRS_STATUS_TRANSITIONS,
    "txt": _TXT_STATUS_TRANSITIONS,
    "set": _SET_STATUS_TRANSITIONS,
}

# Program invariants (import-time), the full-coverage form of REQ-003/ACC-007's drift assert
# (Phase 120, Task 120.120 -- the phased rollout is finished): the aggregation is keyed to the
# shared domain registry (keys equal the 14 whole-body domains), every entry is the domain's
# own landed table (no ``None`` passthrough remains), and every table names only statuses from
# its domain's own closed vocabulary.
assert set(_STATUS_TRANSITIONS_BY_TYPE) == set(WHOLE_BODY_DOMAINS), (
    "_STATUS_TRANSITIONS_BY_TYPE keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- "
    "add or remove the domain in both places (feat-125-domain-lists, REQ-006; feat-108-fsm, REQ-003)"
)
for _domain, _table in _STATUS_TRANSITIONS_BY_TYPE.items():
    assert _table is not None, (
        f"_STATUS_TRANSITIONS_BY_TYPE[{_domain!r}] is still the None passthrough -- the feat-108-fsm "
        "rollout is complete: every whole-body domain's _STATUS_TRANSITIONS table has landed "
        "(feat-108-fsm, REQ-003/ACC-007)"
    )
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
    table (a table-less domain, or a type with no aggregation entry) is a passthrough; a
    ``target`` inside the current state's allowed set is allowed; everything else
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
    delegates to :func:`decide_transition`. A ``None`` lookup result passes through (``None``):
    as of Phase 120 no whole-body domain's entry is ``None`` any more (the rollout is complete,
    every whole-body domain is enforced), so the passthrough covers only types without an
    aggregation entry (feat-108-fsm, REQ-003).
    The adapters call this inside their domain lock, after the unchanged-status no-op comparison
    and before the raw-body re-read -- a rejection is pre-write (nothing is persisted,
    ``updated`` is not bumped).

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
