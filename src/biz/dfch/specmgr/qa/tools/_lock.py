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

"""Per-document in-process lock guarding Question and Answer (QA) mutations.

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
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

from ...general.tools._path_safety import DEFAULT_LANGUAGE

__all__ = ["qa_lock", "qa_lock_key"]

#: Guards creation of/lookup into `_locks` -- held only for the instant it
#: takes to get-or-create a per-id lock, never for the duration of a
#: mutation itself.
_registry_lock = threading.Lock()

#: One lock per QA document id, created lazily on first use and never
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


def qa_lock_key(id_: str, language: str | None = None) -> str:
    """Return the lock key for QA document ``id_`` in ``language``.

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
    """
    assert isinstance(id_, str), type(id_)
    assert language is None or isinstance(language, str), type(language)

    result = id_ if language is None or language == DEFAULT_LANGUAGE else f"{id_}/{language}"
    return result


@contextmanager
def qa_lock(id_: str) -> Iterator[None]:
    """Serialize the read-modify-write mutation sequence for QA document ``id_``.

    Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
    sequence in ``with qa_lock(id):`` so two concurrent calls targeting the
    same id run one after another instead of interleaving, preventing the
    lost-update race described in this module's docstring. The argument is
    the lock *key*: the bare id for the default (EN) document, or
    :func:`qa_lock_key`'s per-language key for a language variant
    (feat-197-i18n Phase 125), so the language variants of one id are
    serialized independently of each other.
    """
    lock = _lock_for(id_)
    with lock:
        yield
