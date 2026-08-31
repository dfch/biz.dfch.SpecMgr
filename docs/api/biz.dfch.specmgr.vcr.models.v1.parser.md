# `biz.dfch.specmgr.vcr.models.v1.parser`

Parse raw verification case record (VCR) ``.md`` text into a :class:`VcrDocument`.

Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
flags: ``VcrDocument`` deliberately holds no such method itself, and the generic
``models/md`` engine only ever parses a *body* (``Vcr.from_text``), never
the combination of frontmatter + body a full on-disk file is. This module is
the thin free-function glue between the two, mirroring
``dec/models/v1/parser.parse_dec``'s own layout -- a free function, not a
classmethod on the document model.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants (e.g. a duplicate ``### AC-NNN`` number) --
  deliberately left uncaught here, same as all other parsers in the project.

Like ``dec.models.v1.parser.parse_dec``, there is no dedicated structural-error
exception type (no ``VcrParseError`` equivalent); both error channels are plain
``AssertionError`` / ``pydantic.ValidationError`` that propagate uncaught.

## Functions

### `_stringify_metadata(metadata: 'dict[str, object]') -> 'dict[str, object]'`

Coerce YAML-native scalar types back to ``str`` (or ``None``).

``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
which auto-converts unquoted dates/timestamps into Python datetime objects,
but every :class:`VcrFrontmatter` field inherited from
:class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
string validation. Converting via ``str()`` reproduces what a human would have
written.  ``None`` (from an empty YAML key like ``version:``) is passed
through so the field's own optional-ness applies normally.

Mirrors the same helper in ``dec/models/v1/parser._stringify_metadata``.


### `parse_vcr(text: 'str') -> 'VcrDocument'`

Parse a full verification case record ``.md`` file's text into a :class:`VcrDocument`.

Parameters
----------
text:
    The complete file content, YAML frontmatter block and markdown body
    together, exactly as read from disk (or submitted verbatim by an MCP
    tool call that never wrote it to disk at all).

Returns
-------
VcrDocument
    The structured document. Raises ``AssertionError`` for a malformed
    heading/list structure, or ``pydantic.ValidationError`` for a
    structurally-sound document whose field values (or cross-field
    invariants) fail schema validation -- see this module's docstring
    for the full split.

