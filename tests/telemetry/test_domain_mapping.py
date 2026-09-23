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

"""Tests for ``telemetry/domain_mapping.py`` (feat-139-logging-telemetry, Phase 5, Task 5.1/5.6).

The Task 5.1 explicit name/uri -> domain mapping behind the ``mcp.domain``
attribute (and the log records' ``domain`` extra): the generic dispatch
tools via their own ``type`` argument, the domain-specific tools and
prompts via their registered name, the resources via their ``uri``'s first
path segment, and the no-domain case yielding ``None`` (the attribute is
then omitted entirely, never an empty string).

The live-registration drift test (Task 5.6's "how is the mapping's
coverage tested") imports the real ``server`` module and asserts the
static tables match what ``server.py`` actually registers in both
directions: no registered tool/prompt may go unmapped, and no table entry
may name an unregistered tool/prompt (the tables must not grow stale as
items are added/removed/renamed).
"""

import asyncio
import importlib
import logging
import os
import types
import unittest
from unittest import mock

from biz.dfch.specmgr.telemetry import domain_mapping

# A representative sample per domain of the edge-case names the explicit
# (non-heuristic) tables exist for -- every one of these maps to its
# domain even though its registered name does not contain the domain name.
_EDGE_CASE_TOOLS = (
    ("create_adr", "adr"),
    ("option_list", "adr"),
    ("validate_adr", "adr"),
    ("set_feat_id", "feat"),
    ("create_dec", "dec"),
    ("get_sysrs", "sysrs"),
)
_EDGE_CASE_PROMPTS = (
    ("create_adr_test", "adr"),
    ("update_adr_test", "adr"),
    ("refine", "qa"),
    ("create_task", "tsk"),
    ("implement_task", "tsk"),
    ("update_task", "tsk"),
    ("create_risk", "rsk"),
    ("update_risk", "rsk"),
)
_NO_DOMAIN_TOOLS = ("mdformat",)
_NO_DOMAIN_PROMPTS = ("compact_history",)
_NO_DOMAIN_RESOURCES = (
    "specmgr://version",
    "specmgr://config",
    "specmgr://iso25010",
    "specmgr://dtais",
    "specmgr://ears",
    "specmgr://rasci",
    "specmgr://telemetry/status",
)
_DOMAIN_RESOURCES = (
    ("specmgr://req/schema", "req"),
    ("specmgr://uc/example", "uc"),
    ("specmgr://tsk/template", "tsk"),
    ("specmgr://qa/schema", "qa"),
    ("specmgr://prb/example", "prb"),
    ("specmgr://gol/template", "gol"),
    ("specmgr://rsk/schema", "rsk"),
    ("specmgr://rsk/tara", "rsk"),
    ("specmgr://rsk/risk-matrix", "rsk"),
    ("specmgr://dec/example", "dec"),
    ("specmgr://sop/template", "sop"),
    ("specmgr://feat/schema", "feat"),
    ("specmgr://vcr/example", "vcr"),
    ("specmgr://sysrs/template", "sysrs"),
    # the parameterized ADR resource template and a concrete read of it:
    ("specmgr://adr/{id}", "adr"),
    ("specmgr://adr/00000000-0000-4000-8000-000000000000", "adr"),
)
_GENERIC_DISPATCH_TOOLS = tuple(sorted(domain_mapping.GENERIC_DISPATCH_TOOLS))


class TestToolDomainMapping(unittest.TestCase):
    """Domain-specific tools map by registered name; the no-domain case yields None."""

    def test_every_domain_tool_maps_to_its_domain(self):
        sut = domain_mapping.item_domain
        for name, expected_domain in _EDGE_CASE_TOOLS:
            self.assertEqual(sut("tool", name), expected_domain, name)

    def test_every_table_entry_maps_to_a_registered_domain(self):
        for name, expected_domain in domain_mapping._TOOL_DOMAINS.items():
            self.assertIn(expected_domain, domain_mapping.DOMAINS, name)
            self.assertEqual(domain_mapping.item_domain("tool", name), expected_domain, name)

    def test_every_domain_has_tools_in_the_table(self):
        self.assertEqual(set(domain_mapping._TOOL_DOMAINS.values()), domain_mapping.DOMAINS)

    def test_the_no_domain_tool_maps_to_none(self):
        sut = domain_mapping.item_domain
        for name in _NO_DOMAIN_TOOLS:
            self.assertIsNone(sut("tool", name), name)

    def test_an_unknown_tool_name_maps_to_none(self):
        self.assertIsNone(domain_mapping.item_domain("tool", "a_future_tool_that_is_not_mapped_yet"))


class TestPromptDomainMapping(unittest.TestCase):
    """Prompts map by registered name (the irregular names are the point)."""

    def test_every_prompt_maps_to_its_domain(self):
        sut = domain_mapping.item_domain
        for name, expected_domain in _EDGE_CASE_PROMPTS:
            self.assertEqual(sut("prompt", name), expected_domain, name)

    def test_every_table_entry_maps_to_a_registered_domain(self):
        for name, expected_domain in domain_mapping._PROMPT_DOMAINS.items():
            self.assertIn(expected_domain, domain_mapping.DOMAINS, name)
            self.assertEqual(domain_mapping.item_domain("prompt", name), expected_domain, name)

    def test_the_no_domain_prompt_maps_to_none(self):
        sut = domain_mapping.item_domain
        for name in _NO_DOMAIN_PROMPTS:
            self.assertIsNone(sut("prompt", name), name)

    def test_a_tool_name_is_not_matched_against_the_prompt_table_and_vice_versa(self):
        self.assertIsNone(domain_mapping.item_domain("prompt", "get_req"))
        self.assertIsNone(domain_mapping.item_domain("tool", "update_req"))


class TestResourceDomainMapping(unittest.TestCase):
    """Resources map by their uri's first path segment (never a name argument)."""

    def test_every_domain_resource_maps_to_its_domain(self):
        sut = domain_mapping.resource_domain
        for uri, expected_domain in _DOMAIN_RESOURCES:
            self.assertEqual(sut(uri), expected_domain, uri)
            self.assertEqual(domain_mapping.item_domain("resource", uri), expected_domain, uri)

    def test_the_no_domain_resources_map_to_none(self):
        sut = domain_mapping.resource_domain
        for uri in _NO_DOMAIN_RESOURCES:
            self.assertIsNone(sut(uri), uri)

    def test_a_non_specmgr_uri_maps_to_none(self):
        self.assertIsNone(domain_mapping.resource_domain("https://example.com/req/schema"))
        self.assertIsNone(domain_mapping.resource_domain("req/schema"))
        self.assertIsNone(domain_mapping.item_domain("resource", "not-a-uri-at-all"))


class TestGenericDispatchToolMapping(unittest.TestCase):
    """The generic dispatch tools map via their own ``type`` argument at call time."""

    def test_every_generic_dispatch_tool_maps_via_its_type_argument(self):
        sut = domain_mapping.item_domain
        for tool in _GENERIC_DISPATCH_TOOLS:
            self.assertIn(tool, domain_mapping.GENERIC_DISPATCH_TOOLS)
            for domain in sorted(domain_mapping.DOMAINS):
                self.assertEqual(sut("tool", tool, type_argument=domain), domain, (tool, domain))

    def test_set_status_with_the_adr_type_argument_maps_to_adr(self):
        self.assertEqual(domain_mapping.item_domain("tool", "set_status", type_argument="adr"), "adr")

    def test_a_type_argument_outside_the_domains_yields_no_domain(self):
        sut = domain_mapping.item_domain
        self.assertIsNone(sut("tool", "update", type_argument="bogus"))
        self.assertIsNone(sut("tool", "update"))
        self.assertIsNone(sut("tool", "delete", type_argument=""))

    def test_the_type_argument_is_ignored_for_non_dispatch_tools(self):
        self.assertEqual(domain_mapping.item_domain("tool", "get_req", type_argument="adr"), "req")

    def test_a_non_tool_item_type_never_consults_the_type_argument(self):
        self.assertIsNone(domain_mapping.item_domain("resource", "specmgr://version", type_argument="req"))
        self.assertIsNone(domain_mapping.item_domain("prompt", "compact_history", type_argument="req"))


class TestNoDomainAndExtractionFailures(unittest.TestCase):
    """The no-domain case and a missing identity yield None (attribute omitted, never empty)."""

    def test_a_missing_identity_yields_no_domain(self):
        sut = domain_mapping.item_domain
        self.assertIsNone(sut("tool", None))
        self.assertIsNone(sut("tool", None, type_argument="req"))
        self.assertIsNone(sut("resource", None))
        self.assertIsNone(sut("prompt", None))

    def test_the_mapping_never_returns_an_empty_string(self):
        sut = domain_mapping.item_domain
        for item_type in ("tool", "resource", "prompt"):
            for name in (None, "", "mdformat", "compact_history", "specmgr://version"):
                result = sut(item_type, name)
                self.assertIn(result, (None, *sorted(domain_mapping.DOMAINS)), (item_type, name))


class _ServerImportTestCase(unittest.TestCase):
    """Save/restore the root logger around a real ``server`` import (MCPServer installs handlers)."""

    def setUp(self) -> None:
        self.root = logging.getLogger()
        self.saved_root_handlers = list(self.root.handlers)
        self.saved_root_level = self.root.level
        self.root.handlers.clear()

    def tearDown(self) -> None:
        for handler in list(self.root.handlers):
            if handler not in self.saved_root_handlers:
                self.root.removeHandler(handler)
                handler.close()
        self.root.handlers = self.saved_root_handlers
        self.root.level = self.saved_root_level

    def _import_server(self) -> types.ModuleType:
        """Import the real server module with the telemetry env vars stripped (defaults: disabled)."""
        from biz.dfch.specmgr.telemetry.config import (
            ENV_LOG_ENABLED,
            ENV_LOG_FILE_ENABLED,
            ENV_LOG_FILE_PATH,
            ENV_LOG_FORMAT,
            ENV_LOG_LEVEL,
            ENV_OTEL_ENABLED,
            ENV_OTEL_ENDPOINT,
            ENV_OTEL_EXPORTER,
        )

        telemetry_env_vars = (
            ENV_LOG_ENABLED,
            ENV_LOG_LEVEL,
            ENV_LOG_FORMAT,
            ENV_LOG_FILE_ENABLED,
            ENV_LOG_FILE_PATH,
            ENV_OTEL_ENABLED,
            ENV_OTEL_EXPORTER,
            ENV_OTEL_ENDPOINT,
        )
        clean = {name: value for name, value in os.environ.items() if name not in telemetry_env_vars}
        with mock.patch.dict(os.environ, clean, clear=True):
            result = importlib.import_module("biz.dfch.specmgr.server")
        assert isinstance(result, types.ModuleType), type(result)
        return result


class TestMappingAgainstLiveRegistrations(_ServerImportTestCase):
    """The static tables cover exactly what ``server.py`` registers (Task 5.6's coverage test).

    Both directions: every registered tool/prompt must be mapped (or be one
    of the explicitly no-domain ones), and every table entry must name a
    registered tool/prompt -- so a renamed/new item trips this test in CI
    instead of silently losing its ``mcp.domain`` attribution.
    """

    def test_every_registered_tool_is_mapped_or_explicitly_no_domain(self):
        server = self._import_server()

        registered_tools = {tool.name for tool in asyncio.run(server.mcp.list_tools())}

        mapped_or_excluded = (
            set(domain_mapping._TOOL_DOMAINS) | domain_mapping.GENERIC_DISPATCH_TOOLS | set(_NO_DOMAIN_TOOLS)
        )
        self.assertEqual(registered_tools, mapped_or_excluded, "unmapped or stale tool names")

    def test_every_registered_prompt_is_mapped_or_explicitly_no_domain(self):
        server = self._import_server()

        registered_prompts = {prompt.name for prompt in asyncio.run(server.mcp.list_prompts())}

        mapped_or_excluded = set(domain_mapping._PROMPT_DOMAINS) | set(_NO_DOMAIN_PROMPTS)
        self.assertEqual(registered_prompts, mapped_or_excluded, "unmapped or stale prompt names")

    def test_every_registered_resource_maps_consistently_with_the_first_segment_rule(self):
        server = self._import_server()

        registered_uris = {resource.uri for resource in asyncio.run(server.mcp.list_resources())}

        for uri in sorted(registered_uris):
            first_segment = uri.removeprefix(domain_mapping.URI_SCHEME_PREFIX).split("/", 1)[0]
            expected = first_segment if first_segment in domain_mapping.DOMAINS else None
            self.assertEqual(domain_mapping.resource_domain(uri), expected, uri)
        # the no-domain cross-cutting resources are actually registered (the rule's None branch is live)
        for uri in _NO_DOMAIN_RESOURCES:
            self.assertIn(uri, registered_uris, uri)


if __name__ == "__main__":
    unittest.main()
