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

"""End-to-end tests of the generic ``set_status`` tool's status state machine enforcement for the
pilot domain ``req`` (feat-108-fsm Phase 110, Task 110.110, ACC-001/ACC-002/ACC-003/ACC-004/
ACC-005, GitHub issue #108).

Mirrors the fixture strategy of ``tests/general/tools/test_set_status.py``: a temp
``SPECMGR_DOCS_DIR`` (via ``DOCS_DIR_ENV_VAR``), a real requirement seeded through
``req.tools.create_req.create_req`` (fresh status ``draft``), the public ``set_status(id, "req",
...)`` entry point, and the on-disk file as the authority (every case asserts the file state,
not just the return value). This module is the per-domain e2e home of the phased rollout: Phase
120 lands the sibling coverage for the remaining whole-body domains.

Covers: an allowed transition persisting (``draft`` -> ``proposed``); a disallowed transition
(``accepted`` -> ``draft``) returning the non-raising ``InvalidStatusTransitionResult`` with the
current-state-relative ``allowed_values`` (sorted, pinned) and the exact normal-form message,
file byte-identical; a multi-step cycle walking back (``draft`` -> ``proposed`` -> ``draft`` ->
``proposed`` -> ``accepted``); a terminal current state (``superseded``) returning the empty
``allowed_values`` and the exact terminal-form message, file untouched; the no-op running BEFORE
the transition check (a ``superseded`` req requesting ``superseded`` succeeds with no write and
no ``updated`` bump); the out-of-vocabulary path still returning the pre-existing, distinct
``InvalidStatusResult`` (the full flat vocabulary, pre-load) on any req; and the full 7x7
transition matrix over req's vocabulary, every (current, target) pair classified through the
public tool exactly as the landed table says (ACC-001's pilot pin).
"""

from __future__ import annotations

import re
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

import frontmatter

from biz.dfch.specmgr.general.models import InvalidStatusResult, InvalidStatusTransitionResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.req.models.v1 import ReqFrontmatter
from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES, _STATUS_TRANSITIONS
from biz.dfch.specmgr.req.tools.create_req import create_req

#: The canonical date+time timestamp shape (feat-146) the ``updated`` bump must match -- the same
#: pattern ``test_set_status.py`` pins.
_DATE_TIME_TIMESTAMP = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})"

_REQ_MINIMAL_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 °C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    SRS

    ## Source

    The International Safety Board Association (TISBA)
    """
)

#: The allowed walk from a fresh (``draft``) requirement to every one of req's seven states --
#: every step allowed by the landed table (the tests' precondition: any state is reachable
#: without a rejected transition).
_WALKS_FROM_DRAFT: dict[str, tuple[str, ...]] = {
    "draft": (),
    "proposed": ("proposed",),
    "accepted": ("proposed", "accepted"),
    "rejected": ("rejected",),
    "implemented": ("proposed", "accepted", "implemented"),
    "superseded": ("proposed", "accepted", "superseded"),
    "deprecated": ("proposed", "accepted", "deprecated"),
}


class TempReqFsmDocsDirTestCase(unittest.TestCase):
    """Common fixture: a temp docs root set as ``SPECMGR_DOCS_DIR`` (the ``test_set_status.py``
    strategy, scoped to ``req`` alone) plus the req seeding/walk helpers."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def _seed_req(self) -> ReqFrontmatter:
        """Create a real, persisted requirement (fresh status ``draft``) and return its frontmatter."""
        created = create_req(_REQ_MINIMAL_BODY)
        self.assertIsInstance(created, ReqFrontmatter)
        self.assertEqual(created.status, "draft")
        self.assertIsInstance(created.id, str)
        result = created
        return result

    def _path_for(self, doc_id: str) -> Path:
        """The on-disk file of the req document with ``doc_id``."""
        matches = list((self.docs_root / "req").glob("*.md"))
        result = next(path for path in matches if doc_id in path.name)
        return result

    def _walk_to(self, doc_id: str, created: ReqFrontmatter, state: str) -> ReqFrontmatter:
        """Drive the freshly created (``draft``) requirement to ``state`` through allowed
        transitions only; return the final step's frontmatter (``created`` itself for ``draft``)."""
        current = created
        for step in _WALKS_FROM_DRAFT[state]:
            stepped = set_status(id=doc_id, type="req", status=step)
            self.assertIsInstance(stepped, ReqFrontmatter)
            self.assertEqual(stepped.status, step)
            current = stepped
        result = current
        return result


class TestSetStatusFsmReq(TempReqFsmDocsDirTestCase):
    """Task 110.110: the end-to-end req state-machine pins (ACC-001's matrix plus ACC-002..ACC-005)."""

    def test_allowed_transition_draft_to_proposed_succeeds_and_persists(self) -> None:
        """ACC-002 (allowed side): ``draft`` -> ``proposed`` changes the status on disk, bumps
        ``updated``, and leaves the raw body byte-identical (the success return shape is the
        domain's own frontmatter, not the document)."""
        created = self._seed_req()
        path = self._path_for(created.id)
        raw_body_before = body_text(path)

        result = set_status(id=created.id, type="req", status="proposed")

        self.assertIsInstance(result, ReqFrontmatter)
        self.assertEqual(result.status, "proposed")
        self.assertEqual(result.id, created.id)
        self.assertEqual(result.type, "req")
        self.assertEqual(result.created, created.created)
        self.assertEqual(result.version, created.version)
        self.assertNotEqual(result.updated, created.updated)
        self.assertIsNotNone(re.fullmatch(_DATE_TIME_TIMESTAMP, result.updated))
        on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
        self.assertEqual(on_disk_metadata["status"], "proposed")
        self.assertEqual(body_text(path), raw_body_before)

    def test_disallowed_transition_accepted_to_draft_returns_transition_result_file_untouched(self) -> None:
        """ACC-002 (rejected side): ``accepted`` -> ``draft`` is rejected pre-write with the
        non-raising ``InvalidStatusTransitionResult`` -- the current-state-relative
        ``allowed_values`` (sorted, the exact list pinned), the exact normal-form message, and
        the file byte-identical (no write, ``updated`` unchanged)."""
        created = self._seed_req()
        self._walk_to(created.id, created, "accepted")
        path = self._path_for(created.id)
        before = path.read_text(encoding="utf-8")

        result = set_status(id=created.id, type="req", status="draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertNotIsInstance(result, InvalidStatusResult)
        self.assertFalse(result.valid)
        self.assertEqual(result.type, "req")
        self.assertEqual(result.from_status, "accepted")
        self.assertEqual(result.to_status, "draft")
        self.assertEqual(result.allowed_values, ["deprecated", "implemented", "rejected", "superseded"])
        self.assertEqual(
            result.message,
            "Invalid status transition 'accepted' -> 'draft' for type 'req'. "
            "Allowed from 'accepted': deprecated, implemented, rejected, superseded",
        )
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_multi_step_cycle_walks_back_and_forth(self) -> None:
        """ACC-003: the machine is cycling-friendly -- ``draft`` -> ``proposed`` -> ``draft`` ->
        ``proposed`` -> ``accepted`` succeeds step by step, ending in ``accepted`` on disk."""
        created = self._seed_req()
        path = self._path_for(created.id)

        for step in ("proposed", "draft", "proposed", "accepted"):
            with self.subTest(step=step):
                result = set_status(id=created.id, type="req", status=step)
                self.assertIsInstance(result, ReqFrontmatter)
                self.assertEqual(result.status, step)
                on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                self.assertEqual(on_disk_metadata["status"], step)

    def test_terminal_current_state_returns_empty_allowed_values_file_untouched(self) -> None:
        """ACC-002 (terminal edge): from ``superseded`` (reached ``draft`` -> ``proposed`` ->
        ``accepted`` -> ``superseded``) any target is rejected with the empty ``allowed_values``
        and the exact terminal-form message; the file stays untouched."""
        created = self._seed_req()
        self._walk_to(created.id, created, "superseded")
        path = self._path_for(created.id)
        before = path.read_text(encoding="utf-8")

        result = set_status(id=created.id, type="req", status="draft")

        self.assertIsInstance(result, InvalidStatusTransitionResult)
        self.assertEqual(result.type, "req")
        self.assertEqual(result.from_status, "superseded")
        self.assertEqual(result.to_status, "draft")
        self.assertEqual(result.allowed_values, [])
        self.assertEqual(
            result.message,
            "Invalid status transition 'superseded' -> 'draft' for type 'req'. "
            "Status 'superseded' is terminal (no outgoing transitions).",
        )
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_noop_on_a_terminal_state_is_a_success_not_a_rejection(self) -> None:
        """ACC-004 + the no-op-before-transition-check order pin: a ``superseded`` req requesting
        ``superseded`` again returns the success shape (the domain's own frontmatter) with no
        write and no ``updated`` bump -- the no-op comparison runs before the machine ever sees
        the call, so a terminal current state is never rejected on its own status."""
        created = self._seed_req()
        self._walk_to(created.id, created, "superseded")
        path = self._path_for(created.id)
        metadata_before = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
        before = path.read_bytes()
        mtime_before = path.stat().st_mtime_ns

        result = set_status(id=created.id, type="req", status="superseded")

        self.assertIsInstance(result, ReqFrontmatter)
        self.assertNotIsInstance(result, InvalidStatusTransitionResult)
        self.assertEqual(result.status, "superseded")
        self.assertEqual(result.updated, metadata_before["updated"])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(path.stat().st_mtime_ns, mtime_before)

    def test_out_of_vocabulary_status_returns_invalid_status_result_not_transition_result(self) -> None:
        """ACC-005: an out-of-vocabulary target (``"bogus"``) still takes the pre-existing
        pre-load ``InvalidStatusResult`` channel (the full flat vocabulary, a distinct object
        type from the transition result) on any req, whatever its current state -- the two
        error surfaces stay distinct."""
        for state in ("draft", "accepted"):
            with self.subTest(state=state):
                created = self._seed_req()
                self._walk_to(created.id, created, state)
                path = self._path_for(created.id)
                before = path.read_text(encoding="utf-8")

                result = set_status(id=created.id, type="req", status="bogus")

                self.assertIsInstance(result, InvalidStatusResult)
                self.assertNotIsInstance(result, InvalidStatusTransitionResult)
                self.assertFalse(result.valid)
                self.assertEqual(result.type, "req")
                self.assertEqual(result.status, "bogus")
                expected_allowed = sorted(_ALLOWED_STATUSES)
                self.assertEqual(result.allowed_values, expected_allowed)
                self.assertEqual(
                    result.message,
                    f"Invalid status 'bogus' for type 'req'. Allowed values: {', '.join(expected_allowed)}",
                )
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_full_transition_matrix_over_the_seven_state_vocabulary(self) -> None:
        """ACC-001 (pilot pin): every (current, target) pair of req's 7x7 vocabulary is
        classified through the public ``set_status`` tool exactly as the landed table says --
        the diagonal is the no-op success (the machine never sees it), a table-allowed
        off-diagonal pair persists the move, and every other pair is rejected pre-write with
        the current-state-relative payload and the exact message form (normal or terminal)."""
        for current in sorted(_ALLOWED_STATUSES):
            for target in sorted(_ALLOWED_STATUSES):
                with self.subTest(current=current, target=target):
                    created = self._seed_req()
                    doc_id = created.id
                    self._walk_to(doc_id, created, current)
                    path = self._path_for(doc_id)
                    before = path.read_text(encoding="utf-8")

                    result = set_status(id=doc_id, type="req", status=target)

                    if target == current:
                        self.assertIsInstance(result, ReqFrontmatter)
                        self.assertEqual(result.status, current)
                        self.assertEqual(path.read_text(encoding="utf-8"), before)
                    elif target in _STATUS_TRANSITIONS[current]:
                        self.assertIsInstance(result, ReqFrontmatter)
                        self.assertEqual(result.status, target)
                        on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                        self.assertEqual(on_disk_metadata["status"], target)
                    else:
                        self.assertIsInstance(result, InvalidStatusTransitionResult)
                        self.assertEqual(result.type, "req")
                        self.assertEqual(result.from_status, current)
                        self.assertEqual(result.to_status, target)
                        allowed_values = sorted(_STATUS_TRANSITIONS[current])
                        self.assertEqual(result.allowed_values, allowed_values)
                        if allowed_values:
                            expected_message = (
                                f"Invalid status transition '{current}' -> '{target}' for type 'req'. "
                                f"Allowed from '{current}': {', '.join(allowed_values)}"
                            )
                        else:
                            expected_message = (
                                f"Invalid status transition '{current}' -> '{target}' for type 'req'. "
                                f"Status '{current}' is terminal (no outgoing transitions)."
                            )
                        self.assertEqual(result.message, expected_message)
                        self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
