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

"""Tests for the ``get_reference_diagram`` MCP tool (feat-207-reference-graph, Phase 120, Task 120.150,
ACC-003).

The tool's own contract over the Phase 110 library: the guard order of
Design Notes §7 (``validate_id`` + the ``depth`` 1..5 range check, BOTH a
``ValueError`` before any filesystem access -- pinned with the
``list_references`` tests' missing-docs-root idiom, so a lookup that ever
reached the filesystem would surface as the domain's own ``LookupError``,
not a ``ValueError``), the source load's error mapping (a missing source
raises the source domain's own ``XNotFoundError`` for every one of the 13
domains; an existing-but-broken source returns the non-raising
``ParseFailureResult`` -- its ``error`` text byte-identical to the domain's
``list_<d>`` failed-row ``error`` for the same file, ADR 9080b37c), the
byte-stable return over the Phase 110 seeded registries (the env var
UNSET in the test process, guarded by the shared
``_SeededRegistryTestCase`` base, so ``max_label`` is the frozen default
40 -- the output equals the committed golden), the ``title`` override
(sanitized but never truncated), and the ``SPECMGR_DIAGRAM_MAX_TITLE`` env
var's effect on the tool's own return (truncation at a custom value,
fallback to 40 on a set-but-invalid value). Every success return is
additionally asserted checker-clean in both structure modes with zero
findings (the full path end-to-end: tool → ``str`` → ``check_structure``).

The registry-wide sibling tool's tests live in
``test_get_reference_diagram_all.py``; the two tools' registration is
pinned here (one class, both names).
"""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR, FeatNotFoundError
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.models.reference_graph import render_reference_graph
from biz.dfch.specmgr.general.tools._diagram_config import ENV_VAR_DIAGRAM_MAX_TITLE
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._domains import ALL_DOMAINS
from biz.dfch.specmgr.general.tools._reference_graph import build_source_graph
from biz.dfch.specmgr.general.tools.get_reference_diagram import get_reference_diagram
from biz.dfch.specmgr.plantuml.structure import MODE_PREFLIGHT, MODE_STANDALONE, check_structure
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
from biz.dfch.specmgr.sop.tools._paths import SopNotFoundError
from biz.dfch.specmgr.sysrs.tools._paths import SysrsNotFoundError
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError

from ._reference_graph_helpers import (
    _MISSING_UUID,
    _SeededRegistryTestCase,
    _A001,
    _B001,
    _C001,
    _C002,
    _D001,
    _D002,
    _G001,
    _H001,
    _K001,
    _N001,
    _R001,
    _U001,
    _W001,
    _WG001,
)

#: The pinned traversal/malformed id shapes (the ``list_references`` path-safety tests' own set).
_TRAVERSAL_IDS = ("../escape", "a/b", "a\\b", "")
_FEAT_SLUG_ID = "feat-36-delete"
_BARE_FEAT_ID = "feat-42"

#: The full ``feat-NNN-slug`` of the seeded reverse-fixture feature.
_SEEDED_FEAT_ID = "feat-42-reverse-feat"


def _checker_clean(text: str) -> None:
    """Assert ``text`` passes the structure checker in BOTH modes with zero findings (errors and warnings)."""
    for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
        result = check_structure(text, mode)
        assert result.errors == [], (mode, result.errors)
        assert result.warnings == [], (mode, result.warnings)


class TestGetReferenceDiagramRegistration(unittest.TestCase):
    """Both Phase 120 tools are registered exactly once, with the frozen signatures' schemas."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_get_reference_diagram_registered_with_13_value_type_enum(self) -> None:
        """``type`` is the full 13-domain vocabulary (adr included), ``type``/``id`` required, the
        remaining parameters optional with the frozen defaults."""
        matching = [t for t in self._tools if t.name == "get_reference_diagram"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(type_prop["enum"], list(ALL_DOMAINS))
        self.assertEqual(type_prop["type"], "string")
        self.assertEqual(schema["properties"]["id"]["type"], "string")
        self.assertEqual(set(schema["required"]), {"id", "type"})
        self.assertEqual(schema["properties"]["depth"].get("default"), 1)
        self.assertEqual(schema["properties"]["depth"]["type"], "integer")
        self.assertEqual(schema["properties"]["reverse"].get("default"), False)
        self.assertEqual(schema["properties"]["include_feat"].get("default"), True)
        self.assertNotIn("title", schema["required"])

    def test_get_reference_diagram_all_registered_with_no_required_parameters(self) -> None:
        """No id guards: neither parameter is required, the defaults are frozen."""
        matching = [t for t in self._tools if t.name == "get_reference_diagram_all"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        self.assertEqual(schema.get("required", []), [])
        self.assertEqual(schema["properties"]["include_feat"].get("default"), True)
        self.assertNotIn("title", schema.get("required", []))


class TestGetReferenceDiagramPathSafety(unittest.TestCase):
    """ACC-003: a malformed ``type``/``id``/``depth`` raises ``ValueError`` before any filesystem
    access -- the docs root is a path that does not exist, so a source lookup that ever reached the
    filesystem would surface as the domain's own ``LookupError`` (not-found), not a ``ValueError``."""

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
            get_reference_diagram(type="bogus", id=_MISSING_UUID)

        self.assertIn("bogus", str(ctx.exception))

    def test_wrong_format_source_ids_raise_value_error_for_uuid_domains(self) -> None:
        """A feat-NNN-slug (and every pinned traversal shape, and the empty string) must raise
        ``ValueError`` for every UUID source domain -- the docs root does not exist, so a lookup
        that reached the filesystem would have raised the domain's ``LookupError`` instead."""
        for doc_type in ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs", "adr"):
            for bad_id in (*_TRAVERSAL_IDS, _FEAT_SLUG_ID, _BARE_FEAT_ID):
                with self.subTest(doc_type=doc_type, bad_id=bad_id):
                    with self.assertRaises(ValueError):
                        get_reference_diagram(type=doc_type, id=bad_id)

    def test_wrong_format_source_ids_raise_value_error_for_feat(self) -> None:
        """A UUID (and every pinned traversal shape, and the empty string) must raise ``ValueError``
        for the feat source domain -- and a BARE ``feat-NNN`` is a wrong-format id, not a
        normalization candidate (the ``get_feat``/``list_references`` parity; the rulebook and the
        tool docstring point at ``list_feat`` to discover the exact ``feat-NNN-slug`` id)."""
        for bad_id in (*_TRAVERSAL_IDS, _MISSING_UUID, _BARE_FEAT_ID):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(ValueError):
                    get_reference_diagram(type="feat", id=bad_id)

    def test_depth_out_of_range_or_non_int_raises_value_error_before_any_filesystem_access(self) -> None:
        """``depth`` 0, 6, and non-int (including a ``bool``) raise ``ValueError`` with a valid
        ``type``/``id`` -- the docs root does not exist, so a build that reached the filesystem
        would have raised the domain's ``LookupError`` instead."""
        for bad_depth in (0, 6, "3", 2.0, True):
            with self.subTest(bad_depth=bad_depth):
                with self.assertRaises(ValueError) as ctx:
                    get_reference_diagram(type="req", id=_MISSING_UUID, depth=bad_depth)
                self.assertIn("depth", str(ctx.exception))

    def test_a_malformed_id_and_an_out_of_range_depth_still_raise_value_error(self) -> None:
        """Both guards are pure pre-filesystem input validation: the combination raises too
        (whichever guard fires first), never a filesystem-shaped error."""
        for doc_type, bad_id in (("req", "../escape"), ("feat", _BARE_FEAT_ID)):
            with self.subTest(doc_type=doc_type, bad_id=bad_id):
                with self.assertRaises(ValueError):
                    get_reference_diagram(type=doc_type, id=bad_id, depth=9)


class TestGetReferenceDiagramSourceMissing(_SeededRegistryTestCase):
    """ACC-003: a validly-shaped source id with no file on disk raises the source domain's own
    ``XNotFoundError``, identical to ``get_<d>``/``list_references`` -- for every one of the 13
    domains."""

    SEEDS = (("cycle/req-c001.md", f"docs/req/{_C001}.md"),)

    def test_a_well_formed_but_missing_source_id_raises_the_domain_not_found_error(self) -> None:
        cases: list[tuple[str, str, type[Exception]]] = [
            ("req", _MISSING_UUID, ReqNotFoundError),
            ("uc", _MISSING_UUID, UcNotFoundError),
            ("tsk", _MISSING_UUID, TskNotFoundError),
            ("qa", _MISSING_UUID, QaNotFoundError),
            ("prb", _MISSING_UUID, PrbNotFoundError),
            ("sysrs", _MISSING_UUID, SysrsNotFoundError),
            ("gol", _MISSING_UUID, GolNotFoundError),
            ("rsk", _MISSING_UUID, RskNotFoundError),
            ("dec", _MISSING_UUID, DecNotFoundError),
            ("sop", _MISSING_UUID, SopNotFoundError),
            ("vcr", _MISSING_UUID, VcrNotFoundError),
            ("feat", "feat-999-no-such-feature", FeatNotFoundError),
            ("adr", _MISSING_UUID, AdrNotFoundError),
        ]
        for doc_type, missing_id, error_type in cases:
            with self.subTest(doc_type=doc_type):
                with self.assertRaises(error_type) as ctx:
                    get_reference_diagram(type=doc_type, id=missing_id)

                self.assertIsInstance(ctx.exception, LookupError)
                self.assertIn(missing_id, str(ctx.exception))


class TestGetReferenceDiagramBrokenSource(_SeededRegistryTestCase):
    """ACC-003: an existing-but-broken source returns the non-raising ``ParseFailureResult``
    (never the not-found error, never a diagram) -- for ``dec`` the ``error`` text is
    byte-identical to the domain's ``list_<d>`` failed-row ``error`` for the same file (ADR
    9080b37c); for ``feat`` (folder-per-document) and ``adr`` the result carries the broken file's
    resolved path and the domain's own parse-error text."""

    SEEDS = (("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),)

    def test_broken_dec_source_returns_parse_failure_result_byte_identical_to_list_dec(self) -> None:
        from biz.dfch.specmgr.dec.tools.list_dec import list_dec

        result = get_reference_diagram(type="dec", id=_D002)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertNotIsInstance(result, str)
        self.assertEqual(result.id, _D002)
        self.assertEqual(result.path, str((self.docs_root / "dec" / f"dec-{_D002}-broken.md").resolve()))
        self.assertTrue(result.error)

        listing = list_dec()
        failed = [row for row in listing.results if row.error is not None]
        self.assertEqual(len(failed), 1)
        # ADR 9080b37c: byte-identical to the domain's list_<d> failed row for the same file.
        self.assertEqual(result.error, failed[0].error)
        self.assertEqual(result.path, failed[0].path)

    def test_broken_feat_source_returns_parse_failure_result(self) -> None:
        broken_folder = self.feat_dir / "feat-9-broken"
        broken_folder.mkdir(parents=True)
        (broken_folder / "README.md").write_text(
            "---\nid: feat-9-broken\ntype: feat\nstatus: planning\nversion: 1.0.0\n---\n\n"
            "# Feature: Broken\n\nnot a valid feature body\n",
            encoding="utf-8",
        )

        result = get_reference_diagram(type="feat", id="feat-9-broken")

        self.assertIsInstance(result, ParseFailureResult)
        self.assertNotIsInstance(result, str)
        self.assertEqual(result.id, "feat-9-broken")
        self.assertEqual(result.path, str((broken_folder / "README.md").resolve()))
        self.assertTrue(result.error)

    def test_broken_adr_source_returns_parse_failure_result(self) -> None:
        broken = self.adr_dir / f"{_D002}-broken.md"
        broken.parent.mkdir(parents=True, exist_ok=True)
        broken.write_text(
            "---\nid: c00dc00d-c00d-4c0d-8c0d-c00dc00dc00d\ntype: adr\nstatus: draft\nversion: 1.0.0\n---\n\n"
            "# Broken ADR\n\n## A Wrong Heading\n\nThe heading structure does not fit the ADR schema.\n",
            encoding="utf-8",
        )

        result = get_reference_diagram(type="adr", id=_D002)

        self.assertIsInstance(result, ParseFailureResult)
        self.assertNotIsInstance(result, str)
        self.assertEqual(result.id, _D002)
        self.assertEqual(result.path, str(broken.resolve()))
        self.assertTrue(result.error)


class TestCycleRegistryTool(_SeededRegistryTestCase):
    """The scoped tool's byte-stable return over the 2-node-cycle registry: the depth-1/depth-2
    goldens (the env var UNSET, so ``max_label`` is the frozen default 40) + the default-``depth``
    pin + checker-clean over the tool's actual return (the full path end-to-end)."""

    SEEDS = (
        ("cycle/req-c001.md", f"docs/req/{_C001}.md"),
        ("cycle/req-c002.md", f"docs/req/{_C002}.md"),
    )

    def test_depth1_golden(self):
        result = get_reference_diagram(type="req", id=_C001, depth=1)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("cycle-scoped-depth1.puml"))
        _checker_clean(result)

    def test_depth2_golden(self):
        result = get_reference_diagram(type="req", id=_C001, depth=2)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("cycle-scoped-depth2.puml"))
        self.assertIn("-[#red]->", result)  # the on-cycle edges are red
        _checker_clean(result)

    def test_omitted_depth_is_the_default_one(self):
        result = get_reference_diagram(type="req", id=_C001)
        self.assertEqual(result, self._golden("cycle-scoped-depth1.puml"))


class TestChainRegistryTool(_SeededRegistryTestCase):
    """The scoped tool's byte-stable return over the depth-2 chain registry + the >40-char scoped
    H1 (the diagram title is untruncated, the node label truncates at the default 40)."""

    SEEDS = (
        ("chain/req-h001.md", f"docs/req/{_H001}.md"),
        ("chain/gol-g001.md", f"docs/gol/{_G001}.md"),
        ("chain/rsk-k001.md", f"docs/rsk/{_K001}.md"),
    )

    def test_depth1_golden(self):
        result = get_reference_diagram(type="req", id=_H001, depth=1)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("chain-scoped-depth1.puml"))
        _checker_clean(result)

    def test_depth2_golden(self):
        result = get_reference_diagram(type="req", id=_H001, depth=2)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("chain-scoped-depth2.puml"))

    def test_title_untruncated_label_truncated_at_the_default_40(self):
        result = get_reference_diagram(type="req", id=_H001, depth=1)
        long_h1 = "Chain Top Requirement With A Very Long Title"
        self.assertGreater(len(long_h1), 40)
        self.assertTrue(result.startswith(f"@startuml {long_h1}\n"))  # the title: never truncated
        self.assertIn(f'component "Chain Top Requirement With A Very Long…" as [REQ-{_H001}]', result)


class TestReverseRegistryTool(_SeededRegistryTestCase):
    """The scoped tool's byte-stable return over the reverse-hit registry: the plain depth-1
    golden, the additive reverse goldens (depth 1 and depth 2 -- the latter where only the forward
    part grows), and the feat dual-spelling nodes (the scoped source is a req, so ``include_feat``
    defaults to keeping them)."""

    SEEDS = (
        ("reverse/req-r001.md", f"docs/req/{_R001}.md"),
        ("reverse/dec-d001.md", f"docs/dec/{_D001}.md"),
        ("reverse/feat-42-reverse-feat", "feat/feat-42-reverse-feat"),
    )

    def test_depth1_golden(self):
        result = get_reference_diagram(type="req", id=_R001, depth=1)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("reverse-scoped-depth1.puml"))
        _checker_clean(result)

    def test_depth1_reverse_golden(self):
        result = get_reference_diagram(type="req", id=_R001, depth=1, reverse=True)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("reverse-scoped-depth1-reverse.puml"))

    def test_depth2_reverse_golden(self):
        result = get_reference_diagram(type="req", id=_R001, depth=2, reverse=True)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("reverse-scoped-depth2-reverse.puml"))

    def test_feat_source_round_trip(self):
        """The feat source itself (the full ``feat-NNN-slug`` id) renders its own golden."""
        result = get_reference_diagram(type="feat", id=_SEEDED_FEAT_ID, depth=1)
        self.assertIsInstance(result, str)
        self.assertIn("as [feat-42-reverse-feat] <<FEAT>>", result)  # the feat alias is the verbatim id
        _checker_clean(result)


class TestReverseFeatSourceRegistryTool(_SeededRegistryTestCase):
    """The scoped tool's byte-stable return over the G1 FEAT-source reverse registry (Phase 150):
    ``get_reference_diagram(type="feat", id="feat-42-reverse-feat", depth=1, reverse=True)`` pins
    the full tool path end-to-end -- including the ``feat`` source-id guard accepting the full
    spelling -- to the builder-level ``reverse-feat-source-reverse.puml`` golden (the
    bare-spelling branch's ``dec-b001 -> feat`` edge is only reachable through the tool's own
    reverse scan over this seed set)."""

    SEEDS = (
        ("reverse/req-r001.md", f"docs/req/{_R001}.md"),
        ("reverse/dec-d001.md", f"docs/dec/{_D001}.md"),
        ("reverse/dec-b001.md", f"docs/dec/{_B001}.md"),
        ("reverse/feat-42-reverse-feat", "feat/feat-42-reverse-feat"),
    )

    def test_reverse_feat_source_golden(self):
        result = get_reference_diagram(type="feat", id=_SEEDED_FEAT_ID, depth=1, reverse=True)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("reverse-feat-source-reverse.puml"))
        _checker_clean(result)


class TestNoFeatRegistryTool(_SeededRegistryTestCase):
    """The scoped tool's byte-stable return over the ``include_feat`` drop-semantics registry:
    the req source's plain and ``include_feat=False`` goldens, and the feat SOURCE's plain and
    ``include_feat=False`` goldens (the source exception: the requested feat node stays)."""

    SEEDS = (
        ("no-feat/req-n001.md", f"docs/req/{_N001}.md"),
        ("no-feat/feat-7-no-feat", "feat/feat-7-no-feat"),
        ("no-feat/feat-8-no-feat-two", "feat/feat-8-no-feat-two"),
    )

    def test_scoped_source_golden(self):
        result = get_reference_diagram(type="req", id=_N001, depth=1)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("no-feat-scoped-source.puml"))
        _checker_clean(result)

    def test_scoped_source_no_feat_golden(self):
        result = get_reference_diagram(type="req", id=_N001, depth=1, include_feat=False)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("no-feat-scoped-source-no-feat.puml"))

    def test_scoped_feat_source_golden(self):
        result = get_reference_diagram(type="feat", id="feat-7-no-feat", depth=1)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("no-feat-scoped-feat-source.puml"))

    def test_scoped_feat_source_no_feat_keeps_the_source(self):
        result = get_reference_diagram(type="feat", id="feat-7-no-feat", depth=1, include_feat=False)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("no-feat-scoped-feat-source-no-feat.puml"))
        self.assertIn("feat-7-no-feat", result)  # the source exception
        self.assertNotIn("feat-8-no-feat-two", result)


class TestWideRegistryTool(_SeededRegistryTestCase):
    """The scoped tool's byte-stable return over the multi-domain registry (the never-cached adr
    leg included, the broken dec present as a scanned-but-skipped document)."""

    SEEDS = (
        ("wide/req-w001.md", f"docs/req/{_W001}.md"),
        ("wide/uc-u001.md", f"docs/uc/{_U001}.md"),
        ("wide/gol-g001.md", f"docs/gol/{_WG001}.md"),
        ("wide/adr-a001.md", f"adr/{_A001}.md"),
        ("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),
    )

    def test_scoped_reverse_golden(self):
        result = get_reference_diagram(type="req", id=_W001, depth=1, reverse=True)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("wide-scoped-reverse.puml"))
        self.assertNotIn(_D002, result)  # the broken dec is skipped (never a node)
        _checker_clean(result)


class TestGetReferenceDiagramTitleOverride(_SeededRegistryTestCase):
    """The ``title`` override: it replaces the graph's title before rendering -- sanitized (an
    embedded ``"`` becomes ``#quot;``) but NEVER truncated, even past the label limit."""

    SEEDS = (("chain/req-h001.md", f"docs/req/{_H001}.md"),)

    def test_a_long_title_stays_whole_on_the_startuml_line(self):
        long_title = "A very long custom diagram title well over forty characters long"
        self.assertGreater(len(long_title), 40)

        result = get_reference_diagram(type="req", id=_H001, depth=1, title=long_title)

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith(f"@startuml {long_title}\n"))  # not truncated
        # the override replaces the diagram's TITLE only: the source node's own
        # label (its H1, truncated at the default 40) is unchanged
        self.assertIn(f'component "Chain Top Requirement With A Very Long…" as [REQ-{_H001}]', result)

    def test_an_embedded_quote_is_sanitised(self):
        result = get_reference_diagram(type="req", id=_H001, depth=1, title='Say "hello"')

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("@startuml Say #quot;hello#quot;\n"))


class TestGetReferenceDiagramEnvVar(_SeededRegistryTestCase):
    """The tool reads ``SPECMGR_DIAGRAM_MAX_TITLE`` via the shared helper: a valid custom value
    truncates at it (word-boundary cut + ``…``), a set-but-invalid value falls back to the
    default 40 (the golden again), and the title is never affected."""

    SEEDS = (
        ("chain/req-h001.md", f"docs/req/{_H001}.md"),
        ("chain/gol-g001.md", f"docs/gol/{_G001}.md"),
        ("chain/rsk-k001.md", f"docs/rsk/{_K001}.md"),
    )

    def test_a_custom_limit_truncates_the_labels(self):
        with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: "8"}):
            result = get_reference_diagram(type="req", id=_H001, depth=1)

        self.assertIsInstance(result, str)
        self.assertIn(f'component "Chain…" as [REQ-{_H001}]', result)  # word-boundary cut at 8
        self.assertTrue(result.startswith("@startuml Chain Top Requirement With A Very Long Title\n"))

    def test_a_set_but_invalid_limit_falls_back_to_the_default_40(self):
        for value in ("", "abc", "0"):
            with self.subTest(value=value):
                with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: value}):
                    result = get_reference_diagram(type="req", id=_H001, depth=1)
                self.assertEqual(result, self._golden("chain-scoped-depth1.puml"))  # the default-40 golden

    def test_a_large_limit_never_truncates(self):
        with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: "100"}):
            result = get_reference_diagram(type="req", id=_H001, depth=1)

        self.assertIsInstance(result, str)
        self.assertIn(f'component "Chain Top Requirement With A Very Long Title" as [REQ-{_H001}]', result)
        self.assertNotIn("…", result)


class TestGetReferenceDiagramGoldenRoundTrip(_SeededRegistryTestCase):
    """A sanity round-trip over every committed builder golden the scoped tool can produce: the
    tool's return equals the golden (the library's builder+renderer, not a second copy of it) --
    the full MCP path is pinned to the Phase 110 library's byte-stable output."""

    SEEDS = (
        ("cycle/req-c001.md", f"docs/req/{_C001}.md"),
        ("cycle/req-c002.md", f"docs/req/{_C002}.md"),
        ("chain/req-h001.md", f"docs/req/{_H001}.md"),
        ("chain/gol-g001.md", f"docs/gol/{_G001}.md"),
        ("chain/rsk-k001.md", f"docs/rsk/{_K001}.md"),
        ("reverse/req-r001.md", f"docs/req/{_R001}.md"),
        ("reverse/dec-d001.md", f"docs/dec/{_D001}.md"),
        ("reverse/dec-b001.md", f"docs/dec/{_B001}.md"),
        ("reverse/feat-42-reverse-feat", "feat/feat-42-reverse-feat"),
        ("no-feat/req-n001.md", f"docs/req/{_N001}.md"),
        ("no-feat/feat-7-no-feat", "feat/feat-7-no-feat"),
        ("no-feat/feat-8-no-feat-two", "feat/feat-8-no-feat-two"),
        ("wide/req-w001.md", f"docs/req/{_W001}.md"),
        ("wide/uc-u001.md", f"docs/uc/{_U001}.md"),
        ("wide/gol-g001.md", f"docs/gol/{_WG001}.md"),
        ("wide/adr-a001.md", f"adr/{_A001}.md"),
        ("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),
    )

    def test_every_scoped_golden_is_reachable_through_the_tool(self):
        scenarios: list[tuple[str, str, dict[str, Any], str]] = [
            ("cycle-scoped-depth1.puml", "req", {"id": _C001, "depth": 1}, "cycle"),
            ("cycle-scoped-depth2.puml", "req", {"id": _C001, "depth": 2}, "cycle"),
            ("chain-scoped-depth1.puml", "req", {"id": _H001, "depth": 1}, "chain"),
            ("chain-scoped-depth2.puml", "req", {"id": _H001, "depth": 2}, "chain"),
            ("reverse-scoped-depth1.puml", "req", {"id": _R001, "depth": 1}, "reverse"),
            ("reverse-scoped-depth1-reverse.puml", "req", {"id": _R001, "depth": 1, "reverse": True}, "reverse"),
            ("reverse-scoped-depth2-reverse.puml", "req", {"id": _R001, "depth": 2, "reverse": True}, "reverse"),
            (
                "reverse-feat-source-reverse.puml",
                "feat",
                {"id": _SEEDED_FEAT_ID, "depth": 1, "reverse": True},
                "reverse",
            ),
            ("no-feat-scoped-source.puml", "req", {"id": _N001, "depth": 1}, "no-feat"),
            ("no-feat-scoped-source-no-feat.puml", "req", {"id": _N001, "depth": 1, "include_feat": False}, "no-feat"),
            ("no-feat-scoped-feat-source.puml", "feat", {"id": "feat-7-no-feat", "depth": 1}, "no-feat"),
            (
                "no-feat-scoped-feat-source-no-feat.puml",
                "feat",
                {"id": "feat-7-no-feat", "depth": 1, "include_feat": False},
                "no-feat",
            ),
            ("wide-scoped-reverse.puml", "req", {"id": _W001, "depth": 1, "reverse": True}, "wide"),
        ]
        for golden_name, doc_type, kwargs, _scenario in scenarios:
            with self.subTest(golden=golden_name):
                self.assertEqual(get_reference_diagram(type=doc_type, **kwargs), self._golden(golden_name))
                self.assertEqual(
                    get_reference_diagram(type=doc_type, **kwargs),
                    render_reference_graph(
                        build_source_graph(doc_type, kwargs["id"], **{k: v for k, v in kwargs.items() if k != "id"})
                    ),
                )


if __name__ == "__main__":
    unittest.main()
