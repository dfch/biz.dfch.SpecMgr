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

"""``@mcp.prompt()``: refine_feat (feat-167-mcp-lifecycle-commands-2, Phase 100).

Returns instructional text -- not itself a tool call -- that guides an
LLM through a pre-implementation plan-readiness review of an existing
Feature (FEAT) document, fully over the MCP-native path: reading the
plan via ``get_feat`` with ``raw=True`` (and ``raw=True, numbered=True``
for the edit coordinates -- never from a raw file read), assessing it
against the four readiness checklist areas (testable acceptance
criteria, phase ordering and dependencies, scope clarity, unresolved
decisions), asking the user which findings to apply via the ``question``
tool, applying each approved fix with the generic ``update`` tool with
``type="feat"`` (line-range replace preferred, so unchanged regions stay
byte-identical), and re-checking with the generic ``validate`` tool with
``type="feat"`` and ``full=True``. Host file tools are only a fallback
for hosts that cannot reach those specmgr tools.

Unlike every other domain in this codebase, ``id`` is a
``feat-NNN-slug`` (the containing folder's own name), not a UUID -- a
blank or malformed id fails fast with ``ValueError`` (the shared
``general.tools._path_safety.assert_feat_id`` guard, the same one every
``feat`` tool applies) before any packaged data is read.

This prompt only ever *narrates* the review-and-edit flow -- it never
calls ``get_feat``/``question``/``update``/``validate`` itself, exactly
like every other prompt in this codebase (see
``general.prompts.repair``'s own docstring for the same contract).
``refine_feat`` is distinct from the pre-existing, read-only
``feat-refiner`` OpenCode agent (which reports findings and never
edits): this prompt -- and the ``feat-planner`` subagent /
``/plan-feature`` command that carry the same workflow on OpenCode --
apply the user-approved fixes to the plan itself.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_refine_instructions.md``, read fresh on every call via
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
    name="refine_feat",
    title="Refine a feature plan for implementation readiness",
    description=(
        "Guides the LLM through a pre-implementation plan-readiness review of an existing "
        "feature (testable acceptance criteria, phase ordering and dependencies, scope "
        "clarity, unresolved decisions): reading the plan via get_feat with raw=True, asking "
        "the user which findings to apply via the question tool, applying the approved "
        'fixes with the generic update tool (type="feat", line-range replace preferred so '
        "unchanged regions stay byte-identical), and re-checking with the generic validate "
        'tool (type="feat", full=True) -- host file tools only as a fallback for hosts '
        "without those specmgr tools."
    ),
)
def refine_feat(id: str) -> str:
    """Return instructional text for a plan-readiness review of the feature ``id``.

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
        ``get_feat``, ``question``, ``update``, or ``validate`` itself
        -- it only narrates that sequence for the LLM to carry out.

    Raises
    ------
    ValueError
        If ``id`` is a blank/whitespace-only string, or not a
        well-formed ``feat-NNN-slug`` folder name.
    """
    assert isinstance(id, str), f"refine_feat() expects id as a str, got {id!r}"
    normalized_id = id.strip()
    if not normalized_id:
        raise ValueError(
            "refine_feat() received a blank id; pass the feature's feat-NNN-slug id "
            "(the containing folder's own name, e.g. 'feat-36-delete')."
        )
    assert_feat_id(normalized_id)
    template = Template(read_packaged_text("feat", "refine_instructions", "md"))
    result = template.substitute(id=normalized_id)
    return result
