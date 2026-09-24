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

Covers the aware-comparison newest-first rule and the "equal values are
allowed" (non-strict `>=`) semantics -- the same matrix `sop.models.v1.body.Updates`/
`dec.models.v1.body.Updates`/`vcr.models.v1.body.Updates`/`tsk.models.v1.body.RecentUpdates`'s
own `_validate_newest_first` `model_validator`s each delegate to. Every
timestamp passed here is the full date+time form the six entry-heading
domains' `@alias` regexes enforce (date-only was rejected by feat-146
Phase 2, ADR 8c889262-152b-4b8e-ae2c-75371f7a9edf, so the helper's former
mixed date-only/date+time day-granularity rule is gone).
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

    def test_same_day_t_vs_space_pair_orders_by_time_component(self) -> None:
        # Both separators are accepted; on the same day the time component
        # decides: 16:00Z is later than 10:00Z, so newest-first.
        validate_newest_first(["2026-09-01T16:00:00.000Z", "2026-09-01 10:00:00.000Z"], "Updates")

    def test_same_day_t_vs_space_pair_out_of_order_raises(self) -> None:
        with self.assertRaises(AssertionError):
            validate_newest_first(["2026-09-01 10:00:00.000Z", "2026-09-01T16:00:00.000Z"], "Updates")

    def test_mixed_offsets_compare_correctly(self) -> None:
        # 16:00Z is later than 17:30+02:00 (== 15:30Z), so this is
        # newest-first despite the later string's larger wall-clock hour.
        validate_newest_first(["2026-09-01 16:00:00.000Z", "2026-09-01 17:30:00.000+02:00"], "Updates")

    def test_error_message_includes_label_and_offending_values(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            validate_newest_first(["2026-08-30 09:00:00.000+02:00", "2026-09-01 10:00:00.000Z"], "RecentUpdates")

        message = str(ctx.exception)
        self.assertIn("RecentUpdates", message)
        self.assertIn("2026-08-30 09:00:00.000+02:00", message)
        self.assertIn("2026-09-01 10:00:00.000Z", message)


if __name__ == "__main__":
    unittest.main()
