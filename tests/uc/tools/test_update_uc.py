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

"""Tests for the ``update_uc`` ``@mcp.tool()`` wrapper (Task 3.1.5)."""

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
from biz.dfch.specmgr.uc.tools.update_uc import update_uc

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

_UPDATED_BODY = textwrap.dedent(
    """\
    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues an updated request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    User Goal

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
    3. Company ships the order.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized use-case sections.\n"


class TempUcDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def existing_uc(self) -> UcDocument:
        """Create and return a real, persisted use case via create_uc."""
        return create_uc(_MINIMAL_BODY)


class TestUpdateUc(TempUcDirTestCase):
    """Tests for the update_uc tool."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """update_uc must replace the body but preserve every frontmatter field but `updated`."""
        original = self.existing_uc()

        result = update_uc(original.frontmatter.id, _UPDATED_BODY)

        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.type, original.frontmatter.type)
        self.assertEqual(result.frontmatter.status, original.frontmatter.status)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertEqual(result.body.characteristic_information.level.body[0].text, "User Goal")

    def test_written_file_round_trips_via_parse_uc(self) -> None:
        """The updated file on disk must parse back into the returned document's shape."""
        original = self.existing_uc()

        result = update_uc(original.frontmatter.id, _UPDATED_BODY)

        base_dir = ensure_uc_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        self.assertEqual(len(matching), 1)
        on_disk = parse_uc(matching[0].read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.updated, result.frontmatter.updated)
        self.assertEqual(len(on_disk.body.main_success_scenario.steps), 3)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """update_uc must raise UcNotFoundError for an id with no matching file."""
        with self.assertRaises(UcNotFoundError):
            update_uc("no-such-id", _MINIMAL_BODY)

    def test_invalid_content_raises_and_leaves_file_unchanged(self) -> None:
        """A structurally invalid body must raise AssertionError, leaving the file untouched."""
        original = self.existing_uc()
        base_dir = ensure_uc_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_uc(original.frontmatter.id, _MALFORMED_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)

    def test_field_validation_failure_raises_and_leaves_file_unchanged(self) -> None:
        """A cross-field validation failure (unresolvable Extension step reference) must raise,
        leaving the file untouched."""
        original = self.existing_uc()
        base_dir = ensure_uc_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")
        text = _UPDATED_BODY + ("\n## Extensions\n\n### Extension 99a. Out-of-range reference\n\n1. Not resolvable.\n")

        with self.assertRaises(ValidationError):
            update_uc(original.frontmatter.id, text)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
