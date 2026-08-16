# `biz.dfch.specmgr.commands.mdformat`

``mdformat`` -- format a markdown file the same way the MCP server does.

Thin CLI wrapper around `models.md._markdown.format_markdown_document` -- the
same shared formatting logic the `mdformat` MCP tool
(`general.tools.mdformat`) uses -- so both entry points normalize a markdown
document (numbering ordered lists, YAML frontmatter preserved verbatim, exact
one trailing newline) identically. This command performs no content
validation, only formatting.

Unlike the MCP tool, which always writes the formatted result to disk when it
differs from the original, this command supports ``--dry-run``/``-d`` to show
the formatted result on the console (via `rich.markdown.Markdown`) without
writing anything back to disk.

Exit code carries the "did anything change" signal in both modes:

- ``0``: the file was already in canonical form (no change detected).
- ``1``: a change was detected (and, unless ``--dry-run`` was passed,
  written back to disk).

A missing file, or any other I/O error, is not caught here -- it propagates
naturally as an uncaught exception (Typer reports it and exits non-zero),
consistent with the `mdformat` MCP tool's own behavior.

## Functions

### `mdformat(path: "Annotated[Path, typer.Argument(help='Path to the markdown file to format.', file_okay=True, dir_okay=False, exists=True)]", dry_run: "Annotated[bool, typer.Option('--dry-run', '-d', help='Show the formatted result on the console; do not write to disk.')]" = False) -> 'None'`

Format the markdown file at `path`, the same way the MCP server does.

Reads `path`, normalizes it via `format_markdown_document` (YAML
frontmatter, if present, is preserved verbatim; only the body is
reformatted -- e.g. ordered lists are renumbered consecutively), and
either writes the result back to disk or, with `--dry-run`/`-d`, prints
it to the console instead. No content validation is performed.

Exits with status 1 if the formatted content differs from the original
(whether or not `--dry-run` was passed), or 0 if the file was already in
canonical form. With `--dry-run`, the file on disk is never modified,
regardless of the exit code.

