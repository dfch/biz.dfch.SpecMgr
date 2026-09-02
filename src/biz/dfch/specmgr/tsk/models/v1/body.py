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

"""TaskList (TSK) body models: whole-section fields under a single H1.

Built on the generic `models.md` `MarkdownSection1WithComment`/
`MarkdownSection2`/`MarkdownSection3`/`MarkdownParagraph`/`TaskItem` engine,
mirroring `req/models/v1/body.py`'s "one class per heading/list" shape. `Task`
is the top-level H1 container:

```
# {H1 title}
<!-- optional leading comment -->        comment: MarkdownComment | None
- [ ] flat checklist item                items: list[TaskItem]  (>=1)
- [x] another item
...

## Recent Updates                        recent_updates: RecentUpdates
### {free-form title}
{update text}
### {another entry}
{update text}
```

Field declaration order on `Task` enforces markdown order (title -> optional
comment (inherited) -> items (>=1) -> mandatory `## Recent Updates`), since
`models.md`'s `MarkdownStr.from_text` distributes text among declared fields
in that same order.
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, model_validator

from ....models.md import (
    MarkdownParagraph,
    MarkdownSection1WithComment,
    MarkdownSection2WithComment,
    MarkdownSection3,
    alias,
    AliasType,
)
from ....models.md._ordering import validate_newest_first
from .task_item import TaskItem

#: Matches a `{yyyy-MM-dd or full date+time} ( - | : ) {title}` heading line
#: as retained in a composite `MarkdownSection3`'s `.text` (which carries the
#: heading's inline content, no `###` marker), capturing the timestamp
#: (named group `timestamp`) and the title (named group `title`). Mirrors
#: `dec.models.v1.body._UPDATE_ENTRY_HEADING_PATTERN`/`vcr.models.v1.body._UPDATE_ENTRY_HEADING_PATTERN`
#: exactly.
_UPDATE_ENTRY_HEADING_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))?)(?: - | : )(?P<title>.+)"
)


@alias(
    value=r"^\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))?(?: - | : ).+$",
    type=AliasType.REGEX,
)
class UpdateEntry(MarkdownSection3):
    """`### {timestamp} ( - | : ) {title}` under `## Recent Updates` -- one update entry.

    The H3 heading text carries a timestamp and a title, joined by either
    ``" - "`` (space, hyphen, space) or ``" : "`` (space, colon, space):
    e.g. `### 2026-08-19 - Kickoff` or
    `### 2026-08-19 05:42:00.000+02:00 : Kickoff`. The em-dash separator is
    rejected. The timestamp is either a bare ``yyyy-MM-dd`` date or the
    full ``yyyy-MM-dd HH:mm:ss.fff`` + explicit UTC offset (``+02:00``,
    ``-05:00``) or ``Z`` for UTC variant (REQ-004). Mirrors DEC/VCR's own
    `UpdateEntry` shape exactly.

    Parameters
    ----------
    content:
        The lead paragraph right after the H3 heading -- this entry's own
        update text. Mandatory.
    timestamp:
        Computed. The timestamp carried by the heading, verbatim. Never
        stored separately -- derived from the retained heading text.
    title:
        Computed. The title carried by the heading (the text after
        ``" - "``/``" : "``). Never stored separately -- derived from the
        retained heading text.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The timestamp carried by this heading (e.g. `2026-08-19` or `2026-08-19 05:42:00.000+02:00`).

        Returns:
            The timestamp string parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The title carried by this heading (e.g. `Kickoff` for `### 2026-08-19 - Kickoff`).

        Returns:
            The title parsed from the retained heading text (the text
            after ``" - "``/``" : "``).

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("title")
        return result


class RecentUpdates(MarkdownSection2WithComment):
    """`## Recent Updates` -- a dynamic, newest-first list of timestamp-led `### ` update entries.

    A fixed-title (non-alias) `MarkdownSection2WithComment`, structurally
    similar to `AdrBody`'s `## Pros and Cons of the Options`/`AdrOption`
    collection, but with no dedicated per-entry tools (no
    `option_create`/`option_list` equivalent) -- entries are prepended
    (newest-first) by editing the whole body. May be preceded by an
    explanatory HTML comment (e.g. an ordering hint).

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`), e.g.
        `<!-- Newest entry first -- prepend new entries directly below
        this comment. -->`. Inherited from `MarkdownSection2WithComment`.
    updates:
        The dynamic collection of `### ` entries, in document order,
        newest-first (enforced, see `_validate_newest_first`). Requires
        at least one entry (``min_length=1``), same as `Task.items` below --
        `models.md`'s generic list-parsing engine already enforces this
        during `from_text` for any non-`Optional` `list[X]` field regardless
        of `min_length`, so this constraint makes direct Python construction
        (e.g. a future `create_tsk` tool) consistent with parsing instead of
        silently allowing `RecentUpdates(updates=[])`. A newly created `tsk`
        document must therefore seed a first entry (e.g. "Created") -- see
        the feature README's Decisions Made.
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `### {timestamp} ( - | : ) {title}` entries, in document order, "
        "newest-first. Must contain at least one entry.",
    )

    @model_validator(mode="after")
    def _validate_newest_first(self) -> RecentUpdates:
        """Reject entries that are not in newest-first order.

        Delegates to the shared `models.md._ordering.validate_newest_first`
        helper (mixed date-only/date+time day-granularity rule, equal
        values allowed) -- mirrors `feat.models.v1.body.Updates._validate_newest_first`
        without duplicating its logic. Raises on the first out-of-order pair.
        """
        validate_newest_first([update.timestamp for update in self.updates], "RecentUpdates")
        return self


@alias(value=".+", type=AliasType.REGEX)
class Task(MarkdownSection1WithComment):
    """The `tsk` body: a single H1 section with the fields below.

    The H1 heading text is free-form. `comment` is inherited from
    `MarkdownSection1WithComment` (see its own docstring) -- not redeclared
    here.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`) preceding
        `items`. Inherited from `MarkdownSection1WithComment`.
    items:
        The flat checklist -- one `- [ ] .../- [x] ...` entry per line.
        Mandatory. At least one item.
    recent_updates:
        `## Recent Updates`. Mandatory.
    """

    items: list[TaskItem] = Field(
        min_length=1,
        description="The flat checklist -- one `- [ ] .../- [x] ...` entry per line; must contain at least one item.",
    )
    recent_updates: RecentUpdates = Field(description="`## Recent Updates` section. Mandatory.")

    @model_validator(mode="after")
    def _validate_items_eagerly(self) -> "Task":
        """Force every `TaskItem.checked` computed field to evaluate eagerly, not lazily.

        `TaskItem.checked`/`.description` are `@computed_field`s -- Pydantic
        only evaluates a computed field's getter on access (e.g. during
        `model_dump()`/serialization), never during construction/validation
        of the underlying model itself. Left unchecked, that would mean
        `Task.from_text(...)` (and therefore `create_tsk`, the generic
        `update` tool in `general.tools`, and `validate_tsk`) could
        silently accept a malformed checkbox marker like `"- [z] foo"`,
        breaking this project's universal "successfully
        constructing the model *is* the validation" convention -- a caller
        could write a bad file to disk before the error ever surfaced, if it
        surfaced at all.

        A `model_validator` on `TaskItem` itself cannot fix this:
        `MarkdownListItem.from_text` constructs each item via a bare,
        no-argument `cls()` first and only assigns its parsed text to the
        private `_value` attribute *afterward* (bypassing Pydantic's own
        validation pipeline), so a `TaskItem`-level `model_validator` would
        fire on an empty, not-yet-populated instance. By the time *this*
        validator runs, `self.items` already holds fully-parsed `TaskItem`
        instances (each already went through its own `from_text` above), so
        accessing `.checked` here is safe and forces the check immediately.
        """
        for item in self.items:
            _ = item.checked
        return self
