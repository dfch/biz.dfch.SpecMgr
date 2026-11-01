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


"""Tests for the ``get_sop_schema`` ``@mcp.tool()`` wrapper (feat-189 Phase 105, ADR
112b6498-078b-4a59-88b8-8ffb7a5041b3)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr._paths import REPO_ROOT
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.sop.tools.get_sop_schema import get_sop_schema

#: The schema-layout version marker the generated SOP schema carries
#: (its ``sop/models/vN``-derived layout).
_EXPECTED_COMMENT = "v1"

#: The JSON Schema dialect every generated schema declares.
_EXPECTED_DIALECT = "https://json-schema.org/draft/2020-12/schema"


class TestGetSOPSchemaTool(unittest.TestCase):
    """Tests for the get_sop_schema tool."""

    def test_returns_real_packaged_schema(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_sop_schema()

        self.assertIsInstance(result, str)
        data = json.loads(result)
        self.assertEqual(data["$comment"], _EXPECTED_COMMENT)
        self.assertEqual(data["$schema"], _EXPECTED_DIALECT)
        self.assertIn("frontmatter", data["properties"])
        self.assertIn("body", data["properties"])

    def test_output_byte_identical_to_docs_schema(self) -> None:
        """The tool's output must be byte-identical to docs/sop_schema.json."""
        docs_path = REPO_ROOT / "docs" / "sop_schema.json"

        result = get_sop_schema()

        self.assertEqual(result, docs_path.read_text(encoding="utf-8"))

    def test_output_byte_identical_to_packaged_copy(self) -> None:
        """The tool's output must be byte-identical to the packaged data copy
        read through _packaged_data.read_packaged_text."""
        result = get_sop_schema()

        packaged = _packaged_data.read_packaged_text("sop", "schema", "json")

        self.assertEqual(result, packaged)

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "sop_schema.json"
            schema_path.write_text('{"$comment": "v99"}\n', encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=schema_path):
                result = get_sop_schema()

            self.assertEqual(result, '{"$comment": "v99"}\n')

    def test_raises_file_not_found_when_schema_missing(self) -> None:
        """A missing packaged schema file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_sop_schema()


if __name__ == "__main__":
    unittest.main()
