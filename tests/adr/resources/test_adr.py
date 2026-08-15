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

"""Tests for the specmgr://adr/list and specmgr://adr/{id} resources."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, AdrSummary, render_adr
from biz.dfch.specmgr.adr.resources.adr_get import adr_get
from biz.dfch.specmgr.adr.resources.adr_list import adr_list
from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError


def _body(title: str) -> AdrBody:
    return AdrBody(
        title=title,
        context_and_problem_statement="Context.",
        considered_options="Options.",
        decision_outcome="Outcome.",
    )


class TestAdrListResource(unittest.TestCase):
    """Tests for the `adr_list` resource function (`specmgr://adr/list`)."""

    def test_returns_summaries_and_skips_malformed_file(self):
        """adr_list must return exactly the valid ADRs, silently skipping a broken file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)

            first = Adr(frontmatter=AdrFrontmatter(id="id-1", status="accepted"), body=_body("First title"))
            (base / "1.md").write_text(render_adr(first), encoding="utf-8")

            second = Adr(frontmatter=AdrFrontmatter(id="id-2", status="proposed"), body=_body("Second title"))
            (base / "2.md").write_text(render_adr(second), encoding="utf-8")

            (base / "3-broken.md").write_text("not a valid ADR, no headings at all", encoding="utf-8")

            with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(base)}):
                result = adr_list()

            self.assertEqual(len(result), 2)
            for summary in result:
                self.assertIsInstance(summary, AdrSummary)
            titles = {summary.title for summary in result}
            self.assertEqual(titles, {"First title", "Second title"})
            refs = {summary.ref for summary in result}
            self.assertEqual(refs, {"1", "2"})
            for ref in refs:
                self.assertNotIn(".md", ref)

    def test_empty_list_for_missing_directory(self):
        """adr_list must return an empty list when the base directory does not exist."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist"
            with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(missing)}):
                self.assertEqual(adr_list(), [])


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
