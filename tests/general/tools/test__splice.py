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

"""Tests for ``general.tools._splice``'s ``window_body`` and ``splice_body`` helpers (feat-28-get-update, Phase 2)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._splice import splice_body, window_body

_BODY = "l1\nl2\nl3\nl4\n"


class TestWindowBody(unittest.TestCase):
    """Tests for the no-I/O window_body helper (clamping, never erroring)."""

    def test_defaults_return_the_full_body_byte_for_byte(self) -> None:
        """No arguments (and explicit offset=1, limit=None) must equal a normal trailing-newline body byte-for-byte."""
        self.assertEqual(window_body(_BODY), _BODY)
        self.assertEqual(window_body(_BODY, 1, None), _BODY)

    def test_mid_window_returns_exactly_the_requested_lines(self) -> None:
        """offset=k, limit=m must return exactly lines k..k+m-1, each with its trailing newline, joined."""
        self.assertEqual(window_body(_BODY, 2, 2), "l2\nl3\n")
        self.assertEqual(window_body(_BODY, 2, 3), "l2\nl3\nl4\n")
        self.assertEqual(window_body(_BODY, 4, 1), "l4\n")

    def test_offset_past_last_line_returns_empty_string(self) -> None:
        """An offset past the last body line (offset > N) must return the empty string."""
        self.assertEqual(window_body(_BODY, 5), "")
        self.assertEqual(window_body(_BODY, 100, 3), "")

    def test_limit_caps_at_the_remaining_lines(self) -> None:
        """A limit larger than the remaining lines must cap at the remaining lines."""
        self.assertEqual(window_body(_BODY, 3, 99), "l3\nl4\n")
        self.assertEqual(window_body(_BODY, 1, 99), _BODY)

    def test_zero_limit_returns_empty_string(self) -> None:
        """limit=0 must return the empty string (an empty window)."""
        self.assertEqual(window_body(_BODY, 2, 0), "")

    def test_offset_below_one_floors_to_one(self) -> None:
        """An offset below 1 must floor to 1."""
        self.assertEqual(window_body(_BODY, 0, 2), "l1\nl2\n")
        self.assertEqual(window_body(_BODY, -5), _BODY)

    def test_negative_limit_returns_empty_string(self) -> None:
        """A negative limit must return the empty string."""
        self.assertEqual(window_body(_BODY, 1, -3), "")

    def test_empty_text_returns_empty_string(self) -> None:
        """An empty text must return the empty string for any coordinates."""
        self.assertEqual(window_body(""), "")
        self.assertEqual(window_body("", 1, None), "")
        self.assertEqual(window_body("", 2, 3), "")

    def test_consecutive_windows_reproduce_the_body(self) -> None:
        """Concatenating consecutive non-overlapping windows must reproduce the body."""
        self.assertEqual(window_body(_BODY, 1, 2) + window_body(_BODY, 3, 2), _BODY)
        self.assertEqual(window_body(_BODY, 1, 1) + window_body(_BODY, 2, 2) + window_body(_BODY, 4), _BODY)


class TestSpliceBody(unittest.TestCase):
    """Tests for the no-I/O splice_body helper's offset/limit signature (strict)."""

    def test_single_line_replace(self) -> None:
        """offset=k, limit=1 must replace line k only."""
        self.assertEqual(splice_body(_BODY, 2, 1, "x"), "l1\nx\nl3\nl4\n")

    def test_multi_line_replace(self) -> None:
        """offset=k, limit=m must replace exactly lines k..k+m-1."""
        self.assertEqual(splice_body(_BODY, 2, 2, "x"), "l1\nx\nl4\n")

    def test_omitted_limit_replaces_through_end(self) -> None:
        """An omitted limit must replace through the last body line."""
        self.assertEqual(splice_body(_BODY, 3, None, "x\ny"), "l1\nl2\nx\ny\n")

    def test_zero_limit_is_a_pure_insert(self) -> None:
        """limit=0 mid-body must insert content's lines before offset, dropping nothing."""
        self.assertEqual(splice_body(_BODY, 3, 0, "i"), "l1\nl2\ni\nl3\nl4\n")

    def test_offset_past_last_line_appends(self) -> None:
        """offset=N+1 (limit=0 or omitted) must append after the last line."""
        self.assertEqual(splice_body(_BODY, 5, 0, "a"), "l1\nl2\nl3\nl4\na\n")
        self.assertEqual(splice_body(_BODY, 5, None, "a"), "l1\nl2\nl3\nl4\na\n")

    def test_offset_below_one_raises_value_error(self) -> None:
        """offset < 1 must raise ValueError naming the offending value."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 0, 1, "x")
        message = str(ctx.exception)
        self.assertIn("offset", message)
        self.assertIn("0", message)

    def test_offset_above_n_plus_one_raises_value_error(self) -> None:
        """offset > N+1 must raise ValueError naming the offending value and the allowed range."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 6, 0, "x")
        message = str(ctx.exception)
        self.assertIn("offset", message)
        self.assertIn("6", message)
        self.assertIn("N+1", message)

    def test_negative_limit_raises_value_error(self) -> None:
        """limit < 0 must raise ValueError naming the offending value."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 1, -1, "x")
        message = str(ctx.exception)
        self.assertIn("limit", message)
        self.assertIn("-1", message)

    def test_range_past_end_raises_value_error(self) -> None:
        """offset + limit - 1 > N must raise ValueError naming the offending values."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 3, 3, "x")
        message = str(ctx.exception)
        self.assertIn("offset", message)
        self.assertIn("limit", message)
        self.assertIn("3", message)


if __name__ == "__main__":
    unittest.main()
