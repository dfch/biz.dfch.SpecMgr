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

"""Tests for the ``create_feat`` ``@mcp.prompt()`` (Task 4.2, ACC-006).

``create_feat`` (the prompt) only ever returns instructional text -- it
never calls ``TodoWrite``/``question``/``list_feat``/``create_feat`` (the
tool) itself -- so most of these are string-content/ordering assertions on
the narrated text confirming every required step from the feature README's
Design Notes is actually present, in the right order, rather than
behavioral tests of a live agent run.

Per ACC-006, ``TestCreateFeatInstructionsWalkthrough`` goes further: it
actually drives the real ``create_feat``/``get_feat``/``list_feat`` tools
against a temporary ``SPECMGR_FEAT_DIR``, following exactly the sequence
the packaged instructions narrate (dedup-check via ``list_feat``, then
``create_feat(content)``), to prove the narrated sequence is not just
plausible text but an actually-followable, correct one.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.prompts.create_feat import create_feat
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools.create_feat import create_feat as create_feat_tool
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.general.tools import _packaged_data


class TestCreateFeatPrompt(unittest.TestCase):
    """Tests for the create_feat prompt."""

    def test_returns_substituted_instruction_text(self):
        """A distinctive topic must be interpolated, and no literal $topic placeholder may remain."""
        result = create_feat("Distinctive topic XYZ-42")
        self.assertIsInstance(result, str)
        self.assertIn("Distinctive topic XYZ-42", result)
        self.assertNotIn("$topic", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        feat/data/feat_create_instructions.md -- evidence the text comes from packaged data."""
        result = create_feat("Some topic")
        self.assertIn("Follow this structure and tool sequence exactly.", result)

    def test_mentions_duplicate_check_tool(self):
        """The prompt must instruct the LLM to check the list_feat tool first."""
        result = create_feat("Some topic")
        self.assertIn("list_feat", result)

    def test_mentions_todowrite_list(self):
        """The prompt must instruct building a todo list covering the mandatory
        sections and each optional section."""
        result = create_feat("Some topic")
        self.assertIn("todo list", result)
        for section in (
            "Overview",
            "Requirements",
            "Acceptance Criteria",
            "Scope",
            "Included",
            "Explicitly Out Of Scope",
            "Task List",
            "Current Status",
            "Updates",
            "Dependencies",
            "Design Notes",
            "Related Decisions",
            "Blockers",
            "Decisions Made",
            "Related PRs / Commits",
            "More Information",
        ):
            self.assertIn(section, result)

    def test_mentions_question_tool(self):
        """The prompt must instruct using the question tool to elicit information."""
        result = create_feat("Some topic")
        self.assertIn("question", result)

    def test_mentions_allowing_skip_for_optional_sections(self):
        """The prompt must explicitly allow the user to skip any optional field."""
        result = create_feat("Some topic")
        self.assertIn("skip", result)

    def test_mentions_starting_point_resources(self):
        """The prompt must point at the template/example/schema resources."""
        result = create_feat("Some topic")
        self.assertIn("specmgr://feat/template", result)
        self.assertIn("specmgr://feat/example", result)
        self.assertIn("specmgr://feat/schema", result)

    def test_mentions_tool_sequence_in_order(self):
        """The prompt must mention the list_feat tool, the template/example
        resources, specmgr://feat/schema, and create_feat, in that order,
        matching the intended sequence."""
        result = create_feat("Some topic")
        markers = [
            "list_feat",
            "specmgr://feat/template",
            "specmgr://feat/schema",
            "create_feat(content)",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_mentions_no_frontmatter_to_draft(self):
        """The prompt must clarify that create_feat builds the entire frontmatter
        automatically -- the caller only ever supplies body markdown."""
        result = " ".join(create_feat("Some topic").split())
        self.assertIn("There is no frontmatter for you to draft", result)
        self.assertIn('`status="planning"` always', result)

    def test_mentions_update_feat_for_later_revisions(self):
        """The prompt must point at the update_feat prompt for later changes,
        with the generic update/set_status tools as the direct alternative."""
        result = create_feat("Some topic")
        self.assertIn("`update_feat`", result)
        self.assertIn('update(id, type="feat", content)', result)
        self.assertIn('set_status(id, type="feat", status)', result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from feat/data/feat_create_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "feat_create_instructions.md"
            instructions_path.write_text("first $topic", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = create_feat("Some topic")
                instructions_path.write_text("second $topic", encoding="utf-8")
                second = create_feat("Some topic")

            self.assertEqual(first, "first Some topic")
            self.assertEqual(second, "second Some topic")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    create_feat("Some topic")


_WALKTHROUGH_BODY = textwrap.dedent(
    """\
    # Feature: Widget Renderer

    ## Plan

    ### Overview

    Renders widgets quickly.

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


class TestCreateFeatInstructionsWalkthrough(TempFeatDirTestCase):
    """ACC-006: walk the packaged create instructions end to end against a real document.

    Follows step 0 (dedup check via list_feat) and step 4 (call create_feat(content))
    of feat/data/feat_create_instructions.md literally, against a real temporary
    SPECMGR_FEAT_DIR, proving the narrated sequence actually works, not just reads
    plausibly.
    """

    def test_dedup_check_then_create_produces_a_real_document(self) -> None:
        """list_feat (empty) -> create_feat(content) -> list_feat (1), per step 0/4."""
        # Step 0: check for an existing feature on this topic first.
        before = list_feat()
        self.assertEqual(before.total, 0)

        # Step 4: assemble body markdown (no frontmatter block) and call create_feat.
        created = create_feat_tool(_WALKTHROUGH_BODY)
        self.assertEqual(created.frontmatter.status, "planning")
        self.assertEqual(created.frontmatter.id, "feat-1-widget-renderer")

        # A second dedup check now finds the just-created document.
        after = list_feat()
        self.assertEqual(after.total, 1)
        self.assertEqual(after.results[0].title, "Widget Renderer")


if __name__ == "__main__":
    unittest.main()
