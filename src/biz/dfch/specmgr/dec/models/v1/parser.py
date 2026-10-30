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

"""Parse raw decision (DEC) ``.md`` text into a :class:`DecDocument`.

Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
flags: ``DecDocument`` deliberately holds no such method itself, and the generic
``models/md`` engine only ever parses a *body* (``Decision.from_text``), never
the combination of frontmatter + body a full on-disk file is. This module is
the thin free-function glue between the two, mirroring
``req/models/v1/parser.parse_req``/``gol/models/v1/parser.parse_gol``'s own
layout -- a free function, not a classmethod on the document model.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants (e.g. a duplicate ``### Option`` number) --
  deliberately left uncaught here, same as all other parsers in the project.

Like ``req.models.v1.parser.parse_req``/``gol.models.v1.parser.parse_gol``,
there is no dedicated structural-error exception type (no ``DecParseError``
equivalent); both error channels are plain ``AssertionError`` /
``pydantic.ValidationError`` that propagate uncaught.

**Heading-mapping table pre-pass (feat-197-i18n Phase 110, ADR 38efdb66
item 5).** This free function is ``dec``'s single text-to-model parse
boundary -- the choke point behind ``get_dec``'s non-raw reads, ``list_dec``'s
rows (both via the cache-backed ``read_dec``), and the path-based ``parse_dec``
tool -- and it is where the per-language heading-mapping table is applied: an
optional ``language`` keyword (``None``/omitted or ``"en"`` = canonical, no
table -- the parse runs byte-identically to the pre-i18n EN path; any other
language resolves its table via
:func:`biz.dfch.specmgr.general.models.resolve_heading_table`, which raises
its own actionable ``ValueError`` for a shape-valid language without a table
file) and, when a table exists, the mdformat-normalized body passes the
fence-aware :func:`biz.dfch.specmgr.general.models.normalize_heading_lines`
pre-pass before the *unchanged* ``models/md`` engine runs, so the parsed
model holds canonical heading text while the on-disk file keeps its
translation. The pre-pass is a ``ValueError``-free transform (it only rewrites
heading lines the table maps); every other error channel is unchanged.
"""

from __future__ import annotations

from datetime import datetime

from biz.dfch.specmgr.general.models.heading_table import normalize_heading_lines, resolve_heading_table
from biz.dfch.specmgr.models.md._frontmatter_parse import parse_frontmatter
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md._timestamps import normalize_yaml_datetime

from .body import Decision
from .document import DecDocument
from .frontmatter import DecFrontmatter

__all__ = ["parse_dec"]


def parse_dec(text: str, *, language: str | None = None) -> DecDocument:
    """Parse a full decision ``.md`` file's text into a :class:`DecDocument`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by an MCP
        tool call that never wrote it to disk at all).
    language:
        The document's language (feat-197-i18n, ADR 38efdb66 item 5):
        ``None`` (the default) or ``"en"`` parses the canonical, English
        headings as-is (no table -- byte-identical to the pre-i18n path);
        any other value resolves that language's heading-mapping table and
        applies the fence-aware heading-normalization pre-pass to the
        mdformat-normalized body before the ``models/md`` engine runs, so a
        translated document's fixed-text headings parse to the same
        canonical schema keys as their EN counterpart (the data-carrying
        regex headings -- ``### Option {N}:`` and the timestamp-led
        ``### {timestamp} - {title}`` entries -- carry no table entry and
        match directly, their schema-constant tokens staying canonical in
        the file). The frontmatter is never transformed (its values are
        language-invariant, REQ-010).

    Returns
    -------
    DecDocument
        The structured document, holding canonical heading text for every
        section (the same key set the EN parser produces, ACC-011).

    Raises
    ------
    AssertionError
        A malformed heading/list structure, propagating from
        ``process_field``/``from_text``.
    pydantic.ValidationError
        A structurally-sound document whose field values (or cross-field
        invariants) fail schema validation.
    yaml.YAMLError
        Malformed frontmatter YAML (both frontmatter error channels
        enriched by
        :func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`,
        feat-27-validation Phase 2).
    ValueError
        A non-default ``language`` without a packaged heading-mapping table
        (the table loader's actionable error,
        :func:`biz.dfch.specmgr.general.models.load_heading_table`).
    """
    fm, content = parse_frontmatter(text, DecFrontmatter, domain="dec", stringify_metadata=_stringify_metadata)
    formatted = format_text(content)
    table = resolve_heading_table(language)
    if table is not None:
        formatted = normalize_heading_lines(formatted, table)
    body = Decision.from_text(formatted)
    return DecDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python ``datetime``/
    ``date`` objects, but every :class:`DecFrontmatter` field inherited from
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

    Mirrors the same helper in ``req/models/v1/parser._stringify_metadata``/
    ``gol/models/v1/parser._stringify_metadata``.
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
