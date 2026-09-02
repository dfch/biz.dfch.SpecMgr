# `biz.dfch.specmgr.sysrs.prompts`

MCP prompt wrappers for System Requirements Specification (SYSRS) documents (Task 5.1).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``sysrs/tools/``/``sysrs/resources/`` surface in the right order --
one module per prompt, mirroring ``sop/prompts/``'s/``vcr/prompts/``'s own
one-module-per-prompt split. Import this package to register both SYSRS
prompts at once::

    from biz.dfch.specmgr.sysrs import prompts  # noqa: F401 (side-effects only)
