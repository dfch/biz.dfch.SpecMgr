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
(``general.tools._status_fsm``, feat-108-fsm Phase 100, REQ-003/REQ-004, GitHub issue #108).

Covers the Phase 100 import-time invariants (the aggregation is keyed to the shared
``general.tools._domains`` registry, ADR excluded, every entry still the ``None`` passthrough
seam), the pure :func:`decide_transition` core (passthrough, allowed, disallowed with the sorted
current-state-relative ``allowed_values`` + the locked normal message form, the terminal message
form, and the total/terminal treatment of a ``current`` that is not a table key), and the public
:func:`check_status_transition` helper (table-less and unregistered types pass through; the
aggregation lookup is exercised with a temporarily patched entry, no module state mutated).
"""

from __future__ import annotations

import importlib
import unittest
from unittest import mock

from biz.dfch.specmgr.general.models import InvalidStatusTransitionResult
from biz.dfch.specmgr.general.tools._domains import ADR, WHOLE_BODY_DOMAINS

status_fsm_module = importlib.import_module("biz.dfch.specmgr.general.tools._status_fsm")
check_status_transition = status_fsm_module.check_status_transition
decide_transition = status_fsm_module.decide_transition

#: A temporary state machine (the req design shape from the feature plan's Design Notes -- the
#: table itself is NOT yet in the module: that is Phase 110) the decision-path tests run
#: :func:`decide_transition` against. Every current status and every target is inside req's own
#: closed vocabulary, so the import-time per-entry validity check would accept it.
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
    """REQ-003/ACC-007 (Phase 100 form): the aggregation is keyed to the registry, ADR excluded,
    and the import-time drift assert passed (the module import at the top of this file is the
    proof -- a failed assert would have made this file unimportable)."""

    def test_module_imports_cleanly(self) -> None:
        self.assertIsNotNone(status_fsm_module)
        self.assertIsNotNone(check_status_transition)
        self.assertIsNotNone(decide_transition)

    def test_every_whole_body_domain_has_an_entry(self) -> None:
        sut = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE

        self.assertEqual(set(sut), set(WHOLE_BODY_DOMAINS))

    def test_adr_has_no_entry(self) -> None:
        sut = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE

        self.assertNotIn(ADR, sut)

    def test_phase_100_every_entry_is_the_none_passthrough(self) -> None:
        sut = status_fsm_module._STATUS_TRANSITIONS_BY_TYPE

        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIsNone(sut[domain])

    def test_vocabularies_cover_exactly_the_whole_body_domains(self) -> None:
        sut = status_fsm_module._STATUS_VOCABULARIES_BY_TYPE

        self.assertEqual(set(sut), set(WHOLE_BODY_DOMAINS))
        self.assertNotIn(ADR, sut)


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
    """The public helper: the aggregation lookup (table-less pass-through, unregistered types)
    plus one temporarily patched entry proving the lookup delegates to the core."""

    def test_tableless_whole_body_domain_passes_through(self) -> None:
        for domain in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIsNone(check_status_transition(domain, "draft", "accepted"))

    def test_unregistered_type_passes_through(self) -> None:
        self.assertIsNone(check_status_transition(ADR, "draft", "accepted"))
        self.assertIsNone(check_status_transition("bogus", "draft", "accepted"))

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
