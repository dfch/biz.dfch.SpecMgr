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

"""Tests for the `specmgr://rsk/example` resource (`rsk.resources.rsk_example.rsk_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.rsk.models.v1 import parse_rsk
from biz.dfch.specmgr.rsk.resources.rsk_example import rsk_example
from biz.dfch.specmgr.rsk.tools.get_rsk_example import get_rsk_example


class TestRskExampleResource(unittest.TestCase):
    """Tests for the rsk_example resource function."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = rsk_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: rsk", result)
        self.assertIn("# Untrusted File Uploads Parsed by an Unmaintained Parser Library", result)

    def test_matches_the_get_rsk_example_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(rsk_example(), get_rsk_example())

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "rsk_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = rsk_example

                first = sut()
                example_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_example_missing(self):
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = rsk_example

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_packaged_example_round_trips_through_parse_rsk(self):
        """The committed example must be a fully-parseable risk document."""
        document = parse_rsk(rsk_example())

        self.assertEqual(document.frontmatter.id, "deadbeef-risk-risk-risk-deadbeefrisk")
        self.assertEqual(document.body.initial_assessment.level, "high")  # 4 x 3 = 12
        self.assertEqual(document.body.residual_assessment.level, "medium")  # 2 x 3 = 6


if __name__ == "__main__":
    unittest.main()
