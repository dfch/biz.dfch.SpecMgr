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

"""The Architecture Decision Record (ADR) domain package.

See ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain".

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
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
