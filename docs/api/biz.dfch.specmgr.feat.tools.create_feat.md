# `biz.dfch.specmgr.feat.tools.create_feat`

``@mcp.tool()`` wrapper: create_feat (Task 2.3).

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

## Functions

### `_next_feat_number(base_dir: 'Path') -> 'int'`

Return one past the highest existing ``feat-NNN-...`` folder number under ``base_dir``.

Scans only folder *names* (not their content) directly under
``base_dir`` -- a folder that fails to parse as a feature document still
counts toward the ``NNN`` derivation, since its name alone is enough to
reserve that number. Returns ``1`` if ``base_dir`` holds no matching
folder yet.


### `create_feat(content: 'str') -> 'FeatDocument'`

Create and write a new feature document.

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

