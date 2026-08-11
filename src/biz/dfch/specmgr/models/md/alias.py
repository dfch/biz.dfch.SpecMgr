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

"""Alias decorator for MarkdownStr class name transformation.

This module provides the @alias decorator to control how class names are
displayed, independent of the @annotate decorator. Works in combination with
@annotate to separate concerns: @annotate defines markdown-it properties, while
@alias controls display naming.
"""

from __future__ import annotations

from .alias_type import AliasType


def alias(value: str | None = None, type: AliasType = AliasType.SPACE_SEPARATED):
    """Decorator to set a display name/alias for a MarkdownStr class.

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
    """

    def decorator(cls):
        cls._alias_metadata = {
            "value": value or cls.__name__,
            "type": type,
        }
        return cls

    return decorator
