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

"""Pytest conftest for the c4-skills harness tests (feat-250, Phase 100).

Two responsibilities:

1. **The import path** -- `evals/` is deliberately not part of the wheel
   (development-only, Task 100.100); this conftest puts the harness root
   (`evals/c4-skills/`) on `sys.path` so `import c4_skills` works from
   every test module here, mirroring the thin launcher
   `evals/c4-skills/run.py`. The pre-commit pytest hook is scoped to
   `src/`+`tests/` changes, so these tests run in pre-commit/CI exactly
   like every other test in this package.

2. **The Docker gate** -- the tests that exercise the real Structurizr CLI
   (the grader collection) skip when Docker is missing (ACC-006); every
   other test runs with no Docker and no model call.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

#: The repository root (this file is tests/evals/conftest.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The harness root (evals/c4-skills), home of the importable `c4_skills`
#: package.
_HARNESS_ROOT = _REPO_ROOT / "evals" / "c4-skills"

if str(_HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(_HARNESS_ROOT))

#: The fixtures directory for this test package.
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def docker_available() -> bool:
    """Return True iff the docker CLI answers `--version` (the test gate)."""
    try:
        proc = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=30)  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        return False
    result = proc.returncode == 0
    return result
