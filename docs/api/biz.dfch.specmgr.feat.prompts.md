# `biz.dfch.specmgr.feat.prompts`

MCP prompt wrappers for Features (Task 4.1).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``feat/tools/``/``feat/resources/`` surface in the right order --
one module per prompt, mirroring ``dec/prompts/``'s own one-module-per-
prompt split. Import this package to register all feature prompts at
once::

    from biz.dfch.specmgr.feat import prompts  # noqa: F401 (side-effects only)
