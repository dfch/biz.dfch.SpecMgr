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

"""Tests for the `specmgr://dec/example` resource (`dec.resources.dec_example.dec_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.models.v1 import parse_dec
from biz.dfch.specmgr.dec.resources.dec_example import dec_example
from biz.dfch.specmgr.dec.tools.get_dec_example import get_dec_example
from biz.dfch.specmgr.general.tools import _packaged_data

_MIN_RELATED_SUB_LISTS = 2


class TestDecExampleResource(unittest.TestCase):
    """Tests for the dec_example resource function."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = dec_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: dec", result)
        self.assertIn("# Hybrid Working Arrangement for the Engineering Organization", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-004: the resource must equal the packaged dec_example.md byte-for-byte."""
        sut = dec_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("dec", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_dec_example_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(dec_example(), get_dec_example())

    def test_packaged_example_parses_and_exercises_every_section(self):
        """The committed example must parse via parse_dec and exercise the expected sections."""
        document = parse_dec(dec_example())

        outcome = document.body.outcome
        self.assertIsNotNone(outcome.consequences)
        self.assertIsNotNone(outcome.confirmation)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        present_sub_lists = [
            sub_list
            for sub_list in (
                related_artifacts.requirements,
                related_artifacts.decisions,
                related_artifacts.goals,
                related_artifacts.acceptance_criteria,
            )
            if sub_list is not None
        ]
        self.assertGreaterEqual(len(present_sub_lists), _MIN_RELATED_SUB_LISTS)

        pros_and_cons = document.body.pros_and_cons
        self.assertIsNotNone(pros_and_cons)
        self.assertEqual(len(pros_and_cons.options), 2)

        updates = document.body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 2)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "dec_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = dec_example

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
                sut = dec_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
