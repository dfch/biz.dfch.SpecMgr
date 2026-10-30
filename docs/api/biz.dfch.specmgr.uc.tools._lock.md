# `biz.dfch.specmgr.uc.tools._lock`

Per-document in-process lock guarding use-case mutations.

Ported from ``req.tools._lock.req_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="uc"``) wrap their whole sequence in ``with uc_lock(id):``.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `uc_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for use-case ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
sequence in ``with uc_lock(id):`` so two concurrent calls targeting the
same id run one after another instead of interleaving, preventing the
lost-update race described in this module's docstring. The argument is
the lock *key*: the bare id for the default (EN) document, or
:func:`uc_lock_key`'s per-language key for a language variant
(feat-197-i18n Phase 125), so the language variants of one id are
serialized independently of each other.


### `uc_lock_key(id_: 'str', language: 'str | None' = None) -> 'str'`

Return the lock key for use case ``id_`` in ``language``.

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
    The use case's id (shared across every language variant).
language:
    The variant's language; ``None``/omitted or ``"en"`` = the default
    (flat EN) document.

Returns
-------
str
    The key to pass to :func:`uc_lock`.

