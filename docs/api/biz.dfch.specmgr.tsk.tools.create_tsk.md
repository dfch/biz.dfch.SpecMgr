# `biz.dfch.specmgr.tsk.tools.create_tsk`

``@mcp.tool()`` wrapper: create_tsk (Task 3.3).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_tsk`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``req.tools.create_req`` exactly.

**No auto-seeding of ``## Recent Updates``.** ``Task.recent_updates.updates``
requires ``min_length=1`` (see the feature README's Decisions Made): this
tool does *not* inject a "Created" entry on the caller's behalf -- it simply
validates whatever ``content`` is submitted via
``Task.from_text(format_text(content))``, exactly like ``create_req`` never
special-cases any of its own mandatory sections. A caller whose submitted
body lacks a ``## Recent Updates`` section with at least one ``### `` entry
gets a validation failure, the same way an empty ``items`` checklist would.
It is the packaged example/template files and the ``create_task`` prompt's
own instructional text that demonstrate/instruct seeding a first entry (e.g.
``### Created``) so a caller drafting new content naturally satisfies the
constraint.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.

## Functions

### `create_tsk(content: 'str') -> 'TskDocument'`

Create and write a new task list document.

``content`` is body markdown only (the ``Task`` H1 and its sections) --
it must not carry a YAML frontmatter block. The entire frontmatter is
built by this tool: a fresh id (``uuid.uuid4()``), ``type="tsk"``,
``status="draft"`` (always, never caller-supplied on create),
``created``/``updated`` both set to the current timestamp, and
``version`` set to the current ``models.md`` schema version.

``content`` is validated by constructing a
:class:`~biz.dfch.specmgr.tsk.models.v1.Task` from it
(``Task.from_text(format_text(content))``); a structural failure raises
``AssertionError`` and a field/cross-field failure raises
``pydantic.ValidationError``, both re-raised with domain/tool context
prepended (see Raises below) -- nothing is written in
either case. In particular, a ``content`` whose ``## Recent Updates``
section has zero ``### `` entries fails this same way
(``RecentUpdates.updates`` requires ``min_length=1``) -- this tool does
not auto-seed a first entry; see this module's own docstring.

No body rendering is ever needed: the caller's own already-validated
``content`` is persisted byte-for-byte, exactly as submitted; only the
small, code-constructed frontmatter YAML block is (re)generated.

Parameters
----------
content:
    The new document's body markdown, with no frontmatter block.

Returns
-------
TskDocument
    The newly created document, with its assigned id in
    ``frontmatter.id``.

Raises
------
AssertionError
    A structural failure in ``content``. The message is prefixed with domain/tool/channel
    context (e.g. ``"tsk create_tsk (body): ..."``) by the shared tool-boundary
    wrapper (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top
    of the engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
    Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in ``content`` -- similarly prefixed. Nothing is
    written.

