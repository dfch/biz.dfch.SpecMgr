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

"""``mcp`` -- start the ``biz-dfch-specmgr`` MCP server.

Additionally requires the ``mcp`` extra
(``pip install biz-dfch-specmgr[mcp]``). Supports two transport modes:

* **stdio** (default) — the host process communicates over stdin/stdout;
  suitable for OpenCode and other MCP hosts that launch the server
  as a subprocess::

      specmgr mcp
      uv run specmgr mcp
      python -m biz.dfch.specmgr mcp

* **SSE / network** — the server binds a TCP port and accepts HTTP
  connections; suitable for cloud deployments::

      specmgr mcp --transport sse --host localhost --port 8000

Environment variables (all optional, CLI flags take precedence):

``SPECMGR_MCP_TRANSPORT``
    ``stdio`` (default) or ``sse``.
``SPECMGR_MCP_HOST``
    Bind address for SSE mode (default ``localhost``).
``SPECMGR_MCP_PORT``
    TCP port for SSE mode (default ``8000``).
"""

import os
import sys
from typing import Annotated

import typer


def _warn_on_public_binding(host: str) -> None:
    """Warn when binding to all interfaces outside a container."""
    if host not in ("0.0.0.0", "::"):
        return
    in_container = (
        os.path.exists("/.dockerenv")
        or bool(os.environ.get("KUBERNETES_SERVICE_HOST"))
        or bool(os.environ.get("RAILWAY_PROJECT_ID"))
        or bool(os.environ.get("RENDER"))
    )
    if not in_container:
        sys.stderr.write(
            f"WARNING: binding specmgr to '{host}' outside a container "
            "exposes it to the local network. Use --host localhost for "
            "local development.\n"
        )


def mcp(
    transport: Annotated[
        str,
        typer.Option(
            "--transport",
            "-t",
            envvar="SPECMGR_MCP_TRANSPORT",
            help="Transport mode: 'stdio' or 'sse'.",
            show_default=True,
        ),
    ] = "stdio",
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            envvar="SPECMGR_MCP_HOST",
            help="Bind address (SSE mode only).",
            show_default=True,
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            envvar="SPECMGR_MCP_PORT",
            help="TCP port (SSE mode only).",
            show_default=True,
        ),
    ] = 8000,
) -> None:
    """Start the ``biz-dfch-specmgr`` MCP server."""
    try:
        from ..server import mcp as mcp_server  # noqa: PLC0415
    except ImportError as ex:
        typer.echo("You must install the `mcp` extra to start this command (`biz-dfch-specmgr[mcp]`).")
        raise typer.Exit(1) from ex

    if transport.lower() == "sse":
        _warn_on_public_binding(host)
        mcp_server.run(transport="sse", host=host, port=port)
    else:
        mcp_server.run(transport="stdio")
