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

"""``@mcp.tool()`` wrapper: validate_dec (Task 2.2).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_dec`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the decision
base directory or resolving an id. This lets a caller check a draft before
ever calling ``create_dec`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here.
"""

from __future__ import annotations

import frontmatter

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Decision, parse_dec


@mcp.tool(
    name="validate_dec",
    title="Validate decision content",
    description=(
        "Disk-free, id-free dry run validating decision content. `full=False` (default) "
        "validates body-only content (no frontmatter); `full=True` validates a complete document "
        "(frontmatter + body)."
    ),
)
def validate_dec(content: str, full: bool = False) -> bool:
    """Validate ``content`` as decision markdown, without reading or writing any file.

    "Validate" means letting :class:`~biz.dfch.specmgr.dec.models.v1.Decision`/
    :class:`~biz.dfch.specmgr.dec.models.v1.DecFrontmatter`/
    :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument`'s own Pydantic
    validators run during parsing -- there is no separate validation pass.
    Successfully constructing the model *is* the validation, so this
    function only ever returns ``True``; any parse/validation failure
    instead propagates as ``AssertionError``/``pydantic.ValidationError``,
    exactly as ``create_dec`` and the generic ``update`` tool do.

    Whether ``content`` carries a YAML frontmatter block is detected via
    ``frontmatter.loads(content).metadata`` (non-empty means "has
    frontmatter") -- the same ``python-frontmatter`` library every parser in
    this codebase already depends on, rather than a hand-rolled
    ``startswith("---")`` heuristic.

    Parameters
    ----------
    content:
        The decision markdown to validate.
    full:
        ``False`` (default): ``content`` must be body markdown only (the
        shape ``create_dec`` and the generic ``update`` tool accept) --
        raises ``ValueError``
        if a frontmatter block is found instead. ``True``: ``content`` must
        be a complete document, frontmatter and body together (the shape
        ``parse_dec`` expects for an on-disk file) -- raises the symmetric
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
        parse_dec(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        Decision.from_text(format_text(content))

    return True
