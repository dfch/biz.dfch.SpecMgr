# `biz.dfch.specmgr.prb`

Problem Statement (PRB) domain -- Six-Sigma-style problem statement specifications.

This is a domain-first package, mirroring ``tsk``/``qa``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models (and, in later
phases, tools, prompts, and resources) for managing ``prb`` documents.

Only ``models`` exists so far (`.specmgr/feat/feat-16-problem-statement/README.md`
Phase 1: Specification) -- this package intentionally does not yet import
``prompts``/``resources``/``tools`` sub-packages, since none exist yet.
