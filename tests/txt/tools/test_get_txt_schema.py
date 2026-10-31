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

"""Tests for the ``get_txt_schema`` ``@mcp.tool()`` wrapper (feat-229-txt Phase 110).

The packaged ``txt_schema.json`` was generated (not hand-written) from
``TxtDocument.model_json_schema()`` with EXACTLY the formatting
``commands/schema.py`` uses for every other domain (``json.dumps(schema_dict,
indent=2, sort_keys=True) + "\\n"`` plus the ``$schema``/``$comment``
injections). ``test_output_matches_regenerated_schema`` pins that byte
identity here, which the ``commands/schema.py`` ``generate_txt_schema`` CLI
entry (feat-229-txt Phase 160) and the pre-commit
``specmgr-schema-txt-package`` hook/CI step keeping the packaged copy in
sync with ``docs/txt_schema.json`` rely on.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pydantic.json_schema import GenerateJsonSchema

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.txt.models.v1 import SCHEMA_COMMENT_VERSION, TxtDocument
from biz.dfch.specmgr.txt.tools.get_txt_schema import get_txt_schema

#: The JSON Schema dialect every generated schema declares.
_EXPECTED_DIALECT = "https://json-schema.org/draft/2020-12/schema"


def _regenerated_schema_text() -> str:
    """Regenerate TXT's schema in memory, exactly as ``commands/schema.py``'s per-domain generators do."""
    schema_dict = TxtDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = SCHEMA_COMMENT_VERSION
    result = json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"
    return result


class TestGetTxtSchemaTool(unittest.TestCase):
    """Tests for the get_txt_schema tool."""

    def test_returns_real_packaged_schema(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_txt_schema()

        self.assertIsInstance(result, str)
        data = json.loads(result)
        self.assertEqual(data["$comment"], SCHEMA_COMMENT_VERSION)
        self.assertEqual(data["$schema"], _EXPECTED_DIALECT)
        self.assertIn("frontmatter", data["properties"])
        self.assertIn("body", data["properties"])

    def test_output_matches_regenerated_schema(self) -> None:
        """The packaged schema must be byte-identical to an in-memory regeneration from
        ``TxtDocument.model_json_schema()`` with ``commands/schema.py``'s exact formatting
        (the Phase 160 ``generate_txt_schema`` entry reproduces this same text)."""
        self.assertEqual(get_txt_schema(), _regenerated_schema_text())

    def test_output_byte_identical_to_packaged_copy(self) -> None:
        """The tool's output must be byte-identical to the packaged data copy
        read through _packaged_data.read_packaged_text."""
        result = get_txt_schema()

        packaged = _packaged_data.read_packaged_text("txt", "schema", "json")

        self.assertEqual(result, packaged)

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "txt_schema.json"
            schema_path.write_text('{"$comment": "v99"}\n', encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=schema_path):
                result = get_txt_schema()

            self.assertEqual(result, '{"$comment": "v99"}\n')

    def test_raises_file_not_found_when_schema_missing(self) -> None:
        """A missing packaged schema file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_txt_schema()


if __name__ == "__main__":
    unittest.main()
