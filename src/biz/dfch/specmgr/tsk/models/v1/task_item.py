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

"""`TaskItem` -- a single `- [ ] .../- [x] ...` checklist entry.

The project's shared markdown parser (`MarkdownIt("commonmark")`, see
`models/md/_markdown.py`) has no GFM task-list plugin enabled, so `- [ ] text`/
`- [x] text` is not a distinct AST node -- it parses as an ordinary bullet-list
item whose leading-paragraph text is the literal string `"[ ] text"`/
`"[x] text"` (see `MarkdownListItem.text`). `TaskItem` recovers the intended
`checked`/`description` split from that literal text via a regular expression.
"""

from __future__ import annotations

import re

from pydantic import ConfigDict, computed_field

from ....models.md import MarkdownListItem, MarkdownParagraph

#: Matches a literal `[ ]`/`[x]`/`[X]` checkbox marker at the start of a
#: `TaskItem`'s own leading-paragraph text (see `MarkdownListItem.text`),
#: capturing the marker character (group 1) and the remaining description
#: text (named group `description`). The marker check is case-insensitive
#: for the "checked" state (`[x]`/`[X]` both count), matching common GFM
#: task-list authoring conventions.
_MARKER_PATTERN = re.compile(r"^\[( |x|X)\]\s*(?P<description>.*)$")

#: JSON Schema (ECMAScript) form of `_MARKER_PATTERN` for `TaskItem`'s own
#: `model_config` `json_schema_extra` metadata (feat-189 Phase 120, C13):
#: the same start-anchored `[ ]`/`[x]`/`[X]` checkbox-marker shape, with the
#: Python-only `(?P<description>...)` named group as an unnamed `(...)`
#: (ECMAScript has no `(?P<name>...)` syntax). Metadata only -- the
#: enforcement is `_MARKER_PATTERN` itself, matched by `checked`/
#: `description` below; this constant is never matched in Python.
_MARKER_SCHEMA_PATTERN = r"^\[( |x|X)\]\s*(.*)$"


class TaskItem(MarkdownListItem):
    """One `- [ ] .../- [x] ...` checklist entry of a `Task`'s flat item list.

    A leaf `MarkdownListItem` subclass (declares no nested `MarkdownStr`
    fields of its own, only the two computed properties below), so it parses/
    renders exactly like the base class -- `checked`/`description` are purely
    derived views over the inherited `.text`, computed lazily rather than
    stored, and therefore never interfere with `MarkdownStr`'s field-based
    `from_text`/`__str__` distribution (see `MarkdownStr._get_field_names`).

    Parameters
    ----------
    checked:
        Computed. `True` for a `[x]`/`[X]` marker, `False` for a `[ ]`
        marker. Raises `AssertionError` if `.text` does not start with a
        well-formed checkbox marker at all.
    description:
        Computed. The item's own text with the leading checkbox marker
        stripped, e.g. `"Do the thing"` for `"- [ ] Do the thing"`. Raises
        `AssertionError` under the same condition as `checked`.
    content:
        An optional list of paragraphs with details content of the task item.
    """

    # feat-189 Phase 120 (C13): the checkbox-marker constraint as a `pattern`
    # key on this class's own generated JSON Schema entry -- metadata only
    # (the item text itself is private `_value` state, invisible to the
    # validation-mode schema, and `checked`/`description` are computed
    # fields, which the generator's `model_json_schema()` default mode
    # omits): `_MARKER_PATTERN` matched in those computed properties below
    # remains the sole enforcement point.
    model_config = ConfigDict(json_schema_extra={"pattern": _MARKER_SCHEMA_PATTERN})

    @computed_field  # type: ignore
    @property
    def checked(self) -> bool:
        """Whether this item's checkbox marker is `[x]`/`[X]` (checked) rather than `[ ]` (unchecked).

        Returns:
            `True` for a `[x]`/`[X]` marker, `False` for a `[ ]` marker.

        Raises:
            AssertionError: `.text` does not start with a well-formed
                checkbox marker (see `_MARKER_PATTERN`), or spans more
                than one physical line (soft-wrapped/lazy-continuation
                list items are not supported, see
                `MarkdownListItem.single_line_text`). The message names
                this item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        text = self.single_line_text(expected="a '- [ ]'/'- [x]' checkbox marker")
        match = _MARKER_PATTERN.match(text)
        assert match, f"{self._path} (line {self._line}): expected a '- [ ]'/'- [x]' checkbox marker, got {text!r}"
        return match.group(1).lower() == "x"

    @computed_field  # type: ignore
    @property
    def description(self) -> str:
        """This item's own text with the leading checkbox marker stripped.

        Returns:
            The description text following the checkbox marker, e.g.
            `"Do the thing"` for `"- [ ] Do the thing"`.

        Raises:
            AssertionError: `.text` does not start with a well-formed
                checkbox marker (see `_MARKER_PATTERN`), or spans more
                than one physical line (soft-wrapped/lazy-continuation
                list items are not supported, see
                `MarkdownListItem.single_line_text`). The message names
                this item's own path and 1-based line (REQ-001/REQ-002, via
                `self._path`/`self._line`, threaded in by `models.md`'s
                `MarkdownListItem.from_text`).
        """
        text = self.single_line_text(expected="a '- [ ]'/'- [x]' checkbox marker")
        match = _MARKER_PATTERN.match(text)
        assert match, f"{self._path} (line {self._line}): expected a '- [ ]'/'- [x]' checkbox marker, got {text!r}"
        return match.group("description").strip()

    content: list[MarkdownParagraph] | None = None
