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

"""Tests for the AdrFrontmatter Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models import CURRENT_SCHEMA_VERSION, SCHEMA_MAJOR_VERSION, AdrFrontmatter


class TestAdrFrontmatter(unittest.TestCase):
    """Tests for the AdrFrontmatter Pydantic model."""

    def test_version_defaults_to_current_schema_version(self):
        """Omitting version must default to CURRENT_SCHEMA_VERSION."""
        frontmatter = AdrFrontmatter(status="accepted")
        self.assertEqual(frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(frontmatter.version, f"{SCHEMA_MAJOR_VERSION}.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        """A version with the same major but a different minor/patch must be accepted."""
        frontmatter = AdrFrontmatter(status="accepted", version=f"{SCHEMA_MAJOR_VERSION}.4.2")
        self.assertEqual(frontmatter.version, f"{SCHEMA_MAJOR_VERSION}.4.2")

    def test_version_rejects_mismatched_major(self):
        """A version whose major component doesn't match this package's must be rejected."""
        with self.assertRaises(ValidationError):
            AdrFrontmatter(status="accepted", version=f"{SCHEMA_MAJOR_VERSION + 1}.0.0")

    def test_version_rejects_non_semver_string(self):
        """A malformed version string must be rejected."""
        with self.assertRaises(ValidationError):
            AdrFrontmatter(status="accepted", version="not-a-version")

    def test_accepts_each_fixed_status(self):
        """Each of the six fixed status values must be accepted."""
        for status in ("draft", "proposed", "rejected", "accepted", "deprecated", "superseded"):
            with self.subTest(status=status):
                self.assertEqual(AdrFrontmatter(status=status).status, status)

    def test_accepts_superseded_by_status(self):
        """A 'superseded by ...' status must be accepted verbatim."""
        frontmatter = AdrFrontmatter(status="superseded by ADR-0123")
        self.assertEqual(frontmatter.status, "superseded by ADR-0123")

    def test_rejects_unknown_status(self):
        """A status outside the fixed set and the superseded-by pattern must fail."""
        with self.assertRaises(ValidationError):
            AdrFrontmatter(status="in-review")

    def test_status_defaults_to_draft(self):
        """Omitting status must default to 'draft'."""
        frontmatter = AdrFrontmatter()
        self.assertEqual(frontmatter.status, "draft")

    def test_decision_makers_alias_accepts_hyphenated_key(self):
        """The frontmatter's literal YAML key 'decision-makers' must populate the field."""
        frontmatter = AdrFrontmatter.model_validate({"status": "accepted", "decision-makers": "Alice, Bob"})
        self.assertEqual(frontmatter.decision_makers, "Alice, Bob")

    def test_decision_makers_accepts_field_name(self):
        """The snake_case field name must also work (populate_by_name)."""
        frontmatter = AdrFrontmatter(status="accepted", decision_makers="Alice, Bob")
        self.assertEqual(frontmatter.decision_makers, "Alice, Bob")

    def test_blank_optional_fields_normalize_to_none(self):
        """A whitespace-only optional field must normalize to None."""
        frontmatter = AdrFrontmatter(status="accepted", date="   ", consulted="", informed="\t")
        self.assertIsNone(frontmatter.date)
        self.assertIsNone(frontmatter.consulted)
        self.assertIsNone(frontmatter.informed)

    def test_optional_fields_default_to_none(self):
        """date, decision-makers, consulted, informed default to None when omitted."""
        frontmatter = AdrFrontmatter(status="proposed")
        self.assertIsNone(frontmatter.date)
        self.assertIsNone(frontmatter.decision_makers)
        self.assertIsNone(frontmatter.consulted)
        self.assertIsNone(frontmatter.informed)


if __name__ == "__main__":
    unittest.main()
