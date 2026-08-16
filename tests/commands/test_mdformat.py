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

"""Tests for the ``mdformat`` CLI command (exit codes, ``--dry-run``, no-write vs. write)."""

from __future__ import annotations

import io
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import typer

from biz.dfch.specmgr.commands.mdformat import mdformat

_UNFORMATTED = textwrap.dedent(
    """\
    # Title

    Some   text   with    extra  spacing.

    1) first item
    2) second item
    """
)

_FORMATTED = "# Title\n\nSome text.\n"


def _write(tmp_dir: str, text: str, name: str = "test.md") -> Path:
    path = Path(tmp_dir) / name
    path.write_text(text, encoding="utf-8")
    return path


class TestMdformatCommand(unittest.TestCase):
    """Tests for the `mdformat()` Typer command."""

    def test_changed_file_writes_and_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, _UNFORMATTED)

            with self.assertRaises(typer.Exit) as ctx:
                mdformat(path)

            self.assertEqual(ctx.exception.exit_code, 1)
            content = path.read_text(encoding="utf-8")
            self.assertIn("Some text with extra spacing.", content)
            self.assertIn("1. first item", content)
            self.assertIn("2. second item", content)

    def test_unchanged_file_does_not_raise_and_leaves_file_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, _FORMATTED)
            original_mtime = path.stat().st_mtime

            result = mdformat(path)  # type: ignore

            self.assertIsNone(result)
            self.assertEqual(path.read_text(encoding="utf-8"), _FORMATTED)
            self.assertEqual(path.stat().st_mtime, original_mtime)

    def test_dry_run_changed_file_does_not_write_but_exits_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, _UNFORMATTED)
            original_mtime = path.stat().st_mtime

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(typer.Exit) as ctx:
                    mdformat(path, dry_run=True)

            self.assertEqual(ctx.exception.exit_code, 1)
            # File on disk must be untouched.
            self.assertEqual(path.read_text(encoding="utf-8"), _UNFORMATTED)
            self.assertEqual(path.stat().st_mtime, original_mtime)
            # Formatted content shown on the console.
            printed = stdout.getvalue()
            self.assertIn("Some text with extra spacing.", printed)

    def test_dry_run_unchanged_file_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, _FORMATTED)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = mdformat(path, dry_run=True)  # type: ignore

            self.assertIsNone(result)
            self.assertEqual(path.read_text(encoding="utf-8"), _FORMATTED)
            self.assertEqual("", stdout.getvalue())

    def test_frontmatter_preserved_body_reformatted(self) -> None:
        unformatted = textwrap.dedent(
            """\
            ---
            id: adr-001
            type: adr
            status: draft
            ---

            # ADR Title

            Some   text   with    spacing.
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(tmp, unformatted)

            with self.assertRaises(typer.Exit) as ctx:
                mdformat(path)

            self.assertEqual(ctx.exception.exit_code, 1)
            content = path.read_text(encoding="utf-8")
            self.assertIn("id: adr-001", content)
            self.assertIn("type: adr", content)
            self.assertIn("Some text with spacing.", content)

    def test_missing_file_propagates_uncaught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with self.assertRaises(FileNotFoundError):
                mdformat(path=missing_path)


if __name__ == "__main__":
    unittest.main()
