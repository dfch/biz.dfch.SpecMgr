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

"""A leaf-only fenced ("```") code block, never subclassable with declared fields."""

from __future__ import annotations

from pydantic import computed_field

from .markdown_str import MarkdownStr
from ._markdown import format_text, not_in_mdformat_message, parse
from .markdown import markdown


@markdown(type="fence", tag="code")
class MarkdownCodeBlock(MarkdownStr):
    """A fenced ("```") code block ("fence"/"code").

    Deliberately **leaf-only** -- unlike `MarkdownParagraph`/`MarkdownListItem`,
    there is no composite case at all: nothing can ever be nested inside a
    code block's content, since that content is opaque code, not further
    markdown. `get_extent`/`from_text` both `assert not cls._get_field_names()`
    to enforce this actively (fail loudly if ever subclassed with a declared
    field), rather than merely documenting it as a convention.

    Only handles a *fenced* block (`` ``` ``), never an indented (4-space)
    one -- markdown-it tokenizes those as a different token type
    (`"code_block"`, not `"fence"`), so an indented block simply never
    matches `get_extent`/`from_text` here. `~~~`-fenced blocks are not
    special-cased either: `mdformat.text()` already normalizes `~~~` to
    `` ``` `` before this class ever sees the text (both `get_extent` and
    `from_text` assert `text == format_text(text)`), so by the time either
    method runs, only `` ``` `` fences remain. The language/info string after
    the opening fence (e.g. ` ```python `) is not validated or restricted in
    any way -- any info string, or none at all, matches.

    Unlike a heading/paragraph/list item, markdown-it tokenizes a fenced
    block as a single self-closing token (`nesting == 0`), not an
    open/inline/close triple -- its own `.map` already spans the fence
    markers and content exactly, so no stop-condition scan is needed.

    `_value` holds the block's complete extent verbatim: both fence marker
    lines (with any info string) and the code content, exactly like any
    other leaf `MarkdownStr`/`MarkdownSection`/`MarkdownParagraph`/
    `MarkdownListItem` -- nothing else will ever retain this text. No
    `__str__` override is needed: the inherited `MarkdownStr.__str__` already
    returns `_value` unchanged whenever there are no declared fields, which
    is always true here.
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this fenced code block, as a line count.

        There is only an extent at all if the *first* token parsed from
        `text` is a `"fence"`/`"code"` token matching this class's own
        `@markdown` metadata; otherwise this returns `0`, same as the base
        class's "no extent" case.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` does not start with a fenced code block (no extent).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by the
                fence's own `.map`, i.e. both fence marker lines and the code
                content.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), not_in_mdformat_message(text)
        assert not cls._get_field_names(), f"{cls.__name__}: leaf-only, must not declare any nested fields"

        own_type = cls._metadata.get("type")
        own_tag = cls._metadata.get("tag")
        assert own_type == "fence" and own_tag == "code", (
            f"{cls.__name__}: expected type='fence', tag='code', got type={own_type!r}, tag={own_tag!r}"
        )

        tokens = parse(text)

        if not tokens or tokens[0].type != own_type or tokens[0].tag != own_tag:
            return 0

        own_map = tokens[0].map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: fence token has no line map"

        result: int = own_map[1]

        return result

    @classmethod
    def from_text(cls, text: str, *, _path: str = "", _offset: int = 0) -> MarkdownCodeBlock:
        """Create an instance from markdown text starting with a fenced code block.

        Validates that `text` starts with a single self-closing token
        (`nesting == 0`) matching the `type`/`tag` declared by the
        `@markdown` decorator's metadata. Since this class is leaf-only,
        `_value` is unconditionally set to the complete extent `from_text`
        received (both fence marker lines and the code content, verbatim) --
        there is no composite branch to delegate to, unlike
        `MarkdownParagraph`/`MarkdownSection`/`MarkdownListItem`.

        Args:
            text: Markdown source, pre-formatted with `mdformat`, starting
                with this class's own fenced code block.
            _path: this block's own document-relative path (REQ-001) as
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
        assert tokens, "Expected at least one token for a fenced code block"

        metadata = getattr(cls, "_metadata", {})
        expected_type = str(metadata.get("type"))
        assert isinstance(expected_type, str), type(expected_type)
        expected_tag = str(metadata.get("tag"))
        assert isinstance(expected_tag, str), type(expected_tag)

        t_fence = tokens[0]
        assert t_fence.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_fence.type}'."
        assert t_fence.tag == expected_tag, f"{cls.__name__}: expected tag '{expected_tag}', got '{t_fence.tag}'."
        assert t_fence.nesting == 0, (
            f"{cls.__name__}: expected a self-closing fence token, got nesting={t_fence.nesting}"
        )

        instance = cls()
        instance._value = text
        instance._path = _path or cls.__name__
        instance._line = _offset + 1

        return instance

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Computed property that extracts this code block's inner content only.

        Re-parses `_value` (which always starts with this block's own fence,
        see `from_text`) and returns the fence token's own `.content`
        unchanged -- fence marker lines and any info string are excluded,
        but the trailing `"\\n"` markdown-it always includes on a non-empty
        fence's `.content` is kept as-is, since `mdformat` re-normalizes on
        render anyway.

        Returns:
            The fenced block's code content, or an empty string if `_value`
            is unset (e.g. before `from_text` runs) or holds no matching
            fence token.

        Example:
            >>> block = MarkdownCodeBlock.from_text("```python\\nprint(1)\\n```\\n")
            >>> block.text
            'print(1)\\n'
        """
        tokens = parse(self._value)

        metadata = getattr(type(self), "_metadata", {})
        expected_type = metadata.get("type")
        expected_tag = metadata.get("tag")

        for token in tokens:
            if token.type == expected_type and token.tag == expected_tag:
                return token.content

        return ""
