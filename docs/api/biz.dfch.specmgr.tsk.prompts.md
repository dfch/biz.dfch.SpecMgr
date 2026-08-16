# `biz.dfch.specmgr.tsk.prompts`

MCP prompt wrappers for Task Lists (Task 3.13-3.14).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``tsk/tools/``/``tsk/resources/`` surface in the right order --
one module per prompt, mirroring ``req/prompts/``'s own one-module-per-
prompt split. Named ``create_task``/``update_task``/``implement_task``
(the issue's literal wording), not the ``tsk``-prefixed convention the
tools/resources use -- see each prompt's own docstring. Import this
package to register all TSK prompts at once::

    from biz.dfch.specmgr.tsk import prompts  # noqa: F401 (side-effects only)
