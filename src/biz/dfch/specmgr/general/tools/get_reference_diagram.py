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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: get_reference_diagram (feat-207-reference-graph, Phase 120, REQ-004).

Read-only, id-based diagram tool for one source document's reference
neighbourhood, rendered as the deterministic PlantUML component diagram of
the reference-graph rulebook (``specmgr://reference-graph`` /
``general/data/general_reference_graph.md`` §2–§5): one node per artifact
(label = the document title, truncated to the ``SPECMGR_DIAGRAM_MAX_TITLE``
label limit, default 40), a stereotype + colour per artifact type (the
frozen 14-entry palette), nodes grouped into per-domain curly
``component "TYPE" { … }`` domain groups (the 2026-10-15 corrected form,
rulebook §2.7), one label-free edge per unique reference (``{src} -->
{dst}`` -- the referenced item carries the incoming arrow), every edge
lying on a cycle (SCC-based) drawn with the red label-free ``-[#red]->``
arrow, and every reference whose target cannot be resolved on disk drawn
as a top-level ``<<UNRESOLVED>>`` node.

Thin over the Phase 110 library (``_reference_graph.build_source_graph`` +
``reference_graph.render_reference_graph`` + ``_diagram_config.
diagram_max_title``): this module adds only the tool layer's own contract --
the guard order of Design Notes §7 (``_path_safety.validate_id`` and the
``depth`` 1..5 range check are BOTH pure input validation raising
``ValueError`` before any filesystem access; for ``type="feat"`` a bare
``feat-NNN`` is a wrong-format id, not a normalization candidate -- use
``list_feat`` to discover the exact ``feat-NNN-slug`` id), the source load's
error mapping (a missing source raises the source domain's own
``XNotFoundError``, identical to ``get_<d>``/``list_references``; an
existing-but-broken source returns the non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` -- case 3 of the
ADR 519d1206 workaround chain -- with the ``error`` text byte-identical to
the domain's ``list_<d>`` failed-row ``error`` for the same file (ADR
9080b37c) for the 12 whole-body domains -- time-qualified by ADR
3982712a for ``feat`` (``get_feat`` the unconditional full-fidelity
authority) -- and, for ``adr`` (whose ``list_adr`` carries no failed row:
broken ADRs are skipped), the leg-read ``AdrParseError``'s own text), the
``title`` override (replaces the graph's title before
rendering; the renderer sanitizes the title but never truncates it), and the
``max_label`` read via the shared env-var helper (the pure renderer takes it
as a plain parameter and never reads the env var itself).

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects to
the builtin shadow.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from ...adr.tools._paths import iter_adr_paths
from ...feat.tools._paths import find_feat_parse_failure
from ...general.models import ParseFailureResult
from ...general.models.reference_graph import ReferenceGraph, render_reference_graph
from ...general.tools._diagram_config import diagram_max_title
from ...general.tools._doc_paths import find_parse_failure
from ...general.tools._path_safety import assert_within, validate_id
from ...general.tools._reference_graph import (
    _SCAN_ERROR_TYPES,
    _SCAN_READERS,
    _SOURCE_LOADERS,
    build_source_graph,
)
from ...server import mcp
from ._domains import ADR, ALL_DOMAINS, FEAT, WholeBodyOrAdrType

__all__ = ["get_reference_diagram"]

#: The frozen forward BFS depth range (rulebook §3.1: 1..5, default 1).
_DEPTH_MIN = 1
_DEPTH_MAX = 5


def _validate_depth(depth: Any) -> int:
    """The pure ``depth`` input validation (Design Notes §7 guard 2, rulebook §7).

    ``depth`` must be a plain ``int`` in 1..5 (a ``bool`` -- an ``int``
    subclass -- is rejected; the contract is a plain int). Raises a
    ``ValueError`` before any filesystem access; returns the validated int.

    Parameters
    ----------
    depth:
        The requested forward BFS depth (annotated ``int`` in the public
        signature; direct-Python callers may pass anything).

    Returns
    -------
    int
        The validated depth, unchanged.

    Raises
    ------
    ValueError
        ``depth`` is not a plain ``int``, or it lies outside 1..5; the
        message names the offending value.
    """
    # Strict int check: a bool (an int subclass) is rejected, not coerced.
    if type(depth) is not int:  # pylint: disable=unidiomatic-typecheck
        raise ValueError(
            f"depth must be a plain int in {_DEPTH_MIN}..{_DEPTH_MAX} (the forward BFS depth), "
            f"got {type(depth).__name__} ({depth!r})"
        )
    if not _DEPTH_MIN <= depth <= _DEPTH_MAX:
        raise ValueError(f"depth must be in {_DEPTH_MIN}..{_DEPTH_MAX} (the forward BFS depth), got {depth!r}")
    return depth


def _broken_source_failure(type_: str, id_: str) -> ParseFailureResult | None:
    """The non-raising ``ParseFailureResult`` for an existing-but-broken source, or ``None``.

    The Phase 110 probe mechanism re-run from the tool layer (the builder's
    own ``_raise_broken_source`` runs the identical probes and re-raises;
    this one returns instead): ``feat`` goes through
    ``feat.tools._paths.find_feat_parse_failure`` (the folder-per-document
    counterpart -- its ``error`` is byte-identical to ``list_feat``'s own
    failed row for the same file once that file's clean stage has converged,
    time-qualified by ADR 3982712a), every other domain through the shared
    flat-file ``find_parse_failure`` name-match scan called with the
    domain's own ``read_<d>`` leg (cache-backed for the 11 flat-file
    whole-body domains, whose ``list_<d>`` failed row reads with the same
    ``read_fn``, so the captured ``str(exc)`` is byte-identical to that
    row's ``error`` -- ADR 9080b37c). For ``adr``, ``find_parse_failure``
    's own leg read propagates the domain's parse error (``AdrParseError`` is
    outside its catch tuple -- the Phase 110 mechanism's own adr channel), in
    which case the single name-matching file is the broken source itself and
    the captured ``str(exc)`` is that ``AdrParseError``'s own text
    (``list_adr`` carries no failed row -- broken ADRs are skipped -- so the
    ADR 9080b37c byte-identity has no referent there). The probed path
    passes the same ``assert_within`` guard every ``get_<d>``/``update``
    branch applies.

    Parameters
    ----------
    type_:
        The source document's domain (one of ``ALL_DOMAINS``; assumed
        validated by the caller).
    id_:
        The source document's id (assumed validated by the caller).

    Returns
    -------
    ParseFailureResult | None
        The result for the name-matching, unparseable source file, or
        ``None`` if there is no parse failure to surface (no name match, a
        vanished file, or a name-matching file that parses cleanly).
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(id_, str), type(id_)

    base_dir_fn, _load_fn = _SOURCE_LOADERS[type_]
    read_fn = _SCAN_READERS[type_]
    base_dir = base_dir_fn()
    failure: tuple[Path, str] | None
    if type_ == FEAT:
        failure = find_feat_parse_failure(base_dir, id_)
    elif type_ == ADR:
        try:
            failure = find_parse_failure(base_dir, id_, read_fn)
        except _SCAN_ERROR_TYPES as exc:
            matches = [
                path for path in iter_adr_paths(base_dir) if f"-{id_}-" in path.stem or path.stem.startswith(f"{id_}-")
            ]
            failure = None if len(matches) != 1 else (matches[0], str(exc))
    else:
        failure = find_parse_failure(base_dir, id_, read_fn)
    if failure is None:
        result: ParseFailureResult | None = None
        return result
    failure_path, failure_error = failure
    assert_within(base_dir, failure_path)
    result = ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id_)
    return result


@mcp.tool(
    name="get_reference_diagram",
    title="Get the reference diagram of one document",
    description=(
        "Render and return the deterministic PlantUML component diagram of one source document's "
        "reference neighbourhood (the frozen rulebook specmgr://reference-graph §2–§5): one node "
        "per artifact (label = the document title, truncated to SPECMGR_DIAGRAM_MAX_TITLE, "
        "default 40), a stereotype + colour per artifact type, nodes grouped into per-domain "
        "curly-brace component groups (one per non-empty domain, closed with `}` -- the "
        "2026-10-15 corrected form), one label-free edge per unique reference "
        "(`{src} --> {dst}`, the referenced item carries the incoming arrow), every edge "
        "lying on a cycle "
        "(SCC-based) drawn with the red label-free `-[#red]->` arrow, and every reference whose "
        "target cannot be resolved on disk drawn as a top-level `<<UNRESOLVED>>` node. `type` "
        f"is the source document's domain (one of "
        f"{', '.join(ALL_DOMAINS)}) and `id` the source's own identifier; `depth` (1..5, "
        "default 1) is the forward BFS depth; `reverse=True` is additive (the forward expansion "
        "to `depth` plus the direct incoming references to the source, direct-only on the "
        "incoming side); `include_feat=False` drops every FEAT node except the explicitly "
        "requested source (then every edge touching a dropped node); `title` overrides the "
        "diagram title (default: the source's H1; sanitized but never truncated). Guard order: "
        '`id` (path-injection attempt or wrong format -- for `type="feat"` the full '
        "feat-NNN-slug only; a bare feat-NNN is rejected, use list_feat to discover the exact "
        "id) and `depth` are both a `ValueError` raised before any filesystem access; a missing "
        "source raises the source domain's own `XNotFoundError`; an existing-but-broken source "
        "returns the non-raising `ParseFailureResult` (`error`/`path`/`id`, the `error` text "
        "byte-identical to the domain's `list_<d>` failed-row `error` for the same file (ADR "
        "9080b37c) for the 12 whole-body domains -- time-qualified by ADR 3982712a for `feat`; "
        "for `adr` (whose `list_adr` carries no failed row: broken ADRs are skipped), the "
        "leg-read `AdrParseError`'s own text). Returns PlantUML source (not a specmgr document) "
        "-- run it through "
        "`specmgr plantuml-check` (CLI) or the `validate_plantuml` tool for a validation verdict."
    ),
)
# The frozen Design Notes §10 signature carries six parameters
# (type/id/depth/reverse/include_feat/title) -- more than pylint's 5-argument default.
def get_reference_diagram(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    type: WholeBodyOrAdrType,
    id: str,
    depth: int = 1,
    reverse: bool = False,
    include_feat: bool = True,
    title: str | None = None,
) -> str | ParseFailureResult:
    """Render and return the PlantUML reference diagram of one source document's neighbourhood.

    The source is identified by ``type`` (every whole-body domain
    ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
    ``feat``/``vcr``/``sysrs``, plus ``adr``) and its own ``id``. The graph
    is the source document, its outgoing reference neighbourhood to
    ``depth`` (level 0 = the source; a level-k node is expanded only if
    k < ``depth`` and it resolved to an existing document), optionally plus
    the direct incoming references to the source (``reverse``: additive and
    direct-only on the incoming side), with the FEAT exclusion
    (``include_feat=False``) applied last -- the Phase 110
    ``build_source_graph`` construction semantics (rulebook §3), rendered
    by the pure, byte-stable ``render_reference_graph`` (rulebook §2).

    Guard order (Design Notes §7, rulebook §7): (1) ``_path_safety.
    validate_id`` and (2) the ``depth`` range check (a plain ``int`` in
    1..5) are BOTH pure input validation raising ``ValueError`` before any
    filesystem access -- a malformed ``type``/``id``/``depth`` never reaches
    the filesystem. For ``type="feat"`` the full ``feat-NNN-slug`` is the
    only accepted source id: a bare ``feat-NNN`` is a wrong-format id, not a
    normalization candidate (the ``get_feat``/``list_references`` parity) --
    use ``list_feat`` to discover the exact id. Then the source load: a
    missing source raises the source domain's own ``XNotFoundError``
    (identical to ``get_<d>``/``list_references``); an existing-but-broken
    source returns the non-raising
    :class:`~biz.dfch.specmgr.general.models.ParseFailureResult` (case 3 of
    the ADR 519d1206 workaround chain) instead of raising -- its ``error``
    text is byte-identical to that domain's ``list_<d>`` failed-row
    ``error`` for the same file (ADR 9080b37c) for the 12 whole-body domains
    -- time-qualified by ADR 3982712a for ``feat`` (``get_feat`` the
    unconditional full-fidelity authority) -- and, for ``adr`` (whose
    ``list_adr`` carries no failed row: broken ADRs are skipped), the
    leg-read ``AdrParseError``'s own text. The build then never raises
    for target-side content (a dangling target becomes the unresolved node),
    and the render is pure.

    The diagram title is the ``title`` override when given (sanitized but
    never truncated by the renderer), else the source's derived H1 (the
    ``feature_title`` prefix strip for ``feat``, the ``adr`` body's own
    ``title`` field, every other domain's body H1). The resolved-node label
    limit is the ``SPECMGR_DIAGRAM_MAX_TITLE`` env var via the shared
    ``_diagram_config.diagram_max_title`` helper (default 40; a
    set-but-invalid value falls back to 40 -- the ``specmgr://config``
    ``diagram`` section reports its set/valid/default/resolved status).

    Parameters
    ----------
    type:
        The source document's type / domain: one of ``adr``, ``req``,
        ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``,
        ``sop``, ``feat``, ``vcr``, ``sysrs``.
    id:
        The source document's specmgr-assigned identifier (the canonical
        lowercase-hex UUID for every domain other than ``feat``; the full
        ``feat-NNN-slug`` folder name for ``feat`` -- a bare ``feat-NNN``
        is rejected, rulebook §6).
    depth:
        The forward BFS depth: 1..5 (default 1). Governs the forward part
        only; ``reverse`` is additive and direct-only on the incoming side
        (rulebook §3.2).
    reverse:
        When ``True``, add the direct incoming references to the source
        (the additive 13-domain scan, rulebook §3.2).
    include_feat:
        When ``False``, apply the FEAT exclusion (rulebook §3.5) last: drop
        every FEAT node except this source (when it is one), then every
        edge touching a dropped node.
    title:
        An optional diagram-title override (sanitized but never truncated);
        when ``None``, the source's derived H1.

    Returns
    -------
    str | ParseFailureResult
        The byte-stable PlantUML source (``@startuml …`` through
        ``@enduml``, one trailing newline) on success; the non-raising
        :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
        (``error``/``path``/``id``) for an existing-but-broken source.

    Raises
    ------
    ValueError
        ``type`` is outside the 13-domain vocabulary, ``id`` is a
        path-injection attempt or not in the dispatched domain's own format
        (for ``feat``: not a full ``feat-NNN-slug``), or ``depth`` is not a
        plain ``int`` in 1..5 -- all raised before any filesystem access;
        nothing is read.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError /
    QaNotFoundError / PrbNotFoundError / GolNotFoundError /
    RskNotFoundError / DecNotFoundError / SopNotFoundError /
    FeatNotFoundError / VcrNotFoundError / SysrsNotFoundError /
    AdrNotFoundError
        No document of the dispatched source ``type`` has this ``id`` --
        the source domain's own not-found error, propagated unchanged from
        the source domain's own ``load_by_id`` (identical to ``get_<d>``).
    """
    # Design Notes §7 guard order: (1) id validation + (2) the depth range
    # check -- both pure input validation, a ValueError before any
    # filesystem access.
    validate_id(type, id)
    depth = _validate_depth(depth)
    try:
        graph: ReferenceGraph = build_source_graph(type, id, depth=depth, reverse=reverse, include_feat=include_feat)
    except _SCAN_ERROR_TYPES:
        # An existing-but-broken source: the builder raised the domain's
        # own parse error (its _raise_broken_source probe, the Phase 110
        # mechanism) -- convert to the non-raising ParseFailureResult (the
        # feat-150 precedent, case 3 of the ADR 519d1206 chain).
        failure = _broken_source_failure(type, id)
        if failure is not None:
            return failure
        # A repair/delete race (the source parses cleanly or is gone now):
        # re-run the build and let the current state's own outcome stand
        # (a success, or the domain's XNotFoundError / a fresh parse error).
        graph = build_source_graph(type, id, depth=depth, reverse=reverse, include_feat=include_feat)
    if title is not None:
        graph = replace(graph, title=title)
    max_label, _valid = diagram_max_title()
    result: str = render_reference_graph(graph, max_label=max_label)
    return result
