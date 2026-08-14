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

"""Tests for `req._data.read_req_example_text`/`read_req_template_text`/`read_req_schema_text`
(Tasks 3.6, 3.7, 3.8)."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.req import _data
from biz.dfch.specmgr.req._data import read_req_example_text, read_req_schema_text, read_req_template_text


class TestReadReqExampleText(unittest.TestCase):
    """Tests for the packaged REQ example reader."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = read_req_example_text

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)
        self.assertIn("# Maximum Engine Temperature", result)

    def test_returns_content_for_a_given_file(self):
        """A patched-in example file's exact content must round-trip verbatim."""
        payload = "---\ntype: req\n---\n\n# Title\n\nBody text.\n"
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "req_example.md"
            example_path.write_text(payload, encoding="utf-8")

            with mock.patch.object(_data, "_EXAMPLE_PATH", example_path):
                sut = read_req_example_text

                result = sut()

            self.assertEqual(result, payload)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "req_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_data, "_EXAMPLE_PATH", example_path):
                sut = read_req_example_text

                first = sut()
                example_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_example_missing(self):
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_data, "_EXAMPLE_PATH", missing_path):
                sut = read_req_example_text

                with self.assertRaises(FileNotFoundError):
                    sut()


class TestReadReqTemplateText(unittest.TestCase):
    """Tests for the packaged REQ template reader (Task 3.7)."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = read_req_template_text

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)
        self.assertIn("# Level 1 Heading is the Title of the Requirement", result)

    def test_returns_content_for_a_given_file(self):
        """A patched-in template file's exact content must round-trip verbatim."""
        payload = "---\ntype: req\n---\n\n# Title\n\nBody text.\n"
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "req_template.md"
            template_path.write_text(payload, encoding="utf-8")

            with mock.patch.object(_data, "_TEMPLATE_PATH", template_path):
                sut = read_req_template_text

                result = sut()

            self.assertEqual(result, payload)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "req_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_data, "_TEMPLATE_PATH", template_path):
                sut = read_req_template_text

                first = sut()
                template_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_template_missing(self):
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_data, "_TEMPLATE_PATH", missing_path):
                sut = read_req_template_text

                with self.assertRaises(FileNotFoundError):
                    sut()


class TestReadReqSchemaText(unittest.TestCase):
    """Tests for the packaged REQ JSON Schema reader (Task 3.8)."""

    def test_returns_real_packaged_schema(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = read_req_schema_text

        result = sut()

        parsed = json.loads(result)
        self.assertEqual(parsed["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(parsed["$comment"], "v1")

    def test_returns_content_for_a_given_file(self):
        """A patched-in schema file's exact content must round-trip verbatim."""
        payload = json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "$comment": "v1"})
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "req_schema.json"
            schema_path.write_text(payload, encoding="utf-8")

            with mock.patch.object(_data, "_SCHEMA_PATH", schema_path):
                sut = read_req_schema_text

                result = sut()

            self.assertEqual(result, payload)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "req_schema.json"
            schema_path.write_text('{"$comment": "v1"}', encoding="utf-8")

            with mock.patch.object(_data, "_SCHEMA_PATH", schema_path):
                sut = read_req_schema_text

                first = sut()
                schema_path.write_text('{"$comment": "v2"}', encoding="utf-8")
                second = sut()

            self.assertEqual(json.loads(first)["$comment"], "v1")
            self.assertEqual(json.loads(second)["$comment"], "v2")

    def test_raises_file_not_found_when_schema_missing(self):
        """A missing packaged schema file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"

            with mock.patch.object(_data, "_SCHEMA_PATH", missing_path):
                sut = read_req_schema_text

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
