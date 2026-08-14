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

"""Tests for the ``set_status_req`` ``@mcp.tool()`` wrapper (Task 3.14)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.req.models.v1 import ReqDocument, parse_req
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError, ensure_req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.req.tools.set_status_req import set_status_req

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


class TempReqDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_req(self) -> ReqDocument:
        """Create and return a real, persisted requirement via create_req."""
        return create_req(_MINIMAL_BODY)

    def _find_path(self, id_: str) -> Path:
        base_dir = ensure_req_base_dir()
        matching = [p for p in base_dir.glob("*.md") if id_ in p.name]
        assert len(matching) == 1
        return matching[0]


class TestSetStatusReq(TempReqDirTestCase):
    """Tests for the set_status_req tool."""

    def test_sets_status_and_bumps_updated(self) -> None:
        """set_status_req must write the new status and a fresh `updated` timestamp."""
        original = self.existing_req()

        result = set_status_req(original.frontmatter.id, "accepted")

        self.assertEqual(result.frontmatter.status, "accepted")
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)

    def test_body_is_left_unchanged(self) -> None:
        """set_status_req must not alter the body at all."""
        original = self.existing_req()

        set_status_req(original.frontmatter.id, "accepted")

        on_disk = parse_req(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.body.text, original.body.text)
        self.assertEqual([item.text for item in on_disk.body.characteristics.items], ["Safety", "Reliability"])

    def test_written_file_round_trips_via_parse_req(self) -> None:
        """The updated file on disk must parse back with the new status."""
        original = self.existing_req()

        set_status_req(original.frontmatter.id, "implemented")

        on_disk = parse_req(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.status, "implemented")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """set_status_req must raise ReqNotFoundError for an id with no matching file."""
        with self.assertRaises(ReqNotFoundError):
            set_status_req("no-such-id", "accepted")

    def test_invalid_status_raises_and_leaves_file_unchanged(self) -> None:
        """An invalid status must fail validation without writing."""
        original = self.existing_req()
        path = self._find_path(original.frontmatter.id)
        before = path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status_req(original.frontmatter.id, "not-a-real-status")

        self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
