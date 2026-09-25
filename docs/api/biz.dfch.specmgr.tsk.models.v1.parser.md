# `biz.dfch.specmgr.tsk.models.v1.parser`

Parse raw TaskList ``.md`` text into a :class:`TskDocument` (Phase 2, Task 2.2).

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

## Functions

### `_stringify_metadata(metadata: 'dict[str, object]') -> 'dict[str, object]'`

Coerce YAML-native scalar types back to ``str`` (or ``None``).

``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
which auto-converts unquoted dates/timestamps into Python ``datetime``/
``date`` objects, but every :class:`TskFrontmatter` field inherited from
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


### `parse_tsk(text: 'str') -> 'TskDocument'`

Parse a full TaskList ``.md`` file's text into a :class:`TskDocument`.

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

