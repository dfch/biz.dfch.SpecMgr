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

"""Tests for the ``refine_feat`` ``@mcp.prompt()`` (feat-167-mcp-lifecycle-commands-2, Phase 100).

``refine_feat`` (the prompt) only ever returns instructional text -- it
never calls ``get_feat``/``question``/``update``/``validate`` (the
tools) itself -- so most of these are string-content assertions on the
rendered instructions confirming ACC-001: the MCP-native
read/apply/re-check path is named -- ``get_feat(id, raw=True)`` (with
``raw=True, numbered=True`` as the only source of the edit coordinates),
the generic ``update`` tool with ``type="feat"`` (line-range replace
preferred over whole-body), and ``validate`` with ``type="feat"`` and
``full=True`` -- the ``question`` tool is named for user decisions, and
the host file tools appear only as the fallback for hosts without the
specmgr tools.

``TestRefineFeatInstructionsWalkthrough`` goes further: it creates a
small fixture plan in a temporary ``SPECMGR_FEAT_DIR`` seeded with two
deliberate plan-readiness defects (an untestable ACC and a task that
depends on a phase listed after it), then drives
``get_feat(id, raw=True)`` -> ``get_feat(id, raw=True, numbered=True)``
-> ``update(type="feat", ...)`` (line-range, twice, re-reading between
edits) -> ``validate(type="feat", content, full=True)`` exactly as the
packaged instructions narrate, proving the narrated sequence is not just
plausible text but an actually-followable, correct one. The ACC-002
manual smoke test (``/plan-feature`` against a fixture plan) is the live
agent-side counterpart of this walkthrough.
"""

from __future__ import annotations

import asyncio
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.prompts.refine_feat import refine_feat
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.feat.models.v1 import FeatDocument, FeatFrontmatter
from biz.dfch.specmgr.feat.tools.create_feat import create_feat as create_feat_tool
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.general.models import UpdateResult
from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.general.tools.validate import validate

_ID = "feat-42-widget-plan"


def _one_line(text: str) -> str:
    """Collapse the rendered instructions' hard line breaks to single spaces.

    The packaged markdown is hand-wrapped at word boundaries outside
    inline spans, so a prose phrase (or a tool-call form) may span two
    physical lines; assertions against such phrases run against this
    normalized form.
    """
    result = " ".join(text.split())
    return result


class TestRefineFeatPrompt(unittest.TestCase):
    """Tests for the refine_feat prompt's rendered instructions (ACC-001)."""

    def test_returns_substituted_id(self):
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = refine_feat(_ID)
        self.assertIsInstance(result, str)
        self.assertIn(_ID, result)
        self.assertNotIn("$id", result)

    def test_id_stripped_before_validation(self):
        """Surrounding whitespace must be stripped, yielding the same rendered text."""
        self.assertEqual(refine_feat(f"  {_ID}  "), refine_feat(_ID))

    def test_names_get_feat_raw_true(self):
        """The read path must name get_feat with raw=True (and numbered=True for coordinates)."""
        result = refine_feat(_ID)
        self.assertIn(f"`get_feat({_ID})`", result)
        self.assertIn(f"`get_feat({_ID}, raw=True)`", result)
        self.assertIn(f"`get_feat({_ID}, raw=True, numbered=True)`", _one_line(result))

    def test_parse_failure_report_and_stop(self):
        """The unparseable-plan branch (cycle-4 G1): a parse-failure result is reported and stopped, not refined."""
        result = _one_line(refine_feat(_ID))
        self.assertIn(
            f"If `get_feat({_ID})` returns a parse-failure result (`error`/`path`) instead of a "
            "document, report the error and stop: the plan must be repaired first (the `/repair` "
            "surface), not refined.",
            result,
        )

    def test_update_line_range_preferred(self):
        """The apply path must name the generic update tool with type="feat", line-range preferred."""
        result = _one_line(refine_feat(_ID))
        self.assertIn(
            f'`update({_ID}, type="feat", content=<the replacement lines>, '
            "offset=<the first body line>, limit=<the number of lines>)`",
            result,
        )
        self.assertIn("A **line-range replace** is the preferred form", result)
        self.assertIn("unchanged regions of the plan stay byte-identical", result)

    def test_whole_body_replace_only_as_escape_hatch(self):
        """The whole-body form must be named only for a fix spanning most of the document."""
        result = _one_line(refine_feat(_ID))
        self.assertIn(
            "whole-body replace** (`update(" + _ID + ', type="feat", '
            "content=<the full replacement body>)` with no `offset`/`limit`) only "
            "when a single fix spans most of the document",
            result,
        )

    def test_coordinates_never_from_a_raw_file_read(self):
        """Coordinates must come only from the numbered read, never from a raw file read."""
        result = _one_line(refine_feat(_ID))
        self.assertIn("Get the edit coordinates only from a", result)
        self.assertIn(f"Never from a raw file read of `.specmgr/feat/{_ID}/README.md`", result)
        self.assertIn("a raw file's line numbers are never body-line coordinates", result)

    def test_re_read_between_edits(self):
        """The stale-coordinate rule (re-read after each update) must be stated."""
        result = _one_line(refine_feat(_ID))
        self.assertIn("re-read with `get_feat(" + _ID + ", raw=True, numbered=True)` before the next edit", result)
        self.assertIn("every line number you had before is stale", result)

    def test_never_renumber_phases_or_tasks(self):
        """The no-renumbering rule (permanent numbers, gap-friendly insertions) must be stated."""
        result = refine_feat(_ID)
        self.assertIn("Never renumber an existing phase or task", result)
        self.assertIn("once assigned a number is permanent", result)

    def test_names_validate_full_true(self):
        """The re-check path must name validate with type="feat" and full=True, over the full text."""
        result = _one_line(refine_feat(_ID))
        self.assertIn('validate(type="feat", content=<the full document text>, full=True)', result)
        self.assertIn("each taken verbatim from a fresh parsed `get_feat(" + _ID + ")` read", result)
        self.assertIn(
            "followed by a blank line and the current body from a fresh `get_feat(" + _ID + ", raw=True)` read", result
        )

    def test_names_question_tool_for_user_decisions(self):
        """The question tool must be named for user decisions, and guessing must be ruled out."""
        result = _one_line(refine_feat(_ID))
        self.assertIn("use the `question` tool whenever a finding needs a user decision", result)
        self.assertIn("do not guess at design decisions the plan leaves open", result)
        self.assertIn("apply only what the user approves", result)

    def test_checklist_areas_named(self):
        """The four readiness checklist areas of REQ-001 must all be named."""
        result = refine_feat(_ID)
        for area in (
            "**Testable acceptance criteria**",
            "**Phase ordering and dependencies**",
            "**Scope clarity**",
            "**Unresolved decisions**",
        ):
            with self.subTest(area=area):
                self.assertIn(area, result)

    def test_host_file_tools_only_in_the_fallback_section(self):
        """Host file tools must appear only in the fallback section, for hosts without the specmgr tools."""
        result = refine_feat(_ID)
        fallback_heading = "## Fallback: hosts without the specmgr tools"
        self.assertIn(fallback_heading, result)
        main_part = _one_line(result[: result.index(fallback_heading)])
        fallback_part = _one_line(result[result.index(fallback_heading) :])
        self.assertNotIn("your host's own file", main_part)
        self.assertIn("your host's own file-read tool", fallback_part)
        self.assertIn("your host's own file `edit`/`write` tools", fallback_part)

    def test_status_and_id_left_untouched(self):
        """A readiness review must not change the plan's status or id."""
        result = _one_line(refine_feat(_ID))
        self.assertIn("Do not change the plan's `status` or `id`", result)
        self.assertIn("`set_status` tool's and the `set_feat_id` tool's jobs", result)

    def test_never_commits(self):
        """The report step must say: do not commit, touch no file but the plan's README."""
        result = _one_line(refine_feat(_ID))
        self.assertIn("Do not commit, and do not touch any file other than the plan's own README", result)

    def test_raises_value_error_for_blank_id(self):
        """A blank/whitespace-only id must fail fast with ValueError."""
        with self.assertRaises(ValueError) as ctx:
            refine_feat("   ")
        self.assertIn("blank", str(ctx.exception))

    def test_raises_value_error_for_malformed_id(self):
        """A non-feat-NNN-slug id (bare number, uppercase, UUID) must fail fast with ValueError."""
        for bad in ("feat-36", "FEAT-36-DELETE", "11111111-2222-3333-4444-555555555555", "feat-36-delete/../x"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    refine_feat(bad)
                self.assertIn("feat-NNN-slug", str(ctx.exception))

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from feat/data/feat_refine_instructions.md, not an
        inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "feat_refine_instructions.md"
            instructions_path.write_text("first $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = refine_feat(_ID)
                instructions_path.write_text("second $id", encoding="utf-8")
                second = refine_feat(_ID)

            self.assertEqual(first, f"first {_ID}")
            self.assertEqual(second, f"second {_ID}")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    refine_feat(_ID)


class TestRefineFeatRegistration(unittest.TestCase):
    """The ``feat.prompts`` package exposes ``refine_feat``, and the live ``mcp`` registration carries it."""

    def test_exposed_in_package_all(self):
        """Importing feat.prompts must expose refine_feat in __all__."""
        import biz.dfch.specmgr.feat.prompts as feat_prompts

        self.assertIn("refine_feat", feat_prompts.__all__)
        self.assertIs(feat_prompts.refine_feat, refine_feat)

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._prompts = asyncio.run(mcp.list_prompts())

    def test_refine_feat_registered_on_mcp_server(self):
        """The live mcp application must register the refine_feat prompt exactly once."""
        matching = [p for p in self._prompts if p.name == "refine_feat"]
        self.assertEqual(len(matching), 1)


# A fixture plan seeded with two deliberate plan-readiness defects:
# (1) an untestable ACC ("in good shape and ready"), and (2) a task that
# depends on a phase listed after it (Phase 120, which does not exist).
_WALKTHROUGH_BODY = textwrap.dedent(
    """\
    # Feature: Plan Readiness Walkthrough

    ## Plan

    ### Overview

    A minimal plan seeded with two deliberate plan-readiness defects.

    ### Requirements

    - REQ-001: The plan must be ready to implement.

    ### Acceptance Criteria

    - [ ] ACC-001: The plan is in good shape and ready.

    ### Scope

    #### Included

    - The plan itself.

    #### Explicitly Out Of Scope

    - Implementation code.

    ### Task List

    #### Phase 100: Build

    - [ ] Task 100.100: Build the feature.

    #### Phase 110: Integrate

    - [ ] Task 110.100: Integrate the feature once Phase 120 has delivered its output.

    ## Progress

    ### Current Status

    **As of 2026-08-30**: Draft, awaiting implementation.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Created

    Seeded the walkthrough fixture with two plan-readiness defects.
    """
)

_DEFECT_ACC_LINE = "- [ ] ACC-001: The plan is in good shape and ready."
_FIXED_ACC_LINE = (
    "- [ ] ACC-001: Every Phase in the Task List carries at least one Task, "
    "and no Task depends on a Phase listed after it."
)
_DEFECT_TASK_LINE = "- [ ] Task 110.100: Integrate the feature once Phase 120 has delivered its output."
_FIXED_TASK_LINE = "- [ ] Task 110.100: Integrate the feature once Phase 100 has delivered its output."


def _line_number(numbered_text: str, line_text: str) -> int:
    """The 1-based body-line number of ``line_text`` in a ``numbered=True`` read.

    The numbered form prefixes every line with ``"<n>: "``; the match is on
    the stripped line text, exactly how step 4 of the packaged instructions
    says to read the coordinates.
    """
    for line in numbered_text.splitlines():
        number, _, rest = line.partition(": ")
        if rest == line_text:
            return int(number)
    raise AssertionError(f"line {line_text!r} not found in the numbered read")


def _full_document_text(frontmatter: FeatFrontmatter) -> str:
    """Assemble the ``validate(full=True)`` content per step 5 of the packaged instructions.

    A YAML frontmatter block -- the fields taken verbatim from the parsed
    read's frontmatter, each single-quoted where it carries ``:`` --
    followed by a blank line; the current body (a fresh ``raw=True`` read)
    is appended by the caller.
    """
    lines = ["---", f"id: {frontmatter.id}", f"type: {frontmatter.type}", f"status: {frontmatter.status}"]
    if frontmatter.classification is not None:
        lines.append(f"classification: '{frontmatter.classification}'")
    lines.extend(
        [
            f"created: '{frontmatter.created}'",
            f"updated: '{frontmatter.updated}'",
            f"version: {frontmatter.version}",
            "---",
            "",
        ]
    )
    result: str = "\n".join(lines)
    return result


class TempFeatDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the feature base dir via SPECMGR_FEAT_DIR."""

    def setUp(self) -> None:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_root = tmp / "feat"
        self.enterContext(mock.patch.dict("os.environ", {FEAT_DIR_ENV_VAR: str(self.feat_root)}))


class TestRefineFeatInstructionsWalkthrough(TempFeatDirTestCase):
    """ACC-002 (test-file half): walk the packaged refine instructions end to end against a real document.

    Follows feat/data/feat_refine_instructions.md literally: step 1
    (``get_feat(id)`` parsed + ``get_feat(id, raw=True)``), step 4 (two
    line-range ``update`` calls with ``type="feat"``, coordinates from the
    ``numbered=True`` read, a re-read between edits), and step 5
    (``validate(type="feat", content, full=True)`` over the assembled full
    text) -- against a real temporary ``SPECMGR_FEAT_DIR``, proving the
    narrated sequence actually works, not just reads plausibly.
    """

    def test_read_assess_apply_recheck_walkthrough(self) -> None:
        """Seeded defects -> line-range updates -> validate(full=True) green, per steps 1/4/5."""
        created = create_feat_tool(_WALKTHROUGH_BODY)
        feat_id = created.id
        assert feat_id is not None
        self.assertEqual(feat_id, "feat-0-plan-readiness-walkthrough")

        # Step 1: read the plan (parsed for the frontmatter, raw for the body).
        document = get_feat(feat_id)
        assert isinstance(document, FeatDocument)
        self.assertEqual(document.frontmatter.id, feat_id)
        raw = get_feat(feat_id, raw=True)
        assert isinstance(raw, str)
        self.assertIn(_DEFECT_ACC_LINE, raw)
        self.assertIn(_DEFECT_TASK_LINE, raw)

        # Step 4, edit 1 (the untestable ACC): coordinates from the numbered read only.
        numbered = get_feat(feat_id, raw=True, numbered=True)
        assert isinstance(numbered, str)
        update(
            feat_id,
            "feat",
            _FIXED_ACC_LINE,
            offset=_line_number(numbered, _DEFECT_ACC_LINE),
            limit=1,
        )

        # Step 4 discipline: re-read before the next edit -- earlier numbers are stale.
        numbered = get_feat(feat_id, raw=True, numbered=True)
        assert isinstance(numbered, str)
        self.assertIn(_FIXED_ACC_LINE, numbered)
        result = update(
            feat_id,
            "feat",
            _FIXED_TASK_LINE,
            offset=_line_number(numbered, _DEFECT_TASK_LINE),
            limit=1,
        )
        self.assertIsInstance(result, UpdateResult)
        self.assertIsNotNone(result.snippet)

        # Step 5: re-check -- frontmatter from a fresh parsed read, body from a fresh raw read.
        final_document = get_feat(feat_id)
        assert isinstance(final_document, FeatDocument)
        final_raw = get_feat(feat_id, raw=True)
        assert isinstance(final_raw, str)
        full_text = _full_document_text(final_document.frontmatter) + final_raw
        validation = validate("feat", full_text, full=True)
        self.assertTrue(validation.valid, validation.errors)

        # The fixes are in, the seeded defects are gone, and the plan still parses.
        self.assertIn(_FIXED_ACC_LINE, final_raw)
        self.assertIn(_FIXED_TASK_LINE, final_raw)
        self.assertNotIn("in good shape and ready", final_raw)
        self.assertNotIn("Phase 120 has delivered", final_raw)
        self.assertEqual(final_document.frontmatter.id, feat_id)


if __name__ == "__main__":
    unittest.main()
