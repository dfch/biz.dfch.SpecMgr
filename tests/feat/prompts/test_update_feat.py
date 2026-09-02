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

"""Tests for the ``update_feat`` ``@mcp.prompt()`` (Task 4.2, ACC-006).

``update_feat`` (the prompt) only ever returns instructional text -- it
never calls ``get_feat``/``question``/``update``/``set_status`` (the
tools) itself -- so most of these are string-content/ordering assertions
on the narrated text confirming every required step from the feature
README's Design Notes is actually present, in the right order.

Per ACC-006, ``TestUpdateFeatInstructionsWalkthrough`` goes further: it
actually creates a real document via ``create_feat``, then follows exactly
what the packaged update instructions say to do -- reading current state
via ``get_feat``, applying a whole-body change via the generic ``update``
tool (``type="feat"``), applying a line-range change the same way, and
changing status via the generic ``set_status`` tool (``type="feat"``) --
against a real temporary ``SPECMGR_FEAT_DIR``, asserting the end state is
correct. This proves the narration is an actually-followable, correct
sequence, not just plausible text.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.prompts.update_feat import update_feat
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools.create_feat import create_feat as create_feat_tool
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update


class TestUpdateFeatPrompt(unittest.TestCase):
    """Tests for the update_feat prompt."""

    def test_returns_substituted_id(self):
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = update_feat("feat-42-widget")
        self.assertIsInstance(result, str)
        self.assertIn("feat-42-widget", result)
        self.assertNotIn("$id", result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text, and no literal
        $instructions placeholder may remain."""
        result = update_feat("feat-42-widget", instructions="Add REQ-002 to Requirements.")
        self.assertIn("Add REQ-002 to Requirements.", result)
        self.assertNotIn("$instructions", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must be replaced by the literal fallback the packaged
        instructions file itself checks for: '(not given)'."""
        result = update_feat("feat-42-widget")
        self.assertIn("Requested change: (not given)", result)
        self.assertIn('If "Requested change" above says "(not given)"', result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        feat/data/feat_update_instructions.md -- evidence the text comes from packaged data."""
        result = update_feat("feat-42-widget")
        self.assertIn("Never assume prior state", result)

    def test_mentions_get_feat_tool_first(self):
        """The prompt must instruct the LLM to call get_feat first,
        before the generic `update` write call."""
        result = update_feat("feat-42-widget")
        self.assertIn("get_feat(id)", result)
        self.assertLess(result.index("get_feat(id)"), result.index('update(id, type="feat", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="feat") and `set_status`
        (type="feat") call shapes must be named."""
        result = update_feat("feat-42-widget")
        for tool in ('update(id, type="feat", content)', 'set_status(id, type="feat", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_feat(id, raw=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_feat("feat-42-widget")
        self.assertIn("get_feat(id, raw=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="feat", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_feat(id, raw=True)"),
            result.index('update(id, type="feat", content, offset=..., limit=...)'),
        )

    def test_mentions_showing_which_sections_are_present(self):
        """The prompt must instruct showing which sections are already present
        vs. empty, and asking which to add or revise."""
        result = " ".join(update_feat("feat-42-widget").split())
        self.assertIn("are already present with content and which are still absent", result)
        for section in (
            "Overview",
            "Requirements",
            "Acceptance Criteria",
            "Included",
            "Explicitly Out Of Scope",
            "Task List",
            "Current Status",
            "Updates",
            "Dependencies",
            "Depends On",
            "Blocks",
            "Design Notes",
            "Related Decisions",
            "Blockers",
            "Decisions Made",
            "Related PRs / Commits",
            "More Information",
        ):
            self.assertIn(section, result)

    def test_mentions_eliciting_revisions_via_question_tool(self):
        """The prompt must instruct using the question tool to elicit new/revised text."""
        result = update_feat("feat-42-widget")
        self.assertIn("question", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_feat("feat-42-widget")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_feat("feat-42-widget")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_closed_status_set_no_hyphens(self):
        """The four-value, hyphen-free status set must be named explicitly."""
        result = update_feat("feat-42-widget")
        self.assertIn("planning, progress, review, done", result)
        self.assertIn("`in-progress`", result)

    def test_mentions_set_status_as_separate_optional_followup(self):
        """The generic `set_status` tool (type="feat") must be framed as a separate,
        optional follow-up -- do not call it unless the user actually asks."""
        result = update_feat("feat-42-widget")
        self.assertIn("separate, optional", result)
        self.assertIn("do not call", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from feat/data/feat_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "feat_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_feat("feat-42-widget", instructions="Add REQ-002.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_feat("feat-42-widget", instructions="Add REQ-002.")

            self.assertEqual(first, "first feat-42-widget / Add REQ-002.")
            self.assertEqual(second, "second feat-42-widget / Add REQ-002.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_feat("feat-42-widget")


_INITIAL_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z — Paused for review

    Free-form prose describing what happened in this update.
    """
)


class TempFeatDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the feature base dir via SPECMGR_FEAT_DIR."""

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))


class TestUpdateFeatInstructionsWalkthrough(TempFeatDirTestCase):
    """ACC-006: walk the packaged update instructions end to end against a real document.

    Follows feat/data/feat_update_instructions.md literally: step 1 (get_feat(id)),
    step 4's line-range replace and whole-body replace via the generic `update` tool
    (type="feat"), and the separate, optional set_status(type="feat") follow-up --
    against a real temporary SPECMGR_FEAT_DIR, asserting the end state is correct.
    """

    def test_get_then_range_update_then_whole_body_then_set_status(self) -> None:
        """get_feat(id, raw=True) -> update (line-range) -> update (whole-body) ->
        set_status, live, exactly as step 1/4 of the packaged instructions narrate."""
        created = create_feat_tool(_INITIAL_BODY)
        feat_id = created.frontmatter.id
        assert feat_id is not None

        # Step 1: read current state first.
        current = get_feat(feat_id)
        self.assertEqual(current.frontmatter.id, feat_id)

        # Step 4, line-range replace: get_feat(id, raw=True) to find the exact line,
        # then update(id, type="feat", content, offset=..., limit=1).
        raw_lines = get_feat(feat_id, raw=True).splitlines()
        line_number = raw_lines.index("Short description.") + 1
        update(feat_id, "feat", "Updated short description.", offset=line_number, limit=1)

        after_range = get_feat(feat_id, raw=True).splitlines()
        self.assertEqual(after_range[line_number - 1], "Updated short description.")
        self.assertEqual(len(after_range), len(raw_lines))

        # Step 4, whole-body replace: carry forward every section, changing Requirements.
        current_body = get_feat(feat_id, raw=True)
        revised_body = current_body.replace(
            "- REQ-001: The widget must render within 200ms.",
            "- REQ-001: The widget must render within 200ms.\n\n- REQ-002: The widget must be keyboard-navigable.",
        )
        whole_body_result = update(feat_id, "feat", revised_body)
        self.assertEqual(len(whole_body_result.body.plan.requirements.items), 2)
        self.assertEqual(whole_body_result.frontmatter.id, feat_id)
        self.assertEqual(whole_body_result.frontmatter.created, created.frontmatter.created)

        # Step 4, status change: a separate, optional follow-up via the generic
        # set_status tool (never through `update`).
        status_result = set_status(feat_id, "feat", "progress")
        self.assertEqual(status_result.frontmatter.status, "progress")
        self.assertEqual(status_result.frontmatter.id, feat_id)
        # The body carried forward by the whole-body update stays untouched by set_status.
        self.assertEqual(len(status_result.body.plan.requirements.items), 2)

        final = get_feat(feat_id)
        self.assertEqual(final.frontmatter.status, "progress")
        self.assertEqual(len(final.body.plan.requirements.items), 2)


if __name__ == "__main__":
    unittest.main()
