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

"""General-purpose (cross-cutting, not domain-specific) tools, resources, and
prompts.

This package provides tools, resources, and prompts that apply to any markdown
file in the system, regardless of document type (ADR, use case, etc.), or that
are not specific to any single document domain at all (e.g. the server
version). It complements the domain-specific packages (``adr``, ``req``,
``uc``).

``tools`` (e.g. ``mdformat``, ``webfetch``) operate on raw markdown files or
external URLs and are registered as ``@mcp.tool()`` functions. ``resources``
(e.g. ``version``, ``iso25010``, ``rasci``) are registered as
``@mcp.resource()`` functions. ``prompts`` (e.g. ``compact_history``) return
instructional text and are registered as ``@mcp.prompt()`` functions. Import
this package to register all general tools, resources, and prompts against
the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import general  # noqa: F401 (side-effects only)
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
