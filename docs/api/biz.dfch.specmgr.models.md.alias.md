# `biz.dfch.specmgr.models.md.alias`

Alias decorator for MarkdownStr class name transformation.

This module provides the @alias decorator to control how class names are
displayed, independent of the @annotate decorator. Works in combination with
@annotate to separate concerns: @annotate defines markdown-it properties, while
@alias controls display naming.

## Functions

### `alias(value: 'str | None' = None, type: 'AliasType' = <AliasType.SPACE_SEPARATED: 'SPACE_SEPARATED'>)`

Decorator to set a display name/alias for a MarkdownStr class.

Separates alias configuration from markdown-it type information. Use this
decorator in combination with @annotate to control how class names are
displayed.

Args:
    value: The alias/display name for the class. Interpretation depends on type:
           - LITERAL: Used as exact display name
           - SPACE_SEPARATED: Ignored; class name is converted automatically
           - REGEX: Treated as a regex pattern for matching
           If not provided, class name is used.
    type: How to interpret the alias value. One of AliasType values:
          - AliasType.SPACE_SEPARATED: Auto-convert class name to title case
            with spaces (e.g., RequiredInformation → Required Information)
          - AliasType.LITERAL: Use alias as exact string (explicit override)
          - AliasType.REGEX: Treat alias as regex pattern
          Defaults to AliasType.SPACE_SEPARATED.

Returns:
    A class decorator that attaches alias metadata to the decorated class.

Example:
    Space-separated (automatic conversion):
    >>> @annotate(type="paragraph_open")
    ... @alias(type=AliasType.SPACE_SEPARATED)
    ... class RequiredInformation(MarkdownStr): ...
    >>> RequiredInformation._alias_metadata['value']
    'Required Information'

    Literal alias (explicit):
    >>> @annotate(type="heading_open", tag="h1")
    ... @alias(value="Custom Title")
    ... class Title(MarkdownStr): ...
    >>> Title._alias_metadata
    {'value': 'Custom Title', 'type': 'LITERAL'}

    Regex pattern matching:
    >>> @annotate(type="inline")
    ... @alias(value=r"^Title.*", type=AliasType.REGEX)
    ... class Title(MarkdownStr): ...
    >>> Title._alias_metadata['type']
    'REGEX'

