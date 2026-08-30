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

"""Tests for the ``get_feat_template`` ``@mcp.tool()`` wrapper (Task 2.3).

**Deferred to Phase 3** (Task 3.2) -- see ``test_get_feat_example.py``'s own
module docstring for the full rationale; this module mirrors it exactly for
the template, not the example.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.tools.get_feat_template import get_feat_template
from biz.dfch.specmgr.general.tools import _packaged_data


class TestGetFeatTemplateTool(unittest.TestCase):
    """Tests for the get_feat_template tool."""

    def test_raises_file_not_found_until_phase_3_ships_the_packaged_file(self) -> None:
        """As of Phase 2, feat/data/feat_template.md does not exist yet -- see this module's docstring."""
        with self.assertRaises(FileNotFoundError):
            get_feat_template()

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "feat_template.md"
            template_path.write_text("---\ntype: feat\n---\n\n# Feature: Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                result = get_feat_template()

            self.assertEqual(result, "---\ntype: feat\n---\n\n# Feature: Title\n")

    def test_raises_file_not_found_when_template_missing(self) -> None:
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_feat_template()


if __name__ == "__main__":
    unittest.main()
