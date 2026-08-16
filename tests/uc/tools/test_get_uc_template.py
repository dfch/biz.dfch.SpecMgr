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

"""Tests for the ``get_uc_template`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.uc.tools.get_uc_template import get_uc_template


class TestGetUcTemplateTool(unittest.TestCase):
    """Tests for the get_uc_template tool."""

    def test_returns_real_packaged_template(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_uc_template()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: uc", result)
        self.assertIn("# Level 1 Heading is the Name of the Use Case", result)

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "uc_template.md"
            template_path.write_text("---\ntype: uc\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                result = get_uc_template()

            self.assertEqual(result, "---\ntype: uc\n---\n\n# Title\n")

    def test_raises_file_not_found_when_template_missing(self) -> None:
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_uc_template()


if __name__ == "__main__":
    unittest.main()
