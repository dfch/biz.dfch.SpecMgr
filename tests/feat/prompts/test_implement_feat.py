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

"""Tests for the ``implement_feat`` ``@mcp.prompt()`` (feat-263-delegation-prompts, Phase 110).

``implement_feat`` (the prompt) only ever returns instructional text --
it never calls ``get_feat``/``question``/``set_status`` (the tools)
itself -- so these are string-content assertions on the rendered
instructions confirming ACC-001: the orchestrator discipline is named
(read the plan in full, a phase-by-phase ``TodoWrite`` list, each phase
delegated to a fresh subagent, the result independently verified BEFORE
advancing -- re-run the phase's quality gate, inspect the diff, confirm
the phase's acceptance criteria -- and never write or edit code files
yourself, delegate all implementation), the optional-delegation naming
is the DEC's own verbatim phrase ("your host's task-delegation tool, if
one exists", never assumed present), the explicit fallback to direct
single-session implementation is stated, the delegation-pattern DEC is
named by UUID, and the capped review-fix loop is described (the
``[NEEDS DECISION]`` resolution via ``question``, the
implementer-appends-the-fix-phase delegation step, the 3-cycle cap, and
the ``done`` closeout only after a clean loop exit).

``TestImplementFeatRegistration`` pins the package surface and the live
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

from biz.dfch.specmgr.feat.prompts.implement_feat import implement_feat
from biz.dfch.specmgr.general.tools import _packaged_data

_ID = "feat-42-implement-walk"
_DEC_UUID = "4481b1fd-26e5-46bc-8f1b-236b638385b2"


def _one_line(text: str) -> str:
    """Collapse the rendered instructions' hard line breaks to single spaces.

    The packaged markdown is hand-wrapped at word boundaries outside
    inline spans, so a prose phrase (or a tool-call form) may span two
    physical lines; assertions against such phrases run against this
    normalized form.
    """
    result = " ".join(text.split())
    return result


class TestImplementFeatPrompt(unittest.TestCase):
    """Tests for the implement_feat prompt's rendered instructions (ACC-001)."""

    def test_returns_substituted_id(self):
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = implement_feat(_ID)
        self.assertIsInstance(result, str)
        self.assertIn(_ID, result)
        self.assertNotIn("$id", result)

    def test_id_stripped_before_validation(self):
        """Surrounding whitespace must be stripped, yielding the same rendered text."""
        self.assertEqual(implement_feat(f"  {_ID}  "), implement_feat(_ID))

    def test_optional_delegation_naming_is_the_dec_phrase(self):
        """The DEC's verbatim optional-delegation phrase must appear, and be never assumed present."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("your host's task-delegation tool, if one exists", result)
        self.assertIn("never assumed present", result)

    def test_names_the_delegation_dec_by_uuid(self):
        """The Phase 100 DEC must be named by its UUID (its Decision Outcome's own phrasing governs)."""
        result = implement_feat(_ID)
        self.assertIn(_DEC_UUID, result)

    def test_reads_the_plan_in_full(self):
        """Step 1 must read the plan in full over get_feat (the parsed document + the raw body)."""
        result = implement_feat(_ID)
        self.assertIn("## 1. Read the plan in full", result)
        self.assertIn(f"`get_feat({_ID})`", result)
        self.assertIn(f"`get_feat({_ID}, raw=True)`", result)

    def test_parse_failure_report_and_stop(self):
        """The unparseable-plan branch: a parse-failure result is reported and stopped, not implemented."""
        result = _one_line(implement_feat(_ID))
        self.assertIn(
            f"If `get_feat({_ID})` returns a parse-failure result (`error`/`path`) "
            "instead of a document, report the error and stop: the plan must be "
            "repaired first (the `/repair` surface), not implemented.",
            result,
        )

    def test_builds_a_phase_by_phase_todo_list(self):
        """The orchestrator must build a phase-by-phase TodoWrite list in dependency order."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("phase-by-phase `TodoWrite` list", result)
        self.assertIn("one entry per phase of the plan's Task List, in dependency order", result)

    def test_delegates_each_phase_to_a_fresh_subagent(self):
        """Each phase must be delegated to a fresh subagent via the optional delegation tool."""
        result = _one_line(implement_feat(_ID))
        self.assertIn(
            "Delegate the phase to a fresh subagent via your host's task-delegation tool, if one exists", result
        )

    def test_verify_before_advancing(self):
        """The result must be independently verified BEFORE advancing: gate, diff, acceptance criteria."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("independently verify its result BEFORE advancing", result)
        self.assertIn("re-run the phase's quality gate", result)
        self.assertIn("inspect the diff", result)
        self.assertIn("confirm the phase's acceptance criteria", result)
        self.assertIn('Never take "tests pass" on trust -- run them.', result)

    def test_never_writes_code_itself(self):
        """The orchestrator discipline: never write or edit code files yourself -- delegate all implementation."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("Never write or edit code files yourself -- delegate all implementation.", result)

    def test_explicit_fallback_sentence(self):
        """ACC-001: the explicit fallback to direct single-session implementation, never a hard failure."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("fall back to direct single-session implementation, phase by phase", result)
        self.assertIn("This is never a hard failure", result)

    def test_review_fix_loop_named(self):
        """REQ-004: the capped review-fix loop after the final verification phase must be described."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("the feature is then at `review`, not yet `done`", result)
        self.assertIn("no Errors, Gaps, or Discrepancies", result)
        self.assertIn("resolve any `[NEEDS DECISION]` items with the user via the `question` tool first", result)
        self.assertIn("append the reviewer's ready-to-paste block to the plan's Task List", result)
        self.assertIn("capped at 3 review-fix cycles", result)
        self.assertIn("handed to the user instead of auto-fixed again", result)
        self.assertIn("the `done` closeout happens only after a clean loop exit", result)

    def test_done_only_after_clean_exit(self):
        """The report step must keep the feature at review until the loop exits clean."""
        result = _one_line(implement_feat(_ID))
        self.assertIn("Stop at `review` until the loop exits clean", result)
        self.assertIn("do not set `done` early", result)

    def test_raises_value_error_for_blank_id(self):
        """A blank/whitespace-only id must fail fast with ValueError."""
        with self.assertRaises(ValueError) as ctx:
            implement_feat("   ")
        self.assertIn("blank", str(ctx.exception))

    def test_raises_value_error_for_malformed_id(self):
        """A non-feat-NNN-slug id (bare number, uppercase, UUID) must fail fast with ValueError."""
        for bad in ("feat-36", "FEAT-36-DELETE", "11111111-2222-3333-4444-555555555555", "feat-36-delete/../x"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    implement_feat(bad)
                self.assertIn("feat-NNN-slug", str(ctx.exception))

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from feat/data/feat_implement_instructions.md, not an
        inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "feat_implement_instructions.md"
            instructions_path.write_text("first $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = implement_feat(_ID)
                instructions_path.write_text("second $id", encoding="utf-8")
                second = implement_feat(_ID)

            self.assertEqual(first, f"first {_ID}")
            self.assertEqual(second, f"second {_ID}")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    implement_feat(_ID)


class TestImplementFeatRegistration(unittest.TestCase):
    """The ``feat.prompts`` package exposes ``implement_feat``, and the live ``mcp`` registration carries it."""

    def test_exposed_in_package_all(self):
        """Importing feat.prompts must expose implement_feat in __all__."""
        import biz.dfch.specmgr.feat.prompts as feat_prompts

        self.assertIn("implement_feat", feat_prompts.__all__)
        self.assertIs(feat_prompts.implement_feat, implement_feat)

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._prompts = asyncio.run(mcp.list_prompts())

    def test_implement_feat_registered_on_mcp_server(self):
        """The live mcp application must register the implement_feat prompt exactly once."""
        matching = [p for p in self._prompts if p.name == "implement_feat"]
        self.assertEqual(len(matching), 1)


if __name__ == "__main__":
    unittest.main()
