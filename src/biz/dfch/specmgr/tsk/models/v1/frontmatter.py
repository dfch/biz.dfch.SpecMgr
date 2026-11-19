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

"""TaskList frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `req/models/v1/frontmatter.py::ReqFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["tsk"]`` and narrows the free-form ``status`` to an appropriate
closed vocabulary for task lists.

This module also owns the task-list status state machine (feat-108-fsm,
GitHub issue #108): the ``_STATUS_TRANSITIONS`` table, next to
``_ALLOWED_STATUSES``, enforced by the generic ``set_status`` tool
post-load/pre-write (REQ-001/REQ-002).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.frontmatter import DEFAULT_STATUS

#: Fixed, closed set of accepted ``status`` values for task lists -- a small,
#: purpose-fit set matching how a task list is actually used (start it, work
#: it, finish it, or drop it), rather than reusing REQ's larger set
#: (`.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md` Design Notes).
_ALLOWED_STATUSES = frozenset(
    {
        "draft",
        "active",
        "done",
        "cancelled",
    }
)

#: The authoring form of :data:`_STATUS_TRANSITIONS` (feat-108-fsm, GitHub issue #108, REQ-007):
#: the task-list status state machine as a plain mapping of current status to a list of the
#: allowed next statuses. The machine is cycling-friendly (``active`` may return to ``draft``,
#: ``done`` and ``cancelled`` may return to ``active``); this domain has no terminal state
#: (every current status carries at least one allowed target).
_STATUS_TRANSITIONS_RAW: dict[str, list[str]] = {
    "draft": ["active", "cancelled"],
    "active": ["done", "cancelled", "draft"],
    "done": ["active", "cancelled"],
    "cancelled": ["draft", "active"],
}

#: The task-list status state machine (feat-108-fsm, GitHub issue #108, REQ-001/REQ-002),
#: normalized from :data:`_STATUS_TRANSITIONS_RAW` to set semantics: current status -> the
#: allowed target statuses (a ``frozenset`` per entry, the shape
#: ``general.tools._status_fsm._STATUS_TRANSITIONS_BY_TYPE``'s own per-entry validity check
#: requires). The generic ``set_status`` tool enforces this machine post-load/pre-write
#: (immediately after the unchanged-status no-op comparison): a transition not in the current
#: state's target set is rejected before any write with the non-raising
#: ``InvalidStatusTransitionResult`` (its ``allowed_values`` are the current state's targets,
#: sorted); this domain has no terminal state (every current status carries at least one
#: allowed target).
_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    current: frozenset(targets) for current, targets in _STATUS_TRANSITIONS_RAW.items()
}

# Program invariants (import-time, feat-108-fsm REQ-001/REQ-003): the machine covers exactly the
# domain's own closed status vocabulary -- so a document's on-disk status is always a key and
# the "current not a key" case is structurally unreachable -- and every target is in-vocabulary.
assert set(_STATUS_TRANSITIONS) == _ALLOWED_STATUSES, (
    "_STATUS_TRANSITIONS drifted from tsk's own closed status vocabulary _ALLOWED_STATUSES -- every "
    "status must be a key exactly once (feat-108-fsm, REQ-001)"
)
for _current, _targets in _STATUS_TRANSITIONS.items():
    assert _targets <= _ALLOWED_STATUSES, (
        f"_STATUS_TRANSITIONS[{_current!r}] names target status(es) {sorted(_targets - _ALLOWED_STATUSES)} "
        f"outside tsk's own closed status vocabulary (feat-108-fsm, REQ-001)"
    )


class TskFrontmatter(MarkdownFrontmatter):
    """TaskList frontmatter: `MarkdownFrontmatter` narrowed for the ``tsk`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"tsk"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["tsk"] = "tsk"``, so a document
        omitting ``type`` entirely still parses as a task list document.
    status:
        One of ``"draft"``, ``"active"``, ``"done"``, ``"cancelled"``. Narrows
        the base's free-form ``str = "draft"`` default to this closed
        four-value set. Blank/absent still defaults to ``"draft"`` (inherited
        from the base's ``_default_blank_status_to_draft`` validator, which
        runs before this one).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["tsk"] = "tsk"  # type: ignore

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
