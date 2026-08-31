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

"""Tests for the `specmgr://sop/example` resource (`sop.resources.sop_example.sop_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.sop.models.v1 import parse_sop
from biz.dfch.specmgr.sop.resources.sop_example import sop_example
from biz.dfch.specmgr.sop.tools.get_sop_example import get_sop_example

_EXPECTED_PROCEDURE_STEPS = 5


class TestSopExampleResource(unittest.TestCase):
    """Tests for the sop_example resource function."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = sop_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: sop", result)
        self.assertIn("# New Employee IT Account Provisioning", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-004: the resource must equal the packaged sop_example.md byte-for-byte."""
        sut = sop_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("sop", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_sop_example_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(sop_example(), get_sop_example())

    def test_packaged_example_parses_and_exercises_every_section(self):
        """The committed example must parse via parse_sop and exercise the expected sections."""
        document = parse_sop(sop_example())

        self.assertEqual(document.frontmatter.status, "active")
        self.assertEqual(document.frontmatter.type, "sop")

        roles = document.body.roles_and_responsibilities
        self.assertIsNotNone(roles)
        self.assertIsNotNone(roles.accountable)
        self.assertGreaterEqual(len(roles.responsible.items), 1)
        # Support is present-but-empty: the heading exists with zero items (items is None),
        # demonstrating the three-way "present-with-zero-items" shape distinct from absence.
        self.assertIsNotNone(roles.support)
        self.assertIsNone(roles.support.items)
        self.assertGreaterEqual(len(roles.consulted.items), 1)
        self.assertGreaterEqual(len(roles.informed.items), 1)

        self.assertEqual(len(document.body.procedure.steps), _EXPECTED_PROCEDURE_STEPS)

        related_artifacts = document.body.related_artifacts
        self.assertIsNotNone(related_artifacts)
        self.assertIsNotNone(related_artifacts.requirements)
        self.assertIsNotNone(related_artifacts.decisions)
        self.assertIsNotNone(related_artifacts.goals)
        self.assertIsNotNone(related_artifacts.acceptance_criteria)
        self.assertIsNotNone(related_artifacts.sops)

        updates = document.body.updates
        self.assertIsNotNone(updates)
        self.assertEqual(len(updates.updates), 1)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "sop_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = sop_example

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
                sut = sop_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
