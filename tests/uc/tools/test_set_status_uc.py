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

"""Tests for the ``set_status_uc`` ``@mcp.tool()`` wrapper (Task 3.1.5)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.uc.models.v2 import UcDocument, parse_uc
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, ensure_uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.uc.tools.set_status_uc import set_status_uc

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


class TempUcDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_uc(self) -> UcDocument:
        """Create and return a real, persisted use case via create_uc."""
        return create_uc(_MINIMAL_BODY)

    def _find_path(self, id_: str) -> Path:
        base_dir = ensure_uc_base_dir()
        matching = [p for p in base_dir.glob("*.md") if id_ in p.name]
        assert len(matching) == 1
        return matching[0]


class TestSetStatusUc(TempUcDirTestCase):
    """Tests for the set_status_uc tool."""

    def test_sets_status_and_bumps_updated(self) -> None:
        """set_status_uc must write the new status and a fresh `updated` timestamp."""
        original = self.existing_uc()

        result = set_status_uc(original.frontmatter.id, "accepted")

        self.assertEqual(result.frontmatter.status, "accepted")
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)

    def test_body_is_left_unchanged(self) -> None:
        """set_status_uc must not alter the body at all."""
        original = self.existing_uc()

        set_status_uc(original.frontmatter.id, "accepted")

        on_disk = parse_uc(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.body.text, original.body.text)

    def test_written_file_round_trips_via_parse_uc(self) -> None:
        """The updated file on disk must parse back with the new status."""
        original = self.existing_uc()

        set_status_uc(original.frontmatter.id, "deprecated")

        on_disk = parse_uc(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.status, "deprecated")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """set_status_uc must raise UcNotFoundError for an id with no matching file."""
        with self.assertRaises(UcNotFoundError):
            set_status_uc("no-such-id", "accepted")

    def test_invalid_status_raises_and_leaves_file_unchanged(self) -> None:
        """An invalid status must fail validation without writing."""
        original = self.existing_uc()
        path = self._find_path(original.frontmatter.id)
        before = path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status_uc(original.frontmatter.id, "not-a-real-status")

        self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
