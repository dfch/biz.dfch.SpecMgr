# `biz.dfch.specmgr.adr`

The Architecture Decision Record (ADR) domain package (doc/refactor-domain.md).

Groups every ADR-specific *interface* module -- ``tools`` (``@mcp.tool()``
wrappers), ``prompts`` (``@mcp.prompt()`` flows), and ``resources``
(``@mcp.resource()`` read-only counterparts) -- under one top-level,
domain-first package. The ADR *schema* layer (``Adr``, ``parse_adr``,
``render_adr``, mutation functions) stays under the shared
``biz.dfch.specmgr.models.adr`` package instead, since it has no dependency
on ``mcp`` and is meant to stay importable standalone.

Future document types (``req``, ``uc``, ``ac``, ...) are expected to mirror
this exact shape: a top-level ``biz.dfch.specmgr.<domain>`` package with its
own ``tools``/``prompts``/``resources`` sub-packages, plus a
``biz.dfch.specmgr.models.<domain>`` schema package.

Import this package to register all of the ADR domain's tools, prompts, and
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import adr  # noqa: F401 (side-effects only)
