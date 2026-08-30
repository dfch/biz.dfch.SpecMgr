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

"""Tests for the FeatFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.feat.models.v1.frontmatter import FeatFrontmatter


class TestFeatFrontmatter(unittest.TestCase):
    """Tests for the FeatFrontmatter Pydantic model."""

    def test_type_defaults_to_feat(self) -> None:
        sut = FeatFrontmatter()

        self.assertEqual(sut.type, "feat")

    def test_type_rejects_other_document_types(self) -> None:
        for other in ("req", "gol", "dec", "adr"):
            with self.subTest(other=other):
                with self.assertRaises(ValidationError):
                    FeatFrontmatter(type=other)

    def test_version_defaults_to_current_schema_version(self) -> None:
        sut = FeatFrontmatter(status="progress")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self) -> None:
        sut = FeatFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self) -> None:
        with self.assertRaises(ValidationError):
            FeatFrontmatter(version="2.0.0")

    def test_accepts_all_four_statuses(self) -> None:
        for status in ("planning", "progress", "review", "done"):
            with self.subTest(status=status):
                self.assertEqual(FeatFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaises(ValidationError):
            FeatFrontmatter(status="in-progress")

    def test_rejects_base_only_draft_status(self) -> None:
        # "draft" belongs to the base `MarkdownFrontmatter`'s default vocabulary
        # (and most other domains' own sets), but is not part of `feat`'s own
        # closed four-value set.
        with self.assertRaises(ValidationError):
            FeatFrontmatter(status="draft")

    def test_status_defaults_to_planning(self) -> None:
        sut = FeatFrontmatter()

        self.assertEqual(sut.status, "planning")

    def test_blank_status_defaults_to_planning(self) -> None:
        self.assertEqual(FeatFrontmatter.model_validate({"status": None}).status, "planning")
        self.assertEqual(FeatFrontmatter.model_validate({"status": "   "}).status, "planning")

    def test_optional_fields_default_to_none(self) -> None:
        sut = FeatFrontmatter(status="progress")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


if __name__ == "__main__":
    unittest.main()
