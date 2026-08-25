# `biz.dfch.specmgr.rsk`

Risk (RSK) domain -- risk registers for system specifications.

This is a domain-first package, mirroring ``tsk``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), that will eventually contain models,
tools, prompts, and resources for managing ``rsk`` documents.

As of `.specmgr/feat/feat-15-add-artifact-type-risk/README.md` Phase 1
("Specification"), only ``models`` exists (``rsk.models.v1``). There are no
``tools``/``prompts``/``resources`` sub-packages yet -- those are Phase 3 --
so, unlike ``req``/``uc``/``adr``/``general``, this package deliberately does
not yet import/re-export them here.
