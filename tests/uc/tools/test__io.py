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

"""Tests for ``uc.tools._io`` (thin file read helpers)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.uc.models.v2 import UcDocument
from biz.dfch.specmgr.uc.tools._io import load_by_id, read_uc
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: uc
    version: 1.0.0
    status: draft
    created: 2026-08-05
    updated: 2026-08-05
    ---

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


def _uc_text(id_: str) -> str:
    """Render a minimal, valid use-case document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReadUc(unittest.TestCase):
    """Tests for read_uc."""

    def test_reads_and_parses_a_real_file(self):
        """read_uc must return a UcDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_uc_text("some-id"), encoding="utf-8")

            document = read_uc(path)

            self.assertIsInstance(document, UcDocument)
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.body.text, "Buy Goods")


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_uc(self):
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            expected_path.write_text(_uc_text("the-id"), encoding="utf-8")

            path, document = load_by_id(base, "the-id")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self):
        """load_by_id must raise UcNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(UcNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
