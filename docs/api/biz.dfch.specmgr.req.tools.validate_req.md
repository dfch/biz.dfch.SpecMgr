# `biz.dfch.specmgr.req.tools.validate_req`

``@mcp.tool()`` wrapper: validate_req (Task 3.16).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_req`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the
requirement base directory or resolving an id. This lets a caller check a
draft before ever calling ``create_req`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here.

## Functions

### `validate_req(content: 'str', full: 'bool' = False) -> 'bool'`

Validate ``content`` as requirement markdown, without reading or writing any file.

"Validate" means letting :class:`~biz.dfch.specmgr.req.models.v1.Requirement`/
:class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter`/
:class:`~biz.dfch.specmgr.req.models.v1.ReqDocument`'s own Pydantic
validators run during parsing -- there is no separate validation pass.
Successfully constructing the model *is* the validation, so this
function only ever returns ``True``; any parse/validation failure
instead propagates as ``AssertionError``/``pydantic.ValidationError``,
exactly as ``create_req`` and the generic ``update`` tool do.

Whether ``content`` carries a YAML frontmatter block is detected via
``frontmatter.loads(content).metadata`` (non-empty means "has
frontmatter") -- the same ``python-frontmatter`` library every parser in
this codebase already depends on, rather than a hand-rolled
``startswith("---")`` heuristic.

Parameters
----------
content:
    The requirement markdown to validate.
full:
    ``False`` (default): ``content`` must be body markdown only (the
    shape ``create_req`` and the generic ``update`` tool accept) --
    raises ``ValueError``
    if a frontmatter block is found instead. ``True``: ``content`` must
    be a complete document, frontmatter and body together (the shape
    ``parse_req`` expects for an on-disk file) -- raises the symmetric
    ``ValueError`` if no frontmatter block is found.

Returns
-------
bool
    Always ``True`` on success.

