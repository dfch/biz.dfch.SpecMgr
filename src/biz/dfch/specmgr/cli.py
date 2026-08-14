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

import typer
from dotenv import find_dotenv, load_dotenv

from .commands import adr_toc, coverage_badge, docs, mcp, req_parse, schema, unused_code, version

# ---------------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------------


def _load_default_dotenv() -> None:
    """Load ``.env`` walking upward from this file, then from CWD as fallback."""
    dotenv_path = find_dotenv(usecwd=False) or find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, verbose=False)


_load_default_dotenv()

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
app.command()(adr_toc)
app.command()(coverage_badge)
app.command()(schema)
app.command()(unused_code)
app.command()(req_parse)


if __name__ == "__main__":
    app()
