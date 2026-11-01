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
lost-update race described in this module's docstring. The argument is
the lock *key*: the bare id for the default (EN) document, or
:func:`qa_lock_key`'s per-language key for a language variant
(feat-197-i18n Phase 125), so the language variants of one id are
serialized independently of each other.


### `qa_lock_key(id_: 'str', language: 'str | None' = None) -> 'str'`

Return the lock key for QA document ``id_`` in ``language``.

**Per-language keying (feat-197-i18n Phase 125, ADR 38efdb66 item 9).**
The language variants of one ``id`` are distinct files (distinct
paths), so a mutation of one variant must neither race with, nor
needlessly block on, a mutation of another. The lock key is therefore
the pair (``id_``, language): for the default language (``None``/
omitted or ``"en"``) the key is the bare ``id_`` -- exactly today's
key, so the EN locking is byte-identical -- and for any other language
it is ``"<id_>/<language>"`` (an id never contains ``/``: it is a bare
UUID, validated before any lock is taken, so a variant key can never
collide with an id key).

Parameters
----------
id_:
    The QA document's id (shared across every language variant).
language:
    The variant's language; ``None``/omitted or ``"en"`` = the default
    (flat EN) document.

Returns
-------
str
    The key to pass to :func:`qa_lock`.

