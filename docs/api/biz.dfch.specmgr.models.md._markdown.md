# `biz.dfch.specmgr.models.md._markdown`

Markdown shared instance.

## Functions

### `_assert_no_raw_html(tokens: list[markdown_it.token.Token], _fallback_map: tuple[int, int] | None = None) -> None`

Raise if any token in `tokens` (recursively, including `.children`) is raw HTML.

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


### `_first_differing_line(actual: str, expected: str) -> tuple[int, str, str]`

Return the 1-based line number and both lines at the first point `actual`/`expected` differ.

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


### `_raw_html_message(tok: markdown_it.token.Token, own_map: tuple[int, int] | None) -> str`

Build the enriched raw-HTML rejection message for `tok` (REQ-002/REQ-003).

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


### `format_markdown_document(text: str) -> tuple[bool, str]`

Normalize a whole markdown document, preserving any leading YAML frontmatter block.

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


### `format_text(text: str) -> str`

Normalize `text` with the shared `mdformat` options (see `_MDFORMAT_OPTIONS`).

Every module under `models/md/` must call this instead of calling
`mdformat.text(text)` directly, so the whole engine normalizes
consistently -- `get_extent`/`from_text`'s `text == format_text(text)`
precondition would otherwise fail as soon as two call sites disagreed on
options.

Args:
    text: Markdown source to normalize.

Returns:
    The `mdformat`-normalized text.


### `not_in_mdformat_message(text: str) -> str`

Build the enriched message for the `text == format_text(text)` precondition (REQ-002/REQ-003).

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


### `parse(text: str) -> list[markdown_it.token.Token]`

Tokenize `text` with the shared `md` instance, rejecting raw HTML (REQ-005).

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


### `snippet(text: str, max_lines: int = 5, max_chars: int = 300) -> str`

Return a truncated snippet of `text` for use in an error message.

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

