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

"""The reference-graph builders: scoped source-centred and registry-wide graph construction
(feat-207-reference-graph, Phase 110, REQ-002).

Thin over the feat-144-ref-artifact reference machinery (``general.tools._references``'s
:func:`find_references` / :func:`resolve_reference`) and the ``list_references``
tool's own per-domain source-scan legs (the ``(<d>_base_dir, load_<d>_by_id)``
pairs the tool's ``_SOURCE_LOADERS`` table holds, here re-dispatched over
``general.tools._domains.ALL_DOMAINS``): the reference extraction and target
resolution semantics are inherited verbatim -- the 12-tag ``<TYPE> <id>``
vocabulary (the UUID tags with a canonical uuid id, plus ``FEAT`` carrying the
full ``feat-NNN-slug`` id or the bare ``feat-NNN`` number), the code-fence
extraction caveat, and the feat dual-spelling behaviour (rulebook §3.7).

Two builders, one frozen construction semantics each (rulebook §3):

- :func:`build_source_graph` -- the scoped graph: the requested source
  document, its outgoing reference neighbourhood to ``depth`` (level 0 = the
  source; a level-k node is expanded only if k < depth and it resolved to an
  existing document, its body read through the domain's own read path -- the
  cache-aware leg for the 13 whole-body domains, the never-cached leg for
  ``adr``, ADR bfd76370), optionally plus the direct incoming references to
  the source (``reverse``: a full scan of all 14 source domains, additive and
  direct-only on the incoming side, with the feat dual-spelling match rule).
- :func:`build_registry_graph` -- the registry-wide graph: the same 14-domain
  scan; every successfully parsed document is a node; every extracted
  reference an edge; a target not present as a scanned document gets its
  title via :func:`resolve_reference` (dangling ⇒ the unresolved node).

Broken documents in any scan are **skipped** (never a node, never an edge
source; the render never fails -- the ``get_use_case_package_diagram``
precedent). A document that **vanishes mid-build** (a concurrent delete
between the scan's parse leg and one of the builders' own ``body_text``
re-reads -- the three EXTRACTION legs: the forward BFS's resolved-node read,
the reverse pass's scanned-document read, and the registry build's
scanned-document read) is skipped the same way the parse-leg vanish is: the
forward leg skips that node's EXPANSION only (the node and the edge that
reached it remain; no outgoing references from the vanished document are
added), the reverse/registry legs skip the document entirely (no node, no
incoming edge / no edges) -- the render never fails for content. The
builders **never raise for target-side content** (a dangling
target becomes a ``title=None`` node); a **missing** source raises the source
domain's own ``XNotFoundError`` (propagated unchanged from the source
domain's own ``load_by_id``), and an **existing-but-broken** source raises
the domain's own parse error (the ``AssertionError``/
``pydantic.ValidationError``/``yaml.YAMLError`` channels, ``AdrParseError``
for ``adr``) -- the Phase 120 tool layer converts that to the non-raising
``ParseFailureResult`` (the feat-150 precedent), the builders themselves
raise. Every build runs over a visited (type, id) set (reference cycles
terminate by construction; they affect only rendering, rulebook §4).

The FEAT exclusion (``include_feat=False``, rulebook §3.5) is ONE post-hoc
rule applied LAST in all three modes: drop every FEAT node except the
explicitly requested source (scoped mode only has such a thing), then drop
every edge touching a dropped node -- a feat target must not surface as a
node in any mode.

Input contract: the builders assume VALIDATED input -- the ``type``/``id``
``_path_safety.validate_id`` guards and the ``depth`` 1..5 validation are the
Phase 120 tool / Phase 130 CLI layer's job (rulebook §7); an unvalidated
``type`` outside ``ALL_DOMAINS`` is a ``KeyError`` programming error (the
``resolve_reference`` unknown-tag channel), not a content failure.

No ``@mcp.tool()`` registration here (and no ``server`` import): the Phase
120 tool modules call into these builders. Plain Python over the per-domain
legs -- independently testable against isolated ``SPECMGR_*_DIR`` registries.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ...adr.tools._io import load_by_id as load_adr_by_id
from ...adr.tools._io import read_adr
from ...adr.tools._paths import adr_base_dir, iter_adr_paths
from ...dec.tools._cache import read_dec
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._paths import dec_base_dir
from ...feat.tools._cache import read_feat
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._paths import feat_base_dir, feature_title, find_feat_parse_failure
from ...gol.tools._cache import read_gol
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._paths import gol_base_dir
from ...models.adr import AdrParseError
from ...prb.tools._cache import read_prb
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._paths import prb_base_dir
from ...qa.tools._cache import read_qa
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._paths import qa_base_dir
from ...req.tools._cache import read_req
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._paths import req_base_dir
from ...rsk.tools._cache import read_rsk
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._paths import rsk_base_dir
from ...sop.tools._cache import read_sop
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._paths import sop_base_dir
from ...sysrs.tools._cache import read_sysrs
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._paths import sysrs_base_dir
from ...tsk.tools._cache import read_tsk
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._paths import tsk_base_dir
from ...txt.tools._cache import read_txt
from ...txt.tools._io import load_by_id as load_txt_by_id
from ...txt.tools._paths import txt_base_dir
from ...uc.tools._cache import read_uc
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._paths import uc_base_dir
from ...vcr.tools._cache import read_vcr
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._paths import vcr_base_dir
from ..models.reference_graph import GraphEdge, GraphNode, ReferenceGraph
from ._doc_paths import find_parse_failure
from ._domains import ALL_DOMAINS, ADR, FEAT, whole_body_domain
from ._listing import DEFAULT_ERROR_TYPES
from ._path_safety import assert_within
from ._references import find_references, resolve_reference
from ._splice import body_text

__all__ = ["build_registry_graph", "build_source_graph"]

#: The parse-failure channels the source scans skip broken documents on
#: (rulebook §3.4): the three whole-body channels plus ``adr``'s own
#: ``AdrParseError`` (a ``ValueError`` subclass -- the ``read_adr`` leg's
#: structural channel).
_SCAN_ERROR_TYPES: tuple[type[Exception], ...] = DEFAULT_ERROR_TYPES + (AdrParseError,)

#: The frozen registry-wide diagram title (rulebook §2.2: the default for
#: ``build_registry_graph``'s output; the scoped builder's default is the
#: source's own H1).
_REGISTRY_TITLE = "Reference Graph"

#: Per source-domain ``(<d>_base_dir, load_<d>_by_id)`` pair (the
#: ``list_references`` tool's own ``_SOURCE_LOADERS`` legs, re-dispatched
#: here over ``ALL_DOMAINS``): the source document is resolved through the
#: source domain's own id resolution (the domain's own ``XNotFoundError``
#: propagates unchanged), and every scanned document is read through the
#: domain's own read path below (cache-aware for the 13 whole-body domains,
#: never-cached for ``adr``).
_SOURCE_LOADERS: dict[str, tuple[Callable[[], Path], Callable[[Path, str], tuple[Path, BaseModel]]]] = {
    "req": (req_base_dir, load_req_by_id),
    "uc": (uc_base_dir, load_uc_by_id),
    "tsk": (tsk_base_dir, load_tsk_by_id),
    "qa": (qa_base_dir, load_qa_by_id),
    "prb": (prb_base_dir, load_prb_by_id),
    "gol": (gol_base_dir, load_gol_by_id),
    "rsk": (rsk_base_dir, load_rsk_by_id),
    "dec": (dec_base_dir, load_dec_by_id),
    "sop": (sop_base_dir, load_sop_by_id),
    "feat": (feat_base_dir, load_feat_by_id),
    "vcr": (vcr_base_dir, load_vcr_by_id),
    "sysrs": (sysrs_base_dir, load_sysrs_by_id),
    "txt": (txt_base_dir, load_txt_by_id),
    "adr": (adr_base_dir, load_adr_by_id),
}

assert set(_SOURCE_LOADERS) == set(ALL_DOMAINS), (
    "_SOURCE_LOADERS keys drifted from the shared general.tools._domains.ALL_DOMAINS source -- add or "
    "remove the missing source domain's (<d>_base_dir, load_<d>_by_id) pair in both places "
    "(feat-207-reference-graph, Phase 110)"
)

#: Per source-domain read leg (rulebook §3's "the per-domain cache-aware
#: reads; the never-cached adr leg"): the 13 whole-body domains read through
#: their own content-hash-validated ``read_<d>`` cache singleton
#: (feat-107-doc-cache; ``feat``'s CLEAN, full-parse stage), and ``adr``
#: through its own plain ``read_adr`` (permanently DocCache-excluded, ADR
#: bfd76370) -- a broken document's parse failure raises out of the leg and
#: is skipped by the scans, never a node and never an edge source.
_SCAN_READERS: dict[str, Callable[[Path], Any]] = {
    "req": read_req,
    "uc": read_uc,
    "tsk": read_tsk,
    "qa": read_qa,
    "prb": read_prb,
    "gol": read_gol,
    "rsk": read_rsk,
    "dec": read_dec,
    "sop": read_sop,
    "feat": read_feat,
    "vcr": read_vcr,
    "sysrs": read_sysrs,
    "txt": read_txt,
    "adr": read_adr,
}

assert set(_SCAN_READERS) == set(ALL_DOMAINS), (
    "_SCAN_READERS keys drifted from the shared general.tools._domains.ALL_DOMAINS source -- add or "
    "remove the missing source domain's read leg in both places (feat-207-reference-graph, Phase 110)"
)


def _doc_title(type_: str, doc: Any) -> str:
    """The scanned/loaded document's derived title (rulebook §3's node titles).

    The same per-domain derivation ``general.tools._references``'s target
    resolvers use (so a node reached via a reference and the same document
    loaded as a source or scanned in a full scan always carry the identical
    title): the ``feat`` H1 with its ``Feature: `` prefix stripped
    (:func:`feature_title`), the ``adr`` body's own ``title`` field, every
    other domain's body H1 (``doc.body.text``).
    """
    assert isinstance(type_, str), type(type_)

    if type_ == FEAT:
        result: str = feature_title(doc.body.text)
    elif type_ == ADR:
        result = doc.body.title
    else:
        result = doc.body.text
    return result


def _unique_references(text: str) -> list[tuple[str, str]]:
    """``find_references`` with repeated (type, id) occurrences deduped (first-occurrence order kept).

    The row-materialization-level dedup the ``list_references`` tool does
    itself (rulebook §3: each unique (type, id) reference adds exactly one
    edge + one node).
    """
    assert isinstance(text, str), type(text)

    result: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for pair in find_references(text):
        if pair not in seen:
            seen.add(pair)
            result.append(pair)
    return result


def _iter_source_documents() -> Iterator[tuple[str, Path, Any]]:
    """Every parseable document across all 14 source domains (rulebook §3.2/§3.3's full scan).

    The full scan the reverse and registry-wide builders share (no listing,
    no pagination), in ``ALL_DOMAINS`` order (adr first) and each domain's
    own sorted path
    order (the domain's own path iterator: the shared flat-file
    ``iter_doc_paths`` for every whole-body domain other than ``feat``,
    ``iter_feat_paths`` for ``feat``, ``iter_adr_paths`` for ``adr``). Each
    path is read through the domain's own leg (the cache-aware
    ``read_<d>`` for the 13 whole-body domains, the never-cached
    ``read_adr`` for ``adr``); a document that fails to parse
    (:data:`_SCAN_ERROR_TYPES` channels) or vanishes mid-scan
    (``FileNotFoundError``) is skipped (rulebook §3.4 -- never a node, never
    an edge source), so the scan never raises for content. That guard
    covers the PARSE leg (the domain's read call); each builder's own
    EXTRACTION leg -- the ``body_text`` re-read over the yielded path --
    carries its own ``FileNotFoundError`` skip (a document vanishing between
    the two reads is handled there, module docstring), so the scan plus its
    extraction legs together never raise for content.

    Yields ``(type, path, doc)`` -- the document's own parsed model, whose
    frontmatter id and derived title the builders read; the reference
    extraction itself scans the raw, frontmatter-stripped body text
    (``_splice.body_text`` over the yielded path -- the ``list_references``
    source-read precedent: extraction needs the literal markdown).
    """
    for type_ in ALL_DOMAINS:
        base_dir_fn, _load_fn = _SOURCE_LOADERS[type_]
        read_fn = _SCAN_READERS[type_]
        base_dir = base_dir_fn()
        if type_ == ADR:
            paths = iter_adr_paths(base_dir)
        else:
            paths = whole_body_domain(type_).iter_paths(base_dir)
        for path in paths:
            try:
                doc = read_fn(path)
            except _SCAN_ERROR_TYPES:
                continue  # rulebook §3.4: broken documents are skipped (the render never fails)
            except FileNotFoundError:
                continue  # a file vanishing mid-scan is omitted silently (the build_summaries precedent)
            yield type_, path, doc


def _raise_broken_source(type_: str, base_dir: Path, id_: str, read_fn: Callable[[Path], Any]) -> None:
    """Re-raise the domain's own parse error for an existing-but-broken source (rulebook §3.4).

    Called from :func:`_load_source` on the source domain's
    ``XNotFoundError`` (a broken source's own id is unreadable by the id
    lookup, which skips unparseable files -- so missing and broken surface
    as the same ``LookupError`` and must be probed apart here). The
    flat domains and ``adr`` go through the shared
    :func:`general.tools._doc_paths.find_parse_failure` name-match scan
    (for ``adr``, a broken file's own ``AdrParseError``/``ValidationError``
    propagates out of ``find_parse_failure``'s leg read directly -- already
    the domain's parse error); ``feat`` goes through its folder-per-document
    counterpart :func:`find_feat_parse_failure` (the flat-file stem match
    cannot see a ``<base>/<id>/README.md``). For a name-matching broken
    file, the leg is re-run on the matched path to re-raise the live
    exception (the cache-backed leg re-raises a fresh, equivalent stored
    failure at near-zero cost, feat-162's byte-identical message); a
    name-matching file that parses cleanly on the re-run (a repair racing
    the probe) returns silently, letting the original not-found propagate.
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)

    if type_ == FEAT:
        failure = find_feat_parse_failure(base_dir, id_)
    else:
        failure = find_parse_failure(base_dir, id_, read_fn)
    if failure is None:
        return
    failure_path, _error_text = failure
    try:
        read_fn(failure_path)
    except _SCAN_ERROR_TYPES as exc:
        assert_within(base_dir, failure_path)  # defense-in-depth confinement
        raise exc


def _load_source(type_: str, id_: str) -> tuple[Path, Any]:
    """Resolve + parse the scoped source document (rulebook §3.4's source-side contract).

    The ``list_references`` source-leg precedent (the source domain's own
    id resolution, the parsed document discarded except for its path and
    derived title): a **missing** source raises the source domain's own
    ``XNotFoundError`` (propagated unchanged, identical to ``get_<d>``); an
    **existing-but-broken** source raises the domain's own parse error (via
    :func:`_raise_broken_source` -- the Phase 120 tool layer converts that
    to the non-raising ``ParseFailureResult``, the feat-150 precedent).

    Returns
    -------
    tuple[Path, Any]
        ``(path, doc)`` -- the resolved source file (confined to the source
        domain's own base directory) and its parsed document.
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(id_, str), type(id_)

    base_dir_fn, load_fn = _SOURCE_LOADERS[type_]
    read_fn = _SCAN_READERS[type_]
    base_dir = base_dir_fn()
    try:
        path, doc = load_fn(base_dir, id_)
    except LookupError:
        _raise_broken_source(type_, base_dir, id_, read_fn)
        raise  # no parse failure to surface: the domain's own XNotFoundError propagates unchanged
    assert_within(base_dir, path)  # defense-in-depth confinement
    result: tuple[Path, Any] = (path, doc)
    return result


def _bare_feat_id(feat_id: str) -> str:
    """The bare ``feat-NNN`` number form of a full ``feat-NNN-slug`` id (rulebook §3.2's match rule).

    The source-id ``feat-177-list-ref-feat`` splits at the second hyphen
    into ``feat-177`` -- the one reference spelling a full-spelling source
    additionally matches in the reverse scan (a bare-spelling source cannot
    occur: ``validate_id`` rejects it, rulebook §6).
    """
    assert isinstance(feat_id, str), type(feat_id)

    parts = feat_id.split("-")
    result = "-".join(parts[:2])
    return result


def _reference_matches_source(
    reference: tuple[str, str], source_key: tuple[str, str], source_bare_id: str | None
) -> bool:
    """Whether one extracted reference matches the scoped source on (type, id) (rulebook §3.2).

    Strict (type, id) equality for the UUID domains; for a full
    ``feat-NNN-slug`` source additionally the bare ``feat-NNN`` spelling
    (the feat dual-spelling rule -- the reverse side of the inherited
    extraction caveat, rulebook §3.7).
    """
    assert isinstance(reference, tuple), type(reference)

    ref_type, ref_id = reference
    source_type, source_id = source_key
    if ref_type != source_type:
        result = False
    elif ref_id == source_id:
        result = True
    else:
        result = source_bare_id is not None and ref_id == source_bare_id
    return result


def _apply_feat_exclusion(
    title: str,
    nodes: dict[tuple[str, str], str | None],
    edges: set[tuple[str, str, str, str]],
    include_feat: bool,
    source_key: tuple[str, str] | None,
) -> ReferenceGraph:
    """The FEAT exclusion (rulebook §3.5 -- ONE post-hoc rule, applied LAST in all modes).

    ``include_feat=True``: the full graph, unchanged. ``include_feat=False``:
    drop every FEAT node except the explicitly requested source
    (``source_key`` -- scoped mode only; the registry-wide builder passes
    ``None``), then drop every edge touching a dropped node. A feat target
    must not surface as a node in any mode (the post-hoc drop is the
    definition; the builders above never special-case feat during the
    build, so this one rule is the whole exclusion).
    """
    assert isinstance(title, str), type(title)
    assert isinstance(include_feat, bool), type(include_feat)

    if include_feat:
        dropped: set[tuple[str, str]] = set()
    else:
        dropped = {key for key in nodes if key[0] == FEAT and key != source_key}
    kept_nodes = {key: node_title for key, node_title in nodes.items() if key not in dropped}
    kept_edges = {edge for edge in edges if (edge[0], edge[1]) not in dropped and (edge[2], edge[3]) not in dropped}
    result = ReferenceGraph(
        title=title,
        nodes=tuple(
            GraphNode(type=key[0], id=key[1], title=node_title) for key, node_title in sorted(kept_nodes.items())
        ),
        edges=tuple(GraphEdge(*edge) for edge in sorted(kept_edges)),
    )
    return result


def build_source_graph(
    source_type: str,
    source_id: str,
    *,
    depth: int = 1,
    reverse: bool = False,
    include_feat: bool = True,
) -> ReferenceGraph:
    """Build the scoped reference graph of one source document (rulebook §3.1/§3.2/§3.5).

    Level 0 = the source (loaded via the source domain's own id resolution:
    a missing source raises the domain's own ``XNotFoundError``, an
    existing-but-broken source raises the domain's own parse error -- the
    Phase 120 tool layer's ``ParseFailureResult`` conversion point). The
    forward expansion is a BFS over outgoing references: a level-k node is
    expanded only if k < ``depth`` and it resolved to an existing document
    (its body read through ``_splice.body_text`` -- the raw,
    frontmatter-stripped markdown, the ``list_references`` source-read
    precedent); each unique (type, id) reference adds exactly one edge +
    one node (the node title via :func:`resolve_reference`; a dangling
    target = ``title=None`` = the unresolved node). ``reverse=True`` is
    ADDITIVE and direct-only on the incoming side: the full 14-domain scan
    adds a scanned document as a node + one incoming edge to the source iff
    it carries a reference matching the source on (type, id) (the feat
    dual-spelling rule: a full ``feat-NNN-slug`` source also matches a bare
    ``feat-NNN`` reference) -- no transitive incoming expansion (a scanned
    document's own references are never walked; only the forward frontier
    grows with ``depth``). A document that vanishes mid-build between the
    parse leg and one of the two EXTRACTION legs (the forward BFS's
    resolved-node ``body_text`` re-read, the reverse pass's
    scanned-document re-read) is skipped on that leg only: the forward leg
    drops the node's expansion (the node and the edge that reached it
    remain), the reverse leg drops the document entirely (no node, no
    incoming edge) -- the build never raises for content (module
    docstring). The graph title is the source's derived H1
    (the :func:`_doc_title` derivation -- the same one a reference to the
    source would resolve to). The visited (type, id) set bounds the build
    (rulebook §3.6); the FEAT exclusion is applied last (rulebook §3.5).

    Parameters
    ----------
    source_type:
        The source document's lowercase domain name: one of
        ``ALL_DOMAINS`` (the 13 whole-body domains plus ``adr``). Assumed
        validated by the caller (the Phase 120 tool's own ``type``
        parameter); a name outside ``ALL_DOMAINS`` is a ``KeyError``
        programming error.
    source_id:
        The source document's verbatim id (the canonical lowercase-hex
        uuid for the UUID domains, the full ``feat-NNN-slug`` for
        ``feat`` -- a bare ``feat-NNN`` is a wrong-format id the tool layer
        rejects, rulebook §6). Assumed validated by the caller.
    depth:
        The forward BFS depth (1..5, default 1 -- the tool/CLI layer
        validates the range; this builder assumes validated input and
        ``assert``s the contract). Governs the forward part only.
    reverse:
        When ``True``, add the direct incoming references to the source
        (the additive 14-domain scan, rulebook §3.2).
    include_feat:
        When ``False``, apply the FEAT exclusion (rulebook §3.5) last:
        drop every FEAT node except this source (when it is one), then
        every edge touching a dropped node.

    Returns
    -------
    ReferenceGraph
        The scoped graph (title = the source's derived H1).

    Raises
    ------
    KeyError
        ``source_type`` is outside ``ALL_DOMAINS`` -- a programming error
        (the tool layer validates the type first).
    LookupError
        The source domain's own ``XNotFoundError`` (a ``LookupError``
        subclass): no document of ``source_type`` has this id.
    AssertionError / pydantic.ValidationError / yaml.YAMLError / AdrParseError
        The source exists but fails to parse -- the domain's own parse
        error (the tool layer converts it to the non-raising
        ``ParseFailureResult``).
    AssertionError
        ``depth`` outside 1..5 or a non-int ``depth`` (the caller's
        validation contract), or a non-str/bool argument.
    """
    assert isinstance(source_type, str), type(source_type)
    assert isinstance(source_id, str), type(source_id)
    assert isinstance(depth, int), type(depth)
    assert 1 <= depth <= 5, depth
    assert isinstance(reverse, bool), type(reverse)
    assert isinstance(include_feat, bool), type(include_feat)

    path, doc = _load_source(source_type, source_id)
    source_key = (source_type, source_id)
    source_title = _doc_title(source_type, doc)

    nodes: dict[tuple[str, str], str | None] = {source_key: source_title}
    edges: set[tuple[str, str, str, str]] = set()
    resolved_paths: dict[tuple[str, str], Path] = {source_key: path}
    visited: set[tuple[str, str]] = {source_key}

    # The forward BFS: level 0 = the source; a level-k node is expanded
    # only if k < depth (the range-depth loop) and it resolved (it sits in
    # resolved_paths); each unique reference adds one edge + one node. A
    # resolved node whose file vanishes between its resolution and this
    # re-read skips its EXPANSION only (the node and the edge that reached
    # it remain; no outgoing references from the vanished document are
    # added -- the module docstring's vanished-mid-build rule).
    frontier: list[tuple[str, str]] = [source_key]
    for _level in range(depth):
        if not frontier:
            break
        next_frontier: list[tuple[str, str]] = []
        for key in frontier:
            try:
                references = _unique_references(body_text(resolved_paths[key]))
            except FileNotFoundError:
                continue  # vanished mid-build: skip this node's expansion only (the render never fails)
            for ref_type, ref_id in references:
                target_key = (ref_type, ref_id)
                edges.add((key[0], key[1], ref_type, ref_id))
                if target_key not in nodes:
                    row = resolve_reference(ref_type, ref_id)
                    nodes[target_key] = row.title  # None for a dangling target (the unresolved node)
                    if row.path is not None:
                        resolved_paths[target_key] = Path(row.path)
                if target_key in resolved_paths and target_key not in visited:
                    visited.add(target_key)
                    next_frontier.append(target_key)
        frontier = next_frontier

    # The reverse pass (additive, direct-only): the full 14-domain scan adds
    # a scanned document as a node + one incoming edge to the source iff it
    # carries a matching reference (the feat dual-spelling rule for a full
    # feat source). The source's own document is skipped (its self-reference,
    # if any, already came from the forward pass). A scanned document whose
    # file vanishes between the scan's parse leg and this re-read is skipped
    # entirely (no node, no incoming edge -- exactly the parse-leg vanished
    # rule, the module docstring's vanished-mid-build rule).
    if reverse:
        source_bare_id = _bare_feat_id(source_id) if source_type == FEAT else None
        for scan_type, scan_path, scan_doc in _iter_source_documents():
            scan_id = scan_doc.frontmatter.id
            if scan_id is None:
                continue  # not addressable and not referenceable (see the module docstring)
            scan_key = (scan_type, scan_id)
            if scan_key == source_key:
                continue
            try:
                references = _unique_references(body_text(scan_path))
            except FileNotFoundError:
                continue  # vanished mid-build: skipped entirely (the render never fails)
            for reference in references:
                if _reference_matches_source(reference, source_key, source_bare_id):
                    nodes.setdefault(scan_key, _doc_title(scan_type, scan_doc))
                    edges.add((scan_type, scan_id, source_type, source_id))
                    break

    result = _apply_feat_exclusion(source_title, nodes, edges, include_feat, source_key)
    return result


def build_registry_graph(*, include_feat: bool = True) -> ReferenceGraph:
    """Build the registry-wide reference graph (rulebook §3.3/§3.5).

    The same full 14-domain scan the reverse pass uses: every successfully
    parsed document is a node (title via :func:`_doc_title`); every
    extracted reference is an edge (deduped per source document); a target
    not present as a scanned document gets its title via
    :func:`resolve_reference` (dangling ⇒ ``title=None`` ⇒ the unresolved
    node). Broken documents are skipped (rulebook §3.4) and documents whose
    frontmatter id is ``None`` are not addressable nor referenceable, so
    they contribute no node (every reference id is a concrete uuid or feat
    id; the builders' graph keys are (type, id) pairs). A scanned document
    that vanishes mid-build between the scan's parse leg and this builder's
    own EXTRACTION leg (the ``body_text`` re-read -- the body is read first
    and the node added only on a successful read) is skipped entirely (no
    node, no edges) -- the build never raises for registry content (module
    docstring). The graph title is the frozen ``Reference Graph`` default
    (the tool layer's ``title`` override replaces it before rendering). The
    FEAT exclusion is applied last (rulebook §3.5 -- ``source_key=None``:
    every FEAT node drops).

    Parameters
    ----------
    include_feat:
        When ``False``, apply the FEAT exclusion (rulebook §3.5) last:
        drop every FEAT node, then every edge touching a dropped node.

    Returns
    -------
    ReferenceGraph
        The registry-wide graph (title = ``Reference Graph``).

    Raises
    ------
    AssertionError
        A non-bool ``include_feat`` (program-invariant failure only -- the
        builder never raises for registry content).
    """
    assert isinstance(include_feat, bool), type(include_feat)

    nodes: dict[tuple[str, str], str | None] = {}
    edges: set[tuple[str, str, str, str]] = set()
    for scan_type, scan_path, scan_doc in _iter_source_documents():
        scan_id = scan_doc.frontmatter.id
        if scan_id is None:
            continue  # not addressable and not referenceable (see the module docstring)
        # The body is read FIRST and the node added only on a successful
        # read: a document whose file vanishes between the scan's parse leg
        # and this re-read is skipped entirely (no node, no edges -- the
        # module docstring's vanished-mid-build rule).
        try:
            references = _unique_references(body_text(scan_path))
        except FileNotFoundError:
            continue  # vanished mid-build: skipped entirely (the render never fails)
        nodes[(scan_type, scan_id)] = _doc_title(scan_type, scan_doc)
        for ref_type, ref_id in references:
            edges.add((scan_type, scan_id, ref_type, ref_id))
    for ref_type, ref_id in {(edge[2], edge[3]) for edge in edges}:
        if (ref_type, ref_id) not in nodes:
            row = resolve_reference(ref_type, ref_id)
            nodes[(ref_type, ref_id)] = row.title  # None for a dangling target (the unresolved node)

    result = _apply_feat_exclusion(_REGISTRY_TITLE, nodes, edges, include_feat, None)
    return result
