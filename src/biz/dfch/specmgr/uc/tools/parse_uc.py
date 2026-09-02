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

"""``@mcp.tool()`` wrapper: parse_uc.

Reads a use-case markdown file from disk and parses it into a structured
:class:`UcDocument`. Path-based (not id-based) by design -- ``get_uc``
(``uc.tools.get_uc``) is the id-based read path over the use-case base
directory (``uc.tools._paths``/``_io``); this tool instead parses any
markdown file the caller points it at directly.
"""

from __future__ import annotations

from pathlib import Path

from ...models.md._errors import wrap_tool_errors
from ...server import mcp
from ..models.v2 import UcDocument, parse_uc as _parse_uc


@mcp.tool(
    name="parse_uc",
    title="Parse use case",
    description="Parse a use-case markdown file (YAML frontmatter + body) from disk into a structured document.",
)
def parse_uc(path: str) -> UcDocument:
    """Parse the use-case file at ``path`` into a :class:`UcDocument`.

    Reads the file from disk, then parses and validates its content. "Parse"
    here also means "validate": letting :class:`UseCase`/
    :class:`UcFrontmatter`/:class:`UcDocument`'s own Pydantic validators
    run during parsing is the only validation pass there is, exactly like
    `adr.tools.validate_adr`'s own docstring describes for ADRs -- there is
    no separate validation step. Any structural problem (an unrecognized/
    misplaced heading, a list the schema doesn't expect) or field/
    cross-field validation failure propagates as ``AssertionError``/``pydantic.ValidationError``,
    so the MCP layer reports it as a tool error with the underlying
    message, giving the caller something concrete to self-correct from.
    Similarly, file-access errors (missing file, permission denied) propagate
    as ``FileNotFoundError``/``PermissionError``/``OSError``.

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to parse (absolute or
        relative to the current working directory).

    Returns
    -------
    UcDocument
        The parsed, validated document.

    Raises
    ------
    AssertionError
        A structural problem in the parsed body (unrecognized/misplaced heading, a list the
        schema doesn't expect, ...). The message is prefixed with domain/tool context (e.g.
        ``"uc parse_uc: ..."``) by the shared tool-boundary wrapper
        (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top of the
        engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
    pydantic.ValidationError
        A field/cross-field validation failure -- similarly prefixed.
    yaml.YAMLError
        Malformed frontmatter YAML -- similarly prefixed, on top of the frontmatter-block
        naming and document-relative line remap :mod:`~biz.dfch.specmgr.models.md.
        _frontmatter_parse` already applies.
    FileNotFoundError / PermissionError / OSError
        A file-access failure reading ``path`` -- untouched by this wrapper (already
        actionable; out of this feature's scope).
    """
    text = Path(path).read_text(encoding="utf-8")
    with wrap_tool_errors(domain="uc", tool="parse_uc"):
        return _parse_uc(text)
