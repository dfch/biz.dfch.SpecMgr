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

"""Tests for the QaFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.qa.models.v1.frontmatter import QaFrontmatter


class TestQaFrontmatter(unittest.TestCase):
    """Tests for the QaFrontmatter Pydantic model."""

    def test_type_defaults_to_qa(self):
        sut = QaFrontmatter()

        self.assertEqual(sut.type, "qa")

    def test_version_defaults_to_current_schema_version(self):
        sut = QaFrontmatter(status="active")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        sut = QaFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self):
        with self.assertRaises(ValidationError):
            QaFrontmatter(version="2.0.0")

    def test_accepts_all_four_statuses(self):
        for status in ("draft", "active", "done", "cancelled"):
            with self.subTest(status=status):
                self.assertEqual(QaFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self):
        with self.assertRaises(ValidationError):
            QaFrontmatter(status="in-review")

    def test_status_defaults_to_draft(self):
        sut = QaFrontmatter()

        self.assertEqual(sut.status, "draft")

    def test_blank_status_defaults_to_draft(self):
        self.assertEqual(QaFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(QaFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self):
        sut = QaFrontmatter(status="active")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


if __name__ == "__main__":
    unittest.main()
