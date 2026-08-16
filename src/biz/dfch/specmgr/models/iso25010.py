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

"""Pydantic schema and parser for the ISO/IEC 25010:2023 product quality
model.

Flat and unversioned, not a user-edited or independently-versioned document
type.
"""

from __future__ import annotations

from pydantic import Field

from .md import (
    AliasType,
    MarkdownComment,
    MarkdownListItem,
    MarkdownParagraph,
    MarkdownSection1,
    MarkdownSection2,
    MarkdownSection3,
    alias,
)
from .md._markdown import format_text

__all__ = ["Characteristic", "Iso25010", "SubCharacteristic", "parse_iso25010"]


@alias(value=".+", type=AliasType.REGEX)
class SubCharacteristic(MarkdownSection3):
    """One of the sub-characteristics of ISO/IEC 25010:2023."""

    description: MarkdownParagraph = Field(description="The definition of this sub-characteristic.")


@alias(value=".+", type=AliasType.REGEX)
class Characteristic(MarkdownSection2):
    """One of the 9 main ISO/IEC 25010:2023 characteristics."""

    description: MarkdownParagraph = Field(description="The definition of this main characteristic.")
    sub_characteristics: list[SubCharacteristic] = Field(
        min_length=1,
        description="The definition of the sub-characteristics for this main characteristic.",
    )


@alias(value=".+", type=AliasType.REGEX)
class Iso25010(MarkdownSection1):
    """The ISO/IEC 25010:2023 product quality model.

    Parameters
    ----------
    names:
        The 9-item list of main characteristic names (in order).
    comment:
        Copyright notice.
    characteristics:
        The 9 main characteristics.
    """

    names: list[MarkdownListItem] = Field(
        min_length=9,
        max_length=9,
        description="The exact names of the nine main characteristics.",
    )
    comment: MarkdownComment | None = Field(default=None, description="Copyright notice.")
    characteristics: list[Characteristic] = Field(
        min_length=9,
        max_length=9,
        description="The detailed description of the nine main characteristics.",
    )


def parse_iso25010(text: str) -> Iso25010:
    """Parse the packaged ISO/IEC 25010:2023 markdown text into an :class:`Iso25010`.

    Thin `format_text` + `Iso25010.from_text` wrapper -- unlike `parse_adr`/
    `parse_req`, there is no YAML frontmatter to split off first, since this
    is a plain packaged data file, not a user-authored document.

    Parameters
    ----------
    text:
        The complete markdown file content, exactly as read from disk (e.g.
        via `general.tools._packaged_data.read_packaged_text`).

    Returns
    -------
    Iso25010
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation.
    """
    result = Iso25010.from_text(format_text(text))
    assert isinstance(result, Iso25010), type(result)
    return result
