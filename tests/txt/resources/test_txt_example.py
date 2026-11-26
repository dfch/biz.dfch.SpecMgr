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

"""Tests for the `specmgr://txt/example` resource (`txt.resources.txt_example.txt_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.txt.models.v1 import TxtDocument, parse_txt
from biz.dfch.specmgr.txt.resources.txt_example import txt_example
from biz.dfch.specmgr.txt.tools.get_txt_example import get_txt_example

_EXPECTED_UPDATE_COUNT = 2


class TestTxtExampleResource(unittest.TestCase):
    """Tests for the txt_example resource function."""

    def test_returns_real_packaged_example(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        sut = txt_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: txt", result)
        self.assertIn("# Gateway Incident Review Notes", result)

    def test_matches_packaged_file_byte_for_byte(self) -> None:
        """The resource must equal the packaged txt_example.md byte-for-byte."""
        sut = txt_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("txt", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_txt_example_tool(self) -> None:
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(txt_example(), get_txt_example())

    def test_packaged_example_parses_and_exercises_the_shape(self) -> None:
        """The committed example must parse via parse_txt and exercise the free-form body
        (free H2/H3, the free-floating REQ reference) plus the two ordered ``## Updates``
        entries."""
        document = parse_txt(txt_example())

        self.assertIsInstance(document, TxtDocument)
        self.assertEqual(document.frontmatter.status, "done")

        body_text = document.body.body.text
        self.assertIn("## Findings", body_text)
        self.assertIn("### Root Cause", body_text)
        self.assertIn("REQ deaddead-beef-beef-beef-deaddeadbeef:", body_text)

        updates = document.body.updates.updates
        self.assertEqual(len(updates), _EXPECTED_UPDATE_COUNT)
        self.assertEqual(updates[0].title, "Review complete")
        self.assertEqual(updates[1].title, "Initial draft created")
        # Newest first: the first entry's timestamp must be >= the second's.
        self.assertGreaterEqual(updates[0].timestamp, updates[1].timestamp)

    def test_reads_fresh_on_every_call(self) -> None:
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "txt_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = txt_example

                first = sut()
                example_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_example_missing(self) -> None:
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = txt_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
