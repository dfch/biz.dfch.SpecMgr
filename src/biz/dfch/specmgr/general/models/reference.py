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

"""One row of the generic ``list_references`` tool's ``PagedResult`` (feat-144-ref-artifact Phase 2).

The ``list_references`` tool (``general.tools.list_references``)
regex-extracts every ``<TYPE> <uuid>`` cross-reference from one source
document's frontmatter-stripped body, deduplicates repeated occurrences of
the same reference (first-occurrence order preserved), resolves each unique
reference to the referenced document in its own target domain, and returns
one :class:`ReferenceRow` per unique reference, paged
(``PagedResult[ReferenceRow]`` via the shared ``list_*`` mechanism, ADR
ec9f5262). A reference that cannot be resolved on disk still yields a row --
``title``/``path`` are ``None`` and ``error`` carries the target domain's
own not-found message (``list_*``-style inline failure) instead of the tool
raising.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["ReferenceRow"]


class ReferenceRow(BaseModel):
    """One cross-reference extracted from a source document, plus its resolution outcome.

    Parameters
    ----------
    type:
        The referenced document's target domain name, lowercase -- one of
        ``general.tools._references.REFERENCE_TYPES`` (``gol``/``prb``/
        ``qa``/``uc``/``req``/``rsk``/``dec``/``adr``/``vcr``/``sysrs``;
        the reference tag itself is the uppercase form of this value).
    id:
        The referenced document's own specmgr-assigned identifier -- a
        canonical lowercase-hex UUID, as it appeared in the source body
        (lowercased).
    title:
        The referenced document's ``# {title}`` H1, re-derived from the
        resolved document on disk (``doc.body.text`` for the flat target
        domains, ``doc.body.title`` for ``adr``) -- or ``None`` if the
        reference could not be resolved (``error`` is set).
    path:
        The referenced document's real, absolute (``.resolve()``d)
        on-disk file path, for a caller that wants to read it directly
        instead of going through the matching ``get_<domain>`` tool -- or
        ``None`` if the reference could not be resolved (``error`` is
        set).
    error:
        ``None`` for a successfully resolved reference. Otherwise, the
        ``str()`` of the target domain's ``XNotFoundError`` raised while
        resolving this reference, so a caller can see *why* it failed
        without a second round trip.
    """

    type: str
    id: str
    title: str | None = None
    path: str | None = None
    error: str | None = None
