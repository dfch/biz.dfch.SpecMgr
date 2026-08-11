# `biz.dfch.specmgr.models.md.markdown`

No documentation available.

## Functions

### `markdown(type: 'str | None' = None, tag: 'str | None' = None)`

Decorator to add markdown-it metadata to MarkdownStr subclasses.

Attaches metadata (type and tag) to a MarkdownStr subclass via the `_metadata`
class attribute. This decorator focuses on markdown-it token properties only.
Use the @alias decorator separately to control display naming.

Args:
    type: The markdown-it token type (e.g., 'heading_open', 'paragraph_open', 'inline').
          This identifies the type of markdown token this class represents.
    tag: Expected HTML tag (e.g., 'h1', 'h2', 'h3', 'p').
         Use None if the class does not correspond to a specific HTML tag.

Returns:
    A class decorator that attaches markdown-it metadata to the decorated class.

Example:
    Basic usage with type only:
    >>> @markdown(type="paragraph_open")
    ... class Notes(MarkdownStr): ...
    >>> Notes._metadata
    {'type': 'paragraph_open', 'tag': None}

    With both type and tag:
    >>> @markdown(type="heading_open", tag="h1")
    ... class Title(MarkdownStr): ...
    >>> Title._metadata
    {'type': 'heading_open', 'tag': 'h1'}

    Combined with @alias decorator:
    >>> @markdown(type="heading_open", tag="h1")
    ... @alias(value="Custom Title")
    ... class Title(MarkdownStr): ...
    >>> Title._metadata['type']
    'heading_open'
    >>> Title._alias_metadata['value']
    'Custom Title'

