# `biz.dfch.specmgr.qa`

Question and Answer (QA) domain -- requirements-elicitation interview specifications.

This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
mirroring ``req``'s/``tsk``'s layout, containing models (and, from
`.specmgr/feat/feat-12-qa-artifact/README.md` Phase 4 onward, tools,
prompts, and resources) for managing ``qa`` documents.

As of Phase 3 (Pydantic Models & Parser), only ``qa.models.v1`` exists --
``qa.tools``/``qa.resources``/``qa.prompts`` are Phase 4 work and this
module deliberately does not import them yet (there is nothing to import).
Once Phase 4 lands, this module's own import line should mirror
``tsk/__init__.py``'s ``from . import prompts, resources, tools`` so
``server.py``'s bottom-of-file import registers ``qa``'s MCP surface too.
