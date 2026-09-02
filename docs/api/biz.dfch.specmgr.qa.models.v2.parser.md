# `biz.dfch.specmgr.qa.models.v2.parser`

Parse raw Question and Answer (QA) ``.md`` text into a :class:`QaDocument` (v2).

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

## Functions

### `_stringify_metadata(metadata: 'dict[str, object]') -> 'dict[str, object]'`

Coerce YAML-native scalar types back to ``str`` (or ``None``).

``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
which auto-converts unquoted dates/timestamps into Python datetime objects,
but every :class:`QaFrontmatter` field inherited from
:class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
string validation. Converting via ``str()`` reproduces what a human would have
written.  ``None`` (from an empty YAML key like ``version:``) is passed
through so the field's own optional-ness applies normally.


### `parse_qa(text: 'str') -> 'QaDocument'`

Parse a full Question and Answer (QA) ``.md`` file's text into a :class:`QaDocument` (v2).

Parameters
----------
text:
    The complete file content, YAML frontmatter block and markdown body
    together, exactly as read from disk (or submitted verbatim by an MCP
    tool call that never wrote it to disk at all).

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

