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

"""Consistency guard for the shared `What`/`Who`/`Why` -> 4-blank derive-mapping
clause (REQ-015, Phase 5 Task 5.4).

`prb_create_instructions.md` (step 9) and `prb_update_instructions.md`
(step 1's old-shape recovery sub-list) each narrate deriving the Problem
Statement lead sentence's 4 blanks from pre-existing `What`/`Who`/`Why`
answers. The mapping clause itself is aligned to identical, verbatim
wording in both files -- this module is the mechanical drift guard that
fails loudly if the two ever diverge again, rather than leaving the
duplication as a silent, undocumented trade-off.
"""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

#: The exact, verbatim `What`/`Who`/`Why` -> 4-blank derive-mapping clause
#: (REQ-015) that must appear, unchanged, in both packaged instruction
#: files. Only this clause itself is required to match -- the surrounding
#: sentence may legitimately differ by context (see the feature README's
#: Decisions Made log, 2026-09-19 19:00:00.000Z entry).
_DERIVE_MAPPING_CLAUSE = (
    "`What` -> both `[Current state]` and `[specific issue]` (a single `What` answer must "
    "populate two distinct blanks, so draft your best split of it across the two -- e.g. the "
    "underlying condition into `[Current state]`, the concrete symptom into `[specific issue]`); "
    "`Who` -> `[stakeholder]`; `Why` -> `[underlying cause]`."
)


class TestDeriveMappingClauseConsistency(unittest.TestCase):
    """`_DERIVE_MAPPING_CLAUSE` must appear verbatim in both packaged instruction files."""

    def test_clause_appears_verbatim_in_create_instructions(self) -> None:
        text = read_packaged_text("prb", "create_instructions", "md")

        self.assertIn(_DERIVE_MAPPING_CLAUSE, text)

    def test_clause_appears_verbatim_in_update_instructions(self) -> None:
        text = read_packaged_text("prb", "update_instructions", "md")

        self.assertIn(_DERIVE_MAPPING_CLAUSE, text)
