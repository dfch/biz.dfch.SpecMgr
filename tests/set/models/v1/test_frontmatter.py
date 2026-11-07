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

"""Tests for the SetFrontmatter Pydantic model (ACC-003, REQ-005)."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.set.models.v1.frontmatter import SetFrontmatter


class TestSetFrontmatter(unittest.TestCase):
    """Tests for the SetFrontmatter Pydantic model."""

    def test_type_defaults_to_set(self) -> None:
        sut = SetFrontmatter()

        self.assertEqual(sut.type, "set")

    def test_type_rejects_other_document_types(self) -> None:
        for other in ("req", "gol", "dec", "vcr", "sop"):
            with self.subTest(other=other):
                with self.assertRaises(ValidationError):
                    SetFrontmatter(type=other)

    def test_version_defaults_to_current_schema_version(self) -> None:
        sut = SetFrontmatter(status="progress")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self) -> None:
        sut = SetFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self) -> None:
        with self.assertRaises(ValidationError):
            SetFrontmatter(version="2.0.0")

    def test_accepts_exactly_the_four_statuses(self) -> None:
        for status in ("draft", "progress", "done", "review"):
            with self.subTest(status=status):
                self.assertEqual(SetFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaises(ValidationError):
            SetFrontmatter(status="in-review")

    def test_rejects_vcr_only_statuses(self) -> None:
        # "complete"/"approved" belong to VCR's four-value verification
        # lifecycle, not set's own four-value set.
        for status in ("complete", "approved"):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    SetFrontmatter(status=status)

    def test_rejects_dec_only_statuses(self) -> None:
        # "accepted"/"proposed"/etc. belong to DEC's six-value set, not set's four.
        for status in ("accepted", "proposed", "rejected", "superseded", "deprecated"):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    SetFrontmatter(status=status)

    def test_rejects_feat_only_status(self) -> None:
        # "planning" belongs to the feature-README status set, not set's four.
        with self.assertRaises(ValidationError):
            SetFrontmatter(status="planning")

    def test_status_defaults_to_draft(self) -> None:
        sut = SetFrontmatter()

        self.assertEqual(sut.status, "draft")

    def test_blank_status_defaults_to_draft(self) -> None:
        self.assertEqual(SetFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(SetFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self) -> None:
        sut = SetFrontmatter(status="progress")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)
        self.assertIsNone(sut.classification)

    def test_classification_is_optional_free_text(self) -> None:
        sut = SetFrontmatter(classification="internal")

        self.assertEqual(sut.classification, "internal")


if __name__ == "__main__":
    unittest.main()
