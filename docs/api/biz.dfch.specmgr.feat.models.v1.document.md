# `biz.dfch.specmgr.feat.models.v1.document`

Pydantic model for a full feature document (frontmatter + body).

Mirrors `dec.models.v1.document.DecDocument`'s own frontmatter+body pairing.
``FeatDocument`` holds no file/id/path information itself -- that lives on
``frontmatter.id``, same convention as ``FeatFrontmatter.id`` (though, unlike
every other domain, `feat`'s own `id` is also -- by REQ-004's addressing
convention -- the name of the containing folder, an invariant enforced at
the *tool* layer in Phase 2, not here).

Frontmatter *stripping* is deliberately not this module's responsibility:
a caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata`` as
``FeatFrontmatter`` and ``.content`` as ``Feature.from_text(...)`` separately,
then constructs a ``FeatDocument`` from the two already-parsed pieces -- see
``feat/models/v1/parser.py::parse_feat`` for that glue.

## Classes

### `FeatDocument`

A full feature document: YAML frontmatter and body.

Attributes
----------
frontmatter:
    The YAML frontmatter block. See :class:`FeatFrontmatter`.
body:
    The parsed feature sections. See :class:`Feature`.

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

