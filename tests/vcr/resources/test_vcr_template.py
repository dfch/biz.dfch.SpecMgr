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

"""Tests for the `specmgr://vcr/template` resource (`vcr.resources.vcr_template.vcr_template`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.vcr.models.v1 import parse_vcr
from biz.dfch.specmgr.vcr.resources.vcr_template import vcr_template
from biz.dfch.specmgr.vcr.tools.get_vcr_template import get_vcr_template

_TEMPLATE_STATUS = "draft"


class TestVcrTemplateResource(unittest.TestCase):
    """Tests for the vcr_template resource function."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = vcr_template

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: vcr", result)
        self.assertIn("# Level 1 Heading is the Title of the Verification Case Record", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-006: the resource must equal the packaged vcr_template.md byte-for-byte."""
        sut = vcr_template

        result = sut()

        packaged = _packaged_data.packaged_data_path("vcr", "template").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_vcr_template_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(vcr_template(), get_vcr_template())

    def test_packaged_template_round_trips_through_parse_vcr(self):
        """The committed template must be a fully-parseable verification case record document."""
        document = parse_vcr(vcr_template())

        self.assertEqual(document.frontmatter.status, _TEMPLATE_STATUS)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "vcr_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                sut = vcr_template

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
                sut = vcr_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
