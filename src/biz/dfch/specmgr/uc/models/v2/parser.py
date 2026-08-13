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

"""Parse raw use-case ``.md`` text into a :class:`UcDocument` (Task 1.8).

Fills the `from_text`/parser entry point gap `document.py`'s own docstring
flags: `UcDocument` deliberately holds no such method itself, and the
generic `models/md` engine only ever parses a *body* (`UseCase.from_text`),
never the combination of frontmatter + body a full on-disk file is. This
module is the thin free-function glue between the two, mirroring
`models.adr.v1.parser.parse_adr`'s own split (a free function, not a
classmethod on the document model) -- the "mirror whichever convention
feels closer" choice the feature README's Task 1.8 entry left open.

Unlike `parse_adr`, there is no dedicated structural-error exception type
here (no `UcParseError` equivalent on the v2 model tree): the generic
`models/md` engine reports a malformed heading/list structure as a plain
`AssertionError` (see `MarkdownStr.from_text`/`process_field`), and a
structurally-sound document whose field values or cross-field invariants
are invalid raises `pydantic.ValidationError` the normal Pydantic way --
both are deliberately left to propagate uncaught, exactly like `parse_adr`
leaves its own two error channels uncaught.
"""

from __future__ import annotations

import frontmatter

from biz.dfch.specmgr.models.md._markdown import format_text

from .document import UcDocument
from .frontmatter import UcFrontmatter
from .use_case import UseCase

__all__ = ["parse_uc"]


def parse_uc(text: str) -> UcDocument:
    """Parse a full use-case ``.md`` file's text into a :class:`UcDocument`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by a
        caller that never wrote it to disk at all, e.g. an MCP tool call).

    Returns
    -------
    UcDocument
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values (or cross-field
        invariants, e.g. an unresolvable `Extension`/`SubVariation`
        reference) fail schema validation -- see this module's docstring
        for the full split.
    """
    post = frontmatter.loads(text)
    fm = UcFrontmatter.model_validate(_stringify_metadata(post.metadata))
    body = UseCase.from_text(format_text(post.content))
    return UcDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block with a standard YAML
    loader, which auto-converts an unquoted date/timestamp (e.g.
    ``created: 2026-08-05T08:15:42``) into a ``datetime.date``/
    ``datetime.datetime`` -- but every :class:`UcFrontmatter` field
    inherited from :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter`
    is ``str | None``, so a raw non-``str`` object would fail Pydantic's
    (deliberately non-coercive) string validation. Converting via ``str()``
    reproduces the same text a human would have written. ``None`` (an empty
    YAML key) is passed through so the field's own optional-ness applies
    normally. Mirrors `models.adr.v1.parser._stringify_metadata` verbatim.
    """
    return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}
