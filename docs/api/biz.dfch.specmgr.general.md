# `biz.dfch.specmgr.general`

General-purpose (cross-cutting, not domain-specific) tools and resources.

This package provides tools and resources that apply to any markdown file in
the system, regardless of document type (ADR, use case, etc.), or that are not
specific to any single document domain at all (e.g. the server version).
It complements the domain-specific packages (``adr``, ``req``, ``uc``).

``tools`` (e.g. ``mdformat``) operate on raw markdown files and are registered
as ``@mcp.tool()`` functions. ``resources`` (e.g. ``version``, ``iso25010``)
are registered as ``@mcp.resource()`` functions. Import this package to
register all general tools and resources against the shared ``mcp``
application instance at once::

    from biz.dfch.specmgr import general  # noqa: F401 (side-effects only)
