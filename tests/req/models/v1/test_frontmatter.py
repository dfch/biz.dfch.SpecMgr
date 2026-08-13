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

"""Tests for the ReqFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.req.models.v1.frontmatter import ReqFrontmatter


class TestReqFrontmatter(unittest.TestCase):
    """Tests for the ReqFrontmatter Pydantic model."""

    def test_type_defaults_to_req(self):
        frontmatter = ReqFrontmatter()
        self.assertEqual(frontmatter.type, "req")

    def test_version_defaults_to_current_schema_version(self):
        frontmatter = ReqFrontmatter(status="accepted")
        self.assertEqual(frontmatter.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        frontmatter = ReqFrontmatter(version="1.4.2")
        self.assertEqual(frontmatter.version, "1.4.2")

    def test_version_rejects_mismatched_major(self):
        with self.assertRaises(ValidationError):
            ReqFrontmatter(version="2.0.0")

    def test_accepts_all_seven_statuses(self):
        for status in (
            "draft",
            "proposed",
            "accepted",
            "superseded",
            "deprecated",
            "rejected",
            "implemented",
        ):
            with self.subTest(status=status):
                self.assertEqual(ReqFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            ReqFrontmatter(status="in-review")

    def test_status_defaults_to_draft(self):
        frontmatter = ReqFrontmatter()
        self.assertEqual(frontmatter.status, "draft")

    def test_blank_status_defaults_to_draft(self):
        self.assertEqual(ReqFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(ReqFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self):
        frontmatter = ReqFrontmatter(status="proposed")
        self.assertIsNone(frontmatter.id)
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)


if __name__ == "__main__":
    unittest.main()
