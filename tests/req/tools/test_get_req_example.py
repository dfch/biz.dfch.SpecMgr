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

"""Tests for the ``get_req_example`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.req import _data
from biz.dfch.specmgr.req.tools.get_req_example import get_req_example


class TestGetReqExampleTool(unittest.TestCase):
    """Tests for the get_req_example tool."""

    def test_returns_real_packaged_example(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_req_example()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)
        self.assertIn("# Maximum Engine Temperature", result)

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever req._data.read_req_example_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "req_example.md"
            example_path.write_text("---\ntype: req\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_data, "_EXAMPLE_PATH", example_path):
                result = get_req_example()

            self.assertEqual(result, "---\ntype: req\n---\n\n# Title\n")

    def test_raises_file_not_found_when_example_missing(self) -> None:
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_data, "_EXAMPLE_PATH", missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_req_example()


if __name__ == "__main__":
    unittest.main()
