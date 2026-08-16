# `biz.dfch.specmgr.uc.tools._lock`

Per-document in-process lock guarding use-case mutations.

Ported from ``req.tools._lock.req_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
``update_uc`` and any future use-case mutation tool (``set_status_uc``) wrap
their whole sequence in ``with uc_lock(id):``.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `uc_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for use-case ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with uc_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

