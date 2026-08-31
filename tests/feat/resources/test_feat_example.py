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

"""Tests for the `specmgr://feat/example` resource (`feat.resources.feat_example.feat_example`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import frontmatter

from biz.dfch.specmgr.feat.models.v1 import parse_feat
from biz.dfch.specmgr.feat.resources.feat_example import feat_example
from biz.dfch.specmgr.feat.tools.get_feat_example import get_feat_example
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.models.md._markdown import format_text

_MIN_TASK_LIST_PHASES = 2
_MIN_UPDATES = 2
_MIN_DECISIONS_MADE = 2


class TestFeatExampleResource(unittest.TestCase):
    """Tests for the feat_example resource function."""

    def test_returns_real_packaged_example(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = feat_example

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: feat", result)
        self.assertIn("# Feature: Example Widget", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-005/ACC-007: the resource must equal the packaged feat_example.md byte-for-byte."""
        sut = feat_example

        result = sut()

        packaged = _packaged_data.packaged_data_path("feat", "example").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_feat_example_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(feat_example(), get_feat_example())

    def test_matches_the_reference_fixture_byte_for_byte(self):
        """ACC-001: the packaged example is a byte-identical copy of the Phase 1 reference fixture."""
        reference_path = Path(__file__).parent.parent / "models" / "v1" / "data" / "feat_reference.md"
        reference_text = reference_path.read_text(encoding="utf-8")

        self.assertEqual(feat_example(), reference_text)

    def test_packaged_example_round_trips_through_parse_feat(self):
        """ACC-001: the committed example must round-trip through parse_feat byte-exact."""
        original = feat_example()

        document = parse_feat(original)

        self.assertEqual(str(document.body), format_text(frontmatter.loads(original).content))

    def test_packaged_example_parses_and_exercises_every_section(self):
        """The committed example must parse via parse_feat and exercise every optional section."""
        document = parse_feat(feat_example())

        plan = document.body.plan
        self.assertIsNotNone(plan.dependencies)
        self.assertIsNotNone(plan.dependencies.depends_on)
        self.assertIsNotNone(plan.dependencies.blocks)
        self.assertIsNotNone(plan.design_notes)
        self.assertIsNotNone(plan.related_decisions)
        self.assertGreaterEqual(len(plan.task_list.phases), _MIN_TASK_LIST_PHASES)

        progress = document.body.progress
        self.assertIsNotNone(progress.blockers)
        self.assertGreaterEqual(len(progress.updates.updates), _MIN_UPDATES)
        self.assertIsNotNone(progress.decisions_made)
        self.assertGreaterEqual(len(progress.decisions_made.decisions), _MIN_DECISIONS_MADE)
        self.assertIsNotNone(progress.related_prs_commits)
        self.assertIsNotNone(progress.more_information)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "feat_example.md"
            example_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                sut = feat_example

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
                sut = feat_example

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
