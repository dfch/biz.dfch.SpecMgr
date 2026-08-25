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

"""Tests for the ``update_rsk`` ``@mcp.tool()`` wrapper (Task 3.4)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.rsk.models.v1 import RskDocument, parse_rsk
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError, ensure_rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.rsk.tools.update_rsk import update_rsk

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

_UPDATED_BODY = textwrap.dedent(
    """\
    # Sample Risk

    ## Cause

    A revised root condition.

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

    Revised treatment measures.

    ## Residual Assessment

    ### Probability 1

    ### Impact 2
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized risk sections.\n"

_NO_STRATEGY_BODY = _MINIMAL_BODY.replace("## Strategy\n\nreduce\n\n", "")


class TempRskDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_rsk(self) -> RskDocument:
        """Create and return a real, persisted risk via create_rsk."""
        return create_rsk(_MINIMAL_BODY)


class TestUpdateRsk(TempRskDirTestCase):
    """Tests for the update_rsk tool."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """update_rsk must replace the body but preserve every frontmatter field but `updated`."""
        original = self.existing_rsk()

        result = update_rsk(original.frontmatter.id, _UPDATED_BODY)

        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.type, original.frontmatter.type)
        self.assertEqual(result.frontmatter.status, original.frontmatter.status)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(result.body.cause.text, "## Cause\n\nA revised root condition.\n")
        self.assertEqual(result.body.residual_assessment.level, "low")

    def test_written_file_round_trips_via_parse_rsk(self) -> None:
        """The updated file on disk must parse back into the returned document's shape."""
        original = self.existing_rsk()

        result = update_rsk(original.frontmatter.id, _UPDATED_BODY)

        base_dir = ensure_rsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        self.assertEqual(len(matching), 1)
        on_disk = parse_rsk(matching[0].read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.updated, result.frontmatter.updated)
        self.assertEqual(on_disk.body.residual_assessment.probability.value, 1)
        self.assertEqual(on_disk.body.residual_assessment.impact.value, 2)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """update_rsk must raise RskNotFoundError for an id with no matching file."""
        with self.assertRaises(RskNotFoundError):
            update_rsk("no-such-id", _MINIMAL_BODY)

    def test_invalid_content_raises_and_leaves_file_unchanged(self) -> None:
        """A structurally invalid body must raise AssertionError, leaving the file untouched."""
        original = self.existing_rsk()
        base_dir = ensure_rsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_rsk(original.frontmatter.id, _MALFORMED_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)

    def test_dropping_mandatory_section_raises_and_leaves_file_unchanged(self) -> None:
        """Replacing the body without its mandatory `## Strategy` section must raise, leaving the file untouched."""
        original = self.existing_rsk()
        base_dir = ensure_rsk_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_rsk(original.frontmatter.id, _NO_STRATEGY_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
