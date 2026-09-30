# `biz.dfch.specmgr.general.tools.edit`

``@mcp.tool()`` wrapper: edit (feat-159-edit, GitHub issue #159).

The generic, cross-domain, surgical exact-match string-replacement tool for
the frontmatter-stripped body of the whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``). It dispatches on the explicit ``type``
parameter to a private per-domain adapter (``_edit_<d>``), each mirroring
the generic ``update`` tool's own adapter shape (same domain lock, same
``load_by_id``, same frontmatter carry-over with only ``updated`` bumped,
same verbatim persistence via the domain's own ``write_<d>_file``, same
domain ``XNotFoundError``, same doc-cache warm) with a different in-lock
sequence: the domain lock is held **across the entire read -> match ->
validate -> write**, because the match runs against *on-disk* content
(unlike ``update``'s whole-body mode, which validates client-supplied
content before taking the lock) -- reading the body outside the lock would
be a TOCTOU race.

``feat`` is the one domain whose adapter (``_edit_feat``) diverges from
every other domain's identical shape in how it resolves ``id``: via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes, "Addressing").

The signature and the stage-1 runtime error strings mirror the OpenCode
``edit`` tool (parity pinned to opencode dev commit
``236cfcbbc31530fde6a9e65318703f40adad8455``,
``packages/opencode/src/tool/edit.ts`` ``replace()``; see the feature
README's Design Notes): the exact-match semantics, the optional
``replace_all`` flag, and the four verbatim stage-1 messages (the
identical-input guard, the empty-``old_str`` guard -- OC's ``write``
reference adapted to specmgr's ``update`` --, the not-found message, and
the multiple-matches message). OC's 9-stage fuzzy matcher chain -- and its
``isDisproportionateMatch`` refusal guard, which exists only to police
those fuzzy stages -- is deliberately not replicated: this tool is
exact-match only.

**2-fold contract (REQ-003).** The edited document is written to disk only
if both stages pass: stage 1 (match) counts exact ``old_str`` occurrences
in the on-disk body -- zero -> the OC not-found ``ValueError``, more than
one without ``replace_all`` -> the OC multiple-matches ``ValueError`` --
then stage 2 validates the *edited* body as a whole document via
``<Domain>.from_text(format_text(edited))`` under ``wrap_tool_errors``.
The disk write via ``write_<d>_file`` happens strictly after stage 2
succeeds; on any failure (either stage) nothing is written and the file is
byte-unchanged.

**Stage-1 errors are plain ``ValueError``s (REQ-002/REQ-008, D3).** The
four stage-1 failures (identical input, empty ``old_str``, not found,
multiple matches) each raise a plain ``ValueError`` carrying the OC message
verbatim with **no** ``domain tool (channel)`` wrap prefix -- they are
client-controlled-input guards (the ``update`` tool's coordinate-guard
precedent), not document-structure failures; ``wrap_tool_errors`` applies
to stage 2 only, exactly as in ``update``. The two match-stage strings,
quoted verbatim from the pinned commit (parity targets the *runtime*
strings -- OC's own tool description text promises different messages that
its runtime never throws)::

    Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
    Found multiple matches for oldString. Provide more surrounding context to make the match unique.

**Byte-exact matching (REQ-009, D2).** Matching is pure byte-exact over
the frontmatter-stripped body text the shared ``body_text`` helper returns
(the same text ``get_<d>(id, raw=True)`` returns): no line-ending
normalization (OC's file-dominant-EOL conversion is deliberately not
replicated -- an ``old_str`` containing a ``\n`` will not match a CRLF
body), no BOM handling (UTF-8, like every other tool), no fuzzy/regex
fallback. ``replace_all`` rewrites every exact occurrence; an empty
``new_str`` (a pure deletion, REQ-001, D1) is legal iff stage 2 validates
the result.

**Explicit type check (REQ-004, D4).** Unlike ``update``/``delete``/
``set_classification`` -- whose dispatch-table lookup inherits a
``KeyError`` for ``type="adr"`` -- the public :func:`edit` raises an
explicit ``ValueError`` for an unknown or ``adr`` ``type`` before
dispatch, following the generic ``validate`` tool's own precedent (ADR
078bf395-0a5f-4afd-84f6-b7a2191a00e6). ADR is deliberately *not* a
``type`` here: its section-level MADR mutation contract
(``update_frontmatter``/``update_section``/``option_*``) has no whole-body
replace by design, and an exact-match body edit is outside it.

**Persistence (REQ-006).** On success the existing frontmatter is carried
over with only ``updated`` bumped (via ``now_timestamp()``), the edited
body is persisted verbatim via the domain's own ``write_<d>_file`` (no
mdformat reformat on write -- ``format_text`` is applied during validation
only, exactly like ``update``; "verbatim" is additionally modulo the
python-frontmatter ``YAMLHandler``'s trailing-whitespace strip on
serialization, the inherited ``_write.py`` caveat identical to
``update``), the domain doc cache is warmed via the domain's own
``read_<d>`` (the feat-107-doc-cache precedent), and the updated
frontmatter only is returned (no body).

**Safety (REQ-005).** The public :func:`edit` validates ``id`` via
``_path_safety.validate_id`` before any filesystem access (a
``ValueError`` before any file access -- mirroring the generic ``update``
tool's own guard), and every adapter confines the resolved path to the
domain's own base directory with ``_path_safety.assert_within`` after
``load_by_id``, inside the domain lock.

OC's read-before-edit enforcement is a *client* session-state convention
in OC; no server-side counterpart is replicated (nothing is enforced
here), and the tool description instead documents the convention to read
the current body via ``get_<d>(id, raw=True)`` before editing.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow. The union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete frontmatter model is returned.

## Functions

### `_edit_dec(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'DecFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the decision identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``dec_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_dec_file``,
``DecNotFoundError``).


### `_edit_feat(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'FeatFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the feature identified by ``id_``.

Mirror of :func:`_edit_dec`'s shape (same ``feat_lock``, ``load_by_id``,
``write_feat_file``, ``FeatNotFoundError``) with one feat-only
divergence (see the module docstring): ``id_`` resolves via
``feat.tools._paths``'s bespoke folder-per-document shortcut (through
``load_by_id``/``feat_base_dir``), not a flat-file directory scan.


### `_edit_gol(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'GolFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the goal identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``gol_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_gol_file``,
``GolNotFoundError``).


### `_edit_prb(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'PrbFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the problem statement identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``prb_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_prb_file``,
``PrbNotFoundError``).


### `_edit_qa(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'QaFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the QA document identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``qa_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_qa_file``,
``QaNotFoundError``).


### `_edit_req(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'ReqFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the requirement identified by ``id_``.

Mirror of the generic ``update`` tool's own ``_update_req`` adapter
shape (same ``req_lock``, ``load_by_id``, frontmatter carry-over with
only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``) with
the edit-specific in-lock sequence (see the module docstring): the
domain lock is held across the entire read -> match -> validate ->
write, stage 1 is the domain-agnostic :func:`_match_and_replace` over
:func:`body_text(path)`, and stage 2 validates the *edited* body as a
whole document before the verbatim persist and the cache warm.


### `_edit_rsk(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'RskFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the risk identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``rsk_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_rsk_file``,
``RskNotFoundError``).


### `_edit_sop(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'SopFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the SOP identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``sop_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_sop_file``,
``SopNotFoundError``).


### `_edit_sysrs(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'SysrsFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the System Requirements Specification for ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``sysrs_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped,
``write_sysrs_file``, ``SysrsNotFoundError``).


### `_edit_tsk(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'TskFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the task list identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``tsk_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_tsk_file``,
``TskNotFoundError``).


### `_edit_uc(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'UcFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the use case identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``uc_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_uc_file``,
``UcNotFoundError``).


### `_edit_vcr(id_: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'VcrFrontmatter | ParseFailureResult | ValidateResult'`

Surgically replace exact occurrences of ``old_str`` in the verification case record identified by ``id_``.

Mirror of :func:`_edit_req`'s shape (same ``vcr_lock``, ``load_by_id``,
frontmatter carry-over with only ``updated`` bumped, ``write_vcr_file``,
``VcrNotFoundError``).


### `_match_and_replace(body: 'str', old_str: 'str', new_str: 'str', replace_all: 'bool') -> 'str'`

Stage 1 of the 2-fold edit contract: byte-exact match and replace (REQ-009, D2).

Domain-agnostic: the per-domain ``_edit_<d>`` adapters call this on the
on-disk body text (:func:`body_text`'s result -- the same text
``get_<d>(id, raw=True)`` returns) and stage-2-validate, persist, and
cache-warm the returned edited body themselves.

Counts exact ``old_str`` occurrences in ``body``: zero occurrences
raises the OC not-found ``ValueError`` verbatim (REQ-002, the pinned
string quoted in the module docstring); more than one occurrence
without ``replace_all`` raises the OC multiple-matches ``ValueError``
verbatim. Matching is pure byte-exact -- no line-ending normalization
(an ``old_str`` containing a ``\n`` will not match a CRLF body), no
BOM handling, no fuzzy/regex fallback. A successful match is applied
via ``str.replace`` (``count=1`` for the single rewrite, no ``count``
for ``replace_all``); an empty ``new_str`` (a pure deletion, REQ-001)
is legal here -- its validity is stage 2's job. The raised
``ValueError``s are plain, with no ``domain tool (channel)`` wrap
prefix (D3).

Parameters
----------
body:
    The current frontmatter-stripped on-disk body text.
old_str:
    The exact text to find (byte-exact; never empty -- the public
    :func:`edit` guard rejects an empty ``old_str`` before dispatch).
new_str:
    The replacement text; the empty string deletes the match(es).
replace_all:
    ``True``: rewrite every exact occurrence. ``False``: the match must
    be unique (exactly one occurrence), else the multiple-matches
    error.

Returns
-------
str
    The edited body text (one replacement applied, or all of them when
    ``replace_all``).

Raises
------
ValueError
    ``old_str`` is not found at all, or is found more than once while
    ``replace_all`` is ``False`` -- the OC message verbatim, plain (no
    wrap prefix), nothing written.


### `edit(id: 'str', type: 'Literal[*WHOLE_BODY_DOMAINS,]', old_str: 'str', new_str: 'str', replace_all: 'bool' = False) -> '_EditFrontmatter'`

Surgically replace a byte-exact occurrence of ``old_str`` in an existing document's body.

Cross-domain generic for the whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``); dispatches on ``type`` to the domain's own
private adapter (same lock, same id resolution, same frontmatter
carry-over, same verbatim persistence, same domain not-found error).
The signature and the stage-1 runtime error strings mirror the
OpenCode ``edit`` tool (parity pinned in the module docstring).

**Stage 1 (match).** ``old_str`` is counted byte-exactly in the
current frontmatter-stripped on-disk body (the text
``get_<d>(id, raw=True)`` returns): no line-ending normalization, no
BOM handling, no fuzzy/regex fallback. Zero occurrences raise the OC
not-found ``ValueError`` verbatim; more than one occurrence raises the
OC multiple-matches ``ValueError`` verbatim unless ``replace_all`` is
``True``, in which case every exact occurrence is rewritten. An empty
``new_str`` (a pure deletion, REQ-001) is legal iff stage 2 validates
the result.

**Stage 2 (validate).** The *edited* body is validated as a whole
document via the domain body model's ``from_text(format_text(edited))``
under ``wrap_tool_errors`` -- letting ``AssertionError`` (structural
failure) or ``pydantic.ValidationError`` (field/cross-field failure)
propagate uncaught, with nothing written in either case.

**2-fold write (REQ-003).** The disk write happens strictly after both
stages pass: the domain lock is held across the entire read -> match ->
validate -> write sequence (the match is against on-disk content, so
reading it outside the lock would be a TOCTOU race -- unlike
``update``'s whole-body mode, which validates client-supplied content
before taking the lock), the existing frontmatter is carried over with
every field preserved except ``updated`` (bumped to the current
date+time timestamp, via ``general.tools._timestamps.now_timestamp()``),
the edited body is persisted verbatim (no mdformat reformat on write --
``format_text`` is applied during validation only, exactly like
``update``), the domain doc cache is warmed via the domain's own
``read_<d>`` (the feat-107-doc-cache precedent), and the updated
frontmatter only is returned (no body). On any failure (either stage)
nothing is written and the file is byte-unchanged.

Safety (REQ-005): ``id`` is validated via ``_path_safety.validate_id``
**before** any filesystem access, so a path-injection attempt or a
wrong-format id is a ``ValueError`` raised before dispatch; an unknown
or ``adr`` ``type`` is likewise an explicit ``ValueError`` before
dispatch (REQ-004, D4 -- the generic ``validate`` tool's precedent, a
deliberate divergence from ``update``'s inherited ``KeyError``); the
identical-input and empty-``old_str`` guards (the OC messages verbatim,
plain ``ValueError``s with no wrap prefix, REQ-008) fire after them and
still before any filesystem access. Each adapter additionally confines
the resolved path to the domain's own base directory with
``_path_safety.assert_within`` inside the lock -- defense-in-depth
against any future gap in the id validation.

OC's read-before-edit enforcement is a client session-state convention
(no server-side counterpart is replicated): read the current body via
the corresponding ``get_<d>(id, raw=True)`` before calling this tool.
The YAML frontmatter is never addressable (body only); use the generic
``update`` tool for a whole-body or line-range replacement instead.

Parameters
----------
id:
    The document's specmgr-assigned identifier.
type:
    The document type / domain: one of ``req``, ``uc``, ``tsk``,
    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
    ``vcr``, ``sysrs``.
old_str:
    The exact text to find in the current frontmatter-stripped on-disk
    body (byte-exact, including whitespace, indentation, and line
    endings); never empty (the empty-``old_str`` guard) and never
    identical to ``new_str`` (the identical-input guard).
new_str:
    The replacement text; the empty string is a pure deletion (legal
    iff the edited body still validates as a whole document).
replace_all:
    ``False`` (default): ``old_str`` must match exactly once (multiple
    matches are an error). ``True``: every exact occurrence is
    rewritten.

Returns
-------
ReqFrontmatter | UcFrontmatter | TskFrontmatter | QaFrontmatter | PrbFrontmatter |
GolFrontmatter | RskFrontmatter | DecFrontmatter | FeatFrontmatter | SopFrontmatter |
VcrFrontmatter | SysrsFrontmatter
    The updated document's frontmatter only (no body) of the dispatched domain type
    (``updated`` bumped); use the corresponding ``get_<d>`` tool to fetch the full
    document afterward.

Raises
------
ValueError
    ``id`` is a path-injection attempt or not in the dispatched
    domain's own format (raised before any filesystem access);
    ``type`` is not one of the supported domains, including
    ``"adr"`` (raised before dispatch, REQ-004 -- ``"adr"`` with a
    well-formed UUID id reaches the edit-specific message; any other
    unknown type is rejected first by ``validate_id``'s own
    message); ``old_str`` is
    identical to ``new_str`` or empty (raised before any filesystem
    access); or the stage-1 match fails -- ``old_str`` not found, or
    multiple matches without ``replace_all`` (raised under the domain
    lock after the on-disk body is read). All four guard/stage-1
    ``ValueError``s carry the OC message verbatim with no
    ``domain tool (channel)`` wrap prefix (REQ-002/REQ-008). Nothing
    is written in any of these cases.
AssertionError
    The edited body is structurally invalid (stage 2) -- e.g. deleting
    the H1. The message is prefixed with domain/tool/channel context
    (e.g. ``"req edit (body): ..."``) by the shared tool-boundary
    wrapper (:func:`~biz.dfch.specmgr.models.md._errors.
    wrap_tool_errors`), layered on top of the engine's own
    field-path/line/snippet enrichment (feat-27-validation Phases
    1/2). Nothing is written.
pydantic.ValidationError
    A field/cross-field validation failure in the edited body (stage
    2, e.g. an edit producing an out-of-vocabulary value) -- similarly
    prefixed. Nothing is written.
ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
FeatNotFoundError / SopNotFoundError / VcrNotFoundError / SysrsNotFoundError
    No document of the dispatched ``type`` has this id -- the
    domain's own not-found error, unchanged from the per-domain tools.

