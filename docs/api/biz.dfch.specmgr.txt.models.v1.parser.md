# `biz.dfch.specmgr.txt.models.v1.parser`

Parse raw free-form text (TXT) ``.md`` text into a :class:`TxtDocument`.

Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
flags: ``TxtDocument`` deliberately holds no such method itself, and the generic
``models/md`` engine only ever parses a *body* (``Txt.from_text``), never
the combination of frontmatter + body a full on-disk file is. This module is
the thin free-function glue between the two, mirroring
``vcr/models/v1/parser.parse_vcr``'s own layout -- a free function, not a
classmethod on the document model.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections -- e.g. a missing ``## Updates`` or a leftover second
  top-level H2), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values
  or cross-field invariants (e.g. out-of-order ``## Updates`` entries, a
  frontmatter ``status`` outside the closed three-value set) --
  deliberately left uncaught here, same as all other parsers in the project.

Like ``vcr.models.v1.parser.parse_vcr``, there is no dedicated structural-error
exception type (no ``TxtParseError`` equivalent); both error channels are plain
``AssertionError`` / ``pydantic.ValidationError`` that propagate uncaught.
The engine's default error messages are kept unchanged -- no custom
cause/fix-hint wrapping for the leftover-text or missing-``Updates`` errors
(REQ-011).

**Heading-mapping table pre-pass (feat-197-i18n Phase 125, ADR 38efdb66
item 5).** A 1:1 port of ``dec.models.v1.parser``'s own pre-pass for this
domain: ``parse_txt`` is this domain's single text-to-model parse boundary --
the choke point behind ``get_txt``'s non-raw reads, ``list_txt``'s rows (both
via the cache-backed ``read_txt``), and the path-based ``parse_txt`` tool -- and
it takes an optional ``language`` keyword (``None``/omitted or ``"en"`` =
canonical, no table -- byte-identical to the pre-i18n EN path; any other
language resolves its table via
:func:`biz.dfch.specmgr.general.models.resolve_heading_table`). When a table
exists, the mdformat-normalized body passes the fence-aware
:func:`biz.dfch.specmgr.general.models.normalize_heading_lines` pre-pass
before the *unchanged* ``models/md`` engine runs, so the parsed model holds
canonical heading text while the on-disk file keeps its translation.
``parse_txt_body`` is the body-only half of it (the single body-validation
entry point the write side shares: ``create_txt`` and the generic
``update``/``edit`` tools' ``txt`` adapters validate the caller's raw body
through it).

Unlike every other domain, ``txt`` does **not** run the generic
:func:`~biz.dfch.specmgr.general.models.normalize_heading_lines` pass over the
whole body (feat-229-txt Phase 180, review finding E1): the free-form body is
opaque (REQ-002, "accepted verbatim"), so its free headings are *not* schema
headings and must never be rewritten -- a free ``## Zusammenfassung`` has to stay
exactly that in the parsed model, not become ``## Summary``. The only fixed-text
schema heading of this domain is ``## Updates``, so :func:`_normalize_updates_heading`
rewrites exactly that one line: the first top-level (outside a code fence) H2
whose text the table maps to ``Updates`` (or that already reads ``Updates``) --
the same "first top-level ``## Updates`` is the boundary" rule as the EN
path, with the language's own spelling of the word. Every other line, free
headings and update-entry content included, stays byte-identical.

## Functions

### `_normalize_updates_heading(text: 'str', table: 'dict[str, str]') -> 'str'`

Rewrite the one table-mapped ``## Updates`` heading line to its canonical text; touch nothing else.

The txt-specific replacement for the generic
:func:`~biz.dfch.specmgr.general.models.normalize_heading_lines` pass
(feat-229-txt Phase 180, review finding E1): ``txt``'s body is opaque, so
only the boundary heading is a schema heading. The first top-level H2
(:func:`~biz.dfch.specmgr.general.models.heading_table.iter_heading_lines`:
fence-aware, ``^## `` at column 0) whose text equals ``Updates`` after the
table lookup is the boundary; when its text differs from ``Updates`` its
line is rewritten to ``## Updates``. Free body headings -- even ones whose
text happens to be another table key -- stay byte-identical, and so does
everything after the boundary (update-entry headings are timestamp-led and
carry no table entry; entry content is opaque too).

Parameters
----------
text:
    The mdformat-normalized body text.
table:
    The language's ``<translated> -> <canonical>`` mapping.

Returns
-------
str
    ``text`` with at most one line (the boundary heading) rewritten; same
    line count, same join. Unchanged when no heading maps to ``Updates``
    (the engine then rejects the document with its own missing-section error).


### `_stringify_metadata(metadata: 'dict[str, object]') -> 'dict[str, object]'`

Coerce YAML-native scalar types back to ``str`` (or ``None``).

``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
which auto-converts unquoted dates/timestamps into Python ``datetime``/
``date`` objects, but every :class:`TxtFrontmatter` field inherited from
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

Mirrors the same helper in ``vcr/models/v1/parser._stringify_metadata``.


### `parse_txt(text: 'str', *, language: 'str | None' = None) -> 'TxtDocument'`

Parse a full free-form text ``.md`` file's text into a :class:`TxtDocument`.

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
TxtDocument
    The structured document. Raises ``AssertionError`` for a malformed
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


### `parse_txt_body(content: 'str', *, language: 'str | None' = None) -> 'Txt'`

Parse a frontmatter-free free-form text body text into a :class:`Txt`, in the given language.

The body-only half of :func:`parse_txt` (feat-197-i18n Phase 125, ADR
38efdb66 item 5): ``Txt.from_text(format_text(content))`` with the
optional per-language heading-normalization pre-pass between the two.
It is the single body-validation entry point the write side shares --
``create_txt`` and the generic ``update``/``edit`` tools' ``txt``
adapters validate the caller's raw body through it, so a language
variant's translated headings are accepted exactly as the read side
(:func:`parse_txt`, which itself delegates here) accepts them, and the
persisted text stays the caller's raw body byte-for-byte (this function
only validates; it never renders). With ``language`` omitted/``None``
or ``"en"`` there is no table and the parse is byte-identical to the
pre-i18n ``Txt.from_text(format_text(content))``.

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
Txt
    The structured body (canonical heading text for every section).

Raises
------
AssertionError
    A malformed heading/list structure.
pydantic.ValidationError
    A field or cross-field validation failure.
ValueError
    A non-default ``language`` without a packaged heading-mapping table.

