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

"""``@mcp.tool()`` wrapper: list_references (feat-144-ref-artifact, Phase 2).

The generic, cross-domain cross-reference listing tool (ADR 36905d5b's
dispatch-only convention: one ``general/tools/`` module, not a per-domain
``list_references_<d>``). It takes a *source* document's ``type``/``id`` --
every whole-body domain (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/
``rsk``/``dec``/``sop``/``feat``/``vcr``/``sysrs``) plus ``adr`` -- reads
the source as raw, frontmatter-stripped body text
(``general.tools._splice.body_text``: the doc-cache does **not** apply to
the source, since extraction needs the literal markdown), extracts every
``<TYPE> <uuid>`` cross-reference from it
(``general.tools._references.find_references``), deduplicates repeated
occurrences of the same reference (first-occurrence order preserved), and
resolves each unique reference to the referenced document in its own target
domain (``general.tools._references.resolve_reference``: the target
domains' own cache-backed ``load_by_id``; ``adr`` never, ADR bfd76370).
The result is one
:class:`~biz.dfch.specmgr.general.models.reference.ReferenceRow` per unique
reference, wrapped in ``PagedResult[ReferenceRow]`` via the exact ``list_*``
paging mechanism (``normalize_paging`` + ``paginate``, ADR ec9f5262):
``total`` = the number of unique references, ``error_count`` = the number
of references that could not be resolved, ``truncated`` when more
references exist beyond the page.

The naive per-reference resolution strategy (every unique reference is
resolved on each call) is the accepted v1 limitation -- the per-domain
batched optimization is tracked in GitHub issue #145.

Error semantics: an invalid source ``type``/``id`` (unknown type,
path-injection attempt, wrong-format id) is a ``ValueError`` raised by
``_path_safety.validate_id`` **before** any filesystem access (ACC-005); a
source document that does not exist on disk raises the source domain's own
``XNotFoundError`` (identical to ``get_<d>``, ACC-006); a *reference* that
cannot be resolved never raises -- it is a row with null ``title``/``path``
and the target domain's not-found message in ``error`` (ACC-003).

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from ...adr.tools._io import load_by_id as load_adr_by_id
from ...adr.tools._paths import adr_base_dir
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._paths import dec_base_dir
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._paths import feat_base_dir
from ...general.models import PagedResult, ReferenceRow
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
from ...server import mcp
from ...sop.tools._io import load_by_id as load_sop_by_id
from ...sop.tools._paths import sop_base_dir
from ...sysrs.tools._io import load_by_id as load_sysrs_by_id
from ...sysrs.tools._paths import sysrs_base_dir
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._paths import tsk_base_dir
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._paths import uc_base_dir
from ...vcr.tools._io import load_by_id as load_vcr_by_id
from ...vcr.tools._paths import vcr_base_dir
from ._domains import ALL_DOMAINS
from ._paging import normalize_paging, paginate
from ._path_safety import assert_within, validate_id
from ._references import find_references, resolve_reference
from ._splice import body_text

__all__ = ["list_references"]

#: Per source-domain ``(<d>_base_dir, load_<d>_by_id)`` pair (feat-144
#: Task 2.3): the source document is resolved through the source domain's
#: own id resolution (the domain's own ``XNotFoundError`` propagates
#: unchanged -- identical to ``get_<d>``), and its parsed document is
#: discarded (only the path is needed: the extraction scans the raw,
#: frontmatter-stripped body text, not the parsed model -- the doc-cache
#: does not apply to the source read).
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
    "adr": (adr_base_dir, load_adr_by_id),
}

assert set(_SOURCE_LOADERS) == set(ALL_DOMAINS), (
    "_SOURCE_LOADERS keys drifted from the shared general.tools._domains.ALL_DOMAINS source -- add or "
    "remove the missing source domain's (<d>_base_dir, load_<d>_by_id) pair in both places "
    "(feat-144-ref-artifact, Task 7.3)"
)


def _load_source_path(type_: str, id_: str) -> tuple[Path, Path]:
    """Resolve the source document's on-disk path (feat-144 Task 2.3).

    Returns ``(base_dir, path)`` for the source domain: ``base_dir`` the
    source domain's own base directory (for the caller's
    ``_path_safety.assert_within`` defense-in-depth check), ``path`` the
    resolved source file. The source domain's own ``XNotFoundError``
    propagates unchanged (a source that does not exist on disk is this
    tool's only not-found *raise* -- ACC-006, identical to ``get_<d>``).
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(id_, str), type(id_)

    base_dir_fn, load_fn = _SOURCE_LOADERS[type_]
    base_dir = base_dir_fn()
    path, _doc = load_fn(base_dir, id_)
    result: tuple[Path, Path] = (base_dir, path)
    return result


@mcp.tool(
    name="list_references",
    title="List referenced artifacts",
    description=(
        "Cross-references of one source document, resolved and paged. `type` is the source "
        f"document's domain (one of {', '.join(ALL_DOMAINS)}) and `id` the source's own "
        "identifier. The tool scans the source's frontmatter-stripped body for `<TYPE> <uuid>` "
        "references (the shared reference-tag vocabulary in "
        "general.tools._references: case-insensitive tag, space or dash separator, anywhere in a "
        "line), dedupes repeated occurrences (first-occurrence order preserved), and resolves each "
        "unique reference to the referenced document in its own target domain. Returns a "
        "`PagedResult` of one `ReferenceRow` per unique reference: `type`, `id`, `title` (the "
        "referenced document's H1), and `path` (the referenced document's resolved absolute file "
        "path). A reference that cannot be resolved on disk is a row with null `title`/`path` and "
        "the target domain's not-found message in `error` -- it never raises. `max_results`/"
        "`offset` control paging (default page size 25, capped at 100); out-of-range values are "
        "clamped, not errored. An invalid `id` (path-injection attempt or wrong format for "
        "`type`) is a `ValueError` raised before any file access; a missing source document is "
        "the source domain's own `XNotFoundError`."
    ),
)
def list_references(
    type: Literal[*ALL_DOMAINS],
    id: str,
    max_results: int | None = None,
    offset: int | None = None,
) -> PagedResult[ReferenceRow]:
    """List the cross-references of one source document, resolved and paged.

    The source is identified by ``type`` (every whole-body domain
    ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
    ``feat``/``vcr``/``sysrs``, plus ``adr``) and its own ``id``, and is
    validated via ``_path_safety.validate_id`` before any filesystem
    access (ACC-005). The source is then read as raw, frontmatter-stripped
    body text (``_splice.body_text`` -- the doc-cache does not apply to it,
    since extraction needs the literal markdown), and every ``<TYPE>
    <uuid>`` cross-reference in that text is extracted
    (``_references.find_references``: the reference tag is case-insensitive
    and separated from the uuid by one or more space/tab/dash characters;
    a match may sit anywhere in a line; the reference's own inline title is
    not captured). Repeated occurrences of the same ``(type, id)``
    reference are deduplicated to one row, first-occurrence order preserved
    (REQ-005).

    Each unique reference is resolved to the referenced document in its own
    target domain (``_references.resolve_reference``: the nine flat target
    domains read through their own cache-backed ``load_by_id``; ``adr``
    never does -- ADR bfd76370). The row's ``title`` is the referenced
    document's own ``# {title}`` H1 and its ``path`` the referenced
    document's resolved absolute file path; a reference whose target does
    not exist on disk is a row with ``title``/``path`` ``None`` and the
    target domain's own not-found message in ``error`` -- target resolution
    never raises (ACC-003).

    The full, deduplicated row list is wrapped in
    ``PagedResult[ReferenceRow]`` via the exact ``list_*`` paging
    mechanism (``_paging.normalize_paging`` + ``paginate``, ADR ec9f5262):
    ``total`` = the number of unique references, ``error_count`` = the
    number of references that could not be resolved, ``truncated`` when
    more references exist beyond the page (ACC-009).

    Parameters
    ----------
    type:
        The source document's type / domain: one of ``adr``, ``req``,
        ``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``,
        ``sop``, ``feat``, ``vcr``, ``sysrs``.
    id:
        The source document's specmgr-assigned identifier (the
        ``feat-NNN-slug`` folder name for ``feat``).
    max_results:
        Maximum number of reference rows to return in this page. Defaults
        to ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given
        (``None``); otherwise clamped into range (see
        :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
    offset:
        Zero-based index of the first reference row to include in this
        page. Defaults to ``0`` when not given (``None``); negative values
        are floored to ``0``.

    Returns
    -------
    PagedResult[ReferenceRow]
        One row per unique cross-reference in the source document's body,
        in first-occurrence order, windowed to the requested page.
        ``results`` is empty if the source body contains no references at
        all, or if ``offset`` is past the end of the full list.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not in the dispatched
        domain's own format (raised before any filesystem access; nothing
        is read) -- ACC-005.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError /
    QaNotFoundError / PrbNotFoundError / GolNotFoundError /
    RskNotFoundError / DecNotFoundError / SopNotFoundError /
    FeatNotFoundError / VcrNotFoundError / SysrsNotFoundError /
    AdrNotFoundError
        No document of the dispatched source ``type`` has this ``id`` --
        the source domain's own not-found error, propagated unchanged from
        the source domain's own ``load_by_id`` (identical to ``get_<d>``)
        -- ACC-006.
    """
    # feat-144 REQ-006: validate the source id before any filesystem access (injection prevention).
    validate_id(type, id)
    # feat-144 REQ-001/ACC-006: resolve the source through its own domain's id resolution.
    base_dir, path = _load_source_path(type, id)
    assert_within(base_dir, path)  # feat-144 REQ-006: defense-in-depth
    text = body_text(path)  # feat-144 REQ-006: the raw, frontmatter-stripped markdown to scan
    # feat-144 REQ-002/REQ-005: unique references, first-occurrence order.
    rows: list[ReferenceRow] = []
    seen: set[tuple[str, str]] = set()
    error_count = 0
    for ref_type, ref_id in find_references(text):
        key = (ref_type, ref_id)
        if key in seen:
            continue
        seen.add(key)
        row = resolve_reference(ref_type, ref_id)
        rows.append(row)
        if row.error is not None:
            error_count += 1
    # feat-144 REQ-010: the exact `list_*` paging mechanism.
    result: PagedResult[ReferenceRow] = paginate(rows, *normalize_paging(max_results, offset), error_count=error_count)
    return result
