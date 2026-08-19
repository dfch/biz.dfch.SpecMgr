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
"""

import importlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.commands.docs import (
    _collect_module_docs_by_domain,
    _count_mcp_features,
    _count_test_files,
    _format_signature,
    _generate_api_docs,
    _list_domain_packages,
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
            count = _generate_api_docs(api_dir, "biz.dfch.specmgr.commands")

            self.assertGreater(count, 0)
            self.assertTrue((api_dir / "biz.dfch.specmgr.commands.md").is_file())
            self.assertTrue((api_dir / "biz.dfch.specmgr.commands.docs.md").is_file())

            index = (api_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("# API Documentation Index", index)
            self.assertIn("biz.dfch.specmgr.commands.docs", index)

    def test_returns_zero_and_writes_no_index_for_unimportable_package(self):
        """An unimportable package name must not blow up, and must skip the index."""
        with tempfile.TemporaryDirectory() as tmp:
            api_dir = Path(tmp) / "api"
            count = _generate_api_docs(api_dir, "no_such_package_xyz")

            self.assertEqual(count, 0)
            self.assertFalse((api_dir / "README.md").exists())


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
        """Must count MCP tools/resources under adr/ (12 tools, 1 resource).

        The former ``specmgr://adr/list`` resource was converted into the
        ``list_adr`` tool (feat-13-list-paging Task 2.1), shifting one
        module from ``adr/resources/`` to ``adr/tools/``.
        """
        features = _count_mcp_features()
        self.assertEqual(features["tools"], 12)
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


if __name__ == "__main__":
    unittest.main()
