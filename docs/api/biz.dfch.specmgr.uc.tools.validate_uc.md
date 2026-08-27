# `biz.dfch.specmgr.uc.tools.validate_uc`

``@mcp.tool()`` wrapper: validate_uc (Task 3.1.5).

Mirrors ``req.tools.validate_req``: a **disk-free, id-free dry run**. It
validates a submitted ``content`` string directly, without ever touching the
use-case base directory or resolving an id. This lets a caller check a draft
before ever calling ``create_uc`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here.

## Functions

### `validate_uc(content: 'str', full: 'bool' = False) -> 'bool'`

Validate ``content`` as use-case markdown, without reading or writing any file.

"Validate" means letting :class:`~biz.dfch.specmgr.uc.models.v2.UseCase`/
:class:`~biz.dfch.specmgr.uc.models.v2.UcFrontmatter`/
:class:`~biz.dfch.specmgr.uc.models.v2.UcDocument`'s own Pydantic
validators run during parsing -- there is no separate validation pass.
Successfully constructing the model *is* the validation, so this
function only ever returns ``True``; any parse/validation failure
instead propagates as ``AssertionError``/``pydantic.ValidationError``,
exactly as ``create_uc`` and the generic ``update`` tool do.

Whether ``content`` carries a YAML frontmatter block is detected via
``frontmatter.loads(content).metadata`` (non-empty means "has
frontmatter") -- the same ``python-frontmatter`` library every parser in
this codebase already depends on, rather than a hand-rolled
``startswith("---")`` heuristic.

Parameters
----------
content:
    The use-case markdown to validate.
full:
    ``False`` (default): ``content`` must be body markdown only (the
    shape ``create_uc`` and the generic ``update`` tool accept) --
    raises ``ValueError``
    if a frontmatter block is found instead. ``True``: ``content`` must
    be a complete document, frontmatter and body together (the shape
    ``parse_uc`` expects for an on-disk file) -- raises the symmetric
    ``ValueError`` if no frontmatter block is found.

Returns
-------
bool
    Always ``True`` on success.

