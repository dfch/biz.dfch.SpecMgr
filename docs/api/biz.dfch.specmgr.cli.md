# `biz.dfch.specmgr.cli`

Typer CLI entry point for ``biz-dfch-specmgr``.

Requires the ``cli`` extra (``pip install biz-dfch-specmgr[cli]``)::

    specmgr version
    uv run specmgr version
    python -m biz.dfch.specmgr version

Each command is implemented in its own module under ``commands/`` and
registered on ``app`` below; see that module for the ``mcp`` command's
transport/host/port options and environment variables. ``mcp``
additionally requires the ``mcp`` extra
(``pip install biz-dfch-specmgr[mcp]``).

## Functions

### `_callback() -> None`

An artifact manager for system specifications.

An explicit callback is required so Typer keeps dispatching
subcommands (``specmgr version``) instead of collapsing to a single
top-level command, which is its default when only one command is
registered. Remove this docstring note once a second command exists.


### `_load_default_dotenv() -> None`

Load ``.env`` walking upward from this file, then from CWD as fallback.

