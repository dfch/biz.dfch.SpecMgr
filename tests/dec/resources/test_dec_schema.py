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

"""Tests for the `specmgr://dec/schema` resource (`dec.resources.dec_schema.dec_schema`)."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.commands.schema import generate_dec_schema
from biz.dfch.specmgr.dec.models.v1 import SCHEMA_COMMENT_VERSION
from biz.dfch.specmgr.dec.resources.dec_schema import dec_schema
from biz.dfch.specmgr.general.tools import _packaged_data

_DIALECT = "https://json-schema.org/draft/2020-12/schema"


class TestDecSchemaResource(unittest.TestCase):
    """Tests for the `dec_schema` resource function."""

    def test_returns_parsed_repo_schema_by_default(self):
        """Against the real, committed packaged dec_schema.json, without any patching."""
        sut = dec_schema

        result = sut()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["$comment"], SCHEMA_COMMENT_VERSION)
        self.assertEqual(result["$schema"], _DIALECT)
        self.assertIn("frontmatter", result["properties"])
        self.assertIn("body", result["properties"])

    def test_matches_fresh_generate_dec_schema_output(self):
        """ACC-004: the resource must equal a fresh `generate_dec_schema()` output (parsed JSON)."""
        sut = dec_schema

        result = sut()

        self.assertEqual(result, json.loads(generate_dec_schema()))

    def test_returns_parsed_dict_for_a_given_file(self):
        """A patched-in schema file's exact content must round-trip through json.loads."""
        payload = {"$schema": _DIALECT, "$comment": SCHEMA_COMMENT_VERSION, "properties": {}}
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "dec_schema.json"
            schema_path.write_text(json.dumps(payload), encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=schema_path):
                sut = dec_schema

                result = sut()

            self.assertEqual(result, payload)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "dec_schema.json"
            schema_path.write_text(json.dumps({"$comment": "v1"}), encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=schema_path):
                sut = dec_schema

                first = sut()
                schema_path.write_text(json.dumps({"$comment": "v2"}), encoding="utf-8")
                second = sut()

            self.assertEqual(first["$comment"], "v1")
            self.assertEqual(second["$comment"], "v2")

    def test_raises_file_not_found_when_schema_missing(self):
        """A missing packaged dec_schema.json must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = dec_schema

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_json_decode_error_for_corrupted_file(self):
        """Corrupted (non-JSON) content on disk must propagate json.JSONDecodeError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "dec_schema.json"
            schema_path.write_text("{not valid json", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=schema_path):
                sut = dec_schema

                with self.assertRaises(json.JSONDecodeError):
                    sut()


if __name__ == "__main__":
    unittest.main()
