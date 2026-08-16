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

"""Tests for ``uc.tools._write.write_uc_file`` (shared create/update write helper)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.uc.models.v2 import UcFrontmatter, parse_uc
from biz.dfch.specmgr.uc.tools._write import write_uc_file

_BODY = textwrap.dedent(
    """\
    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)


class TestWriteUcFile(unittest.TestCase):
    """Tests for write_uc_file."""

    def test_writes_frontmatter_and_body_that_round_trips(self) -> None:
        """The written file must parse back into an equivalent document."""
        frontmatter = UcFrontmatter(
            id="some-id",
            type="uc",
            status="draft",
            created="2026-08-14T10:00:00",
            updated="2026-08-14T10:00:00",
            version="1.0.0",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            write_uc_file(path, frontmatter, _BODY)

            self.assertTrue(path.exists())
            document = parse_uc(path.read_text(encoding="utf-8"))
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.frontmatter.status, "draft")
            self.assertEqual(document.body.text, "Buy Goods")

    def test_file_ends_with_exactly_one_trailing_newline(self) -> None:
        """The written file must end with exactly one trailing newline."""
        frontmatter = UcFrontmatter(id="some-id")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            write_uc_file(path, frontmatter, _BODY)

            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            self.assertFalse(text.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
