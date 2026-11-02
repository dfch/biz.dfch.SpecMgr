#!/usr/bin/env python3
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

"""Thin launcher for the c4-skills measurement harness.

`evals/` is development-only and deliberately not part of the wheel (the
folder name `c4-skills` is not a legal Python identifier, so the importable
package lives one level down as `c4_skills/`). This launcher puts the
harness root on `sys.path` and dispatches to `c4_skills.cli.main` -- it is
the run entry point recorded for Task 100.100:

    python3 evals/c4-skills/run.py run --cases smoke-create-system --conditions none,upstream --k 2 --label smoke
    python3 evals/c4-skills/run.py preflight
    python3 evals/c4-skills/run.py probe
    python3 evals/c4-skills/run.py report --results-dir evals/c4-skills/results/<run-id>

The same module is importable by the unit tests under `tests/evals/`
(whose `conftest.py` performs the identical `sys.path` insertion).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from c4_skills.cli import main  # noqa: E402 -- path setup must run first

if __name__ == "__main__":
    sys.exit(main())
