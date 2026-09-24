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

from datetime import datetime

from biz.dfch.specmgr.models.md._frontmatter_parse import parse_frontmatter
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md._timestamps import normalize_yaml_datetime

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
        for the full split. Raises ``yaml.YAMLError`` for malformed
        frontmatter YAML -- both frontmatter error channels are enriched by
        :func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`
        (feat-27-validation Phase 2).
    """
    fm, content = parse_frontmatter(text, UcFrontmatter, domain="uc", stringify_metadata=_stringify_metadata)
    body = UseCase.from_text(format_text(content))
    return UcDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python ``datetime``/
    ``date`` objects, but every :class:`UcFrontmatter` field inherited from
    :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
    so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
    string validation. ``None`` (from an empty YAML key like ``version:``) is
    passed through so the field's own optional-ness applies normally.

    A coerced ``datetime`` (an unquoted timestamp in either the ``T`` or the
    space separator) is normalized to the ``T``-canonical form with exactly
    three millisecond digits via
    :func:`~biz.dfch.specmgr.models.md._timestamps.normalize_yaml_datetime`
    (feat-146, REQ-006): a bare ``str()`` would drop the milliseconds of a
    whole-millisecond value (rendering six fraction digits -- a rejected
    shape), render a zero UTC offset as ``+00:00`` instead of ``Z``, and keep
    the space separator instead of converging to the machine-written ``T``
    form. That same helper's own guard returns a bare ``str()`` for a
    six-digit-fraction unquoted timestamp instead, so it reaches the
    frontmatter's date+time pattern validator in a rejected, actionable shape
    rather than being silently truncated into an accepted one. A coerced
    ``date`` (an unquoted date-only value) still stringifies via ``str()`` to
    its ``yyyy-MM-dd`` text, where the same pattern validator rejects it --
    date-only and six-digit fractions remain rejected (feat-146 REQ-003).

    Mirrors the same helper in ``req/models/v1/parser._stringify_metadata``.
    """
    result: dict[str, object] = {}
    for key, value in metadata.items():
        if value is None or isinstance(value, str):
            result[key] = value
        elif isinstance(value, datetime):
            result[key] = normalize_yaml_datetime(value)
        else:
            result[key] = str(value)
    return result
