# Copyright (C) 2026 Ronald Rink, http://d-fens.ch
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

"""Tests for the `specmgr://uc/plantuml-template` resource (`uc.resources.uc_plantuml_template.uc_plantuml_template`).

The resource serves the packaged PlantUML sequence-skeleton template
(``uc/data/uc_plantuml_template.md``) as raw PlantUML source with the
frozen ``text/plain`` mime type (the plan's §11 resource mime-type
contract: PlantUML source -- not markdown, not a specmgr document: no
frontmatter, not validate-able). The tool-side half of the same
packaged-data pair is ``get_uc_plantuml_template``.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from mcp.server.mcpserver.resources.base import Resource

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.server import mcp
from biz.dfch.specmgr.uc.resources.uc_plantuml_template import uc_plantuml_template


def _registered_resource(uri: str) -> Resource:
    """Return the registered Resource model for `uri` from the server's resource manager."""
    result = [resource for resource in mcp._resource_manager.list_resources() if resource.uri == uri]
    assert len(result) == 1, f"expected exactly one registration for {uri}, got {len(result)}"
    return result[0]


class TestUcPlantumlTemplateResource(unittest.TestCase):
    """Tests for the uc_plantuml_template resource function."""

    def test_is_registered_with_plain_mime_type(self):
        """The resource must be registered under its unversioned URI as text/plain (the §11 freeze)."""
        resource = _registered_resource("specmgr://uc/plantuml-template")

        self.assertEqual(resource.name, "uc_plantuml_template")
        self.assertEqual(resource.mime_type, "text/plain")

    def test_returns_the_packaged_data_file_verbatim(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = uc_plantuml_template

        result = sut()

        on_disk = _packaged_data.packaged_data_path("uc", "plantuml_template")
        self.assertIsInstance(result, str)
        self.assertEqual(result, on_disk.read_text(encoding="utf-8"))
        self.assertTrue(result.startswith("@startuml"))
        self.assertNotIn("---\n", result)  # no frontmatter: not a specmgr document

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            template_path = Path(tmp) / "uc_plantuml_template.md"
            template_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=template_path):
                sut = uc_plantuml_template

                first = sut()
                template_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_template_missing(self):
        """A missing packaged template file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = uc_plantuml_template

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
