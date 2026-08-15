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

"""Tests for the ``req_list`` resource (``specmgr://req/list``, Task 3.18)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.req.models.v1 import ReqSummary
from biz.dfch.specmgr.req.resources.req_list import req_list
from biz.dfch.specmgr.req.tools._paths import ensure_req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req

_MINIMAL_BODY = textwrap.dedent(
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

_OTHER_BODY = _MINIMAL_BODY.replace("Maximum Engine Temperature", "Minimum Oil Pressure")


class TestReqListResource(unittest.TestCase):
    """Tests for the `req_list` resource function (`specmgr://req/list`)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        """req_list must return exactly the valid requirements, silently skipping a broken file."""
        first = create_req(_MINIMAL_BODY)
        second = create_req(_OTHER_BODY)

        base_dir = ensure_req_base_dir()
        (base_dir / "broken.md").write_text("not a valid requirement, no headings at all", encoding="utf-8")

        result = req_list()

        self.assertEqual(len(result), 2)
        for summary in result:
            self.assertIsInstance(summary, ReqSummary)
        ids = {summary.id for summary in result}
        self.assertEqual(ids, {first.frontmatter.id, second.frontmatter.id})
        titles = {summary.title for summary in result}
        self.assertEqual(titles, {"Maximum Engine Temperature", "Minimum Oil Pressure"})
        statuses = {summary.status for summary in result}
        self.assertEqual(statuses, {"draft"})
        for summary in result:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_list_for_missing_directory(self) -> None:
        """req_list must return an empty list when the base directory does not exist."""
        self.assertFalse((self.docs_root / "req").exists())
        self.assertEqual(req_list(), [])


if __name__ == "__main__":
    unittest.main()
