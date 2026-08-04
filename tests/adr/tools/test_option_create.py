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

"""Tests for the ``option_create`` ``@mcp.tool()`` wrapper (plan §5, §8, §9a)."""

import concurrent.futures
import unittest

from biz.dfch.specmgr.adr.tools.option_create import option_create
from biz.dfch.specmgr.adr.tools.option_list import option_list
from biz.dfch.specmgr.adr.tools.option_read import option_read

from ._helpers import TempAdrDirTestCase


class TestOptionCreate(TempAdrDirTestCase):
    """Tests for the option_create tool."""

    def test_option_create_writes_new_option_and_returns_full_title(self):
        """option_create must append the new option on disk and return its full title."""
        self.existing_adr(id_="doc-id")
        full_title = option_create("doc-id", "First option", "Some content.")
        self.assertEqual(full_title, "Option 1: First option")
        self.assertEqual(option_list("doc-id"), ["Option 1: First option"])
        self.assertEqual(option_read("doc-id", full_title), "Some content.")

    def test_concurrent_calls_against_the_same_id_do_not_lose_updates(self):
        """Two option_create calls racing on the same doc must both survive.

        Regression test for the read-modify-write lost-update race: without
        ``_lock.adr_lock`` serializing ``load_by_id`` -> mutate -> ``write_adr``,
        two threads can both read the same "no options yet" state, each compute
        the same next option number, and then one thread's ``write_adr`` clobbers
        the other's -- silently dropping one of the two options.
        """
        self.existing_adr(id_="doc-id")
        worker_count = 8

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [
                executor.submit(option_create, "doc-id", f"Option body {i}", f"Content {i}")
                for i in range(worker_count)
            ]
            full_titles = [future.result() for future in futures]

        # Every call must have returned a distinct title (no number reused)...
        self.assertEqual(len(set(full_titles)), worker_count)
        # ...and every one of them must actually be present on disk afterward.
        self.assertEqual(len(option_list("doc-id")), worker_count)


if __name__ == "__main__":
    unittest.main()
