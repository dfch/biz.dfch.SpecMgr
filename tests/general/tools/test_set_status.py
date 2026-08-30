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

"""Tests for the generic ``set_status`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 4).

Parameterized over all nine document types (ACC-004); seeds a real,
persisted document per type -- the eight whole-body domains via the
domain's own ``create_<d>`` tool in a temp ``SPECMGR_DOCS_DIR`` (mirroring
the fixture strategy of ``tests/general/tools/test_update.py``), the ADR
by rendering a minimal valid model into a temp ``SPECMGR_ADR_DIR`` -- and
covers: status changed + ``updated`` bumped (microsecond timestamp) + body
untouched (eight domains: raw body byte-identical; ADR: re-render round-
trip equal apart from status); each domain's closed-vocabulary
enforcement (positive value from the domain's own ``_ALLOWED_STATUSES``;
negative value valid in one domain but invalid in the tested one -- each a
``pydantic.ValidationError`` with the file left byte-identical on disk);
the ADR-only ``superseded_by`` composition (``"superseded by X"`` in the
file) and the guard that rejects it for every non-``adr`` type *before*
any file access; and the per-domain not-found errors for an unknown id.

The per-type case data ties each ``valid_status``/``invalid_status`` pair
to the domain's own closed set (the authoritative source of truth in
``models/<v>/frontmatter.py`` -- imported as a private name here on
purpose) -- the case-data test asserts the membership relations rather
than trusting the pair literals.
"""

from __future__ import annotations

import re
import tempfile
import textwrap
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from unittest import mock

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError
from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_ALLOWED_STATUSES
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, parse_adr, render_adr
from biz.dfch.specmgr.models.adr.v1.frontmatter import _FIXED_STATUSES as _ADR_ALLOWED_STATUSES
from biz.dfch.specmgr.prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_ALLOWED_STATUSES
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_ALLOWED_STATUSES
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_ALLOWED_STATUSES
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_ALLOWED_STATUSES
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_ALLOWED_STATUSES
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_ALLOWED_STATUSES
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_ALLOWED_STATUSES
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
from biz.dfch.specmgr.uc.tools.create_uc import create_uc

#: ISO-8601 microsecond timestamp shape (the ``updated`` bump precision).
_MICROSECOND_TIMESTAMP = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}"

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

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

_UC_MINIMAL_BODY = textwrap.dedent(
    """\
    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    Summary

    ### Preconditions

    - We know Buyer

    ### Success End Condition

    - Buyer has goods

    ### Primary Actor

    Buyer.

    ### Trigger

    Purchase request comes in.

    ## Main Success Scenario

    1. Buyer calls in with a purchase request.
    2. Company creates order in system.
    """
)

_TSK_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### Kickoff

    Started the task list.
    """
)

_QA_MINIMAL_BODY = textwrap.dedent(
    """\
    # Some QA Title

    ## General

    ### Introduction

    Some intro text.

    ### Raw Requirements

    Some raw requirements text.

    ## Elicitation Context

    ## Functional Suitability

    ## Performance Efficiency

    ## Compatibility

    ## Interaction Capability

    ## Reliability

    ## Security

    ## Maintainability

    ## Flexibility

    ## Safety
    """
)

_PRB_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is wrong.

    ## Gap

    There is a gap.

    ## Future State

    It will be fixed.
    """
)

_GOL_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_RSK_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Risk

    ## Cause

    A root condition.

    ## Trigger

    An event that sets the risk in motion.

    ## Consequence

    A bounded consequence.

    ## Scope

    - Sample subsystem

    ## Initial Assessment

    ### Probability 4

    ### Impact 3

    ## Strategy

    reduce

    ## Mitigation

    Sample treatment measures.

    ## Residual Assessment

    ### Probability 2

    ### Impact 3
    """
)

_DEC_MINIMAL_BODY = textwrap.dedent(
    """\
    # Title of the Decision

    ## Context and Problem Statement

    Something is wrong with the status quo.

    ## Decision Outcome

    We chose the structured arrangement.
    """
)

_SOP_MINIMAL_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.
    """
)


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eight whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    minimal_body: str
    #: A value from the domain's OWN closed set (the positive vocabulary case).
    valid_status: str
    #: A value valid in one other domain but outside this one's closed set
    #: (the negative vocabulary case).
    invalid_status: str
    #: The domain's own closed set (the source of truth, imported above).
    allowed_statuses: frozenset[str]


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        not_found_error=ReqNotFoundError,
        minimal_body=_REQ_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="open",
        allowed_statuses=_REQ_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
        minimal_body=_UC_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="implemented",
        allowed_statuses=_UC_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        minimal_body=_TSK_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_TSK_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
        minimal_body=_QA_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_QA_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
        minimal_body=_PRB_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_PRB_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
        minimal_body=_GOL_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="open",
        allowed_statuses=_GOL_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
        minimal_body=_RSK_MINIMAL_BODY,
        valid_status="mitigating",
        invalid_status="implemented",
        allowed_statuses=_RSK_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
        minimal_body=_DEC_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="implemented",
        allowed_statuses=_DEC_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="sop",
        create=create_sop,
        not_found_error=SopNotFoundError,
        minimal_body=_SOP_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_SOP_ALLOWED_STATUSES,
    ),
]

_ADR_ID = "adr-test-id"
_ADR_SEED_BODY = AdrBody(
    title="A title",
    context_and_problem_statement="Context.",
    considered_options="Options.",
    decision_outcome="Outcome.",
)


class TempDocsDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via SPECMGR_DOCS_DIR and the ADR base dir via SPECMGR_ADR_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.adr_dir = self.docs_root / "adr"
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {DOCS_DIR_ENV_VAR: str(self.docs_root), ADR_DIR_ENV_VAR: str(self.adr_dir)},
            )
        )

    def _doc_path(self, case: _Case) -> Path:
        """The single on-disk document file seeded for ``case``."""
        matches = list((self.docs_root / case.doc_type).glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def _seed(self, case: _Case, body: str) -> Any:
        """Create a real, persisted document from ``body`` and return it."""
        result = case.create(body)
        return result

    def _seed_adr(self, id_: str = _ADR_ID) -> Path:
        """Write a minimal, valid ADR (id ``id_``) to the temp ADR dir and return its path."""
        path = self.adr_dir / f"{id_}.md"
        path.write_text(render_adr(Adr(frontmatter=AdrFrontmatter(id=id_), body=_ADR_SEED_BODY)), encoding="utf-8")
        return path


class TestSetStatusWholeBodyDomains(TempDocsDirTestCase):
    """ACC-004: the eight whole-body domains -- status changed, ``updated`` bumped, body untouched."""

    def test_case_data_matches_the_domains_own_closed_sets(self) -> None:
        """Each ``valid_status``/``invalid_status`` pair must be exactly as claimed against the domain's own set."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self.assertIn(case.valid_status, case.allowed_statuses)
                self.assertNotIn(case.invalid_status, case.allowed_statuses)
        self.assertIn("accepted", _ADR_ALLOWED_STATUSES)
        self.assertNotIn("implemented", _ADR_ALLOWED_STATUSES)

    def test_changes_status_bumps_updated_leaves_body_untouched(self) -> None:
        """A domain-valid status must change ``status`` on disk, bump ``updated``, and leave the raw body byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                doc_id = created.frontmatter.id
                path = self._doc_path(case)
                raw_body_before = body_text(path)

                result = set_status(id=doc_id, type=case.doc_type, status=case.valid_status)

                self.assertEqual(result.frontmatter.status, case.valid_status)
                self.assertEqual(result.frontmatter.id, created.frontmatter.id)
                self.assertEqual(result.frontmatter.type, case.doc_type)
                self.assertEqual(result.frontmatter.created, created.frontmatter.created)
                self.assertEqual(result.frontmatter.version, created.frontmatter.version)
                self.assertNotEqual(result.frontmatter.updated, created.frontmatter.updated)
                self.assertIsNotNone(re.fullmatch(_MICROSECOND_TIMESTAMP, result.frontmatter.updated))
                on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                self.assertEqual(on_disk_metadata["status"], case.valid_status)
                self.assertEqual(body_text(path), raw_body_before)

    def test_out_of_vocabulary_status_raises_validation_error_file_untouched(self) -> None:
        """A status valid in one domain but not the tested one must raise ``pydantic.ValidationError``, file byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(ValidationError):
                    set_status(id=created.frontmatter.id, type=case.doc_type, status=case.invalid_status)

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_superseded_by_with_non_adr_type_raises_value_error_file_untouched(self) -> None:
        """``superseded_by`` with any non-``adr`` type must raise ``ValueError``, leaving the file byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(ValueError) as ctx:
                    set_status(
                        id=created.frontmatter.id,
                        type=case.doc_type,
                        status=case.valid_status,
                        superseded_by="other-id",
                    )

                self.assertIn(case.doc_type, str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_unknown_id_raises_domain_not_found(self) -> None:
        """An unknown id must raise the domain's own not-found error."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._seed(case, case.minimal_body)

                with self.assertRaises(case.not_found_error):
                    set_status(id="no-such-id", type=case.doc_type, status=case.valid_status)


class TestSetStatusAdr(TempDocsDirTestCase):
    """ACC-004: the ADR -- status changed (render round-trip), body untouched, ``superseded_by`` composition."""

    def test_changes_plain_status_with_superseded_by_none(self) -> None:
        """A plain ADR status value must persist with ``superseded_by=None``, the body equal on re-parse (no ``updated`` field)."""
        path = self._seed_adr()
        before_adr = parse_adr(path.read_text(encoding="utf-8"))

        result = set_status(id=_ADR_ID, type="adr", status="accepted")

        self.assertEqual(result.frontmatter.status, "accepted")
        on_disk = parse_adr(path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.status, "accepted")
        self.assertEqual(on_disk.body, _ADR_SEED_BODY)
        self.assertEqual(on_disk.frontmatter.id, before_adr.frontmatter.id)
        self.assertEqual(on_disk.frontmatter.version, before_adr.frontmatter.version)
        self.assertEqual(on_disk.frontmatter.date, before_adr.frontmatter.date)
        self.assertEqual(on_disk, result)

    def test_superseded_by_composes_status_string_in_file(self) -> None:
        """``superseded_by`` must compose the status as ``"superseded by X"`` in the file."""
        path = self._seed_adr()

        result = set_status(id=_ADR_ID, type="adr", status="accepted", superseded_by="other-decision")

        self.assertEqual(result.frontmatter.status, "superseded by other-decision")
        on_disk = parse_adr(path.read_text(encoding="utf-8"))
        self.assertEqual(on_disk.frontmatter.status, "superseded by other-decision")

    def test_out_of_vocabulary_status_raises_validation_error_file_untouched(self) -> None:
        """A status valid in one domain but not ADR's must raise ``pydantic.ValidationError``, file byte-identical."""
        path = self._seed_adr()
        before = path.read_text(encoding="utf-8")

        with self.assertRaises(ValidationError):
            set_status(id=_ADR_ID, type="adr", status="implemented")

        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_unknown_id_raises_adr_not_found(self) -> None:
        """An unknown id must raise ``AdrNotFoundError``."""
        self._seed_adr()

        with self.assertRaises(AdrNotFoundError):
            set_status(id="no-such-id", type="adr", status="accepted")


class TestSetStatusSupersededByGuard(TempDocsDirTestCase):
    """The ``superseded_by`` guard must fire before any file access -- even for an unknown id."""

    def test_unknown_id_with_superseded_by_raises_value_error_not_not_found(self) -> None:
        """``set_status("no-such-id", <non-adr type>, status, superseded_by=...)`` must raise ``ValueError``, not the domain not-found."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                with self.assertRaises(ValueError):
                    set_status(
                        id="no-such-id",
                        type=case.doc_type,
                        status=case.valid_status,
                        superseded_by="other-id",
                    )


if __name__ == "__main__":
    unittest.main()
