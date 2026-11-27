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

"""Tests for the ``lint`` command (feat-218, Phase 110).

The command is the in-tree spec artifact parseability gate (REQ-001
through REQ-008): the model-level FULL parse of each document's own
domain, every unparseable document reported (file + error + the
per-type repair pointer), one summary per invocation, and the pinned
exit codes 0/1/2. These tests pin its CLI contract against temporary
directories only (the in-tree corpus is never mutated) plus the
static and drift pins that keep the command import-safe and derived:

* Task 110.100 -- path-layout inference, the ``--type`` override,
  ``--skip-unrecognized`` (skipped and counted, ``feat/<id>/README.md``
  always linted), and the exit-2 usage errors.
* Task 110.110 -- the negative pins (the feat-214-shape dated-bullet
  fixture built from the packaged feat template and a broken ``req``
  document) and the healthy fixtures (every whole-body domain's
  packaged ``get_<d>_example`` data, each first verified to parse with
  its own model-level parser), with the per-type repair pointer (the
  derived id -- lowercased for the UUID-shaped types, the folder name
  for feat -- and the id-less fallback).
* Task 110.120 -- environment behaviour: path mode independent of
  ``SPECMGR_*_DIR``, sweep mode honoring them, ``--dir`` overriding,
  the all-sweep finding zero documents exiting 2, a
  registered-but-empty ``--type`` domain exiting 0 with a 0-document
  summary, and a path run in which every path is skipped exiting 0
  with a 0-linted summary.
* Task 110.130 -- the drift pins: the runtime ``--type`` acceptance
  set equals the registry's ``ALL_DOMAINS`` (never a hand-listed
  set), ``commands/lint.py``'s module level carries no import of the
  registry or any tools package (AST pin plus a real import with
  ``mcp`` blocked, loading the module from its own file to bypass the
  package's ``__init__`` per Task 100.100's finding), and the
  canonical anchored hook file pattern (the one the pre-commit hook
  and the CI step share verbatim) matches one representative path
  per ``ALL_DOMAINS`` type and no non-artifact location; when the
  hook or the CI step is present, its pattern must equal that
  constant (the identity assertions run conditionally on the
  hook/step being present, so this module is green from Phase 110
  and becomes a hard pin automatically once Phases 120/130 land).
* Task 110.140 -- REQ-003 (full parses, never the ``DocCache``/
  ``list_<d>`` path: the feat-214 defect the dirty stage reports
  healthy is reported failed, and a cache patched to explode on any
  read/peek use cannot affect the command) and REQ-011 (no sweep
  invocation of the command in the hook, the CI workflow, or the
  test suite).
 * feat-245 Phase 120 (Tasks 120.100-120.120) -- the sharded layout
   gate (REQ-006/ACC-005): the valid sharded shape lints clean (EN and
   a table-closed variant), the four misplaced depths are layout
   violations (exit 2, the correct path named -- concrete for a uuid-
   carrying file name, shape-level otherwise -- the summary's own
   ``layout`` counter, never parsed, the ``--type`` override does not
   rescue, the violation outranks a parse failure), the no-table
   language dir is placement-valid (the existing no-table content
   error, exit 1), the non-domain-dir skip at every depth (pinned
   against the repo's real ``docs/archive/`` tree), and the
   ``_derive_id``/repair-pointer pins on sharded paths; the anchored
   artifact pattern constant is the open-depth form (every misplaced
   depth and the non-domain dirs selected, the identity pins against
   the pre-commit hook and the CI step unchanged); the three
   flat-seeded sweep tests are re-seeded to the sharded layout.
 * feat-245 Phase 150 (Task 150.155, user decision I1=B) -- the
   type/all sweep's all-language coverage for the thirteen sharded
   domains: a healthy EN doc + a healthy table-closed ``de/`` variant
   both lint (count 2, exit 0), a broken ``de/`` variant is a sweep
   parse failure (exit 1 -- the sweep is not language-blind), a
   single EN doc is counted exactly once (the union's dedup
   semantics, the 6e90d3de double-count defect class), and a
   misplaced flat variant directly inside a language dir stays
   invisible to the sweep (shard-only; the placement gate remains
   path mode's job).
"""

from __future__ import annotations

import ast
import contextlib
import importlib
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from click.testing import Result
from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.feat.tools._cache import read_feat_dirty
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.general.models.heading_table import load_heading_table
from biz.dfch.specmgr.general.tools._doc_cache import DocCache
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._domains import (
    ALL_DOMAINS,
    FEAT,
    UUID_DOMAINS,
    WHOLE_BODY_DOMAINS,
    whole_body_domain,
)
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text

runner = CliRunner()

#: The repository root (this file lives at ``tests/commands/test_lint.py``).
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The lint command's own source file (the subject of the AST and
#: import-safety pins).
_LINT_PY = _REPO_ROOT / "src" / "biz" / "dfch" / "specmgr" / "commands" / "lint.py"

#: The canonical anchored in-tree artifact file pattern the pre-commit hook
#:(feat-218) and the CI pull-request step (feat-218) both use verbatim (one
#: shared pattern, the lint command's own derived type list deciding which
#: matched files are artifacts). feat-245 Phase 120 (REQ-006): the docs part
#: is an OPEN-DEPTH match under ``docs/<dir>/`` (any ``.md`` one or more
#: levels below) so the sharded valid shape AND every misplaced depth are
#: selected for the lint command's placement validator, and non-domain dirs
#: (``docs/archive/adr/x.md`` at depth >= 3, ``docs/api/x/y.md``) are
#: selected and then skipped by the command (exit 0, counted).
_HOOK_FILE_PATTERN = r"^(\.specmgr/feat/[^/]+/README\.md|docs/[^/]+/.+\.md)$"

#: The command name and the two sweep flags, each built from parts so this
#: file's own source never carries a contiguous command-name-plus-flag line
#: that the REQ-011 scan (:class:`TestLintNoSweepOnCommitPath`) would flag.
_LINT_CMD = "specmgr " + "lint"
_SWEEP_FLAGS = ("--" + "all", "--" + "type")


def _line_carries_sweep_flag(line: str) -> bool:
    """True when a sweep flag occurs on ``line`` as a STANDALONE flag token.

    Word-boundary match, not substring (Phase 130 fix): the CI step's
    mandated invocation line carries ``--all-extras`` (mandatory for the
    mcp extra) directly next to the command name, and a substring scan
    would flag it as a sweep invocation -- the false positive this pin
    exists for. A standalone ``--all`` or ``--type`` (not followed by
    ``-`` or a word character) still counts.
    """
    return any(re.search(flag + r"(?![\w-])", line) for flag in _SWEEP_FLAGS)


def _logical_lines(text: str) -> list[tuple[int, str]]:
    """The physical lines of ``text`` folded at shell-style continuations.

    A physical line whose last character is a backslash is joined with the
    next physical line (the backslash is dropped, a single space inserted),
    so an invocation split across lines by trailing-backslash continuations
    is scanned as the single logical line the shell executes it as (Phase
    160, I4: before the fold, a continuation-split invocation -- the command
    on line N ending in a backslash, a sweep flag on line N+1 -- escaped the
    per-physical-line command-name-plus-flag check). Each logical line
    reports the 1-based number of the FIRST physical line it starts on, so a
    violation's file:line points at the line a reader sees the invocation
    begin on.
    """
    lines = text.splitlines()
    result: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        start = index
        logical = lines[index]
        while logical.endswith("\\") and index + 1 < len(lines):
            logical = logical[:-1] + " " + lines[index + 1]
            index += 1
        result.append((start + 1, logical))
        index += 1
    return result


def _healthy_whole_body_text(doc_type: str) -> str:
    """One healthy document of the whole-body domain ``doc_type``.

    The packaged ``get_<d>_example`` data (the exact file the domain's own
    ``get_<d>_example`` tool reads), verified to parse with the domain's own
    model-level parser before it is handed to a test (the plan: "each first
    verified to parse").
    """
    text = read_packaged_text(doc_type, "example")
    whole_body_domain(doc_type).parse_text(text)
    return text


def _feat214_shaped_text() -> str:
    """The feat-214 failure shape: the packaged feat template (itself valid)
    with its one ``Decisions Made`` H4 date entry authored as a dated BULLET
    line, which the schema's H4 date-entry form rejects (a body-level defect
    the dirty stage never sees)."""
    template = read_packaged_text(FEAT, "template")
    whole_body_domain(FEAT).parse_text(template)
    broken = template.replace(
        "#### 2025-06-14 19:22:53.667Z - Placeholder decision",
        "- 2025-06-14 19:22:53.667Z - Placeholder decision",
        1,
    )
    assert broken != template
    return broken


def _broken_req_text() -> str:
    """A ``req`` document broken at the body level: the packaged example with
    its mandatory ``## Characteristics`` heading renamed, which the
    model-level parser rejects."""
    text = read_packaged_text("req", "example")
    broken = text.replace("## Characteristics", "## Bogus", 1)
    assert broken != text
    return broken


def _de_variant_text(doc_type: str) -> str:
    """The table-closed ``de`` variant of the packaged healthy document: every fixed-text
    heading translated into German via the packaged ``de.json`` table's reverse direction
    (fence-aware -- the same helper shape ``tests/general/tools/test_i18n_all_domains.py``
    uses). Data-carrying headings hold no table entry and stay byte-identical; prose and
    frontmatter are never touched (REQ-010)."""
    reverse = {canonical: translated for translated, canonical in load_heading_table("de").items()}
    pattern = re.compile(r"^(#{1,6}) (.*)$")
    out: list[str] = []
    in_fence = False
    for line in _healthy_whole_body_text(doc_type).split("\n"):
        if re.match(r"^(```|~~~)", line):
            in_fence = not in_fence
        match = pattern.match(line)
        if match and not in_fence and match.group(2) in reverse:
            out.append(f"{match.group(1)} {reverse[match.group(2)]}")
        else:
            out.append(line)
    return "\n".join(out)


def _hook_files_pattern(text: str) -> str | None:
    """The spec ``files:`` pattern of the ``specmgr-lint`` hook block in a
    ``.pre-commit-config.yaml`` text, or ``None`` when no such hook is present.

    An empty string means the hook IS present but carries no ``files:`` line
    (a defect the caller must fail on).
    """
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip().startswith("- id: specmgr-lint"):
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^\s*- id:", lines[index]):
            end = index
            break
    for line in lines[start + 1 : end]:
        stripped = line.strip()
        if stripped.startswith("files:"):
            value = stripped.split("files:", 1)[1].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            return value
    return ""


class _LintTestBase(unittest.TestCase):
    """Shared setup: one per-test temporary directory (the in-tree corpus is never mutated)."""

    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def _write(self, rel_path: str, text: str) -> Path:
        path = self.tmp / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def _invoke(self, *args: str) -> Result:
        result = runner.invoke(app, ["lint", *args])
        return result


class TestLintPathInference(_LintTestBase):
    """Task 110.100: the per-path type inference from the layout alone, the ``--type`` override
    (which also rescues a nonstandard layout), and ``--skip-unrecognized`` (skipped and counted,
    never changing the exit code of an otherwise healthy run)."""

    def test_containing_directory_named_after_a_type_is_inferred(self):
        path = self._write("req/healthy.md", _healthy_whole_body_text("req"))

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0", result.stdout)

    def test_feat_folder_shape_is_inferred(self):
        text = _healthy_whole_body_text(FEAT)
        doc_id = whole_body_domain(FEAT).parse_text(text).frontmatter.id
        path = self._write(f"feat/{doc_id}/README.md", text)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0", result.stdout)

    def test_type_option_overrides_inference(self):
        path = self._write("elsewhere/foo.md", _healthy_whole_body_text("req"))

        result = self._invoke(str(path), "--type", "req")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0", result.stdout)

    def test_unrecognized_layout_is_a_usage_error(self):
        path = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("unrecognized layout", result.output)

    def test_unrecognized_layout_is_skipped_and_counted_with_flag(self):
        path = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(path), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=1", result.stdout)

    def test_skip_flag_does_not_change_exit_code_for_a_healthy_run(self):
        healthy = self._write("req/healthy.md", _healthy_whole_body_text("req"))
        unknown = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(healthy), str(unknown), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=1", result.stdout)


class TestLintUsageErrors(_LintTestBase):
    """Task 110.100 / REQ-008: the exit-2 usage and resolution errors (reported to stderr with
    the ``error: `` prefix, before any parsing)."""

    def test_no_paths_and_no_sweep_flag_exits_2(self):
        result = self._invoke()

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("error: ", result.output)

    def test_explicit_paths_combined_with_all_flag_exits_2(self):
        path = self._write("req/healthy.md", _healthy_whole_body_text("req"))

        result = self._invoke(str(path), "--all")

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("explicit paths cannot be combined with --all", result.output)

    def test_type_flag_combined_with_all_flag_exits_2(self):
        result = self._invoke("--type", "req", "--all")

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("cannot be combined", result.output)

    def test_dir_without_type_exits_2(self):
        result = self._invoke("--dir", str(self.tmp))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("--dir is only valid together with --type", result.output)

    def test_dir_combined_with_all_flag_exits_2(self):
        """Phase 160 (G3): ``--dir`` combined with ``--all`` is the same shape error as
        ``--dir`` alone (the guard is on ``dir is not None and type is None`` -- ``--all``
        is a sweep flag, not a type), so it exits 2 with the ``--dir is only valid
        together with --type`` message."""
        result = self._invoke("--dir", str(self.tmp), "--all")

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("--dir is only valid together with --type", result.output)

    def test_dir_combined_with_paths_and_type_exits_2(self):
        """Phase 170 (G1): ``--dir`` is valid in sweep mode only (``--type`` WITHOUT explicit
        paths); combined with explicit paths and ``--type`` it was silently ignored before --
        now a usage error, and no file is linted."""
        path = self._write("req/broken.md", _broken_req_text())

        result = self._invoke(str(path), "--type", "req", "--dir", str(self.tmp))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("--dir cannot be combined with explicit paths", result.output)
        self.assertNotIn("summary:", result.output)
        self.assertNotIn(str(path), result.stdout)

    def test_missing_path_exits_2(self):
        result = self._invoke(str(self.tmp / "req" / "nope.md"))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("no such file", result.output)

    def test_unreadable_path_is_a_usage_error(self):
        """A user-named path that exists but cannot be read is REQ-008's exit-2 ``unreadable or
        missing path`` case (in contrast to a sweep-enumerated unreadable file: that is a
        per-file parse failure, exit 1 -- pinned in :class:`TestLintReadFailures`)."""
        path = self._write("req/healthy.md", _healthy_whole_body_text("req"))
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o644)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("unreadable", result.output)


class TestLintFeat214Shape(_LintTestBase):
    """Task 110.110 / ACC-001: the feat-214 failure shape -- a Decisions Made entry authored as a
    dated bullet line -- fails the gate with the file named, a recognizable error fragment, the
    summary, and the feat repair pointer whose id is the folder name."""

    FEAT_ID = "feat-214-shape"

    def test_dated_bullet_decisions_entry_fails_with_file_error_and_pointer(self):
        path = self._write(f"feat/{self.FEAT_ID}/README.md", _feat214_shaped_text())

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("DecisionsMade", result.stdout)
        self.assertIn("expected list[DecisionEntry]", result.stdout)
        self.assertIn(f"repair via: /repair {FEAT} {self.FEAT_ID}", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0", result.stdout)


class TestLintWholeBodyFailure(_LintTestBase):
    """Task 110.110 / ACC-002: one other whole-body domain (``req``) broken at the body level
    fails with the file named and a recognizable error fragment; the repair pointer pins the id
    derivation -- the file-name UUID printed lowercased (a mixed-case file name), and the
    ``/repair {type}`` fallback when no id can be derived from the path."""

    def test_broken_req_fails_with_lowercased_uuid_pointer(self):
        example_text = read_packaged_text("req", "example")
        doc_id = whole_body_domain("req").parse_text(example_text).frontmatter.id
        broken = example_text.replace("## Characteristics", "## Bogus", 1)
        assert broken != example_text
        path = self._write(f"req/{doc_id.upper()}.md", broken)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("Requirement > Characteristics", result.stdout)
        self.assertIn(f"repair via: /repair req {doc_id}", result.stdout)
        self.assertNotIn(f"repair via: /repair req {doc_id.upper()}", result.stdout)

    def test_broken_doc_without_uuid_in_name_gets_fallback_pointer(self):
        path = self._write("req/broken-no-uuid.md", _broken_req_text())

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("\n  repair via: /repair req\n", result.stdout)


class TestLintMultiFailureReporting(_LintTestBase):
    """Phase 160 (G1) / REQ-001: EVERY unparseable document is reported, not just the first.
    One invocation over two broken fixtures (a feat-214-shape feature README and a
    body-level broken ``req``) names BOTH files with both their errors and both repair
    pointers, and the summary counts ``failed=2`` -- a regression that stopped reporting
    after the first failure would fail this pin while passing every single-failure test
    in the module (whose summaries all carry ``failed`` of 0 or 1)."""

    def test_two_broken_documents_in_one_run_are_both_reported(self):
        feat_path = self._write("feat/feat-multi-failure/README.md", _feat214_shaped_text())
        req_path = self._write("req/broken-req.md", _broken_req_text())

        result = self._invoke(str(feat_path), str(req_path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(feat_path), result.stdout)
        self.assertIn(str(req_path), result.stdout)
        self.assertIn("DecisionsMade", result.stdout)
        self.assertIn("Requirement > Characteristics", result.stdout)
        self.assertIn("repair via: /repair feat feat-multi-failure", result.stdout)
        self.assertIn("\n  repair via: /repair req\n", result.stdout)
        self.assertIn("summary: linted=2 failed=2 skipped=0", result.stdout)

    def test_report_order_is_decode_failures_first_then_parse_failures(self):
        """Phase 170 (I2, accepted): decode failures (path mode) print before parse failures in
        encounter order, regardless of the command-line argument order."""
        parse_path = self._write("req/broken-req.md", _broken_req_text())
        decode_path = self.tmp / "req" / "bad-encoding.md"
        decode_path.write_bytes(b"\xff\xfe this is not valid utf-8 \x00\x01")

        result = self._invoke(str(parse_path), str(decode_path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(parse_path), result.stdout)
        self.assertIn(str(decode_path), result.stdout)
        self.assertLess(result.stdout.index(str(decode_path)), result.stdout.index(str(parse_path)))
        self.assertIn("summary: linted=2 failed=2 skipped=0", result.stdout)


class TestLintHealthyFixtures(_LintTestBase):
    """Task 110.110 / ACC-002: the healthy fixtures -- every whole-body domain's packaged
    ``get_<d>_example`` data (each first verified to parse with its own model-level parser, and
    written under a layout the command infers from the path alone) -- each exits 0."""

    def test_every_whole_body_example_lints_clean(self):
        for doc_type in WHOLE_BODY_DOMAINS:
            with self.subTest(domain=doc_type):
                text = _healthy_whole_body_text(doc_type)
                doc_id = whole_body_domain(doc_type).parse_text(text).frontmatter.id
                if doc_type == FEAT:
                    path = self._write(f"feat/{doc_id}/README.md", text)
                else:
                    path = self._write(f"{doc_type}/{doc_id}.md", text)

                result = self._invoke(str(path))

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=1 failed=0 skipped=0", result.stdout)


class TestLintReadFailures(_LintTestBase):
    """Task 110.110 (negative pins, REQ-008): a user-named path that exists but fails to decode
    is a per-file parse FAILURE (exit 1, counted in ``linted`` -- Phase 100's decision (3)), a
    sweep-enumerated file that fails to read is a per-file parse failure too (exit 1, in contrast
    to the user-named unreadable path's exit 2) -- with the two sweep read-failure channels
    split (Phase 160, I3): an ``OSError`` prints ``unreadable: ...`` and a
    ``UnicodeDecodeError`` prints ``not valid utf-8: ...``, the same text path mode uses, and a
    feat-typed document whose path is not the ``feat/<id>/README.md`` folder shape gets the
    id-less ``/repair feat`` fallback pointer."""

    def test_decode_failure_is_a_lint_failure_counted_as_linted(self):
        path = self.tmp / "req" / "bad-encoding.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfe this is not valid utf-8 \x00\x01")

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("not valid utf-8", result.stdout)
        self.assertIn("\n  repair via: /repair req\n", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0", result.stdout)

    def test_sweep_enumerated_unreadable_file_is_a_lint_failure(self):
        """feat-245 Phase 120: re-seeded to the sharded layout (the sweep's own
        ``iter_doc_paths`` yields ``<base>/*/*.md`` of the registered ``en/``
        base dir, so a flat ``docsroot/req/`` seed is invisible to it)."""
        docs_root = self.tmp / "docsroot"
        file_path = docs_root / "req" / "en" / "00" / "unreadable.md"
        file_path.parent.mkdir(parents=True)
        file_path.write_text(_broken_req_text(), encoding="utf-8")
        os.chmod(file_path, 0)
        self.addCleanup(os.chmod, file_path, 0o644)

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(docs_root)}):
            result = self._invoke("--type", "req")

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(file_path), result.stdout)
        self.assertIn("unreadable:", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0", result.stdout)

    def test_sweep_enumerated_invalid_utf8_file_is_a_lint_failure(self):
        """Phase 160 (I3): the same decode failure in SWEEP mode prints the same
        ``not valid utf-8`` text path mode does (before the split, sweep printed
        ``unreadable: ...`` for a ``UnicodeDecodeError`` -- asymmetric).
        feat-245 Phase 120: re-seeded to the sharded layout (see the sibling
        unreadable test)."""
        docs_root = self.tmp / "docsroot"
        file_path = docs_root / "req" / "en" / "00" / "bad-encoding.md"
        file_path.parent.mkdir(parents=True)
        file_path.write_bytes(b"\xff\xfe this is not valid utf-8 \x00\x01")

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(docs_root)}):
            result = self._invoke("--type", "req")

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(file_path), result.stdout)
        self.assertIn("not valid utf-8", result.stdout)
        self.assertNotIn("unreadable:", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0", result.stdout)

    def test_feat_typed_non_folder_shape_path_gets_fallback_pointer(self):
        path = self._write("elsewhere/not-a-folder-shape.md", _feat214_shaped_text())

        result = self._invoke(str(path), "--type", FEAT)

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("\n  repair via: /repair feat\n", result.stdout)


class TestLintEnvVars(_LintTestBase):
    """Task 110.120 / ACC-004, ACC-010, ACC-016: path mode is independent of every
    ``SPECMGR_*_DIR`` variable, sweep mode honors them, ``--dir`` overrides, the all-sweep
    finding zero documents in total exits 2 (a registered-but-empty ``--type`` domain exits 0
    with a 0-document summary), and a path run in which every path is skipped exits 0 with a
    0-linted summary."""

    def _empty_env(self) -> dict[str, str]:
        return {
            DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs"),
            FEAT_DIR_ENV_VAR: str(self.tmp / "empty-feat"),
        }

    def test_path_mode_is_unaffected_by_env_vars(self):
        path = self._write("req/healthy.md", _healthy_whole_body_text("req"))

        with mock.patch.dict(os.environ, self._empty_env()):
            result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0", result.stdout)

    def test_sweep_mode_honors_env_vars(self):
        for doc_type, env_var in ((FEAT, FEAT_DIR_ENV_VAR), ("req", DOCS_DIR_ENV_VAR)):
            with self.subTest(domain=doc_type):
                with mock.patch.dict(os.environ, {env_var: str(self.tmp / "empty")}):
                    result = self._invoke("--type", doc_type)

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=0 failed=0 skipped=0", result.stdout)

    def test_dir_overrides_env_var(self):
        """feat-245 Phase 120: the ``--dir`` override seeds the sharded shape (one
        shard dir level below the swept base -- ``iter_doc_paths``' own
        ``<base>/*/*.md`` listing)."""
        example_text = read_packaged_text("req", "example")
        doc_id = whole_body_domain("req").parse_text(example_text).frontmatter.id
        sweep_dir = self.tmp / "sweep"
        (sweep_dir / doc_id[:2]).mkdir(parents=True)
        (sweep_dir / doc_id[:2] / f"{doc_id}.md").write_text(example_text, encoding="utf-8")

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs")}):
            result = self._invoke("--type", "req", "--dir", str(sweep_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0", result.stdout)

    def test_all_with_zero_documents_exits_2(self):
        with mock.patch.dict(os.environ, self._empty_env()):
            result = self._invoke("--all")

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("zero documents", result.output)

    def test_type_uc_with_no_documents_exits_0(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs")}):
            result = self._invoke("--type", "uc")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=0", result.stdout)

    def test_every_path_skipped_exits_0_with_zero_linted(self):
        skipped = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(skipped), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=1", result.stdout)


class TestLintShardedPlacement(_LintTestBase):
    """feat-245 Phase 120 (Task 120.100/120.120) / REQ-006 / ACC-005: the sharded layout
    recognition and the placement validator. The one valid file shape
    ``docs/<type>/<lang>/<2-hex>/<file>.md`` lints clean (a valid EN shard and a valid
    table-closed variant shard); every misplaced depth is a layout violation -- its own
    result class, never a usage error and never a content-parse failure: exit 2, the
    defect and the correct path named (concrete when the file name carries a canonical
    uuid, shape-level otherwise), the file's own repair pointer, the summary's own
    ``layout`` counter, never parsed; a no-table language dir stays placement-valid and
    takes the existing no-table content error (exit 1); the ``--type`` override never
    rescues a misplaced file; and a layout violation outranks a parse failure in the
    same run."""

    DOC_TYPE = "req"

    def _doc_id(self) -> str:
        return whole_body_domain(self.DOC_TYPE).parse_text(read_packaged_text(self.DOC_TYPE, "example")).frontmatter.id

    def _assert_violation(self, rel_path: str, kind: str, correct_path: str) -> None:
        path = self._write(rel_path, _healthy_whole_body_text(self.DOC_TYPE))

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(f"layout violation: {kind}; correct path: {correct_path}", result.stdout)
        self.assertIn("summary: linted=0 failed=0 skipped=0 layout=1", result.stdout)

    def test_valid_en_shard_lints_clean(self):
        doc_id = self._doc_id()
        path = self._write(
            f"docs/{self.DOC_TYPE}/en/{doc_id[:2]}/{doc_id}-sharded.md", _healthy_whole_body_text(self.DOC_TYPE)
        )

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_valid_variant_shard_lints_clean(self):
        """The table-closed ``de`` variant in its own sharded placement parses through the
        de heading table (the path-derived language) and lints clean."""
        doc_id = self._doc_id()
        path = self._write(f"docs/{self.DOC_TYPE}/de/{doc_id[:2]}/{doc_id}-sharded.md", _de_variant_text(self.DOC_TYPE))

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_missing_language_dir_is_a_layout_violation(self):
        self._assert_violation(
            f"docs/{self.DOC_TYPE}/foo.md",
            "missing language directory",
            f"docs/{self.DOC_TYPE}/en/<2-hex-shard>/foo.md",
        )

    def test_missing_language_dir_with_uuid_names_the_concrete_correct_path(self):
        """ACC-005 + the correct-path contract: a file name carrying a canonical uuid gets the
        CONCRETE correct path (shard = the uuid's first two hex digits), and the violation's
        own repair pointer derives that uuid (the ``_derive_id`` pin for sharded placements)."""
        doc_id = self._doc_id()
        file_name = f"{doc_id}-sharded.md"
        path = self._write(f"docs/{self.DOC_TYPE}/{file_name}", _healthy_whole_body_text(self.DOC_TYPE))

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(
            f"layout violation: missing language directory; correct path: docs/{self.DOC_TYPE}/en/{doc_id[:2]}/{file_name}",
            result.stdout,
        )
        self.assertIn(f"repair via: /repair {self.DOC_TYPE} {doc_id}", result.stdout)
        self.assertIn("summary: linted=0 failed=0 skipped=0 layout=1", result.stdout)

    def test_invalid_language_dir_is_a_layout_violation(self):
        """One dir segment that is not a shape-valid two-letter language dir (``Notes``): the
        missing-(valid)-language-dir violation, correct path falling back to ``en``."""
        self._assert_violation(
            f"docs/{self.DOC_TYPE}/Notes/foo.md",
            "missing (valid) language directory",
            f"docs/{self.DOC_TYPE}/en/<2-hex-shard>/foo.md",
        )

    def test_missing_shard_dir_is_a_layout_violation(self):
        """A file directly in a shape-valid language dir: the missing-shard-dir violation."""
        self._assert_violation(
            f"docs/{self.DOC_TYPE}/en/foo.md",
            "missing shard directory",
            f"docs/{self.DOC_TYPE}/en/<2-hex-shard>/foo.md",
        )

    def test_missing_shard_dir_in_a_variant_language_keeps_that_language(self):
        """The correct path keeps the misplaced file's own shape-valid language dir (``de``),
        not the ``en`` fallback."""
        self._assert_violation(
            f"docs/{self.DOC_TYPE}/de/foo.md",
            "missing shard directory",
            f"docs/{self.DOC_TYPE}/de/<2-hex-shard>/foo.md",
        )

    def test_non_hex_shard_is_a_layout_violation(self):
        """ACC-005: the non-hex shard (``zz``) -- a shape-valid LANGUAGE that sits at the
        SHARD level: the placement, not the language, is defective."""
        self._assert_violation(
            f"docs/{self.DOC_TYPE}/en/zz/x.md", "non-hex shard", f"docs/{self.DOC_TYPE}/en/<2-hex-shard>/x.md"
        )

    def test_deeper_than_one_shard_level_is_a_layout_violation(self):
        self._assert_violation(
            f"docs/{self.DOC_TYPE}/en/10/20/x.md",
            "deeper than one shard level",
            f"docs/{self.DOC_TYPE}/en/<2-hex-shard>/x.md",
        )

    def test_no_table_language_dir_is_placement_valid_and_takes_the_no_table_content_error(self):
        """REQ-006: a shape-valid language dir WITHOUT a packaged heading table (``zz``) is
        placement-valid -- the file is PARSED (language-aware) and fails with the table
        loader's existing no-table content error (exit 1, ``failed=1``), never a layout
        violation (``layout=0``)."""
        path = self._write(f"docs/{self.DOC_TYPE}/zz/aa/foo.md", _healthy_whole_body_text(self.DOC_TYPE))

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("no heading-mapping table for language 'zz'", result.stdout)
        self.assertNotIn("layout violation", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 layout=0", result.stdout)
        self.assertIn(f"\n  repair via: /repair {self.DOC_TYPE}\n", result.stdout)

    def test_type_override_does_not_rescue_a_misplaced_file(self):
        """A misplaced ``docs/<type>/`` file is a layout violation even when ``--type`` names
        the parse explicitly: the placement defect stands (the gate's job is to catch the
        invisible document, REQ-006)."""
        path = self._write(f"docs/{self.DOC_TYPE}/foo.md", _healthy_whole_body_text(self.DOC_TYPE))

        result = self._invoke(str(path), "--type", self.DOC_TYPE)

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("layout violation: missing language directory", result.stdout)
        self.assertIn("summary: linted=0 failed=0 skipped=0 layout=1", result.stdout)

    def test_layout_violation_outranks_a_parse_failure_in_the_same_run(self):
        """Both findings are reported (REQ-001 ethos: every failure, not just the first),
        and the run exits 2 (the layout violation outranks the parse failure)."""
        doc_id = self._doc_id()
        misplaced = self._write(f"docs/{self.DOC_TYPE}/foo.md", _healthy_whole_body_text(self.DOC_TYPE))
        broken = self._write(f"docs/{self.DOC_TYPE}/en/{doc_id[:2]}/{doc_id}-sharded.md", _broken_req_text())

        result = self._invoke(str(misplaced), str(broken))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(str(misplaced), result.stdout)
        self.assertIn(str(broken), result.stdout)
        self.assertIn("layout violation: missing language directory", result.stdout)
        self.assertIn("Requirement > Characteristics", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 layout=1", result.stdout)

    def test_repair_pointer_derives_the_uuid_on_a_valid_sharded_path(self):
        """ACC-005 + the ``_derive_id`` pin: on the valid sharded shape the repair pointer
        derives the canonical uuid from the file name (printed lowercased) -- unchanged by
        the shard dirs in between."""
        doc_id = self._doc_id()
        path = self._write(f"docs/{self.DOC_TYPE}/en/{doc_id[:2]}/{doc_id.upper()}-sharded.md", _broken_req_text())

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(f"repair via: /repair {self.DOC_TYPE} {doc_id}", result.stdout)
        self.assertNotIn(f"repair via: /repair {self.DOC_TYPE} {doc_id.upper()}", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 layout=0", result.stdout)

    def test_repair_pointer_falls_back_when_the_sharded_name_carries_no_uuid(self):
        path = self._write(f"docs/{self.DOC_TYPE}/en/aa/foo.md", _broken_req_text())

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(f"\n  repair via: /repair {self.DOC_TYPE}\n", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 layout=0", result.stdout)


class TestLintNonDomainDirSkip(unittest.TestCase):
    """feat-245 Phase 120 (Task 120.120) / REQ-006 / ACC-005: a file anchored under
    ``docs/<dir>/`` where ``<dir>`` is NOT a registered domain keeps the skip behavior at
    every depth -- exit 0, counted in ``skipped``, never parsed, never a layout violation.
    Pinned against the repo's real ``docs/archive/`` tree (real files, depth >= 3:
    ``docs/archive/adr/<uuid>-<slug>.md`` and ``docs/archive/sop/``) plus synthetic depths
    under a temporary docs root (the in-tree corpus is never mutated)."""

    def test_repo_archive_tree_files_skip_clean_at_their_real_depths(self):
        archive = _REPO_ROOT / "docs" / "archive"
        self.assertTrue(archive.is_dir(), "the repo's docs/archive tree must exist for this pin")
        files = sorted(path for path in archive.rglob("*.md") if path.is_file())
        self.assertGreater(len(files), 0, "the repo's docs/archive tree must carry real .md files")
        for path in files:
            with self.subTest(path=str(path.relative_to(_REPO_ROOT))):
                self.assertGreaterEqual(len(path.relative_to(_REPO_ROOT / "docs").parts), 3, "the pin needs depth >= 3")
                result = runner.invoke(app, ["lint", str(path)])
                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=0 failed=0 skipped=1 layout=0", result.stdout)

    def test_synthetic_non_domain_dirs_skip_clean_at_every_depth(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for rel in (
            "docs/archive/x.md",
            "docs/archive/adr/x.md",
            "docs/archive/a/b/x.md",
            "docs/api/x/y.md",
        ):
            with self.subTest(path=rel):
                path = tmp / rel
                path.parent.mkdir(parents=True)
                path.write_text("anything", encoding="utf-8")

                result = runner.invoke(app, ["lint", str(path)])

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=0 failed=0 skipped=1 layout=0", result.stdout)


class TestLintTypeAcceptanceRuntime(_LintTestBase):
    """Task 110.130 / ACC-008: the runtime ``--type`` acceptance set equals the registry's
    ``ALL_DOMAINS`` -- every member is accepted (sweeping an empty ``--dir`` exits 0 with a
    0-document summary) and any other value is a usage error (exit 2). The test iterates the
    registry, never a hand-listed set."""

    def test_every_all_domains_member_is_accepted(self):
        empty_dir = self.tmp / "empty"
        for doc_type in ALL_DOMAINS:
            with self.subTest(domain=doc_type):
                result = self._invoke("--type", doc_type, "--dir", str(empty_dir))

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=0 failed=0 skipped=0", result.stdout)

    def test_non_member_type_exits_2(self):
        result = self._invoke("--type", "no-such-domain", "--dir", str(self.tmp / "empty"))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("unknown --type", result.output)


class TestLintModuleImportSafety(unittest.TestCase):
    """Task 110.130 / ACC-008 / REQ-002: ``commands/lint.py`` stays import-safe in a
    ``[cli]``-only install -- no module-level import of the registry or any tools package (AST
    pin), no hand-listed collection of domain-name literals at module level, and a real import
    with the ``mcp`` extra blocked. The real import loads the module FROM ITS FILE (an
    ``importlib`` spec with the file's own dotted name) so the package's ``__init__`` is bypassed
    -- Task 100.100's finding: the CLI's sibling tangles already require the extra, so only the
    file's own module level can be verified in-process this way."""

    def _module_level_imports(self) -> list[str]:
        """The fully-qualified names of every module ``lint.py`` imports at module level."""
        tree = ast.parse(_LINT_PY.read_text(encoding="utf-8"))
        package_parts = "biz.dfch.specmgr.commands".split(".")
        result: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                result.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0:
                    base: str | None = node.module
                else:
                    base = ".".join(package_parts[: len(package_parts) - (node.level - 1)])
                    if node.module:
                        base = f"{base}.{node.module}"
                result.append(base or "")
        return result

    def test_no_module_level_specmgr_import(self):
        for name in self._module_level_imports():
            if name.startswith("biz.dfch.specmgr"):
                self.fail(
                    f"module-level specmgr import {name!r} in lint.py: the registry and every "
                    "tools package require the mcp extra and must stay inside the lazily "
                    "imported command body",
                )
            else:
                root = name.split(".")[0]
                self.assertIn(
                    root,
                    set(sys.stdlib_module_names) | {"typer", "__future__"},
                    f"unexpected module-level import {name!r} in lint.py",
                )

    def test_no_module_level_collection_of_domain_name_literals(self):
        tree = ast.parse(_LINT_PY.read_text(encoding="utf-8"))
        domain_names = set(ALL_DOMAINS)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                value: Any = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                value = node.value
            else:
                continue
            if not isinstance(value, (ast.Tuple, ast.List, ast.Set)):
                continue
            literals = {elt.value for elt in value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
            overlapping = sorted(literals & domain_names)
            self.assertLess(
                len(overlapping),
                2,
                f"module-level collection of {len(overlapping)} domain names {overlapping} in lint.py: the "
                "--type acceptance set must be derived from the registry at run time, never "
                "hand-listed (REQ-002)",
            )

    def test_lint_module_imports_with_mcp_blocked(self):
        with mock.patch.dict(sys.modules, {"mcp": None}):
            spec = importlib.util.spec_from_file_location("biz.dfch.specmgr.commands.lint_isolated", _LINT_PY)
            assert spec is not None, "spec_from_file_location failed for the lint command's own file"
            assert spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module  # the module-level dataclasses resolve PEP 563 annotations against it
            try:
                spec.loader.exec_module(module)
            finally:
                sys.modules.pop(spec.name, None)

        self.assertEqual(module.EXIT_OK, 0)
        self.assertEqual(module.EXIT_LINT_FAILURE, 1)
        self.assertEqual(module.EXIT_USAGE, 2)
        self.assertTrue(callable(module.lint))


class TestLintMissingMcpExtra(unittest.TestCase):
    """Task 110.130 / REQ-002: the missing-``mcp``-extra guard -- with the registry-backed chain
    genuinely unimportable, the command exits 1 with the clear install message instead of a
    raw traceback. This runs in a FRESH interpreter subprocess (in the test process every module
    is already in ``sys.modules``, so the lazily imported registry chain would import cleanly and
    the guard could never fire in-process); the subprocess blocks ``mcp`` and loads
    ``commands/lint.py`` from its own file, mirroring the in-process import test above."""

    def test_guard_exits_1_with_clear_message_when_registry_chain_unimportable(self):
        code = (
            "import importlib.util\n"
            "import sys\n"
            "sys.modules['mcp'] = None\n"
            f"spec = importlib.util.spec_from_file_location('biz.dfch.specmgr.commands.lint_sub', {str(_LINT_PY)!r})\n"
            "assert spec is not None and spec.loader is not None\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "sys.modules[spec.name] = module\n"
            "spec.loader.exec_module(module)\n"
            "try:\n"
            "    module.lint(type='req')\n"
            "except BaseException as ex:\n"
            "    print('CAUGHT', type(ex).__name__, getattr(ex, 'exit_code', None))\n"
        )

        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=_REPO_ROOT,
        )

        self.assertIn("CAUGHT Exit 1", proc.stdout, f"stdout: {proc.stdout!r}\nstderr: {proc.stderr!r}")
        self.assertIn("You must install the `mcp` extra to use this command", proc.stderr, proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


class TestLintHookPattern(unittest.TestCase):
    """Task 110.130 / ACC-008 + feat-245 Phase 120 (Task 120.110) / REQ-006: the canonical
    anchored in-tree artifact file pattern (the one the pre-commit hook and the CI step share
    verbatim), pinned against this module's own constant :data:`_HOOK_FILE_PATTERN`. The
    constant matches one representative path per ``ALL_DOMAINS`` type (the sharded valid shape
    for the UUID domains, the folder shape for feat -- the registry is iterated, never a
    hand-listed set), every misplaced depth of every UUID domain (the open-depth docs part that
    selects them for the lint command's placement validator), the non-domain dirs at every
    depth (selected, then skipped by the command), and no non-artifact location. The identity
    assertions run conditionally on the hook / CI step being present: until then there is
    nothing to compare (green from Phase 110), and once a file carries a specmgr-lint
    hook/step, its pattern MUST equal the constant (the assertion never weakens to a no-op)."""

    def test_pattern_matches_one_representative_path_per_type(self):
        for doc_type in ALL_DOMAINS:
            with self.subTest(domain=doc_type):
                path = ".specmgr/feat/feat-1-x/README.md" if doc_type == FEAT else f"docs/{doc_type}/en/00/x.md"
                self.assertIsNotNone(re.fullmatch(_HOOK_FILE_PATTERN, path), path)

    def test_pattern_matches_every_misplaced_depth_for_every_uuid_domain(self):
        """feat-245 Phase 120 / REQ-006: the open-depth docs part selects every misplaced depth
        of a registered UUID domain -- the flat file (missing language dir), the file directly
        in the language dir (missing shard dir), the non-hex shard, and the deeper-than-one-
        shard-level file -- so the lint command's placement validator can fail them (exit 2)."""
        for doc_type in UUID_DOMAINS:
            with self.subTest(domain=doc_type):
                for path in (
                    f"docs/{doc_type}/x.md",
                    f"docs/{doc_type}/en/x.md",
                    f"docs/{doc_type}/en/zz/x.md",
                    f"docs/{doc_type}/en/10/20/x.md",
                ):
                    self.assertIsNotNone(re.fullmatch(_HOOK_FILE_PATTERN, path), path)

    def test_pattern_matches_non_domain_dirs_at_every_depth(self):
        """feat-245 Phase 120 / REQ-006: non-domain dirs under ``docs/`` (``docs/archive/`` at
        depth >= 3, ``docs/api/``, ``docs/appendix/``) are selected by the pattern and then
        SKIPPED by the lint command (exit 0, counted) -- the pattern has no per-type list, the
        command's own derived type list decides which matched files are artifacts."""
        for path in (
            "docs/archive/adr/x.md",
            "docs/archive/a/b/x.md",
            "docs/api/x/y.md",
            "docs/appendix/x.md",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(re.fullmatch(_HOOK_FILE_PATTERN, path), path)

    def test_pattern_does_not_match_non_artifact_locations(self):
        for path in (
            ".specmgr/conventions/x.md",
            ".specmgr/feat/feat-1-x/evidence/some/docs/tsk/x.md",
            "other/docs/req/en/00/x.md",
            "src/biz/x.md",
        ):
            with self.subTest(path=path):
                self.assertIsNone(re.fullmatch(_HOOK_FILE_PATTERN, path), path)

    def test_hook_files_pattern_is_the_canonical_one_when_present(self):
        text = (_REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        if "id: specmgr-lint" not in text:
            return  # the hook lands in Phase 120; until then there is nothing to compare

        pattern = _hook_files_pattern(text)
        self.assertIsNotNone(pattern, "the specmgr-lint hook is present but carries no files: pattern")
        self.assertEqual(pattern, _HOOK_FILE_PATTERN)

    def test_ci_step_uses_the_identical_pattern_when_present(self):
        text = (_REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        if _LINT_CMD not in text:
            return  # the CI step lands in Phase 130; until then there is nothing to compare

        self.assertIn(_HOOK_FILE_PATTERN, text)


class TestLintFullParseNotCache(_LintTestBase):
    """Task 110.140 / ACC-013 / REQ-003: the gate runs full parses with the document's own
    model-level parser, never the ``list_<d>``/``DocCache`` path -- the feat-214 defect the
    dirty stage (frontmatter+H1 only) reports healthy is reported failed by the command, and a
    ``DocCache`` patched to explode on any read/peek use cannot affect the command (a cache
    that raises on every use proves the command never touches it)."""

    def test_feat214_defect_dirty_stage_healthy_full_parse_and_lint_fail(self):
        path = self._write("feat/feat-214-shape/README.md", _feat214_shaped_text())
        text = path.read_text(encoding="utf-8")

        summary = read_feat_dirty(path)  # the dirty stage never sees the body defect: healthy
        self.assertEqual(summary.title, "Feature: Level 1 Heading is the Title of the Feature")
        with self.assertRaises(Exception):
            whole_body_domain(FEAT).parse_text(text)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("DecisionsMade", result.stdout)

    def test_lint_fails_with_doc_cache_exploding_on_any_use(self):
        path = self._write("feat/feat-214-shape/README.md", _feat214_shaped_text())
        boom = AssertionError("the lint command must never read or peek a DocCache")

        with mock.patch.object(DocCache, "read", side_effect=boom):
            with mock.patch.object(DocCache, "peek_preloaded", side_effect=boom):
                with mock.patch.object(DocCache, "read_preloaded", side_effect=boom):
                    result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("repair via: /repair feat feat-214-shape", result.stdout)


class TestLintNoSweepOnCommitPath(unittest.TestCase):
    """Task 110.140 / ACC-014 / REQ-011: the full-corpus sweep is never part of the commit path,
    the CI pull-request step, or the test suite -- no invocation of the command carries a sweep
    flag on the same command line in ``.pre-commit-config.yaml``,
    ``.github/workflows/ci.yml``, or any file under ``tests/``. A sweep flag counts only as a
    standalone flag token (:func:`_line_carries_sweep_flag`, word-boundary match), so the CI
    step's own mandated line (``--all-extras`` adjacent to the command name, mandatory for the
    mcp extra) is no false positive (Phase 130). The scan is CONTINUATION-AWARE (Phase 160,
    I4): physical lines are folded at trailing-backslash continuations
    (:func:`_logical_lines`) before matching, so a continuation-split invocation (the command
    on line N ending in a backslash, a sweep flag on line N+1) is one logical command line and
    cannot escape the check; a violation is still reported at the logical line's FIRST physical
    line. The command name and the flags are built from parts (see
    :data:`_LINT_CMD`/:data:`_SWEEP_FLAGS`), so this file's own source cannot trip the scan it
    implements."""

    def test_no_sweep_invocation_in_hook_ci_or_tests(self):
        targets: list[Path] = [
            _REPO_ROOT / ".pre-commit-config.yaml",
            _REPO_ROOT / ".github" / "workflows" / "ci.yml",
        ]
        # every source file under tests/ (the __pycache__ bytecode caches are excluded: a binary
        # "line" of a .pyc conflates unrelated source lines' constants, e.g. a docstring naming
        # the command with a different line's flag tuple -- false positives, not invocations)
        targets.extend(
            sorted(
                path for path in (_REPO_ROOT / "tests").rglob("*") if path.is_file() and "__pycache__" not in path.parts
            )
        )

        violations: list[str] = []
        for target in targets:
            text = target.read_text(encoding="utf-8", errors="replace")
            # folded at continuation lines: a backslash-terminated physical line joins with the
            # next, reported at the first physical line (Phase 160, I4)
            for line_number, line in _logical_lines(text):
                if _LINT_CMD not in line:
                    continue
                if _line_carries_sweep_flag(line):
                    violations.append(f"{target.relative_to(_REPO_ROOT)}:{line_number}: {line.strip()}")

        self.assertEqual(
            violations,
            [],
            "a sweep invocation of the lint command on the commit path (REQ-011):\n" + "\n".join(violations),
        )

    def test_sweep_flag_matcher_is_word_boundary_not_substring(self):
        """The Phase 130 regression pin for the word-boundary fix: the
        command name adjacent to ``--all-extras`` (the CI step's mandated
        line shape, the extra mandatory for the registry import chain) is
        NOT a sweep invocation, while a genuine standalone ``--all`` or
        ``--type`` on the command line still is."""
        self.assertFalse(
            _line_carries_sweep_flag(
                "uv run --frozen --all-extras --python 3.13.13 " + _LINT_CMD + " --skip-unrecognized"
            )
        )
        self.assertTrue(_line_carries_sweep_flag(_LINT_CMD + " --all"))
        self.assertTrue(_line_carries_sweep_flag(_LINT_CMD + " --type feat"))

    def test_logical_lines_fold_a_continuation_split_sweep_invocation(self):
        """The Phase 160 (I4) regression pin for the continuation fold: a
        continuation-split invocation (the command on one physical line
        ending in a backslash, a standalone sweep flag on the next) folds
        to ONE logical line the matcher flags, reported at the first
        physical line -- the shape that escaped the pre-fold scan; the
        mandated one-line invocation stays unflagged (the negative
        control)."""
        text = "run " + _LINT_CMD + " \\\n    --all\n" + _LINT_CMD + " --skip-unrecognized\n"
        folded = _logical_lines(text)

        self.assertEqual([number for number, _ in folded], [1, 3])
        self.assertTrue(_line_carries_sweep_flag(folded[0][1]))
        self.assertFalse(_line_carries_sweep_flag(folded[1][1]))


class TestLintSweepAllLanguages(_LintTestBase):
    """feat-245 Phase 150 (Task 150.155) / user decision I1=B: the type/all sweep covers
    every language directory for the thirteen sharded domains (the domain-wide union of
    the sharded listings, ``en/`` + every variant) -- a variant document is linted
    exactly like its EN file, and the sweep is not language-blind (a broken variant is
    a parse failure, exit 1). The sweep derives each item's parse language
    POSITION-RELATIVE to the configured domain base -- the root's NAME is irrelevant
    (feat-245 Phase 160, D9: the same healthy EN + ``de/`` variant seeds lint clean under a
    root NOT named ``docs``, the unnamed-root pin -- before the fix the variant was
    canonical-parsed and spurious failed the sweep, exit 1). A mis-PLACED (flat)
    variant file directly inside a language dir stays invisible to the sweep
    (shard-only listing -- the placement gate remains path mode's job), and the
    union's dedup semantics keep a single EN document counted exactly once (the
    6e90d3de double-count defect class)."""

    DOC_TYPE = "dec"

    def _doc_id(self) -> str:
        return whole_body_domain(self.DOC_TYPE).parse_text(read_packaged_text(self.DOC_TYPE, "example")).frontmatter.id

    def _docs_root(self) -> Path:
        # The SPECMGR_DOCS_DIR root (the directory that CONTAINS the domain
        # dirs -- the default is literally "docs"): "docs" is a root NAME,
        # not a dependency -- the D9 fix derives each sweep item's parse
        # language position-relative to this configured base, so the
        # unnamed-root sibling pin exercises any other name.
        return self.tmp / "docs"

    def _sweep(self, root: Path | None = None) -> Result:
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(root or self._docs_root())}):
            return self._invoke("--type", self.DOC_TYPE)

    def _seed_sharded(self, language: str, text: str, root: Path | None = None) -> Path:
        doc_id = self._doc_id()
        path = (root or self._docs_root()) / self.DOC_TYPE / language / doc_id[:2] / f"{doc_id}-sweep.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_type_sweep_lints_a_variant_exactly_like_its_en_file(self):
        """(a) a healthy EN doc + a healthy ``de/`` variant: both linted (count 2),
        exit 0 -- the variant parses through its own heading table (the
        path-derived language) and passes."""
        self._seed_sharded("en", _healthy_whole_body_text(self.DOC_TYPE))
        self._seed_sharded("de", _de_variant_text(self.DOC_TYPE))

        result = self._sweep()

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=2 failed=0 skipped=0 layout=0", result.stdout)

    def test_type_sweep_reports_a_broken_variant_as_a_parse_failure(self):
        """(b) a BROKEN ``de/`` variant (corrupt frontmatter, correct placement):
        the sweep reports it as a parse failure, exit 1 -- the sweep is not
        language-blind."""
        self._seed_sharded("en", _healthy_whole_body_text(self.DOC_TYPE))
        broken_variant = self._seed_sharded(
            "de", _de_variant_text(self.DOC_TYPE).replace("status: accepted", "status: [broken", 1)
        )

        result = self._sweep()

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(broken_variant), result.stdout)
        self.assertIn(f"repair via: /repair {self.DOC_TYPE} {self._doc_id()}", result.stdout)
        self.assertIn("summary: linted=2 failed=1 skipped=0 layout=0", result.stdout)

    def test_type_sweep_counts_a_single_en_document_exactly_once(self):
        """(c) the EN-only regression pin: with only an EN doc, the sweep count
        is 1 -- the union's dedup semantics keep the ``en/`` directory counted
        exactly once (the 6e90d3de double-count defect class)."""
        self._seed_sharded("en", _healthy_whole_body_text(self.DOC_TYPE))

        result = self._sweep()

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_misplaced_flat_variant_is_invisible_to_the_type_sweep(self):
        """(d) a misplaced flat variant file directly under ``docs/<d>/de/``
        (missing the shard dir): still NOT swept (shard-only listing), exit 0
        with count 1 -- the placement gate remains path mode's job, not the
        sweep's."""
        self._seed_sharded("en", _healthy_whole_body_text(self.DOC_TYPE))
        doc_id = self._doc_id()
        misplaced = self.tmp / "docs" / self.DOC_TYPE / "de" / f"{doc_id}-sweep.md"
        misplaced.parent.mkdir(parents=True, exist_ok=True)
        misplaced.write_text(_de_variant_text(self.DOC_TYPE), encoding="utf-8")

        result = self._sweep()

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_type_sweep_lints_a_variant_under_an_unnamed_docs_root(self):
        """(e) feat-245 Phase 160, D9 (user decision Option A): the sweep's parse-language
        derivation is POSITION-RELATIVE to the configured domain base -- a
        ``SPECMGR_DOCS_DIR`` root NOT named ``docs`` (``specdocs``) still
        lints a healthy EN doc + a healthy table-closed ``de/`` variant
        clean (count 2, exit 0 -- the variant parses through its own
        heading table). Before the fix the variant was canonical-parsed
        under an unnamed root and spurious failed the sweep with the
        German-heading mismatch (exit 1) -- the pre-fix red is proven by
        stashing the src fix (the Phase 160 entry records it)."""
        root = self.tmp / "specdocs"
        self._seed_sharded("en", _healthy_whole_body_text(self.DOC_TYPE), root)
        self._seed_sharded("de", _de_variant_text(self.DOC_TYPE), root)

        result = self._sweep(root)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=2 failed=0 skipped=0 layout=0", result.stdout)


class TestLintDocsAnchorIsRooted(_LintTestBase):
    """feat-245 Phase 180 (Task 180.110, E2): path mode must not take an ANCESTOR directory that
    happens to be named ``docs`` for the repo's own ``docs/`` tree. Before the fix the LAST ``docs``
    segment of an absolute path anchored, so ``<tmp>/docs/repo/.specmgr/feat/feat-1-x/README.md``
    was anchored to the non-domain ``repo`` dir and a BROKEN feat README silently passed the gate
    (skipped, exit 0). Each case runs twice: ROOTED (the temp repo carries a ``.git`` marker, so the
    anchor is taken relative to the repo root) and UN-ROOTED (no marker, outside the working
    directory -- the last-``docs`` fallback, whose non-domain skip applies only when no other rule
    matches)."""

    def _repo(self, rooted: bool) -> Path:
        """A temp repo under a ``docs``-named ancestor: ``<tmp>/docs/repo-rooted`` (with a ``.git``
        marker) or ``<tmp>/docs/repo-unrooted`` (none; outside the working directory)."""
        repo = self.tmp / "docs" / ("repo-rooted" if rooted else "repo-unrooted")
        repo.mkdir(parents=True, exist_ok=True)
        if rooted:
            (repo / ".git").mkdir(exist_ok=True)
        return repo

    def _doc_id(self) -> str:
        return whole_body_domain("req").parse_text(read_packaged_text("req", "example")).frontmatter.id

    def test_a_broken_feat_readme_under_a_docs_named_ancestor_fails(self):
        """(a) the broken feat README is inferred as ``feat`` and fails (exit 1), never skipped."""
        for rooted in (True, False):
            with self.subTest(rooted=rooted):
                path = self._repo(rooted) / ".specmgr" / "feat" / "feat-1-x" / "README.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(_feat214_shaped_text(), encoding="utf-8")

                result = self._invoke(str(path.resolve()))

                self.assertEqual(result.exit_code, 1, result.output)
                self.assertIn("DecisionsMade", result.stdout)
                self.assertIn("summary: linted=1 failed=1 skipped=0 layout=0", result.stdout)

    def test_a_valid_sharded_doc_under_a_docs_named_ancestor_is_linted(self):
        """(b) a valid sharded doc (repo-``docs`` anchored, and root-name-independent outside any
        ``docs`` dir) is linted, exit 0."""
        doc_id = self._doc_id()
        for rooted in (True, False):
            for rel in (f"docs/req/en/{doc_id[:2]}/{doc_id}-x.md", f"specdocs/req/en/{doc_id[:2]}/{doc_id}-x.md"):
                with self.subTest(rooted=rooted, rel=rel):
                    path = self._repo(rooted) / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(_healthy_whole_body_text("req"), encoding="utf-8")

                    result = self._invoke(str(path.resolve()))

                    self.assertEqual(result.exit_code, 0, result.output)
                    self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_a_real_non_domain_archive_file_under_a_docs_named_ancestor_is_still_skipped(self):
        """(c) a real ``docs/archive/`` file (copied from the repo's own archive tree) stays skipped
        (exit 0). Rooted: every real archive file, ``docs/archive/sop/`` included (the rooted anchor is
        trustworthy, the skip unconditional); un-rooted: an ``adr`` archive file (no other inference
        rule matches it)."""
        archive = _REPO_ROOT / "docs" / "archive"
        real_files = sorted(path for path in archive.rglob("*.md") if path.is_file())
        adr_file = next(path for path in real_files if path.parent.name == "adr")
        for rooted, sources in ((True, real_files), (False, [adr_file])):
            repo = self._repo(rooted)
            for source in sources:
                rel = source.relative_to(_REPO_ROOT)
                with self.subTest(rooted=rooted, rel=str(rel)):
                    path = repo / rel
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(source.read_bytes())

                    result = self._invoke(str(path.resolve()))

                    self.assertEqual(result.exit_code, 0, result.output)
                    self.assertIn("summary: linted=0 failed=0 skipped=1 layout=0", result.stdout)

    def test_a_rooted_misplaced_file_is_still_a_layout_violation(self):
        """The rooted anchor still drives the placement validator: ``<repo>/docs/req/foo.md`` is the
        missing-language-dir violation (exit 2)."""
        repo = self._repo(True)
        path = repo / "docs" / "req" / "foo.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_healthy_whole_body_text("req"), encoding="utf-8")

        result = self._invoke(str(path.resolve()))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("layout violation: missing language directory", result.stdout)


class TestLintDocsAnchorNestedProject(_LintTestBase):
    """feat-245 Phase 190 (Task 190.110, G2 of review cycle 5; E1): the docs anchor of a path is a ``docs``
    segment that is the FIRST segment relative to EITHER the working directory (when the path lies under it
    and the working directory is inside the repo) OR the repo root (the nearest ``.git``). Before the fix the
    repo root ALWAYS won over the working directory, so in a nested project (``mono/.git``, docs at
    ``mono/proj/docs/``, run from ``mono/proj``) ``docs/req/foo.md`` was not anchored, inferred by its parent
    name and linted (exit 0, ``linted=1``) instead of the Phase 120 layout violation (exit 2), and a real
    ``docs/archive/sop/README.md`` there was linted as ``sop`` instead of skipped."""

    def _nested(self) -> tuple[Path, Path]:
        """``<tmp>/mono`` (with a ``.git`` marker) and its nested project ``<tmp>/mono/proj``."""
        mono = self.tmp / "mono"
        (mono / ".git").mkdir(parents=True, exist_ok=True)
        proj = mono / "proj"
        proj.mkdir(parents=True, exist_ok=True)
        return mono, proj

    def _doc_id(self) -> str:
        return whole_body_domain("req").parse_text(read_packaged_text("req", "example")).frontmatter.id

    def test_a_misplaced_file_in_a_nested_project_is_a_layout_violation(self):
        """(a) ``docs/req/<file>.md`` run from the nested project is the missing-language-dir violation
        (exit 2), naming the correct ``docs/req/en/<shard>/<file>.md`` path."""
        _mono, proj = self._nested()
        doc_id = self._doc_id()
        self.enterContext(contextlib.chdir(proj))
        for name, correct in (
            ("foo.md", "docs/req/en/<2-hex-shard>/foo.md"),
            (f"{doc_id}-x.md", f"docs/req/en/{doc_id[:2]}/{doc_id}-x.md"),
        ):
            with self.subTest(name=name):
                path = proj / "docs" / "req" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(_healthy_whole_body_text("req"), encoding="utf-8")

                result = self._invoke(f"docs/req/{name}")

                self.assertEqual(result.exit_code, 2, result.output)
                self.assertIn("layout violation: missing language directory", result.stdout)
                self.assertIn(f"correct path: {correct}", result.stdout)
                self.assertIn("summary: linted=0 failed=0 skipped=0 layout=1", result.stdout)

    def test_a_valid_sharded_doc_in_a_nested_project_is_linted(self):
        """(b) a valid sharded doc under the nested project's ``docs/`` is linted (exit 0)."""
        _mono, proj = self._nested()
        doc_id = self._doc_id()
        rel = f"docs/req/en/{doc_id[:2]}/{doc_id}-x.md"
        path = proj / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_healthy_whole_body_text("req"), encoding="utf-8")
        self.enterContext(contextlib.chdir(proj))

        result = self._invoke(rel)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_a_real_non_domain_archive_file_in_a_nested_project_is_skipped(self):
        """(c) every real ``docs/archive/`` file (copied from the repo's own archive tree, the
        ``docs/archive/sop/`` files included) under the nested project is skipped (exit 0)."""
        _mono, proj = self._nested()
        archive = _REPO_ROOT / "docs" / "archive"
        real_files = sorted(path for path in archive.rglob("*.md") if path.is_file())
        self.assertTrue(any(path.parent.name == "sop" for path in real_files), real_files)
        self.enterContext(contextlib.chdir(proj))
        for source in real_files:
            rel = source.relative_to(_REPO_ROOT)
            with self.subTest(rel=str(rel)):
                path = proj / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(source.read_bytes())

                result = self._invoke(str(rel))

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=0 failed=0 skipped=1 layout=0", result.stdout)

    def test_docs_directly_under_the_repo_root_stay_anchored_from_a_subdirectory(self):
        """(d) the working directory is a subdirectory of the repo root and the docs sit directly under
        the repo root: the repo-root anchor still applies (absolute and ``../``-relative paths)."""
        mono, _proj = self._nested()
        sub = mono / "sub"
        sub.mkdir()
        path = mono / "docs" / "req" / "foo.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_healthy_whole_body_text("req"), encoding="utf-8")
        self.enterContext(contextlib.chdir(sub))
        for given in (str(path.resolve()), "../docs/req/foo.md"):
            with self.subTest(given=given):
                result = self._invoke(given)

                self.assertEqual(result.exit_code, 2, result.output)
                self.assertIn("layout violation: missing language directory", result.stdout)
                self.assertIn("correct path: docs/req/en/<2-hex-shard>/foo.md", result.stdout)

    def test_a_working_directory_above_the_repo_never_anchors_a_docs_named_ancestor(self):
        """(e) the working directory sits ABOVE the repo, at the parent of an ancestor named ``docs``
        (``<tmp>`` over ``<tmp>/docs/repo/.git``): the working directory is no root candidate (it is
        outside the repo), so ``docs/repo/.specmgr/feat/feat-1-x/README.md`` is not anchored to the
        non-domain ``repo`` dir -- the broken feat README is inferred as ``feat`` and fails (exit 1),
        the Phase 180 E2 case kept closed (Decisions Made 2026-11-27, Phase 190)."""
        repo = self.tmp / "docs" / "repo"
        (repo / ".git").mkdir(parents=True)
        path = repo / ".specmgr" / "feat" / "feat-1-x" / "README.md"
        path.parent.mkdir(parents=True)
        path.write_text(_feat214_shaped_text(), encoding="utf-8")
        self.enterContext(contextlib.chdir(self.tmp))

        result = self._invoke("docs/repo/.specmgr/feat/feat-1-x/README.md")

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("summary: linted=1 failed=1 skipped=0 layout=0", result.stdout)


class TestLintShardedShapeIsRootNameIndependent(_LintTestBase):
    """feat-245 Phase 180 (Task 180.140, G2 = Option A): path mode recognises the sharded shape
    ``<domain>/<lang>/<2-hex>/<file>.md`` by SHAPE, under a ``SPECMGR_DOCS_DIR`` root of any name
    (``specdocs``) -- before the fix ``specdocs/req/en/ab/x.md`` was an unrecognized layout (exit 2,
    the parent-name rule saw the shard), and with ``--type`` a variant was canonical-parsed (a false
    failure, the D9 class Phase 160 fixed for the sweep only). The path-mode parse language is derived
    from the same position."""

    def _doc_id(self, doc_type: str) -> str:
        return whole_body_domain(doc_type).parse_text(read_packaged_text(doc_type, "example")).frontmatter.id

    def test_an_en_shard_file_under_an_unnamed_root_is_linted(self):
        doc_id = self._doc_id("req")
        path = self._write(f"specdocs/req/en/{doc_id[:2]}/{doc_id}-x.md", _healthy_whole_body_text("req"))

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_a_table_closed_variant_under_an_unnamed_root_parses_with_its_own_table(self):
        doc_id = self._doc_id("dec")
        path = self._write(f"specdocs/dec/de/{doc_id[:2]}/{doc_id}-x.md", _de_variant_text("dec"))
        for args in ((), ("--type", "dec")):
            with self.subTest(args=args):
                result = self._invoke(str(path), *args)

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=1 failed=0 skipped=0 layout=0", result.stdout)

    def test_a_broken_variant_under_an_unnamed_root_still_fails(self):
        doc_id = self._doc_id("dec")
        broken = _de_variant_text("dec").replace("## Quelle", "## Völlig Falsch", 1)
        self.assertNotEqual(broken, _de_variant_text("dec"))
        path = self._write(f"specdocs/dec/de/{doc_id[:2]}/{doc_id}-x.md", broken)
        for args in ((), ("--type", "dec")):
            with self.subTest(args=args):
                result = self._invoke(str(path), *args)

                self.assertEqual(result.exit_code, 1, result.output)
                self.assertIn("summary: linted=1 failed=1 skipped=0 layout=0", result.stdout)


class TestLintImportSafeMirrorsMatchTheirSources(unittest.TestCase):
    """feat-245 Phase 180 (Task 180.210, S2): ``commands/lint.py``'s import-safe mirrors equal their
    sources (lazy import -- the sources sit behind the ``mcp`` extra), and the shard-dir pattern is
    derived from the same mirrored shard width the correct-path builder uses."""

    def test_mirrors_equal_their_sources(self):
        lint = importlib.import_module("biz.dfch.specmgr.commands.lint")
        from biz.dfch.specmgr.general.models.heading_table import DEFAULT_LANGUAGE  # noqa: PLC0415
        from biz.dfch.specmgr.general.tools._doc_paths import SHARD_DIGITS  # noqa: PLC0415
        from biz.dfch.specmgr.general.tools._path_safety import LANGUAGE_PATTERN  # noqa: PLC0415

        self.assertEqual(lint._LANG_DIR_PATTERN.pattern, LANGUAGE_PATTERN.pattern)  # pylint: disable=protected-access
        self.assertEqual(lint._SHARD_DIGITS, SHARD_DIGITS)  # pylint: disable=protected-access
        self.assertEqual(lint._DEFAULT_LANGUAGE, DEFAULT_LANGUAGE)  # pylint: disable=protected-access

    def test_the_two_shard_dir_patterns_accept_and_reject_the_same_samples(self):
        """feat-245 Phase 190 (Task 190.170, I1): ``lint.py``'s import-safe ``_SHARD_DIR_PATTERN`` and the read
        scan's own ``general/tools/_doc_paths._SHARD_DIR_PATTERN`` (both used with ``fullmatch``) agree on every
        sample, so the lint placement gate and the read scan cannot disagree on what a shard dir is."""
        lint = importlib.import_module("biz.dfch.specmgr.commands.lint")
        doc_paths = importlib.import_module("biz.dfch.specmgr.general.tools._doc_paths")
        lint_pattern = lint._SHARD_DIR_PATTERN  # pylint: disable=protected-access
        read_pattern = doc_paths._SHARD_DIR_PATTERN  # pylint: disable=protected-access
        expected = {"ab": True, "0f": True, "00": True, "AB": False, "zz": False, "a": False, "abc": False}
        for sample, accepted in expected.items():
            with self.subTest(sample=sample):
                self.assertEqual(lint_pattern.fullmatch(sample) is not None, accepted)
                self.assertEqual(read_pattern.fullmatch(sample) is not None, accepted)

    def test_the_shard_pattern_and_the_correct_path_derive_from_the_same_width(self):
        lint = importlib.import_module("biz.dfch.specmgr.commands.lint")

        width = lint._SHARD_DIGITS  # pylint: disable=protected-access
        pattern = lint._SHARD_DIR_PATTERN  # pylint: disable=protected-access
        self.assertIsNotNone(pattern.fullmatch("a" * width))
        self.assertIsNone(pattern.fullmatch("a" * (width + 1)))
        self.assertIsNone(pattern.fullmatch("a" * (width - 1)))
        doc_id = "deadbeef-0000-0000-0000-000000000000"
        correct = lint._correct_sharded_path("req", (), f"{doc_id}-x.md", doc_id)  # pylint: disable=protected-access
        shard = correct.split("/")[3]
        self.assertEqual(shard, doc_id[:width])
        self.assertIsNotNone(pattern.fullmatch(shard))


if __name__ == "__main__":
    unittest.main()
