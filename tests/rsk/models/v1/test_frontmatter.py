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

"""Tests for the RskFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.rsk.models.v1.frontmatter import RskFrontmatter


class TestRskFrontmatter(unittest.TestCase):
    """Tests for the RskFrontmatter Pydantic model."""

    def test_type_defaults_to_rsk(self):
        sut = RskFrontmatter()

        self.assertEqual(sut.type, "rsk")

    def test_version_defaults_to_current_schema_version(self):
        sut = RskFrontmatter(status="mitigating")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        sut = RskFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self):
        with self.assertRaises(ValidationError):
            RskFrontmatter(version="2.0.0")

    def test_accepts_all_six_statuses(self):
        for status in ("open", "mitigating", "accepted", "occurred", "closed", "dropped"):
            with self.subTest(status=status):
                self.assertEqual(RskFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            RskFrontmatter(status="in-review")

    def test_rejects_base_default_status_draft(self):
        with self.assertRaises(ValidationError):
            RskFrontmatter(status="draft")

    def test_status_defaults_to_open(self):
        sut = RskFrontmatter()

        self.assertEqual(sut.status, "open")

    def test_blank_status_defaults_to_open(self):
        self.assertEqual(RskFrontmatter.model_validate({"status": None}).status, "open")
        self.assertEqual(RskFrontmatter.model_validate({"status": "   "}).status, "open")

    def test_optional_fields_default_to_none(self):
        sut = RskFrontmatter(status="mitigating")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


if __name__ == "__main__":
    unittest.main()
