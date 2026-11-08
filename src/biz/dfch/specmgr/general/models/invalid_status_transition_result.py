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

"""The generic ``set_status`` tool's own non-raising, structured result for its second, post-load
failure mode: a status transition the dispatched domain's own state machine does not allow
(feat-108-fsm, GitHub issue #108 -- case 6 of the DEC
519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result workaround chain).

This is a distinct, purpose-built model for ``set_status``'s post-load/pre-write transition
check (``general.tools._status_fsm.check_status_transition``, called by each whole-body
``_set_status_<d>`` adapter immediately after its own unchanged-status no-op comparison) -- it is
a sibling of, not a reuse or subclass of,
:class:`~biz.dfch.specmgr.general.models.invalid_status_result.InvalidStatusResult`, which
remains the first, pre-dispatch/pre-load error surface (an out-of-vocabulary ``status`` value,
rejected before any document is loaded -- no current state is known there, so it carries the
domain's full flat vocabulary). ``InvalidStatusTransitionResult`` is the second surface: the
document has been loaded, so the result is current-state-relative -- ``allowed_values`` holds
exactly the target statuses the domain's machine allows from ``from_status`` (sorted; an empty
list marks a terminal current state), never the domain's full closed vocabulary. Every other
``set_status`` failure mode (unknown id, path-injection/wrong-shape id) continues to raise
unchanged.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["InvalidStatusTransitionResult"]


class InvalidStatusTransitionResult(BaseModel):
    """``set_status``'s non-raising result for a status transition the domain's machine rejects.

    There is no successful variant of this model -- it is only ever constructed and returned
    when the requested transition (``from_status`` -> ``to_status``) is rejected by the
    dispatched domain's own ``_STATUS_TRANSITIONS`` table, after the document has been loaded
    and before any write (nothing is persisted, ``updated`` is not bumped).

    Parameters
    ----------
    valid:
        Always ``False`` -- there is no successful variant of this model; its mere presence in a
        ``set_status`` return value signals rejection.
    type:
        The dispatched domain type, echoed back verbatim.
    from_status:
        The document's current on-disk status (loaded by the adapter before the check).
    to_status:
        The requested target status, echoed back verbatim.
    allowed_values:
        The target statuses the domain's machine allows from ``from_status``, sorted (NOT the
        domain's full closed vocabulary -- that is ``InvalidStatusResult``'s own payload);
        an empty list marks a terminal current state (no outgoing transitions).
    message:
        The exact wording, normal form: ``"Invalid status transition '{from_status}' ->
        '{to_status}' for type '{type}'. Allowed from '{from_status}': {allowed_values}"``,
        where ``{allowed_values}`` is ``allowed_values`` comma-and-space-joined
        (``", ".join(allowed_values)``) in the same order as the ``allowed_values`` field
        (sorted); terminal form (``allowed_values`` empty): ``"Invalid status transition
        '{from_status}' -> '{to_status}' for type '{type}'. Status '{from_status}' is terminal
        (no outgoing transitions)."``.
    """

    valid: bool
    type: str
    from_status: str
    to_status: str
    allowed_values: list[str]
    message: str
