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

"""Tests for the MarkdownFrontmatter Pydantic model."""

import unittest
from typing import Literal

from pydantic import ValidationError

from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION, SCHEMA_MAJOR_VERSION, MarkdownFrontmatter


class _UcFrontmatter(MarkdownFrontmatter):
    """A concrete document-type subclass narrowing `type` to a fixed Literal, per the ADR."""

    type: Literal["uc"] = "uc"


class TestMarkdownFrontmatter(unittest.TestCase):
    """Tests for the MarkdownFrontmatter Pydantic model."""

    def test_type_is_mandatory(self):
        """The base model requires `type` -- there is no accept-anything default."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter()

    def test_type_rejects_blank(self):
        """A blank/whitespace-only `type` must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="   ")

    def test_type_accepts_explicit_value(self):
        """An explicit, non-blank `type` must be accepted verbatim."""
        frontmatter = MarkdownFrontmatter(type="uc")
        self.assertEqual(frontmatter.type, "uc")

    def test_version_defaults_to_current_schema_version(self):
        """Omitting version must default to CURRENT_SCHEMA_VERSION."""
        frontmatter = MarkdownFrontmatter(type="uc")
        self.assertEqual(frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(frontmatter.version, f"{SCHEMA_MAJOR_VERSION}.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        """A version with the same major but a different minor/patch must be accepted."""
        frontmatter = MarkdownFrontmatter(type="uc", version=f"{SCHEMA_MAJOR_VERSION}.4.2")
        self.assertEqual(frontmatter.version, f"{SCHEMA_MAJOR_VERSION}.4.2")

    def test_version_rejects_mismatched_major(self):
        """A version whose major component doesn't match this package's must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", version=f"{SCHEMA_MAJOR_VERSION + 1}.0.0")

    def test_version_rejects_non_semver_string(self):
        """A malformed version string must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", version="not-a-version")

    def test_status_defaults_to_draft(self):
        """Omitting status must default to 'draft'."""
        frontmatter = MarkdownFrontmatter(type="uc")
        self.assertEqual(frontmatter.status, "draft")

    def test_status_blank_or_none_defaults_to_draft(self):
        """An explicit but blank/None status must also default to 'draft'."""
        self.assertEqual(MarkdownFrontmatter.model_validate({"type": "uc", "status": None}).status, "draft")
        self.assertEqual(MarkdownFrontmatter.model_validate({"type": "uc", "status": "   "}).status, "draft")

    def test_status_accepts_arbitrary_free_form_value(self):
        """Unlike AdrFrontmatter, status is not restricted to a fixed enum here."""
        frontmatter = MarkdownFrontmatter(type="uc", status="in-review")
        self.assertEqual(frontmatter.status, "in-review")

    def test_id_defaults_to_none(self):
        """id must default to None -- existing/hand-authored files without one still parse."""
        frontmatter = MarkdownFrontmatter(type="uc")
        self.assertIsNone(frontmatter.id)

    def test_id_accepts_explicit_string(self):
        """id must accept an explicit string."""
        frontmatter = MarkdownFrontmatter(type="uc", id="11111111-1111-1111-1111-111111111111")
        self.assertEqual(frontmatter.id, "11111111-1111-1111-1111-111111111111")

    def test_created_and_updated_default_to_none(self):
        """created/updated default to None when omitted."""
        frontmatter = MarkdownFrontmatter(type="uc")
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)

    def test_created_and_updated_accept_explicit_values(self):
        """created/updated must accept explicit date-like strings verbatim."""
        frontmatter = MarkdownFrontmatter(type="uc", created="2026-08-05", updated="2026-08-11")
        self.assertEqual(frontmatter.created, "2026-08-05")
        self.assertEqual(frontmatter.updated, "2026-08-11")

    def test_blank_created_and_updated_normalize_to_none(self):
        """A whitespace-only created/updated value must normalize to None."""
        frontmatter = MarkdownFrontmatter(type="uc", created="   ", updated="\t")
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)


class TestMarkdownFrontmatterSubclassing(unittest.TestCase):
    """Tests for the document-type subclassing pattern (ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29)."""

    def test_subclass_defaults_type_to_its_own_literal_value(self):
        """A subclass narrowing `type` to a Literal with a default needs no explicit `type=`."""
        frontmatter = _UcFrontmatter()
        self.assertEqual(frontmatter.type, "uc")

    def test_subclass_rejects_mismatched_type(self):
        """A subclass's Literal-narrowed `type` must reject any other value."""
        with self.assertRaises(ValidationError):
            _UcFrontmatter(type="req")

    def test_subclass_inherits_core_field_defaults(self):
        """A subclass must still inherit status/version defaults from the base model."""
        frontmatter = _UcFrontmatter()
        self.assertEqual(frontmatter.status, "draft")
        self.assertEqual(frontmatter.version, CURRENT_SCHEMA_VERSION)

    def test_subclass_accepts_its_own_additional_fields(self):
        """A subclass may declare further fields beyond the core set."""

        class _WithExtra(MarkdownFrontmatter):
            type: Literal["uc"] = "uc"
            decision_makers: str | None = None

        frontmatter = _WithExtra(decision_makers="Alice, Bob")
        self.assertEqual(frontmatter.decision_makers, "Alice, Bob")


if __name__ == "__main__":
    unittest.main()
