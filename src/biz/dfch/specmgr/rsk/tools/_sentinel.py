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

"""RSK's sentinel-document construction for ``list_rsk``'s failed-entry rows (feat-81-83-validation Phase 3, Task 3.2).

``RskSummary`` is the only domain summary type carrying fields beyond the
shared ``DocSummary`` base (``initial_level``, ``residual_level``,
``strategy``, ``scope``, ``residual_probability``, ``residual_impact``,
``residual_product``) -- see the feature README's Design Notes
("``RskSummary``'s extra fields -- sentinel-document design") for the full
rationale, including why weakening those fields to ``Optional`` or
fabricating schema-valid-but-plausible placeholder data were both rejected.

Instead, :data:`_SENTINEL_RSK_TEXT` is a fixed, valid, deliberately
worst-case-severity risk document -- ``Probability 5``/``Impact 5`` in both
``## Initial Assessment`` and ``## Residual Assessment`` -- parsed exactly
once, at import time, via the real, unmodified :func:`parse_rsk` pipeline
into :data:`_SENTINEL_RSK_DOCUMENT`. Every risk-specific value on a failed
row (``strategy``, ``scope``, ``initial_level``/``residual_level``,
``residual_probability``/``residual_impact``/``residual_product``) comes
from genuine parsing and derivation, never a hand-typed literal, so it can
never drift out of sync with ``level_from_product``'s own thresholds: a
future schema-breaking change to the RSK model surfaces as a loud
sentinel-parse failure (caught by this module's own dedicated test), not
silent staleness.

**Deviation from the plan's original design** (recorded in the feature
README's Decisions Made log): the sentinel's own H1 is a plain descriptive
title, not literally the ``FAILED_TO_PARSE_MARKER`` text
(``"<failed to parse>"``) -- writing that literal string as a markdown H1
is rejected by ``models.md``'s own raw-HTML guard (a bare ``<...>`` token
parses as ``html_inline``, feat-27-validation), and every escape-hatch that
survives the guard (a code span, a backslash escape) leaves its own
markdown syntax embedded in ``MarkdownSection.text``'s raw-source-derived
output instead of yielding the bare marker string. ``title`` is therefore
overridden via ``model_copy`` alongside ``id``/``status``/``path``/
``error`` -- five fields instead of the originally-planned four -- both
using the exact same
:data:`~biz.dfch.specmgr.general.tools._listing.FAILED_TO_PARSE_MARKER`
constant every other domain's failed entries use, so the two can never
drift apart from each other even though ``title`` is no longer read off
the sentinel document itself.

:func:`build_failed_rsk_summary` builds one failed row by running the
already-parsed sentinel through the same
:meth:`~biz.dfch.specmgr.rsk.models.v1.RskSummary.from_document` factory
every real row uses, then ``model_copy(update=...)`` for the five fields no
document could ever supply: ``id``, ``title``/``status`` (both the shared
marker), ``path``, and ``error``.
"""

from __future__ import annotations

from pathlib import Path

from ...general.tools._listing import FAILED_TO_PARSE_MARKER
from ..models.v1 import RskDocument, RskSummary, parse_rsk

__all__ = ["build_failed_rsk_summary"]

#: A fixed, valid, deliberately worst-case-severity (Probability 5 / Impact
#: 5 in both assessments) sentinel risk document. Its H1 is a plain
#: descriptive title, not the ``FAILED_TO_PARSE_MARKER`` text itself -- see
#: this module's own docstring ("Deviation from the plan's original
#: design") for why. ``status: dropped`` and ``## Strategy`` -- ``accept``
#: -- are the most passive/neutral values of their respective closed
#: vocabularies (``RskFrontmatter._ALLOWED_STATUSES`` / ``Strategy``'s TARA
#: 4-value set), so a fabricated row cannot accidentally trigger any
#: strategy/status-keyed downstream automation.
_SENTINEL_RSK_TEXT = """\
---
created: '2026-01-01 00:00:00.000Z'
status: dropped
type: rsk
updated: '2026-01-01 00:00:00.000Z'
version: 1.0.0
---

# RSK Sentinel Document (Internal)

<!-- Internal sentinel document for list_rsk's failed-entry rows (feat-81-83-validation Phase 3); never a real risk. -->

## Cause

This is a fixed sentinel document parsed once by rsk.tools._sentinel, not a real risk register entry.

## Trigger

Not applicable -- this sentinel document represents a risk document that failed to parse, not an actual risk.

## Consequence

Not applicable -- see Cause.

## Scope

- unknown

## Initial Assessment

### Probability 5

### Impact 5

## Strategy

accept

## Mitigation

none

## Residual Assessment

### Probability 5

### Impact 5

## More Information

Parsed once at import time via the real parse_rsk pipeline (no validation bypass) to back a failed
list_rsk row's derived fields; see the feature README's Design Notes ("RskSummary's extra fields --
sentinel-document design").
"""

#: Parsed exactly once, at import time, via the real, unmodified `parse_rsk` pipeline (no bypass).
_SENTINEL_RSK_DOCUMENT: RskDocument = parse_rsk(_SENTINEL_RSK_TEXT)


def build_failed_rsk_summary(path: Path, error: Exception) -> RskSummary:
    """Build one ``list_rsk`` failed-entry row from the parsed sentinel document.

    Parameters
    ----------
    path:
        The on-disk path of the risk file that failed to parse.
    error:
        The exception caught while parsing ``path``.

    Returns
    -------
    RskSummary
        A summary built from :data:`_SENTINEL_RSK_DOCUMENT` via
        :meth:`RskSummary.from_document` (so every risk-specific field is
        genuinely derived, never hand-typed), with ``id``/``title``/
        ``status``/``path``/``error`` overridden -- the five fields no
        document could ever supply (``title``, unlike the other eleven
        domains, is one of those five here -- see this module's own
        docstring).
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(error, Exception), type(error)

    base = RskSummary.from_document(_SENTINEL_RSK_DOCUMENT, ref=path.stem)
    result = base.model_copy(
        update={
            "id": None,
            "title": FAILED_TO_PARSE_MARKER,
            "status": FAILED_TO_PARSE_MARKER,
            "path": str(path.resolve()),
            "error": str(error),
        }
    )
    return result
