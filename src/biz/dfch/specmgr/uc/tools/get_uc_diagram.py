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

# pylint: disable=redefined-builtin  # id intentionally shadows the builtin: public tool API, issue #41

"""``@mcp.tool()`` wrapper: get_uc_diagram (feat-185-uc-diagrams, Phase 120).

Read-only, id-based diagram tool: renders one use case's deterministic
PlantUML usecase diagram (rulebook ``specmgr://uc/plantuml`` §2.5 -- one
``usecase`` node labelled by title + level stereotype, one ``actor`` node
per distinct cleaned actor label, plain associations). Thin wrapper: the id
resolution mirrors ``get_uc`` exactly (``_path_safety``-guarded, cache-aware
via ``load_by_id``; a truly-absent id raises the domain's not-found error,
an existing-but-broken document returns the non-raising
``ParseFailureResult`` per the feat-150 precedent), and the rendering is the
pure ``uc.models.v2.renderer.render_uc_diagram`` (Phase 110).
"""

from __future__ import annotations

from ...general.models import ParseFailureResult
from ...general.tools._doc_paths import find_parse_failure
from ...general.tools._path_safety import assert_within, validate_id
from ...server import mcp
from ..models.v2.renderer import render_uc_diagram
from ._io import load_by_id, read_uc
from ._paths import UcNotFoundError, uc_base_dir


@mcp.tool(
    name="get_uc_diagram",
    title="Get the per-UC usecase diagram",
    description=(
        "Render and return the deterministic PlantUML usecase diagram for one use case (the frozen "
        "rulebook specmgr://uc/plantuml §2.5): one `usecase` node (title + level stereotype), one "
        "`actor` node per distinct cleaned actor label, plain associations. Read-only: the id is "
        "path-safety-guarded (a wrong-format id is a ValueError before any file access) and the "
        "document is read cache-aware; a document that exists but fails to parse returns the "
        "non-raising ParseFailureResult (`error`/`path`/`id`, the feat-150 precedent), and a truly "
        "absent id raises the domain's not-found error. Returns PlantUML source (not a specmgr "
        "document) -- run it through the validate_plantuml tool for a validation verdict."
    ),
)
def get_uc_diagram(id: str) -> str | ParseFailureResult:
    """Render and return the PlantUML usecase diagram for the use case ``id``.

    Parameters
    ----------
    id:
        The use case document's specmgr-assigned identifier.

    Returns
    -------
    str | ParseFailureResult
        The diagram text (``@startuml ...`` through ``@enduml``, one trailing
        newline) -- byte-stable per the rulebook §2.6 frozen reference. When
        the document exists but fails to parse, a
        :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
        (``error``/``path``/``id``) is returned instead of raising (the
        feat-150 precedent, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c).
        Raises :class:`._paths.UcNotFoundError` if no use case has this id.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not a well-formed id for this
        domain (raised before any filesystem access).
    """
    validate_id("uc", id)

    base_dir = uc_base_dir()
    try:
        path, doc = load_by_id(base_dir, id)
    except UcNotFoundError:
        parse_failure = find_parse_failure(base_dir, id, read_uc)
        if parse_failure is None:
            raise
        failure_path, failure_error = parse_failure
        assert_within(base_dir, failure_path)
        return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id)
    assert_within(base_dir, path)

    result: str = render_uc_diagram(doc.body)
    return result
