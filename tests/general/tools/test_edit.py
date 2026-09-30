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

"""Tests for the generic ``edit`` ``@mcp.tool()`` wrapper (feat-159-edit, Phase 3).

Parameterized over all 12 whole-body document types; seeds a real, persisted
document per type in a temp ``SPECMGR_DOCS_DIR`` (plus ``SPECMGR_FEAT_DIR`` for
``feat``, the folder-per-document domain) via the domain's own ``create_<d>``
tool -- the fixture strategy and the per-domain ``_Case`` harness mirror
``test_update.py``, ported to the edit-specific fields below.

Covers ACC-001..ACC-006 and ACC-008..ACC-010 (ACC-007's docs are Phase 4):

- The match-stage unit tests (direct ``_match_and_replace`` calls: 0/1/n
  occurrences, ``replace_all``, empty ``new_str`` deletion, the pure-byte-exact
  CRLF pin per ACC-010) plus the public ``edit`` guard tests (the identical-
  input guard, the empty-``old_str`` guard, the guard order, and fire-before-
  file-access -- including for a non-existent document).
- The per-domain tool tests (happy path, not found, multiple matches, invalid
  result, invalid id, domain not-found) -- ACC-001..ACC-005, ACC-008.
- The byte-unchanged-on-every-failure-path regression (raw bytes) -- ACC-002/
  003/004, Task 3.3.
- The registration/input-schema test (live ``mcp.list_tools()``) and the pinned
  ``type="adr"`` explicit-``ValueError`` test (Task 3.4, REQ-004/ACC-006).

Two notes on derivation (as in ``test_update.py``'s own approach note):

- The per-type stage-2 field-failure cases: ``req``, ``uc``, ``tsk``, ``gol``,
  ``rsk``, ``dec``, ``sop``, ``feat``, ``vcr``, and ``sysrs`` each have a
  genuine field-level ``pydantic.ValidationError`` path (closed vocabularies,
  cross-field validators, or a model validator that eagerly forces an
  item-pattern check), while ``qa`` and ``prb`` bodies fail structurally with
  ``AssertionError`` instead (an unrecognized section heading) -- each case's
  ``field_error_is_validation`` flag pins which channel its edit raises.
- ``prb``'s multi-occurrence case seeds a dedicated optional ``## More
  Information`` section carrying the marker three times, because ``prb``'s
  mandatory lead paragraph is template-validated (``[Current state] is causing
  [specific issue], for [stakeholder] because [underlying cause].``) and must
  not be rewritten.

The ACC-010 CRLF pin lives at the ``_match_and_replace`` unit level on purpose:
REQ-009's byte-exactness claim is about the *matcher* performing no OC-style
dominant-EOL conversion of ``old_str``/``new_str``. The shared ``body_text``
read helper (the same text ``get_<d>(id, raw=True)`` returns) is the single
definition of "the body text" in this codebase, and a document file persisted
with CRLF line endings is read back through it as LF text -- that read
contract is ``update``'s/``get_<d>``'s own, not the edit tool's.
"""

from __future__ import annotations

import asyncio
import importlib
import re
import tempfile
import textwrap
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.dec.models.v1 import DecDocument, DecFrontmatter
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError, dec_base_dir
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.list_dec import list_dec
from biz.dfch.specmgr.feat.models.v1 import FeatDocument, FeatFrontmatter
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR

#: The shared domain-name source (feat-125-domain-lists): the whole-body
#: document types the registration test's expected ``type`` enum derives from.
from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.gol.models.v1 import GolDocument, GolFrontmatter
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.gol.tools.list_gol import list_gol
from biz.dfch.specmgr.prb.models.v1 import PrbDocument, PrbFrontmatter
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.prb.tools.list_prb import list_prb
from biz.dfch.specmgr.qa.models.v2 import QaDocument, QaFrontmatter
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError, qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.qa.tools.list_qa import list_qa
from biz.dfch.specmgr.req.models.v1 import ReqDocument, ReqFrontmatter
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError, req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.req.tools.list_req import list_req
from biz.dfch.specmgr.rsk.models.v1 import RskDocument, RskFrontmatter
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError, rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.rsk.tools.list_rsk import list_rsk
from biz.dfch.specmgr.sop.models.v1 import SopDocument, SopFrontmatter
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError, sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.sop.tools.list_sop import list_sop
from biz.dfch.specmgr.sysrs.models.v1 import SysrsDocument, SysrsFrontmatter
from biz.dfch.specmgr.sysrs.tools._paths import SysrsNotFoundError, sysrs_base_dir
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.sysrs.tools.list_sysrs import list_sysrs
from biz.dfch.specmgr.tsk.models.v1 import TskDocument, TskFrontmatter
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.tsk.tools.list_tsk import list_tsk
from biz.dfch.specmgr.uc.models.v2 import UcDocument, UcFrontmatter
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.uc.tools.list_uc import list_uc
from biz.dfch.specmgr.vcr.models.v1 import VcrDocument, VcrFrontmatter
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr
from biz.dfch.specmgr.vcr.tools.list_vcr import list_vcr

edit_module = importlib.import_module("biz.dfch.specmgr.general.tools.edit")
edit = edit_module.edit
_match_and_replace = edit_module._match_and_replace  # pylint: disable=protected-access

#: The OC-parity stage-1 messages, pinned verbatim (REQ-002, feat-159-edit's
#: Design Notes; parity target: opencode dev commit
#: ``236cfcbbc31530fde6a9e65318703f40adad8455``'s ``edit.ts`` ``replace()``
#: runtime strings, OC's parameter names retained on purpose). Every one of
#: them is raised as a plain ``ValueError`` with *no* ``domain tool (channel)``
#: wrap prefix -- the full-message equality assertions below pin both facts.
_NOT_FOUND_MESSAGE = (
    "Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings."
)
_MULTIPLE_MATCHES_MESSAGE = (
    "Found multiple matches for oldString. Provide more surrounding context to make the match unique."
)
_IDENTICAL_INPUT_MESSAGE = "No changes to apply: oldString and newString are identical."
_EMPTY_OLD_STR_MESSAGE = (
    "oldString cannot be empty when editing an existing file. "
    "Provide the exact text to replace, "
    "or use update for an intentional full-file replacement."
)


def _unknown_type_message(type_: str) -> str:
    """The public dispatcher's explicit pre-dispatch ``type`` rejection message (REQ-004)."""
    result = (
        f"unknown document type {type_!r}; expected one of {', '.join(WHOLE_BODY_DOMAINS)} ('adr' is not supported)"
    )
    return result


#: A fixed date+time timestamp (feat-146 shape, ``T``-separated canonical form)
#: the ``now_timestamp`` patch returns so the ``updated`` bump is deterministic.
_FIXED_TIMESTAMP = "2026-08-27 12:00:00.123Z"

#: A well-formed but non-existent canonical UUID (the id must be well-formed to
#: reach the domain's own not-found error past the ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: A well-formed but non-existent ``feat-NNN-slug`` folder name (``feat``'s
#: own id shape).
_MISSING_FEAT_ID = "feat-999-does-not-exist"

#: The pinned path-injection shapes (mirrors ``test_update.py``/``test_delete.py``'s own).
_TRAVERSAL_IDS = ("../x", "a/b", "a\\b", "..")

#: A well-formed feat-NNN-slug folder name (the wrong-format id for every UUID domain).
_FEAT_SLUG_ID = "feat-36-delete"

#: An ``old_str`` that appears in none of the per-domain seed bodies below.
_ABSENT_MARKER = "This exact text does not appear in the document at all."

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

    ### 2026-08-19 00:00:00.000Z - Kickoff

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

    The current process is causing delays, for users because of missing automation.

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

    ## Source

    The QA interview on 2026-09-17 that elicited this risk.
    """
)

_DEC_MINIMAL_BODY = textwrap.dedent(
    """\
    # Title of the Decision

    ## Context and Problem Statement

    Something is wrong with the status quo.

    ## Decision Outcome

    We chose the structured arrangement.

    ## Roles and Responsibilities

    ### Accountable

    The platform architecture lead.

    ### Responsible

    - The order service team.

    ## Source

    The customer dashboard latency incident review meeting.
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

    #### Phase 100: Scaffolding

    - [x] Task 100.100: Create branch and package skeleton

    ## Progress

    ### Current Status

    **As of 2026-08-30**: free-form narrative.

    ### Updates

    #### 2026-08-30 16:47:59.981Z - Paused for review

    Free-form prose describing what happened in this update.
    """
)


#: The corrupted on-disk body every parse-failure case below seeds (the same corruption the
#: ``get_<d>`` parse-failure tests use: no H1 heading at all, so every domain's parser fails at
#: the markdown engine level, before any domain-specific section validation).
_BROKEN_BODY = "not a valid document, no headings at all\n"

#: The core parse defect ``_BROKEN_BODY`` produces in every domain's parse error text.
_CORE_DEFECT = "Token[0]: expected 'heading_open', got 'paragraph_open'."


def _strip_pydantic_footer(text: str) -> str:
    """Strip the optional trailing pydantic documentation line from a parse-error text.

    Module-local copy of the helper every ``get_<d>`` parse-failure test module carries
    (the convention is 12 local copies, not a shared import): the ``DocCache``'s exception
    reconstruction drops pydantic's "For further information visit
    https://errors.pydantic.dev/..." line on warm re-raises, so the error-text identity
    against the domain's ``list_<d>`` failed row is asserted modulo that line (Option B,
    2026-09-26; the str-faithful reconstruction is tracked as follow-up issue #162).
    """
    result = re.sub(r"[ \t]*For further information visit https://errors\.pydantic\.dev/.*$", "", text, flags=re.S)
    return result


@dataclass(frozen=True)
class _ParseFailureCase:
    """Per-domain test data for the parse-failure (Bug 1) coverage of the generic ``edit`` tool.

    All 12 whole-body domains, ``feat`` included (this module's own ``_CASES`` already carries
    ``feat`` in the unified shape, unlike ``test_update.py``/``test_set_status.py``).
    """

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    base_dir: Callable[[], Path]
    #: The domain's own ``list_<d>`` tool -- the consistency reference for ``error`` text.
    list_fn: Callable[..., Any]
    minimal_body: str


_PARSE_FAILURE_CASES: list[_ParseFailureCase] = [
    _ParseFailureCase("req", create_req, ReqNotFoundError, req_base_dir, list_req, _REQ_MINIMAL_BODY),
    _ParseFailureCase("uc", create_uc, UcNotFoundError, uc_base_dir, list_uc, _UC_MINIMAL_BODY),
    _ParseFailureCase("tsk", create_tsk, TskNotFoundError, tsk_base_dir, list_tsk, _TSK_MINIMAL_BODY),
    _ParseFailureCase("qa", create_qa, QaNotFoundError, qa_base_dir, list_qa, _QA_MINIMAL_BODY),
    _ParseFailureCase("prb", create_prb, PrbNotFoundError, prb_base_dir, list_prb, _PRB_MINIMAL_BODY),
    _ParseFailureCase("gol", create_gol, GolNotFoundError, gol_base_dir, list_gol, _GOL_MINIMAL_BODY),
    _ParseFailureCase("rsk", create_rsk, RskNotFoundError, rsk_base_dir, list_rsk, _RSK_MINIMAL_BODY),
    _ParseFailureCase("dec", create_dec, DecNotFoundError, dec_base_dir, list_dec, _DEC_MINIMAL_BODY),
    _ParseFailureCase("sop", create_sop, SopNotFoundError, sop_base_dir, list_sop, _SOP_MINIMAL_BODY),
    _ParseFailureCase("feat", create_feat, FeatNotFoundError, feat_base_dir, list_feat, _FEAT_MINIMAL_BODY),
    _ParseFailureCase("vcr", create_vcr, VcrNotFoundError, vcr_base_dir, list_vcr, _VCR_MINIMAL_BODY),
    _ParseFailureCase("sysrs", create_sysrs, SysrsNotFoundError, sysrs_base_dir, list_sysrs, _SYSRS_MINIMAL_BODY),
]


@dataclass(frozen=True)
class _Case:
    """Per-domain test data for the whole-body document types (edit-specific fields)."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    #: The domain's own frontmatter class -- the type ``edit`` must return (feat-69).
    frontmatter_type: type
    #: The domain's own document (frontmatter+body wrapper) class -- what ``edit`` must
    #: NOT return any more (feat-69).
    document_type: type
    base_dir: Callable[[], Path]
    #: A well-formed but non-existent id of the domain's own shape (``_MISSING_UUID``
    #: for the UUID domains, a ``feat-NNN-slug`` for ``feat``).
    missing_id: str
    #: A well-formed id of a *different* domain shape (``_FEAT_SLUG_ID`` for the UUID
    #: domains, ``_MISSING_UUID`` for ``feat``).
    wrong_format_id: str
    minimal_body: str
    #: A unique single-occurrence substring of ``minimal_body``; rewriting it to
    #: ``edit_replacement`` keeps the document valid (ACC-001's happy path).
    edit_marker: str
    edit_replacement: str
    #: The domain's H1 line -- deleting it (an empty ``new_str``) breaks the document
    #: structurally in every domain (ACC-008's mandatory-part case).
    h1_line: str
    #: A valid optional trailing section appended to ``minimal_body`` for the
    #: empty-``new_str`` deletion test; deleting ``deletable_suffix.rstrip("\\n")``
    #: (the on-disk body's own tail) yields exactly ``minimal_body`` again.
    deletable_suffix: str
    #: A substring occurring at least twice in the (possibly suffixed) multi seed;
    #: ``replace_all`` rewrites every exact occurrence, keeping the document valid.
    multi_marker: str
    multi_replacement: str
    #: Appended to ``minimal_body`` only for the multi-occurrence seeds -- ``""`` in
    #: every case but ``prb``'s, whose template-validated lead paragraph must not be
    #: rewritten (see the module docstring).
    multi_seed_suffix: str
    #: The line rewritten to ``field_error_fragment`` to reproduce the domain's
    #: stage-2 field failure (or the ``body``'s last line, when
    #: ``field_error_is_append`` -- see :func:`_field_error_edit`).
    field_error_marker: str
    field_error_fragment: str
    field_error_is_append: bool
    #: Whether that stage-2 failure raises ``pydantic.ValidationError``
    #: (``req``/``uc``/``tsk``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/
    #: ``sysrs``) or a structural ``AssertionError`` (``qa``/``prb`` -- their bodies
    #: fail on the unrecognized section heading itself).
    field_error_is_validation: bool


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        not_found_error=ReqNotFoundError,
        frontmatter_type=ReqFrontmatter,
        document_type=ReqDocument,
        base_dir=req_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_REQ_MINIMAL_BODY,
        edit_marker="If the engine becomes too hot, the lifetime of the system decreases.",
        edit_replacement="Updated description text.",
        h1_line="# Maximum Engine Temperature",
        deletable_suffix="\n## Notes\n\nA note.\n",
        multi_marker="the",
        multi_replacement="that",
        multi_seed_suffix="",
        field_error_marker="MUST",
        field_error_fragment="NOT-A-VALID-LEVEL",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
        frontmatter_type=UcFrontmatter,
        document_type=UcDocument,
        base_dir=uc_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_UC_MINIMAL_BODY,
        edit_marker="Buyer issues request directly to our company.",
        edit_replacement="Buyer issues an updated request directly to our company.",
        h1_line="# Buy Goods",
        deletable_suffix="\n## Open Issues\n\n- Is the scope final?\n",
        multi_marker="Buyer",
        multi_replacement="Customer",
        multi_seed_suffix="",
        field_error_marker="## Extensions",
        field_error_fragment="## Extensions\n\n### Extension 99a. Out-of-range reference\n\n1. Not resolvable.\n",
        field_error_is_append=True,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        frontmatter_type=TskFrontmatter,
        document_type=TskDocument,
        base_dir=tsk_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_TSK_MINIMAL_BODY,
        edit_marker="Started the task list.",
        edit_replacement="Started the task list with a kickoff note.",
        h1_line="# Simple Task List",
        deletable_suffix="\n### 2026-08-19 00:00:00.000Z - Progress\n\nFinished the first item.\n",
        multi_marker="the",
        multi_replacement="that",
        multi_seed_suffix="",
        field_error_marker="- [ ] Do the first thing",
        field_error_fragment="- [z] Not a valid checkbox marker",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
        frontmatter_type=QaFrontmatter,
        document_type=QaDocument,
        base_dir=qa_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_QA_MINIMAL_BODY,
        edit_marker="Some intro text.",
        edit_replacement="Updated intro text.",
        h1_line="# Some QA Title",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        multi_marker="Some",
        multi_replacement="Sample",
        multi_seed_suffix="",
        field_error_marker="## Functional Suitability",
        field_error_fragment="## Not A Category",
        field_error_is_append=False,
        field_error_is_validation=False,
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
        frontmatter_type=PrbFrontmatter,
        document_type=PrbDocument,
        base_dir=prb_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_PRB_MINIMAL_BODY,
        edit_marker="Something is wrong.",
        edit_replacement="Something is very wrong indeed.",
        h1_line="# Simple Problem Statement",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        multi_marker="The gap",
        multi_replacement="The wider gap",
        multi_seed_suffix="\n## More Information\n\nThe gap is real. The gap is wide. The gap is deep.\n",
        field_error_marker="### Summary",
        field_error_fragment="### Not A Question",
        field_error_is_append=False,
        field_error_is_validation=False,
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
        frontmatter_type=GolFrontmatter,
        document_type=GolDocument,
        base_dir=gol_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_GOL_MINIMAL_BODY,
        edit_marker="THE company shall provide engines that are competitive in power output and fuel consumption.",
        edit_replacement="THE company shall provide competitive engines in power output and fuel consumption.",
        h1_line="# Competitive Engines in Consumer Vehicles",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        multi_marker="in ",
        multi_replacement="at ",
        multi_seed_suffix="",
        field_error_marker="## Source",
        field_error_fragment="## Priority\n\n100\n\n## Source",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
        frontmatter_type=RskFrontmatter,
        document_type=RskDocument,
        base_dir=rsk_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_RSK_MINIMAL_BODY,
        edit_marker="A root condition.",
        edit_replacement="A revised root condition.",
        h1_line="# Sample Risk",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        multi_marker="Sample",
        multi_replacement="Example",
        multi_seed_suffix="",
        field_error_marker="reduce",
        field_error_fragment="not-a-strategy",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
        frontmatter_type=DecFrontmatter,
        document_type=DecDocument,
        base_dir=dec_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_DEC_MINIMAL_BODY,
        edit_marker="Something is wrong with the status quo.",
        edit_replacement="Something is very wrong with the status quo.",
        h1_line="# Title of the Decision",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        multi_marker="the",
        multi_replacement="that",
        multi_seed_suffix="",
        field_error_marker="## Decision Outcome",
        field_error_fragment=(
            "\n## Pros and Cons\n"
            "\n### Option 1: First option\n"
            "\nThe first option text.\n"
            "\n### Option 1: Duplicate option\n"
            "\nThe duplicate option text.\n"
        ),
        field_error_is_append=True,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="sop",
        create=create_sop,
        not_found_error=SopNotFoundError,
        frontmatter_type=SopFrontmatter,
        document_type=SopDocument,
        base_dir=sop_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_SOP_MINIMAL_BODY,
        edit_marker="Provision accounts for new hires.",
        edit_replacement="Provision accounts for all new hires.",
        h1_line="# New Employee IT Account Provisioning",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        multi_marker="request",
        multi_replacement="ticket",
        multi_seed_suffix="",
        field_error_marker="### Step 1: Submit request",
        field_error_fragment="\n### Step 1: Duplicate step\n\nDuplicate step text.\n",
        field_error_is_append=True,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="feat",
        create=create_feat,
        not_found_error=FeatNotFoundError,
        frontmatter_type=FeatFrontmatter,
        document_type=FeatDocument,
        base_dir=feat_base_dir,
        missing_id=_MISSING_FEAT_ID,
        wrong_format_id=_MISSING_UUID,
        minimal_body=_FEAT_MINIMAL_BODY,
        edit_marker="- REQ-001: The widget must render within 200ms.",
        edit_replacement="- REQ-001: The widget must render within 100ms.",
        h1_line="# Feature: Example Widget",
        deletable_suffix="\n### More Information\n\nFree-form supplementary text.\n",
        multi_marker="widget",
        multi_replacement="gadget",
        multi_seed_suffix="",
        field_error_marker="- REQ-001: The widget must render within 200ms.",
        field_error_fragment="- Not a requirement at all.",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="vcr",
        create=create_vcr,
        not_found_error=VcrNotFoundError,
        frontmatter_type=VcrFrontmatter,
        document_type=VcrDocument,
        base_dir=vcr_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_VCR_MINIMAL_BODY,
        edit_marker="Confirms that the sample requirement is met.",
        edit_replacement="Confirms that the sample requirement is thoroughly met.",
        h1_line="# Sample Verification Case",
        deletable_suffix="\n## More Information\n\nAdditional verification context.\n",
        multi_marker="sample",
        multi_replacement="reference",
        multi_seed_suffix="",
        field_error_marker="### AC-001 (Test): The sample criterion passes",
        field_error_fragment="\n### AC-001 (Analysis): Duplicate AC number\n",
        field_error_is_append=True,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="sysrs",
        create=create_sysrs,
        not_found_error=SysrsNotFoundError,
        frontmatter_type=SysrsFrontmatter,
        document_type=SysrsDocument,
        base_dir=sysrs_base_dir,
        missing_id=_MISSING_UUID,
        wrong_format_id=_FEAT_SLUG_ID,
        minimal_body=_SYSRS_MINIMAL_BODY,
        edit_marker="Onboarding only.",
        edit_replacement="Onboarding and renewals.",
        h1_line="# System Requirements Specification: Sample Document",
        deletable_suffix="\n## References\n\n- ISO/IEC/IEEE 29148:2018, Systems and software engineering\n",
        multi_marker="A ",
        multi_replacement="An ",
        multi_seed_suffix="",
        field_error_marker=f"- GOL {_SYSRS_GOL_ID}: A goal",
        field_error_fragment=f"- PRB {_SYSRS_GOL_ID}: A goal",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
]


def _field_error_edit(case: _Case) -> tuple[str, str]:
    """The ``(old_str, new_str)`` pair that reproduces ``case``'s stage-2 field failure via ``edit``.

    The line-replace cases rewrite ``field_error_marker`` to ``field_error_fragment``
    directly; the append cases grow the body's last line into exactly the text
    ``test_update.py``'s own ``_field_error_body`` helper appends, so the edited
    document matches the one that test pins for the same error channel.
    """
    if case.field_error_is_append:
        anchor = case.minimal_body.rstrip("\n").splitlines()[-1]
        result = (anchor, anchor + "\n" + case.field_error_fragment.rstrip("\n"))
        return result
    result = (case.field_error_marker, case.field_error_fragment)
    return result


def _wrapped_prefix(doc_type: str) -> str:
    """The ``wrap_tool_errors`` label every stage-2 failure message carries (feat-27-validation)."""
    result = f"{doc_type} edit (body): "
    return result


class TempEditDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via ``SPECMGR_DOCS_DIR`` and
    ``SPECMGR_FEAT_DIR`` (mirrors ``test_update.py``'s ``TempUpdateInjectionDirTestCase``,
    since every test class below spans all 12 whole-body domains, feat included)."""

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
        """The on-disk document file/README.md path for ``case``'s document ``doc_id``."""
        if case.doc_type == "feat":
            result = case.base_dir() / doc_id / "README.md"
        else:
            result = next(p for p in (self.docs_root / case.doc_type).glob("*.md") if doc_id in p.name)
        return result

    def _seed(self, case: _Case, body: str) -> Any:
        """Create a real, persisted document from ``body`` and return its frontmatter."""
        result = case.create(body)
        return result


class TestMatchStageUnit(unittest.TestCase):
    """Task 3.1: the domain-agnostic ``_match_and_replace`` match stage (REQ-002/REQ-009).

    Every raised ``ValueError`` is pinned by *full message equality* against the
    verbatim OC-parity string -- which also pins that it is a plain ``ValueError``
    with no ``domain tool (channel)`` wrap prefix (REQ-008/D3).
    """

    def test_zero_occurrences_raises_oc_not_found_message_verbatim(self) -> None:
        """REQ-002/ACC-002: zero occurrences raise the OC not-found message verbatim as a plain ``ValueError``."""
        with self.assertRaises(ValueError) as ctx:
            _match_and_replace("line one\nline two\nline three", "absent text", "replacement", replace_all=False)

        self.assertEqual(str(ctx.exception), _NOT_FOUND_MESSAGE)

    def test_single_occurrence_rewrites_exactly_once(self) -> None:
        """REQ-009: a single exact occurrence is rewritten exactly once, nothing else touched."""
        result = _match_and_replace("alpha marker beta", "marker", "pin", replace_all=False)

        self.assertEqual(result, "alpha pin beta")

    def test_single_occurrence_with_replace_all_rewrites_that_one_occurrence(self) -> None:
        """REQ-009: ``replace_all`` with a single occurrence rewrites that one occurrence (no error)."""
        result = _match_and_replace("alpha marker beta", "marker", "pin", replace_all=True)

        self.assertEqual(result, "alpha pin beta")

    def test_multiple_occurrences_without_replace_all_raises_oc_multiple_message_verbatim(self) -> None:
        """REQ-002/ACC-003: multiple occurrences without ``replace_all`` raise the OC
        multiple-matches message verbatim."""
        with self.assertRaises(ValueError) as ctx:
            _match_and_replace("alpha marker beta marker gamma", "marker", "pin", replace_all=False)

        self.assertEqual(str(ctx.exception), _MULTIPLE_MATCHES_MESSAGE)

    def test_multiple_occurrences_with_replace_all_rewrites_every_occurrence(self) -> None:
        """REQ-009/ACC-003: ``replace_all`` rewrites every exact occurrence."""
        result = _match_and_replace("alpha marker beta marker gamma", "marker", "pin", replace_all=True)

        self.assertEqual(result, "alpha pin beta pin gamma")

    def test_empty_new_str_deletes_the_match(self) -> None:
        """REQ-001/D1: an empty ``new_str`` deletes the match (a pure deletion)."""
        result = _match_and_replace("hello brave new world", "brave new ", "", replace_all=False)

        self.assertEqual(result, "hello world")

    def test_crlf_body_does_not_match_lf_old_str(self) -> None:
        """ACC-010: no line-ending normalization -- an ``old_str`` containing ``\\n`` is not
        found in a CRLF body for the same logical text."""
        with self.assertRaises(ValueError) as ctx:
            _match_and_replace("line one\r\nline two\r\nline three", "line one\nline two", "line X", replace_all=False)

        self.assertEqual(str(ctx.exception), _NOT_FOUND_MESSAGE)

    def test_crlf_body_matches_crlf_old_str(self) -> None:
        """Positive control for the CRLF pin: the same logical text *does* match when
        ``old_str`` carries the body's own ``\\r\\n`` line endings."""
        result = _match_and_replace(
            "line one\r\nline two\r\nline three", "line one\r\nline two", "line X", replace_all=False
        )

        self.assertEqual(result, "line X\r\nline three")


class TestEditPublicGuards(TempEditDirTestCase):
    """Task 3.1/ACC-009: the public dispatcher's guards fire in the pinned order, before
    any filesystem access -- including for a non-existent document (the guard's
    ``ValueError``, not the domain's not-found error), in every domain."""

    def test_identical_input_guard_fires_before_file_access_for_nonexistent_document(self) -> None:
        """REQ-008/ACC-009: the identical-input guard fires before any file access, even for a non-existent document."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                with self.assertRaises(ValueError) as ctx:
                    edit(id=case.missing_id, type=case.doc_type, old_str="identical text", new_str="identical text")

                self.assertEqual(str(ctx.exception), _IDENTICAL_INPUT_MESSAGE)

    def test_empty_old_str_guard_fires_before_file_access_for_nonexistent_document(self) -> None:
        """REQ-008/ACC-009: the empty-``old_str`` guard fires before any file access, even for a missing document."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                with self.assertRaises(ValueError) as ctx:
                    edit(id=case.missing_id, type=case.doc_type, old_str="", new_str="replacement text")

                self.assertEqual(str(ctx.exception), _EMPTY_OLD_STR_MESSAGE)

    def test_identical_input_guard_precedes_empty_old_str_guard(self) -> None:
        """``old_str == "" == new_str`` trips the identical-input guard first (guard order, REQ-008)."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                with self.assertRaises(ValueError) as ctx:
                    edit(id=case.missing_id, type=case.doc_type, old_str="", new_str="")

                self.assertEqual(str(ctx.exception), _IDENTICAL_INPUT_MESSAGE)

    def test_id_validation_precedes_identical_input_guard(self) -> None:
        """A malformed/traversal ``id`` with identical inputs still raises the id ``ValueError`` first."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                with self.assertRaises(ValueError) as ctx:
                    edit(id="../x", type=case.doc_type, old_str="identical text", new_str="identical text")

                self.assertEqual(
                    str(ctx.exception),
                    "id '../x' contains a path separator or a '..' traversal sequence; a bare id is expected",
                )

    def test_identical_input_guard_leaves_existing_document_byte_unchanged(self) -> None:
        """REQ-008: the identical-input guard leaves an existing document byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()

                with self.assertRaises(ValueError) as ctx:
                    edit(id=created.id, type=case.doc_type, old_str="x", new_str="x")

                self.assertEqual(str(ctx.exception), _IDENTICAL_INPUT_MESSAGE)
                self.assertEqual(path.read_bytes(), before)

    def test_empty_old_str_guard_leaves_existing_document_byte_unchanged(self) -> None:
        """REQ-008: the empty-``old_str`` guard leaves an existing document byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()

                with self.assertRaises(ValueError) as ctx:
                    edit(id=created.id, type=case.doc_type, old_str="", new_str="replacement text")

                self.assertEqual(str(ctx.exception), _EMPTY_OLD_STR_MESSAGE)
                self.assertEqual(path.read_bytes(), before)


class TestEditUnsupportedType(TempEditDirTestCase):
    """REQ-004/ACC-006: an unknown or ``adr`` ``type`` is an explicit pre-dispatch ``ValueError``
    (the generic ``validate`` tool's precedent; a deliberate divergence from ``update``'s
    inherited ``KeyError``), before any filesystem access."""

    def test_adr_type_raises_explicit_value_error_before_any_filesystem_access(self) -> None:
        """REQ-004/ACC-006: ``type="adr"`` raises the edit-specific explicit pre-dispatch
        ``ValueError``, before any filesystem access."""
        with self.assertRaises(ValueError) as ctx:
            edit(id=_MISSING_UUID, type="adr", old_str="old text", new_str="new text")  # type: ignore[arg-type]

        self.assertEqual(str(ctx.exception), _unknown_type_message("adr"))
        self.assertFalse(any(self.docs_root.iterdir()))
        self.assertFalse(any(self.feat_dir.iterdir()))

    def test_adr_type_precedes_identical_input_guard(self) -> None:
        """Guard order (REQ-008): the explicit ``type`` check fires before the input guards."""
        with self.assertRaises(ValueError) as ctx:
            edit(id=_MISSING_UUID, type="adr", old_str="identical text", new_str="identical text")  # type: ignore[arg-type]

        self.assertEqual(str(ctx.exception), _unknown_type_message("adr"))

    def test_unknown_type_raises_value_error(self) -> None:
        """REQ-004: an unknown non-``adr`` type is rejected with a plain pre-dispatch ``ValueError``.

        Containment (not full equality) is deliberate: for every type other than ``"adr"``,
        ``validate_id`` -- which runs before ``edit``'s own explicit check -- raises first with
        its own message (naming the UUID domains, ``adr`` included); the edit-specific message
        is reachable only for ``type="adr"`` (pinned by full equality in the adjacent test).
        """
        with self.assertRaises(ValueError) as ctx:
            edit(id=_MISSING_UUID, type="bogus", old_str="old text", new_str="new text")  # type: ignore[arg-type]

        self.assertIn("bogus", str(ctx.exception))


class TestEditHappyPath(TempEditDirTestCase):
    """ACC-001/ACC-008: a unique exact match rewrites the body on disk and returns the
    domain's own frontmatter with only ``updated`` bumped; an empty ``new_str`` deletes
    an optional section and the document still validates."""

    def test_unique_exact_match_rewrites_body_and_returns_bumped_frontmatter(self) -> None:
        """ACC-001/REQ-006: a unique exact match rewrites the body on disk and returns the
        frontmatter with every field carried over and only ``updated`` bumped."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)

                with mock.patch.object(edit_module, "now_timestamp", return_value=_FIXED_TIMESTAMP):
                    result = edit(
                        id=created.id,
                        type=case.doc_type,
                        old_str=case.edit_marker,
                        new_str=case.edit_replacement,
                    )

                self.assertIsInstance(result, case.frontmatter_type)
                self.assertNotIsInstance(result, case.document_type)
                self.assertFalse(hasattr(result, "body"))
                self.assertEqual(result.id, created.id)
                self.assertEqual(result.type, case.doc_type)
                self.assertEqual(result.status, created.status)
                self.assertEqual(result.created, created.created)
                self.assertEqual(result.version, created.version)
                self.assertEqual(result.classification, created.classification)
                self.assertEqual(result.updated, _FIXED_TIMESTAMP)
                self.assertNotEqual(result.updated, created.updated)
                self.assertEqual(
                    body_text(path),
                    case.minimal_body.rstrip("\n").replace(case.edit_marker, case.edit_replacement),
                )

    def test_empty_new_str_deletes_optional_section_and_still_validates(self) -> None:
        """ACC-008/REQ-001: an empty ``new_str`` deletes an optional section and the document still validates."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body + case.deletable_suffix)
                path = self._doc_path(case, created.id)

                with mock.patch.object(edit_module, "now_timestamp", return_value=_FIXED_TIMESTAMP):
                    result = edit(
                        id=created.id,
                        type=case.doc_type,
                        old_str=case.deletable_suffix.rstrip("\n"),
                        new_str="",
                    )

                self.assertIsInstance(result, case.frontmatter_type)
                self.assertEqual(result.updated, _FIXED_TIMESTAMP)
                self.assertEqual(body_text(path), case.minimal_body.rstrip("\n"))


class TestEditMatchStageOnDisk(TempEditDirTestCase):
    """ACC-002/ACC-003: the stage-1 match failures over the real on-disk body -- the OC
    messages verbatim as plain ``ValueError``s, the file byte-unchanged -- and the
    ``replace_all`` success path."""

    def test_old_str_not_found_raises_oc_message_verbatim_file_byte_unchanged(self) -> None:
        """ACC-002: an absent ``old_str`` raises the OC not-found message verbatim; the file stays byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()

                with self.assertRaises(ValueError) as ctx:
                    edit(id=created.id, type=case.doc_type, old_str=_ABSENT_MARKER, new_str="replacement text")

                self.assertEqual(str(ctx.exception), _NOT_FOUND_MESSAGE)
                self.assertEqual(path.read_bytes(), before)

    def test_multiple_matches_without_replace_all_raises_oc_message_verbatim_file_byte_unchanged(self) -> None:
        """ACC-003: multiple matches without ``replace_all`` raise the OC multiple-matches
        message verbatim; the file stays byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body + case.multi_seed_suffix)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()
                self.assertGreaterEqual(body_text(path).count(case.multi_marker), 2)

                with self.assertRaises(ValueError) as ctx:
                    edit(
                        id=created.id,
                        type=case.doc_type,
                        old_str=case.multi_marker,
                        new_str=case.multi_replacement,
                    )

                self.assertEqual(str(ctx.exception), _MULTIPLE_MATCHES_MESSAGE)
                self.assertEqual(path.read_bytes(), before)

    def test_replace_all_rewrites_every_occurrence(self) -> None:
        """ACC-003: ``replace_all`` rewrites every exact occurrence (full-text equality), nothing else touched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body + case.multi_seed_suffix)
                path = self._doc_path(case, created.id)
                before_body = body_text(path)
                self.assertGreaterEqual(before_body.count(case.multi_marker), 2)

                result = edit(
                    id=created.id,
                    type=case.doc_type,
                    old_str=case.multi_marker,
                    new_str=case.multi_replacement,
                    replace_all=True,
                )

                self.assertIsInstance(result, case.frontmatter_type)
                self.assertEqual(result.id, created.id)
                # Full-text equality: every exact occurrence rewritten, nothing else touched.
                self.assertEqual(body_text(path), before_body.replace(case.multi_marker, case.multi_replacement))


class TestEditInvalidResult(TempEditDirTestCase):
    """ACC-004/ACC-008: an edit that yields an invalid document raises the wrapped
    validation error (the ``"<d> edit (body):"`` prefix, per-domain channel) and nothing
    is written -- the disk write happens only after whole-document validation passes."""

    def test_deleting_mandatory_h1_raises_wrapped_assertion_error_file_byte_unchanged(self) -> None:
        """ACC-004: deleting the mandatory H1 raises the wrapped ``AssertionError`` (the
        per-domain ``"<d> edit (body):"`` prefix); the file stays byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()

                with self.assertRaises(AssertionError) as ctx:
                    edit(id=created.id, type=case.doc_type, old_str=case.h1_line, new_str="")

                self.assertTrue(str(ctx.exception).startswith(_wrapped_prefix(case.doc_type)), str(ctx.exception))
                self.assertEqual(path.read_bytes(), before)

    def test_edit_producing_field_error_raises_wrapped_error_file_byte_unchanged(self) -> None:
        """ACC-004: an edit producing a per-domain field error raises the wrapped error;
        the file stays byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()
                field_error_old, field_error_new = _field_error_edit(case)
                expected_error = ValidationError if case.field_error_is_validation else AssertionError

                with self.assertRaises(expected_error) as ctx:
                    edit(id=created.id, type=case.doc_type, old_str=field_error_old, new_str=field_error_new)

                message = str(ctx.exception)
                prefix = _wrapped_prefix(case.doc_type)
                if case.field_error_is_validation:
                    self.assertIn(prefix, message, message)
                else:
                    self.assertTrue(message.startswith(prefix), message)
                self.assertEqual(path.read_bytes(), before)

    def test_replace_all_invalid_edit_raises_wrapped_error_file_byte_unchanged(self) -> None:
        """The 2-fold contract under ``replace_all=True``: an edit that yields an invalid
        document raises the wrapped validation error and nothing is written -- the same
        behavior as the single-match path (``_match_and_replace`` does not branch on the
        occurrence count after the replacement)."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()
                field_error_old, field_error_new = _field_error_edit(case)
                expected_error = ValidationError if case.field_error_is_validation else AssertionError

                with self.assertRaises(expected_error) as ctx:
                    edit(
                        id=created.id,
                        type=case.doc_type,
                        old_str=field_error_old,
                        new_str=field_error_new,
                        replace_all=True,
                    )

                message = str(ctx.exception)
                prefix = _wrapped_prefix(case.doc_type)
                if case.field_error_is_validation:
                    self.assertIn(prefix, message, message)
                else:
                    self.assertTrue(message.startswith(prefix), message)
                self.assertEqual(path.read_bytes(), before)


class TestEditInvalidId(TempEditDirTestCase):
    """ACC-005: path-injection and wrong-format ids raise ``ValueError`` before any
    filesystem access, in every domain (the ``validate_id`` guard); the seeded document
    stays byte-unchanged."""

    def test_traversal_and_wrong_format_ids_raise_value_error_before_file_access(self) -> None:
        """ACC-005: path-injection and wrong-format ids raise ``ValueError`` before any
        filesystem access; the seeded document stays byte-unchanged."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                before = path.read_bytes()

                for bad_id in (*_TRAVERSAL_IDS, case.wrong_format_id):
                    with self.subTest(doc_type=case.doc_type, bad_id=bad_id):
                        with self.assertRaises(ValueError):
                            edit(id=bad_id, type=case.doc_type, old_str="old text", new_str="new text")
                        self.assertEqual(path.read_bytes(), before)


class TestEditDomainNotFound(TempEditDirTestCase):
    """ACC-005/REQ-004: a well-formed but non-existent id (of the domain's own shape)
    raises the domain's own ``XNotFoundError``, unchanged from the per-domain tools."""

    def test_well_formed_nonexistent_id_raises_domain_not_found_error(self) -> None:
        """ACC-005: a well-formed but non-existent id raises the domain's own not-found error."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._seed(case, case.minimal_body)

                with self.assertRaises(case.not_found_error):
                    edit(id=case.missing_id, type=case.doc_type, old_str="old text", new_str="new text")


class TestEditAssertWithinSpy(TempEditDirTestCase):
    """REQ-005: ``assert_within`` is actually invoked (not just present in source) during a
    successful edit, in every domain."""

    def test_assert_within_is_called_with_base_dir_and_resolved_path(self) -> None:
        """REQ-005: ``assert_within`` is invoked with the base dir and the resolved path during a successful edit."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case, created.id)
                base_dir = case.base_dir()

                with mock.patch.object(edit_module, "assert_within", wraps=edit_module.assert_within) as spy:
                    edit(id=created.id, type=case.doc_type, old_str=case.edit_marker, new_str=case.edit_replacement)

                spy.assert_any_call(base_dir, path)


class TestEditRegistration(unittest.TestCase):
    """Task 3.4: the live ``mcp`` registration carries ``edit`` exactly once, with the pinned
    input schema (ACC-006): the 12-value ``type`` enum (no ``adr``),
    ``required == [id, type, old_str, new_str]``, optional boolean ``replace_all``
    defaulting to ``false``, and no ``minLength`` on ``new_str`` (REQ-001/D1)."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_edit_registered_exactly_once_with_pinned_input_schema(self) -> None:
        """ACC-006: the live MCP registration carries ``edit`` exactly once, with the
        12-value ``type`` enum (no ``adr``)."""
        matching = [t for t in self._tools if t.name == "edit"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(type_prop["enum"], list(WHOLE_BODY_DOMAINS))
        self.assertEqual(type_prop["type"], "string")
        self.assertEqual(len(type_prop["enum"]), 12)
        self.assertNotIn("adr", type_prop["enum"])
        self.assertEqual(schema["required"], ["id", "type", "old_str", "new_str"])

        replace_all_prop = schema["properties"]["replace_all"]
        self.assertEqual(replace_all_prop.get("type"), "boolean")
        self.assertIs(replace_all_prop.get("default"), False)
        self.assertNotIn("replace_all", schema["required"])

        self.assertNotIn("minLength", schema["properties"]["new_str"])


class TestEditParseFailure(TempEditDirTestCase):
    """feat-170 Phase 110 (Bug 1, ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f): an id whose only
    on-disk file fails to parse must return the non-raising ``ParseFailureResult`` (never the
    domain's ``XNotFoundError``) from the generic ``edit`` tool's single protected
    ``load_by_id`` call site (the lock is held across the whole read -> match -> validate ->
    write sequence, so stage 1/stage 2 are never reached), with nothing written to disk -- the
    ``error`` carries the same parse defect as the domain's own ``list_<d>`` failed row for
    the same file (the ``get_<d>`` precedent, ADR 9080b37c). All 12 whole-body domains,
    ``feat`` included (this module's unified case shape).

    A truly-absent id still raises the domain's own not-found error (REQ-002): the regression
    is this module's existing ``TestEditDomainNotFound`` (unchanged by this phase, all 12
    domains including ``feat``).
    """

    def _assert_parse_failure_result(self, list_fn: Callable[..., Any], path: Path, doc_id: str, result: Any) -> None:
        """The shared result-shape and list-row consistency assertions (the ``get_<d>`` precedent)."""
        self.assertIsInstance(result, ParseFailureResult)
        self.assertEqual(result.id, doc_id)
        self.assertEqual(result.path, str(path.resolve()))
        self.assertTrue(result.error)
        failed = [summary for summary in list_fn().results if summary.title == "<failed to parse>"]
        self.assertEqual(len(failed), 1)
        # Option B (2026-09-26): identity is modulo the trailing pydantic line (follow-up issue #162).
        self.assertEqual(_strip_pydantic_footer(result.error), _strip_pydantic_footer(failed[0].error))
        # The core defect content (this fixture's structural parse failure) must be present in both texts.
        self.assertIn(_CORE_DEFECT, result.error)
        self.assertIn(_CORE_DEFECT, failed[0].error)

    def test_broken_document_returns_parse_failure_result_nothing_written(self) -> None:
        """A valid edit (``old_str``/``new_str``) against a broken existing document must return
        ``ParseFailureResult``; the corrupted file stays byte-unchanged (no edit is applied)."""
        for case in _PARSE_FAILURE_CASES:
            with self.subTest(doc_type=case.doc_type):
                created = case.create(case.minimal_body)
                doc_id = created.id
                path = self._doc_path(case, doc_id)
                path.write_text(_BROKEN_BODY, encoding="utf-8")
                before = path.read_bytes()

                result = edit(id=doc_id, type=case.doc_type, old_str="old text", new_str="new text")

                self._assert_parse_failure_result(case.list_fn, path, doc_id, result)
                self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
