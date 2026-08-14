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

"""Tests for the ``req-parse`` command (pure helper + CLI wrapper, exit codes)."""

import io
import json
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import typer

from biz.dfch.specmgr.commands.req_parse import _frontmatter_and_formatted_body, req_parse

_MINIMAL_DOC = textwrap.dedent(
    """\
    ---
    id: req-001
    type: req
    version: 1.0.0
    status: draft
    created: 2026-08-05
    updated: 2026-08-05
    ---

    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

_NO_FRONTMATTER_DOC = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"

_MALFORMED_DOC = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Characteristics

    1. Safety
    """
)


def _write_doc(tmp_dir: str, text: str, name: str = "req.md") -> Path:
    path = Path(tmp_dir) / name
    path.write_text(text, encoding="utf-8")
    return path


class TestFrontmatterAndFormattedBody(unittest.TestCase):
    """Tests for `_frontmatter_and_formatted_body()` in isolation."""

    def test_splits_frontmatter_and_body(self) -> None:
        frontmatter_text, formatted_body = _frontmatter_and_formatted_body(_MINIMAL_DOC)

        self.assertIn("id: req-001", frontmatter_text)
        self.assertIn("status: draft", frontmatter_text)
        self.assertIn("# Maximum Engine Temperature", formatted_body)

    def test_returns_empty_frontmatter_when_absent(self) -> None:
        frontmatter_text, formatted_body = _frontmatter_and_formatted_body(_NO_FRONTMATTER_DOC)

        self.assertEqual(frontmatter_text, "")
        self.assertIn("# Maximum Engine Temperature", formatted_body)

    def test_does_not_modify_original_text(self) -> None:
        original = _MINIMAL_DOC

        _frontmatter_and_formatted_body(_MINIMAL_DOC)

        self.assertEqual(_MINIMAL_DOC, original)


class TestReqParseCommand(unittest.TestCase):
    """Tests for the `req_parse()` Typer command."""

    def test_json_format_prints_parsed_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_doc(tmp, _MINIMAL_DOC)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = req_parse(path=str(path), output_format="json")

            self.assertIsNone(result)
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["frontmatter"]["id"], "req-001")
            self.assertEqual(printed["body"]["text"], "Maximum Engine Temperature")

    def test_json_is_default_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_doc(tmp, _MINIMAL_DOC)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                req_parse(path=str(path))

            json.loads(stdout.getvalue())  # must not raise

    def test_markdown_format_prints_frontmatter_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_doc(tmp, _MINIMAL_DOC)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = req_parse(path=str(path), output_format="markdown")

            self.assertIsNone(result)
            printed = stdout.getvalue()
            self.assertIn("id: req-001", printed)
            self.assertIn("Maximum Engine Temperature", printed)

    def test_unknown_format_exits_1_with_helpful_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_doc(tmp, _MINIMAL_DOC)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(typer.Exit) as ctx:
                    req_parse(path=str(path), output_format="bogus")

            self.assertEqual(ctx.exception.exit_code, 1)
            self.assertIn("bogus", stdout.getvalue())
            self.assertIn("json", stdout.getvalue())
            self.assertIn("markdown", stdout.getvalue())

    def test_missing_file_exits_1_with_original_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = str(Path(tmp) / "does-not-exist.md")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(typer.Exit) as ctx:
                    req_parse(path=missing_path)

            self.assertEqual(ctx.exception.exit_code, 1)
            self.assertIn(missing_path, stdout.getvalue())
            self.assertIn("No such file or directory", stdout.getvalue())

    def test_malformed_structure_exits_1_with_original_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_doc(tmp, _MALFORMED_DOC)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(typer.Exit) as ctx:
                    req_parse(path=str(path))

            self.assertEqual(ctx.exception.exit_code, 1)
            self.assertIn(str(path), stdout.getvalue())

    def test_invalid_frontmatter_exits_1_with_original_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = _MINIMAL_DOC.replace("status: draft", "status: not-a-real-status")
            path = _write_doc(tmp, text)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(typer.Exit) as ctx:
                    req_parse(path=str(path))

            self.assertEqual(ctx.exception.exit_code, 1)
            self.assertIn(str(path), stdout.getvalue())
            self.assertIn("not-a-real-status", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
