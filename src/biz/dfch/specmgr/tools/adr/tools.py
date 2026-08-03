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

"""``@mcp.tool()``-decorated ADR wrappers (plan §8, §9a, §10 item 4).

Thin file-I/O/id-lookup adapters over ``models/adr/v1/mutations.py``: every
function here re-reads and re-parses the current on-disk state before
acting, and (for mutating operations) re-renders and re-writes the full
file afterward -- there is no in-memory cache of a parsed :class:`Adr`
(plan §7, §9a): the ``.md`` file itself is always the source of truth.

The ``models.adr.v1.mutations`` module is imported qualified (as
``mutations``), rather than importing its individual functions by name,
because several of them (``update_section``, ``set_status``,
``option_list``, ``option_create``, ``option_read``, ``option_update``,
``option_delete``) share their name with the tool wrapper defined here --
the wrapper is the id/file-aware adapter, ``mutations.<name>`` is the pure,
in-memory operation it delegates to.
"""

from __future__ import annotations

import uuid

from ...models.adr import Adr, AdrBody, AdrFrontmatter
from ...models.adr.v1 import mutations
from ...server import mcp
from ._io import load_by_id, write_adr
from ._paths import adr_base_dir, ensure_adr_base_dir, slugify


@mcp.tool(
    name="get_adr",
    title="Get ADR",
    description="Read, parse, and return a full ADR document (frontmatter and body) by its id.",
)
def get_adr(id: str) -> Adr:
    """Read and return the ADR identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier (plan §9a).

    Returns
    -------
    Adr
        The current on-disk document, freshly re-read and re-parsed.
        Raises :class:`._paths.AdrNotFoundError` if no ADR has this id.
    """
    base_dir = adr_base_dir()
    _, adr = load_by_id(base_dir, id)
    return adr


@mcp.tool(
    name="create_adr",
    title="Create ADR",
    description=(
        "Create a new ADR: assigns a fresh id, derives a filename from the title, "
        "validates, renders, and writes the new document to the ADR base directory."
    ),
)
def create_adr(frontmatter: AdrFrontmatter, body: AdrBody) -> Adr:
    """Create and write a new ADR document.

    A fresh id (``uuid.uuid4()``) is generated and always overwrites
    whatever ``frontmatter.id`` the caller submitted -- the id is
    system-managed and assigned exactly once, at creation time (plan §9a),
    the same "system-owned id" rule :func:`update_frontmatter` applies on
    every subsequent edit. The filename is ``f"{id}-{slug}.md"``, where
    ``slug`` is derived from ``body.title`` (plan §9a).

    Parameters
    ----------
    frontmatter:
        The new document's frontmatter. Any submitted ``id`` is ignored.
    body:
        The new document's body.

    Returns
    -------
    Adr
        The newly created document, with its assigned id in
        ``frontmatter.id``.
    """
    new_id = str(uuid.uuid4())
    final_frontmatter = frontmatter.model_copy(update={"id": new_id})
    filename = f"{new_id}-{slugify(body.title)}.md"

    base_dir = ensure_adr_base_dir()
    new_adr = Adr(frontmatter=final_frontmatter, body=body)
    write_adr(base_dir / filename, new_adr)
    return new_adr


@mcp.tool(
    name="update_frontmatter",
    title="Update ADR Frontmatter",
    description="Whole-object replace of an ADR's frontmatter (plan §3), preserving its existing id.",
)
def update_frontmatter(id: str, frontmatter: AdrFrontmatter) -> Adr:
    """Replace the frontmatter of the ADR identified by ``id``.

    Whole-object, full-replace semantics (plan §3): the submitted
    ``frontmatter`` entirely replaces the current one. The one exception
    is ``id`` itself -- it is always re-injected from the currently
    resolved document, ignoring whatever ``frontmatter.id`` the caller
    submitted, because the id is system-managed and never changes via this
    tool (plan §9a), even though every other frontmatter key follows
    normal full-replace semantics.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    frontmatter:
        The new frontmatter to write (its ``id`` field is ignored).

    Returns
    -------
    Adr
        The updated document. Raises :class:`._paths.AdrNotFoundError` if
        no ADR has this id.
    """
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    new_frontmatter = frontmatter.model_copy(update={"id": adr.frontmatter.id})
    new_adr = adr.model_copy(update={"frontmatter": new_frontmatter})
    write_adr(path, new_adr)
    return new_adr


@mcp.tool(
    name="update_section",
    title="Update ADR Section",
    description="Whole-section replace/delete of one AdrBody field (plan §4).",
)
def update_section(id: str, key: str, value: str) -> Adr:
    """Replace (or, via a deletion sentinel, clear) one whole-section field.

    Delegates to ``models.adr.v1.mutations.update_section`` (plan §4):
    ``value`` being blank/whitespace-only or the literal ``"REMOVE"``
    (case-insensitive) clears the section, unless ``key`` names a
    mandatory field, in which case ``AdrSectionError`` is raised and
    nothing is written. Lets ``AdrSectionError``/``pydantic.ValidationError``
    propagate unmodified -- this tool does not catch or wrap them.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    key:
        An ``AdrBody`` field name, e.g. ``"decision_drivers"``. ``"options"``
        is rejected -- use the ``option_*`` tools instead.
    value:
        The new section text, or a deletion sentinel.

    Returns
    -------
    Adr
        The updated document.
    """
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    new_adr = mutations.update_section(adr, key, value)
    write_adr(path, new_adr)
    return new_adr


@mcp.tool(
    name="set_status",
    title="Set ADR Status",
    description="Narrow convenience wrapper over a frontmatter update for the common status-change case.",
)
def set_status(id: str, status: str, superseded_by: str | None = None) -> Adr:
    """Replace the status of the ADR identified by ``id``.

    Delegates to ``models.adr.v1.mutations.set_status``: when
    ``superseded_by`` is given, ``status`` is composed as
    ``f"superseded by {superseded_by}"`` instead of being used verbatim.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    status:
        The new status. Ignored if ``superseded_by`` is given.
    superseded_by:
        When given, composes the ``"superseded by ..."`` status string.

    Returns
    -------
    Adr
        The updated document.
    """
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    new_adr = mutations.set_status(adr, status, superseded_by)
    write_adr(path, new_adr)
    return new_adr


@mcp.tool(
    name="option_list",
    title="List ADR Options",
    description="Full titles of every current 'Option N: ...' sub-section, in document order (plan §5).",
)
def option_list(id: str) -> list[str]:
    """Return the full titles of every option on the ADR identified by ``id``.

    Read-only -- does not write.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    list[str]
        Full titles, e.g. ``["Option 1: A title"]``, in document order.
    """
    base_dir = adr_base_dir()
    _, adr = load_by_id(base_dir, id)
    return mutations.option_list(adr)


@mcp.tool(
    name="option_create",
    title="Create ADR Option",
    description="Append a new 'Option N: ...' sub-section (plan §5), returning its assigned full title.",
)
def option_create(id: str, partial_title: str, value: str) -> str:
    """Append a new option to the ADR identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    partial_title:
        The ``{title}`` portion after ``"Option {number}: "``.
    value:
        The new option's content.

    Returns
    -------
    str
        The assigned full title, e.g. ``"Option 3: A title"``.
    """
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    new_adr, full_title = mutations.option_create(adr, partial_title, value)
    write_adr(path, new_adr)
    return full_title


@mcp.tool(
    name="option_update",
    title="Update ADR Option",
    description="Full-content replace of the option named full_title (plan §5), returning the new content.",
)
def option_update(id: str, full_title: str, value: str) -> str:
    """Replace the content of one option on the ADR identified by ``id``.

    Lets :class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError`
    propagate if no option matches ``full_title``; nothing is written in
    that case.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    full_title:
        The option's current full title, e.g. ``"Option 1: A title"``.
    value:
        The option's new content.

    Returns
    -------
    str
        The option's new content (i.e. ``value``).
    """
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    new_adr, new_content = mutations.option_update(adr, full_title, value)
    write_adr(path, new_adr)
    return new_content


@mcp.tool(
    name="option_read",
    title="Read ADR Option",
    description="Return the current content of the option named full_title (plan §5).",
)
def option_read(id: str, full_title: str) -> str:
    """Return the content of one option on the ADR identified by ``id``.

    Read-only -- does not write. Lets
    :class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError` propagate
    if no option matches ``full_title``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    full_title:
        The option's full title, e.g. ``"Option 1: A title"``.

    Returns
    -------
    str
        The option's current content.
    """
    base_dir = adr_base_dir()
    _, adr = load_by_id(base_dir, id)
    return mutations.option_read(adr, full_title)


@mcp.tool(
    name="option_delete",
    title="Delete ADR Option",
    description="Remove the option named full_title (plan §5), returning the remaining full titles.",
)
def option_delete(id: str, full_title: str) -> list[str]:
    """Remove one option from the ADR identified by ``id``.

    Does not renumber or reorder the remaining options -- deleting one
    leaves a gap in the numbering (plan §5). Lets
    :class:`~biz.dfch.specmgr.models.adr.AdrOptionNotFoundError` propagate
    if no option matches ``full_title``; nothing is written in that case.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    full_title:
        The option's full title, e.g. ``"Option 1: A title"``.

    Returns
    -------
    list[str]
        The remaining options' full titles, in their original order.
    """
    base_dir = adr_base_dir()
    path, adr = load_by_id(base_dir, id)
    new_adr, remaining = mutations.option_delete(adr, full_title)
    write_adr(path, new_adr)
    return remaining


@mcp.tool(
    name="validate_adr",
    title="Validate ADR",
    description="Re-read and re-parse an ADR by id, letting the models' own Pydantic validators run.",
)
def validate_adr(id: str) -> bool:
    """Validate the ADR identified by ``id``.

    "Validate" is simply letting :class:`Adr`/:class:`AdrBody`/
    :class:`AdrFrontmatter`'s own Pydantic validators run during parsing
    (plan §7): there is no separate validation pass here. Successfully
    constructing the :class:`Adr` *is* the validation, so this function
    only ever returns ``True`` -- it never returns ``False``. Any parse or
    validation failure instead propagates as
    ``AdrParseError``/``pydantic.ValidationError`` (not caught or wrapped
    here), so the MCP layer reports it naturally as a tool error, giving
    the LLM the underlying message to self-correct from.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.

    Returns
    -------
    bool
        Always ``True`` on success.
    """
    base_dir = adr_base_dir()
    load_by_id(base_dir, id)
    return True
