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

"""Tests for the `specmgr://dec/template` resource (`dec.resources.dec_template.dec_template`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.models.v1 import parse_dec
from biz.dfch.specmgr.dec.resources.dec_template import dec_template
from biz.dfch.specmgr.dec.tools.get_dec_template import get_dec_template
from biz.dfch.specmgr.general.tools import _packaged_data

_TEMPLATE_STATUS = "draft"


class TestDecTemplateResource(unittest.TestCase):
    """Tests for the dec_template resource function."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = dec_template

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: dec", result)
        self.assertIn("# Level 1 Heading is the Title of the Decision", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-004: the resource must equal the packaged dec_template.md byte-for-byte."""
        sut = dec_template

        result = sut()

        packaged = _packaged_data.packaged_data_path("dec", "template").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_dec_template_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(dec_template(), get_dec_template())

    def test_packaged_template_round_trips_through_parse_dec(self):
        """The committed template must be a fully-parseable decision document (RSK precedent)."""
        document = parse_dec(dec_template())

        self.assertEqual(document.frontmatter.status, _TEMPLATE_STATUS)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "dec_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                sut = dec_template

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
                sut = dec_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
