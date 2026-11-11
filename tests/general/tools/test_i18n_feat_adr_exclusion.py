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

"""Registered-surface and behavioral regression tests for the permanent ``feat`` i18n exclusion
(feat-197-i18n Phase 150, Task 150.100; REQ-002/ACC-002, DEC 38efdb66 item 10).

``tests/general/tools/test_language_guard.py`` pins the *Python signatures* of a handful of ``feat`` tool
functions. This module pins the *registered MCP surface* itself -- the tools, prompts, resources and resource
templates the live ``mcp`` app actually exposes -- so the exclusion holds for what a client sees, not only for what a
function signature says:

- the set of registered tools carrying a ``language`` input property is *exactly* the intended one (the thirteen
  domains' ``get_<d>``/``list_<d>``/``create_<d>``, the five generic write tools, and ``check_translation_drift``) --
  a new ``language`` parameter anywhere else fails here;
- every tool/prompt/resource whose implementing function lives in the ``feat`` domain package has no
  ``language`` parameter, argument, or URI segment;
- the only prompt with a ``language`` argument is the cross-cutting ``translate_artifact``, the only resource
  template with a ``{language}`` placeholder is ``specmgr://i18n/headings/{language}``;
- behaviorally: ``feat`` operations with their unchanged arguments never create, read, or list a
  ``{language}``-shaped path (``docs/feat/{language}``, ``<base>/<id>/{language}``).
"""

from __future__ import annotations

import asyncio
import inspect
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.feat.tools.set_feat_id import set_feat_id
from biz.dfch.specmgr.general.models import ParseFailureResult
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS
from biz.dfch.specmgr.server import mcp

from ._reference_graph_helpers import _reset_caches
from ._similarity_helpers import _FEAT_MINIMAL_BODY

#: The ``language`` parameter's name (and the placeholder spelling in a URI template).
_LANGUAGE = "language"

#: The tools that legitimately carry a ``language`` input property: per language-aware domain the read pair and the
#: create tool, the five generic write tools, and the drift checker (``list_languages`` takes only ``type``/``id``).
_EXPECTED_LANGUAGE_TOOLS: frozenset[str] = frozenset(
    {f"{verb}_{domain}" for domain in LANGUAGE_AWARE_DOMAINS for verb in ("get", "list", "create")}
    | {"update", "edit", "set_status", "set_classification", "delete", "check_translation_drift"}
)

#: Every ``feat``-specific tool the surface registers (``create_feat`` ... ``get_feat_schema``), by name.
_FEAT_TOOLS: frozenset[str] = frozenset(
    {
        "create_feat",
        "set_feat_id",
        "parse_feat",
        "list_feat",
        "get_feat",
        "get_feat_example",
        "get_feat_template",
        "get_feat_schema",
    }
)

_FEAT_PROMPTS: frozenset[str] = frozenset({"create_feat", "update_feat"})

#: The module-path prefix that identifies a ``feat`` implementing function.
_FEAT_PACKAGE = "biz.dfch.specmgr.feat."


def _owned_by(function: object, package_prefix: str) -> bool:
    """Whether ``function`` is implemented in the domain package named by ``package_prefix``."""
    result = getattr(function, "__module__", "").startswith(package_prefix)
    return result


class _SurfaceTestCase(unittest.TestCase):
    """Loads the live registered surface once: tool schemas, prompts, resources and resource templates."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}
        cls.prompts = {prompt.name: prompt for prompt in asyncio.run(mcp.list_prompts())}
        cls.resources = list(mcp._resource_manager.list_resources())
        cls.templates = list(mcp._resource_manager.list_templates())

    @classmethod
    def tool_function(cls, name: str) -> object:
        """The Python function implementing the registered tool ``name``."""
        result = mcp._tool_manager.get_tool(name).fn
        return result

    @classmethod
    def prompt_function(cls, name: str) -> object:
        """The Python function implementing the registered prompt ``name``."""
        result = mcp._prompt_manager.get_prompt(name).fn
        return result


class TestRegisteredToolSurface(_SurfaceTestCase):
    """ACC-002 for tools: no ``feat`` tool carries ``language``; the carrier set is exact."""

    def test_the_tools_with_a_language_input_property_are_exactly_the_intended_set(self):
        """45 tools: 13 domains x (get/list/create) + the five generic write tools + ``check_translation_drift``."""
        carriers = {
            name for name, tool in self.tools.items() if _LANGUAGE in (tool.input_schema.get("properties") or {})
        }

        self.assertEqual(len(_EXPECTED_LANGUAGE_TOOLS), 45)
        self.assertEqual(carriers - _EXPECTED_LANGUAGE_TOOLS, set(), "a tool gained an unplanned language parameter")
        self.assertEqual(_EXPECTED_LANGUAGE_TOOLS - carriers, set(), "a planned language parameter is missing")

    def test_language_is_never_a_required_input(self):
        """Omitting ``language`` must stay valid for every carrier (REQ-006/REQ-007: optional, default ``en``)."""
        for name in sorted(_EXPECTED_LANGUAGE_TOOLS - {"check_translation_drift"}):
            with self.subTest(tool=name):
                schema = self.tools[name].input_schema
                self.assertNotIn(_LANGUAGE, schema.get("required", []))
                self.assertEqual(schema["properties"][_LANGUAGE].get("default"), "en")

    def test_the_feat_specific_tools_are_all_registered(self):
        """The by-name list below is not stale: every listed tool is registered, and so is nothing else owned by feat."""
        for name in sorted(_FEAT_TOOLS):
            with self.subTest(tool=name):
                self.assertIn(name, self.tools)
        owned_feat = {n for n in self.tools if _owned_by(self.tool_function(n), _FEAT_PACKAGE)}
        self.assertEqual(owned_feat, _FEAT_TOOLS)

    def test_no_feat_tool_has_a_language_parameter_in_schema_or_signature(self):
        for name in sorted(_FEAT_TOOLS):
            with self.subTest(tool=name):
                self.assertNotIn(_LANGUAGE, self.tools[name].input_schema.get("properties") or {})
                self.assertNotIn(_LANGUAGE, inspect.signature(self.tool_function(name)).parameters)

    def test_no_property_of_a_feat_tool_mentions_a_language_at_all(self):
        """Also no ``lang``-ish alias (``locale``, ``lang``, ``source_language``): the exclusion is by meaning."""
        pattern = re.compile(r"lang|locale", re.IGNORECASE)
        for name in sorted(_FEAT_TOOLS):
            with self.subTest(tool=name):
                for prop in self.tools[name].input_schema.get("properties") or {}:
                    self.assertIsNone(pattern.search(prop), prop)

    def test_the_type_enums_of_the_generic_tools_still_accept_feat_only_to_reject_it_actionably(self):
        """``feat`` stays in the ``type`` enum of the language-aware generic tools so a caller gets the
        permanent explanation instead of a bare schema error (the guard tests pin the wording)."""
        for name in ("check_translation_drift", "list_languages"):
            with self.subTest(tool=name):
                enum = self.tools[name].input_schema["properties"]["type"]["enum"]
                self.assertIn("feat", enum)


class TestRegisteredPromptSurface(_SurfaceTestCase):
    """ACC-002/ACC-015 for prompts."""

    def test_the_only_prompt_with_a_language_argument_is_translate_artifact(self):
        carriers = {
            name
            for name, prompt in self.prompts.items()
            if any(argument.name in (_LANGUAGE, "source_language") for argument in (prompt.arguments or []))
        }

        self.assertEqual(carriers, {"translate_artifact"})

    def test_no_feat_prompt_has_a_language_argument(self):
        for name in sorted(_FEAT_PROMPTS):
            with self.subTest(prompt=name):
                self.assertIn(name, self.prompts)
                self.assertNotIn(_LANGUAGE, {argument.name for argument in self.prompts[name].arguments or []})
                self.assertNotIn(_LANGUAGE, inspect.signature(self.prompt_function(name)).parameters)

    def test_the_by_name_list_covers_every_prompt_owned_by_feat(self):
        owned_feat = {n for n in self.prompts if _owned_by(self.prompt_function(n), _FEAT_PACKAGE)}
        self.assertEqual(owned_feat, _FEAT_PROMPTS)


class TestRegisteredResourceSurface(_SurfaceTestCase):
    """ACC-002/ACC-015 for resources and resource templates."""

    def test_the_only_resource_template_with_a_language_placeholder_is_the_headings_template(self):
        placeholders = {str(t.uri_template) for t in self.templates if "{" + _LANGUAGE + "}" in str(t.uri_template)}

        self.assertEqual(placeholders, {"specmgr://i18n/headings/{language}"})

    def test_no_static_resource_uri_encodes_a_language(self):
        for resource in self.resources:
            with self.subTest(uri=str(resource.uri)):
                self.assertNotIn(_LANGUAGE, str(resource.uri))

    def test_no_feat_resource_or_template_has_a_language_segment_or_parameter(self):
        """Every resource whose function lives in ``feat``, and every ``specmgr://feat/...`` URI."""
        seen = 0
        for resource in self.resources:
            uri = str(resource.uri)
            owned = _owned_by(resource.fn, _FEAT_PACKAGE)
            if owned or uri.startswith("specmgr://feat/"):
                seen += 1
                with self.subTest(uri=uri):
                    self.assertNotIn(_LANGUAGE, uri)
                    self.assertNotIn(_LANGUAGE, inspect.signature(resource.fn).parameters)
        for template in self.templates:
            uri = str(template.uri_template)
            owned = _owned_by(template.fn, _FEAT_PACKAGE)
            if owned or uri.startswith("specmgr://feat/"):
                seen += 1
                with self.subTest(uri=uri):
                    self.assertNotIn(_LANGUAGE, uri)
                    self.assertNotIn(_LANGUAGE, inspect.signature(template.fn).parameters)
        self.assertGreaterEqual(seen, 2, "the feat example/template resources were not found")


class _IsolatedRegistryTestCase(unittest.TestCase):
    """Isolated docs/feat directories with every per-domain cache reset around each test."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.feat_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(
            mock.patch.dict(
                os.environ,
                {
                    DOCS_DIR_ENV_VAR: str(self.docs_root),
                    FEAT_DIR_ENV_VAR: str(self.feat_dir),
                },
            )
        )
        _reset_caches()
        self.addCleanup(_reset_caches)

    @staticmethod
    def relative_files(root: Path) -> set[str]:
        """Every file below ``root`` as a POSIX relative path."""
        result = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        return result

    @staticmethod
    def relative_dirs(root: Path) -> set[str]:
        """Every directory below ``root`` as a POSIX relative path."""
        result = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()}
        return result


class TestFeatBehaviorIsUnchanged(_IsolatedRegistryTestCase):
    """ACC-002 behavioral half: ``feat`` keeps its folder-per-document layout and never touches a language path."""

    _ID = "feat-197-regress"
    _RENAMED = "feat-197-renamed"

    def test_create_get_list_and_rename_use_only_the_folder_per_document_layout(self):
        created = create_feat(_FEAT_MINIMAL_BODY, id=self._ID)
        self.assertEqual(created.id, self._ID)
        self.assertEqual(self.relative_files(self.feat_dir), {f"{self._ID}/README.md"})
        self.assertEqual(get_feat(self._ID).frontmatter.id, self._ID)
        self.assertEqual([row.id for row in list_feat().results], [self._ID])

        renamed = set_feat_id(self._ID, self._RENAMED)

        self.assertEqual(renamed.id, self._RENAMED)
        self.assertEqual(self.relative_files(self.feat_dir), {f"{self._RENAMED}/README.md"})
        self.assertEqual(self.relative_dirs(self.feat_dir), {self._RENAMED})
        # nothing language-shaped anywhere under the feat base, and the docs root never grew a feat/ tree
        self.assertFalse([d for d in self.relative_dirs(self.feat_dir) if re.search(r"(^|/)[a-z]{2}(/|$)", d)])
        self.assertEqual(self.relative_dirs(self.docs_root), set())
        self.assertFalse((self.docs_root / "feat").exists())

    def test_a_language_shaped_path_below_a_feature_folder_is_never_read_or_listed(self):
        create_feat(_FEAT_MINIMAL_BODY, id=self._ID)
        en_title = "Feature: Example Widget"
        variant_dir = self.feat_dir / self._ID / "de"
        variant_dir.mkdir()
        (variant_dir / "README.md").write_text(
            (self.feat_dir / self._ID / "README.md").read_text(encoding="utf-8").replace(en_title, "Merkmal: Deutsch"),
            encoding="utf-8",
        )
        _reset_caches()

        document = get_feat(self._ID)
        rows = list_feat()

        self.assertNotIsInstance(document, ParseFailureResult)
        self.assertEqual(document.frontmatter.id, self._ID)
        self.assertIn(en_title, get_feat(self._ID, raw=True))
        self.assertEqual([row.id for row in rows.results], [self._ID])
        self.assertEqual(rows.total, 1)
        self.assertEqual(get_feat(self._ID, raw=True).count("Merkmal: Deutsch"), 0)

    def test_a_language_shaped_docs_tree_is_never_consulted_by_feat(self):
        """``docs/feat/de/`` (the shape REQ-001 would give ``feat``) is ignored: ``feat`` reads ``SPECMGR_FEAT_DIR``."""
        (self.docs_root / "feat" / "de").mkdir(parents=True)
        (self.docs_root / "feat" / "de" / f"{self._ID}.md").write_text(_FEAT_MINIMAL_BODY, encoding="utf-8")
        create_feat(_FEAT_MINIMAL_BODY, id=self._ID)

        self.assertEqual([row.id for row in list_feat().results], [self._ID])
        self.assertEqual(get_feat(self._ID).frontmatter.id, self._ID)

    def test_the_feat_tools_reject_a_language_keyword(self):
        """No ``language`` parameter exists to be passed: a direct call is a ``TypeError``, nothing is written."""
        with self.assertRaises(TypeError):
            create_feat(_FEAT_MINIMAL_BODY, id=self._ID, language="de")  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            get_feat(self._ID, language="de")  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            list_feat(language="de")  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            set_feat_id(self._ID, self._RENAMED, language="de")  # type: ignore[call-arg]
        self.assertEqual(self.relative_files(self.feat_dir), set())


if __name__ == "__main__":
    unittest.main()
