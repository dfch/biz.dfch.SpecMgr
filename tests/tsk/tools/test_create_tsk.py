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

"""Tests for the ``create_tsk`` ``@mcp.tool()`` wrapper (Task 3.3)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.tsk.models.v1 import TskDocument, parse_tsk
from biz.dfch.specmgr.tsk.tools._paths import tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing
    - [x] Do the second thing

    ## Recent Updates

    ### 2026-08-19 - Kickoff

    Started the task list.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized task list sections.\n"

_NO_RECENT_UPDATES_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing
    """
)

_MALFORMED_CHECKBOX_MARKER_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [z] Not a valid checkbox marker

    ## Recent Updates

    ### 2026-08-19 - Kickoff

    Started the task list.
    """
)


class TempTskDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateTsk(TempTskDirTestCase):
    """Tests for the create_tsk tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_tsk must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_tsk(_MINIMAL_BODY)

        self.assertIsInstance(result, TskDocument)
        self.assertIsNotNone(result.frontmatter.id)
        self.assertEqual(result.frontmatter.type, "tsk")
        self.assertEqual(result.frontmatter.status, "draft")
        self.assertIsNotNone(result.frontmatter.created)
        self.assertEqual(result.frontmatter.created, result.frontmatter.updated)
        self.assertEqual(result.frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(result.body.text, "Simple Task List")

    def test_writes_expected_filename(self) -> None:
        """create_tsk must write f'tsk-{id}-{slug}.md' under the task list base dir."""
        result = create_tsk(_MINIMAL_BODY)

        expected_path = tsk_base_dir() / f"tsk-{result.frontmatter.id}-simple-task-list.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_tsk(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_tsk(_MINIMAL_BODY)

        expected_path = tsk_base_dir() / f"tsk-{result.frontmatter.id}-simple-task-list.md"
        on_disk = parse_tsk(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Simple Task List")
        self.assertEqual(
            [(item.checked, item.description) for item in on_disk.body.items],
            [(False, "Do the first thing"), (True, "Do the second thing")],
        )

    def test_creates_base_dir_if_missing(self) -> None:
        """create_tsk must create the task list base directory if it does not exist yet."""
        self.assertFalse(tsk_base_dir().exists())

        create_tsk(_MINIMAL_BODY)

        self.assertTrue(tsk_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_tsk(_MALFORMED_BODY)

        self.assertFalse(tsk_base_dir().exists())

    def test_zero_recent_updates_entries_raises_and_writes_nothing(self) -> None:
        """A body with no `## Recent Updates` section at all must raise, writing nothing.

        Confirms `create_tsk` does no auto-seeding: a caller who omits the
        mandatory `## Recent Updates` section (`RecentUpdates.updates` requires
        `min_length=1`) gets a validation failure, the same as an empty
        checklist would -- not a silently-injected "Created" entry.
        """
        with self.assertRaises(AssertionError):
            create_tsk(_NO_RECENT_UPDATES_BODY)

        self.assertFalse(tsk_base_dir().exists())

    def test_malformed_checkbox_marker_raises_and_writes_nothing(self) -> None:
        """A malformed checklist marker (e.g. `- [z] ...`) must raise and write nothing.

        Regression test: `TaskItem.checked`/`.description` are lazily-evaluated
        `@computed_field`s, so `Task.from_text` alone would not have caught
        this without `Task`'s own eager-validation `model_validator` (see
        `tsk.models.v1.body.Task._validate_items_eagerly`) -- without it, this
        tool could have written a malformed file to disk before any error
        ever surfaced.
        """
        with self.assertRaises((AssertionError, ValueError)):
            create_tsk(_MALFORMED_CHECKBOX_MARKER_BODY)

        self.assertFalse(tsk_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
