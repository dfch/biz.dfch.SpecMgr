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

# pylint: disable=redefined-builtin  # id intentionally shadows the builtin: public prompt API, issue #41

"""``@mcp.prompt()``: review_feat (feat-263-delegation-prompts, Phase 110).

Returns instructional text -- not itself a tool call -- that guides an
LLM through a post-implementation review of a **finished** Feature
(FEAT) document, mirroring ``.opencode/agent/feat-reviewer.md``'s own
checklist and report format portably: reading the plan in full,
resolving the code diff (the merge-base against dev per the
feat-reviewer's own instructions), applying the full review checklist
(the nine ISO/IEC 25010:2023 product-quality characteristics plus the
feature-plan convention layer and an optional local layer), and
reporting Errors/Gaps/Discrepancies/Improvements/Positives as
TSK-compatible checklist items, each with a file:line citation --
report-only, never editing, writing, or committing.

The narration INCLUDES the conditional "Proposed Fix Phase" section:
present only when the report contains any Errors, Gaps, or
Discrepancies, it carries a ready-to-paste block for the plan's
``### Task List`` -- a ``#### Phase NNN: Fix phase (review cycle k)``
heading using the NEXT UNUSED phase number (3-digit, step 10, never
renumbering existing phases) plus ``- [ ] Task NNN.MMM`` items derived
STRICTLY from the report's own Errors/Gaps/Discrepancies
(Improvements/Positives stay advisory), with any item needing a user
decision explicitly flagged ``[NEEDS DECISION]`` rather than guessed
at.

Unlike every other domain in this codebase, ``id`` is a
``feat-NNN-slug`` (the containing folder's own name), not a UUID -- a
blank or malformed id fails fast with ``ValueError`` (the shared
``general.tools._path_safety.assert_feat_id`` guard, the same one every
``feat`` tool applies) before any packaged data is read.

This prompt only ever *narrates* the review flow -- it never calls
``get_feat`` or any git command itself, exactly like every other prompt
in this codebase (see ``general.prompts.repair``'s own docstring for
the same contract). ``review_feat`` is the portable counterpart of the
pre-existing, read-only ``feat-reviewer`` OpenCode agent
(``.opencode/agent/feat-reviewer.md``) and the ``/review-feature``
command (``.opencode/command/review-feature.md``), which carry the same
workflow with real file and tool access.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_review_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``. Placeholders use
``string.Template`` (``$id``), not ``str.format``, so the instructions
file itself is free to use plain, unescaped ``{...}`` braces.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...general.tools._path_safety import assert_feat_id
from ...server import mcp


@mcp.prompt(
    name="review_feat",
    title="Review a finished feature implementation (portable feat-reviewer)",
    description=(
        "Guides the LLM through a portable post-implementation review of a finished feature: "
        "read the plan in full, resolve the code diff (the merge-base against dev), apply the "
        "feat-reviewer checklist (the nine ISO/IEC 25010:2023 product-quality characteristics "
        "plus the feature-plan convention layer and an optional local layer), and report "
        "Errors/Gaps/Discrepancies/Improvements/Positives as TSK-compatible checklist items, "
        "each with a file:line citation -- report-only, never edits, writes, or commits -- "
        "including the conditional, ready-to-paste Proposed Fix Phase block (next unused phase "
        "number, tasks derived from Errors/Gaps/Discrepancies only, [NEEDS DECISION] flagging) "
        "when any Errors/Gaps/Discrepancies remain."
    ),
)
def review_feat(id: str) -> str:
    """Return instructional text for a post-implementation review of the feature ``id``.

    Parameters
    ----------
    id:
        The feature's ``feat-NNN-slug`` identifier (the containing
        folder's own name, e.g. ``feat-36-delete``).

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``get_feat`` or any git command itself -- it only narrates that
        sequence for the LLM to carry out.

    Raises
    ------
    ValueError
        If ``id`` is a blank/whitespace-only string, or not a
        well-formed ``feat-NNN-slug`` folder name.
    """
    assert isinstance(id, str), f"review_feat() expects id as a str, got {id!r}"
    normalized_id = id.strip()
    if not normalized_id:
        raise ValueError(
            "review_feat() received a blank id; pass the feature's feat-NNN-slug id "
            "(the containing folder's own name, e.g. 'feat-36-delete')."
        )
    assert_feat_id(normalized_id)
    template = Template(read_packaged_text("feat", "review_instructions", "md"))
    result = template.substitute(id=normalized_id)
    return result
