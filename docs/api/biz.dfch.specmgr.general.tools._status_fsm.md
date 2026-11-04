# `biz.dfch.specmgr.general.tools._status_fsm`

The generic ``set_status`` tool's own per-domain status state machine (feat-108-fsm, GitHub issue #108).

The cross-cutting half of feat-108-fsm's design (domain-owned ``_STATUS_TRANSITIONS`` tables plus
a central aggregation): :data:`_STATUS_TRANSITIONS_BY_TYPE` holds one entry per whole-body domain,
keyed to the shared ``general.tools._domains`` registry, and :func:`check_status_transition` is the
single pure check the whole-body ``_set_status_<d>`` adapters in ``set_status.py`` call --
immediately after their own unchanged-status no-op comparison and before the raw-body re-read and
``write_<d>_file`` -- to decide whether the transition from the document's current on-disk status
to the requested target is allowed by that domain's machine. A rejection is always pre-write:
nothing is persisted and ``updated`` is not bumped.

Two distinct error surfaces (the feature's own Design Notes): (A) the pre-existing pre-dispatch,
pre-load out-of-vocabulary check in ``set_status.py`` still returns
:class:`~biz.dfch.specmgr.general.models.invalid_status_result.InvalidStatusResult` (the domain's full
flat vocabulary) before any document is loaded -- no current state is known there, and this module
does not touch it; (B) this module's post-load transition check returns the non-raising
:class:`~biz.dfch.specmgr.general.models.invalid_status_transition_result.InvalidStatusTransitionResult`
(the targets allowed from the current state, sorted -- never the full vocabulary; an empty list
marks a terminal current state) -- case 6 of the ADR
519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result workaround chain, so the
current-state-relative detail survives MCP clients that truncate ``isError`` text.

Phased rollout (REQ-003's opt-in seam): an entry's value is ``None`` until the domain's own
``_STATUS_TRANSITIONS`` table lands (Phases 110/120, next to the domain's own ``_ALLOWED_STATUSES``
in its ``models/<v>/frontmatter.py``); a ``None`` entry is a passthrough -- :func:`check_status_transition`
returns ``None`` and the adapter proceeds exactly as before. As of Phase 110 the pilot domain
``req`` is enforced (its own table has landed) and every other whole-body domain is still a
passthrough until Phase 120 lands its table. ADR is excluded (REQ-006): it has no entry
and ``_set_status_adr`` never calls into this module.

**No ``mcp`` dependency here**, like every other private ``general/tools/`` support module: this
module is plain data plus pure functions (it imports the per-domain closed vocabularies from each
domain's own ``models/<v>/frontmatter.py`` exactly as ``set_status.py`` does for its own
``_ALLOWED_STATUSES_BY_TYPE`` -- no re-derived vocabulary), so importing it never registers or
touches a tool.

## Functions

### `check_status_transition(type_: 'str', current: 'str', target: 'str') -> 'InvalidStatusTransitionResult | None'`

The shared check the whole-body ``_set_status_<d>`` adapters call post-load/pre-write.

Looks up the dispatched ``type_``'s own table in :data:`_STATUS_TRANSITIONS_BY_TYPE` and
delegates to :func:`decide_transition`. A table-less domain (a ``None`` entry, or any type
without an entry -- e.g. ``adr``, which never calls this) passes through (``None``), so the
aggregation stays opt-in during the phased rollout (feat-108-fsm, REQ-003). The adapters call
this inside their domain lock, after the unchanged-status no-op comparison and before the
raw-body re-read -- a rejection is pre-write (nothing is persisted, ``updated`` is not
bumped).

Parameters
----------
type_:
    The dispatched domain type (one of ``general.tools._domains.WHOLE_BODY_DOMAINS``).
current:
    The document's current on-disk status (already loaded by the adapter).
target:
    The requested target status.

Returns
-------
``InvalidStatusTransitionResult | None``
    ``None`` when the transition is allowed (or the domain is table-less); otherwise the
    non-raising structured rejection (never raises).


### `decide_transition(table: 'dict[str, frozenset[str]] | None', type_: 'str', current: 'str', target: 'str') -> 'InvalidStatusTransitionResult | None'`

The pure transition decision over one domain's own table (:func:`check_status_transition`'s core).

Total and deterministic, with no module-state dependency (the testability seam): a ``None``
table (a table-less domain, or a type with no aggregation entry such as ``adr``) is a
passthrough; a ``target`` inside the current state's allowed set is allowed; everything else
is a non-raising :class:`InvalidStatusTransitionResult` whose ``allowed_values`` are the
current state's allowed targets, sorted (never the domain's full vocabulary). A ``current``
status that is not a key of the table (structurally unreachable once a domain's table pins
full vocabulary coverage, but the decision must stay total) is treated as a terminal state:
empty ``allowed_values`` and the terminal message form.

Parameters
----------
table:
    The dispatched domain's own ``_STATUS_TRANSITIONS`` table (current status -> allowed
    target statuses), or ``None`` for a table-less (passthrough) domain.
type_:
    The dispatched domain type, echoed verbatim into the result.
current:
    The document's current on-disk status (already loaded by the adapter).
target:
    The requested target status.

Returns
-------
``InvalidStatusTransitionResult | None``
    ``None`` when the call may proceed (passthrough or allowed transition); otherwise the
    non-raising structured rejection (never raises).

