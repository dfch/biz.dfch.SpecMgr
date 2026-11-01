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

"""MCP prompt registrations that are not specific to any single document
domain (Various improvements, Task 0.21; repair: feat-150-mcp-lifecycle-
commands, Phase 1).

``compact_history`` guides rotating older ``### Recent Updates`` entries out
of any `.specmgr` feature folder's ``README.md`` into an optional sibling
``history.md``. ``repair`` (cross-cutting: takes ``type`` + an optional
``id``, ADR excluded) guides repairing a whole-body document that fails to
parse via a host-native raw read, a ``validate(full=True)`` loop, a raw
write-back, and a post-write ``get_<d>``/``list_<d>`` confirmation.
``translate_artifact`` (feat-197-i18n, Phase 130; cross-cutting: takes
``type`` + ``id`` + a target ``language`` + an optional ``source_language``,
``feat``/``adr`` rejected as always-English) guides producing or updating a
language variant of a document from its source-language content: read the
``specmgr://i18n`` resource first, read the source, decide create versus
update, translate only free-form prose and fixed heading text (never the
closed-vocabulary tokens), retry the write on a non-raising ``ValidateResult``,
verify against the file on disk. Domain-specific prompts (e.g.
``create_adr``/``refine``) live under their own domain package instead. Import this package to register all general
prompts against the shared ``mcp`` application instance::

    from biz.dfch.specmgr.general import prompts  # noqa: F401 (side-effects only)
"""

from .compact_history import compact_history
from .repair import repair
from .translate_artifact import translate_artifact

__all__ = [
    "compact_history",
    "repair",
    "translate_artifact",
]
