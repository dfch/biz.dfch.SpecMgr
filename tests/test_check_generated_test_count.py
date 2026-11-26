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

"""`scripts/check_generated_test_count.py` tests (feat-274, issue #274)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "check_generated_test_count.py"


def _load_script():  # noqa: ANN202 -- a dynamically loaded module
    """Import the script as a module (it lives outside any package)."""
    spec = importlib.util.spec_from_file_location("check_generated_test_count", _SCRIPT)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class TestStaleCountMessage(unittest.TestCase):
    """`stale_count_message` compares the recorded and the actual count."""

    def setUp(self) -> None:
        self.sut = _load_script()

    def test_matching_count_returns_none(self) -> None:
        result = self.sut.stale_count_message("## Test Coverage\n\n**Test files**: 42\n", 42)

        self.assertIsNone(result)

    def test_stale_count_names_both_counts_and_the_fix(self) -> None:
        result = self.sut.stale_count_message("**Test files**: 41\n", 42)

        self.assertIsNotNone(result)
        self.assertIn("records 41 test file(s), but tests/ has 42", result)
        self.assertIn("specmgr docs", result)

    def test_missing_line_is_reported(self) -> None:
        result = self.sut.stale_count_message("# Generated\n", 42)

        self.assertIsNotNone(result)
        self.assertIn("no '**Test files**: N' line", result)


class TestScriptOnRepository(unittest.TestCase):
    """The committed `docs/GENERATED.md` records the current test-file count."""

    def test_script_exits_zero_on_the_repository(self) -> None:
        proc = subprocess.run(  # noqa: S603 -- fixed interpreter and script path
            [sys.executable, str(_SCRIPT)], capture_output=True, text=True, timeout=120, check=False
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
