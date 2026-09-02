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

"""Tests for the generic ``update`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 2).

Parameterized over all ten whole-body document types; seeds a real,
persisted document per type in a temp ``SPECMGR_DOCS_DIR`` via the domain's
own ``create_<d>`` tool (mirroring the fixture strategy of the per-domain
``tests/<d>/tools/test_update_<d>.py`` files still on disk at this phase).
Covers ACC-001 (whole-body mode) and ACC-002 (range mode) plus the
registration smoke test of Task 2.8.

Note on the per-type out-of-vocabulary field-value cases: ``req``, ``uc``,
``tsk``, ``gol``, ``rsk``, ``dec``, ``sop``, and ``vcr`` each have a genuine
field-level ``pydantic.ValidationError`` path in their body schema (closed
vocabularies or cross-field validators -- for ``dec``/``sop``/``vcr``, a
duplicated ``### Option``/``### Step``/``### AC-NNN`` number), while ``qa``
and ``prb`` bodies are
free-form text only -- no closed vocabulary, no field constraint -- so their
out-of-vocabulary input (an unrecognized section heading) fails structurally
with ``AssertionError`` instead. Each type's case data flags which of the
two its field-error input raises.
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
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, feat_base_dir
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.gol.models.v1 import GolDocument, GolFrontmatter
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError, gol_base_dir
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.prb.models.v1 import PrbDocument, PrbFrontmatter
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError, prb_base_dir
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.models.v2 import QaDocument, QaFrontmatter
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError, qa_base_dir
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.models.v1 import ReqDocument, ReqFrontmatter
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError, req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.models.v1 import RskDocument, RskFrontmatter
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError, rsk_base_dir
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sop.models.v1 import SopDocument, SopFrontmatter
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError, sop_base_dir
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.tsk.models.v1 import TskDocument, TskFrontmatter
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError, tsk_base_dir
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.models.v2 import UcDocument, UcFrontmatter
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError, uc_base_dir
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.vcr.models.v1 import VcrDocument, VcrFrontmatter
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError, vcr_base_dir
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

update_module = importlib.import_module("biz.dfch.specmgr.general.tools.update")
update = update_module.update

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

_REQ_UPDATED_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 90 °C.

    ## Description

    Updated description text.

    ## Characteristics

    1. Safety

    ## Level

    SHOULD

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

_UC_UPDATED_BODY = textwrap.dedent(
    """\
    # Buy Goods

    ## Characteristic Information

    ### Goal in Context

    Buyer issues an updated request directly to our company.

    ### Scope

    Company (the system being designed as a black box)

    ### Level

    User Goal

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
    3. Company ships the order.
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

_TSK_UPDATED_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [x] Do the first thing
    - [ ] Do a new second thing

    ## Recent Updates

    ### 2026-08-19 - Kickoff

    Started the task list.

    ### 2026-08-19 - Progress

    Finished the first item.
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

_QA_UPDATED_BODY = _QA_MINIMAL_BODY.replace("Some intro text.", "Updated intro text.")

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

_PRB_UPDATED_BODY = textwrap.dedent(
    """\
    # Simple Problem Statement

    ## Current State

    ### Summary

    Something is very wrong indeed.

    ### What Is the Problem?

    Widgets keep disappearing.

    ## Gap

    There is a much bigger gap than we thought.

    ## Future State

    It will actually be fixed.
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

_GOL_UPDATED_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output, fuel consumption, and price.

    ## Description

    Updated description text.

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

_RSK_UPDATED_BODY = textwrap.dedent(
    """\
    # Sample Risk

    ## Cause

    A revised root condition.

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

    Revised treatment measures.

    ## Residual Assessment

    ### Probability 1

    ### Impact 2
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

_DEC_UPDATED_BODY = textwrap.dedent(
    """\
    # Title of the Decision

    ## Context and Problem Statement

    Something is very wrong with the status quo.

    ## Decision Outcome

    We chose the revised arrangement.
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

_SOP_UPDATED_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for all new hires.

    ## Scope

    All new hires in the engineering organization.

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

_VCR_UPDATED_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is fully met.

    ## Coverage

    full

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes
    """
)

#: A minimal, valid feat body (ACC-008's injection coverage: feat is the one whole-body domain
#: whose id shape differs from the ten UUID domains, mirroring ``test_delete.py``'s own fixture).
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

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized sections.\n"


#: A fixed date+time timestamp (the 1..N ≡ whole-body equivalence test needs both calls
#: to bump ``updated`` to the identical value so the two resulting files compare byte-equal).
_FIXED_TIMESTAMP = "2026-08-27 12:00:00.123Z"

#: A well-formed but non-existent canonical UUID (feat-38-39-41-43-44 Phase 4: the id must be
#: well-formed to reach the domain's own not-found error past the new ``validate_id`` guard).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eight whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    #: The domain's own frontmatter class -- the type ``update`` must return (feat-69).
    frontmatter_type: type
    #: The domain's own document (frontmatter+body wrapper) class -- what ``update`` must
    #: NOT return any more (feat-69).
    document_type: type
    minimal_body: str
    updated_body: str
    #: A unique line of ``minimal_body``; replacing just that line keeps the document valid.
    middle_marker: str
    middle_replacement: str
    #: The fragment appended at ``offset = N+1`` (a valid trailing optional section).
    append_fragment: str
    #: The line from which ``offset`` (with ``limit`` omitted) replaces through end of body.
    eof_marker: str
    eof_fragment: str
    #: A valid optional trailing section appended to the seed for the empty-fragment
    #: deletion test (its lines, ``N_minimal+1..N``, are deleted).
    deletable_suffix: str
    #: The line to replace with ``field_error_fragment`` (or the fragment is appended
    #: at ``N+1`` when ``field_error_is_append``) to produce the domain's field-level
    #: failure.
    field_error_marker: str
    field_error_fragment: str
    field_error_is_append: bool
    #: Whether that field-level failure raises ``pydantic.ValidationError``
    #: (``req``/``uc``/``tsk``/``gol``/``rsk``) or structural ``AssertionError``
    #: (``qa``/``prb`` -- their body schemas have no field-level validation).
    field_error_is_validation: bool
    #: The section heading line that directly follows the blank line the
    #: ``limit = 0`` insert test targets (``offset = _line_no(lines, marker) -
    #: 1``); the inserted line joins the current section's text (or checklist),
    #: keeping the document valid.
    insert_marker: str
    #: The single line inserted by the ``limit = 0`` mid-body insert test.
    insert_line: str


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        not_found_error=ReqNotFoundError,
        frontmatter_type=ReqFrontmatter,
        document_type=ReqDocument,
        minimal_body=_REQ_MINIMAL_BODY,
        updated_body=_REQ_UPDATED_BODY,
        middle_marker="If the engine becomes too hot, the lifetime of the system decreases.",
        middle_replacement="Updated description text.",
        append_fragment="\n## Notes\n\nA note.\n",
        eof_marker="## Level",
        eof_fragment="## Level\n\nSHOULD\n\n## Source\n\nThe TISBA.\n",
        deletable_suffix="\n## Notes\n\nA note.\n",
        field_error_marker="MUST",
        field_error_fragment="NOT-A-VALID-LEVEL",
        field_error_is_append=False,
        field_error_is_validation=True,
        insert_marker="## Characteristics",
        insert_line="Inserted description detail.",
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
        frontmatter_type=UcFrontmatter,
        document_type=UcDocument,
        minimal_body=_UC_MINIMAL_BODY,
        updated_body=_UC_UPDATED_BODY,
        middle_marker="Buyer issues request directly to our company.",
        middle_replacement="Buyer issues an updated request directly to our company.",
        append_fragment="\n## Open Issues\n\n- Is the scope final?\n",
        eof_marker="## Main Success Scenario",
        eof_fragment=(
            "## Main Success Scenario\n\n"
            "1. Buyer calls in with a purchase request.\n"
            "2. Company creates order in system.\n"
            "3. Company ships the order.\n"
        ),
        deletable_suffix="\n## Open Issues\n\n- Is the scope final?\n",
        field_error_marker="## Extensions",
        field_error_fragment="## Extensions\n\n### Extension 99a. Out-of-range reference\n\n1. Not resolvable.\n",
        field_error_is_append=True,
        field_error_is_validation=True,
        insert_marker="### Scope",
        insert_line="Inserted goal context.",
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        frontmatter_type=TskFrontmatter,
        document_type=TskDocument,
        minimal_body=_TSK_MINIMAL_BODY,
        updated_body=_TSK_UPDATED_BODY,
        middle_marker="Started the task list.",
        middle_replacement="Started the task list with a kickoff note.",
        append_fragment="\n### 2026-08-19 - Progress\n\nFinished the first item.\n",
        eof_marker="## Recent Updates",
        eof_fragment="## Recent Updates\n\n### 2026-08-19 - Kickoff\n\nStarted the task list.\n",
        deletable_suffix="\n### 2026-08-19 - Progress\n\nFinished the first item.\n",
        field_error_marker="- [ ] Do the first thing",
        field_error_fragment="- [z] Not a valid checkbox marker",
        field_error_is_append=False,
        field_error_is_validation=True,
        insert_marker="## Recent Updates",
        insert_line="- [ ] Inserted task.",
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
        frontmatter_type=QaFrontmatter,
        document_type=QaDocument,
        minimal_body=_QA_MINIMAL_BODY,
        updated_body=_QA_UPDATED_BODY,
        middle_marker="Some intro text.",
        middle_replacement="Updated intro text.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Safety",
        eof_fragment="## Safety\n\nInterview notes here.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="## Functional Suitability",
        field_error_fragment="## Not A Category",
        field_error_is_append=False,
        field_error_is_validation=False,
        insert_marker="### Raw Requirements",
        insert_line="Inserted introduction detail.",
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
        frontmatter_type=PrbFrontmatter,
        document_type=PrbDocument,
        minimal_body=_PRB_MINIMAL_BODY,
        updated_body=_PRB_UPDATED_BODY,
        middle_marker="Something is wrong.",
        middle_replacement="Something is very wrong indeed.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Future State",
        eof_fragment="## Future State\n\nIt will actually be fixed.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="### Summary",
        field_error_fragment="### Not A Question",
        field_error_is_append=False,
        field_error_is_validation=False,
        insert_marker="## Gap",
        insert_line="Inserted summary detail.",
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
        frontmatter_type=GolFrontmatter,
        document_type=GolDocument,
        minimal_body=_GOL_MINIMAL_BODY,
        updated_body=_GOL_UPDATED_BODY,
        middle_marker="THE company shall provide engines that are competitive in power output and fuel consumption.",
        middle_replacement="THE company shall provide competitive engines in power output and fuel consumption.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Source",
        eof_fragment="## Source\n\nThe 2028 market analysis.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="## Source",
        field_error_fragment="## Priority\n\n100\n\n## Source",
        field_error_is_append=False,
        field_error_is_validation=True,
        insert_marker="## Source",
        insert_line="Inserted statement detail.",
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
        frontmatter_type=RskFrontmatter,
        document_type=RskDocument,
        minimal_body=_RSK_MINIMAL_BODY,
        updated_body=_RSK_UPDATED_BODY,
        middle_marker="A root condition.",
        middle_replacement="A revised root condition.",
        append_fragment="\n## Owner\n\nThe safety team.\n",
        eof_marker="## Residual Assessment",
        eof_fragment="## Residual Assessment\n\n### Probability 1\n\n### Impact 2\n",
        deletable_suffix="\n## Owner\n\nThe safety team.\n",
        field_error_marker="reduce",
        field_error_fragment="not-a-strategy",
        field_error_is_append=False,
        field_error_is_validation=True,
        insert_marker="## Trigger",
        insert_line="Inserted cause detail.",
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
        frontmatter_type=DecFrontmatter,
        document_type=DecDocument,
        minimal_body=_DEC_MINIMAL_BODY,
        updated_body=_DEC_UPDATED_BODY,
        middle_marker="Something is wrong with the status quo.",
        middle_replacement="Something is very wrong with the status quo.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Decision Outcome",
        eof_fragment="## Decision Outcome\n\nWe chose the revised arrangement.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
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
        insert_marker="## Decision Outcome",
        insert_line="Inserted context detail.",
    ),
    _Case(
        doc_type="sop",
        create=create_sop,
        not_found_error=SopNotFoundError,
        frontmatter_type=SopFrontmatter,
        document_type=SopDocument,
        minimal_body=_SOP_MINIMAL_BODY,
        updated_body=_SOP_UPDATED_BODY,
        middle_marker="Provision accounts for new hires.",
        middle_replacement="Provision accounts for all new hires.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Procedure",
        eof_fragment="## Procedure\n\n### Step 1: Submit request\n\nHR submits the revised request.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="### Step 1: Submit request",
        field_error_fragment=("\n### Step 1: Duplicate step\n\nDuplicate step text.\n"),
        field_error_is_append=True,
        field_error_is_validation=True,
        insert_marker="## Procedure",
        insert_line="Inserted purpose detail.",
    ),
    _Case(
        doc_type="vcr",
        create=create_vcr,
        not_found_error=VcrNotFoundError,
        frontmatter_type=VcrFrontmatter,
        document_type=VcrDocument,
        minimal_body=_VCR_MINIMAL_BODY,
        updated_body=_VCR_UPDATED_BODY,
        middle_marker="Confirms that the sample requirement is met.",
        middle_replacement="Confirms that the sample requirement is thoroughly met.",
        append_fragment="\n## More Information\n\nAdditional verification context.\n",
        eof_marker="## Acceptance Criteria",
        eof_fragment="## Acceptance Criteria\n\n### AC-001 (Test): The sample criterion passes, revised\n",
        deletable_suffix="\n## More Information\n\nAdditional verification context.\n",
        field_error_marker="### AC-001 (Test): The sample criterion passes",
        field_error_fragment="\n### AC-001 (Analysis): Duplicate AC number\n",
        field_error_is_append=True,
        field_error_is_validation=True,
        insert_marker="## Coverage",
        insert_line="Inserted verification detail.",
    ),
]


def _line_no(lines: list[str], marker: str) -> int:
    """Return the 1-based line number of the first line equal to ``marker``."""
    result = lines.index(marker) + 1
    return result


def _field_error_body(case: _Case, base_body: str) -> str:
    """Apply ``case``'s field-level failure to ``base_body`` (line replace or append)."""
    lines = base_body.splitlines()
    if case.field_error_is_append:
        new_lines = lines + case.field_error_fragment.splitlines()
    else:
        idx = lines.index(case.field_error_marker)
        new_lines = lines[:idx] + case.field_error_fragment.splitlines() + lines[idx + 1 :]
    result = "\n".join(new_lines) + "\n"
    return result


class TempDocsDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

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


class TestUpdateWholeBody(TempDocsDirTestCase):
    """ACC-001: whole-body mode (no ``offset``/``limit``) across all eight types."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """Whole-body mode must replace the body but preserve every frontmatter field but ``updated``."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)

                result = update(id=created.id, type=case.doc_type, content=case.updated_body)

                self.assertIsInstance(result, case.frontmatter_type)
                self.assertNotIsInstance(result, case.document_type)
                self.assertFalse(hasattr(result, "body"))
                self.assertEqual(result.id, created.id)
                self.assertEqual(result.type, case.doc_type)
                self.assertEqual(result.status, created.status)
                self.assertEqual(result.created, created.created)
                self.assertEqual(result.version, created.version)
                self.assertNotEqual(result.updated, created.updated)
                self.assertIsNotNone(re.fullmatch(_DATE_TIME_TIMESTAMP, result.updated))
                self.assertEqual(body_text(self._doc_path(case)), case.updated_body.rstrip("\n"))

    def test_status_not_settable_through_update(self) -> None:
        """A YAML frontmatter block smuggled into ``content`` must fail validation, leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")
                smuggled = "---\nstatus: accepted\n---\n" + case.updated_body

                with self.assertRaises(AssertionError):
                    update(id=created.id, type=case.doc_type, content=smuggled)

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_structural_failure_raises_and_leaves_file_byte_identical(self) -> None:
        """A structurally invalid whole body must raise ``AssertionError``, leaving the file byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(AssertionError):
                    update(id=created.id, type=case.doc_type, content=_MALFORMED_BODY)

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_field_validation_failure_raises_and_leaves_file_byte_identical(self) -> None:
        """An out-of-vocabulary field value must raise, leaving the file byte-identical (per-type error type)."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")
                expected_error = ValidationError if case.field_error_is_validation else AssertionError

                with self.assertRaises(expected_error):
                    update(
                        id=created.id,
                        type=case.doc_type,
                        content=_field_error_body(case, case.minimal_body),
                    )

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_raises_domain_not_found_for_unknown_id(self) -> None:
        """Whole-body mode must raise the domain's own not-found error for an unknown id."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._seed(case, case.minimal_body)

                with self.assertRaises(case.not_found_error):
                    update(id=_MISSING_UUID, type=case.doc_type, content=case.minimal_body)


class TestUpdateRange(TempDocsDirTestCase):
    """ACC-002: range mode (``offset``/``limit``) across all eight types."""

    def test_middle_range_replace_leaves_out_of_range_lines_byte_identical(self) -> None:
        """A single middle-line replace must change only that line, leaving every other line identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                k = _line_no(lines, case.middle_marker)

                update(id=created.id, type=case.doc_type, content=case.middle_replacement, offset=k, limit=1)

                new_lines = body_text(self._doc_path(case)).splitlines()
                expected = lines[: k - 1] + [case.middle_replacement] + lines[k:]
                self.assertEqual(new_lines, expected)
                self.assertNotIn(case.middle_marker, new_lines)

    def test_zero_limit_inserts_without_dropping(self) -> None:
        """``limit = 0`` must be a pure mid-body insert: no line dropped, fragment in, rest byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                offset = _line_no(lines, case.insert_marker) - 1

                update(id=created.id, type=case.doc_type, content=case.insert_line, offset=offset, limit=0)

                self.assertEqual(
                    body_text(self._doc_path(case)).splitlines(),
                    lines[: offset - 1] + [case.insert_line] + lines[offset - 1 :],
                )

    def test_n_plus_one_appends_at_end_of_body(self) -> None:
        """``offset = N+1`` with ``limit = 0`` must be a pure append after the last body line."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                n = len(lines)

                update(id=created.id, type=case.doc_type, content=case.append_fragment, offset=n + 1, limit=0)

                expected = lines + case.append_fragment.splitlines()
                self.assertEqual(body_text(self._doc_path(case)).splitlines(), expected)

    def test_limit_omitted_replaces_through_end_of_body(self) -> None:
        """An omitted ``limit`` must extend the range through the last line, replacing it with the fragment."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                k = _line_no(lines, case.eof_marker)

                update(id=created.id, type=case.doc_type, content=case.eof_fragment, offset=k)

                expected = lines[: k - 1] + case.eof_fragment.splitlines()
                self.assertEqual(body_text(self._doc_path(case)).splitlines(), expected)

    def test_empty_content_deletes_an_optional_section(self) -> None:
        """An empty fragment must delete the range -- here an optional trailing section, yielding a still-valid document."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                seed_body = case.minimal_body + case.deletable_suffix
                created = self._seed(case, seed_body)
                lines = body_text(self._doc_path(case)).splitlines()
                n_min = len(case.minimal_body.splitlines())

                update(
                    id=created.id,
                    type=case.doc_type,
                    content="",
                    offset=n_min + 1,
                    limit=len(lines) - n_min,
                )

                self.assertEqual(body_text(self._doc_path(case)), case.minimal_body.rstrip("\n"))

    def test_offset_one_equals_whole_body_mode(self) -> None:
        """``offset = 1`` (``limit`` omitted) must produce the same file as whole-body mode with the identical text."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                doc_id = created.id
                with mock.patch.object(update_module, "now_timestamp", return_value=_FIXED_TIMESTAMP):
                    update(id=doc_id, type=case.doc_type, content=case.updated_body)
                    path = self._doc_path(case)
                    whole_body_file = path.read_text(encoding="utf-8")

                    update(id=doc_id, type=case.doc_type, content=case.updated_body, offset=1)

                    self.assertEqual(path.read_text(encoding="utf-8"), whole_body_file)

    def test_limit_without_offset_raises_value_error_before_file_access(self) -> None:
        """``limit`` without ``offset`` must raise ``ValueError`` -- even for an unknown id (no file access)."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)

                with self.assertRaises(ValueError):
                    update(id=_MISSING_UUID, type=case.doc_type, content="frag", limit=2)
                with self.assertRaises(ValueError):
                    update(id=created.id, type=case.doc_type, content="frag", limit=2)

    def test_offset_below_one_raises_value_error_file_untouched(self) -> None:
        """``offset < 1`` must raise ``ValueError`` naming the value and range, leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.id, type=case.doc_type, content="frag", offset=0, limit=3)

                self.assertIn("offset", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_offset_above_n_plus_one_raises_value_error_file_untouched(self) -> None:
        """``offset > N+1`` must raise ``ValueError`` naming the value and range, leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")
                n = len(body_text(path).splitlines())

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.id, type=case.doc_type, content="frag", offset=n + 2, limit=1)

                self.assertIn("offset", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_negative_limit_raises_value_error_file_untouched(self) -> None:
        """``limit < 0`` must raise ``ValueError`` naming the value and range, leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.id, type=case.doc_type, content="frag", offset=5, limit=-2)

                self.assertIn("limit", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_offset_plus_limit_past_body_raises_value_error_file_untouched(self) -> None:
        """``offset + limit - 1 > N`` must raise ``ValueError`` naming the values and range, file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")
                n = len(body_text(path).splitlines())

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.id, type=case.doc_type, content="frag", offset=2, limit=n + 1)

                self.assertIn("offset", str(ctx.exception))
                self.assertIn("limit", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_range_deleting_the_h1_raises_and_leaves_file_untouched(self) -> None:
        """A range deleting the H1 must raise ``AssertionError`` (structural), leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(AssertionError):
                    update(id=created.id, type=case.doc_type, content="", offset=1, limit=1)

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_range_producing_out_of_vocabulary_value_raises_and_leaves_file_untouched(self) -> None:
        """A range producing an out-of-vocabulary field value must raise, leaving the file untouched (per-type error)."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")
                lines = body_text(path).splitlines()
                expected_error = ValidationError if case.field_error_is_validation else AssertionError

                if case.field_error_is_append:
                    n = len(lines)
                    with self.assertRaises(expected_error):
                        update(
                            id=created.id,
                            type=case.doc_type,
                            content=case.field_error_fragment,
                            offset=n + 1,
                            limit=0,
                        )
                else:
                    k = _line_no(lines, case.field_error_marker)
                    with self.assertRaises(expected_error):
                        update(
                            id=created.id,
                            type=case.doc_type,
                            content=case.field_error_fragment,
                            offset=k,
                            limit=1,
                        )

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_range_mode_raises_domain_not_found_for_unknown_id(self) -> None:
        """Range mode must raise the domain's own not-found error for an unknown id."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._seed(case, case.minimal_body)

                with self.assertRaises(case.not_found_error):
                    update(id=_MISSING_UUID, type=case.doc_type, content="frag", offset=1, limit=1)


class TestUpdateRegistration(unittest.TestCase):
    """Task 2.8: the live ``mcp`` registration carries ``update`` with the 11-value ``type`` enum and
    optional integer ``offset``/``limit`` in its input schema (and no ``begin``/``end`` any more)."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_update_registered_with_type_enum_and_optional_range(self) -> None:
        """``update`` must be registered once, with the 11-value ``type`` enum and optional int ``offset``/``limit``."""
        matching = [t for t in self._tools if t.name == "update"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(
            type_prop["enum"], ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr"]
        )
        self.assertEqual(type_prop["type"], "string")
        for name in ("offset", "limit"):
            prop = schema["properties"][name]
            self.assertEqual(prop["anyOf"], [{"type": "integer"}, {"type": "null"}])
            self.assertIsNone(prop["default"])
        self.assertNotIn("begin", schema["properties"])
        self.assertNotIn("end", schema["properties"])
        self.assertEqual(schema["required"], ["id", "type", "content"])


@dataclass(frozen=True)
class _InjectionCase:
    """Per-type test data for the eleven whole-body domains' ``_path_safety`` coverage (ACC-008)."""

    doc_type: str
    create: Callable[[str], Any]
    base_dir: Callable[[], Path]
    minimal_body: str
    #: A well-formed id of a *different* domain shape (feat-NNN-slug for the UUID domains, a UUID for feat).
    wrong_format_id: str


#: The pinned path-injection shapes (mirrors ``test_delete.py``'s own ``_TRAVERSAL_IDS``).
_TRAVERSAL_IDS = ("../x", "a/b", "a\\b", "..")

#: A well-formed feat-NNN-slug folder name (the wrong-format id for the ten UUID domains).
_FEAT_SLUG_ID = "feat-36-delete"

_INJECTION_CASES: list[_InjectionCase] = [
    _InjectionCase("req", create_req, req_base_dir, _REQ_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("uc", create_uc, uc_base_dir, _UC_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("tsk", create_tsk, tsk_base_dir, _TSK_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("qa", create_qa, qa_base_dir, _QA_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("prb", create_prb, prb_base_dir, _PRB_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("gol", create_gol, gol_base_dir, _GOL_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("rsk", create_rsk, rsk_base_dir, _RSK_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("dec", create_dec, dec_base_dir, _DEC_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("sop", create_sop, sop_base_dir, _SOP_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("vcr", create_vcr, vcr_base_dir, _VCR_MINIMAL_BODY, _FEAT_SLUG_ID),
    _InjectionCase("feat", create_feat, feat_base_dir, _FEAT_MINIMAL_BODY, _MISSING_UUID),
]


class TempUpdateInjectionDirTestCase(unittest.TestCase):
    """Common fixture for ACC-008: temp dirs for both SPECMGR_DOCS_DIR and SPECMGR_FEAT_DIR
    (mirrors ``test_delete.py``'s ``TempDeleteDirTestCase``, since injection coverage spans
    all eleven whole-body domains, feat included)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {DOCS_DIR_ENV_VAR: str(self.docs_root), FEAT_DIR_ENV_VAR: str(self.feat_dir)},
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


class TestUpdateInjection(TempUpdateInjectionDirTestCase):
    """ACC-008: injection ids raise ValueError before any filesystem access; the seeded document untouched."""

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
                            update(id=bad_id, type=case.doc_type, content="irrelevant")
                        self.assertEqual(path.read_text(encoding="utf-8"), before)


class TestUpdateAssertWithinSpy(TempUpdateInjectionDirTestCase):
    """ACC-008: ``assert_within`` is actually invoked (not just present in source) during a valid update."""

    def test_assert_within_is_called_with_base_dir_and_resolved_path(self) -> None:
        """For each of the eleven domains, a valid whole-body update must call ``assert_within(base_dir, path)``."""
        for case in _INJECTION_CASES:
            with self.subTest(doc_type=case.doc_type):
                created = case.create(case.minimal_body)
                doc_id = created.id
                path = self._doc_path(case, doc_id)
                base_dir = case.base_dir()

                with mock.patch.object(update_module, "assert_within", wraps=update_module.assert_within) as spy:
                    update(id=doc_id, type=case.doc_type, content=case.minimal_body)

                spy.assert_any_call(base_dir, path)


if __name__ == "__main__":
    unittest.main()
