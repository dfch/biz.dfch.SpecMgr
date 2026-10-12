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

"""Tests for the ``diagram refs`` command (feat-207-reference-graph, Phase 130, ACC-004).

The command is a thin, deterministic-only layer over the Phase 120 tools
``get_reference_diagram`` / ``get_reference_diagram_all`` (imported lazily by
the command — those modules register with the MCP server and so require the
``mcp`` extra) and the Phase 110 library. These tests pin the CLI's own
contract: the rulebook §7 file layout (``<id>.refs.puml`` scoped,
``reference-graph.puml`` registry-wide, under ``--out``, default
``diagrams/refs/`` CWD-relative), byte parity with the committed Phase
110/120 goldens at the frozen default label limit 40, the pinned exit codes
(0 written / no diff, 1 ``--check`` diff — including a missing output file —
or the missing ``mcp`` extra, 2 usage-or-resolution error: a wrong-format
type/id/depth before any file access, a missing source, an
existing-but-broken source with the parse error reported, ``all`` combined
with a source), the ``--check`` no-write property, the flag effects on the
written bytes (``--depth``/``--reverse``/``--no-feat``/``--title``), the
``SPECMGR_DIAGRAM_MAX_TITLE`` env-var effect, and the absence of the
agent-path ``' validated: structure-only`` header (checker-clean by
construction — ``plantuml-check`` works on the files unchanged).

The isolated docs root follows the Phase 110/120 pattern: the shared
``_SeededRegistryTestCase`` base (``SPECMGR_DOCS_DIR``/``SPECMGR_ADR_DIR``/
``SPECMGR_FEAT_DIR`` tmp dirs seeded from the committed fixtures under
``tests/fixtures/reference-graphs/``, every per-domain doc cache reset, the
``SPECMGR_DIAGRAM_MAX_TITLE`` env var guarded to UNSET so the golden
comparisons run at the default label limit), plus a fresh tmp ``--out``
dir (never pre-created) the way ``tests/commands/test_diagram.py`` does.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.general.tools._diagram_config import ENV_VAR_DIAGRAM_MAX_TITLE
from biz.dfch.specmgr.plantuml import chain

from tests.general.tools._reference_graph_helpers import (
    _SeededRegistryTestCase,
    _A001,
    _C001,
    _C002,
    _D001,
    _D002,
    _G001,
    _H001,
    _K001,
    _MISSING_UUID,
    _N001,
    _R001,
    _U001,
    _W001,
    _WG001,
)

runner = CliRunner()

#: The committed fixture seed sets (the same ``(fixture, destination)`` pairs the Phase 110/120
#: tests seed with — the goldens were generated over exactly these registries).
_SEED_CYCLE = (
    ("cycle/req-c001.md", f"docs/req/{_C001}.md"),
    ("cycle/req-c002.md", f"docs/req/{_C002}.md"),
)
_SEED_CHAIN = (
    ("chain/req-h001.md", f"docs/req/{_H001}.md"),
    ("chain/gol-g001.md", f"docs/gol/{_G001}.md"),
    ("chain/rsk-k001.md", f"docs/rsk/{_K001}.md"),
)
_SEED_REVERSE = (
    ("reverse/req-r001.md", f"docs/req/{_R001}.md"),
    ("reverse/dec-d001.md", f"docs/dec/{_D001}.md"),
    ("reverse/feat-42-reverse-feat", "feat/feat-42-reverse-feat"),
)
_SEED_NO_FEAT = (
    ("no-feat/req-n001.md", f"docs/req/{_N001}.md"),
    ("no-feat/feat-7-no-feat", "feat/feat-7-no-feat"),
    ("no-feat/feat-8-no-feat-two", "feat/feat-8-no-feat-two"),
)
_SEED_WIDE = (
    ("wide/req-w001.md", f"docs/req/{_W001}.md"),
    ("wide/uc-u001.md", f"docs/uc/{_U001}.md"),
    ("wide/gol-g001.md", f"docs/gol/{_WG001}.md"),
    ("wide/adr-a001.md", f"adr/{_A001}.md"),
    ("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),
)
_SEED_BROKEN_DEC = (("wide/dec-d002.md", f"docs/dec/dec-{_D002}-broken.md"),)

#: The Phase 120 tool modules the command imports lazily (the ``mcp``-extra dependency).
_TOOL_MODULES = (
    "biz.dfch.specmgr.general.tools.get_reference_diagram",
    "biz.dfch.specmgr.general.tools.get_reference_diagram_all",
)


class _DiagramRefsTestBase(_SeededRegistryTestCase):
    """CLI-specific shared setUp: a fresh tmp ``--out`` dir (never pre-created)."""

    def setUp(self) -> None:
        super().setUp()
        self.out_dir = Path(self.enterContext(tempfile.TemporaryDirectory())) / "diagrams" / "refs"

    def _invoke(self, *args: str) -> mock.MagicMock:
        """One ``specmgr diagram refs ...`` invocation (the full Typer app, like every CLI test)."""
        return runner.invoke(app, ["diagram", "refs", *args])


class TestDiagramRefsScopedWrite(_DiagramRefsTestBase):
    """``diagram refs req <id>`` over the 2-node-cycle registry: exit 0, the §7 file layout, byte
    parity with the Phase 110/120 golden at the default label limit, the ``--check`` contract, and
    no agent-path header."""

    SEEDS = _SEED_CYCLE

    def test_scoped_write_exits_0_and_matches_the_golden(self):
        """ACC-004: a clean write of ``<id>.refs.puml`` — the (never pre-created) parent ``--out``
        dir is created on write, and the content is byte-equal to the corresponding Phase 110/120
        golden at the frozen default limit 40 (the env var is guarded UNSET)."""
        self.assertFalse(self.out_dir.exists())

        result = self._invoke("req", _C001, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("✓ Wrote", result.stdout)
        path = self.out_dir / f"{_C001}.refs.puml"
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_text(encoding="utf-8"), self._golden("cycle-scoped-depth1.puml"))

    def test_no_structure_only_header_in_the_written_artifact(self):
        """The written artifact carries no ``' validated: structure-only`` header (checker-clean by
        construction — the ``diagram uc`` deterministic-artifact precedent)."""
        result = self._invoke("req", _C001, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertNotIn("validated: structure-only", (self.out_dir / f"{_C001}.refs.puml").read_text(encoding="utf-8"))

    def test_check_green_then_red_after_mutation(self):
        """ACC-004: ``--check`` on the just-written file → exit 0 (no diff); after mutating the
        file → exit 1 naming the differing file."""
        write = self._invoke("req", _C001, "--out", str(self.out_dir))
        self.assertEqual(write.exit_code, 0, write.output)

        green = self._invoke("req", _C001, "--out", str(self.out_dir), "--check")
        self.assertEqual(green.exit_code, 0, green.output)
        self.assertIn("(unchanged)", green.stdout)
        self.assertNotIn("(differs)", green.stdout)

        path = self.out_dir / f"{_C001}.refs.puml"
        path.write_text(path.read_text(encoding="utf-8") + "' drift\n", encoding="utf-8")

        red = self._invoke("req", _C001, "--out", str(self.out_dir), "--check")
        self.assertEqual(red.exit_code, 1, red.output)
        self.assertIn("(differs)", red.stdout)

    def test_check_missing_file_counts_as_differing_and_writes_nothing(self):
        """ACC-004: ``--check`` against an out dir that was never written → exit 1, the file reported
        missing; check mode never creates the directory or writes a file."""
        result = self._invoke("req", _C001, "--out", str(self.out_dir), "--check")

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("(missing)", result.stdout)
        self.assertFalse(self.out_dir.exists())

    def test_default_out_is_cwd_relative_diagrams_refs(self):
        """The default ``--out`` is CWD-relative ``diagrams/refs/`` (rulebook §7 file layout)."""
        cwd = Path(self.enterContext(tempfile.TemporaryDirectory()))
        old_cwd = os.getcwd()
        os.chdir(cwd)
        self.addCleanup(os.chdir, old_cwd)

        result = self._invoke("req", _C001)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue((cwd / "diagrams" / "refs" / f"{_C001}.refs.puml").is_file())


class TestDiagramRefsAllWrite(_DiagramRefsTestBase):
    """``diagram refs all`` over the multi-domain registry: exit 0, ``reference-graph.puml``, byte
    parity with the Phase 110/120 registry golden (the deliberately broken dec is skipped —
    never raised, never a node)."""

    SEEDS = _SEED_WIDE

    def test_all_writes_reference_graph_puml_and_matches_the_golden(self):
        """ACC-004: a clean write of ``reference-graph.puml`` byte-equal to the corresponding
        Phase 110/120 registry golden at the default limit."""
        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        path = self.out_dir / "reference-graph.puml"
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_text(encoding="utf-8"), self._golden("wide-registry-all.puml"))
        self.assertNotIn(_D002, path.read_text(encoding="utf-8"))  # the broken dec is skipped

    def test_all_check_green_then_red_after_mutation(self):
        """ACC-004: the ``--check`` contract in all mode: no diff → 0, a mutation → 1 (differs)."""
        write = self._invoke("all", "--out", str(self.out_dir))
        self.assertEqual(write.exit_code, 0, write.output)

        green = self._invoke("all", "--out", str(self.out_dir), "--check")
        self.assertEqual(green.exit_code, 0, green.output)
        self.assertIn("(unchanged)", green.stdout)

        path = self.out_dir / "reference-graph.puml"
        path.write_text(path.read_text(encoding="utf-8") + "' drift\n", encoding="utf-8")

        red = self._invoke("all", "--out", str(self.out_dir), "--check")
        self.assertEqual(red.exit_code, 1, red.output)
        self.assertIn("(differs)", red.stdout)


class TestDiagramRefsDepth(_DiagramRefsTestBase):
    """The ``--depth`` flag effect on the written bytes (against the goldens)."""

    SEEDS = _SEED_CHAIN

    def test_depth_two_writes_the_depth2_golden(self):
        result = self._invoke("req", _H001, "--depth", "2", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            (self.out_dir / f"{_H001}.refs.puml").read_text(encoding="utf-8"),
            self._golden("chain-scoped-depth2.puml"),
        )


class TestDiagramRefsReverse(_DiagramRefsTestBase):
    """The ``--reverse`` flag effect on the written bytes (against the goldens) + the feat source
    (the full ``feat-NNN-slug`` id in the ``<id>.refs.puml`` filename)."""

    SEEDS = _SEED_REVERSE

    def test_reverse_writes_the_reverse_golden(self):
        result = self._invoke("req", _R001, "--reverse", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            (self.out_dir / f"{_R001}.refs.puml").read_text(encoding="utf-8"),
            self._golden("reverse-scoped-depth1-reverse.puml"),
        )

    def test_depth_two_reverse_writes_the_depth2_reverse_golden(self):
        result = self._invoke("req", _R001, "--depth", "2", "--reverse", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            (self.out_dir / f"{_R001}.refs.puml").read_text(encoding="utf-8"),
            self._golden("reverse-scoped-depth2-reverse.puml"),
        )

    def test_feat_source_writes_the_full_slug_filename(self):
        """The feat source (the full ``feat-NNN-slug`` id) writes ``<id>.refs.puml`` with the
        verbatim id, byte-equal to the Phase 120 tool's own render for the same source."""
        from biz.dfch.specmgr.general.tools.get_reference_diagram import get_reference_diagram

        result = self._invoke("feat", "feat-42-reverse-feat", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        path = self.out_dir / "feat-42-reverse-feat.refs.puml"
        self.assertTrue(path.is_file())
        self.assertEqual(
            path.read_text(encoding="utf-8"), get_reference_diagram(type="feat", id="feat-42-reverse-feat")
        )


class TestDiagramRefsNoFeat(_DiagramRefsTestBase):
    """The ``--no-feat`` flag effect on the written bytes (against the goldens): scoped (the source
    exception) + registry-wide (every FEAT node drops)."""

    SEEDS = _SEED_NO_FEAT

    def test_scoped_no_feat_writes_the_no_feat_golden(self):
        result = self._invoke("req", _N001, "--no-feat", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            (self.out_dir / f"{_N001}.refs.puml").read_text(encoding="utf-8"),
            self._golden("no-feat-scoped-source-no-feat.puml"),
        )

    def test_scoped_feat_source_no_feat_keeps_the_source(self):
        result = self._invoke("feat", "feat-7-no-feat", "--no-feat", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        text = (self.out_dir / "feat-7-no-feat.refs.puml").read_text(encoding="utf-8")
        self.assertEqual(text, self._golden("no-feat-scoped-feat-source-no-feat.puml"))
        self.assertIn("feat-7-no-feat", text)  # the source exception
        self.assertNotIn("feat-8-no-feat-two", text)

    def test_all_writes_the_registry_golden(self):
        result = self._invoke("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            (self.out_dir / "reference-graph.puml").read_text(encoding="utf-8"),
            self._golden("no-feat-registry-all.puml"),
        )

    def test_all_no_feat_writes_the_no_feat_registry_golden(self):
        result = self._invoke("all", "--no-feat", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        text = (self.out_dir / "reference-graph.puml").read_text(encoding="utf-8")
        self.assertEqual(text, self._golden("no-feat-registry-no-feat.puml"))
        self.assertNotIn('package "FEAT"', text)
        self.assertNotIn(": refers to", text)  # every edge touched a dropped feat node


class TestDiagramRefsTitleOverride(_DiagramRefsTestBase):
    """The ``--title`` flag effect on the written bytes: it replaces the diagram title before
    rendering — sanitized (an embedded ``"`` becomes ``#quot;``) but NEVER truncated, even past
    the label limit; the node labels still truncate at the default 40."""

    SEEDS = _SEED_CHAIN

    def test_a_long_title_stays_whole_on_the_startuml_line(self):
        long_title = "A very long custom diagram title well over forty characters long"
        self.assertGreater(len(long_title), 40)

        result = self._invoke("req", _H001, "--title", long_title, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        text = (self.out_dir / f"{_H001}.refs.puml").read_text(encoding="utf-8")
        self.assertTrue(text.startswith(f"@startuml {long_title}\n"))  # not truncated
        self.assertIn(f'component "Chain Top Requirement With A Very Long…" as [REQ-{_H001}]', text)

    def test_an_embedded_quote_is_sanitised(self):
        result = self._invoke("req", _H001, "--title", 'Say "hello"', "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        text = (self.out_dir / f"{_H001}.refs.puml").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("@startuml Say #quot;hello#quot;\n"))

    def test_all_title_override_replaces_the_default(self):
        result = self._invoke("all", "--title", "My Registry", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        text = (self.out_dir / "reference-graph.puml").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("@startuml My Registry\n"))
        self.assertNotIn("Reference Graph", text)  # the default is replaced


class TestDiagramRefsEnvVar(_DiagramRefsTestBase):
    """The ``SPECMGR_DIAGRAM_MAX_TITLE`` env-var effect on the written bytes (guarded UNSET by the
    shared base): a valid custom value truncates the written labels (word-boundary cut + ``…``,
    the title untouched), a set-but-invalid value falls back to the default 40 (the golden
    again)."""

    SEEDS = _SEED_CHAIN

    def test_a_custom_limit_truncates_the_written_labels(self):
        with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: "8"}):
            result = self._invoke("req", _H001, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        text = (self.out_dir / f"{_H001}.refs.puml").read_text(encoding="utf-8")
        self.assertIn(f'component "Chain…" as [REQ-{_H001}]', text)  # word-boundary cut at 8
        self.assertTrue(text.startswith("@startuml Chain Top Requirement With A Very Long Title\n"))

    def test_a_set_but_invalid_limit_falls_back_to_the_default_40(self):
        for value in ("", "abc", "0"):
            with self.subTest(value=value):
                with mock.patch.dict("os.environ", {ENV_VAR_DIAGRAM_MAX_TITLE: value}):
                    result = self._invoke("req", _H001, "--out", str(self.out_dir))

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertEqual(
                    (self.out_dir / f"{_H001}.refs.puml").read_text(encoding="utf-8"),
                    self._golden("chain-scoped-depth1.puml"),  # the default-40 golden
                )


class TestDiagramRefsUsageAndResolutionErrors(_DiagramRefsTestBase):
    """The exit-2 channels of ACC-004: a wrong-format type/id/depth (before any file access), a
    missing source, ``all`` combined with a source, and a scoped call without an id — none of
    these creates the out dir or writes a file."""

    SEEDS = _SEED_CYCLE

    def test_no_type_is_a_usage_error(self):
        """Zero arguments (the required ``type`` positional is missing) → the Typer usage error,
        exit 2, no out dir."""
        result = self._invoke("--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertFalse(self.out_dir.exists())

    def test_all_combined_with_a_source_exits_2(self):
        """``all`` alongside a source is a usage error (the literal selects the registry-wide graph
        on its own) — before the lazy import and before any file access."""
        result = self._invoke("all", _C001, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("all", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_scoped_without_an_id_exits_2(self):
        result = self._invoke("req", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertFalse(self.out_dir.exists())

    def test_an_unknown_type_exits_2_before_any_file_access(self):
        """A type outside the 13-domain vocabulary → exit 2 (the ``validate_id`` unknown-type
        channel, before any file access), naming the offending value."""
        result = self._invoke("bogus", _C001, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("bogus", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_a_wrong_format_id_exits_2_before_any_file_access(self):
        """A traversal id and a ``feat-NNN-slug`` for a UUID domain → exit 2 (the ``_path_safety``
        guards, before any file access), no out dir."""
        for bad_id in ("../escape", "feat-36-delete", ""):
            with self.subTest(bad_id=bad_id):
                result = self._invoke("req", bad_id, "--out", str(self.out_dir))

                self.assertEqual(result.exit_code, 2, result.output)
                self.assertFalse(self.out_dir.exists())

    def test_a_bare_feat_id_exits_2_for_the_feat_source(self):
        """A bare ``feat-NNN`` is a wrong-format id, not a normalization candidate (the
        ``get_feat``/``list_references`` parity; the help points at ``list_feat``)."""
        result = self._invoke("feat", "feat-42", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("feat-42", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_a_uuid_exits_2_for_the_feat_source(self):
        result = self._invoke("feat", _MISSING_UUID, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertFalse(self.out_dir.exists())

    def test_depth_out_of_range_exits_2(self):
        """``--depth 0`` / ``--depth 6`` → exit 2 (the tool's own ``depth`` 1..5 guard), no out dir."""
        for bad_depth in ("0", "6"):
            with self.subTest(bad_depth=bad_depth):
                result = self._invoke("req", _C001, "--depth", bad_depth, "--out", str(self.out_dir))

                self.assertEqual(result.exit_code, 2, result.output)
                self.assertIn("depth", result.output)
                self.assertFalse(self.out_dir.exists())

    def test_a_non_int_depth_is_a_typer_usage_error(self):
        result = self._invoke("req", _C001, "--depth", "abc", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertFalse(self.out_dir.exists())

    def test_a_missing_source_exits_2_naming_the_id(self):
        """A well-formed source id with no file on disk → exit 2 (the source domain's own
        not-found message is reported), no out dir."""
        result = self._invoke("req", _MISSING_UUID, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(_MISSING_UUID, result.output)
        self.assertFalse(self.out_dir.exists())


class TestDiagramRefsBrokenSource(_DiagramRefsTestBase):
    """The broken-source exit-2 channel: an existing-but-broken source document → exit 2 with the
    parse error reported (the CLI has no ``ParseFailureResult``-return concept — the ``diagram uc``
    render-error shape: the file is named, the error is surfaced), no out dir."""

    SEEDS = _SEED_BROKEN_DEC

    def test_a_broken_source_exits_2_and_reports_the_parse_error(self):
        result = self._invoke("dec", _D002, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(_D002, result.output)
        self.assertIn("fails to parse (render error)", result.output)
        self.assertIn(f"dec-{_D002}-broken.md", result.output)  # the resolved path names the file
        self.assertFalse(self.out_dir.exists())


class TestDiagramRefsMissingMcpExtra(_DiagramRefsTestBase):
    """The lazy import of the Phase 120 tools requires the ``mcp`` extra: missing → exit 1 with the
    install hint (the ``commands/mcp.py`` precedent) in both modes, nothing written."""

    SEEDS = _SEED_CYCLE

    def _invoke_without_extra(self, *args: str) -> mock.MagicMock:
        """One invocation with the Phase 120 tool modules blocked (``None`` in ``sys.modules`` →
        ``ImportError`` — the ``test_unused_code`` missing-extra idiom)."""
        with mock.patch.dict(sys.modules, dict.fromkeys(_TOOL_MODULES, None)):
            return self._invoke(*args)

    def test_scoped_missing_extra_exits_1(self):
        result = self._invoke_without_extra("req", _C001, "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("must install", result.output)
        self.assertIn("`mcp` extra", result.output)
        self.assertFalse(self.out_dir.exists())

    def test_all_missing_extra_exits_1(self):
        result = self._invoke_without_extra("all", "--out", str(self.out_dir))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("must install", result.output)
        self.assertIn("`mcp` extra", result.output)
        self.assertFalse(self.out_dir.exists())


class TestDiagramRefsPlantumlCheck(_DiagramRefsTestBase):
    """``specmgr plantuml-check`` on a written file: the all-unset structure-only floor (exit 0,
    ``checked_by=structure``) — the written artifact is checker-clean by construction and the
    checker works on the file unchanged (REQ-009's ``plantuml-check``/``plantuml-encode`` clause)."""

    SEEDS = _SEED_CYCLE

    _SOURCE_VARS = (chain.ENV_VAR_JAR, chain.ENV_VAR_BIN, chain.ENV_VAR_URL)

    def setUp(self) -> None:
        super().setUp()
        # The three plantuml source vars are deleted for the whole class (the gitignored root
        # ``.env`` is loaded by ``cli.py`` at import time, so the deletion must be explicit —
        # the ``test_plantuml_check`` precedent); the memoised canary probe caches are cleared
        # on the way in and out.
        self._saved = {var: os.environ.get(var) for var in self._SOURCE_VARS}
        for var in self._SOURCE_VARS:
            os.environ.pop(var, None)
        chain.clear_probe_caches()
        self.addCleanup(self._restore_source_vars)
        self.addCleanup(chain.clear_probe_caches)

    def _restore_source_vars(self) -> None:
        for var, value in self._saved.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    def test_written_file_is_structure_clean_at_the_all_unset_floor(self):
        write = self._invoke("req", _C001, "--out", str(self.out_dir))
        self.assertEqual(write.exit_code, 0, write.output)

        result = runner.invoke(app, ["plantuml-check", str(self.out_dir / f"{_C001}.refs.puml")])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("checked_by=structure", result.stdout)
        self.assertIn("valid=not-run", result.stdout)
        self.assertIn("source_state=none", result.stdout)


if __name__ == "__main__":
    unittest.main()
