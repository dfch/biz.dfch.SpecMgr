# `biz.dfch.specmgr.prb.tools.validate_prb`

``@mcp.tool()`` wrapper: validate_prb (Task 3.7).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_prb`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the problem
statement base directory or resolving an id. This lets a caller check a
draft before ever calling ``create_prb`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here.
Mirrors ``tsk.tools.validate_tsk``/``qa.tools.validate_qa`` exactly.

## Functions

### `validate_prb(content: 'str', full: 'bool' = False) -> 'bool'`

Validate ``content`` as problem statement markdown, without reading or writing any file.

"Validate" means letting :class:`~biz.dfch.specmgr.prb.models.v1.Prb`/
:class:`~biz.dfch.specmgr.prb.models.v1.PrbFrontmatter`/
:class:`~biz.dfch.specmgr.prb.models.v1.PrbDocument`'s own Pydantic
validators run during parsing -- there is no separate validation pass.
Successfully constructing the model *is* the validation, so this
function only ever returns ``True``; any parse/validation failure
instead propagates as ``AssertionError``/``pydantic.ValidationError``,
exactly as ``create_prb`` and the generic ``update`` tool do.

Whether ``content`` carries a YAML frontmatter block is detected via
``frontmatter.loads(content).metadata`` (non-empty means "has
frontmatter") -- the same ``python-frontmatter`` library every parser in
this codebase already depends on, rather than a hand-rolled
``startswith("---")`` heuristic.

Parameters
----------
content:
    The problem statement markdown to validate.
full:
    ``False`` (default): ``content`` must be body markdown only (the
    shape ``create_prb`` and the generic ``update`` tool accept) --
    raises ``ValueError``
    if a frontmatter block is found instead. ``True``: ``content`` must
    be a complete document, frontmatter and body together (the shape
    ``parse_prb`` expects for an on-disk file) -- raises the symmetric
    ``ValueError`` if no frontmatter block is found.

Returns
-------
bool
    Always ``True`` on success.

Raises
------
ValueError
    ``full`` does not match whether ``content`` carries a frontmatter block (see above).
AssertionError
    A structural failure in ``content``. The message is prefixed with domain/tool/channel
    context by the shared tool-boundary wrapper
    (:func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`), layered on top of the
    engine's own field-path/line/snippet enrichment (feat-27-validation Phases 1/2).
pydantic.ValidationError
    A field/cross-field validation failure in ``content`` -- similarly prefixed.
yaml.YAMLError
    ``full=True`` only: malformed frontmatter YAML -- similarly prefixed.

