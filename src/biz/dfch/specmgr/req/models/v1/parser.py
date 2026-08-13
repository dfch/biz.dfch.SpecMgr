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

"""Parse raw requirement ``.md`` text into a :class:`ReqDocument` (Task 1.x).

Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
flags: ``ReqDocument`` deliberately holds no such method itself, and the generic
``models/md`` engine only ever parses a *body* (``Requirement.from_text``),
never the combination of frontmatter + body a full on-disk file is. This module
is the thin free-function glue between the two, mirroring
``uc/models/v2/parser.parse_uc``'s own layout -- a free function, not a
classmethod on the document model.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants -- deliberately left uncaught here, same as all other
  parsers in the project.

Unlike ADR's ``models.adr.v1.parser.parse_adr``, there is no dedicated
structural-error exception type (no ``ReqParseError`` equivalent); both error
channels are plain ``AssertionError`` / ``pydantic.ValidationError`` that
propagate uncaught, exactly like ``uc.models.v2.parser.parse_uc``.
"""

from __future__ import annotations

import frontmatter  # requires the ``frontmatter`` extra from pyproject.toml

from biz.dfch.specmgr.models.md._markdown import format_text

from .document import ReqDocument
from .body import Requirement
from .frontmatter import ReqFrontmatter

__all__ = ["parse_req"]


def parse_req(text: str) -> ReqDocument:
    """Parse a full requirement ``.md`` file's text into a :class:`ReqDocument`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by an MCP
        tool call that never wrote it to disk at all).

    Returns
    -------
    ReqDocument
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values (or cross-field
        invariants) fail schema validation -- see this module's docstring
        for the full split.
    """
    post = frontmatter.loads(text)  # type: ignore[union-attr]
    fm = ReqFrontmatter.model_validate(_stringify_metadata(post.metadata))
    body = Requirement.from_text(format_text(post.content))
    return ReqDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python datetime objects,
    but every :class:`ReqFrontmatter` field inherited from
    :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
    so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
    string validation. Converting via ``str()`` reproduces what a human would have
    written.  ``None`` (from an empty YAML key like ``version:``) is passed
    through so the field's own optional-ness applies normally.

    Mirrors the same helper in ``uc/models/v2/parser._stringify_metadata``.
    """
    return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}
