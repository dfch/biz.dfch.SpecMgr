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

"""Pydantic model for one line of FEAT listing output (Phase 2, ``list_feat``).

Mirrors :class:`~biz.dfch.specmgr.dec.models.v1.summary.DecSummary`'s shape,
plus one extra field, ``path``, beyond the inherited
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary`'s
``id``/``title``/``status``/``ref`` -- a deliberate, `feat`-only divergence.
``DocSummary.ref``'s own docstring states callers "must not read this off
disk themselves, only pass it to the matching domain's ``get_<domain>``
tool" -- a policy every other domain's summary (including
:class:`~biz.dfch.specmgr.models.adr.v1.summary.AdrSummary`) enforces. `feat`
is the opposite case: ADR e369ee2e-3353-4f92-991c-6367d76d832e's whole
governing convention *is* direct hand/agent markdown editing of
``.specmgr/feat/<id>/README.md``, which remains normal and sanctioned even
after `feat`'s own MCP tools exist -- so hiding the real path behind ``ref``
alone would work against the domain's own intended workflow. ``id``/``ref``
stay on ``FeatSummary`` too (still useful for ``get_feat``/``update``/
``set_status`` lookups) -- ``path`` is additive, not a replacement. See
``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Addressing") for
the full rationale.
"""

from __future__ import annotations

from ....general.models.summary import DocSummary

__all__ = ["FeatSummary"]


class FeatSummary(DocSummary):
    """One line of ``list_feat`` output.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier (its containing folder's
        own name, e.g. ``"feat-31-feature"`` -- REQ-004's addressing
        convention), or ``None`` if the file has not been assigned one yet
        (e.g. hand-authored without the ``id`` frontmatter key).
    title:
        The feature's ``# Feature: {title}`` H1 (the free-form title after
        the ``"Feature: "`` prefix, i.e. `Feature.text`).
    status:
        The feature's ``frontmatter.status`` value, verbatim.
    ref:
        The document's extensionless base name, deliberately *not* a
        filename or path -- callers must not read this off disk themselves,
        only pass it to ``get_feat`` alongside (or instead of) ``id``. Named
        ``ref`` rather than ``filename`` precisely to avoid inviting direct
        filesystem access (mirrors
        :class:`~biz.dfch.specmgr.dec.models.v1.summary.DecSummary`).
    path:
        The real filesystem path to the document's ``README.md`` (e.g.
        ``.specmgr/feat/feat-31-feature/README.md``); the containing folder
        is trivially ``Path(path).parent`` for a caller that wants to look
        at sibling files. A deliberate, `feat`-only addition -- see this
        module's own docstring above.
    """

    path: str
