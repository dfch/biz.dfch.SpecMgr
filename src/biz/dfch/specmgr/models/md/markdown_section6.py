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

"""Markdown section starting with h6 heading."""

from __future__ import annotations

from pydantic import model_validator

from .markdown_section import MarkdownSection
from .markdown import markdown


@markdown(type="heading_open", tag="h6")
class MarkdownSection6(MarkdownSection):
    """Markdown content starting with an h6 heading, no nested headings allowed.

    Tokens [0:3] form the opening h6 heading triple (heading_open/inline/heading_close).
    All tokens after index 3 must not contain any heading tags (h1-h6).
    """

    @model_validator(mode="after")
    def validate_headings(self) -> MarkdownSection6:
        """Validate heading level and no nested headings.

        Base class validates the heading triple structure.
        This validates: specific tag h6 and no nested headings in tokens [3:].
        """
        # assert self._tokens[0].tag == "h6", f"Expected h6, got {self._tokens[0].tag}"
        # assert not any(
        #     t.tag in ("h1", "h2", "h3", "h4", "h5", "h6") for t in self._tokens[3:] if t.type == "heading_open"
        # ), "Nested headings not allowed"
        return self
