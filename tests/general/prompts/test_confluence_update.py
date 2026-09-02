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

"""Tests for the ``confluence_update`` ``@mcp.prompt()`` (feat-50-confluence Phase 8,
ACC-011). This prompt never calls the ``confluence_update`` tool itself -- it only
returns instructional text -- so no ``httpx``/tool mocking is needed here.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.prompts.confluence_update import confluence_update
from biz.dfch.specmgr.general.tools import _packaged_data


class TestConfluenceUpdatePrompt(unittest.TestCase):
    """Tests for the confluence_update prompt."""

    def test_mentions_page_url_or_id(self):
        """The page_url_or_id argument must be interpolated into the returned text."""
        result = confluence_update("123456", "/tmp/doc.md")
        self.assertIn("123456", result)

    def test_mentions_markdown_file_path(self):
        """The markdown_file_path argument must be interpolated into the returned text."""
        result = confluence_update("123456", "/tmp/doc.md")
        self.assertIn("/tmp/doc.md", result)

    def test_names_confluence_update_tool(self):
        """The instructions must name the confluence_update tool by name."""
        result = confluence_update("123456", "/tmp/doc.md")
        self.assertIn("`confluence_update` MCP tool", result)

    def test_mentions_version_and_failed_images_report_back(self):
        """The instructions must tell the LLM to report back version/failed_images."""
        result = confluence_update("123456", "/tmp/doc.md")
        self.assertIn("version", result)
        self.assertIn("failed_images", result)

    def test_page_url_can_be_a_browsable_url(self):
        """A full browsable Confluence URL must round-trip unchanged into the text."""
        url = "https://example.atlassian.net/wiki/spaces/DEV/pages/123456/My+Page"
        result = confluence_update(url, "docs/page.md")
        self.assertIn(url, result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from
        general/data/general_confluence_update_instructions.md, not an inline
        Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "general_confluence_update_instructions.md"
            instructions_path.write_text("first $page_url_or_id / $markdown_file_path", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = confluence_update("123456", "/tmp/doc.md")
                instructions_path.write_text("second $page_url_or_id / $markdown_file_path", encoding="utf-8")
                second = confluence_update("123456", "/tmp/doc.md")

            self.assertEqual(first, "first 123456 / /tmp/doc.md")
            self.assertEqual(second, "second 123456 / /tmp/doc.md")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    confluence_update("123456", "/tmp/doc.md")


if __name__ == "__main__":
    unittest.main()
