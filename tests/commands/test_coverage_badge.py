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

"""Tests for the ``coverage-badge`` command."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.commands.coverage_badge import (
    _color_for_coverage,
    _get_coverage_percentage,
    _render_svg_badge,
)


class TestColorForCoverage(unittest.TestCase):
    """Tests for coverage percentage to color mapping."""

    def test_90_and_above_returns_green(self):
        """Coverage ≥90% should map to green."""
        self.assertEqual(_color_for_coverage(90.0), "green")
        self.assertEqual(_color_for_coverage(95.5), "green")
        self.assertEqual(_color_for_coverage(100.0), "green")

    def test_75_to_89_returns_yellowgreen(self):
        """Coverage ≥75% and <90% should map to yellowgreen."""
        self.assertEqual(_color_for_coverage(75.0), "yellowgreen")
        self.assertEqual(_color_for_coverage(80.0), "yellowgreen")
        self.assertEqual(_color_for_coverage(89.9), "yellowgreen")

    def test_50_to_74_returns_yellow(self):
        """Coverage ≥50% and <75% should map to yellow."""
        self.assertEqual(_color_for_coverage(50.0), "yellow")
        self.assertEqual(_color_for_coverage(60.0), "yellow")
        self.assertEqual(_color_for_coverage(74.9), "yellow")

    def test_below_50_returns_red(self):
        """Coverage <50% should map to red."""
        self.assertEqual(_color_for_coverage(0.0), "red")
        self.assertEqual(_color_for_coverage(25.0), "red")
        self.assertEqual(_color_for_coverage(49.9), "red")


class TestRenderSvgBadge(unittest.TestCase):
    """Tests for SVG badge rendering."""

    def test_returns_valid_svg_string(self):
        """Badge rendering must return a valid SVG XML string."""
        svg = _render_svg_badge(75.0)
        self.assertIsInstance(svg, str)
        self.assertIn("<svg", svg)
        self.assertIn("xmlns=", svg)
        self.assertIn("</svg>", svg)

    def test_svg_contains_coverage_percentage(self):
        """SVG must include the coverage percentage in the badge label."""
        svg = _render_svg_badge(82.5)
        self.assertIn("82%", svg)

    def test_svg_contains_aria_label(self):
        """SVG must include proper accessibility labels."""
        svg = _render_svg_badge(75.0)
        self.assertIn("coverage: 75%", svg)

    def test_svg_color_matches_coverage_level(self):
        """SVG fill color must correspond to coverage percentage."""
        # Green SVG contains the green color hex
        svg_green = _render_svg_badge(95.0)
        self.assertIn("#4c1", svg_green)  # Green color

        # Yellow SVG contains the yellow color hex
        svg_yellow = _render_svg_badge(60.0)
        self.assertIn("#dfb317", svg_yellow)  # Yellow color

        # Red SVG contains the red color hex
        svg_red = _render_svg_badge(20.0)
        self.assertIn("#e05d44", svg_red)  # Red color


class TestGetCoveragePercentage(unittest.TestCase):
    """Tests for coverage data loading."""

    def test_missing_coverage_file_raises_exit(self):
        """Missing .coverage file should exit with clear error message."""
        with tempfile.TemporaryDirectory() as tmp:
            original_path = Path

            def mock_path(arg):
                if arg == ".coverage":
                    # Return path to non-existent file
                    return original_path(tmp) / ".coverage"
                return original_path(arg)

            with mock.patch("biz.dfch.specmgr.commands.coverage_badge.Path", side_effect=mock_path):
                with self.assertRaises(SystemExit):
                    _get_coverage_percentage()

    def test_loads_coverage_from_file(self):
        """Must instantiate Coverage and call load() on it."""
        with tempfile.TemporaryDirectory() as tmp:
            coverage_file = Path(tmp) / ".coverage"
            coverage_file.write_bytes(b"coverage_data")  # Create the file

            original_path = Path

            def mock_path(arg):
                if arg == ".coverage":
                    return coverage_file
                return original_path(arg)

            with mock.patch("biz.dfch.specmgr.commands.coverage_badge.Path", side_effect=mock_path):
                with mock.patch("coverage.Coverage") as mock_coverage_class:
                    mock_cov = mock.MagicMock()
                    mock_cov.report.return_value = 87.5
                    mock_coverage_class.return_value = mock_cov

                    result = _get_coverage_percentage()
                    self.assertEqual(result, 87.5)
                    mock_coverage_class.assert_called_once()
                    mock_cov.load.assert_called_once()

    def test_returns_coverage_percentage_as_float(self):
        """Must return the coverage percentage as a float."""
        with tempfile.TemporaryDirectory() as tmp:
            coverage_file = Path(tmp) / ".coverage"
            coverage_file.write_bytes(b"coverage_data")

            original_path = Path

            def mock_path(arg):
                if arg == ".coverage":
                    return coverage_file
                return original_path(arg)

            with mock.patch("biz.dfch.specmgr.commands.coverage_badge.Path", side_effect=mock_path):
                with mock.patch("coverage.Coverage") as mock_coverage_class:
                    mock_cov = mock.MagicMock()
                    mock_cov.report.return_value = 42.7
                    mock_coverage_class.return_value = mock_cov

                    result = _get_coverage_percentage()
                    self.assertIsInstance(result, float)
                    self.assertEqual(result, 42.7)


if __name__ == "__main__":
    unittest.main()
