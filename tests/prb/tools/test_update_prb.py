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

"""Tests for the ``update_prb`` ``@mcp.tool()`` wrapper (Task 3.4)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.prb.models.v1 import PrbDocument, parse_prb
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, ensure_prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.prb.tools.update_prb import update_prb

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

_UPDATED_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is very wrong indeed.

    ### What Is the Problem?

    Widgets keep disappearing.

    ## Gap

    There is a much bigger gap than we thought.

    ## Future State

    It will actually be fixed.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized problem statement sections.\n"

_MISSING_GAP_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is wrong.

    ## Future State

    It will be fixed.
    """
)


class TempPrbDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_prb(self) -> PrbDocument:
        """Create and return a real, persisted problem statement via create_prb."""
        return create_prb(_MINIMAL_BODY)


class TestUpdatePrb(TempPrbDirTestCase):
    """Tests for the update_prb tool."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """update_prb must replace the body but preserve every frontmatter field but `updated`."""
        original = self.existing_prb()

        result = update_prb(original.frontmatter.id, _UPDATED_BODY)

        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.type, original.frontmatter.type)
        self.assertEqual(result.frontmatter.status, original.frontmatter.status)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertIn("very wrong indeed", result.body.current_state.summary.text)
        self.assertIsNotNone(result.body.current_state.question_1)

    def test_written_file_round_trips_via_parse_prb(self) -> None:
        """The updated file on disk must parse back into the returned document's shape."""
        original = self.existing_prb()

        result = update_prb(original.frontmatter.id, _UPDATED_BODY)

        base_dir = ensure_prb_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        self.assertEqual(len(matching), 1)
        on_disk = parse_prb(matching[0].read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.updated, result.frontmatter.updated)
        self.assertIn("much bigger gap", on_disk.body.gap.text)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """update_prb must raise PrbNotFoundError for an id with no matching file."""
        with self.assertRaises(PrbNotFoundError):
            update_prb("no-such-id", _MINIMAL_BODY)

    def test_invalid_content_raises_and_leaves_file_unchanged(self) -> None:
        """A structurally invalid body must raise AssertionError, leaving the file untouched."""
        original = self.existing_prb()
        base_dir = ensure_prb_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_prb(original.frontmatter.id, _MALFORMED_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)

    def test_dropping_mandatory_section_raises_and_leaves_file_unchanged(self) -> None:
        """Replacing the body with a missing mandatory `## Gap` section must raise, leaving the file untouched."""
        original = self.existing_prb()
        base_dir = ensure_prb_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_prb(original.frontmatter.id, _MISSING_GAP_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
