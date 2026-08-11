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

"""Match a parsed heading's actual text against a class's declared `@alias`.

Encapsulates the comparison logic so `MarkdownSection.from_text` can assert
that the heading it just parsed is actually the one the class claims to
represent, instead of leaving `@alias`'s `_alias_metadata` as inert,
never-checked class data.
"""

from __future__ import annotations

import re

from .alias_type import AliasType

_SPACE_SEPARATED_PATTERN = re.compile(r"(?<!^)(?=[A-Z])|(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])")


def space_separated_name(class_name: str) -> str:
    """Convert a PascalCase class name to space-separated title case.

    E.g. `"GoalInContext"` -> `"Goal In Context"`, `"SectionLevel1"` ->
    `"Section Level 1"`. This is `AliasType.SPACE_SEPARATED`'s
    auto-derivation rule -- an explicit, opt-in alternative for a class
    whose natural heading text differs from its bare class name (see
    `match_alias`; this is no longer the fallback for a class with no
    `@alias` metadata at all).

    Args:
        class_name: A class's `__name__`, e.g. `"GoalInContext"`.

    Returns:
        `class_name` with a space inserted before every non-leading
        uppercase letter, and at every letter<->digit boundary in either
        direction (e.g. `"SectionLevel1"` -> `"Section Level 1"`,
        `"Level1abc"` -> `"Level 1 abc"`). A run of consecutive digits
        (`"Level123"` -> `"Level 123"`) or consecutive uppercase letters is
        never split internally by this rule.
    """
    assert isinstance(class_name, str) and class_name, class_name

    result = _SPACE_SEPARATED_PATTERN.sub(" ", class_name)

    return result


def match_alias(cls: type, heading_text: str) -> bool:
    """Return whether `heading_text` satisfies `cls`'s declared `@alias`.

    A class with no `_alias_metadata` at all (no `@alias` decorator applied,
    directly or inherited) defaults to `AliasType.SPACE_SEPARATED`'s own
    derivation of `cls.__name__` -- equivalent to an implicit
    `@alias(type=AliasType.SPACE_SEPARATED)` -- rather than accepting any
    heading text (see ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0; a
    literal match against `cls.__name__` verbatim was v1.2.0/v1.3.0/v1.3.1's
    incorrect specification of this same default, corrected in v1.4.0).
    `@alias` is opt-in for *customizing* the comparison away from that
    default (a literal value with different wording/casing/suffixes/
    formatting, or a regex), not for enabling matching in the first place:
    an undecorated `MarkdownSection` subclass is always checked against
    something. A class whose heading text is data rather than a fixed
    schema label (e.g. a document's own H1 title) should declare an
    explicit `@alias(value=".+", type=AliasType.REGEX)` to accept any
    non-empty heading text (v1.3.1) -- there is no separate opt-out of alias
    matching for this case; the `SPACE_SEPARATED` default alone would still
    pin such a title to a fixed, class-name-derived value.

    Args:
        cls: A `MarkdownSection` subclass, possibly decorated with `@alias`.
        heading_text: The heading's actual inline content, as parsed by
            `MarkdownSection.from_text` (e.g. `t_mid.content.strip()`).

    Returns:
        `True` if `heading_text` satisfies the effective `@alias` -- either
        the declared one, or the implicit `SPACE_SEPARATED`-derived default
        when none is declared -- under the applicable `AliasType`:
        - `LITERAL`: `heading_text` equals the declared value exactly
          (case-sensitive, no normalization).
        - `SPACE_SEPARATED`: `heading_text` equals `cls.__name__` converted
          via `space_separated_name`.
        - `REGEX`: `heading_text` fully matches the declared value as a
          regular expression pattern.
        `False` otherwise.
    """
    assert isinstance(cls, type), type(cls)
    assert isinstance(heading_text, str), type(heading_text)

    metadata = getattr(cls, "_alias_metadata", None)
    if metadata is None:
        return heading_text == space_separated_name(cls.__name__)

    alias_type = metadata["type"]
    alias_value = metadata["value"]

    if alias_type == AliasType.LITERAL:
        result = heading_text == alias_value
    elif alias_type == AliasType.SPACE_SEPARATED:
        result = heading_text == space_separated_name(cls.__name__)
    elif alias_type == AliasType.REGEX:
        result = re.fullmatch(alias_value, heading_text) is not None
    else:
        assert False, f"{cls.__name__}: unknown alias type {alias_type!r}"

    return result
