# `biz.dfch.specmgr.gol.tools._lock`

Per-document in-process lock guarding goal mutations.

Ported from ``prb.tools._lock.prb_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
``update_gol``/``set_status_gol`` wrap their whole sequence in
``with gol_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive. Kept as its own small, GOL-specific module for now,
mirroring PRB/REQ's own non-generalized precedent; migrating both onto one
shared module remains optional future cleanup.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `gol_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for goal ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with gol_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

