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

"""Tests for the SopFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.sop.models.v1.frontmatter import SopFrontmatter


class TestSopFrontmatter(unittest.TestCase):
    """Tests for the SopFrontmatter Pydantic model."""

    def test_type_defaults_to_sop(self) -> None:
        sut = SopFrontmatter()

        self.assertEqual(sut.type, "sop")

    def test_type_rejects_other_document_types(self) -> None:
        for other in ("req", "gol", "dec", "adr", "rsk"):
            with self.subTest(other=other):
                with self.assertRaises(ValidationError):
                    SopFrontmatter(type=other)

    def test_version_defaults_to_current_schema_version(self) -> None:
        sut = SopFrontmatter(status="active")

        self.assertEqual(sut.version, "1.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self) -> None:
        sut = SopFrontmatter(version="1.4.2")

        self.assertEqual(sut.version, "1.4.2")

    def test_version_rejects_mismatched_major(self) -> None:
        with self.assertRaises(ValidationError):
            SopFrontmatter(version="2.0.0")

    def test_accepts_all_five_statuses(self) -> None:
        for status in ("draft", "review", "approved", "active", "retired"):
            with self.subTest(status=status):
                self.assertEqual(SopFrontmatter(status=status).status, status)

    def test_rejects_unknown_status(self) -> None:
        with self.assertRaises(ValidationError):
            SopFrontmatter(status="in-review")

    def test_rejects_dec_only_proposed_status(self) -> None:
        # "proposed" belongs to DEC/GOL's set, not SOP's five-value set.
        with self.assertRaises(ValidationError):
            SopFrontmatter(status="proposed")

    def test_rejects_gol_only_implemented_status(self) -> None:
        # "implemented" belongs to GOL's seven-value set, not SOP's five.
        with self.assertRaises(ValidationError):
            SopFrontmatter(status="implemented")

    def test_rejects_dec_only_superseded_status(self) -> None:
        # "superseded"/"deprecated"/"rejected" belong to DEC's six-value set,
        # not SOP's five-value approval/effectivity lifecycle.
        for status in ("superseded", "deprecated", "rejected"):
            with self.subTest(status=status):
                with self.assertRaises(ValidationError):
                    SopFrontmatter(status=status)

    def test_status_defaults_to_draft(self) -> None:
        sut = SopFrontmatter()

        self.assertEqual(sut.status, "draft")

    def test_blank_status_defaults_to_draft(self) -> None:
        self.assertEqual(SopFrontmatter.model_validate({"status": None}).status, "draft")
        self.assertEqual(SopFrontmatter.model_validate({"status": "   "}).status, "draft")

    def test_optional_fields_default_to_none(self) -> None:
        sut = SopFrontmatter(status="review")

        self.assertIsNone(sut.id)
        self.assertIsNone(sut.created)
        self.assertIsNone(sut.updated)


if __name__ == "__main__":
    unittest.main()
