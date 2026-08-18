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

"""``@mcp.tool()`` wrapper: parse_qa (Phase 4, Task 4.1).

Reads a QA markdown file from disk and parses it into a structured
:class:`QaDocument`, mirroring ``req.tools.parse_req``'s own pattern -- read
path -> parse via free-function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.
"""

from __future__ import annotations

from pathlib import Path

from ...server import mcp
from ..models.v1 import QaDocument, parse_qa as _parse_qa


@mcp.tool(
    name="parse_qa",
    title="Parse QA document",
    description=(
        "Parse a QA document markdown file (YAML frontmatter + body) from disk "
        "into a structured :class:`~biz.dfch.specmgr.qa.models.v1.QaDocument`."
    ),
)
def parse_qa(path: str) -> QaDocument:
    """Parse the QA file at ``path`` into a :class:`QaDocument`.

    Reads the file from disk, then parses and validates its content. "Parse"
    here also means "validate": letting :class:`Qa` / :class:`QaFrontmatter`
    / :class:`QaDocument`'s own Pydantic validators run during parsing is the
    only validation pass there is, exactly like ``adr.tools.validate_adr``'s
    own docstring describes for ADRs -- there is no separate validation step.
    Any structural problem (unrecognized/misplaced heading, list the schema
    doesn't expect) or field/cross-field validation failure is not caught or
    wrapped here: it propagates naturally as ``AssertionError``/
    ``pydantic.ValidationError``, so the MCP layer reports it as a tool error
    with the underlying message, giving the caller something concrete to
    self-correct from. Similarly, file-access errors migrate as
    ``FileNotFoundError``/``PermissionError``/``OSError``.

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to parse (absolute or
        relative to the current working directory).

    Returns
    -------
    QaDocument
        The parsed, validated document.
    """
    text = Path(path).read_text(encoding="utf-8")
    return _parse_qa(text)
