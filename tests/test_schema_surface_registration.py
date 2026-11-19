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
(DEC 112b6498-078b-4a59-88b8-8ffb7a5041b3, "Convert the 12 per-domain schema
resources to get_<d>_schema tools"):

- every whole-body domain's ``get_<d>_schema`` tool is registered
  (the 12 ``specmgr://<domain>/schema`` resources' own replacement);
- none of the former ``specmgr://<domain>/schema`` URIs is registered any
  more (neither as a static resource nor as a URI template);
- the surface totals moved from 103 tools / 49 resources to 115 tools /
  37 resources (36 static + 1 URI template), as measured against the
  worktree surface at that decision's writing time;
- feat-229-txt Phase 130 (generic-tool registration) grew the live
  surface by the 7 ``txt`` tools (115 + 7 = 122) and the 2 ``txt``
  resources (37 + 2 = 39) **at the ``general.tools._domains`` import
  edge** -- importing ``txt.tools._io``/``txt.tools._paths`` runs
  ``txt/__init__.py``'s vcr-precedent ``from . import prompts, resources,
  tools`` line, so every test process that imports
  ``biz.dfch.specmgr.server`` registers the whole ``txt`` decorator
  surface on the live ``mcp`` singleton ahead of Phase 160's own
  ``server.py`` bottom-line import (which is then a no-op re-import).
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

    def test_no_registered_name_mentions_the_retired_artifact_type(self) -> None:
        """feat-46 Phase 140 (ACC-011): the retired artifact type is fully gone from the
        registered surface -- no tool, resource, URI template, or prompt name mentions it."""
        names = {tool.name for tool in self._tools}
        names.update(resource.uri for resource in self._resources)
        names.update(template.uri_template for template in self._templates)
        names.update(prompt.name for prompt in asyncio.run(mcp.list_prompts()))

        # the retired type's name, built at runtime so this regression pin never itself carries
        # the contiguous token (the removal checklist greps for it)
        retired = "a" + "dr"
        offenders = sorted(name for name in names if retired in name.lower())
        self.assertEqual(offenders, [], f"retired-artifact surface still registered: {offenders}")

    def test_tool_total_is_120(self) -> None:
        """103 tools (the worktree surface at that decision's writing time) + 12 = 115, + 7 txt tools
        (feat-229 Phase 130 import edge: ``general.tools._domains``'s module-level
        ``txt.tools._io``/``txt.tools._paths`` imports run ``txt/__init__.py``'s
        ``from . import prompts, resources, tools`` line, registering all 7 on the live
        singleton ahead of Phase 160's ``server.py`` line), + 2 for the read-only
        translation tools ``list_languages`` and ``check_translation_drift``
        (feat-197-i18n Phase 140) = 124, + 7 set tools
        (feat-173-req-iso29148-level-set Phase 180, the same import edge:
        ``general.tools._domains``'s module-level ``set.tools._io``/``set.tools._paths``
        imports run ``set/__init__.py``'s ``from . import prompts, resources, tools``
        line) = 131, - 11 for the retired domain's tools (feat-46 Phase 140)
        = 120 (measured against the post-merge live surface)."""
        result = len(self._tools)

        self.assertEqual(result, 120)

    def test_resource_total_is_44(self) -> None:
        """49 resources (12 schema + 36 static + 1 template) - 12 = 37, + 2 txt resources
        (``specmgr://txt/example``/``specmgr://txt/template``, the same Phase 130 import
        edge -- ``txt/__init__.py`` pulls ``txt.resources`` in with ``txt.tools``), + 1 for
        ``specmgr://i18n`` and + 1 for the ``specmgr://i18n/headings/{language}`` template
        (feat-197-i18n Phase 130), + 1 for ``specmgr://iso29148``
        (feat-173-req-iso29148-level-set Phase 130), + 1 for
        ``specmgr://harness-bundle`` (feat-167-mcp-lifecycle-commands-2
        Phase 130), + 2 set resources
        (``specmgr://set/example``/``specmgr://set/template``, the same Phase 180 import
        edge -- ``set/__init__.py`` pulls ``set.resources`` in with ``set.tools``)
        = 45, - 1 for the retired URI template (feat-46 Phase 140) = 44
        (measured against the post-merge live surface)."""
        result = len(self._resources) + len(self._templates)

        self.assertEqual(result, 44)


if __name__ == "__main__":
    unittest.main()
