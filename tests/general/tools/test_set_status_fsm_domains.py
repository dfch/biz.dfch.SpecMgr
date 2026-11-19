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

"""End-to-end tests of the generic ``set_status`` tool's status state machine enforcement for
the remaining whole-body domains (feat-108-fsm Phase 120, Task 120.110, ACC-001/ACC-002/
ACC-003/ACC-004/ACC-005, GitHub issue #108).

The sibling home of the pilot's own ``tests/general/tools/test_set_status_fsm_req.py``
(``req`` stays there): the per-domain e2e coverage of the Phase 120 rollout, in one module
over every whole-body domain except the pilot. Mirrors the fixture strategy of
``tests/general/tools/test_set_status.py``: a temp ``SPECMGR_DOCS_DIR`` (via
``DOCS_DIR_ENV_VAR``) plus a temp ``SPECMGR_FEAT_DIR`` (via ``FEAT_DIR_ENV_VAR`` --
``feat``'s folder-per-document addressing needs its own base directory), a real document
per domain seeded through the domain's own ``create_<d>`` tool (fresh status the domain's
own create status), the public ``set_status(id, type, ...)`` entry point, and the on-disk
file as the authority (every case asserts the file state, not just the return value).

Per domain, over the domain's own vocabulary and landed table (the spec data below is
pinned to the central aggregation's own entries, so it cannot drift from the source of
truth): the FULL N x N transition matrix through the public tool (every (current, target)
pair: the diagonal is the no-op success with the file untouched, a table-allowed pair
persists the move, every other pair is rejected pre-write with the current-state-relative
``allowed_values`` and the exact message form -- normal or terminal -- and the file
byte-identical); one named multi-step CYCLE walk including a back edge (the per-domain
segment of ACC-003); one out-of-vocabulary ``set_status`` returning the distinct pre-load
``InvalidStatusResult`` (the full flat vocabulary, exact message), file untouched; and the
no-op-before-check pin on the domain's most "final-feeling" state (success, no write, no
``updated`` bump -- so even a terminal current state, where one exists, is never rejected
on its own status).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from unittest import mock
from uuid import uuid4

import frontmatter

from biz.dfch.specmgr.dec.models.v1 import DecFrontmatter
from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
from biz.dfch.specmgr.dec.models.v1.frontmatter import _STATUS_TRANSITIONS as _DEC_STATUS_TRANSITIONS
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.feat.models.v1 import FeatFrontmatter
from biz.dfch.specmgr.feat.models.v1.frontmatter import _ALLOWED_STATUSES as _FEAT_ALLOWED_STATUSES
from biz.dfch.specmgr.feat.models.v1.frontmatter import _STATUS_TRANSITIONS as _FEAT_STATUS_TRANSITIONS
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.models import InvalidStatusResult, InvalidStatusTransitionResult, ValidateResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.general.tools._status_fsm import _STATUS_TRANSITIONS_BY_TYPE
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.gol.models.v1 import GolFrontmatter
from biz.dfch.specmgr.gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_ALLOWED_STATUSES
from biz.dfch.specmgr.gol.models.v1.frontmatter import _STATUS_TRANSITIONS as _GOL_STATUS_TRANSITIONS
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.prb.models.v1 import PrbFrontmatter
from biz.dfch.specmgr.prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_ALLOWED_STATUSES
from biz.dfch.specmgr.prb.models.v1.frontmatter import _STATUS_TRANSITIONS as _PRB_STATUS_TRANSITIONS
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.models.v2 import QaFrontmatter
from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_ALLOWED_STATUSES
from biz.dfch.specmgr.qa.models.v2.frontmatter import _STATUS_TRANSITIONS as _QA_STATUS_TRANSITIONS
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.rsk.models.v1 import RskFrontmatter
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_ALLOWED_STATUSES
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _STATUS_TRANSITIONS as _RSK_STATUS_TRANSITIONS
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.set.models.v1 import SetFrontmatter
from biz.dfch.specmgr.set.models.v1.frontmatter import _ALLOWED_STATUSES as _SET_ALLOWED_STATUSES
from biz.dfch.specmgr.set.models.v1.frontmatter import _STATUS_TRANSITIONS as _SET_STATUS_TRANSITIONS
from biz.dfch.specmgr.set.tools.create_set import create_set
from biz.dfch.specmgr.sop.models.v1 import SopFrontmatter
from biz.dfch.specmgr.sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_ALLOWED_STATUSES
from biz.dfch.specmgr.sop.models.v1.frontmatter import _STATUS_TRANSITIONS as _SOP_STATUS_TRANSITIONS
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.sysrs.models.v1 import SysrsFrontmatter
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import _ALLOWED_STATUSES as _SYSRS_ALLOWED_STATUSES
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import _STATUS_TRANSITIONS as _SYSRS_STATUS_TRANSITIONS
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.tsk.models.v1 import TskFrontmatter
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_ALLOWED_STATUSES
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _STATUS_TRANSITIONS as _TSK_STATUS_TRANSITIONS
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.txt.models.v1 import TxtFrontmatter
from biz.dfch.specmgr.txt.models.v1.frontmatter import _ALLOWED_STATUSES as _TXT_ALLOWED_STATUSES
from biz.dfch.specmgr.txt.models.v1.frontmatter import _STATUS_TRANSITIONS as _TXT_STATUS_TRANSITIONS
from biz.dfch.specmgr.txt.tools.create_txt import create_txt
from biz.dfch.specmgr.uc.models.v2 import UcFrontmatter
from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_ALLOWED_STATUSES
from biz.dfch.specmgr.uc.models.v2.frontmatter import _STATUS_TRANSITIONS as _UC_STATUS_TRANSITIONS
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.vcr.models.v1 import VcrFrontmatter
from biz.dfch.specmgr.vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_ALLOWED_STATUSES
from biz.dfch.specmgr.vcr.models.v1.frontmatter import _STATUS_TRANSITIONS as _VCR_STATUS_TRANSITIONS
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

from .test_set_status import (
    _DEC_MINIMAL_BODY,
    _FEAT_MINIMAL_BODY,
    _GOL_MINIMAL_BODY,
    _PRB_MINIMAL_BODY,
    _QA_MINIMAL_BODY,
    _RSK_MINIMAL_BODY,
    _SOP_MINIMAL_BODY,
    _SYSRS_MINIMAL_BODY,
    _TSK_MINIMAL_BODY,
    _TXT_MINIMAL_BODY,
    _UC_MINIMAL_BODY,
    _VCR_MINIMAL_BODY,
)

#: A well-formed canonical UUID for the ``set`` fixture's own ``## Items`` bullet (shape-only:
#: ``set``'s parser checks the reference shape, not the target's existence on disk).
_SET_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"

#: A minimal, valid ``set`` body (H1, the mandatory opaque ``## Description``, one ``## Items``
#: bullet in the shared reference shape) -- ``test_set_status.py`` carries no ``set`` case
#: (its own pre-existing gap), so this fixture follows ``set``'s packaged example shape.
_SET_MINIMAL_BODY = textwrap.dedent(
    f"""\
    # Sample Bundle

    ## Description

    A convenience bundle of the sample program's artifacts.

    ## Items

    - GOL {_SET_GOL_ID}: A goal
    """
)


def _create_feat_unique(body: str) -> FeatFrontmatter:
    """Seed a ``feat`` document with a unique caller-chosen id (``feat-0-<hex>``).

    ``create_feat``'s own default id derives from the body's H1 slug, so repeated seeds of
    the same minimal body would collide (``FileExistsError``); a per-seed unique id keeps
    every seed independent while staying inside ``feat``'s own ``feat-NNN-slug`` id shape
    (``models.md._cross_reference.FEAT_ID_PATTERN``).
    """
    result = create_feat(body, id=f"feat-0-{uuid4().hex}")
    assert not isinstance(result, ValidateResult), result
    assert isinstance(result, FeatFrontmatter), type(result)
    return result


@dataclass(frozen=True)
class _FsmDomainSpec:
    """Everything the parameterized e2e pins need to drive one whole-body domain generically
    (the sibling of ``test_set_status.py``'s own ``_Case``; ``req`` stays in the pilot's own
    module, so every other whole-body domain is covered here)."""

    doc_type: str
    create: Callable[[str], Any]
    frontmatter_type: type
    minimal_body: str
    #: The domain's own closed set (the source of truth, imported from the frontmatter module).
    allowed_statuses: frozenset[str]
    #: The domain's own landed state machine (imported from the frontmatter module; pinned
    #: against the central aggregation's own entry in ``TestFsmDomainSpecs``).
    status_transitions: dict[str, frozenset[str]]
    #: The status a freshly created (persisted) document is in (``create_*`` takes no status
    #: argument: ``rsk`` is born ``open``, ``feat`` is born ``planning``, every other domain
    #: ``draft``).
    start_status: str
    #: An allowed walk from the create status to every one of the domain's states (the tests'
    #: precondition: any state is reachable without a rejected transition).
    walks_from_start: dict[str, tuple[str, ...]]
    #: A named multi-step walk from the create status including a back edge (ACC-003's
    #: per-domain segment).
    cycle: tuple[str, ...]
    #: A value valid in one other domain but outside this one's closed set (the negative
    #: vocabulary case, mirroring ``test_set_status.py``'s own per-domain picks).
    out_of_vocab: str
    #: The domain's most "final-feeling" state -- the no-op-before-check pin's target.
    noop_state: str


_SPECS: tuple[_FsmDomainSpec, ...] = (
    _FsmDomainSpec(
        doc_type="uc",
        create=create_uc,
        frontmatter_type=UcFrontmatter,
        minimal_body=_UC_MINIMAL_BODY,
        allowed_statuses=_UC_ALLOWED_STATUSES,
        status_transitions=_UC_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "proposed": ("proposed",),
            "accepted": ("proposed", "accepted"),
            "deprecated": ("proposed", "accepted", "deprecated"),
            "superseded": ("proposed", "accepted", "superseded"),
        },
        cycle=("proposed", "draft", "proposed", "accepted"),
        out_of_vocab="implemented",
        noop_state="superseded",
    ),
    _FsmDomainSpec(
        doc_type="tsk",
        create=create_tsk,
        frontmatter_type=TskFrontmatter,
        minimal_body=_TSK_MINIMAL_BODY,
        allowed_statuses=_TSK_ALLOWED_STATUSES,
        status_transitions=_TSK_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "active": ("active",),
            "done": ("active", "done"),
            "cancelled": ("cancelled",),
        },
        cycle=("active", "done", "active", "cancelled"),
        out_of_vocab="implemented",
        noop_state="cancelled",
    ),
    _FsmDomainSpec(
        doc_type="qa",
        create=create_qa,
        frontmatter_type=QaFrontmatter,
        minimal_body=_QA_MINIMAL_BODY,
        allowed_statuses=_QA_ALLOWED_STATUSES,
        status_transitions=_QA_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "active": ("active",),
            "done": ("active", "done"),
            "cancelled": ("cancelled",),
        },
        cycle=("active", "done", "active", "cancelled"),
        out_of_vocab="implemented",
        noop_state="cancelled",
    ),
    _FsmDomainSpec(
        doc_type="prb",
        create=create_prb,
        frontmatter_type=PrbFrontmatter,
        minimal_body=_PRB_MINIMAL_BODY,
        allowed_statuses=_PRB_ALLOWED_STATUSES,
        status_transitions=_PRB_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "active": ("active",),
            "resolved": ("active", "resolved"),
            "cancelled": ("cancelled",),
        },
        cycle=("active", "resolved", "active", "cancelled"),
        out_of_vocab="implemented",
        noop_state="cancelled",
    ),
    _FsmDomainSpec(
        doc_type="gol",
        create=create_gol,
        frontmatter_type=GolFrontmatter,
        minimal_body=_GOL_MINIMAL_BODY,
        allowed_statuses=_GOL_ALLOWED_STATUSES,
        status_transitions=_GOL_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "proposed": ("proposed",),
            "accepted": ("proposed", "accepted"),
            "rejected": ("rejected",),
            "implemented": ("proposed", "accepted", "implemented"),
            "superseded": ("proposed", "accepted", "superseded"),
            "deprecated": ("proposed", "accepted", "deprecated"),
        },
        cycle=("proposed", "draft", "proposed", "accepted"),
        out_of_vocab="open",
        noop_state="deprecated",
    ),
    _FsmDomainSpec(
        doc_type="rsk",
        create=create_rsk,
        frontmatter_type=RskFrontmatter,
        minimal_body=_RSK_MINIMAL_BODY,
        allowed_statuses=_RSK_ALLOWED_STATUSES,
        status_transitions=_RSK_STATUS_TRANSITIONS,
        start_status="open",
        walks_from_start={
            "open": (),
            "mitigating": ("mitigating",),
            "accepted": ("accepted",),
            "occurred": ("occurred",),
            "closed": ("mitigating", "closed"),
            "dropped": ("dropped",),
        },
        cycle=("mitigating", "open", "mitigating", "closed", "occurred"),
        out_of_vocab="implemented",
        noop_state="dropped",
    ),
    _FsmDomainSpec(
        doc_type="dec",
        create=create_dec,
        frontmatter_type=DecFrontmatter,
        minimal_body=_DEC_MINIMAL_BODY,
        allowed_statuses=_DEC_ALLOWED_STATUSES,
        status_transitions=_DEC_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "proposed": ("proposed",),
            "accepted": ("proposed", "accepted"),
            "rejected": ("rejected",),
            "superseded": ("proposed", "accepted", "superseded"),
            "deprecated": ("proposed", "accepted", "deprecated"),
        },
        cycle=("proposed", "draft", "proposed", "accepted"),
        out_of_vocab="implemented",
        noop_state="deprecated",
    ),
    _FsmDomainSpec(
        doc_type="sop",
        create=create_sop,
        frontmatter_type=SopFrontmatter,
        minimal_body=_SOP_MINIMAL_BODY,
        allowed_statuses=_SOP_ALLOWED_STATUSES,
        status_transitions=_SOP_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "review": ("review",),
            "approved": ("approved",),
            "active": ("approved", "active"),
            "retired": ("approved", "retired"),
        },
        cycle=("review", "draft", "review", "approved", "active", "retired"),
        out_of_vocab="implemented",
        noop_state="retired",
    ),
    _FsmDomainSpec(
        doc_type="feat",
        create=_create_feat_unique,
        frontmatter_type=FeatFrontmatter,
        minimal_body=_FEAT_MINIMAL_BODY,
        allowed_statuses=_FEAT_ALLOWED_STATUSES,
        status_transitions=_FEAT_STATUS_TRANSITIONS,
        start_status="planning",
        walks_from_start={
            "planning": (),
            "progress": ("progress",),
            "review": ("progress", "review"),
            "done": ("progress", "review", "done"),
        },
        # The plan's ACC-003 example segment (`review` -> `done` -> `progress` -> `done`) names
        # `progress` -> `done`, which the locked feat table does not allow (`progress`:
        # [review, planning]); the machine is locked (user-approved), so the walk takes the
        # minimal legal back-edge to `done` through `review` instead (feat-108-fsm Phase 120,
        # Decisions Made): `planning` -> `progress` -> `review` -> `done` -> `review` -> `done`.
        cycle=("progress", "review", "done", "review", "done"),
        out_of_vocab="draft",
        noop_state="done",
    ),
    _FsmDomainSpec(
        doc_type="vcr",
        create=create_vcr,
        frontmatter_type=VcrFrontmatter,
        minimal_body=_VCR_MINIMAL_BODY,
        allowed_statuses=_VCR_ALLOWED_STATUSES,
        status_transitions=_VCR_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "progress": ("progress",),
            "complete": ("progress", "complete"),
            "approved": ("progress", "complete", "approved"),
        },
        cycle=("progress", "draft", "progress", "complete", "approved", "progress"),
        out_of_vocab="accepted",
        noop_state="approved",
    ),
    _FsmDomainSpec(
        doc_type="sysrs",
        create=create_sysrs,
        frontmatter_type=SysrsFrontmatter,
        minimal_body=_SYSRS_MINIMAL_BODY,
        allowed_statuses=_SYSRS_ALLOWED_STATUSES,
        status_transitions=_SYSRS_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "review": ("review",),
            "approved": ("approved",),
            "active": ("approved", "active"),
            "retired": ("approved", "retired"),
        },
        cycle=("review", "draft", "review", "approved", "active", "retired"),
        out_of_vocab="accepted",
        noop_state="retired",
    ),
    _FsmDomainSpec(
        doc_type="txt",
        create=create_txt,
        frontmatter_type=TxtFrontmatter,
        minimal_body=_TXT_MINIMAL_BODY,
        allowed_statuses=_TXT_ALLOWED_STATUSES,
        status_transitions=_TXT_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "progress": ("progress",),
            "done": ("progress", "done"),
        },
        cycle=("progress", "draft", "progress", "done", "progress"),
        out_of_vocab="accepted",
        noop_state="done",
    ),
    _FsmDomainSpec(
        doc_type="set",
        create=create_set,
        frontmatter_type=SetFrontmatter,
        minimal_body=_SET_MINIMAL_BODY,
        allowed_statuses=_SET_ALLOWED_STATUSES,
        status_transitions=_SET_STATUS_TRANSITIONS,
        start_status="draft",
        walks_from_start={
            "draft": (),
            "progress": ("progress",),
            "review": ("review",),
            "done": ("review", "done"),
        },
        cycle=("progress", "draft", "progress", "review", "done", "progress"),
        out_of_vocab="accepted",
        noop_state="done",
    ),
)


class TestFsmDomainSpecs(unittest.TestCase):
    """The spec data itself is pinned to the landed machines: the specs cover exactly the
    remaining whole-body domains, their table/vocabulary copies ARE the central aggregation's
    own entries (no drift between this module and the source of truth), every walk and cycle
    step is table-allowed and every state is reachable, and the out-of-vocabulary value is
    genuinely foreign to its own domain while valid in another."""

    def test_specs_cover_exactly_the_remaining_whole_body_domains(self) -> None:
        expected = tuple(domain for domain in WHOLE_BODY_DOMAINS if domain != "req")

        self.assertEqual(tuple(spec.doc_type for spec in _SPECS), expected)

    def test_spec_tables_and_vocabularies_are_the_landed_constants(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                self.assertIs(spec.status_transitions, _STATUS_TRANSITIONS_BY_TYPE[spec.doc_type])
                self.assertEqual(set(spec.status_transitions), spec.allowed_statuses)

    def test_spec_walks_are_machine_legal_and_reach_every_state(self) -> None:
        for spec in _SPECS:
            table = spec.status_transitions
            self.assertEqual(set(spec.walks_from_start), set(table))
            for state in table:
                with self.subTest(domain=spec.doc_type, state=state):
                    current = spec.start_status
                    for step in spec.walks_from_start[state]:
                        self.assertIn(step, table[current], (spec.doc_type, current, step))
                        current = step
                    self.assertEqual(current, state)

    def test_spec_cycles_are_machine_legal_and_include_a_back_edge(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                table = spec.status_transitions
                current = spec.start_status
                for step in spec.cycle:
                    self.assertIn(step, table[current], (spec.doc_type, current, step))
                    current = step
                # a back edge: some step returns to a state already on the walk (the create
                # state or any earlier intermediate state)
                seen = {spec.start_status}
                has_back_edge = False
                for step in spec.cycle:
                    if step in seen:
                        has_back_edge = True
                    seen.add(step)
                self.assertTrue(has_back_edge, spec.doc_type)

    def test_spec_out_of_vocab_is_foreign_here_but_valid_in_another_domain(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                self.assertNotIn(spec.out_of_vocab, spec.allowed_statuses)
                others = [other.allowed_statuses for other in _SPECS if other is not spec]
                self.assertTrue(any(spec.out_of_vocab in vocabulary for vocabulary in others))

    def test_spec_start_and_noop_states_are_in_vocabulary_and_reachable(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                self.assertIn(spec.start_status, spec.allowed_statuses)
                self.assertIn(spec.noop_state, spec.allowed_statuses)
                self.assertIn(spec.noop_state, spec.walks_from_start)


class TempFsmDocsDirTestCase(unittest.TestCase):
    """Common fixture: a temp docs root set as ``SPECMGR_DOCS_DIR`` (the ``test_set_status.py``
    strategy) plus a temp feat base dir set as ``SPECMGR_FEAT_DIR`` (``feat``'s folder-per-
    document addressing needs its own base directory, the same split ``test_set_status.py``'s
    injection-case fixture uses), with the seeding/walk helpers for every spec'd domain."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {DOCS_DIR_ENV_VAR: str(self.docs_root), FEAT_DIR_ENV_VAR: str(self.feat_dir)},
            )
        )

    def _seed(self, spec: _FsmDomainSpec) -> Any:
        """Create a real, persisted document through the domain's own ``create_<d>`` tool (fresh
        status the spec's ``start_status``) and return its frontmatter."""
        created = spec.create(spec.minimal_body)
        assert not isinstance(created, ValidateResult), created
        self.assertIsInstance(created, spec.frontmatter_type)
        self.assertEqual(created.status, spec.start_status)
        result = created
        return result

    def _path_for(self, spec: _FsmDomainSpec, doc_id: str) -> Path:
        """The on-disk file of the spec's document with ``doc_id`` (``feat``: its folder's
        ``README.md``; every other domain: the flat ``<docs_root>/<doc_type>/`` file)."""
        if spec.doc_type == "feat":
            result = self.feat_dir / doc_id / "README.md"
        else:
            matches = list((self.docs_root / spec.doc_type).glob("*.md"))
            result = next(path for path in matches if doc_id in path.name)
        return result

    def _walk_to(self, spec: _FsmDomainSpec, doc_id: str, state: str) -> None:
        """Drive the freshly created (``start_status``) document to ``state`` through allowed
        transitions only (the spec's ``walks_from_start``), asserting each step's return shape
        and on-disk status (a no-op for the create state itself)."""
        path = self._path_for(spec, doc_id)
        for step in spec.walks_from_start[state]:
            with self.subTest(domain=spec.doc_type, step=step):
                result = set_status(id=doc_id, type=spec.doc_type, status=step)
                self.assertIsInstance(result, spec.frontmatter_type)
                self.assertEqual(result.status, step)
                on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                self.assertEqual(on_disk_metadata["status"], step)


class TestSetStatusFsmDomainsMatrix(TempFsmDocsDirTestCase):
    """Task 120.110 (ACC-001 per domain): every (current, target) pair of each domain's
    vocabulary is classified through the public ``set_status`` tool exactly as the landed
    table says -- the diagonal is the no-op success (the machine never sees it, the file
    untouched), a table-allowed off-diagonal pair persists the move, and every other pair is
    rejected pre-write with the current-state-relative ``allowed_values`` (sorted, pinned)
    and the exact message form (normal or terminal), file byte-identical."""

    def test_full_transition_matrix_over_each_domain_vocabulary(self) -> None:
        for spec in _SPECS:
            for current in sorted(spec.allowed_statuses):
                for target in sorted(spec.allowed_statuses):
                    with self.subTest(domain=spec.doc_type, current=current, target=target):
                        created = self._seed(spec)
                        doc_id = created.id
                        self._walk_to(spec, doc_id, current)
                        path = self._path_for(spec, doc_id)
                        before = path.read_text(encoding="utf-8")

                        result = set_status(id=doc_id, type=spec.doc_type, status=target)

                        if target == current:
                            self.assertIsInstance(result, spec.frontmatter_type)
                            self.assertEqual(result.status, current)
                            self.assertEqual(path.read_text(encoding="utf-8"), before)
                        elif target in spec.status_transitions[current]:
                            self.assertIsInstance(result, spec.frontmatter_type)
                            self.assertEqual(result.status, target)
                            on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                            self.assertEqual(on_disk_metadata["status"], target)
                        else:
                            self.assertIsInstance(result, InvalidStatusTransitionResult)
                            self.assertEqual(result.type, spec.doc_type)
                            self.assertEqual(result.from_status, current)
                            self.assertEqual(result.to_status, target)
                            allowed_values = sorted(spec.status_transitions[current])
                            self.assertEqual(result.allowed_values, allowed_values)
                            if allowed_values:
                                expected_message = (
                                    f"Invalid status transition '{current}' -> '{target}' for type "
                                    f"'{spec.doc_type}'. Allowed from '{current}': {', '.join(allowed_values)}"
                                )
                            else:
                                expected_message = (
                                    f"Invalid status transition '{current}' -> '{target}' for type "
                                    f"'{spec.doc_type}'. Status '{current}' is terminal (no outgoing transitions)."
                                )
                            self.assertEqual(result.message, expected_message)
                            self.assertEqual(path.read_text(encoding="utf-8"), before)


class TestSetStatusFsmDomainsCycles(TempFsmDocsDirTestCase):
    """Task 120.110 (ACC-003 per domain): each domain's named multi-step cycle walk (including
    a back edge) succeeds step by step through the public tool, ending in its final state on
    disk -- the machine is cycling-friendly in every domain, not just the pilot."""

    def test_named_cycle_walks_back_and_forth(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                created = self._seed(spec)
                doc_id = created.id
                path = self._path_for(spec, doc_id)

                for step in spec.cycle:
                    with self.subTest(domain=spec.doc_type, step=step):
                        result = set_status(id=doc_id, type=spec.doc_type, status=step)
                        self.assertIsInstance(result, spec.frontmatter_type)
                        self.assertEqual(result.status, step)
                        on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                        self.assertEqual(on_disk_metadata["status"], step)


class TestSetStatusFsmDomainsOutOfVocabulary(TempFsmDocsDirTestCase):
    """Task 120.110 (ACC-005 per domain): an out-of-vocabulary target (valid in another
    domain, not this one) still takes the pre-existing pre-load ``InvalidStatusResult``
    channel (the full flat vocabulary, a distinct object type from the transition result,
    the exact message) on a fresh document, file untouched -- the two error surfaces stay
    distinct in every domain, not just the pilot."""

    def test_out_of_vocabulary_status_returns_invalid_status_result_not_transition_result(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                created = self._seed(spec)
                doc_id = created.id
                path = self._path_for(spec, doc_id)
                before = path.read_text(encoding="utf-8")

                result = set_status(id=doc_id, type=spec.doc_type, status=spec.out_of_vocab)

                self.assertIsInstance(result, InvalidStatusResult)
                self.assertNotIsInstance(result, InvalidStatusTransitionResult)
                self.assertFalse(result.valid)
                self.assertEqual(result.type, spec.doc_type)
                self.assertEqual(result.status, spec.out_of_vocab)
                expected_allowed = sorted(spec.allowed_statuses)
                self.assertEqual(result.allowed_values, expected_allowed)
                self.assertEqual(
                    result.message,
                    f"Invalid status '{spec.out_of_vocab}' for type '{spec.doc_type}'. "
                    f"Allowed values: {', '.join(expected_allowed)}",
                )
                self.assertEqual(path.read_text(encoding="utf-8"), before)


class TestSetStatusFsmDomainsNoop(TempFsmDocsDirTestCase):
    """Task 120.110 (ACC-004 per domain): the no-op-before-transition-check order pin on each
    domain's most "final-feeling" state -- requesting that state again returns the success
    shape (the domain's own frontmatter) with no write and no ``updated`` bump, so even a
    terminal current state (where one exists) is never rejected on its own status."""

    def test_noop_on_the_final_feeling_state_is_a_success_not_a_rejection(self) -> None:
        for spec in _SPECS:
            with self.subTest(domain=spec.doc_type):
                created = self._seed(spec)
                doc_id = created.id
                self._walk_to(spec, doc_id, spec.noop_state)
                path = self._path_for(spec, doc_id)
                metadata_before = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                before = path.read_bytes()
                mtime_before = path.stat().st_mtime_ns

                result = set_status(id=doc_id, type=spec.doc_type, status=spec.noop_state)

                self.assertIsInstance(result, spec.frontmatter_type)
                self.assertNotIsInstance(result, InvalidStatusTransitionResult)
                self.assertEqual(result.status, spec.noop_state)
                self.assertEqual(result.updated, metadata_before["updated"])
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(path.stat().st_mtime_ns, mtime_before)


if __name__ == "__main__":
    unittest.main()
