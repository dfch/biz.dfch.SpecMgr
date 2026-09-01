# `biz.dfch.specmgr.feat.tools.validate_feat`

``@mcp.tool()`` wrapper: validate_feat (Task 2.3).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_feat`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the feature
base directory or resolving an id. This lets a caller check a draft before
ever calling ``create_feat`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here. Mirrors ``validate_dec`` file-for-file.

## Functions

### `validate_feat(content: 'str', full: 'bool' = False) -> 'bool'`

Validate ``content`` as feature markdown, without reading or writing any file.

"Validate" means letting :class:`~biz.dfch.specmgr.feat.models.v1.Feature`/
:class:`~biz.dfch.specmgr.feat.models.v1.FeatFrontmatter`/
:class:`~biz.dfch.specmgr.feat.models.v1.FeatDocument`'s own Pydantic
validators run during parsing -- there is no separate validation pass.
Successfully constructing the model *is* the validation, so this
function only ever returns ``True``; any parse/validation failure
instead propagates as ``AssertionError``/``pydantic.ValidationError``,
exactly as ``create_feat`` and the generic ``update`` tool do.

Whether ``content`` carries a YAML frontmatter block is detected via
``frontmatter.loads(content).metadata`` (non-empty means "has
frontmatter") -- the same ``python-frontmatter`` library every parser in
this codebase already depends on, rather than a hand-rolled
``startswith("---")`` heuristic.

Parameters
----------
content:
    The feature markdown to validate.
full:
    ``False`` (default): ``content`` must be body markdown only (the
    shape ``create_feat`` and the generic ``update`` tool accept) --
    raises ``ValueError``
    if a frontmatter block is found instead. ``True``: ``content`` must
    be a complete document, frontmatter and body together (the shape
    ``parse_feat`` expects for an on-disk file) -- raises the symmetric
    ``ValueError`` if no frontmatter block is found. Note that
    ``full=True`` does **not** check the "frontmatter ``id`` equals
    containing folder's name" invariant -- that is enforced at the
    addressing/tool layer (``feat.tools._paths``), not here, since this
    tool has no path/folder-name to check against.

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

