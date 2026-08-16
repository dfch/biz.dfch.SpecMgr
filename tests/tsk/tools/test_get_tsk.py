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

"""Tests for the ``get_tsk`` ``@mcp.tool()`` wrapper (Task 3.8)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.tsk.models.v1 import TskDocument
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.tsk.tools.get_tsk import get_tsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### Kickoff

    Started the task list.
    """
)


class TestGetTsk(unittest.TestCase):
    """Tests for the get_tsk tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_tsk must return the full TskDocument for a matching id."""
        created = create_tsk(_MINIMAL_BODY)

        result = get_tsk(created.frontmatter.id)

        self.assertIsInstance(result, TskDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "Simple Task List")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_tsk must raise TskNotFoundError when no task list matches the given id."""
        create_tsk(_MINIMAL_BODY)

        with self.assertRaises(TskNotFoundError):
            get_tsk("no-such-id")


if __name__ == "__main__":
    unittest.main()
