# `biz.dfch.specmgr.feat.tools.create_feat`

``@mcp.tool()`` wrapper: create_feat (Task 2.3, feat-48-feat-id Phase 2).

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

## Functions

### `create_feat(content: 'str', id: 'str | None' = None) -> 'FeatFrontmatter'`

Create and write a new feature document.

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
(``Feature.from_text(format_text(content))``); a structural failure
raises ``AssertionError`` and a field/cross-field failure raises
``pydantic.ValidationError``, both re-raised with domain/tool context
prepended (see Raises below) -- nothing is written in
either case, and neither the base directory nor any new folder is
touched (validation happens before the create lock is even acquired).
A malformed caller-supplied ``id`` is validated in that same
before-any-lock window and raises a bare ``ValueError`` (see Raises
below), also before anything is written.

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
FeatFrontmatter
    The newly created document's frontmatter only (no body), with its
    assigned ``feat-NNN-slug`` id in ``.id``. Use the corresponding
    ``get_feat`` tool to fetch the full document afterward.

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
AssertionError
    A structural failure in ``content``. The message is prefixed with domain/tool/channel
    context (e.g. ``"feat create_feat (body): ..."``) by the shared tool-boundary
    wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
    of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
    Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
    written.

