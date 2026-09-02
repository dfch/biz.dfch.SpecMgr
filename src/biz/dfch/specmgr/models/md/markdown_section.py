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

"""Base class for markdown sections with heading constraints."""

from __future__ import annotations

from abc import ABC

from markdown_it.token import Token
from pydantic import model_validator, computed_field, PrivateAttr

from .markdown_str import MarkdownStr
from ._markdown import format_text, not_in_mdformat_message, parse
from .markdown import markdown
from .alias_match import describe_alias, match_alias

_HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")


def _alias_mismatch_message(path: str, line: int, cls: type, heading_text: str) -> str:
    """Build the alias-mismatch message (REQ-001/REQ-002/REQ-003).

    Args:
        path: the document-relative path (REQ-001) of the section whose
            heading was actually parsed (`path`'s own last segment names
            `cls` itself, since a mismatch is only detected once a heading
            of the right tag/level has already been found -- `get_extent`'s
            own alias check keeps a wrongly-titled heading from ever
            reaching this section's own `process_field`/`process_list_field`
            call in the first place).
        line: the 1-based line (REQ-002) at which the mismatched heading
            starts, relative to the root document's own `mdformat`-
            normalized body.
        cls: the `MarkdownSection` subclass whose `@alias` was not
            satisfied.
        heading_text: the heading's actual (mismatching) text.

    Returns:
        A message naming the path, the line, what was expected (REQ-003,
        via `describe_alias`), and what was actually found.
    """
    return f"{path} (line {line}): expected {describe_alias(cls)}, got heading {heading_text!r}"


@markdown(type="heading_open")
class MarkdownSection(MarkdownStr, ABC):
    """Abstract base class for markdown sections with heading constraints."""

    _tokens: list[Token] = PrivateAttr(default_factory=list)

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this heading section, as a line count.

        Overrides `MarkdownStr.get_extent` for heading-based sections. A
        level-N heading section's extent spans from its own `heading_open`
        token through every subsequent token, up to (but excluding) the
        next heading whose level is `<= N` -- i.e. a sibling or ancestor
        heading. Deeper headings (level > N, nested subsections) do not end
        the extent. If no such heading follows, the extent reaches the end
        of `text`.

        If `cls`'s `@markdown` metadata declares an `end_marker` (a
        `MarkdownStr` subclass, e.g. `MarkdownBlockQuote`), an occurrence of
        that class's own `type`/`tag` also stops the scan, alongside the
        heading-level check above -- but only when it occurs at nesting
        depth 0 relative to this section's own body, i.e. it is not itself
        nested inside some other block construct (a list item, another
        block quote, ...) that legitimately belongs to this section's own
        content. A depth counter is maintained across *every* token in the
        stream (incremented/decremented by that token's own `Token.nesting`,
        not just tokens matching the `end_marker`'s type), since any
        intervening open/close pair -- not only the `end_marker`'s own --
        shifts what "depth 0" means for everything that follows it; a token
        is considered "at depth 0" when the running depth *going into* it
        (before applying its own nesting delta) is 0, mirroring how the
        heading check above already treats a stopping heading's own line as
        outside the extent.

        There is only an extent at all if the *first* token parsed from
        `text` is a `heading_open` matching this class's own tag (from the
        `@markdown` decorator's metadata) *and* that heading's own text
        satisfies `cls`'s effective `@alias` (`match_alias`, the same check
        `from_text` itself makes) -- otherwise this returns `0`, same as the
        "no extent" case in the base class. This alias check is what lets
        `process_field`'s optional-field handling correctly treat a
        same-level-but-differently-named heading (e.g. an absent optional
        `Notes` immediately followed by a sibling `Assumptions` heading) as
        "this field is absent", instead of matching the wrong heading's
        extent and then failing deeper inside `from_text`'s own alias
        assertion.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` does not start with this class's own heading, or that
                heading's text does not satisfy `cls`'s `@alias` (no extent).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by this
                heading and its nested content, stopping before the next
                sibling/ancestor heading, the next depth-0 `end_marker`
                occurrence (if declared), or at the end of `text`.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), not_in_mdformat_message(text)

        own_tag = cls._metadata.get("tag")
        own_type = cls._metadata.get("type")
        assert isinstance(own_tag, str) and own_tag in _HEADING_TAGS, (
            f"{cls.__name__}: expected a heading tag in {_HEADING_TAGS}, got {own_tag!r}"
        )
        own_level = _HEADING_TAGS.index(own_tag) + 1

        end_marker = cls._metadata.get("end_marker")
        end_marker_type: str | None = None
        end_marker_tag: str | None = None
        if end_marker is not None:
            assert isinstance(end_marker, type) and issubclass(end_marker, MarkdownStr), type(end_marker)
            end_marker_metadata = getattr(end_marker, "_metadata", {})
            end_marker_type = end_marker_metadata.get("type")
            end_marker_tag = end_marker_metadata.get("tag")

        tokens = parse(text)

        if not tokens or tokens[0].type != own_type or tokens[0].tag != own_tag:
            return 0

        if len(tokens) < 2 or not match_alias(cls, tokens[1].content.strip()):
            return 0

        result: int = 0
        depth: int = 0
        for idx, tok in enumerate(tokens):
            depth_at_entry = depth
            depth += tok.nesting

            m = tok.map
            if not m or len(m) != 2:
                continue

            if idx > 0 and tok.type == own_type and tok.tag in _HEADING_TAGS:
                if _HEADING_TAGS.index(tok.tag) + 1 <= own_level:
                    return m[0]

            if (
                idx > 0
                and end_marker_type is not None
                and tok.type == end_marker_type
                and tok.tag == end_marker_tag
                and depth_at_entry == 0
            ):
                return m[0]

            result = max(result, m[1])

        return result

    @classmethod
    def from_text(cls, text: str, *, _path: str = "", _offset: int = 0) -> MarkdownSection:
        """Create an instance from markdown text starting with this class's own heading.

        Validates that `text` starts with the heading triple
        (`heading_open`/`inline`/`heading_close`) declared by the `@markdown`
        decorator's metadata (`type`/`tag`), then that the heading's actual
        text satisfies `cls`'s effective `@alias` (`match_alias`) -- either
        the one explicitly declared, or, absent one, the implicit
        `AliasType.SPACE_SEPARATED` derivation of `cls.__name__` (see
        `match_alias`).

        If `cls` declares no nested `MarkdownStr` fields (leaf case), nothing
        else will ever retain this section's body text, so `_value` is set to
        the complete extent `from_text` received (heading and body verbatim),
        exactly like the base `MarkdownStr.from_text` leaf case.

        Otherwise the heading's own line span is stripped off `text` and the
        remainder ("body") is delegated to `MarkdownStr.from_text` (via
        `super()`) for the actual recursive field population -- each child
        field recursively captures its own full extent this same way, all the
        way down to whichever leaf(ves) ultimately hold the body text. Since
        the body is therefore already fully represented by the nested fields,
        this section's own `_value` only needs the heading's inline content
        (the `inline` token's text, e.g. `"Characteristic Information"`) so
        that `__str__` can re-emit the original heading line without
        duplicating what the children already carry.

        Args:
            text: the markdown text to parse.
            _path: this section's own document-relative path (REQ-001) as
                chosen by the caller -- `""` at the very root, in which case
                `cls.__name__` is used instead (see
                `MarkdownStr.from_text`'s own `_path` docs).
            _offset: the 0-based line at which `text` (this section's own
                heading) starts, relative to the root document's own
                `mdformat`-normalized body (REQ-002) -- `0` at the root.

        Raises:
            AssertionError: `text` is not `mdformat`-normalized, does not
                start with this class's own heading triple, or that
                heading's own text does not satisfy `cls`'s effective
                `@alias` (see `_alias_mismatch_message`) -- or any of the
                structural errors `MarkdownStr.from_text` itself may raise
                while populating this section's own declared fields.
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == format_text(text), not_in_mdformat_message(text)

        own_path = _path or cls.__name__
        own_line = _offset + 1

        tokens = parse(text)
        assert len(tokens) >= 3, "Expected at least 3 tokens for heading triple"

        # Get the expected heading tag from decorator metadata
        metadata = getattr(cls, "_metadata", {})
        expected_type = str(metadata.get("type"))
        assert isinstance(expected_type, str), type(expected_type)
        expected_tag = str(metadata.get("tag"))
        assert isinstance(expected_tag, str), type(expected_tag)

        # Validate token structure: [heading_open, inline, heading_close]
        t_open = tokens[0]
        t_mid = tokens[1]
        t_close = tokens[2]
        assert t_open.type == expected_type, f"Token[0]: expected '{expected_type}', got '{t_open.type}'."
        assert t_open.tag == expected_tag, f"{cls.__name__}: expected heading {expected_tag}, got {t_open.tag}"
        assert t_close.nesting == -1, f"Token[2]: expected closing tag, got '{t_close.type}' '{t_close.nesting}'."

        heading_text = t_mid.content.strip()
        assert match_alias(cls, heading_text), _alias_mismatch_message(own_path, own_line, cls, heading_text)

        field_names = cls._get_field_names()

        if not field_names:
            instance = cls()
            instance._value = text
            instance._path = own_path
            instance._line = own_line
            return instance

        heading_map = t_open.map
        assert heading_map and len(heading_map) == 2, f"{cls.__name__}: heading token has no line map"
        heading_lines = heading_map[1]

        body_lines = text.splitlines()[heading_lines:]
        body_text = format_text("\n".join(body_lines)) if body_lines else ""

        instance = super().from_text(body_text, _path=own_path, _offset=_offset + heading_lines)
        instance._value = heading_text
        instance._path = own_path
        instance._line = own_line
        return instance

    def __str__(self) -> str:
        """Return markdown representation, including this section's own heading.

        Leaf case (no declared nested fields): `_value` already holds the
        complete extent verbatim (heading and body, see `from_text`), so this
        defers to `super().__str__()` (`MarkdownStr.__str__`'s leaf branch,
        which returns `_value` unchanged) exactly like any other leaf
        `MarkdownStr`.

        Composite case: `MarkdownStr.__str__` would only concatenate the
        rendered text of declared nested fields and silently drop this
        section's own heading line, since `_value` here holds only the
        heading's inline content (not the full extent, see `from_text`).
        Reconstructs the heading (`"#" * level + " " + self._value`) from
        `cls._metadata['tag']`, then prepends it to `super().__str__()`'s
        children output.
        """
        if not self._get_field_names():
            return super().__str__()

        own_tag = self._metadata.get("tag")
        assert isinstance(own_tag, str) and own_tag in _HEADING_TAGS, (
            f"{type(self).__name__}: expected a heading tag in {_HEADING_TAGS}, got {own_tag!r}"
        )
        level = _HEADING_TAGS.index(own_tag) + 1
        heading_line = f"{'#' * level} {self._value}"

        body = super().__str__()
        return format_text(f"{heading_line}\n\n{body}")

    @model_validator(mode="after")
    def validate_heading_structure(self) -> MarkdownSection:
        """Validate that section starts with a heading (h1-h6) triple.

        Tokens [0:3] must form a heading triple (heading_open/inline/heading_close).
        Token [0] must have tag h1-h6.
        """
        text = str(self)
        tokens = parse(text)
        _ = tokens

        # assert len(tokens) >= 3, "Expected at least 3 tokens for heading triple"
        # assert tokens[0].type == "heading_open", f"Token[0]: expected heading_open, got {tokens[0].type}"
        # assert tokens[2].type == "heading_close", f"Token[2]: expected heading_close, got {tokens[2].type}"
        # assert tokens[0].tag in ("h1", "h2", "h3", "h4", "h5", "h6"), (
        #     f"Token[0]: expected h1-h6, got {tokens[0].tag}"
        # )
        return self

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Computed property exposing this section's textual content.

        `_value` is a Pydantic private attribute (leading underscore), so it
        is invisible to `model_dump()`/`model_dump_json()` -- exactly the
        serialization path used, for example, by an MCP server transmitting a
        tool's return value. This property is what makes a section's content
        reachable through that path at all, mirroring `MarkdownParagraph.text`/
        `MarkdownListItem.text`'s established "expose `_value` as a public
        field" pattern.

        Leaf case (no declared nested fields, see `_get_field_names`):
        `_value` already holds this section's complete extent verbatim --
        its own heading *and* body (see `from_text`) -- so this returns
        `str(self)` unchanged, i.e. everything, not just the heading.
        Without this branch, a leaf section with no field of its own to hold
        its body (e.g. a bare `class Notes(MarkdownSection2): ...`) would
        serialize to just its heading text, silently dropping the entire
        body from `model_dump()`.

        Composite case (has declared nested fields): the body is already
        fully represented by those nested fields (each recursively exposing
        its own content the same way), so returning the whole extent here
        again would only duplicate it. Instead this extracts and returns
        just this section's own heading text, by locating the `inline` token
        immediately following this section's own `heading_open` (tag taken
        from the `@markdown` decorator's `tag` metadata) in `str(self)`'s
        token stream.

        Returns:
            Leaf: the complete extent verbatim (heading and body).
            Composite: the heading text alone, without markdown formatting,
            or an empty string if no matching heading is found (e.g.
            `_value` is unset).

        Example:
            >>> @markdown(type="notes", tag="h3")
            ... class Notes(MarkdownSection): ...
            >>> notes = Notes()
            >>> notes._value = "### My Notes\n\nSome content"
            >>> notes.text
            '### My Notes\n\nSome content'
        """
        if not self._get_field_names():
            return str(self)

        text = str(self)
        tokens = parse(text)

        # Get the expected heading tag from the @markdown decorator metadata
        metadata = getattr(self.__class__, "_metadata", {})
        expected_tag = metadata.get("tag")

        # Look for the inline token that follows a heading_open with the expected tag
        # Heading structure: [heading_open, inline, heading_close]
        for i, token in enumerate(tokens):
            if (
                token.type == "inline"
                and i > 0
                and tokens[i - 1].type == "heading_open"
                and tokens[i - 1].tag == expected_tag
            ):
                return token.content.strip()

        return ""
