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

"""Shared cross-reference extraction and per-domain target resolution
(feat-144-ref-artifact, Phase 2; the ``FEAT`` tag: feat-177-list-ref-feat).

Plain Python with **no** ``mcp`` import (like ``_paging.py``,
``_path_safety.py``, and ``_splice.py``), so it stays independently
testable. It holds the two shared, doc-type-agnostic halves of the
generic ``list_references`` tool (``general.tools.list_references``):

- :func:`find_references` extracts every ``<TYPE> <id>``
  cross-reference from a frontmatter-stripped body text via
  :data:`_REFERENCE_PATTERN` (the UUID tags, a canonical 8-4-4-4-12
  hex id) and :data:`_FEAT_REFERENCE_PATTERN` (the ``FEAT`` tag, a full
  ``feat-NNN-slug`` id or a bare ``feat-NNN`` number), each applied with
   ``re.finditer``, the two match sets merged by stable sort on match
   position (a FEAT match can never start inside a UUID span -- a uuid
   cannot contain ``t`` -- while a feat slug can contain a
   ``<TAG>-<uuid>``-shaped substring (the hyphen doubling as the
   separator), in which case the merge keeps BOTH spans -- the outer FEAT
   reference plus the inner, phantom UUID-tag row, which resolves like any
   other reference (typically a not-found row) -- and that corner case is
   pinned by a dedicated test, feat-177 review round), yielding
   ``(type, id)`` pairs with ``type``/``id`` lowercased, in
   first-occurrence order. Repeated
  occurrences of the same reference are **not** deduped here -- dedup
  happens in the row-materialization step (in the tool itself).
- :func:`resolve_reference` resolves one unique reference into a
  :class:`~biz.dfch.specmgr.general.models.reference.ReferenceRow` by
  dispatching on the reference's tag to the target domain's own
  cache-backed ``load_by_id`` and ``<d>_base_dir``. Target resolution
  **never raises for a missing document**: a reference whose target is
  absent on disk (a ``LookupError`` from ``load_by_id`` -- every domain's
  ``XNotFoundError`` subclasses ``LookupError``) yields a row with
  ``title=None``, ``path=None``, and the not-found message in ``error``.
  An unknown ``ref_type`` (a tag with no ``_TARGET_RESOLVERS`` entry) is
  a programming error that propagates as a ``KeyError`` (feat-144-ref-artifact, Task 7.4).
- Caveat (accepted v1 tradeoff of the regex-based, schema-agnostic
  extractor; pinned by a dedicated test -- feat-144-ref-artifact Task 7.6):
  :data:`_REFERENCE_PATTERN` and :data:`_FEAT_REFERENCE_PATTERN` scan the
  raw, frontmatter-stripped body text **unconditionally**, including
  inside fenced code blocks and inline code spans. A document that
  quotes/illustrates the ``<TAG> <id>`` syntax as a literal example
  (rather than as a live reference) is still extracted and
  resolved/reported as if it were real.

The reference *tag* vocabulary consists of the tags the SYSRS/VCR
structured patterns validate as reference targets, plus ``sysrs`` (the
aggregator document type may reference in free-form prose), plus ``feat``
(feat-177-list-ref-feat -- the one tag whose id is not a UUID: a FEAT
reference carries the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
number, and :func:`_load_feat` resolves it by its own folder lookup). It
is deliberately distinct from the source-domain set every ``list_*``/
generic tool dispatches over (``sop``/``tsk`` are plausible future tag
additions).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from ...adr.tools._io import load_by_id as load_adr_by_id
from ...adr.tools._paths import adr_base_dir
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._paths import dec_base_dir
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._paths import FeatNotFoundError, feat_base_dir, feature_title, iter_feat_paths
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._paths import gol_base_dir
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._paths import prb_base_dir
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._paths import qa_base_dir
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._paths import req_base_dir
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._paths import rsk_base_dir
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._paths import sysrs_base_dir
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._paths import uc_base_dir
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._paths import vcr_base_dir
from ..models.reference import ReferenceRow
from ._path_safety import _FEAT_ID_PATTERN as _FEAT_FULL_ID_PATTERN

__all__ = [
    "REFERENCE_TYPES",
    "find_references",
    "resolve_reference",
]

#: The UUID-tagged reference types (the reference-tag vocabulary as of
#: feat-144-ref-artifact, before feat-177-list-ref-feat added ``feat``):
#: the lowercase target-domain name of each tag, same order.
#: :data:`_REFERENCE_PATTERN`'s tag group is derived from this constant
#: (not from :data:`REFERENCE_TYPES`) so the UUID pattern keeps matching
#: exactly these tags: a feat's id is never a UUID, so ``FEAT
#: <uuid>``-shaped text matches nothing under the UUID pattern.
_UUID_REFERENCE_TYPES: tuple[str, ...] = ("gol", "prb", "qa", "uc", "req", "rsk", "dec", "adr", "vcr", "sysrs")

#: The reference *types* a cross-reference tag can name (feat-144 REQ-002;
#: ``feat`` added by feat-177-list-ref-feat): the lowercase target-domain
#: name of each tag -- the tag itself is the uppercase form (``GOL`` ->
#: ``"gol"``, ``FEAT`` -> ``"feat"``). The tags the SYSRS/VCR
#: structured patterns validate as reference targets, plus ``sysrs`` (the
#: aggregator document type may reference in free-form prose), plus
#: ``feat`` (whose ids are ``feat-NNN-slug`` folder names -- or the bare
#: ``feat-NNN`` number -- not uuids; see :data:`_FEAT_REFERENCE_PATTERN`).
#: This set is distinct from the source-domain set the generic tools
#: dispatch over: ``sop``/``tsk`` are plausible future tag additions.
REFERENCE_TYPES: tuple[str, ...] = _UUID_REFERENCE_TYPES + ("feat",)

#: The compiled UUID cross-reference extraction pattern (feat-144 REQ-002).
#: The tag group is derived from :data:`_UUID_REFERENCE_TYPES` (the
#: uppercase forms, same order -- so the group is exactly
#: ``GOL|PRB|QA|UC|REQ|RSK|DEC|ADR|VCR|SYSRS`` and the two cannot drift
#: apart; ``feat`` is deliberately not in the group, since a feat's id is
#: never a UUID). The separator is one or more space/tab/dash characters
#: (so both ``REQ 4f2a...`` and ``GOL-0e15...`` match); the uuid is a
#: canonical 8-4-4-4-12 hex shape with a trailing-hex guard
#: (``(?![0-9a-f])``) so an overlong hex tail is rejected. Matching is
#: case-insensitive (on the tag, and -- via the hex class -- on the uuid
#: as well), and a match may sit anywhere in a line, not only at column 0.
#: The reference's own inline title after the uuid is deliberately **not**
#: captured (it is re-derived from the resolved document).
_REFERENCE_PATTERN = re.compile(
    r"\b(" + "|".join(tag.upper() for tag in _UUID_REFERENCE_TYPES) + r")"
    r"[ \t-]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?![0-9a-f])",
    re.IGNORECASE,
)

#: The full feat id shape shared from ``general.tools._path_safety`` (its
#: anchored :data:`_FEAT_FULL_ID_PATTERN` minus the ``^``/``$`` anchors,
#: e.g. ``feat-[0-9]+-[a-z0-9-]+``): the single source for the FEAT
#: reference pattern's id shapes below and for :func:`_load_feat`'s
#: full/bare classification, so neither can drift from
#: ``assert_feat_id``'s own check (feat-177-list-ref-feat, Task 100.100).
_FEAT_FULL_ID_SHAPE = _FEAT_FULL_ID_PATTERN.pattern.removeprefix("^").removesuffix("$")

#: :data:`_FEAT_FULL_ID_SHAPE` split at the hyphen preceding its final
#: character class, into the leading ``feat-NNN`` number prefix (e.g.
#: ``feat-[0-9]+``) and the trailing slug class with quantifier (e.g.
#: ``[a-z0-9-]+``).
_FEAT_ID_SPLIT = re.split(r"-(?=\[[^\]]*\]\+?$)", _FEAT_FULL_ID_SHAPE, maxsplit=1)
assert len(_FEAT_ID_SPLIT) == 2, (
    f"the shared full feat id shape {_FEAT_FULL_ID_SHAPE!r} must stay of the form "
    "'<number-part>-<slug-class><quantifier>' so it can be split into its number prefix and slug parts "
    "(feat-177-list-ref-feat, Task 100.100)"
)
_FEAT_ID_PREFIX, _FEAT_ID_SLUG = _FEAT_ID_SPLIT
assert re.fullmatch(r"feat-\[[^\]]*\]\+", _FEAT_ID_PREFIX), (
    f"the shared full feat id shape's number prefix {_FEAT_ID_PREFIX!r} must be exactly 'feat-' plus "
    "ONE character class with a '+' quantifier (the bare/full id boundary -- a two-class suffix would "
    "silently move the _FEAT_BARE_ID_PATTERN classifier) (feat-177-list-ref-feat, review round)"
)

#: The compiled FEAT cross-reference extraction pattern
#: (feat-177-list-ref-feat REQ-001). The tag is the literal ``FEAT`` (the
#: one tag whose id is not a UUID); the separator is one or more
#: space/tab/dash characters (same semantics as :data:`_REFERENCE_PATTERN`);
#: the id is the full ``feat-NNN-slug`` shape or the bare ``feat-NNN``
#: number -- ``<prefix>(?:-<slug>)?`` above, built from
#: :data:`_FEAT_FULL_ID_SHAPE` -- with a trailing ``(?![0-9a-z-])`` guard
#: (the same style as the UUID pattern's ``(?![0-9a-f])``) so an overlong
#: or malformed tail such as ``feat-177x`` or ``feat-177-`` is not
#: extracted as ``feat-177``. Matching is case-insensitive (on the tag,
#: and -- via the id character classes -- on the id as well), and a match
#: may sit anywhere in a line, not only at column 0. The reference's own
#: inline title after the id is deliberately **not** captured (it is
#: re-derived from the resolved feature).
_FEAT_REFERENCE_PATTERN = re.compile(
    r"\b(FEAT)"
    rf"[ \t-]+({_FEAT_ID_PREFIX}(?:-{_FEAT_ID_SLUG})?)"
    r"(?![0-9a-z-])",
    re.IGNORECASE,
)

#: The bare ``feat-NNN`` number shape (the full-id shape minus its slug
#: suffix, e.g. ``^feat-[0-9]+$``): :func:`_load_feat`'s full/bare
#: classifier -- the anchored :data:`_FEAT_FULL_ID_PATTERN` covers the
#: full id shape, this one covers the bare number, and any other shape
#: falls through to the exact ``load_by_id`` (a not-found row).
_FEAT_BARE_ID_PATTERN = re.compile(rf"^{_FEAT_ID_PREFIX}$")


def find_references(text: str) -> list[tuple[str, str]]:
    """Extract every ``<TYPE> <id>`` cross-reference from ``text`` (feat-144 REQ-002, the ``FEAT``
    tag's own id shapes added by feat-177-list-ref-feat REQ-001).

    ``text`` is the source document's frontmatter-stripped body markdown
    (e.g. from ``general.tools._splice.body_text``). Both
    :data:`_REFERENCE_PATTERN` (the UUID tags with a canonical
    8-4-4-4-12 hex id) and :data:`_FEAT_REFERENCE_PATTERN` (the ``FEAT``
    tag with the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
    number) are applied via ``re.finditer`` over the whole text, and the
    two match sets are merged by stable sort on match position -- the
    patterns' match spans are not provably disjoint: a FEAT match can never
    start inside a UUID span (a uuid cannot contain ``t``), while a feat
    slug can contain a ``<TAG>-<uuid>``-shaped substring (the hyphen
    doubling as the separator), in which case the merge keeps BOTH spans --
    the outer FEAT reference plus the inner, phantom UUID-tag row, which
    resolves like any other reference (typically a not-found row) -- and
    that corner case is pinned by a dedicated test (feat-177 review round)
    -- and a match may sit anywhere in any line (bullet prefixes,
    indentation, and mid-prose references all count).

    Parameters
    ----------
    text:
        The frontmatter-stripped body text to scan.

    Returns
    -------
    list[tuple[str, str]]
        One ``(type, id)`` pair per match, with ``type``/``id`` lowercased
        (the tag's lowercase target-domain name, and the referenced id as
        it appeared: the canonical lowercase-hex uuid for the UUID
        tags, the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
        number for ``feat``), in first-occurrence order. Repeated
        occurrences of the same reference are **not** deduped here -- dedup
        happens in the row-materialization step.
    """
    assert isinstance(text, str), type(text)

    matches: list[re.Match[str]] = list(_REFERENCE_PATTERN.finditer(text)) + list(
        _FEAT_REFERENCE_PATTERN.finditer(text)
    )
    matches.sort(key=lambda match: (match.start(), match.end()))

    result: list[tuple[str, str]] = [(match.group(1).lower(), match.group(2).lower()) for match in matches]
    return result


def _load_gol(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``gol`` reference to ``(title, path)`` (feat-144 Task 2.1).

    ``title`` is the referenced goal's own ``# {title}`` H1
    (``doc.body.text``); ``path`` is the resolved on-disk file path.
    ``GolNotFoundError`` propagates unchanged (caught by
    :func:`resolve_reference`).
    """
    base_dir = gol_base_dir()
    path, doc = load_gol_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_prb(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``prb`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``prb`` domain.
    """
    base_dir = prb_base_dir()
    path, doc = load_prb_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_qa(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``qa`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``qa`` domain.
    """
    base_dir = qa_base_dir()
    path, doc = load_qa_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_uc(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``uc`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``uc`` domain.
    """
    base_dir = uc_base_dir()
    path, doc = load_uc_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_req(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``req`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``req`` domain.
    """
    base_dir = req_base_dir()
    path, doc = load_req_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_rsk(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``rsk`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``rsk`` domain.
    """
    base_dir = rsk_base_dir()
    path, doc = load_rsk_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_dec(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``dec`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``dec`` domain.
    """
    base_dir = dec_base_dir()
    path, doc = load_dec_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_vcr(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``vcr`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``vcr`` domain.
    """
    base_dir = vcr_base_dir()
    path, doc = load_vcr_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_sysrs(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``sysrs`` reference to ``(title, path)``.

    Same as :func:`_load_gol`, for the ``sysrs`` domain.
    """
    base_dir = sysrs_base_dir()
    path, doc = load_sysrs_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.text, path)
    return result


def _load_adr(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``adr`` reference to ``(title, path)`` (feat-144 Task 2.1).

    ``adr`` is the one target domain that never reads through the doc
    cache (ADR bfd76370-b59b-4d65-b550-a969f6c93c9d -- ADR is permanently
    excluded from the cache mechanism), and ``title`` is the referenced
    ADR's own ``# {title}`` H1 via ``doc.body.title`` (not
    ``doc.body.text``). ``AdrNotFoundError`` propagates unchanged (caught
    by :func:`resolve_reference`).
    """
    base_dir = adr_base_dir()
    path, doc = load_adr_by_id(base_dir, ref_id)
    result: tuple[str, Path] = (doc.body.title, path)
    return result


def _load_feat(ref_id: str) -> tuple[str, Path]:
    """Resolve one ``feat`` reference to ``(title, path)`` (feat-177-list-ref-feat Task 100.110).

    ``feat`` is the one target domain whose ids are not uuids: ``ref_id``
    is either the full ``feat-NNN-slug`` folder name or the bare
    ``feat-NNN`` number (lowercased by :func:`find_references`). A
    full-id-shaped ref -- and any other shape, e.g. a UUID, which can
    never be a feat id -- resolves through feat's own cache-backed exact
    ``load_by_id`` (a miss is a ``FeatNotFoundError`` -> not-found row).
    A bare ``feat-NNN`` ref resolves through the first README-backed
    feature folder (the :func:`iter_feat_paths` view, lexicographic
    folder-name order -- the same order ``list_feat`` reports) whose name
    starts with ``feat-NNN-``: a name-only prefix filter that parses no
    document in the scan (the prefix's trailing hyphen keeps ``feat-1``
    from ever matching ``feat-10-*``; a ``feat-NNN-*`` folder without a
    ``README.md`` is not a candidate), followed by the same exact
    ``load_by_id`` for that first match -- if the first match's README
    fails to parse, the collapsed ``FeatNotFoundError`` yields a not-found
    row, and the resolver does not skip on to the next match. ``title`` is
    the referenced feature's own ``# Feature: {title}`` H1 with the
    ``Feature: `` prefix stripped (:func:`feature_title`); ``path`` is the
    resolved on-disk ``README.md`` path. ``FeatNotFoundError`` propagates
    unchanged (caught by :func:`resolve_reference`).
    """
    assert isinstance(ref_id, str), type(ref_id)

    base_dir = feat_base_dir()
    if _FEAT_BARE_ID_PATTERN.match(ref_id):
        # A bare feat-NNN number: the first README-backed feature folder
        # (iter_feat_paths' lexicographic folder-name order) whose name
        # starts with the feat-NNN- prefix -- name-only, no document
        # parsing in the scan.
        prefix = f"{ref_id}-"
        first_match: Path | None = None
        for path in iter_feat_paths(base_dir):
            if path.parent.name.startswith(prefix):
                first_match = path
                break
        if first_match is None:
            raise FeatNotFoundError(
                f"no feature found for bare number {ref_id!r}: no feature folder named {ref_id}-* with a README.md "
                f"exists under {base_dir!r} (use list_feat to discover the exact id)"
            )
        folder_id = first_match.parent.name
    else:
        # The full-id shape (and any other shape, e.g. a UUID): the exact,
        # cache-backed load_by_id -- a miss is a FeatNotFoundError (a
        # LookupError) -> not-found row.
        folder_id = ref_id
    path, doc = load_feat_by_id(base_dir, folder_id)
    result: tuple[str, Path] = (feature_title(doc.body.text), path)
    return result


#: Per target-domain reference resolver (feat-144 Task 2.1, ``feat`` added
#: by feat-177-list-ref-feat Task 100.110): each returns ``(title, path)``
#: for one reference id and propagates the domain's own ``XNotFoundError``
#: (a ``LookupError``) if the target is absent on disk. Every target
#: domain except ``adr`` reads through its own cache-backed
#: ``load_by_id`` (feat-107-doc-cache; ``feat`` is folder-per-document
#: rather than flat-file -- see :func:`_load_feat`); ``adr`` never does
#: (see :func:`_load_adr`).
_TARGET_RESOLVERS: dict[str, Callable[[str], tuple[str, Path]]] = {
    "gol": _load_gol,
    "prb": _load_prb,
    "qa": _load_qa,
    "uc": _load_uc,
    "req": _load_req,
    "rsk": _load_rsk,
    "dec": _load_dec,
    "vcr": _load_vcr,
    "sysrs": _load_sysrs,
    "adr": _load_adr,
    "feat": _load_feat,
}

assert set(_TARGET_RESOLVERS) == set(REFERENCE_TYPES), (
    "_TARGET_RESOLVERS keys drifted from this module's REFERENCE_TYPES reference-tag vocabulary -- "
    "add or remove the missing target domain's _load_<d> resolver in both places (feat-144-ref-artifact, "
    "Task 7.4)"
)


def resolve_reference(ref_type: str, ref_id: str) -> ReferenceRow:
    """Resolve one unique reference into a :class:`ReferenceRow` (feat-144 REQ-003/REQ-004).

    Dispatches on ``ref_type`` (the reference tag's lowercase
    target-domain name) to the target domain's own ``load_by_id`` +
    ``<d>_base_dir`` (see :data:`_TARGET_RESOLVERS`). The row's ``title``
    is the referenced document's ``# {title}`` H1, re-derived from the
    resolved document on disk, and its ``path`` the referenced document's
    resolved absolute file path (``str(path.resolve())``).

    Target resolution **never raises for a missing document**: a
    ``LookupError`` from ``load_by_id`` (every domain's
    ``XNotFoundError`` subclasses ``LookupError``) -- i.e. a reference
    whose target is absent on disk -- yields a row with ``title=None``,
    ``path=None``, and the not-found message in ``error``
    (``list_*``-style inline failure). An unknown ``ref_type`` (a tag
    with no ``_TARGET_RESOLVERS`` entry) is a programming error that
    propagates as a ``KeyError`` (feat-144-ref-artifact, Task 7.4); the
    module-scope drift guard above makes the missing-entry case
    impossible by construction. Only the source read (in the
    ``list_references`` tool itself) raises for a missing document.

    Parameters
    ----------
    ref_type:
        The reference tag's lowercase target-domain name, e.g. ``"req"``.
    ref_id:
        The referenced document's id, as it appeared in the source body
        (lowercased): the canonical lowercase-hex UUID for the UUID
        tags, the full ``feat-NNN-slug`` id or the bare ``feat-NNN``
        number for ``feat``.

    Returns
    -------
    ReferenceRow
        The resolved row (``title``/``path`` populated, ``error`` ``None``)
        or the not-found row (``title``/``path`` ``None``, ``error`` set).

    Raises
    ------
    KeyError
        ``ref_type`` is not one of :data:`REFERENCE_TYPES` (no
        ``_TARGET_RESOLVERS`` entry) -- a programming error, never
        expected by construction (the module-scope drift guard above).
    """
    assert isinstance(ref_type, str), type(ref_type)
    assert isinstance(ref_id, str), type(ref_id)

    resolver = _TARGET_RESOLVERS[ref_type]  # feat-144 Task 7.4: a KeyError here is a programming error
    try:
        title, path = resolver(ref_id)  # only the domain's own XNotFoundError (a LookupError) is caught
    except LookupError as exc:
        result = ReferenceRow(type=ref_type, id=ref_id, error=str(exc))
        return result
    result = ReferenceRow(type=ref_type, id=ref_id, title=title, path=str(path.resolve()))
    return result
