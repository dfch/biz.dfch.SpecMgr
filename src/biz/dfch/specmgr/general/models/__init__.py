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

"""Shared, cross-domain Pydantic models with no document-type-specific content.

Backs feat-13's ``<domain>_list`` -> ``list_<domain>`` pagination rollout
(``.specmgr/feat/feat-13-list-paging/README.md`` Task 1.1/Task 1.3):

- :class:`PagedResult` -- a generic ``{total, offset, max_results, truncated,
  results}`` page wrapper, shared by every domain's ``list_<domain>`` tool.
- :class:`DocSummary` -- the common ``id``/``title``/``status``/``ref`` field
  set that every domain's own ``*Summary`` model (``ReqSummary``,
  ``UcSummary``, ``TskSummary``, ``QaSummary``) subclasses.

Also backs feat-81-83-validation Phase 2's generic ``validate`` tool
(REQ-004) -- originally greenfield for that tool alone; since feat-170
(case 4 of the ADR 519d1206 non-raising chain) it also backs the generic
``update``/``edit`` tools' own content-validation-failure branches, and
since feat-204-create-error (case 5 of the same chain) the 24
``create_<d>``/``parse_<d>`` tools' branches:

- :class:`ValidateResult`/:class:`ValidationErrorEntry` -- the non-raising,
  structured ``{valid, errors}`` result those tools return for a
  content-validation failure instead of letting the exception propagate.
  The ``validate_result`` submodule
  (``biz.dfch.specmgr.general.models.validate_result``) is the chain
  record and owns the two shared constants every such branch must
  import -- ``_CAUGHT_EXCEPTIONS`` (the exact exception channels to
  catch) and ``_MAX_VALIDATE_ERROR_CHARS`` (the
  ``ValidationErrorEntry.message`` cap, feat-110) -- re-exported by
  ``general.tools.validate`` under the same private names.

Also backs feat-103-set-status-error's narrow extension of that same
non-raising workaround to the generic ``set_status`` tool's own single
failure mode (ADR b399f1ce-ed42-4929-b01c-7a57d18e8014):

- :class:`InvalidStatusResult` -- the non-raising, structured result the
  generic ``set_status`` tool (``general.tools.set_status``) returns for an
  out-of-vocabulary ``status`` value, instead of letting
  ``pydantic.ValidationError`` propagate. Distinct from
  :class:`ValidateResult` -- a different tool's own model.

Also backs feat-134-related-artifact-similarity's (Phase 3) two generic
similarity tools (ADR 750842b2-aca4-4649-ba0c-855ec8e1f505):

- :class:`SimilarityUnavailableResult` -- the non-raising, structured
  ``{available, reason, message}`` result the ``find_related``/
  ``find_similar_text`` tools return whenever the embedding backend is
  unavailable (the ``SPECMGR_SIMILARITY_DISABLED`` opt-out env var is
  present, or the backend fails to import or the model fails to load),
  instead of raising. Mirrors :class:`InvalidStatusResult`'s own
  non-raising precedent -- a different tool surface's own model.
- :class:`SimilarityHit` -- one ranked hit row (the plan's own hit shape
  ``{type, id, title, status, path, score}``, ACC-001/ACC-002) the
  ``find_related``/``find_similar_text`` tools return, sorted by
  ``score`` descending; an unparseable candidate's row carries
  ``id = None`` and the ``"<failed to parse>"`` marker title/status
  (REQ-009).

Also backs feat-150-mcp-lifecycle-commands Phase 1a's narrow extension of
that same non-raising workaround to the ``get_<d>`` tools' own parse-
failure case (ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c):

- :class:`ParseFailureResult` -- the non-raising, structured result every
  ``get_<d>`` tool returns when the requested id resolves to an on-disk
  file whose content fails to parse, instead of letting the domain's
  ``XNotFoundError`` propagate. Distinct from :class:`ValidateResult` and
  :class:`InvalidStatusResult` -- a different tool's own model.

Also backs feat-92-resources's cross-cutting reference-resource
model-backed drift-guard convention (ADR
356d8781-e446-4c26-917a-eda85648ce9d, REQ-002/REQ-005/REQ-006):

- :func:`parse_dtais`/:class:`Dtais` -- parses the DTAIS verification-
  methods guidance document (``general/data/general_dtais.md``) backing
  ``specmgr://dtais``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).
- :func:`parse_rasci`/:class:`Rasci` -- parses the RASCI responsibility-
  assignment guidance document (``general/data/general_rasci.md``) backing
  ``specmgr://rasci``, purely to fail fast on structural drift (the parsed
  result is discarded by the resource itself).
- :func:`parse_ears`/:class:`Ears` -- parses the EARS requirement-
  phrasing-templates guidance document (``general/data/general_ears.md``)
  backing ``specmgr://ears``, purely to fail fast on structural drift (the
  parsed result is discarded by the resource itself).

Also backs feat-144-ref-artifact's generic ``list_references`` tool
(REQ-002/REQ-003/REQ-004):

- :class:`ReferenceRow` -- one row of that tool's
  ``PagedResult[ReferenceRow]`` result: a single cross-reference extracted
  from a source document's frontmatter-stripped body, carrying the
  reference's own ``type`` (lowercase tag) and ``id`` plus the referenced
  document's ``title`` (its H1) and absolute on-disk ``path`` -- or, for a
  reference that could not be resolved, ``None`` for both and the target
  domain's not-found message in ``error`` (a never-raising, ``list_*``-
  style inline failure).

Also backs feat-153-off-by-n Phase 2's revision of the generic ``update``
tool's success return (ADR 19ff316b-cd11-41a7-a616-ffd84917da51, revising
feature feat-69-update-context's "frontmatter-only" precedent for ``update``
alone):

- :class:`UpdateResult`/:data:`UpdateFrontmatter` -- the wrapper every
  successful ``update`` call returns: the dispatched domain's own frontmatter
  object plus an optional ``snippet`` (the before/after window of the touched
  range in range mode -- dropped lines numbered pre-splice, inserted lines
  numbered post-splice, up to 2 unchanged context lines per side; ``None`` in
  whole-body mode and for the whole-body-equivalent ``offset=1`` +
  omitted-``limit`` range), and the whole-body domains' frontmatter union the
  ``frontmatter`` field is typed with (single source, re-exported so the
  ``update`` tool's dispatch module does not keep a second copy). These two
   names are exported lazily (PEP 562 ``__getattr__``, see below) because
   their own module imports every whole-body domain's models package and must
   therefore never be imported eagerly from this ``__init__``.
   :class:`UpdateResult`'s own API reference lives on the dedicated
   ``biz.dfch.specmgr.general.models.update_result`` page rather than this
   one: the ``specmgr docs`` generator's package index pages list only
   members defined in the module's own ``__init__.py`` (its
   ``_get_classes``/``_get_functions`` filter, ``obj.__module__ ==
   module.__name__``), never merely re-exported ones.

Import this package to use either model directly::

    from biz.dfch.specmgr.general.models import DocSummary, PagedResult
"""

from typing import Any

from .dtais import (
    CoverageItem,
    CoverageRelationship,
    Dtais,
    MethodItem,
    WhenToApply,
    WhenToApplyItem,
    parse_dtais,
)
from .ears import (
    CombiningPatterns,
    Ears,
    PatternItem,
    Patterns,
    WhenToUse,
    WhenToUseItem,
    parse_ears,
)
from .invalid_status_result import InvalidStatusResult
from .paged_result import PagedResult
from .parse_failure_result import ParseFailureResult
from .rasci import Rasci, RasciVsRaci, RoleItem, Roles, parse_rasci
from .reference import ReferenceRow
from .similarity_hit import SimilarityHit
from .similarity_unavailable import (
    REASON_BACKEND_UNAVAILABLE,
    REASON_DISABLED,
    SimilarityUnavailableResult,
)
from .summary import DocSummary
from .validate_result import ValidateResult, ValidationErrorEntry

__all__ = [
    "CombiningPatterns",
    "CoverageItem",
    "CoverageRelationship",
    "Dtais",
    "DocSummary",
    "Ears",
    "InvalidStatusResult",
    "MethodItem",
    "PagedResult",
    "ParseFailureResult",
    "PatternItem",
    "Patterns",
    "REASON_BACKEND_UNAVAILABLE",
    "REASON_DISABLED",
    "Rasci",
    "RasciVsRaci",
    "ReferenceRow",
    "RoleItem",
    "Roles",
    "SimilarityHit",
    "SimilarityUnavailableResult",
    # PEP 562 lazy export: pylint cannot see the __getattr__-provided names (see update_result.py's module docstring).
    "UpdateFrontmatter",  # pylint: disable=undefined-all-variable
    "UpdateResult",  # pylint: disable=undefined-all-variable
    "ValidateResult",
    "ValidationErrorEntry",
    "WhenToApply",
    "WhenToApplyItem",
    "WhenToUse",
    "WhenToUseItem",
    "parse_dtais",
    "parse_ears",
    "parse_rasci",
]

#: PEP 562: the names this package exports lazily from its ``update_result``
#: submodule (both are defined there).
_LAZY_EXPORTS = frozenset({"UpdateFrontmatter", "UpdateResult"})


def __getattr__(name: str) -> Any:
    """Lazily export the ``update_result`` names (PEP 562) -- see the module docstring.

    ``update_result`` imports every whole-body domain's own models package (for
    the ``frontmatter`` union), so it must never be imported eagerly from this
    ``__init__``: every domain's ``summary.py`` re-enters this package (``from
    ....general.models.summary import DocSummary``) while sibling domains' own
    ``__init__`` files may still be mid-import -- e.g. ``feat.models.v1.body``
    imports ``tsk``'s models, and ``tsk``'s package ``__init__`` pulls in the
    server's full domain-import list, leaving ``feat.models.v1`` partially
    initialized. Deferring the import to first name access is safe: the only
    module that requests these names at import time is ``general.tools.update``
    (the generic ``update`` tool's dispatch module), and that always loads
    after ``general.tools.__init__`` has completed its first import
    (``delete``) -- which cascades through the server's full domain list, so by
    then every domain package, and every domain models package, is fully loaded.
    """
    if name in _LAZY_EXPORTS:
        from . import update_result  # pylint: disable=import-outside-toplevel  # must stay deferred: see the docstring

        result = getattr(update_result, name)
        return result
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return this module's names so ``dir()``/``inspect``/the docs generator see the PEP 562 lazy exports.

    The default module ``dir()`` only sees names defined eagerly in this
    module's ``__dict__``; ``UpdateResult``/``UpdateFrontmatter`` are
    provided by :func:`__getattr__` and would otherwise be invisible to
    ``dir()``, ``inspect.getmembers`` (which the ``specmgr docs`` generator
    relies on), and IDEs. Returning the union of ``globals().keys()`` and
    :data:`_LAZY_EXPORTS` exposes them without converting the export to an
    eager import (which would re-introduce the circular import the PEP 562
    workaround in :func:`__getattr__` exists to avoid).
    """
    result = sorted(set(globals().keys()) | _LAZY_EXPORTS)
    return result
