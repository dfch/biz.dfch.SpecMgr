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

"""Tests for the ``mcp-docs`` command.

Mirrors ``tests/commands/test_docs.py``'s approach: exercise the actual
``mcp_docs()`` Typer entry point and assert on the file it writes -- once
via its ``--output`` parameter, and once via its default (patching the
module's ``_DEFAULT_OUTPUT`` constant so the default branch is covered
without touching the real ``docs/`` tree). This is deliberate: an earlier
version of this module resolved ``_DEFAULT_OUTPUT`` one parent directory
too shallow (``src/docs/MCP.md`` instead of ``docs/MCP.md``), a bug the
private-helper-only test style ``test_docs.py``'s docstring warns about
would not have caught.
"""

import importlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.commands.mcp_docs import (
    _schema_type_str,
    _slugify,
    _tool_parameters,
    generate_mcp_docs,
    mcp_docs,
)

# `commands/__init__.py` does `from .mcp_docs import mcp_docs`, which rebinds
# the `mcp_docs` attribute on the `commands` package to the function itself
# -- so `import biz.dfch.specmgr.commands.mcp_docs as x` would resolve `x` to
# that function, not the submodule. Go through `importlib` to get the real
# module (needed below to patch its `_DEFAULT_OUTPUT` constant).
mcp_docs_module = importlib.import_module("biz.dfch.specmgr.commands.mcp_docs")


class TestMcpDocsEntryPoint(unittest.TestCase):
    """Tests for the ``mcp_docs()`` Typer entry point -- the actual write path."""

    def _assert_docs_were_written(self, output_path: Path) -> None:
        self.assertTrue(output_path.is_file())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("# MCP Server Reference", content)
        self.assertIn("## Resources", content)
        self.assertIn("## Resource Templates", content)
        self.assertIn("## Tools", content)
        self.assertIn("## Prompts", content)
        # A resource/tool known to always be registered (cross-cutting, not tied
        # to any one domain going away): version resource, mdformat tool.
        self.assertIn("specmgr://version", content)
        self.assertIn("### Tool: mdformat", content)

    def test_mcp_docs_output_flag_redirects_output(self):
        """Passing --output must write there, untouched real docs/ directory."""
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "custom" / "MCP.md"
            mcp_docs(output=output_path)
            self._assert_docs_were_written(output_path)

    def test_mcp_docs_default_output_writes_into_repo_docs_dir(self):
        """With no --output, mcp_docs() must fall back to the module's _DEFAULT_OUTPUT constant."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_output_path = Path(tmp) / "docs" / "MCP.md"
            with mock.patch.object(mcp_docs_module, "_DEFAULT_OUTPUT", tmp_output_path):
                mcp_docs()
            self._assert_docs_were_written(tmp_output_path)

    def test_mcp_docs_output_option_defaults_to_none(self):
        """The --output CLI parameter must default to None (mapped to _DEFAULT_OUTPUT internally)."""
        import inspect

        params = inspect.signature(mcp_docs).parameters
        self.assertIn("output", params)
        self.assertIsNone(params["output"].default)

    def test_default_output_resolves_under_repo_root_not_src(self):
        """Regression guard: _DEFAULT_OUTPUT must be docs/MCP.md at the repo root, not under src/."""
        self.assertEqual(mcp_docs_module._DEFAULT_OUTPUT.name, "MCP.md")
        self.assertEqual(mcp_docs_module._DEFAULT_OUTPUT.parent.name, "docs")
        # The repo root must contain pyproject.toml -- src/ never does.
        self.assertTrue((mcp_docs_module._REPO_ROOT / "pyproject.toml").is_file())


class TestGenerateMcpDocs(unittest.TestCase):
    """Tests for ``generate_mcp_docs`` in isolation (no file I/O)."""

    def test_output_is_deterministic_across_calls(self):
        """Two back-to-back calls must produce byte-identical output (stable sort order)."""
        first = generate_mcp_docs()
        second = generate_mcp_docs()
        self.assertEqual(first, second)

    def test_ends_with_single_trailing_newline(self):
        """Output must end with exactly one trailing newline, not zero or two."""
        content = generate_mcp_docs()
        self.assertTrue(content.endswith("\n"))
        self.assertFalse(content.endswith("\n\n"))

    def test_anchors_stay_unique_across_kinds_with_same_name(self):
        """create_adr exists as both a tool and a prompt; their headings/anchors must differ."""
        content = generate_mcp_docs()
        self.assertIn("### Tool: create_adr", content)
        self.assertIn("### Prompt: create_adr", content)
        self.assertIn("(#tool-create_adr)", content)
        self.assertIn("(#prompt-create_adr)", content)


class TestSchemaTypeStr(unittest.TestCase):
    """Tests for the ``_schema_type_str`` JSON Schema -> short type string helper."""

    def test_plain_type(self):
        """A plain ``{"type": "string"}`` schema renders as its bare type name."""
        self.assertEqual(_schema_type_str({"type": "string"}), "string")

    def test_ref_resolves_to_bare_name(self):
        """A ``$ref`` schema resolves to the referenced definition's bare name."""
        self.assertEqual(_schema_type_str({"$ref": "#/$defs/AdrBody"}), "AdrBody")

    def test_any_of_with_null_becomes_none_union(self):
        """An ``anyOf: [T, null]`` union (optional field) renders as ``T | None``."""
        schema = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        self.assertEqual(_schema_type_str(schema), "string | None")

    def test_array_becomes_list_of_item_type(self):
        """An ``array`` schema renders as ``list[<item type>]``."""
        schema = {"type": "array", "items": {"type": "integer"}}
        self.assertEqual(_schema_type_str(schema), "list[integer]")

    def test_unrecognized_shape_falls_back_to_any(self):
        """An empty/unrecognized schema shape falls back to ``"any"`` rather than raising."""
        self.assertEqual(_schema_type_str({}), "any")

    def test_enum_renders_base_type_plus_values(self):
        """A closed ``enum`` property renders as ``T (enum: v1, v2, ...)`` -- the values are contract."""
        schema = {
            "type": "string",
            "enum": ["req", "uc", "tsk", "qa", "prb", "gol", "rsk"],
        }
        self.assertEqual(_schema_type_str(schema), "string (enum: req, uc, tsk, qa, prb, gol, rsk)")


class TestToolParameters(unittest.TestCase):
    """Tests for the ``_tool_parameters`` top-level input-schema extractor."""

    def test_extracts_name_type_and_required_flag(self):
        """Each top-level property must yield a (name, type, required) tuple."""
        input_schema = {
            "properties": {
                "id": {"type": "string"},
                "value": {"anyOf": [{"type": "string"}, {"type": "null"}]},
            },
            "required": ["id"],
        }
        result = _tool_parameters(input_schema)
        self.assertIn(("id", "string", True), result)
        self.assertIn(("value", "string | None", False), result)

    def test_no_properties_returns_empty_list(self):
        """A schema with no ``properties`` key must yield an empty list, not raise."""
        self.assertEqual(_tool_parameters({}), [])


class TestSlugify(unittest.TestCase):
    """Tests for the ``_slugify`` GitHub-style heading slug helper."""

    def test_lowercases_and_replaces_spaces_with_hyphens(self):
        """A kind-prefixed heading lowercases and turns spaces into hyphens."""
        self.assertEqual(_slugify("Tool: create_adr"), "tool-create_adr")

    def test_strips_punctuation_but_keeps_underscores_and_hyphens(self):
        """Punctuation (``:``, ``/``, ``!``) is dropped; underscores/hyphens survive."""
        self.assertEqual(_slugify("Resource: adr/list!"), "resource-adrlist")
