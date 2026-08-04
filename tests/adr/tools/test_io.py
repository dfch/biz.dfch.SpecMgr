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

"""Tests for ``adr.tools._io`` (thin file read/write helpers)."""

import tempfile
import unittest
from pathlib import Path

from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter
from biz.dfch.specmgr.adr.tools._io import load_by_id, read_adr, write_adr
from biz.dfch.specmgr.adr.tools._paths import AdrNotFoundError


def _adr(id_: str | None = None) -> Adr:
    return Adr(
        frontmatter=AdrFrontmatter(id=id_, status="accepted"),
        body=AdrBody(
            title="A title",
            context_and_problem_statement="Context.",
            considered_options="Options.",
            decision_outcome="Outcome.",
        ),
    )


class TestReadWriteAdr(unittest.TestCase):
    """Tests for read_adr/write_adr round-tripping through a real file."""

    def test_write_then_read_round_trips(self):
        """Writing an Adr and reading it back must reproduce the same document."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            original = _adr(id_="some-id")
            write_adr(path, original)
            self.assertTrue(path.exists())
            reread = read_adr(path)
            self.assertEqual(reread, original)


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_adr(self):
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            write_adr(expected_path, _adr(id_="the-id"))
            path, adr = load_by_id(base, "the-id")
            self.assertEqual(path, expected_path)
            self.assertEqual(adr.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self):
        """load_by_id must raise AdrNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(AdrNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
