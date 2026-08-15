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

"""Tests for `general.tools._packaged_data` (`packaged_data_path`/`read_packaged_text`,
Task 5.3).

Exercised against REQ's real, committed packaged data files (``req/data/*``)
since REQ is currently the only artifact domain with packaged example/
template/schema data -- there is no synthetic fixture package to test
against instead. This mirrors the deleted, REQ-only ``tests/req/test_data.py``
that this module replaces, generalized across the ``type_name``/``kind``/
``ext`` parameters instead of one test class per hardcoded file.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.general.tools._packaged_data import packaged_data_path, read_packaged_text


class TestPackagedDataPath(unittest.TestCase):
    """Tests for `packaged_data_path`'s convention computation."""

    def test_resolves_the_real_req_example_file(self):
        """`packaged_data_path("req", "example")` must resolve to the real, committed file."""
        sut = packaged_data_path("req", "example")

        result = sut.read_text(encoding="utf-8")

        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)

    def test_defaults_ext_to_md(self):
        """Omitting `ext` must be equivalent to passing `ext="md"` explicitly."""
        default_ext = packaged_data_path("req", "example")
        explicit_ext = packaged_data_path("req", "example", "md")

        self.assertEqual(default_ext.read_text(encoding="utf-8"), explicit_ext.read_text(encoding="utf-8"))

    def test_resolves_a_non_default_ext(self):
        """`ext="json"` must resolve to the `.json` sibling, not the `.md` default."""
        sut = packaged_data_path("req", "schema", "json")

        result = sut.read_text(encoding="utf-8")

        parsed = json.loads(result)
        self.assertEqual(parsed["$comment"], "v1")

    def test_never_reads_the_file_itself(self):
        """Computing the path for a nonexistent kind must not raise -- only reading would."""
        sut = packaged_data_path("req", "does-not-exist-kind")

        self.assertIsNotNone(sut)


class TestReadPackagedText(unittest.TestCase):
    """Tests for `read_packaged_text`'s file-reading behavior."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        result = read_packaged_text("req", "example")

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)
        self.assertIn("# Maximum Engine Temperature", result)

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        result = read_packaged_text("req", "template")

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: req", result)

    def test_returns_real_packaged_schema(self):
        """Against the real, committed packaged data file, without any patching."""
        result = read_packaged_text("req", "schema", "json")

        parsed = json.loads(result)
        self.assertEqual(parsed["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(parsed["$comment"], "v1")

    def test_returns_content_for_a_patched_path(self):
        """A patched-in file's exact content must round-trip verbatim."""
        payload = "arbitrary packaged content\n"
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "fixture.md"
            data_path.write_text(payload, encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=data_path):
                result = read_packaged_text("req", "example")

            self.assertEqual(result, payload)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            data_path = Path(tmp) / "fixture.md"
            data_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=data_path):
                first = read_packaged_text("req", "example")
                data_path.write_text("second", encoding="utf-8")
                second = read_packaged_text("req", "example")

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    read_packaged_text("req", "example")


if __name__ == "__main__":
    unittest.main()
