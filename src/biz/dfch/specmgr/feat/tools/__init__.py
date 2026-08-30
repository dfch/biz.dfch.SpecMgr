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

"""Feature (FEAT) MCP tools.

**Phase 0 scaffolding only.** Populated in Phase 2 of
``.specmgr/feat/feat-31-feature/README.md``: bespoke, folder-per-document
addressing (``_paths.py``, ``_io.py``, ``_lock.py``, ``_write.py`` -- *not*
built on ``general/tools/_doc_paths.py``, since ``feat`` documents live one
per folder at ``<base>/<id>/README.md`` with a non-UUID id) plus the eight
lifecycle tools (``create_feat``, ``parse_feat``, ``list_feat``,
``get_feat``, ``get_feat_example``, ``get_feat_template``, ``delete_feat``,
``validate_feat``). No ``update_feat``/``set_status_feat`` -- those go
through the generic ``update``/``set_status`` tools in ``general.tools``
(``type="feat"``, added in the same phase).
"""

__all__: list[str] = []
