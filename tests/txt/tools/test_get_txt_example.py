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

"""Tests for the ``get_txt_example`` ``@mcp.tool()`` wrapper (feat-229-txt Phase 110, real packaged data).

The packaged-data ``specmgr://txt/example`` resource (Phase 120) will add its
own resource-level tests; this module pins the tool half: the real committed
file parses green through ``txt.models.v1.parser.parse_txt`` and is
byte-stable under parse -> re-render (the mdformat-clean property).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import frontmatter

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.txt.models.v1 import TxtDocument, parse_txt
from biz.dfch.specmgr.txt.tools.get_txt_example import get_txt_example

_EXPECTED_UPDATE_COUNT = 2


class TestGetTxtExampleTool(unittest.TestCase):
    """Tests for the get_txt_example tool."""

    def test_returns_real_packaged_example(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_txt_example()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: txt", result)
        self.assertIn("# Gateway Incident Review Notes", result)

    def test_packaged_example_parses_green_and_exercises_the_shape(self) -> None:
        """The committed example must parse via parse_txt and exercise the free-form body
        (free H2/H3, a list, the free-floating REQ reference) plus the two ordered
        ``## Updates`` entries."""
        document = parse_txt(get_txt_example())

        self.assertIsInstance(document, TxtDocument)
        self.assertEqual(document.frontmatter.type, "txt")
        self.assertEqual(document.frontmatter.status, "done")
        self.assertEqual(document.body.text, "Gateway Incident Review Notes")

        body_text = document.body.body.text
        self.assertIn("## Findings", body_text)
        self.assertIn("### Root Cause", body_text)
        self.assertIn("- The gateway logged the revocation request 40 ms after the agent action.", body_text)
        self.assertIn("REQ deaddead-beef-beef-beef-deaddeadbeef:", body_text)

        updates = document.body.updates.updates
        self.assertEqual(len(updates), _EXPECTED_UPDATE_COUNT)
        self.assertEqual(updates[0].title, "Review complete")
        self.assertEqual(updates[1].title, "Initial draft created")
        # Newest first: the first entry's timestamp must be >= the second's.
        self.assertGreaterEqual(updates[0].timestamp, updates[1].timestamp)

    def test_packaged_example_is_byte_stable_under_parse_re_render(self) -> None:
        """The committed example's body must already be in the engine's canonical (mdformat)
        form: the re-rendered body equals the mdformat-normalized body byte-for-byte
        (pins the mdformat-clean property the Phase 120 resource tests will reuse)."""
        text = get_txt_example()
        document = parse_txt(text)
        raw_body = frontmatter.loads(text).content
        assert isinstance(raw_body, str)

        self.assertEqual(str(document.body), format_text(raw_body))
        # frontmatter.loads strips the file's single trailing newline, so the
        # on-disk body is the normalized form minus that one newline.
        self.assertEqual(raw_body + "\n", format_text(raw_body))

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "txt_example.md"
            example_path.write_text("---\ntype: txt\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                result = get_txt_example()

            self.assertEqual(result, "---\ntype: txt\n---\n\n# Title\n")

    def test_raises_file_not_found_when_example_missing(self) -> None:
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_txt_example()


if __name__ == "__main__":
    unittest.main()
