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

"""Tests for the `specmgr://tsk/template` resource (`tsk.resources.tsk_template.tsk_template`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.tsk.resources.tsk_template import tsk_template
from biz.dfch.specmgr.tsk.tools.get_tsk_template import get_tsk_template


class TestTskTemplateResource(unittest.TestCase):
    """Tests for the tsk_template resource function."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = tsk_template

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: tsk", result)
        self.assertIn("# Level 1 Heading is the Title of the Task List", result)

    def test_matches_the_get_tsk_template_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(tsk_template(), get_tsk_template())

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "tsk_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                sut = tsk_template

                first = sut()
                template_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_template_missing(self):
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = tsk_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
