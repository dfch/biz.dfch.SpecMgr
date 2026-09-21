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

"""Resource: specmgr://telemetry/status -- current logging/telemetry state.

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
"""

from __future__ import annotations

from ...server import mcp
from ...telemetry.config import load_telemetry_config


@mcp.resource(
    "specmgr://telemetry/status",
    name="telemetry_status",
    title="SpecMgr Logging/Telemetry Status",
    description=(
        "The current logging/telemetry enablement state of this MCP server process as a "
        "list of two strings: one line for logging (enablement plus level, format, and "
        "file-sink mode) and one line for telemetry (enablement plus exporter). Read-only; "
        "reflects the SPECMGR_LOG_*/SPECMGR_OTEL_* environment the process started with."
    ),
    mime_type="application/json",
)
def telemetry_status() -> list[str]:
    """Return the current logging/telemetry state as a list of status lines.

    Returns:
        Two strings: the logging line (``logging: disabled`` or
        ``logging: enabled (level=<LEVEL>, format=<rich|json>,
        file=<on|off>)``) followed by the telemetry line (``telemetry:
        disabled`` or ``telemetry: enabled (exporter=<console|otlp>)``).
    """
    config = load_telemetry_config()
    if config.log_enabled:
        file_state = "on" if config.log_file_enabled else "off"
        logging_line = f"logging: enabled (level={config.log_level}, format={config.log_format}, file={file_state})"
    else:
        logging_line = "logging: disabled"
    if config.otel_enabled:
        telemetry_line = f"telemetry: enabled (exporter={config.otel_exporter})"
    else:
        telemetry_line = "telemetry: disabled"
    result: list[str] = [logging_line, telemetry_line]
    return result
