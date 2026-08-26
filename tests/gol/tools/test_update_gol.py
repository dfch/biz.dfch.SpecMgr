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

"""Tests for the ``update_gol`` ``@mcp.tool()`` wrapper (Task 3.4)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.gol.models.v1 import GolDocument, parse_gol
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, ensure_gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.gol.tools.update_gol import update_gol

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_UPDATED_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output, fuel consumption, and price.

    ## Description

    Updated description text.

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_BAD_PRIORITY_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Priority

    100

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized goal sections.\n"


class TempGolDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_gol(self) -> GolDocument:
        """Create and return a real, persisted goal via create_gol."""
        return create_gol(_MINIMAL_BODY)


class TestUpdateGol(TempGolDirTestCase):
    """Tests for the update_gol tool."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """update_gol must replace the body but preserve every frontmatter field but `updated`."""
        original = self.existing_gol()

        result = update_gol(original.frontmatter.id, _UPDATED_BODY)

        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.type, original.frontmatter.type)
        self.assertEqual(result.frontmatter.status, original.frontmatter.status)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertIsNotNone(result.body.description)

    def test_written_file_round_trips_via_parse_gol(self) -> None:
        """The updated file on disk must parse back into the returned document's shape."""
        original = self.existing_gol()

        result = update_gol(original.frontmatter.id, _UPDATED_BODY)

        base_dir = ensure_gol_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        self.assertEqual(len(matching), 1)
        on_disk = parse_gol(matching[0].read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.updated, result.frontmatter.updated)
        self.assertIsNotNone(on_disk.body.description)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """update_gol must raise GolNotFoundError for an id with no matching file."""
        with self.assertRaises(GolNotFoundError):
            update_gol("no-such-id", _MINIMAL_BODY)

    def test_invalid_content_raises_and_leaves_file_unchanged(self) -> None:
        """A structurally invalid body must raise AssertionError, leaving the file untouched."""
        original = self.existing_gol()
        base_dir = ensure_gol_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_gol(original.frontmatter.id, _MALFORMED_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)

    def test_field_validation_failure_raises_and_leaves_file_unchanged(self) -> None:
        """A field-level validation failure (bad `## Priority` value) must raise, leaving the file untouched."""
        original = self.existing_gol()
        base_dir = ensure_gol_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            update_gol(original.frontmatter.id, _BAD_PRIORITY_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
