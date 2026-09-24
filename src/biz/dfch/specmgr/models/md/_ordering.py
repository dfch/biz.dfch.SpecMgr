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

Every caller only ever passes full date+time timestamps (the shared
`yyyy-MM-dd` + (`T` or space) + `HH:mm:ss.fff` + `Z`/`±HH:MM` fragment all
six entry-heading domains' own `@alias` regexes enforce; date-only values
are rejected at parse time -- ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf), so the comparison below is a plain
aware `datetime.fromisoformat` pair comparison, with no mixed-granularity
(day-granularity for date-only pairs) rule.
"""

from __future__ import annotations

from datetime import datetime


def validate_newest_first(timestamps: list[str], label: str) -> None:
    """Assert that `timestamps` are ordered newest-first (non-increasing).

    Each consecutive pair is compared with `datetime.fromisoformat` (aware
    comparison; `Z` and the space separator are both supported by
    `fromisoformat` on Python 3.11+, this package's floor). Equal
    timestamps are always allowed (`>=`, not `>`), matching the FEAT
    precedent's own non-strict "newest-first" semantics.

    Args:
        timestamps: The entries' own full date+time timestamp strings, in
            document order (index 0 is the first/topmost entry).
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
        assert earlier_dt >= later_dt, f"{label}: entries must be newest-first; {earlier!r} precedes {later!r}"
