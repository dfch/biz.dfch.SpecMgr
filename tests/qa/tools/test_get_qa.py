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

"""Tests for the ``get_qa`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.qa.models.v2 import QaDocument
from biz.dfch.specmgr.qa.tools import _io
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.qa.tools.get_qa import get_qa

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)

_V1_SHAPED_DOC = textwrap.dedent(
    """\
    ---
    id: v1-shaped-id
    type: qa
    status: draft
    ---

    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Functional Suitability

    ### What must happen?

    > Is this acceptable?

    Yes, it is acceptable.

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)


class TestGetQa(unittest.TestCase):
    """Tests for the get_qa tool."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def test_returns_matching_document(self) -> None:
        """get_qa must return the full QaDocument for a matching id."""
        created = create_qa(_MINIMAL_BODY)

        result = get_qa(created.frontmatter.id)

        self.assertIsInstance(result, QaDocument)
        self.assertEqual(result.frontmatter.id, created.frontmatter.id)
        self.assertEqual(result.body.text, "Some QA Title")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """get_qa must raise QaNotFoundError, with the standardized message, when no document matches."""
        create_qa(_MINIMAL_BODY)

        with self.assertRaises(QaNotFoundError) as ctx:
            get_qa("no-such-id")
        message = str(ctx.exception)
        self.assertIn("bare document UUID", message)
        self.assertIn("without a domain prefix", message)

    def test_read_path_surfaces_structural_error_for_v1_shaped_document(self) -> None:
        """`get_qa`'s own read path (`qa.tools._io.read_qa`, which `load_by_id`
        calls once an id has been resolved to a path) must fail with the same
        structural `AssertionError`/`pydantic.ValidationError` that
        `qa.models.v2.parser.parse_qa`/`Qa.from_text` raise on their own for a
        v1-shaped document -- no version gate, no silent fallback to v1
        parsing (ACC-005, REQ-004 revised 2026-08-23).

        Exercised directly against `_io.read_qa(path)` rather than
        `get_qa(id)` itself: `get_qa` resolves an id to a path by scanning and
        parsing every file under the QA base directory
        (`qa.tools._paths.find_qa_path`), silently skipping any file that
        fails to parse -- a pre-existing, unrelated-to-this-cutover behavior
        (see `test__paths.py`'s own `test_skips_malformed_file_and_still_finds_valid_one`).
        A v1-shaped file therefore can never be *found* by id in the first
        place, so calling `get_qa` with its id surfaces `QaNotFoundError`, not
        the structural parse error -- `read_qa` is the smallest unit that
        demonstrates the actual "no v1 fallback" guarantee.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_V1_SHAPED_DOC, encoding="utf-8")

            with self.assertRaises(AssertionError):
                _io.read_qa(path)


if __name__ == "__main__":
    unittest.main()
