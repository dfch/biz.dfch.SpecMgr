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

"""Tests for the ``harness-bundle`` command (feat-167-mcp-lifecycle-commands-2, Phase 130).

Pins the REQ-007 generator contract:

* **Determinism** -- two runs over an unchanged tree are byte-identical
  (no timestamps; ``json.dumps(indent=2, ensure_ascii=False)`` + trailing
  newline), both in the pure generator and end-to-end over a tmp fixture.
* **Enumeration completeness** -- the current repo tree's 43 files (7 in
  ``agent/``, 11 in ``command/``, 25 in ``skill/*/``) all appear, each with
  a correct ``sha256`` and verbatim ``content``; a tmp-fixture copy of the
  scoped dirs gains a file and the generated bundle contains it with the
  correct ``sha256``.
* **Exclusions** -- ``node_modules/``, ``package.json``/
  ``package-lock.json``, a similarly-named sibling directory
  (``zzz-skill/``), and a top-level stray ``*.md`` never appear (the
  strays warn on stderr, one warning per stray top-level entry).
* **Shape and ordering** -- the bundle is ``{"instructions", "files":
  [{"path", "sha256", "content"}]}`` with ``instructions`` present,
  non-empty, and the module constant verbatim; ``files`` sorted by
  ``.opencode/``-relative ``path``.
* **Usage error** -- a missing ``.opencode/`` directory, a scoped file that
  is not decodable as UTF-8, and an unwritable/uncreatable bundle output
  path are each exit 2, nothing written, no traceback.
* **Drift pin** -- the committed bundle is byte-identical to a fresh
  in-memory generation over the current tree (the
  ``specmgr-harness-bundle`` hook's own regenerate step, minus the write).
* **Hook/CI pins** -- the ``specmgr-harness-bundle`` pre-commit hook
  (entry, ``files`` regex, the regenerate + fail-on-diff pair, placement
  after ``specmgr-mcp-docs`` and before ``specmgr-lint``) and the Python
  3.13-pinned CI parity step (the same regenerate + ``git diff
  --exit-code`` pair over the bundle path, the ``::error::`` hint), the
  ``tests/commands/test_lint.py`` shape-pin precedent.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

from click.testing import Result
from typer.testing import CliRunner

from biz.dfch.specmgr.cli import app
from biz.dfch.specmgr.commands.harness_bundle import INSTRUCTIONS, generate_bundle_text

runner = CliRunner()

#: The repository root (this file lives at ``tests/commands/test_harness_bundle.py``).
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The bundled top-level directory names under ``.opencode/`` (singular, exact match).
_SCOPED_DIRS = ("agent", "command", "skill")

#: The bundle's own path, relative to the repo root (the packaged-data
#: convention, read back by the ``specmgr://harness-bundle`` resource).
_BUNDLE_RELPATH = Path("src") / "biz" / "dfch" / "specmgr" / "general" / "data" / "general_harness_bundle.json"

#: The hook's own entry line (regenerate + fail on diff, the
#: ``specmgr-mcp-docs`` family's shape).
_HOOK_ENTRY = "bash -c 'uv run --frozen specmgr harness-bundle && git diff --exit-code -- " + str(_BUNDLE_RELPATH) + "'"

#: The hook's anchored ``files:`` pattern (a bundled markdown file only).
_HOOK_FILES_PATTERN = r"^\.opencode/(agent|command|skill)/.*\.md$"


def _expected_scoped_paths(repo_root: Path) -> list[str]:
    """The scoped markdown files of ``repo_root``, as sorted ``.opencode/``-relative POSIX paths."""
    opencode_dir = repo_root / ".opencode"
    paths: list[str] = []
    for name in _SCOPED_DIRS:
        scoped_dir = opencode_dir / name
        if not scoped_dir.is_dir():
            continue
        paths.extend(path.relative_to(opencode_dir).as_posix() for path in scoped_dir.rglob("*.md") if path.is_file())
    result = sorted(paths)
    return result


class TestGenerateBundleTextCurrentTree(unittest.TestCase):
    """The pure generator over the real repo tree (read-only; the tree is never mutated)."""

    def _bundle(self) -> dict[str, Any]:
        text, _ = generate_bundle_text(_REPO_ROOT / ".opencode")
        payload: dict[str, Any] = json.loads(text)
        return payload

    def test_current_tree_enumerates_exactly_43_files(self):
        payload = self._bundle()

        paths = [entry["path"] for entry in payload["files"]]

        self.assertEqual(paths, _expected_scoped_paths(_REPO_ROOT))
        self.assertEqual(len(paths), 43)
        per_dir = {name: sum(1 for path in paths if path.startswith(name + "/")) for name in _SCOPED_DIRS}
        self.assertEqual(per_dir, {"agent": 7, "command": 11, "skill": 25})

    def test_top_level_and_file_entry_shape(self):
        payload = self._bundle()

        self.assertEqual(list(payload.keys()), ["instructions", "files"])
        for entry in payload["files"]:
            with self.subTest(path=entry["path"]):
                self.assertEqual(list(entry.keys()), ["path", "sha256", "content"])

    def test_paths_are_sorted(self):
        payload = self._bundle()

        paths = [entry["path"] for entry in payload["files"]]

        self.assertEqual(paths, sorted(paths))

    def test_sha256_and_content_match_the_tree(self):
        payload = self._bundle()

        for entry in payload["files"]:
            on_disk = (_REPO_ROOT / ".opencode" / entry["path"]).read_text(encoding="utf-8")
            with self.subTest(path=entry["path"]):
                self.assertEqual(entry["content"], on_disk)
                self.assertEqual(entry["sha256"], hashlib.sha256(on_disk.encode("utf-8")).hexdigest())

    def test_instructions_present_non_empty_and_the_module_constant(self):
        payload = self._bundle()

        self.assertEqual(payload["instructions"], INSTRUCTIONS)
        self.assertTrue(INSTRUCTIONS.strip())
        for token in ("customize-opencode", "sha256", "question", "opencode.json", "byte-exact"):
            with self.subTest(token=token):
                self.assertIn(token, INSTRUCTIONS)
        # the both-spellings collision case (review cycle 3, finding I3): a root
        # containing both a singular and a plural directory must not be guessed at
        self.assertIn("both a singular and a plural", INSTRUCTIONS)

    def test_two_calls_are_byte_identical(self):
        first, _ = generate_bundle_text(_REPO_ROOT / ".opencode")
        second, _ = generate_bundle_text(_REPO_ROOT / ".opencode")

        self.assertEqual(first, second)

    def test_trailing_newline_and_utf8_unescaped(self):
        text, _ = generate_bundle_text(_REPO_ROOT / ".opencode")

        self.assertTrue(text.endswith("\n"))
        self.assertFalse(text.endswith("\n\n"))

    def test_committed_bundle_is_byte_identical_to_a_fresh_generation(self):
        """The drift pin: the committed file equals the hook's regenerate step, minus the write."""
        committed = (_REPO_ROOT / _BUNDLE_RELPATH).read_text(encoding="utf-8")

        text, _ = generate_bundle_text(_REPO_ROOT / ".opencode")
        self.assertEqual(committed, text)


class _HarnessBundleCommandBase(unittest.TestCase):
    """Shared setup: a tmp repo fixture (the real tree is never mutated) plus a CWD switch into it."""

    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self._build_fixture()
        old_cwd = os.getcwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, old_cwd)

    def _build_fixture(self) -> None:
        """Three scoped files plus the full stray set (never bundled)."""
        opencode = self.tmp / ".opencode"
        (opencode / "agent").mkdir(parents=True)
        (opencode / "command").mkdir(parents=True)
        (opencode / "skill" / "demo-skill").mkdir(parents=True)
        (opencode / "agent" / "a-agent.md").write_text("# A Agent\n", encoding="utf-8")
        (opencode / "command" / "a-command.md").write_text("# A Command\n", encoding="utf-8")
        (opencode / "skill" / "demo-skill" / "SKILL.md").write_text("# Demo Skill\n", encoding="utf-8")
        # strays: top-level file, a similarly-named sibling directory, node_modules,
        # and the package manifest files (all never bundled; the markdown strays warn)
        (opencode / "stray.md").write_text("# Stray\n", encoding="utf-8")
        (opencode / "zzz-skill").mkdir()
        (opencode / "zzz-skill" / "z.md").write_text("# Z\n", encoding="utf-8")
        (opencode / "node_modules" / "pkg").mkdir(parents=True)
        (opencode / "node_modules" / "pkg" / "README.md").write_text("# Pkg\n", encoding="utf-8")
        (opencode / "package.json").write_text("{}", encoding="utf-8")
        (opencode / "package-lock.json").write_text("{}", encoding="utf-8")

    def _invoke(self) -> Result:
        result = runner.invoke(app, ["harness-bundle"])
        return result

    def _bundle_path(self) -> Path:
        path = self.tmp / _BUNDLE_RELPATH
        return path

    def _payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = json.loads(self._bundle_path().read_text(encoding="utf-8"))
        return payload


class TestHarnessBundleCommand(_HarnessBundleCommandBase):
    """The Typer entry point end-to-end: the write path, the summary line, the exclusions, the usage error."""

    def test_run_writes_the_bundle_and_prints_the_summary_line(self):
        result = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(self._bundle_path().is_file())
        self.assertIn("✓ Wrote 3 harness file(s)", result.stdout)
        self.assertIn(str(self._bundle_path()), result.stdout)
        payload = self._payload()
        self.assertEqual(
            [entry["path"] for entry in payload["files"]],
            ["agent/a-agent.md", "command/a-command.md", "skill/demo-skill/SKILL.md"],
        )

    def test_two_runs_over_an_unchanged_tree_are_byte_identical(self):
        self._invoke()
        first = self._bundle_path().read_bytes()

        result = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(self._bundle_path().read_bytes(), first)

    def test_a_new_scoped_file_appears_with_the_correct_sha256(self):
        content = "# B Agent\n"
        (self.tmp / ".opencode" / "agent" / "b-agent.md").write_text(content, encoding="utf-8")

        result = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        payload = self._payload()
        paths = [entry["path"] for entry in payload["files"]]
        self.assertEqual(len(paths), 4)
        self.assertIn("agent/b-agent.md", paths)
        entry = next(e for e in payload["files"] if e["path"] == "agent/b-agent.md")
        self.assertEqual(entry["content"], content)
        self.assertEqual(entry["sha256"], hashlib.sha256(content.encode("utf-8")).hexdigest())

    def test_exclusions_never_appear_in_the_bundle(self):
        result = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        paths = [entry["path"] for entry in self._payload()["files"]]
        for excluded in (
            "stray.md",
            "zzz-skill/z.md",
            "node_modules/pkg/README.md",
            "package.json",
            "package-lock.json",
        ):
            with self.subTest(excluded=excluded):
                self.assertNotIn(excluded, paths)

    def test_strays_warn_on_stderr(self):
        result = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        for stray in ("stray.md", "zzz-skill", "node_modules"):
            with self.subTest(stray=stray):
                self.assertIn(stray, result.stderr)

    def test_paths_are_sorted_and_instructions_are_the_module_constant(self):
        result = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        payload = self._payload()
        paths = [entry["path"] for entry in payload["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(payload["instructions"], INSTRUCTIONS)


class TestHarnessBundleMissingOpencodeDir(_HarnessBundleCommandBase):
    """The I/O usage errors (review cycle 3, finding G4): a missing ``.opencode/``
    directory, a scoped file that is not decodable as UTF-8, and an unwritable
    or uncreatable bundle output path -- each exit 2, nothing written, no traceback."""

    def test_missing_opencode_dir_exits_2_and_writes_nothing(self):
        shutil.rmtree(self.tmp / ".opencode")

        result = self._invoke()

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn(".opencode", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self._bundle_path().exists())
        self.assertFalse((self.tmp / "src").exists())

    def test_non_utf8_scoped_file_exits_2_and_writes_nothing(self):
        (self.tmp / ".opencode" / "agent" / "binary-agent.md").write_bytes(b"\xff\xfe not utf8\n")

        result = self._invoke()

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("nothing was written", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self._bundle_path().exists())
        self.assertFalse((self.tmp / "src").exists())

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permission modes")
    def test_unwritable_output_path_exits_2_and_writes_nothing(self):
        parent = self.tmp / "src" / "biz" / "dfch" / "specmgr" / "general"
        parent.mkdir(parents=True)
        parent.chmod(0o555)
        self.addCleanup(parent.chmod, 0o755)

        result = self._invoke()

        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("nothing was written", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self._bundle_path().exists())


class TestHookAndCiPins(unittest.TestCase):
    """The ``specmgr-harness-bundle`` hook and the CI parity step, pinned by shape
    (the ``tests/commands/test_lint.py`` ``TestLintHookPattern`` precedent: the entry/command
    strings, the ``files`` regex, and the step text -- the regenerate + fail-on-diff pair)."""

    @staticmethod
    def _hook_block(text: str, hook_id: str) -> list[str]:
        """The lines of the hook block starting at ``- id: {hook_id}`` (up to the next ``- id:``)."""
        lines = text.splitlines()
        start: int | None = None
        for index, line in enumerate(lines):
            if line.strip() == f"- id: {hook_id}":
                start = index
                break
        assert start is not None, f"no {hook_id!r} hook in .pre-commit-config.yaml"
        end = len(lines)
        for index in range(start + 1, len(lines)):
            if re.match(r"^\s*- id:", lines[index]):
                end = index
                break
        block = lines[start:end]
        return block

    @staticmethod
    def _block_field(block: list[str], field: str) -> str:
        for line in block:
            stripped = line.strip()
            if stripped.startswith(f"{field}:"):
                value = stripped.split(":", 1)[1].strip()
                return value
        raise AssertionError(f"no {field!r} field in the hook block:\n" + "\n".join(block))

    def test_hook_entry_is_the_regenerate_plus_diff_pair(self):
        text = (_REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        block = self._hook_block(text, "specmgr-harness-bundle")

        self.assertEqual(self._block_field(block, "entry"), _HOOK_ENTRY)

    def test_hook_shape_and_files_pattern(self):
        text = (_REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        block = self._hook_block(text, "specmgr-harness-bundle")

        self.assertEqual(self._block_field(block, "language"), "system")
        self.assertEqual(self._block_field(block, "pass_filenames"), "false")
        self.assertEqual(self._block_field(block, "files"), _HOOK_FILES_PATTERN)

    def test_hook_is_placed_after_mcp_docs_and_before_lint(self):
        text = (_REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

        mcp_docs = text.index("- id: specmgr-mcp-docs")
        harness_bundle = text.index("- id: specmgr-harness-bundle")
        lint = text.index("- id: specmgr-lint")

        self.assertLess(mcp_docs, harness_bundle)
        self.assertLess(harness_bundle, lint)

    def test_files_pattern_matches_only_bundled_locations(self):
        for path in (".opencode/agent/a.md", ".opencode/command/a.md", ".opencode/skill/s/SKILL.md"):
            with self.subTest(path=path):
                self.assertIsNotNone(re.fullmatch(_HOOK_FILES_PATTERN, path), path)
        for path in (".opencode/stray.md", ".opencode/zzz-skill/z.md", ".opencode/node_modules/a.md", "src/a.py"):
            with self.subTest(path=path):
                self.assertIsNone(re.fullmatch(_HOOK_FILES_PATTERN, path), path)

    def test_ci_step_is_the_313_pinned_regenerate_plus_diff_pair(self):
        text = (_REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        step_name = "Make sure `src/biz/dfch/specmgr/general/data/general_harness_bundle.json` is correct"
        self.assertIn(step_name, text)
        block = text.split(step_name, 1)[1].split("- name:", 1)[0]

        self.assertIn("if: matrix.python-version == '3.13'", block)
        self.assertIn("uv run --frozen --all-extras --python 3.13.13 specmgr harness-bundle", block)
        self.assertIn(f"git diff --exit-code -- {_BUNDLE_RELPATH}", block)
        self.assertIn(
            f"::error::{_BUNDLE_RELPATH} is out of date -- run 'uv run --frozen --all-extras "
            "specmgr harness-bundle' and commit the result (see AGENTS.md).",
            block,
        )


if __name__ == "__main__":
    unittest.main()
