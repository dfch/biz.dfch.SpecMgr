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

"""Tests for the ``schema`` command (generator + CLI, ``--type``/no-option, exit codes)."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import typer

from biz.dfch.specmgr.commands.schema import _GENERATORS, generate_req_schema, schema


class TestGenerateReqSchema(unittest.TestCase):
    """Tests for `generate_req_schema()` in isolation."""

    def test_returns_valid_json(self):
        """The generated string must parse as JSON."""
        result = generate_req_schema()
        json.loads(result)  # must not raise

    def test_ends_with_trailing_newline(self):
        """Output must end with exactly one trailing newline."""
        result = generate_req_schema()
        self.assertTrue(result.endswith("\n"))
        self.assertFalse(result.endswith("\n\n"))

    def test_schema_dialect_is_2020_12(self):
        """`$schema` must be the JSON Schema 2020-12 URI, not draft-07."""
        result = json.loads(generate_req_schema())
        self.assertEqual(result["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_comment_is_schema_layout_version(self):
        """`$comment` must be the bare schema-layout version token (currently 'v1')."""
        result = json.loads(generate_req_schema())
        self.assertEqual(result["$comment"], "v1")

    def test_contains_frontmatter_and_body_properties(self):
        """Top-level `ReqDocument` schema must expose `frontmatter`/`body` as required properties."""
        result = json.loads(generate_req_schema())
        self.assertIn("frontmatter", result["properties"])
        self.assertIn("body", result["properties"])
        self.assertIn("frontmatter", result["required"])
        self.assertIn("body", result["required"])

    def test_is_deterministic_across_calls(self):
        """Two independent calls must produce byte-identical output."""
        self.assertEqual(generate_req_schema(), generate_req_schema())

    def test_registered_under_req_in_generators(self):
        """The generator registry must expose this function under the 'req' key."""
        self.assertIs(_GENERATORS["req"], generate_req_schema)


class TestSchemaCommand(unittest.TestCase):
    """Tests for the `schema()` Typer command."""

    def test_writes_req_schema_json_by_default(self):
        """With no `--type`, all registered types (today: just req) must be written."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit):
                    schema(type_=None, output_dir=output_dir)

            written = output_dir / "req_schema.json"
            self.assertTrue(written.exists())
            json.loads(written.read_text(encoding="utf-8"))  # must be valid JSON

    def test_type_req_writes_only_req_schema(self):
        """`--type req` must restrict generation to req_schema.json."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit):
                    schema(type_="req", output_dir=output_dir)

            self.assertEqual([p.name for p in output_dir.iterdir()], ["req_schema.json"])

    def test_unknown_type_exits_1_with_helpful_message(self):
        """An unregistered `--type` value must exit 1 without writing anything."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(typer.Exit) as ctx:
                    schema(type_="bogus", output_dir=output_dir)

            self.assertEqual(ctx.exception.exit_code, 1)
            self.assertIn("bogus", stdout.getvalue())
            self.assertFalse(any(output_dir.iterdir()))

    def test_exit_code_1_when_file_did_not_exist_before(self):
        """First-ever generation (no prior file) must exit 1 -- content 'differs' from absent."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit) as ctx:
                    schema(type_="req", output_dir=output_dir)

            self.assertEqual(ctx.exception.exit_code, 1)

    def test_exit_code_0_when_content_unchanged(self):
        """A second run against already-up-to-date output must exit 0 (no `typer.Exit` raised)."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit):
                    schema(type_="req", output_dir=output_dir)  # first run: creates the file

            with redirect_stdout(io.StringIO()):
                result = schema(type_="req", output_dir=output_dir)  # second run: unchanged

            self.assertIsNone(result)

    def test_exit_code_1_when_on_disk_content_differs(self):
        """A stale on-disk file (different content) must be overwritten and exit 1."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            output_dir.mkdir(exist_ok=True)
            stale_path = output_dir / "req_schema.json"
            stale_path.write_text('{"stale": true}\n', encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit) as ctx:
                    schema(type_="req", output_dir=output_dir)

            self.assertEqual(ctx.exception.exit_code, 1)
            written = json.loads(stale_path.read_text(encoding="utf-8"))
            self.assertNotIn("stale", written)

    def test_reports_changed_and_unchanged_in_output(self):
        """stdout must distinguish a changed write from an unchanged one."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)

            first_stdout = io.StringIO()
            with redirect_stdout(first_stdout):
                with self.assertRaises(typer.Exit):
                    schema(type_="req", output_dir=output_dir)
            self.assertIn("(changed)", first_stdout.getvalue())

            second_stdout = io.StringIO()
            with redirect_stdout(second_stdout):
                schema(type_="req", output_dir=output_dir)
            self.assertIn("(unchanged)", second_stdout.getvalue())

    def test_creates_output_dir_if_missing(self):
        """A nonexistent --output-dir must be created rather than raising."""
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "nested" / "docs"
            self.assertFalse(output_dir.exists())

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit):
                    schema(type_="req", output_dir=output_dir)

            self.assertTrue((output_dir / "req_schema.json").exists())


if __name__ == "__main__":
    unittest.main()
