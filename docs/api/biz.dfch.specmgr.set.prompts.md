# `biz.dfch.specmgr.set.prompts`

MCP prompt wrappers for set (set) documents (feat-173-req-iso29148-level-set Phase 180).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``set/tools/``/``set/resources/`` surface in the right order --
one module per prompt, mirroring ``vcr/prompts/``'s own one-module-per-
prompt split. Import this package to register all set
prompts at once::

    from biz.dfch.specmgr.set import prompts  # noqa: F401 (side-effects only)
