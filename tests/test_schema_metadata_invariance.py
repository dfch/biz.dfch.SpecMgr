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

"""feat-189 Phase 120 (C13/C14): parse-behavior invariance for the emitted schema metadata.

Every closed set this phase emits as ``json_schema_extra`` metadata (``enum``/
``pattern``) must parse exactly as before the metadata change: every accept
fixture below still parses and yields the same value, and every reject
fixture still raises the same exception type with the same message. The
metadata is inert by construction (``json_schema_extra`` only -- never
``Literal``/``Field(pattern=...)``, no new validator, no type change), and
these tests pin that invariance against the domain's own parse entry points
(``from_text``/frontmatter construction, the same paths every ``parse_<d>``
tool runs).

Pinned reject messages follow ``tests/models/md/test_validation_error_baseline.py``'s own
precedent: the full, project-owned ``str()`` for ``AssertionError``; the
stable project-owned message part for ``pydantic.ValidationError`` (the
pydantic-version-coupled URL footer is not pinned). The pinned strings were
captured from the pre-metadata tree (2026-10-18, clean worktree at the Phase
120 start) by running these identical fixtures, and the post-metadata run
reproduced them byte-for-byte.

Placement: a single central file (rather than one per domain) because the
status-enum matrix is uniform across all 12 domains and the body-level sets
are pinned against the same pre-captured baseline; mirrors
``tests/test_schema_surface_registration.py``'s central placement for the
Phase 105 schema-surface tests.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.dec.models.v1.frontmatter import DecFrontmatter
from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_STATUSES
from biz.dfch.specmgr.feat.models.v1.frontmatter import FeatFrontmatter
from biz.dfch.specmgr.feat.models.v1.frontmatter import _ALLOWED_STATUSES as _FEAT_STATUSES
from biz.dfch.specmgr.gol.models.v1.frontmatter import GolFrontmatter
from biz.dfch.specmgr.gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_STATUSES
from biz.dfch.specmgr.prb.models.v1.body import Prb
from biz.dfch.specmgr.prb.models.v1.body import Question1
from biz.dfch.specmgr.prb.models.v1.body import Question7
from biz.dfch.specmgr.prb.models.v1.frontmatter import PrbFrontmatter
from biz.dfch.specmgr.prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_STATUSES
from biz.dfch.specmgr.qa.models.v2.frontmatter import QaFrontmatter
from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_STATUSES
from biz.dfch.specmgr.qa.models.v2.question_answer import QaQuestionAnswer
from biz.dfch.specmgr.req.models.v1.body import Level as ReqLevel
from biz.dfch.specmgr.req.models.v1.frontmatter import ReqFrontmatter
from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_STATUSES
from biz.dfch.specmgr.rsk.models.v1.assessment import Impact as RskImpact
from biz.dfch.specmgr.rsk.models.v1.assessment import Probability as RskProbability
from biz.dfch.specmgr.rsk.models.v1.body import Strategy as RskStrategy
from biz.dfch.specmgr.rsk.models.v1.frontmatter import RskFrontmatter
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_STATUSES
from biz.dfch.specmgr.sop.models.v1.frontmatter import SopFrontmatter
from biz.dfch.specmgr.sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_STATUSES
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import SysrsFrontmatter
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import _ALLOWED_STATUSES as _SYSRS_STATUSES
from biz.dfch.specmgr.tsk.models.v1.body import Task
from biz.dfch.specmgr.tsk.models.v1.body import UpdateEntry as TskUpdateEntry
from biz.dfch.specmgr.tsk.models.v1.body import _UPDATE_ENTRY_ALIAS_PATTERN
from biz.dfch.specmgr.tsk.models.v1.frontmatter import TskFrontmatter
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_STATUSES
from biz.dfch.specmgr.uc.models.v2.frontmatter import UcFrontmatter
from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_STATUSES
from biz.dfch.specmgr.vcr.models.v1.body import AcceptanceCriterion
from biz.dfch.specmgr.vcr.models.v1.body import Coverage as VcrCoverage
from biz.dfch.specmgr.vcr.models.v1.body import _AC_ALIAS_PATTERN
from biz.dfch.specmgr.vcr.models.v1.frontmatter import VcrFrontmatter
from biz.dfch.specmgr.vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_STATUSES

#: (domain, frontmatter class, the domain's own closed status set) -- every
#: whole-body domain, in the same order ``general/tools/_domains.py`` lists
#: them.
_STATUS_MATRIX = [
    ("req", ReqFrontmatter, _REQ_STATUSES),
    ("uc", UcFrontmatter, _UC_STATUSES),
    ("tsk", TskFrontmatter, _TSK_STATUSES),
    ("qa", QaFrontmatter, _QA_STATUSES),
    ("prb", PrbFrontmatter, _PRB_STATUSES),
    ("gol", GolFrontmatter, _GOL_STATUSES),
    ("rsk", RskFrontmatter, _RSK_STATUSES),
    ("dec", DecFrontmatter, _DEC_STATUSES),
    ("sop", SopFrontmatter, _SOP_STATUSES),
    ("feat", FeatFrontmatter, _FEAT_STATUSES),
    ("vcr", VcrFrontmatter, _VCR_STATUSES),
    ("sysrs", SysrsFrontmatter, _SYSRS_STATUSES),
]

#: A status value that is outside every domain's own closed set.
_INVALID_STATUS = "in-review"

_TSK_CHECKBOX_RECENT_UPDATES = "## Recent Updates\n### 2026-08-19 05:42:00.000+02:00 - Kickoff\nKicked off."

_PRB_ACCEPT_BODY = """# Problem

The old manual process is causing constant rework, for the engineering team because it is error-prone.

## Current State

### Summary

The current state is as documented.

## Gap

Actual does not match expected.

## Future State

The process is automated.
"""


class TestStatusEnumInvariance(unittest.TestCase):
    """The 12 frontmatter `status` closed sets parse identically after the `enum` metadata."""

    def test_every_allowed_status_still_parses(self) -> None:
        for domain, cls, allowed in _STATUS_MATRIX:
            for status in sorted(allowed):
                with self.subTest(domain=domain, status=status):
                    sut = cls(status=status)
                    self.assertEqual(sut.status, status)

    def test_default_status_unchanged(self) -> None:
        for domain, cls, allowed in _STATUS_MATRIX:
            with self.subTest(domain=domain):
                sut = cls()
                expected = "open" if domain == "rsk" else "planning" if domain == "feat" else "draft"
                self.assertEqual(sut.status, expected)
                self.assertIn(expected, allowed)

    def test_unknown_status_still_rejected_with_same_message(self) -> None:
        for domain, cls, allowed in _STATUS_MATRIX:
            with self.subTest(domain=domain):
                with self.assertRaises(ValidationError) as ctx:
                    cls(status=_INVALID_STATUS)
                self.assertIn(
                    f"status must be one of {sorted(allowed)}, got '{_INVALID_STATUS}'",
                    str(ctx.exception),
                )


class TestReqLevelInvariance(unittest.TestCase):
    """The req `## Level` RFC 2119 closed set parses identically after the `enum` metadata."""

    def test_every_allowed_level_still_parses(self) -> None:
        for word in ["MUST", "SHOULD", "MUST NOT", "SHOULD NOT", "MAY"]:
            with self.subTest(level=word):
                sut = ReqLevel.from_text(format_text(f"## Level\n\n{word}\n"))
                self.assertEqual(sut.value.text, word)

    def test_unknown_level_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            ReqLevel.from_text(format_text("## Level\n\nNEVER\n"))
        self.assertIn(
            "value must match pattern '^(MUST|SHOULD|MUST NOT|SHOULD NOT|MAY)$', got 'NEVER'",
            str(ctx.exception),
        )


class TestTskCheckboxInvariance(unittest.TestCase):
    """The tsk checkbox-marker constraint parses identically after the `pattern` metadata."""

    def test_space_x_and_X_markers_still_parse(self) -> None:
        text = (
            f"# Task List\n\n- [ ] First task\n- [x] Second task\n- [X] Third task\n\n{_TSK_CHECKBOX_RECENT_UPDATES}\n"
        )

        sut = Task.from_text(format_text(text))

        self.assertEqual([item.checked for item in sut.items], [False, True, True])
        self.assertEqual([item.description for item in sut.items], ["First task", "Second task", "Third task"])

    def test_bad_marker_character_still_rejected_with_same_message(self) -> None:
        text = f"# Task List\n\n- [z] Bad checkbox\n\n{_TSK_CHECKBOX_RECENT_UPDATES}\n"

        with self.assertRaises(ValidationError) as ctx:
            Task.from_text(format_text(text))

        self.assertIn(
            "Task > TaskItem (line 2): expected a '- [ ]'/'- [x]' checkbox marker, got '[z] Bad checkbox'",
            str(ctx.exception),
        )

    def test_missing_marker_still_rejected_with_same_message(self) -> None:
        text = f"# Task List\n\n- foo no marker at all\n\n{_TSK_CHECKBOX_RECENT_UPDATES}\n"

        with self.assertRaises(ValidationError) as ctx:
            Task.from_text(format_text(text))

        self.assertIn(
            "Task > TaskItem (line 2): expected a '- [ ]'/'- [x]' checkbox marker, got 'foo no marker at all'",
            str(ctx.exception),
        )


class TestTskUpdateEntryHeadingInvariance(unittest.TestCase):
    """The tsk `### {timestamp} ( - | : ) {title}` heading constraint parses identically
    after the `pattern` metadata."""

    def test_hyphen_colon_and_T_separator_headings_still_parse(self) -> None:
        for heading in [
            "### 2026-08-19 05:42:00.000+02:00 - Kickoff",
            "### 2026-08-19T05:42:00.000Z : Kickoff",
            "### 2026-08-19T05:42:00.000+02:00 - Kickoff",
        ]:
            with self.subTest(heading=heading):
                sut = TskUpdateEntry.from_text(format_text(f"{heading}\nKicked off.\n"))
                self.assertEqual(sut.title, "Kickoff")

    def test_date_only_heading_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            TskUpdateEntry.from_text(format_text("### 2026-08-19 - Kickoff\nKicked off.\n"))
        # The message interpolates the class's own alias pattern via `repr()`
        # (`models.md.alias_match.describe_alias`), so the pattern part of the
        # expected string is derived from the domain's own constant (backslashes
        # doubled by the `repr`); the literal pin covers the message's own
        # wording and the observed heading.
        expected = (
            "UpdateEntry (line 1): expected heading matching regex "
            f"{_UPDATE_ENTRY_ALIAS_PATTERN!r}, got heading '2026-08-19 - Kickoff'"
        )
        self.assertEqual(str(ctx.exception), expected)


class TestQaQuestionPrefixInvariance(unittest.TestCase):
    """The qa question-number prefix constraint parses identically after the `pattern` metadata."""

    def test_valid_prefixes_still_parse(self) -> None:
        for question in ["> **0.0010**: What is the expected load?", "> **1.0010**: When does it run?"]:
            with self.subTest(question=question):
                sut = QaQuestionAnswer.from_text(format_text(f"{question}\n\nTODO: answer pending\n"))
                self.assertEqual(sut.question.text, question[2:])

    def test_missing_prefix_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            QaQuestionAnswer.from_text(format_text("> What is the expected load?\n\nTODO: answer pending\n"))
        self.assertIn(
            "question must start with the bold question-number prefix '**<d>.<NNNN>**: '",
            str(ctx.exception),
        )
        self.assertIn("got 'What is the expected load?'", str(ctx.exception))

    def test_five_digit_sequence_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            QaQuestionAnswer.from_text(format_text("> **1.00100**: Five digits?\n\nTODO: answer pending\n"))
        self.assertIn("got '**1.00100**: Five digits?'", str(ctx.exception))


class TestPrbLeadSentenceInvariance(unittest.TestCase):
    """The prb lead-sentence template constraint parses identically after the `pattern` metadata."""

    def test_on_template_lead_sentence_still_parses(self) -> None:
        sut = Prb.from_text(format_text(_PRB_ACCEPT_BODY))
        self.assertEqual(
            sut.problem_statement.text,
            "The old manual process is causing constant rework, for the engineering team because it is error-prone.",
        )

    def test_off_template_lead_sentence_still_rejected_with_same_message(self) -> None:
        text = (
            "# Problem\n\nThis sentence does not follow the template at all.\n\n"
            "## Current State\n\n### Summary\nSome text.\n\n"
            "## Gap\nSome text.\n\n## Future State\nSome text.\n"
        )

        with self.assertRaises(ValidationError) as ctx:
            Prb.from_text(format_text(text))

        self.assertIn(
            "problem_statement must match the template '[Current state] is causing [specific issue], for "
            "[stakeholder] because [underlying cause].', got 'This sentence does not follow the template at all.'",
            str(ctx.exception),
        )


class TestPrbFiveW2HHeadingInvariance(unittest.TestCase):
    """The seven fixed prb 5W2H question headings parse identically after the per-class `enum`
    metadata."""

    def test_own_headings_still_parse(self) -> None:
        for cls, heading in [
            (Question1, "What Is the Problem?"),
            (Question7, "How Often Is the Problem Observed?"),
        ]:
            with self.subTest(cls=cls.__name__):
                sut = cls.from_text(format_text(f"### {heading}\n\nAn answer.\n"))
                self.assertIn(heading, str(sut))

    def test_foreign_heading_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            Question1.from_text(format_text("### Why Is It a Problem?\n\nAn answer.\n"))
        # `\\\\?` in this source is the `repr()` of Question1's own alias value
        # (`What Is the Problem\?`) -- see `describe_alias`; the alias value
        # itself stays inline in the decorator, so this pin is literal.
        self.assertEqual(
            str(ctx.exception),
            "Question1 (line 1): expected heading matching regex 'What Is the Problem\\\\?', "
            "got heading 'Why Is It a Problem?'",
        )


class TestRskTaraInvariance(unittest.TestCase):
    """The rsk TARA closed 4-value set parses identically after the `enum` metadata."""

    def test_every_tara_word_still_parses(self) -> None:
        for word in ["transfer", "accept", "reduce", "avoid"]:
            with self.subTest(word=word):
                sut = RskStrategy.from_text(format_text(f"## Strategy\n\n{word}\n"))
                self.assertEqual(sut.value.text, word)

    def test_non_tara_word_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            RskStrategy.from_text(format_text("## Strategy\n\ntolerate\n"))
        self.assertIn("value must match pattern '^(transfer|accept|reduce|avoid)$', got 'tolerate'", str(ctx.exception))


class TestRskAssessmentHeadingInvariance(unittest.TestCase):
    """The rsk `### Probability [1-5]`/`### Impact [1-5]` heading constraints parse identically
    after the `pattern` metadata."""

    def test_every_1_to_5_value_still_parses(self) -> None:
        for value in [1, 2, 3, 4, 5]:
            with self.subTest(value=value):
                self.assertEqual(RskProbability.from_text(format_text(f"### Probability {value}\n")).value, value)
                self.assertEqual(RskImpact.from_text(format_text(f"### Impact {value}\n")).value, value)

    def test_probability_6_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            RskProbability.from_text(format_text("### Probability 6\n"))
        self.assertEqual(
            str(ctx.exception),
            "Probability (line 1): expected heading matching regex '^Probability [1-5]$', got heading 'Probability 6'",
        )

    def test_probability_without_digit_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            RskProbability.from_text(format_text("### Probability\n"))
        self.assertEqual(
            str(ctx.exception),
            "Probability (line 1): expected heading matching regex '^Probability [1-5]$', got heading 'Probability'",
        )

    def test_impact_misspelled_word_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            RskImpact.from_text(format_text("### Impactality 3\n"))
        self.assertEqual(
            str(ctx.exception),
            "Impact (line 1): expected heading matching regex '^Impact [1-5]$', got heading 'Impactality 3'",
        )


class TestVcrAcHeadingInvariance(unittest.TestCase):
    """The vcr `### AC-NNN (Method): <text>` heading constraint (number shape + DTAIS method word)
    parses identically after the class-level `pattern`/`enum` metadata."""

    def test_every_dtais_method_still_parses(self) -> None:
        for method in ["Demonstration", "Test", "Analysis", "Inspection", "Special"]:
            with self.subTest(method=method):
                sut = AcceptanceCriterion.from_text(format_text(f"### AC-001 ({method}): The endpoint works\n"))
                self.assertEqual(sut.method, method)
                self.assertEqual(sut.number, 1)

    def test_unknown_method_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            AcceptanceCriterion.from_text(format_text("### AC-001 (Verification): The endpoint works\n"))
        # The message interpolates the class's own alias pattern via `repr()`
        # (`models.md.alias_match.describe_alias`), so the pattern part of the
        # expected string is derived from the domain's own constant -- the
        # literal pin covers the message's own wording and the observed
        # heading (see `TestTskUpdateEntryHeadingInvariance` for the rationale).
        expected = (
            "AcceptanceCriterion (line 1): expected heading matching regex "
            f"{_AC_ALIAS_PATTERN!r}, got heading 'AC-001 (Verification): The endpoint works'"
        )
        self.assertEqual(str(ctx.exception), expected)

    def test_one_digit_number_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            AcceptanceCriterion.from_text(format_text("### AC-1 (Test): Two-digit number\n"))
        self.assertIn("got heading 'AC-1 (Test): Two-digit number'", str(ctx.exception))

    def test_title_less_heading_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            AcceptanceCriterion.from_text(format_text("### AC-001 (Test):\n"))
        # Derived the same way as `test_unknown_method_still_rejected_with_same_message`.
        expected = (
            "AcceptanceCriterion (line 1): expected heading matching regex "
            f"{_AC_ALIAS_PATTERN!r}, got heading 'AC-001 (Test):'"
        )
        self.assertEqual(str(ctx.exception), expected)


class TestVcrCoverageInvariance(unittest.TestCase):
    """The vcr coverage closed 3-value set parses identically after the `enum` metadata."""

    def test_every_coverage_value_still_parses(self) -> None:
        for word in ["full", "partial", "none"]:
            with self.subTest(word=word):
                sut = VcrCoverage.from_text(format_text(f"## Coverage\n\n{word}\n"))
                self.assertEqual(sut.value.text, word)

    def test_unknown_coverage_still_rejected_with_same_message(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            VcrCoverage.from_text(format_text("## Coverage\n\nmostly\n"))
        self.assertIn("value must match pattern '^(full|partial|none)$', got 'mostly'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
