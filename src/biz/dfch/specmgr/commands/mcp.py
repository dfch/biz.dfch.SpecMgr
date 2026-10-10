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

The three defaults are sourced from the central env-var registry's
records for these variables (registered below; feat-208 Phase 140) and
evaluated to the same static import-time values as before the migration
(``stdio``/``localhost``/``8000``); the ``envvar=`` wiring itself stays
Typer's (Typer reads the variables from the environment at parse time,
overriding the defaults).
"""

import os
import sys
from typing import Annotated

import typer

from .. import _envregistry

# ---------------------------------------------------------------------------
# env-var registration (feat-208, Phase 110; the mcp() option defaults
# sourced from the records, Phase 140)
# ---------------------------------------------------------------------------
# The three Typer MCP options' environment variables, registered at module
# level so the central env-var registry is complete by the time any CLI
# entry point runs (REQ-001, ACC-001). The registry import is safe at
# module level in a `[cli]`-only install (the registry is stdlib-only;
# Design Notes "Registry placement"). The `envvar=` literals on the
# `mcp()` options below stay the read sites Typer itself uses (they are the
# feat-126 drift test's shape-4 anchor, so no name constant is introduced
# here -- the registration uses the same literals); the options'
# Python-side `default=` values are sourced from these registry records
# (feat-208 Phase 140) -- `register()` performs no environment read, so
# the signature defaults are the same static import-time constants as the
# pre-migration literals ("stdio"/"localhost"/8000).
_mcp_transport_var = _envregistry.register(
    "SPECMGR_MCP_TRANSPORT",
    default="stdio",
    description="Transport mode for the MCP server.",
    owner="cli",
    choices=("stdio", "sse", "streamable-http"),
)
_mcp_host_var = _envregistry.register(
    "SPECMGR_MCP_HOST",
    default="localhost",
    description="Bind address, SSE/streamable-http mode only.",
    owner="cli",
)
_mcp_port_var = _envregistry.register(
    "SPECMGR_MCP_PORT",
    default="8000",
    description="TCP port, SSE/streamable-http mode only.",
    owner="cli",
    format="number",
)

# Type-narrowing asserts for static checkers only (feat-208 Phase 140,
# conventions Rule 2, mirroring the base-dir modules' Phase 120
# derived-constant asserts and `_envregistry.get_with_default`'s own
# narrowing): each of the three register() calls above registered a
# non-None literal default, so the record's `.default` is a str here and
# the `mcp()` signature defaults below can read it.
assert _mcp_transport_var.default is not None, (
    "'SPECMGR_MCP_TRANSPORT' is registered with a non-None default in the register() call above; "
    "the mcp() signature default cannot be None"
)
assert _mcp_host_var.default is not None, (
    "'SPECMGR_MCP_HOST' is registered with a non-None default in the register() call above; "
    "the mcp() signature default cannot be None"
)
assert _mcp_port_var.default is not None, (
    "'SPECMGR_MCP_PORT' is registered with a non-None default in the register() call above; "
    "the mcp() signature default cannot be None"
)


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
            help="Transport mode: 'stdio', 'sse', or 'streamable-http'.",
            show_default=True,
        ),
    ] = _mcp_transport_var.default,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            envvar="SPECMGR_MCP_HOST",
            help="Bind address (SSE/streamable-http mode only).",
            show_default=True,
        ),
    ] = _mcp_host_var.default,
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            envvar="SPECMGR_MCP_PORT",
            help="TCP port (SSE/streamable-http mode only).",
            show_default=True,
        ),
    ] = int(_mcp_port_var.default),
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
    elif transport.lower() == "streamable-http":
        _warn_on_public_binding(host)
        mcp_server.run(transport="streamable-http", host=host, port=port, stateless_http=True)
    else:
        mcp_server.run(transport="stdio")
