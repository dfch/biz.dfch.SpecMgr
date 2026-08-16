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

"""``mdformat`` -- format a markdown file the same way the MCP server does.

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
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown

from ..models.md._markdown import format_markdown_document


def mdformat(
    path: Annotated[
        Path, typer.Argument(help="Path to the markdown file to format.", file_okay=True, dir_okay=False, exists=True)
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-d",
            help="Show the formatted result on the console; do not write to disk.",
        ),
    ] = False,
) -> None:
    """Format the markdown file at `path`, the same way the MCP server does.

    Reads `path`, normalizes it via `format_markdown_document` (YAML
    frontmatter, if present, is preserved verbatim; only the body is
    reformatted -- e.g. ordered lists are renumbered consecutively), and
    either writes the result back to disk or, with `--dry-run`/`-d`, prints
    it to the console instead. No content validation is performed.

    Exits with status 1 if the formatted content differs from the original
    (whether or not `--dry-run` was passed), or 0 if the file was already in
    canonical form. With `--dry-run`, the file on disk is never modified,
    regardless of the exit code.
    """

    assert isinstance(path, Path), type(path)

    original_text = path.read_text(encoding="utf-8")
    changed, formatted_text = format_markdown_document(original_text)

    if dry_run and changed:
        console = Console()
        console.print(Markdown(formatted_text))
    elif changed:
        path.write_text(formatted_text, encoding="utf-8")

    if changed:
        raise typer.Exit(1)
