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

"""One adjacent question/answer pair with no heading of its own (QA v2).

Many Q&A pairs can appear directly one after another inside a single
ISO/IEC 25010:2023 characteristic section, each shaped as
`<!-- optional comment -->` + `> {question}` (a block quote) + free-form
answer prose -- with **no heading of its own** per pair:

```
<!-- optional comment -->                comment: MarkdownComment | None
> {question}                             question: MarkdownBlockQuote | None
{free-form answer prose}                 answer: QaAnswer | None
```

`QaQuestionAnswer` needs no override of `from_text`/`__str__`/
`_get_field_names()` -- all three fields are plain `Optional[SingleClass]`
(no lists, no unions), which the generic, unmodified `MarkdownStr` engine
already distributes/renders correctly. It does, however, need a `get_extent`
override: the generic engine has no notion of "a composite's own extent is
the sum of its declared fields' own extents" (every other composite in this
codebase is either heading-bounded or a single pre-grouped markdown-it
token) -- see the feature README's Design Notes for the full rationale.

Both `get_extent` overrides in this module are local, throwaway adaptations
of the depth-0 scanning technique `MarkdownSection.get_extent`'s
`end_marker` mechanism (feat-12) already established -- generalized here
from "stop at one declared marker type" to "stop at the first of: heading
(any level), block quote, or comment". Neither override touches, imports
from, or is exported to `models/md/` -- by explicit instruction, this
feature adds zero changes to that shared engine.
"""

from __future__ import annotations

from markdown_it.token import Token
from pydantic import Field, computed_field

from ....models.md import MarkdownBlockQuote, MarkdownComment, MarkdownStr
from ....models.md._markdown import format_text, parse

#: Every markdown-it heading tag, indexed the same way `models/md/markdown_section.py`'s
#: own (private, un-imported) `_HEADING_TAGS` is -- duplicated locally rather than reaching
#: into that module's private constant, per this feature's "zero changes to, and no reuse
#: of internals from, `models/md/`" design constraint.
_HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")


def _is_heading(tok: Token) -> bool:
    """Return whether `tok` is a `heading_open` token of any level (h1-h6)."""
    result = tok.type == "heading_open" and tok.tag in _HEADING_TAGS
    return result


def _is_block_quote(tok: Token) -> bool:
    """Return whether `tok` is a `blockquote_open` token, matching `MarkdownBlockQuote`'s own metadata."""
    result = tok.type == "blockquote_open" and tok.tag == "blockquote"
    return result


def _is_comment(tok: Token) -> bool:
    """Return whether `tok` is an HTML comment block, matching `MarkdownComment`'s own metadata."""
    result = tok.type == "html_block" and tok.tag == "" and tok.content.startswith("<!--")
    return result


class QaAnswer(MarkdownStr):
    """One `QaQuestionAnswer`'s free-form prose answer -- an opaque, unparsed markdown blob.

    Deliberately **not** heading-anchored: since further adjacent Q&A pairs
    can follow within the same enclosing category section, the base
    `MarkdownStr.get_extent`'s "swallow everything remaining" (correct for a
    field declared *last* in a heading-bounded section) would be wrong here
    -- so this class overrides `get_extent` to stop at the first depth-0
    occurrence of a heading (any level), a block quote, or a comment, and
    only runs to the end of the given text when none of those follow.

    Adds a `text` computed property (mirroring
    `MarkdownParagraph.text`/`MarkdownSection.text`) so this otherwise-private
    `_value` is reachable through `model_dump()`/`model_dump_json()`.
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this answer blob, as a line count.

        Scans every token parsed from `text`, tracking a depth counter the
        same way `MarkdownSection.get_extent`'s `end_marker` mechanism does
        (incremented/decremented by each token's own `Token.nesting`): the
        first token encountered at depth 0 that is a heading (any level), a
        block quote, or a comment stops the scan, and its own `.map[0]`
        (start line) is returned as the extent -- excluding that terminating
        token itself, same convention as `MarkdownSection.get_extent`.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` starts immediately with one of the three terminator
                kinds (no answer text present at all).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by
                the answer's own prose, stopping before the first depth-0
                heading/block quote/comment, or at the end of `text` if
                none follows.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), "text is not in 'mdformat'."

        tokens = parse(text)

        result: int = 0
        depth: int = 0
        for tok in tokens:
            depth_at_entry = depth
            depth += tok.nesting

            m = tok.map
            if not m or len(m) != 2:
                continue

            if depth_at_entry == 0 and (_is_heading(tok) or _is_block_quote(tok) or _is_comment(tok)):
                return m[0]

            result = max(result, m[1])

        return result

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Return this answer's raw markdown text verbatim (or `""` if unset)."""
        return self._value


class QaQuestionAnswer(MarkdownStr):
    """One adjacent question/answer pair, with no heading of its own (QA v2).

    All three fields are independently optional. A comment with nothing
    recognizable following it (end of section, or another heading right
    after) becomes its own final `QaQuestionAnswer` with only `comment` set
    (`question`/`answer` both `None`) -- accepted, not an error.

    No override of `from_text`/`__str__`/`_get_field_names()` is needed --
    all three fields are plain `Optional[SingleClass]`, which the generic,
    unmodified `MarkdownStr` engine already distributes/renders correctly.

    Parameters
    ----------
    comment:
        Optional leading `<!-- ... -->` comment, belonging to the question
        that follows it.
    question:
        The interviewer's question, as a block quote. Optional.
    answer:
        The interviewee's free-form prose answer. Optional.
    """

    comment: MarkdownComment | None = Field(
        default=None, description="Optional explanatory HTML comment (`<!-- ... -->`), belongs to `question`."
    )
    question: MarkdownBlockQuote | None = Field(
        default=None, description="The interviewer's question, as a block quote. Optional."
    )
    answer: QaAnswer | None = Field(default=None, description="Free-form prose answer. Optional.")

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return this pair's own extent, as a line count, as the sum of its fields' own extents.

        No class elsewhere in this codebase computes a composite's own
        extent this way (every other composite is either heading-bounded or
        a single pre-grouped markdown-it token) -- this is a local,
        throwaway mechanism for `qa/models/v2/` only (see this module's
        docstring).

        Rather than calling each field's own `get_extent` on successively
        re-normalized substrings (which would silently under-count: a raw
        substring can start with a blank separator line that `mdformat`
        would strip, exactly the class of bug `process_list_field`'s own
        docstring in `markdown_str.py` already documents), this walks the
        *same* single token stream `MarkdownStr.get_extent`'s continuous
        scan already uses, tracking which of `comment`/`question` have
        already been matched for *this* pair:

        - A depth-0 heading (any level) always stops the scan.
        - A depth-0 comment stops the scan unless it is the very first thing
          encountered for this pair (i.e. `comment` not yet matched, and no
          other content yet accumulated) -- otherwise it is either a second
          comment or a comment following already-started answer prose,
          either way belonging to the *next* pair.
        - A depth-0 block quote stops the scan unless `question` has not yet
          been matched and no other content has yet been accumulated for
          this pair -- otherwise it is either a second question or a block
          quote appearing after answer prose has already started, either way
          belonging to the *next* pair.
        - Anything else at depth 0 (a paragraph, a list, ...) is `answer`
          prose: once any such content has been seen, no further depth-0
          comment/block quote can still be *this* pair's own `question`.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: nothing matches at all (the enclosing `list[QaQuestionAnswer]`,
                and therefore the whole category section, may legitimately be
                empty).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by
                this pair's own `comment`/`question`/`answer`, stopping
                before the next pair (or the next heading), or at the end of
                `text` if neither follows.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), "text is not in 'mdformat'."

        tokens = parse(text)

        result: int = 0
        depth: int = 0
        seen_comment: bool = False
        seen_question: bool = False
        content_seen: bool = False
        for tok in tokens:
            depth_at_entry = depth
            depth += tok.nesting

            m = tok.map
            if not m or len(m) != 2:
                continue

            if depth_at_entry == 0:
                if _is_heading(tok):
                    return result
                if _is_comment(tok):
                    if seen_comment or seen_question or content_seen:
                        return result
                    seen_comment = True
                elif _is_block_quote(tok):
                    if seen_question or content_seen:
                        return result
                    seen_question = True
                else:
                    content_seen = True

            result = max(result, m[1])

        return result
