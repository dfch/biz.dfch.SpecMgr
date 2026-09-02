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

"""Parse raw TaskList ``.md`` text into a :class:`TskDocument` (Phase 2, Task 2.2).

Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
flags: ``TskDocument`` deliberately holds no such method itself, and the generic
``models/md`` engine only ever parses a *body* (``Task.from_text``), never the
combination of frontmatter + body a full on-disk file is. This module is the
thin free-function glue between the two, mirroring ``req/models/v1/parser.parse_req``'s
own layout -- a free function, not a classmethod on the document model.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants -- deliberately left uncaught here, same as all other
  parsers in the project.

Like ``req.models.v1.parser.parse_req``, there is no dedicated structural-error
exception type; both error channels are plain ``AssertionError`` /
``pydantic.ValidationError`` that propagate uncaught.
"""

from __future__ import annotations

from biz.dfch.specmgr.models.md._frontmatter_parse import parse_frontmatter
from biz.dfch.specmgr.models.md._markdown import format_text

from .document import TskDocument
from .body import Task
from .frontmatter import TskFrontmatter

__all__ = ["parse_tsk"]


def parse_tsk(text: str) -> TskDocument:
    """Parse a full TaskList ``.md`` file's text into a :class:`TskDocument`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by an MCP
        tool call that never wrote it to disk at all).

    Returns
    -------
    TskDocument
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values (or cross-field
        invariants) fail schema validation -- see this module's docstring
        for the full split. Raises ``yaml.YAMLError`` for malformed
        frontmatter YAML -- both frontmatter error channels are enriched by
        :func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`
        (feat-27-validation Phase 2).
    """
    fm, content = parse_frontmatter(text, TskFrontmatter, domain="tsk", stringify_metadata=_stringify_metadata)
    body = Task.from_text(format_text(content))
    return TskDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python datetime objects,
    but every :class:`TskFrontmatter` field inherited from
    :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
    so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
    string validation. Converting via ``str()`` reproduces what a human would have
    written.  ``None`` (from an empty YAML key like ``version:``) is passed
    through so the field's own optional-ness applies normally.

    Mirrors the same helper in ``req/models/v1/parser._stringify_metadata``.
    """
    return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}
