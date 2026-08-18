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
mirroring ``req``'s/``tsk``'s layout, containing models (and, from
`.specmgr/feat/feat-12-qa-artifact/README.md` Phase 4 onward, tools,
prompts, and resources) for managing ``qa`` documents.

As of Phase 3 (Pydantic Models & Parser), only ``qa.models.v1`` exists --
``qa.tools``/``qa.resources``/``qa.prompts`` are Phase 4 work and this
module deliberately does not import them yet (there is nothing to import).
Once Phase 4 lands, this module's own import line should mirror
``tsk/__init__.py``'s ``from . import prompts, resources, tools`` so
``server.py``'s bottom-of-file import registers ``qa``'s MCP surface too.
"""
