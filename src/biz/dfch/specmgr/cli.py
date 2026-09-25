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

"""Typer CLI entry point for ``biz-dfch-specmgr``.

Requires the ``cli`` extra (``pip install biz-dfch-specmgr[cli]``)::

    specmgr version
    uv run specmgr version
    python -m biz.dfch.specmgr version

Each command is implemented in its own module under ``commands/`` and
registered on ``app`` below; see that module for the ``mcp`` command's
transport/host/port options and environment variables. ``mcp``
additionally requires the ``mcp`` extra
(``pip install biz-dfch-specmgr[mcp]``).
"""

import sys

import typer
from dotenv import find_dotenv, load_dotenv

from .telemetry.config import TelemetryConfigError

# ---------------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------------


def _load_default_dotenv() -> None:
    """Load ``.env`` walking upward from this file, then from CWD as fallback."""
    dotenv_path = find_dotenv(usecwd=False) or find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, verbose=False)


# Must run before the command imports below: that import chain transitively
# executes server.py's module scope, where the telemetry config is validated,
# the structured logging is set up, and the OTel providers are bootstrapped
# -- all of them reading os.environ at import time (feat-139-logging-telemetry
# Tasks 1.6/2.5/4.9). A project .env's SPECMGR_LOG_*/SPECMGR_OTEL_* values
# only take effect if loaded before that point, like every other SPECMGR_*
# variable family (which the command functions read lazily at call time).
_load_default_dotenv()

try:
    from .commands import (
        adr_toc,
        coverage_badge,
        docs,
        mcp,
        mcp_docs,
        mdformat,
        req_parse,
        schema,
        unused_code,
        version,
    )
except TelemetryConfigError as ex:
    # ACC-011 (feat-139-logging-telemetry): this import chain transitively
    # executes server.py's module scope -- where the telemetry config is
    # validated unconditionally at startup (Task 1.6) -- before any command
    # function runs, but after _load_default_dotenv() above, so a project
    # .env's SPECMGR_LOG_*/SPECMGR_OTEL_* values are seen by the validation
    # and fail closed on a .env-only misconfiguration too. Surface a static
    # misconfiguration as a single clear stderr line naming the offending
    # env var(s) plus exit code 1, mirroring commands/mcp.py's own handling
    # of the same error.
    typer.echo(str(ex), err=True)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Typer application
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="specmgr",
    help="An artifact manager for system specifications.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def _callback() -> None:
    """An artifact manager for system specifications.

    An explicit callback is required so Typer keeps dispatching
    subcommands (``specmgr version``) instead of collapsing to a single
    top-level command, which is its default when only one command is
    registered. Remove this docstring note once a second command exists.
    """


app.command()(version)
app.command()(mcp)
app.command()(docs)
app.command()(mcp_docs)
app.command()(adr_toc)
app.command()(coverage_badge)
app.command()(schema)
app.command()(unused_code)
app.command()(req_parse)
app.command()(mdformat)


if __name__ == "__main__":
    app()
