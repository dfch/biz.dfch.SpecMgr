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

"""Markdown shared instance."""

from itertools import zip_longest

import frontmatter
import mdformat
from markdown_it import MarkdownIt
from markdown_it.token import Token

md = MarkdownIt("commonmark")

#: Token types that mark raw HTML (REQ-005). `"html_block"` always appears in
#: the flat top-level token list; `"html_inline"` only ever appears nested
#: inside an `"inline"` token's own `.children` (verified empirically -- the
#: shared `md` instance's default inline-token representation keeps inline
#: children nested, it does not flatten them into the top-level list), which
#: is why `_assert_no_raw_html` below recurses into `.children` rather than
#: scanning the top-level list alone.
_RAW_HTML_TOKEN_TYPE_BLOCK = "html_block"
_RAW_HTML_TOKEN_TYPE_INLINE = "html_inline"

#: Both `"html_block"` and `"html_inline"` are permitted when their own
#: `.content` starts with this prefix (an HTML comment, e.g. `<!-- note -->`)
#: -- see `_assert_no_raw_html` (feat-6-requirement-artifact Task 3.20). Any
#: other raw HTML (an actual tag) of either kind is still rejected.
_ALLOWED_RAW_HTML_PREFIX = "<!--"

#: `mdformat` options shared by every normalization call across `models/md/`.
#:
#: `number=True` switches `mdformat`'s ordered-list renderer from its default
#: behavior (collapsing every item's marker to `"1."`, since CommonMark only
#: treats a list's *first* number as semantically meaningful) to genuine
#: consecutive numbering (`"1."`, `"2."`, `"3."`, ...) derived from each
#: item's position. This is required for `MarkdownListItem`-based ordered
#: lists to round-trip their real numbering at all -- without it, the
#: `text == format_text(text)` invariant every `get_extent`/`from_text`
#: implementation asserts would hold, but only by *destroying* the original
#: sequential numbers on the very first normalization pass. It has no effect
#: on bullet lists, headings, or paragraphs.
_MDFORMAT_OPTIONS = {"number": True}

#: `mdformat.parser_extension` plugins enabled for every normalization call
#: across `models/md/`. `"simple_breaks"` (package `mdformat-simple-breaks`,
#: pinned exactly in `pyproject.toml`) overrides `mdformat`'s hardcoded `hr`
#: renderer (`"_" * 70`, not otherwise configurable -- see
#: executablebooks/mdformat#69) so a thematic break renders as a literal
#: `---` instead, regardless of whether the source used `---`, `***`, or
#: `___` (GitHub issue #47).
_MDFORMAT_EXTENSIONS = {"simple_breaks"}


def format_text(text: str) -> str:
    """Normalize `text` with the shared `mdformat` options (see `_MDFORMAT_OPTIONS`).

    Every module under `models/md/` must call this instead of calling
    `mdformat.text(text)` directly, so the whole engine normalizes
    consistently -- `get_extent`/`from_text`'s `text == format_text(text)`
    precondition would otherwise fail as soon as two call sites disagreed on
    options.

    Args:
        text: Markdown source to normalize.

    Returns:
        The `mdformat`-normalized text.
    """
    assert isinstance(text, str), type(text)
    return mdformat.text(text, options=_MDFORMAT_OPTIONS, extensions=_MDFORMAT_EXTENSIONS)


def snippet(text: str, max_lines: int = 5, max_chars: int = 300) -> str:
    """Return a truncated snippet of `text` for use in an error message.

    Shared by every message-building helper across `models/md/` that needs
    to show the caller a short excerpt of the offending text (REQ-002),
    rather than dumping a whole (potentially huge) document into an
    exception message.

    Args:
        text: the markdown text to excerpt.
        max_lines: maximum number of lines to include before truncating.
        max_chars: maximum number of characters to include before truncating.

    Returns:
        A snippet of up to `max_lines` lines and `max_chars` characters,
        with a "... (truncated)" suffix if either limit was exceeded.
    """
    lines = text.splitlines()
    truncated_lines = lines[:max_lines]
    result = "\n".join(truncated_lines)

    if len(lines) > max_lines or len(result) > max_chars:
        result = result[:max_chars]
        result = f"{result}... (truncated)"
    return result


def _first_differing_line(actual: str, expected: str) -> tuple[int, str, str]:
    """Return the 1-based line number and both lines at the first point `actual`/`expected` differ.

    Args:
        actual: the text as received (not, or not yet, `mdformat`-normalized).
        expected: `format_text(actual)`, the normalized text.

    Returns:
        `(line_no, actual_line, expected_line)`. `line_no` is 1-based,
        relative to both `actual` and `expected`'s own line numbering (the
        two agree up to and including the returned line number minus one).
        `actual_line`/`expected_line` are `"<end of text>"` when one side
        has fewer lines than the other at that position. `(0, "", "")` if
        `actual == expected` (no difference at all -- unreachable via
        `not_in_mdformat_message` below, which is only ever called once the
        caller's own `text == format_text(text)` check has already failed).
    """
    actual_lines = actual.splitlines()
    expected_lines = expected.splitlines()
    for line_no, (actual_line, expected_line) in enumerate(zip_longest(actual_lines, expected_lines), start=1):
        if actual_line != expected_line:
            result = (
                line_no,
                actual_line if actual_line is not None else "<end of text>",
                expected_line if expected_line is not None else "<end of text>",
            )
            return result
    return 0, "", ""


def not_in_mdformat_message(text: str) -> str:
    """Build the enriched message for the `text == format_text(text)` precondition (REQ-002/REQ-003).

    Every `get_extent`/`from_text` implementation across `models/md/`
    asserts this precondition against its own `text` argument before doing
    anything else -- callers must always pre-normalize with `format_text`.
    A violation is usually a caller bug (an un-normalized slice handed to
    the engine), not a document-authoring mistake, so this message states
    exactly where `text` first diverges from its own `mdformat`-normalized
    form instead of the previous bare "text is not in 'mdformat'.".

    Args:
        text: the text that failed `text == format_text(text)`.

    Returns:
        A message naming the 1-based line (relative to `text`'s own
        numbering, stated as such) and content of the first line at which
        `text` and `format_text(text)` disagree -- or, when every line
        compares equal under `str.splitlines()` (e.g. `text` is missing
        its single trailing newline, which `splitlines()` does not turn
        into an extra empty line), a message naming that instead.
    """
    assert isinstance(text, str), type(text)
    formatted = format_text(text)
    line_no, actual_line, expected_line = _first_differing_line(text, formatted)
    if line_no == 0:
        return (
            "text is not in 'mdformat' -- every line matches, but the text still differs (typically a "
            f"missing/extra trailing newline): got {text!r}, mdformat produces {formatted!r}"
        )
    return (
        f"text is not in 'mdformat' -- first difference at line {line_no} (relative to this text's own "
        f"numbering): got {actual_line!r}, mdformat produces {expected_line!r}"
    )


def format_markdown_document(text: str) -> tuple[bool, str]:
    """Normalize a whole markdown document, preserving any leading YAML frontmatter block.

    Parses `text` for a leading YAML frontmatter block (as recognized by the
    `frontmatter` library). If present, only the body is normalized via
    `format_text` and the frontmatter is re-serialized (key order may change,
    value types/quoting may normalize, but content is never altered). If no
    frontmatter is present, the whole text is normalized via `format_text`.
    Exactly one trailing newline is then enforced.

    This is the single shared implementation behind both the `mdformat`
    MCP tool (`general.tools.mdformat`) and the `mdformat` CLI command
    (`commands.mdformat`); both compare `text` against `formatted_text` to
    decide whether a file needs to be (re)written.

    Args:
        text: The complete file content (YAML frontmatter block and markdown
            body together, or plain markdown with no frontmatter).

    Returns:
        A `(changed, formatted_text)` pair. `changed` is `True` iff
        `formatted_text != text`.
    """
    assert isinstance(text, str), type(text)

    post = frontmatter.loads(text)
    if post.metadata:
        post.content = format_text(post.content)
        formatted_text = frontmatter.dumps(post)
    else:
        formatted_text = format_text(text)

    if not formatted_text.endswith("\n"):
        formatted_text += "\n"

    changed = formatted_text != text
    return changed, formatted_text


def _raw_html_message(tok: Token, own_map: tuple[int, int] | None) -> str:
    """Build the enriched raw-HTML rejection message for `tok` (REQ-002/REQ-003).

    Args:
        tok: the offending `"html_block"`/`"html_inline"` token.
        own_map: `tok.map` if it has one, else the nearest ancestor
            (block-level) token's own `.map` -- an `"html_inline"` token
            nested inside an `"inline"` token's `.children` never carries a
            `.map` of its own, so `_assert_no_raw_html` passes its parent's
            down as a fallback (see that function's docstring).

    Returns:
        A message naming the token kind/content, a line reference (when
        `own_map` is available) relative to whatever text `parse()` was
        called with, and a fix hint for the two documented remedies (wrap
        in a code span, or write it as an HTML comment).
    """
    where = f" at line {own_map[0] + 1} (relative to this text's own numbering)" if own_map else ""
    content = tok.content.strip()
    return (
        f"raw HTML is not permitted in a parsed document{where}: {tok.type} {content!r}; "
        f"fix: wrap it in a code span (e.g. `{content}`) or write it as an HTML comment "
        f"(e.g. `<!-- {content} -->`) instead"
    )


def _assert_no_raw_html(tokens: list[Token], _fallback_map: tuple[int, int] | None = None) -> None:
    """Raise if any token in `tokens` (recursively, including `.children`) is raw HTML.

    An `"html_block"` or `"html_inline"` token is permitted, not rejected,
    when its own `.content` starts with `_ALLOWED_RAW_HTML_PREFIX` (an HTML
    comment) -- both an already-established exception for `"html_block"`
    (e.g. `<!-- note -->` on its own line) and, since
    feat-6-requirement-artifact Task 3.20, the same exception for
    `"html_inline"` (e.g. an inline `MUST <!-- one of: ... -->` annotation on
    the same line as a value). Any other raw HTML (an actual tag, either
    kind) is still rejected.

    Args:
        tokens: a token list, or a token's own `.children`.
        _fallback_map: the nearest ancestor (block-level) token's own
            `.map`, used as the line reference for a nested child token
            (typically an `"html_inline"` token inside an `"inline"`
            token's `.children`) that has no `.map` of its own.
    """
    for tok in tokens:
        own_map = tok.map if tok.map else _fallback_map
        tok_type = tok.type.lower()
        if tok_type in (_RAW_HTML_TOKEN_TYPE_BLOCK, _RAW_HTML_TOKEN_TYPE_INLINE):
            assert tok.content.startswith(_ALLOWED_RAW_HTML_PREFIX), _raw_html_message(tok, own_map)

        if tok.children:
            _assert_no_raw_html(tok.children, _fallback_map=own_map)


def parse(text: str) -> list[Token]:
    """Tokenize `text` with the shared `md` instance, rejecting raw HTML (REQ-005).

    Every module under `models/md/` must call this instead of calling
    `md.parse(text)` directly, so raw HTML (both HTML blocks and inline HTML
    tags) is rejected consistently everywhere text gets tokenized -- the same
    "one shared call site" convention `format_text` above already
    establishes for `mdformat` normalization options.

    Args:
        text: Markdown source to tokenize.

    Returns:
        The token list `md.parse(text)` would have returned.

    Raises:
        AssertionError: `text` contains an `html_block` or `html_inline`
            token anywhere (including nested inside an `"inline"` token's
            `.children`) whose content is not an HTML comment. The message
            (see `_raw_html_message`) names the offending token/content, a
            line reference when available, and the fix (a code span or an
            HTML comment).
    """
    assert isinstance(text, str), type(text)
    tokens = md.parse(text)
    _assert_no_raw_html(tokens)
    return tokens
