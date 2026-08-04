# `biz.dfch.specmgr.adr.tools._lock`

Per-document in-process lock guarding ADR mutations (plan §7, §9a).

Every mutating tool in this package (``update_section``,
``update_frontmatter``, ``set_status``, ``option_create``, ``option_update``,
``option_delete``) follows the same read-modify-write shape: ``load_by_id``
(re-read/re-parse the file), mutate the in-memory :class:`~..models.adr.Adr`,
then ``write_adr`` (re-render/re-write the file). There is deliberately no
in-memory cache (plan §7, §9a) -- the ``.md`` file is the sole source of
truth -- which means that sequence is the *only* place document state lives
between the read and the write.

An MCP host is free to dispatch two tool calls against the same document id
at the same time, and every ``@mcp.tool()``-decorated function here is a
plain (synchronous) function: the MCP server runs those off the event loop
via ``anyio.to_thread.run_sync`` (a worker-thread pool), so two overlapping
calls targeting the same id genuinely execute in parallel threads within
this one process. Without serialization, two read-modify-write sequences
can interleave -- both threads read the same pre-update state, mutate their
own in-memory copy, and then write back one after another, so whichever
thread's ``write_adr`` runs last silently overwrites the other thread's
otherwise-successful change (the classic lost-update race).

``adr_lock`` closes that window by serializing the whole read-modify-write
sequence per document id: a plain :class:`threading.Lock` (not an
:class:`asyncio.Lock` -- the mutation runs in a worker thread, not on the
event loop), created lazily per id and never removed. Concurrent mutations
against *different* ids are unaffected (each id gets its own lock instance),
and read-only tools (``get_adr``, ``option_list``, ``option_read``,
``validate_adr``) intentionally do not take this lock -- they still re-read
whatever is currently on disk, matching the existing "no cache, always
re-read" design; only mutation ordering is guaranteed, not read/write
isolation.

This is process-local only: it does not protect against a second OS process
(or a human editor) writing the same file concurrently. The threat model
here is a single MCP server process fielding overlapping tool calls from one
host, not multiple concurrent processes/writers.

## Functions

### `_lock_for(id_: 'str') -> 'threading.Lock'`

Return the (lazily created) lock instance for ``id_``.


### `adr_lock(id_: 'str') -> 'Iterator[None]'`

Serialize the read-modify-write mutation sequence for ADR ``id_``.

Every mutating tool wraps its whole ``load_by_id`` -> mutate ->
``write_adr`` sequence in ``with adr_lock(id):`` so two concurrent calls
targeting the same id run one after another instead of interleaving,
preventing the lost-update race described in this module's docstring.

