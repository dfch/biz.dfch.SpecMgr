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

"""``@mcp.tool()`` wrapper: validate_qa (Phase 4, Task 4.1).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_qa`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the QA base
directory or resolving an id. This lets a caller check a draft before ever
calling ``create_qa``/``update_qa`` (or independently of either), and is
exactly the same check both of those tools already run internally on their
own ``content`` argument, exposed standalone here. 1:1 port of
``req.tools.validate_req``.
"""

from __future__ import annotations

import frontmatter

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Qa, parse_qa


@mcp.tool(
    name="validate_qa",
    title="Validate QA document content",
    description=(
        "Disk-free, id-free dry run validating QA document content. `full=False` (default) "
        "validates body-only content (no frontmatter); `full=True` validates a complete document "
        "(frontmatter + body)."
    ),
)
def validate_qa(content: str, full: bool = False) -> bool:
    """Validate ``content`` as QA markdown, without reading or writing any file.

    "Validate" means letting :class:`~biz.dfch.specmgr.qa.models.v1.Qa`/
    :class:`~biz.dfch.specmgr.qa.models.v1.QaFrontmatter`/
    :class:`~biz.dfch.specmgr.qa.models.v1.QaDocument`'s own Pydantic
    validators run during parsing -- there is no separate validation pass.
    Successfully constructing the model *is* the validation, so this
    function only ever returns ``True``; any parse/validation failure
    instead propagates as ``AssertionError``/``pydantic.ValidationError``,
    exactly as ``create_qa``/``update_qa`` themselves do.

    Whether ``content`` carries a YAML frontmatter block is detected via
    ``frontmatter.loads(content).metadata`` (non-empty means "has
    frontmatter") -- the same ``python-frontmatter`` library every parser in
    this codebase already depends on, rather than a hand-rolled
    ``startswith("---")`` heuristic.

    Parameters
    ----------
    content:
        The QA markdown to validate.
    full:
        ``False`` (default): ``content`` must be body markdown only (the
        shape ``create_qa``/``update_qa`` accept) -- raises ``ValueError``
        if a frontmatter block is found instead. ``True``: ``content`` must
        be a complete document, frontmatter and body together (the shape
        ``parse_qa`` expects for an on-disk file) -- raises the symmetric
        ``ValueError`` if no frontmatter block is found.

    Returns
    -------
    bool
        Always ``True`` on success.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        parse_qa(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        Qa.from_text(format_text(content))

    return True
