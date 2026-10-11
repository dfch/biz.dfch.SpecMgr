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

from . import _envregistry
from .commands import (
    adr_toc,
    coverage_badge,
    diagram,
    docs,
    mcp,
    mcp_docs,
    mdformat,
    plantuml_check,
    plantuml_encode,
    req_parse,
    schema,
    unused_code,
    version,
)

# ---------------------------------------------------------------------------
# .env loading
# ---------------------------------------------------------------------------

#: Sentinel env var (test hook — never set outside test runs): when set, the
#: ``.env`` load below is skipped entirely, so the CLI process runs under the
#: CI (source-less) condition whatever the local (gitignored) ``.env``
#: configures. ``tests/conftest.py`` honours the same sentinel (its own copy
#: of the name, drift-pinned in ``tests/plantuml/test_source_gate.py``); the
#: pair is what makes the ``specmgr coverage-badge`` pre-commit hook's
#: source-less re-run source-less end-to-end — the hook sets it so that no
#: ``.env``-loading code path in the test process can select a PlantUML
#: source (feat-185-uc-diagrams Phase 145, amendment C).
NO_DOTENV_SENTINEL = "SPECMGR_TESTS_NO_DOTENV"

# The registry record for :data:`NO_DOTENV_SENTINEL` (feat-208, Phase
# 110; the read site migrated to the registry accessor in Phase 130):
# presence-based (no default). The constant stays the name authority
# -- the registration sources its name from it, and the
# :func:`_load_default_dotenv` check below is a truthiness test
# (``if _envregistry.get(NO_DOTENV_SENTINEL):``), so a set-but-empty
# value behaves as absent there.
_envregistry.register(
    NO_DOTENV_SENTINEL,
    description=(
        "Presence-based test/CI sentinel: set to any value to skip the CLI's module-level default "
        ".env load entirely, so the process runs under the CI (source-less) condition whatever the "
        "local (gitignored) .env configures; this is what keeps the specmgr coverage-badge "
        "pre-commit hook's source-less re-run source-less end-to-end. Unset by default, never set "
        "outside test runs."
    ),
    owner="cli",
)


def _load_default_dotenv() -> None:
    """Load ``.env`` walking upward from this file, then from CWD as fallback.

    Skipped entirely when the :data:`NO_DOTENV_SENTINEL` env var is set (see
    its docstring).
    """
    if _envregistry.get(NO_DOTENV_SENTINEL):
        return
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
app.command()(mcp_docs)
app.command()(adr_toc)
app.command()(coverage_badge)
app.command()(schema)
app.command()(unused_code)
app.command()(req_parse)
app.command()(mdformat)
app.command()(plantuml_check)
app.command()(plantuml_encode)
app.add_typer(diagram, name="diagram")


if __name__ == "__main__":
    app()
