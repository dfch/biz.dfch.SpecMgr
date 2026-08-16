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

from pydantic import Field

from ....models.md import (
    MarkdownParagraph,
    MarkdownSection1WithComment,
    MarkdownSection2,
    MarkdownSection3,
    alias,
    AliasType,
)
from .task_item import TaskItem


@alias(value=".+", type=AliasType.REGEX)
class UpdateEntry(MarkdownSection3):
    """`### {free-form title}` under `## Recent Updates` -- one dated/titled update entry.

    The H3 heading text is free-form (no fixed vocabulary/numbering, unlike
    ADR's `### Option N: ...` -- update entries are not numbered options).

    Parameters
    ----------
    content:
        The lead paragraph right after the H3 heading -- this entry's own
        update text. Mandatory.
    """

    content: MarkdownParagraph = Field(
        description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
    )


class RecentUpdates(MarkdownSection2):
    """`## Recent Updates` -- a dynamic list of free-form-titled `### ` update entries.

    A fixed-title (non-alias) `MarkdownSection2`, structurally similar to
    `AdrBody`'s `## Pros and Cons of the Options`/`AdrOption` collection, but
    with no dedicated per-entry tools (no `option_create`/`option_list`
    equivalent) -- entries are appended by editing the whole body.

    Parameters
    ----------
    updates:
        The dynamic collection of `### ` entries, in document order. Requires
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
        description="Dynamic collection of `### {free-form title}` entries, in document order. "
        "Must contain at least one entry.",
    )


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
