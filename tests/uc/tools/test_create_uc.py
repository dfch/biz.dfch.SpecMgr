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

"""Tests for the ``create_uc`` ``@mcp.tool()`` wrapper (Task 3.1.5)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.uc.models.v2 import UcDocument, UcFrontmatter, parse_uc
from biz.dfch.specmgr.uc.tools._paths import uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.uc.tools.get_uc import get_uc

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

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized use-case sections.\n"


class TempUcDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateUc(TempUcDirTestCase):
    """Tests for the create_uc tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_uc must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_uc(_MINIMAL_BODY)

        self.assertIsInstance(result, UcFrontmatter)
        self.assertNotIsInstance(result, UcDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "uc")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_uc(result.id)
        self.assertEqual(fetched.body.text, "Buy Goods")

    def test_writes_expected_filename(self) -> None:
        """create_uc must write f'uc-{id}-{slug}.md' under the use-case base dir."""
        result = create_uc(_MINIMAL_BODY)

        expected_path = uc_base_dir() / f"uc-{result.id}-buy-goods.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_uc(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_uc(_MINIMAL_BODY)

        expected_path = uc_base_dir() / f"uc-{result.id}-buy-goods.md"
        on_disk = parse_uc(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Buy Goods")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_uc must create the use-case base directory if it does not exist yet."""
        self.assertFalse(uc_base_dir().exists())

        create_uc(_MINIMAL_BODY)

        self.assertTrue(uc_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_uc(_MALFORMED_BODY)

        self.assertFalse(uc_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A cross-field validation failure (unresolvable Extension step reference) must raise,
        writing nothing."""
        text = _MINIMAL_BODY + ("\n## Extensions\n\n### Extension 99a. Out-of-range reference\n\n1. Not resolvable.\n")

        with self.assertRaises(ValidationError):
            create_uc(text)

        self.assertFalse(uc_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
