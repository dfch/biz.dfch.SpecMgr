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

"""Tests for the `specmgr://vcr/example` resource (`vcr.resources.vcr_example.vcr_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.vcr.models.v1 import parse_vcr
from biz.dfch.specmgr.vcr.resources.vcr_example import vcr_example
from biz.dfch.specmgr.vcr.tools.get_vcr_example import get_vcr_example

_EXPECTED_AC_COUNT = 4


class TestVcrExampleResource(unittest.TestCase):
    """Tests for the vcr_example resource function."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = vcr_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: vcr", result)
        self.assertIn("# API Key Revocation Latency Verification", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-006: the resource must equal the packaged vcr_example.md byte-for-byte."""
        sut = vcr_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("vcr", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_vcr_example_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(vcr_example(), get_vcr_example())

    def test_packaged_example_parses_and_exercises_every_section(self):
        """The committed example must parse via parse_vcr and exercise the expected sections."""
        document = parse_vcr(vcr_example())

        self.assertEqual(document.body.coverage.value.text, "partial")

        acceptance_criteria = document.body.acceptance_criteria
        self.assertEqual(len(acceptance_criteria.criteria), _EXPECTED_AC_COUNT)
        methods = [criterion.method for criterion in acceptance_criteria.criteria]
        self.assertEqual(methods, ["Test", "Analysis", "Inspection", "Special"])

        self.assertIsNotNone(document.body.more_information)

        updates = document.body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 1)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "vcr_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = vcr_example

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
                sut = vcr_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
