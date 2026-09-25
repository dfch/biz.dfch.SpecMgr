# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Parse and validate the ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*`` environment
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
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------

#: Master switch for structured logging (``true``/``false``).
ENV_LOG_ENABLED = "SPECMGR_LOG_ENABLED"
#: Logging level; one of :data:`LOG_LEVELS` (case-insensitive).
ENV_LOG_LEVEL = "SPECMGR_LOG_LEVEL"
#: Log format; one of :data:`LOG_FORMATS`.
ENV_LOG_FORMAT = "SPECMGR_LOG_FORMAT"
#: File-sink switch; only takes effect when :data:`ENV_LOG_ENABLED` is true.
ENV_LOG_FILE_ENABLED = "SPECMGR_LOG_FILE_ENABLED"
#: File-sink path; required when :data:`ENV_LOG_FILE_ENABLED` is true.
ENV_LOG_FILE_PATH = "SPECMGR_LOG_FILE_PATH"
#: Master switch for telemetry (``true``/``false``).
ENV_OTEL_ENABLED = "SPECMGR_OTEL_ENABLED"
#: Telemetry exporter; one of :data:`OTEL_EXPORTERS`.
ENV_OTEL_EXPORTER = "SPECMGR_OTEL_EXPORTER"
#: OTLP base URL; required when :data:`ENV_OTEL_EXPORTER` is ``otlp``.
ENV_OTEL_ENDPOINT = "SPECMGR_OTEL_ENDPOINT"

# ---------------------------------------------------------------------------
# Closed value sets and defaults
# ---------------------------------------------------------------------------

#: The five named logging levels (uppercase canonical form) -- the same
#: literal set the MCP SDK's own ``configure_logging()`` accepts.
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
#: The closed log-format set (exact, case-sensitive).
LOG_FORMATS = ("rich", "json")
#: The closed telemetry-exporter set (exact, case-sensitive).
OTEL_EXPORTERS = ("console", "otlp")

#: Default for :data:`ENV_LOG_ENABLED` (all features off by default).
DEFAULT_LOG_ENABLED = False
#: Default for :data:`ENV_LOG_LEVEL`.
DEFAULT_LOG_LEVEL = "INFO"
#: Default for :data:`ENV_LOG_FORMAT`.
DEFAULT_LOG_FORMAT = "rich"
#: Default for :data:`ENV_LOG_FILE_ENABLED`.
DEFAULT_LOG_FILE_ENABLED = False
#: Default for :data:`ENV_OTEL_ENABLED`.
DEFAULT_OTEL_ENABLED = False
#: Default for :data:`ENV_OTEL_EXPORTER`.
DEFAULT_OTEL_EXPORTER = "console"

#: The exact spellings accepted for the boolean flags (matched case-insensitively).
_BOOL_TRUE = "true"
_BOOL_FALSE = "false"
#: The :data:`ENV_OTEL_EXPORTER` value that requires :data:`ENV_OTEL_ENDPOINT`.
_OTLP_EXPORTER = "otlp"


class TelemetryConfigError(ValueError):
    """An invalid or incomplete ``SPECMGR_LOG_*``/``SPECMGR_OTEL_*`` combination (ACC-011).

    A ``ValueError`` subclass -- consistent with every other ``SPECMGR_*``
    environment variable in this codebase failing on a bad value -- that
    the CLI's ``mcp`` command (``commands/mcp.py``) catches to refuse
    starting with a single clear stderr line. The message always names
    the offending env var(s) and is a single line.
    """


@dataclass(frozen=True)
class TelemetryConfig:
    """The parsed, validated logging/telemetry configuration.

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
    """

    log_enabled: bool  # SPECMGR_LOG_ENABLED
    log_level: str  # SPECMGR_LOG_LEVEL, uppercase canonical
    log_format: str  # SPECMGR_LOG_FORMAT
    log_file_enabled: bool  # SPECMGR_LOG_FILE_ENABLED
    log_file_path: str | None  # SPECMGR_LOG_FILE_PATH, or None when unset/blank
    otel_enabled: bool  # SPECMGR_OTEL_ENABLED
    otel_exporter: str  # SPECMGR_OTEL_EXPORTER
    otel_endpoint: str | None  # SPECMGR_OTEL_ENDPOINT, or None when unset/blank


def load_telemetry_config(environ: Mapping[str, str] | None = None) -> TelemetryConfig:
    """Parse and validate the eight telemetry env vars into a :class:`TelemetryConfig`.

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
    """
    env: Mapping[str, str] = os.environ if environ is None else environ

    log_enabled = _parse_bool(env, ENV_LOG_ENABLED, DEFAULT_LOG_ENABLED)
    log_level = _parse_choice(env, ENV_LOG_LEVEL, LOG_LEVELS, DEFAULT_LOG_LEVEL, case_insensitive=True)
    log_format = _parse_choice(env, ENV_LOG_FORMAT, LOG_FORMATS, DEFAULT_LOG_FORMAT)
    log_file_enabled = _parse_bool(env, ENV_LOG_FILE_ENABLED, DEFAULT_LOG_FILE_ENABLED)
    log_file_path = _non_blank(env.get(ENV_LOG_FILE_PATH))
    if log_file_enabled and log_file_path is None:
        raise TelemetryConfigError(
            f"{ENV_LOG_FILE_PATH} is required and must be non-blank when {ENV_LOG_FILE_ENABLED}=true"
        )

    otel_enabled = _parse_bool(env, ENV_OTEL_ENABLED, DEFAULT_OTEL_ENABLED)
    otel_exporter = _parse_choice(env, ENV_OTEL_EXPORTER, OTEL_EXPORTERS, DEFAULT_OTEL_EXPORTER)
    otel_endpoint = _non_blank(env.get(ENV_OTEL_ENDPOINT))
    if otel_exporter == _OTLP_EXPORTER and otel_endpoint is None:
        raise TelemetryConfigError(
            f"{ENV_OTEL_ENDPOINT} is required and must be non-blank when {ENV_OTEL_EXPORTER}={_OTLP_EXPORTER}"
        )

    result = TelemetryConfig(
        log_enabled=log_enabled,
        log_level=log_level,
        log_format=log_format,
        log_file_enabled=log_file_enabled,
        log_file_path=log_file_path,
        otel_enabled=otel_enabled,
        otel_exporter=otel_exporter,
        otel_endpoint=otel_endpoint,
    )
    return result


def _parse_bool(env: Mapping[str, str], name: str, default: bool) -> bool:
    """Parse a boolean-flag env var: exact ``"true"``/``"false"``, case-insensitive.

    Args:
        env: The mapping to read from.
        name: The env var name (named in any error).
        default: The value when the env var is unset.

    Returns:
        The parsed boolean.

    Raises:
        TelemetryConfigError: When the env var is set to anything other
            than ``"true"``/``"false"`` (case-insensitive).
    """
    raw = env.get(name)
    if raw is None:
        result = default
        return result
    lowered = raw.lower()
    if lowered == _BOOL_TRUE:
        result = True
        return result
    if lowered == _BOOL_FALSE:
        result = False
        return result
    raise TelemetryConfigError(f"{name} must be 'true' or 'false' (case-insensitive); got {raw!r}")


def _parse_choice(
    env: Mapping[str, str],
    name: str,
    allowed: tuple[str, ...],
    default: str,
    *,
    case_insensitive: bool = False,
) -> str:
    """Parse an env var against a closed set of allowed values.

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
    """
    raw = env.get(name)
    if raw is None:
        result = default
        return result
    if case_insensitive:
        normalized = {value.lower(): value for value in allowed}
        canonical: str | None = normalized.get(raw.lower())
    else:
        canonical = raw if raw in allowed else None
    if canonical is None:
        note = " (case-insensitive)" if case_insensitive else ""
        raise TelemetryConfigError(f"{name} must be one of: {'/'.join(allowed)}{note}; got {raw!r}")
    result = canonical
    return result


def _non_blank(raw: str | None) -> str | None:
    """Return ``raw`` as given, or ``None`` when it is unset or whitespace-only.

    Args:
        raw: The env var's raw value (``None`` when unset).

    Returns:
        The value as given, or ``None``.
    """
    if raw is None or not raw.strip():
        result: str | None = None
        return result
    result = raw
    return result
