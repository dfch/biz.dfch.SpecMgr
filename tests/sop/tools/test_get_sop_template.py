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

"""Tests for the ``get_sop_template`` ``@mcp.tool()`` wrapper (Task 2.2, real packaged data from Task 3.2).

Mock-based only in Phase 2: the real packaged template data file
(``sop/data/sop_template.md``) is created in Phase 3 (Task 3.2), so a
``test_returns_real_packaged_template``-style test against the committed
data file is deliberately deferred to Phase 3 -- it would raise
``FileNotFoundError`` here. The two mock-based methods below verify the
tool's delegation to the shared packaged-data reader and its
let-it-raise behaviour on a missing file, without requiring the real data
file to exist yet.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.sop.tools.get_sop_template import get_sop_template


class TestGetSopTemplateTool(unittest.TestCase):
    """Tests for the get_sop_template tool."""

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "sop_template.md"
            template_path.write_text("---\ntype: sop\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                result = get_sop_template()

            self.assertEqual(result, "---\ntype: sop\n---\n\n# Title\n")

    def test_raises_file_not_found_when_template_missing(self) -> None:
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_sop_template()


if __name__ == "__main__":
    unittest.main()
