# `biz.dfch.specmgr.txt.tools._lock`

Per-document in-process lock guarding free-form text mutations.

Ported from ``vcr.tools._lock.vcr_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="txt"``) wrap their whole sequence in ``with txt_lock(id):`` (their
own ``txt`` adapters land with the domain's Phase 130 generic-tool
registration).

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive. Kept as its own small, TXT-specific module,
mirroring VCR's own non-generalized precedent; migrating all of them onto
one shared module remains optional future cleanup.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `txt_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for free-form text document ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with txt_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

