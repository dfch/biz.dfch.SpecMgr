# `biz.dfch.specmgr.models.md._frontmatter_parse`

Shared frontmatter-parsing error enrichment (feat-27-validation Phase 2, Tasks 2.1/2.2).

Every one of the twelve domains' ``parser.py`` modules (eleven whole-body domains plus ADR)
shares the exact same three-line shape::

    post = frontmatter.loads(text)                                    # yaml.YAMLError
    fm = SomeFrontmatter.model_validate(_stringify_metadata(post.metadata))  # ValidationError
    body = SomeBody.from_text(format_text(post.content))

This module centralizes the first two lines' error handling behind :func:`parse_frontmatter`,
so every domain parser gets identical enrichment of both frontmatter error channels without
duplicating the line-remap/message-building logic twelve times (REQ-005):

- ``yaml.YAMLError`` (malformed YAML) -- :func:`enrich_frontmatter_yaml_error` returns a
  same-type, re-raiseable copy whose location marks name "the frontmatter block" (instead of
  PyYAML's own opaque ``"<unicode string>"``) and whose line numbers are remapped from
  block-relative (relative to the YAML substring ``frontmatter.loads`` hands to PyYAML) to
  document-relative (REQ-004). No new exception type -- the returned object is the exact same
  ``type(error)`` (e.g. ``yaml.parser.ParserError``), per REQ-006.
- ``pydantic.ValidationError`` (out-of-vocabulary/invalid field values) --
  :func:`enrich_frontmatter_validation_error` returns a same-type, re-raiseable copy whose
  per-field messages are prefixed with the domain and the frontmatter field's own
  document-relative line (when locatable), per REQ-004/REQ-006.

This module deliberately is NOT ``models/md/_errors.py`` -- that name is reserved for Phase
3's Task 3.1 shared tool-boundary (domain + tool + frontmatter-vs-body) context wrapper, which
is free to reuse the helpers here (:func:`frontmatter_opening_line` in particular) rather than
duplicate them.

## Functions

### `_describe_validation_error(text: 'str', domain: 'str', detail: 'dict[str, object]') -> 'str'`

Build one enriched per-field message: domain + frontmatter block + field path + a
document-relative line number (when locatable) + the original pydantic message.


### `_field_line(text: 'str', field_name: 'str') -> 'int | None'`

Return the 1-based document line number of ``field_name``'s own ``key:`` line within
``text``'s frontmatter block, or ``None`` if it cannot be located (e.g. a dotted/nested
``field_name``, which never appears as its own top-level ``key:`` line).


### `_frontmatter_content_lines(text: 'str') -> 'tuple[list[str], int]'`

Return the frontmatter block's own content lines (the lines strictly between the
opening and closing ``---`` delimiters) and the 1-based document line number of the first
one.


### `_remap_mark(mark: 'yaml.error.Mark | None', opening_line: 'int') -> 'yaml.error.Mark | None'`

Return a copy of ``mark`` renamed to the frontmatter block and shifted to a
document-relative line, or ``None`` if ``mark`` itself is ``None`` (context/problem marks
are optional on a ``MarkedYAMLError``).


### `enrich_frontmatter_validation_error(text: 'str', error: 'ValidationError', *, domain: 'str') -> 'ValidationError'`

Return a same-type, re-raiseable copy of ``error`` whose per-field messages name the
domain, the frontmatter block, and (when locatable) a document-relative line number
(REQ-004/Task 2.2/REQ-006).

Parameters
----------
text:
    The complete, original file content whose frontmatter failed field validation.
error:
    The ``pydantic.ValidationError`` raised by ``SomeFrontmatter.model_validate(...)``.
domain:
    The short domain code (e.g. ``"tsk"``, ``"req"``, ``"adr"``) to name in each enriched
    message.

Returns
-------
pydantic.ValidationError
    A new ``pydantic.ValidationError`` (the exact same exception type, per REQ-006, since
    ``pydantic.ValidationError`` *is* ``pydantic_core.ValidationError`` and
    ``ValidationError.from_exception_data`` is its own public constructor) whose per-field
    messages are the enriched ones built by this function.


### `enrich_frontmatter_yaml_error(text: 'str', error: 'yaml.YAMLError') -> 'yaml.YAMLError'`

Return a same-type, re-raiseable copy of ``error`` naming the frontmatter block and
carrying document-relative line numbers (REQ-004/REQ-006).

PyYAML's ``mark.line`` is 0-based and relative to the YAML substring
``frontmatter.loads`` hands it (block-relative), and ``mark.name`` is the opaque
placeholder ``"<unicode string>"`` PyYAML uses for any string (as opposed to file) input.
Both are replaced -- the mark's ``column``/``buffer``/``pointer`` (which drive the
"offending snippet" PyYAML prints) are left untouched, so the underlying PyYAML detail
(the ``context``/``problem`` messages and the source snippet) is carried alongside the
corrected location, not replaced by it.

Parameters
----------
text:
    The complete, original file content passed to ``frontmatter.loads``.
error:
    The ``yaml.YAMLError`` raised by ``frontmatter.loads(text)``.

Returns
-------
yaml.YAMLError
    A new instance of ``type(error)`` (e.g. ``yaml.parser.ParserError``) -- the exact same
    exception type, per REQ-006 -- with enriched location marks. If ``error`` is not a
    ``yaml.error.MarkedYAMLError`` (no mark to remap), ``error`` itself is returned
    unchanged.


### `frontmatter_opening_line(text: 'str') -> 'int'`

Return the 1-based document line number of the frontmatter's opening ``---`` delimiter.

``frontmatter.loads``/``frontmatter.parse`` call ``text.strip()`` internally before
splitting on the ``---`` boundary (see ``frontmatter.parse``), so the opening delimiter is
always the stripped text's own line 1 -- but any leading blank/whitespace lines in the
*original*, unstripped ``text`` shift that delimiter's real document-relative line number.
This restores that offset by counting the newlines within the leading whitespace
``str.strip()``/``str.lstrip()`` would remove.

Parameters
----------
text:
    The complete, original file content (frontmatter block and body together), exactly as
    passed to ``frontmatter.loads``.

Returns
-------
int
    The 1-based document line number of the opening ``---`` delimiter line.


### `parse_frontmatter(text: 'str', frontmatter_cls: 'type[FrontmatterT]', *, domain: 'str', stringify_metadata: 'Callable[[dict[str, object]], dict[str, object]] | None' = None) -> 'tuple[FrontmatterT, str]'`

Parse ``text``'s YAML frontmatter block into ``frontmatter_cls``, enriching both
frontmatter error channels uniformly (Phase 2, Tasks 2.1/2.2), and return the validated
frontmatter plus the frontmatter-stripped body text.

Every domain ``parser.py`` module's own ``parse_<d>`` function calls this once in place of
its previous bare ``frontmatter.loads(text)`` / ``SomeFrontmatter.model_validate(...)``
pair, so every domain gets identical enrichment without duplicating it.

Parameters
----------
text:
    The complete file content, YAML frontmatter block and markdown body together, exactly
    as read from disk (or submitted verbatim by an MCP tool call).
frontmatter_cls:
    The concrete frontmatter model to validate the parsed metadata against (a
    ``MarkdownFrontmatter`` subclass for every whole-body domain, or ADR's own
    ``AdrFrontmatter``/UC v1's own ``UseCaseFrontmatter``, both plain
    ``pydantic.BaseModel`` subclasses with no shared base).
domain:
    The short domain code (e.g. ``"tsk"``, ``"req"``, ``"adr"``) named in the enriched
    ``pydantic.ValidationError`` message.
stringify_metadata:
    Optional metadata-normalizing callable, mirroring every domain parser's own
    ``_stringify_metadata`` helper (coercing YAML-native scalar types, e.g. dates, back to
    ``str``). Defaults to ``None``, passing ``post.metadata`` through unchanged -- matching
    ``uc/models/v1/parser.py``'s own (deliberately different) behavior, whose
    ``UseCaseFrontmatter`` fields are typed ``date``, not ``str | None``.

Returns
-------
tuple[FrontmatterT, str]
    The validated frontmatter instance and the frontmatter-stripped body text
    (``post.content``), ready for ``SomeBody.from_text(format_text(...))``.

Raises
------
yaml.YAMLError
    For malformed frontmatter YAML -- the exact same exception type ``frontmatter.loads``
    itself would raise, enriched per :func:`enrich_frontmatter_yaml_error`.
pydantic.ValidationError
    For a structurally-sound frontmatter block whose field values fail schema validation --
    the exact same exception type ``frontmatter_cls.model_validate`` itself would raise,
    enriched per :func:`enrich_frontmatter_validation_error`.

