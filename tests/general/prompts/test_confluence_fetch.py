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

"""Tests for the ``confluence_fetch`` ``@mcp.prompt()`` (feat-50-confluence Phase 8,
ACC-012). This prompt never calls the ``confluence_fetch`` tool itself -- it only
returns instructional text -- so no ``httpx``/tool mocking is needed here.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.prompts.confluence_fetch import confluence_fetch
from biz.dfch.specmgr.general.tools import _packaged_data

_PAGE_URL = "https://example.atlassian.net/wiki/spaces/DEV/pages/123456/My+Page"


class TestConfluenceFetchPrompt(unittest.TestCase):
    """Tests for the confluence_fetch prompt."""

    def test_mentions_url(self):
        """The url argument must be interpolated into the returned text."""
        result = confluence_fetch(_PAGE_URL)
        self.assertIn(_PAGE_URL, result)

    def test_names_confluence_fetch_tool(self):
        """The instructions must name the confluence_fetch tool by name."""
        result = confluence_fetch(_PAGE_URL)
        self.assertIn("`confluence_fetch` MCP tool", result)

    def test_destination_path_given_is_interpolated(self):
        """A given destination_path must appear verbatim in the returned text."""
        result = confluence_fetch(_PAGE_URL, destination_path="/tmp/image.png")
        self.assertIn("/tmp/image.png", result)

    def test_destination_path_none_uses_explanatory_placeholder(self):
        """Omitted destination_path must not be blank -- an explanatory placeholder is used."""
        result = confluence_fetch(_PAGE_URL)
        self.assertIn("not given", result)
        self.assertNotIn("$destination_path", result)

    def test_mentions_binary_content_requirement(self):
        """The instructions must explain destination_path is only needed for binary content."""
        result = confluence_fetch(_PAGE_URL)
        self.assertIn("binary", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from
        general/data/general_confluence_fetch_instructions.md, not an inline
        Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "general_confluence_fetch_instructions.md"
            instructions_path.write_text("first $url / $destination_path", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = confluence_fetch(_PAGE_URL, destination_path="/tmp/a.png")
                instructions_path.write_text("second $url / $destination_path", encoding="utf-8")
                second = confluence_fetch(_PAGE_URL, destination_path="/tmp/a.png")

            self.assertEqual(first, f"first {_PAGE_URL} / /tmp/a.png")
            self.assertEqual(second, f"second {_PAGE_URL} / /tmp/a.png")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    confluence_fetch(_PAGE_URL)


if __name__ == "__main__":
    unittest.main()
