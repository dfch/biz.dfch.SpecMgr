# `biz.dfch.specmgr.models.md.markdown`

No documentation available.

## Functions

### `markdown(*, type: 'str | None' = <object object>, tag: 'str | None' = <object object>, end_marker: 'type[MarkdownStr] | None' = <object object>)`

Decorator to add markdown-it metadata to MarkdownStr subclasses.

Attaches metadata (type, tag, and end_marker) to a MarkdownStr subclass
via the `_metadata` class attribute. This decorator focuses on
markdown-it token properties only. Use the @alias decorator separately
to control display naming.

Merges into `cls`'s already-inherited `_metadata` (via
`getattr(cls, "_metadata", {})`) instead of unconditionally replacing
it: only the keyword arguments actually passed to this call are written
into the merged dict; a keyword left out entirely leaves whatever `cls`
already inherited for that key untouched. All three parameters are
keyword-only and default to a private sentinel (`_UNSET`), not `None`,
specifically so "this keyword was not passed" can be told apart from
"this keyword was explicitly passed as `None`" -- the latter is a real,
honored value that overwrites (or clears) an inherited entry, exactly
like passing any other explicit value would.

Args:
    type: The markdown-it token type (e.g., 'heading_open', 'paragraph_open', 'inline').
          This identifies the type of markdown token this class represents. Omit
          to leave any inherited `type` untouched; pass `None` to explicitly clear it.
    tag: Expected HTML tag (e.g., 'h1', 'h2', 'h3', 'p').
         Use None if the class does not correspond to a specific HTML tag. Omit
         to leave any inherited `tag` untouched; pass `None` to explicitly clear it.
    end_marker: A `MarkdownStr` subclass (e.g. `MarkdownBlockQuote`) whose own
         markdown-it `type`/`tag` should stop a `MarkdownSection.get_extent` scan
         the moment it occurs at nesting depth 0, in addition to the existing
         heading-level stop condition. Omit to leave any inherited `end_marker`
         untouched; pass `None` to explicitly clear it. Defaults to no end marker.

Returns:
    A class decorator that attaches markdown-it metadata to the decorated class.

Example:
    Basic usage with type only:
    >>> @markdown(type="paragraph_open")
    ... class Notes(MarkdownStr): ...
    >>> Notes._metadata
    {'type': 'paragraph_open'}

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

    A subclass re-applying @markdown only overrides what it explicitly
    passes, keeping any other inherited key (here, `end_marker`):
    >>> @markdown(type="heading_open", tag="h4", end_marker=MarkdownBlockQuote)
    ... class Base(MarkdownSection): ...
    >>> @markdown(tag="h4")
    ... class Sub(Base): ...
    >>> Sub._metadata
    {'type': 'heading_open', 'tag': 'h4', 'end_marker': <class 'MarkdownBlockQuote'>}

