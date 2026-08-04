# `biz.dfch.specmgr.adr.prompts`

MCP prompt wrappers for Architecture Decision Records (doc/adr-tool-plan.md §11).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``adr/tools/`` tool surface in the right order -- one module per
prompt, mirroring ``adr/tools/``'s own one-tool-per-module split. Import
this package to register all ADR prompts at once::

    from biz.dfch.specmgr.adr import prompts  # noqa: F401 (side-effects only)
