# `biz.dfch.specmgr.req.tools._lock`

Per-document in-process lock guarding requirement mutations.

Ported from ``adr.tools._lock.adr_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` tool in ``general.tools`` (``type="req"``) and any
future requirement mutation tool (``set_status_req``, Task 3.14) wrap their
whole sequence in ``with req_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` (Task
3.10) -- the id -> path lookup plumbing was generalized because it was
already shared, read-only, dependency-light code; a lock, by contrast, is a
mutation-time correctness primitive that was never part of Task 3.9's
recorded design discussion. Kept as its own small, REQ-specific module for
now, mirroring ADR's own non-generalized precedent; migrating both onto one
shared module remains optional future cleanup.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `req_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for requirement ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with req_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

