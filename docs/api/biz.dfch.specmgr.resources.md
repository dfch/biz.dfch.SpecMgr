# `biz.dfch.specmgr.resources`

MCP resource registrations that are not specific to any single document
domain (doc/refactor-domain.md).

``version`` registers the server package version resource. Domain-specific
resources (e.g. ``adr_list``/``adr_get``) live under their own domain
package instead (``biz.dfch.specmgr.adr.resources``). Import this package
to load all cross-cutting resources at once::

    from biz.dfch.specmgr import resources  # noqa: F401 (side-effects only)
