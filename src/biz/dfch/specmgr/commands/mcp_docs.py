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

"""``mcp-docs`` -- regenerate docs/MCP.md from the live MCP server registration.

Imports ``biz.dfch.specmgr.server:mcp`` (which, as a side effect, imports
every domain package so all ``@mcp.tool()``/``@mcp.resource()``/
``@mcp.prompt()`` decorators run -- see ``server.py``) and introspects it at
runtime via its public ``list_tools``/``list_resources``/
``list_resource_templates``/``list_prompts`` methods, rather than statically
parsing decorators via ``ast`` (contrast ``commands/docs.py``). This means
the generated reference can never drift from what the server actually
registers -- there is no separate catalog to keep in sync by hand.

Writes a single Markdown file (default ``docs/MCP.md``) with one table per
kind (Resources, Resource Templates, Tools, Prompts), each row linking to a
per-item subsection with description, parameters/arguments, and (for
resources) MIME type. Run this after adding/renaming/removing any tool,
resource, or prompt and commit the result -- see ``AGENTS.md``
"Developer Commands".
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Any

import typer

# __file__ = src/biz/dfch/specmgr/commands/mcp_docs.py
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent  # repo root
_DEFAULT_OUTPUT = _REPO_ROOT / "docs" / "MCP.md"


# ---------------------------------------------------------------------------
# JSON Schema -> short human-readable type string
# ---------------------------------------------------------------------------


def _schema_type_str(prop_schema: dict[str, Any]) -> str:
    """Render a single JSON Schema property as a short type string.

    Resolves ``$ref`` to the referenced definition's bare name (e.g.
    ``#/$defs/AdrBody`` -> ``AdrBody``), collapses ``anyOf`` (typically an
    optional field's ``[T, null]`` union) into ``T | None``, renders
    ``array`` as ``list[T]``, and surfaces a closed ``enum`` (e.g. the
    generic ``update`` tool's 7-value ``type``) as
    ``T (enum: v1, v2, ...)`` -- the enum's values are part of the
    contract, not an implementation detail. Falls back to ``"any"`` when
    no recognizable shape is present -- this is a best-effort summary for
    documentation, not a full schema renderer.
    """
    if "$ref" in prop_schema:
        return str(prop_schema["$ref"]).rsplit("/", maxsplit=1)[-1]

    if "anyOf" in prop_schema:
        parts = [_schema_type_str(sub) for sub in prop_schema["anyOf"]]
        # Normalize a plain JSON Schema "null" branch to Python's "None".
        parts = ["None" if p == "null" else p for p in parts]
        return " | ".join(parts)

    schema_type = prop_schema.get("type")
    if schema_type == "array":
        items = prop_schema.get("items", {})
        return f"list[{_schema_type_str(items)}]"
    if schema_type == "null":
        return "None"
    if isinstance(schema_type, str):
        enum_values = prop_schema.get("enum")
        if enum_values is not None:
            values = ", ".join(str(value) for value in enum_values)
            return f"{schema_type} (enum: {values})"
        return schema_type

    return "any"


def _tool_parameters(input_schema: dict[str, Any]) -> list[tuple[str, str, bool]]:
    """Extract (name, type, required) tuples from a tool's top-level input schema.

    Only looks at top-level ``properties``/``required`` -- nested
    ``$defs`` (Pydantic model field docs, which can run to many
    paragraphs) are deliberately not unpacked; the resolved ``$ref`` name
    is shown as the type instead, keeping the generated table readable.
    """
    properties: dict[str, Any] = input_schema.get("properties", {})
    required: set[str] = set(input_schema.get("required") or [])

    result: list[tuple[str, str, bool]] = []
    for name, prop_schema in properties.items():
        result.append((name, _schema_type_str(prop_schema), name in required))
    return result


# ---------------------------------------------------------------------------
# docs/MCP.md generation
# ---------------------------------------------------------------------------


async def _collect_registration() -> dict[str, list[Any]]:
    """Call the four ``list_*`` methods on the live ``mcp`` server instance."""
    from ..server import mcp  # deferred: importing server registers every domain's tools

    return {
        "tools": sorted(await mcp.list_tools(), key=lambda t: t.name),
        "resources": sorted(await mcp.list_resources(), key=lambda r: r.name),
        "resource_templates": sorted(await mcp.list_resource_templates(), key=lambda t: t.name),
        "prompts": sorted(await mcp.list_prompts(), key=lambda p: p.name),
    }


def _render_index_table(rows: list[tuple[str, str]]) -> list[str]:
    """Render a two-column ``Name | Description`` Markdown table linking into subsections."""
    lines = ["| Name | Description |", "| --- | --- |"]
    for anchor_text, description in rows:
        lines.append(f"| {anchor_text} | {description} |")
    lines.append("")
    return lines


def _slugify(heading: str) -> str:
    """GitHub-style Markdown heading slug: lowercase, drop punctuation, spaces -> hyphens.

    Headings below are always prefixed with their kind (``"Resource: ..."``,
    ``"Tool: ..."``, ...) specifically so their slugs stay unique even when
    the same bare name is reused across kinds (e.g. the ``create_adr`` tool
    and the ``create_adr`` prompt) -- this function does not attempt to
    reproduce GitHub's ``-1``/``-2``/... duplicate-heading suffixing, which
    would otherwise have to be guessed and kept in lock-step by hand.
    """
    keep = "".join(ch for ch in heading.lower() if ch.isalnum() or ch in " -_")
    return keep.replace(" ", "-")


def generate_mcp_docs() -> str:
    """Generate the full contents of ``docs/MCP.md`` from the live MCP server registration."""
    registration = asyncio.run(_collect_registration())
    tools = registration["tools"]
    resources = registration["resources"]
    resource_templates = registration["resource_templates"]
    prompts = registration["prompts"]

    lines: list[str] = [
        "# MCP Server Reference",
        "",
        "Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --",
        "do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).",
        "",
        f"{len(resources)} resource(s), {len(resource_templates)} resource template(s), "
        f"{len(tools)} tool(s), {len(prompts)} prompt(s).",
        "",
        "## Table of Contents",
        "",
        "- [Resources](#resources)",
        "- [Resource Templates](#resource-templates)",
        "- [Tools](#tools)",
        "- [Prompts](#prompts)",
        "",
    ]

    # -- Resources --------------------------------------------------------
    lines.append("## Resources")
    lines.append("")
    if resources:
        lines += _render_index_table(
            [(f"[`{r.uri}`](#{_slugify(f'Resource: {r.name}')})", r.description or "") for r in resources]
        )
        for r in resources:
            lines.append(f"### Resource: {r.name}")
            lines.append("")
            lines.append(f"- **URI:** `{r.uri}`")
            if r.mime_type:
                lines.append(f"- **MIME type:** `{r.mime_type}`")
            lines.append("")
            if r.description:
                lines.append(r.description)
                lines.append("")
    else:
        lines.append("_No resources registered._")
        lines.append("")

    # -- Resource Templates -------------------------------------------------
    lines.append("## Resource Templates")
    lines.append("")
    if resource_templates:
        lines += _render_index_table(
            [
                (f"[`{t.uri_template}`](#{_slugify(f'Resource Template: {t.name}')})", t.description or "")
                for t in resource_templates
            ]
        )
        for t in resource_templates:
            lines.append(f"### Resource Template: {t.name}")
            lines.append("")
            lines.append(f"- **URI template:** `{t.uri_template}`")
            if t.mime_type:
                lines.append(f"- **MIME type:** `{t.mime_type}`")
            lines.append("")
            if t.description:
                lines.append(t.description)
                lines.append("")
    else:
        lines.append("_No resource templates registered._")
        lines.append("")

    # -- Tools --------------------------------------------------------------
    lines.append("## Tools")
    lines.append("")
    if tools:
        lines += _render_index_table(
            [(f"[`{t.name}`](#{_slugify(f'Tool: {t.name}')})", t.description or "") for t in tools]
        )
        for t in tools:
            lines.append(f"### Tool: {t.name}")
            lines.append("")
            if t.title and t.title != t.name:
                lines.append(f"**{t.title}**")
                lines.append("")
            if t.description:
                lines.append(t.description)
                lines.append("")
            params = _tool_parameters(t.input_schema)
            if params:
                lines.append("| Parameter | Type | Required |")
                lines.append("| --- | --- | --- |")
                for name, type_str, is_required in params:
                    lines.append(f"| `{name}` | `{type_str}` | {'Yes' if is_required else 'No'} |")
                lines.append("")
    else:
        lines.append("_No tools registered._")
        lines.append("")

    # -- Prompts --------------------------------------------------------------
    lines.append("## Prompts")
    lines.append("")
    if prompts:
        lines += _render_index_table(
            [(f"[`{p.name}`](#{_slugify(f'Prompt: {p.name}')})", p.description or "") for p in prompts]
        )
        for p in prompts:
            lines.append(f"### Prompt: {p.name}")
            lines.append("")
            if p.description:
                lines.append(p.description)
                lines.append("")
            if p.arguments:
                lines.append("| Argument | Required | Description |")
                lines.append("| --- | --- | --- |")
                for arg in p.arguments:
                    lines.append(f"| `{arg.name}` | {'Yes' if arg.required else 'No'} | {arg.description or ''} |")
                lines.append("")
    else:
        lines.append("_No prompts registered._")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def mcp_docs(
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to write the reference Markdown into (default: docs/MCP.md).",
        ),
    ] = None,
) -> None:
    """Regenerate ``docs/MCP.md`` from the live MCP server registration.

    Requires the ``mcp`` extra (imports ``biz.dfch.specmgr.server``). Pass
    ``--output`` to write elsewhere instead. Run this after adding,
    renaming, or removing any tool, resource, or prompt and commit the
    result (see ``AGENTS.md``).
    """
    output_path = output if output is not None else _DEFAULT_OUTPUT

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_mcp_docs(), encoding="utf-8")
    typer.echo(f"✓ Wrote {output_path}")
