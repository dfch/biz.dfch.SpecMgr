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

"""Tests for the ``parse_dec`` ``@mcp.tool()`` wrapper (Task 2.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.models.v1 import DecDocument
from biz.dfch.specmgr.dec.tools.parse_dec import parse_dec
from biz.dfch.specmgr.general.models import ValidateResult
from biz.dfch.specmgr.general.tools.validate import _MAX_VALIDATE_ERROR_CHARS

_VALID_DOC = textwrap.dedent(
    """\
    ---
    id: dec-001
    type: dec
    status: draft
    ---

    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Drivers

    - Latency under 100 ms at p95.

    ## Decision Outcome

    We chose the document store.

    ### Consequences

    Reporting reads from the nightly export.

    ## Roles and Responsibilities

    ### Accountable

    The platform architecture lead.

    ### Responsible

    - The order service team.

    ## Source

    The customer dashboard latency incident review meeting.

    ## More Information

    Harness config in the platform repository.
    """
)


class TestParseDecTool(unittest.TestCase):
    """Tests for the parse_dec tool."""

    def test_returns_parsed_document(self) -> None:
        """parse_dec must return the parsed, validated DecDocument for a valid file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_dec(str(path))

            self.assertIsInstance(result, DecDocument)
            self.assertEqual(result.frontmatter.id, "dec-001")
            self.assertEqual(result.body.text, "Choose a Document Store")

    def test_model_dump_surfaces_markdownparagraph_backed_fields(self) -> None:
        """Regression test: `model_dump()` must surface real content for the
        `MarkdownParagraph`-backed field (`outcome.statement`), not an empty
        object.

        Before `MarkdownParagraph` gained its `text` computed_field, this
        field serialized to `{}` because `_value` (where the parsed content
        actually lives) is a Pydantic private attribute, invisible to
        `model_dump()`/`model_dump_json()` -- exactly the path an MCP server
        uses to transmit a tool's return value over the wire.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_dec(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["outcome"]["statement"]["text"],
                "We chose the document store.",
            )

    def test_model_dump_surfaces_leaf_section_body_content(self) -> None:
        """Regression test: `model_dump()` must surface the full body prose --
        not just the heading -- for `Context`/`MoreInformation`, the bare leaf
        `MarkdownSection2`s in `dec.models.v1.body` that declare no field of
        their own to hold their content.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(_VALID_DOC, encoding="utf-8")

            result = parse_dec(str(path))
            dump = result.model_dump(mode="json")

            body = dump["body"]
            self.assertEqual(
                body["context"]["text"],
                "## Context and Problem Statement\n\nThe current store cannot serve the dashboard read path.\n",
            )
            self.assertEqual(
                body["more_information"]["text"],
                "## More Information\n\nHarness config in the platform repository.\n",
            )

    def test_invalid_frontmatter_returns_validate_result(self) -> None:
        """parse_dec must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        frontmatter validation failure (`implemented` is GOL's, not DEC's;
        feat-204-create-error, Phase 120)."""
        text = _VALID_DOC.replace("status: draft", "status: implemented")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_dec(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("dec parse_dec: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))
            self.assertTrue(message.endswith("... (truncated)"), message)

    def test_malformed_structure_returns_validate_result(self) -> None:
        """parse_dec must return the non-raising ``ValidateResult(valid=False, ...)`` for a
        structural parse failure (feat-204-create-error, Phase 120)."""
        text = "# Title\n\nJust a paragraph, no recognized decision sections.\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_dec(str(path))

            self.assertIsInstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertTrue(message)
            self.assertIn("dec parse_dec: ", message)
            self.assertLessEqual(len(message), _MAX_VALIDATE_ERROR_CHARS + len("... (truncated)"))

    def test_raises_for_nonexistent_file(self) -> None:
        """parse_dec must raise FileNotFoundError for a nonexistent path."""
        with self.assertRaises(FileNotFoundError):
            parse_dec("/nonexistent/path/to/file.md")

    def test_unreadable_file_raises_permission_error(self) -> None:
        """parse_dec must raise PermissionError for an unreadable path -- ``Path.read_text()``
        sits outside the tool's own catch, so the unreadable half of the "truly-absent or
        unreadable path" file-access contract (feat-204-create-error REQ-002/ACC-002) is never
        intercepted by the non-raising ``ValidateResult`` branch (Phase 150)."""
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("permission denied")):
            with self.assertRaises(PermissionError):
                parse_dec("/path/to/file.md")


class TestParseDecToolOutcomeBlocks(unittest.TestCase):
    """The ``parse_dec`` tool with the relaxed ``## Decision Outcome`` lead (feat-247-dec-outcome-blocks, ACC-001/ACC-003)."""

    _DOC_WITH_BLOCKS = textwrap.dedent(
        """\
        ---
        id: dec-001
        type: dec
        status: draft
        ---

        # Choose a Document Store

        ## Context and Problem Statement

        The current store cannot serve the dashboard read path.

        ## Decision Outcome

        We chose the document store because it meets the latency budget.

        The choice carries two sub-decisions.

        - The read path stays synchronous.
        - Writes go through the existing queue.

        ### Consequences

        Reporting reads from the nightly export.

        ## Roles and Responsibilities

        ### Accountable

        The platform architecture lead.

        ### Responsible

        - The order service team.

        ## Source

        The customer dashboard latency incident review meeting.
        """
    )

    def test_returns_parsed_document_with_further_blocks(self) -> None:
        """parse_dec must return the parsed DecDocument for the relaxed shape: `statement` holds
        the lead paragraph, `further_blocks` the remainder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(self._DOC_WITH_BLOCKS, encoding="utf-8")

            result = parse_dec(str(path))

            self.assertIsInstance(result, DecDocument)
            assert isinstance(result, DecDocument)
            outcome = result.body.outcome
            self.assertEqual(outcome.statement.text, "We chose the document store because it meets the latency budget.")
            assert outcome.further_blocks is not None
            self.assertIn("- The read path stays synchronous.", outcome.further_blocks.text)
            assert outcome.consequences is not None
            self.assertIn("nightly export", outcome.consequences.text)

    def test_model_dump_carries_further_blocks_text(self) -> None:
        """`model_dump(mode='json')` on the tool's return value must carry the extra blocks under
        `outcome.further_blocks.text` (REQ-003)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(self._DOC_WITH_BLOCKS, encoding="utf-8")

            result = parse_dec(str(path))
            assert isinstance(result, DecDocument)
            dump = result.model_dump(mode="json")

            self.assertEqual(
                dump["body"]["outcome"]["further_blocks"]["text"],
                "The choice carries two sub-decisions.\n\n- The read path stays synchronous.\n- Writes go through the existing queue.\n",
            )

    def test_rejected_block_in_the_outcome_lead_returns_validate_result(self) -> None:
        """A block quote in the outcome lead is a content-validation failure: the non-raising
        ``ValidateResult`` (feat-204-create-error precedent), never an accepted document."""
        text = self._DOC_WITH_BLOCKS.replace("- Writes go through the existing queue.", "> A quoted block.")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text(text, encoding="utf-8")

            result = parse_dec(str(path))

            self.assertIsInstance(result, ValidateResult)
            assert isinstance(result, ValidateResult)
            self.assertFalse(result.valid)
            self.assertEqual(len(result.errors), 1)
            message = result.errors[0].message
            self.assertIn("dec parse_dec: ", message)
            self.assertIn("text left over", message)


if __name__ == "__main__":
    unittest.main()
