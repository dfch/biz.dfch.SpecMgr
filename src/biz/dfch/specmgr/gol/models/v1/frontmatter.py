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

"""Goal (GOL) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `req/models/v1/frontmatter.py::ReqFrontmatter`/
`prb/models/v1/frontmatter.py::PrbFrontmatter`: a subtype of `MarkdownFrontmatter`
that restricts `type` to a fixed ``Literal["gol"]`` and narrows the free-form
``status`` to REQ's exact seven-value set -- goals are business-level
requirements, so requirement-lifecycle semantics apply (see
`.specmgr/feat/feat-18-goal/README.md` Design Notes).

This module also owns the goal status state machine (feat-108-fsm, GitHub
issue #108): the ``_STATUS_TRANSITIONS`` table, next to
``_ALLOWED_STATUSES``, enforced by the generic ``set_status`` tool
post-load/pre-write (REQ-001/REQ-002).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.frontmatter import DEFAULT_STATUS

#: Fixed, closed set of accepted ``status`` values for goals -- REQ's exact
#: seven-value set: ``draft`` (still being written), ``proposed`` (under
#: consideration), ``accepted`` (agreed to be pursued), ``implemented`` (the
#: goal has genuinely been reached), ``superseded`` (replaced by another
#: goal), ``deprecated`` (no longer pursued, kept for reference), or
#: ``rejected`` (considered and not pursued).
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "proposed",
        "accepted",
        "superseded",
        "deprecated",
        "rejected",
        "implemented",
    }
)

#: The authoring form of :data:`_STATUS_TRANSITIONS` (feat-108-fsm, GitHub issue #108, REQ-007):
#: the goal status state machine as a plain mapping of current status to a list of the
#: allowed next statuses. The machine is cycling-friendly (``proposed`` may return to ``draft``,
#: ``rejected`` may return to ``proposed``); ``superseded`` and ``deprecated`` are terminal
#: states (an empty target list).
_STATUS_TRANSITIONS_RAW: dict[str, list[str]] = {
    "draft": ["proposed", "rejected"],
    "proposed": ["accepted", "rejected", "draft"],
    "accepted": ["implemented", "superseded", "deprecated", "rejected"],
    "rejected": ["proposed", "draft"],
    "implemented": ["superseded", "deprecated"],
    "superseded": [],
    "deprecated": [],
}

#: The goal status state machine (feat-108-fsm, GitHub issue #108, REQ-001/REQ-002),
#: normalized from :data:`_STATUS_TRANSITIONS_RAW` to set semantics: current status -> the
#: allowed target statuses (a ``frozenset`` per entry, the shape
#: ``general.tools._status_fsm._STATUS_TRANSITIONS_BY_TYPE``'s own per-entry validity check
#: requires). The generic ``set_status`` tool enforces this machine post-load/pre-write
#: (immediately after the unchanged-status no-op comparison): a transition not in the current
#: state's target set is rejected before any write with the non-raising
#: ``InvalidStatusTransitionResult`` (its ``allowed_values`` are the current state's targets,
#: sorted); ``superseded`` and ``deprecated`` are terminal (an empty target set).
_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    current: frozenset(targets) for current, targets in _STATUS_TRANSITIONS_RAW.items()
}

# Program invariants (import-time, feat-108-fsm REQ-001/REQ-003): the machine covers exactly the
# domain's own closed status vocabulary -- so a document's on-disk status is always a key and
# the "current not a key" case is structurally unreachable -- and every target is in-vocabulary.
assert set(_STATUS_TRANSITIONS) == _ALLOWED_STATUSES, (
    "_STATUS_TRANSITIONS drifted from gol's own closed status vocabulary _ALLOWED_STATUSES -- every "
    "status must be a key exactly once (feat-108-fsm, REQ-001)"
)
for _current, _targets in _STATUS_TRANSITIONS.items():
    assert _targets <= _ALLOWED_STATUSES, (
        f"_STATUS_TRANSITIONS[{_current!r}] names target status(es) {sorted(_targets - _ALLOWED_STATUSES)} "
        f"outside gol's own closed status vocabulary (feat-108-fsm, REQ-001)"
    )


class GolFrontmatter(MarkdownFrontmatter):
    """Goal (GOL) frontmatter: `MarkdownFrontmatter` narrowed for the ``gol`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"gol"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["gol"] = "gol"``, so a document
        omitting ``type`` entirely still parses as a goal document.
    status:
        One of ``"draft"``, ``"proposed"``, ``"accepted"``, ``"superseded"``,
        ``"deprecated"``, ``"rejected"``, ``"implemented"``. Narrows the base's
        free-form ``str = "draft"`` default to this closed seven-value set
        (REQ's exact set -- goals are business-level requirements, so
        requirement-lifecycle semantics apply). Blank/absent still defaults
        to ``"draft"`` (inherited from the base's
        ``_default_blank_status_to_draft`` validator, which runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["gol"] = "gol"  # type: ignore

    # feat-189 Phase 120 (C13): redeclare the inherited `status` field (the
    # only way to attach `json_schema_extra` to it) so the generated JSON
    # Schema carries this same closed set as an `enum` key -- schema-level
    # documentation only, in the `MarkdownFrontmatter.created`/`.updated`
    # `pattern`-metadata precedent: pydantic-core never enforces it, and
    # `_validate_status` below remains the sole enforcement point. The
    # default stays the base's own `"draft"`.
    status: str = Field(default=DEFAULT_STATUS, json_schema_extra={"enum": sorted(_ALLOWED_STATUSES)})

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
