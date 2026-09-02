# `biz.dfch.specmgr.sysrs`

System Requirements Specification (SYSRS) domain -- an aggregator document type that
ties together already-existing specmgr artifacts (``gol``, ``prb``, ``qa``, ``uc``,
``req``, ``rsk``, ``dec``/``adr``, ``vcr``) into one coherent, navigable specification,
rather than duplicating their content.

This is a domain-first package, mirroring ``sop``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts, and
resources for managing ``sysrs`` documents. A ``sysrs`` is built on the
generic ``models/md`` parser with the simple surface used by GOL/RSK/QA/DEC/
SOP/VCR -- no fine-grained mutation tools, no by-id resource, no
deterministic re-render.

``sysrs`` is, like SOP, built from scratch entirely on the generic
mutation tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0): it has no
``update_sysrs``/``set_status_sysrs`` tools of its own -- it dispatches
straight into the generic ``update``/``set_status`` tools in
``general.tools``, and deletion goes through the generic ``delete`` tool
in ``general.tools`` (``type="sysrs"``), the same convention SOP/VCR
already use.

As of this package's Phase 4 (resources + packaged data + schema -- see
``.specmgr/feat/feat-32-sysrs/README.md``), ``sysrs.models``,
``sysrs.tools`` (7 tools), and ``sysrs.resources`` (3 resources --
``specmgr://sysrs/schema``, ``specmgr://sysrs/example``,
``specmgr://sysrs/template``; no ``/{id}``, no ``/list``) all carry real
content; ``sysrs.prompts`` is still an empty placeholder sub-package,
filled in during Phase 5 of that plan. Every cross-reference section
(``### Goals``, ``## Decisions``, ``## Requirements``'s nine H3s, ...)
carries a per-section type-tag regex enforcing which domain(s) it may
reference -- see ``sysrs.models.v1.body``.

Import this package to register everything SYSRS eventually exposes
against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import sysrs  # noqa: F401 (side-effects only)
