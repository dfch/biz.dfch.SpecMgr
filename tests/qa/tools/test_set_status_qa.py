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

"""Tests for the ``set_status_qa`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.qa.models.v1 import QaDocument, parse_qa
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError, ensure_qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.qa.tools.set_status_qa import set_status_qa

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)


class TempQaDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_qa(self) -> QaDocument:
        """Create and return a real, persisted QA document via create_qa."""
        return create_qa(_MINIMAL_BODY)

    def _find_path(self, id_: str) -> Path:
        base_dir = ensure_qa_base_dir()
        matching = [p for p in base_dir.glob("*.md") if id_ in p.name]
        assert len(matching) == 1
        return matching[0]


class TestSetStatusQa(TempQaDirTestCase):
    """Tests for the set_status_qa tool."""

    def test_sets_status_and_bumps_updated(self) -> None:
        """set_status_qa must write the new status and a fresh `updated` timestamp."""
        original = self.existing_qa()

        result = set_status_qa(original.frontmatter.id, "active")

        self.assertEqual(result.frontmatter.status, "active")
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)

    def test_body_is_left_unchanged(self) -> None:
        """set_status_qa must not alter the body at all."""
        original = self.existing_qa()

        set_status_qa(original.frontmatter.id, "active")

        on_disk = parse_qa(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.body.text, original.body.text)
        self.assertIsNone(on_disk.body.compatibility.items)

    def test_written_file_round_trips_via_parse_qa(self) -> None:
        """The updated file on disk must parse back with the new status."""
        original = self.existing_qa()

        set_status_qa(original.frontmatter.id, "done")

        on_disk = parse_qa(self._find_path(original.frontmatter.id).read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.status, "done")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """set_status_qa must raise QaNotFoundError for an id with no matching file."""
        with self.assertRaises(QaNotFoundError):
            set_status_qa("no-such-id", "active")

    def test_invalid_status_raises_and_leaves_file_unchanged(self) -> None:
        """An invalid status must fail validation without writing."""
        original = self.existing_qa()
        path = self._find_path(original.frontmatter.id)
        before = path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status_qa(original.frontmatter.id, "not-a-real-status")

        self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
