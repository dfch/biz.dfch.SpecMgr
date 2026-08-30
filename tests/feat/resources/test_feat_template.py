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

"""Tests for the `specmgr://feat/template` resource (`feat.resources.feat_template.feat_template`)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.models.v1 import parse_feat
from biz.dfch.specmgr.feat.resources.feat_template import feat_template
from biz.dfch.specmgr.feat.tools.get_feat_template import get_feat_template
from biz.dfch.specmgr.general.tools import _packaged_data

_TEMPLATE_STATUS = "planning"


class TestFeatTemplateResource(unittest.TestCase):
    """Tests for the feat_template resource function."""

    def test_returns_real_packaged_template(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = feat_template

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: feat", result)
        self.assertIn("# Feature: Level 1 Heading is the Title of the Feature", result)

    def test_matches_packaged_file_byte_for_byte(self):
        """ACC-005/ACC-007: the resource must equal the packaged feat_template.md byte-for-byte."""
        sut = feat_template

        result = sut()

        packaged = _packaged_data.packaged_data_path("feat", "template").read_text(encoding="utf-8")
        self.assertEqual(result, packaged)

    def test_matches_the_get_feat_template_tool(self):
        """The resource and the tool must return identical content -- same underlying reader."""
        self.assertEqual(feat_template(), get_feat_template())

    def test_packaged_template_round_trips_through_parse_feat(self):
        """The committed template must be a fully-parseable feature document (DEC/RSK precedent)."""
        document = parse_feat(feat_template())

        self.assertEqual(document.frontmatter.status, _TEMPLATE_STATUS)

        plan = document.body.plan
        self.assertIsNotNone(plan.dependencies)
        self.assertIsNotNone(plan.dependencies.depends_on)
        self.assertIsNotNone(plan.dependencies.blocks)
        self.assertIsNotNone(plan.design_notes)
        self.assertIsNotNone(plan.related_decisions)

        progress = document.body.progress
        self.assertIsNotNone(progress.blockers)
        self.assertIsNotNone(progress.decisions_made)
        self.assertIsNotNone(progress.related_prs_commits)
        self.assertIsNotNone(progress.more_information)

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "feat_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                sut = feat_template

                first = sut()
                template_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_template_missing(self):
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = feat_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
