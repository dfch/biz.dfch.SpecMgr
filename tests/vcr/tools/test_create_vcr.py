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

"""Tests for the ``create_vcr`` ``@mcp.tool()`` wrapper (Task 2.1)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.vcr.models.v1 import VcrDocument, parse_vcr
from biz.dfch.specmgr.vcr.tools._paths import vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes
    """
)

# Structurally valid, but a field/cross-field failure: two `### AC-001`
# headings are duplicate AC numbers (the `Vcr` after-validator's
# `ValidationError` channel).
_BAD_AC_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes

    ### AC-001 (Analysis): Duplicate AC number
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized verification case record sections.\n"


class TempVcrDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateVcr(TempVcrDirTestCase):
    """Tests for the create_vcr tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_vcr must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_vcr(_MINIMAL_BODY)

        self.assertIsInstance(result, VcrDocument)
        self.assertIsNotNone(result.frontmatter.id)
        self.assertEqual(result.frontmatter.type, "vcr")
        self.assertEqual(result.frontmatter.status, "draft")
        self.assertIsNotNone(result.frontmatter.created)
        self.assertEqual(result.frontmatter.created, result.frontmatter.updated)
        self.assertEqual(result.frontmatter.version, CURRENT_SCHEMA_VERSION)
        self.assertEqual(result.body.text, "Sample Verification Case")

    def test_writes_expected_filename(self) -> None:
        """create_vcr must write f'vcr-{id}-{slug}.md' under the verification case record base dir."""
        result = create_vcr(_MINIMAL_BODY)

        expected_path = vcr_base_dir() / f"vcr-{result.frontmatter.id}-sample-verification-case.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_vcr(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_vcr(_MINIMAL_BODY)

        expected_path = vcr_base_dir() / f"vcr-{result.frontmatter.id}-sample-verification-case.md"
        on_disk = parse_vcr(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Sample Verification Case")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_vcr must create the verification case record base directory if it does not exist yet."""
        self.assertFalse(vcr_base_dir().exists())

        create_vcr(_MINIMAL_BODY)

        self.assertTrue(vcr_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_vcr(_MALFORMED_BODY)

        self.assertFalse(vcr_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (duplicate `### AC-001` number) must raise, writing nothing."""
        with self.assertRaises(ValidationError):
            create_vcr(_BAD_AC_BODY)

        self.assertFalse(vcr_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
