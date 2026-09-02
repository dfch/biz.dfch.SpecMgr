# `biz.dfch.specmgr.models.md._errors`

Shared tool-boundary error enrichment (feat-27-validation Phase 3, Task 3.1).

Every ``parse_<d>``/``create_<d>``/``validate_<d>`` ``@mcp.tool()`` wrapper, plus the generic
``update``/``set_status`` tools' per-domain adapters, calls one of a small number of
"validating" functions (a domain body's ``from_text``, a domain parser's ``parse_<d>``, or a
domain frontmatter's own constructor) that can raise one of the two channels REQ-006 fixes in
place -- ``AssertionError`` (structural) or ``pydantic.ValidationError`` (field/cross-field) --
or, for ``parse_<d>``/``validate_<d>(full=True)``, additionally ``yaml.YAMLError`` (malformed
frontmatter YAML). Phases 1/2 already enrich the *engine* message itself (field path, line
number, snippet, frontmatter block naming); this module adds the one remaining layer REQ-005
asks for: naming *which tool, on which domain* raised it, so the message the MCP SDK forwards
to the caller (``str(e)`` -- see the feature README's Overview) is self-contained without the
caller needing to already know which tool it called.

:func:`wrap_tool_errors` is the single shared mechanism every touched tool wraps its own
validating call with -- a context manager (chosen over a decorator since most tools need to
wrap only *one* inner call, not their entire body, e.g. ``validate_<d>`` has an early
``ValueError`` guard before the wrapped call that must NOT gain this prefix)::

    with wrap_tool_errors(domain="tsk", tool="create_tsk", channel=BODY_CHANNEL):
        body = Task.from_text(format_text(content))

On a caught exception it re-raises the exact same runtime exception type (REQ-006) with an
enriched message -- reusing the same two techniques already established by Phases 1/2:
message-only reconstruction for ``AssertionError`` (and any domain-specific structural error
type opted into via ``also_catch``, e.g. ADR's own :class:`~biz.dfch.specmgr.models.adr.v1.
parser.AdrParseError`, a plain ``ValueError`` subclass with the same single-message
constructor shape), and ``pydantic_core.ValidationError.from_exception_data`` (the same
construction Phase 2's ``models/md/_frontmatter_parse.py`` uses) for ``pydantic.
ValidationError``. ``yaml.YAMLError`` is reconstructed the same ``yaml.error.Mark``-preserving
way Phase 2's ``enrich_frontmatter_yaml_error`` does, except here only the ``context`` field
(shown *first* in ``MarkedYAMLError.__str__``) is prefixed -- the marks themselves were already
remapped to document-relative coordinates by Phase 2, so this module never touches them again.

``channel`` is an optional, free-text hint for what "vs. body" is knowable *before* the wrapped
call runs (see the module-level ``BODY_CHANNEL``/``FRONTMATTER_CHANNEL`` constants): a
``create_<d>``/whole-body-or-range-mode ``update`` call only ever validates body-only content,
so it always passes ``BODY_CHANNEL``; ``set_status``'s frontmatter reconstruction always passes
``FRONTMATTER_CHANNEL``. A ``parse_<d>`` call (or ``validate_<d>(full=True)``, which delegates
to ``parse_<d>``) cannot know in advance which of the three channels will actually fire, so it
passes ``channel=None`` -- the underlying, already-enriched message self-identifies "the
frontmatter block" vs. a field path regardless (Phases 1/2), so nothing is lost.

## Functions

### `_context_label(domain: 'str', tool: 'str', channel: 'str | None') -> 'str'`

Build the ``"{domain} {tool}"`` (optionally ``" ({channel})"``) prefix label.


### `_reraise_assertion_like(error: 'Exception', label: 'str') -> 'Exception'`

Return a same-type, message-only reconstruction of ``error`` prefixed with ``label``.

Used for ``AssertionError`` and any domain-specific structural exception type opted into
via ``also_catch`` (e.g. ADR's ``AdrParseError``) -- both take a single message argument,
so ``type(error)(message)`` is a faithful, same-type reconstruction (REQ-006).


### `_reraise_validation_error(error: 'ValidationError', label: 'str') -> 'ValidationError'`

Return a same-type reconstruction of ``error`` with every per-field message prefixed
with ``label`` (REQ-006 -- the exact same technique as ``_frontmatter_parse.py``'s own
``enrich_frontmatter_validation_error``, generalized to a plain prefix instead of a
domain/field/line composition, since by this point in the call stack that composition --
when applicable -- has already happened once, at the parser boundary).


### `_reraise_yaml_error(error: 'yaml.YAMLError', label: 'str') -> 'yaml.YAMLError'`

Return a same-type reconstruction of ``error`` with ``label`` prefixed to its own
``context`` (the first line ``MarkedYAMLError.__str__`` renders), or, for a plain
(non-``Marked``) ``yaml.YAMLError``, a same-type reconstruction from the prefixed message
text directly (REQ-006). Marks are passed through unchanged -- Phase 2 already remapped
them to document-relative coordinates; this module only ever adds tool-boundary context on
top, never touches a mark again.


### `wrap_tool_errors(domain: 'str', tool: 'str', *, channel: 'str | None' = None, also_catch: 'tuple[type[Exception], ...]' = ()) -> 'Iterator[None]'`

Context manager: prepend domain + tool + (optional) channel context to any of the
validation-error channels raised by the wrapped block (Task 3.1, REQ-005/REQ-006).

Every touched ``@mcp.tool()`` wrapper calls this once around its own validating call
(never around its entire body -- see the module docstring)::

    with wrap_tool_errors(domain="tsk", tool="create_tsk", channel=BODY_CHANNEL):
        body = Task.from_text(format_text(content))

On a caught ``AssertionError``, ``pydantic.ValidationError``, ``yaml.YAMLError``, or any
type listed in ``also_catch``, the exact same exception type is re-raised (``raise ... from
error``, so the original remains chained) with the domain/tool/channel label prepended to
its message -- see :func:`_reraise_assertion_like`/:func:`_reraise_validation_error`/
:func:`_reraise_yaml_error` for the per-type reconstruction. Any other exception (including
a domain's own ``*NotFoundError``, a coordinate ``ValueError`` from the generic ``update``
tool's own range guard, file-access errors, ...) propagates completely untouched -- this
context manager only ever touches the three REQ-006 channels (plus ``also_catch``).

Parameters
----------
domain:
    The short domain code (e.g. ``"tsk"``, ``"req"``, ``"adr"``) to name in the label.
tool:
    The tool name (e.g. ``"create_tsk"``, ``"update"``, ``"set_status"``) to name in the
    label.
channel:
    Optional free-text hint for what "vs. body" is knowable in advance at this call site
    (see :data:`BODY_CHANNEL`/:data:`FRONTMATTER_CHANNEL`). ``None`` (the default) omits
    it -- used where the call site cannot know in advance which channel will actually fire
    (``parse_<d>``, ``validate_<d>(full=True)``), since the underlying, already-enriched
    message self-identifies it regardless (Phases 1/2).
also_catch:
    Additional exception types to treat exactly like ``AssertionError`` (message-only,
    same-type reconstruction) -- e.g. ADR's own
    :class:`~biz.dfch.specmgr.models.adr.v1.parser.AdrParseError` for ``create_adr``/
    ``validate_adr``, whose structural channel is a plain ``ValueError`` subclass rather
    than ``AssertionError``. Defaults to ``()``.

Yields
------
None

