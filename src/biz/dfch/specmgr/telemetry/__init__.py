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

"""Shared logging/telemetry infrastructure for the MCP server (feat-139-logging-telemetry).

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
"""

from . import config, logging, middleware, otel  # noqa: F401

__all__ = [
    "config",
    "logging",
    "middleware",
    "otel",
]
