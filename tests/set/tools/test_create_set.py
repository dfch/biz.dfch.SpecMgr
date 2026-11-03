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

"""Tests for the ``create_set`` ``@mcp.tool()`` wrapper (feat-229-set Phase 110)."""

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
from biz.dfch.specmgr.set.models.v1 import SetDocument, SetFrontmatter, parse_set
from biz.dfch.specmgr.set.tools._paths import set_base_dir
from biz.dfch.specmgr.set.tools.create_set import create_set
from biz.dfch.specmgr.set.tools.get_set import get_set

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Ad-hoc review set

    ## Description

    Some prose about what the set bundles and why the items belong together.

    ## Items

    - REQ 00000000-0000-4000-8000-000000000001: Sample Requirement
    """
)

# Structurally valid, but a cross-field failure: the same ``(tag, id)`` pair
# twice -- the `Set` model-validator's `ValidationError` channel.
_BAD_ITEMS_BODY = textwrap.dedent(
    """\
    # Ad-hoc review set

    ## Description

    Some prose about what the set bundles and why the items belong together.

    ## Items

    - REQ 00000000-0000-4000-8000-000000000001: Sample Requirement

    - REQ 00000000-0000-4000-8000-000000000001: The same requirement again
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no Description and no Items section.\n"


class TempSetDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateSet(TempSetDirTestCase):
    """Tests for the create_set tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_set must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_set(_MINIMAL_BODY)

        self.assertIsInstance(result, SetFrontmatter)
        self.assertNotIsInstance(result, SetDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "set")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_set(result.id)
        self.assertEqual(fetched.body.text, "Ad-hoc review set")

    def test_writes_expected_filename(self) -> None:
        """create_set must write f'set-{id}-{slug}.md' under the set base dir."""
        result = create_set(_MINIMAL_BODY)

        expected_path = set_base_dir() / f"set-{result.id}-ad-hoc-review-set.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_set(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_set(_MINIMAL_BODY)

        expected_path = set_base_dir() / f"set-{result.id}-ad-hoc-review-set.md"
        on_disk = parse_set(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Ad-hoc review set")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_set must create the set base directory if it does not exist yet."""
        self.assertFalse(set_base_dir().exists())

        create_set(_MINIMAL_BODY)

        self.assertTrue(set_base_dir().is_dir())

    def test_invalid_content_returns_validate_result_and_writes_nothing(self) -> None:
        """A structurally invalid body must return ``ValidateResult(valid=False, ...)`` and write no
        file at all (feat-204-create-error)."""
        result = create_set(_MALFORMED_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertTrue(message)
        self.assertIn("set create_set (body): ", message)
        self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
        self.assertFalse(set_base_dir().exists())

    def test_field_validation_failure_returns_validate_result_and_writes_nothing(self) -> None:
        """A cross-field validation failure (a duplicate ``(tag, id)`` item) must return
        ``ValidateResult(valid=False, ...)`` and write nothing (feat-204-create-error)."""
        result = create_set(_BAD_ITEMS_BODY)

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertTrue(message)
        self.assertIn("set create_set (body): ", message)
        self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
        self.assertFalse(set_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
