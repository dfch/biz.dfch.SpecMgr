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

"""Tests for the ``create_dec`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1 import DecFrontmatter, parse_dec
from biz.dfch.specmgr.dec.tools._paths import dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)

# Structurally valid, but a field/cross-field failure: two `### Option 1:`
# headings are duplicate option numbers (the `Decision` after-validator's
# `ValidationError` channel).
_BAD_OPTION_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.

    ## Pros and Cons

    ### Option 1: Document Store

    Meets the latency budget.

    ### Option 1: Key-Value Store

    Even faster reads.
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized decision sections.\n"


class TempDecDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateDec(TempDecDirTestCase):
    """Tests for the create_dec tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_dec must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_dec(_MINIMAL_BODY)

        self.assertIsInstance(result, DecFrontmatter)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "dec")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_dec(result.id)
        self.assertEqual(fetched.body.text, "Choose a Document Store")

    def test_writes_expected_filename(self) -> None:
        """create_dec must write f'dec-{id}-{slug}.md' under the decision base dir."""
        result = create_dec(_MINIMAL_BODY)

        expected_path = dec_base_dir() / f"dec-{result.id}-choose-a-document-store.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_dec(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_dec(_MINIMAL_BODY)

        expected_path = dec_base_dir() / f"dec-{result.id}-choose-a-document-store.md"
        on_disk = parse_dec(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Choose a Document Store")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_dec must create the decision base directory if it does not exist yet."""
        self.assertFalse(dec_base_dir().exists())

        create_dec(_MINIMAL_BODY)

        self.assertTrue(dec_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_dec(_MALFORMED_BODY)

        self.assertFalse(dec_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (duplicate `### Option 1:` number) must raise, writing nothing."""
        with self.assertRaises(ValidationError):
            create_dec(_BAD_OPTION_BODY)

        self.assertFalse(dec_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
