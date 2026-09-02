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

"""Tests for ``sysrs.tools._lock.sysrs_lock`` (per-document mutation serialization)."""

from __future__ import annotations

import threading
import time
import unittest

from biz.dfch.specmgr.sysrs.tools._lock import sysrs_lock


def _run_and_track_overlap(ids: list[str], hold_seconds: float = 0.05) -> int:
    """Run one thread per entry in ``ids``, each holding ``sysrs_lock(id_)`` for
    ``hold_seconds``, and return the maximum number of threads observed
    executing inside their critical section at the same time.
    """
    active = 0
    max_active = 0
    guard = threading.Lock()

    def worker(id_: str) -> None:
        nonlocal active, max_active
        with sysrs_lock(id_):
            with guard:
                active += 1
                max_active = max(max_active, active)
            time.sleep(hold_seconds)
            with guard:
                active -= 1

    threads = [threading.Thread(target=worker, args=(id_,)) for id_ in ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return max_active


class TestSysrsLock(unittest.TestCase):
    """Tests for sysrs_lock's serialization behaviour."""

    def test_serializes_calls_against_the_same_id(self) -> None:
        """Concurrent sysrs_lock(id) calls for the same id must never overlap."""
        max_active = _run_and_track_overlap(["same-id"] * 5)
        self.assertEqual(max_active, 1)

    def test_does_not_serialize_calls_against_different_ids(self) -> None:
        """sysrs_lock calls for distinct ids must be able to run concurrently."""
        max_active = _run_and_track_overlap([f"id-{i}" for i in range(5)])
        self.assertGreater(max_active, 1)

    def test_lock_is_reentrant_safe_release(self) -> None:
        """A second, sequential acquisition of the same id must succeed (not deadlock)."""
        with sysrs_lock("doc-id"):
            pass
        with sysrs_lock("doc-id"):
            pass


if __name__ == "__main__":
    unittest.main()
