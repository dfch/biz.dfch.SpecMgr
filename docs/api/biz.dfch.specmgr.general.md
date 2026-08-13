# `biz.dfch.specmgr.general`

General-purpose (cross-cutting, not domain-specific) tools.

This package provides tools that apply to any markdown file in the system,
regardless of document type (ADR, use case, etc.). It complements the
domain-specific packages (``adr``, ``uc``) and the cross-cutting ``resources``
package (which holds read-only resources like version).

Tools here (e.g. ``mdformat``) operate on raw markdown files and are registered
as ``@mcp.tool()`` functions. Import this package to register all general tools
against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import general  # noqa: F401 (side-effects only)
