# `biz.dfch.specmgr.vcr`

Verification Case Record (VCR) domain -- how a REQ/UC is verified.

This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
still under construction: only ``vcr.models`` exists so far (Phase 1 --
``.specmgr/feat/feat-33-vcr/README.md``). Deliberately does **not** yet import
``tools``/``resources``/``prompts`` sub-packages -- those, and the resulting
``from biz.dfch.specmgr import vcr  # noqa: F401`` domain-registration
side-effect import, are Phase 2/3/4's job, not Phase 1's.
