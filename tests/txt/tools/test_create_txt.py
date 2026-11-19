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

"""Tests for the ``create_txt`` ``@mcp.tool()`` wrapper (feat-229-txt Phase 110)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.txt.models.v1 import TxtDocument, TxtFrontmatter, parse_txt
from biz.dfch.specmgr.txt.tools._paths import txt_base_dir
from biz.dfch.specmgr.txt.tools.create_txt import create_txt
from biz.dfch.specmgr.txt.tools.get_txt import get_txt

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Ad-hoc review notes

    Some free-form prose about what was reviewed.

    ## Updates

    ### 2026-08-31 00:00:00.000Z - Created

    Initial draft of the review notes.
    """
)

# Structurally valid, but a field/cross-field failure: two out-of-order
# `### ` update entries (newest-first violated) -- the `Updates`
# model-validator's `ValidationError` channel.
_BAD_UPDATES_BODY = textwrap.dedent(
    """\
    # Ad-hoc review notes

    Some free-form prose about what was reviewed.

    ## Updates

    ### 2026-08-30 00:00:00.000Z - Older

    An older entry.

    ### 2026-08-31 00:00:00.000Z - Created

    A newer entry below it.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized sections and no Updates log.\n"


class TempTxtDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateTxt(TempTxtDirTestCase):
    """Tests for the create_txt tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_txt must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_txt(_MINIMAL_BODY)

        self.assertIsInstance(result, TxtFrontmatter)
        self.assertNotIsInstance(result, TxtDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "txt")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_txt(result.id)
        self.assertEqual(fetched.body.text, "Ad-hoc review notes")

    def test_writes_expected_filename(self) -> None:
        """create_txt must write f'txt-{id}-{slug}.md' under the free-form text base dir."""
        result = create_txt(_MINIMAL_BODY)

        expected_path = txt_base_dir() / f"txt-{result.id}-ad-hoc-review-notes.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_txt(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_txt(_MINIMAL_BODY)

        expected_path = txt_base_dir() / f"txt-{result.id}-ad-hoc-review-notes.md"
        on_disk = parse_txt(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Ad-hoc review notes")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_txt must create the free-form text base directory if it does not exist yet."""
        self.assertFalse(txt_base_dir().exists())

        create_txt(_MINIMAL_BODY)

        self.assertTrue(txt_base_dir().is_dir())

    def test_invalid_content_returns_validate_result_and_writes_nothing(self) -> None:
        """A structurally invalid body must return ``ValidateResult(valid=False, ...)`` and write no
        file at all (feat-204-create-error)."""
        result = create_txt(_MALFORMED_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertTrue(message)
        self.assertIn("txt create_txt (body): ", message)
        self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
        self.assertFalse(txt_base_dir().exists())

    def test_field_validation_failure_returns_validate_result_and_writes_nothing(self) -> None:
        """A field-level validation failure (out-of-order `## Updates` entries) must return
        ``ValidateResult(valid=False, ...)`` and write nothing (feat-204-create-error)."""
        result = create_txt(_BAD_UPDATES_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertTrue(message)
        self.assertIn("txt create_txt (body): ", message)
        self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
        self.assertFalse(txt_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
