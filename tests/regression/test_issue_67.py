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

"""feat-67-70-71 Phase 2 (REQ-002/ACC-001): repo-wide regression test asserting every domain's
`*/data/*_template.md`/`*/data/*_example.md` file no longer carries a round, all-zero
placeholder time-of-day such as `00:00:00.000Z`.

GitHub issue #67 (and its literal duplicate, #71) reported that every domain's placeholder
`created`/`updated` frontmatter timestamps, and `feat`'s body-level `#### {timestamp} - {title}`
headings, used a suspiciously round `00:00:00.000` time-of-day -- round enough to invite an
agent or human to copy it verbatim into a real document instead of substituting the actual
current timestamp. Phase 1's Task 1.5 audit (see this feature's README, Design Notes) found the
defect in all 24 affected files (ADR has none, since it has no `*/data/*_template.md`/
`*/data/*_example.md` files), with severity ranging from full midnight (`00:00:00.000`, the
literal ACC-001 pattern) down to a "round milliseconds only" borderline tier at a real,
non-round hour/minute/second (e.g. `08:15:42.000Z`). Phase 2 fixed every tier in all 24 files
(this feature's own Decisions Made log records that scope decision), so this test asserts on
both the literal ACC-001 pattern and the broader round-milliseconds class, to lock in the wider
fix and catch any future regression of the same defect class -- not just its narrowest reported
symptom.

Deliberately excluded from both checks: a date-only `### yyyy-MM-dd - {title}` heading (no
time-of-day component at all). Task 1.5 confirmed these are a deliberately supported alternate
granularity (several domains' own `_UPDATE_ENTRY_HEADING_PATTERN` makes the time-of-day
component optional), not a placeholder defect -- this test's patterns only ever match a
timestamp that *has* an explicit `HH:mm:ss.fff` time-of-day component, so date-only headings
never trip either check.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

#: The literal ACC-001 pattern: a fully round, all-zero time-of-day.
_FULL_MIDNIGHT_PATTERN = re.compile(r"\d{2}:\d{2}:\d{2}\.000[Z+-]")

#: The broader class Phase 2 also fixed: round (all-zero) milliseconds at *any* hour/minute/
#: second, not just full midnight -- e.g. `08:15:42.000Z`. Every full-midnight match is also a
#: round-milliseconds match, so `_FULL_MIDNIGHT_PATTERN` is a strict subset of this one.
_ROUND_MILLISECONDS_PATTERN = re.compile(r"\.000[Z+-]")

#: Repo root, resolved from this test file's own location (`tests/regression/test_issue_67.py`).
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: Every domain's `data/` directory lives directly under its own package, i.e.
#: `src/biz/dfch/specmgr/<domain>/data/`.
_SPECMGR_PACKAGE_DIR = _REPO_ROOT / "src" / "biz" / "dfch" / "specmgr"


def _iter_template_and_example_files() -> list[Path]:
    """Collect every domain's `*_template.md`/`*_example.md` file under `<domain>/data/`.

    Returns:
        A sorted list of matching file paths, across every domain package.
    """
    result: list[Path] = []
    for domain_dir in sorted(_SPECMGR_PACKAGE_DIR.iterdir()):
        data_dir = domain_dir / "data"
        if not data_dir.is_dir():
            continue
        result.extend(sorted(data_dir.glob("*_template.md")))
        result.extend(sorted(data_dir.glob("*_example.md")))
    return result


class TestIssue67NoRoundPlaceholderTimestamps(unittest.TestCase):
    """ACC-001: no `*/data/*_template.md`/`*/data/*_example.md` file has a round timestamp."""

    def setUp(self) -> None:
        self.files = _iter_template_and_example_files()

    def test_at_least_one_domain_file_is_found(self) -> None:
        # A guard against this test silently passing because the glob matched nothing (e.g. a
        # future refactor moves `data/` elsewhere).
        MIN_EXPECTED_FILE_COUNT = 20
        self.assertGreaterEqual(len(self.files), MIN_EXPECTED_FILE_COUNT, self.files)

    def test_no_file_contains_the_literal_full_midnight_pattern(self) -> None:
        offenders: list[str] = []
        for path in self.files:
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if _FULL_MIDNIGHT_PATTERN.search(line):
                    offenders.append(f"{path.relative_to(_REPO_ROOT)}:{lineno}: {line.strip()}")

        self.assertEqual([], offenders, "\n".join(offenders))

    def test_no_file_contains_a_round_milliseconds_timestamp(self) -> None:
        offenders: list[str] = []
        for path in self.files:
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if _ROUND_MILLISECONDS_PATTERN.search(line):
                    offenders.append(f"{path.relative_to(_REPO_ROOT)}:{lineno}: {line.strip()}")

        self.assertEqual([], offenders, "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
