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

"""Tests for the `specmgr://txt/template` resource (`txt.resources.txt_template.txt_template`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.txt.models.v1 import TxtDocument, parse_txt
from biz.dfch.specmgr.txt.resources.txt_template import txt_template
from biz.dfch.specmgr.txt.tools.get_txt_template import get_txt_template

_TEMPLATE_STATUS = "draft"


class TestTxtTemplateResource(unittest.TestCase):
    """Tests for the txt_template resource function."""

    def test_returns_real_packaged_template(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        sut = txt_template

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: txt", result)
        self.assertIn("# Level 1 Heading is the Title of the Free-Form Text Document", result)

    def test_matches_packaged_file_byte_for_byte(self) -> None:
        """The resource must equal the packaged txt_template.md byte-for-byte."""
        sut = txt_template

        result = sut()

        packaged = _packaged_data.packaged_data_path("txt", "template").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_txt_template_tool(self) -> None:
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(txt_template(), get_txt_template())

    def test_packaged_template_round_trips_through_parse_txt(self) -> None:
        """The committed template must be a fully-parseable free-form text document: its
        blind-text placeholder content satisfies every structural constraint."""
        document = parse_txt(txt_template())

        self.assertIsInstance(document, TxtDocument)
        self.assertEqual(document.frontmatter.status, _TEMPLATE_STATUS)
        self.assertEqual(len(document.body.updates.updates), 1)

    def test_reads_fresh_on_every_call(self) -> None:
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "txt_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                sut = txt_template

                first = sut()
                template_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_template_missing(self) -> None:
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = txt_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
