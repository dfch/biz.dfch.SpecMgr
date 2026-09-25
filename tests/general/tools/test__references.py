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

"""Tests for ``general.tools._references`` (feat-144-ref-artifact Phase 3, Task 3.1).

``find_references`` is pure string extraction (no fixture required);
``resolve_reference`` resolves against real, referenced artifacts created
in a temp ``SPECMGR_DOCS_DIR``/``SPECMGR_ADR_DIR``/``SPECMGR_FEAT_DIR``
(fixture convention mirrors ``tests/general/tools/test_delete.py``'s
``TempDeleteDirTestCase``: the env vars are read per call, so patching is
clean and isolated).
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from typing import Any, Callable

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.adr.tools.create_adr import create_adr
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.general.models.reference import ReferenceRow
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._references import REFERENCE_TYPES, find_references, resolve_reference
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.models.adr import AdrBody, AdrFrontmatter
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.uc.tools.create_uc import create_uc
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr

#: A canonical lowercase 8-4-4-4-12 hex UUID.
_UUID = "4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d"

#: A second, distinct canonical UUID.
_UUID2 = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"

#: A well-formed but non-existent canonical UUID (the unknown-id case).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

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

_REQ_TITLE = "Maximum Engine Temperature"

_GOL_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_GOL_TITLE = "Competitive Engines in Consumer Vehicles"

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

_SYSRS_MINIMAL_BODY = textwrap.dedent(
    """\
    # System Requirements Specification: Sample Document

    ## System Purpose

    Provision partner accounts.

    ## System Scope

    Onboarding only.

    ## Business Context and Goals

    ### Goals

    - GOL 0e15c5de-4ac9-4279-aa75-53249a3e43e4: A goal

    ## System Overview

    ### System Context

    Context.

    ### System Functions

    Functions.

    ## Requirements

    ### Functional Suitability

    - REQ a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734: A requirement
    """
)

_ADR_TITLE = "Use the dispatch convention"

#: Per flat target domain: (the lowercase reference tag, the domain's own
#: ``create_<d>`` tool, its minimal valid body, and that body's H1 title).
_TARGET_SEEDS: tuple[tuple[str, Callable[[str], Any], str, str], ...] = (
    ("gol", create_gol, _GOL_MINIMAL_BODY, _GOL_TITLE),
    ("prb", create_prb, _PRB_MINIMAL_BODY, "Simple Problem Statement"),
    ("qa", create_qa, _QA_MINIMAL_BODY, "Some QA Title"),
    ("uc", create_uc, _UC_MINIMAL_BODY, "Buy Goods"),
    ("req", create_req, _REQ_MINIMAL_BODY, _REQ_TITLE),
    ("rsk", create_rsk, _RSK_MINIMAL_BODY, "Sample Risk"),
    ("dec", create_dec, _DEC_MINIMAL_BODY, "Title of the Decision"),
    ("vcr", create_vcr, _VCR_MINIMAL_BODY, "Sample Verification Case"),
    ("sysrs", create_sysrs, _SYSRS_MINIMAL_BODY, "System Requirements Specification: Sample Document"),
)


class TestFindReferences(unittest.TestCase):
    """Tests for find_references (pure string extraction; no fixture)."""

    def test_each_vocabulary_tag_matches_a_well_formed_reference(self):
        """Every one of the 10 vocabulary tags must match '<TAG> <uuid>' and come back lowercased."""
        for tag in REFERENCE_TYPES:
            with self.subTest(tag=tag):
                text = f"{tag.upper()} {_UUID}: A title"

                result = find_references(text)

                self.assertEqual(result, [(tag, _UUID)])

    def test_tag_is_case_insensitive(self):
        """lowercase, CamelCase, and UPPERCASE tag spellings must all match."""
        for text in (f"req {_UUID}: A title", f"Req {_UUID}: A title", f"REQ {_UUID}: A title"):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), [("req", _UUID)])

    def test_separator_variants_all_match(self):
        """a single space, a dash, multiple spaces, and a tab must all separate tag from uuid."""
        for text in (
            f"GOL {_UUID}: A title",
            f"GOL-{_UUID}: A title",
            f"GOL  {_UUID}: A title",
            f"GOL\t{_UUID}: A title",
        ):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), [("gol", _UUID)])

    def test_a_reference_matches_anywhere_in_a_line(self):
        """column 0, after a bullet prefix, indented (a nested bullet), and mid-prose must all match."""
        for text, ref_type in (
            (f"REQ {_UUID}: A title", "req"),
            (f"- GOL {_UUID}: A title", "gol"),
            (f"  - SYSRS {_UUID}: A title", "sysrs"),
            (f"See also RSK {_UUID} for details.", "rsk"),
        ):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), [(ref_type, _UUID)])

    def test_a_reference_inside_code_fences_and_inline_code_spans_is_still_extracted(self):
        """Task 7.6 pins the accepted v1 tradeoff recorded in the plan's Design Notes caveat
        bullet and ``_references.py``'s module docstring: the extraction regex scans the raw
        frontmatter-stripped body text unconditionally -- including inside fenced code blocks
        and inline code spans -- so a reference-shaped line that merely quotes the
        <TAG> <uuid> syntax (rather than naming a live reference) is still extracted."""
        text = (
            f"```\nREQ {_UUID}: a literal example, not a live reference\n```\n\n"
            f"See the `GOL-{_UUID2}` tag for the inline variant."
        )

        result = find_references(text)

        self.assertEqual(result, [("req", _UUID), ("gol", _UUID2)])

    def test_tags_outside_the_vocabulary_do_not_match(self):
        """SOP/TSK/FEAT (and longer words containing a tag) must not match."""
        for text in (
            f"SOP {_UUID}: A title",
            f"TSK {_UUID}: A title",
            f"FEAT {_UUID}: A title",
            f"REQS {_UUID}: A title",
            f"MYREQ {_UUID}: A title",
        ):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), [])

    def test_a_non_hex_uuid_does_not_match(self):
        """a non-hex character in the tail and a dash-less hex run must not match."""
        for text in (
            "REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4g: A title",
            "REQ 4f2a1b3c8d5e4a919c721e6f8a2b3c4d: A title",
        ):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), [])

    def test_an_overlong_hex_tail_does_not_match(self):
        """one extra hex character after the 36-char uuid must be rejected by the trailing-hex guard."""
        self.assertEqual(find_references(f"REQ {_UUID}a: A title"), [])

    def test_a_feat_slug_id_does_not_match(self):
        """a feat-NNN-slug (not uuid-shaped) must not match, whatever tag precedes it."""
        for text in (
            "GOL feat-144-ref-artifact: A title",
            f"REQ-{_UUID}: A title\nGOL feat-36-delete: A title",
        ):
            with self.subTest(text=text):
                result = find_references(text)
                self.assertEqual([pair for pair in result if pair[0] == "gol"], [])

    def test_first_occurrence_order_is_preserved(self):
        """the pairs must come back in the order the references first occur in the text."""
        text = f"REQ {_UUID}: one\n\nGOL {_UUID2}: two\n\nRSK {_UUID}: three"

        result = find_references(text)

        self.assertEqual(result, [("req", _UUID), ("gol", _UUID2), ("rsk", _UUID)])

    def test_repeated_occurrences_are_not_deduped_at_this_level(self):
        """dedup is the tool's job -- the engine must report every occurrence."""
        text = f"REQ {_UUID}: one\n\nREQ {_UUID}: one again"

        result = find_references(text)

        self.assertEqual(result, [("req", _UUID), ("req", _UUID)])

    def test_text_without_references_yields_an_empty_list(self):
        self.assertEqual(find_references("No references at all in this prose."), [])


class TempRefDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via SPECMGR_DOCS_DIR, the ADR base dir via
    SPECMGR_ADR_DIR, and the feat base dir via SPECMGR_FEAT_DIR (the lifecycle is managed by
    ``enterContext``, per the sibling ``test_delete.py``/``test_set_status.py`` fixture convention)."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.adr_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {
                    DOCS_DIR_ENV_VAR: str(self.docs_root),
                    ADR_DIR_ENV_VAR: str(self.adr_dir),
                    FEAT_DIR_ENV_VAR: str(self.feat_dir),
                },
            )
        )

    def _flat_path(self, doc_type: str) -> Path:
        """The single on-disk document file seeded for the flat domain ``doc_type``."""
        matches = list((self.docs_root / doc_type).glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result


class TestResolveReference(TempRefDirTestCase):
    """Tests for resolve_reference (real referenced artifacts in temp base dirs)."""

    def test_resolved_rows_for_every_flat_target_domain(self):
        """For every flat target domain, the row must carry the referenced document's H1 and its
        resolved absolute path, with no error."""
        for ref_type, create_fn, minimal_body, title in _TARGET_SEEDS:
            with self.subTest(ref_type=ref_type):
                created = create_fn(minimal_body)

                row = resolve_reference(ref_type, created.id)

                self.assertIsInstance(row, ReferenceRow)
                self.assertEqual((row.type, row.id), (ref_type, created.id))
                self.assertEqual(row.title, title)
                self.assertEqual(row.path, str(self._flat_path(ref_type).resolve()))
                self.assertIsNone(row.error)
                path = Path(row.path)
                self.assertTrue(path.is_absolute())
                self.assertTrue(path.exists())

    def test_adr_target_row_uses_the_adr_h1(self):
        """The adr special case: the row's title is the referenced ADR's own H1 (doc.body.title)."""
        created_adr = create_adr(
            AdrFrontmatter(),
            AdrBody(
                title=_ADR_TITLE,
                context_and_problem_statement="Context.",
                considered_options="Options.",
                decision_outcome="Outcome.",
            ),
        )

        row = resolve_reference("adr", created_adr.frontmatter.id)

        self.assertEqual((row.type, row.id), ("adr", created_adr.frontmatter.id))
        self.assertEqual(row.title, _ADR_TITLE)
        expected_path = self.adr_dir / f"{created_adr.frontmatter.id}-use-the-dispatch-convention.md"
        self.assertEqual(row.path, str(expected_path.resolve()))
        self.assertIsNone(row.error)

    def test_not_found_rows_never_raise(self):
        """A target absent on disk must yield a row with null title/path and the domain's own
        not-found message in error -- for the flat, the adr, and a second flat domain."""
        for ref_type, error_fragment in (
            ("req", "no requirement found with id"),
            ("gol", "no goal found with id"),
            ("adr", "no ADR found with id"),
        ):
            with self.subTest(ref_type=ref_type):
                row = resolve_reference(ref_type, _MISSING_UUID)

                self.assertIsInstance(row, ReferenceRow)
                self.assertEqual((row.type, row.id), (ref_type, _MISSING_UUID))
                self.assertIsNone(row.title)
                self.assertIsNone(row.path)
                self.assertIsNotNone(row.error)
                self.assertIn(error_fragment, row.error)


if __name__ == "__main__":
    unittest.main()
