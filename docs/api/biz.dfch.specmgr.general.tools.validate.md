# `biz.dfch.specmgr.general.tools.validate`

``@mcp.tool()`` wrapper: validate (feat-81-83-validation, Phase 2).

The generic, cross-domain, type-dispatched dry-run validation tool for the
twelve whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``). It dispatches on the explicit ``type``
parameter to a private per-domain adapter (``_validate_<d>``), each a
verbatim port of the deleted ``validate_<d>`` tool's body: ``has_frontmatter``
detection via ``bool(frontmatter.loads(content).metadata)``, then either
``<Model>.from_text(format_text(content))`` (``full=False``, body-only path)
or ``parse_<d>(content)`` (``full=True``, full-document path), wrapped in
``wrap_tool_errors(domain=..., tool="validate", channel=...)`` for message
enrichment (feat-27-validation) -- same as every deleted per-domain tool,
except the generic tool's own name (``"validate"``) is now the ``tool=``
label, mirroring ``update``'s/``set_status``'s own generic-tool-name
convention rather than the retired per-domain tool name.

Unlike ``update``/``set_status``/``set_classification``/``delete``,
``validate`` is disk-free and id-free (a content-based dry run) for all
twelve domains -- no lock, no filesystem access, no id resolution is
needed, exactly like every one of today's per-domain ``validate_<d>`` tools
already was.

**Non-raising contract (REQ-004)**: unlike every other generic tool in this
package, ``validate`` never raises for a content-validation failure. The
public :func:`validate` wraps each adapter call in
``try``/``except (AssertionError, pydantic.ValidationError, yaml.YAMLError)``
and turns a caught exception into
``{"valid": False, "errors": [{"message": str(exception)}]}`` instead of
letting it propagate -- reusing feat-27-validation's already-enriched
message verbatim as the sole error entry's ``message``. A ``full``/
content-shape mismatch (``full=True`` with body-only content, or
``full=False`` with a complete document) is a caller-usage error, not a
content-validation failure, and is **not** in that catch set: it is a bare
``ValueError`` raised by the adapter itself, before the wrapped parse call
ever runs, and it still propagates through :func:`validate` unchanged, same
as it always did through the retired per-domain tools. An unsupported
``type`` (including ``"adr"``) is likewise a ``ValueError``, raised before
any adapter runs at all.

ADR is deliberately *not* a ``type`` here, mirroring ``update``'s/
``set_classification``'s/``delete``'s own exclusion: ``validate_adr`` is
structurally the odd one out among the (previously) thirteen
``validate_<d>`` tools -- ``id``-based and disk-touching, with no ``full``
parameter, and its own structural-failure channel is ``AdrParseError``
(a ``ValueError`` subclass) rather than ``AssertionError`` -- so it is kept
as its own standalone tool, unchanged, and excluded from this
consolidation. See ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6, which extends
ADR 36905d5b-8057-4294-8665-c7eed5534db0's dispatch-only convention
(previously covering only mutation-adjacent tools) to this read-only/
dry-run tool category.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow.

## Functions

### `_validate_dec(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as decision markdown -- verbatim port of the retired ``validate_dec``.

See :func:`_validate_req` for the shared semantics.


### `_validate_feat(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as feature markdown -- verbatim port of the retired ``validate_feat``.

See :func:`_validate_req` for the shared semantics. Note that
``full=True`` does **not** check the "frontmatter ``id`` equals
containing folder's name" invariant -- that is enforced at the
addressing/tool layer (``feat.tools._paths``), not here, since this
disk-free tool has no path/folder-name to check against.


### `_validate_gol(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as goal markdown -- verbatim port of the retired ``validate_gol``.

See :func:`_validate_req` for the shared semantics.


### `_validate_prb(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as problem statement markdown -- verbatim port of the retired ``validate_prb``.

See :func:`_validate_req` for the shared semantics.


### `_validate_qa(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as QA markdown -- verbatim port of the retired ``validate_qa``.

See :func:`_validate_req` for the shared semantics.


### `_validate_req(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as requirement markdown -- verbatim port of the retired ``validate_req``.

See the module docstring for the shared ``has_frontmatter``/``full``
semantics every adapter in this module follows.


### `_validate_rsk(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as risk markdown -- verbatim port of the retired ``validate_rsk``.

See :func:`_validate_req` for the shared semantics.


### `_validate_sop(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as SOP markdown -- verbatim port of the retired ``validate_sop``.

See :func:`_validate_req` for the shared semantics.


### `_validate_sysrs(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as System Requirements Specification markdown.

Verbatim port of the retired ``validate_sysrs`` -- see
:func:`_validate_req` for the shared semantics.


### `_validate_tsk(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as task list markdown -- verbatim port of the retired ``validate_tsk``.

See :func:`_validate_req` for the shared semantics.


### `_validate_uc(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as use case markdown -- verbatim port of the retired ``validate_uc``.

See :func:`_validate_req` for the shared semantics.


### `_validate_vcr(content: 'str', full: 'bool') -> 'None'`

Validate ``content`` as verification case record markdown -- verbatim port of the retired ``validate_vcr``.

See :func:`_validate_req` for the shared semantics.


### `validate(type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'sop', 'feat', 'vcr', 'sysrs']", content: 'str', full: 'bool' = False) -> 'ValidateResult'`

Validate ``content`` as markdown of the given document ``type``, without reading or writing any file.

Cross-domain generic for every whole-body document type
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``); dispatches on ``type`` to the domain's own
private adapter (same ``has_frontmatter`` detection, same
``full=True``/``full=False`` body-only-vs-complete-document semantics,
same ``wrap_tool_errors`` message enrichment as every retired
per-domain ``validate_<d>`` tool). "Validate" means letting the
domain's own Pydantic model/document validators run during parsing --
there is no separate validation pass; successfully constructing the
model *is* the validation.

Unlike every other generic tool in ``general.tools``, ``validate``
never raises for a content-validation failure (REQ-004): a caught
``AssertionError``, ``pydantic.ValidationError``, or ``yaml.YAMLError``
(``full=True`` only, malformed frontmatter YAML) is turned into
``ValidateResult(valid=False, errors=[ValidationErrorEntry(message=str(exception))])``
instead of propagating -- reusing feat-27-validation's already-enriched
message (field path, line reference, cause/fix hint, plus this tool's
own domain/``validate``/channel prefix) verbatim as the sole error
entry's ``message``.

A ``full``/content-shape mismatch is a caller-usage error, not a
content-validation failure, and is **not** caught: ``content`` must be
body markdown only when ``full=False`` (the shape ``create_<d>`` and
the generic ``update`` tool accept), or a complete document
(frontmatter and body together) when ``full=True`` -- passing the
wrong shape raises ``ValueError`` before the domain's own parse/
validation logic ever runs. An unsupported ``type`` (including
``"adr"``, which has its own standalone ``validate_adr`` tool) is
likewise a ``ValueError``, raised before any adapter is dispatched.

Parameters
----------
type:
    The document type / domain: one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
    ``vcr``, ``sysrs``.
content:
    The markdown to validate.
full:
    ``False`` (default): ``content`` must be body markdown only.
    ``True``: ``content`` must be a complete document (frontmatter and
    body together).

Returns
-------
ValidateResult
    ``{valid: True, errors: []}`` on success;
    ``{valid: False, errors: [{message: "..."}]}`` on a caught
    content-validation failure.

Raises
------
ValueError
    ``type`` is not one of the twelve supported domains (including
    ``"adr"``), or ``full`` does not match whether ``content`` carries
    a frontmatter block.

