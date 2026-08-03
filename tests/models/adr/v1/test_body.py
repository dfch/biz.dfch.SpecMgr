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

"""Tests for the AdrBody Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models import AdrBody, AdrOption

_MANDATORY_FIELDS = {
    "title": "A title",
    "context_and_problem_statement": "Some context",
    "considered_options": "* Option A\n* Option B",
    "decision_outcome": "Chosen option: A",
}


class TestAdrBody(unittest.TestCase):
    """Tests for the AdrBody Pydantic model."""

    def test_accepts_only_mandatory_fields(self):
        """A body with just the four mandatory fields must validate."""
        body = AdrBody(**_MANDATORY_FIELDS)
        self.assertEqual(body.title, "A title")
        self.assertIsNone(body.decision_drivers)
        self.assertIsNone(body.consequences)
        self.assertIsNone(body.confirmation)
        self.assertIsNone(body.more_information)
        self.assertEqual(body.options, [])

    def test_missing_mandatory_field_fails(self):
        """Omitting a mandatory field must fail validation."""
        fields = dict(_MANDATORY_FIELDS)
        del fields["decision_outcome"]
        with self.assertRaises(ValidationError):
            AdrBody(**fields)

    def test_blank_mandatory_field_fails(self):
        """A whitespace-only mandatory field must fail validation, not silently pass."""
        fields = dict(_MANDATORY_FIELDS)
        fields["title"] = "   "
        with self.assertRaises(ValidationError):
            AdrBody(**fields)

    def test_blank_optional_field_normalizes_to_none(self):
        """A whitespace-only optional field must normalize to None."""
        body = AdrBody(**_MANDATORY_FIELDS, decision_drivers="  ", consequences="", confirmation="\t")
        self.assertIsNone(body.decision_drivers)
        self.assertIsNone(body.consequences)
        self.assertIsNone(body.confirmation)

    def test_holds_option_collection(self):
        """options must hold validated AdrOption instances."""
        body = AdrBody(
            **_MANDATORY_FIELDS,
            options=[
                {"number": 1, "partial_title": "Use Postgres", "content": "Good, because ..."},
                AdrOption(number=2, partial_title="Use SQLite", content="Bad, because ..."),
            ],
        )
        self.assertEqual(len(body.options), 2)
        self.assertIsInstance(body.options[0], AdrOption)
        self.assertEqual(body.options[0].full_title, "Option 1: Use Postgres")
        self.assertEqual(body.options[1].full_title, "Option 2: Use SQLite")


if __name__ == "__main__":
    unittest.main()
