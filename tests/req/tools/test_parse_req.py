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

"""Tests for the ``parse_req`` ``@mcp.tool()`` wrapper."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from pydantic import ValidationError

from biz.dfch.specmgr.req.models.v1 import ReqDocument
from biz.dfch.specmgr.req.tools.parse_req import parse_req

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: req-001
    type: req
    status: draft
    ---

    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)

    ## More Information

    This optional section can contain additional information.

    ## Notes

    This optional section can contain additional notes.
    """
)


class TestParseReqTool(unittest.TestCase):
    """Tests for the parse_req tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_req must return the parsed, validated ReqDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_req(str(path))

            self.assertIsInstance(result, ReqDocument)
            self.assertEqual(result.frontmatter.id, "req-001")
            self.assertEqual(result.body.text, "Maximum Engine Temperature")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for every
        `MarkdownParagraph`-backed field (`statement`, `level.value`), not an
        empty object.

        Before `MarkdownParagraph` gained its `text` computed_field, these
        fields serialized to `{}` because `_value` (where the parsed content
        actually lives) is a Pydantic private attribute, invisible to
        `model_dump()`/`model_dump_json()` -- exactly the path an MCP server
        uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_req(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["statement"]["text"],
                "WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.",
            )
            self.assertEqual(body["level"]["value"]["text"], "MUST")

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose --
        not just the heading -- for `Description`/`MoreInformation`/`Notes`,
        the bare leaf `MarkdownSection2`s in `req.models.v1.body` that declare
        no field of their own to hold their content.

        Before `MarkdownSection.text` special-cased the leaf (no declared
        nested fields) branch, these sections' `.text` computed_field always
        extracted only the heading's own inline text (e.g. `"Notes"`),
        because it re-parsed `str(self)` looking for the heading token
        unconditionally. The section's actual prose body was retained
        verbatim in `_value`, but `_value` is a Pydantic private attribute --
        invisible to `model_dump()`/`model_dump_json()`, exactly the path an
        MCP server uses to transmit a tool's return value over the wire -- so
        the body silently never reached the caller.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_req(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["description"]["text"],
                "## Description\n\nIf the engine becomes too hot, the lifetime of the system decreases.\n",
            )
            self.assertEqual(
                body["more_information"]["text"],
                "## More Information\n\nThis optional section can contain additional information.\n",
            )
            self.assertEqual(
                body["notes"]["text"],
                "## Notes\n\nThis optional section can contain additional notes.\n",
            )

    def test_raises_for_invalid_frontmatter(self) -> None:
        """parse_req must let a frontmatter validation failure propagate."""
        text = _VALID_DOC.replace("status: draft", "status: not-a-real-status")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(ValidationError):
                parse_req(str(path))

    def test_raises_for_malformed_structure(self) -> None:
        """parse_req must let a structural parse failure propagate."""
        text = "# Title\n\nJust a paragraph, no recognized requirement sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            with self.assertRaises(AssertionError):
                parse_req(str(path))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_req must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_req("/nonexistent/path/to/file.md")


if __name__ == "__main__":
    unittest.main()
