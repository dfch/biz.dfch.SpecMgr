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

Parameterized over all thirteen document types (ACC-004); seeds a real,
persisted document per type -- the twelve whole-body domains via the
domain's own ``create_<d>`` tool in a temp ``SPECMGR_DOCS_DIR`` (mirroring
the fixture strategy of ``tests/general/tools/test_update.py``), the ADR
by rendering a minimal valid model into a temp ``SPECMGR_ADR_DIR`` -- and
covers: status changed + ``updated`` bumped (microsecond timestamp) + body
untouched (twelve domains: raw body byte-identical; ADR: re-render round-
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

import importlib
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

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError, adr_base_dir
from biz.dfch.specmgr.dec.models.v1 import DecDocument, DecFrontmatter
from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.gol.models.v1 import GolDocument, GolFrontmatter
from biz.dfch.specmgr.gol.models.v1.frontmatter import _ALLOWED_STATUSES as _GOL_ALLOWED_STATUSES
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, parse_adr, render_adr
from biz.dfch.specmgr.models.adr.v1.frontmatter import _FIXED_STATUSES as _ADR_ALLOWED_STATUSES
from biz.dfch.specmgr.prb.models.v1 import PrbDocument, PrbFrontmatter
from biz.dfch.specmgr.prb.models.v1.frontmatter import _ALLOWED_STATUSES as _PRB_ALLOWED_STATUSES
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.models.v2 import QaDocument, QaFrontmatter
from biz.dfch.specmgr.qa.models.v2.frontmatter import _ALLOWED_STATUSES as _QA_ALLOWED_STATUSES
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError, qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.models.v1 import ReqDocument, ReqFrontmatter
from biz.dfch.specmgr.req.models.v1.frontmatter import _ALLOWED_STATUSES as _REQ_ALLOWED_STATUSES
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError, req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.models.v1 import RskDocument, RskFrontmatter
from biz.dfch.specmgr.rsk.models.v1.frontmatter import _ALLOWED_STATUSES as _RSK_ALLOWED_STATUSES
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError, rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sop.models.v1 import SopDocument, SopFrontmatter
from biz.dfch.specmgr.sop.models.v1.frontmatter import _ALLOWED_STATUSES as _SOP_ALLOWED_STATUSES
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError, sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.sysrs.models.v1 import SysrsDocument, SysrsFrontmatter
from biz.dfch.specmgr.sysrs.models.v1.frontmatter import _ALLOWED_STATUSES as _SYSRS_ALLOWED_STATUSES
from biz.dfch.specmgr.sysrs.tools._paths import SysrsNotFoundError, sysrs_base_dir
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.tsk.models.v1 import TskDocument, TskFrontmatter
from biz.dfch.specmgr.tsk.models.v1.frontmatter import _ALLOWED_STATUSES as _TSK_ALLOWED_STATUSES
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.models.v2 import UcDocument, UcFrontmatter
from biz.dfch.specmgr.uc.models.v2.frontmatter import _ALLOWED_STATUSES as _UC_ALLOWED_STATUSES
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.vcr.models.v1 import VcrDocument, VcrFrontmatter
from biz.dfch.specmgr.vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_ALLOWED_STATUSES
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

set_status_module = importlib.import_module("biz.dfch.specmgr.general.tools.set_status")

#: The canonical date+time timestamp shape (D4/D7) the ``updated`` bump must match: space-separated,
#: exactly three millisecond digits, `Z` or a signed `±HH:mm` offset.
_DATE_TIME_TIMESTAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})"

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

    ### 2026-08-19 - Kickoff

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

_VCR_MINIMAL_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes
    """
)

_SYSRS_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_SYSRS_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"

_SYSRS_MINIMAL_BODY = textwrap.dedent(
    f"""\
    # System Requirements Specification: Sample Document

    ## System Purpose

    Provision partner accounts.

    ## System Scope

    Onboarding only.

    ## Business Context and Goals

    ### Goals

    - GOL {_SYSRS_GOL_ID}: A goal

    ## System Overview

    ### System Context

    Context.

    ### System Functions

    Functions.

    ## Requirements

    ### Functional Suitability

    - REQ {_SYSRS_REQ_ID}: A requirement
    """
)


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the twelve whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    #: The domain's own frontmatter class -- the type ``set_status`` must return (feat-69).
    frontmatter_type: type
    #: The domain's own document (frontmatter+body wrapper) class -- what ``set_status`` must
    #: NOT return any more (feat-69).
    document_type: type
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
        frontmatter_type=ReqFrontmatter,
        document_type=ReqDocument,
        minimal_body=_REQ_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="open",
        allowed_statuses=_REQ_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
        frontmatter_type=UcFrontmatter,
        document_type=UcDocument,
        minimal_body=_UC_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="implemented",
        allowed_statuses=_UC_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        frontmatter_type=TskFrontmatter,
        document_type=TskDocument,
        minimal_body=_TSK_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_TSK_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
        frontmatter_type=QaFrontmatter,
        document_type=QaDocument,
        minimal_body=_QA_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_QA_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
        frontmatter_type=PrbFrontmatter,
        document_type=PrbDocument,
        minimal_body=_PRB_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_PRB_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
        frontmatter_type=GolFrontmatter,
        document_type=GolDocument,
        minimal_body=_GOL_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="open",
        allowed_statuses=_GOL_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
        frontmatter_type=RskFrontmatter,
        document_type=RskDocument,
        minimal_body=_RSK_MINIMAL_BODY,
        valid_status="mitigating",
        invalid_status="implemented",
        allowed_statuses=_RSK_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
        frontmatter_type=DecFrontmatter,
        document_type=DecDocument,
        minimal_body=_DEC_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="implemented",
        allowed_statuses=_DEC_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="sop",
        create=create_sop,
        not_found_error=SopNotFoundError,
        frontmatter_type=SopFrontmatter,
        document_type=SopDocument,
        minimal_body=_SOP_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_SOP_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="vcr",
        create=create_vcr,
        not_found_error=VcrNotFoundError,
        frontmatter_type=VcrFrontmatter,
        document_type=VcrDocument,
        minimal_body=_VCR_MINIMAL_BODY,
        valid_status="progress",
        invalid_status="accepted",
        allowed_statuses=_VCR_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="sysrs",
        create=create_sysrs,
        not_found_error=SysrsNotFoundError,
        frontmatter_type=SysrsFrontmatter,
        document_type=SysrsDocument,
        minimal_body=_SYSRS_MINIMAL_BODY,
        valid_status="review",
        invalid_status="accepted",
        allowed_statuses=_SYSRS_ALLOWED_STATUSES,
    ),
]

#: A well-formed canonical UUID (feat-38-39-41-43-44 Phase 4 added "adr" to ``_path_safety``'s
#: UUID-shaped domains, so this fixture id must be UUID-shaped, not a free-form string).
_ADR_ID = "0d8f4c2a-1b3e-4f5a-9c7d-2e6b8a0f1c3d"

#: A well-formed but non-existent canonical UUID, for the unknown-id not-found cases.
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"
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
    """ACC-004: the twelve whole-body domains -- status changed, ``updated`` bumped, body untouched."""

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
                doc_id = created.id
                path = self._doc_path(case)
                raw_body_before = body_text(path)

                result = set_status(id=doc_id, type=case.doc_type, status=case.valid_status)

                self.assertIsInstance(result, case.frontmatter_type)
                self.assertNotIsInstance(result, case.document_type)
                self.assertFalse(hasattr(result, "body"))
                self.assertEqual(result.status, case.valid_status)
                self.assertEqual(result.id, created.id)
                self.assertEqual(result.type, case.doc_type)
                self.assertEqual(result.created, created.created)
                self.assertEqual(result.version, created.version)
                self.assertNotEqual(result.updated, created.updated)
                self.assertIsNotNone(re.fullmatch(_DATE_TIME_TIMESTAMP, result.updated))
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
                    set_status(id=created.id, type=case.doc_type, status=case.invalid_status)

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
                        id=created.id,
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
                    set_status(id=_MISSING_UUID, type=case.doc_type, status=case.valid_status)


class TestSetStatusAdr(TempDocsDirTestCase):
    """ACC-004: the ADR -- status changed (render round-trip), body untouched, ``superseded_by`` composition."""

    def test_changes_plain_status_with_superseded_by_none(self) -> None:
        """A plain ADR status value must persist with ``superseded_by=None``, the body equal on re-parse (no ``updated`` field)."""
        path = self._seed_adr()
        before_adr = parse_adr(path.read_text(encoding="utf-8"))

        result = set_status(id=_ADR_ID, type="adr", status="accepted")

        # feat-69 regression: the ADR branch is explicitly out of scope for the
        # frontmatter-only response change -- set_status(type="adr", ...) must
        # keep returning the full `Adr` document, body included, unaffected.
        self.assertIsInstance(result, Adr)
        self.assertEqual(result.body, _ADR_SEED_BODY)
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
            set_status(id=_MISSING_UUID, type="adr", status="accepted")


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


@dataclass(frozen=True)
class _InjectionCase:
    """Per-type test data for ``_path_safety`` coverage (ACC-008), across all thirteen document types."""

    doc_type: str
    create: Callable[[str], Any]
    base_dir: Callable[[], Path]
    minimal_body: str
    valid_status: str
    #: A well-formed id of a *different* domain shape (feat-NNN-slug for the UUID domains, a UUID for feat).
    wrong_format_id: str


#: The pinned path-injection shapes (mirrors ``test_delete.py``'s own ``_TRAVERSAL_IDS``).
_TRAVERSAL_IDS = ("../x", "a/b", "a\\b", "..")

#: A well-formed feat-NNN-slug folder name (the wrong-format id for the twelve UUID domains).
_FEAT_SLUG_ID = "feat-36-delete"

#: A minimal, valid feat body (ACC-008's injection coverage: feat is the one whole-body domain
#: whose id shape differs from the eleven UUID domains, mirroring ``test_delete.py``'s own fixture).
_FEAT_MINIMAL_BODY = textwrap.dedent(
    """\
    # Feature: Example Widget

    ## Plan

    ### Overview

    Short description.

    ### Requirements

    - REQ-001: The widget must render within 200ms.

    ### Acceptance Criteria

    - [ ] ACC-001: Render time stays below 200ms.

    ### Scope

    #### Included

    - The widget component itself.

    #### Explicitly Out Of Scope

    - Mobile touch gestures.

    ### Task List

    #### Phase 0: Scaffolding

    - [x] Task 0.1: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)

_INJECTION_CASES: list[_InjectionCase] = [
    _InjectionCase("req", create_req, req_base_dir, _REQ_MINIMAL_BODY, "accepted", _FEAT_SLUG_ID),
    _InjectionCase("uc", create_uc, uc_base_dir, _UC_MINIMAL_BODY, "accepted", _FEAT_SLUG_ID),
    _InjectionCase("tsk", create_tsk, tsk_base_dir, _TSK_MINIMAL_BODY, "active", _FEAT_SLUG_ID),
    _InjectionCase("qa", create_qa, qa_base_dir, _QA_MINIMAL_BODY, "active", _FEAT_SLUG_ID),
    _InjectionCase("prb", create_prb, prb_base_dir, _PRB_MINIMAL_BODY, "active", _FEAT_SLUG_ID),
    _InjectionCase("gol", create_gol, gol_base_dir, _GOL_MINIMAL_BODY, "accepted", _FEAT_SLUG_ID),
    _InjectionCase("rsk", create_rsk, rsk_base_dir, _RSK_MINIMAL_BODY, "mitigating", _FEAT_SLUG_ID),
    _InjectionCase("dec", create_dec, dec_base_dir, _DEC_MINIMAL_BODY, "accepted", _FEAT_SLUG_ID),
    _InjectionCase("sop", create_sop, sop_base_dir, _SOP_MINIMAL_BODY, "active", _FEAT_SLUG_ID),
    _InjectionCase("vcr", create_vcr, vcr_base_dir, _VCR_MINIMAL_BODY, "progress", _FEAT_SLUG_ID),
    _InjectionCase("sysrs", create_sysrs, sysrs_base_dir, _SYSRS_MINIMAL_BODY, "review", _FEAT_SLUG_ID),
    _InjectionCase("feat", create_feat, feat_base_dir, _FEAT_MINIMAL_BODY, "progress", _MISSING_UUID),
]


class TempSetStatusInjectionDirTestCase(unittest.TestCase):
    """Common fixture for ACC-008: temp dirs for SPECMGR_DOCS_DIR, SPECMGR_FEAT_DIR, and
    SPECMGR_ADR_DIR (mirrors ``test_delete.py``'s ``TempDeleteDirTestCase``, since injection
    coverage spans all thirteen document types, feat and adr included)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.adr_dir = self.docs_root / "adr"
        self.adr_dir.mkdir(parents=True, exist_ok=True)
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {
                    DOCS_DIR_ENV_VAR: str(self.docs_root),
                    FEAT_DIR_ENV_VAR: str(self.feat_dir),
                    ADR_DIR_ENV_VAR: str(self.adr_dir),
                },
            )
        )

    def _doc_path(self, case: _InjectionCase, doc_id: str) -> Path:
        """The single on-disk document file/README.md path for ``case``'s just-seeded document."""
        if case.doc_type == "feat":
            result = feat_base_dir() / doc_id / "README.md"
        else:
            matches = list((self.docs_root / case.doc_type).glob("*.md"))
            self.assertEqual(len(matches), 1)
            result = matches[0]
        return result

    def _seed_adr(self, id_: str = _ADR_ID) -> Path:
        """Write a minimal, valid ADR (id ``id_``) to the temp ADR dir and return its path."""
        path = self.adr_dir / f"{id_}.md"
        path.write_text(render_adr(Adr(frontmatter=AdrFrontmatter(id=id_), body=_ADR_SEED_BODY)), encoding="utf-8")
        return path


class TestSetStatusInjection(TempSetStatusInjectionDirTestCase):
    """ACC-008: injection ids raise ValueError before any filesystem access, the seed untouched."""

    def test_injection_ids_raise_value_error_and_leave_the_seed_untouched(self) -> None:
        """Each pinned traversal shape and a wrong-format id must raise ValueError before dispatch, seed intact."""
        for case in _INJECTION_CASES:
            with self.subTest(doc_type=case.doc_type):
                created = case.create(case.minimal_body)
                doc_id = created.id
                path = self._doc_path(case, doc_id)
                before = path.read_text(encoding="utf-8")

                for bad_id in (*_TRAVERSAL_IDS, case.wrong_format_id):
                    with self.subTest(doc_type=case.doc_type, bad_id=bad_id):
                        with self.assertRaises(ValueError):
                            set_status(id=bad_id, type=case.doc_type, status=case.valid_status)
                        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_adr_injection_ids_raise_value_error_and_leave_the_seed_untouched(self) -> None:
        """The same, for type="adr" (feat-38-39-41-43-44 Phase 4 added adr to the UUID-shaped domains)."""
        path = self._seed_adr()
        before = path.read_text(encoding="utf-8")

        for bad_id in (*_TRAVERSAL_IDS, _FEAT_SLUG_ID):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(ValueError):
                    set_status(id=bad_id, type="adr", status="accepted")
                self.assertEqual(path.read_text(encoding="utf-8"), before)


class TestSetStatusAssertWithinSpy(TempSetStatusInjectionDirTestCase):
    """ACC-008: ``assert_within`` is actually invoked (not just present in source) during a valid set_status."""

    def test_assert_within_is_called_with_base_dir_and_resolved_path(self) -> None:
        """For each of the twelve whole-body domains, a valid status change must call ``assert_within(base_dir, path)``."""
        for case in _INJECTION_CASES:
            with self.subTest(doc_type=case.doc_type):
                created = case.create(case.minimal_body)
                doc_id = created.id
                path = self._doc_path(case, doc_id)
                base_dir = case.base_dir()

                with mock.patch.object(
                    set_status_module, "assert_within", wraps=set_status_module.assert_within
                ) as spy:
                    set_status(id=doc_id, type=case.doc_type, status=case.valid_status)

                spy.assert_any_call(base_dir, path)

    def test_assert_within_is_called_for_adr(self) -> None:
        """The same, for type="adr"."""
        path = self._seed_adr()

        with mock.patch.object(set_status_module, "assert_within", wraps=set_status_module.assert_within) as spy:
            set_status(id=_ADR_ID, type="adr", status="accepted")

        spy.assert_any_call(adr_base_dir(), path)


if __name__ == "__main__":
    unittest.main()
