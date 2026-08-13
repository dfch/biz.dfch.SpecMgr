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

"""Parse markdown into tokens using shared MarkdownIt instance.

Note: `md.parse(text, env)` accepts optional `env: dict` (EnvType) to pass data
between parsing rules and collect metadata like reference definitions.
"""

from __future__ import annotations

import types
import typing
from typing import Any
from pydantic import BaseModel
from ._markdown import format_text, parse


def _snippet(text: str, max_lines: int = 5, max_chars: int = 300) -> str:
    """Return a truncated snippet of text for error messages.

    Args:
        text: the markdown text to excerpt.
        max_lines: maximum number of lines to include before truncating.
        max_chars: maximum number of characters to include before truncating.

    Returns:
        A snippet of up to `max_lines` lines and `max_chars` characters,
        with a "... (truncated)" suffix if either limit was exceeded.
    """
    lines = text.splitlines()
    truncated_lines = lines[:max_lines]
    snippet = "\n".join(truncated_lines)

    if len(lines) > max_lines or len(snippet) > max_chars:
        snippet = snippet[:max_chars]
        return f"{snippet}... (truncated)"
    return snippet


class MarkdownStr(BaseModel):
    """Markdown text parsed into token stream."""

    _value: str = ""

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of the markdown token stream parsed from `text`, as a line count.

        The result is a count, not a 0-based line index, matching Python's own
        slicing/`len()`/`range()` convention: `text.splitlines()[:get_extent(text)]`
        yields exactly the lines covered by the extent. This also keeps `0`
        unambiguous as "no extent" -- a single-line extent returns `1`, never
        colliding with the no-extent sentinel the way a 0-based last-line-index
        would.

        NOTE that `text` must already be formatted with `mdformat`.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: no extend found.
            int > 0: the number of lines, from the start of `text`, covered by
                the extent. Equivalent to the highest `token.map[1]` across all
                tokens with a 2-element `.map` (`token.map[1]` is already the
                exclusive-end line bound, so it doubles as a line count since
                every extent starts at line 0).
        """

        assert isinstance(text, str), type(text)
        assert text == format_text(text), "text is not in 'mdformat'."

        tokens = parse(text)

        result: int = 0
        for tok in tokens:
            m = tok.map
            if not m or len(m) != 2:
                continue
            result = max(result, m[1])

        return result

    @classmethod
    def _unwrap_optional(cls, annotation: Any) -> tuple[Any, bool]:
        """Return `(inner_type, is_optional)` for a field's raw annotation.

        Recognizes `Optional[X]` and PEP 604 `X | None` -- both of which are
        `typing.Union[X, None]` under the hood -- with exactly one non-`None`
        member, and unwraps them to `(X, True)`. Any other annotation
        (including plain `X`, or a `Union` with more than one non-`None`
        member) is returned unchanged as `(annotation, False)`.

        Args:
            annotation: a field's raw `model_fields[...].annotation`.

        Returns:
            `(inner_type, is_optional)`.
        """
        origin = typing.get_origin(annotation)
        if origin is typing.Union or origin is types.UnionType:
            args = typing.get_args(annotation)
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1 and type(None) in args:
                return non_none[0], True

        return annotation, False

    @classmethod
    def _unwrap_list(cls, annotation: Any) -> tuple[Any, bool]:
        """Return `(item_type, is_list)` for a field's (already `Optional`-unwrapped) annotation.

        Recognizes plain `list[X]` (`typing.get_origin(annotation) is list`)
        with exactly one type argument, and unwraps it to `(X, True)`. Any
        other annotation (including a bare `X`, or `tuple[X, ...]`/
        `Sequence[X]`, deliberately not supported) is returned unchanged as
        `(annotation, False)`.

        Callers apply this *after* `_unwrap_optional`, so `list[X] | None`
        first unwraps to `(list[X], True)` via `_unwrap_optional`, then to
        `(X, True)` here -- i.e. "optional" and "list" are independent axes,
        checked one after the other.

        Args:
            annotation: a field's annotation, already passed through
                `_unwrap_optional`.

        Returns:
            `(item_type, is_list)`.
        """
        origin = typing.get_origin(annotation)
        if origin is list:
            args = typing.get_args(annotation)
            if len(args) == 1:
                return args[0], True

        return annotation, False

    @classmethod
    def process_field(
        cls, name: str, type_: type[MarkdownStr], text: str, *, optional: bool = False
    ) -> tuple[int, MarkdownStr | None]:
        """Resolve one nested field's extent and parsed instance from `text`.

        Args:
            name: the field's attribute name (used only for error messages).
            type_: the field's declared `MarkdownStr` subclass.
            text: the not-yet-consumed remainder of the parent's markdown text;
                the field is assumed to start at the very first line of `text`.
            optional: whether the field is declared `Optional[type_]`/
                `type_ | None`. When `True` and `type_.get_extent(text)` finds
                no extent, this is not an error: the field is simply absent
                from `text` (e.g. an optional section whose heading doesn't
                appear next), and `(0, None)` is returned so the caller can
                move on to the next field without consuming any of `text`.

        Returns:
            A `(extent, instance)` pair: `extent` is the number of leading
            lines of `text` this field consumes (see `MarkdownStr.get_extent`),
            and `instance` is the field's value, parsed via
            `type_.from_text` on exactly those `extent` leading lines -- or
            `(0, None)` for an absent optional field (see `optional` above).
        """
        assert isinstance(name, str), type(name)
        assert isinstance(type_, type) and issubclass(type_, MarkdownStr), type_
        assert isinstance(text, str), type(text)

        extent = type_.get_extent(text)
        if optional and extent == 0:
            result: tuple[int, MarkdownStr | None] = (0, None)
            return result

        assert extent > 0, (
            f"{cls.__name__}.{name}: expected {type_.__name__}, found no match; "
            f"remaining text ({len(text.splitlines())} line(s)) starts with:\n{_snippet(text)}"
        )

        lines = text.splitlines()
        field_text = format_text("\n".join(lines[:extent]))
        instance = type_.from_text(field_text)

        result = (extent, instance)

        return result

    @classmethod
    def process_list_field(
        cls, name: str, item_type: type[MarkdownStr], text: str, *, optional: bool = False
    ) -> tuple[str, list[MarkdownStr] | None]:
        """Resolve one repeated `list[MarkdownStr]` field's parsed items and new remainder from `text`.

        Repeats `process_field`'s single-item extent/slice/parse step against
        a local `remaining_text`, once per matched item, re-normalizing with
        `mdformat.text()` after every item consumed -- same reasoning as
        `from_text`'s own `remaining_text` handling: a raw substring of an
        already-`mdformat`-compliant document is not itself guaranteed
        `mdformat`-compliant (e.g. it can start with a blank line separating
        two items, which `mdformat` would strip). The loop stops as soon as
        `item_type.get_extent` finds no further extent.

        Unlike `process_field`, this does **not** return a single combined
        line-count `extent` for the caller to slice `text` with. Doing so
        would silently miscount: every intermediate `mdformat.text()`
        renormalization can drop lines (e.g. a blank line separating two
        items) that never show up in any individual item's own `get_extent`
        result, so a caller-side `text.splitlines()[extent:]` computed from a
        *summed* extent would not line up with `text`'s original line
        numbering (exactly the class of bug `from_text` itself already moved
        away from a line-index `cursor` to avoid). Returning the
        already-fully-reduced `remaining_text` string sidesteps this by
        construction, the same way `from_text` tracks its own state.

        The *first* item follows the same `optional` contract as
        `process_field`: no item found there is an absence, which is an
        error for a mandatory `list[X]` field, or `(text, None)` (untouched)
        for an optional `list[X] | None` field. Every *subsequent* item is
        implicitly optional -- no further item found there simply ends the
        list, with no `Optional[X]` needed on `item_type` itself.

        Args:
            name: the field's attribute name (used only for error messages).
            item_type: the field's declared `MarkdownStr` subclass (the `X`
                in `list[X]`/`list[X] | None`).
            text: the not-yet-consumed remainder of the parent's markdown
                text; the first item, if any, is assumed to start at the very
                first line of `text`.
            optional: whether the field is declared `list[X] | None`. When
                `True` and no item at all is found, this is not an error:
                `(text, None)` is returned so the caller can move on to the
                next field without consuming any of `text`.

        Returns:
            A `(remaining_text, items)` pair: `remaining_text` is `text` with
            every matched item (and any separating blank lines) removed and
            re-normalized via `mdformat.text()`, ready to be handed directly
            to the next declared field -- and `items` is the non-empty list
            of parsed instances, or `(text, None)` for an absent optional
            field (see `optional` above).
        """
        assert isinstance(name, str), type(name)
        assert isinstance(item_type, type) and issubclass(item_type, MarkdownStr), item_type
        assert isinstance(text, str), type(text)

        items: list[MarkdownStr] = []
        remaining_text = text
        while remaining_text:
            extent = item_type.get_extent(remaining_text)
            if extent == 0:
                break

            lines = remaining_text.splitlines()
            item_text = format_text("\n".join(lines[:extent]))
            items.append(item_type.from_text(item_text))

            remaining_lines = lines[extent:]
            remaining_text = format_text("\n".join(remaining_lines)) if remaining_lines else ""

        if not items:
            if optional:
                result: tuple[str, list[MarkdownStr] | None] = (text, None)
                return result
            assert False, (
                f"{cls.__name__}.{name}: expected list[{item_type.__name__}], found no match; "
                f"remaining text ({len(text.splitlines())} line(s)) starts with:\n{_snippet(text)}"
            )

        result = (remaining_text, items)

        return result

    @classmethod
    def from_text(cls, text: str) -> MarkdownStr:
        """Create an instance from markdown text, splitting `text` among nested fields.

        If `cls` declares no nested `MarkdownStr` fields, `text` is stored verbatim
        in `_value` (leaf case).

        Otherwise `text` is split into one block per declared field, in
        declaration order. Each block's length is determined by calling that
        field's own `get_extent` on the not-yet-consumed remainder of `text` --
        this lets each field type decide its own boundary (e.g.
        `MarkdownSection.get_extent` stops at the next sibling/ancestor
        heading, while the base `MarkdownStr.get_extent` consumes everything
        remaining).

        The not-yet-consumed remainder is tracked as a string (`remaining_text`),
        re-normalized with `mdformat.text()` after every field is sliced off,
        rather than as a line-index `cursor` into the original `text`. A raw
        substring of an already-`mdformat`-compliant document is not itself
        guaranteed to be `mdformat`-compliant (e.g. it can start with a blank
        line that `mdformat` would strip), which is exactly what `get_extent`
        requires of its input -- so `remaining_text` is kept compliant by
        construction on every iteration instead of being handed to the next
        field's `get_extent` unnormalized.

        A field declared `Optional[X]`/`X | None` (see `_unwrap_optional`) is
        allowed a `0` extent: `process_field` reports it as `(0, None)`
        instead of raising, that field is left unset (pydantic default, i.e.
        `None`) rather than added to `kwargs`, `remaining_text` is left
        untouched (nothing was consumed), and the loop simply continues to
        the next declared field.

        A field declared `list[X]`/`list[X] | None` (see `_unwrap_list`) is
        handled by `process_list_field` instead of `process_field`: it
        repeatedly matches `X` against the not-yet-consumed remainder, once
        per item, until `X.get_extent` finds no further extent. The `list[X]`
        vs. `list[X] | None` distinction plays exactly the same role as it
        does for a scalar field -- a mandatory `list[X]` requires at least
        one matched item (else `process_list_field` raises), while
        `list[X] | None` allows zero items (the field is left `None`); once
        the first item is found, every subsequent item is implicitly
        optional regardless of which of the two was declared.
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == format_text(text), "text is not in 'mdformat'."

        field_names = cls._get_field_names()

        if not field_names:
            # Nothing below calls `get_extent` on `text` for a leaf class reached
            # directly (as opposed to via a parent's `process_field`/
            # `process_list_field`, which already tokenizes it first) -- parse
            # here purely to enforce REQ-005's raw-HTML rejection at every entry
            # point, not just ones a composite parent happens to route through.
            parse(text)
            instance = cls()
            instance._value = text
            return instance

        kwargs: dict[str, MarkdownStr | list[MarkdownStr]] = {}
        remaining_text = text
        for field_name in field_names:
            raw_field_type = cls.model_fields[field_name].annotation
            field_type, is_optional = cls._unwrap_optional(raw_field_type)
            item_type, is_list = cls._unwrap_list(field_type)

            if is_list:
                # `process_list_field` returns the already-fully-reduced remaining
                # text directly (see its docstring for why a combined line-count
                # extent would be unsafe here), so it is adopted as-is below
                # instead of going through the generic extent-based slicing.
                assert isinstance(item_type, type) and issubclass(item_type, MarkdownStr), type(item_type)
                new_remaining_text, list_value = cls.process_list_field(
                    field_name, item_type, remaining_text, optional=is_optional
                )
                if list_value is None:
                    # Optional field with no item found in the remaining text: leave it
                    # unset (pydantic default, e.g. `None`) and don't consume any
                    # of `remaining_text` -- move on to the next field.
                    continue
                kwargs[field_name] = list_value
                remaining_text = new_remaining_text
                continue

            assert isinstance(field_type, type) and issubclass(field_type, MarkdownStr), type(field_type)
            extent, instance_value = cls.process_field(field_name, field_type, remaining_text, optional=is_optional)
            if instance_value is None:
                # Optional field with no extent in the remaining text: leave it
                # unset (pydantic default, e.g. `None`) and don't consume any
                # of `remaining_text` -- move on to the next field.
                continue
            kwargs[field_name] = instance_value

            remaining_lines = remaining_text.splitlines()[extent:]
            remaining_text = format_text("\n".join(remaining_lines)) if remaining_lines else ""

        assert remaining_text == "", f"{cls.__name__}: text left over after processing all fields: {remaining_text!r}"

        instance = cls(**kwargs)  # type: ignore
        instance._value = text
        return instance

    def __str__(self) -> str:
        """Return markdown representation."""
        result: list[str] = []

        field_names = self._get_field_names()
        if not field_names:
            return self._value

        for field_name in field_names:
            field = getattr(self, field_name)
            if field is None:
                # Absent optional field (see `_unwrap_optional`/`from_text`): nothing to render.
                continue
            if isinstance(field, list):
                # `list[MarkdownStr]`/`list[MarkdownStr] | None` field (see `_unwrap_list`):
                # render every item in order, same as a scalar field rendered once.
                for item in field:
                    assert isinstance(item, MarkdownStr), type(item)
                    result.append(str(item))
                continue
            assert isinstance(field, MarkdownStr), type(field)
            result.append(str(field))

        formatted = format_text("\n".join(result))
        return formatted

    def __repr__(self) -> str:
        """Return markdown representation."""
        return self.__str__()

    @classmethod
    def _get_field_names(cls) -> list[str]:
        """Enumerate all class attributes that are MarkdownStr subclasses, in order of definition.

        `Optional[X]`/`X | None` fields are included too (unwrapped via
        `_unwrap_optional` before the `issubclass` check) -- they are still
        `MarkdownStr` fields as far as `from_text`/`__str__` distribution is
        concerned, just ones that may end up unset (`None`) after `from_text`.

        `list[X]`/`list[X] | None` fields are included as well: `annotation`
        is unwrapped via `_unwrap_optional` and then `_unwrap_list` (in that
        order) before the `issubclass` check, so both axes -- optional and
        repeated -- are resolved down to the underlying `X` independently of
        each other.
        """
        field_names = []
        for field_name, field_info in cls.model_fields.items():
            # Check if the field type is a MarkdownStr subclass, possibly wrapped
            # in Optional[...] and/or list[...].
            field_type, _is_optional = cls._unwrap_optional(field_info.annotation)
            field_type, _is_list = cls._unwrap_list(field_type)
            try:
                if isinstance(field_type, type) and issubclass(field_type, MarkdownStr):
                    field_names.append(field_name)
            except TypeError:
                # Handle complex types (nested Optional/Union combinations, etc.)
                pass
        return field_names

    # @field_validator("_value")
    # @classmethod
    # def validate_and_convert_text(cls, v: str) -> str:
    #     if not isinstance(v, str):
    #         raise ValueError(f"'text': '{type(v)}' != 'str'.")

    #     env: dict = {}
    #     tokens = md.parse(v, env)

    #     # Normalise: parse and render roundtrip.
    #     result: str = md.renderer.render(tokens, {}, env)

    #     return result

    # @model_validator(mode="after")
    # def model_validator_after(self) -> MarkdownStr:
    #     """Validate that _tokens is a list of Token instances."""
    #     assert isinstance(self._tokens, list), f"Expected list, got {type(self._tokens)}"
    #     for i, token in enumerate(self._tokens):
    #         assert isinstance(token, Token), f"Token[{i}]: '{type(token)}' != 'Token'."
    #     return self
