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

"""Shared test fixtures for the per-tool ``tools.adr.*`` test modules.

Not itself a ``test_*.py`` module -- imported by the individual per-tool
test files under this directory so the temp-dir/env-var fixture and the
``AdrBody`` builder are not duplicated across them.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, render_adr
from biz.dfch.specmgr.tools.adr._paths import ADR_DIR_ENV_VAR


def body(**overrides: object) -> AdrBody:
    """Build a minimal, valid ``AdrBody``, overriding any field by keyword."""
    fields = {
        "title": "A title",
        "context_and_problem_statement": "Context.",
        "considered_options": "Options.",
        "decision_outcome": "Outcome.",
    }
    fields.update(overrides)
    return AdrBody(**fields)


class TempAdrDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the ADR base dir via SPECMGR_ADR_DIR."""

    def setUp(self):
        self.base_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(self.base_dir)}))

    def _write(self, filename: str, adr: Adr) -> Path:
        path = self.base_dir / filename
        path.write_text(render_adr(adr), encoding="utf-8")
        return path

    def existing_adr(self, id_: str = "existing-id", **body_overrides: object) -> Adr:
        """Write a valid ADR (id ``id_``) to the temp base dir and return it."""
        adr = Adr(frontmatter=AdrFrontmatter(id=id_), body=body(**body_overrides))
        self._write(f"{id_}.md", adr)
        return adr
