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

"""Tests for the `specmgr://set/example` resource (`set.resources.set_example.set_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.set.models.v1 import SetDocument, parse_set
from biz.dfch.specmgr.set.resources.set_example import set_example
from biz.dfch.specmgr.set.tools.get_set_example import get_set_example

_EXPECTED_ITEM_COUNT = 6


class TestSetExampleResource(unittest.TestCase):
    """Tests for the set_example resource function."""

    def test_returns_real_packaged_example(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        sut = set_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: set", result)
        self.assertIn("# Engine Thermal Management Bundle", result)

    def test_matches_packaged_file_byte_for_byte(self) -> None:
        """The resource must equal the packaged set_example.md byte-for-byte."""
        sut = set_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("set", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_set_example_tool(self) -> None:
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(set_example(), get_set_example())

    def test_packaged_example_parses_and_exercises_the_shape(self) -> None:
        """The committed example must parse via parse_set and exercise the opaque
        ``## Description`` (nested H3, a fenced code block) plus the mixed-tag
        ``## Items`` list (GOL/REQ/RSK/UC/FEAT, per-bullet notes)."""
        document = parse_set(set_example())

        self.assertIsInstance(document, SetDocument)
        self.assertEqual(document.frontmatter.type, "set")
        self.assertEqual(document.frontmatter.status, "review")
        self.assertEqual(document.body.text, "Engine Thermal Management Bundle")

        description = document.body.description
        self.assertIn("### Why this grouping", str(description))
        self.assertIn("80 C", str(description))

        items = document.body.items.items
        self.assertEqual(len(items), _EXPECTED_ITEM_COUNT)
        self.assertIn(
            "GOL 7d1e6c2a-4b3f-4a9e-8c5d-2f6e9a1b3c4d: Competitive Engines in Consumer Vehicles", items[0].text
        )
        self.assertEqual(len(items[0].notes or []), 1)  # the first bullet carries a notes paragraph
        self.assertIn("FEAT feat-42-thermal-management: Thermal Management", items[-1].text)
        # the tag mix: at least five distinct reference tags in one list
        tags = {item.text.split()[0] for item in items}
        self.assertEqual(tags, {"GOL", "REQ", "RSK", "UC", "FEAT"})

    def test_reads_fresh_on_every_call(self) -> None:
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "set_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = set_example

                first = sut()
                example_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_example_missing(self) -> None:
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = set_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
