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

"""MCP resource registrations for Use Case (UC) documents (Task 3.1.4, 3.1.6).

``uc_schema`` registers the persisted-JSON-Schema resource
(``specmgr://uc/schema``). ``uc_example`` registers the packaged sample
use-case document resource (``specmgr://uc/example``). ``uc_template``
registers the packaged use-case template resource (``specmgr://uc/template``)
-- every field present, populated with short placeholder ("blind text")
content rather than a valid document instance. ``uc_plantuml`` registers the
static domain-knowledge rulebook resource (``specmgr://uc/plantuml``,
feat-185-uc-diagrams Phase 100) -- the frozen UC → PlantUML mapping and
validation spec, raw markdown, the same shape as ``specmgr://rsk/tara``.
``uc_plantuml_template``/``uc_plantuml_example`` register the packaged
PlantUML-source pair (``specmgr://uc/plantuml-template``/
``specmgr://uc/plantuml-example``, feat-185-uc-diagrams Phase 120) -- the
sequence-skeleton template and the complete, fully attributed "Buy Goods"
sequence example, raw PlantUML source, ``text/plain`` (not markdown, not
specmgr documents: no frontmatter, not validate-able).
Import this package to
register all use-case resources against the shared ``mcp`` application
instance::

    from biz.dfch.specmgr.uc import resources  # noqa: F401 (side-effects only)

Unlike ADR, UC has no by-id single-document *resource* --
``specmgr://uc/{id}`` was never added; ``get_uc`` (``uc.tools.get_uc``) is
the id-based read path instead, mirroring REQ's own precedent (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614). The former listing resource
(``uc_list``, ``specmgr://uc/list``, Task 3.1.6) was replaced the same way
by the ``list_uc`` ``@mcp.tool()`` (``uc.tools.list_uc``), so that paging
parameters (``max_results``/``offset``) could be accepted -- see
``.specmgr/feat/feat-13-list-paging/README.md``.
"""

from . import uc_example, uc_plantuml, uc_plantuml_example, uc_plantuml_template, uc_schema, uc_template  # noqa: F401

__all__ = [
    "uc_example",
    "uc_plantuml",
    "uc_plantuml_example",
    "uc_plantuml_template",
    "uc_schema",
    "uc_template",
]
