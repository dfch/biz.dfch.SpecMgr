# `biz.dfch.specmgr.general.resources.telemetry_status`

Resource: specmgr://telemetry/status -- current logging/telemetry state.

Read-only (feat-139-logging-telemetry, Phase 1, Task 1.3; REQ
``41444084-6821-426d-84a2-028a3f4fed0b``): reports, as an extensible
``list[str]``, whether structured logging and telemetry are each currently
enabled and in what mode, so an operator can confirm what an already-
running server has active without inspecting its environment or
restarting it.

The lines are built from the same parsed, fail-closed-validated config
object the server startup (``server.py``'s module-scope
``load_telemetry_config()`` call, Task 1.6) and the later middleware
(Phase 3) read: the resource re-parses on every read, so it always
reflects the environment the server process started with -- changing the
env vars only takes effect on a restart (per the VCR's AC-002). The
pinned entry format (Design Notes, "Status resource") is
``logging: disabled`` | ``logging: enabled (level=<LEVEL>,
format=<rich|json>, file=<on|off>)`` and ``telemetry: disabled`` |
``telemetry: enabled (exporter=<console|otlp>)``.

## Functions

### `telemetry_status() -> 'list[str]'`

Return the current logging/telemetry state as a list of status lines.

Returns:
    Two strings: the logging line (``logging: disabled`` or
    ``logging: enabled (level=<LEVEL>, format=<rich|json>,
    file=<on|off>)``) followed by the telemetry line (``telemetry:
    disabled`` or ``telemetry: enabled (exporter=<console|otlp>)``).

