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

"""Alias type enumeration for MarkdownStr class name transformation.

This module defines how class name aliases should be interpreted and transformed
when generating display names for MarkdownStr subclasses via the @annotate decorator.
"""

from __future__ import annotations

from enum import StrEnum


class AliasType(StrEnum):
    """Enum defining how class name aliases should be interpreted and transformed.

    This enum controls how the `alias` parameter in the `@annotate` decorator
    is processed when generating display names for MarkdownStr subclasses.

    The three alias types allow for different naming conventions and transformations:
    - Automatic space-separated formatting from PascalCase names
    - Explicit literal string overrides
    - Regular expression pattern matching for complex transformations

    Attributes:
        SPACE_SEPARATED: Converts PascalCase/camelCase class names to space-separated
                        words in title case. For example:
                        - 'RequiredInformation' → 'Required Information'
                        - 'GoalInContext' → 'Goal In Context'
                        - 'CharacteristicInformation' → 'Characteristic Information'
                        Ignores any explicit `alias` parameter when used.

        LITERAL: Treats the `alias` parameter as an exact, literal string to use as
                the display name. If no `alias` is provided, the class name is used
                without any transformation. Most suitable for custom display names
                (e.g. a heading carrying a "(required)"/"(optional)" suffix, or
                inline formatting markup). Not the default: `@alias`'s own default
                `type` is `SPACE_SEPARATED` (see `alias.py`), and a class with no
                `@alias` decorator at all also defaults to `SPACE_SEPARATED`'s
                derivation of its own class name, not a `LITERAL` match (ADR
                832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0).

        REGEX: Treats the `alias` parameter as a regular expression pattern that can
              be used to match or transform class names. Useful for complex naming
              conventions or pattern-based transformations that don't fit into the
              SPACE_SEPARATED or LITERAL categories.

    Example:
        Space-separated formatting (automatic):
        >>> from biz.dfch.specmgr.models.md import annotate, AliasType
        >>> @annotate(type="paragraph_open", alias_type=AliasType.SPACE_SEPARATED)
        ... class RequiredInformation(MarkdownStr): ...
        >>> RequiredInformation._metadata['alias']
        'Required Information'

        Literal override (explicit):
        >>> @annotate(type="heading_open", alias="Custom Title", alias_type=AliasType.LITERAL)
        ... class Title(MarkdownStr): ...
        >>> Title._metadata['alias']
        'Custom Title'

        Regex pattern matching:
        >>> @annotate(
        ...     type="inline",
        ...     alias=r"^(Goal|Scope).*",
        ...     alias_type=AliasType.REGEX
        ... )
        ... class GoalInContext(MarkdownStr): ...
        >>> GoalInContext._metadata['alias_type']
        'REGEX'
    """

    SPACE_SEPARATED = "SPACE_SEPARATED"
    LITERAL = "LITERAL"
    REGEX = "REGEX"
