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

"""``adr-toc`` -- generate table of contents for all ADRs in docs/adr.

Scans the ADR base directory (default ``docs/adr``, configurable via
``SPECMGR_ADR_DIR`` environment variable), collects all ADR documents,
and generates a README.md that lists them with their titles, links, and
frontmatter. This table of contents makes it easy to browse all ADRs
at a glance.

Run this after adding new ADRs and commit the result.
"""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from ..adr.tools._paths import adr_base_dir, iter_adr_paths
from ..models.adr import AdrParseError, parse_adr

# __file__ = src/biz/dfch/specmgr/commands/adr_toc.py
_SRC_ROOT = Path(__file__).resolve().parent.parent  # src/biz/dfch/specmgr


def _collect_adr_summaries() -> list[tuple[str, str, str, dict[str, str | None]]]:
    """Collect (id, title, filename, frontmatter_dict) from all valid ADR files in the base directory.

    Returns a sorted list of tuples. Silently skips files that fail to parse.
    """
    base_dir = adr_base_dir()
    summaries: list[tuple[str, str, str, dict[str, str | None]]] = []

    for path in iter_adr_paths(base_dir):
        try:
            content = path.read_text(encoding="utf-8")
            adr = parse_adr(content)
            if adr.frontmatter.id:
                # Build a frontmatter dict with relevant fields
                frontmatter_dict = {
                    "id": adr.frontmatter.id,
                    "status": adr.frontmatter.status,
                    "date": adr.frontmatter.date,
                    "decision-makers": adr.frontmatter.decision_makers,
                    "consulted": adr.frontmatter.consulted,
                    "informed": adr.frontmatter.informed,
                }
                summaries.append((adr.frontmatter.id, adr.body.title, path.name, frontmatter_dict))
        except (AdrParseError, ValidationError):
            # Silently skip unparseable files (e.g. test.md, broken files)
            continue

    # Sort by filename so output is stable and deterministic
    return sorted(summaries, key=lambda x: x[2])


def generate_adr_toc() -> str:
    """Generate the full contents of ``docs/adr/README.md`` (table of contents)."""
    summaries = _collect_adr_summaries()

    lines = [
        "# Architecture Decision Records",
        "",
        "Index of all ADRs in this repository.",
        "",
    ]

    if summaries:
        lines.append("## All ADRs")
        lines.append("")
        for adr_id, title, filename, frontmatter_dict in summaries:
            lines.append(f"- [{title}]({filename})")
            # Add frontmatter fields as indented nested list items (skip None values)
            for key, value in frontmatter_dict.items():
                if value is not None:
                    # Capitalize key for display: "decision-makers" -> "Decision-makers"
                    display_key = key.replace("-", "-").capitalize()
                    lines.append(f"  - {display_key}: {value}")
        lines.append("")
    else:
        lines.append("No ADRs found.")
        lines.append("")

    return "\n".join(lines)


def adr_toc(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to write README.md into (default: docs/adr/README.md).",
        ),
    ] = None,
) -> None:
    """Generate table of contents (README.md) for all ADRs.

    Scans the ADR base directory (default ``docs/adr``, configurable via
    ``SPECMGR_ADR_DIR`` environment variable) and generates a README.md
    that lists all ADRs with their titles, links, and frontmatter.
    Pass ``--output`` to write elsewhere instead. Run this after adding
    new ADRs and commit the result.
    """
    base_dir = adr_base_dir()
    output_path = output if output is not None else base_dir / "README.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_adr_toc(), encoding="utf-8")
    typer.echo(f"✓ Wrote {output_path}")
