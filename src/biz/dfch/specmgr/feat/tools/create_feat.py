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

"""``@mcp.tool()`` wrapper: create_feat (Task 2.3).

Unlike every other domain's ``create_<d>`` (a fresh server-generated UUID,
always assignable without coordinating with any other in-flight create),
``create_feat`` derives its id (``feat-NNN-slug``) by scanning existing
``feat-*`` folder names for the highest ``NNN`` and adding one, under the
**global** :func:`~biz.dfch.specmgr.feat.tools._lock.feat_create_lock` --
see that module's docstring for why a global (not per-id) lock is needed
here. ``content`` is body markdown only (no frontmatter block), same shape
as ``create_dec``/``create_gol``: the caller's own already-validated body is
persisted byte-for-byte, and only the small, code-constructed frontmatter
YAML block is (re)generated.

``created``/``updated`` use the same shared date+time timestamp format
(``general.tools._timestamps.now_timestamp()``) as every other whole-body
domain's ``create_<d>`` -- an earlier, deliberate ``feat``-only divergence
(plain ``YYYY-MM-DD`` dates, matching the 17 pre-existing hand-authored
feature files) was reversed for cross-domain consistency; see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes ("Frontmatter") and
Decisions Made.
"""

from __future__ import annotations

from pathlib import Path

from ...general.tools._timestamps import now_timestamp
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import FeatDocument, FeatFrontmatter, Feature
from ._lock import feat_create_lock
from ._paths import FEAT_FOLDER_PATTERN, README_FILENAME, ensure_feat_base_dir, feature_title, slugify
from ._write import write_feat_file


@mcp.tool(
    name="create_feat",
    title="Create feature",
    description=(
        "Create a new feature: assigns a fresh id, derives a filename from the body's H1 title, "
        "validates the submitted body-only content, and writes the new document to the feature base "
        "directory."
    ),
)
def create_feat(content: str) -> FeatDocument:
    """Create and write a new feature document.

    ``content`` is body markdown only (the ``Feature`` H1 and its sections)
    -- it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh ``feat-NNN-slug`` id (see this module's
    docstring), ``type="feat"``, ``status="planning"`` (always, never
    caller-supplied on create -- `feat`'s own default lifecycle state),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.feat.models.v1.Feature` from it
    (``Feature.from_text(format_text(content))``); a structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both re-raised with domain/tool context
    prepended (see Raises below) -- nothing is written in
    either case, and neither the base directory nor any new folder is
    touched (validation happens before the create lock is even acquired).

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    FeatDocument
        The newly created document, with its assigned ``feat-NNN-slug`` id
        in ``frontmatter.id``.

    Raises
    ------
    AssertionError
        A structural failure in ``content``. The message is prefixed with domain/tool/channel
        context (e.g. ``"feat create_feat (body): ..."``) by the shared tool-boundary
        wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
        of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
        Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
        written.
    """
    with wrap_tool_errors(domain="feat", tool="create_feat", channel=BODY_CHANNEL):
        body = Feature.from_text(format_text(content))
    slug = slugify(feature_title(body.text))

    with feat_create_lock():
        base_dir = ensure_feat_base_dir()
        new_id = f"feat-{_next_feat_number(base_dir)}-{slug}"

        now = now_timestamp()
        new_frontmatter = FeatFrontmatter(
            id=new_id,
            type="feat",
            status="planning",
            created=now,
            updated=now,
            version=CURRENT_SCHEMA_VERSION,
        )
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)

        write_feat_file(base_dir / new_id / README_FILENAME, new_frontmatter, content)
    return new_doc


def _next_feat_number(base_dir: Path) -> int:
    """Return one past the highest existing ``feat-NNN-...`` folder number under ``base_dir``.

    Scans only folder *names* (not their content) directly under
    ``base_dir`` -- a folder that fails to parse as a feature document still
    counts toward the ``NNN`` derivation, since its name alone is enough to
    reserve that number. Returns ``1`` if ``base_dir`` holds no matching
    folder yet.
    """
    assert isinstance(base_dir, Path), type(base_dir)

    existing = [
        int(match.group(1))
        for entry in base_dir.iterdir()
        if entry.is_dir() and (match := FEAT_FOLDER_PATTERN.match(entry.name))
    ]
    result = max(existing, default=0) + 1
    return result
