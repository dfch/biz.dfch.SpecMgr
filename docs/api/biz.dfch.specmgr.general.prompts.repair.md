# `biz.dfch.specmgr.general.prompts.repair`

``@mcp.prompt()``: repair (feat-150-mcp-lifecycle-commands, Phase 1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through repairing a whole-body specmgr document that currently fails to
parse: discovering it (with an ``id``: ``get_<d>(id)`` -- a document that
exists but fails to parse is returned, not raised: the result carries
``error`` (the parse-failure message, byte-identical to
``list_<d>``'s failed-row ``error`` for the same file -- identical field
path and cause, including the trailing pydantic documentation line) and
``path`` (the absolute on-disk
file), for every one of the whole-body domains per ADR
9080b37c-82b3-4f63-81f1-79641d0bf14c; a truly absent id still raises the
domain's not-found error. Without one: ``list_<d>()``'s failed row, whose
``title``/``status`` carry the fixed ``"<failed to parse>"`` marker and
whose ``id`` is null while ``ref``/``path``/``error`` are populated),
reading the raw file via the host's own file-read tool (no specmgr MCP tool
can return the raw content of a document that fails to parse:
``get_<d>(raw=True)`` and the generic ``update`` (or ``edit``) tool both
re-parse the existing document first, and their per-domain adapters convert
that failure into the domain's not-found error before any write), fixing only
what the error addresses while preserving the frontmatter
``id``/``created``/``status``/``version`` byte-for-byte and leaving
``updated`` untouched (a repair is not an edit), looping the generic
``validate(type, content, full=True)`` tool over the full raw text until
green, writing the repaired text back to the same path via the host's own
file-write tool -- explicitly NOT via the generic ``update`` tool, which is
structurally unable to repair a document that fails to parse -- and then
confirming the repair actually succeeded by calling ``get_<d>(id)`` again
(success: the parsed document, not an ``error``-carrying result; or,
without an ``id``, ``list_<d>()`` again, checking that the row's
``"<failed to parse>"`` marker and ``error`` are gone) against the file as
it now exists on disk. On a host without file read/write tools the
instructions degrade to diagnose-only (report the error and the proposed
fix, touch nothing).

``type`` is one of the whole-body domains (imported from
``general.tools._domains.WHOLE_BODY_DOMAINS``, the single source of truth
per feat-125-domain-lists); ADR is explicitly out of scope -- it has no
generic dry-run ``validate``/``update`` tooling of its own.

This prompt is cross-cutting (it takes ``type`` + an optional ``id``, not
tied to one domain), so -- like ``compact_history`` -- it lives under
``general.prompts`` rather than any single domain package. ``repair`` is a
deliberate exception to the ``<verb>_<domain>`` prompt-naming convention,
following the short, bare-word precedent of the cross-cutting,
type-dispatched tools ``validate``/``delete``/``list_references``.

The actual instructional text lives in its own packaged data file,
``general/data/general_repair_instructions.md``, read fresh on every call
via ``general.tools._packaged_data.read_packaged_text`` -- following the
same packaging convention already used for prompt instructions in the
``qa``/``adr``/``req``/``tsk`` domains (Task 0.19.1, Task 0.20).
Placeholders use ``string.Template`` (``$type``/``$id``), not
``str.format``, so the packaged file is free to use plain, unescaped
``{...}`` braces of its own.

## Functions

### `repair(type: 'str', id: 'str | None' = None) -> 'str'`

Return instructional text for repairing a whole-body document that fails to parse.

Parameters
----------
type:
    The document domain to repair: one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
    ``vcr``, ``sysrs`` (matched case-insensitively). ``"adr"`` is
    explicitly rejected with an actionable error (ADR is not a
    whole-body domain and has no generic dry-run ``validate`` tooling);
    so is any other unknown value.
id:
    The failing document's id, when known. When absent, the returned
    instructions direct discovery via ``list_<type>()``'s failed row
    (the ``<failed to parse>`` marker, a null ``id``, populated
    ``ref``/``path``/``error``) instead of ``get_<type>(id)``.

Returns
-------
str
    Instructional text (auto-wrapped as a single ``UserMessage`` by
    the MCP SDK), not itself a tool call.

Raises
------
ValueError
    If ``type`` is ``"adr"`` (ADR exclusion) or an unknown domain, or
    if ``id`` is a blank/whitespace-only string (pass a real id, or
    omit the parameter entirely).

