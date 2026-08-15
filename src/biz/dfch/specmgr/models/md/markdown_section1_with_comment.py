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

"""Opt-in `MarkdownSection1` variant allowing a leading explanatory comment."""

from __future__ import annotations

from pydantic import Field

from .markdown_comment import MarkdownComment
from .markdown_section1 import MarkdownSection1


class MarkdownSection1WithComment(MarkdownSection1):
    """Adds an optional leading `<!-- ... -->` comment before another field.

    Must be paired with >=1 other declared field to hold the section's body
    content -- comment-only use raises (see `get_extent`/`from_text`).
    """

    comment: MarkdownComment | None = Field(
        default=None, description="Optional explanatory HTML comment (`<!-- ... -->`)."
    )

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Enforce the >=1-other-field constraint, then defer to `MarkdownSection1.get_extent`."""
        assert len(cls._get_field_names()) > 1, (
            f"{cls.__name__}: 'comment' must be paired with at least one other declared field "
            "to absorb the section's body content"
        )
        return super().get_extent(text)

    @classmethod
    def from_text(cls, text: str) -> MarkdownSection1WithComment:
        """Enforce the >=1-other-field constraint, then defer to `MarkdownSection1.from_text`."""
        assert len(cls._get_field_names()) > 1, (
            f"{cls.__name__}: 'comment' must be paired with at least one other declared field "
            "to absorb the section's body content"
        )
        return super().from_text(text)
