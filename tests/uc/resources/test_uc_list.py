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

"""Tests for the ``uc_list`` resource (``specmgr://uc/list``, Task 3.1.6).

Also exercises :class:`~biz.dfch.specmgr.uc.models.v2.UcSummary` -- no
dedicated ``test_summary.py`` exists (mirroring REQ, which has none either).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.uc.models.v2 import UcSummary
from biz.dfch.specmgr.uc.resources.uc_list import uc_list
from biz.dfch.specmgr.uc.tools._paths import ensure_uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc

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

_OTHER_BODY = _MINIMAL_BODY.replace("Buy Goods", "Return Goods")


class TestUcListResource(unittest.TestCase):
    """Tests for the `uc_list` resource function (`specmgr://uc/list`)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_summaries_and_skips_malformed_file(self) -> None:
        """uc_list must return exactly the valid use cases, silently skipping a broken file."""
        first = create_uc(_MINIMAL_BODY)
        second = create_uc(_OTHER_BODY)

        base_dir = ensure_uc_base_dir()
        (base_dir / "broken.md").write_text("not a valid use case, no headings at all", encoding="utf-8")

        result = uc_list()

        self.assertEqual(len(result), 2)
        for summary in result:
            self.assertIsInstance(summary, UcSummary)
        ids = {summary.id for summary in result}
        self.assertEqual(ids, {first.frontmatter.id, second.frontmatter.id})
        titles = {summary.title for summary in result}
        self.assertEqual(titles, {"Buy Goods", "Return Goods"})
        statuses = {summary.status for summary in result}
        self.assertEqual(statuses, {"draft"})
        for summary in result:
            self.assertNotIn(".md", summary.ref)
            self.assertTrue(summary.ref)

    def test_empty_list_for_missing_directory(self) -> None:
        """uc_list must return an empty list when the base directory does not exist."""
        self.assertFalse((self.docs_root / "uc").exists())
        self.assertEqual(uc_list(), [])


if __name__ == "__main__":
    unittest.main()
