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

"""Question and Answer (QA) domain -- requirements-elicitation interview specifications.

This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
mirroring ``req``'s/``tsk``'s layout, containing models, tools, prompts, and
resources for managing ``qa`` documents.

Import this package to register all QA tools/prompts/resources against the
shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import qa  # noqa: F401 (side-effects only)

``tools`` (``parse_qa``, ``get_qa``, ``get_qa_example``, ``get_qa_template``,
``create_qa``, ``update_qa``, ``set_status_qa``, ``delete_qa``,
``validate_qa``), ``resources`` (``specmgr://qa/schema``,
``specmgr://qa/example``, ``specmgr://qa/template``, ``specmgr://qa/list``),
and ``prompts`` (``create_qa``, ``update_qa``) all exist. Like REQ, QA has no
``specmgr://qa/{id}`` resource -- id-based reads go through the ``get_qa``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Note: as of Phase 4 (MCP Surface), this domain's tools/resources/prompts are
implemented and importable standalone, but ``server.py``'s own bottom-of-file
import list does not import ``qa`` yet -- that registration wiring is Phase
5's Task 5.1.
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
