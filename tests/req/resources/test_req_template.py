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

"""Tests for the `specmgr://req/template` resource (`req.resources.req_template.req_template`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.req import _data
from biz.dfch.specmgr.req.resources.req_template import req_template
from biz.dfch.specmgr.req.tools.get_req_template import get_req_template


class TestReqTemplateResource(unittest.TestCase):
    """Tests for the req_template resource function."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = req_template

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)
        self.assertIn("# Level 1 Heading is the Title of the Requirement", result)

    def test_matches_the_get_req_template_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(req_template(), get_req_template())

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "req_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_data, "_TEMPLATE_PATH", template_path):
                sut = req_template

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
                sut = req_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
