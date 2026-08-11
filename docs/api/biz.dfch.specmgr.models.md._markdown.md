# `biz.dfch.specmgr.models.md._markdown`

Markdown shared instance.

## Functions

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

