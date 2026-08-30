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

Parameterized over all eight whole-body document types; seeds a real,
persisted document per type in a temp ``SPECMGR_DOCS_DIR`` via the domain's
own ``create_<d>`` tool (mirroring the fixture strategy of the per-domain
``tests/<d>/tools/test_update_<d>.py`` files still on disk at this phase).
Covers ACC-001 (whole-body mode) and ACC-002 (range mode) plus the
registration smoke test of Task 2.8.

Note on the per-type out-of-vocabulary field-value cases: ``req``, ``uc``,
``tsk``, ``gol``, ``rsk``, and ``dec`` each have a genuine field-level
``pydantic.ValidationError`` path in their body schema (closed vocabularies
or cross-field validators -- for ``dec``, a duplicated ``### Option``
number), while ``qa`` and ``prb`` bodies are free-form text only -- no
closed vocabulary, no field constraint -- so their out-of-vocabulary input
(an unrecognized section heading) fails structurally with ``AssertionError``
instead. Each type's case data flags which of the two its field-error input
raises.
"""

from __future__ import annotations

import asyncio
import importlib
import re
import tempfile
import textwrap
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError
from biz.dfch.specmgr.sop.tools.create_sop import create_sop
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
from biz.dfch.specmgr.uc.tools.create_uc import create_uc

update_module = importlib.import_module("biz.dfch.specmgr.general.tools.update")
update = update_module.update

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

    ### Kickoff

    Started the task list.
    """
)

_TSK_UPDATED_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [x] Do the first thing
    - [ ] Do a new second thing

    ## Recent Updates

    ### Kickoff

    Started the task list.

    ### Progress

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

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized sections.\n"


class _FixedDatetime(datetime):
    """``datetime`` stand-in with a frozen ``now`` (the 1..N ≡ whole-body equivalence test)."""

    @classmethod
    def now(cls, tz: Any = None) -> datetime:
        result = datetime(2026, 8, 27, 12, 0, 0, 123456)
        return result


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eight whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    minimal_body: str
    updated_body: str
    #: A unique line of ``minimal_body``; replacing just that line keeps the document valid.
    middle_marker: str
    middle_replacement: str
    #: The fragment appended at ``begin = end = N+1`` (a valid trailing optional section).
    append_fragment: str
    #: The line from which ``end = N+1`` replaces through end of body.
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


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        not_found_error=ReqNotFoundError,
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
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
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
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        minimal_body=_TSK_MINIMAL_BODY,
        updated_body=_TSK_UPDATED_BODY,
        middle_marker="Started the task list.",
        middle_replacement="Started the task list with a kickoff note.",
        append_fragment="\n### Progress\n\nFinished the first item.\n",
        eof_marker="## Recent Updates",
        eof_fragment="## Recent Updates\n\n### Kickoff\n\nStarted the task list.\n",
        deletable_suffix="\n### Progress\n\nFinished the first item.\n",
        field_error_marker="- [ ] Do the first thing",
        field_error_fragment="- [z] Not a valid checkbox marker",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
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
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
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
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
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
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
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
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
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
    ),
    _Case(
        doc_type="sop",
        create=create_sop,
        not_found_error=SopNotFoundError,
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
    """ACC-001: whole-body mode (no ``begin``/``end``) across all eight types."""

    def test_replaces_body_preserving_id_type_status_created_version(self) -> None:
        """Whole-body mode must replace the body but preserve every frontmatter field but ``updated``."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)

                result = update(id=created.frontmatter.id, type=case.doc_type, content=case.updated_body)

                self.assertEqual(result.frontmatter.id, created.frontmatter.id)
                self.assertEqual(result.frontmatter.type, case.doc_type)
                self.assertEqual(result.frontmatter.status, created.frontmatter.status)
                self.assertEqual(result.frontmatter.created, created.frontmatter.created)
                self.assertEqual(result.frontmatter.version, created.frontmatter.version)
                self.assertNotEqual(result.frontmatter.updated, created.frontmatter.updated)
                self.assertIsNotNone(re.fullmatch(_MICROSECOND_TIMESTAMP, result.frontmatter.updated))
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
                    update(id=created.frontmatter.id, type=case.doc_type, content=smuggled)

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_structural_failure_raises_and_leaves_file_byte_identical(self) -> None:
        """A structurally invalid whole body must raise ``AssertionError``, leaving the file byte-identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(AssertionError):
                    update(id=created.frontmatter.id, type=case.doc_type, content=_MALFORMED_BODY)

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
                        id=created.frontmatter.id,
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
                    update(id="no-such-id", type=case.doc_type, content=case.minimal_body)


class TestUpdateRange(TempDocsDirTestCase):
    """ACC-002: range mode (``begin``/``end``) across all eight types."""

    def test_middle_range_replace_leaves_out_of_range_lines_byte_identical(self) -> None:
        """A single middle-line replace must change only that line, leaving every other line identical."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                k = _line_no(lines, case.middle_marker)

                update(id=created.frontmatter.id, type=case.doc_type, content=case.middle_replacement, begin=k, end=k)

                new_lines = body_text(self._doc_path(case)).splitlines()
                expected = lines[: k - 1] + [case.middle_replacement] + lines[k:]
                self.assertEqual(new_lines, expected)
                self.assertNotIn(case.middle_marker, new_lines)

    def test_n_plus_one_appends_at_end_of_body(self) -> None:
        """``begin = end = N+1`` must be a pure append after the last body line."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                n = len(lines)

                update(
                    id=created.frontmatter.id, type=case.doc_type, content=case.append_fragment, begin=n + 1, end=n + 1
                )

                expected = lines + case.append_fragment.splitlines()
                self.assertEqual(body_text(self._doc_path(case)).splitlines(), expected)

    def test_end_n_plus_one_replaces_through_end_of_body(self) -> None:
        """``end = N+1`` must extend the range through the last line, replacing it with the fragment."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                lines = body_text(self._doc_path(case)).splitlines()
                n = len(lines)
                k = _line_no(lines, case.eof_marker)

                update(id=created.frontmatter.id, type=case.doc_type, content=case.eof_fragment, begin=k, end=n + 1)

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

                update(id=created.frontmatter.id, type=case.doc_type, content="", begin=n_min + 1, end=len(lines))

                self.assertEqual(body_text(self._doc_path(case)), case.minimal_body.rstrip("\n"))

    def test_begin_one_end_n_equals_whole_body_mode(self) -> None:
        """``begin = 1``, ``end = N`` must produce the same file as whole-body mode with the identical text."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                doc_id = created.frontmatter.id
                with mock.patch.object(update_module, "datetime", _FixedDatetime):
                    update(id=doc_id, type=case.doc_type, content=case.updated_body)
                    path = self._doc_path(case)
                    whole_body_file = path.read_text(encoding="utf-8")
                    n = len(body_text(path).splitlines())

                    update(id=doc_id, type=case.doc_type, content=case.updated_body, begin=1, end=n)

                    self.assertEqual(path.read_text(encoding="utf-8"), whole_body_file)

    def test_exactly_one_of_begin_end_raises_value_error_before_file_access(self) -> None:
        """Passing exactly one of ``begin``/``end`` must raise ``ValueError`` -- even for an unknown id (no file access)."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._seed(case, case.minimal_body)

                with self.assertRaises(ValueError):
                    update(id="no-such-id-" + case.doc_type, type=case.doc_type, content="frag", begin=2)
                with self.assertRaises(ValueError):
                    update(id="no-such-id-" + case.doc_type, type=case.doc_type, content="frag", end=2)

    def test_begin_below_one_raises_value_error_file_untouched(self) -> None:
        """``begin < 1`` must raise ``ValueError`` naming the value and range, leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.frontmatter.id, type=case.doc_type, content="frag", begin=0, end=2)

                self.assertIn("begin", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_begin_above_end_raises_value_error_file_untouched(self) -> None:
        """``begin > end`` must raise ``ValueError`` naming both values, leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.frontmatter.id, type=case.doc_type, content="frag", begin=5, end=3)

                self.assertIn("begin", str(ctx.exception))
                self.assertIn("end", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_end_above_n_plus_one_raises_value_error_file_untouched(self) -> None:
        """``end > N+1`` must raise ``ValueError`` naming the value and the allowed range, file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")
                n = len(body_text(path).splitlines())

                with self.assertRaises(ValueError) as ctx:
                    update(id=created.frontmatter.id, type=case.doc_type, content="frag", begin=2, end=n + 2)

                self.assertIn("end", str(ctx.exception))
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_range_deleting_the_h1_raises_and_leaves_file_untouched(self) -> None:
        """A range deleting the H1 must raise ``AssertionError`` (structural), leaving the file untouched."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                created = self._seed(case, case.minimal_body)
                path = self._doc_path(case)
                before = path.read_text(encoding="utf-8")

                with self.assertRaises(AssertionError):
                    update(id=created.frontmatter.id, type=case.doc_type, content="", begin=1, end=1)

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
                            id=created.frontmatter.id,
                            type=case.doc_type,
                            content=case.field_error_fragment,
                            begin=n + 1,
                            end=n + 1,
                        )
                else:
                    k = _line_no(lines, case.field_error_marker)
                    with self.assertRaises(expected_error):
                        update(
                            id=created.frontmatter.id,
                            type=case.doc_type,
                            content=case.field_error_fragment,
                            begin=k,
                            end=k,
                        )

                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_range_mode_raises_domain_not_found_for_unknown_id(self) -> None:
        """Range mode must raise the domain's own not-found error for an unknown id."""
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                self._seed(case, case.minimal_body)

                with self.assertRaises(case.not_found_error):
                    update(id="no-such-id", type=case.doc_type, content="frag", begin=1, end=1)


class TestUpdateRegistration(unittest.TestCase):
    """Task 2.8: the live ``mcp`` registration carries ``update`` with the 9-value ``type`` enum and
    optional integer ``begin``/``end`` in its input schema."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_update_registered_with_type_enum_and_optional_range(self) -> None:
        """``update`` must be registered exactly once, with the 9-value ``type`` enum and optional int ``begin``/``end``."""
        matching = [t for t in self._tools if t.name == "update"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(type_prop["enum"], ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop"])
        self.assertEqual(type_prop["type"], "string")
        for name in ("begin", "end"):
            prop = schema["properties"][name]
            self.assertEqual(prop["anyOf"], [{"type": "integer"}, {"type": "null"}])
            self.assertIsNone(prop["default"])
        self.assertEqual(schema["required"], ["id", "type", "content"])


if __name__ == "__main__":
    unittest.main()
