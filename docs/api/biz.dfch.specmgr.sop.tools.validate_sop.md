# `biz.dfch.specmgr.sop.tools.validate_sop`

``@mcp.tool()`` wrapper: validate_sop (Task 2.2).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_sop`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the SOP
base directory or resolving an id. This lets a caller check a draft before
ever calling ``create_sop`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here.

## Functions

### `validate_sop(content: 'str', full: 'bool' = False) -> 'bool'`

Validate ``content`` as SOP markdown, without reading or writing any file.

"Validate" means letting :class:`~biz.dfch.specmgr.sop.models.v1.Sop`/
:class:`~biz.dfch.specmgr.sop.models.v1.SopFrontmatter`/
:class:`~biz.dfch.specmgr.sop.models.v1.SopDocument`'s own Pydantic
validators run during parsing -- there is no separate validation pass.
Successfully constructing the model *is* the validation, so this
function only ever returns ``True``; any parse/validation failure
instead propagates as ``AssertionError``/``pydantic.ValidationError``,
exactly as ``create_sop`` and the generic ``update`` tool do.

Whether ``content`` carries a YAML frontmatter block is detected via
``frontmatter.loads(content).metadata`` (non-empty means "has
frontmatter") -- the same ``python-frontmatter`` library every parser in
this codebase already depends on, rather than a hand-rolled
``startswith("---")`` heuristic.

Parameters
----------
content:
    The SOP markdown to validate.
full:
    ``False`` (default): ``content`` must be body markdown only (the
    shape ``create_sop`` and the generic ``update`` tool accept) --
    raises ``ValueError``
    if a frontmatter block is found instead. ``True``: ``content`` must
    be a complete document, frontmatter and body together (the shape
    ``parse_sop`` expects for an on-disk file) -- raises the symmetric
    ``ValueError`` if no frontmatter block is found.

Returns
-------
bool
    Always ``True`` on success.

