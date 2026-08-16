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

"""Tests for the ``get_uc`` ``@mcp.tool()`` wrapper (Task 3.1.5)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.uc.models.v2 import UcDocument
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.uc.tools.get_uc import get_uc

_MINIMAL_BODY = textwrap.dedent(
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


class TestGetUc(unittest.TestCase):
    """Tests for the get_uc tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_uc must return the full UcDocument for a matching id."""
        created = create_uc(_MINIMAL_BODY)

        result = get_uc(created.frontmatter.id)

        self.assertIsInstance(result, UcDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "Buy Goods")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_uc must raise UcNotFoundError when no use case matches the given id."""
        create_uc(_MINIMAL_BODY)

        with self.assertRaises(UcNotFoundError):
            get_uc("no-such-id")


if __name__ == "__main__":
    unittest.main()
