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

"""Tests for :func:`parse_tsk`: the `TskDocument`-level `from_text` entry point."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.tsk.models.v1 import TskDocument
from biz.dfch.specmgr.tsk.models.v1.parser import parse_tsk

_REFERENCE_PATH = (
    Path(__file__).resolve().parents[4]
    / ".specmgr"
    / "feat"
    / "feat-10-add-artifact-type-tasklist"
    / "tsk_reference.md"
)

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: tsk-001
    type: tsk
    version: 1.0.0
    status: draft
    created: '2026-08-16 00:00:00.000Z'
    updated: '2026-08-16 00:00:00.000Z'
    ---

    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### 2026-08-16 - Kickoff

    Started the task list.
    """
)


class TestParseTsk(unittest.TestCase):
    """Tests for `parse_tsk`."""

    def test_parses_minimal_document(self) -> None:
        """A minimal, valid document parses into a TskDocument with the expected shape."""
        document = parse_tsk(_MINIMAL_DOC)

        self.assertIsInstance(document, TskDocument)
        self.assertEqual(document.frontmatter.id, "tsk-001")
        self.assertEqual(document.frontmatter.status, "draft")
        self.assertEqual(document.body.text, "Simple Task List")
        self.assertIsNone(document.body.comment)
        self.assertEqual(
            [(item.checked, item.description) for item in document.body.items],
            [(False, "Do the first thing")],
        )
        self.assertEqual(
            [(entry.title, entry.content.text) for entry in document.body.recent_updates.updates],
            [("Kickoff", "Started the task list.")],
        )

    def test_parses_full_reference_document(self) -> None:
        """The feature's own reference document round-trips through parse_tsk."""
        text = _REFERENCE_PATH.read_text(encoding="utf-8")

        document = parse_tsk(text)

        self.assertEqual(document.frontmatter.id, "deaddead-face-face-face-deaddeadface")
        self.assertEqual(document.frontmatter.status, "active")
        self.assertEqual(document.body.text, "Migrate Widgets to the New Registry")
        self.assertIsNotNone(document.body.comment)
        self.assertEqual(
            [(item.checked, item.description) for item in document.body.items],
            [
                (True, "Inventory existing widgets and their registrations"),
                (False, "Migrate each widget to WidgetRegistryV2"),
                (False, "Remove the deprecated WidgetRegistryV1 shim"),
            ],
        )
        self.assertEqual(
            [(entry.title, entry.content.text) for entry in document.body.recent_updates.updates],
            [
                ("Migration in progress", "Migrated 5 of 12 widgets so far; no regressions found."),
                (
                    "Kickoff",
                    "Started the migration; inventoried 12 widgets currently registered against WidgetRegistryV1.",
                ),
            ],
        )

    def test_defaults_frontmatter_when_absent(self) -> None:
        """Omitting the frontmatter block entirely still parses, applying TskFrontmatter's defaults."""
        text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

        document = parse_tsk(text)

        self.assertIsNone(document.frontmatter.id)
        self.assertEqual(document.frontmatter.type, "tsk")
        self.assertEqual(document.frontmatter.status, "draft")

    def test_invalid_status_raises_validation_error(self) -> None:
        """A frontmatter `status` outside TskFrontmatter's closed set fails validation."""
        text = _MINIMAL_DOC.replace("status: draft", "status: not-a-real-status")

        with self.assertRaises(ValidationError):
            parse_tsk(text)

    def test_missing_recent_updates_section_raises_assertion_error(self) -> None:
        """A missing mandatory `## Recent Updates` section is a structural failure."""
        text = textwrap.dedent(
            """\
            # Simple Task List

            - [ ] Do the first thing
            """
        )

        with self.assertRaises(AssertionError):
            parse_tsk(text)

    def test_missing_items_raises_assertion_error(self) -> None:
        """A missing mandatory checklist (no `- [ ]`/`- [x]` items at all) is a structural failure."""
        text = textwrap.dedent(
            """\
            # Simple Task List

            ## Recent Updates

            ### 2026-08-16 - Kickoff

            Started the task list.
            """
        )

        with self.assertRaises(AssertionError):
            parse_tsk(text)

    def test_recent_updates_with_multiple_entries_round_trips(self) -> None:
        """A `## Recent Updates` section with several entries parses correctly (non-empty case)."""
        text = textwrap.dedent(
            """\
            ---
            id: tsk-001
            type: tsk
            version: 1.0.0
            status: draft
            created: '2026-08-16 00:00:00.000Z'
            updated: '2026-08-16 00:00:00.000Z'
            ---

            # Simple Task List

            - [ ] Do the first thing

            ## Recent Updates

            ### 2026-08-17 - Follow-up

            Made more progress.

            ### 2026-08-16 - Kickoff

            Started the task list.
            """
        )

        document = parse_tsk(text)

        self.assertEqual(
            [(entry.title, entry.content.text) for entry in document.body.recent_updates.updates],
            [("Follow-up", "Made more progress."), ("Kickoff", "Started the task list.")],
        )

    def test_recent_updates_with_zero_entries_raises_assertion_error(self) -> None:
        """A `## Recent Updates` heading present but with zero `### ` entries is a structural failure.

        Confirms the Phase 1 finding (see this feature's README "Recent Updates"/2026-08-16 entry):
        `RecentUpdates.updates` is declared `list[UpdateEntry]` (mandatory, not `list[UpdateEntry] | None`),
        so `models/md`'s generic `process_list_field` engine requires at least one matched `### ` entry when
        parsing from text and raises `AssertionError` otherwise -- only direct Python construction
        (`RecentUpdates(updates=[])`) allows a truly empty list; a *persisted* document cannot have a
        `## Recent Updates` section with zero entries and still parse.
        """
        text = textwrap.dedent(
            """\
            # Simple Task List

            - [ ] Do the first thing

            ## Recent Updates
            """
        )

        with self.assertRaises(AssertionError):
            parse_tsk(text)


if __name__ == "__main__":
    unittest.main()
