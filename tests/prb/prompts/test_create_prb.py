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

"""Tests for the ``create_prb`` ``@mcp.prompt()`` (Task 3.14; feat-132-prb-update
Phase 2, ACC-002/ACC-003/ACC-004/ACC-006).

``create_prb`` (the prompt) only ever returns instructional text -- it never
calls ``TodoWrite``/``question``/``list_prb``/``get_qa``/``create_prb`` (the
tool) itself -- so these are string-content/ordering assertions on the
narrated text confirming every required step from the feature README's
Design Notes is actually present, in the right order, rather than
behavioral tests of a live agent run.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.prb.prompts.create_prb import create_prb


class TestCreatePrbPrompt(unittest.TestCase):
    """Tests for the create_prb prompt."""

    def test_mentions_topic(self):
        """The topic argument must be interpolated into the returned text."""
        result = create_prb("Widget registry migration rollback failures")
        self.assertIn("Widget registry migration rollback failures", result)

    def test_mentions_qa_id_when_given(self):
        """A given qa_id must be interpolated into the returned text verbatim."""
        result = create_prb("Some topic", qa_id="11111111-1111-1111-1111-111111111111")
        self.assertIn("11111111-1111-1111-1111-111111111111", result)

    def test_qa_id_fallback_when_absent(self):
        """Absent qa_id must fall back to a standalone-mode explanation, not a blank/None."""
        result = create_prb("Some topic")
        self.assertIn("(not given -- proceed standalone, asking all 7 5W2H questions)", result)

    def test_mentions_get_qa_and_bad_id_handling(self):
        """The prompt must instruct fetching the linked QA via get_qa, with explicit
        QaNotFoundError handling that surfaces the failure and offers a standalone-or-
        corrected-id choice via the question tool (REQ-004) -- never a silent fallback."""
        result = create_prb("Some topic")
        self.assertIn("get_qa(qa_id)", result)
        self.assertIn("QaNotFoundError", result)
        self.assertIn("tell the user the lookup failed", result)
        self.assertIn("retry with a corrected QA id", result)
        self.assertIn("Never silently fall through", result)

    def test_mentions_scanning_every_qa_category(self):
        """The prompt must instruct scanning all 10 QA categories (Elicitation Context
        plus the 9 ISO/IEC 25010:2023 characteristics), not only Elicitation Context."""
        result = create_prb("Some topic")
        self.assertIn("Elicitation Context", result)
        for characteristic in (
            "Functional Suitability",
            "Performance Efficiency",
            "Compatibility",
            "Interaction Capability",
            "Reliability",
            "Security",
            "Maintainability",
            "Flexibility",
            "Safety",
        ):
            self.assertIn(characteristic, result)
        self.assertIn("not only `Elicitation Context`", result)

    def test_mentions_one_pair_to_one_question_rule(self):
        """The prompt must state the one-pair-to-one-question matching rule and the
        non-committal-counts-as-unanswered rule (REQ-003) -- citing QA's own
        `TODO: answer pending` placeholder (feat-156 REQ-009), which replaced the
        retired legacy awaiting-response placeholder (feat-156 ACC-006)."""
        result = create_prb("Some topic")
        self.assertIn("at most one", result)
        self.assertIn("duplicated across two sub-questions", result)
        self.assertIn("Non-committal counts as unanswered", result)
        self.assertIn("TODO: answer pending", result)

    def test_one_pair_to_one_question_rule_has_a_worked_example(self):
        """REQ-014/ACC-010: the one-pair-to-one-question rule must include a worked
        example of a QA pair that could plausibly answer two of the 7 5W2H
        sub-questions, and how "best match only" resolves the tie-break."""
        result = create_prb("Some topic")
        self.assertIn("Worked example:", result)
        self.assertIn("When does the checkout page time out?", result)
        self.assertIn("During peak traffic hours, right at the payment confirmation", result)
        self.assertIn("Best match only:", result)
        self.assertIn('since the QA question literally asks "when"', result)

    def test_mentions_asking_only_remaining_questions(self):
        """The prompt must instruct asking only whichever 5W2H questions were not
        pre-filled from the linked QA, or all 7 if standalone (REQ-005)."""
        result = create_prb("Some topic")
        self.assertIn("only whichever of the 7 5W2H answers were", result)
        self.assertIn("pre-filled in step 2", result)

    def test_mentions_derive_then_confirm_lead_sentence(self):
        """The prompt must instruct deriving the lead sentence's 4 blanks from
        pre-filled What/Who/Why answers and confirming (not re-asking) them in
        QA-linked mode, versus eliciting all 4 fresh in standalone mode (REQ-006)."""
        result = create_prb("Some topic")
        self.assertIn("QA-linked mode", result)
        self.assertIn("[Current state]", result)
        self.assertIn("[specific issue]", result)
        self.assertIn("[stakeholder]", result)
        self.assertIn("[underlying cause]", result)
        self.assertIn("`What` -> both `[Current state]` and `[specific issue]`", result)
        self.assertIn("`Who` -> `[stakeholder]`", result)
        self.assertIn("`Why` -> `[underlying cause]`", result)
        self.assertIn("Standalone mode", result)
        self.assertIn("elicit all 4", result)
        self.assertIn("never ask all 4 blanks as fresh", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_prb tool first."""
        result = create_prb("Some topic")
        self.assertIn("list_prb", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a TodoWrite list covering Summary + 7
        questions + Gap + Impact + Future State."""
        result = create_prb("Some topic")
        self.assertIn("todo list", result)
        self.assertIn("Summary", result)
        self.assertIn("Gap", result)
        self.assertIn("Impact", result)
        self.assertIn("Future State", result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit answers."""
        result = create_prb("Some topic")
        self.assertIn("question", result)

    def test_mentions_all_seven_5w2h_questions(self):
        """All 7 fixed 5W2H question headings must be named verbatim."""
        result = create_prb("Some topic")
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

    def test_mentions_allowing_skip(self):
        """The prompt must explicitly allow the user to skip any of the 7 questions."""
        result = create_prb("Some topic")
        self.assertIn("skip", result)

    def test_mentions_synthesizing_summary(self):
        """The prompt must instruct synthesizing a Summary from whichever answers were given."""
        result = create_prb("Some topic")
        self.assertIn("Synthesize", result)

    def test_mentions_drafting_and_confirming_gap(self):
        """The prompt must instruct drafting a Gap statement and confirming it via the question tool."""
        result = create_prb("Some topic")
        self.assertIn("Draft", result)
        self.assertIn("confirm", result)

    def test_mentions_no_root_cause_section(self):
        """The prompt must not narrate a `## Root Cause` heading as part of the structure
        recap -- deliberately excluded by design, though the prompt is allowed to explain
        the exclusion in prose (which does mention "Root Cause" by name, quoted as a
        code span, never as its own heading line). Per REQ-009, the rationale text now
        acknowledges the mandatory lead sentence carries the best-known cause by design,
        rather than claiming the problem statement stays "free of assumed causes"."""
        result = create_prb("Some topic")
        heading_lines = [line for line in result.splitlines() if line.strip() == "## Root Cause"]
        self.assertEqual(heading_lines, [])
        self.assertIn("No `## Root Cause` section exists; the lead sentence carries the", result)
        self.assertIn("best-known cause by design", result)
        self.assertIn("formal root-cause analysis remains a separate, later activity", result.lower())
        self.assertNotIn("free of assumed causes", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_prb("Some topic")
        self.assertIn("specmgr://prb/template", result)
        self.assertIn("specmgr://prb/example", result)
        self.assertIn("specmgr://prb/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_prb tool, the template/example
        resources, specmgr://prb/schema, and create_prb, in that order,
        matching the intended sequence."""
        result = create_prb("Some topic")
        markers = [
            "list_prb",
            "specmgr://prb/template",
            "specmgr://prb/schema",
            "create_prb(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_update_prb_for_later_revisions(self):
        """The prompt must point at the update_prb prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_prb("Some topic")
        self.assertIn("`update_prb` prompt", result)
        self.assertIn('update(id, type="prb", content)', result)
        self.assertIn('set_status(id, type="prb", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from prb/data/prb_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "prb_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_prb("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_prb("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_prb("Some topic")


if __name__ == "__main__":
    unittest.main()
