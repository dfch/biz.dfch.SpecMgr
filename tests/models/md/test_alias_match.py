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

"""Unit tests for alias_match.space_separated_name / alias_match.match_alias."""

import unittest

from biz.dfch.specmgr.models.md.alias_match import match_alias, space_separated_name
from biz.dfch.specmgr.models.md.alias_type import AliasType


class TestSpaceSeparatedName(unittest.TestCase):
    """Tests for space_separated_name (PascalCase -> title case with spaces)."""

    def test_single_word_is_unchanged(self) -> None:
        self.assertEqual(space_separated_name("Scope"), "Scope")

    def test_two_words(self) -> None:
        self.assertEqual(space_separated_name("GoalInContext"), "Goal In Context")

    def test_three_words(self) -> None:
        self.assertEqual(space_separated_name("CharacteristicInformation"), "Characteristic Information")


class NoAliasMultiWord:
    """A class with no @alias metadata at all, and a multi-word class name.

    Deliberately not leading-underscore-prefixed (unlike this module's other
    fixtures): `space_separated_name` inserts a space before every
    non-leading uppercase letter with no special-casing for a leading
    underscore, so a name like `_NoAlias` would derive to the slightly odd
    `"_ No Alias"` -- irrelevant noise for what this fixture demonstrates.
    """


class _LiteralAlias:
    _alias_metadata = {"value": "Exact Title", "type": AliasType.LITERAL}


class GoalInContext:
    """Name deliberately mirrors a real fixture class, for SPACE_SEPARATED tests."""

    _alias_metadata = {"value": None, "type": AliasType.SPACE_SEPARATED}


class _RegexAlias:
    _alias_metadata = {"value": r"^(Goal|Scope).*", "type": AliasType.REGEX}


class _AcceptAnyNonEmptyHeading:
    _alias_metadata = {"value": ".+", "type": AliasType.REGEX}


class TestMatchAlias(unittest.TestCase):
    """Tests for match_alias, covering every AliasType plus the no-@alias case."""

    def test_class_with_no_alias_defaults_to_space_separated_class_name_match(self) -> None:
        """No @alias declared defaults to `AliasType.SPACE_SEPARATED`'s derivation
        of `cls.__name__`, not a literal match against the raw class name (ADR
        832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.4.0)."""
        self.assertTrue(match_alias(NoAliasMultiWord, "No Alias Multi Word"))

    def test_class_with_no_alias_rejects_the_raw_class_name(self) -> None:
        """The default is `SPACE_SEPARATED`, not `LITERAL`: the raw, un-spaced
        class name itself no longer matches."""
        self.assertFalse(match_alias(NoAliasMultiWord, "NoAliasMultiWord"))

    def test_class_with_no_alias_rejects_a_different_heading(self) -> None:
        """The space-separated-class-name default is not a wildcard: other text
        is rejected."""
        self.assertFalse(match_alias(NoAliasMultiWord, "literally anything"))

    def test_regex_alias_accepts_any_non_empty_heading_text(self) -> None:
        """The `.+` regex opt-out (ADR 832cd6c1 v1.3.1) accepts any non-empty text,
        but still rejects an empty heading."""
        self.assertTrue(match_alias(_AcceptAnyNonEmptyHeading, "Buy Goods"))
        self.assertTrue(match_alias(_AcceptAnyNonEmptyHeading, "*Emphasized* Title"))
        self.assertFalse(match_alias(_AcceptAnyNonEmptyHeading, ""))

    def test_literal_match(self) -> None:
        self.assertTrue(match_alias(_LiteralAlias, "Exact Title"))

    def test_literal_mismatch(self) -> None:
        self.assertFalse(match_alias(_LiteralAlias, "Not Exact Title"))

    def test_literal_is_case_sensitive_with_no_normalization(self) -> None:
        """LITERAL means literal: no case-folding, no trailing-parenthetical stripping."""
        self.assertFalse(match_alias(_LiteralAlias, "exact title"))
        self.assertFalse(match_alias(_LiteralAlias, "Exact Title (optional)"))

    def test_space_separated_match(self) -> None:
        self.assertTrue(match_alias(GoalInContext, "Goal In Context"))

    def test_space_separated_mismatch(self) -> None:
        self.assertFalse(match_alias(GoalInContext, "Goal in context"))

    def test_regex_match(self) -> None:
        self.assertTrue(match_alias(_RegexAlias, "Goal In Context"))
        self.assertTrue(match_alias(_RegexAlias, "Scope"))

    def test_regex_mismatch(self) -> None:
        self.assertFalse(match_alias(_RegexAlias, "Notes"))


if __name__ == "__main__":
    unittest.main()
