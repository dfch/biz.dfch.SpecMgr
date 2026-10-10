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
domain-scoped one. ``ears`` registers the EARS requirement-phrasing-
templates guidance resource (``specmgr://ears``, feat-92-resources
REQ-006) -- cross-cutting domain knowledge for any requirement-phrasing
document type (``req``, ``gol``, ``sysrs``, ...), not owned by any single
domain's own schema, mirroring ``dtais``'s cross-domain placement
rationale. ``reference_graph`` registers the frozen reference-graph
rulebook resource (``specmgr://reference-graph``,
feat-207-reference-graph Phase 100) -- the deterministic PlantUML
component-diagram spec for the cross-reference network (emission layout +
palette, alias/label/truncation, title rules, FEAT-exclusion, the
bare-``feat-NNN`` source-id rejection, the cycle rule + red-arrow syntax,
the construction semantics, the CLI file layout) plus the pointer at the
UC rulebook §3–§6 for the validation chain reused as-is; it spans every
document domain, so it is cross-cutting rather than owned by any single
domain's schema (the ``specmgr://uc/plantuml`` rulebook shape, registered
flat top-level like ``dtais``/``iso25010``). ``config`` registers the
``specmgr://config`` diagnostic resource (feat-51-mcp-cwd REQ-001) -- the
resolved absolute base directory
and env-var-set flag for every document domain, so a client can
self-diagnose a CWD/env-var misconfiguration without shell access to the
server's host; it never discloses the value of any environment variable,
only whether a domain's own ``SPECMGR_*_DIR`` is set (REQ-002). Domain-specific
resources (e.g. ``adr_list``/``adr_get``)
live under their own domain package instead (``biz.dfch.specmgr.adr.resources``).
Import this package to load all cross-cutting resources at once::

    from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)
