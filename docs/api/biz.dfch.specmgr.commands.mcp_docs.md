# `biz.dfch.specmgr.commands.mcp_docs`

``mcp-docs`` -- regenerate docs/MCP.md from the live MCP server registration.

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

## Functions

### `_collect_registration() -> 'dict[str, list[Any]]'`

Call the four ``list_*`` methods on the live ``mcp`` server instance.


### `_render_index_table(rows: 'list[tuple[str, str]]') -> 'list[str]'`

Render a two-column ``Name | Description`` Markdown table linking into subsections.


### `_schema_type_str(prop_schema: 'dict[str, Any]') -> 'str'`

Render a single JSON Schema property as a short type string.

Resolves ``$ref`` to the referenced definition's bare name (e.g.
``#/$defs/AdrBody`` -> ``AdrBody``), collapses ``anyOf`` (typically an
optional field's ``[T, null]`` union) into ``T | None``, renders
``array`` as ``list[T]``, and surfaces a closed ``enum`` (e.g. the
generic ``update`` tool's 7-value ``type``) as
``T (enum: v1, v2, ...)`` -- the enum's values are part of the
contract, not an implementation detail. Falls back to ``"any"`` when
no recognizable shape is present -- this is a best-effort summary for
documentation, not a full schema renderer.


### `_slugify(heading: 'str') -> 'str'`

GitHub-style Markdown heading slug: lowercase, drop punctuation, spaces -> hyphens.

Headings below are always prefixed with their kind (``"Resource: ..."``,
``"Tool: ..."``, ...) specifically so their slugs stay unique even when
the same bare name is reused across kinds (e.g. the ``create_adr`` tool
and the ``create_adr`` prompt) -- this function does not attempt to
reproduce GitHub's ``-1``/``-2``/... duplicate-heading suffixing, which
would otherwise have to be guessed and kept in lock-step by hand.


### `_tool_parameters(input_schema: 'dict[str, Any]') -> 'list[tuple[str, str, bool]]'`

Extract (name, type, required) tuples from a tool's top-level input schema.

Only looks at top-level ``properties``/``required`` -- nested
``$defs`` (Pydantic model field docs, which can run to many
paragraphs) are deliberately not unpacked; the resolved ``$ref`` name
is shown as the type instead, keeping the generated table readable.


### `generate_mcp_docs() -> 'str'`

Generate the full contents of ``docs/MCP.md`` from the live MCP server registration.


### `mcp_docs(output: "Annotated[Path | None, typer.Option('--output', '-o', help='Path to write the reference Markdown into (default: docs/MCP.md).')]" = None) -> 'None'`

Regenerate ``docs/MCP.md`` from the live MCP server registration.

Requires the ``mcp`` extra (imports ``biz.dfch.specmgr.server``). Pass
``--output`` to write elsewhere instead. Run this after adding,
renaming, or removing any tool, resource, or prompt and commit the
result (see ``AGENTS.md``).

