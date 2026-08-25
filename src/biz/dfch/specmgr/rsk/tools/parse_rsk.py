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

"""``@mcp.tool()`` wrapper: parse_rsk (Task 3.2).

Reads a risk markdown file from disk and parses it into a structured
:class:`RskDocument`, mirroring ``tsk.tools.parse_tsk``'s own pattern -- read
path -> parse via free-function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v1 import RskDocument, parse_rsk as _parse_rsk
from ...server import mcp


@mcp.tool(
    name="parse_rsk",
    title="Parse risk",
    description=(
        "Parse a risk markdown file (YAML frontmatter + body) from disk "
        "into a structured :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument`."
    ),
)
def parse_rsk(path: str) -> RskDocument:
    """Parse the risk file at ``path`` into a :class:`RskDocument`.

    Reads the file from disk, then parses and validates its content. "Parse"
    here also means "validate": letting :class:`Risk` /
    :class:`RskFrontmatter` / :class:`RskDocument`'s own Pydantic validators
    run during parsing is the only validation pass there is, exactly like
    ``tsk.tools.parse_tsk``'s own docstring describes for task lists --
    there is no separate validation step. Any structural problem
    (unrecognized/misplaced heading, an assessment H3 outside its regex
    ``@alias``, wrong section order) or field/cross-field validation
    failure is not caught or wrapped here: it propagates naturally as
    ``AssertionError``/``pydantic.ValidationError``, so the MCP layer
    reports it as a tool error with the underlying message, giving the
    caller something concrete to self-correct from. Similarly, file-access
    errors migrate as ``FileNotFoundError``/``PermissionError``/``OSError``.

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to parse (absolute or
        relative to the current working directory).

    Returns
    -------
    RskDocument
        The parsed, validated document.
    """
    text = Path(path).read_text(encoding="utf-8")
    return _parse_rsk(text)
