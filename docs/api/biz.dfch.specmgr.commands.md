# `biz.dfch.specmgr.commands`

commands module.

Each CLI command lives in its own module, exposing a plain function that
``cli.py`` registers on the Typer ``app`` via ``app.command()(fn)``. The
``diagram`` module is the one Typer sub-command group (registered via
``app.add_typer``) — ``specmgr diagram uc`` (feat-185-uc-diagrams, Phase 130).
The ``lint`` module (feat-218, Phase 100) is the one command that
contributes nothing to the ``mcp``-extra import chain at module level —
no registry (``general.tools._domains``) or ``tools``-package import,
where every sibling module reaches ``server.py`` through its package
inits (Task 100.100's import test; the feature plan's Updates entry);
its registry-backed names load lazily inside the command body, behind
the ``ImportError`` -> exit 1 guard for the missing ``mcp`` extra (the
``mcp``/``diagram`` precedent).
