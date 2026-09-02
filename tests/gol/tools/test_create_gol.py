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

"""Tests for the ``create_gol`` ``@mcp.tool()`` wrapper (Task 3.3)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.gol.models.v1 import GolFrontmatter, parse_gol
from biz.dfch.specmgr.gol.tools._paths import gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.gol.tools.get_gol import get_gol
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

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


class TestCreateGol(TempGolDirTestCase):
    """Tests for the create_gol tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_gol must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_gol(_MINIMAL_BODY)

        self.assertIsInstance(result, GolFrontmatter)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "gol")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_gol(result.id)
        self.assertEqual(fetched.body.text, "Competitive Engines in Consumer Vehicles")

    def test_writes_expected_filename(self) -> None:
        """create_gol must write f'gol-{id}-{slug}.md' under the goal base dir."""
        result = create_gol(_MINIMAL_BODY)

        expected_path = gol_base_dir() / f"gol-{result.id}-competitive-engines-in-consumer-vehicles.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_gol(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_gol(_MINIMAL_BODY)

        expected_path = gol_base_dir() / f"gol-{result.id}-competitive-engines-in-consumer-vehicles.md"
        on_disk = parse_gol(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Competitive Engines in Consumer Vehicles")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_gol must create the goal base directory if it does not exist yet."""
        self.assertFalse(gol_base_dir().exists())

        create_gol(_MINIMAL_BODY)

        self.assertTrue(gol_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_gol(_MALFORMED_BODY)

        self.assertFalse(gol_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (bad `## Priority` value) must raise, writing nothing."""
        with self.assertRaises(ValidationError):
            create_gol(_BAD_PRIORITY_BODY)

        self.assertFalse(gol_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
