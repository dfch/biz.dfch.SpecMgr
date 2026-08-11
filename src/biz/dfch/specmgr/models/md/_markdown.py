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

"""Markdown shared instance."""

import mdformat
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark")

#: `mdformat` options shared by every normalization call across `models/md/`.
#:
#: `number=True` switches `mdformat`'s ordered-list renderer from its default
#: behavior (collapsing every item's marker to `"1."`, since CommonMark only
#: treats a list's *first* number as semantically meaningful) to genuine
#: consecutive numbering (`"1."`, `"2."`, `"3."`, ...) derived from each
#: item's position. This is required for `MarkdownListItem`-based ordered
#: lists to round-trip their real numbering at all -- without it, the
#: `text == format_text(text)` invariant every `get_extent`/`from_text`
#: implementation asserts would hold, but only by *destroying* the original
#: sequential numbers on the very first normalization pass. It has no effect
#: on bullet lists, headings, or paragraphs.
_MDFORMAT_OPTIONS = {"number": True}


def format_text(text: str) -> str:
    """Normalize `text` with the shared `mdformat` options (see `_MDFORMAT_OPTIONS`).

    Every module under `models/md/` must call this instead of calling
    `mdformat.text(text)` directly, so the whole engine normalizes
    consistently -- `get_extent`/`from_text`'s `text == format_text(text)`
    precondition would otherwise fail as soon as two call sites disagreed on
    options.

    Args:
        text: Markdown source to normalize.

    Returns:
        The `mdformat`-normalized text.
    """
    assert isinstance(text, str), type(text)
    return mdformat.text(text, options=_MDFORMAT_OPTIONS)
