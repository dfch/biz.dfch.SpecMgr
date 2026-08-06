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

"""Tests for MdStr feature exploration.

This module contains exploratory tests for the Markdown string type feature (feat-4).
These tests are for validation purposes and will be adapted or removed once the
MdStr implementation is complete.
"""

import unittest
from pathlib import Path


class TestMdStrExploration(unittest.TestCase):
    """Exploratory tests for MdStr feature validation."""

    @staticmethod
    def read_markdown_file(file_path: Path) -> str | None:
        """Read content from a markdown file if it exists.

        Args:
            file_path: Path to the markdown file

        Returns:
            File content as string, or None if file doesn't exist
        """
        path = Path(file_path)
        if path.exists() and path.is_file():
            try:
                return path.read_text(encoding="utf-8")
            except UnicodeDecodeError as e:
                print(f"Error reading {file_path}: {e}")
                return None
        return None

    def test_read_local_md_file(self):
        """Test reading a local markdown file for MdStr exploration.

        This test verifies we can successfully read a markdown file from disk.
        The file path can be updated with actual test cases as needed.
        """

        test_file = Path(__file__).parent / Path("./uc_example.md")

        content = TestMdStrExploration.read_markdown_file(test_file)

        # Basic validation - file should exist and contain text
        if content is None:
            print(f"No markdown file found at: {test_file}")
            print("This is expected if no test files exist yet.")
            self.skipTest("No test markdown file available")

        self.assertIsInstance(content, str)
        self.assertGreater(len(content.strip()), 0)
        print(f"Successfully read markdown file: {test_file}")
        print(f"Content length: {len(content)} characters")


if __name__ == "__main__":
    unittest.main()
