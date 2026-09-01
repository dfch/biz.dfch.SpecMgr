# `biz.dfch.specmgr.models.md.markdown_block_quote`

A markdown block quote ("blockquote"), grouping every consecutive '>' line as one instance.

## Classes

### `MarkdownBlockQuote`

A markdown block quote ("blockquote"), the non-heading, non-leaf-only sibling of `MarkdownSection`.

markdown-it already groups every *consecutive* `">"` line -- including
internal blank `">"` continuation lines (a "loose" quote with several
paragraphs) and any more deeply nested quote (`"> > ..."`) -- into a
single `blockquote_open`/`blockquote_close` pair whose own `.map`
already spans the whole thing; two quotes separated by a real blank
line (no `">"` at all) are two separate pairs. So, unlike
`MarkdownSection`/`MarkdownParagraph`, `get_extent` needs no
stop-condition scan -- `tokens[0].map[1]` is already correct, the same
situation as `MarkdownListItem`/`MarkdownCodeBlock`. There is no
`@alias` enforcement, same as `MarkdownParagraph`/`MarkdownListItem` --
quoted content is free-form, not a title.

Unlike `MarkdownListItem` (which always assumes a leading paragraph), a
quote's content can start with *any* block type (a heading, a list, a
nested quote, ...), so `from_text` validates only the `blockquote_open`
token itself (`type`/`tag`/`nesting == 1`), not anything about what
follows it.

Deliberately **not leaf-only** (unlike `MarkdownCodeBlock`) -- a
subclass may declare nested fields (e.g. `emphasis`/`strong` as future,
separate typed objects), same composite capability as
`MarkdownParagraph`/`MarkdownListItem`. But a quote has no separate
"own text" line the way a heading/paragraph/list item does -- *every*
line of its extent carries the `">"` marker, and the marker is
unrelated to what block type each line's content actually is. So the
composite split works differently:

- Leaf (no declared fields): `_value` holds the complete extent
  verbatim, marker included on every line -- nothing else will ever
  retain it, exactly like any other leaf `MarkdownStr` subclass.
- Composite (a subclass declares fields): the marker is stripped from
  *every* line of the extent (`_dedent_quote_lines`), not just a
  leading line, and the fully-dedented result -- re-normalized with
  `format_text` -- is delegated whole to `super().from_text()`. Since
  the entire extent is body this way, there is no "own text" left for
  this instance to keep, so `_value` is set to `""`. `__str__`
  re-applies the marker to every line of `super().__str__()`'s output
  (`_indent_quote_lines`), rather than reconstructing a single heading
  line (`MarkdownSection`) or prepending a marker-free lead sentence
  (`MarkdownParagraph`).

**Methods:**

- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`

- `from_orm(obj: 'Any') -> 'Self'`

- `from_text(text: 'str', *, _path: 'str' = '', _offset: 'int' = 0) -> 'MarkdownBlockQuote'`
  Create an instance from markdown text starting with a block quote.

  Validates only the `blockquote_open` token itself (`type`/`tag`
  from the `@markdown` decorator's metadata, and `nesting == 1`) --
  unlike `MarkdownListItem`, nothing is assumed about what block type
  follows it.

  If `cls` declares no nested `MarkdownStr` fields (leaf case),
  nothing else will ever retain this quote's text, so `_value` is set
  to the complete extent `from_text` received (every line, marker
  included, verbatim).

  Otherwise the marker is stripped from *every* line of `text`
  (`_dedent_quote_lines`) -- not just a leading line, since a quote
  has no separate "own text" the way a heading/paragraph does -- and
  the fully-dedented, re-normalized result is delegated whole to
  `MarkdownStr.from_text` (via `super()`) for the declared fields'
  population. Since the body is therefore already fully represented
  by the nested fields, `_value` is set to `""`.

  Args:
      text: Markdown source, pre-formatted with `mdformat`, starting
          with this class's own block quote.
      _path: this quote's own document-relative path (REQ-001) as
          chosen by the caller -- `""` at the very root, in which case
          `cls.__name__` is used instead.
      _offset: the 0-based line at which `text` starts, relative to
          the root document's own `mdformat`-normalized body
          (REQ-002) -- `0` at the root.

  Returns:
      A new instance, populated per the leaf/composite case above.

- `get_extent(text: 'str') -> 'int'`
  Return the extent of this block quote, as a line count.

  There is only an extent at all if the *first* token parsed from
  `text` is a `"blockquote_open"`/`"blockquote"` token matching this
  class's own `@markdown` metadata; otherwise this returns `0`, same
  as the base class's "no extent" case.

  Args:
      text: Markdown source, pre-formatted with `mdformat`.

  Returns:
      0: `text` does not start with a block quote (no extent).
      int > 0: line count (see `MarkdownStr.get_extent`) covered by
          the quote's own `.map`, i.e. every consecutive `">"` line,
          including any more deeply nested quote.

- `model_construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
  Creates a new instance of the `Model` class with validated data.

  Creates a new model setting `__dict__` and `__pydantic_fields_set__` from trusted or pre-validated data.
  Default values are respected, but no other validation is performed.

  !!! note
      `model_construct()` generally respects the `model_config.extra` setting on the provided model.
      That is, if `model_config.extra == 'allow'`, then all extra passed values are added to the model instance's `__dict__`
      and `__pydantic_extra__` fields. If `model_config.extra == 'ignore'` (the default), then all extra passed values are ignored.
      Because no validation is performed with a call to `model_construct()`, having `model_config.extra == 'forbid'` does not result in
      an error if extra values are passed, but they will be ignored.

  Args:
      _fields_set: A set of field names that were originally explicitly set during instantiation. If provided,
          this is directly used for the [`model_fields_set`][pydantic.BaseModel.model_fields_set] attribute.
          Otherwise, the field names from the `values` argument will be used.
      values: Trusted or pre-validated data dictionary.

  Returns:
      A new instance of the `Model` class with validated data.

- `model_json_schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', schema_generator: 'type[GenerateJsonSchema]' = <class 'pydantic.json_schema.GenerateJsonSchema'>, mode: 'JsonSchemaMode' = 'validation', *, union_format: "Literal['any_of', 'primitive_type_array']" = 'any_of') -> 'dict[str, Any]'`
  Generates a JSON schema for a model class.

  Args:
      by_alias: Whether to use attribute aliases or not.
      ref_template: The reference template.
      union_format: The format to use when combining schemas from unions together. Can be one of:

          - `'any_of'`: Use the [`anyOf`](https://json-schema.org/understanding-json-schema/reference/combining#anyOf)
          keyword to combine schemas (the default).
          - `'primitive_type_array'`: Use the [`type`](https://json-schema.org/understanding-json-schema/reference/type)
          keyword as an array of strings, containing each type of the combination. If any of the schemas is not a primitive
          type (`string`, `boolean`, `null`, `integer` or `number`) or contains constraints/metadata, falls back to
          `any_of`.
      schema_generator: To override the logic used to generate the JSON schema, as a subclass of
          `GenerateJsonSchema` with your desired modifications
      mode: The mode in which to generate the schema.

  Returns:
      The JSON schema for the given model class.

- `model_parametrized_name(params: 'tuple[type[Any], ...]') -> 'str'`
  Compute the class name for parametrizations of generic classes.

  This method can be overridden to achieve a custom naming scheme for generic BaseModels.

  Args:
      params: Tuple of types of the class. Given a generic class
          `Model` with 2 type variables and a concrete model `Model[str, int]`,
          the value `(str, int)` would be passed to `params`.

  Returns:
      String representing the new class where `params` are passed to `cls` as type variables.

  Raises:
      TypeError: Raised when trying to generate concrete names for non-generic models.

- `model_rebuild(*, force: 'bool' = False, raise_errors: 'bool' = True, _parent_namespace_depth: 'int' = 2, _types_namespace: 'MappingNamespace | None' = None) -> 'bool | None'`
  Try to rebuild the pydantic-core schema for the model.

  This may be necessary when one of the annotations is a ForwardRef which could not be resolved during
  the initial attempt to build the schema, and automatic rebuilding fails.

  Args:
      force: Whether to force the rebuilding of the model schema, defaults to `False`.
      raise_errors: Whether to raise errors, defaults to `True`.
      _parent_namespace_depth: The depth level of the parent namespace, defaults to 2.
      _types_namespace: The types namespace, defaults to `None`.

  Returns:
      Returns `None` if the schema is already "complete" and rebuilding was not required.
      If rebuilding _was_ required, returns `True` if rebuilding was successful, otherwise `False`.

- `model_validate(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, from_attributes: 'bool | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
  Validate a pydantic model instance.

  Args:
      obj: The object to validate.
      strict: Whether to enforce types strictly.
      extra: Whether to ignore, allow, or forbid extra data during model validation.
          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
      from_attributes: Whether to extract data from object attributes.
      context: Additional context to pass to the validator.
      by_alias: Whether to use the field's alias when validating against the provided input data.
      by_name: Whether to use the field's name when validating against the provided input data.

  Raises:
      ValidationError: If the object could not be validated.

  Returns:
      The validated model instance.

- `model_validate_json(json_data: 'str | bytes | bytearray', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
  !!! abstract "Usage Documentation"
      [JSON Parsing](../concepts/json.md#json-parsing)

  Validate the given JSON data against the Pydantic model.

  Args:
      json_data: The JSON data to validate.
      strict: Whether to enforce types strictly.
      extra: Whether to ignore, allow, or forbid extra data during model validation.
          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
      context: Extra variables to pass to the validator.
      by_alias: Whether to use the field's alias when validating against the provided input data.
      by_name: Whether to use the field's name when validating against the provided input data.

  Returns:
      The validated Pydantic model.

  Raises:
      ValidationError: If `json_data` is not a JSON string or the object could not be validated.

- `model_validate_strings(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
  Validate the given object with string data against the Pydantic model.

  Args:
      obj: The object containing string data to validate.
      strict: Whether to enforce types strictly.
      extra: Whether to ignore, allow, or forbid extra data during model validation.
          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
      context: Extra variables to pass to the validator.
      by_alias: Whether to use the field's alias when validating against the provided input data.
      by_name: Whether to use the field's name when validating against the provided input data.

  Returns:
      The validated Pydantic model.

- `parse_file(path: 'str | Path', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`

- `parse_obj(obj: 'Any') -> 'Self'`

- `parse_raw(b: 'str | bytes', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`

- `process_field(name: 'str', type_: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False, _path: 'str' = '', _offset: 'int' = 0) -> 'tuple[int, MarkdownStr | None]'`
  Resolve one nested field's extent and parsed instance from `text`.

  Args:
      name: the field's attribute name (used to build the document-
          relative path -- see `_field_label` -- and, on failure, the
          error message).
      type_: the field's declared `MarkdownStr` subclass.
      text: the not-yet-consumed remainder of the parent's markdown text;
          the field is assumed to start at the very first line of `text`.
      optional: whether the field is declared `Optional[type_]`/
          `type_ | None`. When `True` and `type_.get_extent(text)` finds
          no extent, this is not an error: the field is simply absent
          from `text` (e.g. an optional section whose heading doesn't
          appear next), and `(0, None)` is returned so the caller can
          move on to the next field without consuming any of `text`.
      _path: the calling container's own document-relative path
          (REQ-001), e.g. `"Task > RecentUpdates"` -- `""` at the root.
          Threaded down into `type_.from_text` (with this field's own
          label appended) so nested errors keep naming their real
          location instead of a bare class name.
      _offset: the 0-based line at which `text` starts, relative to the
          root document's own `mdformat`-normalized body (REQ-002) --
          `0` at the root.

  Returns:
      A `(extent, instance)` pair: `extent` is the number of leading
      lines of `text` this field consumes (see `MarkdownStr.get_extent`),
      and `instance` is the field's value, parsed via
      `type_.from_text` on exactly those `extent` leading lines -- or
      `(0, None)` for an absent optional field (see `optional` above).

  Raises:
      AssertionError: `optional` is `False` and `type_.get_extent(text)`
          finds no extent -- see `_no_match_message`.

- `process_list_field(name: 'str', item_type: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False, _path: 'str' = '', _offset: 'int' = 0) -> 'tuple[str, list[MarkdownStr] | None]'`
  Resolve one repeated `list[MarkdownStr]` field's parsed items and new remainder from `text`.

  Repeats `process_field`'s single-item extent/slice/parse step against
  a local `remaining_text`, once per matched item, re-normalizing with
  `mdformat.text()` after every item consumed -- same reasoning as
  `from_text`'s own `remaining_text` handling: a raw substring of an
  already-`mdformat`-compliant document is not itself guaranteed
  `mdformat`-compliant (e.g. it can start with a blank line separating
  two items, which `mdformat` would strip). The loop stops as soon as
  `item_type.get_extent` finds no further extent.

  Unlike `process_field`, this does **not** return a single combined
  line-count `extent` for the caller to slice `text` with. Doing so
  would silently miscount: every intermediate `mdformat.text()`
  renormalization can drop lines (e.g. a blank line separating two
  items) that never show up in any individual item's own `get_extent`
  result, so a caller-side `text.splitlines()[extent:]` computed from a
  *summed* extent would not line up with `text`'s original line
  numbering (exactly the class of bug `from_text` itself already moved
  away from a line-index `cursor` to avoid). Returning the
  already-fully-reduced `remaining_text` string sidesteps this by
  construction, the same way `from_text` tracks its own state.

  The *first* item follows the same `optional` contract as
  `process_field`: no item found there is an absence, which is an
  error for a mandatory `list[X]` field, or `(text, None)` (untouched)
  for an optional `list[X] | None` field. Every *subsequent* item is
  implicitly optional -- no further item found there simply ends the
  list, with no `Optional[X]` needed on `item_type` itself.

  Args:
      name: the field's attribute name (used to build the document-
          relative path -- see `_field_label` -- and, on failure, the
          error message).
      item_type: the field's declared `MarkdownStr` subclass (the `X`
          in `list[X]`/`list[X] | None`).
      text: the not-yet-consumed remainder of the parent's markdown
          text; the first item, if any, is assumed to start at the very
          first line of `text`.
      optional: whether the field is declared `list[X] | None`. When
          `True` and no item at all is found, this is not an error:
          `(text, None)` is returned so the caller can move on to the
          next field without consuming any of `text`.
      _path: the calling container's own document-relative path
          (REQ-001) -- `""` at the root. Every matched item's own path
          is `_child_path(_path, _field_label(name, item_type))` (the
          item's own type identity when it has one, else `name`),
          threaded into each item's `from_text` call.
      _offset: the 0-based line at which `text` starts, relative to
          the root document's own `mdformat`-normalized body
          (REQ-002) -- `0` at the root. Each matched item's own
          `_offset` is tracked by measuring the actual line-count
          delta of `remaining_text` before/after that item is
          consumed (not a summed `get_extent`), so per-item blank-line
          elision from re-normalization (see this docstring's own
          discussion above) never desynchronizes the running offset.

  Returns:
      A `(remaining_text, items)` pair: `remaining_text` is `text` with
      every matched item (and any separating blank lines) removed and
      re-normalized via `mdformat.text()`, ready to be handed directly
      to the next declared field -- and `items` is the non-empty list
      of parsed instances, or `(text, None)` for an absent optional
      field (see `optional` above).

  Raises:
      AssertionError: `optional` is `False` and zero items are matched
          at all -- see `_no_match_message`.

- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`

- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`

- `update_forward_refs(**localns: 'Any') -> 'None'`

- `validate(value: 'Any') -> 'Self'`

- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`

- `copy(self, *, include: 'AbstractSetIntStr | MappingIntStrAny | None' = None, exclude: 'AbstractSetIntStr | MappingIntStrAny | None' = None, update: 'Dict[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'`
  Returns a copy of the model.

  !!! warning "Deprecated"
      This method is now deprecated; use `model_copy` instead.

  If you need `include` or `exclude`, use:

  ```python {test="skip" lint="skip"}
  data = self.model_dump(include=include, exclude=exclude, round_trip=True)
  data = {**data, **(update or {})}
  copied = self.model_validate(data)
  ```

  Args:
      include: Optional set or mapping specifying which fields to include in the copied model.
      exclude: Optional set or mapping specifying which fields to exclude in the copied model.
      update: Optional dictionary of field-value pairs to override field values in the copied model.
      deep: If True, the values of fields that are Pydantic models will be deep-copied.

  Returns:
      A copy of the model with included, excluded and updated fields as specified.

- `dict(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False) -> 'Dict[str, Any]'`

- `from_orm(obj: 'Any') -> 'Self'`

- `from_text(text: 'str', *, _path: 'str' = '', _offset: 'int' = 0) -> 'MarkdownBlockQuote'`
  Create an instance from markdown text starting with a block quote.

  Validates only the `blockquote_open` token itself (`type`/`tag`
  from the `@markdown` decorator's metadata, and `nesting == 1`) --
  unlike `MarkdownListItem`, nothing is assumed about what block type
  follows it.

  If `cls` declares no nested `MarkdownStr` fields (leaf case),
  nothing else will ever retain this quote's text, so `_value` is set
  to the complete extent `from_text` received (every line, marker
  included, verbatim).

  Otherwise the marker is stripped from *every* line of `text`
  (`_dedent_quote_lines`) -- not just a leading line, since a quote
  has no separate "own text" the way a heading/paragraph does -- and
  the fully-dedented, re-normalized result is delegated whole to
  `MarkdownStr.from_text` (via `super()`) for the declared fields'
  population. Since the body is therefore already fully represented
  by the nested fields, `_value` is set to `""`.

  Args:
      text: Markdown source, pre-formatted with `mdformat`, starting
          with this class's own block quote.
      _path: this quote's own document-relative path (REQ-001) as
          chosen by the caller -- `""` at the very root, in which case
          `cls.__name__` is used instead.
      _offset: the 0-based line at which `text` starts, relative to
          the root document's own `mdformat`-normalized body
          (REQ-002) -- `0` at the root.

  Returns:
      A new instance, populated per the leaf/composite case above.

- `get_extent(text: 'str') -> 'int'`
  Return the extent of this block quote, as a line count.

  There is only an extent at all if the *first* token parsed from
  `text` is a `"blockquote_open"`/`"blockquote"` token matching this
  class's own `@markdown` metadata; otherwise this returns `0`, same
  as the base class's "no extent" case.

  Args:
      text: Markdown source, pre-formatted with `mdformat`.

  Returns:
      0: `text` does not start with a block quote (no extent).
      int > 0: line count (see `MarkdownStr.get_extent`) covered by
          the quote's own `.map`, i.e. every consecutive `">"` line,
          including any more deeply nested quote.

- `json(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any') -> 'str'`

- `model_construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
  Creates a new instance of the `Model` class with validated data.

  Creates a new model setting `__dict__` and `__pydantic_fields_set__` from trusted or pre-validated data.
  Default values are respected, but no other validation is performed.

  !!! note
      `model_construct()` generally respects the `model_config.extra` setting on the provided model.
      That is, if `model_config.extra == 'allow'`, then all extra passed values are added to the model instance's `__dict__`
      and `__pydantic_extra__` fields. If `model_config.extra == 'ignore'` (the default), then all extra passed values are ignored.
      Because no validation is performed with a call to `model_construct()`, having `model_config.extra == 'forbid'` does not result in
      an error if extra values are passed, but they will be ignored.

  Args:
      _fields_set: A set of field names that were originally explicitly set during instantiation. If provided,
          this is directly used for the [`model_fields_set`][pydantic.BaseModel.model_fields_set] attribute.
          Otherwise, the field names from the `values` argument will be used.
      values: Trusted or pre-validated data dictionary.

  Returns:
      A new instance of the `Model` class with validated data.

- `model_copy(self, *, update: 'Mapping[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'`
  !!! abstract "Usage Documentation"
      [`model_copy`](../concepts/models.md#model-copy)

  Returns a copy of the model.

  !!! note
      The underlying instance's [`__dict__`][object.__dict__] attribute is copied. This
      might have unexpected side effects if you store anything in it, on top of the model
      fields (e.g. the value of [cached properties][functools.cached_property]).

  Args:
      update: Values to change/add in the new model. Note: the data is not validated
          before creating the new model. You should trust this data.
      deep: Set to `True` to make a deep copy of the model.

  Returns:
      New model instance.

- `model_dump(self, *, mode: "Literal['json', 'python'] | str" = 'python', include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'dict[str, Any]'`
  !!! abstract "Usage Documentation"
      [`model_dump`](../concepts/serialization.md#python-mode)

  Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

  Args:
      mode: The mode in which `to_python` should run.
          If mode is 'json', the output will only contain JSON serializable types.
          If mode is 'python', the output may contain non-JSON-serializable Python objects.
      include: A set of fields to include in the output.
      exclude: A set of fields to exclude from the output.
      context: Additional context to pass to the serializer.
      by_alias: Whether to use the field's alias in the dictionary key if defined.
      exclude_unset: Whether to exclude fields that have not been explicitly set.
      exclude_defaults: Whether to exclude fields that are set to their default value.
      exclude_none: Whether to exclude fields that have a value of `None`.
      exclude_computed_fields: Whether to exclude computed fields.
          While this can be useful for round-tripping, it is usually recommended to use the dedicated
          `round_trip` parameter instead.
      round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
      warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
          "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
      fallback: A function to call when an unknown value is encountered. If not provided,
          a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
      serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.
      polymorphic_serialization: Whether to use model and dataclass polymorphic serialization for this call.

  Returns:
      A dictionary representation of the model.

- `model_dump_json(self, *, indent: 'int | None' = None, ensure_ascii: 'bool' = False, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'str'`
  !!! abstract "Usage Documentation"
      [`model_dump_json`](../concepts/serialization.md#json-mode)

  Generates a JSON representation of the model using Pydantic's `to_json` method.

  Args:
      indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
      ensure_ascii: If `True`, the output is guaranteed to have all incoming non-ASCII characters escaped.
          If `False` (the default), these characters will be output as-is.
      include: Field(s) to include in the JSON output.
      exclude: Field(s) to exclude from the JSON output.
      context: Additional context to pass to the serializer.
      by_alias: Whether to serialize using field aliases.
      exclude_unset: Whether to exclude fields that have not been explicitly set.
      exclude_defaults: Whether to exclude fields that are set to their default value.
      exclude_none: Whether to exclude fields that have a value of `None`.
      exclude_computed_fields: Whether to exclude computed fields.
          While this can be useful for round-tripping, it is usually recommended to use the dedicated
          `round_trip` parameter instead.
      round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
      warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
          "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
      fallback: A function to call when an unknown value is encountered. If not provided,
          a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
      serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.
      polymorphic_serialization: Whether to use model and dataclass polymorphic serialization for this call.

  Returns:
      A JSON string representation of the model.

- `model_json_schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', schema_generator: 'type[GenerateJsonSchema]' = <class 'pydantic.json_schema.GenerateJsonSchema'>, mode: 'JsonSchemaMode' = 'validation', *, union_format: "Literal['any_of', 'primitive_type_array']" = 'any_of') -> 'dict[str, Any]'`
  Generates a JSON schema for a model class.

  Args:
      by_alias: Whether to use attribute aliases or not.
      ref_template: The reference template.
      union_format: The format to use when combining schemas from unions together. Can be one of:

          - `'any_of'`: Use the [`anyOf`](https://json-schema.org/understanding-json-schema/reference/combining#anyOf)
          keyword to combine schemas (the default).
          - `'primitive_type_array'`: Use the [`type`](https://json-schema.org/understanding-json-schema/reference/type)
          keyword as an array of strings, containing each type of the combination. If any of the schemas is not a primitive
          type (`string`, `boolean`, `null`, `integer` or `number`) or contains constraints/metadata, falls back to
          `any_of`.
      schema_generator: To override the logic used to generate the JSON schema, as a subclass of
          `GenerateJsonSchema` with your desired modifications
      mode: The mode in which to generate the schema.

  Returns:
      The JSON schema for the given model class.

- `model_parametrized_name(params: 'tuple[type[Any], ...]') -> 'str'`
  Compute the class name for parametrizations of generic classes.

  This method can be overridden to achieve a custom naming scheme for generic BaseModels.

  Args:
      params: Tuple of types of the class. Given a generic class
          `Model` with 2 type variables and a concrete model `Model[str, int]`,
          the value `(str, int)` would be passed to `params`.

  Returns:
      String representing the new class where `params` are passed to `cls` as type variables.

  Raises:
      TypeError: Raised when trying to generate concrete names for non-generic models.

- `model_post_init(self: 'BaseModel', context: 'Any', /) -> 'None'`
  This function is meant to behave like a BaseModel method to initialize private attributes.

  It takes context as an argument since that's what pydantic-core passes when calling it.

  Args:
      self: The BaseModel instance.
      context: The context.

- `model_rebuild(*, force: 'bool' = False, raise_errors: 'bool' = True, _parent_namespace_depth: 'int' = 2, _types_namespace: 'MappingNamespace | None' = None) -> 'bool | None'`
  Try to rebuild the pydantic-core schema for the model.

  This may be necessary when one of the annotations is a ForwardRef which could not be resolved during
  the initial attempt to build the schema, and automatic rebuilding fails.

  Args:
      force: Whether to force the rebuilding of the model schema, defaults to `False`.
      raise_errors: Whether to raise errors, defaults to `True`.
      _parent_namespace_depth: The depth level of the parent namespace, defaults to 2.
      _types_namespace: The types namespace, defaults to `None`.

  Returns:
      Returns `None` if the schema is already "complete" and rebuilding was not required.
      If rebuilding _was_ required, returns `True` if rebuilding was successful, otherwise `False`.

- `model_validate(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, from_attributes: 'bool | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
  Validate a pydantic model instance.

  Args:
      obj: The object to validate.
      strict: Whether to enforce types strictly.
      extra: Whether to ignore, allow, or forbid extra data during model validation.
          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
      from_attributes: Whether to extract data from object attributes.
      context: Additional context to pass to the validator.
      by_alias: Whether to use the field's alias when validating against the provided input data.
      by_name: Whether to use the field's name when validating against the provided input data.

  Raises:
      ValidationError: If the object could not be validated.

  Returns:
      The validated model instance.

- `model_validate_json(json_data: 'str | bytes | bytearray', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
  !!! abstract "Usage Documentation"
      [JSON Parsing](../concepts/json.md#json-parsing)

  Validate the given JSON data against the Pydantic model.

  Args:
      json_data: The JSON data to validate.
      strict: Whether to enforce types strictly.
      extra: Whether to ignore, allow, or forbid extra data during model validation.
          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
      context: Extra variables to pass to the validator.
      by_alias: Whether to use the field's alias when validating against the provided input data.
      by_name: Whether to use the field's name when validating against the provided input data.

  Returns:
      The validated Pydantic model.

  Raises:
      ValidationError: If `json_data` is not a JSON string or the object could not be validated.

- `model_validate_strings(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
  Validate the given object with string data against the Pydantic model.

  Args:
      obj: The object containing string data to validate.
      strict: Whether to enforce types strictly.
      extra: Whether to ignore, allow, or forbid extra data during model validation.
          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
      context: Extra variables to pass to the validator.
      by_alias: Whether to use the field's alias when validating against the provided input data.
      by_name: Whether to use the field's name when validating against the provided input data.

  Returns:
      The validated Pydantic model.

- `parse_file(path: 'str | Path', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`

- `parse_obj(obj: 'Any') -> 'Self'`

- `parse_raw(b: 'str | bytes', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`

- `process_field(name: 'str', type_: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False, _path: 'str' = '', _offset: 'int' = 0) -> 'tuple[int, MarkdownStr | None]'`
  Resolve one nested field's extent and parsed instance from `text`.

  Args:
      name: the field's attribute name (used to build the document-
          relative path -- see `_field_label` -- and, on failure, the
          error message).
      type_: the field's declared `MarkdownStr` subclass.
      text: the not-yet-consumed remainder of the parent's markdown text;
          the field is assumed to start at the very first line of `text`.
      optional: whether the field is declared `Optional[type_]`/
          `type_ | None`. When `True` and `type_.get_extent(text)` finds
          no extent, this is not an error: the field is simply absent
          from `text` (e.g. an optional section whose heading doesn't
          appear next), and `(0, None)` is returned so the caller can
          move on to the next field without consuming any of `text`.
      _path: the calling container's own document-relative path
          (REQ-001), e.g. `"Task > RecentUpdates"` -- `""` at the root.
          Threaded down into `type_.from_text` (with this field's own
          label appended) so nested errors keep naming their real
          location instead of a bare class name.
      _offset: the 0-based line at which `text` starts, relative to the
          root document's own `mdformat`-normalized body (REQ-002) --
          `0` at the root.

  Returns:
      A `(extent, instance)` pair: `extent` is the number of leading
      lines of `text` this field consumes (see `MarkdownStr.get_extent`),
      and `instance` is the field's value, parsed via
      `type_.from_text` on exactly those `extent` leading lines -- or
      `(0, None)` for an absent optional field (see `optional` above).

  Raises:
      AssertionError: `optional` is `False` and `type_.get_extent(text)`
          finds no extent -- see `_no_match_message`.

- `process_list_field(name: 'str', item_type: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False, _path: 'str' = '', _offset: 'int' = 0) -> 'tuple[str, list[MarkdownStr] | None]'`
  Resolve one repeated `list[MarkdownStr]` field's parsed items and new remainder from `text`.

  Repeats `process_field`'s single-item extent/slice/parse step against
  a local `remaining_text`, once per matched item, re-normalizing with
  `mdformat.text()` after every item consumed -- same reasoning as
  `from_text`'s own `remaining_text` handling: a raw substring of an
  already-`mdformat`-compliant document is not itself guaranteed
  `mdformat`-compliant (e.g. it can start with a blank line separating
  two items, which `mdformat` would strip). The loop stops as soon as
  `item_type.get_extent` finds no further extent.

  Unlike `process_field`, this does **not** return a single combined
  line-count `extent` for the caller to slice `text` with. Doing so
  would silently miscount: every intermediate `mdformat.text()`
  renormalization can drop lines (e.g. a blank line separating two
  items) that never show up in any individual item's own `get_extent`
  result, so a caller-side `text.splitlines()[extent:]` computed from a
  *summed* extent would not line up with `text`'s original line
  numbering (exactly the class of bug `from_text` itself already moved
  away from a line-index `cursor` to avoid). Returning the
  already-fully-reduced `remaining_text` string sidesteps this by
  construction, the same way `from_text` tracks its own state.

  The *first* item follows the same `optional` contract as
  `process_field`: no item found there is an absence, which is an
  error for a mandatory `list[X]` field, or `(text, None)` (untouched)
  for an optional `list[X] | None` field. Every *subsequent* item is
  implicitly optional -- no further item found there simply ends the
  list, with no `Optional[X]` needed on `item_type` itself.

  Args:
      name: the field's attribute name (used to build the document-
          relative path -- see `_field_label` -- and, on failure, the
          error message).
      item_type: the field's declared `MarkdownStr` subclass (the `X`
          in `list[X]`/`list[X] | None`).
      text: the not-yet-consumed remainder of the parent's markdown
          text; the first item, if any, is assumed to start at the very
          first line of `text`.
      optional: whether the field is declared `list[X] | None`. When
          `True` and no item at all is found, this is not an error:
          `(text, None)` is returned so the caller can move on to the
          next field without consuming any of `text`.
      _path: the calling container's own document-relative path
          (REQ-001) -- `""` at the root. Every matched item's own path
          is `_child_path(_path, _field_label(name, item_type))` (the
          item's own type identity when it has one, else `name`),
          threaded into each item's `from_text` call.
      _offset: the 0-based line at which `text` starts, relative to
          the root document's own `mdformat`-normalized body
          (REQ-002) -- `0` at the root. Each matched item's own
          `_offset` is tracked by measuring the actual line-count
          delta of `remaining_text` before/after that item is
          consumed (not a summed `get_extent`), so per-item blank-line
          elision from re-normalization (see this docstring's own
          discussion above) never desynchronizes the running offset.

  Returns:
      A `(remaining_text, items)` pair: `remaining_text` is `text` with
      every matched item (and any separating blank lines) removed and
      re-normalized via `mdformat.text()`, ready to be handed directly
      to the next declared field -- and `items` is the non-empty list
      of parsed instances, or `(text, None)` for an absent optional
      field (see `optional` above).

  Raises:
      AssertionError: `optional` is `False` and zero items are matched
          at all -- see `_no_match_message`.

- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`

- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`

- `update_forward_refs(**localns: 'Any') -> 'None'`

- `validate(value: 'Any') -> 'Self'`


## Functions

### `_dedent_quote_lines(text: 'str') -> 'str'`

Strip the leading `">"`/`"> "` marker from every line of `text`.

Every line of a block quote's extent (after `format_text` normalization)
is guaranteed to start with `">"` (a bare `">"` for a blank continuation
line, `"> "` otherwise) -- this is the inverse of `_indent_quote_lines`.

Args:
    text: Markdown source, every line of which starts with a block
        quote marker.

Returns:
    `text` with each line's marker removed, joined back with `"\n"`.


### `_indent_quote_lines(text: 'str') -> 'str'`

Prepend a block quote marker (`"> "`, or bare `">"` for a blank line) to every line of `text`.

Inverse of `_dedent_quote_lines`.

Args:
    text: Markdown source with no block quote markers of its own.

Returns:
    `text` with each line prefixed by `"> "` (non-blank line) or `">"`
    (blank line), joined back with `"\n"`.

