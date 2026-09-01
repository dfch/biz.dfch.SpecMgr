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

"""``@mcp.tool()`` wrapper: validate_adr (plan §7, §8, §9a, §10 item 4; Task 3.2).

Thin file-I/O/id-lookup adapter -- re-reads and re-parses the current
on-disk state on every call; there is no in-memory cache of a parsed
:class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
of truth.

ADR's own structural error channel is :class:`~biz.dfch.specmgr.models.adr.
v1.parser.AdrParseError` (a plain ``ValueError`` subclass), not
``AssertionError`` like the eleven whole-body domains -- see that module's
own docstring for the full two-channel split. :func:`~biz.dfch.specmgr.
models.md._errors.wrap_tool_errors` is given ``also_catch=(AdrParseError,)``
here so that channel gets the same domain/tool context prefix as
``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError`` (REQ-005).
"""

from __future__ import annotations

from ...models.adr import AdrParseError
from ...models.md._errors import wrap_tool_errors
from ...server import mcp
from ._io import load_by_id
from ._paths import adr_base_dir


@mcp.tool(
    name="validate_adr",
    title="Validate ADR",
    description="Re-read and re-parse an ADR by id, letting the models' own Pydantic validators run.",
)
def validate_adr(id: str) -> bool:
    """Validate the ADR identified by ``id``.

    "Validate" is simply letting :class:`Adr`/:class:`AdrBody`/
    :class:`AdrFrontmatter`'s own Pydantic validators run during parsing
    (plan §7): there is no separate validation pass here. Successfully
    constructing the :class:`Adr` *is* the validation, so this function
    only ever returns ``True`` -- it never returns ``False``. Any parse or
    validation failure instead propagates as
    ``AdrParseError``/``pydantic.ValidationError``/``yaml.YAMLError`` --
    prefixed with domain/tool context by the shared tool-boundary wrapper
    (see Raises below), but otherwise the exact same exception -- so the
    MCP layer reports it naturally as a tool error, giving the LLM the
    underlying message to self-correct from.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    bool
        Always ``True`` on success.

    Raises
    ------
    AdrParseError
        A structural problem in the ADR's markdown body. The message is prefixed with
        domain/tool context by the shared tool-boundary wrapper
        (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`).
    pydantic.ValidationError
        A field/cross-field validation failure -- similarly prefixed.
    yaml.YAMLError
        Malformed frontmatter YAML -- similarly prefixed.
    AdrNotFoundError
        No ADR with this id -- untouched by this wrapper (already actionable).
    """
    base_dir = adr_base_dir()
    with wrap_tool_errors(domain="adr", tool="validate_adr", also_catch=(AdrParseError,)):
        load_by_id(base_dir, id)
    return True
