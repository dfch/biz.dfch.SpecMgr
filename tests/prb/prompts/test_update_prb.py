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

"""Tests for the ``update_prb`` ``@mcp.prompt()`` (Task 3.15; feat-132-prb-update
Phase 2, ACC-007).

``update_prb`` (the prompt) only ever returns instructional text -- it never
calls ``get_prb``/``question``/``update``/``set_status`` (the tools) itself
-- so these are string-content/ordering assertions on the narrated text
confirming every required step from the feature README's Design Notes is
actually present, in the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.prb.prompts.update_prb import update_prb


class TestUpdatePrbPrompt(unittest.TestCase):
    """Tests for the update_prb prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_prb("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_prb_tool_first(self):
        """The prompt must instruct the LLM to call get_prb first,
        before the generic `update` write call."""
        result = update_prb("abc-123")
        self.assertIn("get_prb(id)", result)
        self.assertLess(result.index("get_prb(id)"), result.index('update(id, type="prb", content)'))

    def test_mentions_old_shape_recovery_via_host_file_repair(self):
        """The prompt must carry the present-tense recovery directive: a
        get_prb(id) parse failure whose error names the `problem_statement`
        field (the body missing the mandatory lead sentence under the H1, or
        the first paragraph not matching the template) leads to repairing the
        file with the host's own file-read/file-write tools (no specmgr read
        returns the body of a document that fails to parse, and the generic
        update/edit tools cannot repair one), leaving the frontmatter
        byte-unchanged, a full-text validate(full=True) dry-run before the
        write-back, and a confirming get_prb(id) call before proceeding with
        the requested change, in that order (file-read < insert < replace <
        validate < file-write < confirming get_prb(id)). Both trigger cases are
        covered: a missing lead paragraph gets the sentence inserted under the
        H1, and a non-template first paragraph is derive input for the 4 blanks
        and, after a `question`-tool check whether its uncaptured content moves
        to `## More Information`, is replaced by the sentence (never kept as a
        second paragraph). The frontmatter rule follows the second case bullet
        after a blank line, indented as a paragraph of sub-step 3, so CommonMark
        renders it for both cases, not as a lazy continuation of that bullet. The
        negative assertions run on the recovery-block slice only: the rest of
        the prompt legitimately keeps `update(id, type="prb", content)` and
        `get_prb(id, raw=True, numbered=True)`. The slice ends at the
        `## 2. If no change was specified` heading line itself, not at the
        block's own backticked reference to it."""
        result = update_prb("abc-123")
        start = result.index("**Old-shape recovery.**")
        end = result.index("\n## 2. If no change was specified")
        self.assertLess(result.index("get_prb(id)"), start)
        self.assertLess(start, end)
        block = result[start:end]
        self.assertIn("If `get_prb(id)` returns a parse failure", block)
        self.assertIn("missing the mandatory lead sentence", block)
        self.assertIn("problem_statement", block)
        self.assertIn("No specmgr read returns the body of a document that fails to parse", block)
        self.assertIn("read the raw file with the host's own file-read tool at", block)
        self.assertIn("the `path` the parse-failure result carries", block)
        self.assertIn("In both cases, leave the frontmatter block byte-for-byte unchanged", block)
        # A blank line, then a 3-space indent: a paragraph of sub-step 3, outside both nested case bullets.
        self.assertIn(
            "before the sub-step 4 `validate` dry-run.\n\n   In both cases, leave the frontmatter block byte-for-byte",
            block,
        )
        self.assertIn("`updated` included: a repair is", block)
        self.assertIn("file-write tool -- the generic `update`/`edit` tools re-parse the", block)
        self.assertIn("cannot repair one", block)
        self.assertIn("Confirm the repair with a real `get_prb(id)` call -- it must parse", block)
        self.assertIn("which bumps `updated`", block)
        # The two-case wording is asserted wrap-independently on the whitespace-normalized slice.
        flat = " ".join(block.split())
        self.assertIn(
            "If the first paragraph under the H1 does not match the template, read that existing paragraph "
            "as well: it is derive input for the same 4 blanks.",
            flat,
        )
        self.assertIn("- If the lead paragraph is missing: Insert the confirmed sentence", flat)
        self.assertIn(
            "- If the first paragraph under the H1 does not match the template: First use the `question` tool "
            "to ask whether content of the existing paragraph that the confirmed sentence does not capture "
            "moves to the PRB's `## More Information` section (confirm the exact heading with "
            "`get_prb_schema` or `get_prb_template` first). Then replace that paragraph with the confirmed "
            "sentence. Do not add the sentence as a second paragraph above it. On a yes to that question, append "
            "that content under `## More Information`, adding the heading as the last section of the body (after "
            "`## References`) if the PRB has none, in the same raw-file edit and before the sub-step 4 `validate` "
            "dry-run.",
            flat,
        )
        validate_call = 'validate(type="prb", content=<the full raw file text>, full=True)'
        self.assertIn(validate_call, block)
        file_read = block.index("read the raw file with the host's own file-read tool at")
        insert = block.index("Insert the confirmed sentence as its own paragraph directly under the")
        validate = block.index(validate_call)
        replace = block.index("replace that paragraph with the confirmed sentence")
        move = block.index("append that content under `## More Information`")
        file_write = block.index("file-write tool -- the generic `update`/`edit` tools re-parse the")
        confirm = block.index("Confirm the repair with a real `get_prb(id)` call -- it must parse")
        self.assertLess(file_read, insert)
        self.assertLess(insert, replace)
        self.assertLess(replace, move)
        self.assertLess(move, validate)
        self.assertLess(validate, file_write)
        self.assertLess(file_write, confirm)
        self.assertNotIn("get_prb(id, raw=True)", block)
        self.assertNotIn('update(id, type="prb", content)', block)

    def test_mentions_deriving_or_eliciting_lead_sentence_blanks(self):
        """The recovery flow must instruct deriving/confirming (or eliciting)
        the lead sentence's 4 blanks, mirroring create_prb's own flow (REQ-006)."""
        result = update_prb("abc-123")
        self.assertIn("create_prb", result)
        self.assertIn("derive-then-confirm", result)
        self.assertIn("`What` -> both `[Current state]` and", result)
        self.assertIn("`Who` -> `[stakeholder]`", result)
        self.assertIn("`Why` ->", result)
        self.assertIn("[underlying cause]", result)

    def test_mentions_inserting_sentence_under_h1_then_proceeding(self):
        """The recovery flow must instruct inserting the composed sentence
        directly under the H1, then proceeding with the originally requested
        change once the document parses again."""
        result = update_prb("abc-123")
        self.assertIn("Insert the confirmed sentence as its own paragraph directly under the", result)
        self.assertIn("H1 title", result)
        self.assertIn("proceeding to `## 2. If no change was specified`", result)
        self.assertIn("below with the originally requested change", result)

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="prb") and `set_status`
        (type="prb") call shapes must be named."""
        result = update_prb("abc-123")
        for tool in ('update(id, type="prb", content)', 'set_status(id, type="prb", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_prb(id, raw=True, numbered=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_prb("abc-123")
        self.assertIn("get_prb(id, raw=True, numbered=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="prb", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_prb(id, raw=True, numbered=True)"),
            result.index('update(id, type="prb", content, offset=..., limit=...)'),
        )

    def test_mentions_showing_which_questions_are_answered(self):
        """The prompt must instruct showing which of the 7 questions are already answered."""
        result = update_prb("abc-123")
        self.assertIn("already have answers", result)
        for heading in (
            "What Is the Problem?",
            "Why Is It a Problem?",
            "Where Is the Problem Observed?",
            "Who Is Impacted?",
            "When Was the Problem First Observed?",
            "How Is the Problem Observed?",
            "How Often Is the Problem Observed?",
        ):
            self.assertIn(heading, result)

    def test_mentions_full_resynthesis_not_append(self):
        """The prompt must call out that Summary regeneration is a full re-synthesis, not an append."""
        result = update_prb("abc-123")
        self.assertIn("full re-synthesis", result)
        self.assertIn("not an append", result)

    def test_mentions_redrafting_and_confirming_gap(self):
        """The prompt must instruct re-drafting Gap and confirming it via the question tool."""
        result = update_prb("abc-123")
        self.assertIn("Re-draft", result)
        self.assertIn("confirm", result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_prb("abc-123", instructions="Add a new Impact statement.")
        self.assertIn("Add a new Impact statement.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_prb("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_prb("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_prb("abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_set_status_as_separate_optional_followup(self):
        """The generic `set_status` tool (type="prb") must be framed as a
        separate, optional follow-up."""
        result = update_prb("abc-123")
        self.assertIn("separate, optional", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from prb/data/prb_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "prb_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_prb("abc-123", instructions="Add a new Impact statement.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_prb("abc-123", instructions="Add a new Impact statement.")

            self.assertEqual(first, "first abc-123 / Add a new Impact statement.")
            self.assertEqual(second, "second abc-123 / Add a new Impact statement.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_prb("abc-123")


if __name__ == "__main__":
    unittest.main()
