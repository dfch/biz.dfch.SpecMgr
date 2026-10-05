# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""Tests for the ``get_uc_plantuml_template`` ``@mcp.tool()`` wrapper (feat-185-uc-diagrams, Phase 120).

The tool returns the packaged PlantUML sequence-skeleton template
(``uc/data/uc_plantuml_template.md``) verbatim -- the tool-side half of
the ``specmgr://uc/plantuml-template`` packaged-data pair. REQ-008: the
file must pass the structure checker in both modes.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.plantuml import structure as S
from biz.dfch.specmgr.uc.tools.get_uc_plantuml_template import get_uc_plantuml_template


class TestGetUcPlantumlTemplateTool(unittest.TestCase):
    """Tests for the get_uc_plantuml_template tool."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        result = get_uc_plantuml_template()

        self.assertIsInstance(result, str)
        on_disk = _packaged_data.packaged_data_path("uc", "plantuml_template")
        self.assertEqual(result, on_disk.read_text(encoding="utf-8"))
        self.assertTrue(result.startswith("@startuml"))
        self.assertIn("UNATTRIBUTED", result)  # the mapping comments name the three marker forms

    def test_passes_the_structure_checker_both_modes(self):
        """REQ-008: the packaged template must be checker-clean in both modes (no UNATTRIBUTED
        marker lines in the template itself -- only its comments name them)."""
        result = get_uc_plantuml_template()

        for mode in (S.MODE_PREFLIGHT, S.MODE_STANDALONE):
            with self.subTest(mode=mode):
                check = S.check_structure(result, mode)
                self.assertTrue(check.ok)
                self.assertEqual(check.errors, [])
        self.assertFalse(any(line.startswith(S.UNATTRIBUTED_MARKER_PREFIX) for line in result.split("\n")))

    def test_delegates_to_shared_data_reader(self):
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "uc_plantuml_template.md"
            template_path.write_text("@startuml\n@enduml\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                result = get_uc_plantuml_template()

            self.assertEqual(result, "@startuml\n@enduml\n")

    def test_raises_file_not_found_when_template_missing(self):
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_uc_plantuml_template()


if __name__ == "__main__":
    unittest.main()
