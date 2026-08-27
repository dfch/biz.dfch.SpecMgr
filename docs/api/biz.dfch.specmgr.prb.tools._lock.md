# `biz.dfch.specmgr.prb.tools._lock`

Per-document in-process lock guarding problem statement mutations.

Ported from ``tsk.tools._lock.tsk_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` tool in ``general.tools`` (``type="prb"``) and
``set_status_prb`` wrap their whole sequence in ``with prb_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive. Kept as its own small, PRB-specific module for now,
mirroring TSK/QA's own non-generalized precedent; migrating both onto one
shared module remains optional future cleanup.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `prb_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for problem statement ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with prb_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

