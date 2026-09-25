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

"""Tests for `models.md._timestamps` (feat-146 Phase 1, Tasks 1.1/1.3).

Covers the shared `T`-canonical formatting core (`format_timestamp` -- the
write side's single formatting implementation, which
`general.tools._timestamps.format_timestamp` delegates to) and the frontmatter
read path's PyYAML-coercion normalization (`normalize_yaml_datetime` -- the
feat-146 REQ-006 fix for unquoted `created`/`updated` values: canonical
values converge to the `T` form, six-digit-fraction and date-only values stay
rejected instead of being silently truncated into an accepted shape).
"""

from __future__ import annotations

import re
import unittest
from datetime import datetime, timedelta, timezone

import yaml

from biz.dfch.specmgr.models.md._timestamps import format_timestamp, normalize_yaml_datetime

#: The date+time variant accepted for frontmatter `created`/`updated`
#: (feat-146): `T` or space separator, exactly three millisecond digits,
#: `Z` or a signed `±HH:mm` offset.
_DATE_TIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})$")


class TestFormatTimestampT(unittest.TestCase):
    """Tests for `format_timestamp()` (the shared `T`-canonical core)."""

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
        """Six-digit microseconds must be truncated (not rounded) to exactly three digits."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 999, tzinfo=timezone.utc)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.000Z")

    def test_milliseconds_are_always_exactly_three_digits(self) -> None:
        """A small microsecond value must still zero-pad to three millisecond digits."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 5000, tzinfo=timezone.utc)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.005Z")

    def test_naive_datetime_has_no_suffix(self) -> None:
        """A naive datetime (no tzinfo) must format with no `Z`/offset suffix at all."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000)
        self.assertEqual(format_timestamp(dt), "2026-09-01T12:30:45.123")

    def test_separator_is_t(self) -> None:
        """The date/time separator must be a literal `T` (feat-146, ADR 8c889262)."""
        dt = datetime(2026, 9, 1, 12, 30, 45, 123000, tzinfo=timezone.utc)
        value = format_timestamp(dt)
        self.assertEqual(value[10], "T")
        self.assertNotIn(" ", value)


class TestNormalizeYamlDatetime(unittest.TestCase):
    """Tests for `normalize_yaml_datetime()` (feat-146 REQ-006, the unquoted-value fix)."""

    def _coerce(self, raw: str) -> object:
        """Run `raw` through the same PyYAML standard loader `python-frontmatter` uses."""
        return yaml.safe_load(f"created: {raw}")["created"]

    def test_unquoted_t_canonical_converges_to_t_form(self) -> None:
        """An unquoted `T`-separated canonical timestamp must parse back as its own `T` text."""
        value = self._coerce("2026-09-23T12:00:00.123+02:00")
        assert isinstance(value, datetime)
        self.assertEqual(normalize_yaml_datetime(value), "2026-09-23T12:00:00.123+02:00")

    def test_unquoted_space_canonical_converges_to_t_form(self) -> None:
        """An unquoted space-separated canonical timestamp must converge to the `T` form."""
        value = self._coerce("2026-09-23 12:00:00.123+02:00")
        assert isinstance(value, datetime)
        self.assertEqual(normalize_yaml_datetime(value), "2026-09-23T12:00:00.123+02:00")

    def test_unquoted_space_z_renders_z_not_plus_00_00(self) -> None:
        """An unquoted zero-offset timestamp must normalize to `Z`, not `+00:00` (bare `str()`'s bug)."""
        value = self._coerce("2026-09-23 12:00:00.123Z")
        assert isinstance(value, datetime)
        self.assertEqual(normalize_yaml_datetime(value), "2026-09-23T12:00:00.123Z")

    def test_unquoted_second_precision_converges_to_t_form_with_zero_milliseconds(self) -> None:
        """An unquoted second-precision timestamp (no fraction digits) must normalize to `.000`."""
        value = self._coerce("2026-09-23T12:00:00+02:00")
        assert isinstance(value, datetime)
        self.assertEqual(normalize_yaml_datetime(value), "2026-09-23T12:00:00.000+02:00")

    def test_unquoted_six_digit_fraction_stays_rejected(self) -> None:
        """An unquoted six-digit-fraction timestamp must NOT be truncated into an accepted shape.

        The guard returns the bare `str()` text (space separator, six fraction
        digits) so the frontmatter's own date+time pattern rejects it with an
        actionable error instead of silently accepting a lossy truncation
        (feat-146 REQ-003/ACC-002: six-digit fractions remain rejected).
        """
        value = self._coerce("2026-09-23T12:00:00.123456+02:00")
        assert isinstance(value, datetime)
        result = normalize_yaml_datetime(value)
        self.assertFalse(_DATE_TIME_PATTERN.fullmatch(result))
        self.assertEqual(result, str(value))

    def test_unquoted_naive_value_stays_rejected(self) -> None:
        """An unquoted timezone-less timestamp must normalize to `T` form with no suffix, where
        the frontmatter pattern still rejects it (timezone-less values remain rejected)."""
        value = self._coerce("2026-09-23T12:00:00.123")
        assert isinstance(value, datetime)
        result = normalize_yaml_datetime(value)
        self.assertEqual(result, "2026-09-23T12:00:00.123")
        self.assertFalse(_DATE_TIME_PATTERN.fullmatch(result))

    def test_normalized_canonical_values_match_the_frontmatter_pattern(self) -> None:
        """Every information-preserving unquoted canonical value must normalize to pattern-conformant text."""
        for raw in (
            "2026-09-23T12:00:00.123Z",
            "2026-09-23 12:00:00.123Z",
            "2026-09-23T12:00:00.123+02:00",
            "2026-09-23 12:00:00.123+02:00",
            "2026-09-23T12:00:00.123-05:00",
            "2026-09-23T12:00:00+02:00",
        ):
            value = self._coerce(raw)
            with self.subTest(raw=raw):
                assert isinstance(value, datetime)
                self.assertRegex(normalize_yaml_datetime(value), _DATE_TIME_PATTERN)


if __name__ == "__main__":
    unittest.main()
