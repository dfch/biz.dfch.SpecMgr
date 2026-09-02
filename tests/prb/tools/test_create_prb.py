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

"""Tests for the ``create_prb`` ``@mcp.tool()`` wrapper (Task 3.3)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.prb.models.v1 import PrbFrontmatter, parse_prb
from biz.dfch.specmgr.prb.tools._paths import prb_base_dir
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

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized problem statement sections.\n"

_MISSING_FUTURE_STATE_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is wrong.

    ## Gap

    There is a gap.
    """
)


class TempPrbDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreatePrb(TempPrbDirTestCase):
    """Tests for the create_prb tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_prb must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_prb(_MINIMAL_BODY)

        self.assertIsInstance(result, PrbFrontmatter)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "prb")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_prb(result.id)
        self.assertEqual(fetched.body.text, "Simple Problem Statement")

    def test_writes_expected_filename(self) -> None:
        """create_prb must write f'prb-{id}-{slug}.md' under the problem statement base dir."""
        result = create_prb(_MINIMAL_BODY)

        expected_path = prb_base_dir() / f"prb-{result.id}-simple-problem-statement.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_prb(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_prb(_MINIMAL_BODY)

        expected_path = prb_base_dir() / f"prb-{result.id}-simple-problem-statement.md"
        on_disk = parse_prb(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Simple Problem Statement")
        self.assertIn("Something is wrong.", on_disk.body.current_state.summary.text)

    def test_creates_base_dir_if_missing(self) -> None:
        """create_prb must create the problem statement base directory if it does not exist yet."""
        self.assertFalse(prb_base_dir().exists())

        create_prb(_MINIMAL_BODY)

        self.assertTrue(prb_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_prb(_MALFORMED_BODY)

        self.assertFalse(prb_base_dir().exists())

    def test_missing_mandatory_section_raises_and_writes_nothing(self) -> None:
        """A body missing the mandatory `## Future State` section must raise, writing nothing."""
        with self.assertRaises(AssertionError):
            create_prb(_MISSING_FUTURE_STATE_BODY)

        self.assertFalse(prb_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
