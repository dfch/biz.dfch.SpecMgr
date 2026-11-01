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

"""Tests for the `specmgr://harness-bundle` resource (`general.resources.harness_bundle.harness_bundle`).

Mirrors `tests/general/resources/test_rasci.py`'s structure and style
(real-content assertions, fresh-read-per-call, `FileNotFoundError` on a
missing packaged file) minus the dedicated model: the bundle has no schema
of its own, so the fail-fast guard on every call is a plain `json.loads`
(a malformed packaged file must raise `json.JSONDecodeError`, not return
silently). The load-bearing content assertions are byte-identity to the
committed on-disk bundle and the full file list's shape (sorted paths,
self-consistent sha256/content pairs, the non-empty `instructions`
protocol text).
"""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.resources.harness_bundle import harness_bundle
from biz.dfch.specmgr.general.tools import _packaged_data

#: The repository root (this file lives at `tests/general/resources/test_harness_bundle.py`).
_REPO_ROOT = Path(__file__).resolve().parents[3]

#: The committed on-disk bundle the resource must serve byte-identically.
_BUNDLE_PATH = _REPO_ROOT / "src" / "biz" / "dfch" / "specmgr" / "general" / "data" / "general_harness_bundle.json"


class TestHarnessBundleResource(unittest.TestCase):
    """Tests for the `harness_bundle` resource function."""

    def test_returns_the_on_disk_bundle_byte_identically(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = harness_bundle
        expected = _BUNDLE_PATH.read_text(encoding="utf-8")

        result = sut()

        self.assertEqual(result, expected)

    def test_json_loads_parses_to_the_full_file_list(self):
        """The returned text must parse to `{"instructions", "files"}` with every file entry self-consistent."""
        payload: dict[str, Any] = json.loads(harness_bundle())

        self.assertEqual(list(payload.keys()), ["instructions", "files"])
        self.assertTrue(payload["instructions"].strip())
        files = payload["files"]
        self.assertGreater(len(files), 0)
        paths = [entry["path"] for entry in files]
        self.assertEqual(paths, sorted(paths))
        for entry in files:
            with self.subTest(path=entry["path"]):
                self.assertEqual(list(entry.keys()), ["path", "sha256", "content"])
                self.assertEqual(
                    entry["sha256"],
                    hashlib.sha256(entry["content"].encode("utf-8")).hexdigest(),
                )

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        first_text = json.dumps({"instructions": "first", "files": []}, indent=2, ensure_ascii=False) + "\n"
        second_text = json.dumps({"instructions": "second", "files": []}, indent=2, ensure_ascii=False) + "\n"

        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "general_harness_bundle.json"
            bundle_path.write_text(first_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=bundle_path):
                sut = harness_bundle

                first = sut()
                bundle_path.write_text(second_text, encoding="utf-8")
                second = sut()

            self.assertEqual(first, first_text)
            self.assertEqual(second, second_text)

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged general_harness_bundle.json must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.json"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = harness_bundle

                with self.assertRaises(FileNotFoundError):
                    sut()

    def test_raises_on_invalid_json(self):
        """A non-JSON packaged file must fail fast via json.loads, not return silently."""
        malformed_text = "{ this is not valid json"

        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "general_harness_bundle.json"
            bundle_path.write_text(malformed_text, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=bundle_path):
                sut = harness_bundle

                with self.assertRaises(json.JSONDecodeError):
                    sut()


if __name__ == "__main__":
    unittest.main()
