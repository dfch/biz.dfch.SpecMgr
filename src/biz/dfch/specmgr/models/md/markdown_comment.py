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

"""A leaf-only HTML comment block (`<!-- ... -->`), never subclassable with declared fields."""

from __future__ import annotations

from pydantic import computed_field

from .markdown_str import MarkdownStr
from ._markdown import format_text, not_in_mdformat_message, parse
from .markdown import markdown


@markdown(type="html_block", tag="")
class MarkdownComment(MarkdownStr):
    """A standalone HTML comment block (`"html_block"`, e.g. `<!-- some note -->`).

    Deliberately leaf-only, like `MarkdownCodeBlock`. Declare an optional
    `comment: MarkdownComment | None` field on any `MarkdownStr` subclass to
    let a value be preceded by such an explanatory comment without it
    breaking that class's own structural field matching. See `get_extent`/
    `from_text`/`text` for the full mechanics.
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this comment block, as a line count.

        There is only an extent at all if the *first* token parsed from
        `text` is an `"html_block"` token whose content starts with
        `"<!--"`; otherwise this returns `0`, same as the base class's "no
        extent" case.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` does not start with a matching comment block (no extent).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by the
                comment block's own `.map`.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), not_in_mdformat_message(text)
        assert not cls._get_field_names(), f"{cls.__name__}: leaf-only, must not declare any nested fields"

        own_type = cls._metadata.get("type")
        own_tag = cls._metadata.get("tag")
        assert own_type == "html_block" and own_tag == "", (
            f"{cls.__name__}: expected type='html_block', tag='', got type={own_type!r}, tag={own_tag!r}"
        )

        tokens = parse(text)

        if not tokens or tokens[0].type != own_type or tokens[0].tag != own_tag:
            return 0

        if not tokens[0].content.startswith("<!--"):
            return 0

        own_map = tokens[0].map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: html_block token has no line map"

        result: int = own_map[1]

        return result

    @classmethod
    def from_text(cls, text: str, *, _path: str = "", _offset: int = 0) -> MarkdownComment:
        """Create an instance from markdown text starting with a comment block.

        Validates that `text` starts with a single self-closing `"html_block"`
        token whose content starts with `"<!--"`. Since this class is
        leaf-only, `_value` is unconditionally set to the complete extent
        `from_text` received (the comment block, verbatim).

        Args:
            text: Markdown source, pre-formatted with `mdformat`, starting
                with this class's own comment block.
            _path: this comment's own document-relative path (REQ-001) as
                chosen by the caller -- `""` at the very root, in which case
                `cls.__name__` is used instead.
            _offset: the 0-based line at which `text` starts, relative to
                the root document's own `mdformat`-normalized body
                (REQ-002) -- `0` at the root.

        Returns:
            A new instance with `_value` set to `text` verbatim.
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == format_text(text), not_in_mdformat_message(text)
        assert not cls._get_field_names(), f"{cls.__name__}: leaf-only, must not declare any nested fields"

        tokens = parse(text)
        assert tokens, "Expected at least one token for a comment block"

        metadata = getattr(cls, "_metadata", {})
        expected_type = str(metadata.get("type"))
        assert isinstance(expected_type, str), type(expected_type)
        expected_tag = str(metadata.get("tag"))
        assert isinstance(expected_tag, str), type(expected_tag)

        t_html_block = tokens[0]
        assert t_html_block.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_html_block.type}'."
        assert t_html_block.tag == expected_tag, (
            f"{cls.__name__}: expected tag '{expected_tag}', got '{t_html_block.tag}'."
        )
        assert t_html_block.nesting == 0, (
            f"{cls.__name__}: expected a self-closing html_block token, got nesting={t_html_block.nesting}"
        )
        assert t_html_block.content.startswith("<!--"), (
            f"{cls.__name__}: expected an HTML comment, got {t_html_block.content!r}"
        )

        instance = cls()
        instance._value = text
        instance._path = _path or cls.__name__
        instance._line = _offset + 1

        return instance

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Computed property that extracts this comment block's raw content.

        Re-parses `_value` (which always starts with this block's own
        `html_block` token, see `from_text`) and returns that token's own
        `.content` unchanged, including the `<!--`/`-->` delimiters.

        Returns:
            The comment block's raw content (e.g. `"<!-- note -->\\n"`), or an
            empty string if `_value` is unset (e.g. before `from_text` runs)
            or holds no matching token.

        Example:
            >>> comment = MarkdownComment.from_text("<!-- a note -->\\n")
            >>> comment.text
            '<!-- a note -->\\n'
        """
        tokens = parse(self._value)

        metadata = getattr(type(self), "_metadata", {})
        expected_type = metadata.get("type")
        expected_tag = metadata.get("tag")

        for token in tokens:
            if token.type == expected_type and token.tag == expected_tag:
                return token.content

        return ""
