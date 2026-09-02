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

"""Tests for the ``get_sysrs_template`` ``@mcp.tool()`` wrapper (Task 3.2, mock-only this phase).

The real packaged ``sysrs_template.md`` data file does not exist yet as of
Phase 3 -- it arrives in Phase 4 (``sysrs/data/``, Task 4.2) -- so, unlike
the shipped `vcr`/`sop` domains' own tests, there is no "against the real,
committed packaged data file" test here yet; that test is added once Phase
4 ships the real file.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.sysrs.tools.get_sysrs_template import get_sysrs_template


class TestGetSysrsTemplateTool(unittest.TestCase):
    """Tests for the get_sysrs_template tool."""

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "sysrs_template.md"
            template_path.write_text("---\ntype: sysrs\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                result = get_sysrs_template()

            self.assertEqual(result, "---\ntype: sysrs\n---\n\n# Title\n")

    def test_raises_file_not_found_when_template_missing(self) -> None:
        """A missing packaged template file must propagate FileNotFoundError uncaught (expected this phase)."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_sysrs_template()

    def test_no_real_packaged_data_yet(self) -> None:
        """The real packaged sysrs_template.md does not exist yet this phase -- calling without mocks raises."""
        with self.assertRaises(FileNotFoundError):
            get_sysrs_template()


if __name__ == "__main__":
    unittest.main()
