# `biz.dfch.specmgr.uc.prompts`

MCP prompt wrappers for Use Cases (feat-57-uc-commands).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``uc/tools/``/``uc/resources/`` surface in the right order --
one module per prompt, mirroring ``req/prompts/``'s own one-module-per-
prompt split. Import this package to register all UC prompts at once::

    from biz.dfch.specmgr.uc import prompts  # noqa: F401 (side-effects only)
