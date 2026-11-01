# `biz.dfch.specmgr.txt.prompts`

MCP prompt wrappers for free-form text (TXT) documents (feat-229-txt Phase 120).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``txt/tools/``/``txt/resources/`` surface in the right order --
one module per prompt, mirroring ``vcr/prompts/``'s own one-module-per-
prompt split. Import this package to register all free-form text
prompts at once::

    from biz.dfch.specmgr.txt import prompts  # noqa: F401 (side-effects only)
