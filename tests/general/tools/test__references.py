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
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
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

#: A well-formed full feat-NNN-slug id (the FEAT tag's full id form, feat-177 REQ-001).
_FEAT_FULL_ID = "feat-177-list-ref-feat"

#: The bare feat-NNN number form of the same feature (the FEAT tag's bare id form, feat-177 REQ-001).
_FEAT_BARE_ID = "feat-177"

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


def _feat_body(title: str) -> str:
    """A valid, minimal feat body with the given ``# Feature: {title}`` H1 and no cross-references
    (the ``test_list_references`` ``_feat_body_with_references`` shape, minus the references)."""
    result = textwrap.dedent(
        f"""\
        # Feature: {title}

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
    return result


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
        """Every vocabulary tag except ``feat`` (whose id is never a UUID) must match '<TAG> <uuid>'
        and come back lowercased."""
        for tag in REFERENCE_TYPES:
            if tag == "feat":
                # feat's UUID form is deliberately not a feat reference (feat-177 ACC-003); the
                # separate FEAT-form loop is test_each_feat_form_matches_a_well_formed_reference.
                continue
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
        """SOP/TSK (and longer words containing a tag) must not match; the ``FEAT <uuid>`` case is
        not a tag outside the vocabulary -- FEAT is in it now -- but the uuid-form regression pin
        (a feat's id is never a UUID, feat-177 REQ-002/ACC-003)."""
        for text in (
            f"SOP {_UUID}: A title",
            f"TSK {_UUID}: A title",
            # FEAT is now a vocabulary tag (feat-177): this subtest is the uuid-form regression pin
            # -- a feat's id is never a UUID, so FEAT <uuid> matches nothing (REQ-002/ACC-003).
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

    def test_each_feat_form_matches_a_well_formed_reference(self):
        """Both of the FEAT tag's id forms -- the full feat-NNN-slug id and the bare feat-NNN number --
        must match and come back as they appeared (the separate FEAT-form loop of
        test_each_vocabulary_tag_matches_a_well_formed_reference, feat-177 REQ-001/ACC-003)."""
        for id_ in (_FEAT_FULL_ID, _FEAT_BARE_ID):
            with self.subTest(id_=id_):
                text = f"FEAT {id_}: A title"

                result = find_references(text)

                self.assertEqual(result, [("feat", id_)])

    def test_a_feat_tag_is_case_insensitive(self):
        """lowercase, CamelCase, and UPPERCASE FEAT tag spellings must all match, and a mixed-case id
        must come back lowercased -- for both id forms (feat-177 review round: pinning the id's own
        case-insensitivity, not just the tag's)."""
        for id_ in (_FEAT_FULL_ID, _FEAT_BARE_ID):
            for text in (f"feat {id_}: A title", f"Feat {id_}: A title", f"FEAT {id_}: A title"):
                with self.subTest(text=text):
                    self.assertEqual(find_references(text), [("feat", id_)])
        for text, expected in (
            ("FEAT Feat-177: A title", [("feat", _FEAT_BARE_ID)]),
            ("FEAT Feat-177-List-Ref-Feat: A title", [("feat", _FEAT_FULL_ID)]),
        ):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), expected)

    def test_a_feat_separator_variants_all_match(self):
        """a single space, a dash, multiple spaces, and a tab must all separate the FEAT tag from its
        id, for both id forms."""
        for id_ in (_FEAT_FULL_ID, _FEAT_BARE_ID):
            for text in (
                f"FEAT {id_}: A title",
                f"FEAT-{id_}: A title",
                f"FEAT  {id_}: A title",
                f"FEAT\t{id_}: A title",
            ):
                with self.subTest(text=text):
                    self.assertEqual(find_references(text), [("feat", id_)])

    def test_a_feat_reference_matches_anywhere_in_a_line(self):
        """column 0, after a bullet prefix, indented (a nested bullet), and mid-prose must all match,
        for both id forms."""
        for id_ in (_FEAT_FULL_ID, _FEAT_BARE_ID):
            for text in (
                f"FEAT {id_}: A title",
                f"- FEAT {id_}: A title",
                f"  - FEAT-{id_}: A title",
                f"See also FEAT {id_} for details.",
            ):
                with self.subTest(text=text):
                    self.assertEqual(find_references(text), [("feat", id_)])

    def test_a_feat_id_with_a_malformed_tail_does_not_match(self):
        """an overlong tail (feat-177x) and a dangling dash (feat-177-) must be rejected by the
        trailing guard, not extracted as the bare feat-177 (feat-177 REQ-001)."""
        for text in (
            "FEAT feat-177x: A title",
            "FEAT feat-177-: A title",
        ):
            with self.subTest(text=text):
                self.assertEqual(find_references(text), [])

    def test_feat_and_uuid_references_merge_in_first_occurrence_order(self):
        """the two patterns' match sets are merged by match position: a FEAT reference between (or
        before) UUID references must come back in its own position (feat-177 Task 100.100)."""
        for id_ in (_FEAT_FULL_ID, _FEAT_BARE_ID):
            for text, expected in (
                (
                    f"REQ {_UUID}: one\n\nFEAT {id_}: two\n\nGOL {_UUID2}: three",
                    [("req", _UUID), ("feat", id_), ("gol", _UUID2)],
                ),
                (
                    f"FEAT {id_}: first\n\nREQ {_UUID}: second",
                    [("feat", id_), ("req", _UUID)],
                ),
            ):
                with self.subTest(id_=id_, text=text):
                    result = find_references(text)
                    self.assertEqual(result, expected)

    def test_a_feat_slug_containing_a_uuid_tag_substring_keeps_both_rows(self):
        """feat-177 review round: the two patterns' match spans are not disjoint when a feat slug
        embeds a '<TAG>-<uuid>'-shaped substring (the hyphen doubling as the separator -- a FEAT
        match can never start inside a UUID span, since a uuid cannot contain 't', but a slug can
        contain one): the merge keeps BOTH spans -- the outer FEAT reference (its span starts
        first, so it sorts first) plus the inner, phantom UUID-tag row, which resolves like any
        other reference (typically a not-found row). Keep-both is the pinned v1 behavior -- no
        overlap handling."""
        text = f"FEAT feat-1-req-{_UUID}: A title"

        result = find_references(text)

        self.assertEqual(result, [("feat", f"feat-1-req-{_UUID}"), ("req", _UUID)])

    def test_dual_spellings_of_a_feat_reference_yield_two_pairs(self):
        """the same feature cited bare and full in one text yields two (type, id) pairs, in
        first-occurrence order -- no normalization at the extraction level (feat-177 REQ-007)."""
        text = f"FEAT {_FEAT_BARE_ID}: the bare spelling\n\nFEAT {_FEAT_FULL_ID}: the full spelling"

        result = find_references(text)

        self.assertEqual(result, [("feat", _FEAT_BARE_ID), ("feat", _FEAT_FULL_ID)])

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

    def test_a_feat_full_id_resolves_to_a_resolved_row(self):
        """feat-177 ACC-001 shape at the resolve level: the full feat-NNN-slug id resolves through
        the exact load_by_id -- the row carries the feature's H1 (the 'Feature: ' prefix stripped)
        and its README.md path, with no error."""
        created = create_feat(_feat_body("List Ref Feat"), id=_FEAT_FULL_ID)

        row = resolve_reference("feat", created.id)

        self.assertIsInstance(row, ReferenceRow)
        self.assertEqual((row.type, row.id), ("feat", _FEAT_FULL_ID))
        self.assertEqual(row.title, "List Ref Feat")
        self.assertEqual(row.path, str((self.feat_dir / _FEAT_FULL_ID / "README.md").resolve()))
        self.assertIsNone(row.error)

    def test_a_feat_bare_number_resolves_retaining_the_bare_id(self):
        """feat-177 ACC-002: a bare feat-NNN mention resolves to the matching feat-NNN-* feature,
        and the row's id stays the bare feat-NNN as it appeared in the source -- not the resolved
        full id."""
        create_feat(_feat_body("List Ref Feat"), id=_FEAT_FULL_ID)

        row = resolve_reference("feat", _FEAT_BARE_ID)

        self.assertEqual((row.type, row.id), ("feat", _FEAT_BARE_ID))
        self.assertEqual(row.title, "List Ref Feat")
        self.assertEqual(row.path, str((self.feat_dir / _FEAT_FULL_ID / "README.md").resolve()))
        self.assertIsNone(row.error)

    def test_a_bare_feat_number_resolves_the_first_folder_in_sorted_order(self):
        """feat-177 ACC-005: a bare number matching multiple feature folders resolves the first one
        in lexicographically sorted folder-name order (the list_feat order)."""
        create_feat(_feat_body("Beta Feature"), id="feat-1-beta")
        create_feat(_feat_body("Alpha Feature"), id="feat-1-alpha")

        row = resolve_reference("feat", "feat-1")

        self.assertEqual((row.type, row.id), ("feat", "feat-1"))
        self.assertEqual(row.title, "Alpha Feature")
        self.assertEqual(row.path, str((self.feat_dir / "feat-1-alpha" / "README.md").resolve()))
        self.assertIsNone(row.error)

    def test_a_readme_less_feat_folder_is_not_a_bare_number_candidate(self):
        """feat-177 ACC-005: the bare-number candidate set is the iter_feat_paths view
        (README-backed folders only) -- a feat-NNN-* folder without a README.md is not a candidate
        and cannot shadow a later, valid match, even when it sorts first."""
        create_feat(_feat_body("Zeta Feature"), id="feat-3-zeta")
        no_readme = self.feat_dir / "feat-3-noreadme"
        no_readme.mkdir()
        (no_readme / "NOTES.txt").write_text("a non-README file", encoding="utf-8")

        row = resolve_reference("feat", "feat-3")

        self.assertEqual((row.type, row.id), ("feat", "feat-3"))
        self.assertEqual(row.title, "Zeta Feature")
        self.assertEqual(row.path, str((self.feat_dir / "feat-3-zeta" / "README.md").resolve()))
        self.assertIsNone(row.error)

    def test_a_bare_feat_number_never_matches_a_longer_number(self):
        """feat-177 REQ-003: the bare-number prefix carries its trailing hyphen, so feat-1 never
        matches feat-10-* -- with only a feat-10-* folder on disk, a bare feat-1 is a not-found
        row (while a bare feat-10 still resolves the feat-10-* folder)."""
        created = create_feat(_feat_body("Ten Feature"), id="feat-10-multi")

        row = resolve_reference("feat", "feat-1")

        self.assertEqual((row.type, row.id), ("feat", "feat-1"))
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("no feature found for bare number 'feat-1'", row.error)

        row = resolve_reference("feat", "feat-10")

        self.assertEqual((row.type, row.id), ("feat", "feat-10"))
        self.assertEqual(row.title, "Ten Feature")
        self.assertEqual(row.path, str((self.feat_dir / created.id / "README.md").resolve()))
        self.assertIsNone(row.error)

    def test_a_broken_first_match_feat_readme_is_a_not_found_row(self):
        """feat-177 REQ-003: if the first (sorted) name match's README fails to parse, the resolver
        does not skip on to the next match -- the collapsed FeatNotFoundError yields a not-found
        row (written directly to the temp dir, since create_feat validates its input)."""
        create_feat(_feat_body("Good Feature"), id="feat-1-good")
        broken = self.feat_dir / "feat-1-broken"
        broken.mkdir()
        (broken / "README.md").write_text("# Feature: Broken\n\nnot a valid feature body", encoding="utf-8")

        row = resolve_reference("feat", "feat-1")

        self.assertEqual((row.type, row.id), ("feat", "feat-1"))
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("feat-1-broken", row.error)
        self.assertIn("could not be parsed", row.error)

    def test_a_feat_folder_with_a_mismatching_frontmatter_id_is_a_not_found_row(self):
        """feat-177 (optional review follow-up): a feature folder that parses but whose frontmatter
        id mismatches its folder name is a not-found row via load_by_id's own mismatch guard
        (feat/tools/_paths.py) -- never raises; written directly by mutating the created document's
        frontmatter id, since create_feat enforces id == folder name."""
        create_feat(_feat_body("Mismatch Feature"), id="feat-5-mismatch")
        readme = self.feat_dir / "feat-5-mismatch" / "README.md"
        text = readme.read_text(encoding="utf-8")
        self.assertEqual(text.count("id: feat-5-mismatch"), 1)
        readme.write_text(text.replace("id: feat-5-mismatch", "id: feat-9-other"), encoding="utf-8")

        row = resolve_reference("feat", "feat-5-mismatch")

        self.assertIsInstance(row, ReferenceRow)
        self.assertEqual((row.type, row.id), ("feat", "feat-5-mismatch"))
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("does not match the containing folder's own name", row.error)
        self.assertIn("feat-5-mismatch", row.error)
        self.assertIn("feat-9-other", row.error)

    def test_a_missing_feat_full_id_is_a_not_found_row(self):
        """feat-177 ACC-004 (full id): a full-id mention of an absent feature is a row with null
        title/path and the domain's own not-found message in error -- never raises."""
        row = resolve_reference("feat", "feat-999-no-such-feature")

        self.assertIsInstance(row, ReferenceRow)
        self.assertEqual((row.type, row.id), ("feat", "feat-999-no-such-feature"))
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("no feature found with id 'feat-999-no-such-feature'", row.error)

    def test_a_missing_bare_feat_number_is_a_not_found_row(self):
        """feat-177 ACC-004 (bare number): a bare-number mention with no matching folder is a row
        with null title/path and the bare-number not-found message in error -- never raises."""
        row = resolve_reference("feat", "feat-42")

        self.assertIsInstance(row, ReferenceRow)
        self.assertEqual((row.type, row.id), ("feat", "feat-42"))
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("no feature found for bare number 'feat-42'", row.error)

    def test_a_uuid_shaped_feat_id_is_a_not_found_row(self):
        """feat-177 REQ-003: a feat's id is never a UUID -- a UUID-shaped feat ref falls through to
        the exact load_by_id and yields a not-found row."""
        row = resolve_reference("feat", _UUID)

        self.assertEqual((row.type, row.id), ("feat", _UUID))
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("no feature found with id", row.error)
        self.assertIn(_UUID, row.error)


if __name__ == "__main__":
    unittest.main()
