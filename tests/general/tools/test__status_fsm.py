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

"""Unit tests for the generic ``set_status`` tool's own per-domain status state machine
(``general.tools._status_fsm``, feat-108-fsm Phase 100/110/120, REQ-003/REQ-004, GitHub
issue #108).

Covers the import-time invariants (the aggregation is keyed to the shared ``general.tools.
_domains`` registry, and -- as of Phase 120 -- every whole-body entry carries its domain's
own landed table by identity: the rollout is complete, no ``None`` passthrough
remains), the pure :func:`decide_transition` core (passthrough, allowed, disallowed with the
sorted current-state-relative ``allowed_values`` + the locked normal message form, the
terminal message form, and the total/terminal treatment of a ``current`` that is not a table
key), and the public :func:`check_status_transition` helper (unregistered types pass
through; the aggregation lookup is exercised with a temporarily patched entry, no module
state mutated; every whole-body domain's landed table is enforced straight from module
state).
"""

from __future__ import annotations

import importlib
import unittest
from unittest import mock

from biz.dfch.specmgr.dec.models.v1.frontmatter import _STATUS_TRANSITIONS as _DEC_LANDED_TABLE
from biz.dfch.specmgr.feat.models.v1.frontmatter import _STATUS_TRANSITIONS as _FEAT_LANDED_TABLE
from biz.dfch.specmgr.general.models import InvalidStatusTransitionResult
from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.gol.models.v1.frontmatter import _STATUS_TRANSITIONS as _GOL_LANDED_TABLE
from biz.dfch.specmgr.prb.models.v1.frontmatter import _STATUS_TRANSITIONS as _PRB_LANDED_TABLE
from biz.dfch.specmgr.qa.models.v2.frontmatter import _STATUS_TRANSITIONS as _QA_LANDED_TABLE
from biz.dfch.specmgr.req.models.v1.frontmatter import _STATUS_TRANSITIONS as _REQ_LANDED_TABLE
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _STATUS_TRANSITIONS as _RSK_LANDED_TABLE
from biz.dfch.specmgr.set.models.v1.frontmatter import _STATUS_TRANSITIONS as _SET_LANDED_TABLE
from biz.dfch.specmgr.sop.models.v1.frontmatter import _STATUS_TRANSITIONS as _SOP_LANDED_TABLE
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import _STATUS_TRANSITIONS as _SYSRS_LANDED_TABLE
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _STATUS_TRANSITIONS as _TSK_LANDED_TABLE
from biz.dfch.specmgr.txt.models.v1.frontmatter import _STATUS_TRANSITIONS as _TXT_LANDED_TABLE
from biz.dfch.specmgr.uc.models.v2.frontmatter import _STATUS_TRANSITIONS as _UC_LANDED_TABLE
from biz.dfch.specmgr.vcr.models.v1.frontmatter import _STATUS_TRANSITIONS as _VCR_LANDED_TABLE

status_fsm_module = importlib.import_module("biz.dfch.specmgr.general.tools._status_fsm")
check_status_transition = status_fsm_module.check_status_transition
decide_transition = status_fsm_module.decide_transition

#: Every whole-body domain's own landed table, keyed by type (Phase 120: full coverage --
#: ``req`` since Phase 110, the remaining whole-body domains since Phase 120): the identity
#: pin for the aggregation's entries (domain-owned constants, carried by the aggregation,
#: not copies).
_LANDED_TABLES_BY_TYPE: dict[str, dict[str, frozenset[str]]] = {
    "req": _REQ_LANDED_TABLE,
    "uc": _UC_LANDED_TABLE,
    "tsk": _TSK_LANDED_TABLE,
    "qa": _QA_LANDED_TABLE,
    "prb": _PRB_LANDED_TABLE,
    "gol": _GOL_LANDED_TABLE,
    "rsk": _RSK_LANDED_TABLE,
    "dec": _DEC_LANDED_TABLE,
    "sop": _SOP_LANDED_TABLE,
    "feat": _FEAT_LANDED_TABLE,
    "vcr": _VCR_LANDED_TABLE,
    "sysrs": _SYSRS_LANDED_TABLE,
    "txt": _TXT_LANDED_TABLE,
    "set": _SET_LANDED_TABLE,
}

assert set(_LANDED_TABLES_BY_TYPE) == set(WHOLE_BODY_DOMAINS), (
    "_LANDED_TABLES_BY_TYPE keys drifted from the shared general.tools._domains.WHOLE_BODY_DOMAINS source -- "
    "add or remove the domain in both places (feat-125-domain-lists)"
)

#: The locked req table (the feature plan's Design Notes shape): the golden pin for the landed
#: ``req.models.v1.frontmatter._STATUS_TRANSITIONS`` constant (the full 7x7 matrix walk lives in
#: ``tests/req/models/v1/test_frontmatter.py`` and the e2e module
#: ``tests/general/tools/test_set_status_fsm_req.py``). Every current status and every target is
#: inside req's own closed vocabulary, so the import-time per-entry validity check accepts it.
_REQ_TABLE: dict[str, frozenset[str]] = {
    "draft": frozenset({"proposed", "rejected"}),
    "proposed": frozenset({"accepted", "rejected", "draft"}),
    "accepted": frozenset({"implemented", "superseded", "deprecated", "rejected"}),
    "rejected": frozenset({"proposed", "draft"}),
    "implemented": frozenset({"superseded", "deprecated"}),
    "superseded": frozenset(),
    "deprecated": frozenset(),
}

#: The locked normal-form message for the representative disallowed transition.
_NORMAL_MESSAGE = (
    "Invalid status transition 'accepted' -> 'draft' for type 'req'. "
    "Allowed from 'accepted': deprecated, implemented, rejected, superseded"
)

#: The locked terminal-form message for a terminal current state.
_TERMINAL_MESSAGE = (
    "Invalid status transition 'superseded' -> 'draft' for type 'req'. "
    "Status 'superseded' is terminal (no outgoing transitions)."
)


class TestStatusTransitionsAggregation(unittest.TestCase):
    """REQ-003/ACC-007 (the full-coverage form, Phase 120): the aggregation is keyed to the
    registry, and the import-time drift assert passed (the module import at the top of this
    file is the proof -- a failed assert would have made this file unimportable).
    As of Phase 120 the rollout is complete: every whole-body entry is the domain's own
    landed table (``req`` since Phase 110, the rest since Phase 120), carried by identity,
    and no ``None`` passthrough entry remains."""

    def test_module_imports_cleanly(self) -> None:
        self.assertIsNotNone(status_fsm_module)
        self.assertIsNotNone(check_status_transition)
        self.assertIsNotNone(decide_transition)

    def test_every_whole_body_domain_has_an_entry(self) -> None:
        sut = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE

        self.assertEqual(set(sut), set(WHOLE_BODY_DOMAINS))

    def test_every_entry_is_its_own_landed_domain_table(self) -> None:
        """REQ-001/REQ-003/ACC-007: the aggregation carries every domain's own constant by
        identity (domain-owned, no copy) and each equals the locked table shape."""
        sut = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE

        for domain, landed_table in _LANDED_TABLES_BY_TYPE.items():
            with self.subTest(domain=domain):
                self.assertIs(sut[domain], landed_table)
        self.assertEqual(sut["req"], _REQ_TABLE)

    def test_no_entry_is_the_none_passthrough(self) -> None:
        """ACC-007 (full coverage): the Phase-100/110 ``None`` passthrough seam is gone --
        every whole-body domain's table has landed and is enforced."""
        sut = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE

        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIsNotNone(sut[domain])

    def test_vocabularies_cover_exactly_the_whole_body_domains(self) -> None:
        sut = status_fsm_module._STATUS_VOCABULARIES_BY_TYPE

        self.assertEqual(set(sut), set(WHOLE_BODY_DOMAINS))


class TestDecideTransition(unittest.TestCase):
    """The pure core: passthrough, allowed, disallowed (normal form), terminal form, and the
    total/terminal treatment of a ``current`` that is not a table key -- no module state mutated."""

    def test_none_table_passthrough_returns_none(self) -> None:
        result = decide_transition(None, "req", "accepted", "draft")

        self.assertIsNone(result)

    def test_allowed_transition_returns_none(self) -> None:
        result = decide_transition(_REQ_TABLE, "req", "draft", "proposed")

        self.assertIsNone(result)

    def test_disallowed_transition_returns_result_with_sorted_allowed_values(self) -> None:
        result = decide_transition(_REQ_TABLE, "req", "accepted", "draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertFalse(result.valid)
        self.assertEqual(result.type, "req")
        self.assertEqual(result.from_status, "accepted")
        self.assertEqual(result.to_status, "draft")
        self.assertEqual(result.allowed_values, ["deprecated", "implemented", "rejected", "superseded"])
        self.assertEqual(result.allowed_values, sorted(result.allowed_values))

    def test_disallowed_transition_message_normal_form_pinned(self) -> None:
        """The exact literal message wording must not silently drift (the sorted field order)."""
        result = decide_transition(_REQ_TABLE, "req", "accepted", "draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertEqual(result.message, _NORMAL_MESSAGE)

    def test_terminal_current_state_returns_empty_allowed_values_and_terminal_message(self) -> None:
        result = decide_transition(_REQ_TABLE, "req", "superseded", "draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertFalse(result.valid)
        self.assertEqual(result.allowed_values, [])
        self.assertEqual(result.message, _TERMINAL_MESSAGE)

    def test_current_not_a_table_key_is_treated_as_terminal(self) -> None:
        """A ``current`` that is not a key of the table (structurally unreachable once a table
        pins full vocabulary coverage, but the decision must stay total) takes the terminal form."""
        result = decide_transition(_REQ_TABLE, "req", "not-a-key", "draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertEqual(result.from_status, "not-a-key")
        self.assertEqual(result.allowed_values, [])
        self.assertEqual(
            result.message,
            "Invalid status transition 'not-a-key' -> 'draft' for type 'req'. "
            "Status 'not-a-key' is terminal (no outgoing transitions).",
        )


class TestCheckStatusTransition(unittest.TestCase):
    """The public helper: the aggregation lookup (unregistered types pass through; every
    whole-body domain is enforced straight from module state as of Phase 120) plus one
    temporarily patched entry proving the lookup delegates to the core."""

    def test_every_whole_body_domain_is_enforced_not_passthrough(self) -> None:
        """Phase 120: no whole-body domain is a table-less passthrough any more -- for each,
        a table-allowed transition from its create status passes and the diagonal (no
        state carries itself as its own target in any locked table) is rejected."""
        start_statuses = {"rsk": "open", "feat": "planning"}
        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                table = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE[domain]
                start = start_statuses.get(domain, "draft")
                self.assertIsNone(check_status_transition(domain, start, sorted(table[start])[0]))

                result = check_status_transition(domain, start, start)

                self.assertIsInstance(result, InvalidStatusTransitionResult)
                self.assertEqual(result.type, domain)
                self.assertEqual(result.from_status, start)
                self.assertEqual(result.to_status, start)

    def test_unregistered_type_passes_through(self) -> None:
        self.assertIsNone(check_status_transition("bogus", "draft", "accepted"))

    def test_landed_req_table_is_enforced_straight_from_module_state(self) -> None:
        """Phase 110: with no patching, the aggregation's req entry (the landed domain table)
        decides -- an allowed transition passes, a disallowed one returns the normal form, a
        terminal current state the terminal form."""
        self.assertIsNone(check_status_transition("req", "draft", "proposed"))

        result = check_status_transition("req", "accepted", "draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertEqual(result.from_status, "accepted")
        self.assertEqual(result.to_status, "draft")
        self.assertEqual(result.allowed_values, ["deprecated", "implemented", "rejected", "superseded"])
        self.assertEqual(result.message, _NORMAL_MESSAGE)

        terminal = check_status_transition("req", "superseded", "draft")

        self.assertIsInstance(terminal, InvalidStatusTransitionResult)
        self.assertEqual(terminal.allowed_values, [])
        self.assertEqual(terminal.message, _TERMINAL_MESSAGE)

    def test_helper_indexes_the_aggregation(self) -> None:
        with mock.patch.dict(status_fsm_module._STATUS_TRANSITIONS_BY_TYPE, {"req": _REQ_TABLE}):
            result = check_status_transition("req", "accepted", "draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertEqual(result.from_status, "accepted")
        self.assertEqual(result.to_status, "draft")
        self.assertEqual(result.allowed_values, ["deprecated", "implemented", "rejected", "superseded"])
        self.assertEqual(result.message, _NORMAL_MESSAGE)

    def test_helper_passes_through_an_allowed_transition_of_a_patched_entry(self) -> None:
        with mock.patch.dict(status_fsm_module._STATUS_TRANSITIONS_BY_TYPE, {"req": _REQ_TABLE}):
            result = check_status_transition("req", "draft", "proposed")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
