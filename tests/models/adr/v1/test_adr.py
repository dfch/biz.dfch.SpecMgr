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

"""Tests for the Adr Pydantic model (frontmatter + body composition)."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models import CURRENT_SCHEMA_VERSION, SCHEMA_MAJOR_VERSION, Adr, AdrBody, AdrFrontmatter


def _make_body() -> AdrBody:
    return AdrBody(
        title="A title",
        context_and_problem_statement="Some context",
        considered_options="* Option A",
        decision_outcome="Chosen option: A",
    )


class TestAdr(unittest.TestCase):
    """Tests for the Adr Pydantic model."""

    def test_holds_frontmatter_and_body(self):
        """An Adr must hold both a validated frontmatter and body."""
        adr = Adr(frontmatter=AdrFrontmatter(status="accepted"), body=_make_body())
        self.assertEqual(adr.frontmatter.status, "accepted")
        self.assertEqual(adr.body.title, "A title")

    def test_version_defaults_to_current_schema_version(self):
        """Omitting version must default to CURRENT_SCHEMA_VERSION."""
        adr = Adr(frontmatter=AdrFrontmatter(status="accepted"), body=_make_body())
        self.assertEqual(adr.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(adr.version, f"{SCHEMA_MAJOR_VERSION}.0.0")

    def test_version_accepts_matching_major_with_different_minor_patch(self):
        """A version with the same major but a different minor/patch must be accepted."""
        adr = Adr(
            version=f"{SCHEMA_MAJOR_VERSION}.4.2", frontmatter=AdrFrontmatter(status="accepted"), body=_make_body()
        )
        self.assertEqual(adr.version, f"{SCHEMA_MAJOR_VERSION}.4.2")

    def test_version_rejects_mismatched_major(self):
        """A version whose major component doesn't match this package's must be rejected."""
        with self.assertRaises(ValidationError):
            Adr(
                version=f"{SCHEMA_MAJOR_VERSION + 1}.0.0",
                frontmatter=AdrFrontmatter(status="accepted"),
                body=_make_body(),
            )

    def test_version_rejects_non_semver_string(self):
        """A malformed version string must be rejected."""
        with self.assertRaises(ValidationError):
            Adr(version="not-a-version", frontmatter=AdrFrontmatter(status="accepted"), body=_make_body())

    def test_accepts_nested_dicts(self):
        """Adr must validate nested plain dicts into the right sub-models."""
        adr = Adr.model_validate(
            {
                "frontmatter": {"status": "proposed"},
                "body": {
                    "title": "A title",
                    "context_and_problem_statement": "Some context",
                    "considered_options": "* Option A",
                    "decision_outcome": "Chosen option: A",
                },
            }
        )
        self.assertIsInstance(adr.frontmatter, AdrFrontmatter)
        self.assertIsInstance(adr.body, AdrBody)

    def test_invalid_nested_frontmatter_fails(self):
        """An invalid nested frontmatter must fail validation at the Adr level."""
        with self.assertRaises(ValidationError):
            Adr.model_validate(
                {
                    "frontmatter": {"status": "not-a-real-status"},
                    "body": {
                        "title": "A title",
                        "context_and_problem_statement": "Some context",
                        "considered_options": "* Option A",
                        "decision_outcome": "Chosen option: A",
                    },
                }
            )


if __name__ == "__main__":
    unittest.main()
