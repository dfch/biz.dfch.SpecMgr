# `biz.dfch.specmgr.req.prompts`

MCP prompt wrappers for Requirements (Task 3.19).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``req/tools/``/``req/resources/`` surface in the right order --
one module per prompt, mirroring ``adr/prompts/``'s own one-module-per-
prompt split. Import this package to register all REQ prompts at once::

    from biz.dfch.specmgr.req import prompts  # noqa: F401 (side-effects only)
