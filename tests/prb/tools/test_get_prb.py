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

"""Tests for the ``get_prb`` ``@mcp.tool()`` wrapper (Task 3.8)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.prb.models.v1 import PrbDocument
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.prb.tools.get_prb import get_prb

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is wrong.

    ## Gap

    There is a gap.

    ## Future State

    It will be fixed.
    """
)


class TestGetPrb(unittest.TestCase):
    """Tests for the get_prb tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_prb must return the full PrbDocument for a matching id."""
        created = create_prb(_MINIMAL_BODY)

        result = get_prb(created.frontmatter.id)

        self.assertIsInstance(result, PrbDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "Simple Problem Statement")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_prb must raise PrbNotFoundError, with the standardized message, when no problem statement matches."""
        create_prb(_MINIMAL_BODY)

        with self.assertRaises(PrbNotFoundError) as ctx:
            get_prb("no-such-id")
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)


if __name__ == "__main__":
    unittest.main()
