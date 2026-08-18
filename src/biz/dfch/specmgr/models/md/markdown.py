# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from typing import Any

from .markdown_str import MarkdownStr

#: Sentinel distinguishing "caller did not pass this keyword argument at all"
#: from "caller explicitly passed `None`" for `markdown()`'s merge-into-
#: inherited-`_metadata` semantics (see `markdown()` below). A plain `None`
#: default cannot make this distinction, since `None` is also a legitimate,
#: explicit value for `type`/`tag`/`end_marker` (e.g. explicitly clearing an
#: inherited `end_marker`). Never compared for equality, only identity
#: (`is`/`is not`), so any unique object works; a private module-level
#: sentinel avoids importing/depending on a third-party "missing" marker.
_UNSET: Any = object()


def markdown(
    *,
    type: str | None = _UNSET,
    tag: str | None = _UNSET,
    end_marker: type[MarkdownStr] | None = _UNSET,
):
    """Decorator to add markdown-it metadata to MarkdownStr subclasses.

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
    """

    def decorator(cls):
        metadata: dict[str, Any] = dict(getattr(cls, "_metadata", {}))

        if type is not _UNSET:
            metadata["type"] = type
        if tag is not _UNSET:
            metadata["tag"] = tag
        if end_marker is not _UNSET:
            metadata["end_marker"] = end_marker

        cls._metadata = metadata
        return cls

    return decorator
