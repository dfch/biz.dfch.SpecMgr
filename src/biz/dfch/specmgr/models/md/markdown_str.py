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
import mdformat

from ._markdown import md


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
        assert text == mdformat.text(text), "text is not in 'mdformat'."

        tokens = md.parse(text)

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

        assert extent > 0, f"{cls.__name__}.{name}: get_extent found no extent in remaining text"

        lines = text.splitlines()
        field_text = mdformat.text("\n".join(lines[:extent]))
        instance = type_.from_text(field_text)

        result = (extent, instance)

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
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == mdformat.text(text), "text is not in 'mdformat'."

        field_names = cls._get_field_names()

        if not field_names:
            instance = cls()
            instance._value = text
            return instance

        kwargs: dict[str, MarkdownStr] = {}
        remaining_text = text
        for field_name in field_names:
            raw_field_type = cls.model_fields[field_name].annotation
            field_type, is_optional = cls._unwrap_optional(raw_field_type)
            assert isinstance(field_type, type) and issubclass(field_type, MarkdownStr), type(field_type)

            extent, instance_field = cls.process_field(field_name, field_type, remaining_text, optional=is_optional)
            if instance_field is None:
                # Optional field with no extent in the remaining text: leave it
                # unset (pydantic default, e.g. `None`) and don't consume any
                # of `remaining_text` -- move on to the next field.
                continue
            kwargs[field_name] = instance_field

            remaining_lines = remaining_text.splitlines()[extent:]
            remaining_text = mdformat.text("\n".join(remaining_lines)) if remaining_lines else ""

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
            assert isinstance(field, MarkdownStr), type(field)
            result.append(str(field))

        formatted = mdformat.text("\n".join(result))
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
        """
        field_names = []
        for field_name, field_info in cls.model_fields.items():
            # Check if the field type is a MarkdownStr subclass
            field_type, _is_optional = cls._unwrap_optional(field_info.annotation)
            try:
                if isinstance(field_type, type) and issubclass(field_type, MarkdownStr):
                    field_names.append(field_name)
            except TypeError:
                # Handle complex types (nested Optional/Union combinations, etc.)
                pass
        print(f"_get_field_names: '{cls.__name__}': {field_names}")
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
