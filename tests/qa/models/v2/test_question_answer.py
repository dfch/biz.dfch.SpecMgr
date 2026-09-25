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

"""Tests for the QA v2 `QaAnswer`/`QaQuestionAnswer` models (ACC-001).

Covers `QaAnswer.get_extent`'s bounded terminator scan (heading/block
quote/comment, independently, and "runs to end of text" when none follow)
and `QaQuestionAnswer.get_extent`/`from_text` round-tripping for every case
listed in ACC-001: empty, comment-only, question+answer, a full
comment+question+answer triple, a multi-paragraph answer embedding an
ordered list (captured verbatim, opaque), two/three adjacent pairs in
sequence, and a trailing dangling comment (accepted as a comment-only pair).
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.qa.models.v2.question_answer import QaAnswer, QaQuestionAnswer


class TestQaAnswerGetExtentStopsAtEachTerminatorKind(unittest.TestCase):
    """`QaAnswer.get_extent` stops at the first depth-0 heading/block quote/comment, independently."""

    def test_stops_before_a_depth_zero_heading_of_any_level(self) -> None:
        for heading in ("## A Heading", "### A Heading", "#### A Heading"):
            with self.subTest(heading=heading):
                text = format_text(f"First para.\n\nSecond para.\n\n{heading}\n\nmore stuff after\n")
                lines = text.splitlines()
                stop_line = next(i for i, line in enumerate(lines) if line.startswith("#"))

                result = QaAnswer.get_extent(text)

                self.assertEqual(result, stop_line)

    def test_stops_before_a_depth_zero_block_quote(self) -> None:
        text = format_text("First para.\n\nSecond para.\n\n> **0.0010**: A question\n\nmore stuff after\n")
        lines = text.splitlines()
        stop_line = next(i for i, line in enumerate(lines) if line.startswith(">"))

        result = QaAnswer.get_extent(text)

        self.assertEqual(result, stop_line)

    def test_stops_before_a_depth_zero_comment(self) -> None:
        text = format_text("First para.\n\nSecond para.\n\n<!-- a note -->\n\nmore stuff after\n")
        lines = text.splitlines()
        stop_line = next(i for i, line in enumerate(lines) if line.startswith("<!--"))

        result = QaAnswer.get_extent(text)

        self.assertEqual(result, stop_line)

    def test_runs_to_end_of_text_when_no_terminator_follows(self) -> None:
        text = format_text("First para.\n\nSecond para.\n")

        result = QaAnswer.get_extent(text)

        self.assertEqual(result, len(text.splitlines()))

    def test_returns_zero_when_text_starts_with_a_terminator(self) -> None:
        text = format_text("## A Heading\n\nBody.\n")

        result = QaAnswer.get_extent(text)

        self.assertEqual(result, 0)

    def test_from_text_does_not_absorb_the_terminating_heading(self) -> None:
        text = format_text("First para.\n\nSecond para.\n\n## Next Section\n\nmore stuff after\n")
        extent = QaAnswer.get_extent(text)
        own_text = format_text("\n".join(text.splitlines()[:extent]))

        sut = QaAnswer.from_text(own_text)

        self.assertIn("First para.", sut.text)
        self.assertIn("Second para.", sut.text)
        self.assertNotIn("Next Section", sut.text)


class TestQaQuestionAnswerEmpty(unittest.TestCase):
    """A `QaQuestionAnswer` with no fields set at all is a valid, empty pair."""

    def test_direct_construction_with_no_fields_set(self) -> None:
        sut = QaQuestionAnswer()

        self.assertIsNone(sut.comment)
        self.assertIsNone(sut.question)
        self.assertIsNone(sut.answer)

    def test_get_extent_returns_zero_when_nothing_matches(self) -> None:
        text = format_text("## Next Category\n\nBody.\n")

        result = QaQuestionAnswer.get_extent(text)

        self.assertEqual(result, 0)


class TestQaQuestionAnswerCommentOnly(unittest.TestCase):
    """A comment with nothing recognizable following it is a valid comment-only pair."""

    def test_round_trips_at_end_of_text(self) -> None:
        text = format_text("<!-- just a note -->\n")

        extent = QaQuestionAnswer.get_extent(text)
        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertEqual(extent, len(text.splitlines()))
        self.assertIsNotNone(sut.comment)
        self.assertIsNone(sut.question)
        self.assertIsNone(sut.answer)
        self.assertEqual(str(sut), text)


class TestQaQuestionAnswerQuestionAndAnswerOnly(unittest.TestCase):
    """`comment` may be absent while `question`/`answer` are both present."""

    def test_round_trips(self) -> None:
        text = format_text("> **0.0010**: Question?\n\nAnswer prose.\n")

        extent = QaQuestionAnswer.get_extent(text)
        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertEqual(extent, len(text.splitlines()))
        self.assertIsNone(sut.comment)
        self.assertIsNotNone(sut.question)
        self.assertEqual(sut.question.text, "**0.0010**: Question?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "Answer prose.")
        self.assertEqual(str(sut), text)


class TestQaQuestionAnswerFullTriple(unittest.TestCase):
    """`comment`, `question`, and `answer` are all present at once."""

    def test_round_trips(self) -> None:
        text = format_text("<!-- comment -->\n\n> **0.0010**: Question?\n\nAnswer prose.\n")

        extent = QaQuestionAnswer.get_extent(text)
        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertEqual(extent, len(text.splitlines()))
        self.assertIsNotNone(sut.comment)
        self.assertIsNotNone(sut.question)
        self.assertEqual(sut.question.text, "**0.0010**: Question?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "Answer prose.")
        self.assertEqual(str(sut), text)


class TestQaQuestionAnswerMultiParagraphAnswerWithOrderedList(unittest.TestCase):
    """A multi-paragraph answer embedding an ordered list is captured verbatim, opaque."""

    def test_round_trips_and_keeps_the_list_verbatim(self) -> None:
        text = format_text(
            """\
<!-- comment belongs to the question right after it -->

> **1.0010**: How should malformed widgets be handled?

Malformed widgets are rejected and logged. The rejection flow is:

1. Validate the widget schema.
2. Log the failure with the widget's id.
3. Increment the `rejected_total` counter.

No retry is attempted for malformed input.
"""
        )

        extent = QaQuestionAnswer.get_extent(text)
        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertEqual(extent, len(text.splitlines()))
        self.assertIsNotNone(sut.comment)
        self.assertIsNotNone(sut.question)
        self.assertIsNotNone(sut.answer)
        self.assertIn("Validate the widget schema.", sut.answer.text)
        self.assertIn("Log the failure with the widget's id.", sut.answer.text)
        self.assertIn("Increment the `rejected_total` counter.", sut.answer.text)
        self.assertIn("No retry is attempted for malformed input.", sut.answer.text)
        self.assertEqual(str(sut), text)


class TestQaQuestionAnswerAdjacentPairs(unittest.TestCase):
    """Multiple `QaQuestionAnswer` pairs, back-to-back with no heading between them."""

    def test_two_adjacent_pairs(self) -> None:
        text = format_text(
            """\
<!-- comment -->

> **0.0010**: First question?

First answer.

> **0.0020**: Second question?

Second answer.
"""
        )

        remaining, items = QaQuestionAnswer.process_list_field("questions", QaQuestionAnswer, text, optional=True)

        self.assertIsNotNone(items)
        assert items is not None
        self.assertEqual(len(items), 2)
        self.assertEqual(remaining, "")

        first, second = items
        assert isinstance(first, QaQuestionAnswer)
        assert isinstance(second, QaQuestionAnswer)
        self.assertIsNotNone(first.comment)
        self.assertEqual(first.question.text, "**0.0010**: First question?")
        self.assertEqual(first.answer.text.strip(), "First answer.")
        self.assertIsNone(second.comment)
        self.assertEqual(second.question.text, "**0.0020**: Second question?")
        self.assertEqual(second.answer.text.strip(), "Second answer.")

    def test_three_adjacent_pairs(self) -> None:
        text = format_text(
            """\
> **0.0010**: Q1?

A1.

<!-- c2 -->

> **0.0020**: Q2?

A2.

> **0.0030**: Q3?

A3.
"""
        )

        remaining, items = QaQuestionAnswer.process_list_field("questions", QaQuestionAnswer, text, optional=True)

        self.assertIsNotNone(items)
        assert items is not None
        self.assertEqual(len(items), 3)
        self.assertEqual(remaining, "")

        first, second, third = items
        assert isinstance(first, QaQuestionAnswer)
        assert isinstance(second, QaQuestionAnswer)
        assert isinstance(third, QaQuestionAnswer)
        self.assertIsNone(first.comment)
        self.assertEqual(first.question.text, "**0.0010**: Q1?")
        self.assertIsNotNone(second.comment)
        self.assertEqual(second.question.text, "**0.0020**: Q2?")
        self.assertIsNone(third.comment)
        self.assertEqual(third.question.text, "**0.0030**: Q3?")


class TestQaQuestionAnswerTrailingDanglingComment(unittest.TestCase):
    """A trailing dangling comment (nothing recognizable following it) is accepted as a comment-only pair."""

    def test_dangling_comment_after_a_full_pair_becomes_its_own_pair(self) -> None:
        text = format_text(
            """\
> **0.0010**: Q1?

A1.

<!-- dangling comment -->
"""
        )

        remaining, items = QaQuestionAnswer.process_list_field("questions", QaQuestionAnswer, text, optional=True)

        self.assertIsNotNone(items)
        assert items is not None
        self.assertEqual(len(items), 2)
        self.assertEqual(remaining, "")

        first, second = items
        assert isinstance(first, QaQuestionAnswer)
        assert isinstance(second, QaQuestionAnswer)
        self.assertEqual(first.question.text, "**0.0010**: Q1?")
        self.assertIsNotNone(second.comment)
        self.assertIsNone(second.question)
        self.assertIsNone(second.answer)

    def test_dangling_comment_followed_by_a_heading_still_becomes_its_own_pair(self) -> None:
        text = format_text(
            """\
> **0.0010**: Q1?

A1.

<!-- dangling comment -->

## Next Category
"""
        )

        remaining, items = QaQuestionAnswer.process_list_field("questions", QaQuestionAnswer, text, optional=True)

        self.assertIsNotNone(items)
        assert items is not None
        self.assertEqual(len(items), 2)
        self.assertEqual(remaining.strip(), "## Next Category")

        _first, second = items
        assert isinstance(second, QaQuestionAnswer)
        self.assertIsNotNone(second.comment)
        self.assertIsNone(second.question)
        self.assertIsNone(second.answer)


class TestQaQuestionAnswerEmptyCategoryIsLegitimate(unittest.TestCase):
    """A category section with zero pairs is legitimate -- `process_list_field` reports no items."""

    def test_process_list_field_finds_no_items_when_a_heading_comes_first(self) -> None:
        text = format_text("## Next Category\n\nBody.\n")

        remaining, items = QaQuestionAnswer.process_list_field("questions", QaQuestionAnswer, text, optional=True)

        self.assertIsNone(items)
        self.assertEqual(remaining, text)


class TestQaQuestionAnswerNumberPrefix(unittest.TestCase):
    """`QaQuestionAnswer`'s own `field_validator("question")` enforces the bold `**<d>.<NNNN>**: `
    question-number prefix (feat-156 ACC-001, REQ-001/004).

    Every malformed shape in ACC-001 rejects with `pydantic.ValidationError`
    (the validator's own `ValueError`, channeled by pydantic at `from_text`'s
    final `cls(**kwargs)`); the number prefix is the *only* constraint on the
    number -- gaps, in-between numbers, and any category digit all parse
    (REQ-003, Design Notes 4), and a pair with no `question` at all skips the
    validator entirely (Design Note 3).
    """

    def _parse_pair(self, question: str) -> QaQuestionAnswer:
        """Parse one `question` block quote plus a free-form answer into a `QaQuestionAnswer`."""
        text = format_text(f"{question}\n\nAn answer.\n")
        return QaQuestionAnswer.from_text(text)

    def test_single_line_numbered_question_parses(self) -> None:
        sut = self._parse_pair("> **0.0010**: What is the expected load?")

        self.assertEqual(sut.question.text, "**0.0010**: What is the expected load?")

    def test_numbered_question_round_trips(self) -> None:
        text = format_text("> **1.0020**: What is the expected load?\n\nAn answer.\n")

        sut = QaQuestionAnswer.from_text(text)

        self.assertEqual(str(sut), text)

    def test_multi_line_numbered_question_parses(self) -> None:
        """The prefix is a start-anchored check: the question text itself stays free-form
        and may span several quoted lines."""
        sut = self._parse_pair("> **0.0010**: What is the\n> expected load?")

        self.assertEqual(sut.question.text, "**0.0010**: What is the\nexpected load?")

    def test_line_break_after_the_colon_is_accepted(self) -> None:
        """The `\\s` after the colon also accepts a line break (feat-156 Design Note 13's
        one documented softness, accepted as-is): the number alone on the first quoted
        line, the question continuing on the next."""
        sut = self._parse_pair("> **0.0010**:\n> What is the expected load?")

        self.assertEqual(sut.question.text, "**0.0010**:\nWhat is the expected load?")

    def test_missing_prefix_rejects(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            self._parse_pair("> What is the expected load?")

        self.assertIn("question must start with the bold question-number prefix", str(ctx.exception))

    def test_bare_number_only_line_rejects(self) -> None:
        """A `**<d>.<NNNN>**: ` line with no question text after it rejects -- `format_text`
        strips the trailing space, so the `\\s` after the colon has nothing to match."""
        with self.assertRaises(ValidationError) as ctx:
            self._parse_pair("> **0.0010**: ")

        self.assertIn("question must start with the bold question-number prefix", str(ctx.exception))

    def test_three_digit_sequence_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> **0.010**: What is the expected load?")

    def test_five_digit_sequence_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> **0.00100**: What is the expected load?")

    def test_two_digit_sequence_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> **0.10**: What is the expected load?")

    def test_two_digit_category_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> **10.0010**: What is the expected load?")

    def test_missing_colon_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> **0.0010** What is the expected load?")

    def test_space_before_the_colon_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> **0.0010 **: What is the expected load?")

    def test_number_not_at_the_start_rejects(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse_pair("> Q **0.0010**: What is the expected load?")

    def test_question_absent_skips_the_validator(self) -> None:
        """A comment-only pair (no `question`) parses fine -- the validator runs only when
        `question` is present (feat-156 Design Note 3)."""
        text = format_text("<!-- just a note -->\n")
        extent = QaQuestionAnswer.get_extent(text)

        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertIsNone(sut.question)


class TestQaQuestionAnswerNumberGapsAndNonTenSteps(unittest.TestCase):
    """Gaps and in-between numbers (e.g. `0.0015` between `0.0010` and `0.0020`) parse
    without complaint -- the parser never enforces the start-at/step-by convention
    (feat-156 ACC-002, REQ-003, Design Note 4)."""

    def test_gaps_and_in_between_numbers_parse(self) -> None:
        text = format_text(
            """\
> **0.0010**: First question?

First answer.

> **0.0015**: In-between question?

In-between answer.

> **0.0030**: Third question?

Third answer.
"""
        )

        remaining, items = QaQuestionAnswer.process_list_field("questions", QaQuestionAnswer, text, optional=True)

        self.assertIsNotNone(items)
        assert items is not None
        self.assertEqual(len(items), 3)
        self.assertEqual(remaining, "")

        numbers = [item.question.text for item in items]
        self.assertEqual(
            numbers,
            ["**0.0010**: First question?", "**0.0015**: In-between question?", "**0.0030**: Third question?"],
        )


if __name__ == "__main__":
    unittest.main()
