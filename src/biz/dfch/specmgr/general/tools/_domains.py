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

"""The shared document-type domain names and per-domain adapter registry (feat-125-domain-lists
+ feat-134, Phase 1, REQ-012).

This module is the single source of truth for the document-type domain
**names** (feat-125-domain-lists, REQ-001, ADR c4efbde6-fd19-4aa8-8668-
95316ed62dcc "Single source of truth for the document-type domain-name
set") and for the per-domain **adapters** every cross-domain consumer
needs (feat-134, Phase 1, REQ-012, ADR 750842b2-aca4-4649-ba0c-855ec8e1f505,
**corpus and registry** sub-decision).

Every other module that names a set of document types imports the names
from here instead of hand-listing them itself (the feat-125 sweep
ruling: no other ``src/`` or ``tests/`` module may hand-list a
domain-name set). Before the feat-134 registry, the same set
(req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs) was copy-pasted as
``Literal``/tuple literals across the five existing generic tools in
this package (``update``'s/``set_status``'s/``set_classification``'s/
``delete``'s/``validate``'s own ``type`` parameter literals, plus
``delete.py``'s and ``validate.py``'s own module-scope tuples) -- and
the two new similarity tools (Phase 3) would have been the sixth and
seventh copies.

- :data:`WHOLE_BODY_DOMAINS` -- the 12-domain tuple itself: the only
  hand-listed tuple in the module, the whole-body document types in the
  canonical order ``req``, ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``,
  ``rsk``, ``dec``, ``sop``, ``feat``, ``vcr``, ``sysrs``. Every other
  name-set constant is derived from it, never hand-listed a second
  time: :data:`WHOLE_BODY_NO_FEAT_DOMAINS` is the whole-body domains
  without ``feat``, :data:`UUID_DOMAINS` is those plus ``adr``, and
  :data:`ALL_DOMAINS` is ``adr`` prefixed to the whole-body domains.
  :data:`ADR` and :data:`FEAT` are the two name singletons. The five
  existing generic tools' and the two Phase 3 similarity tools' ``type``
  parameter annotations are derived from it (via the
  :data:`WholeBodyType`/:data:`WholeBodyOrAdrType` aliases below), so a
  new document type (e.g. the reserved ``ac``) registers its name in
  :data:`WHOLE_BODY_DOMAINS` once and every derived tuple and tool
  domain set picks it up by construction.
- :class:`WholeBodyDomain` + the module-scope ``_DOMAINS`` mapping --
  the per-domain adapters every cross-domain consumer needs: the
  base-dir resolver, the path iterator, ``load_by_id``, and the pure
  text parser (``parse_text``) -- the same per-domain adapter shape
  ``general/tools/delete.py`` already imports at module level. ``feat``'s
  ``<base>/<id>/README.md`` folder shape is the one bespoke path iterator
  (``iter_feat_paths``); every other domain uses the shared flat-file
  ``iter_doc_paths``. ``parse_text`` (added feat-134 Phase 2, Task 2.1)
  backs the similarity engine's per-candidate parseability check -- a
  document is unparseable when its domain's own text parser raises on any
  of the three parse-failure channels (REQ-009) -- and its candidate
  enumeration / source resolution live in
  ``general/tools/_similarity_corpus.py``, built on this registry.
- :data:`WholeBodyType` / :data:`WholeBodyOrAdrType` -- the derived
  ``Literal`` ``type``-parameter annotations for the generic tools.
- :func:`whole_body_domain` -- the ``name -> WholeBodyDomain`` lookup with
  the path-safety-convention ``ValueError`` for an unknown name (raised
  before any filesystem access).

**``adr`` is structurally excluded** from :data:`WHOLE_BODY_DOMAINS`
(issue #46, "Remove adr artifact type": ADR is being removed as an
artifact type entirely, so it is not a useful similarity target/source,
and it never had a whole-body
replace/status/classification/delete/validate adapter of its own to begin
with -- ``set_status``'s own ``adr`` branch is the single generic-tool
exception, hence the separate :data:`WholeBodyOrAdrType`; ``adr`` enters
the name-set constants only through :data:`UUID_DOMAINS` and
:data:`ALL_DOMAINS`).

**No ``mcp`` dependency here**, like every other private ``general/tools/``
support module: the registry is plain data plus the per-domain adapter
imports (the same imports ``delete.py``/``update.py``/``set_status.py``/
``set_classification.py`` already make at module level), so importing it
never registers or touches a tool.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypeAlias

from ...dec.models.v1.parser import parse_dec
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._paths import dec_base_dir
from ...feat.models.v1.parser import parse_feat
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._paths import feat_base_dir, iter_feat_paths
from ...gol.models.v1.parser import parse_gol
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._paths import gol_base_dir
from ...prb.models.v1.parser import parse_prb
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._paths import prb_base_dir
from ...qa.models.v2.parser import parse_qa
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._paths import qa_base_dir
from ...req.models.v1.parser import parse_req
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._paths import req_base_dir
from ...rsk.models.v1.parser import parse_rsk
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._paths import rsk_base_dir
from ...sop.models.v1.parser import parse_sop
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._paths import sop_base_dir
from ...sysrs.models.v1.parser import parse_sysrs
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._paths import sysrs_base_dir
from ...tsk.models.v1.parser import parse_tsk
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._paths import tsk_base_dir
from ...uc.models.v2.parser import parse_uc
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._paths import uc_base_dir
from ...vcr.models.v1.parser import parse_vcr
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._paths import vcr_base_dir
from ._doc_paths import iter_doc_paths

__all__ = [
    "ADR",
    "FEAT",
    "WHOLE_BODY_DOMAINS",
    "WHOLE_BODY_NO_FEAT_DOMAINS",
    "UUID_DOMAINS",
    "ALL_DOMAINS",
    "WholeBodyDomain",
    "WholeBodyType",
    "WholeBodyOrAdrType",
    "whole_body_domain",
]

#: The ``adr`` document type (singleton).
ADR = "adr"

#: The ``feat`` document type (singleton): the one whole-body domain whose
#: ``id`` is a chosen ``feat-NNN-slug`` folder name, not a server-generated
#: UUID.
FEAT = "feat"

#: The whole-body document types in the canonical order -- the only
#: hand-listed tuple in this module, the one source of the domain set
#: (REQ-012). ``adr`` is structurally excluded (issue #46; see the module
#: docstring). The five existing generic tools and the two Phase 3
#: similarity tools all derive their own ``type`` domain set from this
#: tuple.
WHOLE_BODY_DOMAINS: tuple[str, ...] = (
    "req",
    "uc",
    "tsk",
    "qa",
    "prb",
    "gol",
    "rsk",
    "dec",
    "sop",
    "feat",
    "vcr",
    "sysrs",
)

#: The whole-body document types without ``feat`` (derived from
#: :data:`WHOLE_BODY_DOMAINS`, never hand-listed).
WHOLE_BODY_NO_FEAT_DOMAINS = tuple(d for d in WHOLE_BODY_DOMAINS if d != FEAT)

#: The UUID-shaped document types: the whole-body domains without ``feat``,
#: plus ``adr`` (derived from :data:`WHOLE_BODY_DOMAINS`, never hand-listed).
UUID_DOMAINS = WHOLE_BODY_NO_FEAT_DOMAINS + (ADR,)

#: Every document type: ``adr`` plus the whole-body domains (derived from
#: :data:`WHOLE_BODY_DOMAINS`, never hand-listed).
ALL_DOMAINS = (ADR,) + WHOLE_BODY_DOMAINS


@dataclass(frozen=True)
class WholeBodyDomain:
    """One whole-body domain's registry entry: its name plus its adapters (REQ-012).

    Attributes:
        name:
            The domain's name: the ``type`` value the generic tools
            dispatch on (``"req"``, ``"feat"``, ...).
        base_dir:
            The domain's base-dir resolver -- its own ``<d>.tools._paths``
            function, reading the domain's own ``SPECMGR_*_DIR`` env var
            with its own default (the shared ``SPECMGR_DOCS_DIR``-rooted
            one for every domain other than ``feat``, ``SPECMGR_FEAT_DIR``
            for ``feat``).
        iter_paths:
            The domain's document path iterator: the shared flat-file
            ``iter_doc_paths`` (every ``*.md`` directly under the base
            directory, sorted) for every domain other than ``feat``,
            ``iter_feat_paths`` (``<base>/<id>/README.md``, sorted by
            folder name) for ``feat`` -- the one bespoke,
            folder-per-document domain (ADR 8cf940c5).
        load_by_id:
            The domain's ``load_by_id`` -- resolves ``id_`` under the given
            base directory and parses the matching document, raising the
            domain's own ``XNotFoundError``. The document slot is typed
            ``object`` (each domain's own concrete document type --
            ``tuple[Path, ReqDocument]`` and so on -- is what the specific
            function actually returns); registry callers that only need
            the path (the generic ``delete`` adapters' own
            resolve-then-act pattern) discard it.
        parse_text:
            The domain's own pure text parser -- the ``parse_<d>(text)``
            function from the domain's ``models`` package (no file I/O, no
            ``mcp``): the single call that decides whether a document's
            exact text is parseable at all, raising the domain's three
            parse-failure channels (structural ``AssertionError``,
            ``pydantic.ValidationError``, ``yaml.YAMLError`` --
            ``general.tools._listing.DEFAULT_ERROR_TYPES``) on failure.
            On success it yields the validated document (the return slot
            is typed ``Any`` -- each domain's own concrete document type,
            whose ``.frontmatter`` the feat-134 Phase 2 candidate
            extraction reads for the result-row ``id``/``status``);
            ``general/tools/_similarity_corpus.py`` is the first caller.
    """

    name: str
    base_dir: Callable[[], Path]
    iter_paths: Callable[[Path], Iterator[Path]]
    load_by_id: Callable[[Path, str], tuple[Path, object]]
    parse_text: Callable[[str], Any]


#: The per-domain adapter registry, keyed by :data:`WHOLE_BODY_DOMAINS`
#: name, in the same order. ``feat`` is the one entry whose ``iter_paths``
#: is not the shared flat-file ``iter_doc_paths`` (see the dataclass
#: docstring); every entry's ``load_by_id`` is the domain's own, cache-
#: backed ``<d>.tools._io.load_by_id``.
_DOMAINS: dict[str, WholeBodyDomain] = {
    "req": WholeBodyDomain(
        name="req",
        base_dir=req_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_req_by_id,
        parse_text=parse_req,
    ),
    "uc": WholeBodyDomain(
        name="uc",
        base_dir=uc_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_uc_by_id,
        parse_text=parse_uc,
    ),
    "tsk": WholeBodyDomain(
        name="tsk",
        base_dir=tsk_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_tsk_by_id,
        parse_text=parse_tsk,
    ),
    "qa": WholeBodyDomain(
        name="qa",
        base_dir=qa_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_qa_by_id,
        parse_text=parse_qa,
    ),
    "prb": WholeBodyDomain(
        name="prb",
        base_dir=prb_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_prb_by_id,
        parse_text=parse_prb,
    ),
    "gol": WholeBodyDomain(
        name="gol",
        base_dir=gol_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_gol_by_id,
        parse_text=parse_gol,
    ),
    "rsk": WholeBodyDomain(
        name="rsk",
        base_dir=rsk_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_rsk_by_id,
        parse_text=parse_rsk,
    ),
    "dec": WholeBodyDomain(
        name="dec",
        base_dir=dec_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_dec_by_id,
        parse_text=parse_dec,
    ),
    "sop": WholeBodyDomain(
        name="sop",
        base_dir=sop_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_sop_by_id,
        parse_text=parse_sop,
    ),
    "feat": WholeBodyDomain(
        name="feat",
        base_dir=feat_base_dir,
        iter_paths=iter_feat_paths,
        load_by_id=load_feat_by_id,
        parse_text=parse_feat,
    ),
    "vcr": WholeBodyDomain(
        name="vcr",
        base_dir=vcr_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_vcr_by_id,
        parse_text=parse_vcr,
    ),
    "sysrs": WholeBodyDomain(
        name="sysrs",
        base_dir=sysrs_base_dir,
        iter_paths=iter_doc_paths,
        load_by_id=load_sysrs_by_id,
        parse_text=parse_sysrs,
    ),
}

# Program invariants (import-time). feat-125 (ADR c4efbde6): the derived
# name sets keep their intended relation to the single hand-listed source
# -- ``feat`` is one of the whole-body domains (so the ``-feat`` derivation
# actually drops it), ``adr`` is structurally excluded from them (issue
# #46), and no name appears twice in :data:`ALL_DOMAINS`. feat-134 (REQ-012,
# ADR 750842b2): the adapter mapping and the domain tuple must stay exactly
# in sync -- same names, same order -- so the tuple (the single source of
# the set) and the adapters can never drift apart.
assert FEAT in WHOLE_BODY_DOMAINS, "feat must be one of the whole-body domains"
assert ADR not in WHOLE_BODY_DOMAINS, "adr is structurally excluded from the whole-body domains (issue #46)"
assert len(ALL_DOMAINS) == len(set(ALL_DOMAINS)), "ALL_DOMAINS must not contain a name twice"
assert tuple(_DOMAINS) == WHOLE_BODY_DOMAINS, (
    "the _DOMAINS adapter mapping must match WHOLE_BODY_DOMAINS exactly, in order"
)

#: The ``type`` parameter annotation for a generic tool that covers exactly
#: the whole-body domains -- derived from :data:`WHOLE_BODY_DOMAINS`
#: (``Literal[tuple]`` unpacks to the same ``Literal`` an inline spelling
#: would produce, so the generated MCP schema is unchanged) -- REQ-012:
#: the set is derived, not duplicated.
WholeBodyType: TypeAlias = Literal[WHOLE_BODY_DOMAINS]

#: Same derivation, plus ``adr`` -- for the one generic tool that also
#: dispatches on ``adr`` (``set_status``; see the module docstring).
#: Derived from :data:`ALL_DOMAINS` (so the registered enum lists ``adr``
#: first, feat-125-domain-lists' documented, ordering-only change) rather
#: than hand-spelling ``WHOLE_BODY_DOMAINS + (ADR,)``.
WholeBodyOrAdrType: TypeAlias = Literal[ALL_DOMAINS]


def whole_body_domain(name: str) -> WholeBodyDomain:
    """Return the registry entry for the whole-body domain ``name``.

    The ``name -> WholeBodyDomain`` lookup the Phase 3 similarity tools
    (and any future cross-domain consumer) use to reach a domain's own
    adapters without re-importing them per call site.

    Args:
        name:
            The domain's name: one of :data:`WHOLE_BODY_DOMAINS`.

    Returns:
        The domain's :class:`WholeBodyDomain` registry entry.

    Raises:
        ValueError:
            ``name`` is not one of the whole-body domains (e.g. ``"adr"``,
            or a future unregistered name) -- raised before any filesystem
            access (the path-safety convention), naming the offending value
            and the allowed set.
    """
    assert isinstance(name, str), type(name)

    try:
        result = _DOMAINS[name]
    except KeyError:
        raise ValueError(f"unknown document type {name!r}; expected one of {', '.join(WHOLE_BODY_DOMAINS)}") from None
    return result
