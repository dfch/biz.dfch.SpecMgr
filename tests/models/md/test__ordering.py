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

"""Tests for `models.md._ordering.validate_newest_first` (feat-38-39-41-43-44 Phase 2, Task 2.1).

Covers the aware-comparison newest-first rule, the mixed date-only/date+time
day-granularity rule, and the "equal values are allowed" (non-strict `>=`)
semantics -- the same matrix `sop.models.v1.body.Updates`/`dec.models.v1.body.Updates`/
`vcr.models.v1.body.Updates`/`tsk.models.v1.body.RecentUpdates`'s own
`_validate_newest_first` `model_validator`s each delegate to.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.models.md._ordering import validate_newest_first


class TestValidateNewestFirst(unittest.TestCase):
    """Tests for `validate_newest_first()`."""

    def test_empty_list_passes(self) -> None:
        validate_newest_first([], "Updates")

    def test_single_entry_passes(self) -> None:
        validate_newest_first(["2026-09-01 10:00:00.000Z"], "Updates")

    def test_descending_date_time_entries_pass(self) -> None:
        validate_newest_first(
            ["2026-09-01 16:00:00.000Z", "2026-09-01 10:00:00.000Z", "2026-08-30 09:00:00.000+02:00"],
            "Updates",
        )

    def test_ascending_date_time_entries_raise(self) -> None:
        with self.assertRaises(AssertionError):
            validate_newest_first(["2026-08-30 09:00:00.000+02:00", "2026-09-01 10:00:00.000Z"], "Updates")

    def test_equal_date_time_entries_pass(self) -> None:
        validate_newest_first(["2026-09-01 10:00:00.000Z", "2026-09-01 10:00:00.000Z"], "Updates")

    def test_descending_date_only_entries_pass(self) -> None:
        validate_newest_first(["2026-09-01", "2026-08-30"], "Updates")

    def test_ascending_date_only_entries_raise(self) -> None:
        with self.assertRaises(AssertionError):
            validate_newest_first(["2026-08-30", "2026-09-01"], "Updates")

    def test_equal_date_only_entries_pass(self) -> None:
        validate_newest_first(["2026-09-01", "2026-09-01"], "Updates")

    def test_date_only_then_same_day_date_time_pass(self) -> None:
        # Mixed-granularity rule: a date-only entry followed by a
        # date+time entry on the *same* calendar day is treated as equal
        # (day granularity), not ordered by the time-of-day component
        # neither side fully carries.
        validate_newest_first(["2026-09-01", "2026-09-01 23:59:59.999Z"], "Updates")

    def test_date_time_then_same_day_date_only_pass(self) -> None:
        validate_newest_first(["2026-09-01 00:00:00.000Z", "2026-09-01"], "Updates")

    def test_date_only_then_earlier_day_date_time_pass(self) -> None:
        validate_newest_first(["2026-09-01", "2026-08-30 23:59:59.999Z"], "Updates")

    def test_date_only_then_later_day_date_time_raises(self) -> None:
        with self.assertRaises(AssertionError):
            validate_newest_first(["2026-09-01", "2026-09-02 00:00:00.000Z"], "Updates")

    def test_mixed_offsets_compare_correctly(self) -> None:
        # 16:00Z is later than 17:30+02:00 (== 15:30Z), so this is
        # newest-first despite the later string's larger wall-clock hour.
        validate_newest_first(["2026-09-01 16:00:00.000Z", "2026-09-01 17:30:00.000+02:00"], "Updates")

    def test_error_message_includes_label_and_offending_values(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            validate_newest_first(["2026-08-30", "2026-09-01"], "RecentUpdates")

        message = str(ctx.exception)
        self.assertIn("RecentUpdates", message)
        self.assertIn("2026-08-30", message)
        self.assertIn("2026-09-01", message)


if __name__ == "__main__":
    unittest.main()
