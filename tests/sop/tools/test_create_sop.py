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

"""Tests for the ``create_sop`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.sop.models.v1 import SopDocument, parse_sop
from biz.dfch.specmgr.sop.tools._paths import sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop

_MINIMAL_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)

# Structurally valid, but a field/cross-field failure: two `### Step 1:`
# headings are duplicate step numbers (the `Sop` after-validator's
# `ValidationError` channel).
_BAD_STEP_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.

    ### Step 1: Duplicate step

    HR submits the request again.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized SOP sections.\n"


class TempSopDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateSop(TempSopDirTestCase):
    """Tests for the create_sop tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_sop must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_sop(_MINIMAL_BODY)

        self.assertIsInstance(result, SopDocument)
        self.assertIsNotNone(result.frontmatter.id)
        self.assertEqual(result.frontmatter.type, "sop")
        self.assertEqual(result.frontmatter.status, "draft")
        self.assertIsNotNone(result.frontmatter.created)
        self.assertEqual(result.frontmatter.created, result.frontmatter.updated)
        self.assertEqual(result.frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(result.body.text, "New Employee IT Account Provisioning")

    def test_writes_expected_filename(self) -> None:
        """create_sop must write f'sop-{id}-{slug}.md' under the SOP base dir."""
        result = create_sop(_MINIMAL_BODY)

        expected_path = sop_base_dir() / f"sop-{result.frontmatter.id}-new-employee-it-account-provisioning.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_sop(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_sop(_MINIMAL_BODY)

        expected_path = sop_base_dir() / f"sop-{result.frontmatter.id}-new-employee-it-account-provisioning.md"
        on_disk = parse_sop(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "New Employee IT Account Provisioning")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_sop must create the SOP base directory if it does not exist yet."""
        self.assertFalse(sop_base_dir().exists())

        create_sop(_MINIMAL_BODY)

        self.assertTrue(sop_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_sop(_MALFORMED_BODY)

        self.assertFalse(sop_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (duplicate `### Step 1` number) must raise, writing nothing."""
        with self.assertRaises(ValidationError):
            create_sop(_BAD_STEP_BODY)

        self.assertFalse(sop_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
