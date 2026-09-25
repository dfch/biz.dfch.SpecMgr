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

"""The single source of truth for the document-type domain names (feat-125-domain-lists, REQ-001).

Every other module that names a set of document types imports the names from
here instead of hand-listing them itself (the feat-125 sweep ruling: no
other ``src/`` or ``tests/`` module may hand-list a domain-name set).

:data:`WHOLE_BODY_DOMAINS` is the only hand-listed tuple in the module --
the whole-body document types in the canonical order ``req``, ``uc``,
``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
``vcr``, ``sysrs`` -- and every other tuple is derived from it, never
hand-listed a second time: :data:`WHOLE_BODY_NO_FEAT_DOMAINS` is the
whole-body domains without ``feat``, :data:`UUID_DOMAINS` is those plus
``adr``, and :data:`ALL_DOMAINS` is ``adr`` prefixed to the whole-body
domains. :data:`ADR` and :data:`FEAT` are the two name singletons. A new
document type registers its name in :data:`WHOLE_BODY_DOMAINS` once, and
every derived tuple picks it up by construction.
"""

__all__ = [
    "ADR",
    "FEAT",
    "WHOLE_BODY_DOMAINS",
    "WHOLE_BODY_NO_FEAT_DOMAINS",
    "UUID_DOMAINS",
    "ALL_DOMAINS",
]

#: The ``adr`` document type (singleton).
ADR = "adr"

#: The ``feat`` document type (singleton): the one whole-body domain whose
#: ``id`` is a chosen ``feat-NNN-slug`` folder name, not a server-generated
#: UUID.
FEAT = "feat"

#: The whole-body document types in the canonical order -- the only
#: hand-listed tuple in this module.
WHOLE_BODY_DOMAINS = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "sysrs")

#: The whole-body document types without ``feat`` (derived from
#: :data:`WHOLE_BODY_DOMAINS`, never hand-listed).
WHOLE_BODY_NO_FEAT_DOMAINS = tuple(d for d in WHOLE_BODY_DOMAINS if d != FEAT)

#: The UUID-shaped document types: the whole-body domains without ``feat``,
#: plus ``adr`` (derived from :data:`WHOLE_BODY_DOMAINS`, never hand-listed).
UUID_DOMAINS = WHOLE_BODY_NO_FEAT_DOMAINS + (ADR,)

#: Every document type: ``adr`` plus the whole-body domains (derived from
#: :data:`WHOLE_BODY_DOMAINS`, never hand-listed).
ALL_DOMAINS = (ADR,) + WHOLE_BODY_DOMAINS
