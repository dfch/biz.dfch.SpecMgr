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

"""Tests for ``req.tools._write.write_req_file`` (shared create/update write helper)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.req.models.v1 import ReqFrontmatter, parse_req
from biz.dfch.specmgr.req.tools._write import write_req_file

_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)


class TestWriteReqFile(unittest.TestCase):
    """Tests for write_req_file."""

    def test_writes_frontmatter_and_body_that_round_trips(self) -> None:
        """The written file must parse back into an equivalent document."""
        frontmatter = ReqFrontmatter(
            id="some-id",
            type="req",
            status="draft",
            created="2026-08-14 10:00:00.000Z",
            updated="2026-08-14 10:00:00.000Z",
            version="1.0.0",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            write_req_file(path, frontmatter, _BODY)

            self.assertTrue(path.exists())
            document = parse_req(path.read_text(encoding="utf-8"))
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.frontmatter.status, "draft")
            self.assertEqual(document.body.text, "Maximum Engine Temperature")

    def test_file_ends_with_exactly_one_trailing_newline(self) -> None:
        """The written file must end with exactly one trailing newline."""
        frontmatter = ReqFrontmatter(id="some-id")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            write_req_file(path, frontmatter, _BODY)

            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            self.assertFalse(text.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
