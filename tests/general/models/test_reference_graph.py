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

"""Tests for ``general.models.reference_graph`` (feat-207-reference-graph, Phase 110, Task 110.150).

The pure renderer's unit goldens over hand-built :class:`ReferenceGraph`
facts (no registry): the rulebook §2.9 worked example reproduced
byte-for-byte (the anchor golden, rendered at ``max_label=42`` -- the
example's 42-char feat label is the exactly-N no-op case of §5.2), the SCC
characterization cases (a 3-cycle + self-loop, a separate 2-cycle, an
off-cycle edge between SCC neighbours, an isolated node, an unresolved
node), the degenerate zero-edge single-node case, the truncation edge
cases at the default 40 and a custom 12 (word-boundary cut, hard cut,
exactly-N no-op) alongside an untruncated diagram title at a >40-char
scoped H1, and the title/label sanitisation (embedded ``"`` → ``#quot;``,
literal newline → the two-character sequence ``\\n``). Every golden must
pass the amended structure checker in both modes with ZERO findings
(ACC-001's last clause -- pinned over the whole goldens directory, the
builder goldens included, by the last test class here).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from biz.dfch.specmgr.general.models.reference_graph import (
    DEFAULT_MAX_LABEL,
    GraphEdge,
    GraphNode,
    ReferenceGraph,
    _DOMAIN_ORDER,
    _alias,
    _on_cycle_edges,
    _sanitize,
    _single_line,
    _truncate,
    render_reference_graph,
)
from biz.dfch.specmgr.plantuml.structure import MODE_PREFLIGHT, MODE_STANDALONE, check_structure

_GOLDENS = Path(__file__).resolve().parents[2] / "fixtures" / "reference-graphs" / "goldens"

#: The rulebook §2.9 worked example's node ids (the anchor graph).
_A = "1a2b3c4d-5e6f-4a5b-8c9d-0e1f2a3b4c5d"
_B = "6f7e8d9c-5b4a-4f3e-8d7c-6b5a4f3e2d1c"
_C = "9cfe511e-3f0f-4f0e-b3f4-9c8f5f1c1a2b"
_FEAT_ID = "feat-207-reference-graph"
_FEAT_H1 = "Feature: PlantUML Reference Graph Diagrams"

#: The SCC characterization graph's node ids (also the truncation graphs').
_S1 = "eeee0001-0000-4000-8000-eeeeeeeeeeee"
_S2 = "eeee0002-0000-4000-8000-eeeeeeeeeeee"
_S3 = "eeee0003-0000-4000-8000-eeeeeeeeeeee"
_S4 = "eeee0004-0000-4000-8000-eeeeeeeeeeee"
_S5 = "eeee0005-0000-4000-8000-eeeeeeeeeeee"
_S6 = "eeee0006-0000-4000-8000-eeeeeeeeeeee"
_S7 = "eeee0007-0000-4000-8000-eeeeeeeeeeee"

#: The §2.9 anchor graph (hand-built facts, exactly the worked example's
#: node/edge collection).
_SECTION_2_9 = ReferenceGraph(
    title="Requirement A",
    nodes=(
        GraphNode("req", _A, "Requirement A"),
        GraphNode("uc", _B, "Use Case B"),
        GraphNode("dec", _C, None),
        GraphNode("feat", _FEAT_ID, _FEAT_H1),
    ),
    edges=(
        GraphEdge("feat", _FEAT_ID, "req", _A),
        GraphEdge("req", _A, "dec", _C),
        GraphEdge("req", _A, "req", _A),
        GraphEdge("req", _A, "uc", _B),
        GraphEdge("uc", _B, "req", _A),
    ),
)


def _golden(name: str) -> str:
    return (_GOLDENS / name).read_text(encoding="utf-8")


def _scc_graph() -> ReferenceGraph:
    """The SCC characterization graph: a 3-cycle + self-loop (REQ), a 2-cycle (UC), an
    off-cycle edge between SCC neighbours (REQ→UC), an isolated node (GOL), and an
    unresolved node (DEC, referenced only)."""
    return ReferenceGraph(
        title="SCC Characterization",
        nodes=(
            GraphNode("req", _S1, "Scc Node A"),
            GraphNode("req", _S2, "Scc Node B"),
            GraphNode("req", _S3, "Scc Node C"),
            GraphNode("uc", _S4, "Scc Node D"),
            GraphNode("uc", _S5, "Scc Node E"),
            GraphNode("gol", _S6, "Scc Node G"),
            GraphNode("dec", _S7, None),
        ),
        edges=(
            GraphEdge("req", _S1, "req", _S2),
            GraphEdge("req", _S2, "req", _S3),
            GraphEdge("req", _S3, "req", _S1),
            GraphEdge("req", _S2, "req", _S2),
            GraphEdge("uc", _S4, "uc", _S5),
            GraphEdge("uc", _S5, "uc", _S4),
            GraphEdge("req", _S3, "uc", _S4),
            GraphEdge("req", _S1, "dec", _S7),
        ),
    )


def _truncation_graph(limit: int) -> ReferenceGraph:
    """The truncation graph for ``limit``: at 40 the default-limit trio (a 50-char word-boundary
    title, a 45-char hard-cut title, an exactly-40-char no-op title) under a 60-char diagram
    title; at 12 the custom-limit trio (22/15/12-char titles) under a short title."""
    if limit == DEFAULT_MAX_LABEL:
        return ReferenceGraph(
            title="Truncation Default Title With Far More Than Forty Characters",
            nodes=(
                GraphNode("req", _S1, "Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota"),
                GraphNode("req", _S2, "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHI"),
                GraphNode("req", _S3, "Alpha Beta Gamma Delta Epsilon Zeta Etas"),
            ),
            edges=(),
        )
    return ReferenceGraph(
        title="Custom Twelve",
        nodes=(
            GraphNode("req", _S1, "Alpha Beta Gamma Delta"),
            GraphNode("req", _S2, "abcdefghijklmno"),
            GraphNode("req", _S3, "abcdefghijkl"),
        ),
        edges=(),
    )


class TestSanitisationAndTruncation(unittest.TestCase):
    """The pure §5 character rules (sanitisation, single-line, truncation)."""

    def test_quote_sanitisation(self):
        self.assertEqual(_sanitize('A "quoted" title'), "A #quot;quoted#quot; title")
        self.assertEqual(_sanitize("no quotes"), "no quotes")

    def test_single_line_escaping(self):
        # sanitisation first, then the newline escape (the UC rulebook §2.4 order)
        self.assertEqual(_single_line('He said "hi"\nnext'), "He said #quot;hi#quot;\\nnext")
        self.assertEqual(_single_line("plain"), "plain")

    def test_truncation_word_boundary_cut(self):
        label = "Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota"  # 50 chars
        self.assertEqual(_truncate(label, 40), "Alpha Beta Gamma Delta Epsilon Zeta…")
        self.assertLessEqual(len(_truncate(label, 40)), 40)

    def test_truncation_hard_cut_without_space(self):
        label = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHI"  # 45 chars, no space
        self.assertEqual(_truncate(label, 40), "abcdefghijklmnopqrstuvwxyz0123456789ABC…")
        self.assertEqual(len(_truncate(label, 40)), 40)

    def test_truncation_exactly_n_untouched(self):
        label = "Alpha Beta Gamma Delta Epsilon Zeta Etas"  # exactly 40 chars
        self.assertEqual(_truncate(label, 40), label)
        self.assertEqual(_truncate(label, 41), label)

    def test_truncation_custom_limit(self):
        self.assertEqual(_truncate("Alpha Beta Gamma Delta", 12), "Alpha Beta…")
        self.assertEqual(_truncate("abcdefghijklmno", 12), "abcdefghijk…")
        self.assertEqual(_truncate("abcdefghijkl", 12), "abcdefghijkl")

    def test_truncation_limit_one(self):
        self.assertEqual(_truncate("ab", 1), "…")
        self.assertEqual(_truncate("a", 1), "a")


class TestAliasAndConstants(unittest.TestCase):
    """The §2.3 alias rule (bracketed ``TYPE-{uuid}`` for the UUID domains, verbatim id for feat)
    + the module's frozen constants."""

    def test_uuid_domains_take_the_uppercase_type_prefix(self):
        for type_ in ("req", "adr", "sysrs"):
            with self.subTest(type_=type_):
                self.assertEqual(
                    _alias(type_, "0e15c5de-4ac9-4279-aa75-53249a3e43e4"),
                    f"{type_.upper()}-0e15c5de-4ac9-4279-aa75-53249a3e43e4",
                )

    def test_feat_keeps_the_verbatim_id(self):
        self.assertEqual(_alias("feat", "feat-177-list-ref-feat"), "feat-177-list-ref-feat")
        self.assertEqual(_alias("feat", "feat-177"), "feat-177")

    def test_domain_order_constant_matches_all_domains(self):
        # the one constant the import-free module may not import from
        # general.tools._domains -- the drift is pinned here
        from biz.dfch.specmgr.general.tools._domains import ALL_DOMAINS

        self.assertEqual(_DOMAIN_ORDER, ALL_DOMAINS)

    def test_default_max_label_is_forty(self):
        self.assertEqual(DEFAULT_MAX_LABEL, 40)


class TestRendererGoldens(unittest.TestCase):
    """The pure-renderer unit goldens over hand-built graphs (ACC-001's renderer half)."""

    def test_section_2_9_worked_example_byte_for_byte(self):
        # the anchor: the rulebook §2.9 worked example, rendered at
        # max_label=42 (the example's 42-char feat label is the exactly-N
        # no-op case; at the default 40 that label truncates, so the
        # example is the N=42 rendering of its own fact collection)
        self.assertEqual(len(_FEAT_H1), 42)
        self.assertEqual(render_reference_graph(_SECTION_2_9, max_label=42), _golden("renderer-section-2-9.puml"))

    def test_section_2_9_matches_the_rulebook_and_the_phase_100_gate_subset(self):
        # cross-drift pins: the anchor golden equals the rulebook §2.9 worked
        # example verbatim AND the Phase 100 real-parser gate's
        # _EMITTED_SUBSET (the three copies must never diverge)
        golden = _golden("renderer-section-2-9.puml")
        rulebook = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "biz"
            / "dfch"
            / "specmgr"
            / "general"
            / "data"
            / "general_reference_graph.md"
        ).read_text(encoding="utf-8")
        match = re.search(r"```plantuml\n(.*?)```", rulebook.split("### 2.9 Worked example")[1], re.S)
        assert match is not None, "the rulebook §2.9 worked-example plantuml block moved"
        self.assertEqual(golden, match.group(1))
        gate = (Path(__file__).resolve().parents[2] / "plantuml" / "test_reference_graph_subset.py").read_text(
            encoding="utf-8"
        )
        match = re.search(r'_EMITTED_SUBSET = """\\\n(.*?)"""', gate, re.S)
        assert match is not None, "the Phase 100 gate _EMITTED_SUBSET block moved"
        self.assertEqual(golden, match.group(1))

    def test_scc_characterization_golden(self):
        self.assertEqual(render_reference_graph(_scc_graph()), _golden("renderer-scc.puml"))

    def test_scc_red_edge_set(self):
        # the §4.1 characterization over the same hand-built graph: red iff a
        # self-loop or both endpoints in the same SCC of size ≥ 2
        graph = _scc_graph()
        edges = {(e.source_type, e.source_id, e.target_type, e.target_id) for e in graph.edges}
        on_cycle = _on_cycle_edges(sorted({(n.type, n.id) for n in graph.nodes}), edges)
        self.assertEqual(
            on_cycle,
            {
                ("req", _S1, "req", _S2),  # 3-cycle
                ("req", _S2, "req", _S3),  # 3-cycle
                ("req", _S3, "req", _S1),  # 3-cycle
                ("req", _S2, "req", _S2),  # self-loop
                ("uc", _S4, "uc", _S5),  # 2-cycle
                ("uc", _S5, "uc", _S4),  # 2-cycle
            },
        )
        self.assertNotIn(("req", _S3, "uc", _S4), on_cycle)  # off-cycle edge between SCC neighbours
        self.assertNotIn(("req", _S1, "dec", _S7), on_cycle)  # edge to an unresolved node

    def test_single_node_zero_edges_golden(self):
        graph = ReferenceGraph(title="Single Node", nodes=(GraphNode("req", _S1, "Single Node"),), edges=())
        self.assertEqual(render_reference_graph(graph), _golden("renderer-single-node.puml"))

    def test_truncation_default_golden(self):
        self.assertEqual(
            render_reference_graph(_truncation_graph(DEFAULT_MAX_LABEL)), _golden("renderer-truncation-default.puml")
        )

    def test_truncation_custom_golden(self):
        self.assertEqual(
            render_reference_graph(_truncation_graph(12), max_label=12), _golden("renderer-truncation-custom.puml")
        )

    def test_title_sanitised_golden(self):
        graph = ReferenceGraph(
            title='He said "hello"\nsecond line',
            nodes=(GraphNode("req", _S1, 'A "quoted" title'),),
            edges=(),
        )
        self.assertEqual(render_reference_graph(graph), _golden("renderer-title-sanitised.puml"))

    def test_title_never_truncated(self):
        # §2.2: even a scoped H1 longer than max_label stays whole on the
        # @startuml line (the node labels below it truncate)
        long_title = "Truncation Default Title With Far More Than Forty Characters"  # 60 chars
        graph = ReferenceGraph(title=long_title, nodes=(GraphNode("req", _S1, long_title),), edges=())
        rendered = render_reference_graph(graph)
        self.assertTrue(rendered.startswith(f"@startuml {long_title}\n"))
        self.assertIn('component "Truncation Default Title With Far More…"', rendered)

    def test_duplicate_nodes_dedupe_first_title_wins(self):
        graph = ReferenceGraph(
            title="Dup",
            nodes=(
                GraphNode("req", _S1, "First Title"),
                GraphNode("req", _S1, "Second Title"),
            ),
            edges=(),
        )
        rendered = render_reference_graph(graph)
        self.assertIn(f'component "First Title" as [REQ-{_S1}]', rendered)
        self.assertNotIn("Second Title", rendered)

    def test_edge_endpoint_missing_from_nodes_becomes_unresolved(self):
        graph = ReferenceGraph(
            title="Implicit",
            nodes=(GraphNode("req", _S1, "Source"),),
            edges=(GraphEdge("req", _S1, "dec", _C),),
        )
        rendered = render_reference_graph(graph)
        self.assertIn(f'component "{_C}" as [DEC-{_C}] <<UNRESOLVED>>', rendered)

    def test_module_is_import_free(self):
        # REQ-001's import-free bar, AST-level (not a text scan: the module's
        # own docstring names ``general.tools`` siblings in prose): every
        # top-level import must be stdlib.
        import ast
        from ast import parse as parse_ast

        source = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "biz"
            / "dfch"
            / "specmgr"
            / "general"
            / "models"
            / "reference_graph.py"
        ).read_text(encoding="utf-8")
        tree = parse_ast(source)
        imported: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                name = (
                    node.module if isinstance(node, ast.ImportFrom) else ", ".join(alias.name for alias in node.names)
                )
                imported.append(name or "")
        self.assertEqual(sorted(imported), ["__future__", "collections.abc", "dataclasses"])


class TestAllGoldensPassTheChecker(unittest.TestCase):
    """ACC-001's last clause over the whole goldens directory: every golden (the pure-renderer
    unit goldens and the builder integration goldens alike) passes the amended structure
    checker in BOTH modes with ZERO findings (errors and warnings), ends with exactly one
    trailing newline after ``@enduml``, and carries no triple blank line."""

    def test_every_golden_is_checker_clean_both_modes(self):
        goldens = sorted(_GOLDENS.glob("*.puml"))
        self.assertGreater(len(goldens), 0)
        for path in goldens:
            text = path.read_text(encoding="utf-8")
            for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
                with self.subTest(golden=path.name, mode=mode):
                    result = check_structure(text, mode)
                    self.assertEqual(result.errors, [], f"{path.name} {mode}: {result.errors}")
                    self.assertEqual(result.warnings, [], f"{path.name} {mode}: {result.warnings}")
            with self.subTest(golden=path.name):
                self.assertTrue(text.endswith("@enduml\n"), path.name)
                self.assertNotIn("\n\n\n", text, path.name)


if __name__ == "__main__":
    unittest.main()
