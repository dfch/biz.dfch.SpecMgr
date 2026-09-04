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

"""Tests for `parse_dtais`, exercised end-to-end against the real, packaged
``general/data/general_dtais.md`` (feat-92-resources Task 2.1, REQ-002),
plus fail-fast/malformed-content drift-guard tests (ACC-002), mirroring
``tests/models/test_iso25010.py``'s structure and style.
"""

from __future__ import annotations

import unittest

import pydantic

from biz.dfch.specmgr.general.models import Dtais, parse_dtais
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: A deliberately malformed document: only 4 of the required 5 intro method
#: bullets, so `Dtais.methods`'s `min_length=5`/`max_length=5` constraint
#: rejects it.
_MISSING_METHOD_TEXT = """# DTAIS Verification Methods

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria`:

- `Demonstration` -- observing the system in operation.
- `Test` -- exercising the system under controlled conditions.
- `Analysis` -- using calculation, modeling, or simulation.
- `Inspection` -- visual or procedural examination of the system.

## When to apply each method

- **`Demonstration`** -- use when the criterion is about observable behavior.
- **`Test`** -- use when the criterion states a quantitative threshold.
- **`Analysis`** -- use when direct observation is not practical.
- **`Inspection`** -- use when the criterion is about the presence of an artifact.

## Relationship to `## Coverage`

`## Coverage` is the document-level roll-up of every criterion's status.

- **`full`** -- every acceptance criterion has been verified.
- **`partial`** -- at least one criterion has been verified, but not all.
- **`none`** -- no acceptance criterion has been successfully verified yet.

`## Coverage` always reflects the least-verified criterion in the set.
"""

#: A deliberately malformed document: the "when to apply" list's last word
#: (`Analysis`, not `Special`) does not match the corresponding intro
#: method word, so `Dtais._validate_when_to_apply_matches_methods` rejects
#: it.
_MISMATCHED_WHEN_TO_APPLY_TEXT = """# DTAIS Verification Methods

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria`:

- `Demonstration` -- observing the system in operation.
- `Test` -- exercising the system under controlled conditions.
- `Analysis` -- using calculation, modeling, or simulation.
- `Inspection` -- visual or procedural examination of the system.
- `Special` -- any other verification approach not covered above.

## When to apply each method

- **`Demonstration`** -- use when the criterion is about observable behavior.
- **`Test`** -- use when the criterion states a quantitative threshold.
- **`Inspection`** -- use when the criterion is about the presence of an artifact.
- **`Analysis`** -- use when direct observation is not practical.
- **`Analysis`** -- use for verification approaches outside the other four.

## Relationship to `## Coverage`

`## Coverage` is the document-level roll-up of every criterion's status.

- **`full`** -- every acceptance criterion has been verified.
- **`partial`** -- at least one criterion has been verified, but not all.
- **`none`** -- no acceptance criterion has been successfully verified yet.

`## Coverage` always reflects the least-verified criterion in the set.
"""

#: A deliberately malformed document: the coverage list has only 2 of the
#: required 3 values, so `CoverageRelationship.items`'s
#: `min_length=3`/`max_length=3` constraint rejects it.
_WRONG_COVERAGE_COUNT_TEXT = """# DTAIS Verification Methods

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria`:

- `Demonstration` -- observing the system in operation.
- `Test` -- exercising the system under controlled conditions.
- `Analysis` -- using calculation, modeling, or simulation.
- `Inspection` -- visual or procedural examination of the system.
- `Special` -- any other verification approach not covered above.

## When to apply each method

- **`Demonstration`** -- use when the criterion is about observable behavior.
- **`Test`** -- use when the criterion states a quantitative threshold.
- **`Analysis`** -- use when direct observation is not practical.
- **`Inspection`** -- use when the criterion is about the presence of an artifact.
- **`Special`** -- use for verification approaches outside the other four.

## Relationship to `## Coverage`

`## Coverage` is the document-level roll-up of every criterion's status.

- **`full`** -- every acceptance criterion has been verified.
- **`partial`** -- at least one criterion has been verified, but not all.

`## Coverage` always reflects the least-verified criterion in the set.
"""

#: A deliberately malformed document: the coverage list has 3 values, but
#: one (`unknown`) is not in the closed `full`/`partial`/`none` vocabulary,
#: so `CoverageRelationship._validate_coverage_values` rejects it.
_WRONG_COVERAGE_VALUES_TEXT = """# DTAIS Verification Methods

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria`:

- `Demonstration` -- observing the system in operation.
- `Test` -- exercising the system under controlled conditions.
- `Analysis` -- using calculation, modeling, or simulation.
- `Inspection` -- visual or procedural examination of the system.
- `Special` -- any other verification approach not covered above.

## When to apply each method

- **`Demonstration`** -- use when the criterion is about observable behavior.
- **`Test`** -- use when the criterion states a quantitative threshold.
- **`Analysis`** -- use when direct observation is not practical.
- **`Inspection`** -- use when the criterion is about the presence of an artifact.
- **`Special`** -- use for verification approaches outside the other four.

## Relationship to `## Coverage`

`## Coverage` is the document-level roll-up of every criterion's status.

- **`full`** -- every acceptance criterion has been verified.
- **`partial`** -- at least one criterion has been verified, but not all.
- **`unknown`** -- no acceptance criterion has been successfully verified yet.

`## Coverage` always reflects the least-verified criterion in the set.
"""


class TestParseDtais(unittest.TestCase):
    """Tests for `parse_dtais` against the packaged DTAIS guidance data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("general", "dtais", "md")

    def test_returns_dtais_instance(self):
        """The parser must return a `Dtais` instance."""
        result = parse_dtais(self.text)
        self.assertIsInstance(result, Dtais)

    def test_has_five_methods_and_five_when_to_apply_items(self):
        """Exactly 5 intro method bullets and exactly 5 'when to apply' bullets."""
        result = parse_dtais(self.text)
        self.assertEqual(len(result.methods), 5)
        self.assertEqual(len(result.when_to_apply.items), 5)

    def test_has_three_coverage_items(self):
        """Exactly 3 coverage bullets."""
        result = parse_dtais(self.text)
        self.assertEqual(len(result.coverage.items), 3)

    def test_method_words(self):
        """The 5 method words must be exactly the DTAIS vocabulary, in order."""
        result = parse_dtais(self.text)
        words = [item.method for item in result.methods]
        self.assertEqual(words, ["Demonstration", "Test", "Analysis", "Inspection", "Special"])

    def test_when_to_apply_words_match_methods(self):
        """The 'when to apply' words must match the intro method words, in order."""
        result = parse_dtais(self.text)
        words = [item.method for item in result.when_to_apply.items]
        self.assertEqual(words, ["Demonstration", "Test", "Analysis", "Inspection", "Special"])

    def test_coverage_values(self):
        """The 3 coverage values must be exactly `full`/`partial`/`none`, in order."""
        result = parse_dtais(self.text)
        values = [item.value for item in result.coverage.items]
        self.assertEqual(values, ["full", "partial", "none"])

    def test_raises_on_missing_method(self):
        """A document with only 4 of the 5 required intro method bullets must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_dtais(_MISSING_METHOD_TEXT)

    def test_raises_on_mismatched_when_to_apply(self):
        """A 'when to apply' list whose words don't match the intro method list must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_dtais(_MISMATCHED_WHEN_TO_APPLY_TEXT)

    def test_raises_on_wrong_coverage_count(self):
        """A coverage list with only 2 of the required 3 values must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_dtais(_WRONG_COVERAGE_COUNT_TEXT)

    def test_raises_on_wrong_coverage_values(self):
        """A coverage list whose values are not exactly `full`/`partial`/`none` must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_dtais(_WRONG_COVERAGE_VALUES_TEXT)


if __name__ == "__main__":
    unittest.main()
