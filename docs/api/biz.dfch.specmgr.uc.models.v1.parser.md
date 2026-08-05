# `biz.dfch.specmgr.uc.models.v1.parser`

Parse an on-disk Use Case ``.md`` file into a :class:`UseCase` (feature plan Task 1.3A).

Pipeline stage 1 of "parse -> validate" (mirrors ``models/adr/v1/parser.py``'s "parse ->
validate -> render" split, ADR's plan §7). This module only does the "parse" half; "validate"
is letting :class:`UseCase`/its nested models' own Pydantic validators run -- including the
cross-field ``model_validator`` checks added in Task 1.3B (step numbering, action numbering,
step-reference cross-resolution) -- there is no separate validation pass here.

Two error channels, by design (same split as ADR's parser):

- :class:`UcParseError` -- the markdown *structure* doesn't fit the Cockburn-derived heading/
  list layout documented in ``uc_schema.json``/``uc_example.md``: an unrecognized/duplicate/
  misplaced heading, a heading nesting level this schema doesn't define, a malformed numbered-
  list line, or stray non-blank text before the first heading. These are structural problems no
  amount of Pydantic field validation could catch, because the offending content never even
  makes it into a field.
- ``pydantic.ValidationError`` -- once headings/lists are correctly mapped onto field values,
  constructing :class:`UseCase` from that data raises this the normal Pydantic way (missing
  mandatory section, bad ``level``, non-contiguous step numbers, a dangling extension
  ``step_reference``, ...). Deliberately not caught/wrapped here.

Unlike ADR's fixed all-heading layout, the Use Case markdown format (``uc_example.md``) also
uses ordinary Markdown lists for structured content: numbered lists for
``Main Success Scenario`` steps and ``Extension`` actions, bullet lists for most other
``list[str]`` fields. Heading titles in the example additionally carry a
``" (required)"``/``" (optional)`` annotation suffix, stripped before matching against the
fixed title tables below (documentation convention, not itself validated).

## Classes

### `UcParseError`

The markdown body's heading/list structure does not fit the v1 use case schema.

Raised for structural problems -- as opposed to ``pydantic.ValidationError``, raised once
heading/list content has been correctly mapped onto fields but a field's own value (or a
cross-field invariant) is invalid (see this module's docstring for the full split).

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


### `_Node`

One heading, resolved into the document's nesting (outline) tree.

Directly adapted from ``models/adr/v1/parser.py``'s ``_Node`` -- same "table of contents"
nesting rule, same ``heading_line``/``content_start``/``end`` line-index bookkeeping.


## Functions

### `_build_outline(tokens: 'list[Token]', lines: 'list[str]') -> 'list[_Node]'`

Turn a flat, document-order heading token list into a heading *outline* tree.

Identical "table of contents" nesting rule to ``models/adr/v1/parser.py``'s
``_build_outline``.


### `_heading_level(token: 'Token') -> 'int'`


### `_heading_title(lines: 'list[str]', token: 'Token') -> 'str'`


### `_join_text(lines: 'list[str]') -> 'str'`


### `_parse_bullet_list(lines: 'list[str]') -> 'list[str]'`


### `_parse_characteristic_information(node: '_Node', lines: 'list[str]') -> 'CharacteristicInformation'`


### `_parse_extension(node: '_Node', lines: 'list[str]') -> 'Extension'`


### `_parse_h2_section(field_name: 'str', node: '_Node', lines: 'list[str]') -> 'object'`


### `_parse_numbered_items(lines: 'list[str]') -> 'list[tuple[str, str]]'`

Parse a numbered markdown list into ``(number, description)`` pairs.

A non-blank line not matching the numbered-item pattern is treated as a continuation of the
previous item's description (e.g. ``uc_example.md``'s indented free-text lines under step
3 and extension action 3a1), joined onto it with a single space.


### `_parse_related_information(node: '_Node', lines: 'list[str]') -> 'RelatedInformation'`


### `_parse_related_use_cases(lines: 'list[str]') -> 'RelatedUseCases | None'`


### `_parse_steps(lines: 'list[str]') -> 'list[Step]'`


### `_parse_sub_variation(node: '_Node', lines: 'list[str]') -> 'SubVariation'`


### `_reject_leading_content(lines: 'list[str]', heading_tokens: 'list[Token]') -> 'None'`


### `_strip_annotation(title: 'str') -> 'str'`


### `parse_uc(text: 'str') -> 'UseCase'`

Parse a full on-disk use case ``.md`` file's text into a :class:`UseCase`.

Parameters
----------
text:
    The complete file content, YAML frontmatter block and markdown body together, exactly
    as read from disk.

Returns
-------
UseCase
    The structured document. Raises :class:`UcParseError` for a malformed heading/list
    structure, or ``pydantic.ValidationError`` for a structurally-sound document whose
    field values (or cross-field invariants) fail schema validation.

