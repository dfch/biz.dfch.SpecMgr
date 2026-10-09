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

"""``@mcp.tool()`` wrapper: create_feat (Task 2.3, feat-48-feat-id Phase 2).

Unlike every other domain's ``create_<d>`` (a fresh server-generated UUID,
always assignable without coordinating with any other in-flight create),
``create_feat``'s id is either a caller-chosen ``feat-NNN-slug`` (validated
against that shape via
:func:`~biz.dfch.specmgr.general.tools._path_safety.assert_feat_id` before
any lock/filesystem access) or, when ``id`` is omitted, defaults to
``feat-0-<slug-from-title>`` -- there is no max+1 auto-generation fallback
(feat-48-feat-id, REQ-001/REQ-002/REQ-004). Either way, a pre-write
existence check for the resulting id/folder runs under the **global**
:func:`~biz.dfch.specmgr.feat.tools._lock.feat_create_lock` (REQ-003) --
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

from ...general.models import ValidateResult, ValidationErrorEntry
from ...general.tools._path_safety import assert_feat_id
from ...general.tools._timestamps import now_timestamp
from ...general.tools.validate import _CAUGHT_EXCEPTIONS, _MAX_VALIDATE_ERROR_CHARS
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text, snippet
from ...server import mcp
from ..models.v1 import FeatFrontmatter, Feature
from ._cache import read_feat, read_feat_dirty
from ._lock import feat_create_lock
from ._paths import README_FILENAME, ensure_feat_base_dir, feature_title, slugify
from ._write import write_feat_file


@mcp.tool(
    name="create_feat",
    title="Create feature",
    description=(
        "Create a new feature: assigns a fresh id (caller-chosen via the optional 'id' parameter, "
        "or defaulted to feat-0-<slug-from-title> when omitted -- no max+1 auto-generation), derives "
        "a filename from the body's H1 title, validates the submitted body-only content, and writes "
        "the new document to the feature base directory. A content-validation failure of the "
        "submitted body returns a non-raising `ValidateResult` (`valid=False`, a single "
        "`errors[].message` capped at 300 chars as the generic `validate` tool caps it, feat-110) "
        "instead of raising `AssertionError`/`pydantic.ValidationError` (ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e, "
        "GitHub issue #204 -- case 5 of the ADR 519d1206 non-raising-structured-result workaround "
        "chain); nothing is written in that case. Content validation runs BEFORE the id-shape "
        "`ValueError` and already-existing-id/folder `FileExistsError` guards, so a compound failure "
        "(invalid content + a malformed or already-existing id) returns the `ValidateResult` and the "
        "guard never runs in that call; each guard still raises whenever the content is valid. "
        "Returns the newly created document's frontmatter only (no body); use the corresponding "
        "`get_feat` tool to fetch the full document afterward."
    ),
)
def create_feat(content: str, id: str | None = None) -> FeatFrontmatter | ValidateResult:
    """Create and write a new feature document.

    ``content`` is body markdown only (the ``Feature`` H1 and its sections)
    -- it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: ``type="feat"``, ``status="planning"`` (always,
    never caller-supplied on create -- `feat`'s own default lifecycle
    state), ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    The document's ``feat-NNN-slug`` id (see this module's docstring) comes
    from one of two sources:

    - ``id`` given: used verbatim as the folder name/frontmatter id, after
      validation against the ``feat-NNN-slug`` shape (via
      :func:`~biz.dfch.specmgr.general.tools._path_safety.assert_feat_id`).
      The slug derived from ``content``'s own title plays no role in this
      branch.
    - ``id`` omitted: defaults to ``feat-0-<slug>``, where ``<slug>`` is
      derived from ``content``'s ``Feature: ...`` H1 title. There is no
      max+1 auto-generation fallback -- every default-id create targets
      ``feat-0-...`` regardless of what other ``feat-*`` folders already
      exist.

    Either way, a pre-write existence check runs before
    :func:`~biz.dfch.specmgr.feat.tools._write.write_feat_file` is called:
    if the resulting id's folder already exists on disk, this raises
    ``FileExistsError`` and nothing is written (see Raises below).

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.feat.models.v1.Feature` from it
    (``Feature.from_text(format_text(content))``). A structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError`` -- but this tool catches both
    (feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
    case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
    structured-result workaround chain) and returns the enriched message
    (domain/tool/channel context prepended by the shared tool-boundary
    wrapper, :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`,
    on top of the engine's own field-path/line/snippet enrichment,
    feat-27-validation Phases 1/2) as the non-raising
    ``ValidateResult(valid=False, ...)`` (see Returns below) instead --
    nothing is written in that case, and neither the base directory nor
    any new folder is touched (validation happens before the create lock
    is even acquired). A malformed caller-supplied ``id`` is validated in
    that same before-any-lock window and raises a bare ``ValueError``
    (see Raises below), also before anything is written.

    Compound-failure precedence (feat-204-create-error, REQ-003 -- ADR
    f14f125e's item 3): the content validation above runs *before* both
    id guards in the existing execution order, and this feature does not
    re-order that. Consequently, a compound failure (invalid ``content``
    *plus* a malformed or already-existing ``id``/folder) surfaces the
    content error first: the tool returns
    ``ValidateResult(valid=False, ...)`` and the guard never runs in that
    call -- "first-in-execution-order wins." Each guard still raises
    unchanged whenever the content is valid (malformed ``id`` shape ->
    ``ValueError``; valid content + already-existing ``id``/folder ->
    ``FileExistsError``).

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.
    id:
        An optional, caller-chosen ``feat-NNN-slug`` id. When given, it is
        validated against that shape and used verbatim (no slug
        derivation). When omitted (the default), the id defaults to
        ``feat-0-<slug-from-title>``.

    Returns
    -------
    FeatFrontmatter | ValidateResult
        The newly created document's frontmatter only (no body), with its
        assigned ``feat-NNN-slug`` id in ``.id``. Use the corresponding
        ``get_feat`` tool to fetch the full document afterward. On a
        content-validation failure of ``content``, a non-raising
        :class:`~biz.dfch.specmgr.general.models.ValidateResult`
        (``valid=False``) with exactly one ``errors`` entry whose
        ``message`` is the enriched exception text capped at 300 chars
        exactly as the generic ``validate`` tool caps it (feat-110, via
        :func:`~biz.dfch.specmgr.models.md._markdown.snippet`), instead of
        ``AssertionError``/``pydantic.ValidationError`` -- nothing is written
        in that case (feat-204-create-error, ADR
        f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case 5 of the ADR
        519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result
        workaround chain); because content validation runs before both id
        guards, a compound failure (invalid ``content`` plus a malformed or
        already-existing ``id``/folder) returns this ``ValidateResult`` and
        the guard never runs in that call (see the Compound-failure
        precedence paragraph above).

    Raises
    ------
    ValueError
        ``id`` was given but does not match the ``feat-NNN-slug`` shape
        (raised by
        :func:`~biz.dfch.specmgr.general.tools._path_safety.assert_feat_id`).
        Nothing is written.
    FileExistsError
        The resulting id's folder (caller-supplied or defaulted) already
        exists on disk. Nothing is written.
    """
    try:
        with wrap_tool_errors(domain="feat", tool="create_feat", channel=BODY_CHANNEL):
            body = Feature.from_text(format_text(content))
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])
    slug = slugify(feature_title(body.text))

    if id is not None:
        assert_feat_id(id)

    with feat_create_lock():
        base_dir = ensure_feat_base_dir()
        new_id = id if id is not None else f"feat-0-{slug}"

        target_path = base_dir / new_id / README_FILENAME
        if target_path.parent.exists():
            raise FileExistsError(
                f"feature {new_id!r} already exists at {target_path.parent}; choose a different id, "
                f"or use the generic update tool (id, type='feat', content) to modify the existing document"
            )

        now = now_timestamp()
        new_frontmatter = FeatFrontmatter(
            id=new_id,
            type="feat",
            status="planning",
            created=now,
            updated=now,
            version=CURRENT_SCHEMA_VERSION,
        )
        write_feat_file(target_path, new_frontmatter, content)
        read_feat(
            target_path
        )  # warm the clean cache with this write's own validated content (feat-107-doc-cache Phase 4, REQ-003)
        read_feat_dirty(target_path)  # warm the dirty cache too (feat-187-list-feat-timeout, Task 110.130)
    return new_frontmatter
