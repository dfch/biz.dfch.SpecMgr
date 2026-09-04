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

"""System Requirements Specification (SYSRS) domain -- an aggregator document type that
ties together already-existing specmgr artifacts (``gol``, ``prb``, ``qa``, ``uc``,
``req``, ``rsk``, ``dec``/``adr``, ``vcr``) into one coherent, navigable specification,
rather than duplicating their content.

This is a domain-first package, mirroring ``sop``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts, and
resources for managing ``sysrs`` documents. A ``sysrs`` is built on the
generic ``models/md`` parser with the simple surface used by GOL/RSK/QA/DEC/
SOP/VCR -- no fine-grained mutation tools, no by-id resource, no
deterministic re-render.

``sysrs`` is, like SOP, built from scratch entirely on the generic
mutation tools (ADR 36905d5b-8057-4294-8665-c7eed5534db0): it has no
``update_sysrs``/``set_status_sysrs`` tools of its own -- it dispatches
straight into the generic ``update``/``set_status`` tools in
``general.tools``, and deletion goes through the generic ``delete`` tool
in ``general.tools`` (``type="sysrs"``), the same convention SOP/VCR
already use.

``sysrs.models``, ``sysrs.tools`` (6 tools -- ``create_sysrs``,
``get_sysrs``, ``get_sysrs_example``, ``get_sysrs_template``,
``list_sysrs``, ``parse_sysrs``; there is no ``validate_sysrs`` --
disk-free, id-free dry-run content validation goes through the generic
``validate`` tool in ``general.tools`` (``type="sysrs"``) instead, as of
feat-81-83-validation Phase 2), ``sysrs.resources`` (3 resources --
``specmgr://sysrs/schema``, ``specmgr://sysrs/example``,
``specmgr://sysrs/template``; no ``/{id}``, no ``/list``), and
``sysrs.prompts`` (2 prompts -- ``create_sysrs``, ``update_sysrs``) all
carry real content. Every cross-reference section
(``### Goals``, ``## Decisions``, ``## Requirements``'s nine H3s, ...)
carries a per-section type-tag regex enforcing which domain(s) it may
reference -- see ``sysrs.models.v1.body``.

Import this package to register everything SYSRS eventually exposes
against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import sysrs  # noqa: F401 (side-effects only)
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
