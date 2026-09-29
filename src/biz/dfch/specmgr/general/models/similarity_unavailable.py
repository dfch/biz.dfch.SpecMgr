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

"""The two similarity tools' shared non-raising, structured "unavailable" result (feat-134, REQ-003).

Mirrors the non-raising structured-result precedent of
:class:`~biz.dfch.specmgr.general.models.invalid_status_result.InvalidStatusResult`
(ADR b399f1ce-ed42-4929-b01c-7a57d18e8014) and
:class:`~biz.dfch.specmgr.general.models.validate_result.ValidateResult`
(feat-81-83-validation, REQ-004): when the embedding feature is unavailable at
runtime, the ``find_related``/``find_similar_text`` tools (general.tools,
Phase 3) return one of these instead of raising -- one code path, two
triggers, per ADR 750842b2-aca4-4649-ba0c-855ec8e1f505's Availability
sub-decision. A successful call never returns this model: its mere presence
in a tool result signals unavailability, exactly as
:class:`InvalidStatusResult` signals rejection.

There is no successful variant, and no ``valid``-style boolean to confuse
with one: the ``available`` field is always ``False`` on the only shape that
exists (the ``reason`` field is what distinguishes the two triggers).
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import Literal

__all__ = ["SimilarityUnavailableResult"]

#: ``reason`` value: the feature is explicitly opted out via the
#: ``SPECMGR_SIMILARITY_DISABLED`` environment variable (presence-based, any
#: value -- matching the repo's own env-flag convention, see
#: ``general.resources.config``).
REASON_DISABLED = "disabled"

#: ``reason`` value: the embedding backend is not importable or the model
#: failed to load (including a first-use download failure, e.g. no network to
#: the Hub and no local model cache).
REASON_BACKEND_UNAVAILABLE = "backend-unavailable"


class SimilarityUnavailableResult(BaseModel):
    """The structured "unavailable" result both similarity tools return instead of raising.

    Parameters
    ----------
    available:
        Always ``False`` -- there is no successful variant of this model; its
        mere presence in a tool return value signals unavailability.
    reason:
        Which trigger fired: :data:`REASON_DISABLED` (the opt-out env var is
        present) or :data:`REASON_BACKEND_UNAVAILABLE` (the backend failed to
        import or the model failed to load). The two triggers share this one
        code path and this one shape (REQ-003).
    message:
        An actionable enablement hint for the caller: unset the flag
        (:data:`REASON_DISABLED`) or install the ``similarity`` extra and
        allow the one-time model download (:data:`REASON_BACKEND_UNAVAILABLE`).
    """

    available: bool
    reason: Literal["disabled", "backend-unavailable"]
    message: str
