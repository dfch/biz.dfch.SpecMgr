# `biz.dfch.specmgr.vcr.prompts`

MCP prompt wrappers for Verification Case Records (Task 3.2).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``vcr/tools/``/``vcr/resources/`` surface in the right order --
one module per prompt, mirroring ``dec/prompts/``'s own one-module-per-
prompt split. Import this package to register all verification case
record prompts at once::

    from biz.dfch.specmgr.vcr import prompts  # noqa: F401 (side-effects only)
