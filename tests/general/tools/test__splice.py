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

"""Tests for ``general.tools._splice``'s ``window_body``, ``splice_body``, and ``splice_snippet`` helpers
(feat-28-get-update, Phase 2; the snippet helper is feat-153-off-by-n, Phase 2)."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._splice import splice_body, splice_snippet, validate_read_args, window_body

_BODY = "l1\nl2\nl3\nl4\n"


class TestWindowBody(unittest.TestCase):
    """Tests for the no-I/O window_body helper (clamping, never erroring)."""

    def test_defaults_return_the_full_body_byte_for_byte(self) -> None:
        """No arguments (and explicit offset=1, limit=None) must equal a normal trailing-newline body byte-for-byte."""
        self.assertEqual(window_body(_BODY), _BODY)
        self.assertEqual(window_body(_BODY, 1, None), _BODY)

    def test_mid_window_returns_exactly_the_requested_lines(self) -> None:
        """offset=k, limit=m must return exactly lines k..k+m-1, each with its trailing newline, joined."""
        self.assertEqual(window_body(_BODY, 2, 2), "l2\nl3\n")
        self.assertEqual(window_body(_BODY, 2, 3), "l2\nl3\nl4\n")
        self.assertEqual(window_body(_BODY, 4, 1), "l4\n")

    def test_offset_past_last_line_returns_empty_string(self) -> None:
        """An offset past the last body line (offset > N) must return the empty string."""
        self.assertEqual(window_body(_BODY, 5), "")
        self.assertEqual(window_body(_BODY, 100, 3), "")

    def test_limit_caps_at_the_remaining_lines(self) -> None:
        """A limit larger than the remaining lines must cap at the remaining lines."""
        self.assertEqual(window_body(_BODY, 3, 99), "l3\nl4\n")
        self.assertEqual(window_body(_BODY, 1, 99), _BODY)

    def test_zero_limit_returns_empty_string(self) -> None:
        """limit=0 must return the empty string (an empty window)."""
        self.assertEqual(window_body(_BODY, 2, 0), "")

    def test_offset_below_one_floors_to_one(self) -> None:
        """An offset below 1 must floor to 1."""
        self.assertEqual(window_body(_BODY, 0, 2), "l1\nl2\n")
        self.assertEqual(window_body(_BODY, -5), _BODY)

    def test_negative_limit_returns_empty_string(self) -> None:
        """A negative limit must return the empty string."""
        self.assertEqual(window_body(_BODY, 1, -3), "")

    def test_empty_text_returns_empty_string(self) -> None:
        """An empty text must return the empty string for any coordinates."""
        self.assertEqual(window_body(""), "")
        self.assertEqual(window_body("", 1, None), "")
        self.assertEqual(window_body("", 2, 3), "")

    def test_consecutive_windows_reproduce_the_body(self) -> None:
        """Concatenating consecutive non-overlapping windows must reproduce the body."""
        self.assertEqual(window_body(_BODY, 1, 2) + window_body(_BODY, 3, 2), _BODY)
        self.assertEqual(window_body(_BODY, 1, 1) + window_body(_BODY, 2, 2) + window_body(_BODY, 4), _BODY)

    def test_defaults_add_a_trailing_newline_for_a_no_trailing_newline_body(self) -> None:
        """The defaults equal ``body_text`` byte-for-byte ONLY for trailing-newline bodies (the documented
        caveat): a body without a trailing newline gains one here, which is exactly why every ``get_<d>``
        tool's no-window raw path keeps returning ``body_text`` verbatim instead of routing it through
        ``window_body`` (feat-153-off-by-n's pinned no-window wiring, ACC-004's byte-identity)."""
        self.assertEqual(window_body("a\nb", 1, None), "a\nb\n")


class TestWindowBodyNumbered(unittest.TestCase):
    """Tests for ``window_body``'s opt-in ``numbered=`` argument (feat-153-off-by-n Phase 3, REQ-004, ACC-011).

    The full cross-domain tool-level matrix is this feature's Phase 5;
    this class pins the byte-exact line-prefix format and the
    clamped-offset numbering the 12 ``get_<d>`` tools rely on.
    """

    def test_numbered_full_window_prefixes_absolute_line_numbers(self) -> None:
        """numbered=True over the whole body must prefix each line with ``f"{n}: "`` (1-based) plus a single
        trailing newline."""
        self.assertEqual(window_body(_BODY, 1, None, numbered=True), "1: l1\n2: l2\n3: l3\n4: l4\n")

    def test_numbered_window_starts_at_the_clamped_offset_and_never_restarts(self) -> None:
        """A windowed numbered read numbers from the clamped offset -- absolute, not window-relative (ACC-011)."""
        self.assertEqual(window_body(_BODY, 2, 2, numbered=True), "2: l2\n3: l3\n")
        self.assertEqual(window_body(_BODY, 3, None, numbered=True), "3: l3\n4: l4\n")

    def test_numbered_offset_below_one_floors_to_one(self) -> None:
        """An offset below 1 must floor to 1 for numbering as for windowing."""
        self.assertEqual(window_body(_BODY, 0, 2, numbered=True), "1: l1\n2: l2\n")
        self.assertEqual(window_body(_BODY, -5, numbered=True), "1: l1\n2: l2\n3: l3\n4: l4\n")

    def test_numbered_empty_window_returns_empty_string(self) -> None:
        """An offset past the last body line (or a zero/negative limit) must return the empty string, no numbers."""
        self.assertEqual(window_body(_BODY, 5, numbered=True), "")
        self.assertEqual(window_body(_BODY, 2, 0, numbered=True), "")
        self.assertEqual(window_body(_BODY, 2, -1, numbered=True), "")
        self.assertEqual(window_body("", 1, None, numbered=True), "")

    def test_numbered_normalizes_the_trailing_newline(self) -> None:
        """Non-empty numbered output ends with exactly one trailing newline regardless of the source body's own."""
        self.assertEqual(window_body("a\nb", 1, None, numbered=True), "1: a\n2: b\n")

    def test_numbered_empty_line_renders_with_trailing_space(self) -> None:
        """An empty body line is verbatim text: ``"<n>: "`` with the separator's trailing space."""
        self.assertEqual(window_body("h1\n\nh3\n", 1, None, numbered=True), "1: h1\n2: \n3: h3\n")

    def test_numbered_default_off_is_byte_identical(self) -> None:
        """numbered=False (the default) must stay byte-identical to the unnumbered window (ACC-004's helper
        half)."""
        self.assertEqual(window_body(_BODY, 2, 2, numbered=False), window_body(_BODY, 2, 2))
        self.assertEqual(window_body("a\nb", numbered=False), window_body("a\nb"))


class TestValidateReadArgs(unittest.TestCase):
    """Tests for the shared ``get_<d>`` read-argument guard (feat-153-off-by-n Phase 3, REQ-005, ACC-005)."""

    def test_raw_true_accepts_every_combination(self) -> None:
        """raw=True: all read-argument combinations are legal (no raise)."""
        validate_read_args(True, 2, 3, True)
        validate_read_args(True, None, None, False)
        validate_read_args(True, 1, None, True)

    def test_offset_limit_with_raw_false_raise_value_error(self) -> None:
        """offset/limit with raw=False must raise the byte-identical pre-factorization message (existing tests
        assert on it)."""
        with self.assertRaises(ValueError) as ctx:
            validate_read_args(False, 2, 3, False)
        self.assertEqual(str(ctx.exception), "offset/limit are only valid with raw=True, got offset=2, limit=3")
        with self.assertRaises(ValueError) as ctx:
            validate_read_args(False, None, 3, False)
        self.assertIn("raw", str(ctx.exception))
        self.assertIn("limit=3", str(ctx.exception))

    def test_numbered_with_raw_false_raises_value_error(self) -> None:
        """numbered=True with raw=False must raise ValueError naming the offending value."""
        with self.assertRaises(ValueError) as ctx:
            validate_read_args(False, None, None, True)
        message = str(ctx.exception)
        self.assertIn("numbered", message)
        self.assertIn("raw", message)

    def test_offset_limit_checked_before_numbered(self) -> None:
        """Both misuses at once: the pre-existing offset/limit rule keeps priority."""
        with self.assertRaises(ValueError) as ctx:
            validate_read_args(False, 2, None, True)
        self.assertIn("offset/limit", str(ctx.exception))


class TestSpliceBody(unittest.TestCase):
    """Tests for the no-I/O splice_body helper's offset/limit signature (strict)."""

    def test_single_line_replace(self) -> None:
        """offset=k, limit=1 must replace line k only."""
        self.assertEqual(splice_body(_BODY, 2, 1, "x"), "l1\nx\nl3\nl4\n")

    def test_multi_line_replace(self) -> None:
        """offset=k, limit=m must replace exactly lines k..k+m-1."""
        self.assertEqual(splice_body(_BODY, 2, 2, "x"), "l1\nx\nl4\n")

    def test_omitted_limit_replaces_through_end(self) -> None:
        """An omitted limit must replace through the last body line."""
        self.assertEqual(splice_body(_BODY, 3, None, "x\ny"), "l1\nl2\nx\ny\n")

    def test_zero_limit_is_a_pure_insert(self) -> None:
        """limit=0 mid-body must insert content's lines before offset, dropping nothing."""
        self.assertEqual(splice_body(_BODY, 3, 0, "i"), "l1\nl2\ni\nl3\nl4\n")

    def test_offset_past_last_line_appends(self) -> None:
        """offset=N+1 (limit=0 or omitted) must append after the last line."""
        self.assertEqual(splice_body(_BODY, 5, 0, "a"), "l1\nl2\nl3\nl4\na\n")
        self.assertEqual(splice_body(_BODY, 5, None, "a"), "l1\nl2\nl3\nl4\na\n")

    def test_offset_below_one_raises_value_error(self) -> None:
        """offset < 1 must raise ValueError naming the offending value."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 0, 1, "x")
        message = str(ctx.exception)
        self.assertIn("offset", message)
        self.assertIn("0", message)

    def test_offset_above_n_plus_one_raises_value_error(self) -> None:
        """offset > N+1 must raise ValueError naming the offending value and the allowed range."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 6, 0, "x")
        message = str(ctx.exception)
        self.assertIn("offset", message)
        self.assertIn("6", message)
        self.assertIn("N+1", message)

    def test_negative_limit_raises_value_error(self) -> None:
        """limit < 0 must raise ValueError naming the offending value."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 1, -1, "x")
        message = str(ctx.exception)
        self.assertIn("limit", message)
        self.assertIn("-1", message)

    def test_range_past_end_raises_value_error(self) -> None:
        """offset + limit - 1 > N must raise ValueError naming the offending values."""
        with self.assertRaises(ValueError) as ctx:
            splice_body(_BODY, 3, 3, "x")
        message = str(ctx.exception)
        self.assertIn("offset", message)
        self.assertIn("limit", message)
        self.assertIn("3", message)


class TestSpliceSnippet(unittest.TestCase):
    """Tests for the no-I/O splice_snippet helper (feat-153-off-by-n Phase 2, REQ-002, ADR 19ff316b).

    The full ACC-002 matrix (all domains, every splice shape) is this
    feature's Phase 5; this class pins the byte-exact line format (the ADR's
    Decision Outcome item 3 worked example) and the boundary behavior the
    dispatcher relies on.
    """

    def _snippet(self, offset: int, limit: int | None, content: str) -> str:
        """Splice ``_BODY`` at the coordinates and render the snippet from both bodies."""
        pre = _BODY
        post = splice_body(pre, offset, limit, content)
        result = splice_snippet(pre, post, offset, limit)
        return result

    def test_1_for_1_replace(self) -> None:
        """offset=k, limit=1 replaced by 1 line: dropped/inserted share the number, 2 context per side."""
        self.assertEqual(
            self._snippet(2, 1, "x"),
            "  1: l1\n- 2: l2\n+ 2: x\n  3: l3\n  4: l4\n",
        )

    def test_size_changing_replace_1_to_3(self) -> None:
        """offset=k, limit=1 replaced by 3 lines: post numbers continue from the insert, context
        below is renumbered (the pre-splice/post-splice split, not contiguous)."""
        self.assertEqual(
            self._snippet(2, 1, "a\nb\nc"),
            "  1: l1\n- 2: l2\n+ 2: a\n+ 3: b\n+ 4: c\n  5: l3\n  6: l4\n",
        )

    def test_pure_insert_has_no_dropped_lines(self) -> None:
        """limit=0: no `-` lines; the inserted lines take the offset's post numbers."""
        self.assertEqual(
            self._snippet(3, 0, "i"),
            "  1: l1\n  2: l2\n+ 3: i\n  4: l3\n  5: l4\n",
        )

    def test_pure_delete_has_no_inserted_lines(self) -> None:
        """Empty content: no `+` lines; the context below the gap takes the post (shifted) numbers."""
        self.assertEqual(
            self._snippet(2, 2, ""),
            "  1: l1\n- 2: l2\n- 3: l3\n  2: l4\n",
        )

    def test_append_at_n_plus_one(self) -> None:
        """offset=N+1, limit=0: context above is the body's last 2 lines; nothing below."""
        self.assertEqual(
            self._snippet(5, 0, "z"),
            "  3: l3\n  4: l4\n+ 5: z\n",
        )

    def test_omitted_limit_through_end(self) -> None:
        """Omitted limit: all lines from the offset are dropped; the insert ends the body."""
        self.assertEqual(
            self._snippet(3, None, "x\ny"),
            "  1: l1\n  2: l2\n- 3: l3\n- 4: l4\n+ 3: x\n+ 4: y\n",
        )

    def test_context_clamps_at_body_start(self) -> None:
        """offset=2: only one context line above (the body's first line)."""
        self.assertEqual(
            self._snippet(2, 1, "x"),
            "  1: l1\n- 2: l2\n+ 2: x\n  3: l3\n  4: l4\n",
        )

    def test_context_clamps_at_body_end(self) -> None:
        """Replacing the last 2 lines: no context below."""
        self.assertEqual(
            self._snippet(3, 2, "x"),
            "  1: l1\n  2: l2\n- 3: l3\n- 4: l4\n+ 3: x\n",
        )

    def test_empty_body_no_op_returns_empty_string(self) -> None:
        """A no-op splice on an empty body (degenerate helper input) yields ``""`` -- no lines at all."""
        self.assertEqual(splice_snippet("", "", 1, None), "")
        self.assertEqual(splice_snippet("", "", 1, 0), "")

    def test_empty_lines_render_with_trailing_space(self) -> None:
        """An empty body line is verbatim text: ``<marker> <n>: `` with the separator's trailing space."""
        pre = "h1\n\nold\nnext\n"
        post = splice_body(pre, 3, 1, "new")
        snippet = splice_snippet(pre, post, 3, 1)
        self.assertEqual(snippet, "  1: h1\n  2: \n- 3: old\n+ 3: new\n  4: next\n")
        self.assertIn("  2: \n", snippet)

    def test_adr_worked_example_byte_exact(self) -> None:
        """ADR 19ff316b's Decision Outcome item 3 worked example, asserted verbatim."""
        pre = "line one\n\n## Some Heading\n(the single old line that was replaced)\n(unchanged line)\n(final line)\n"
        post = splice_body(pre, 4, 1, "first new line\nsecond new line\nthird new line\n")
        snippet = splice_snippet(pre, post, 4, 1)
        self.assertEqual(
            snippet,
            "  2: \n"
            "  3: ## Some Heading\n"
            "- 4: (the single old line that was replaced)\n"
            "+ 4: first new line\n"
            "+ 5: second new line\n"
            "+ 6: third new line\n"
            "  7: (unchanged line)\n"
            "  8: (final line)\n",
        )

    def test_bad_coordinates_raise_assertion_error(self) -> None:
        """Coordinates outside splice_body's own contract are program-invariant failures (AssertionError)."""
        for offset, limit in [(0, 1), (6, 1), (2, -1), (2, 99)]:
            with self.subTest(offset=offset, limit=limit):
                with self.assertRaises(AssertionError):
                    splice_snippet(_BODY, _BODY, offset, limit)

    def test_offset_one_replacement_has_no_context_above(self) -> None:
        """offset=1: the context above clamps to zero lines at the body's start (Task 5.1's body-start
        boundary case; the existing offset=2 test only covers one context line above)."""
        self.assertEqual(
            self._snippet(1, 1, "x"),
            "- 1: l1\n+ 1: x\n  2: l2\n  3: l3\n",
        )

    def test_size_changing_shrink_3_to_1(self) -> None:
        """offset=k, limit=3 replaced by 1 line (the shrink direction of Task 5.1's size-changing case):
        the dropped lines keep their pre-splice numbers, and the single inserted line plus the context
        below take the post-splice numbers (REQ-002's pre-splice/post-splice split)."""
        self.assertEqual(
            self._snippet(2, 3, "x"),
            "  1: l1\n- 2: l2\n- 3: l3\n- 4: l4\n+ 2: x\n",
        )

    def test_whole_body_equivalent_range_renders_the_full_window(self) -> None:
        """offset=1 with an omitted limit: the helper itself renders the whole body as dropped+inserted
        lines with no context -- it has NO ``snippet=None`` special case. The whole-body-equivalent
        ``snippet=None`` rule (Task 5.1 / REQ-003) is the shared dispatcher's: it never calls the helper
        for that range, and the ACC-relevant pin lives in ``test_update.py``'s
        ``test_offset_one_equals_whole_body_mode`` (all domains)."""
        post = splice_body(_BODY, 1, None, "a\nb")
        self.assertEqual(
            splice_snippet(_BODY, post, 1, None),
            "- 1: l1\n- 2: l2\n- 3: l3\n- 4: l4\n+ 1: a\n+ 2: b\n",
        )


if __name__ == "__main__":
    unittest.main()
