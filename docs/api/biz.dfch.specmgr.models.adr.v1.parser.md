# `biz.dfch.specmgr.models.adr.v1.parser`

Parse an on-disk ADR ``.md`` file into an :class:`Adr` (plan §7, §10 item 2).

Pipeline stage 1 of "parse -> validate -> render" (plan §7). This module only
does the "parse" half; "validate" is simply letting :class:`Adr`/
:class:`AdrBody`/:class:`AdrFrontmatter`'s own Pydantic validators run (the
same schema-driven check the future ``validate_adr`` MCP tool uses, plan
§7/§8) -- there is no separate validation pass here. "render" is a later,
separate module (plan §10 item 2, second half).

Two error channels, by design:

- :class:`AdrParseError` -- the markdown *structure* doesn't fit the fixed
  MADR-derived heading layout (plan §2): an unrecognized/duplicate/misplaced
  heading, more than one H1, a heading nesting level this schema doesn't
  define (H4+), a "superseded"-style duplicate option number, or stray
  non-blank text before the first heading. These are structural problems a
  human hand-editing the file (plan §7) could introduce that no amount of
  Pydantic field validation could catch, because the offending content never
  even makes it into a field.
- ``pydantic.ValidationError`` -- once headings are correctly mapped onto
  field names, constructing :class:`AdrFrontmatter`/:class:`AdrBody`/
  :class:`Adr` from that data raises this the normal Pydantic way (missing
  mandatory section, bad ``status``, bad ``version``, ...). Deliberately not
  caught/wrapped here -- it is already "one schema-driven validate_adr check,
  shared identically between LLM tool calls and human edits" (plan §7).

## Classes

### `AdrParseError`

The markdown body's heading structure does not fit the v1 schema.

Raised for structural problems -- as opposed to
``pydantic.ValidationError``, raised once heading content has been
correctly mapped onto fields but a field's own value is invalid (see
this module's docstring for the full split).

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `_BodyAccumulator`

Mutable state threaded through :func:`_parse_body`'s tree walk.


### `_Node`

One heading, resolved into the document's nesting (outline) tree.

Unlike the old flat "one entry per H1/H2/H3 token" model, a :class:`_Node`
also knows its *direct children* -- every subsequent heading, of any
level, that is nested more deeply and not itself nested under some other
heading in between (the same "outline" rule browsers/editors use to build
a table of contents from arbitrary heading levels, including skipped
ones). This is what lets a "leaf" heading (plan §4/§5's H2 sections other
than "Decision Outcome", plus "Consequences"/"Confirmation"/"Option N:
...") swallow *any* heading nested underneath it -- whatever its level or
title -- as opaque text content, while a "composite" heading ("Decision
Outcome", "Pros and Cons of the Options") still validates its direct
children against the fixed patterns it recognizes.

heading_line/content_start/end are line indices into the body's
``lines``: ``heading_line`` is the heading's own line, ``content_start``
is the first line after it, and ``end`` is the exclusive end of this
heading's *entire* subtree (i.e. up to the next heading anywhere in the
document, at this level or shallower, or end of file).


## Functions

### `_build_outline(tokens: 'list[Token]', lines: 'list[str]') -> 'list[_Node]'`

Turn a flat, document-order token list into a heading *outline* tree.

Standard "table of contents" nesting rule: a heading's children are
every subsequent heading that is more deeply nested and not already
claimed by an intervening shallower-or-equal heading -- regardless of
whether intermediate levels are skipped (e.g. an H4 directly under an
H2, with no H3 in between, is still that H2's direct child).


### `_handle_composite_child(node: '_Node', lines: 'list[str]', state: '_BodyAccumulator') -> 'None'`

Validate/collect one direct child of a composite H2 ("Decision Outcome" or
"Pros and Cons of the Options"): either an "Option N: ..." heading or one of the
fixed H3 sub-fields. Anything else -- wrong level, or an H3 with an unrecognized
title -- is a structural error.


### `_handle_h2_node(node: '_Node', lines: 'list[str]', state: '_BodyAccumulator') -> 'None'`


### `_handle_title(node: '_Node', state: '_BodyAccumulator') -> 'None'`


### `_heading_level(token: 'Token') -> 'int'`


### `_heading_title(lines: 'list[str]', token: 'Token') -> 'str'`


### `_join_content(lines: 'list[str]') -> 'str'`


### `_parse_body(content: 'str') -> 'AdrBody'`

Parse the markdown body (frontmatter stripped) into an :class:`AdrBody`.


### `_reject_leading_content(lines: 'list[str]', heading_tokens: 'list[Token]') -> 'None'`


### `_store_field(field_name: 'str', value: 'str', state: '_BodyAccumulator') -> 'None'`


### `_stringify_metadata(metadata: 'dict[str, object]') -> 'dict[str, object]'`

Coerce YAML-native scalar types back to ``str`` (or ``None``).

``python-frontmatter`` parses the YAML block with a standard YAML
loader, which auto-converts an unquoted ``date: 2024-01-01`` into a
``datetime.date`` -- but every :class:`AdrFrontmatter` field is
``str | None`` (plan §3: "not enforced here since the ``.md`` file is
the source of truth"), so a raw ``date`` object would fail Pydantic's
(deliberately non-coercive) string validation. Converting via ``str()``
reproduces the same ``YYYY-MM-DD`` text a human would have written.
``None`` (an empty YAML key) is passed through so the field's own
optional-ness applies normally.


### `parse_adr(text: 'str') -> 'Adr'`

Parse a full on-disk ADR ``.md`` file's text into an :class:`Adr`.

Parameters
----------
text:
    The complete file content, YAML frontmatter block and markdown body
    together, exactly as read from disk.

Returns
-------
Adr
    The structured document. Raises :class:`AdrParseError` for a
    malformed heading structure, or ``pydantic.ValidationError`` for a
    structurally-sound document whose field values fail schema
    validation (see this module's docstring).

