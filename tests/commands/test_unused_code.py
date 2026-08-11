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

"""Tests for the ``unused-code`` command (default mode and ``--test``/``-t`` mode).

Builds tiny throwaway ``src``/``tests``/whitelist fixture trees per test (never the real repo
tree) so the interesting cases -- a symbol used only from tests, a symbol used from production
code, an unreferenced symbol, and a whitelisted symbol -- are all deliberately present and
unambiguous.
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import typer
from vulture import Vulture

from biz.dfch.specmgr.commands.unused_code import _scan, _unused_names, unused_code


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestScanHelpers(unittest.TestCase):
    """Tests for the `_scan()`/`_unused_names()` scanning helpers in isolation."""

    def test_scan_reports_unreferenced_top_level_function(self):
        """A function with no caller anywhere in the scanned paths must be reported."""
        with tempfile.TemporaryDirectory() as tmp:
            module = Path(tmp) / "module_a.py"
            _write(module, "def totally_unused() -> None:\n    return None\n")

            items = _scan(Vulture, [module], min_confidence=60)

            self.assertIn("totally_unused", {item.name for item in items})

    def test_unused_names_does_not_report_a_function_called_within_the_same_scan(self):
        """A function called from another file in the same scan must not be reported."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _write(base / "module_a.py", "def prod_used() -> None:\n    return None\n")
            _write(base / "module_b.py", "from module_a import prod_used\n\nprod_used()\n")

            result = _unused_names(Vulture, [base], min_confidence=60)

            self.assertNotIn("prod_used", result)


class TestUnusedCodeCommandDefaultMode(unittest.TestCase):
    """Tests for `unused_code()`'s default (plain unused-code) mode."""

    def test_reports_an_unreferenced_symbol(self):
        """An unreferenced top-level function in --src must be reported."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            tests_dir = Path(tmp) / "tests"
            _write(src_dir / "module_a.py", "def totally_unused() -> None:\n    return None\n")
            _write(tests_dir / "test_module_a.py", "assert True\n")
            missing_whitelist = Path(tmp) / "no_such_whitelist.py"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                unused_code(src=src_dir, tests=tests_dir, whitelist=missing_whitelist, test_only=False)

            self.assertIn("totally_unused", stdout.getvalue())

    def test_whitelist_suppresses_a_finding_when_it_exists(self):
        """A symbol name present in an existing --whitelist file must not be reported."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            tests_dir = Path(tmp) / "tests"
            _write(src_dir / "module_a.py", "def totally_unused() -> None:\n    return None\n")
            _write(tests_dir / "test_module_a.py", "assert True\n")
            whitelist = Path(tmp) / "whitelist.py"
            _write(whitelist, "totally_unused\n")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                unused_code(src=src_dir, tests=tests_dir, whitelist=whitelist, test_only=False)

            self.assertNotIn("totally_unused", stdout.getvalue())
            self.assertIn("No unused code found", stdout.getvalue())

    def test_reports_clean_message_when_nothing_is_unused(self):
        """A tree with no unreferenced symbol must print a clean-result message."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            tests_dir = Path(tmp) / "tests"
            _write(src_dir / "module_a.py", "def prod_used() -> None:\n    return None\n")
            _write(src_dir / "module_b.py", "from module_a import prod_used\n\nprod_used()\n")
            _write(tests_dir / "test_module_a.py", "assert True\n")
            missing_whitelist = Path(tmp) / "no_such_whitelist.py"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                unused_code(src=src_dir, tests=tests_dir, whitelist=missing_whitelist, test_only=False)

            self.assertIn("No unused code found", stdout.getvalue())

    def test_strict_raises_exit_1_when_findings_exist(self):
        """`--strict` must raise `typer.Exit(1)` when unused code is found."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            tests_dir = Path(tmp) / "tests"
            _write(src_dir / "module_a.py", "def totally_unused() -> None:\n    return None\n")
            _write(tests_dir / "test_module_a.py", "assert True\n")
            missing_whitelist = Path(tmp) / "no_such_whitelist.py"

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit) as ctx:
                    unused_code(src=src_dir, tests=tests_dir, whitelist=missing_whitelist, test_only=False, strict=True)

            self.assertEqual(ctx.exception.exit_code, 1)


class TestUnusedCodeCommandTestOnlyMode(unittest.TestCase):
    """Tests for `unused_code()`'s `--test`/`-t` (test-only-usage) mode."""

    def _build_fixture(self, tmp: str) -> tuple[Path, Path]:
        """Build a `src/`/`tests/` pair with one test-only, one production-used, one unreferenced symbol."""
        src_dir = Path(tmp) / "src"
        tests_dir = Path(tmp) / "tests"

        _write(
            src_dir / "module_a.py",
            "\n".join(
                [
                    "def prod_used() -> None:",
                    "    return None",
                    "",
                    "",
                    "def test_only_symbol() -> None:",
                    "    return None",
                    "",
                    "",
                    "def totally_unused() -> None:",
                    "    return None",
                    "",
                ]
            ),
        )
        _write(src_dir / "module_b.py", "from module_a import prod_used\n\nprod_used()\n")
        _write(
            tests_dir / "test_module_a.py",
            "from module_a import test_only_symbol\n\ntest_only_symbol()\n",
        )
        return src_dir, tests_dir

    def test_reports_only_the_symbol_exclusive_to_tests(self):
        """Must list the test-only symbol, and neither the production-used nor the unreferenced one."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir, tests_dir = self._build_fixture(tmp)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                unused_code(src=src_dir, tests=tests_dir, min_confidence=60, test_only=True, strict=False)

            output = stdout.getvalue()
            self.assertIn("test_only_symbol", output)
            self.assertNotIn("prod_used", output)
            self.assertNotIn("totally_unused", output)

    def test_strict_raises_exit_1_when_findings_exist(self):
        """`--strict` must raise `typer.Exit(1)` when any test-only symbol is found."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir, tests_dir = self._build_fixture(tmp)

            with redirect_stdout(io.StringIO()):
                with self.assertRaises(typer.Exit) as ctx:
                    unused_code(src=src_dir, tests=tests_dir, min_confidence=60, test_only=True, strict=True)

            self.assertEqual(ctx.exception.exit_code, 1)

    def test_no_strict_does_not_raise_when_findings_exist(self):
        """Without `--strict`, findings must be reported but must not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir, tests_dir = self._build_fixture(tmp)

            with redirect_stdout(io.StringIO()):
                result = unused_code(src=src_dir, tests=tests_dir, min_confidence=60, test_only=True, strict=False)

            self.assertIsNone(result)

    def test_reports_nothing_when_no_symbol_is_test_only(self):
        """A tree with no test-only symbol must print a clean-result message and not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            tests_dir = Path(tmp) / "tests"
            _write(src_dir / "module_a.py", "def prod_used() -> None:\n    return None\n")
            _write(src_dir / "module_b.py", "from module_a import prod_used\n\nprod_used()\n")
            _write(tests_dir / "test_module_a.py", "assert True\n")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                unused_code(src=src_dir, tests=tests_dir, min_confidence=60, test_only=True, strict=True)

            self.assertIn("No symbols", stdout.getvalue())


class TestUnusedCodeCommandMissingExtra(unittest.TestCase):
    """Tests for `unused_code()`'s behaviour when the `test` extra isn't installed."""

    def test_missing_vulture_extra_exits_1_with_a_helpful_message(self):
        """If `vulture` cannot be imported, the command must exit 1 with an install hint."""
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            tests_dir = Path(tmp) / "tests"
            _write(src_dir / "module_a.py", "def prod_used() -> None:\n    return None\n")
            _write(tests_dir / "test_module_a.py", "assert True\n")

            with mock.patch.dict(sys.modules, {"vulture": None}):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    with self.assertRaises(typer.Exit) as ctx:
                        unused_code(src=src_dir, tests=tests_dir)

            self.assertEqual(ctx.exception.exit_code, 1)
            self.assertIn("test", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
