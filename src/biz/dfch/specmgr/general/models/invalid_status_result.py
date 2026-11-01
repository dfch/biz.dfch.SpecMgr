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

"""The generic ``set_status`` tool's own non-raising, structured result for its one narrowly-scoped
failure mode: an out-of-vocabulary ``status`` value for the dispatched domain ``type``
(feat-103-set-status-error, ADR b399f1ce-ed42-4929-b01c-7a57d18e8014, "Extend the non-raising
structured-result workaround to set_status's invalid-status case").

This is a distinct, purpose-built model for ``set_status`` -- it is not a reuse or subclass of
:class:`~biz.dfch.specmgr.general.models.validate_result.ValidateResult`, which is a different
tool's own (``general.tools.validate``) ``{valid, errors}`` shape for a different failure surface
(disk-free/id-free content validation, potentially multiple errors). ``InvalidStatusResult``
instead carries exactly one rejected value plus its domain's full allowed-values list, matching
the single guarded vocabulary check ``set_status`` performs before dispatching to any per-domain
adapter. Every other ``set_status`` failure mode (unknown id, path-injection/wrong-shape id,
``superseded_by`` misuse on a non-``adr`` type) continues to raise unchanged -- see ADR
b399f1ce-ed42-4929-b01c-7a57d18e8014's Decision Outcome for the full rationale and scope.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["InvalidStatusResult"]


class InvalidStatusResult(BaseModel):
    """``set_status``'s non-raising result for an out-of-vocabulary ``status`` value.

    There is no successful variant of this model -- it is only ever constructed and returned
    when the requested ``status`` is rejected, before any domain lock is taken or file is read.

    Parameters
    ----------
    valid:
        Always ``False`` -- there is no successful variant of this model; its mere presence in a
        ``set_status`` return value signals rejection.
    type:
        The requested domain type, echoed back verbatim.
    status:
        The rejected status value, echoed back verbatim.
    allowed_values:
        The domain's allowed values, sorted. For ``type="adr"``: the sorted 6-value fixed status
        set plus one literal trailing descriptive entry ``"superseded by <target-id>"``,
        documenting the ``"superseded by ..."`` pattern rather than trying to enumerate its
        infinite matches.
    message:
        The exact wording ``"Invalid status '{status}' for type '{type}'. Allowed values:
        {allowed_values}"``, where ``{allowed_values}`` is ``allowed_values`` comma-and-space-joined
        (``", ".join(allowed_values)``) in the same order as the ``allowed_values`` field.
    """

    valid: bool
    type: str
    status: str
    allowed_values: list[str]
    message: str
