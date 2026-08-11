# `biz.dfch.specmgr.server`

MCP server for ``biz-dfch-specmgr``.

Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).

Registers the following resources and tools so far (plan §8, §9a):

Resources
---------
specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
specmgr://adr/list --   Ids/titles/statuses/filenames of every ADR
                        (``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md``).
specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md``).

Tools
-----
ADR tools (``adr/tools/``): ``get_adr``, ``create_adr``, ``update_frontmatter``,
``update_section``, ``set_status``, ``option_list``, ``option_create``,
``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.

Prompts
-------
ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-0-doc-in-specmgr/adr-tool-plan.md``
§11).

Modules are grouped domain-first
(ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
document-type domain"): each document
domain (``adr``, and later ``req``/``uc``/``ac``) is a top-level package
with its own ``tools``/``prompts``/``resources`` sub-packages, self-
registered via the domain package's own ``__init__.py``. Cross-cutting,
non-domain-specific resources (e.g. ``specmgr://version``) stay under the
top-level ``resources`` package instead. Add a new domain by creating its
top-level package and importing it at the bottom of this module, next to
the existing ``adr``/``resources`` import, so its ``@mcp.tool()`` /
``@mcp.prompt()`` / ``@mcp.resource()`` decorators actually run.

## Functions

### `_lifespan(_server: 'MCPServer') -> 'AsyncGenerator[None, None]'`

Placeholder lifespan: no shared state to initialise yet.

