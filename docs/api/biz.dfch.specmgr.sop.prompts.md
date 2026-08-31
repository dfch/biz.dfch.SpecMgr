# `biz.dfch.specmgr.sop.prompts`

MCP prompt wrappers for Standard Operating Procedures (Task 4.1).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``sop/tools/``/``sop/resources/`` surface in the right order --
one module per prompt, mirroring ``dec/prompts/``'s own one-module-per-
prompt split. Import this package to register both SOP prompts at once::

    from biz.dfch.specmgr.sop import prompts  # noqa: F401 (side-effects only)
