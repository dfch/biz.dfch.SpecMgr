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

"""Tests for the ``get_reference_diagram_all`` MCP tool (feat-207-reference-graph, Phase 120, Task 120.150,
ACC-003/REQ-005).

The registry-wide tool's own contract over the Phase 110 library: the
byte-stable return over the Phase 110 seeded registries (the env var
UNSET in the test process, guarded by the shared
``_SeededRegistryTestCase`` base, so ``max_label`` is the frozen default
40 -- the output equals the committed registry goldens), the
frozen ``Reference Graph`` default title, the ``title`` override
(sanitized but never truncated), the ``include_feat`` switch, the
never-raises-for-content property (a registry carrying a deliberately
broken document still renders -- the broken document is simply absent),
and checker-clean over the tool's actual return in both structure modes
with zero findings (the full path end-to-end: tool → ``str`` →
``check_structure``).

There are no id guards (there is no id), so no path-safety class: the
tool's only inputs are the ``include_feat`` switch and the optional
``title`` override.
"""

from __future__ import annotations

import unittest
from unittest import mock

from biz.dfch.specmgr.general.tools._diagram_config import ENV_VAR_DIAGRAM_MAX_TITLE
from biz.dfch.specmgr.general.tools.get_reference_diagram_all import get_reference_diagram_all
from biz.dfch.specmgr.plantuml.structure import MODE_PREFLIGHT, MODE_STANDALONE, check_structure

from ._reference_graph_helpers import (
    _SeededRegistryTestCase,
    _A001,
    _C001,
    _D002,
    _N001,
    _U001,
    _W001,
    _WG001,
)


def _checker_clean(text: str) -> None:
    """Assert ``text`` passes the structure checker in BOTH modes with zero findings (errors and warnings)."""
    for mode in (MODE_PREFLIGHT, MODE_STANDALONE):
        result = check_structure(text, mode)
        assert result.errors == [], (mode, result.errors)
        assert result.warnings == [], (mode, result.warnings)


class TestWideRegistryAllTool(_SeededRegistryTestCase):
    """The registry-wide tool over the multi-domain registry (the never-cached adr leg included,
    a deliberately broken dec present): byte-stable return, the frozen default title,
    checker-clean over the tool's actual return -- and the never-raises-for-content property
    (the broken dec is skipped, its id and title absent from the diagram)."""

    SEEDS = (
        ("wide/req-w001.md", f"docs/req/{_W001}.md"),
        ("wide/uc-u001.md", f"docs/uc/{_U001}.md"),
        ("wide/gol-g001.md", f"docs/gol/{_WG001}.md"),
        ("wide/adr-a001.md", f"adr/{_A001}.md"),
        ("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),
    )

    def test_registry_all_golden(self):
        result = get_reference_diagram_all()
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("wide-registry-all.puml"))
        _checker_clean(result)

    def test_the_default_title_is_reference_graph(self):
        result = get_reference_diagram_all()
        self.assertTrue(result.startswith("@startuml Reference Graph\n"))

    def test_the_broken_document_is_skipped_and_never_raises(self):
        """REQ-005/ACC-003: a registry carrying a deliberately broken document still renders --
        the broken document is never a node, never an edge source, and the call never raises."""
        result = get_reference_diagram_all()
        self.assertIsInstance(result, str)
        self.assertNotIn(_D002, result)  # never a node (no alias, no verbatim-id label)
        self.assertNotIn("Broken Decision", result)
        self.assertNotIn(f"[DEC-{_D002}]", result)  # never an edge source

    def test_the_adr_leg_is_carried(self):
        """The never-cached adr leg (ADR bfd76370): the ADR document is a node and its reference
        an edge in the registry-wide diagram too."""
        result = get_reference_diagram_all()
        self.assertIn('package "ADR"', result)
        self.assertIn(f"[ADR-{_A001}] --> [REQ-{_W001}] : refers to", result)


class TestNoFeatRegistryAllTool(_SeededRegistryTestCase):
    """The registry-wide tool's ``include_feat`` switch over the feat registry: the default
    keeps the feat nodes, ``include_feat=False`` drops every FEAT node and every edge touching a
    dropped node (the feat target must not appear as a node or an edge)."""

    SEEDS = (
        ("no-feat/req-n001.md", f"docs/req/{_N001}.md"),
        ("no-feat/feat-7-no-feat", "feat/feat-7-no-feat"),
        ("no-feat/feat-8-no-feat-two", "feat/feat-8-no-feat-two"),
    )

    def test_registry_all_golden(self):
        result = get_reference_diagram_all()
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("no-feat-registry-all.puml"))
        _checker_clean(result)

    def test_registry_all_no_feat_golden(self):
        result = get_reference_diagram_all(include_feat=False)
        self.assertIsInstance(result, str)
        self.assertEqual(result, self._golden("no-feat-registry-no-feat.puml"))
        self.assertNotIn('package "FEAT"', result)
        self.assertNotIn("feat-7-no-feat", result)
        self.assertNotIn("feat-8-no-feat-two", result)
        self.assertNotIn(": refers to", result)  # every edge touched a dropped feat node


class TestGetReferenceDiagramAllTitleOverride(_SeededRegistryTestCase):
    """The ``title`` override: it replaces the frozen ``Reference Graph`` default before
    rendering -- sanitized (an embedded ``"`` becomes ``#quot;``) but NEVER truncated, even past
    the label limit; the node labels still truncate at the default 40."""

    SEEDS = (("cycle/req-c001.md", f"docs/req/{_C001}.md"),)

    def test_a_long_title_stays_whole_on_the_startuml_line(self):
        long_title = "A very long registry-wide diagram title well over forty characters"
        self.assertGreater(len(long_title), 40)

        result = get_reference_diagram_all(title=long_title)

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith(f"@startuml {long_title}\n"))  # not truncated
        self.assertNotIn("Reference Graph", result)  # the default is replaced
        self.assertIn(f"[REQ-{_C001}]", result)  # the graph content is unchanged

    def test_an_embedded_quote_is_sanitised(self):
        result = get_reference_diagram_all(title='The "Whole" Registry')

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("@startuml The #quot;Whole#quot; Registry\n"))


class TestGetReferenceDiagramAllEnvVar(_SeededRegistryTestCase):
    """The tool reads ``SPECMGR_DIAGRAM_MAX_TITLE`` via the shared helper: a valid custom value
    truncates the node labels at it, and a set-but-invalid value falls back to the default 40
    (the golden again)."""

    SEEDS = (
        ("no-feat/req-n001.md", f"docs/req/{_N001}.md"),
        ("no-feat/feat-7-no-feat", "feat/feat-7-no-feat"),
        ("no-feat/feat-8-no-feat-two", "feat/feat-8-no-feat-two"),
    )

    def test_a_set_but_invalid_limit_falls_back_to_the_default_40(self):
        for value in ("", "abc", "0"):
            with self.subTest(value=value):
                with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: value}):
                    result = get_reference_diagram_all()
                self.assertEqual(result, self._golden("no-feat-registry-all.puml"))  # the default-40 golden

    def test_a_custom_limit_truncates_the_labels(self):
        with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: "6"}):
            result = get_reference_diagram_all()

        self.assertIsInstance(result, str)
        # the 14-char "No Feat Source" label truncates at 6 (word-boundary cut + "…")
        self.assertIn('component "No…" as [REQ-{id}]'.replace("{id}", _N001), result)
        self.assertTrue(result.startswith("@startuml Reference Graph\n"))  # the title is untouched


if __name__ == "__main__":
    unittest.main()
