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

"""Tests for `UcFrontmatter` (narrows `MarkdownFrontmatter` for the `uc` type)."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models.v2 import UcFrontmatter


class TestUcFrontmatter(unittest.TestCase):
    """Tests for UcFrontmatter's `type`/`status` narrowing."""

    def test_type_defaults_to_uc(self) -> None:
        """`type` defaults to "uc" when omitted."""
        frontmatter = UcFrontmatter()
        self.assertEqual(frontmatter.type, "uc")

    def test_type_rejects_other_values(self) -> None:
        """`type` is a fixed Literal["uc"] -- any other value fails validation."""
        with self.assertRaises(ValidationError):
            UcFrontmatter(type="adr")

    def test_status_defaults_to_draft(self) -> None:
        """`status` defaults to "draft" (inherited from MarkdownFrontmatter)."""
        frontmatter = UcFrontmatter()
        self.assertEqual(frontmatter.status, "draft")

    def test_status_accepts_every_allowed_value(self) -> None:
        """`status` accepts each of the five allowed values."""
        for status in ("draft", "proposed", "accepted", "deprecated", "superseded"):
            with self.subTest(status=status):
                frontmatter = UcFrontmatter(status=status)
                self.assertEqual(frontmatter.status, status)

    def test_status_rejects_unknown_value(self) -> None:
        """`status` rejects a value outside the closed five-value set."""
        with self.assertRaises(ValidationError):
            UcFrontmatter(status="rejected")

    def test_status_rejects_adr_style_superseded_by_phrase(self) -> None:
        """Unlike AdrFrontmatter, "superseded by ..." is not a use-case status shape."""
        with self.assertRaises(ValidationError):
            UcFrontmatter(status="superseded by uc-002")

    def test_blank_status_defaults_to_draft(self) -> None:
        """A blank status string is normalized to "draft" before validation."""
        frontmatter = UcFrontmatter.model_validate({"status": ""})
        self.assertEqual(frontmatter.status, "draft")

    def test_id_defaults_to_none(self) -> None:
        """`id` (inherited) defaults to None, unlike v1's mandatory uc-NNN pattern."""
        frontmatter = UcFrontmatter()
        self.assertIsNone(frontmatter.id)

    def test_id_accepts_any_non_pattern_string(self) -> None:
        """`id` no longer enforces v1's `^uc-[0-9]+$` pattern -- any string is accepted,
        matching AdrFrontmatter.id's own specmgr-assigned-identifier convention."""
        frontmatter = UcFrontmatter(id="not-uc-shaped-at-all")
        self.assertEqual(frontmatter.id, "not-uc-shaped-at-all")

    def test_created_and_updated_default_to_none(self) -> None:
        """`created`/`updated` (inherited) default to None."""
        frontmatter = UcFrontmatter()
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)

    def test_version_defaults_to_current_schema_version(self) -> None:
        """`version` (inherited) defaults to the current models.md schema version."""
        from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION

        frontmatter = UcFrontmatter()
        self.assertEqual(frontmatter.version, CURRENT_SCHEMA_VERSION)


if __name__ == "__main__":
    unittest.main()
