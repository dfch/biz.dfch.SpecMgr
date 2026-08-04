# `biz.dfch.specmgr.commands`

commands module.

Each CLI command lives in its own module, exposing a plain function that
``cli.py`` registers on the Typer ``app`` via ``app.command()(fn)``.
