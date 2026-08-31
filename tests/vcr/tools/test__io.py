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

"""Tests for ``vcr.tools._io`` (thin file read helpers)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.vcr.models.v1 import VcrDocument
from biz.dfch.specmgr.vcr.tools._io import load_by_id, read_vcr
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError

_DOC_TEMPLATE = textwrap.dedent(
    """\
    ---
    id: {id}
    type: vcr
    version: 1.0.0
    status: draft
    created: 2026-08-31
    updated: 2026-08-31
    ---

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


def _vcr_text(id_: str) -> str:
    """Render a minimal, valid verification case record document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReadVcr(unittest.TestCase):
    """Tests for read_vcr."""

    def test_reads_and_parses_a_real_file(self) -> None:
        """read_vcr must return a VcrDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_vcr_text("some-id"), encoding="utf-8")

            document = read_vcr(path)

            self.assertIsInstance(document, VcrDocument)
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.body.text, "Sample Verification Case")


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_vcr(self) -> None:
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            expected_path.write_text(_vcr_text("the-id"), encoding="utf-8")

            path, document = load_by_id(base, "the-id")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """load_by_id must raise VcrNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(VcrNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
