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

**Heading-mapping table pre-pass (feat-197-i18n Phase 125, ADR 38efdb66
item 5).** A 1:1 port of ``dec.models.v1.parser``'s own pre-pass for this
domain: ``parse_uc`` is this domain's single text-to-model parse boundary --
the choke point behind ``get_uc``'s non-raw reads, ``list_uc``'s rows (both
via the cache-backed ``read_uc``), and the path-based ``parse_uc`` tool -- and
it takes an optional ``language`` keyword (``None``/omitted or ``"en"`` =
canonical, no table -- byte-identical to the pre-i18n EN path; any other
language resolves its table via
:func:`biz.dfch.specmgr.general.models.resolve_heading_table`). When a table
exists, the mdformat-normalized body passes the fence-aware
:func:`biz.dfch.specmgr.general.models.normalize_heading_lines` pre-pass
before the *unchanged* ``models/md`` engine runs, so the parsed model holds
canonical heading text while the on-disk file keeps its translation.
``parse_uc_body`` is the body-only half of it (the single body-validation
entry point the write side shares: ``create_uc`` and the generic
``update``/``edit`` tools' ``uc`` adapters validate the caller's raw body
through it).
"""

from __future__ import annotations

from datetime import datetime

from biz.dfch.specmgr.general.models.heading_table import normalize_heading_lines, resolve_heading_table
from biz.dfch.specmgr.models.md._frontmatter_parse import parse_frontmatter
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md._timestamps import normalize_yaml_datetime

from .document import UcDocument
from .frontmatter import UcFrontmatter
from .use_case import UseCase

__all__ = ["parse_uc", "parse_uc_body"]


def parse_uc(text: str, *, language: str | None = None) -> UcDocument:
    """Parse a full use-case ``.md`` file's text into a :class:`UcDocument`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by a
        caller that never wrote it to disk at all, e.g. an MCP tool call).
    language:
        The document's language (feat-197-i18n, ADR 38efdb66 item 5):
        ``None`` (the default) or ``"en"`` parses the canonical, English
        headings as-is (no table -- byte-identical to the pre-i18n path);
        any other value resolves that language's heading-mapping table and
        applies the fence-aware heading-normalization pre-pass to the
        mdformat-normalized body before the ``models/md`` engine runs, so a
        translated document's fixed-text headings parse to the same
        canonical schema keys as their EN counterpart (data-carrying regex
        headings carry no table entry and match directly, their
        schema-constant tokens staying canonical in the file). The
        frontmatter is never transformed (its values are language-invariant,
        REQ-010).

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

    Raises
    ------
    ValueError
        A non-default ``language`` without a packaged heading-mapping table
        (the table loader's actionable error,
        :func:`biz.dfch.specmgr.general.models.load_heading_table`).
    """
    fm, content = parse_frontmatter(text, UcFrontmatter, domain="uc", stringify_metadata=_stringify_metadata)
    body = parse_uc_body(content, language=language)
    return UcDocument(frontmatter=fm, body=body)


def parse_uc_body(content: str, *, language: str | None = None) -> UseCase:
    """Parse a frontmatter-free use case body text into a :class:`UseCase`, in the given language.

    The body-only half of :func:`parse_uc` (feat-197-i18n Phase 125, ADR
    38efdb66 item 5): ``UseCase.from_text(format_text(content))`` with the
    optional per-language heading-normalization pre-pass between the two.
    It is the single body-validation entry point the write side shares --
    ``create_uc`` and the generic ``update``/``edit`` tools' ``uc``
    adapters validate the caller's raw body through it, so a language
    variant's translated headings are accepted exactly as the read side
    (:func:`parse_uc`, which itself delegates here) accepts them, and the
    persisted text stays the caller's raw body byte-for-byte (this function
    only validates; it never renders). With ``language`` omitted/``None``
    or ``"en"`` there is no table and the parse is byte-identical to the
    pre-i18n ``UseCase.from_text(format_text(content))``.

    Parameters
    ----------
    content:
        The body markdown only (no YAML frontmatter block).
    language:
        The body's language: ``None``/omitted or ``"en"`` = canonical
        headings as-is; any other value resolves that language's
        heading-mapping table via
        :func:`biz.dfch.specmgr.general.models.resolve_heading_table`.

    Returns
    -------
    UseCase
        The structured body (canonical heading text for every section).

    Raises
    ------
    AssertionError
        A malformed heading/list structure.
    pydantic.ValidationError
        A field or cross-field validation failure.
    ValueError
        A non-default ``language`` without a packaged heading-mapping table.
    """
    assert isinstance(content, str), type(content)
    assert language is None or isinstance(language, str), type(language)

    formatted = format_text(content)
    table = resolve_heading_table(language)
    if table is not None:
        formatted = normalize_heading_lines(formatted, table)
    result = UseCase.from_text(formatted)
    return result


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
