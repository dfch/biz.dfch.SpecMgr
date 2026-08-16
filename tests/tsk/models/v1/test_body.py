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

"""Tests for the `Task`/`RecentUpdates`/`UpdateEntry` body models.

`Task` is the first real production consumer of `MarkdownSection1WithComment`
(previously only exercised by `models/md`'s own
`tests/models/md/test_markdown_section_with_comment.py`), so both its
comment-present and comment-absent states are covered explicitly and
thoroughly here, mirroring that file's own well-formed round-trip pattern.
"""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.tsk.models.v1.body import RecentUpdates, Task, UpdateEntry

# A loose (blank-line separated) checklist, so `TaskItem`'s list round-trips
# byte-exact (a *tight* source list round-trips to a structurally-equivalent
# *loose* list instead -- see `MarkdownListItem`'s own docstring/tests,
# `tests/models/md/test_markdown_list_item.py`).
_NO_COMMENT_TEXT = format_text(
    """\
# Migrate Widgets

- [ ] Inventory existing widgets

- [x] Migrate the first widget

## Recent Updates

### Kickoff

Started the migration.

### Progress

Migrated one widget so far.
"""
)

_WITH_COMMENT_TEXT = format_text(
    """\
# Migrate Widgets

<!-- Tracks the widget-registry migration. -->

- [ ] Inventory existing widgets

- [x] Migrate the first widget

## Recent Updates

### Kickoff

Started the migration.
"""
)


class TestTaskWithoutComment(unittest.TestCase):
    """`Task` parses and round-trips with no leading comment."""

    def test_parses_and_round_trips(self) -> None:
        sut = Task.from_text(_NO_COMMENT_TEXT)

        self.assertIsNone(sut.comment)
        self.assertEqual(sut.text, "Migrate Widgets")
        self.assertEqual(
            [(item.checked, item.description) for item in sut.items],
            [(False, "Inventory existing widgets"), (True, "Migrate the first widget")],
        )
        self.assertEqual(
            [(entry.text, entry.content.text) for entry in sut.recent_updates.updates],
            [("Kickoff", "Started the migration."), ("Progress", "Migrated one widget so far.")],
        )
        self.assertEqual(str(sut), _NO_COMMENT_TEXT)


class TestTaskWithComment(unittest.TestCase):
    """`Task` parses and round-trips with a leading comment present."""

    def test_parses_and_round_trips(self) -> None:
        sut = Task.from_text(_WITH_COMMENT_TEXT)

        self.assertIsNotNone(sut.comment)
        self.assertEqual(sut.comment.text, "<!-- Tracks the widget-registry migration. -->\n")
        self.assertEqual(sut.text, "Migrate Widgets")
        self.assertEqual(
            [(item.checked, item.description) for item in sut.items],
            [(False, "Inventory existing widgets"), (True, "Migrate the first widget")],
        )
        self.assertEqual([entry.text for entry in sut.recent_updates.updates], ["Kickoff"])
        self.assertEqual(str(sut), _WITH_COMMENT_TEXT)


class TestTaskItemsValidation(unittest.TestCase):
    """`Task.items` enforces its `min_length=1` constraint."""

    def test_empty_items_raises_validation_error(self) -> None:
        valid_recent_updates = RecentUpdates.from_text(
            format_text(
                """\
## Recent Updates

### Kickoff

Started.
"""
            )
        )

        with self.assertRaises(ValidationError):
            Task(items=[], recent_updates=valid_recent_updates)


class TestTaskItemMarkerValidatedEagerly(unittest.TestCase):
    """`Task.from_text` rejects a malformed checkbox marker immediately, not lazily.

    Regression test: `TaskItem.checked`/`.description` are `@computed_field`s,
    which Pydantic only evaluates on access, never during construction. A
    `Task`-level `model_validator(mode="after")` forces every item's
    `.checked` to be evaluated right after parsing, so a malformed marker
    (e.g. `"- [z] foo"`) raises immediately from `Task.from_text` instead of
    silently parsing and only failing (if ever) whenever something later
    happens to read `.checked`/`.description` -- which would otherwise let a
    caller like `create_tsk` write a bad file to disk before any error
    surfaced.
    """

    def test_malformed_marker_raises_from_from_text(self) -> None:
        text = format_text(
            """\
# Migrate Widgets

- [z] bad marker

## Recent Updates

### Kickoff

Started.
"""
        )

        with self.assertRaises(ValidationError):
            Task.from_text(text)


class TestRecentUpdatesEmpty(unittest.TestCase):
    """`RecentUpdates.updates` enforces its `min_length=1` constraint (consistent with `Task.items`).

    `models.md`'s generic list-parsing engine already rejects a `## Recent
    Updates` heading with zero `### ` entries during `from_text` for any
    non-`Optional` `list[X]` field; `min_length=1` makes direct Python
    construction (e.g. `create_tsk`) consistently reject an empty list too,
    rather than silently allowing `RecentUpdates(updates=[])`.
    """

    def test_zero_entries_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            RecentUpdates(updates=[])


class TestRecentUpdatesSingleEntry(unittest.TestCase):
    """A `## Recent Updates` section with exactly one `### ` entry parses and round-trips."""

    def test_parses_and_round_trips(self) -> None:
        text = format_text(
            """\
## Recent Updates

### Kickoff

Started the migration.
"""
        )

        sut = RecentUpdates.from_text(text)

        self.assertEqual(len(sut.updates), 1)
        self.assertEqual(sut.updates[0].text, "Kickoff")
        self.assertEqual(sut.updates[0].content.text, "Started the migration.")
        self.assertEqual(str(sut), text)


class TestRecentUpdatesMultipleEntries(unittest.TestCase):
    """A `## Recent Updates` section with several free-form-titled entries parses and round-trips."""

    def test_parses_and_round_trips(self) -> None:
        text = format_text(
            """\
## Recent Updates

### Kickoff

Started the migration.

### Halfway there

Migrated half of the widgets.

### Wrapping up

Only the shim removal is left.
"""
        )

        sut = RecentUpdates.from_text(text)

        self.assertEqual(
            [(entry.text, entry.content.text) for entry in sut.updates],
            [
                ("Kickoff", "Started the migration."),
                ("Halfway there", "Migrated half of the widgets."),
                ("Wrapping up", "Only the shim removal is left."),
            ],
        )
        self.assertEqual(str(sut), text)


class TestUpdateEntryFreeFormTitle(unittest.TestCase):
    """`UpdateEntry`'s H3 title is free-form (any non-blank text matches its `@alias`)."""

    def test_accepts_an_arbitrary_title(self) -> None:
        text = format_text(
            """\
### Anything Goes Here 123

Some update text.
"""
        )

        sut = UpdateEntry.from_text(text)

        self.assertEqual(sut.text, "Anything Goes Here 123")
        self.assertEqual(sut.content.text, "Some update text.")
        self.assertEqual(str(sut), text)


if __name__ == "__main__":
    unittest.main()
