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

"""Tests for the ``create_sysrs`` ``@mcp.tool()`` wrapper (Task 3.2)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models.md import CURRENT_SCHEMA_VERSION
from biz.dfch.specmgr.sysrs.models.v1 import SysrsDocument, SysrsFrontmatter, parse_sysrs
from biz.dfch.specmgr.sysrs.tools._paths import sysrs_base_dir
from biz.dfch.specmgr.sysrs.tools.create_sysrs import create_sysrs
from biz.dfch.specmgr.sysrs.tools.get_sysrs import get_sysrs

_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"

_MINIMAL_BODY = textwrap.dedent(
    f"""\
    # System Requirements Specification: Sample Document

    ## System Purpose

    Provision partner accounts.

    ## System Scope

    Onboarding only.

    ## Business Context and Goals

    ### Goals

    - GOL {_GOL_ID}: A goal

    ## System Overview

    ### System Context

    Context.

    ### System Functions

    Functions.

    ## Requirements

    ### Functional Suitability

    - REQ {_REQ_ID}: A requirement
    """
)

# Structurally valid, but a field/cross-field failure: a cross-reference
# bullet with the wrong type tag (`PRB` under `### Goals`, which only
# accepts `GOL`) -- the `Goals` after-validator's `ValidationError` channel.
_BAD_CROSS_REF_BODY = _MINIMAL_BODY.replace(f"- GOL {_GOL_ID}", f"- PRB {_GOL_ID}")

_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized System Requirements Specification sections.\n"


class TempSysrsDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via SPECMGR_DOCS_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateSysrs(TempSysrsDirTestCase):
    """Tests for the create_sysrs tool."""

    def test_builds_frontmatter_and_returns_document(self) -> None:
        """create_sysrs must build the entire frontmatter itself (id/type/status/timestamps/version)."""
        result = create_sysrs(_MINIMAL_BODY)

        self.assertIsInstance(result, SysrsFrontmatter)
        self.assertNotIsInstance(result, SysrsDocument)
        self.assertFalse(hasattr(result, "body"))
        self.assertIsNotNone(result.id)
        self.assertEqual(result.type, "sysrs")
        self.assertEqual(result.status, "draft")
        self.assertIsNotNone(result.created)
        self.assertEqual(result.created, result.updated)
        self.assertEqual(result.version, CURRENT_SCHEMA_VERSION)

        fetched = get_sysrs(result.id)
        self.assertEqual(fetched.body.text, "System Requirements Specification: Sample Document")

    def test_writes_expected_filename(self) -> None:
        """create_sysrs must write f'sysrs-{id}-{slug}.md' under the System Requirements Specification base dir."""
        result = create_sysrs(_MINIMAL_BODY)

        expected_path = sysrs_base_dir() / f"sysrs-{result.id}-system-requirements-specification-sample-document.md"
        self.assertTrue(expected_path.exists())

    def test_written_file_round_trips_via_parse_sysrs(self) -> None:
        """The written file must parse back into an equivalent document."""
        result = create_sysrs(_MINIMAL_BODY)

        expected_path = sysrs_base_dir() / f"sysrs-{result.id}-system-requirements-specification-sample-document.md"
        on_disk = parse_sysrs(expected_path.read_text(encoding="utf-8"))

        self.assertEqual(on_disk.frontmatter.id, result.id)
        self.assertEqual(on_disk.frontmatter.status, "draft")
        self.assertEqual(on_disk.body.text, "System Requirements Specification: Sample Document")

    def test_creates_base_dir_if_missing(self) -> None:
        """create_sysrs must create the System Requirements Specification base directory if it does not exist yet."""
        self.assertFalse(sysrs_base_dir().exists())

        create_sysrs(_MINIMAL_BODY)

        self.assertTrue(sysrs_base_dir().is_dir())

    def test_invalid_content_raises_and_writes_nothing(self) -> None:
        """A structurally invalid body must raise AssertionError and write no file at all."""
        with self.assertRaises(AssertionError):
            create_sysrs(_MALFORMED_BODY)

        self.assertFalse(sysrs_base_dir().exists())

    def test_field_validation_failure_raises_and_writes_nothing(self) -> None:
        """A field-level validation failure (wrong cross-reference type tag) must raise, writing nothing."""
        with self.assertRaises(ValidationError):
            create_sysrs(_BAD_CROSS_REF_BODY)

        self.assertFalse(sysrs_base_dir().exists())


if __name__ == "__main__":
    unittest.main()
