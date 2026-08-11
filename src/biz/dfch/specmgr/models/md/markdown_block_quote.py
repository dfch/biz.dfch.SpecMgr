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

"""A markdown block quote ("blockquote"), grouping every consecutive '>' line as one instance."""

from __future__ import annotations

import re

from pydantic import computed_field

from .markdown_str import MarkdownStr
from ._markdown import format_text, md
from .markdown import markdown

#: Matches a block quote marker (">" or "> ") at the start of a line.
_QUOTE_MARKER_RE = re.compile(r"^>[ ]?")


def _dedent_quote_lines(text: str) -> str:
    """Strip the leading `">"`/`"> "` marker from every line of `text`.

    Every line of a block quote's extent (after `format_text` normalization)
    is guaranteed to start with `">"` (a bare `">"` for a blank continuation
    line, `"> "` otherwise) -- this is the inverse of `_indent_quote_lines`.

    Args:
        text: Markdown source, every line of which starts with a block
            quote marker.

    Returns:
        `text` with each line's marker removed, joined back with `"\\n"`.
    """
    assert isinstance(text, str), type(text)

    lines = text.splitlines()
    dedented: list[str] = []
    for line in lines:
        assert line == ">" or line.startswith(">"), f"expected a block quote marker line, got {line!r}"
        dedented.append(_QUOTE_MARKER_RE.sub("", line, count=1))

    result = "\n".join(dedented)

    return result


def _indent_quote_lines(text: str) -> str:
    """Prepend a block quote marker (`"> "`, or bare `">"` for a blank line) to every line of `text`.

    Inverse of `_dedent_quote_lines`.

    Args:
        text: Markdown source with no block quote markers of its own.

    Returns:
        `text` with each line prefixed by `"> "` (non-blank line) or `">"`
        (blank line), joined back with `"\\n"`.
    """
    assert isinstance(text, str), type(text)

    lines = text.splitlines()
    indented = [f"> {line}" if line else ">" for line in lines]
    result = "\n".join(indented)

    return result


@markdown(type="blockquote_open", tag="blockquote")
class MarkdownBlockQuote(MarkdownStr):
    """A markdown block quote ("blockquote"), the non-heading, non-leaf-only sibling of `MarkdownSection`.

    markdown-it already groups every *consecutive* `">"` line -- including
    internal blank `">"` continuation lines (a "loose" quote with several
    paragraphs) and any more deeply nested quote (`"> > ..."`) -- into a
    single `blockquote_open`/`blockquote_close` pair whose own `.map`
    already spans the whole thing; two quotes separated by a real blank
    line (no `">"` at all) are two separate pairs. So, unlike
    `MarkdownSection`/`MarkdownParagraph`, `get_extent` needs no
    stop-condition scan -- `tokens[0].map[1]` is already correct, the same
    situation as `MarkdownListItem`/`MarkdownCodeBlock`. There is no
    `@alias` enforcement, same as `MarkdownParagraph`/`MarkdownListItem` --
    quoted content is free-form, not a title.

    Unlike `MarkdownListItem` (which always assumes a leading paragraph), a
    quote's content can start with *any* block type (a heading, a list, a
    nested quote, ...), so `from_text` validates only the `blockquote_open`
    token itself (`type`/`tag`/`nesting == 1`), not anything about what
    follows it.

    Deliberately **not leaf-only** (unlike `MarkdownCodeBlock`) -- a
    subclass may declare nested fields (e.g. `emphasis`/`strong` as future,
    separate typed objects), same composite capability as
    `MarkdownParagraph`/`MarkdownListItem`. But a quote has no separate
    "own text" line the way a heading/paragraph/list item does -- *every*
    line of its extent carries the `">"` marker, and the marker is
    unrelated to what block type each line's content actually is. So the
    composite split works differently:

    - Leaf (no declared fields): `_value` holds the complete extent
      verbatim, marker included on every line -- nothing else will ever
      retain it, exactly like any other leaf `MarkdownStr` subclass.
    - Composite (a subclass declares fields): the marker is stripped from
      *every* line of the extent (`_dedent_quote_lines`), not just a
      leading line, and the fully-dedented result -- re-normalized with
      `format_text` -- is delegated whole to `super().from_text()`. Since
      the entire extent is body this way, there is no "own text" left for
      this instance to keep, so `_value` is set to `""`. `__str__`
      re-applies the marker to every line of `super().__str__()`'s output
      (`_indent_quote_lines`), rather than reconstructing a single heading
      line (`MarkdownSection`) or prepending a marker-free lead sentence
      (`MarkdownParagraph`).
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this block quote, as a line count.

        There is only an extent at all if the *first* token parsed from
        `text` is a `"blockquote_open"`/`"blockquote"` token matching this
        class's own `@markdown` metadata; otherwise this returns `0`, same
        as the base class's "no extent" case.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` does not start with a block quote (no extent).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by
                the quote's own `.map`, i.e. every consecutive `">"` line,
                including any more deeply nested quote.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), "text is not in 'mdformat'."

        own_type = cls._metadata.get("type")
        own_tag = cls._metadata.get("tag")
        assert own_type == "blockquote_open" and own_tag == "blockquote", (
            f"{cls.__name__}: expected type='blockquote_open', tag='blockquote', got type={own_type!r}, tag={own_tag!r}"
        )

        tokens = md.parse(text)

        if not tokens or tokens[0].type != own_type or tokens[0].tag != own_tag:
            return 0

        own_map = tokens[0].map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: blockquote_open token has no line map"

        result: int = own_map[1]

        return result

    @classmethod
    def from_text(cls, text: str) -> MarkdownBlockQuote:
        """Create an instance from markdown text starting with a block quote.

        Validates only the `blockquote_open` token itself (`type`/`tag`
        from the `@markdown` decorator's metadata, and `nesting == 1`) --
        unlike `MarkdownListItem`, nothing is assumed about what block type
        follows it.

        If `cls` declares no nested `MarkdownStr` fields (leaf case),
        nothing else will ever retain this quote's text, so `_value` is set
        to the complete extent `from_text` received (every line, marker
        included, verbatim).

        Otherwise the marker is stripped from *every* line of `text`
        (`_dedent_quote_lines`) -- not just a leading line, since a quote
        has no separate "own text" the way a heading/paragraph does -- and
        the fully-dedented, re-normalized result is delegated whole to
        `MarkdownStr.from_text` (via `super()`) for the declared fields'
        population. Since the body is therefore already fully represented
        by the nested fields, `_value` is set to `""`.

        Args:
            text: Markdown source, pre-formatted with `mdformat`, starting
                with this class's own block quote.

        Returns:
            A new instance, populated per the leaf/composite case above.
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == format_text(text), "text is not in 'mdformat'."

        tokens = md.parse(text)
        assert tokens, "Expected at least one token for a block quote"

        metadata = getattr(cls, "_metadata", {})
        expected_type = str(metadata.get("type"))
        assert isinstance(expected_type, str), type(expected_type)
        expected_tag = str(metadata.get("tag"))
        assert isinstance(expected_tag, str), type(expected_tag)

        t_open = tokens[0]
        assert t_open.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_open.type}'."
        assert t_open.tag == expected_tag, f"{cls.__name__}: expected tag '{expected_tag}', got '{t_open.tag}'."
        assert t_open.nesting == 1, (
            f"{cls.__name__}: expected an opening block quote token, got nesting={t_open.nesting}"
        )

        field_names = cls._get_field_names()

        if not field_names:
            instance = cls()
            instance._value = text
            return instance

        dedented_text = _dedent_quote_lines(text)
        body_text = format_text(dedented_text) if dedented_text else ""

        instance = super().from_text(body_text)
        instance._value = ""

        return instance

    def __str__(self) -> str:
        """Return markdown representation, including this quote's own markers.

        Leaf case (no declared nested fields): `_value` already holds the
        complete extent verbatim (marker included on every line, see
        `from_text`), so this defers to `super().__str__()`
        (`MarkdownStr.__str__`'s leaf branch, which returns `_value`
        unchanged).

        Composite case: re-applies the `">"`/`"> "` marker to every line of
        `super().__str__()`'s output (`_indent_quote_lines`) -- unlike
        `MarkdownSection`/`MarkdownParagraph`, there is no single heading
        line or lead sentence to reconstruct; the marker applies uniformly
        to the whole rendered body.
        """
        if not self._get_field_names():
            return super().__str__()

        body = super().__str__()
        indented = _indent_quote_lines(body)

        return format_text(indented)

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Computed property returning this quote's content without its markers.

        Composite instances (declared fields): `_value` is `""` (see
        `from_text`), since the whole body is already delegated to the
        nested fields, so this simply returns `super().__str__()`
        (`MarkdownStr.__str__`) -- exactly the same marker-free markdown
        that was fed to `super().from_text()`, re-derived from the nested
        fields' own rendering.

        Leaf instances (no declared fields): dedents `_value` the same way
        `from_text` would before delegating for a composite instance.

        Nested markdown syntax (e.g. `*emphasis*`, a nested `"> "` quote)
        is preserved as-is, not rendered down to plain text -- mirroring
        `MarkdownSection.name`/`MarkdownListItem.text`'s "own source text,
        markers stripped" semantics, just applied line-by-line instead of
        to a single inline token.

        Returns:
            The quote's markdown content with every line's marker
            stripped, or an empty string if `_value` is unset (e.g. before
            `from_text` runs).

        Example:
            >>> quote = MarkdownBlockQuote.from_text("> This is a quote.\\n")
            >>> quote.text
            'This is a quote.'
        """
        if self._get_field_names():
            return super().__str__()

        if not self._value:
            return ""

        result = _dedent_quote_lines(self._value)

        return result
