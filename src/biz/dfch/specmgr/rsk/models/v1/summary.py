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

"""Pydantic model for one line of RSK listing output (Phase 2, Task 2.3).

Mirrors :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary` for the
paged ``list_rsk`` tool (Phase 3, Task 3.14 -- not yet built; per feat-13 /
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13 there is no ``specmgr://rsk/list``
resource, so a summary line carries more than the base's four fields: the
initial/residual zone levels, the TARA strategy word, the first ``## Scope``
entry, and the residual risk's matrix coordinates, so a register-wide
risk-matrix view can be built from the listing alone). Subclasses
:class:`~biz.dfch.specmgr.general.models.summary.DocSummary` for its
``id``/``title``/``status``/``ref`` fields (feat-13 Task 1.3, REQ-003).

The risk-specific fields are derived by the :meth:`RskSummary.from_document`
classmethod from the parsed document's assessments -- via their computed
``level``/``value`` fields and the shared ``level_from_product`` mapping --
never re-implementing the 5x5 zone mapping here.
"""

from __future__ import annotations

from pydantic import Field

from ....general.models.summary import DocSummary
from .document import RskDocument

__all__ = ["RskSummary"]


class RskSummary(DocSummary):
    """One line of the paged ``list_rsk`` tool's output.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier, or ``None`` if the file
        has not been assigned one yet (e.g. hand-authored without the
        ``id`` frontmatter key). Inherited from :class:`DocSummary`.
    title:
        The risk's ``# {title}`` H1. Inherited from :class:`DocSummary`.
    status:
        The risk's ``frontmatter.status`` value, verbatim (one of the closed
        six-value set). Inherited from :class:`DocSummary`.
    ref:
        The document's extensionless base name (e.g.
        ``"rsk-<uuid>-a-title"``). Inherited from :class:`DocSummary`.
    path:
        The real, absolute (``.resolve()``d) filesystem path to the
        document's on-disk file. Inherited from :class:`DocSummary`
        (feat-81-83-validation Phase 3, REQ-007).
    initial_level:
        The 5x5 zone (`low`/`medium`/`high`/`very high`) of the document's
        `## Initial Assessment` (before mitigation) -- its probability x
        impact product mapped by the assessments' own computed `level`.
    residual_level:
        The 5x5 zone of the document's `## Residual Assessment` (after
        mitigation) -- same derivation as `initial_level`.
    strategy:
        The document's `## Strategy` TARA word, verbatim (`transfer`/
        `accept`/`reduce`/`avoid`).
    scope:
        The first entry of the document's `## Scope` list (the affected
        system/component the summary line represents).
    residual_probability:
        The 1..5 probability coordinate of the residual assessment (value
        carried by its `### Probability {1..5}` heading).
    residual_impact:
        The 1..5 impact coordinate of the residual assessment (value
        carried by its `### Impact {1..5}` heading).
    residual_product:
        The risk product (residual probability x residual impact, 1..25) --
        the matrix coordinate that determines `residual_level` via the
        shared zone mapping.
    """

    initial_level: str = Field(
        description="The 5x5 zone (low/medium/high/very high) of the ## Initial Assessment (before mitigation)."
    )
    residual_level: str = Field(
        description="The 5x5 zone (low/medium/high/very high) of the ## Residual Assessment (after mitigation)."
    )
    strategy: str = Field(description="The ## Strategy TARA word, verbatim (transfer/accept/reduce/avoid).")
    scope: str = Field(
        description="The first entry of the ## Scope list (the affected system/component the summary line represents)."
    )
    residual_probability: int = Field(
        ge=1,
        le=5,
        description="The 1..5 probability coordinate of the ## Residual Assessment (value in its H3 heading).",
    )
    residual_impact: int = Field(
        ge=1,
        le=5,
        description="The 1..5 impact coordinate of the ## Residual Assessment (value in its H3 heading).",
    )
    residual_product: int = Field(
        ge=1,
        le=25,
        description="The risk product (residual probability x residual impact, 1..25).",
    )

    @classmethod
    def from_document(cls, document: RskDocument, ref: str, path: str | None = None) -> RskSummary:
        """Build one summary line from a parsed :class:`RskDocument`.

        The Phase 3 ``list_rsk`` tool's construction site: it derives every
        risk-specific field from the parsed document's assessments (via
        their computed ``level``/``value`` fields -- the 5x5 zone mapping is
        never re-implemented here) and takes the base's four fields
        (``id``/``title``/``status``) from the frontmatter/body as the other
        domains' listing tools do.

        Parameters
        ----------
        document:
            The fully parsed risk document.
        ref:
            The document's extensionless base name (e.g. a file path's
            ``stem``), for the inherited ``ref`` field.
        path:
            The real, absolute (``.resolve()``d) filesystem path to the
            document's on-disk file, for the inherited ``path`` field
            (feat-81-83-validation Phase 3, REQ-007). ``None`` defaults to
            the empty string -- callers building a real ``list_rsk`` row
            always pass this; it is optional only so existing callers that
            construct a summary purely for its risk-specific fields are not
            forced to supply a path.

        Returns
        -------
        RskSummary
            The one-line summary of the document.
        """
        assert isinstance(document, RskDocument), type(document)
        assert isinstance(ref, str), type(ref)
        assert path is None or isinstance(path, str), type(path)

        body = document.body
        residual = body.residual_assessment
        probability: int = residual.probability.value
        impact: int = residual.impact.value

        result = cls(
            id=document.frontmatter.id,
            title=body.text,
            status=document.frontmatter.status,
            ref=ref,
            path=path if path is not None else "",
            initial_level=body.initial_assessment.level,
            residual_level=residual.level,
            strategy=body.strategy.value.text,
            scope=body.scope.items[0].text,
            residual_probability=probability,
            residual_impact=impact,
            residual_product=probability * impact,
        )
        return result
