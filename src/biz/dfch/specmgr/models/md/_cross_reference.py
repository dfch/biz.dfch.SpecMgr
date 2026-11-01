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

"""Shared, private cross-reference format validator for `models.md` domain body models.

Generalizes `sysrs`'s original per-section cross-reference-list validator
(formerly `sysrs.models.v1.body._UUID_PATTERN`/`_validate_cross_reference_items`)
into a single helper reused by `sysrs`, `vcr` (its `UUID_PATTERN` fragment
only, see `vcr.models.v1.body._VERIFIES_PATTERN`), and the new
`RequirementsBase`/`DecisionsBase`/`GoalsBase`/`RisksBase` base classes in
`common_sections.py` (feat-135-related-artifacts-risks, REQ-007/REQ-010),
rather than a third/fourth independent reimplementation of the same
`"<TAG> <uuid>: <title>"` format check.

Like every other private (`_`-prefixed) shared helper in `models/md`
(`_ordering.py`, `_errors.py`, `_markdown.py`), this module is **not**
re-exported from `models/md/__init__.py` -- callers import it directly::

    from ....models.md._cross_reference import UUID_PATTERN, validate_cross_reference_items
"""

from __future__ import annotations

import re

from .markdown_list_item import MarkdownListItemWithNotes

#: The standard lowercase 8-4-4-4-12 hex UUID shape, shared by every
#: cross-reference section's item-text pattern (generalized from `sysrs`'s
#: original local `_UUID_PATTERN`, which already matched `vcr`'s own
#: inline `_VERIFIES_PATTERN` UUID fragment).
UUID_PATTERN = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def build_cross_reference_pattern(*tags: str) -> str:
    """Build a `"^<TAG(S)> {UUID_PATTERN}: .+$"` full-line match pattern for one or more type tags.

    A single tag renders as a bare literal (`"^REQ ...: .+$"`); two or more
    render as a parenthesized alternation (`"^(REQ|UC) ...: .+$"`, mirroring
    `sysrs.models.v1.body._DECISIONS_PATTERN`'s `(DEC|ADR)` shape and
    `vcr.models.v1.body._VERIFIES_PATTERN`'s `(REQ|UC)` shape).

    Args:
        tags: one or more allowed type tags (e.g. `"REQ"`, or `"REQ", "UC"`
            for a multi-tag cross-reference). At least one tag is required.

    Returns:
        A pattern string matching `"<TAG> <uuid>: <title>"` end-to-end
        (`re.fullmatch` shape, anchored with `^`/`$`), where `<TAG>` is any
        one of `tags`.

    Raises:
        AssertionError: `tags` is empty.
    """
    assert tags, "build_cross_reference_pattern: at least one type tag is required"

    tag_fragment = tags[0] if len(tags) == 1 else f"({'|'.join(tags)})"
    return rf"^{tag_fragment} {UUID_PATTERN}: .+$"


def validate_cross_reference_items(
    items: list[MarkdownListItemWithNotes], pattern: str
) -> list[MarkdownListItemWithNotes]:
    """Enforce `pattern` against every item's `.text` (shared by every cross-reference list class).

    `re.DOTALL` is required: an item's `.text` keeps the embedded newline of
    a soft-wrapped bullet line (`mdformat` does not reflow), and `.` would
    not otherwise match it -- confirmed empirically by `sysrs`'s original
    Phase 1 (Task 1.1) implementation of this same check. The pattern
    itself is otherwise a plain `re.fullmatch` against the exact
    `<ALLOWED-TYPE-TAG(S)> <uuid>: <title>` shape (see
    `build_cross_reference_pattern`).

    Args:
        items: The list's already-list-level-validated items (e.g.
            `Field(min_length=1)` has already run).
        pattern: The calling class's own pattern (typically built via
            `build_cross_reference_pattern`).

    Returns:
        `items`, unchanged, once every item matches.

    Raises:
        ValueError: some item's `.text` does not fullmatch `pattern` --
            channeled by Pydantic into `pydantic.ValidationError`.
    """
    for item in items:
        if not re.fullmatch(pattern, item.text, re.DOTALL):
            raise ValueError(f"item must match pattern {pattern!r}, got {item.text!r}")
    return items
