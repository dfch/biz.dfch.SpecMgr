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

"""Parse raw Question and Answer (QA) ``.md`` text into a :class:`QaDocument` (v2).

Mirrors `uc/models/v2/parser.py::parse_uc`'s unconditional-parsing shape:
there is no runtime `version` inspection/gate here at all. `QaFrontmatter.version`
was found to encode the shared `models.md` parsing engine's own schema
version (hardcoded to major 1, `models/md/_util.py::SCHEMA_MAJOR_VERSION`),
not a per-document-type body-schema version, and can never carry a major-2
value for any document that validates as `QaFrontmatter` at all -- so no
`version`-based dispatch is possible. This function always parses the body
via v2's own `Qa` schema; a document shaped for the removed `qa/models/v1/`
body schema (or otherwise non-v2-shaped) simply fails naturally with
whatever structural `AssertionError`/`pydantic.ValidationError`
`Qa.from_text`/`QaFrontmatter.model_validate` raises on its own -- there is
no fallback parsing path and no explicit version check.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants -- deliberately left uncaught here, same as all other
  parsers in the project.

**Heading-mapping table pre-pass (feat-197-i18n Phase 125, ADR 38efdb66
item 5).** A 1:1 port of ``dec.models.v1.parser``'s own pre-pass for this
domain: ``parse_qa`` is this domain's single text-to-model parse boundary --
the choke point behind ``get_qa``'s non-raw reads, ``list_qa``'s rows (both
via the cache-backed ``read_qa``), and the path-based ``parse_qa`` tool -- and
it takes an optional ``language`` keyword (``None``/omitted or ``"en"`` =
canonical, no table -- byte-identical to the pre-i18n EN path; any other
language resolves its table via
:func:`biz.dfch.specmgr.general.models.resolve_heading_table`). When a table
exists, the mdformat-normalized body passes the fence-aware
:func:`biz.dfch.specmgr.general.models.normalize_heading_lines` pre-pass
before the *unchanged* ``models/md`` engine runs, so the parsed model holds
canonical heading text while the on-disk file keeps its translation.
``parse_qa_body`` is the body-only half of it (the single body-validation
entry point the write side shares: ``create_qa`` and the generic
``update``/``edit`` tools' ``qa`` adapters validate the caller's raw body
through it).
"""

from __future__ import annotations

from datetime import datetime

from biz.dfch.specmgr.general.models.heading_table import normalize_heading_lines, resolve_heading_table
from biz.dfch.specmgr.models.md._frontmatter_parse import parse_frontmatter
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.models.md._timestamps import normalize_yaml_datetime

from .body import Qa
from .document import QaDocument
from .frontmatter import QaFrontmatter

__all__ = ["parse_qa", "parse_qa_body"]


def parse_qa(text: str, *, language: str | None = None) -> QaDocument:
    """Parse a full Question and Answer (QA) ``.md`` file's text into a :class:`QaDocument` (v2).

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
        canonical schema keys as their EN counterpart (data-carrying regex
        headings carry no table entry and match directly, their
        schema-constant tokens staying canonical in the file). The
        frontmatter is never transformed (its values are language-invariant,
        REQ-010).

    Returns
    -------
    QaDocument
        The structured v2 document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values (or cross-field
        invariants) fail schema validation -- see this module's docstring
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
    fm, content = parse_frontmatter(text, QaFrontmatter, domain="qa", stringify_metadata=_stringify_metadata)
    body = parse_qa_body(content, language=language)
    return QaDocument(frontmatter=fm, body=body)


def parse_qa_body(content: str, *, language: str | None = None) -> Qa:
    """Parse a frontmatter-free QA document body text into a :class:`Qa`, in the given language.

    The body-only half of :func:`parse_qa` (feat-197-i18n Phase 125, ADR
    38efdb66 item 5): ``Qa.from_text(format_text(content))`` with the
    optional per-language heading-normalization pre-pass between the two.
    It is the single body-validation entry point the write side shares --
    ``create_qa`` and the generic ``update``/``edit`` tools' ``qa``
    adapters validate the caller's raw body through it, so a language
    variant's translated headings are accepted exactly as the read side
    (:func:`parse_qa`, which itself delegates here) accepts them, and the
    persisted text stays the caller's raw body byte-for-byte (this function
    only validates; it never renders). With ``language`` omitted/``None``
    or ``"en"`` there is no table and the parse is byte-identical to the
    pre-i18n ``Qa.from_text(format_text(content))``.

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
    Qa
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
    result = Qa.from_text(formatted)
    return result


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python ``datetime``/
    ``date`` objects, but every :class:`QaFrontmatter` field inherited from
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

    Mirrors the same helper in ``prb/models/v1/parser._stringify_metadata``.
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
