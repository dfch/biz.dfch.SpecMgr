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

Mirrors :class:`~biz.dfch.specmgr.dec.models.v1.summary.DecSummary`'s shape.
``FeatSummary`` originally redeclared its own extra ``path`` field, a
deliberate `feat`-only divergence at the time, since ADR
e369ee2e-3353-4f92-991c-6367d76d832e's whole governing convention *is*
direct hand/agent markdown editing of ``.specmgr/feat/<id>/README.md``,
which remains normal and sanctioned even after `feat`'s own MCP tools
exist. feat-81-83-validation Phase 3/4 (REQ-007) generalized ``path`` (and
``error``) onto the shared
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary` base for
*every* whole-body domain, retrofitting ``FeatSummary.path`` to the same
resolved (absolute) form the other eleven domains use -- so
``FeatSummary``'s own separate ``path`` field declaration was removed in
that same pass; it is now inherited, not redeclared. ``feat``'s own
workflow still treats ``path`` as a first-class, sanctioned direct-read
entry point (unlike the tool-only-mutation convention `path` is scoped to
elsewhere, per feat-81-83-validation's own Design Notes), it just no
longer needs its own field for that. See
``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Addressing")
for the full original rationale.
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
        filename or path (mirrors
        :class:`~biz.dfch.specmgr.dec.models.v1.summary.DecSummary`); pass
        it to ``get_feat`` alongside (or instead of) ``id``. Named ``ref``
        rather than ``filename`` for that reason, even though ``path``
        (below) does now expose the real filesystem path directly.
    path:
        The real, absolute (``.resolve()``d) filesystem path to the
        document's ``README.md`` (e.g.
        ``.specmgr/feat/feat-31-feature/README.md``); the containing folder
        is trivially ``Path(path).parent`` for a caller that wants to look
        at sibling files. Inherited from
        :class:`~biz.dfch.specmgr.general.models.summary.DocSummary`, not
        redeclared here (feat-81-83-validation Phase 4) -- see this
        module's own docstring above.
    """
