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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public prompt API, issue #41

"""``@mcp.prompt()``: repair (feat-150-mcp-lifecycle-commands, Phase 1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through repairing a whole-body specmgr document that currently fails to
parse: discovering it (with an ``id``: ``get_<d>(id)`` -- a document that
exists but fails to parse is returned, not raised: the result carries
``error`` (the parse-failure message, byte-identical to
``list_<d>``'s failed-row ``error`` for the same file -- identical field
path and cause, including the trailing pydantic documentation line) and
``path`` (the absolute on-disk
file), for every one of the whole-body domains per ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c; a truly absent id still raises the
domain's not-found error. Without one: ``list_<d>()``'s failed row, whose
``title``/``status`` carry the fixed ``"<failed to parse>"`` marker and
whose ``id`` is null while ``ref``/``path``/``error`` are populated),
reading the raw file via the host's own file-read tool (no specmgr MCP tool
can return the raw content of a document that fails to parse:
``get_<d>(raw=True)`` returns the non-raising parse-failure result for such
a document instead of its raw text, and the generic ``update`` (or
``edit``) tool re-parses the existing document before it can write
anything, returning the non-raising ``ParseFailureResult`` for a broken
one instead of writing or raising -- a truly-absent id still raises the
domain's not-found error -- and nothing is ever written), fixing only
what the error addresses while preserving the frontmatter
``id``/``created``/``status``/``version`` byte-for-byte and leaving
``updated`` untouched (a repair is not an edit), looping the generic
``validate(type, content, full=True)`` tool over the full raw text until
green, writing the repaired text back to the same path via the host's own
file-write tool -- explicitly NOT via the generic ``update`` tool, which is
structurally unable to repair a document that fails to parse -- and then
confirming the repair actually succeeded by calling ``get_<d>(id)`` again
(success: the parsed document, not an ``error``-carrying result; or,
without an ``id``, ``list_<d>()`` again, checking that the row's
``"<failed to parse>"`` marker and ``error`` are gone) against the file as
it now exists on disk. On a host without file read/write tools the
instructions degrade to diagnose-only (report the error and the proposed
fix, touch nothing).

``type`` is one of the whole-body domains (imported from
``general.tools._domains.WHOLE_BODY_DOMAINS``, the single source of truth
per feat-125-domain-lists); ADR is explicitly out of scope -- it has no
generic dry-run ``validate``/``update`` tooling of its own.

This prompt is cross-cutting (it takes ``type`` + an optional ``id``, not
tied to one domain), so -- like ``compact_history`` -- it lives under
``general.prompts`` rather than any single domain package. ``repair`` is a
deliberate exception to the ``<verb>_<domain>`` prompt-naming convention,
following the short, bare-word precedent of the cross-cutting,
type-dispatched tools ``validate``/``delete``/``list_references``.

The actual instructional text lives in its own packaged data file,
``general/data/general_repair_instructions.md``, read fresh on every call
via ``general.tools._packaged_data.read_packaged_text`` -- following the
same packaging convention already used for prompt instructions in the
``qa``/``adr``/``req``/``tsk`` domains (Task 0.19.1, Task 0.20).
Placeholders use ``string.Template`` (``$type``/``$id``), not
``str.format``, so the packaged file is free to use plain, unescaped
``{...}`` braces of its own.
"""

from __future__ import annotations

from string import Template

from ...general.tools._domains import ADR, WHOLE_BODY_DOMAINS
from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp

#: The literal placeholder substituted for ``$id`` when no ``id`` was given;
#: the instructions branch on whether the rendered text is a real id or this
#: placeholder (referenced in the packaged file by its "(not given --" prefix).
_ID_NOT_GIVEN_TEMPLATE = (
    "(not given -- no id was passed to this prompt; step 1 discovers the failed document via `list_{t}()`)"
)


@mcp.prompt(
    name="repair",
    title="Repair a specmgr document that fails to parse",
    description=(
        "Guides the LLM through repairing a whole-body specmgr document that currently fails to "
        "parse: discover it via get_<d>(id)'s non-raising parse-failure result (error/path/id -- "
        "the error text byte-identical to list_<d>()'s failed row for the same "
        "file; every whole-body "
        "domain, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c) when an id is given, or "
        "list_<d>()'s '<failed to parse>' failed row without one; read the raw file with the "
        "host's own file-read tool, fix only what the error addresses while preserving the "
        "frontmatter id/created/status/version byte-for-byte (a repair is not an edit), loop "
        "validate(type, content, full=True) until green, write the repaired text back to the same "
        "path with the host's own file-write tool (never via the generic update (or edit) tool, "
        "which is structurally unable to repair a document that fails to parse), then confirm the "
        "repair against the file as it now exists on disk with one more real get_<d>(id)/list_<d>() "
        "call (success: the parsed document, not an error-carrying result). Degrades to diagnose-only "
        "on a host without file read/write tools. ADR is out of scope."
    ),
)
def repair(type: str, id: str | None = None) -> str:
    """Return instructional text for repairing a whole-body document that fails to parse.

    Parameters
    ----------
    type:
        The document domain to repair: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
        ``vcr``, ``sysrs`` (matched case-insensitively). ``"adr"`` is
        explicitly rejected with an actionable error (ADR is not a
        whole-body domain and has no generic dry-run ``validate`` tooling);
        so is any other unknown value.
    id:
        The failing document's id, when known. When absent, the returned
        instructions direct discovery via ``list_<type>()``'s failed row
        (the ``<failed to parse>`` marker, a null ``id``, populated
        ``ref``/``path``/``error``) instead of ``get_<type>(id)``.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.

    Raises
    ------
    ValueError
        If ``type`` is ``"adr"`` (ADR exclusion) or an unknown domain, or
        if ``id`` is a blank/whitespace-only string (pass a real id, or
        omit the parameter entirely).
    """
    assert isinstance(type, str), f"repair() expects type as a str, got {type!r}"
    assert id is None or isinstance(id, str), f"repair() expects id as a str or None, got {id!r}"
    if id is not None and not id.strip():
        raise ValueError(
            f"repair() received a blank id for type {type!r}; pass the document's real id, or "
            "omit the id parameter entirely (discovery then scans list_<type>()'s failed rows)."
        )
    normalized_type = type.strip().lower()
    if normalized_type == ADR:
        raise ValueError(
            "repair() does not support type 'adr': ADR is not a whole-body domain and has no "
            "generic dry-run validate tooling of its own (its standalone validate_adr re-reads "
            "the ADR from disk by id), so the repair loop is not defined for it."
        )
    if normalized_type not in WHOLE_BODY_DOMAINS:
        raise ValueError(
            f"repair() does not support type {normalized_type!r}; expected one of "
            f"{'/'.join(WHOLE_BODY_DOMAINS)} ('adr' is explicitly out of scope)."
        )
    template = Template(read_packaged_text("general", "repair_instructions", "md"))
    result = template.substitute(
        type=normalized_type,
        id=id or _ID_NOT_GIVEN_TEMPLATE.format(t=normalized_type),
    )
    return result
