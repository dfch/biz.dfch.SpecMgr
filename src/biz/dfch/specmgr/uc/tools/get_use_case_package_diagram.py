# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""``@mcp.tool()`` wrapper: get_use_case_package_diagram (feat-185-uc-diagrams, Phase 120).

Read-only diagram tool: renders the deterministic PlantUML **package**
diagram (rulebook ``specmgr://uc/plantuml`` §2.7 -- one ``usecase`` node
per document, the deduplicated actor union, and the ``<<include>>`` /
``<<extend>>`` / superordinate edges from ``Related Use Cases``). Thin
wrapper over the pure ``uc.models.v2.renderer.render_use_case_package``
(Phase 110), which takes **resolved facts** (``list[PackageDocument]``),
not directory handles: this tool owns the disk resolution (the §11
contract) --

- ``ids=None``: every UC in ``list_uc`` order (all pages, delegated to the
  ``list_uc`` tool itself so the package can never disagree with the
  listing); a ``list_uc`` failed row (an existing-but-broken document)
  becomes a skipped ``use_case=None`` slot,
- explicit ``ids``: each id ``_path_safety``-guarded (a wrong-format id is
  a ``ValueError`` before any file access), cache-aware via
  ``load_by_id``; an id missing on disk or existing-but-broken becomes the
  same skipped slot -- the render never fails on an id,

and every reference that does not resolve to a parsed slot in the package
(taken up by an explicit id, a ``list_uc`` row, or a legacy ``UC-NNN``
token) takes the renderer's deterministic ``Unresolved UC reference`` note
path (rulebook §2.8).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from ...general.tools._listing import FAILED_TO_PARSE_MARKER
from ...general.tools._path_safety import assert_within, validate_id
from ...server import mcp
from ..models.v2 import PackageDocument, UcSummary
from ..models.v2.renderer import render_use_case_package
from ._cache import read_uc
from ._io import load_by_id
from ._paths import UcNotFoundError, uc_base_dir
from .list_uc import list_uc

# the list_uc tool's own page cap (general.tools._paging); the ids=None slot
# list walks every page at that size.
_LIST_PAGE_SIZE = 100


def _list_uc_all_rows() -> list[UcSummary]:
    """Every ``list_uc`` row, in ``list_uc`` order, across all pages."""
    rows: list[UcSummary] = []
    offset = 0
    while True:
        page = list_uc(max_results=_LIST_PAGE_SIZE, offset=offset)
        rows.extend(page.results)
        if not page.results or len(rows) >= page.total:
            break
        offset += len(page.results)
    return rows


def _slots_from_listing() -> list[PackageDocument]:
    """One slot per ``list_uc`` row, in ``list_uc`` order (all pages).

    A failed row (``title`` the ``<failed to parse>`` marker) is a
    ``use_case=None`` slot. A successful row is read back through the
    domain's own cache-backed reader at the row's resolved path (a cache
    hit in the normal case -- the listing scan moments ago read the same
    file through the same reader); a read that fails in the narrow window
    after the listing scan (a concurrent modification or deletion) degrades
    to the same ``use_case=None`` slot -- the render never fails.
    """
    base_dir = uc_base_dir()
    slots: list[PackageDocument] = []
    for row in _list_uc_all_rows():
        if row.title == FAILED_TO_PARSE_MARKER:
            slots.append(PackageDocument(id=row.id, use_case=None))
            continue
        path = Path(row.path)  # the row's own scan-resolved path (within the base dir)
        assert_within(base_dir, path)
        try:
            doc = read_uc(path)
        except (AssertionError, ValidationError, yaml.YAMLError, FileNotFoundError):
            slots.append(PackageDocument(id=row.id, use_case=None))
            continue
        slots.append(PackageDocument(id=row.id, use_case=doc.body))
    return slots


def _slots_from_ids(ids: list[str]) -> list[PackageDocument]:
    """One slot per explicit id, in the given order.

    A missing id or an existing-but-broken one (both surface as
    ``load_by_id``'s ``UcNotFoundError`` -- a broken file's own id is
    unreadable, so the id scan skips it) is a ``use_case=None`` slot;
    references to it take the renderer's unresolvable-note path. The ids
    were already ``_path_safety``-guarded by the caller before this ran.
    """
    base_dir = uc_base_dir()
    slots: list[PackageDocument] = []
    for id_ in ids:
        try:
            path, doc = load_by_id(base_dir, id_)
            assert_within(base_dir, path)
            slots.append(PackageDocument(id=id_, use_case=doc.body))
        except UcNotFoundError:
            slots.append(PackageDocument(id=id_, use_case=None))
    return slots


@mcp.tool(
    name="get_use_case_package_diagram",
    title="Get the multi-UC package diagram",
    description=(
        "Render and return the deterministic PlantUML package diagram for a set of use cases (the "
        "frozen rulebook specmgr://uc/plantuml §2.7): one `usecase` node per document in the given "
        "order, the deduplicated actor union, and the `<<include>>`/`<<extend>>`/superordinate "
        "edges from `Related Use Cases`. ids=None = every UC in list_uc order (list_uc failed rows "
        "-- existing-but-broken documents -- become skipped slots); an id missing on disk or "
        "existing-but-broken becomes the same skipped slot, and any reference that does not "
        "resolve to a parsed slot in the package (including legacy UC-NNN tokens) takes the "
        "deterministic 'Unresolved UC reference' note -- the render never fails on an id or a "
        "reference. Read-only: every given id is path-safety-guarded (a wrong-format id is a "
        "ValueError before any file access) and the documents are read cache-aware. Returns "
        "PlantUML source -- run it through the validate_plantuml tool for a validation verdict."
    ),
)
def get_use_case_package_diagram(ids: list[str] | None = None) -> str:
    """Render and return the PlantUML package diagram for the given use cases.

    Parameters
    ----------
    ids:
        The use case document ids, in package order. ``None`` (the
        default) selects every UC in ``list_uc`` order -- including the
        ``list_uc`` failed rows, which become skipped slots. An id missing
        on disk or existing-but-broken becomes the same skipped slot; the
        render never fails on an id.

    Returns
    -------
    str
        The package diagram text (``@startuml UC Package`` through
        ``@enduml``, one trailing newline). A reference that does not
        resolve to a parsed slot of the package is emitted as the
        deterministic ``note bottom of {alias}: Unresolved UC reference:
        "{label}"`` line (rulebook §2.8) instead of failing the render.

    Raises
    ------
    ValueError
        Any given ``id`` is a path-injection attempt or not a well-formed
        id for this domain (raised before any filesystem access).
    """
    if ids is None:
        slots = _slots_from_listing()
    else:
        for id_ in ids:
            validate_id("uc", id_)
        slots = _slots_from_ids(ids)

    result: str = render_use_case_package(slots)
    return result
