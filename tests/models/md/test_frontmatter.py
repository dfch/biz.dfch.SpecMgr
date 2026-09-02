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
        """created/updated must accept explicit conforming date+time strings verbatim."""
        frontmatter = MarkdownFrontmatter(
            type="uc", created="2026-08-05 00:00:00.000Z", updated="2026-08-11 00:00:00.000Z"
        )
        self.assertEqual(frontmatter.created, "2026-08-05 00:00:00.000Z")
        self.assertEqual(frontmatter.updated, "2026-08-11 00:00:00.000Z")

    def test_blank_created_and_updated_normalize_to_none(self):
        """A whitespace-only created/updated value must normalize to None."""
        frontmatter = MarkdownFrontmatter(type="uc", created="   ", updated="\t")
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)

    def test_created_and_updated_reject_date_only(self):
        """A date-only value (no time component) must be rejected (D5)."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", created="2026-08-05")

    def test_created_and_updated_reject_six_digit_microseconds(self):
        """A six-digit-fraction (microsecond) value must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", created="2026-08-05 12:00:00.123456Z")

    def test_created_and_updated_reject_t_separator(self):
        """A ``T``-separated value must be rejected -- only the space separator is accepted."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", created="2026-08-05T12:00:00.000Z")

    def test_created_and_updated_reject_timezone_less(self):
        """A value with no ``Z``/offset suffix at all must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", created="2026-08-05 12:00:00.000")

    def test_created_and_updated_reject_two_millisecond_digits(self):
        """A value with only two millisecond digits must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", created="2026-08-05 12:00:00.12Z")

    def test_created_and_updated_reject_four_millisecond_digits(self):
        """A value with four millisecond digits must be rejected."""
        with self.assertRaises(ValidationError):
            MarkdownFrontmatter(type="uc", created="2026-08-05 12:00:00.1234Z")

    def test_created_and_updated_accept_z_variant(self):
        """The exact ``Z`` (zero UTC offset) date+time variant must be accepted."""
        frontmatter = MarkdownFrontmatter(type="uc", created="2026-08-05 12:00:00.000Z")
        self.assertEqual(frontmatter.created, "2026-08-05 12:00:00.000Z")

    def test_created_and_updated_accept_signed_offset_variant(self):
        """The exact signed ``±HH:mm`` offset date+time variant must be accepted."""
        frontmatter = MarkdownFrontmatter(type="uc", created="2026-08-05 12:00:00.000+02:00")
        self.assertEqual(frontmatter.created, "2026-08-05 12:00:00.000+02:00")

        frontmatter_negative = MarkdownFrontmatter(type="uc", updated="2026-08-05 12:00:00.000-05:00")
        self.assertEqual(frontmatter_negative.updated, "2026-08-05 12:00:00.000-05:00")

    def test_created_and_updated_blank_still_becomes_none_and_passes(self):
        """A blank string must still become None via the before-validator, and pass this after-validator."""
        frontmatter = MarkdownFrontmatter(type="uc", created="   ")
        self.assertIsNone(frontmatter.created)

    def test_created_and_updated_explicit_none_passes(self):
        """An explicit None value must pass through unchanged."""
        frontmatter = MarkdownFrontmatter(type="uc", created=None, updated=None)
        self.assertIsNone(frontmatter.created)
        self.assertIsNone(frontmatter.updated)

    def test_classification_defaults_to_none(self):
        """classification must default to None when omitted."""
        frontmatter = MarkdownFrontmatter(type="uc")
        self.assertIsNone(frontmatter.classification)

    def test_classification_accepts_explicit_value(self):
        """An explicit, non-blank classification value must round-trip verbatim."""
        frontmatter = MarkdownFrontmatter(type="uc", classification="Confidential")
        self.assertEqual(frontmatter.classification, "Confidential")

    def test_classification_blank_normalizes_to_none(self):
        """An empty-string classification value must normalize to None."""
        frontmatter = MarkdownFrontmatter(type="uc", classification="")
        self.assertIsNone(frontmatter.classification)

    def test_classification_whitespace_only_normalizes_to_none(self):
        """A whitespace-only classification value must normalize to None."""
        frontmatter = MarkdownFrontmatter(type="uc", classification="   \t")
        self.assertIsNone(frontmatter.classification)

    def test_classification_absent_key_still_parses(self):
        """A pre-feature-style frontmatter dict without a classification key still parses (ACC-004)."""
        frontmatter = MarkdownFrontmatter.model_validate({"type": "uc", "status": "draft"})
        self.assertIsNone(frontmatter.classification)


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
