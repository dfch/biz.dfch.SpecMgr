# `biz.dfch.specmgr.qa.models.v2.question_answer`

One adjacent question/answer pair with no heading of its own (QA v2).

Many Q&A pairs can appear directly one after another inside a single
ISO/IEC 25010:2023 characteristic section, each shaped as
`<!-- optional comment -->` + `> {question}` (a block quote) + free-form
answer prose -- with **no heading of its own** per pair:

```
<!-- optional comment -->                comment: MarkdownComment | None
> {question}                             question: MarkdownBlockQuote | None
{free-form answer prose}                 answer: QaAnswer | None
```

`QaQuestionAnswer` needs no override of `from_text`/`__str__`/
`_get_field_names()` -- all three fields are plain `Optional[SingleClass]`
(no lists, no unions), which the generic, unmodified `MarkdownStr` engine
already distributes/renders correctly. It does, however, need a `get_extent`
override: the generic engine has no notion of "a composite's own extent is
the sum of its declared fields' own extents" (every other composite in this
codebase is either heading-bounded or a single pre-grouped markdown-it
token) -- see the feature README's Design Notes for the full rationale.

Both `get_extent` overrides in this module are local, throwaway adaptations
of the depth-0 scanning technique `MarkdownSection.get_extent`'s
`end_marker` mechanism (feat-12) already established -- generalized here
from "stop at one declared marker type" to "stop at the first of: heading
(any level), block quote, or comment". Neither override touches, imports
from, or is exported to `models/md/` -- by explicit instruction, this
feature adds zero changes to that shared engine.

## Classes

### `QaAnswer`

One `QaQuestionAnswer`'s free-form prose answer -- an opaque, unparsed markdown blob.

Deliberately **not** heading-anchored: since further adjacent Q&A pairs
can follow within the same enclosing category section, the base
`MarkdownStr.get_extent`'s "swallow everything remaining" (correct for a
field declared *last* in a heading-bounded section) would be wrong here
-- so this class overrides `get_extent` to stop at the first depth-0
occurrence of a heading (any level), a block quote, or a comment, and
only runs to the end of the given text when none of those follow.

Adds a `text` computed property (mirroring
`MarkdownParagraph.text`/`MarkdownSection.text`) so this otherwise-private
`_value` is reachable through `model_dump()`/`model_dump_json()`.

**Methods:**

- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`

- `from_orm(obj: 'Any') -> 'Self'`

- `from_text(text: 'str') -> 'MarkdownStr'`
  Create an instance from markdown text, splitting `text` among nested fields.

  If `cls` declares no nested `MarkdownStr` fields, `text` is stored verbatim
  in `_value` (leaf case).

  Otherwise `text` is split into one block per declared field, in
  declaration order. Each block's length is determined by calling that
  field's own `get_extent` on the not-yet-consumed remainder of `text` --
  this lets each field type decide its own boundary (e.g.
  `MarkdownSection.get_extent` stops at the next sibling/ancestor
  heading, while the base `MarkdownStr.get_extent` consumes everything
  remaining).

  The not-yet-consumed remainder is tracked as a string (`remaining_text`),
  re-normalized with `mdformat.text()` after every field is sliced off,
  rather than as a line-index `cursor` into the original `text`. A raw
  substring of an already-`mdformat`-compliant document is not itself
  guaranteed to be `mdformat`-compliant (e.g. it can start with a blank
  line that `mdformat` would strip), which is exactly what `get_extent`
  requires of its input -- so `remaining_text` is kept compliant by
  construction on every iteration instead of being handed to the next
  field's `get_extent` unnormalized.

  A field declared `Optional[X]`/`X | None` (see `_unwrap_optional`) is
  allowed a `0` extent: `process_field` reports it as `(0, None)`
  instead of raising, that field is left unset (pydantic default, i.e.
  `None`) rather than added to `kwargs`, `remaining_text` is left
  untouched (nothing was consumed), and the loop simply continues to
  the next declared field.

  A field declared `list[X]`/`list[X] | None` (see `_unwrap_list`) is
  handled by `process_list_field` instead of `process_field`: it
  repeatedly matches `X` against the not-yet-consumed remainder, once
  per item, until `X.get_extent` finds no further extent. The `list[X]`
  vs. `list[X] | None` distinction plays exactly the same role as it
  does for a scalar field -- a mandatory `list[X]` requires at least
  one matched item (else `process_list_field` raises), while
  `list[X] | None` allows zero items (the field is left `None`); once
  the first item is found, every subsequent item is implicitly
  optional regardless of which of the two was declared.

- `get_extent(text: 'str') -> 'int'`
  Return the extent of this answer blob, as a line count.

  Scans every token parsed from `text`, tracking a depth counter the
  same way `MarkdownSection.get_extent`'s `end_marker` mechanism does
  (incremented/decremented by each token's own `Token.nesting`): the
  first token encountered at depth 0 that is a heading (any level), a
  block quote, or a comment stops the scan, and its own `.map[0]`
  (start line) is returned as the extent -- excluding that terminating
  token itself, same convention as `MarkdownSection.get_extent`.

  Args:
      text: Markdown source, pre-formatted with `mdformat`.

  Returns:
      0: `text` starts immediately with one of the three terminator
          kinds (no answer text present at all).
      int > 0: line count (see `MarkdownStr.get_extent`) covered by
          the answer's own prose, stopping before the first depth-0
          heading/block quote/comment, or at the end of `text` if
          none follows.

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

- `process_field(name: 'str', type_: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[int, MarkdownStr | None]'`
  Resolve one nested field's extent and parsed instance from `text`.

  Args:
      name: the field's attribute name (used only for error messages).
      type_: the field's declared `MarkdownStr` subclass.
      text: the not-yet-consumed remainder of the parent's markdown text;
          the field is assumed to start at the very first line of `text`.
      optional: whether the field is declared `Optional[type_]`/
          `type_ | None`. When `True` and `type_.get_extent(text)` finds
          no extent, this is not an error: the field is simply absent
          from `text` (e.g. an optional section whose heading doesn't
          appear next), and `(0, None)` is returned so the caller can
          move on to the next field without consuming any of `text`.

  Returns:
      A `(extent, instance)` pair: `extent` is the number of leading
      lines of `text` this field consumes (see `MarkdownStr.get_extent`),
      and `instance` is the field's value, parsed via
      `type_.from_text` on exactly those `extent` leading lines -- or
      `(0, None)` for an absent optional field (see `optional` above).

- `process_list_field(name: 'str', item_type: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[str, list[MarkdownStr] | None]'`
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
      name: the field's attribute name (used only for error messages).
      item_type: the field's declared `MarkdownStr` subclass (the `X`
          in `list[X]`/`list[X] | None`).
      text: the not-yet-consumed remainder of the parent's markdown
          text; the first item, if any, is assumed to start at the very
          first line of `text`.
      optional: whether the field is declared `list[X] | None`. When
          `True` and no item at all is found, this is not an error:
          `(text, None)` is returned so the caller can move on to the
          next field without consuming any of `text`.

  Returns:
      A `(remaining_text, items)` pair: `remaining_text` is `text` with
      every matched item (and any separating blank lines) removed and
      re-normalized via `mdformat.text()`, ready to be handed directly
      to the next declared field -- and `items` is the non-empty list
      of parsed instances, or `(text, None)` for an absent optional
      field (see `optional` above).

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

- `from_text(text: 'str') -> 'MarkdownStr'`
  Create an instance from markdown text, splitting `text` among nested fields.

  If `cls` declares no nested `MarkdownStr` fields, `text` is stored verbatim
  in `_value` (leaf case).

  Otherwise `text` is split into one block per declared field, in
  declaration order. Each block's length is determined by calling that
  field's own `get_extent` on the not-yet-consumed remainder of `text` --
  this lets each field type decide its own boundary (e.g.
  `MarkdownSection.get_extent` stops at the next sibling/ancestor
  heading, while the base `MarkdownStr.get_extent` consumes everything
  remaining).

  The not-yet-consumed remainder is tracked as a string (`remaining_text`),
  re-normalized with `mdformat.text()` after every field is sliced off,
  rather than as a line-index `cursor` into the original `text`. A raw
  substring of an already-`mdformat`-compliant document is not itself
  guaranteed to be `mdformat`-compliant (e.g. it can start with a blank
  line that `mdformat` would strip), which is exactly what `get_extent`
  requires of its input -- so `remaining_text` is kept compliant by
  construction on every iteration instead of being handed to the next
  field's `get_extent` unnormalized.

  A field declared `Optional[X]`/`X | None` (see `_unwrap_optional`) is
  allowed a `0` extent: `process_field` reports it as `(0, None)`
  instead of raising, that field is left unset (pydantic default, i.e.
  `None`) rather than added to `kwargs`, `remaining_text` is left
  untouched (nothing was consumed), and the loop simply continues to
  the next declared field.

  A field declared `list[X]`/`list[X] | None` (see `_unwrap_list`) is
  handled by `process_list_field` instead of `process_field`: it
  repeatedly matches `X` against the not-yet-consumed remainder, once
  per item, until `X.get_extent` finds no further extent. The `list[X]`
  vs. `list[X] | None` distinction plays exactly the same role as it
  does for a scalar field -- a mandatory `list[X]` requires at least
  one matched item (else `process_list_field` raises), while
  `list[X] | None` allows zero items (the field is left `None`); once
  the first item is found, every subsequent item is implicitly
  optional regardless of which of the two was declared.

- `get_extent(text: 'str') -> 'int'`
  Return the extent of this answer blob, as a line count.

  Scans every token parsed from `text`, tracking a depth counter the
  same way `MarkdownSection.get_extent`'s `end_marker` mechanism does
  (incremented/decremented by each token's own `Token.nesting`): the
  first token encountered at depth 0 that is a heading (any level), a
  block quote, or a comment stops the scan, and its own `.map[0]`
  (start line) is returned as the extent -- excluding that terminating
  token itself, same convention as `MarkdownSection.get_extent`.

  Args:
      text: Markdown source, pre-formatted with `mdformat`.

  Returns:
      0: `text` starts immediately with one of the three terminator
          kinds (no answer text present at all).
      int > 0: line count (see `MarkdownStr.get_extent`) covered by
          the answer's own prose, stopping before the first depth-0
          heading/block quote/comment, or at the end of `text` if
          none follows.

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

- `process_field(name: 'str', type_: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[int, MarkdownStr | None]'`
  Resolve one nested field's extent and parsed instance from `text`.

  Args:
      name: the field's attribute name (used only for error messages).
      type_: the field's declared `MarkdownStr` subclass.
      text: the not-yet-consumed remainder of the parent's markdown text;
          the field is assumed to start at the very first line of `text`.
      optional: whether the field is declared `Optional[type_]`/
          `type_ | None`. When `True` and `type_.get_extent(text)` finds
          no extent, this is not an error: the field is simply absent
          from `text` (e.g. an optional section whose heading doesn't
          appear next), and `(0, None)` is returned so the caller can
          move on to the next field without consuming any of `text`.

  Returns:
      A `(extent, instance)` pair: `extent` is the number of leading
      lines of `text` this field consumes (see `MarkdownStr.get_extent`),
      and `instance` is the field's value, parsed via
      `type_.from_text` on exactly those `extent` leading lines -- or
      `(0, None)` for an absent optional field (see `optional` above).

- `process_list_field(name: 'str', item_type: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[str, list[MarkdownStr] | None]'`
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
      name: the field's attribute name (used only for error messages).
      item_type: the field's declared `MarkdownStr` subclass (the `X`
          in `list[X]`/`list[X] | None`).
      text: the not-yet-consumed remainder of the parent's markdown
          text; the first item, if any, is assumed to start at the very
          first line of `text`.
      optional: whether the field is declared `list[X] | None`. When
          `True` and no item at all is found, this is not an error:
          `(text, None)` is returned so the caller can move on to the
          next field without consuming any of `text`.

  Returns:
      A `(remaining_text, items)` pair: `remaining_text` is `text` with
      every matched item (and any separating blank lines) removed and
      re-normalized via `mdformat.text()`, ready to be handed directly
      to the next declared field -- and `items` is the non-empty list
      of parsed instances, or `(text, None)` for an absent optional
      field (see `optional` above).

- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`

- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`

- `update_forward_refs(**localns: 'Any') -> 'None'`

- `validate(value: 'Any') -> 'Self'`


### `QaQuestionAnswer`

One adjacent question/answer pair, with no heading of its own (QA v2).

All three fields are independently optional. A comment with nothing
recognizable following it (end of section, or another heading right
after) becomes its own final `QaQuestionAnswer` with only `comment` set
(`question`/`answer` both `None`) -- accepted, not an error.

No override of `from_text`/`__str__`/`_get_field_names()` is needed --
all three fields are plain `Optional[SingleClass]`, which the generic,
unmodified `MarkdownStr` engine already distributes/renders correctly.

Parameters
----------
comment:
    Optional leading `<!-- ... -->` comment, belonging to the question
    that follows it.
question:
    The interviewer's question, as a block quote. Optional.
answer:
    The interviewee's free-form prose answer. Optional.

**Methods:**

- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`

- `from_orm(obj: 'Any') -> 'Self'`

- `from_text(text: 'str') -> 'MarkdownStr'`
  Create an instance from markdown text, splitting `text` among nested fields.

  If `cls` declares no nested `MarkdownStr` fields, `text` is stored verbatim
  in `_value` (leaf case).

  Otherwise `text` is split into one block per declared field, in
  declaration order. Each block's length is determined by calling that
  field's own `get_extent` on the not-yet-consumed remainder of `text` --
  this lets each field type decide its own boundary (e.g.
  `MarkdownSection.get_extent` stops at the next sibling/ancestor
  heading, while the base `MarkdownStr.get_extent` consumes everything
  remaining).

  The not-yet-consumed remainder is tracked as a string (`remaining_text`),
  re-normalized with `mdformat.text()` after every field is sliced off,
  rather than as a line-index `cursor` into the original `text`. A raw
  substring of an already-`mdformat`-compliant document is not itself
  guaranteed to be `mdformat`-compliant (e.g. it can start with a blank
  line that `mdformat` would strip), which is exactly what `get_extent`
  requires of its input -- so `remaining_text` is kept compliant by
  construction on every iteration instead of being handed to the next
  field's `get_extent` unnormalized.

  A field declared `Optional[X]`/`X | None` (see `_unwrap_optional`) is
  allowed a `0` extent: `process_field` reports it as `(0, None)`
  instead of raising, that field is left unset (pydantic default, i.e.
  `None`) rather than added to `kwargs`, `remaining_text` is left
  untouched (nothing was consumed), and the loop simply continues to
  the next declared field.

  A field declared `list[X]`/`list[X] | None` (see `_unwrap_list`) is
  handled by `process_list_field` instead of `process_field`: it
  repeatedly matches `X` against the not-yet-consumed remainder, once
  per item, until `X.get_extent` finds no further extent. The `list[X]`
  vs. `list[X] | None` distinction plays exactly the same role as it
  does for a scalar field -- a mandatory `list[X]` requires at least
  one matched item (else `process_list_field` raises), while
  `list[X] | None` allows zero items (the field is left `None`); once
  the first item is found, every subsequent item is implicitly
  optional regardless of which of the two was declared.

- `get_extent(text: 'str') -> 'int'`
  Return this pair's own extent, as a line count, as the sum of its fields' own extents.

  No class elsewhere in this codebase computes a composite's own
  extent this way (every other composite is either heading-bounded or
  a single pre-grouped markdown-it token) -- this is a local,
  throwaway mechanism for `qa/models/v2/` only (see this module's
  docstring).

  Rather than calling each field's own `get_extent` on successively
  re-normalized substrings (which would silently under-count: a raw
  substring can start with a blank separator line that `mdformat`
  would strip, exactly the class of bug `process_list_field`'s own
  docstring in `markdown_str.py` already documents), this walks the
  *same* single token stream `MarkdownStr.get_extent`'s continuous
  scan already uses, tracking which of `comment`/`question` have
  already been matched for *this* pair:

  - A depth-0 heading (any level) always stops the scan.
  - A depth-0 comment stops the scan unless it is the very first thing
    encountered for this pair (i.e. `comment` not yet matched, and no
    other content yet accumulated) -- otherwise it is either a second
    comment or a comment following already-started answer prose,
    either way belonging to the *next* pair.
  - A depth-0 block quote stops the scan unless `question` has not yet
    been matched and no other content has yet been accumulated for
    this pair -- otherwise it is either a second question or a block
    quote appearing after answer prose has already started, either way
    belonging to the *next* pair.
  - Anything else at depth 0 (a paragraph, a list, ...) is `answer`
    prose: once any such content has been seen, no further depth-0
    comment/block quote can still be *this* pair's own `question`.

  Args:
      text: Markdown source, pre-formatted with `mdformat`.

  Returns:
      0: nothing matches at all (the enclosing `list[QaQuestionAnswer]`,
          and therefore the whole category section, may legitimately be
          empty).
      int > 0: line count (see `MarkdownStr.get_extent`) covered by
          this pair's own `comment`/`question`/`answer`, stopping
          before the next pair (or the next heading), or at the end of
          `text` if neither follows.

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

- `process_field(name: 'str', type_: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[int, MarkdownStr | None]'`
  Resolve one nested field's extent and parsed instance from `text`.

  Args:
      name: the field's attribute name (used only for error messages).
      type_: the field's declared `MarkdownStr` subclass.
      text: the not-yet-consumed remainder of the parent's markdown text;
          the field is assumed to start at the very first line of `text`.
      optional: whether the field is declared `Optional[type_]`/
          `type_ | None`. When `True` and `type_.get_extent(text)` finds
          no extent, this is not an error: the field is simply absent
          from `text` (e.g. an optional section whose heading doesn't
          appear next), and `(0, None)` is returned so the caller can
          move on to the next field without consuming any of `text`.

  Returns:
      A `(extent, instance)` pair: `extent` is the number of leading
      lines of `text` this field consumes (see `MarkdownStr.get_extent`),
      and `instance` is the field's value, parsed via
      `type_.from_text` on exactly those `extent` leading lines -- or
      `(0, None)` for an absent optional field (see `optional` above).

- `process_list_field(name: 'str', item_type: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[str, list[MarkdownStr] | None]'`
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
      name: the field's attribute name (used only for error messages).
      item_type: the field's declared `MarkdownStr` subclass (the `X`
          in `list[X]`/`list[X] | None`).
      text: the not-yet-consumed remainder of the parent's markdown
          text; the first item, if any, is assumed to start at the very
          first line of `text`.
      optional: whether the field is declared `list[X] | None`. When
          `True` and no item at all is found, this is not an error:
          `(text, None)` is returned so the caller can move on to the
          next field without consuming any of `text`.

  Returns:
      A `(remaining_text, items)` pair: `remaining_text` is `text` with
      every matched item (and any separating blank lines) removed and
      re-normalized via `mdformat.text()`, ready to be handed directly
      to the next declared field -- and `items` is the non-empty list
      of parsed instances, or `(text, None)` for an absent optional
      field (see `optional` above).

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

- `from_text(text: 'str') -> 'MarkdownStr'`
  Create an instance from markdown text, splitting `text` among nested fields.

  If `cls` declares no nested `MarkdownStr` fields, `text` is stored verbatim
  in `_value` (leaf case).

  Otherwise `text` is split into one block per declared field, in
  declaration order. Each block's length is determined by calling that
  field's own `get_extent` on the not-yet-consumed remainder of `text` --
  this lets each field type decide its own boundary (e.g.
  `MarkdownSection.get_extent` stops at the next sibling/ancestor
  heading, while the base `MarkdownStr.get_extent` consumes everything
  remaining).

  The not-yet-consumed remainder is tracked as a string (`remaining_text`),
  re-normalized with `mdformat.text()` after every field is sliced off,
  rather than as a line-index `cursor` into the original `text`. A raw
  substring of an already-`mdformat`-compliant document is not itself
  guaranteed to be `mdformat`-compliant (e.g. it can start with a blank
  line that `mdformat` would strip), which is exactly what `get_extent`
  requires of its input -- so `remaining_text` is kept compliant by
  construction on every iteration instead of being handed to the next
  field's `get_extent` unnormalized.

  A field declared `Optional[X]`/`X | None` (see `_unwrap_optional`) is
  allowed a `0` extent: `process_field` reports it as `(0, None)`
  instead of raising, that field is left unset (pydantic default, i.e.
  `None`) rather than added to `kwargs`, `remaining_text` is left
  untouched (nothing was consumed), and the loop simply continues to
  the next declared field.

  A field declared `list[X]`/`list[X] | None` (see `_unwrap_list`) is
  handled by `process_list_field` instead of `process_field`: it
  repeatedly matches `X` against the not-yet-consumed remainder, once
  per item, until `X.get_extent` finds no further extent. The `list[X]`
  vs. `list[X] | None` distinction plays exactly the same role as it
  does for a scalar field -- a mandatory `list[X]` requires at least
  one matched item (else `process_list_field` raises), while
  `list[X] | None` allows zero items (the field is left `None`); once
  the first item is found, every subsequent item is implicitly
  optional regardless of which of the two was declared.

- `get_extent(text: 'str') -> 'int'`
  Return this pair's own extent, as a line count, as the sum of its fields' own extents.

  No class elsewhere in this codebase computes a composite's own
  extent this way (every other composite is either heading-bounded or
  a single pre-grouped markdown-it token) -- this is a local,
  throwaway mechanism for `qa/models/v2/` only (see this module's
  docstring).

  Rather than calling each field's own `get_extent` on successively
  re-normalized substrings (which would silently under-count: a raw
  substring can start with a blank separator line that `mdformat`
  would strip, exactly the class of bug `process_list_field`'s own
  docstring in `markdown_str.py` already documents), this walks the
  *same* single token stream `MarkdownStr.get_extent`'s continuous
  scan already uses, tracking which of `comment`/`question` have
  already been matched for *this* pair:

  - A depth-0 heading (any level) always stops the scan.
  - A depth-0 comment stops the scan unless it is the very first thing
    encountered for this pair (i.e. `comment` not yet matched, and no
    other content yet accumulated) -- otherwise it is either a second
    comment or a comment following already-started answer prose,
    either way belonging to the *next* pair.
  - A depth-0 block quote stops the scan unless `question` has not yet
    been matched and no other content has yet been accumulated for
    this pair -- otherwise it is either a second question or a block
    quote appearing after answer prose has already started, either way
    belonging to the *next* pair.
  - Anything else at depth 0 (a paragraph, a list, ...) is `answer`
    prose: once any such content has been seen, no further depth-0
    comment/block quote can still be *this* pair's own `question`.

  Args:
      text: Markdown source, pre-formatted with `mdformat`.

  Returns:
      0: nothing matches at all (the enclosing `list[QaQuestionAnswer]`,
          and therefore the whole category section, may legitimately be
          empty).
      int > 0: line count (see `MarkdownStr.get_extent`) covered by
          this pair's own `comment`/`question`/`answer`, stopping
          before the next pair (or the next heading), or at the end of
          `text` if neither follows.

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

- `process_field(name: 'str', type_: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[int, MarkdownStr | None]'`
  Resolve one nested field's extent and parsed instance from `text`.

  Args:
      name: the field's attribute name (used only for error messages).
      type_: the field's declared `MarkdownStr` subclass.
      text: the not-yet-consumed remainder of the parent's markdown text;
          the field is assumed to start at the very first line of `text`.
      optional: whether the field is declared `Optional[type_]`/
          `type_ | None`. When `True` and `type_.get_extent(text)` finds
          no extent, this is not an error: the field is simply absent
          from `text` (e.g. an optional section whose heading doesn't
          appear next), and `(0, None)` is returned so the caller can
          move on to the next field without consuming any of `text`.

  Returns:
      A `(extent, instance)` pair: `extent` is the number of leading
      lines of `text` this field consumes (see `MarkdownStr.get_extent`),
      and `instance` is the field's value, parsed via
      `type_.from_text` on exactly those `extent` leading lines -- or
      `(0, None)` for an absent optional field (see `optional` above).

- `process_list_field(name: 'str', item_type: 'type[MarkdownStr]', text: 'str', *, optional: 'bool' = False) -> 'tuple[str, list[MarkdownStr] | None]'`
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
      name: the field's attribute name (used only for error messages).
      item_type: the field's declared `MarkdownStr` subclass (the `X`
          in `list[X]`/`list[X] | None`).
      text: the not-yet-consumed remainder of the parent's markdown
          text; the first item, if any, is assumed to start at the very
          first line of `text`.
      optional: whether the field is declared `list[X] | None`. When
          `True` and no item at all is found, this is not an error:
          `(text, None)` is returned so the caller can move on to the
          next field without consuming any of `text`.

  Returns:
      A `(remaining_text, items)` pair: `remaining_text` is `text` with
      every matched item (and any separating blank lines) removed and
      re-normalized via `mdformat.text()`, ready to be handed directly
      to the next declared field -- and `items` is the non-empty list
      of parsed instances, or `(text, None)` for an absent optional
      field (see `optional` above).

- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`

- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`

- `update_forward_refs(**localns: 'Any') -> 'None'`

- `validate(value: 'Any') -> 'Self'`


## Functions

### `_is_block_quote(tok: 'Token') -> 'bool'`

Return whether `tok` is a `blockquote_open` token, matching `MarkdownBlockQuote`'s own metadata.


### `_is_comment(tok: 'Token') -> 'bool'`

Return whether `tok` is an HTML comment block, matching `MarkdownComment`'s own metadata.


### `_is_heading(tok: 'Token') -> 'bool'`

Return whether `tok` is a `heading_open` token of any level (h1-h6).

