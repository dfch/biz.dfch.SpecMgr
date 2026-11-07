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

"""Tests for the ``get_set_example`` ``@mcp.tool()`` wrapper (feat-229-set Phase 110, real packaged data).

The packaged-data ``specmgr://set/example`` resource (Phase 120) will add its
own resource-level tests; this module pins the tool half: the real committed
file parses green through ``set.models.v1.parser.parse_set`` and is
byte-stable under parse -> re-render (the mdformat-clean property).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import frontmatter

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.set.models.v1 import SetDocument, parse_set
from biz.dfch.specmgr.set.tools.get_set_example import get_set_example

_EXPECTED_ITEM_COUNT = 6


class TestGetSetExampleTool(unittest.TestCase):
    """Tests for the get_set_example tool."""

    def test_returns_real_packaged_example(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_set_example()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: set", result)
        self.assertIn("# Engine Thermal Management Bundle", result)

    def test_packaged_example_parses_green_and_exercises_the_shape(self) -> None:
        """The committed example must parse via parse_set and exercise the opaque
        ``## Description`` (nested H3, a fenced code block) plus the mixed-tag
        ``## Items`` list (GOL/REQ/RSK/UC/FEAT, per-bullet notes)."""
        document = parse_set(get_set_example())

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

    def test_packaged_example_is_byte_stable_under_parse_re_render(self) -> None:
        """The committed example's body must already be in the engine's canonical (mdformat)
        form: the re-rendered body equals the mdformat-normalized body byte-for-byte
        (pins the mdformat-clean property the Phase 120 resource tests will reuse)."""
        text = get_set_example()
        document = parse_set(text)
        raw_body = frontmatter.loads(text).content
        assert isinstance(raw_body, str)

        self.assertEqual(str(document.body), format_text(raw_body))
        # frontmatter.loads strips the file's single trailing newline, so the
        # on-disk body is the normalized form minus that one newline.
        self.assertEqual(raw_body + "\n", format_text(raw_body))

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "set_example.md"
            example_path.write_text("---\ntype: set\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                result = get_set_example()

            self.assertEqual(result, "---\ntype: set\n---\n\n# Title\n")

    def test_raises_file_not_found_when_example_missing(self) -> None:
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_set_example()


if __name__ == "__main__":
    unittest.main()
