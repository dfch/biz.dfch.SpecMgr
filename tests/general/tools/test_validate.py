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

"""Tests for the generic ``validate`` ``@mcp.tool()`` wrapper (feat-81-83-validation, Phase 2).

Parameterized over the twelve whole-body document types the generic tool covers (``adr`` is
excluded, mirroring ``update``/``set_classification``/``delete``'s own 12-way precedent); the
per-domain fixture bodies below are 1:1 ports of the retired per-domain ``test_validate_<d>.py``
files' own ``_MINIMAL_BODY``/``_MALFORMED_BODY``/``_FULL_DOCUMENT`` constants (Task 2.5's
coverage-superseded rationale).

Covers, per REQ-004/ACC-004:

- A valid body-only content and a valid complete document both validate successfully
  (``{valid: True, errors: []}``) for all twelve domains.
- A structurally invalid body-only content never raises -- it returns
  ``{valid: False, errors: [{message: str}]}`` (the ``AssertionError`` channel).
- A field/cross-field-invalid body-only content likewise never raises -- same shape (the
  ``pydantic.ValidationError`` channel), for every domain with a straightforward field/
  cross-field failure mode ported from its own retired test.
- ``validate(type="adr", ...)`` and any other unsupported ``type`` still raise ``ValueError``.
- For a representative sample of domains (``req``, ``dec``, ``vcr``), a ``full``/content-shape
  mismatch (``full=True`` with body-only content, and ``full=False`` with a complete document)
  still raises ``ValueError`` through the generic tool, rather than being swallowed into
  ``{valid: false}``.
- The two regression fixtures from this feature's own Phase 1 investigation (the ``req``
  naive-isoformat-timestamp repro and the ``dec`` em-dash-heading repro) reproduced through the
  new generic ``validate`` tool, asserting ``{valid: False, errors: [...]}`` with the enriched
  message present, not a raised exception.
"""

from __future__ import annotations

import textwrap
import unittest
from dataclasses import dataclass
from typing import Callable

import yaml

from biz.dfch.specmgr.dec.models.v1 import parse_dec as _parse_dec
from biz.dfch.specmgr.general.tools.validate import validate
from biz.dfch.specmgr.models.md._errors import wrap_tool_errors
from biz.dfch.specmgr.req.models.v1 import parse_req as _parse_req

# ---------------------------------------------------------------------------
# Per-domain fixture bodies -- 1:1 ports of the retired test_validate_<d>.py files' own
# _MINIMAL_BODY/_MALFORMED_BODY/_FULL_DOCUMENT (and, where applicable, a field/cross-field-
# invalid body) constants.
# ---------------------------------------------------------------------------

_REQ_MINIMAL_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

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
_REQ_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized requirement sections.\n"
_REQ_BAD_FIELD_BODY = _REQ_MINIMAL_BODY.replace("MUST", "NOT-A-VALID-LEVEL")
_REQ_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: req-001
    type: req
    version: 1.0.0
    status: draft
    created: '2026-08-05 00:00:00.000Z'
    updated: '2026-08-05 00:00:00.000Z'
    ---

    """
    )
    + _REQ_MINIMAL_BODY
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
_UC_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized use-case sections.\n"
_UC_BAD_FIELD_BODY = _UC_MINIMAL_BODY + (
    "\n## Extensions\n\n### Extension 99a. Out-of-range reference\n\n1. Not resolvable.\n"
)
_UC_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: uc-001
    type: uc
    version: 1.0.0
    status: draft
    created: '2026-08-05 00:00:00.000Z'
    updated: '2026-08-05 00:00:00.000Z'
    ---

    """
    )
    + _UC_MINIMAL_BODY
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
_TSK_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized task list sections.\n"
_TSK_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: tsk-001
    type: tsk
    version: 1.0.0
    status: draft
    created: '2026-08-16 00:00:00.000Z'
    updated: '2026-08-16 00:00:00.000Z'
    ---

    """
    )
    + _TSK_MINIMAL_BODY
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
_QA_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized QA sections.\n"
_QA_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: qa-001
    type: qa
    version: 1.0.0
    status: draft
    created: '2026-08-18 00:00:00.000Z'
    updated: '2026-08-18 00:00:00.000Z'
    ---

    """
    )
    + _QA_MINIMAL_BODY
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
_PRB_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized problem statement sections.\n"
_PRB_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: prb-001
    type: prb
    version: 1.0.0
    status: draft
    created: '2026-08-25 00:00:00.000Z'
    updated: '2026-08-25 00:00:00.000Z'
    ---

    """
    )
    + _PRB_MINIMAL_BODY
)

_GOL_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)
_GOL_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized goal sections.\n"
_GOL_BAD_FIELD_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Priority

    100

    ## Source

    The vehicle program's 2027 market analysis
    """
)
_GOL_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: gol-001
    type: gol
    version: 1.0.0
    status: draft
    created: '2026-08-25 00:00:00.000Z'
    updated: '2026-08-25 00:00:00.000Z'
    ---

    """
    )
    + _GOL_MINIMAL_BODY
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
_RSK_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized risk sections.\n"
_RSK_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: rsk-001
    type: rsk
    version: 1.0.0
    status: open
    created: '2026-08-24 00:00:00.000Z'
    updated: '2026-08-24 00:00:00.000Z'
    ---

    """
    )
    + _RSK_MINIMAL_BODY
)

_DEC_MINIMAL_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.
    """
)
_DEC_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized decision sections.\n"
_DEC_BAD_FIELD_BODY = textwrap.dedent(
    """\
    # Choose a Document Store

    ## Context and Problem Statement

    The current store cannot serve the dashboard read path.

    ## Decision Outcome

    We chose the document store.

    ## Pros and Cons

    ### Option 1: Document Store

    Meets the latency budget.

    ### Option 1: Key-Value Store

    Even faster reads.
    """
)
_DEC_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: dec-001
    type: dec
    version: 1.0.0
    status: draft
    created: '2026-08-26 00:00:00.000Z'
    updated: '2026-08-26 00:00:00.000Z'
    ---

    """
    )
    + _DEC_MINIMAL_BODY
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
_SOP_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized SOP sections.\n"
_SOP_BAD_FIELD_BODY = textwrap.dedent(
    """\
    # New Employee IT Account Provisioning

    ## Purpose

    Provision accounts for new hires.

    ## Procedure

    ### Step 1: Submit request

    HR submits the request.

    ### Step 1: Duplicate step

    HR submits the request again.
    """
)
_SOP_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: sop-001
    type: sop
    version: 1.0.0
    status: draft
    created: '2026-08-30 00:00:00.000Z'
    updated: '2026-08-30 00:00:00.000Z'
    ---

    """
    )
    + _SOP_MINIMAL_BODY
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
_FEAT_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized feature sections.\n"
_FEAT_BAD_FIELD_BODY = _FEAT_MINIMAL_BODY.replace(
    "- [ ] ACC-001: Render time stays below 200ms.",
    "- [ ] Not a valid ACC item at all.",
)
_FEAT_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: feat-1-example-widget
    type: feat
    version: 1.0.0
    status: planning
    created: '2026-08-30 00:00:00.000Z'
    updated: '2026-08-30 00:00:00.000Z'
    ---

    """
    )
    + _FEAT_MINIMAL_BODY
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
_VCR_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized verification case record sections.\n"
_VCR_BAD_FIELD_BODY = textwrap.dedent(
    """\
    # Sample Verification Case

    ## Verifies

    REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Sample requirement title

    Confirms that the sample requirement is met.

    ## Coverage

    partial

    ## Acceptance Criteria

    ### AC-001 (Test): The sample criterion passes

    ### AC-001 (Analysis): Duplicate AC number
    """
)
_VCR_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: vcr-001
    type: vcr
    version: 1.0.0
    status: draft
    created: '2026-08-31 00:00:00.000Z'
    updated: '2026-08-31 00:00:00.000Z'
    ---

    """
    )
    + _VCR_MINIMAL_BODY
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
_SYSRS_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized System Requirements Specification sections.\n"
_SYSRS_BAD_FIELD_BODY = _SYSRS_MINIMAL_BODY.replace(f"- GOL {_SYSRS_GOL_ID}", f"- PRB {_SYSRS_GOL_ID}")
_SYSRS_FULL_DOCUMENT = (
    textwrap.dedent(
        """\
    ---
    id: sysrs-001
    type: sysrs
    version: 1.0.0
    status: draft
    created: '2026-08-31 00:00:00.000Z'
    updated: '2026-08-31 00:00:00.000Z'
    ---

    """
    )
    + _SYSRS_MINIMAL_BODY
)


@dataclass(frozen=True)
class _Case:
    """Per-domain fixture bundle for the parameterized tests below."""

    doc_type: str
    minimal_body: str
    malformed_body: str
    full_document: str
    #: A field/cross-field-invalid body-only content (the `pydantic.ValidationError` channel),
    #: or `None` if the retired per-domain test had no straightforward top-level fixture for it.
    bad_field_body: str | None


_CASES: list[_Case] = [
    _Case("req", _REQ_MINIMAL_BODY, _REQ_MALFORMED_BODY, _REQ_FULL_DOCUMENT, _REQ_BAD_FIELD_BODY),
    _Case("uc", _UC_MINIMAL_BODY, _UC_MALFORMED_BODY, _UC_FULL_DOCUMENT, _UC_BAD_FIELD_BODY),
    _Case("tsk", _TSK_MINIMAL_BODY, _TSK_MALFORMED_BODY, _TSK_FULL_DOCUMENT, None),
    _Case("qa", _QA_MINIMAL_BODY, _QA_MALFORMED_BODY, _QA_FULL_DOCUMENT, None),
    _Case("prb", _PRB_MINIMAL_BODY, _PRB_MALFORMED_BODY, _PRB_FULL_DOCUMENT, None),
    _Case("gol", _GOL_MINIMAL_BODY, _GOL_MALFORMED_BODY, _GOL_FULL_DOCUMENT, _GOL_BAD_FIELD_BODY),
    _Case("rsk", _RSK_MINIMAL_BODY, _RSK_MALFORMED_BODY, _RSK_FULL_DOCUMENT, None),
    _Case("dec", _DEC_MINIMAL_BODY, _DEC_MALFORMED_BODY, _DEC_FULL_DOCUMENT, _DEC_BAD_FIELD_BODY),
    _Case("sop", _SOP_MINIMAL_BODY, _SOP_MALFORMED_BODY, _SOP_FULL_DOCUMENT, _SOP_BAD_FIELD_BODY),
    _Case("feat", _FEAT_MINIMAL_BODY, _FEAT_MALFORMED_BODY, _FEAT_FULL_DOCUMENT, _FEAT_BAD_FIELD_BODY),
    _Case("vcr", _VCR_MINIMAL_BODY, _VCR_MALFORMED_BODY, _VCR_FULL_DOCUMENT, _VCR_BAD_FIELD_BODY),
    _Case("sysrs", _SYSRS_MINIMAL_BODY, _SYSRS_MALFORMED_BODY, _SYSRS_FULL_DOCUMENT, _SYSRS_BAD_FIELD_BODY),
]


class TestValidateAllDomains(unittest.TestCase):
    """ACC-003/ACC-004: the generic tool across all twelve applicable domains."""

    def test_returns_valid_true_for_body_only_content(self) -> None:
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                result = validate(type=case.doc_type, content=case.minimal_body)
                self.assertTrue(result.valid)
                self.assertEqual(result.errors, [])

    def test_returns_valid_true_for_a_complete_document(self) -> None:
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                result = validate(type=case.doc_type, content=case.full_document, full=True)
                self.assertTrue(result.valid)
                self.assertEqual(result.errors, [])

    def test_structural_failure_returns_valid_false_with_one_error_never_raises(self) -> None:
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                result = validate(type=case.doc_type, content=case.malformed_body)
                self.assertFalse(result.valid)
                self.assertEqual(len(result.errors), 1)
                self.assertIsInstance(result.errors[0].message, str)
                self.assertTrue(result.errors[0].message)

    def test_field_validation_failure_returns_valid_false_with_one_error_never_raises(self) -> None:
        for case in _CASES:
            if case.bad_field_body is None:
                continue
            with self.subTest(doc_type=case.doc_type):
                result = validate(type=case.doc_type, content=case.bad_field_body)
                self.assertFalse(result.valid)
                self.assertEqual(len(result.errors), 1)
                self.assertIsInstance(result.errors[0].message, str)
                self.assertTrue(result.errors[0].message)

    def test_invalid_frontmatter_field_when_full_returns_valid_false_never_raises(self) -> None:
        for case in _CASES:
            with self.subTest(doc_type=case.doc_type):
                text = case.full_document.replace("status: draft", "status: not-a-real-status")
                if "status: not-a-real-status" not in text:
                    # gol/rsk/feat don't have a literal "status: draft" in their fixture -- skip
                    # rather than silently no-op the substitution.
                    continue
                result = validate(type=case.doc_type, content=text, full=True)
                self.assertFalse(result.valid)
                self.assertEqual(len(result.errors), 1)


class TestValidateUnsupportedType(unittest.TestCase):
    """ACC-004: an unsupported `type` (including `"adr"`) must still raise `ValueError`."""

    def test_adr_type_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="adr", content=_REQ_MINIMAL_BODY)  # type: ignore[arg-type]

    def test_unknown_type_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="bogus", content="irrelevant")  # type: ignore[arg-type]


class TestValidateFullShapeMismatchRaises(unittest.TestCase):
    """ACC-004: a `full`/content-shape mismatch must still raise `ValueError`, for a
    representative sample of domains (`req`, `dec`, `vcr`) -- never swallowed into
    `{valid: false}`."""

    def test_req_full_true_with_body_only_content_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="req", content=_REQ_MINIMAL_BODY, full=True)

    def test_req_full_false_with_complete_document_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="req", content=_REQ_FULL_DOCUMENT)

    def test_dec_full_true_with_body_only_content_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="dec", content=_DEC_MINIMAL_BODY, full=True)

    def test_dec_full_false_with_complete_document_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="dec", content=_DEC_FULL_DOCUMENT)

    def test_vcr_full_true_with_body_only_content_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="vcr", content=_VCR_MINIMAL_BODY, full=True)

    def test_vcr_full_false_with_complete_document_raises(self) -> None:
        with self.assertRaises(ValueError):
            validate(type="vcr", content=_VCR_FULL_DOCUMENT)


class TestValidateIssue83Regressions(unittest.TestCase):
    """REQ-008: issue #83's two literal repro bodies, reproduced through the generic `validate`
    tool, asserting `{valid: False, errors: [...]}` with the enriched message present -- not a
    raised exception (feat-81-83-validation Phase 1 Design Notes)."""

    def test_req_naive_isoformat_timestamp_repro(self) -> None:
        """A `req` document with naive-isoformat `created`/`updated` (no `Z`/offset)."""
        text = _REQ_FULL_DOCUMENT.replace(
            "created: '2026-08-05 00:00:00.000Z'", "created: '2026-08-05T08:15:42'"
        ).replace("updated: '2026-08-05 00:00:00.000Z'", "updated: '2026-08-06T03:27:27'")

        result = validate(type="req", content=text, full=True)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        message = result.errors[0].message
        self.assertIn(
            "must be the date+time variant 'yyyy-MM-dd HH:mm:ss.fff' followed by 'Z' or a signed "
            "'+HH:mm'/'-HH:mm' offset",
            message,
        )

    def test_dec_em_dash_heading_repro(self) -> None:
        """A `dec` document with an em dash instead of a hyphen in an `## Updates` sub-heading."""
        body_with_updates = _DEC_MINIMAL_BODY + ("\n## Updates\n\n### 2026-08-27 \u2014 Created\n\nSome update text.\n")
        text = (
            textwrap.dedent(
                """\
            ---
            id: dec-002
            type: dec
            version: 1.0.0
            status: draft
            created: '2026-08-27 00:00:00.000Z'
            updated: '2026-08-27 00:00:00.000Z'
            ---

            """
            )
            + body_with_updates
        )

        result = validate(type="dec", content=text, full=True)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        self.assertTrue(result.errors[0].message)


class TestValidateYamlErrorEnrichment(unittest.TestCase):
    """REQ-010/ACC-010 (feat-81-83-validation, Phase 6): a malformed-YAML-frontmatter
    ``validate(type=<d>, ..., full=True)`` call's error message must be textually identical to
    ``parse_<d>``'s own message for byte-identical input, modulo the ``wrap_tool_errors`` label
    prefix itself (``"validate"`` vs. ``"parse_<d>"``).

    Regression test for the gap fixed by ``general/tools/validate.py::_detect_frontmatter``:
    before that fix, each adapter's raw, unwrapped ``has_frontmatter`` probe raised PyYAML's own
    opaque error (``"<unicode string>"`` location, block-relative line number) instead of the
    frontmatter-block-naming, document-relative-line-remapped form every ``parse_<d>`` tool
    already produced -- this test fails if that fix is reverted.
    """

    def _assert_message_parity(
        self,
        doc_type: str,
        malformed: str,
        parse_fn: Callable[[str], object],
        parse_tool_name: str,
    ) -> None:
        """Assert ``validate``'s and ``parse_<d>``'s error messages agree past their own labels."""
        result = validate(type=doc_type, content=malformed, full=True)  # type: ignore[arg-type]
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        validate_message = result.errors[0].message

        with self.assertRaises(yaml.YAMLError) as caught:
            with wrap_tool_errors(domain=doc_type, tool=parse_tool_name):
                parse_fn(malformed)
        parse_message = str(caught.exception)

        validate_label = f"{doc_type} validate: "
        parse_label = f"{doc_type} {parse_tool_name}: "
        self.assertTrue(validate_message.startswith(validate_label), validate_message)
        self.assertTrue(parse_message.startswith(parse_label), parse_message)
        # Same block-naming + document-relative line number on both sides, modulo the label.
        self.assertEqual(validate_message[len(validate_label) :], parse_message[len(parse_label) :])
        self.assertIn('"the frontmatter block"', validate_message)

    def test_req_malformed_yaml_frontmatter_matches_parse_req(self) -> None:
        malformed = f"---\nid: req-1\nstatus: [unterminated\n---\n{_REQ_MINIMAL_BODY}"
        self._assert_message_parity("req", malformed, _parse_req, "parse_req")

    def test_dec_malformed_yaml_frontmatter_matches_parse_dec(self) -> None:
        malformed = f"---\nid: dec-1\nstatus: [unterminated\n---\n{_DEC_MINIMAL_BODY}"
        self._assert_message_parity("dec", malformed, _parse_dec, "parse_dec")


if __name__ == "__main__":
    unittest.main()
