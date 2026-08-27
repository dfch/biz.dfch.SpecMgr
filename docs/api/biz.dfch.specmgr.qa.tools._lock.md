# `biz.dfch.specmgr.qa.tools._lock`

Per-document in-process lock guarding Question and Answer (QA) mutations.

Ported from ``adr.tools._lock.adr_lock``/``req.tools._lock.req_lock``
unchanged except for naming -- see that module's own docstring for the full
rationale (the read-modify-write race a mutating tool's ``load_by_id`` ->
mutate -> write sequence is exposed to when an MCP host dispatches two
overlapping calls against the same id). The generic ``update`` tool in
``general.tools`` (``type="qa"``) and the generic ``set_status`` tool in
``general.tools`` (``type="qa"``) wrap their whole sequence in
``with qa_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive that was never part of that design discussion. Kept as
its own small, QA-specific module for now, mirroring ADR's/REQ's own
non-generalized precedent; migrating all three onto one shared module
remains optional future cleanup.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `qa_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for QA document ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with qa_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring.

