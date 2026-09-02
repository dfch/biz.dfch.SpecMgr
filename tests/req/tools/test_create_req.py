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

"""Tests for the ``create_req`` ``@mcp.tool()`` wrapper (Task 3.12)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.req.models.v1 import ReqFrontmatter, parse_req
from biz.dfch.specmgr.req.tools._paths import req_base_dir
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.req.tools.get_req import get_req

_MINIMAL_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 \u00b0C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized requirement sections.\n"


class TempReqDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateReq(TempReqDirTestCase):
    """Tests for the create_req tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_req must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_req(_MINIMAL_BODY)

        self.assertIsInstance(result, ReqFrontmatter)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "req")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_req(result.id)
        self.assertEqual(fetched.body.text, "Maximum Engine Temperature")

    def test_writes_expected_filename(self) -> None:
        """create_req must write f'req-{id}-{slug}.md' under the requirement base dir."""
        result = create_req(_MINIMAL_BODY)

        expected_path = req_base_dir() / f"req-{result.id}-maximum-engine-temperature.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_req(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_req(_MINIMAL_BODY)

        expected_path = req_base_dir() / f"req-{result.id}-maximum-engine-temperature.md"
        on_disk = parse_req(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "Maximum Engine Temperature")
        self.assertEqual(
            [item.text for item in on_disk.body.characteristics.items],
            ["Safety", "Reliability"],
        )

    def test_creates_base_dir_if_missing(self) -> None:
        """create_req must create the requirement base directory if it does not exist yet."""
        self.assertFalse(req_base_dir().exists())

        create_req(_MINIMAL_BODY)

        self.assertTrue(req_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_req(_MALFORMED_BODY)

        self.assertFalse(req_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (bad `## Level` value) must raise, writing nothing."""
        text = _MINIMAL_BODY.replace("MUST", "NOT-A-VALID-LEVEL")

        with self.assertRaises(ValidationError):
            create_req(text)

        self.assertFalse(req_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
