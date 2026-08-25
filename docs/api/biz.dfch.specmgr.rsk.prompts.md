# `biz.dfch.specmgr.rsk.prompts`

MCP prompt wrappers for Risks (Task 3.13).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``rsk/tools/``/``rsk/resources/`` surface in the right order --
one module per prompt, mirroring ``req/prompts/``'s own one-module-per-
prompt split. Named ``create_risk``/``update_risk`` (the issue's literal
wording), not the ``rsk``-prefixed convention the tools/resources use --
see each prompt's own docstring. Import this package to register all risk
prompts at once::

    from biz.dfch.specmgr.rsk import prompts  # noqa: F401 (side-effects only)
