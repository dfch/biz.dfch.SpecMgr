# `biz.dfch.specmgr.prb.prompts`

MCP prompt wrappers for Problem Statements (Tasks 3.14-3.15).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``prb/tools/``/``prb/resources/`` surface in the right order --
one module per prompt, mirroring ``req/prompts/``'s own one-module-per-
prompt split. Named ``create_prb``/``update_prb`` (the per-domain tool-
name convention, like REQ/QA -- the prompt keeps its name, while the
update/status tools are now the generic ``update``/``set_status`` in
``general/tools/``), not literal wording like TSK's
``create_task``/``update_task``. Import this package to register all PRB
prompts at once::

    from biz.dfch.specmgr.prb import prompts  # noqa: F401 (side-effects only)
