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

"""Base class for a markdown paragraph ("p"), the non-heading sibling of `MarkdownSection`."""

from __future__ import annotations

import mdformat

from .markdown_str import MarkdownStr
from ._markdown import md
from .markdown import markdown
from .markdown_section import _HEADING_TAGS


@markdown(type="paragraph_open", tag="p")
class MarkdownParagraph(MarkdownStr):
    """A markdown paragraph ("p"), the non-heading sibling of `MarkdownSection`.

    Unlike a heading, a paragraph has no level, so there is a single
    `MarkdownParagraph` class -- no `MarkdownParagraph1`..`6` spectrum, and no
    `@alias` enforcement of its own text (a paragraph's content is free-form
    prose, not a title to match against a class-name-derived alias).

    - Leaf (no nested `MarkdownStr`/`list[MarkdownStr]` fields declared):
      `_value` holds exactly the matched paragraph's own line span, verbatim
      -- nothing beyond `paragraph_close` is consumed. This mirrors the base
      `MarkdownStr.from_text` leaf case, just with the added `p`-tag
      validation from `@markdown`'s metadata.
    - Composite (has declared fields): `_value` holds only the paragraph's
      own inline text (e.g. a lead-in sentence); the *remaining* text after
      the paragraph's own line span is delegated to `super().from_text()`
      (`MarkdownStr.from_text`) for recursive field population, exactly like
      `MarkdownSection.from_text` delegates its post-heading body. Since a
      paragraph can never structurally contain a heading, the only thing
      that can bound how far this delegation reaches (see `get_extent`) is
      the next heading of any level (h1-h6) -- not some paragraph-specific
      level, since a paragraph has none.
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this paragraph (and, if composite, its fields' content), as a line count.

        Overrides `MarkdownStr.get_extent`. There is only an extent at all if
        the *first* token parsed from `text` is a `paragraph_open` matching
        this class's own `@markdown` metadata (`type="paragraph_open"`,
        `tag="p"`); otherwise this returns `0`, same as the base class's
        "no extent" case.

        If `cls` declares no nested fields (leaf case), the extent is
        exactly the paragraph's own line span (`paragraph_open.map[1]`) --
        nothing more.

        If `cls` declares nested fields (composite case), the extent
        continues scanning past the paragraph's own span, stopping (but
        excluding) at the next `heading_open` token of any level (h1-h6) --
        a paragraph can never itself contain a heading, so a heading always
        marks the end of whatever content belongs to this paragraph's
        fields. If no such heading follows, the extent reaches the end of
        `text`. The declared fields' own `get_extent`/`from_text` (via
        `MarkdownStr.from_text`'s existing field-distribution loop) then
        determine exactly how much of that heading-bounded window they
        actually consume.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` does not start with this class's own paragraph (no extent).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by this
                paragraph and, for a composite class, its fields' content, up
                to (excluding) the next heading of any level or the end of
                `text`.
        """
        assert isinstance(text, str), type(text)
        assert text == mdformat.text(text), "text is not in 'mdformat'."

        own_type = cls._metadata.get("type")
        own_tag = cls._metadata.get("tag")
        assert own_type == "paragraph_open" and own_tag == "p", (
            f"{cls.__name__}: expected type='paragraph_open', tag='p', got type={own_type!r}, tag={own_tag!r}"
        )

        tokens = md.parse(text)

        if not tokens or tokens[0].type != own_type or tokens[0].tag != own_tag:
            return 0

        own_map = tokens[0].map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: paragraph_open token has no line map"
        own_extent = own_map[1]

        if not cls._get_field_names():
            return own_extent

        result = own_extent
        for tok in tokens:
            m = tok.map
            if not m or len(m) != 2:
                continue

            if tok.type == "heading_open" and tok.tag in _HEADING_TAGS:
                return m[0]

            result = max(result, m[1])

        return result

    @classmethod
    def from_text(cls, text: str) -> MarkdownParagraph:
        """Create an instance from markdown text starting with this class's own paragraph.

        Validates that `text` starts with the paragraph triple
        (`paragraph_open`/`inline`/`paragraph_close`) declared by the
        `@markdown` decorator's metadata (`type`/`tag`). Unlike
        `MarkdownSection.from_text`, there is no `@alias`/`match_alias`
        check -- a paragraph's text is free-form content, not a title.

        If `cls` declares no nested `MarkdownStr` fields (leaf case), nothing
        else will ever retain this paragraph's text, so `_value` is set to
        the complete extent `from_text` received (the paragraph, verbatim).

        Otherwise the paragraph's own line span is stripped off `text` and
        the remainder is delegated to `MarkdownStr.from_text` (via `super()`)
        for recursive field population -- each child field recursively
        captures its own extent this same way. Since the body is therefore
        already fully represented by the nested fields, this instance's own
        `_value` only needs the paragraph's own inline text (e.g. a lead-in
        sentence) so that `__str__` can re-emit it without duplicating what
        the children already carry.
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == mdformat.text(text), "text is not in 'mdformat'."

        tokens = md.parse(text)
        assert len(tokens) >= 3, "Expected at least 3 tokens for paragraph triple"

        metadata = getattr(cls, "_metadata", {})
        expected_type = str(metadata.get("type"))
        assert isinstance(expected_type, str), type(expected_type)
        expected_tag = str(metadata.get("tag"))
        assert isinstance(expected_tag, str), type(expected_tag)

        # Validate token structure: [paragraph_open, inline, paragraph_close]
        t_open = tokens[0]
        t_mid = tokens[1]
        t_close = tokens[2]
        assert t_open.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_open.type}'."
        assert t_open.tag == expected_tag, f"{cls.__name__}: expected paragraph '{expected_tag}', got '{t_open.tag}'."
        assert t_close.nesting == -1, f"Token[2]: expected closing tag, got '{t_close.type}' '{t_close.nesting}'."

        paragraph_text = t_mid.content.strip()

        field_names = cls._get_field_names()

        if not field_names:
            instance = cls()
            instance._value = text
            return instance

        own_map = t_open.map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: paragraph_open token has no line map"
        own_lines = own_map[1]

        body_lines = text.splitlines()[own_lines:]
        body_text = mdformat.text("\n".join(body_lines)) if body_lines else ""

        instance = super().from_text(body_text)
        instance._value = paragraph_text
        return instance

    def __str__(self) -> str:
        """Return markdown representation, including this paragraph's own text.

        Leaf case (no declared nested fields): `_value` already holds the
        complete extent verbatim (the paragraph, see `from_text`), so this
        defers to `super().__str__()` (`MarkdownStr.__str__`'s leaf branch,
        which returns `_value` unchanged) exactly like any other leaf
        `MarkdownStr`.

        Composite case: `MarkdownStr.__str__` would only concatenate the
        rendered text of declared nested fields and silently drop this
        paragraph's own text, since `_value` here holds only the
        paragraph's own inline content (not the full extent, see
        `from_text`). Prepends `_value` to `super().__str__()`'s children
        output -- unlike `MarkdownSection.__str__`, there is no heading
        marker (`"#" * level`) to reconstruct, since a paragraph has none.
        """
        if not self._get_field_names():
            return super().__str__()

        body = super().__str__()
        return mdformat.text(f"{self._value}\n\n{body}")
