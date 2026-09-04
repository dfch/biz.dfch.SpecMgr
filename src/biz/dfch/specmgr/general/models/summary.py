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

"""Common base for every domain's one-line listing summary (feat-13 Task 1.3, REQ-003/ACC-001).

``ReqSummary``, ``UcSummary``, ``TskSummary``, and ``QaSummary`` each
subclass :class:`DocSummary` instead of independently redeclaring the same
four fields.

**ADR is a deliberate exception.** ``biz.dfch.specmgr.models.adr.v1.summary.
AdrSummary`` does *not* subclass :class:`DocSummary`: that module is part of
the dependency-free base library (``models/adr`` has no dependency on
``mcp``/``tools``/``resources``/``prompts`` -- see ``AGENTS.md``'s "models
location" note), whereas this ``general`` package's own ``__init__.py``
unconditionally imports its ``tools``/``resources``/``prompts``
sub-packages, which in turn import ``server.mcp`` -- so importing anything
under ``general`` (this module included) already requires the ``mcp``
extra to be installed. Making ``AdrSummary`` subclass :class:`DocSummary`
would therefore silently add a new, previously-absent ``mcp`` dependency to
the base library. ``AdrSummary`` instead keeps its own, field-identical
declaration; a structural (not inheritance-based) test asserts the two
stay in sync. See ``.specmgr/feat/feat-13-list-paging/README.md``'s
Decisions Made log for the full rationale.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["DocSummary"]


class DocSummary(BaseModel):
    """Common ``id``/``title``/``status``/``ref``/``path``/``error`` fields shared by every domain's summary model.

    ``path``/``error`` were added in feat-81-83-validation Phase 3 (REQ-006/
    REQ-007): ``path`` generalizes ``FeatSummary``'s own, previously
    ``feat``-only ``path`` field to every whole-body domain, and ``error``
    lets a failed-to-parse document appear inline in a ``list_<domain>``
    page instead of being silently skipped (see
    ``general.tools._listing.build_summaries``).

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key), or if this entry represents a document
        that failed to parse at all (``error`` is set).
    title:
        The document's ``# {title}`` H1, or the fixed marker
        ``"<failed to parse>"`` if this entry represents a document that
        failed to parse (``error`` is set).
    status:
        The document's ``frontmatter.status`` value, verbatim, or the fixed
        marker ``"<failed to parse>"`` if this entry represents a document
        that failed to parse (``error`` is set).
    ref:
        The document's extensionless base name (e.g.
        ``"req-<uuid>-a-title"``), deliberately *not* a filename or path --
        pass it to the matching domain's ``get_<domain>`` tool alongside
        (or instead of) ``id``. Named ``ref`` rather than ``filename`` for
        that reason, even though ``path`` (below) does now expose the real
        filesystem path directly for a caller that wants it (REQ-007,
        feat-81-83-validation Phase 3/4). Derived from the filename/folder
        alone, so it is always populated even for a document that failed
        to parse.
    path:
        The real, absolute (``.resolve()``d) filesystem path to the
        document's on-disk file, for a caller that wants to read it
        directly instead of going through ``get_<domain>``. Always
        populated, even for a document that failed to parse -- reading a
        filename never requires successfully parsing its content.
    error:
        ``None`` for a successfully-parsed document. Otherwise, the
        ``str()`` of the exception (``AssertionError``,
        ``pydantic.ValidationError``, or ``yaml.YAMLError``) raised while
        parsing this document, so a caller can see *why* it failed without
        a second round trip.
    """

    id: str | None
    title: str
    status: str
    ref: str
    path: str
    error: str | None = None
