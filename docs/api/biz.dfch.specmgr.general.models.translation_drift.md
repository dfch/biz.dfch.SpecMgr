# `biz.dfch.specmgr.general.models.translation_drift`

Translation drift detection: the pure heading-skeleton comparison, the staleness comparison, and the
``check_translation_drift`` tool's result models (feat-197-i18n Phase 140, REQ-014, ACC-009).

Drift between a translated language variant and its source document comes in two kinds (REQ-014), and this module
holds the deterministic, I/O-free core of both:

**(a) Structural drift** -- a section of the variant that is *missing*, *extra*, or *reordered* relative to the
source's canonical schema. :func:`heading_skeleton` reduces a document's body text to its ordered list of
:class:`SkeletonEntry` (one per heading, ``h2`` and deeper), and :func:`compare_skeletons` diffs two skeletons into
:class:`DriftFinding` rows. The skeleton is computed on the document's *raw* body text with the very same
heading/fence recognizer the parse boundary uses (:func:`~biz.dfch.specmgr.general.models.heading_table.
iter_heading_lines`, which :func:`~biz.dfch.specmgr.general.models.heading_table.normalize_heading_lines` is also
built on), so the drift check and the parser can never disagree on what a heading is. Each heading is reduced to a
language-invariant **structural key**:

1. its text is mapped back to canonical English through the language's heading table (``table.get(text, text)``,
   ADR 38efdb66 item 5 -- a heading without an entry is already canonical or genuinely unknown);
2. a **data-carrying heading** -- one whose schema alias carries a free-text group, ADR 38efdb66 item 3 -- is reduced
   to its schema-constant token part, dropping the free text the translator legitimately changes
   (:data:`_TOKEN_PATTERNS`): ``Option N: <title>`` -> ``Option N:`` (dec), ``Step N: <title>`` -> ``Step N:``
   (sop, uc), ``Extension N<l>. <title>`` -> ``Extension N<l>.`` (uc), ``AC-NNN (Method): <text>`` ->
   ``AC-NNN (Method):`` (vcr). A heading whose *whole* text is the schema-constant token (rsk's
   ``Probability {1..5}``/``Impact {1..5}``) needs no reduction -- it already compares as a whole, so a changed
   closed-vocabulary value shows up as a ``missing`` + ``extra`` pair (REQ-010: those tokens stay canonical and
   identical in every language);
3. a **timestamp-led update entry** (``### <timestamp> - <title>`` under ``## Updates``/``## Recent Updates``,
   :data:`_UPDATE_ENTRY_PATTERN`) is a change-log row, not a schema section: a translation keeps its own history, so
   the entry (and anything nested inside it) is *not compared*; the enclosing ``## Updates`` section still is;
4. the **key** of a heading is its canonical ancestor chain plus itself (``Initial Assessment > Probability 3``), so
   a heading that legitimately recurs under different parents (rsk's two ``Probability``/``Impact`` pairs) never
   collides; a repeat under the same parent is disambiguated by an occurrence suffix. A renamed, missing, or extra
   section therefore carries its whole subtree: every sub-section of it is reported as well (the first finding of
   each subtree is its root).

The ``h1`` title is free prose (every domain's own H1 alias is ``.+``, or a fixed prefix plus free text) and is not
part of the skeleton, and prose that is not a heading at all -- paragraphs, list items, fenced code, ``prb``'s
regex-locked ``problem_statement`` lead paragraph (ADR item 11, exempt in every language) -- is invisible to it by
construction: drift detection is about structure and staleness, never about wording or translation quality.

**(b) Staleness** -- the source's frontmatter ``updated`` timestamp is newer than the variant's
(:func:`check_staleness`). Both are compared as *parsed, offset-aware datetimes* (never as strings), so the ``T`` and
space separators and any UTC offset (``Z``/``+01:00``) the frontmatter accepts compare correctly (ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf); equal or older is *not* stale; a missing or unparseable timestamp is reported,
never raised.

:class:`TranslationDriftResult` is the single structured, non-raising answer the ``check_translation_drift`` tool
returns: both drift kinds in one run (ACC-009).

## Classes

### `DriftFinding`

One structural finding of the drift check (REQ-014a).

Parameters
----------
kind:
    ``"missing"`` -- a source section the variant lacks; ``"extra"`` -- a variant section the source lacks;
    ``"reordered"`` -- a section both have but in a different relative order (the sections outside the longest
    common order are reported); ``"unparseable"`` -- the document cannot be parsed (carries ``error``).
heading:
    The canonical English heading token (the schema form), or ``None`` for ``"unparseable"``.
path:
    The canonical ancestor chain including ``heading``, ``" > "``-joined, or ``None`` for ``"unparseable"``.
level:
    The heading level (2-6), or ``None`` for ``"unparseable"``.
text:
    The heading text as it appears on disk in the document where the finding was made (the source for
    ``missing``, the variant for ``extra``/``reordered``) -- what the translator wrote for an ``extra`` section.
source_position:
    The 1-based position among the source's compared headings (``None`` for ``extra``).
variant_position:
    The 1-based position among the variant's compared headings (``None`` for ``missing``).
language:
    For ``"unparseable"``: the language of the document that fails to parse.
error:
    For ``"unparseable"``: the parse-failure message (byte-identical to the domain's ``list_<d>`` failed-row
    ``error`` for the same file).
message:
    A one-line, human-readable description of the finding.

**Methods:**

- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`

- `from_orm(obj: 'Any') -> 'Self'`

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

- `model_post_init(self, context: 'Any', /) -> 'None'`
  Override this method to perform additional initialization after `__init__` and `model_construct`.
  This is useful if you want to do some validation that requires the entire model to be initialized.

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

- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`

- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`

- `update_forward_refs(**localns: 'Any') -> 'None'`

- `validate(value: 'Any') -> 'Self'`


### `SkeletonEntry`

One compared heading of a document's skeleton.

Attributes
----------
level:
    The heading level (2-6).
text:
    The heading text exactly as it appears in the document (its own language).
token:
    The canonical, language-invariant token of the heading (the table-mapped text, reduced to its
    schema-constant part for a data-carrying heading).
path:
    The canonical ancestor chain including ``token``, :data:`_PATH_SEPARATOR`-joined.
key:
    ``path`` made unique within the document by an occurrence suffix (``#2``, ``#3``, ...) for a repeat.
position:
    The 1-based position of this heading among the document's compared headings.


### `Staleness`

The outcome of :func:`check_staleness` (the staleness half of a :class:`TranslationDriftResult`).

Attributes
----------
stale:
    ``True`` iff the source is strictly newer than the variant.
source_updated:
    The source's timestamp as written, or ``None`` if missing.
variant_updated:
    The variant's timestamp as written, or ``None`` if missing.
source_ahead_by_seconds:
    Signed ``source - variant`` in seconds, or ``None`` if not comparable.
error:
    ``None`` if compared; otherwise why not.


### `TranslationDriftResult`

The ``check_translation_drift`` tool's non-raising result: structural drift and staleness in one run.

Parameters
----------
type:
    The artifact's document type, echoed back.
id:
    The artifact's id (shared by both languages), echoed back.
source_language:
    The language compared *against* (``"en"`` by default).
language:
    The translated variant's language.
source_path:
    The absolute, resolved path of the source document.
variant_path:
    The absolute, resolved path of the variant document.
in_sync:
    ``True`` iff there is no structural finding, the variant is not stale, and staleness could be determined
    (``staleness_error`` is ``None``) -- an unverifiable timestamp never counts as in sync.
structural:
    The structural findings (empty when the variant's section structure matches the source's).
stale:
    ``True`` iff the source's ``updated`` timestamp is strictly newer than the variant's (REQ-014b).
source_updated:
    The source's frontmatter ``updated`` value as written (``None`` if missing/unreadable).
variant_updated:
    The variant's frontmatter ``updated`` value as written (``None`` if missing/unreadable).
source_ahead_by_seconds:
    Signed ``source_updated - variant_updated`` in seconds (positive = the source is newer), or ``None`` when
    either timestamp is missing or unparseable.
staleness_error:
    ``None`` when both timestamps were compared; otherwise why they could not be (missing, unparseable, no UTC
    offset, frontmatter unreadable).

**Methods:**

- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`

- `from_orm(obj: 'Any') -> 'Self'`

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

- `model_post_init(self, context: 'Any', /) -> 'None'`
  Override this method to perform additional initialization after `__init__` and `model_construct`.
  This is useful if you want to do some validation that requires the entire model to be initialized.

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

- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`

- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`

- `update_forward_refs(**localns: 'Any') -> 'None'`

- `validate(value: 'Any') -> 'Self'`


## Functions

### `_canonical_token(text: 'str', table: 'dict[str, str] | None') -> 'str | None'`

Return the language-invariant token of a heading ``text``, or ``None`` for an excluded update entry.


### `_longest_common_subsequence(a: 'list[str]', b: 'list[str]') -> 'list[str]'`

Return one longest common subsequence of ``a`` and ``b`` (standard dynamic programming, deterministic).


### `_parse_timestamp(value: 'object', label: 'str') -> 'tuple[datetime | None, str | None, str | None]'`

Parse one frontmatter ``updated`` value into ``(aware datetime, as-written text, error)`` (each may be None).


### `check_staleness(source_updated: 'object', variant_updated: 'object') -> 'Staleness'`

Compare the source's and the variant's ``updated`` timestamps (REQ-014b).

Both values are parsed to offset-aware datetimes and compared as instants -- never as strings -- so the ``T``
and space separators and any UTC offset compare correctly. The variant is stale iff the source is strictly
newer; equal or older is not stale. A missing, unparseable, or offset-less timestamp on either side is
reported in ``error`` (``stale`` stays ``False``, nothing is raised).

Parameters
----------
source_updated:
    The source frontmatter's ``updated`` value (a string as written, a ``datetime`` PyYAML coerced, or ``None``).
variant_updated:
    The variant frontmatter's ``updated`` value, likewise.

Returns
-------
Staleness
    The staleness verdict with both timestamps as written and the signed delta.


### `compare_skeletons(source: 'list[SkeletonEntry]', variant: 'list[SkeletonEntry]') -> 'list[DriftFinding]'`

Diff a variant's skeleton against its source's into ``missing``/``extra``/``reordered`` findings (REQ-014a).

Findings come in a deterministic order: every ``missing`` (source order), every ``extra`` (variant order), then
every ``reordered`` (variant order). A section both documents have but in a different relative order is
``reordered``: the sections *outside* one longest common subsequence of the two documents' shared sections are
reported (so one moved section yields one finding, not a cascade).

Parameters
----------
source:
    The source document's skeleton.
variant:
    The variant document's skeleton.

Returns
-------
list[DriftFinding]
    The structural findings; empty when the two skeletons agree.


### `heading_skeleton(body: 'str', table: 'dict[str, str] | None') -> 'list[SkeletonEntry]'`

Reduce a document's (mdformat-normalized) body text to its ordered, language-invariant heading skeleton.

See the module docstring for the structural-key rule. ``h1`` headings and timestamp-led update entries (with
everything nested inside them) are not part of the skeleton.

Parameters
----------
body:
    The frontmatter-stripped, mdformat-normalized body text.
table:
    The document language's ``<translated> -> <canonical>`` heading table, or ``None`` for a canonical (EN)
    document.

Returns
-------
list[SkeletonEntry]
    One entry per compared heading, in document order, ``position`` numbered from 1.

