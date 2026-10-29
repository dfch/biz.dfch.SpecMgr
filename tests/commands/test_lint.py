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
  ``--skip-unrecognized`` (skipped and counted), the unconditional ADR
  ``README.md`` exclusion (path and sweep mode, with and without the
  flag, a ``README.md`` in another directory via ``--type adr``, and
  ``feat/<id>/README.md`` never excluded), and the exit-2 usage
  errors.
* Task 110.110 -- the negative pins (the feat-214-shape dated-bullet
  fixture built from the packaged feat template, a structurally
  broken ADR, and a broken ``req`` document) and the healthy
  fixtures (every whole-body domain's packaged ``get_<d>_example``
  data, each first verified to parse with its own model-level parser,
  plus a minimal rendered ADR), with the per-type repair pointer
  (the derived id -- lowercased for the UUID-shaped types, the folder
  name for feat -- and the id-less fallback, the ADR fix-manually
  line).
* Task 110.120 -- environment behaviour: path mode independent of
  ``SPECMGR_*_DIR``, sweep mode honoring them, ``--dir`` overriding,
  the all-sweep finding zero documents exiting 2, a
  registered-but-empty ``--type`` domain exiting 0 with a 0-document
  summary, and a path run in which every path is skipped or excluded
  exiting 0 with a 0-linted summary.
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
"""

from __future__ import annotations

import ast
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

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.feat.tools._cache import read_feat_dirty
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._doc_cache import DocCache
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._domains import ALL_DOMAINS, FEAT, WHOLE_BODY_DOMAINS, whole_body_domain
from biz.dfch.specmgr.general.tools._packaged_data import read_packaged_text
from biz.dfch.specmgr.models.adr import Adr, AdrBody, AdrFrontmatter, AdrOption, parse_adr, render_adr

runner = CliRunner()

#: The repository root (this file lives at ``tests/commands/test_lint.py``).
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The lint command's own source file (the subject of the AST and
#: import-safety pins).
_LINT_PY = _REPO_ROOT / "src" / "biz" / "dfch" / "specmgr" / "commands" / "lint.py"

#: The canonical anchored in-tree artifact file pattern the pre-commit hook
#: (Phase 120) and the CI pull-request step (Phase 130) both use verbatim
#: (the plan's Design Notes / REQ-009: one shared pattern, the lint command's
#: own derived type list deciding which matched files are artifacts).
_HOOK_FILE_PATTERN = r"^(\.specmgr/feat/[^/]+/README\.md|docs/[^/]+/[^/]+\.md)$"

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


def _healthy_adr_text() -> str:
    """A minimal rendered ADR (verified to parse), the healthy fixture for the
    one type whose packaged example is not a ``get_<d>_example`` data file."""
    adr = Adr(
        frontmatter=AdrFrontmatter(id="11111111-1111-4111-8111-111111111111", status="accepted", date="2026-01-01"),
        body=AdrBody(
            title="Minimal ADR",
            context_and_problem_statement="A context.",
            considered_options="Option 1 only.",
            decision_outcome="We chose Option 1.",
            options=[AdrOption(number=1, partial_title="The only option", content="Good: fine.")],
        ),
    )
    text = render_adr(adr)
    parse_adr(text)
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
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)

    def test_feat_folder_shape_is_inferred(self):
        text = _healthy_whole_body_text(FEAT)
        doc_id = whole_body_domain(FEAT).parse_text(text).frontmatter.id
        path = self._write(f"feat/{doc_id}/README.md", text)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)

    def test_type_option_overrides_inference(self):
        path = self._write("elsewhere/foo.md", _healthy_whole_body_text("req"))

        result = self._invoke(str(path), "--type", "req")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)

    def test_unrecognized_layout_is_a_usage_error(self):
        path = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("unrecognized layout", result.output)

    def test_unrecognized_layout_is_skipped_and_counted_with_flag(self):
        path = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(path), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=1 excluded=0", result.stdout)

    def test_skip_flag_does_not_change_exit_code_for_a_healthy_run(self):
        healthy = self._write("req/healthy.md", _healthy_whole_body_text("req"))
        unknown = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(healthy), str(unknown), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=1 excluded=0", result.stdout)


class TestLintAdrReadmeExclusion(_LintTestBase):
    """Task 110.100 / REQ-007: the unconditional ADR ``README.md`` exclusion -- resolved type
    ``adr`` (inferred or via ``--type adr``) and base name ``README.md``, in any directory. The
    excluded file is never parsed (the fixtures carry garbage content that would fail any parse)
    and ``feat/<id>/README.md`` (type ``feat``) is never excluded."""

    def test_path_mode_inferred_adr_readme_excluded_without_flag(self):
        path = self._write("adr/README.md", "not an ADR at all")

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=0 excluded=1", result.stdout)

    def test_path_mode_inferred_adr_readme_excluded_with_skip_flag(self):
        path = self._write("adr/README.md", "not an ADR at all")

        result = self._invoke(str(path), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=0 excluded=1", result.stdout)

    def test_path_mode_type_adr_on_readme_in_another_directory_excluded(self):
        path = self._write("elsewhere/README.md", "not an ADR at all")

        result = self._invoke(str(path), "--type", "adr")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=0 excluded=1", result.stdout)

    def test_sweep_type_adr_excludes_readme_and_lints_the_adrs(self):
        adr_root = self.tmp / "adr-root"
        adr_root.mkdir()
        (adr_root / "README.md").write_text("generated table of contents", encoding="utf-8")
        (adr_root / "11111111-1111-4111-8111-111111111111.md").write_text(_healthy_adr_text(), encoding="utf-8")

        with mock.patch.dict(os.environ, {ADR_DIR_ENV_VAR: str(adr_root)}):
            result = self._invoke("--type", "adr")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=1", result.stdout)

    def test_sweep_all_excludes_the_adr_readme(self):
        adr_root = self.tmp / "adr-root"
        adr_root.mkdir()
        (adr_root / "README.md").write_text("generated table of contents", encoding="utf-8")
        (adr_root / "11111111-1111-4111-8111-111111111111.md").write_text(_healthy_adr_text(), encoding="utf-8")

        with mock.patch.dict(
            os.environ,
            {
                DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs"),
                FEAT_DIR_ENV_VAR: str(self.tmp / "empty-feat"),
                ADR_DIR_ENV_VAR: str(adr_root),
            },
        ):
            result = self._invoke("--all")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=1", result.stdout)

    def test_feat_readme_is_never_excluded(self):
        text = _healthy_whole_body_text(FEAT)
        doc_id = whole_body_domain(FEAT).parse_text(text).frontmatter.id
        path = self._write(f"feat/{doc_id}/README.md", text)

        result = self._invoke(str(path), "--type", FEAT)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)


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
        self.assertIn("summary: linted=1 failed=1 skipped=0 excluded=0", result.stdout)


class TestLintAdrFailure(_LintTestBase):
    """Task 110.110 / ACC-002: a structurally broken ADR (an ``AdrParseError`` case) fails with
    the file named and the ADR fix-manually line instead of a ``/repair`` pointer (the repair
    flow is whole-body-only)."""

    _BROKEN_ADR = "---\nstatus: accepted\n---\n\n# Broken ADR\n\n## Bogus Heading\n\ntext\n"

    def test_broken_adr_fails_with_file_error_and_adr_line(self):
        path = self._write("adr/11111111-1111-4111-8111-111111111111.md", self._BROKEN_ADR)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("unrecognized H2 heading", result.stdout)
        self.assertIn(
            "ADR is not covered by the repair flow; fix the file manually from the error above.",
            result.stdout,
        )
        self.assertNotIn("repair via:", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 excluded=0", result.stdout)


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


class TestLintHealthyFixtures(_LintTestBase):
    """Task 110.110 / ACC-002: the healthy fixtures -- every whole-body domain's packaged
    ``get_<d>_example`` data (each first verified to parse with its own model-level parser, and
    written under a layout the command infers from the path alone) plus a minimal rendered ADR --
    each exits 0."""

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
                self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)

    def test_minimal_rendered_adr_lints_clean(self):
        text = _healthy_adr_text()
        path = self._write(f"adr/{parse_adr(text).frontmatter.id}.md", text)

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)


class TestLintReadFailures(_LintTestBase):
    """Task 110.110 (negative pins, REQ-008): a user-named path that exists but fails to decode
    is a per-file parse FAILURE (exit 1, counted in ``linted`` -- Phase 100's decision (3)), a
    sweep-enumerated file that fails to read is a per-file parse failure too (exit 1, in contrast
    to the user-named unreadable path's exit 2), and a feat-typed document whose path is not the
    ``feat/<id>/README.md`` folder shape gets the id-less ``/repair feat`` fallback pointer."""

    def test_decode_failure_is_a_lint_failure_counted_as_linted(self):
        path = self.tmp / "req" / "bad-encoding.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\xfe this is not valid utf-8 \x00\x01")

        result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(path), result.stdout)
        self.assertIn("not valid utf-8", result.stdout)
        self.assertIn("\n  repair via: /repair req\n", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 excluded=0", result.stdout)

    def test_sweep_enumerated_unreadable_file_is_a_lint_failure(self):
        docs_root = self.tmp / "docsroot"
        file_path = docs_root / "req" / "unreadable.md"
        file_path.parent.mkdir(parents=True)
        file_path.write_text(_broken_req_text(), encoding="utf-8")
        os.chmod(file_path, 0)
        self.addCleanup(os.chmod, file_path, 0o644)

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(docs_root)}):
            result = self._invoke("--type", "req")

        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn(str(file_path), result.stdout)
        self.assertIn("unreadable:", result.stdout)
        self.assertIn("summary: linted=1 failed=1 skipped=0 excluded=0", result.stdout)

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
    with a 0-document summary), and a path run in which every path is skipped or excluded exits
    0 with a 0-linted summary."""

    def _empty_env(self) -> dict[str, str]:
        return {
            DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs"),
            FEAT_DIR_ENV_VAR: str(self.tmp / "empty-feat"),
            ADR_DIR_ENV_VAR: str(self.tmp / "empty-adr"),
        }

    def test_path_mode_is_unaffected_by_env_vars(self):
        path = self._write("req/healthy.md", _healthy_whole_body_text("req"))

        with mock.patch.dict(os.environ, self._empty_env()):
            result = self._invoke(str(path))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)

    def test_sweep_mode_honors_env_vars(self):
        for doc_type, env_var in ((FEAT, FEAT_DIR_ENV_VAR), ("req", DOCS_DIR_ENV_VAR)):
            with self.subTest(domain=doc_type):
                with mock.patch.dict(os.environ, {env_var: str(self.tmp / "empty")}):
                    result = self._invoke("--type", doc_type)

                self.assertEqual(result.exit_code, 0, result.output)
                self.assertIn("summary: linted=0 failed=0 skipped=0 excluded=0", result.stdout)

    def test_dir_overrides_env_var(self):
        example_text = read_packaged_text("req", "example")
        doc_id = whole_body_domain("req").parse_text(example_text).frontmatter.id
        sweep_dir = self.tmp / "sweep"
        sweep_dir.mkdir()
        (sweep_dir / f"{doc_id}.md").write_text(example_text, encoding="utf-8")

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs")}):
            result = self._invoke("--type", "req", "--dir", str(sweep_dir))

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=1 failed=0 skipped=0 excluded=0", result.stdout)

    def test_all_with_zero_documents_exits_2(self):
        with mock.patch.dict(os.environ, self._empty_env()):
            result = self._invoke("--all")

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("zero documents", result.output)

    def test_type_uc_with_no_documents_exits_0(self):
        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.tmp / "empty-docs")}):
            result = self._invoke("--type", "uc")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=0 excluded=0", result.stdout)

    def test_every_path_skipped_or_excluded_exits_0_with_zero_linted(self):
        excluded = self._write("adr/README.md", "not an ADR at all")
        skipped = self._write("elsewhere/foo.md", "anything")

        result = self._invoke(str(excluded), str(skipped), "--skip-unrecognized")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("summary: linted=0 failed=0 skipped=1 excluded=1", result.stdout)


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
                self.assertIn("summary: linted=0 failed=0 skipped=0 excluded=0", result.stdout)

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

    def test_no_module_level_import_of_registry_or_tools_packages(self):
        for name in self._module_level_imports():
            if name.startswith("biz.dfch.specmgr"):
                self.assertTrue(
                    name.startswith("biz.dfch.specmgr.models.adr"),
                    f"module-level specmgr import {name!r} in lint.py: only the mcp-free ADR models "
                    "package is allowed -- the registry and every tools package require the mcp "
                    "extra and must stay inside the lazily imported command body",
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
        importlib.import_module("biz.dfch.specmgr.models.adr")  # already in sys.modules during the block

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
    """Task 110.130 / ACC-008: the canonical anchored in-tree artifact file pattern (the one the
    pre-commit hook and the CI step share verbatim), pinned against this module's own constant
    :data:`_HOOK_FILE_PATTERN`. The constant matches one representative path per ``ALL_DOMAINS``
    type (the registry is iterated, never a hand-listed set) and no non-artifact location. The
    identity assertions run conditionally on the hook (Phase 120) / CI step (Phase 130) being
    present: until then there is nothing to compare (green from Phase 110), and once a file
    carries a specmgr-lint hook/step, its pattern MUST equal the constant (the assertion never
    weakens to a no-op)."""

    def test_pattern_matches_one_representative_path_per_type(self):
        for doc_type in ALL_DOMAINS:
            with self.subTest(domain=doc_type):
                path = ".specmgr/feat/feat-1-x/README.md" if doc_type == FEAT else f"docs/{doc_type}/x.md"
                self.assertIsNotNone(re.fullmatch(_HOOK_FILE_PATTERN, path), path)

    def test_pattern_does_not_match_non_artifact_locations(self):
        for path in (
            "docs/api/x/y.md",
            ".specmgr/conventions/x.md",
            ".specmgr/feat/feat-1-x/evidence/some/docs/tsk/x.md",
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
    mcp extra) is no false positive (Phase 130). The command name and the flags are built from
    parts (see :data:`_LINT_CMD`/:data:`_SWEEP_FLAGS`), so this file's own source cannot trip
    the scan it implements."""

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
            for line_number, line in enumerate(text.splitlines(), start=1):
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


if __name__ == "__main__":
    unittest.main()
