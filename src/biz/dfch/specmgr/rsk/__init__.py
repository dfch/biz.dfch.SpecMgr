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

"""Risk (RSK) domain -- risk registers for system specifications.

This is a domain-first package, mirroring ``tsk``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``rsk`` documents.

Import this package to register all risk tools/prompts/resources
against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import rsk  # noqa: F401 (side-effects only)

``tools`` (``parse_rsk``, ``get_rsk``, ``list_rsk``, ``get_rsk_example``,
``get_rsk_template``, ``create_rsk``), ``resources``
(``specmgr://rsk/schema``,
``specmgr://rsk/example``, ``specmgr://rsk/template``,
``specmgr://rsk/tara``, ``specmgr://rsk/risk-matrix``), and ``prompts``
(``create_risk``, ``update_risk``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="rsk"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="rsk"``).
Disk-free, id-free dry-run content validation goes through the generic
``validate`` tool in ``general.tools`` (``type="rsk"``) -- the former
``validate_rsk`` tool was removed in favor of it (feat-81-83-validation).
Like REQ/TSK, RSK has no
``specmgr://rsk/{id}`` resource -- id-based reads go through the
``get_rsk`` tool only (same rationale as ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
"Expose id-based document reads as a tool, not a resource" -- RSK never had
such a resource to remove in the first place). Likewise, there is no
``specmgr://rsk/list`` resource -- listing is the paged ``list_rsk`` tool,
so that paging parameters could be accepted (feat-13-list-paging, ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13).
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
