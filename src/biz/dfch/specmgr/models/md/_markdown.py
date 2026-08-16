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
    return mdformat.text(text, options=_MDFORMAT_OPTIONS)


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


def _assert_no_raw_html(tokens: list[Token]) -> None:
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
    """
    for tok in tokens:
        tok_type = tok.type.lower()
        message = f"raw HTML is not permitted in a parsed document: {tok.type} {tok.content!r}"
        if tok_type in (_RAW_HTML_TOKEN_TYPE_BLOCK, _RAW_HTML_TOKEN_TYPE_INLINE):
            assert tok.content.startswith(_ALLOWED_RAW_HTML_PREFIX), message

        if tok.children:
            _assert_no_raw_html(tok.children)


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
            `.children`).
    """
    assert isinstance(text, str), type(text)
    tokens = md.parse(text)
    _assert_no_raw_html(tokens)
    return tokens
