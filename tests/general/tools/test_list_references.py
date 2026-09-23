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

"""Tests for the generic ``list_references`` ``@mcp.tool()`` wrapper (feat-144-ref-artifact Phase 3).

Seeds real, referenced artifacts per test -- every flat target domain via
the domain's own ``create_<d>`` tool in a temp ``SPECMGR_DOCS_DIR``, ``feat``
via its own ``create_feat`` in a temp ``SPECMGR_FEAT_DIR``, ``adr`` via
``create_adr`` in a temp ``SPECMGR_ADR_DIR`` (mirroring the fixture strategy
of ``tests/general/tools/test_delete.py``) -- and covers: the resolved-row
contract (ACC-001), the empty-list case (ACC-002), the never-raising
not-found row (ACC-003), first-occurrence deduplication (ACC-004), the
path-safety guards (ACC-005), the source-missing raise (ACC-006), the
``list_*`` paging contract (ACC-009), the source-domain spread (a
``feat-NNN-slug``-id ``feat`` source and a UUID-id ``adr`` source), and a
live-``mcp`` registration smoke test (mirroring ``test_delete.py``'s).
"""

from __future__ import annotations

import asyncio
import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError
from biz.dfch.specmgr.adr.tools.create_adr import create_adr
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.general.models.paged_result import PagedResult
from biz.dfch.specmgr.general.models.reference import ReferenceRow
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.list_references import list_references
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.models.adr import AdrBody, AdrFrontmatter
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.sysrs.tools._paths import SysrsNotFoundError
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError

#: A well-formed but non-existent canonical UUID (the unknown-id case for every UUID domain).
_MISSING_UUID = "00000000-0000-0000-0000-000000000000"

#: A well-formed but non-existent feat-NNN-slug (the unknown-id case for feat).
_MISSING_FEAT_ID = "feat-999-no-such-feature"

#: A well-formed feat-NNN-slug folder name (the wrong-format id for every UUID domain).
_FEAT_SLUG_ID = "feat-144-ref-artifact"

#: A well-formed canonical UUID (the wrong-format id for ``feat``).
_VALID_UUID = "0d8f4c2a-1b3e-4f5a-9c7d-2e6b8a0f1c3d"

#: The pinned path-injection shapes (ACC-005).
_TRAVERSAL_IDS = ("../etc/passwd", "a/b", "a\\b", "..")

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

_REQ_SECOND_BODY = textwrap.dedent(
    """\
    # Second Engine Requirement

    WHILE the engine is running, THE second requirement holds.

    ## Description

    If the engine becomes too loud, the lifetime of the system decreases.

    ## Characteristics

    1. Reliability

    ## Level

    SHOULD

    ## Source

    The sample interview.
    """
)

_REQ_SECOND_TITLE = "Second Engine Requirement"

_GOL_MINIMAL_BODY = textwrap.dedent(
    """\
    # Competitive Engines in Consumer Vehicles

    THE company shall provide engines that are competitive in power output and fuel consumption.

    ## Source

    The vehicle program's 2027 market analysis
    """
)

_GOL_TITLE = "Competitive Engines in Consumer Vehicles"

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

_RSK_TITLE = "Sample Risk"


def _sysrs_body(gol_id: str, rsk_id: str, req_id: str) -> str:
    """A valid SYSRS body whose ``### Goals``/``## Risks``/``## Requirements`` bullets reference
    the given goal/risk/requirement ids (the canonical source shape for ACC-001)."""
    result = textwrap.dedent(
        f"""\
        # System Requirements Specification: Sample Document

        ## System Purpose

        Provision partner accounts.

        ## System Scope

        Onboarding only.

        ## Business Context and Goals

        ### Goals

        - GOL {gol_id}: A goal

        ## Risks

        - RSK {rsk_id}: A risk

        ## System Overview

        ### System Context

        Context.

        ### System Functions

        Functions.

        ## Requirements

        ### Functional Suitability

        - REQ {req_id}: A requirement
        """
    )
    return result


def _req_body_with_missing_gol_reference() -> str:
    """A valid REQ body whose free-form ``## Description`` references a goal that does not exist."""
    result = textwrap.dedent(
        f"""\
        # Sample Requirement

        WHILE the system is idle, THE sample requirement holds.

        ## Description

        See also GOL {_MISSING_UUID}: A goal that does not exist.

        ## Characteristics

        1. Safety

        ## Level

        MUST

        ## Source

        The sample interview.
        """
    )
    return result


def _req_body_with_gol_reference_twice(gol_id: str) -> str:
    """A valid REQ body whose ``## Description`` and ``## More Information`` both reference the same goal (ACC-004)."""
    reference_line = f"GOL {gol_id}: A goal"
    result = textwrap.dedent(
        f"""\
        # Sample Requirement

        WHILE the system is idle, THE sample requirement holds.

        ## Description

        {reference_line}

        ## Characteristics

        1. Safety

        ## Level

        MUST

        ## Source

        The sample interview.

        ## More Information

        {reference_line}
        """
    )
    return result


def _req_body_with_30_references(first_id: str, second_id: str, missing_ids: list[str]) -> str:
    """A valid REQ body whose free-form ``## Description`` carries 30 unique references: the two
    seeded (existing) requirements first, then the 28 missing ones (ACC-009)."""
    description_lines = [
        f"REQ {first_id}: First seeded requirement",
        f"REQ {second_id}: Second seeded requirement",
        *(f"REQ {missing_id}: A missing requirement" for missing_id in missing_ids),
    ]
    lines = [
        "# Sample Requirement",
        "",
        "WHILE the system is idle, THE sample requirement holds.",
        "",
        "## Description",
        "",
    ]
    for line in description_lines:
        lines.append(line)
        lines.append("")
    lines += [
        "## Characteristics",
        "",
        "1. Safety",
        "",
        "## Level",
        "",
        "MUST",
        "",
        "## Source",
        "",
        "The sample interview.",
    ]
    result = "\n".join(lines)
    return result


def _feat_body_with_references(req_id: str, gol_id: str) -> str:
    """A valid feat body (the ``_FEAT_MINIMAL_BODY`` shape) whose free-form ``### Overview`` prose
    references one requirement and one goal (the source-domain-spread ``feat`` case)."""
    result = textwrap.dedent(
        f"""\
        # Feature: Example Widget

        ## Plan

        ### Overview

        Short description.

        REQ {req_id}: A requirement.

        GOL {gol_id}: A goal.

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
    return result


def _adr_body_with_reference(req_id: str) -> AdrBody:
    """A minimal valid ADR body whose optional ``## More Information`` references one requirement
    (the source-domain-spread ``adr`` case)."""
    result = AdrBody(
        title="Use the dispatch convention",
        context_and_problem_statement="Context.",
        considered_options="Options.",
        decision_outcome="Outcome.",
        more_information=f"REQ {req_id}: A requirement this decision depends on.",
    )
    return result


class TempListReferencesDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via SPECMGR_DOCS_DIR, the feat base dir via
    SPECMGR_FEAT_DIR, and the ADR base dir via SPECMGR_ADR_DIR (the lifecycle is managed by
    ``enterContext``, per the sibling ``test_delete.py``/``test_set_status.py`` fixture convention).
    The env vars are read per call, so patching is clean and isolated."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.adr_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
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

    def _flat_path(self, doc_type: str) -> Path:
        """The single on-disk document file seeded for the flat domain ``doc_type``."""
        matches = list((self.docs_root / doc_type).glob("*.md"))
        self.assertEqual(len(matches), 1)
        result = matches[0]
        return result


class TestListReferencesResolved(TempListReferencesDirTestCase):
    """ACC-001: a SYSRS source referencing REQ/GOL/RSK artifacts returns one resolved row per
    unique reference, in first-occurrence order."""

    def test_sysrs_source_returns_one_row_per_resolved_reference(self) -> None:
        """Each row must carry the correct type/id, the referenced document's H1, and its resolved
        absolute on-disk path -- with no error."""
        created_gol = create_gol(_GOL_MINIMAL_BODY)
        created_rsk = create_rsk(_RSK_MINIMAL_BODY)
        created_req = create_req(_REQ_MINIMAL_BODY)

        created_sysrs = create_sysrs(_sysrs_body(created_gol.id, created_rsk.id, created_req.id))

        result: PagedResult[ReferenceRow] = list_references(type="sysrs", id=created_sysrs.id)

        self.assertEqual(result.total, 3)
        self.assertFalse(result.truncated)
        self.assertEqual(result.offset, 0)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(len(result.results), 3)

        expected = (
            ("gol", created_gol.id, _GOL_TITLE),
            ("rsk", created_rsk.id, _RSK_TITLE),
            ("req", created_req.id, _REQ_TITLE),
        )
        for row, (ref_type, ref_id, title) in zip(result.results, expected, strict=True):
            with self.subTest(ref_type=ref_type):
                self.assertIsInstance(row, ReferenceRow)
                self.assertEqual(row.type, ref_type)
                self.assertEqual(row.id, ref_id)
                self.assertEqual(row.title, title)
                self.assertIsNone(row.error)
                path = Path(row.path)
                self.assertTrue(path.is_absolute())
                self.assertTrue(path.exists())
                self.assertEqual(path, self._flat_path(ref_type).resolve())


class TestListReferencesEmpty(TempListReferencesDirTestCase):
    """ACC-002: a source with no cross-references returns an empty page, not an error."""

    def test_a_source_without_references_returns_an_empty_page(self) -> None:
        created = create_req(_REQ_MINIMAL_BODY)

        result = list_references(type="req", id=created.id)

        self.assertEqual(result.results, [])
        self.assertEqual(result.total, 0)
        self.assertFalse(result.truncated)
        self.assertEqual(result.error_count, 0)


class TestListReferencesNotFound(TempListReferencesDirTestCase):
    """ACC-003: a reference to a uuid that does not exist on disk is a row with null title/path and
    the target domain's not-found message in error -- the call does not raise."""

    def test_a_not_found_reference_is_a_row_with_error_and_never_raises(self) -> None:
        created = create_req(_req_body_with_missing_gol_reference())

        result = list_references(type="req", id=created.id)

        self.assertEqual(result.total, 1)
        self.assertFalse(result.truncated)
        self.assertEqual(result.error_count, 1)
        self.assertEqual(len(result.results), 1)

        row = result.results[0]
        self.assertEqual(row.type, "gol")
        self.assertEqual(row.id, _MISSING_UUID)
        self.assertIsNone(row.title)
        self.assertIsNone(row.path)
        self.assertIsNotNone(row.error)
        self.assertIn("no goal found with id", row.error)


class TestListReferencesDeduplication(TempListReferencesDirTestCase):
    """ACC-004: repeated occurrences of the same (type, id) reference yield exactly one row."""

    def test_repeated_references_deduplicate_to_a_single_row(self) -> None:
        created_gol = create_gol(_GOL_MINIMAL_BODY)
        created = create_req(_req_body_with_gol_reference_twice(created_gol.id))

        result = list_references(type="req", id=created.id)

        self.assertEqual(result.total, 1)
        self.assertEqual(result.error_count, 0)
        self.assertEqual(len(result.results), 1)

        row = result.results[0]
        self.assertEqual(row.type, "gol")
        self.assertEqual(row.id, created_gol.id)
        self.assertEqual(row.title, _GOL_TITLE)
        self.assertIsNone(row.error)


class TestListReferencesPathSafety(unittest.TestCase):
    """ACC-005: an invalid source type/id raises ValueError before any filesystem access -- the docs
    root is a path that does not exist, so a source lookup that ever reached the filesystem would
    surface as the domain's own LookupError (not-found), not a ValueError."""

    def setUp(self) -> None:
        self.missing_docs_root = Path(self.enterContext(tempfile.TemporaryDirectory())) / "does-not-exist"
        self.enterContext(
            mock.patch.dict(
                "os.environ",
                {
                    DOCS_DIR_ENV_VAR: str(self.missing_docs_root),
                    FEAT_DIR_ENV_VAR: str(self.missing_docs_root / "feat"),
                    ADR_DIR_ENV_VAR: str(self.missing_docs_root / "adr"),
                },
            )
        )

    def test_an_invalid_source_type_raises_value_error_before_any_filesystem_access(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            list_references(type="bogus", id=_VALID_UUID)

        self.assertIn("bogus", str(ctx.exception))

    def test_wrong_format_source_ids_raise_value_error_for_uuid_domains(self) -> None:
        """A feat-NNN-slug (and every pinned traversal shape, and the empty string) must raise
        ValueError for every UUID source domain."""
        for doc_type in ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs", "adr"):
            for bad_id in (*_TRAVERSAL_IDS, _FEAT_SLUG_ID, ""):
                with self.subTest(doc_type=doc_type, bad_id=bad_id):
                    with self.assertRaises(ValueError):
                        list_references(type=doc_type, id=bad_id)

    def test_wrong_format_source_ids_raise_value_error_for_feat(self) -> None:
        """A UUID (and every pinned traversal shape, and the empty string) must raise ValueError
        for the feat source domain."""
        for bad_id in (*_TRAVERSAL_IDS, _VALID_UUID, ""):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(ValueError):
                    list_references(type="feat", id=bad_id)


class TestListReferencesSourceMissing(TempListReferencesDirTestCase):
    """ACC-006: a validly-shaped source id with no file on disk raises the source domain's own
    XNotFoundError, identical to get_<d>."""

    def test_a_well_formed_but_missing_source_id_raises_the_domain_not_found_error(self) -> None:
        cases: list[tuple[str, str, type[Exception]]] = [
            ("req", _MISSING_UUID, ReqNotFoundError),
            ("uc", _MISSING_UUID, UcNotFoundError),
            ("sysrs", _MISSING_UUID, SysrsNotFoundError),
            ("gol", _MISSING_UUID, GolNotFoundError),
            ("rsk", _MISSING_UUID, RskNotFoundError),
            ("feat", _MISSING_FEAT_ID, FeatNotFoundError),
            ("adr", _MISSING_UUID, AdrNotFoundError),
        ]
        for doc_type, missing_id, error_type in cases:
            with self.subTest(doc_type=doc_type):
                with self.assertRaises(error_type) as ctx:
                    list_references(type=doc_type, id=missing_id)

                self.assertIsInstance(ctx.exception, LookupError)
                self.assertIn(missing_id, str(ctx.exception))


class TestListReferencesPaging(TempListReferencesDirTestCase):
    """ACC-009: a source with more than 25 unique references pages like every list_* tool."""

    def _seed_30_reference_source(self) -> tuple[Any, str, str, list[str]]:
        """Create the source REQ body's two seeded targets and the source itself; return the
        source's frontmatter, the two seeded target ids, and the 28 missing reference ids
        (in body order)."""
        created_first = create_req(_REQ_MINIMAL_BODY)
        created_second = create_req(_REQ_SECOND_BODY)
        missing_ids = [f"{index:08x}-0000-0000-0000-{index:012x}" for index in range(1, 29)]
        created_source = create_req(_req_body_with_30_references(created_first.id, created_second.id, missing_ids))
        result: tuple[Any, str, str, list[str]] = (created_source, created_first.id, created_second.id, missing_ids)
        return result

    def test_default_page_of_a_30_reference_source(self) -> None:
        """total/error_count must be correct and the page must hold the first 25 of 30 rows,
        truncated, with the two seeded references resolved and the rest not-found."""
        created_source, first_id, second_id, missing_ids = self._seed_30_reference_source()

        first_page = list_references(type="req", id=created_source.id)

        self.assertEqual(first_page.total, 30)
        self.assertTrue(first_page.truncated)
        self.assertEqual(len(first_page.results), 25)
        self.assertEqual(first_page.offset, 0)
        self.assertEqual(first_page.max_results, 25)
        self.assertEqual(first_page.error_count, 28)

        # The two seeded targets resolve (first-occurrence order: body order); the rest do not.
        self.assertEqual(first_page.results[0].id, first_id)
        self.assertEqual(first_page.results[0].title, _REQ_TITLE)
        self.assertIsNone(first_page.results[0].error)
        self.assertEqual(first_page.results[1].id, second_id)
        self.assertEqual(first_page.results[1].title, _REQ_SECOND_TITLE)
        self.assertIsNone(first_page.results[1].error)
        for row in first_page.results[2:]:
            with self.subTest(ref_id=row.id):
                self.assertIn(row.id, missing_ids)
                self.assertIsNone(row.title)
                self.assertIsNone(row.path)
                self.assertIsNotNone(row.error)
                self.assertIn("no requirement found with id", row.error)

    def test_second_page_starts_where_the_first_ended(self) -> None:
        created_source, _first_id, _second_id, missing_ids = self._seed_30_reference_source()

        first_page = list_references(type="req", id=created_source.id)
        second_page = list_references(type="req", id=created_source.id, offset=25)

        self.assertEqual(second_page.total, 30)
        self.assertFalse(second_page.truncated)
        self.assertEqual(len(second_page.results), 5)
        self.assertEqual(second_page.offset, 25)
        self.assertEqual(second_page.error_count, 28)

        # The window advanced exactly where the first page ended: no overlap, and the five ids
        # are the last five references in body order.
        first_ids = [row.id for row in first_page.results]
        second_ids = [row.id for row in second_page.results]
        self.assertEqual(len(set(first_ids) & set(second_ids)), 0)
        self.assertEqual(second_ids, missing_ids[23:28])

    def test_max_results_clamps_to_the_1_100_range(self) -> None:
        created_source, _first_id, _second_id, _missing_ids = self._seed_30_reference_source()

        clamped_high = list_references(type="req", id=created_source.id, max_results=500)

        self.assertEqual(clamped_high.max_results, 100)
        self.assertEqual(len(clamped_high.results), 30)
        self.assertFalse(clamped_high.truncated)

        clamped_low = list_references(type="req", id=created_source.id, max_results=0)

        self.assertEqual(clamped_low.max_results, 1)
        self.assertEqual(len(clamped_low.results), 1)
        self.assertTrue(clamped_low.truncated)

    def test_a_negative_offset_floors_to_zero(self) -> None:
        created_source, _first_id, _second_id, _missing_ids = self._seed_30_reference_source()

        result = list_references(type="req", id=created_source.id, offset=-5)

        self.assertEqual(result.offset, 0)
        self.assertEqual(len(result.results), 25)
        self.assertTrue(result.truncated)

    def test_an_offset_past_the_end_returns_an_empty_page(self) -> None:
        created_source, _first_id, _second_id, _missing_ids = self._seed_30_reference_source()

        result = list_references(type="req", id=created_source.id, offset=30)

        self.assertEqual(result.results, [])
        self.assertFalse(result.truncated)
        self.assertEqual(result.total, 30)
        self.assertEqual(result.error_count, 28)


class TestListReferencesSourceDomainSpread(TempListReferencesDirTestCase):
    """The source may be any whole-body domain plus adr: a feat-NNN-slug-id ``feat`` source and a
    UUID-id ``adr`` source (in addition to the UUID-domain sources above)."""

    def test_a_feat_source_with_a_feat_slug_id(self) -> None:
        created_gol = create_gol(_GOL_MINIMAL_BODY)
        created_req = create_req(_REQ_MINIMAL_BODY)

        created_feat = create_feat(_feat_body_with_references(created_req.id, created_gol.id), id="feat-144-ref-spread")

        result = list_references(type="feat", id=created_feat.id)

        self.assertEqual(result.total, 2)
        self.assertFalse(result.truncated)
        self.assertEqual(result.error_count, 0)
        self.assertEqual((result.results[0].type, result.results[0].id), ("req", created_req.id))
        self.assertEqual(result.results[0].title, _REQ_TITLE)
        self.assertIsNone(result.results[0].error)
        self.assertEqual((result.results[1].type, result.results[1].id), ("gol", created_gol.id))
        self.assertEqual(result.results[1].title, _GOL_TITLE)
        self.assertIsNone(result.results[1].error)

    def test_an_adr_source_with_a_uuid_id(self) -> None:
        created_req = create_req(_REQ_MINIMAL_BODY)

        created_adr = create_adr(AdrFrontmatter(), _adr_body_with_reference(created_req.id))

        result = list_references(type="adr", id=created_adr.frontmatter.id)

        self.assertEqual(result.total, 1)
        self.assertFalse(result.truncated)
        self.assertEqual(result.error_count, 0)
        row = result.results[0]
        self.assertEqual((row.type, row.id), ("req", created_req.id))
        self.assertEqual(row.title, _REQ_TITLE)
        self.assertIsNone(row.error)
        path = Path(row.path)
        self.assertTrue(path.is_absolute())
        self.assertTrue(path.exists())


class TestListReferencesRegistration(unittest.TestCase):
    """The live ``mcp`` registration carries ``list_references`` with the full ``type`` enum and
    required ``id``/``type``."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_list_references_registered_with_13_value_type_enum(self) -> None:
        """``list_references`` must be registered exactly once, with the full ``type`` enum (every
        whole-body domain plus ``adr``) and required ``id``/``type``."""
        matching = [t for t in self._tools if t.name == "list_references"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(
            type_prop["enum"],
            ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "sysrs", "adr"],
        )
        self.assertEqual(type_prop["type"], "string")
        self.assertEqual(schema["properties"]["id"]["type"], "string")
        self.assertEqual(set(schema["required"]), {"id", "type"})


if __name__ == "__main__":
    unittest.main()
