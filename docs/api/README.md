# API Documentation Index

Auto-generated API documentation for `biz.dfch.specmgr`.

## Modules

### Biz

- [`biz.dfch.specmgr`](biz.dfch.specmgr.md) — The main library init file.
- [`biz.dfch.specmgr.__main__`](biz.dfch.specmgr.__main__.md) — Entry point for ``python -m biz.dfch.specmgr``.
- [`biz.dfch.specmgr.adr`](biz.dfch.specmgr.adr.md) — The Architecture Decision Record (ADR) domain package.
- [`biz.dfch.specmgr.adr.prompts`](biz.dfch.specmgr.adr.prompts.md) — MCP prompt wrappers for Architecture Decision Records (doc/adr-tool-plan.md §11).
- [`biz.dfch.specmgr.adr.prompts.create_adr`](biz.dfch.specmgr.adr.prompts.create_adr.md) — ``@mcp.prompt()``: create_adr (doc/adr-tool-plan.md §11).
- [`biz.dfch.specmgr.adr.prompts.create_adr_test`](biz.dfch.specmgr.adr.prompts.create_adr_test.md) — ``@mcp.prompt()``: create_adr_test (doc/adr-tool-plan.md §11).
- [`biz.dfch.specmgr.adr.prompts.update_adr`](biz.dfch.specmgr.adr.prompts.update_adr.md) — ``@mcp.prompt()``: update_adr (doc/adr-tool-plan.md §11).
- [`biz.dfch.specmgr.adr.prompts.update_adr_test`](biz.dfch.specmgr.adr.prompts.update_adr_test.md) — ``@mcp.prompt()``: update_adr_test (doc/adr-tool-plan.md §11).
- [`biz.dfch.specmgr.adr.resources`](biz.dfch.specmgr.adr.resources.md) — MCP resource registrations for Architecture Decision Records (plan §8, §9a).
- [`biz.dfch.specmgr.adr.resources.adr_get`](biz.dfch.specmgr.adr.resources.adr_get.md) — Resource: specmgr://adr/{id} (plan §8, §9a).
- [`biz.dfch.specmgr.adr.resources.adr_list`](biz.dfch.specmgr.adr.resources.adr_list.md) — Resource: specmgr://adr/list (plan §8, §9a).
- [`biz.dfch.specmgr.adr.tools`](biz.dfch.specmgr.adr.tools.md) — MCP tool wrappers for Architecture Decision Records (plan §6, §8, §10 item 4).
- [`biz.dfch.specmgr.adr.tools._io`](biz.dfch.specmgr.adr.tools._io.md) — Thin file read/write helpers over ``parse_adr``/``render_adr`` (plan §7, §9a).
- [`biz.dfch.specmgr.adr.tools._lock`](biz.dfch.specmgr.adr.tools._lock.md) — Per-document in-process lock guarding ADR mutations (plan §7, §9a).
- [`biz.dfch.specmgr.adr.tools._paths`](biz.dfch.specmgr.adr.tools._paths.md) — ADR base directory resolution, filename slugification, and id -> path
- [`biz.dfch.specmgr.adr.tools.create_adr`](biz.dfch.specmgr.adr.tools.create_adr.md) — ``@mcp.tool()`` wrapper: create_adr (plan §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.get_adr`](biz.dfch.specmgr.adr.tools.get_adr.md) — ``@mcp.tool()`` wrapper: get_adr (plan §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.option_create`](biz.dfch.specmgr.adr.tools.option_create.md) — ``@mcp.tool()`` wrapper: option_create (plan §5, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.option_delete`](biz.dfch.specmgr.adr.tools.option_delete.md) — ``@mcp.tool()`` wrapper: option_delete (plan §5, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.option_list`](biz.dfch.specmgr.adr.tools.option_list.md) — ``@mcp.tool()`` wrapper: option_list (plan §5, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.option_read`](biz.dfch.specmgr.adr.tools.option_read.md) — ``@mcp.tool()`` wrapper: option_read (plan §5, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.option_update`](biz.dfch.specmgr.adr.tools.option_update.md) — ``@mcp.tool()`` wrapper: option_update (plan §5, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.set_status`](biz.dfch.specmgr.adr.tools.set_status.md) — ``@mcp.tool()`` wrapper: set_status (plan §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.update_frontmatter`](biz.dfch.specmgr.adr.tools.update_frontmatter.md) — ``@mcp.tool()`` wrapper: update_frontmatter (plan §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.update_section`](biz.dfch.specmgr.adr.tools.update_section.md) — ``@mcp.tool()`` wrapper: update_section (plan §4, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.adr.tools.validate_adr`](biz.dfch.specmgr.adr.tools.validate_adr.md) — ``@mcp.tool()`` wrapper: validate_adr (plan §7, §8, §9a, §10 item 4).
- [`biz.dfch.specmgr.cli`](biz.dfch.specmgr.cli.md) — Typer CLI entry point for ``biz-dfch-specmgr``.
- [`biz.dfch.specmgr.commands`](biz.dfch.specmgr.commands.md) — commands module.
- [`biz.dfch.specmgr.commands.docs`](biz.dfch.specmgr.commands.docs.md) — ``docs`` -- regenerate ``docs/api/`` and ``docs/GENERATED.md`` from the codebase.
- [`biz.dfch.specmgr.commands.mcp`](biz.dfch.specmgr.commands.mcp.md) — ``mcp`` -- start the ``biz-dfch-specmgr`` MCP server.
- [`biz.dfch.specmgr.commands.version`](biz.dfch.specmgr.commands.version.md) — ``version`` -- print the installed ``biz-dfch-specmgr`` version.
- [`biz.dfch.specmgr.models`](biz.dfch.specmgr.models.md) — Pydantic models used by the ``biz-dfch-specmgr`` MCP server.
- [`biz.dfch.specmgr.models.adr`](biz.dfch.specmgr.models.adr.md) — Pydantic models for MADR 4.0.0-based Architecture Decision Records.
- [`biz.dfch.specmgr.models.adr.v1`](biz.dfch.specmgr.models.adr.v1.md) — ADR schema version 1 (``SCHEMA_MAJOR_VERSION == 1``).
- [`biz.dfch.specmgr.models.adr.v1._util`](biz.dfch.specmgr.models.adr.v1._util.md) — Shared, private validation helpers for the ``models.adr`` subpackage.
- [`biz.dfch.specmgr.models.adr.v1.adr`](biz.dfch.specmgr.models.adr.v1.adr.md) — Pydantic model for a full ADR document (frontmatter + body).
- [`biz.dfch.specmgr.models.adr.v1.body`](biz.dfch.specmgr.models.adr.v1.body.md) — Pydantic model for the ADR body -- whole-section fields plus options
- [`biz.dfch.specmgr.models.adr.v1.frontmatter`](biz.dfch.specmgr.models.adr.v1.frontmatter.md) — Pydantic model for the ADR YAML frontmatter block (plan §3).
- [`biz.dfch.specmgr.models.adr.v1.mutations`](biz.dfch.specmgr.models.adr.v1.mutations.md) — Structured edit operations on an :class:`Adr` (plan §4, §5, §8).
- [`biz.dfch.specmgr.models.adr.v1.option`](biz.dfch.specmgr.models.adr.v1.option.md) — Pydantic model for one ``### Option N: {title}`` sub-section (plan §5).
- [`biz.dfch.specmgr.models.adr.v1.parser`](biz.dfch.specmgr.models.adr.v1.parser.md) — Parse an on-disk ADR ``.md`` file into an :class:`Adr` (plan §7, §10 item 2).
- [`biz.dfch.specmgr.models.adr.v1.renderer`](biz.dfch.specmgr.models.adr.v1.renderer.md) — Render an :class:`Adr` back into the canonical on-disk ``.md`` text (plan §7, §10 item 2).
- [`biz.dfch.specmgr.models.adr.v1.summary`](biz.dfch.specmgr.models.adr.v1.summary.md) — Pydantic model for one line of ADR listing output (plan §8, §9a).
- [`biz.dfch.specmgr.models.version_info`](biz.dfch.specmgr.models.version_info.md) — Pydantic model for the ``specmgr://version`` resource.
- [`biz.dfch.specmgr.resources`](biz.dfch.specmgr.resources.md) — MCP resource registrations that are not specific to any single document
- [`biz.dfch.specmgr.resources.version`](biz.dfch.specmgr.resources.version.md) — Resource: specmgr://version — MCP server package version number.
- [`biz.dfch.specmgr.server`](biz.dfch.specmgr.server.md) — MCP server for ``biz-dfch-specmgr``.
