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

"""Tests for ``tsk.tools._io`` (thin file read helpers)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.tsk.models.v1 import TskDocument
from biz.dfch.specmgr.tsk.tools._io import load_by_id, read_tsk
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: tsk
    version: 1.0.0
    status: draft
    created: '2026-08-16 00:00:00.000Z'
    updated: '2026-08-16 00:00:00.000Z'
    ---

    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### 2026-08-19 - Kickoff

    Started the task list.
    """
)


def _tsk_text(id_: str) -> str:
    """Render a minimal, valid task list document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReadTsk(unittest.TestCase):
    """Tests for read_tsk."""

    def test_reads_and_parses_a_real_file(self):
        """read_tsk must return a TskDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_tsk_text("some-id"), encoding="utf-8")

            document = read_tsk(path)

            self.assertIsInstance(document, TskDocument)
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.body.text, "Simple Task List")


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_tsk(self):
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            expected_path.write_text(_tsk_text("the-id"), encoding="utf-8")

            path, document = load_by_id(base, "the-id")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self):
        """load_by_id must raise TskNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(TskNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
