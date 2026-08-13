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

"""Tests for the ``mdformat`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.general.tools.mdformat import mdformat


class TestMdformatTool(unittest.TestCase):
    """Tests for the mdformat tool."""

    def test_unformatted_body_returns_true_and_writes(self) -> None:
        """mdformat must return True and write when body needs formatting."""
        unformatted = textwrap.dedent(
            """\
            # Title

            Some   text   with    extra  spacing.
            More text here.
            """
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(unformatted, encoding="utf-8")

            result = mdformat(str(path))

            self.assertTrue(result, "mdformat must return True when file is changed")
            content = path.read_text(encoding="utf-8")
            self.assertIn("Some text with extra spacing.", content)
            self.assertTrue(content.endswith("\n"))

    def test_already_formatted_returns_false_and_doesnt_write(self) -> None:
        """mdformat must return False and not write when file is already formatted."""
        formatted = "# Title\n\nSome text.\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(formatted, encoding="utf-8")
            original_mtime = path.stat().st_mtime

            result = mdformat(str(path))

            self.assertFalse(result, "mdformat must return False when no changes needed")
            # Read back to verify no changes.
            content = path.read_text(encoding="utf-8")
            self.assertEqual(content, formatted)
            # Verify mtime unchanged (file was not written).
            self.assertEqual(path.stat().st_mtime, original_mtime)

    def test_frontmatter_preserved_body_reformatted(self) -> None:
        """mdformat must preserve frontmatter and reformat body markdown."""
        unformatted = textwrap.dedent(
            """\
            ---
            id: uc-001
            type: uc
            status: draft
            ---

            # Use Case Title

            Some   text   with    spacing.

            1) first item
            2) second item
            """
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(unformatted, encoding="utf-8")

            result = mdformat(str(path))

            self.assertTrue(result)
            content = path.read_text(encoding="utf-8")
            # Frontmatter should still be present and parseable.
            self.assertIn("---", content)
            self.assertIn("id: uc-001", content)
            self.assertIn("type: uc", content)
            # Body should be reformatted.
            self.assertIn("Some text with spacing.", content)
            # Lists should be normalized to "1." and "2.".
            self.assertIn("1. first item", content)
            self.assertIn("2. second item", content)
            self.assertTrue(content.endswith("\n"))

    def test_no_frontmatter_still_works(self) -> None:
        """mdformat must handle files without frontmatter."""
        unformatted = textwrap.dedent(
            """\
            # Title

            Some   text   with    extra   spaces.
            """
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(unformatted, encoding="utf-8")

            result = mdformat(str(path))

            self.assertTrue(result)
            content = path.read_text(encoding="utf-8")
            self.assertIn("Some text with extra spaces.", content)
            self.assertTrue(content.endswith("\n"))

    def test_idempotency_second_call_returns_false(self) -> None:
        """mdformat must be idempotent: formatting twice, second call returns False."""
        unformatted = textwrap.dedent(
            """\
            ---
            id: test
            type: adr
            ---

            # Title

            Some   text   with    spacing.
            """
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(unformatted, encoding="utf-8")

            result1 = mdformat(str(path))
            self.assertTrue(result1, "first call should return True")

            result2 = mdformat(str(path))
            self.assertFalse(result2, "second call should return False (already formatted)")

    def test_raises_for_nonexistent_file(self) -> None:
        """mdformat must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            mdformat("/nonexistent/path/to/file.md")

    def test_trailing_newline_enforced(self) -> None:
        """mdformat must ensure exactly one trailing newline."""
        # File without trailing newline.
        no_newline = "# Title\n\nText."
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(no_newline, encoding="utf-8")

            result = mdformat(str(path))

            self.assertTrue(result)
            content = path.read_text(encoding="utf-8")
            self.assertTrue(content.endswith("\n"))
            # And should be idempotent.
            result2 = mdformat(str(path))
            self.assertFalse(result2)

    def test_frontmatter_reserialize_preserves_content(self) -> None:
        """mdformat must preserve frontmatter field values despite re-serialization."""
        original = textwrap.dedent(
            """\
            ---
            id: adr-12345
            type: adr
            status: accepted
            date: 2026-08-13
            ---

            # ADR Title

            Some content.
            """
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(original, encoding="utf-8")

            mdformat(str(path))

            content = path.read_text(encoding="utf-8")
            # All frontmatter fields should be present with correct values.
            self.assertIn("id: adr-12345", content)
            self.assertIn("type: adr", content)
            self.assertIn("status: accepted", content)
            self.assertIn("date: 2026-08-13", content)


if __name__ == "__main__":
    unittest.main()
