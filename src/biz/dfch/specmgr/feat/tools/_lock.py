# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Per-document and global in-process locks guarding feature mutations (Task 2.2).

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
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

__all__ = ["feat_create_lock", "feat_lock"]

#: Guards creation of/lookup into `_locks` -- held only for the instant it
#: takes to get-or-create a per-id lock, never for the duration of a
#: mutation itself.
_registry_lock = threading.Lock()

#: One lock per feature id, created lazily on first use and never removed --
#: the id space is small and long-lived relative to a server process's
#: lifetime, so there is no meaningful growth/cleanup concern here.
_locks: dict[str, threading.Lock] = {}

#: The single global lock guarding ``create_feat``'s NNN-scan-then-write
#: sequence. There is exactly one such shared resource (the base
#: directory's folder listing), so -- unlike `_locks` above -- no per-key
#: registry is needed: one module-level instance suffices.
_create_lock = threading.Lock()


def _lock_for(id_: str) -> threading.Lock:
    """Return the (lazily created) lock instance for ``id_``."""
    with _registry_lock:
        lock = _locks.get(id_)
        if lock is None:
            lock = threading.Lock()
            _locks[id_] = lock
        return lock


@contextmanager
def feat_lock(id_: str) -> Iterator[None]:
    """Serialize the read-modify-write mutation sequence for feature ``id_``.

    Every mutating tool wraps its whole ``load_by_id`` -> mutate ->
    ``write_feat_file`` sequence in ``with feat_lock(id):`` so two
    concurrent calls targeting the same id run one after another instead of
    interleaving, preventing the lost-update race described in this
    module's docstring.
    """
    lock = _lock_for(id_)
    with lock:
        yield


@contextmanager
def feat_create_lock() -> Iterator[None]:
    """Serialize ``create_feat``'s whole NNN-scan-then-write sequence.

    Every concurrent ``create_feat`` call wraps its whole "scan existing
    ``feat-*`` folder names for the highest ``NNN``, then create
    ``<base>/feat-<NNN + 1>-<slug>/`` and write its ``README.md``" sequence
    in ``with feat_create_lock():``, so two overlapping calls run one after
    another instead of both reading the same pre-create "last NNN" and
    colliding on the same new id.
    """
    with _create_lock:
        yield
