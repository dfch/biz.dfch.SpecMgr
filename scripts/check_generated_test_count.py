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

"""Fail when the test-file count in `docs/GENERATED.md` is stale (feat-274, issue #274).

`specmgr docs` writes the number of `tests/**/test_*.py` files into
`docs/GENERATED.md`. The `specmgr-docs` pre-commit hook only runs on staged
`src/**/*.py` changes, and pre-commit never passes deleted files to a hook,
so no `files:` pattern can catch a commit that only adds or deletes a test
file. The `specmgr-docs-test-count` hook therefore runs this check on every
commit: it counts the test files with the same function `specmgr docs`
uses and compares the count with the one recorded in `docs/GENERATED.md`.

Exit codes: 0 the count matches, 1 the count is stale or missing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from biz.dfch.specmgr.commands.docs import _count_test_files

#: The repository root (this script lives in `<root>/scripts/`).
_REPO_ROOT = Path(__file__).resolve().parent.parent

#: The line `specmgr docs` writes into `docs/GENERATED.md`.
_TEST_FILES_LINE = re.compile(r"^\*\*Test files\*\*: (\d+)$", re.MULTILINE)


def stale_count_message(generated_text: str, actual_count: int) -> str | None:
    """Return why the recorded test-file count is stale, or None when it matches.

    Args:
        generated_text: The content of `docs/GENERATED.md`.
        actual_count: The number of `tests/**/test_*.py` files.

    Returns:
        None when `generated_text` records `actual_count`; otherwise an
        actionable message naming both counts and the fix.
    """
    match = _TEST_FILES_LINE.search(generated_text)
    if match is None:
        return "docs/GENERATED.md has no '**Test files**: N' line -- run 'uv run --frozen specmgr docs'."
    recorded = int(match.group(1))
    if recorded == actual_count:
        return None
    result = (
        f"docs/GENERATED.md records {recorded} test file(s), but tests/ has {actual_count} -- "
        "run 'uv run --frozen specmgr docs' and 'git add docs/GENERATED.md'."
    )
    return result


def main() -> int:
    """Run the check against the repository and print the message on failure.

    Returns:
        The process exit code: 0 when the count matches, 1 otherwise.
    """
    generated_text = (_REPO_ROOT / "docs" / "GENERATED.md").read_text(encoding="utf-8")
    message = stale_count_message(generated_text, _count_test_files())
    if message is None:
        return 0
    print(message, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
