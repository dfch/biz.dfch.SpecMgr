# `biz.dfch.specmgr.feat.tools._lock`

Per-document and global in-process locks guarding feature mutations (Task 2.2).

``feat_lock(id_)`` mirrors ``dec.tools._lock.dec_lock``'s own per-id shape
unchanged -- see that module's docstring for the full read-modify-write
race rationale (an MCP host dispatching two overlapping tool calls against
the same id). Every mutating tool that already knows the target id (the
generic ``update``/``set_status`` tools in ``general.tools``, ``type="feat"``)
wraps its whole ``load_by_id`` -> mutate -> ``write_feat_file`` sequence in
``with feat_lock(id):``.

``feat_create_lock()`` is the one genuinely new piece here, needed only by
``create_feat``: unlike every other domain (whose id is a freshly minted
UUID, so there is no id to key a per-document lock on yet, but also no
shared mutable state two concurrent creates could race over), ``feat``
derives its id by *scanning existing folder names* for the highest ``NNN``
and adding one -- a read-then-write sequence against directory state shared
by every concurrent ``create_feat`` call, not a single document's own
state. Two overlapping ``create_feat`` calls that both read the same "last
NNN" before either has written its own new folder would otherwise pick the
same ``NNN`` and collide. A single global, no-id lock (there being exactly
one such shared resource, unlike the per-id registry ``feat_lock`` needs)
serializes the whole scan-then-write sequence instead.

Both locks are plain in-process :class:`threading.Lock` instances (not
:class:`asyncio.Lock` -- mutations run in a worker thread, not on the event
loop, mirroring ``adr_lock``/``dec_lock``), and neither is backed by an
on-disk lock file -- this codebase's established precedent for every other
domain's mutation lock is in-process only, and ``feat`` follows that
precedent rather than introducing a new on-disk-lock-file mechanism. This is
process-local only: it does not protect against a second OS process (or a
human editor, sanctioned and expected for `feat` per ADR
e369ee2e-3353-4f92-991c-6367d76d832e) writing the same file/folder
concurrently.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `feat_create_lock() -> 'Iterator[None]'`

Serialize ``create_feat``'s whole NNN-scan-then-write sequence.

Every concurrent ``create_feat`` call wraps its whole "scan existing
``feat-*`` folder names for the highest ``NNN``, then create
``<base>/feat-<NNN + 1>-<slug>/`` and write its ``README.md``" sequence
in ``with feat_create_lock():``, so two overlapping calls run one after
another instead of both reading the same pre-create "last NNN" and
colliding on the same new id.


### `feat_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for feature ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate ->
``write_feat_file`` sequence in ``with feat_lock(id):`` so two
concurrent calls targeting the same id run one after another instead of
interleaving, preventing the lost-update race described in this
module's docstring.

