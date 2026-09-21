# `biz.dfch.specmgr.telemetry`

Shared logging/telemetry infrastructure for the MCP server (feat-139-logging-telemetry).

This package is shared infrastructure, not a document domain: it is not
imported from ``biz.dfch.specmgr``'s own ``__init__.py`` (which would
force the ``mcp``/OpenTelemetry extras onto the base library), and its
modules are imported individually where they are needed -- ``server.py``'s
startup wiring, ``general/resources/telemetry_status.py``, and
``commands/mcp.py``.

Modules (per the feature plan's Design Notes, "Package location"):

- ``config``: parses/validates the eight ``SPECMGR_LOG_*``/
  ``SPECMGR_OTEL_*`` environment variables (stdlib-only, import-safe from
  the base library; Phase 1, Task 1.1).
- ``logging``: the dual rich/JSON formatter and root-logger setup (Phase 2).
- ``middleware``: the ``ServerMiddleware`` implementation (Phase 3).
- ``otel``: the OpenTelemetry SDK bootstrap (Phase 4).
- ``redact``: the body/path/title redaction safeguard (Phase 6).
