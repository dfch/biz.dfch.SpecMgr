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

"""Regression guard: no directory under ``src/biz/dfch/specmgr/`` is an implicit namespace package.

``specmgr docs`` walks the package tree with ``pkgutil.walk_packages``, which
does not descend into a directory without an ``__init__.py``; every module
below such a directory silently gets no ``docs/api/`` page (GitHub issue #249).
The check covers every ancestor directory of each git-tracked ``.py`` file, up
to and including ``src/biz/dfch/specmgr/`` -- not only the file's own parent,
because a directory such as ``req/models/`` may hold no ``.py`` file of its own,
only a sub-package. The implicit namespace roots ``src/biz/`` and
``src/biz/dfch/`` are outside the scope.

Files are enumerated with ``git ls-files`` rather than a filesystem walk, so
untracked ``__pycache__``-only leftovers in a local checkout cannot make the
test flaky.
"""

import shutil
import subprocess
import unittest
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PurePosixPath("src/biz/dfch/specmgr")


def _tracked_python_files() -> list[PurePosixPath]:
    """Return every git-tracked ``.py`` file under ``PACKAGE_ROOT``, repo-relative."""
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", f"{PACKAGE_ROOT}/*.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    result = [PurePosixPath(entry) for entry in completed.stdout.split("\0") if entry]
    return result


def _directories_missing_init(files: list[PurePosixPath], tracked: set[PurePosixPath]) -> list[str]:
    """Return the sorted package directories (ancestors of ``files``) whose ``__init__.py`` is not in ``tracked``."""
    missing: set[str] = set()
    for file in files:
        directory = file.parent
        while True:
            if directory / "__init__.py" not in tracked:
                missing.add(str(directory))
            if directory == PACKAGE_ROOT:
                break
            directory = directory.parent
    result = sorted(missing)
    return result


class TestNoNamespacePackages(unittest.TestCase):
    """Every package directory under ``src/biz/dfch/specmgr/`` is a regular package."""

    def setUp(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git is not available")
        probe = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], cwd=REPO_ROOT, capture_output=True, text=True, check=False
        )
        if probe.returncode != 0:
            self.skipTest("not running inside a git work tree")

    def test_every_ancestor_directory_has_init(self) -> None:
        """Each directory from a tracked ``.py`` file's parent up to the package root has an ``__init__.py``."""
        files = _tracked_python_files()
        self.assertTrue(files, f"git ls-files found no .py file under {PACKAGE_ROOT}")
        # A tracked ``__init__.py`` deleted from the working tree counts as missing too.
        tracked = {file for file in files if (REPO_ROOT / file).is_file()}

        missing = _directories_missing_init(files, tracked)

        self.assertEqual(
            [],
            missing,
            "directories without __init__.py (implicit namespace packages, skipped by `specmgr docs`): "
            + ", ".join(missing),
        )

    def test_check_covers_ancestors_not_only_parent(self) -> None:
        """A directory holding only a sub-package is reported, not only a file's direct parent."""
        files = [PACKAGE_ROOT / "__init__.py", PACKAGE_ROOT / "d" / "models" / "v1" / "__init__.py"]
        tracked = set(files) | {PACKAGE_ROOT / "d" / "__init__.py"}

        missing = _directories_missing_init(files, tracked)

        self.assertEqual([f"{PACKAGE_ROOT}/d/models"], missing)


if __name__ == "__main__":
    unittest.main()
