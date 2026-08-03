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

This is a placeholder skeleton: no domain commands exist yet.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as installed_version

import typer
from dotenv import find_dotenv, load_dotenv

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


@app.command()
def version() -> None:
    """Print the installed ``biz-dfch-specmgr`` version."""
    try:
        typer.echo(installed_version("biz-dfch-specmgr"))
    except PackageNotFoundError:
        typer.echo("unknown (package not installed)")


if __name__ == "__main__":
    app()
