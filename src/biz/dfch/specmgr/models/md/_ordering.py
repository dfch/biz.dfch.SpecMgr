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

"""Shared, private newest-first ordering validation helper for `models.md` domain body models.

Mirrors `feat.models.v1.body.Updates._validate_newest_first`/
`DecisionsMade._validate_newest_first` (the untouched precedent this
package deliberately does not refactor -- see
`.specmgr/feat/feat-38-39-41-43-44/README.md` Design Notes for Phase 2),
factored out here so the newer `sop.Updates`/`dec.Updates`/`vcr.Updates`/
`tsk.RecentUpdates` containers share one implementation instead of four
near-identical copies of the same `model_validator`.
"""

from __future__ import annotations

from datetime import datetime

#: A date-only timestamp (`yyyy-MM-dd`) is always exactly 10 characters;
#: anything longer carries a time component. Every caller only ever passes
#: strings that already matched their own `@alias` regex (either the bare
#: date variant or the full date+time+milliseconds+offset variant), so this
#: length check is a reliable, allocation-free way to tell them apart
#: without re-deriving/duplicating that regex here.
_DATE_ONLY_LENGTH = 10


def validate_newest_first(timestamps: list[str], label: str) -> None:
    """Assert that `timestamps` are ordered newest-first (non-increasing).

    Each consecutive pair is compared with `datetime.fromisoformat` (aware
    comparison; `Z` is supported by `fromisoformat` on Python 3.11+, this
    package's floor). Mixed-granularity rule: when either side of a pair is
    a date-only value (`yyyy-MM-dd`, no time component), the comparison
    happens at day granularity (`.date()`) instead of full `datetime`
    precision -- a date-only entry and a same-day date+time entry are
    therefore treated as equal, not ordered against each other by the time
    component neither, or only one, of them carries. Equal values (same
    day, or identical timestamps) are always allowed (`>=`, not `>`),
    matching the FEAT precedent's own non-strict "newest-first" semantics.

    Args:
        timestamps: The entries' own timestamp strings, in document order
            (index 0 is the first/topmost entry).
        label: The calling container's own name (e.g. `"Updates"`,
            `"RecentUpdates"`), used only to prefix the assertion message.

    Raises:
        AssertionError: some earlier (lower-index) entry's timestamp is
            older than a later (higher-index) entry's timestamp -- i.e. the
            entries are not newest-first.
    """
    for earlier, later in zip(timestamps, timestamps[1:]):
        earlier_dt = datetime.fromisoformat(earlier)
        later_dt = datetime.fromisoformat(later)
        if len(earlier) == _DATE_ONLY_LENGTH or len(later) == _DATE_ONLY_LENGTH:
            earlier_value: datetime | object = earlier_dt.date()
            later_value: datetime | object = later_dt.date()
        else:
            earlier_value = earlier_dt
            later_value = later_dt
        assert earlier_value >= later_value, (  # type: ignore[operator]
            f"{label}: entries must be newest-first; {earlier!r} precedes {later!r}"
        )
