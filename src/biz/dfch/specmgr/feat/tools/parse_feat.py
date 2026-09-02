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

"""``@mcp.tool()`` wrapper: parse_feat (Task 2.3).

Reads a feature markdown file from disk and parses it into a structured
:class:`FeatDocument`, mirroring ``dec.tools.parse_dec``'s own pattern --
read path -> parse via free function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.

Unlike ``load_by_id``/``find_feat_path_by_id`` (Task 2.1/2.2), this tool
takes an arbitrary filesystem path, not an ``id`` -- it never checks that
``frontmatter.id`` matches the containing folder's own name (that invariant
is a *tool-layer addressing* concern, REQ-003, not something a bare
"parse this file" operation should enforce).
"""

from __future__ import annotations

from pathlib import Path

from ...models.md._errors import wrap_tool_errors
from ...server import mcp
from ..models.v1 import FeatDocument, parse_feat as _parse_feat


@mcp.tool(
    name="parse_feat",
    title="Parse feature",
    description=(
        "Parse a feature markdown file (YAML frontmatter + body) from disk into a structured "
        ":class:`~biz.dfch.specmgr.feat.models.v1.FeatDocument`."
    ),
)
def parse_feat(path: str) -> FeatDocument:
    """Parse the feature file at ``path`` into a :class:`FeatDocument`.

    Reads the file from disk, then parses and validates its content. "Parse"
    here also means "validate": letting :class:`Feature` /
    :class:`FeatFrontmatter` / :class:`FeatDocument`'s own Pydantic
    validators run during parsing is the only validation pass there is --
    there is no separate validation step. Any structural problem
    (unrecognized/misplaced heading, list the schema doesn't expect) or
    field/cross-field validation failure propagates as ``AssertionError``/``pydantic.ValidationError``,
    so the MCP layer reports it as a tool error with the underlying
    message, giving the caller something concrete to self-correct from.
    Similarly, file-access errors migrate as
    ``FileNotFoundError``/``PermissionError``/``OSError``.

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to parse (absolute or
        relative to the current working directory) -- typically
        ``<feature base dir>/<id>/README.md``.

    Returns
    -------
    FeatDocument
        The parsed, validated document.

    Raises
    ------
    AssertionError
        A structural problem in the parsed body (unrecognized/misplaced heading, a list the
        schema doesn't expect, ...). The message is prefixed with domain/tool context (e.g.
        ``"feat parse_feat: ..."``) by the shared tool-boundary wrapper
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
    with wrap_tool_errors(domain="feat", tool="parse_feat"):
        return _parse_feat(text)
