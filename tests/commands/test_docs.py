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

"""Tests for the ``docs`` command.

The key regression this closes: previous versions of this feature
(``generate-docs``, ``markdown-docs``) only had tests for private helper
functions, never for the actual file-writing Typer entry point -- which is
exactly where the shipped bugs (broken ``--output`` handling, a regex-splice
bug in ``AGENTS.md``) lived. These tests call ``docs()`` itself and assert on
the files it writes: once via its ``--output`` parameter directly, and once
via its default (patching the module's ``_DOCS_DIR`` constant so the default
branch is exercised without touching the real ``docs/`` tree).
``TestApiDocsPruning`` covers the stale-page prune (feat-40): a healthy run
deletes pre-seeded flat ``*.md`` orphans while leaving ``README.md``,
non-``.md`` files, and nested directories untouched, and an untrustworthy run
(zero pages, a mocked per-module import failure) skips pruning entirely.
``TestDocsRuffFormat`` covers the feat-221 unblock: after the run has written
every rendered markdown document verbatim, ONE in-place ``ruff format`` call
covers all the written paths (embedded code blocks only) -- a fixture whose
docstring embeds an SDK-style, ruff-not-clean ``python`` block must come out
ruff-clean on disk, two full generations are byte-identical, a missing
``ruff`` binary degrades to one stderr warning plus the verbatim
(unformatted) output, a non-zero ``ruff`` exit degrades to one stderr warning
(naming ruff, the exit code, and the first line of ruff's stderr) with the
command still succeeding and the written files left on disk as ruff left them,
and a ruff call that raises ``OSError`` (the resolved binary unrunnable)
degrades the same way (one warning naming ruff, command success, files
intact) -- the command never fails on ruff.
"""

import contextlib
import importlib
import io
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.commands.docs import (
    _collect_module_docs_by_domain,
    _count_mcp_features,
    _count_test_files,
    _format_signature,
    _generate_api_docs,
    _list_domain_packages,
    _ruff_format_written_markdown,
    _stable_signature_str,
    docs,
    generate_generated_md,
    generate_module_reference,
)

# `commands/__init__.py` does `from .docs import docs`, which rebinds the
# `docs` attribute on the `commands` package to the function itself -- so
# `import biz.dfch.specmgr.commands.docs as x` would resolve `x` to that
# function, not the submodule. Go through `importlib` to get the real module
# (needed below to patch its `_DOCS_DIR` constant).
docs_module = importlib.import_module("biz.dfch.specmgr.commands.docs")


class TestDocsEntryPoint(unittest.TestCase):
    """Tests for the ``docs()`` Typer entry point -- the actual write path."""

    def _assert_docs_were_written(self, docs_dir: Path) -> None:
        generated_md = docs_dir / "GENERATED.md"
        api_dir = docs_dir / "api"

        self.assertTrue(generated_md.is_file())
        self.assertIn("# Generated Documentation", generated_md.read_text(encoding="utf-8"))

        self.assertTrue(api_dir.is_dir())
        self.assertTrue((api_dir / "README.md").is_file())
        # The package's own top-level module must have been documented.
        self.assertTrue((api_dir / "biz.dfch.specmgr.md").is_file())

    def test_docs_output_flag_redirects_output(self):
        """Passing --output must write there, untouched real docs/ directory."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_docs_dir = Path(tmp) / "custom"
            docs(output=tmp_docs_dir)
            self._assert_docs_were_written(tmp_docs_dir)

    def test_docs_default_output_writes_into_repo_docs_dir(self):
        """With no --output, docs() must fall back to the module's _DOCS_DIR constant."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_docs_dir = Path(tmp) / "docs"
            with mock.patch.object(docs_module, "_DOCS_DIR", tmp_docs_dir):
                docs()
            self._assert_docs_were_written(tmp_docs_dir)

    def test_docs_output_option_defaults_to_none(self):
        """The --output CLI parameter must default to None (mapped to _DOCS_DIR internally)."""
        import inspect

        params = inspect.signature(docs).parameters
        self.assertIn("output", params)
        self.assertIsNone(params["output"].default)


class TestGenerateApiDocs(unittest.TestCase):
    """Tests for the ``_generate_api_docs`` helper in isolation."""

    def test_writes_module_files_and_index_for_known_package(self):
        """Must write one .md per importable module plus a grouped README index."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            written, pruned, _paths = _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")

            self.assertGreater(written, 0)
            self.assertEqual(pruned, 0)
            self.assertTrue((api_dir / "biz.dfch.specmgr.commands.md").is_file())
            self.assertTrue((api_dir / "biz.dfch.specmgr.commands.docs.md").is_file())

            index = (api_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("# API Documentation Index", index)
            self.assertIn("biz.dfch.specmgr.commands.docs", index)

    def test_returns_zero_and_writes_no_index_for_unimportable_package(self):
        """An unimportable package name must not blow up, and must skip the index."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            written, pruned, _paths = _generate_api_docs(api_dir, "no_such_package_xyz")

            self.assertEqual(written, 0)
            self.assertEqual(pruned, 0)
            self.assertFalse((api_dir / "README.md").exists())


class TestApiDocsPruning(unittest.TestCase):
    """Tests for the stale-page pruning of ``_generate_api_docs`` and ``docs()``."""

    _STALE_PAGE_NAME = "biz.dfch.specmgr.commands.stale_module.md"

    def _preseed_stale_page(self, api_dir: Path) -> Path:
        api_dir.mkdir(parents=True, exist_ok=True)
        stale = api_dir / self._STALE_PAGE_NAME
        stale.write_text("# stale page\n", encoding="utf-8")
        return stale

    def test_prunes_stale_page_and_keeps_current_pages_and_index(self):
        """A pre-seeded stale page must be deleted; current pages and README.md must remain."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            stale = self._preseed_stale_page(api_dir)

            written, pruned, _paths = _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")

            self.assertGreater(written, 0)
            self.assertEqual(pruned, 1)
            self.assertFalse(stale.exists())
            self.assertTrue((api_dir / "biz.dfch.specmgr.commands.md").is_file())
            self.assertTrue((api_dir / "biz.dfch.specmgr.commands.docs.md").is_file())
            self.assertTrue((api_dir / "README.md").is_file())

    def test_prune_never_deletes_readme_index(self):
        """README.md is excluded from the prune set -- only the stale page may be deleted."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            self._preseed_stale_page(api_dir)

            written, pruned, _paths = _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")

            self.assertGreater(written, 0)
            self.assertEqual(pruned, 1)
            self.assertTrue((api_dir / "README.md").is_file())

    def test_zero_page_run_leaves_preexisting_files_untouched(self):
        """An unimportable package writes no pages and must not delete anything."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            api_dir.mkdir()
            stale = api_dir / "preexisting_stale.md"
            stale.write_text("stale\n", encoding="utf-8")
            readme = api_dir / "README.md"
            readme.write_text("old index\n", encoding="utf-8")
            notes = api_dir / "notes.txt"
            notes.write_text("keep\n", encoding="utf-8")

            written, pruned, _paths = _generate_api_docs(api_dir, "no_such_package_xyz")

            self.assertEqual(written, 0)
            self.assertEqual(pruned, 0)
            self.assertTrue(stale.is_file())
            self.assertEqual(readme.read_text(encoding="utf-8"), "old index\n")
            self.assertTrue(notes.is_file())

    def test_prune_ignores_non_md_files_and_nested_directories(self):
        """Only flat, top-level, file-typed ``*.md`` pages are pruned candidates."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            stale = self._preseed_stale_page(api_dir)
            notes = api_dir / "notes.txt"
            notes.write_text("keep\n", encoding="utf-8")
            nested = api_dir / "nested"
            nested.mkdir()
            nested_stale = nested / "inner_stale.md"
            nested_stale.write_text("keep\n", encoding="utf-8")
            md_dir = api_dir / "stale.md"  # a directory carrying a .md name
            md_dir.mkdir()

            written, pruned, _paths = _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")

            self.assertGreater(written, 0)
            self.assertEqual(pruned, 1)
            self.assertFalse(stale.exists())
            self.assertTrue(notes.is_file())
            self.assertTrue(nested_stale.is_file())
            self.assertTrue(md_dir.is_dir())

    def test_single_module_import_failure_skips_pruning(self):
        """One failed module import (mocked) must skip pruning entirely."""
        with tempfile.TemporaryDirectory() as tmp:
            healthy_api_dir = Path(tmp) / "healthy"
            written_healthy, pruned_healthy, _paths_healthy = _generate_api_docs(
                healthy_api_dir, "biz.dfch.specmgr.commands"
            )
            self.assertGreater(written_healthy, 0)
            self.assertEqual(pruned_healthy, 0)

            api_dir = Path(tmp) / "api"
            stale = self._preseed_stale_page(api_dir)
            real_generate = docs_module._generate_module_markdown

            def failing_generate(module_name: str) -> str | None:
                if module_name == "biz.dfch.specmgr.commands":
                    return None
                return real_generate(module_name)

            with mock.patch.object(docs_module, "_generate_module_markdown", side_effect=failing_generate):
                written, pruned, _paths = _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")

            self.assertEqual(written, written_healthy - 1)
            self.assertEqual(pruned, 0)
            self.assertTrue(stale.is_file())

    def test_double_run_into_same_dir_is_idempotent(self):
        """Two consecutive runs into the same scratch dir must yield identical file sets."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            stale = self._preseed_stale_page(api_dir)

            _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")
            files_after_first_run = sorted(p.name for p in api_dir.iterdir())

            _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")
            files_after_second_run = sorted(p.name for p in api_dir.iterdir())

            self.assertEqual(files_after_first_run, files_after_second_run)
            self.assertNotIn(stale.name, files_after_second_run)
            self.assertIn("README.md", files_after_second_run)

    def test_docs_end_to_end_prunes_and_reports_count(self):
        """docs() with a pre-seeded stale page must prune it and echo the count."""
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp) / "docs"
            api_dir = docs_dir / "api"
            api_dir.mkdir(parents=True)
            stale = api_dir / "biz.dfch.specmgr.stale_module_xyz.md"
            stale.write_text("# stale page\n", encoding="utf-8")

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                docs(output=docs_dir)
            echoed = buffer.getvalue()

            self.assertFalse(stale.exists())
            self.assertRegex(echoed, r"✓ Wrote \d+ module file\(s\) to ")
            self.assertIn("✓ Pruned 1 stale page(s) from", echoed)
            self.assertNotIn("⚠", echoed)


class TestGeneratedMdContent(unittest.TestCase):
    """Tests for the ``docs/GENERATED.md`` content-generation helpers."""

    def test_generate_generated_md_includes_expected_sections(self):
        """Must include the domain, module-reference, and test-coverage headings."""
        output = generate_generated_md()
        self.assertIn("# Generated Documentation", output)
        self.assertIn("## Implemented Domains", output)
        self.assertIn("## Module Reference", output)
        self.assertIn("## Test Coverage", output)
        self.assertIn("**Test files**:", output)

    def test_generate_generated_md_test_count_is_static_and_positive(self):
        """The test-file count is a plain filesystem count, not a subprocess result."""
        output = generate_generated_md()
        count = _count_test_files()
        self.assertGreater(count, 0)
        self.assertIn(f"**Test files**: {count}", output)

    def test_list_domain_packages_finds_models_and_adr_subpackages(self):
        """Must detect 'adr' under models/ and tools/resources/prompts under adr/."""
        domains = _list_domain_packages()
        self.assertIn("models", domains)
        self.assertIn("adr", domains["models"])
        self.assertIn("adr_subpackages", domains)
        self.assertIn("tools", domains["adr_subpackages"])
        self.assertIn("resources", domains["adr_subpackages"])
        self.assertIn("prompts", domains["adr_subpackages"])

    def test_count_mcp_features_matches_known_counts(self):
        """Must count MCP tools/resources under adr/ (11 tools, 1 resource).

        The former ``specmgr://adr/list`` resource was converted into the
        ``list_adr`` tool (feat-13-list-paging Task 2.1), shifting one
        module from ``adr/resources/`` to ``adr/tools/``. The ADR
        ``set_status`` tool module was retired into the generic
        ``set_status`` tool in ``general/tools/`` (feat-22 Phase 4),
        shifting one module the other way.
        """
        features = _count_mcp_features()
        self.assertEqual(features["tools"], 11)
        self.assertEqual(features["resources"], 1)

    def test_collect_module_docs_finds_domains(self):
        """Must collect module docstrings organized by domain."""
        docstrings = _collect_module_docs_by_domain()
        self.assertIn("adr", docstrings)
        self.assertIn("commands", docstrings)
        self.assertIn("models", docstrings)
        self.assertIn("general", docstrings)

    def test_module_reference_lists_known_modules(self):
        """Module reference must list first-line docstrings for known modules."""
        output = generate_module_reference()
        self.assertIn("## Module Reference", output)
        self.assertIn("**adr/**", output)
        self.assertIn("**commands/**", output)
        self.assertIn("adr/tools/", output)
        self.assertIn("get_adr", output)


class TestStableSignatureStr(unittest.TestCase):
    """Regression tests: rendered signatures must be reproducible across runs.

    ``typer.Option(...)``/``typer.Argument(...)`` defaults inside
    ``Annotated[...]`` repr with an embedded object memory address (e.g.
    ``<typer.models.OptionInfo object at 0x7f...>``). Left unstripped, every
    module docs for a Typer command would differ between two runs (or two CI
    machines), permanently breaking the pre-commit hook / CI drift check.
    """

    def test_typer_command_signature_has_no_memory_address(self):
        """A real Typer command (mcp, with Annotated[..., typer.Option(...)]) must be stable."""
        from biz.dfch.specmgr.commands.mcp import mcp

        first = _stable_signature_str(mcp)
        second = _stable_signature_str(mcp)
        self.assertIsNotNone(first)
        self.assertEqual(first, second)
        self.assertNotIn("0x", first)
        self.assertNotIn(" at ", first)

    def test_format_signature_has_no_double_parens(self):
        """``str(inspect.signature(...))`` already includes parens -- must not be re-wrapped."""

        def _example(a: int, b: str = "x") -> None:
            pass

        self.assertEqual(_format_signature(_example), "(a: int, b: str = 'x') -> None")

    def test_stable_signature_str_returns_none_for_uninspectable_callable(self):
        """Callables `inspect.signature` cannot introspect must not raise -- return ``None``."""
        with mock.patch("inspect.signature", side_effect=TypeError("no signature")):
            self.assertIsNone(_stable_signature_str(lambda: None))
        with mock.patch("inspect.signature", side_effect=ValueError("no signature")):
            self.assertEqual(_format_signature(lambda: None), "()")

    def test_docs_own_signature_has_no_leaked_private_pathlib_submodule(self):
        """Regression: Python 3.13 moved Path to pathlib._local -- must render as plain pathlib.Path.

        ``docs()``'s own ``--output: Optional[Path]`` parameter is exactly the
        case that broke: 3.11/3.12 report ``Path.__module__ == "pathlib"``,
        3.13 reports ``"pathlib._local"``, so an un-normalized signature would
        render differently across the CI matrix (3.11/3.12/3.13) for a tree
        that hasn't actually changed.
        """
        rendered = _stable_signature_str(docs)
        self.assertIsNotNone(rendered)
        self.assertIn("pathlib.Path", rendered)
        self.assertNotIn("_local", rendered)

    def test_stable_signature_str_collapses_arbitrary_private_submodule(self):
        """The normalization is generic, not pathlib-specific."""

        class _Fake:
            __module__ = "somepkg._internal"
            __qualname__ = "Thing"
            __name__ = "Thing"

        def _example(x: _Fake) -> None:
            pass

        rendered = _stable_signature_str(_example)
        self.assertIn("somepkg.Thing", rendered)
        self.assertNotIn("_internal", rendered)


_FIXTURE_PACKAGE = "fixture_ruff_format_pkg"
_FIXTURE_MODULE = "block"

#: An SDK-style python block ruff would reformat (one blank line between two
#: top-level defs where ruff wants two), embedded in a method docstring -- the
#: same shape the mcp SDK's ``MCPServer.resource`` Example block has in
#: ``docs/api/biz.dfch.specmgr.server.md`` (feat-221 Phase 100 unblock).
_FIXTURE_MODULE_SOURCE = '''\
"""Fixture module with a ruff-not-clean python block in a method docstring."""


class Fixture:
    """A fixture class."""

    def example(self) -> None:
        """Carries an SDK-style python block that ruff would reformat.

        Example:
            ```python
            @server.resource("resource://a")
            def get_a() -> str:
                return "a"

            @server.resource("resource://b")
            def get_b() -> str:
                return "b"
            ```
        """
'''


def _write_fixture_package(tmp_root: Path) -> None:
    pkg_dir = tmp_root / _FIXTURE_PACKAGE
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text('"""Fixture package for the docs ruff-format tests."""\n', encoding="utf-8")
    (pkg_dir / f"{_FIXTURE_MODULE}.py").write_text(_FIXTURE_MODULE_SOURCE, encoding="utf-8")


@contextlib.contextmanager
def _fixture_on_sys_path(tmp_root: Path) -> Iterator[None]:
    """Put the fixture package's root on ``sys.path``; purge stale fixture modules on entry and exit."""
    stale = [name for name in sys.modules if name == _FIXTURE_PACKAGE or name.startswith(_FIXTURE_PACKAGE + ".")]
    for name in stale:
        del sys.modules[name]
    sys.path.insert(0, str(tmp_root))
    try:
        yield
    finally:
        sys.path.remove(str(tmp_root))
        stale = [name for name in sys.modules if name == _FIXTURE_PACKAGE or name.startswith(_FIXTURE_PACKAGE + ".")]
        for name in stale:
            del sys.modules[name]


class TestDocsRuffFormat(unittest.TestCase):
    """feat-221 unblock: the generator ruff-formats its own markdown output -- one in-place call over every written path, after the writes."""

    def _fixture_page(self, api_dir: Path) -> Path:
        return api_dir / f"{_FIXTURE_PACKAGE}.{_FIXTURE_MODULE}.md"

    def test_generated_page_with_sdk_style_block_is_ruff_clean(self):
        """A fixture docstring embedding a ruff-not-clean python block must come out ruff-clean on disk."""
        ruff = docs_module._find_ruff()
        self.assertIsNotNone(ruff)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _write_fixture_package(tmp_root)
            api_dir = tmp_root / "api"
            with _fixture_on_sys_path(tmp_root):
                written, pruned, paths = _generate_api_docs(api_dir, _FIXTURE_PACKAGE)
                _ruff_format_written_markdown(ruff, paths)

            self.assertEqual(written, 2)
            self.assertEqual(pruned, 0)
            self.assertEqual(len(paths), 3)  # the two pages + the README index
            page = self._fixture_page(api_dir).read_text(encoding="utf-8")
            # formatted shape: two blank lines between the block's two top-level defs
            self.assertIn('return "a"\n\n\n', page)
            # and ruff itself agrees the written page is clean
            check = subprocess.run(
                [str(ruff), "format", "--check", str(self._fixture_page(api_dir))], capture_output=True, check=False
            )
            self.assertEqual(check.returncode, 0)

    def test_ruff_none_writes_rendered_text_verbatim(self):
        """With no resolved ruff binary (ruff=None), the written page keeps the single-blank, unformatted shape."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _write_fixture_package(tmp_root)
            api_dir = tmp_root / "api"
            with _fixture_on_sys_path(tmp_root):
                _written, _pruned, paths = _generate_api_docs(api_dir, _FIXTURE_PACKAGE)
                _ruff_format_written_markdown(None, paths)

            page = self._fixture_page(api_dir).read_text(encoding="utf-8")
            self.assertNotIn('return "a"\n\n\n', page)
            self.assertIn('return "a"\n\n', page)

    def test_two_full_generations_are_byte_identical(self):
        """Two consecutive docs() runs into separate directories must write byte-identical trees."""
        with tempfile.TemporaryDirectory() as tmp:
            first_dir = Path(tmp) / "first"
            second_dir = Path(tmp) / "second"

            docs(output=first_dir)
            docs(output=second_dir)

            first_files = {
                p.relative_to(first_dir).as_posix(): p.read_bytes() for p in first_dir.rglob("*") if p.is_file()
            }
            second_files = {
                p.relative_to(second_dir).as_posix(): p.read_bytes() for p in second_dir.rglob("*") if p.is_file()
            }
            self.assertGreater(len(first_files), 0)
            self.assertEqual(first_files, second_files)

    def test_ruff_missing_warns_once_and_command_succeeds(self):
        """A _find_ruff that resolves nothing must emit one stderr warning and write the docs anyway (no failure)."""
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp) / "docs"
            stderr_buffer = io.StringIO()

            with mock.patch.object(docs_module, "_find_ruff", return_value=None):
                with contextlib.redirect_stderr(stderr_buffer):
                    docs(output=docs_dir)
            stderr = stderr_buffer.getvalue()

            self.assertIn("ruff not found", stderr)
            self.assertIn("specmgr docs", stderr)
            self.assertEqual(stderr.count("ruff not found"), 1)
            self.assertTrue((docs_dir / "GENERATED.md").is_file())
            self.assertTrue((docs_dir / "api" / "README.md").is_file())

    def test_ruff_nonzero_exit_warns_once_and_command_succeeds(self):
        """A non-zero ruff exit must warn once (naming ruff, the exit code, and the first stderr line),
        still succeed, and leave the written files on disk (as ruff left them)."""
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp) / "docs"
            stderr_buffer = io.StringIO()
            failed = subprocess.CompletedProcess(
                args=["ruff", "format"], returncode=3, stdout="", stderr="ruff: simulated failure"
            )

            with mock.patch.object(docs_module.subprocess, "run", return_value=failed) as run_mock:
                with contextlib.redirect_stderr(stderr_buffer):
                    docs(output=docs_dir)
            stderr = stderr_buffer.getvalue()

            # exactly one subprocess call, and it is the single in-place `ruff format <paths...>`
            self.assertEqual(run_mock.call_count, 1)
            args = run_mock.call_args[0][0]
            self.assertEqual(args[0].endswith("ruff"), True)
            self.assertEqual(args[1], "format")
            self.assertIn(str(docs_dir / "GENERATED.md"), args)
            self.assertIn(str(docs_dir / "api" / "README.md"), args)
            self.assertIn(str(docs_dir / "api" / "biz.dfch.specmgr.md"), args)

            self.assertEqual(stderr.count("⚠"), 1)
            self.assertIn("ruff format exited with code 3", stderr)
            self.assertIn("ruff: simulated failure", stderr)
            # the command succeeded and the output files remain on disk (as written)
            self.assertTrue((docs_dir / "GENERATED.md").is_file())
            self.assertTrue((docs_dir / "api" / "README.md").is_file())
            self.assertTrue((docs_dir / "api" / "biz.dfch.specmgr.md").is_file())

    def test_ruff_unrunnable_warns_once_and_command_succeeds(self):
        """A ruff call that raises OSError must warn once (naming ruff), still succeed, and leave the written
        files intact (as written)."""
        with tempfile.TemporaryDirectory() as tmp:
            docs_dir = Path(tmp) / "docs"
            stderr_buffer = io.StringIO()

            with mock.patch.object(docs_module.subprocess, "run", side_effect=PermissionError("ruff: not executable")):
                with contextlib.redirect_stderr(stderr_buffer):
                    docs(output=docs_dir)
            stderr = stderr_buffer.getvalue()

            self.assertIn("ruff format could not be run", stderr)
            self.assertIn("ruff", stderr)
            self.assertEqual(stderr.count("⚠"), 1)
            # the command succeeded and the output files remain on disk (as written)
            self.assertTrue((docs_dir / "GENERATED.md").is_file())
            self.assertTrue((docs_dir / "api" / "README.md").is_file())
            self.assertTrue((docs_dir / "api" / "biz.dfch.specmgr.md").is_file())


if __name__ == "__main__":
    unittest.main()
