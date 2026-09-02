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

"""Tests for the ``get_sop`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.sop.models.v1 import SopDocument
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.sop.tools.get_sop import get_sop


#: A well-formed but non-existent canonical UUID (feat-38-39-41-43-44 Phase 4: the id
#: must be well-formed to reach the domain's own not-found error past the new
#: ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"
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


class TestGetSop(unittest.TestCase):
    """Tests for the get_sop tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_sop must return the full SopDocument for a matching id."""
        created = create_sop(_MINIMAL_BODY)

        result = get_sop(created.frontmatter.id)

        self.assertIsInstance(result, SopDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "New Employee IT Account Provisioning")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_sop must raise SopNotFoundError, with the standardized message, when no SOP matches."""
        create_sop(_MINIMAL_BODY)

        with self.assertRaises(SopNotFoundError) as ctx:
            get_sop(_MISSING_UUID)
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)

    def _doc_path(self) -> Path:
        """The single on-disk document file seeded for this test."""
        matches = list((self.docs_root / "sop").glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def test_raw_returns_body_text_via_shared_helper(self) -> None:
        """raw=True must return the frontmatter-stripped body text, byte-identical to the shared body_text helper's output."""
        created = create_sop(_MINIMAL_BODY)

        result = get_sop(created.frontmatter.id, raw=True)

        self.assertIsInstance(result, str)
        self.assertEqual(result, body_text(self._doc_path()))

    def test_raw_line_coordinates_index_into_the_splice_target(self) -> None:
        """The line numbers from a raw read must index byte-for-byte into the text the update splice targets (ACC-003)."""
        created = create_sop(_MINIMAL_BODY)
        lines = get_sop(created.frontmatter.id, raw=True).splitlines()
        k = lines.index("Provision accounts for new hires.") + 1
        replacement = "Provision accounts for all new hires."

        update(id=created.frontmatter.id, type="sop", content=replacement, begin=k, end=k)

        new_lines = get_sop(created.frontmatter.id, raw=True).splitlines()
        self.assertEqual(new_lines[k - 1], replacement)
        self.assertEqual(new_lines[: k - 1] + new_lines[k:], lines[: k - 1] + lines[k:])
        self.assertEqual(len(new_lines), len(lines))

    def test_raw_false_returns_parsed_document_as_before(self) -> None:
        """raw=False (explicit) must return the parsed document, exactly as the default call does."""
        created = create_sop(_MINIMAL_BODY)

        result = get_sop(created.frontmatter.id, raw=False)
        default = get_sop(created.frontmatter.id)

        self.assertIsInstance(result, SopDocument)
        self.assertEqual(result, default)

    def test_raw_unknown_id_raises_not_found_in_both_modes(self) -> None:
        """raw=True and raw=False must both raise SopNotFoundError for an unknown id."""
        create_sop(_MINIMAL_BODY)

        with self.assertRaises(SopNotFoundError):
            get_sop(_MISSING_UUID, raw=True)
        with self.assertRaises(SopNotFoundError):
            get_sop(_MISSING_UUID, raw=False)


if __name__ == "__main__":
    unittest.main()
