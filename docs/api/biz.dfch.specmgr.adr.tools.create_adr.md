# `biz.dfch.specmgr.adr.tools.create_adr`

``@mcp.tool()`` wrapper: create_adr (plan §8, §9a, §10 item 4; Task 3.2).

Thin file-I/O adapter -- writes a brand-new ``.md`` file; there is no
in-memory cache of a parsed :class:`Adr` (plan §7, §9a): the ``.md`` file
itself is always the source of truth.

Unlike the eleven whole-body domains' ``create_<d>`` tools, ``frontmatter``/
``body`` here are already-typed Pydantic models (validated by the MCP SDK's
own parameter parsing *before* this function body ever runs) rather than a
raw ``content: str`` this function validates itself -- so there is little
left for :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors` to
catch at this call site (see the feature README's Decisions Made); it is
still applied around the final :class:`Adr` construction for consistency
with every other domain's ``create_<d>`` (REQ-005).

## Functions

### `create_adr(frontmatter: 'AdrFrontmatter', body: 'AdrBody') -> 'Adr'`

Create and write a new ADR document.

A fresh id (``uuid.uuid4()``) is generated and always overwrites
whatever ``frontmatter.id`` the caller submitted -- the id is
system-managed and assigned exactly once, at creation time (plan §9a),
the same "system-owned id" rule :func:`~.update_frontmatter.update_frontmatter`
applies on every subsequent edit. The filename is ``f"{id}-{slug}.md"``,
where ``slug`` is derived from ``body.title`` (plan §9a).

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

Raises
------
pydantic.ValidationError
    ``frontmatter``/``body`` themselves are validated by the MCP SDK's own parameter
    parsing before this function is even called (not caught here); the message is
    prefixed with domain/tool context by the shared tool-boundary wrapper
    (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`) only for the unlikely
    case of a failure in the final :class:`Adr` construction below.

