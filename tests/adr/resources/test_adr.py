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

"""Tests for the specmgr://adr/{id} resource.

The former ``specmgr://adr/list`` resource test coverage (``TestAdrListResource``)
was migrated to ``tests/adr/tools/test_list_adr.py`` when ``adr_list`` was
converted into the ``list_adr`` tool (feat-13-list-paging Task 2.1).
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, render_adr
from biz.dfch.specmgr.adr.resources.adr_get import adr_get
from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError


def _body(title: str) -> AdrBody:
    return AdrBody(
        title=title,
        context_and_problem_statement="Context.",
        considered_options="Options.",
        decision_outcome="Outcome.",
    )


class TestAdrGetResource(unittest.TestCase):
    """Tests for the `adr_get` resource function (`specmgr://adr/{id}`)."""

    def test_returns_full_adr_for_known_id(self):
        """adr_get must return the full Adr for a matching id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            adr = Adr(frontmatter=AdrFrontmatter(id="id-1", status="accepted"), body=_body("First title"))
            (base / "1.md").write_text(render_adr(adr), encoding="utf-8")

            with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(base)}):
                result = adr_get("id-1")

            self.assertIsInstance(result, Adr)
            self.assertEqual(result.frontmatter.id, "id-1")
            self.assertEqual(result.body.title, "First title")

    def test_raises_not_found_for_unknown_id(self):
        """adr_get must raise AdrNotFoundError when no ADR matches the given id."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            adr = Adr(frontmatter=AdrFrontmatter(id="id-1", status="accepted"), body=_body("First title"))
            (base / "1.md").write_text(render_adr(adr), encoding="utf-8")

            with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(base)}):
                with self.assertRaises(AdrNotFoundError):
                    adr_get("no-such-id")


if __name__ == "__main__":
    unittest.main()
