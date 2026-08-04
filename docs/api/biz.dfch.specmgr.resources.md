# `biz.dfch.specmgr.resources`

MCP resource registrations that are not specific to any single document
domain.

See ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain".

``version`` registers the server package version resource. Domain-specific
resources (e.g. ``adr_list``/``adr_get``) live under their own domain
package instead (``biz.dfch.specmgr.adr.resources``). Import this package
to load all cross-cutting resources at once::

    from biz.dfch.specmgr import resources  # noqa: F401 (side-effects only)
