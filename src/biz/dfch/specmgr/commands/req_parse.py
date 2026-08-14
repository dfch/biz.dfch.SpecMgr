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

"""``req-parse`` -- parse a REQ markdown file from disk and print it to the terminal.

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
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import frontmatter
import typer
from pydantic import ValidationError
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

from ..models.md._markdown import format_text
from ..req.models.v1.parser import parse_req as _parse_req

_FORMAT_JSON = "json"
_FORMAT_MARKDOWN = "markdown"
_VALID_FORMATS = (_FORMAT_JSON, _FORMAT_MARKDOWN)


def _frontmatter_and_formatted_body(text: str) -> tuple[str, str]:
    """Split `text` into its raw YAML frontmatter block and a formatted markdown body.

    Args:
        text: The complete file content (YAML frontmatter block and markdown
            body together), exactly as read from disk.

    Returns:
        A `(frontmatter_text, formatted_body)` pair. `frontmatter_text` is the
        re-serialized YAML frontmatter block (empty string if `text` carries
        no frontmatter). `formatted_body` is the markdown body normalized via
        `format_text()`, the same helper `general.tools.mdformat` uses --
        `text` itself is never modified on disk.
    """
    assert isinstance(text, str), type(text)

    post = frontmatter.loads(text)  # type: ignore[union-attr]

    frontmatter_text = ""
    if post.metadata:
        frontmatter_only = frontmatter.Post(content="", **post.metadata)
        frontmatter_text = frontmatter.dumps(frontmatter_only)

    formatted_body = format_text(post.content)

    result = (frontmatter_text, formatted_body)
    return result


def req_parse(
    path: Annotated[str, typer.Argument(help="Path to the REQ markdown file to parse.")],
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help=f"Output format ({', '.join(_VALID_FORMATS)}).",
        ),
    ] = _FORMAT_JSON,
) -> None:
    """Parse a REQ markdown file from disk and print it to the terminal.

    Reads `path`, parses it via `req.models.v1.parser.parse_req`, and prints
    the result. With `--format json` (default), prints the full parsed
    document as syntax-highlighted JSON. With `--format markdown`, re-reads
    and reformats the original file's body (`format_text()`, no disk write)
    and prints the frontmatter block plus formatted body via `rich`.

    Exits with status 1 -- printing the original exception's message -- if
    the file cannot be read, or the document fails structural
    (`AssertionError`) or field-level (`pydantic.ValidationError`)
    validation.
    """
    if output_format not in _VALID_FORMATS:
        valid = ", ".join(_VALID_FORMATS)
        typer.echo(f"Unknown --format {output_format!r}; must be one of: {valid}")
        raise typer.Exit(1)

    file_path = Path(path)
    console = Console()

    try:
        text = file_path.read_text(encoding="utf-8")
        document = _parse_req(text)
    except (OSError, AssertionError, ValidationError) as ex:
        typer.echo(f"Error parsing '{path}': {ex}")
        raise typer.Exit(1) from ex

    if output_format == _FORMAT_JSON:
        console.print_json(document.model_dump_json())
        return

    frontmatter_text, formatted_body = _frontmatter_and_formatted_body(text)
    if frontmatter_text:
        console.print(Syntax(frontmatter_text, "yaml"))
    console.print(Markdown(formatted_body))
