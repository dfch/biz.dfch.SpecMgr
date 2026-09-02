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

"""Tests for the ``create_adr`` ``@mcp.tool()`` wrapper (plan §8, §9a)."""

import unittest
from unittest import mock

from biz.dfch.specmgr.models.adr import Adr, AdrFrontmatter
from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.adr.tools.create_adr import create_adr
from biz.dfch.specmgr.adr.tools.get_adr import get_adr

from ._helpers import TempAdrDirTestCase, body


class TestCreateAdr(TempAdrDirTestCase):
    """Tests for the create_adr tool."""

    def test_assigns_id_and_writes_expected_filename(self):
        """create_adr must assign a fresh id and write f'{id}-{slug}.md' under the base dir."""
        frontmatter = AdrFrontmatter(status="proposed")
        new_body = body(title="My New Decision")
        result = create_adr(frontmatter, new_body)

        self.assertIsNotNone(result.frontmatter.id)
        expected_path = self.base_dir / f"{result.frontmatter.id}-my-new-decision.md"
        self.assertTrue(expected_path.exists())

        on_disk = get_adr(result.frontmatter.id)
        self.assertEqual(on_disk.body.title, "My New Decision")
        self.assertEqual(on_disk.frontmatter.status, "proposed")

    def test_ignores_caller_submitted_id(self):
        """Any id submitted in the frontmatter argument must be overwritten by a fresh one."""
        frontmatter = AdrFrontmatter(id="caller-supplied-id")
        result = create_adr(frontmatter, body())
        self.assertNotEqual(result.frontmatter.id, "caller-supplied-id")

    def test_response_is_full_document_with_body_intact(self):
        """feat-69 regression: create_adr is explicitly out of scope -- it must keep returning the
        full `Adr` document (frontmatter and body both intact), unlike the 11 whole-body domains'
        own `create_<d>` tools, which now return frontmatter only."""
        new_body = body(title="A Document With A Body")
        result = create_adr(AdrFrontmatter(status="proposed"), new_body)

        self.assertIsInstance(result, Adr)
        self.assertEqual(result.body, new_body)
        self.assertEqual(result.body.title, "A Document With A Body")
        self.assertEqual(result.frontmatter.status, "proposed")

    def test_creates_base_dir_if_missing(self):
        """create_adr must create the ADR base directory if it does not exist yet."""
        nested = self.base_dir / "nested" / "adr-dir"
        with mock.patch.dict("os.environ", {ADR_DIR_ENV_VAR: str(nested)}):
            result = create_adr(AdrFrontmatter(), body(title="Nested"))
        self.assertTrue(nested.is_dir())
        self.assertTrue((nested / f"{result.frontmatter.id}-nested.md").exists())


if __name__ == "__main__":
    unittest.main()
