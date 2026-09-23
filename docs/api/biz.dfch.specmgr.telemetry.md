# `biz.dfch.specmgr.telemetry`

Shared logging/telemetry infrastructure for the MCP server (feat-139-logging-telemetry).

This package is shared infrastructure, not a document domain: it is not
imported from ``biz.dfch.specmgr``'s own ``__init__.py`` (which would
force the ``mcp``/OpenTelemetry extras onto the base library), and its
modules are imported individually where they are needed -- ``server.py``'s
startup wiring, ``general/resources/telemetry_status.py``,
``commands/mcp.py``, and (for ``metrics``) every domain's ``tools/
_lock.py``. This ``__init__`` deliberately carries no imports of its own
(it is documentation only): importing a submodule (e.g.
``telemetry.metrics`` from the base-library-safe ``_lock.py`` modules,
or ``telemetry.config`` from ``commands/mcp.py``) must not drag the
``mcp``/OpenTelemetry extras in through the package's ``__init__`` --
the ``middleware``/``otel`` modules need those extras, so they stay
importable only by code that already has them (``server.py`` and its
tests).

Modules (per the feature plan's Design Notes, "Package location"):

- ``config``: parses/validates the eight ``SPECMGR_LOG_*``/
  ``SPECMGR_OTEL_*`` environment variables (stdlib-only, import-safe from
  the base library; Phase 1, Task 1.1).
- ``logging``: the dual rich/JSON formatter and root-logger setup (Phase 2).
- ``middleware``: the ``ServerMiddleware`` implementation (Phase 3,
  extended in Phase 5 with the call metrics).
- ``metrics``: the shared metric names/attribute keys, the instrument
  slots, the lock-wait helper, and the doc-cache observable callbacks
  (Phase 5, Tasks 5.4/5.5; stdlib-only, import-safe from the base
  library -- the thirteen ``<domain>/tools/_lock.py`` modules import
  only this module).
- ``domain_mapping``: the explicit tool/resource/prompt-name -> domain
  mapping behind the ``mcp.domain`` attribute (Phase 5, Task 5.1;
  stdlib-only, import-safe from the base library).
- ``otel``: the OpenTelemetry SDK bootstrap (Phase 4, extended in
  Phase 5 with the pinned histogram Views and the bootstrap-created
  instruments).
- ``redact``: the body/path/title redaction safeguard (Phase 6).
