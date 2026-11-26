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

"""Tests for the specmgr://iso25010 resource (Task 0.8.6; rewritten for the
raw-markdown-output contract by feat-92-resources Task 1.3, ACC-001)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.resources.iso25010 import iso25010
from biz.dfch.specmgr.general.tools import _packaged_data

#: The 9 characteristic names `Iso25010` requires (`min_length=9`/`max_length=9`).
_NAMES = [f"Characteristic {n}" for n in range(1, 10)]


def _valid_iso25010_text(marker: str) -> str:
    """Build a minimal, well-formed ISO/IEC 25010-shaped document, tagged with `marker`.

    `marker` is embedded in the title so two calls with different markers produce
    distinguishable, but both individually valid, `parse_iso25010`-accepted text.
    """
    names_list = "\n".join(f"- {name}" for name in _NAMES)
    characteristics = "\n\n".join(
        f"## {name}\n\nDescription of {name}.\n\n### Sub {name}\n\nSub-description of {name}." for name in _NAMES
    )
    result = f"# {marker}\n\n{names_list}\n\n{characteristics}\n"
    return result


class TestIso25010Resource(unittest.TestCase):
    """Tests for the `iso25010` resource function (`specmgr://iso25010`)."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = iso25010

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# ISO 25010:2023"))

    def test_has_nine_characteristic_headings(self):
        """The packaged data has exactly 9 main `## ` characteristic headings."""
        result = iso25010()

        heading_count = sum(1 for line in result.splitlines() if line.startswith("## "))

        self.assertEqual(heading_count, 9)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = _valid_iso25010_text("First Marker")
        second_text = _valid_iso25010_text("Second Marker")

        with tempfile.TemporaryDirectory() as tmp:
            iso25010_path = Path(tmp) / "general_iso25010.md"
            iso25010_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=iso25010_path):
                sut = iso25010

                first = sut()
                iso25010_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_iso25010.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = iso25010

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_structural_drift(self):
        """A malformed packaged file must fail fast via `parse_iso25010`, not return silently (ACC-001)."""
        malformed_text = "# Not A Valid ISO25010 Document\n\nThis file has no characteristic headings at all.\n"

        with tempfile.TemporaryDirectory() as tmp:
            iso25010_path = Path(tmp) / "general_iso25010.md"
            iso25010_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=iso25010_path):
                sut = iso25010

                with self.assertRaises((AssertionError, ValueError)):
                    sut()


if __name__ == "__main__":
    unittest.main()
