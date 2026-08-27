# `biz.dfch.specmgr.dec.tools._lock`

Per-document in-process lock guarding decision mutations.

Ported from ``gol.tools._lock.gol_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="dec"``) wrap their whole sequence in ``with dec_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive. Kept as its own small, DEC-specific module, mirroring
GOL/PRB/REQ's own non-generalized precedent; migrating all of them onto one
shared module remains optional future cleanup.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `dec_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for decision ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with dec_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

