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

"""Tests for the ``review_feat`` ``@mcp.prompt()`` (feat-263-delegation-prompts, Phase 110).

``review_feat`` (the prompt) only ever returns instructional text --
it never calls ``get_feat`` or any git command (the host's tools)
itself -- so these are string-content assertions on the rendered
instructions confirming ACC-002: the ``feat-reviewer.md`` checklist and
report format are mirrored portably -- read the plan in full, resolve
the code diff (the merge-base against dev), apply the full review
checklist (the nine ISO/IEC 25010:2023 product-quality characteristics
plus the feature-plan convention layer and the optional local layer),
report the five sections as TSK-compatible checklist items each with a
file:line citation, and stay report-only (no edits, writes, or
commits) -- INCLUDING the conditional "Proposed Fix Phase" section
(present only with Errors/Gaps/Discrepancies, the ready-to-paste
``### Task List`` block with the NEXT UNUSED phase number, tasks
derived STRICTLY from the report's own
Errors/Gaps/Discrepancies, and the ``[NEEDS DECISION]`` flagging rule).

``TestReviewFeatRegistration`` pins the package surface and the live
``mcp`` registration (the exactly-once precedent of
``tests/feat/prompts/test_refine_feat.py``); the dev-CLI
``specmgr mcp-docs`` regeneration listing the prompt in ``docs/MCP.md``
is the machine evidence for the registered prompt surface (the session
MCP server predates the prompt, per the plan's Operational gotcha 6).
"""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.prompts.review_feat import review_feat
from biz.dfch.specmgr.general.tools import _packaged_data

_ID = "feat-42-review-walk"

#: The nine ISO/IEC 25010:2023 product-quality characteristics the
#: Generic checklist layer names, one bullet each.
_CHARACTERISTICS = (
    "**Functional Suitability**",
    "**Performance Efficiency**",
    "**Compatibility**",
    "**Interaction Capability**",
    "**Reliability**",
    "**Security**",
    "**Maintainability**",
    "**Flexibility**",
    "**Safety**",
)

#: The five report sections, in the fixed order the narration gives.
_REPORT_SECTIONS = (
    "## Errors",
    "## Gaps",
    "## Discrepancies",
    "## Improvements",
    "## Positives",
)


def _one_line(text: str) -> str:
    """Collapse the rendered instructions' hard line breaks to single spaces.

    The packaged markdown is hand-wrapped at word boundaries outside
    inline spans, so a prose phrase (or a tool-call form) may span two
    physical lines; assertions against such phrases run against this
    normalized form.
    """
    result = " ".join(text.split())
    return result


class TestReviewFeatPrompt(unittest.TestCase):
    """Tests for the review_feat prompt's rendered instructions (ACC-002)."""

    def test_returns_substituted_id(self):
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = review_feat(_ID)
        self.assertIsInstance(result, str)
        self.assertIn(_ID, result)
        self.assertNotIn("$id", result)

    def test_id_stripped_before_validation(self):
        """Surrounding whitespace must be stripped, yielding the same rendered text."""
        self.assertEqual(review_feat(f"  {_ID}  "), review_feat(_ID))

    def test_reads_the_plan_in_full(self):
        """Step 1 must read the plan README in full (Plan and Progress, plus history.md if present)."""
        result = review_feat(_ID)
        self.assertIn("## 1. Read the plan in full", result)
        self.assertIn(f"`.specmgr/feat/{_ID}/README.md`", result)
        self.assertIn("plus `history.md` if present", result)

    def test_parse_failure_report_and_stop(self):
        """The unparseable-plan branch: a parse-failure result is reported and stopped, not reviewed."""
        result = _one_line(review_feat(_ID))
        self.assertIn(
            f"If `get_feat({_ID})` returns a parse-failure result (`error`/`path`) "
            "instead of a document, report the error and stop: the plan must be "
            "repaired first (the `/repair` surface), not reviewed.",
            result,
        )

    def test_resolves_the_diff_against_dev(self):
        """Step 2 must resolve the diff via the merge-base against dev (the agent's own instructions)."""
        result = _one_line(review_feat(_ID))
        self.assertIn("`git merge-base dev HEAD`", result)
        self.assertIn("`git diff <base>..HEAD --stat`", result)
        self.assertIn(
            "use the `question` tool to ask for an explicit `base..head` ref range rather than guessing",
            result,
        )

    def test_reads_every_changed_file_in_full(self):
        """Step 3 must read every changed file in full, not just diff hunks."""
        result = review_feat(_ID)
        self.assertIn("Read every changed file in full, not just diff hunks", result)

    def test_checklist_layers_named(self):
        """The three checklist layers (Generic, feature-plan conventions, local) must all be named."""
        result = review_feat(_ID)
        self.assertIn("### Generic (any codebase)", result)
        self.assertIn("### Feature-plan conventions (any specmgr-based repo)", result)
        self.assertIn("### Local repo conventions (if any)", result)

    def test_all_nine_characteristics_named(self):
        """The Generic layer must carry one bullet per ISO/IEC 25010:2023 characteristic."""
        result = review_feat(_ID)
        for characteristic in _CHARACTERISTICS:
            with self.subTest(characteristic=characteristic):
                self.assertIn(characteristic, result)

    def test_feature_plan_convention_items_named(self):
        """The feature-plan layer must name Plan-vs-code drift, Documentation, and Good things."""
        result = review_feat(_ID)
        for item in ("**Plan-vs-code drift**", "**Documentation**", "**Good things**"):
            with self.subTest(item=item):
                self.assertIn(item, result)

    def test_five_report_sections_in_fixed_order(self):
        """The report must carry the five sections in the fixed feat-reviewer order."""
        result = review_feat(_ID)
        positions = [result.index(section) for section in _REPORT_SECTIONS]
        self.assertEqual(positions, sorted(positions), "the report sections drifted from the fixed order")

    def test_items_are_tsk_compatible_checklist_lines(self):
        """Every item is a TSK-compatible checklist line, each citing a concrete path:line reference."""
        result = _one_line(review_feat(_ID))
        self.assertIn("- [ ] E1: <what is wrong and why> (<file>:<line>)", result)
        self.assertIn("TSK-compatible checklist line", result)
        self.assertIn("cite at least one concrete `path:line` reference", result)

    def test_report_only_no_edit_write_or_commit(self):
        """The stance must be report-only: do not edit, write, or commit anything."""
        result = _one_line(review_feat(_ID))
        self.assertIn("Do not edit, write, or commit anything: this review is report-only.", result)
        self.assertIn("The fix itself is a separate task for a phase-implementer, not you.", result)

    def test_conditional_proposed_fix_phase_present_only_with_findings(self):
        """REQ-003: the section is present only when the report has any Errors, Gaps, or Discrepancies."""
        result = _one_line(review_feat(_ID))
        self.assertIn(
            "Present this section only when your report above contains any Errors, Gaps, or Discrepancies",
            result,
        )
        self.assertIn("Improvements and Positives stay advisory", result)

    def test_conditional_proposed_fix_phase_block_shape(self):
        """REQ-003: the ready-to-paste Task List block -- next unused phase number, no renumbering."""
        result = _one_line(review_feat(_ID))
        self.assertIn("`#### Phase NNN: Fix phase (review cycle k)`", result)
        self.assertIn("NEXT UNUSED phase number", result)
        self.assertIn("3-digit numbers, step 10, gap-friendly", result)
        self.assertIn("Never renumber an existing phase", result)

    def test_conditional_proposed_fix_phase_items_derived_strictly(self):
        """REQ-003: one Task item per finding, derived STRICTLY from Errors/Gaps/Discrepancies."""
        result = _one_line(review_feat(_ID))
        self.assertIn("`- [ ] Task NNN.MMM`", result)
        self.assertIn(
            "derived STRICTLY from the report's own Errors, Gaps, and Discrepancies",
            result,
        )
        self.assertIn("task numbers start at 100 within the fix phase, step 10", result)

    def test_needs_decision_flagging_rule(self):
        """REQ-003: any item needing a user decision is flagged [NEEDS DECISION], not guessed at."""
        result = _one_line(review_feat(_ID))
        self.assertIn(
            "is explicitly flagged `[NEEDS DECISION]` in its text rather than guessed at",
            result,
        )

    def test_raises_value_error_for_blank_id(self):
        """A blank/whitespace-only id must fail fast with ValueError."""
        with self.assertRaises(ValueError) as ctx:
            review_feat("   ")
        self.assertIn("blank", str(ctx.exception))

    def test_raises_value_error_for_malformed_id(self):
        """A non-feat-NNN-slug id (bare number, uppercase, UUID) must fail fast with ValueError."""
        for bad in ("feat-36", "FEAT-36-DELETE", "11111111-2222-3333-4444-555555555555", "feat-36-delete/../x"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    review_feat(bad)
                self.assertIn("feat-NNN-slug", str(ctx.exception))

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from feat/data/feat_review_instructions.md, not an
        inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "feat_review_instructions.md"
            instructions_path.write_text("first $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = review_feat(_ID)
                instructions_path.write_text("second $id", encoding="utf-8")
                second = review_feat(_ID)

            self.assertEqual(first, f"first {_ID}")
            self.assertEqual(second, f"second {_ID}")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    review_feat(_ID)


class TestReviewFeatRegistration(unittest.TestCase):
    """The ``feat.prompts`` package exposes ``review_feat``, and the live ``mcp`` registration carries it."""

    def test_exposed_in_package_all(self):
        """Importing feat.prompts must expose review_feat in __all__."""
        import biz.dfch.specmgr.feat.prompts as feat_prompts

        self.assertIn("review_feat", feat_prompts.__all__)
        self.assertIs(feat_prompts.review_feat, review_feat)

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._prompts = asyncio.run(mcp.list_prompts())

    def test_review_feat_registered_on_mcp_server(self):
        """The live mcp application must register the review_feat prompt exactly once."""
        matching = [p for p in self._prompts if p.name == "review_feat"]
        self.assertEqual(len(matching), 1)


if __name__ == "__main__":
    unittest.main()
