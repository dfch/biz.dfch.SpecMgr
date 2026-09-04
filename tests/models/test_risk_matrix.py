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

"""Tests for `parse_risk_matrix`, exercised end-to-end against the real, packaged
``rsk/data/rsk_risk_matrix.md`` (feat-92-resources Task 4.1, REQ-004), plus
fail-fast/malformed-content drift-guard tests (ACC-004), mirroring
``tests/models/test_tara.py``'s structure and style.
"""

from __future__ import annotations

import unittest

import pydantic

from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.rsk.models.v1 import RiskMatrix, level_from_product, parse_risk_matrix

#: A minimal, well-formed header shared by every fixture below -- everything
#: up to and including `## Zone table`, which stays leaf/unmodeled and so
#: does not need to be well-formed beyond parsing as ordinary prose.
_HEADER = """# The 5x5 risk matrix for `rsk` documents

Every `rsk` document carries two 5x5 assessments.

## Scale anchors

Probability and impact anchors go here.

## Zone table

The visual 5x5 table goes here.

"""

#: A well-formed footer shared by every fixture below -- the leaf, unmodeled
#: `## Reading initial and residual together` section.
_FOOTER = """
## Reading initial and residual together

- `## Initial Assessment` is the risk as identified.
"""


def _valid_risk_matrix_text() -> str:
    """Build a minimal, well-formed risk-matrix-shaped document."""
    thresholds = """## Product thresholds

The zone is derived from the product `p x i` (range 1..25):

- `1-4` \u2192 `low`
- `5-9` \u2192 `medium`
- `10-14` \u2192 `high`
- `15-25` \u2192 `very high`

These are the same thresholds the schema derives.
"""
    return _HEADER + thresholds + _FOOTER


#: A deliberately malformed document: only 3 of the required 4 threshold
#: bullets, so `ProductThresholds.items`'s `min_length=4`/`max_length=4`
#: constraint rejects it.
_MISSING_THRESHOLD_TEXT = (
    _HEADER
    + """## Product thresholds

The zone is derived from the product `p x i` (range 1..25):

- `1-4` \u2192 `low`
- `5-9` \u2192 `medium`
- `10-14` \u2192 `high`

These are the same thresholds the schema derives.
"""
    + _FOOTER
)

#: A deliberately malformed document: the zone names are out of order
#: (`medium` and `low` swapped), so `_validate_thresholds`'s ordered
#: vocabulary check rejects it.
_WRONG_ZONE_ORDER_TEXT = (
    _HEADER
    + """## Product thresholds

The zone is derived from the product `p x i` (range 1..25):

- `1-4` \u2192 `medium`
- `5-9` \u2192 `low`
- `10-14` \u2192 `high`
- `15-25` \u2192 `very high`

These are the same thresholds the schema derives.
"""
    + _FOOTER
)

#: A deliberately malformed document: the bounds are not contiguous (a gap
#: between `4` and `6`), so `_validate_thresholds`'s contiguity check
#: rejects it.
_NON_CONTIGUOUS_BOUNDS_TEXT = (
    _HEADER
    + """## Product thresholds

The zone is derived from the product `p x i` (range 1..25):

- `1-4` \u2192 `low`
- `6-9` \u2192 `medium`
- `10-14` \u2192 `high`
- `15-25` \u2192 `very high`

These are the same thresholds the schema derives.
"""
    + _FOOTER
)

#: A deliberately malformed document: the last band's stated zone
#: (`high`) does not match what `level_from_product` would actually derive
#: for `15-25` (`very high`), so `_validate_thresholds`'s
#: `level_from_product` cross-check rejects it.
_WRONG_ZONE_FOR_BOUNDS_TEXT = (
    _HEADER
    + """## Product thresholds

The zone is derived from the product `p x i` (range 1..25):

- `1-4` \u2192 `low`
- `5-9` \u2192 `medium`
- `10-14` \u2192 `high`
- `15-25` \u2192 `high`

These are the same thresholds the schema derives.
"""
    + _FOOTER
)


class TestParseRiskMatrix(unittest.TestCase):
    """Tests for `parse_risk_matrix` against the packaged risk-matrix guidance data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_packaged_text("rsk", "risk_matrix", "md")

    def test_returns_risk_matrix_instance(self):
        """The parser must return a `RiskMatrix` instance."""
        result = parse_risk_matrix(self.text)
        self.assertIsInstance(result, RiskMatrix)

    def test_has_four_threshold_items(self):
        """Exactly 4 product-threshold bullets."""
        result = parse_risk_matrix(self.text)
        self.assertEqual(len(result.product_thresholds.items), 4)

    def test_zone_names_in_order(self):
        """The 4 zone names must be exactly the closed vocabulary, in order."""
        result = parse_risk_matrix(self.text)
        zones = [item.zone for item in result.product_thresholds.items]
        self.assertEqual(zones, ["low", "medium", "high", "very high"])

    def test_bounds_exact(self):
        """The 4 bands' bounds must be exactly 1-4, 5-9, 10-14, 15-25."""
        result = parse_risk_matrix(self.text)
        bounds = [(item.low, item.high) for item in result.product_thresholds.items]
        self.assertEqual(bounds, [(1, 4), (5, 9), (10, 14), (15, 25)])

    def test_bounds_match_level_from_product(self):
        """Every band's bounds must match `level_from_product`'s own zone mapping."""
        result = parse_risk_matrix(self.text)
        for item in result.product_thresholds.items:
            with self.subTest(low=item.low, high=item.high, zone=item.zone):
                self.assertEqual(level_from_product(item.low), item.zone)
                self.assertEqual(level_from_product(item.high), item.zone)

    def test_parses_minimal_valid_fixture(self):
        """The hand-built minimal fixture used by the malformed-fixture tests below must itself parse."""
        result = parse_risk_matrix(_valid_risk_matrix_text())
        self.assertIsInstance(result, RiskMatrix)

    def test_raises_on_missing_threshold(self):
        """A document with only 3 of the 4 required threshold bullets must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_risk_matrix(_MISSING_THRESHOLD_TEXT)

    def test_raises_on_wrong_zone_order(self):
        """A threshold list whose zone names are out of order must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_risk_matrix(_WRONG_ZONE_ORDER_TEXT)

    def test_raises_on_non_contiguous_bounds(self):
        """A threshold list whose bounds are not contiguous must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_risk_matrix(_NON_CONTIGUOUS_BOUNDS_TEXT)

    def test_raises_on_wrong_zone_for_bounds(self):
        """A threshold entry whose stated zone doesn't match `level_from_product` must fail fast."""
        with self.assertRaises((AssertionError, pydantic.ValidationError)):
            parse_risk_matrix(_WRONG_ZONE_FOR_BOUNDS_TEXT)


if __name__ == "__main__":
    unittest.main()
