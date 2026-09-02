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

"""Tests for the generic ``set_classification`` ``@mcp.tool()`` wrapper (feat-56-classification, Phase 2).

Parameterized over the eleven whole-body document types (``adr`` is out of
scope for this feature, unlike ``set_status``'s twelve); seeds a real,
persisted document per type via the domain's own ``create_<d>`` tool in a
temp ``SPECMGR_DOCS_DIR``/``SPECMGR_FEAT_DIR`` (mirroring the fixture
strategy of ``tests/general/tools/test_set_status.py``), and covers:
classification set + ``updated`` bumped (microsecond timestamp) + raw body
byte-identical (ACC-002); clearing classification back to ``None``/absent
via a blank or whitespace-only value (ACC-003); an invalid/unsupported
``type`` raising the same ``ValueError`` class the generic ``set_status``
tool raises for the same misuse (ACC-005); the per-domain not-found errors
for an unknown id; and ``_path_safety`` injection/wrong-format-id rejection
before any file access (mirroring ``test_set_status.py``'s own coverage).
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

from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError, qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError, req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError, rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError, sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

set_classification_module = importlib.import_module("biz.dfch.specmgr.general.tools.set_classification")

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


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eleven whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    base_dir: Callable[[], Path]
    not_found_error: type[Exception]
    minimal_body: str
    #: A well-formed id of a different domain shape (feat-NNN-slug for the UUID domains, a UUID for feat).
    wrong_format_id: str


#: A well-formed but non-existent canonical UUID, for the unknown-id not-found cases.
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: A well-formed feat-NNN-slug folder name (the wrong-format id for the ten UUID domains).
_FEAT_SLUG_ID = "feat-36-delete"

_CASES: list[_Case] = [
    _Case("req", create_req, req_base_dir, ReqNotFoundError, _REQ_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("uc", create_uc, uc_base_dir, UcNotFoundError, _UC_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("tsk", create_tsk, tsk_base_dir, TskNotFoundError, _TSK_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("qa", create_qa, qa_base_dir, QaNotFoundError, _QA_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("prb", create_prb, prb_base_dir, PrbNotFoundError, _PRB_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("gol", create_gol, gol_base_dir, GolNotFoundError, _GOL_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("rsk", create_rsk, rsk_base_dir, RskNotFoundError, _RSK_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("dec", create_dec, dec_base_dir, DecNotFoundError, _DEC_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("sop", create_sop, sop_base_dir, SopNotFoundError, _SOP_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("vcr", create_vcr, vcr_base_dir, VcrNotFoundError, _VCR_MINIMAL_BODY, _FEAT_SLUG_ID),
    _Case("feat", create_feat, feat_base_dir, Exception, _FEAT_MINIMAL_BODY, _MISSING_UUID),
]


class TempDocsDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via SPECMGR_DOCS_DIR and the feat base dir via SPECMGR_FEAT_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {DOCS_DIR_ENV_VAR: str(self.docs_root), FEAT_DIR_ENV_VAR: str(self.feat_dir)},
            )
        )

    def _doc_path(self, case: _Case, doc_id: str) -> Path:
        """The single on-disk document file/README.md path for ``case``'s just-seeded document."""
        if case.doc_type == "feat":
            result = feat_base_dir() / doc_id / "README.md"
        else:
            matches = list((self.docs_root / case.doc_type).glob("*.md"))
            self.assertEqual(len(matches), 1)
            result = matches[0]
        return result

    def _seed(self, case: _Case) -> Any:
        """Create a real, persisted document from ``case.minimal_body`` and return it."""
        result = case.create(case.minimal_body)
        return result


class TestSetClassificationWholeBodyDomains(TempDocsDirTestCase):
    """ACC-002/ACC-003: classification set/cleared, ``updated`` bumped, body untouched."""

    def test_sets_classification_bumps_updated_leaves_body_untouched(self) -> None:
        """Setting a classification must change it on disk, bump ``updated``, and leave the raw body byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                path = self._doc_path(case, doc_id)
                raw_body_before = body_text(path)

                result = set_classification(id=doc_id, type=case.doc_type, classification="Confidential")

                self.assertEqual(result.classification, "Confidential")
                self.assertEqual(result.id, created.frontmatter.id)
                self.assertEqual(result.type, case.doc_type)
                self.assertEqual(result.created, created.frontmatter.created)
                self.assertEqual(result.version, created.frontmatter.version)
                self.assertEqual(result.status, created.frontmatter.status)
                self.assertNotEqual(result.updated, created.frontmatter.updated)
                self.assertIsNotNone(re.fullmatch(_DATE_TIME_TIMESTAMP, result.updated))
                on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                self.assertEqual(on_disk_metadata["classification"], "Confidential")
                self.assertEqual(body_text(path), raw_body_before)

    def test_blank_classification_clears_back_to_none(self) -> None:
        """A blank/whitespace classification must clear the field back to ``None``/absent in the rendered YAML."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                path = self._doc_path(case, doc_id)

                set_classification(id=doc_id, type=case.doc_type, classification="Confidential")
                result = set_classification(id=doc_id, type=case.doc_type, classification="   ")

                self.assertIsNone(result.classification)
                on_disk_metadata = frontmatter.loads(path.read_text(encoding="utf-8")).metadata
                self.assertIsNone(on_disk_metadata.get("classification"))

    def test_unknown_id_raises_domain_not_found(self) -> None:
        """An unknown id must raise the domain's own not-found error."""
        for case in _CASES:
            if case.not_found_error is Exception:
                continue
            with self.subTest(doc_type=case.doc_type):
                self._seed(case)

                with self.assertRaises(case.not_found_error):
                    set_classification(id=_MISSING_UUID, type=case.doc_type, classification="Confidential")

    def test_feat_unknown_id_raises_not_found(self) -> None:
        """The ``feat`` domain's own not-found error must be raised for an unknown id."""
        self._seed(_CASES[-1])

        with self.assertRaises(Exception):
            set_classification(id="feat-999-does-not-exist", type="feat", classification="Confidential")


class TestSetClassificationInvalidType(TempDocsDirTestCase):
    """ACC-005: an unsupported ``type`` must raise the same error class ``set_status`` raises for the same misuse."""

    def test_unsupported_type_raises_value_error(self) -> None:
        """``set_classification(id, type="bogus", ...)`` must raise ``ValueError`` before any dispatch."""
        with self.assertRaises(ValueError):
            set_classification(id=_MISSING_UUID, type="bogus", classification="Confidential")

    def test_unsupported_type_matches_set_status_error_class(self) -> None:
        """The error class for an unsupported ``type`` must match ``set_status``'s own behavior for the same misuse."""
        from biz.dfch.specmgr.general.tools.set_status import set_status

        with self.assertRaises(ValueError) as classification_ctx:
            set_classification(id=_MISSING_UUID, type="bogus", classification="Confidential")
        with self.assertRaises(ValueError) as status_ctx:
            set_status(id=_MISSING_UUID, type="bogus", status="accepted")

        self.assertIs(type(classification_ctx.exception), type(status_ctx.exception))

    def test_adr_type_is_not_supported(self) -> None:
        """``type="adr"`` must be rejected -- ADR's separate frontmatter model is out of scope for this feature.

        ``adr`` is one of ``_path_safety``'s known UUID-shaped types, so ``validate_id`` accepts a
        well-formed UUID id for it (same as the generic ``update`` tool, which also excludes ``adr``
        from its own dispatch table); the rejection surfaces as a ``KeyError`` from the dispatch-table
        lookup itself, mirroring ``update``'s own undocumented-but-real behavior for ``type="adr"``.
        """
        with self.assertRaises(KeyError):
            set_classification(id=_MISSING_UUID, type="adr", classification="Confidential")


#: The pinned path-injection shapes (mirrors ``test_set_status.py``'s own ``_TRAVERSAL_IDS``).
_TRAVERSAL_IDS = ("../x", "a/b", "a\\b", "..")


class TestSetClassificationInjection(TempDocsDirTestCase):
    """Path-safety rejection: injection ids raise ValueError before any filesystem access, the seed untouched."""

    def test_injection_ids_raise_value_error_and_leave_the_seed_untouched(self) -> None:
        """Each pinned traversal shape and a wrong-format id must raise ValueError before dispatch, seed intact."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                path = self._doc_path(case, doc_id)
                before = path.read_text(encoding="utf-8")

                for bad_id in (*_TRAVERSAL_IDS, case.wrong_format_id):
                    with self.subTest(doc_type=case.doc_type, bad_id=bad_id):
                        with self.assertRaises(ValueError):
                            set_classification(id=bad_id, type=case.doc_type, classification="Confidential")
                        self.assertEqual(path.read_text(encoding="utf-8"), before)


class TestSetClassificationAssertWithinSpy(TempDocsDirTestCase):
    """``assert_within`` is actually invoked (not just present in source) during a valid set_classification."""

    def test_assert_within_is_called_with_base_dir_and_resolved_path(self) -> None:
        """For each of the eleven whole-body domains, a valid classification change must call ``assert_within``."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                path = self._doc_path(case, doc_id)
                base_dir = case.base_dir()

                with mock.patch.object(
                    set_classification_module, "assert_within", wraps=set_classification_module.assert_within
                ) as spy:
                    set_classification(id=doc_id, type=case.doc_type, classification="Confidential")

                spy.assert_any_call(base_dir, path)


if __name__ == "__main__":
    unittest.main()
