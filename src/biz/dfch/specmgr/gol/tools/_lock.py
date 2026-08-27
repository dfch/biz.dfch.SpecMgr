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

"""Per-document in-process lock guarding goal mutations.

Ported from ``prb.tools._lock.prb_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="gol"``) wrap their whole sequence in ``with gol_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive. Kept as its own small, GOL-specific module for now,
mirroring PRB/REQ's own non-generalized precedent; migrating both onto one
shared module remains optional future cleanup.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

__all__ = ["gol_lock"]

#: Guards creation of/lookup into `_locks` -- held only for the instant it
#: takes to get-or-create a per-id lock, never for the duration of a
#: mutation itself.
_registry_lock = threading.Lock()

#: One lock per goal id, created lazily on first use and never
#: removed -- the id space is small and long-lived relative to a server
#: process's lifetime, so there is no meaningful growth/cleanup concern here.
_locks: dict[str, threading.Lock] = {}


def _lock_for(id_: str) -> threading.Lock:
    """Return the (lazily created) lock instance for ``id_``."""
    with _registry_lock:
        lock = _locks.get(id_)
        if lock is None:
            lock = threading.Lock()
            _locks[id_] = lock
        return lock


@contextmanager
def gol_lock(id_: str) -> Iterator[None]:
    """Serialize the read-modify-write mutation sequence for goal ``id_``.

    Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
    sequence in ``with gol_lock(id):`` so two concurrent calls targeting the
    same id run one after another instead of interleaving, preventing the
    lost-update race described in this module's docstring.
    """
    lock = _lock_for(id_)
    with lock:
        yield
