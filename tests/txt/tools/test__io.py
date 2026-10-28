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

"""Tests for ``txt.tools._io`` (thin file read helpers)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.txt.models.v1 import TxtDocument
from biz.dfch.specmgr.txt.tools._io import load_by_id, read_txt
from biz.dfch.specmgr.txt.tools._paths import TxtNotFoundError

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: txt
    version: 1.0.0
    status: draft
    created: '2026-08-31T00:00:00.000Z'
    updated: '2026-08-31T00:00:00.000Z'
    ---

    # Sample Review Notes

    Some free-form prose about what was reviewed.

    ## Updates

    ### 2026-08-31 00:00:00.000Z - Created

    Initial draft of the review notes.
    """
)


def _txt_text(id_: str) -> str:
    """Render a minimal, valid free-form text document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReadTxt(unittest.TestCase):
    """Tests for read_txt."""

    def test_reads_and_parses_a_real_file(self) -> None:
        """read_txt must return a TxtDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_txt_text("some-id"), encoding="utf-8")

            document = read_txt(path)

            self.assertIsInstance(document, TxtDocument)
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.body.text, "Sample Review Notes")


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_txt(self) -> None:
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            expected_path.write_text(_txt_text("the-id"), encoding="utf-8")

            path, document = load_by_id(base, "the-id")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """load_by_id must raise TxtNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(TxtNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
