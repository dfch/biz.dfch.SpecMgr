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

"""Tests for the ``tsk_list`` resource (``specmgr://tsk/list``, Task 3.10)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.tsk.models.v1 import TskSummary
from biz.dfch.specmgr.tsk.resources.tsk_list import tsk_list
from biz.dfch.specmgr.tsk.tools._paths import ensure_tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### Kickoff

    Started the task list.
    """
)

_OTHER_BODY = _MINIMAL_BODY.replace("Simple Task List", "Another Task List")


class TestTskListResource(unittest.TestCase):
    """Tests for the `tsk_list` resource function (`specmgr://tsk/list`)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        """tsk_list must return exactly the valid task lists, silently skipping a broken file."""
        first = create_tsk(_MINIMAL_BODY)
        second = create_tsk(_OTHER_BODY)

        base_dir = ensure_tsk_base_dir()
        (base_dir / "broken.md").write_text("not a valid task list, no headings at all", encoding="utf-8")

        result = tsk_list()

        self.assertEqual(len(result), 2)
        for summary in result:
            self.assertIsInstance(summary, TskSummary)
        ids = {summary.id for summary in result}
        self.assertEqual(ids, {first.frontmatter.id, second.frontmatter.id})
        titles = {summary.title for summary in result}
        self.assertEqual(titles, {"Simple Task List", "Another Task List"})
        statuses = {summary.status for summary in result}
        self.assertEqual(statuses, {"draft"})
        for summary in result:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_list_for_missing_directory(self) -> None:
        """tsk_list must return an empty list when the base directory does not exist."""
        self.assertFalse((self.docs_root / "tsk").exists())
        self.assertEqual(tsk_list(), [])


if __name__ == "__main__":
    unittest.main()
