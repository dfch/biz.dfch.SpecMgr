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
        text = format_text("First para.\n\nSecond para.\n\n> A question\n\nmore stuff after\n")
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
        text = format_text("> Question?\n\nAnswer prose.\n")

        extent = QaQuestionAnswer.get_extent(text)
        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertEqual(extent, len(text.splitlines()))
        self.assertIsNone(sut.comment)
        self.assertIsNotNone(sut.question)
        self.assertEqual(sut.question.text, "Question?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "Answer prose.")
        self.assertEqual(str(sut), text)


class TestQaQuestionAnswerFullTriple(unittest.TestCase):
    """`comment`, `question`, and `answer` are all present at once."""

    def test_round_trips(self) -> None:
        text = format_text("<!-- comment -->\n\n> Question?\n\nAnswer prose.\n")

        extent = QaQuestionAnswer.get_extent(text)
        sut = QaQuestionAnswer.from_text(format_text("\n".join(text.splitlines()[:extent])))

        self.assertEqual(extent, len(text.splitlines()))
        self.assertIsNotNone(sut.comment)
        self.assertIsNotNone(sut.question)
        self.assertEqual(sut.question.text, "Question?")
        self.assertIsNotNone(sut.answer)
        self.assertEqual(sut.answer.text.strip(), "Answer prose.")
        self.assertEqual(str(sut), text)


class TestQaQuestionAnswerMultiParagraphAnswerWithOrderedList(unittest.TestCase):
    """A multi-paragraph answer embedding an ordered list is captured verbatim, opaque."""

    def test_round_trips_and_keeps_the_list_verbatim(self) -> None:
        text = format_text(
            """\
<!-- comment belongs to the question right after it -->

> How should malformed widgets be handled?

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

> First question?

First answer.

> Second question?

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
        self.assertEqual(first.question.text, "First question?")
        self.assertEqual(first.answer.text.strip(), "First answer.")
        self.assertIsNone(second.comment)
        self.assertEqual(second.question.text, "Second question?")
        self.assertEqual(second.answer.text.strip(), "Second answer.")

    def test_three_adjacent_pairs(self) -> None:
        text = format_text(
            """\
> Q1?

A1.

<!-- c2 -->

> Q2?

A2.

> Q3?

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
        self.assertEqual(first.question.text, "Q1?")
        self.assertIsNotNone(second.comment)
        self.assertEqual(second.question.text, "Q2?")
        self.assertIsNone(third.comment)
        self.assertEqual(third.question.text, "Q3?")


class TestQaQuestionAnswerTrailingDanglingComment(unittest.TestCase):
    """A trailing dangling comment (nothing recognizable following it) is accepted as a comment-only pair."""

    def test_dangling_comment_after_a_full_pair_becomes_its_own_pair(self) -> None:
        text = format_text(
            """\
> Q1?

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
        self.assertEqual(first.question.text, "Q1?")
        self.assertIsNotNone(second.comment)
        self.assertIsNone(second.question)
        self.assertIsNone(second.answer)

    def test_dangling_comment_followed_by_a_heading_still_becomes_its_own_pair(self) -> None:
        text = format_text(
            """\
> Q1?

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


if __name__ == "__main__":
    unittest.main()
