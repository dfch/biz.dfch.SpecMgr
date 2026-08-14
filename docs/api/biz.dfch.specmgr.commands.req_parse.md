# `biz.dfch.specmgr.commands.req_parse`

``req-parse`` -- parse a REQ markdown file from disk and print it to the terminal.

Read-only, path-based command mirroring `req.tools.parse_req`'s own
`Path(path).read_text(...)` -> `parse_req(text)` flow (no id-based lookup:
REQ has no `_paths.py`/`_io.py` equivalent to ADR's yet, so a raw filesystem
path is required, not an id).

Two output formats:

- ``json`` (default): the full parsed `ReqDocument`, as syntax-highlighted
  JSON (`Console.print_json`).
- ``markdown``: the *original* file re-read, split into its YAML frontmatter
  block and markdown body, the body normalized via the same `format_text()`
  helper `general.tools.mdformat` uses -- but never written back to disk,
  purely for terminal display -- then both rendered via `rich` (frontmatter
  as a YAML `Syntax` block, body as `Markdown`).

Parse errors (missing file, malformed structure, invalid field values) are
caught here and reported with the original exception's message, exiting 1 --
unlike the parser/MCP tool, which deliberately let these propagate uncaught.

## Functions

### `_frontmatter_and_formatted_body(text: 'str') -> 'tuple[str, str]'`

Split `text` into its raw YAML frontmatter block and a formatted markdown body.

Args:
    text: The complete file content (YAML frontmatter block and markdown
        body together), exactly as read from disk.

Returns:
    A `(frontmatter_text, formatted_body)` pair. `frontmatter_text` is the
    re-serialized YAML frontmatter block (empty string if `text` carries
    no frontmatter). `formatted_body` is the markdown body normalized via
    `format_text()`, the same helper `general.tools.mdformat` uses --
    `text` itself is never modified on disk.


### `req_parse(path: "Annotated[str, typer.Argument(help='Path to the REQ markdown file to parse.')]", output_format: 'Annotated[str, typer.Option(\'--format\', \'-f\', help=f"Output format ({\', \'.join(_VALID_FORMATS)}).")]' = 'json') -> 'None'`

Parse a REQ markdown file from disk and print it to the terminal.

Reads `path`, parses it via `req.models.v1.parser.parse_req`, and prints
the result. With `--format json` (default), prints the full parsed
document as syntax-highlighted JSON. With `--format markdown`, re-reads
and reformats the original file's body (`format_text()`, no disk write)
and prints the frontmatter block plus formatted body via `rich`.

Exits with status 1 -- printing the original exception's message -- if
the file cannot be read, or the document fails structural
(`AssertionError`) or field-level (`pydantic.ValidationError`)
validation.

