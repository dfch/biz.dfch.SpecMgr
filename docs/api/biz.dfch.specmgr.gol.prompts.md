# `biz.dfch.specmgr.gol.prompts`

MCP prompt wrappers for Goals (Tasks 3.14-3.15).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``gol/tools/``/``gol/resources/`` surface in the right order --
one module per prompt, mirroring ``prb/prompts/``'s own one-module-per-
prompt split. Import this package to register all GOL prompts at once::

    from biz.dfch.specmgr.gol import prompts  # noqa: F401 (side-effects only)
