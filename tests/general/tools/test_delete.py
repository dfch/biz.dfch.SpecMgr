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

"""Tests for the generic ``delete`` ``@mcp.tool()`` wrapper (feat-36-delete, Phase 2).

Parameterized over all eleven whole-body document types
(ACC-001/ACC-004/ACC-005/ACC-006); seeds a real, persisted document per
type -- the ten flat domains via the domain's own ``create_<d>`` tool in a
temp ``SPECMGR_DOCS_DIR``, ``feat`` via its own ``create_feat`` in a temp
``SPECMGR_FEAT_DIR`` (mirroring the fixture strategy of
``tests/general/tools/test_set_status.py`` and
``tests/general/tools/test_update.py``) -- and covers: delete success
(the returned string is the deleted file path for the flat domains / the
deleted folder path for ``feat``, the file/folder is gone, and a
follow-up ``load_by_id`` raises the domain's own ``XNotFoundError``); the
``feat`` folder-per-document delete (the whole ``<base>/<id>/`` folder,
including a seeded ``history.md``, is removed); every path-injection id
(``../x``, ``a/b``, ``a\\b``, ``..``, and a wrong-format id) raising
``ValueError`` before any filesystem access with the seeded document left
intact; a well-formed but non-existent id raising the domain's own
``XNotFoundError``; a mocked ``Path.unlink``/``shutil.rmtree`` I/O failure
raising ``DeleteError`` (an ``OSError`` subclass) with the underlying
``OSError`` as ``__cause__`` and the resolved path in the message; and the
domain's own per-id lock entered around the resolve-then-delete sequence.
A registration smoke test (mirroring ``test_update.py``'s) verifies the
live ``mcp`` registration carries ``delete`` with the 11-value ``type``
enum.
"""

from __future__ import annotations

import asyncio
import importlib
import tempfile
import textwrap
import unittest
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.dec.tools._io import load_by_id as load_dec_by_id
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.feat.tools._io import load_by_id as load_feat_by_id
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.gol.tools._io import load_by_id as load_gol_by_id
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.prb.tools._io import load_by_id as load_prb_by_id
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.tools._io import load_by_id as load_qa_by_id
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError, qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.tools._io import load_by_id as load_req_by_id
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError, req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.tools._io import load_by_id as load_rsk_by_id
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError, rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sop.tools._io import load_by_id as load_sop_by_id
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError, sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.tsk.tools._io import load_by_id as load_tsk_by_id
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.tools._io import load_by_id as load_uc_by_id
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.vcr.tools._io import load_by_id as load_vcr_by_id
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

delete_module = importlib.import_module("biz.dfch.specmgr.general.tools.delete")
delete = delete_module.delete
DeleteError = delete_module.DeleteError

#: The feat document type name (the one folder-per-document domain).
_TYPE_FEAT = "feat"

#: The pinned path-injection shapes (ACC-005), in addition to each type's own wrong-format id.
_TRAVERSAL_IDS = ("../x", "a/b", "a\\b", "..")

#: A well-formed but non-existent canonical UUID (the unknown-id case for the ten UUID domains).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: A well-formed but non-existent feat-NNN-slug (the unknown-id case for feat).
_MISSING_FEAT_ID = "feat-999-no-such-feature"

#: A well-formed feat-NNN-slug folder name (the wrong-format id for the ten UUID domains).
_FEAT_SLUG_ID = "feat-36-delete"

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


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eleven whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    load_by_id: Callable[[Path, str], Any]
    base_dir: Callable[[], Path]
    not_found_error: type[Exception]
    minimal_body: str
    #: A well-formed id of a *different* domain shape (the wrong-format
    #: injection case: a ``feat-NNN-slug`` for the UUID domains, a UUID for
    #: ``feat``).
    wrong_format_id: str


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        load_by_id=load_req_by_id,
        base_dir=req_base_dir,
        not_found_error=ReqNotFoundError,
        minimal_body=_REQ_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        load_by_id=load_uc_by_id,
        base_dir=uc_base_dir,
        not_found_error=UcNotFoundError,
        minimal_body=_UC_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        load_by_id=load_tsk_by_id,
        base_dir=tsk_base_dir,
        not_found_error=TskNotFoundError,
        minimal_body=_TSK_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        load_by_id=load_qa_by_id,
        base_dir=qa_base_dir,
        not_found_error=QaNotFoundError,
        minimal_body=_QA_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        load_by_id=load_prb_by_id,
        base_dir=prb_base_dir,
        not_found_error=PrbNotFoundError,
        minimal_body=_PRB_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        load_by_id=load_gol_by_id,
        base_dir=gol_base_dir,
        not_found_error=GolNotFoundError,
        minimal_body=_GOL_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        load_by_id=load_rsk_by_id,
        base_dir=rsk_base_dir,
        not_found_error=RskNotFoundError,
        minimal_body=_RSK_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        load_by_id=load_dec_by_id,
        base_dir=dec_base_dir,
        not_found_error=DecNotFoundError,
        minimal_body=_DEC_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="sop",
        create=create_sop,
        load_by_id=load_sop_by_id,
        base_dir=sop_base_dir,
        not_found_error=SopNotFoundError,
        minimal_body=_SOP_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
    _Case(
        doc_type="feat",
        create=create_feat,
        load_by_id=load_feat_by_id,
        base_dir=feat_base_dir,
        not_found_error=FeatNotFoundError,
        minimal_body=_FEAT_MINIMAL_BODY,
        wrong_format_id=_MISSING_UUID,
    ),
    _Case(
        doc_type="vcr",
        create=create_vcr,
        load_by_id=load_vcr_by_id,
        base_dir=vcr_base_dir,
        not_found_error=VcrNotFoundError,
        minimal_body=_VCR_MINIMAL_BODY,
        wrong_format_id=_FEAT_SLUG_ID,
    ),
]


class TempDeleteDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via SPECMGR_DOCS_DIR and the feat base
    dir via SPECMGR_FEAT_DIR (the lifecycle is managed by ``enterContext``, per the sibling
    ``test_set_status.py``/``test_update.py`` fixture convention)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {DOCS_DIR_ENV_VAR: str(self.docs_root), FEAT_DIR_ENV_VAR: str(self.feat_dir)},
            )
        )

    def _seed(self, case: _Case) -> Any:
        """Create a real, persisted document from ``case``'s minimal body and return it."""
        result = case.create(case.minimal_body)
        return result

    def _flat_path(self, case: _Case) -> Path:
        """The single on-disk document file seeded for the flat domain ``case``."""
        matches = list((self.docs_root / case.doc_type).glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result

    def _target(self, case: _Case, doc_id: str) -> Path:
        """The deletion target: the ``*.md`` file for the flat domains, the folder for ``feat``."""
        if case.doc_type == _TYPE_FEAT:
            result = feat_base_dir() / doc_id
        else:
            result = self._flat_path(case)
        return result


class TestDeleteWholeBodyDomains(TempDeleteDirTestCase):
    """ACC-001/ACC-006: delete succeeds, returns the deleted path, the file/folder is gone,
    a follow-up load raises the domain not-found."""

    def test_delete_returns_deleted_path_and_removes_the_document(self) -> None:
        """For each of the eleven types, delete must return the deleted file/folder path and remove it from disk."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                target = self._target(case, doc_id)
                self.assertTrue(target.exists())

                result = delete(id=doc_id, type=case.doc_type)

                self.assertEqual(result, str(target))
                self.assertFalse(target.exists())
                with self.assertRaises(case.not_found_error):
                    case.load_by_id(case.base_dir(), doc_id)

    def test_feat_delete_removes_the_whole_folder_including_history_md(self) -> None:
        """For feat, the whole <base>/<id>/ folder -- including a seeded history.md -- must be removed."""
        created = create_feat(_FEAT_MINIMAL_BODY)
        feat_id = created.frontmatter.id
        folder = feat_base_dir() / feat_id
        history = folder / "history.md"
        history.write_text("# History\n\nAn archived older update entry.\n", encoding="utf-8")

        result = delete(id=feat_id, type=_TYPE_FEAT)

        self.assertEqual(result, str(folder))
        self.assertFalse(folder.exists())
        self.assertFalse(history.exists())
        with self.assertRaises(FeatNotFoundError):
            load_feat_by_id(feat_base_dir(), feat_id)

    def test_unknown_id_raises_domain_not_found_and_leaves_the_seed_intact(self) -> None:
        """A well-formed but non-existent id must raise the domain's own not-found error, seed untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                target = self._target(case, doc_id)
                missing_id = _MISSING_FEAT_ID if case.doc_type == _TYPE_FEAT else _MISSING_UUID

                with self.assertRaises(case.not_found_error):
                    delete(id=missing_id, type=case.doc_type)

                self.assertTrue(target.exists())


class TestDeleteInjection(TempDeleteDirTestCase):
    """ACC-005: every path-injection id raises ValueError before any filesystem access, the seed untouched."""

    def test_injection_ids_raise_value_error_and_leave_filesystem_untouched(self) -> None:
        """Each pinned traversal shape and a wrong-format id must raise ValueError, leaving
        the seeded document intact."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                target = self._target(case, doc_id)

                for bad_id in (*_TRAVERSAL_IDS, case.wrong_format_id):
                    with self.subTest(doc_type=case.doc_type, bad_id=bad_id):
                        with self.assertRaises(ValueError):
                            delete(id=bad_id, type=case.doc_type)
                        self.assertTrue(target.exists())


class TestDeleteIoFailure(TempDeleteDirTestCase):
    """ACC-005: a mocked unlink/rmtree OSError surfaces as DeleteError with the cause and the path in the message."""

    def test_unlink_failure_raises_delete_error_with_cause_and_path(self) -> None:
        """For the ten flat domains, a mocked Path.unlink OSError must raise DeleteError wrapping that exact OSError."""
        for case in _CASES:
            if case.doc_type == _TYPE_FEAT:
                continue
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case)
                doc_id = created.frontmatter.id
                path = self._flat_path(case)
                failure = OSError("simulated I/O failure")

                with mock.patch.object(Path, "unlink", side_effect=failure):
                    with self.assertRaises(DeleteError) as ctx:
                        delete(id=doc_id, type=case.doc_type)

                self.assertIsInstance(ctx.exception, OSError)
                self.assertIs(ctx.exception.__cause__, failure)
                self.assertIn(str(path), str(ctx.exception))
                self.assertTrue(path.exists())

    def test_rmtree_failure_raises_delete_error_with_cause_and_path(self) -> None:
        """For feat, a mocked shutil.rmtree OSError must raise DeleteError wrapping that exact
        OSError, folder intact."""
        created = create_feat(_FEAT_MINIMAL_BODY)
        feat_id = created.frontmatter.id
        folder = feat_base_dir() / feat_id
        failure = OSError("simulated I/O failure")

        with mock.patch("shutil.rmtree", side_effect=failure):
            with self.assertRaises(DeleteError) as ctx:
                delete(id=feat_id, type=_TYPE_FEAT)

        self.assertIsInstance(ctx.exception, OSError)
        self.assertIs(ctx.exception.__cause__, failure)
        self.assertIn(str(folder), str(ctx.exception))
        self.assertTrue(folder.exists())


class TestDeleteLocking(TempDeleteDirTestCase):
    """ACC-004: each adapter enters the domain's own per-id lock around the resolve-then-delete sequence."""

    def test_the_domain_lock_is_entered_around_the_delete(self) -> None:
        """For each of the eleven types, the domain's own <d>_lock must be acquired with the id
        before the delete and released after."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._assert_lock_entered(case)

    def _assert_lock_entered(self, case: _Case) -> None:
        """The domain's own <d>_lock must be entered with the id around the delete for ``case``."""
        created = self._seed(case)
        doc_id = created.frontmatter.id
        target = self._target(case, doc_id)

        events: list[str] = []
        lock_attr = f"{case.doc_type}_lock"
        real_lock: Callable[[str], AbstractContextManager[None]] = getattr(delete_module, lock_attr)

        @contextmanager
        def spy_lock(id_: str) -> Iterator[None]:
            events.append(f"acquire:{id_}")
            with real_lock(id_):
                yield
            events.append("release")

        with mock.patch.object(delete_module, lock_attr, spy_lock):
            delete(id=doc_id, type=case.doc_type)

        self.assertEqual(events, [f"acquire:{doc_id}", "release"])
        self.assertFalse(target.exists())


class TestDeleteRegistration(unittest.TestCase):
    """The live ``mcp`` registration carries ``delete`` with the 11-value ``type`` enum and required ``id``/``type``."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_delete_registered_with_11_value_type_enum(self) -> None:
        """``delete`` must be registered exactly once, with the 11-value ``type`` enum and required ``id``/``type``."""
        matching = [t for t in self._tools if t.name == "delete"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(
            type_prop["enum"], ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr"]
        )
        self.assertEqual(type_prop["type"], "string")
        self.assertEqual(schema["properties"]["id"]["type"], "string")
        self.assertEqual(schema["required"], ["id", "type"])


if __name__ == "__main__":
    unittest.main()
