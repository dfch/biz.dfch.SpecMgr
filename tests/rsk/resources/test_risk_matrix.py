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

"""Tests for the `specmgr://rsk/risk-matrix` resource (`rsk.resources.risk_matrix.risk_matrix`).

Includes the feature README's ACC-005 drift guard: the documented product
thresholds and the documented 5x5 zone table must match
`rsk.models.v1.assessment.level_from_product`'s own mapping, so the packaged
domain-knowledge text and the model's derived `level` can never silently
diverge.
"""

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.rsk.models.v1 import (
    LEVEL_HIGH,
    LEVEL_LOW,
    LEVEL_MEDIUM,
    LEVEL_VERY_HIGH,
    level_from_product,
)
from biz.dfch.specmgr.rsk.models.v1.assessment import HIGH_PRODUCT_MAX, LOW_PRODUCT_MAX, MEDIUM_PRODUCT_MAX
from biz.dfch.specmgr.rsk.resources.risk_matrix import risk_matrix

#: A documented product-threshold line, e.g. ``- `1-4` → `low``.
_THRESHOLD_LINE = re.compile(r"^-\s*`(\d+)-(\d+)`\s*→\s*`([^`]+)`\s*$", re.MULTILINE)


def _zone_table(text: str) -> dict[tuple[int, int], str]:
    """Extract the documented 5x5 zone table's cells: (probability, impact) -> zone."""
    cells: dict[tuple[int, int], str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        columns = [column.strip() for column in stripped.strip("|").split("|")]
        if len(columns) != 6 or not columns[0].isdigit():
            continue
        probability = int(columns[0])
        for impact, zone in enumerate(columns[1:], start=1):
            cells[(probability, impact)] = zone
    return cells


class TestRskRiskMatrixResource(unittest.TestCase):
    """Tests for the `risk_matrix` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = risk_matrix

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# The 5x5 risk matrix"))
        self.assertIn("## Scale anchors", result)
        self.assertIn("## Zone table", result)
        self.assertIn("## Product thresholds", result)
        self.assertIn("## Reading initial and residual together", result)

    def test_documented_product_thresholds_match_the_model(self):
        """ACC-005 drift guard: the documented bands (1-4 low, 5-9 medium, 10-14 high,
        15-25 very high) must match `level_from_product`'s own zone mapping, including
        every band boundary.
        """
        result = risk_matrix()

        bands = _THRESHOLD_LINE.findall(result)

        self.assertEqual(len(bands), 4)
        zones = [zone for _low, _high, zone in bands]
        self.assertEqual(zones, [LEVEL_LOW, LEVEL_MEDIUM, LEVEL_HIGH, LEVEL_VERY_HIGH])

        bounds = [(int(low), int(high)) for low, high, _zone in bands]
        self.assertEqual(bounds[0][0], 1)
        self.assertEqual(bounds[0][1], LOW_PRODUCT_MAX)
        self.assertEqual(bounds[1][1], MEDIUM_PRODUCT_MAX)
        self.assertEqual(bounds[2][1], HIGH_PRODUCT_MAX)
        self.assertEqual(bounds[3][0], HIGH_PRODUCT_MAX + 1)
        self.assertEqual(bounds[3][1], 25)  # the 5 x 5 maximum product
        # The bands are contiguous: each one starts where the previous one ends.
        for previous, current in zip(bounds, bounds[1:]):
            self.assertEqual(current[0], previous[1] + 1)

        for low, high, zone in bands:
            self.assertEqual(level_from_product(int(low)), zone)
            self.assertEqual(level_from_product(int(high)), zone)

    def test_documented_zone_table_matches_the_model(self):
        """Every one of the 25 documented table cells must match `level_from_product`."""
        result = risk_matrix()

        cells = _zone_table(result)

        self.assertEqual(len(cells), 25)
        for probability in range(1, 6):
            for impact in range(1, 6):
                with self.subTest(probability=probability, impact=impact):
                    self.assertEqual(cells[(probability, impact)], level_from_product(probability * impact))

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            matrix_path = Path(tmp) / "rsk_risk_matrix.md"
            matrix_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=matrix_path):
                sut = risk_matrix

                first = sut()
                matrix_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged rsk_risk_matrix.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = risk_matrix

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
