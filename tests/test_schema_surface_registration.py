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

"""feat-189 Phase 105 (C17) registration facts against the live ``mcp`` app
(ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3, "Convert the 12 per-domain schema
resources to get_<d>_schema tools"):

- every whole-body domain's ``get_<d>_schema`` tool is registered
  (the 12 ``specmgr://<domain>/schema`` resources' own replacement);
- none of the former ``specmgr://<domain>/schema`` URIs is registered any
  more (neither as a static resource nor as a URI template);
- the surface totals moved from 103 tools / 49 resources to 115 tools /
  37 resources (36 static + the ``specmgr://adr/{id}`` URI template), as
  measured against the worktree surface at the ADR's writing time.
"""

from __future__ import annotations

import asyncio
import unittest

from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.server import mcp


class TestSchemaSurfaceRegistration(unittest.TestCase):
    """The C17 conversion's registration facts, pinned against the live ``mcp`` app."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tools = asyncio.run(mcp.list_tools())
        cls._resources = mcp._resource_manager.list_resources()
        cls._templates = mcp._resource_manager.list_templates()

    def test_every_whole_body_domain_schema_tool_registered(self) -> None:
        """``get_<d>_schema`` is registered for every domain in the shared WHOLE_BODY_DOMAINS source."""
        names = {tool.name for tool in self._tools}

        for domain in WHOLE_BODY_DOMAINS:
            self.assertIn(f"get_{domain}_schema", names)

    def test_no_schema_resources_remain(self) -> None:
        """None of the former ``specmgr://<d>/schema`` URIs is registered (static or template)."""
        uris = {resource.uri for resource in self._resources}
        uris.update(template.uri_template for template in self._templates)

        for domain in WHOLE_BODY_DOMAINS:
            self.assertNotIn(f"specmgr://{domain}/schema", uris)

    def test_tool_total_is_115(self) -> None:
        """103 tools (the worktree surface at the ADR's writing time) + 12 = 115."""
        result = len(self._tools)

        self.assertEqual(result, 115)

    def test_resource_total_is_37(self) -> None:
        """49 resources (12 schema + 36 static + 1 template) - 12 = 37."""
        result = len(self._resources) + len(self._templates)

        self.assertEqual(result, 37)


if __name__ == "__main__":
    unittest.main()
