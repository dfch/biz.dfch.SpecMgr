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

"""Tests for the ``update_tsk`` ``@mcp.tool()`` wrapper (Task 3.4)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.tsk.models.v1 import TskDocument, parse_tsk
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, ensure_tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.tsk.tools.update_tsk import update_tsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### Kickoff

    Started the task list.
    """
)

_UPDATED_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [x] Do the first thing
    - [ ] Do a new second thing

    ## Recent Updates

    ### Kickoff

    Started the task list.

    ### Progress

    Finished the first item.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized task list sections.\n"

_ZERO_RECENT_UPDATES_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [x] Do the first thing
    """
)


class TempTskDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_tsk(self) -> TskDocument:
        """Create and return a real, persisted task list via create_tsk."""
        return create_tsk(_MINIMAL_BODY)


class TestUpdateTsk(TempTskDirTestCase):
    """Tests for the update_tsk tool."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """update_tsk must replace the body but preserve every frontmatter field but `updated`."""
        original = self.existing_tsk()

        result = update_tsk(original.frontmatter.id, _UPDATED_BODY)

        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.type, original.frontmatter.type)
        self.assertEqual(result.frontmatter.status, original.frontmatter.status)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(
            [(item.checked, item.description) for item in result.body.items],
            [(True, "Do the first thing"), (False, "Do a new second thing")],
        )

    def test_written_file_round_trips_via_parse_tsk(self) -> None:
        """The updated file on disk must parse back into the returned document's shape."""
        original = self.existing_tsk()

        result = update_tsk(original.frontmatter.id, _UPDATED_BODY)

        base_dir = ensure_tsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        self.assertEqual(len(matching), 1)
        on_disk = parse_tsk(matching[0].read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.updated, result.frontmatter.updated)
        self.assertEqual(len(on_disk.body.recent_updates.updates), 2)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """update_tsk must raise TskNotFoundError for an id with no matching file."""
        with self.assertRaises(TskNotFoundError):
            update_tsk("no-such-id", _MINIMAL_BODY)

    def test_invalid_content_raises_and_leaves_file_unchanged(self) -> None:
        """A structurally invalid body must raise AssertionError, leaving the file untouched."""
        original = self.existing_tsk()
        base_dir = ensure_tsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_tsk(original.frontmatter.id, _MALFORMED_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)

    def test_dropping_last_recent_updates_entry_raises_and_leaves_file_unchanged(self) -> None:
        """Replacing the body with zero `## Recent Updates` entries must raise, leaving the file untouched."""
        original = self.existing_tsk()
        base_dir = ensure_tsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_tsk(original.frontmatter.id, _ZERO_RECENT_UPDATES_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
