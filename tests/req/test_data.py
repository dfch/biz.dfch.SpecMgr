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

"""Tests for `req._data.read_req_example_text` (Task 3.6)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.req import _data
from biz.dfch.specmgr.req._data import read_req_example_text


class TestReadReqExampleText(unittest.TestCase):
    """Tests for the packaged REQ example reader."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = read_req_example_text

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)
        self.assertIn("# Maximum Engine Temperature", result)

    def test_returns_content_for_a_given_file(self):
        """A patched-in example file's exact content must round-trip verbatim."""
        payload = "---\ntype: req\n---\n\n# Title\n\nBody text.\n"
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "req_example.md"
            example_path.write_text(payload, encoding="utf-8")

            with mock.patch.object(_data, "_EXAMPLE_PATH", example_path):
                sut = read_req_example_text

                result = sut()

            self.assertEqual(result, payload)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "req_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_data, "_EXAMPLE_PATH", example_path):
                sut = read_req_example_text

                first = sut()
                example_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_example_missing(self):
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_data, "_EXAMPLE_PATH", missing_path):
                sut = read_req_example_text

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
