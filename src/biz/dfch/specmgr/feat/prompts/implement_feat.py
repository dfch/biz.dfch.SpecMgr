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

"""``@mcp.prompt()``: implement_feat (feat-263-delegation-prompts, Phase 110).

Returns instructional text -- not itself a tool call -- that guides an
LLM through implementing an existing Feature (FEAT) plan, phase by
phase, under the orchestrator discipline the plan's own structure is
built for: reading the plan in full, building a phase-by-phase
``TodoWrite`` list, delegating each phase to a fresh subagent via the
host's task-delegation tool when available, independently verifying
each subagent's result BEFORE advancing (re-running the phase's quality
gate, inspecting the diff, confirming the phase's acceptance criteria),
and never writing or editing code files itself -- all implementation is
delegated.

The delegation is narrated as OPTIONAL, per DEC
4481b1fd-26e5-46bc-8f1b-236b638385b2 (the first exercise of the
portable-prompt-narrates-optional-delegation pattern): the text refers
to "your host's task-delegation tool, if one exists" -- never assuming
the tool is present -- and always carries the explicit fallback to
direct single-session implementation, phase by phase, when no such tool
exists (never a hard failure). After the plan's final verification
phase (the feature at ``review``, not yet ``done``), the narration
describes the capped review-fix loop: run the reviewer, resolve any
``[NEEDS DECISION]`` items with the user via ``question``, delegate the
reviewer's proposed fix phase to one more subagent cycle (the
implementer appends the ready-to-paste block to the plan's Task List,
since the orchestrator cannot edit files), and repeat until no
Errors/Gaps/Discrepancies remain -- capped at 3 review-fix cycles, the
``done`` closeout only after a clean loop exit.

Unlike every other domain in this codebase, ``id`` is a
``feat-NNN-slug`` (the containing folder's own name), not a UUID -- a
blank or malformed id fails fast with ``ValueError`` (the shared
``general.tools._path_safety.assert_feat_id`` guard, the same one every
``feat`` tool applies) before any packaged data is read.

This prompt only ever *narrates* the implement-and-verify flow -- it
never calls ``get_feat``/``question``/``set_status`` itself, exactly
like every other prompt in this codebase (see
``general.prompts.repair``'s own docstring for the same contract).
``implement_feat`` is the portable counterpart of the OpenCode-native
``phase-orchestrator`` agent (``.opencode/agent/phase-orchestrator.md``)
and the ``/implement-feature`` command
(``.opencode/command/implement-feature.md``), which carry the same
workflow with real file and tool access.

The actual instructional text lives in its own packaged data file,
``feat/data/feat_implement_instructions.md``, read fresh on every call
via ``general.tools._packaged_data.read_packaged_text``. Placeholders
use ``string.Template`` (``$id``), not ``str.format``, so the
instructions file itself is free to use plain, unescaped ``{...}``
braces.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...general.tools._path_safety import assert_feat_id
from ...server import mcp


@mcp.prompt(
    name="implement_feat",
    title="Implement a feature plan phase by phase (orchestrator discipline)",
    description=(
        "Guides the LLM through implementing an existing feature plan, phase by phase, under "
        "the orchestrator discipline: read the plan in full, build a phase-by-phase TodoWrite "
        "list, delegate each phase to a fresh subagent via your host's task-delegation tool, "
        "if one exists (the DEC 4481b1fd-26e5-46bc-8f1b-236b638385b2 optional-delegation "
        "pattern, never assumed present), independently verify each subagent's result before "
        "advancing (re-run the phase's quality gate, inspect the diff, confirm the phase's "
        "acceptance criteria), never write or edit code files yourself, and fall back to "
        "direct single-session implementation when no delegation tool exists -- then run the "
        "capped review-fix loop after the final verification phase (3 cycles; done only "
        "after a clean exit)."
    ),
)
def implement_feat(id: str) -> str:
    """Return instructional text for implementing the feature plan ``id``.

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
        ``get_feat``, ``question``, or ``set_status`` itself -- it only
        narrates that sequence for the LLM to carry out.

    Raises
    ------
    ValueError
        If ``id`` is a blank/whitespace-only string, or not a
        well-formed ``feat-NNN-slug`` folder name.
    """
    assert isinstance(id, str), f"implement_feat() expects id as a str, got {id!r}"
    normalized_id = id.strip()
    if not normalized_id:
        raise ValueError(
            "implement_feat() received a blank id; pass the feature's feat-NNN-slug id "
            "(the containing folder's own name, e.g. 'feat-36-delete')."
        )
    assert_feat_id(normalized_id)
    template = Template(read_packaged_text("feat", "implement_instructions", "md"))
    result = template.substitute(id=normalized_id)
    return result
