# `biz.dfch.specmgr.general.resources`

MCP resource registrations that are not specific to any single document
domain.

See ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain".

``version`` registers the server package version resource. ``iso25010``
registers the ISO/IEC 25010:2023 product quality model resource. ``dtais``
registers the DTAIS verification-method vocabulary resource
(``specmgr://dtais``, feat-33-vcr REQ-006) -- cross-cutting domain
knowledge for ``vcr``'s ``## Acceptance Criteria`` method vocabulary, not
owned by ``vcr``'s own schema. ``rasci`` registers the generic RASCI
responsibility-assignment guidance resource (``specmgr://rasci``,
REQ-011) -- motivated by the ``sop`` domain but not scoped to it, mirroring
``iso25010``'s cross-cutting placement rather than ``rsk/tara``'s
domain-scoped one. Domain-specific resources (e.g. ``adr_list``/``adr_get``)
live under their own domain package instead (``biz.dfch.specmgr.adr.resources``).
Import this package to load all cross-cutting resources at once::

    from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)
