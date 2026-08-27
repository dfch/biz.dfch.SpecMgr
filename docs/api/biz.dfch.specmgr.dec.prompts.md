# `biz.dfch.specmgr.dec.prompts`

MCP prompt wrappers for Decisions (Task 4.1).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``dec/tools/``/``dec/resources/`` surface in the right order --
one module per prompt, mirroring ``gol/prompts/``'s own one-module-per-
prompt split. Import this package to register all decision prompts at
once::

    from biz.dfch.specmgr.dec import prompts  # noqa: F401 (side-effects only)
