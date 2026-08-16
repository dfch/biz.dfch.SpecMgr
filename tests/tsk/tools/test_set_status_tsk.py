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

"""Tests for the ``set_status_tsk`` ``@mcp.tool()`` wrapper (Task 3.5)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.tsk.models.v1 import TskDocument, parse_tsk
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, ensure_tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.tsk.tools.set_status_tsk import set_status_tsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### Kickoff

    Started the task list.
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

    def _find_path(self, id_: str) -> Path:
        base_dir = ensure_tsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if id_ in p.name]
        assert len(matching) == 1
        return matching[0]


class TestSetStatusTsk(TempTskDirTestCase):
    """Tests for the set_status_tsk tool."""

    def test_sets_status_and_bumps_updated(self) -> None:
        """set_status_tsk must write the new status and a fresh `updated` timestamp."""
        original = self.existing_tsk()

        result = set_status_tsk(original.frontmatter.id, "active")

        self.assertEqual(result.frontmatter.status, "active")
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)

    def test_body_is_left_unchanged(self) -> None:
        """set_status_tsk must not alter the body at all."""
        original = self.existing_tsk()

        set_status_tsk(original.frontmatter.id, "active")

        on_disk = parse_tsk(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.body.text, original.body.text)
        self.assertEqual(
            [(item.checked, item.description) for item in on_disk.body.items],
            [(False, "Do the first thing")],
        )

    def test_written_file_round_trips_via_parse_tsk(self) -> None:
        """The updated file on disk must parse back with the new status."""
        original = self.existing_tsk()

        set_status_tsk(original.frontmatter.id, "done")

        on_disk = parse_tsk(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.status, "done")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """set_status_tsk must raise TskNotFoundError for an id with no matching file."""
        with self.assertRaises(TskNotFoundError):
            set_status_tsk("no-such-id", "active")

    def test_invalid_status_raises_and_leaves_file_unchanged(self) -> None:
        """An invalid status must fail validation without writing."""
        original = self.existing_tsk()
        path = self._find_path(original.frontmatter.id)
        before = path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status_tsk(original.frontmatter.id, "not-a-real-status")

        self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
