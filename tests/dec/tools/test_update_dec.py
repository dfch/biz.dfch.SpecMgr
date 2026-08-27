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

"""Tests for the ``update_dec`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1 import DecDocument, parse_dec
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, ensure_dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.update_dec import update_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)

_UPDATED_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Drivers

    - Latency under 100 ms at p95.

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

    def existing_dec(self) -> DecDocument:
        """Create and return a real, persisted decision via create_dec."""
        return create_dec(_MINIMAL_BODY)


class TestUpdateDec(TempDecDirTestCase):
    """Tests for the update_dec tool."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """update_dec must replace the body but preserve every frontmatter field but `updated`."""
        original = self.existing_dec()

        result = update_dec(original.frontmatter.id, _UPDATED_BODY)

        self.assertEqual(result.frontmatter.id, original.frontmatter.id)
        self.assertEqual(result.frontmatter.type, original.frontmatter.type)
        self.assertEqual(result.frontmatter.status, original.frontmatter.status)
        self.assertEqual(result.frontmatter.created, original.frontmatter.created)
        self.assertEqual(result.frontmatter.version, original.frontmatter.version)
        self.assertNotEqual(result.frontmatter.updated, original.frontmatter.updated)
        self.assertIsNotNone(result.body.drivers)

    def test_written_file_round_trips_via_parse_dec(self) -> None:
        """The updated file on disk must parse back into the returned document's shape."""
        original = self.existing_dec()

        result = update_dec(original.frontmatter.id, _UPDATED_BODY)

        base_dir = ensure_dec_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        self.assertEqual(len(matching), 1)
        on_disk = parse_dec(matching[0].read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.updated, result.frontmatter.updated)
        self.assertIsNotNone(on_disk.body.drivers)

    def test_raises_not_found_for_unknown_id(self) -> None:
        """update_dec must raise DecNotFoundError for an id with no matching file."""
        with self.assertRaises(DecNotFoundError):
            update_dec("no-such-id", _MINIMAL_BODY)

    def test_invalid_content_raises_and_leaves_file_unchanged(self) -> None:
        """A structurally invalid body must raise AssertionError, leaving the file untouched."""
        original = self.existing_dec()
        base_dir = ensure_dec_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(AssertionError):
            update_dec(original.frontmatter.id, _MALFORMED_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)

    def test_field_validation_failure_raises_and_leaves_file_unchanged(self) -> None:
        """A field-level validation failure (duplicate `### Option 1:` number) must raise, leaving the file untouched."""
        original = self.existing_dec()
        base_dir = ensure_dec_base_dir()
        matching = [p for p in base_dir.glob("*.md") if original.frontmatter.id in p.name]
        before = matching[0].read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            update_dec(original.frontmatter.id, _BAD_OPTION_BODY)

        self.assertEqual(matching[0].read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
