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

"""Tests for ``general.tools._timestamps`` (feat-38-39-41-43-44 Phase 3, Task 3.1; the ``T``-canonical
form since feat-146 Phase 1).

Covers the machine-written canonical date+time formatting shape (feat-146,
ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf): `T`-separated (ISO 8601's
standard extended combined form; the read side accepts the space separator
too, but the MCP write side always emits `T`), `Z` for a zero UTC offset, a
signed `±HH:mm` offset otherwise, milliseconds truncated (not rounded) to
exactly three digits, and `now_timestamp()`'s own output matching the
canonical date+time regex end to end. (The previous `format_date` helper --
a `yyyy-MM-dd`-only variant for the date-only entry-heading bodies
feat-38-39-41-43-44 D4/REQ-004 allowed -- was removed in feat-146 Phase 1:
entry headings are date+time-only in every domain now, so it had zero
callers; its two tests are replaced by the two `T`-separator tests below.)
"""

from __future__ import annotations

import re
import unittest
from datetime import datetime, timedelta, timezone

from biz.dfch.specmgr.general.tools._timestamps import format_timestamp, now_timestamp

#: The machine-written canonical date+time variant (feat-146): `T`-separated,
#: exactly three millisecond digits, `Z` or a signed `±HH:mm` offset.
_DATE_TIME_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$")


class TestFormatTimestamp(unittest.TestCase):
    """Tests for `format_timestamp()`."""

    def test_zero_offset_produces_z_suffix(self) -> None:
        """An aware datetime with a zero UTC offset must format with a `Z` suffix, not `+00:00`."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000, tzinfo=timezone.utc)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123Z")

    def test_positive_offset_produces_signed_hh_mm(self) -> None:
        """A non-zero positive UTC offset must format as `+HH:mm`."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000, tzinfo=timezone(timedelta(hours=2)))
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123+02:00")

    def test_negative_offset_produces_signed_hh_mm(self) -> None:
        """A non-zero negative UTC offset must format as `-HH:mm`."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000, tzinfo=timezone(timedelta(hours=-5)))
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123-05:00")

    def test_microseconds_are_truncated_not_rounded(self) -> None:
        """Six-digit microseconds must be truncated (not rounded) to exactly three digits.

        999 microseconds truncates to `.000`, not rounded up to `.001` --
        this is the deliberately simpler behavior (feat-38-39-41-43-44
        REQ-007's own wording: "truncated to exactly three digits").
        """
        dt = datetime(2026, 9, 1, 12, 30, 45, 999, tzinfo=timezone.utc)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.000Z")

    def test_microseconds_truncation_drops_lower_digits(self) -> None:
        """`123456` microseconds truncates to `123` milliseconds, not `123` rounded from `456`."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123456, tzinfo=timezone.utc)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123Z")

    def test_milliseconds_are_always_exactly_three_digits(self) -> None:
        """A small microsecond value must still zero-pad to three millisecond digits."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 5000, tzinfo=timezone.utc)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.005Z")

    def test_naive_datetime_has_no_suffix(self) -> None:
        """A naive datetime (no tzinfo) must format with no `Z`/offset suffix at all."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123")

    def test_result_matches_date_time_regex(self) -> None:
        """An aware datetime's formatted result must fullmatch the canonical date+time regex."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000, tzinfo=timezone(timedelta(hours=2)))
        self.assertRegex(format_timestamp(dt), _DATE_TIME_REGEX)


class TestNowTimestamp(unittest.TestCase):
    """Tests for `now_timestamp()`."""

    def test_output_matches_date_time_regex(self) -> None:
        """`now_timestamp()`'s own output must fullmatch the canonical date+time regex."""
        self.assertRegex(now_timestamp(), _DATE_TIME_REGEX)

    def test_output_is_close_to_current_time(self) -> None:
        """`now_timestamp()`'s value must parse back to within a few seconds of `datetime.now()`."""
        before = datetime.now().astimezone()
        value = now_timestamp()
        after = datetime.now().astimezone()

        parsed = datetime.fromisoformat(value)
        self.assertGreaterEqual(parsed, before - timedelta(seconds=5))
        self.assertLessEqual(parsed, after + timedelta(seconds=5))


class TestTSeparator(unittest.TestCase):
    """Tests for the `T`-separator switch itself (feat-146 Phase 1, REQ-004)."""

    def test_separator_is_t_not_space(self) -> None:
        """The date/time separator must be a literal `T`, not a space (feat-146, ADR 8c889262)."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000, tzinfo=timezone.utc)
        value = format_timestamp(dt)
        self.assertEqual(value[10], "T")
        self.assertNotIn(" ", value)
        self.assertEqual(value, "2026-09-01T12:30:45.123Z")

    def test_naive_datetime_uses_t_with_no_suffix(self) -> None:
        """A naive datetime must use the `T` separator too, with no `Z`/offset suffix."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123")


if __name__ == "__main__":
    unittest.main()
