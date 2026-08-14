# `biz.dfch.specmgr.models.md._markdown`

Markdown shared instance.

## Functions

### `_assert_no_raw_html(tokens: list[markdown_it.token.Token]) -> None`

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
        `.children`).

