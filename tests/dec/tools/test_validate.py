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

"""Tests for the generic ``validate`` tool (``type="dec"``) with the relaxed ``## Decision Outcome`` lead (feat-247-dec-outcome-blocks, ACC-001/ACC-004/ACC-009).

Pins the dry-run validator's behavior over the relaxed shape: a body whose
outcome lead carries further blocks (a second paragraph and a bullet list
after the mandatory lead paragraph) validates as body-only (``full=False``,
the default) and as a complete document (``full=True``), a rejected kind
inside the lead (a block quote) validates as invalid with the engine's
actionable "text left over" message, and a lead-only body (no further
blocks) stays valid exactly as before the feature (the REQ-004 parity).
"""

from __future__ import annotations

import textwrap
import unittest

from biz.dfch.specmgr.general.tools.validate import validate

_FRONTMATTER = textwrap.dedent(
    """\
    ---
    id: dec-001
    type: dec
    status: draft
    ---

    """
)

_BODY_WITH_BLOCKS = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store because it meets the latency budget.

    The choice carries two sub-decisions.

    - The read path stays synchronous.
    - Writes go through the existing queue.

    ## Roles and Responsibilities

    ### Accountable

    The platform architecture lead.

    ### Responsible

    - The order service team.

    ## Source

    The customer dashboard latency incident review meeting.
    """
)

#: `_BODY_WITH_BLOCKS` with the two further blocks removed, leaving the
#: lead-only outcome (the pre-feature shape).
_BODY_LEAD_ONLY = _BODY_WITH_BLOCKS.replace(
    "The choice carries two sub-decisions.\n\n- The read path stays synchronous.\n- Writes go through the existing queue.\n\n",
    "",
)


class TestValidateDecOutcomeBlocks(unittest.TestCase):
    """The generic ``validate`` tool (``type="dec"``) over the relaxed outcome lead shape."""

    def test_body_only_relaxed_shape_is_valid(self) -> None:
        """ACC-001: the body-only dry run (``full=False``, the default) accepts the further blocks."""
        result = validate(type="dec", content=_BODY_WITH_BLOCKS)

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, [])

    def test_full_document_relaxed_shape_is_valid(self) -> None:
        """ACC-001: the complete-document dry run (``full=True``) accepts the further blocks."""
        result = validate(type="dec", content=_FRONTMATTER + _BODY_WITH_BLOCKS, full=True)

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, [])

    def test_block_quote_in_the_outcome_lead_is_invalid(self) -> None:
        """ACC-009: a block quote inside the outcome lead is invalid, with the engine's actionable
        "text left over" message (capped, non-raising)."""
        content = _BODY_WITH_BLOCKS.replace("- Writes go through the existing queue.", "> A quoted block.")

        result = validate(type="dec", content=content)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("text left over", result.errors[0].message)

    def test_lead_only_shape_stays_valid(self) -> None:
        """ACC-004 (REQ-004 parity): a lead-only outcome (no further blocks) validates exactly as
        before the feature."""
        result = validate(type="dec", content=_BODY_LEAD_ONLY)

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
