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


def markdown(type: str | None = None, tag: str | None = None):
    """Decorator to add markdown-it metadata to MarkdownStr subclasses.

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
    """

    def decorator(cls):
        cls._metadata = {
            "type": type,
            "tag": tag,
        }
        return cls

    return decorator
