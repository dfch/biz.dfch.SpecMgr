# `biz.dfch.specmgr.uc.models.v2.parser`

Parse raw use-case ``.md`` text into a :class:`UcDocument` (Task 1.8).

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

## Functions

### `_stringify_metadata(metadata: 'dict[str, object]') -> 'dict[str, object]'`

Coerce YAML-native scalar types back to ``str`` (or ``None``).

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


### `parse_uc(text: 'str') -> 'UcDocument'`

Parse a full use-case ``.md`` file's text into a :class:`UcDocument`.

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

