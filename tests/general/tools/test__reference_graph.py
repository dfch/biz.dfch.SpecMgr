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

"""Tests for ``general.tools._reference_graph`` (feat-207-reference-graph, Phase 110, Task 110.150).

The builder integration tests over the synthetic seeded registries under
``tests/fixtures/reference-graphs/`` (ACC-001's scenario matrix): the
isolated ``SPECMGR_DOCS_DIR``/``SPECMGR_ADR_DIR``/``SPECMGR_FEAT_DIR`` tmp
dirs follow the ``tests/commands/test_diagram.py`` precedent (the env vars
are read per call, so patching is clean and isolated), the per-domain
process-local doc caches are reset in ``setUp``/``tearDown`` (the
``reset_<d>_cache`` test hooks; the shared fixture ids and the
``_SeededRegistryTestCase`` base live in ``._reference_graph_helpers``,
which the Phase 120 tool tests use too), and every scenario's graph is rendered
with the default ``max_label=40`` and byte-compared against the committed
goldens under ``tests/fixtures/reference-graphs/goldens/`` (the
checker-clean property of every golden -- both structure-checker modes,
zero findings -- is pinned in ``tests/general/models/test_reference_graph.py``).

Covered scenarios: a 2-node cycle (both edges red, depth 2) + the
incomplete depth-1 case (no red yet), a self-loop (red), a dangling
reference (top-level ``<<UNRESOLVED>>`` node, id verbatim), a depth-2
chain (depth 1 vs 2 goldens differ), the feat dual spellings (two distinct
nodes, both resolved), the reverse hit (the additive union: the forward
neighbourhood plus the direct incoming edges; the ``depth=2`` +
``reverse=True`` call where only the forward part grows, and the
direct-only pin -- a reverse-scanned document's own dangling reference
never surfaces), the ``include_feat=False`` drop semantics (the feat
SOURCE stays, other feat nodes/edges drop), the registry-wide +
``include_feat=False`` combination with a non-feat→feat reference (the
feat target must not appear as a node or an edge), the registry-wide
default (title ``Reference Graph``), the scoped title default (the source's
H1, untruncated even at >40 chars while the node label truncates), the
skip-broken (a broken document is never a node, never an edge source --
registry-wide and reverse alike), and the builder error contract (a
missing source raises the source domain's own ``XNotFoundError``; an
existing-but-broken source raises the domain's own parse error -- the
``ParseFailureResult`` conversion is the Phase 120 tool layer's job).
"""

from __future__ import annotations

import shutil
import unittest

import yaml
from pydantic import ValidationError

from biz.dfch.specmgr.adr.tools._paths import AdrNotFoundError
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.feat.tools._paths import FeatNotFoundError
from biz.dfch.specmgr.general.models.reference_graph import render_reference_graph
from biz.dfch.specmgr.general.tools._reference_graph import build_registry_graph, build_source_graph
from biz.dfch.specmgr.models.adr import AdrParseError
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError

from ._reference_graph_helpers import (
    _FIXTURES,
    _MISSING_UUID,
    _SeededRegistryTestCase,
    _A001,
    _C001,
    _C002,
    _D001,
    _D002,
    _D900,
    _G001,
    _G900,
    _H001,
    _K001,
    _N001,
    _R001,
    _U001,
    _W001,
    _WG001,
)


class TestCycleRegistry(_SeededRegistryTestCase):
    """Scenario 1/2/3: the 2-node cycle (both edges red at depth 2), the self-loop (red), the
    dangling reference (top-level ``<<UNRESOLVED>>`` node, id verbatim) -- and the depth-1 case
    where the cycle is not yet complete (no red edge)."""

    SEEDS = (
        ("cycle/req-c001.md", f"docs/req/{_C001}.md"),
        ("cycle/req-c002.md", f"docs/req/{_C002}.md"),
    )

    def test_depth1_golden(self):
        self._render_golden("cycle-scoped-depth1.puml", build_source_graph("req", _C001, depth=1))

    def test_depth2_golden(self):
        self._render_golden("cycle-scoped-depth2.puml", build_source_graph("req", _C001, depth=2))

    def test_depth1_carries_no_red_edge(self):
        # the cycle is incomplete at depth 1 (c002 is never expanded, so no
        # return edge): the red form must not appear
        rendered = render_reference_graph(build_source_graph("req", _C001, depth=1))
        self.assertNotIn("-[#red]->", rendered)

    def test_depth2_marks_the_cycle_and_the_self_loop_red(self):
        rendered = render_reference_graph(build_source_graph("req", _C001, depth=2))
        self.assertIn(
            f"[REQ-{_C001}] -[#red]-> [REQ-{_C002}] : refers to",
            rendered,  # 2-cycle, edge 1
        )
        self.assertIn(
            f"[REQ-{_C002}] -[#red]-> [REQ-{_C001}] : refers to",
            rendered,  # 2-cycle, edge 2
        )
        self.assertIn(
            f"[REQ-{_C002}] -[#red]-> [REQ-{_C002}] : refers to",
            rendered,  # self-loop
        )
        self.assertIn(
            f'component "{_D900}" as [DEC-{_D900}] <<UNRESOLVED>>',
            rendered,  # dangling: id verbatim
        )
        self.assertNotIn("…", rendered)  # every label here fits the default 40


class TestChainRegistry(_SeededRegistryTestCase):
    """Scenario 5/11: the depth-2 chain (depth 1 vs 2 goldens differ) + the >40-char scoped H1
    (the diagram title is untruncated, the node label is truncated at the default 40)."""

    SEEDS = (
        ("chain/req-h001.md", f"docs/req/{_H001}.md"),
        ("chain/gol-g001.md", f"docs/gol/{_G001}.md"),
        ("chain/rsk-k001.md", f"docs/rsk/{_K001}.md"),
    )

    def test_depth1_golden(self):
        self._render_golden("chain-scoped-depth1.puml", build_source_graph("req", _H001, depth=1))

    def test_depth2_golden(self):
        self._render_golden("chain-scoped-depth2.puml", build_source_graph("req", _H001, depth=2))

    def test_depth1_and_depth2_differ(self):
        depth1 = self._golden("chain-scoped-depth1.puml")
        depth2 = self._golden("chain-scoped-depth2.puml")
        self.assertNotEqual(depth1, depth2)
        self.assertNotIn(f"[RSK-{_K001}]", depth1)
        self.assertIn(f"[RSK-{_K001}]", depth2)

    def test_title_untruncated_label_truncated_at_the_default_40(self):
        rendered = render_reference_graph(build_source_graph("req", _H001, depth=1))
        long_h1 = "Chain Top Requirement With A Very Long Title"
        self.assertGreater(len(long_h1), 40)
        self.assertTrue(rendered.startswith(f"@startuml {long_h1}\n"))  # the title: never truncated
        self.assertIn(f'component "Chain Top Requirement With A Very Long…" as [REQ-{_H001}]', rendered)


class TestReverseRegistry(_SeededRegistryTestCase):
    """Scenario 4/6: the feat dual spellings (two distinct nodes) + the reverse hit (the additive
    union: the forward neighbourhood plus the direct incoming edges; the ``depth=2`` +
    ``reverse=True`` call where only the forward part grows, and the direct-only pin -- the
    reverse-scanned dec's own dangling reference never surfaces)."""

    SEEDS = (
        ("reverse/req-r001.md", f"docs/req/{_R001}.md"),
        ("reverse/dec-d001.md", f"docs/dec/{_D001}.md"),
        ("reverse/feat-42-reverse-feat", "feat/feat-42-reverse-feat"),
    )

    def test_depth1_golden(self):
        self._render_golden("reverse-scoped-depth1.puml", build_source_graph("req", _R001, depth=1))

    def test_depth1_reverse_golden(self):
        self._render_golden(
            "reverse-scoped-depth1-reverse.puml", build_source_graph("req", _R001, depth=1, reverse=True)
        )

    def test_depth2_reverse_golden(self):
        self._render_golden(
            "reverse-scoped-depth2-reverse.puml", build_source_graph("req", _R001, depth=2, reverse=True)
        )

    def test_dual_spellings_are_two_distinct_nodes(self):
        rendered = render_reference_graph(build_source_graph("req", _R001, depth=1))
        self.assertIn('component "Reverse Feature" as [feat-42] <<FEAT>>', rendered)  # the bare spelling
        self.assertIn(
            'component "Reverse Feature" as [feat-42-reverse-feat] <<FEAT>>',
            rendered,  # the full spelling
        )

    def test_reverse_is_additive_and_direct_only(self):
        depth1_reverse = self._golden("reverse-scoped-depth1-reverse.puml")
        depth2_reverse = self._golden("reverse-scoped-depth2-reverse.puml")
        # the dec's own dangling reference (GOL g900) must NEVER surface: a
        # reverse-scanned document is added as a node + one incoming edge, but
        # its own references are never walked (no transitive incoming expansion)
        for rendered in (depth1_reverse, depth2_reverse):
            self.assertNotIn(f"[GOL-{_G900}]", rendered)
            self.assertIn(f"[DEC-{_D001}]", rendered)  # the incoming edge's source is a node
        # only the forward part grows with depth=2: the bare feat spelling
        # (resolved to the same document) gets its own return edge
        self.assertNotIn(f"[feat-42] -[#red]-> [REQ-{_R001}]", depth1_reverse)
        self.assertIn(f"[feat-42] -[#red]-> [REQ-{_R001}]", depth2_reverse)


class TestNoFeatRegistry(_SeededRegistryTestCase):
    """Scenario 7/8/10: the ``include_feat=False`` drop semantics (the feat SOURCE stays, other feat
    nodes/edges drop), the registry-wide + ``include_feat=False`` combination with a
    non-feat→feat reference (the feat target must not appear as a node or an edge), and the
    registry-wide default title (``Reference Graph`` vs the scoped source's H1)."""

    SEEDS = (
        ("no-feat/req-n001.md", f"docs/req/{_N001}.md"),
        ("no-feat/feat-7-no-feat", "feat/feat-7-no-feat"),
        ("no-feat/feat-8-no-feat-two", "feat/feat-8-no-feat-two"),
    )

    def test_scoped_source_golden(self):
        self._render_golden("no-feat-scoped-source.puml", build_source_graph("req", _N001, depth=1))

    def test_scoped_source_no_feat_golden(self):
        self._render_golden(
            "no-feat-scoped-source-no-feat.puml", build_source_graph("req", _N001, depth=1, include_feat=False)
        )

    def test_scoped_feat_source_golden(self):
        self._render_golden("no-feat-scoped-feat-source.puml", build_source_graph("feat", "feat-7-no-feat", depth=1))

    def test_scoped_feat_source_no_feat_keeps_the_source(self):
        # the source exception: the explicitly requested feat source stays,
        # the OTHER feat node + the edge touching it drop
        graph = build_source_graph("feat", "feat-7-no-feat", depth=1, include_feat=False)
        self._render_golden("no-feat-scoped-feat-source-no-feat.puml", graph)
        node_ids = {node.id for node in graph.nodes}
        self.assertIn("feat-7-no-feat", node_ids)  # the source exception
        self.assertNotIn("feat-8-no-feat-two", node_ids)
        self.assertIn(_N001, node_ids)
        self.assertEqual(
            {(edge.source_type, edge.source_id, edge.target_type, edge.target_id) for edge in graph.edges},
            {("feat", "feat-7-no-feat", "req", _N001)},
        )

    def test_registry_all_golden(self):
        self._render_golden("no-feat-registry-all.puml", build_registry_graph())

    def test_registry_all_no_feat_golden(self):
        # the feat target must not appear as a node OR an edge
        graph = build_registry_graph(include_feat=False)
        self._render_golden("no-feat-registry-no-feat.puml", graph)
        self.assertNotIn("feat", {node.type for node in graph.nodes})
        self.assertEqual(graph.edges, ())

    def test_title_defaults(self):
        scoped = render_reference_graph(build_source_graph("req", _N001, depth=1))
        registry = render_reference_graph(build_registry_graph())
        self.assertTrue(scoped.startswith("@startuml No Feat Source\n"))  # the scoped default: the source's H1
        self.assertTrue(registry.startswith("@startuml Reference Graph\n"))  # the registry default


class TestWideRegistry(_SeededRegistryTestCase):
    """Scenario 9/13: the registry-wide default over the multi-domain registry (the never-cached
    adr leg included) + the skip-broken (a broken document is never a node, never an edge
    source -- registry-wide and reverse alike, though its raw text carries a live-looking
    reference)."""

    SEEDS = (
        ("wide/req-w001.md", f"docs/req/{_W001}.md"),
        ("wide/uc-u001.md", f"docs/uc/{_U001}.md"),
        ("wide/gol-g001.md", f"docs/gol/{_WG001}.md"),
        ("wide/adr-a001.md", f"adr/{_A001}.md"),
        ("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),
    )

    def test_registry_all_golden(self):
        self._render_golden("wide-registry-all.puml", build_registry_graph())

    def test_scoped_reverse_golden(self):
        self._render_golden("wide-scoped-reverse.puml", build_source_graph("req", _W001, depth=1, reverse=True))

    def test_broken_document_is_skipped_everywhere(self):
        for graph in (build_registry_graph(), build_source_graph("req", _W001, depth=1, reverse=True)):
            rendered = render_reference_graph(graph)
            self.assertNotIn(_D002, rendered)  # never a node (no alias, no verbatim-id label)
            self.assertNotIn("Broken Decision", rendered)
            # and never an edge source: the broken dec's live-looking
            # reference to w001 must not contribute the edge
            self.assertNotIn(f"[DEC-{_D002}]", rendered)

    def test_adr_leg_is_carried(self):
        # the never-cached adr leg (ADR bfd76370): the ADR document is a node
        # and its reference an edge in both modes
        for graph in (build_registry_graph(), build_source_graph("req", _W001, depth=1, reverse=True)):
            rendered = render_reference_graph(graph)
            self.assertIn('package "ADR"', rendered)
            self.assertIn(f"[ADR-{_A001}] --> [REQ-{_W001}] : refers to", rendered)


class TestBuilderErrorContract(_SeededRegistryTestCase):
    """Scenario 14: the builder error contract -- a missing source raises the source domain's own
    ``XNotFoundError``; an existing-but-broken source raises the domain's own parse error (the
    non-raising ``ParseFailureResult`` is the Phase 120 tool layer's conversion, not the
    builder's)."""

    SEEDS = (("cycle/req-c001.md", f"docs/req/{_C001}.md"),)

    def test_missing_source_raises_the_domain_not_found_error(self):
        with self.assertRaises(ReqNotFoundError):
            build_source_graph("req", _MISSING_UUID)
        with self.assertRaises(DecNotFoundError):
            build_source_graph("dec", _MISSING_UUID)
        with self.assertRaises(FeatNotFoundError):
            build_source_graph("feat", "feat-999-no-such-feature")
        with self.assertRaises(AdrNotFoundError):
            build_source_graph("adr", _MISSING_UUID)

    def test_broken_flat_source_raises_the_domain_parse_error(self):
        # the broken dec fixture re-used as a req file: parse_req rejects the
        # foreign frontmatter type -- a genuine parse error (ValidationError)
        broken = self.docs_root / "req" / f"req-{_D002}-broken.md"
        shutil.copy(_FIXTURES / "wide" / "dec-d002.md", broken)
        with self.assertRaises((AssertionError, ValidationError, yaml.YAMLError)):
            build_source_graph("req", _D002)

    def test_broken_feat_source_raises_the_domain_parse_error(self):
        broken_folder = self.feat_dir / "feat-9-broken"
        broken_folder.mkdir(parents=True)
        (broken_folder / "README.md").write_text(
            "---\nid: feat-9-broken\ntype: feat\nstatus: planning\nversion: 1.0.0\n---\n\n"
            "# Feature: Broken\n\nnot a valid feature body\n",
            encoding="utf-8",
        )
        with self.assertRaises((AssertionError, ValidationError, yaml.YAMLError)):
            build_source_graph("feat", "feat-9-broken")

    def test_broken_adr_source_raises_the_domain_parse_error(self):
        broken = self.adr_dir / f"{_D002}-broken.md"
        broken.parent.mkdir(parents=True, exist_ok=True)
        broken.write_text(
            "---\nid: c00dc00d-c00d-4c0d-8c0d-c00dc00dc00d\ntype: adr\nstatus: draft\nversion: 1.0.0\n---\n\n"
            "# Broken ADR\n\n## A Wrong Heading\n\nThe heading structure does not fit the ADR schema.\n",
            encoding="utf-8",
        )
        with self.assertRaises((AdrParseError, ValidationError)):
            build_source_graph("adr", _D002)


class TestFixtureValidity(unittest.TestCase):
    """The committed fixture documents themselves stay valid: every healthy fixture parses
    through its own domain parser, and the deliberately broken one fails (a fixture drift
    guard -- a schema evolution in any domain must break these fixtures loudly)."""

    def test_healthy_fixtures_parse_and_the_broken_one_fails(self):
        from collections.abc import Callable
        from typing import Any

        from biz.dfch.specmgr.dec.models.v1.parser import parse_dec
        from biz.dfch.specmgr.feat.models.v1.parser import parse_feat
        from biz.dfch.specmgr.gol.models.v1.parser import parse_gol
        from biz.dfch.specmgr.models.adr import parse_adr
        from biz.dfch.specmgr.req.models.v1.parser import parse_req
        from biz.dfch.specmgr.rsk.models.v1.parser import parse_rsk
        from biz.dfch.specmgr.uc.models.v2.parser import parse_uc

        healthy: list[tuple[str, Callable[[str], Any]]] = [
            ("cycle/req-c001.md", parse_req),
            ("cycle/req-c002.md", parse_req),
            ("chain/req-h001.md", parse_req),
            ("chain/gol-g001.md", parse_gol),
            ("chain/rsk-k001.md", parse_rsk),
            ("reverse/req-r001.md", parse_req),
            ("reverse/dec-d001.md", parse_dec),
            ("reverse/feat-42-reverse-feat/README.md", parse_feat),
            ("no-feat/req-n001.md", parse_req),
            ("no-feat/feat-7-no-feat/README.md", parse_feat),
            ("no-feat/feat-8-no-feat-two/README.md", parse_feat),
            ("wide/req-w001.md", parse_req),
            ("wide/uc-u001.md", parse_uc),
            ("wide/gol-g001.md", parse_gol),
            ("wide/adr-a001.md", parse_adr),
        ]
        for relative, parse_fn in healthy:
            with self.subTest(fixture=relative):
                doc = parse_fn((_FIXTURES / relative).read_text(encoding="utf-8"))
                self.assertIsNotNone(doc.frontmatter.id)

        broken_text = (_FIXTURES / "wide" / "dec-d002.md").read_text(encoding="utf-8")
        with self.assertRaises((AssertionError, ValidationError, yaml.YAMLError)):
            parse_dec(broken_text)


if __name__ == "__main__":
    unittest.main()
