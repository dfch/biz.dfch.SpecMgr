# `biz.dfch.specmgr.commands`

commands module.

Each CLI command lives in its own module, exposing a plain function that
``cli.py`` registers on the Typer ``app`` via ``app.command()(fn)``. The
``diagram`` module is the one Typer sub-command group (registered via
``app.add_typer``) — ``specmgr diagram uc`` (feat-185-uc-diagrams, Phase 130).
