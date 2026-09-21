# `biz.dfch.specmgr.telemetry.config`

Parse and validate the ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*`` environment
variables into a typed configuration object (feat-139-logging-telemetry,
Phase 1, Task 1.1).

This module is shared infrastructure, not a document domain: it is
stdlib-only (no ``mcp``, no ``opentelemetry.*``, no ``typer``), so it is
import-safe from the base library, and it is imported individually where
needed (``server.py``'s startup wiring, ``general/resources/
telemetry_status.py``, ``commands/mcp.py``) -- never from ``biz.dfch.
specmgr``'s own ``__init__.py``.

Static misconfiguration fails closed (ACC-011): an invalid or incomplete
combination raises :class:`TelemetryConfigError` (a ``ValueError``
subclass) immediately, regardless of whether the parent
``SPECMGR_LOG_ENABLED``/``SPECMGR_OTEL_ENABLED`` switch is itself
``true`` -- a nonsensical combination is rejected outright rather than
silently tolerated just because it happens to be currently inert. This is
the static-misconfiguration counterpart of the *runtime* fail-open policy;
see ``.specmgr/conventions.md``, "Observability Degrades Gracefully,
Application Logic Never Does".

Accepted spellings (this module defines them; ``README.md`` documents
them in Task 8.1):

- the boolean flags (``SPECMGR_LOG_ENABLED``, ``SPECMGR_LOG_FILE_ENABLED``,
  ``SPECMGR_OTEL_ENABLED``): exact match ``"true"``/``"false"``
  case-insensitively;
- ``SPECMGR_LOG_LEVEL``: one of :data:`LOG_LEVELS`, case-insensitive
  (the same literal set the MCP SDK's own ``configure_logging()``
  accepts), normalized to its uppercase canonical form;
- ``SPECMGR_LOG_FORMAT``: one of :data:`LOG_FORMATS` (exact,
  case-sensitive closed set);
- ``SPECMGR_OTEL_EXPORTER``: one of :data:`OTEL_EXPORTERS` (exact,
  case-sensitive closed set);
- ``SPECMGR_LOG_FILE_PATH``/``SPECMGR_OTEL_ENDPOINT``: free text, matched
  as-is; a whitespace-only value counts as unset for the pairing rules
  below;
- pairing rules: ``SPECMGR_LOG_FILE_PATH`` is required and non-blank when
  ``SPECMGR_LOG_FILE_ENABLED=true``; ``SPECMGR_OTEL_ENDPOINT`` (the OTLP
  base URL, which the OTLP/HTTP exporter extends with the spec-mandated
  ``/v1/traces`` and ``/v1/metrics`` paths itself) is required and
  non-blank when ``SPECMGR_OTEL_EXPORTER=otlp``.

All eight variables default to the disabled/safe configuration: logging
off at ``INFO`` in ``rich`` format with the file sink off, telemetry off
with the ``console`` exporter and no endpoint.

## Classes

### `TelemetryConfig`

The parsed, validated logging/telemetry configuration.

Attributes:
    log_enabled: ``SPECMGR_LOG_ENABLED``; default ``False``.
    log_level: ``SPECMGR_LOG_LEVEL`` normalized to its uppercase
        canonical name (one of :data:`LOG_LEVELS`); default ``"INFO"``.
    log_format: ``SPECMGR_LOG_FORMAT`` (one of :data:`LOG_FORMATS`);
        default ``"rich"``.
    log_file_enabled: ``SPECMGR_LOG_FILE_ENABLED``; default ``False``
        (only takes effect when ``log_enabled`` is ``True``).
    log_file_path: ``SPECMGR_LOG_FILE_PATH``, as given; ``None`` when
        unset/blank (required non-blank when ``log_file_enabled``).
    otel_enabled: ``SPECMGR_OTEL_ENABLED``; default ``False``.
    otel_exporter: ``SPECMGR_OTEL_EXPORTER`` (one of
        :data:`OTEL_EXPORTERS`); default ``"console"``.
    otel_endpoint: ``SPECMGR_OTEL_ENDPOINT``, as given; ``None`` when
        unset/blank (required non-blank when ``otel_exporter`` is
        ``"otlp"``).


### `TelemetryConfigError`

An invalid or incomplete ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*`` combination (ACC-011).

A ``ValueError`` subclass -- consistent with every other ``SPECMGR_*``
environment variable in this codebase failing on a bad value -- that
the CLI's ``mcp`` command (``commands/mcp.py``) catches to refuse
starting with a single clear stderr line. The message always names
the offending env var(s) and is a single line.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_non_blank(raw: 'str | None') -> 'str | None'`

Return ``raw`` as given, or ``None`` when it is unset or whitespace-only.

Args:
    raw: The env var's raw value (``None`` when unset).

Returns:
    The value as given, or ``None``.


### `_parse_bool(env: 'Mapping[str, str]', name: 'str', default: 'bool') -> 'bool'`

Parse a boolean-flag env var: exact ``"true"``/``"false"``, case-insensitive.

Args:
    env: The mapping to read from.
    name: The env var name (named in any error).
    default: The value when the env var is unset.

Returns:
    The parsed boolean.

Raises:
    TelemetryConfigError: When the env var is set to anything other
        than ``"true"``/``"false"`` (case-insensitive).


### `_parse_choice(env: 'Mapping[str, str]', name: 'str', allowed: 'tuple[str, ...]', default: 'str', *, case_insensitive: 'bool' = False) -> 'str'`

Parse an env var against a closed set of allowed values.

Args:
    env: The mapping to read from.
    name: The env var name (named in any error).
    allowed: The closed value set, in canonical spelling.
    default: The value when the env var is unset.
    case_insensitive: Whether matching is case-insensitive (and the
        result normalized to the canonical spelling); exact matching
        otherwise.

Returns:
    The canonical allowed value.

Raises:
    TelemetryConfigError: When the env var is set to a value outside
        the closed set.


### `load_telemetry_config(environ: 'Mapping[str, str] | None' = None) -> 'TelemetryConfig'`

Parse and validate the eight telemetry env vars into a :class:`TelemetryConfig`.

Args:
    environ: The mapping to read the env vars from; ``os.environ``
        when omitted (the server-startup call site in ``server.py``
        and the ``specmgr://telemetry/status`` resource both use the
        default).

Returns:
    The validated configuration; all eight variables default to the
    disabled/safe configuration (see the module docstring).

Raises:
    TelemetryConfigError: Immediately on any invalid or incomplete
        combination. Validation is unconditional -- it fires
        regardless of the parent enable switches (ACC-011).

