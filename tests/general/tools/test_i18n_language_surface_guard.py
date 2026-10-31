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

"""ACC-013 over the WHOLE registered ``language`` surface (feat-197-i18n Phase 150, Task 150.100).

The per-tool modules pin the path-injection rejection tool by tool; this module closes the loop from the other end:
it discovers every registered tool, prompt and resource template that accepts a ``language`` (by introspecting the
live ``mcp`` app, so a future language-carrying surface is covered the moment it is registered) and asserts that a
path-injection payload as ``language`` is rejected with an actionable ``ValueError`` **before any filesystem access** --
the docs directory the call is pointed at is never created, read or listed (REQ-008, ACC-013).
"""

from __future__ import annotations

import asyncio
import inspect
import os
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest import mock

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.server import mcp

#: Path-injection and malformed shapes (REQ-008): traversal, separators, absolute paths, case, length, digits, empty.
_PAYLOADS = ("../../etc", "de/x", "/abs", "..", "DE", "d", "deu", "d1", "")

_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"

#: Values for every non-``language`` parameter any language-carrying surface takes.
_ARGUMENTS: dict[str, Any] = {
    "id": _ID,
    "content": "# x\n",
    "raw": False,
    "status": "draft",
    "classification": "internal",
    "old_str": "a",
    "new_str": "b",
    "type": "dec",
    "source_language": "en",
}


def _call_with(function: Callable[..., Any], language: str) -> Any:
    """Call ``function`` with filler values for every parameter and ``language`` as given."""
    kwargs: dict[str, Any] = {}
    for name, parameter in inspect.signature(function).parameters.items():
        if name == "language":
            kwargs[name] = language
        elif name in _ARGUMENTS:
            kwargs[name] = _ARGUMENTS[name]
        elif parameter.default is inspect.Parameter.empty:
            raise AssertionError(
                f"no filler for required parameter {name!r} of {function.__module__}.{function.__name__}"
            )
    result = function(**kwargs)
    return result


class TestEveryLanguageCarryingSurfaceGuardsBeforeTheFilesystem(unittest.TestCase):
    """The discovered surface is guarded: nothing is created, read or listed for a rejected ``language``."""

    @classmethod
    def setUpClass(cls) -> None:
        tools = asyncio.run(mcp.list_tools())
        cls.tool_functions = {
            tool.name: mcp._tool_manager.get_tool(tool.name).fn
            for tool in tools
            if "language" in (tool.input_schema.get("properties") or {})
        }
        prompts = asyncio.run(mcp.list_prompts())
        cls.prompt_functions = {
            prompt.name: mcp._prompt_manager.get_prompt(prompt.name).fn
            for prompt in prompts
            if any(argument.name == "language" for argument in prompt.arguments or [])
        }
        cls.template_functions = {
            str(template.uri_template): template.fn
            for template in mcp._resource_manager.list_templates()
            if "{language}" in str(template.uri_template)
        }

    def setUp(self) -> None:
        self.parent = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.docs_root = self.parent / "never-created"
        self.enterContext(mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: str(self.docs_root)}))

    def assert_untouched(self) -> None:
        self.assertFalse(self.docs_root.exists(), "a rejected language created the docs directory")
        self.assertEqual(list(self.parent.iterdir()), [])

    def test_the_discovered_surface_is_the_expected_size(self):
        self.assertEqual(len(self.tool_functions), 42)
        self.assertEqual(set(self.prompt_functions), {"translate_artifact"})
        self.assertEqual(set(self.template_functions), {"specmgr://i18n/headings/{language}"})

    def test_every_language_carrying_tool_rejects_every_payload_before_any_filesystem_access(self):
        for name, function in sorted(self.tool_functions.items()):
            for payload in _PAYLOADS:
                with self.subTest(tool=name, language=payload):
                    with self.assertRaises(ValueError) as context:
                        _call_with(function, payload)
                    self.assertIn("language", str(context.exception).lower())
                    self.assert_untouched()

    def test_the_translate_prompt_rejects_every_payload_for_both_language_arguments(self):
        function = self.prompt_functions["translate_artifact"]
        # the prompt (documented) matches the language case-insensitively and renders only the lowercase form, so an
        # uppercase two-letter code is normalized -- not a path-injection shape; every other payload is rejected
        for payload in (p for p in _PAYLOADS if p != "DE"):
            with self.subTest(language=payload):
                with self.assertRaises(ValueError):
                    function("dec", _ID, payload)
                with self.assertRaises(ValueError):
                    function("dec", _ID, "de", payload)
                self.assert_untouched()

    def test_the_translate_prompt_only_ever_renders_the_normalized_lowercase_language(self):
        rendered = self.prompt_functions["translate_artifact"]("dec", _ID, "DE")

        self.assertIn('language="de"', rendered)
        self.assertNotIn('language="DE"', rendered)
        self.assert_untouched()

    def test_the_headings_resource_template_rejects_every_payload_before_the_table_loader(self):
        function = self.template_functions["specmgr://i18n/headings/{language}"]
        for payload in _PAYLOADS:
            with self.subTest(language=payload):
                with mock.patch(
                    "biz.dfch.specmgr.general.models.heading_table.load_heading_table",
                    side_effect=AssertionError("the loader was reached with an unvalidated language"),
                ):
                    with self.assertRaises(ValueError):
                        function(payload)
                self.assert_untouched()

    def test_the_two_read_only_translation_tools_without_a_language_parameter_still_validate_their_inputs(self):
        """``list_languages`` takes no ``language``: it never builds a path from caller text but the id/type."""
        list_languages = mcp._tool_manager.get_tool("list_languages").fn

        with self.assertRaises(ValueError):
            list_languages("dec", "../../etc/passwd")
        self.assert_untouched()


if __name__ == "__main__":
    unittest.main()
