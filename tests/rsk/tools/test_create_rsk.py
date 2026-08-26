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

"""Tests for the ``create_rsk`` ``@mcp.tool()`` wrapper (Task 3.3)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.rsk.models.v1 import RskDocument, parse_rsk
from biz.dfch.specmgr.rsk.tools._paths import rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Risk

    ## Cause

    A root condition.

    ## Trigger

    An event that sets the risk in motion.

    ## Consequence

    A bounded consequence.

    ## Scope

    - Sample subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Sample treatment measures.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized risk sections.\n"

_INVALID_STRATEGY_BODY = _MINIMAL_BODY.replace("reduce\n", "tolerate\n")

_OUT_OF_RANGE_PROBABILITY_BODY = _MINIMAL_BODY.replace("### Probability 4", "### Probability 6")

_ZERO_SCOPE_BODY = _MINIMAL_BODY.replace("- Sample subsystem\n", "")


class TempRskDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateRsk(TempRskDirTestCase):
    """Tests for the create_rsk tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_rsk must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_rsk(_MINIMAL_BODY)

        self.assertIsInstance(result, RskDocument)
        self.assertIsNotNone(result.frontmatter.id)
        self.assertEqual(result.frontmatter.type, "rsk")
        self.assertEqual(result.frontmatter.status, "open")
        self.assertIsNotNone(result.frontmatter.created)
        self.assertEqual(result.frontmatter.created, result.frontmatter.updated)
        self.assertEqual(result.frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(result.body.text, "Sample Risk")

    def test_writes_expected_filename(self) -> None:
        """create_rsk must write f'rsk-{id}-{slug}.md' under the risk base dir."""
        result = create_rsk(_MINIMAL_BODY)

        expected_path = rsk_base_dir() / f"rsk-{result.frontmatter.id}-sample-risk.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_rsk(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_rsk(_MINIMAL_BODY)

        expected_path = rsk_base_dir() / f"rsk-{result.frontmatter.id}-sample-risk.md"
        on_disk = parse_rsk(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.status, "open")
        self.assertEqual(on_disk.body.text, "Sample Risk")
        self.assertEqual(on_disk.body.initial_assessment.level, "high")
        self.assertEqual(on_disk.body.residual_assessment.level, "medium")
        self.assertEqual(on_disk.body.strategy.value.text, "reduce")
        self.assertEqual([item.text for item in on_disk.body.scope.items], ["Sample subsystem"])

    def test_creates_base_dir_if_missing(self) -> None:
        """create_rsk must create the risk base directory if it does not exist yet."""
        self.assertFalse(rsk_base_dir().exists())

        create_rsk(_MINIMAL_BODY)

        self.assertTrue(rsk_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_rsk(_MALFORMED_BODY)

        self.assertFalse(rsk_base_dir().exists())

    def test_invalid_strategy_word_raises_and_writes_nothing(self) -> None:
        """A `## Strategy` word outside the TARA closed set must raise and write nothing."""
        with self.assertRaises(ValidationError):
            create_rsk(_INVALID_STRATEGY_BODY)

        self.assertFalse(rsk_base_dir().exists())

    def test_out_of_range_assessment_heading_raises_and_writes_nothing(self) -> None:
        """An assessment heading value outside 1..5 (e.g. `### Probability 6`) must raise and write nothing."""
        with self.assertRaises(AssertionError):
            create_rsk(_OUT_OF_RANGE_PROBABILITY_BODY)

        self.assertFalse(rsk_base_dir().exists())

    def test_zero_scope_entries_raises_and_writes_nothing(self) -> None:
        """A `## Scope` section with zero list entries must raise and write nothing."""
        with self.assertRaises(AssertionError):
            create_rsk(_ZERO_SCOPE_BODY)

        self.assertFalse(rsk_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
