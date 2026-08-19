# `biz.dfch.specmgr.commands.mcp`

``mcp`` -- start the ``biz-dfch-specmgr`` MCP server.

Additionally requires the ``mcp`` extra
(``pip install biz-dfch-specmgr[mcp]``). Supports three transport modes:

* **stdio** (default) — the host process communicates over stdin/stdout;
  suitable for OpenCode and other MCP hosts that launch the server
  as a subprocess::

      specmgr mcp
      uv run specmgr mcp
      python -m biz.dfch.specmgr mcp

* **SSE / network** — the server binds a TCP port and accepts HTTP
  connections; suitable for cloud deployments::

      specmgr mcp --transport sse --host localhost --port 8000

* **streamable-http / network** — the spec-current HTTP transport,
  replacing the legacy/deprecated ``sse`` transport for HTTP
  deployments; also binds a TCP port::

      specmgr mcp --transport streamable-http --host localhost --port 8000

Environment variables (all optional, CLI flags take precedence):

``SPECMGR_MCP_TRANSPORT``
    ``stdio`` (default), ``sse``, or ``streamable-http``.
``SPECMGR_MCP_HOST``
    Bind address for SSE/streamable-http mode (default ``localhost``).
``SPECMGR_MCP_PORT``
    TCP port for SSE/streamable-http mode (default ``8000``).

## Functions

### `_warn_on_public_binding(host: str) -> None`

Warn when binding to all interfaces outside a container.


### `mcp(transport: Annotated[str, <typer.models.OptionInfo object>] = 'stdio', host: Annotated[str, <typer.models.OptionInfo object>] = 'localhost', port: Annotated[int, <typer.models.OptionInfo object>] = 8000) -> None`

Start the ``biz-dfch-specmgr`` MCP server.

