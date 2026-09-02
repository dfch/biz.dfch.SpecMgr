# `biz.dfch.specmgr.general`

General-purpose (cross-cutting, not domain-specific) tools, resources, and
prompts.

This package provides tools, resources, and prompts that apply to any markdown
file in the system, regardless of document type (ADR, use case, etc.), or that
are not specific to any single document domain at all (e.g. the server
version). It complements the domain-specific packages (``adr``, ``req``,
``uc``).

``tools`` (e.g. ``mdformat``, ``confluence_fetch``, ``confluence_update``) operate on raw
markdown files or external URLs and are registered as ``@mcp.tool()`` functions. ``resources``
(e.g. ``version``, ``iso25010``, ``rasci``) are registered as
``@mcp.resource()`` functions. ``prompts`` (e.g. ``compact_history``,
``confluence_update``, ``confluence_fetch`` -- the latter two sharing their
respective tools' exact names, thin single-tool-call instructional text
only) return instructional text and are registered as ``@mcp.prompt()``
functions. Import this package to register all general tools, resources,
and prompts against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import general  # noqa: F401 (side-effects only)
