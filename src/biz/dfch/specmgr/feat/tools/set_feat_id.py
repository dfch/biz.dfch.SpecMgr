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

"""``@mcp.tool()`` wrapper: set_feat_id (Task 3.1, feat-48-feat-id Phase 3).

Renames an existing feature's ``feat-NNN-slug`` id: the containing folder
``<base>/<id>/`` is renamed to ``<base>/<new_id>/`` and the ``README.md``
frontmatter's ``id`` field is rewritten to match, so the document stays
addressable end-to-end (REQ-005). This is the one path that ever changes a
``feat`` document's id after creation -- ``create_feat`` (Phase 2) assigns
the initial id, but has no way to fix it later (e.g. once a GitHub issue
number is known); ``set_feat_id`` is that fix-up path, motivated by the
``feat-NNN-slug`` convention where ``NNN`` is meant to be the GitHub issue
number (ADR e369ee2e-3353-4f92-991c-6367d76d832e).

``new_id`` is validated against the same ``feat-NNN-slug`` shape
``create_feat``'s optional ``id`` parameter uses
(:func:`~biz.dfch.specmgr.general.tools._path_safety.assert_feat_id`,
reused unchanged per this feature's Phase 1 Decision -- see
``.specmgr/feat/feat-48-feat-id/README.md`` Decisions Made), and this
validation runs *before any lock or filesystem access*, mirroring
``create_feat``'s own before-any-lock validation window.

**Lock order** (Phase 1 Decision, REQ-007): :func:`~biz.dfch.specmgr.feat.
tools._lock.feat_create_lock` is acquired first (outermost), then
:func:`~biz.dfch.specmgr.feat.tools._lock.feat_lock` for the *existing* id
nested inside it -- this exact order, never swapped. ``feat_create_lock()``
serializes this tool against a concurrent ``create_feat`` call that might
race on the same ``new_id`` folder path (covering both the existence check
and the actual rename); ``feat_lock(id)`` serializes it against a
concurrent ``update``/``set_status``/``delete`` targeting the same existing
(old) id. No other tool in this codebase acquires ``feat_lock`` before
``feat_create_lock``, so this ordering introduces no inconsistent-ordering
deadlock risk.

The body is preserved byte-for-byte (REQ-006, REQ-008): the on-disk body is
re-read via the frontmatter-stripping
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper *before*
the rename, then written back verbatim under the new frontmatter -- no
reference to the old id anywhere else in the repository is searched for or
touched (REQ-008 is explicitly out of scope for this tool).
"""

from __future__ import annotations

from ...general.tools._path_safety import assert_feat_id
from ...general.tools._splice import body_text
from ...general.tools._timestamps import now_timestamp
from ...server import mcp
from ..models.v1 import FeatDocument, FeatFrontmatter
from ._io import load_by_id
from ._lock import feat_create_lock, feat_lock
from ._paths import README_FILENAME, feat_base_dir
from ._write import write_feat_file


@mcp.tool(
    name="set_feat_id",
    title="Rename feature id",
    description=(
        "Rename an existing feature's id: validates new_id's feat-NNN-slug shape, refuses if "
        "new_id's folder already exists, renames <base>/<id>/ to <base>/<new_id>/, rewrites the "
        "README frontmatter id to new_id, bumps updated, and leaves the body byte-identical. Does "
        "not update or search for references to the old id in any other document."
    ),
)
def set_feat_id(id: str, new_id: str) -> FeatDocument:
    """Rename the feature identified by ``id`` to ``new_id``.

    ``new_id`` is validated against the ``feat-NNN-slug`` shape (via
    :func:`~biz.dfch.specmgr.general.tools._path_safety.assert_feat_id`)
    before any lock or filesystem access is attempted; a malformed
    ``new_id`` raises a bare ``ValueError`` and nothing is touched.

    Once validated, the whole "resolve ``id`` -> refuse if ``new_id``
    already exists -> rename folder -> rewrite frontmatter" sequence runs
    under both :func:`~biz.dfch.specmgr.feat.tools._lock.feat_create_lock`
    (acquired first) and :func:`~biz.dfch.specmgr.feat.tools._lock.feat_lock`
    for ``id`` (nested inside it) -- see this module's docstring for the
    lock-order rationale. ``id`` is resolved via
    :func:`~biz.dfch.specmgr.feat.tools._io.load_by_id`, which raises
    ``FeatNotFoundError`` naturally if ``id`` does not resolve to an
    existing feature -- this tool does not catch or re-raise that error.

    If ``<base>/<new_id>/`` already exists on disk, this raises
    ``FileExistsError`` before any rename happens.

    Only the frontmatter's ``id`` and ``updated`` fields change; every other
    frontmatter field (``type``, ``status``, ``created``, ``version``) and
    the entire body are carried over unchanged. The body is re-read as raw,
    frontmatter-stripped text before the rename and written back verbatim
    afterward, so it stays byte-identical (REQ-006); no other document's
    references to the old id are searched for or updated (REQ-008).

    Parameters
    ----------
    id:
        The feature's current id (the exact containing folder name).
    new_id:
        The new ``feat-NNN-slug`` id to rename ``id`` to.

    Returns
    -------
    FeatDocument
        The renamed document, with ``frontmatter.id == new_id`` and a
        freshly bumped ``frontmatter.updated``.

    Raises
    ------
    ValueError
        ``new_id`` does not match the ``feat-NNN-slug`` shape (raised by
        :func:`~biz.dfch.specmgr.general.tools._path_safety.assert_feat_id`).
        Nothing is touched.
    FeatNotFoundError
        ``id`` does not resolve to an existing feature (propagated from
        :func:`~biz.dfch.specmgr.feat.tools._io.load_by_id`). Nothing is
        touched.
    FileExistsError
        ``<base>/<new_id>/`` already exists on disk. Nothing is renamed or
        rewritten.
    """
    assert_feat_id(new_id)

    with feat_create_lock(), feat_lock(id):
        base_dir = feat_base_dir()
        old_path, existing = load_by_id(base_dir, id)

        new_path = base_dir / new_id / README_FILENAME
        if new_path.parent.exists():
            raise FileExistsError(f"feature {new_id!r} already exists at {new_path.parent}; choose a different new_id")

        raw_body = body_text(old_path)
        old_path.parent.rename(new_path.parent)

        fm_data = existing.frontmatter.model_dump()
        fm_data["id"] = new_id
        fm_data["updated"] = now_timestamp()
        new_frontmatter = FeatFrontmatter(**fm_data)
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=existing.body)

        write_feat_file(new_path, new_frontmatter, raw_body)
    return new_doc
