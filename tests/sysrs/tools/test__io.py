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

"""Tests for ``sysrs.tools._io`` (thin file read helpers)."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from biz.dfch.specmgr.sysrs.models.v1 import SysrsDocument
from biz.dfch.specmgr.sysrs.tools._io import load_by_id, read_sysrs
from biz.dfch.specmgr.sysrs.tools._paths import SysrsNotFoundError

_GOL_ID = "0e15c5de-4ac9-4279-aa75-53249a3e43e4"
_REQ_ID = "a3f8c2d1-7b4e-4d9a-b6c0-91e5f2a8d734"

_DOC_TEMPLATE = textwrap.dedent(
    f"""\
    ---
    id: {{id}}
    type: sysrs
    version: 1.0.0
    status: draft
    created: '2026-08-30 00:00:00.000Z'
    updated: '2026-08-30 00:00:00.000Z'
    ---

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


def _sysrs_text(id_: str) -> str:
    """Render a minimal, valid System Requirements Specification document's text for the given id."""
    return _DOC_TEMPLATE.format(id=id_)


class TestReadSysrs(unittest.TestCase):
    """Tests for read_sysrs."""

    def test_reads_and_parses_a_real_file(self) -> None:
        """read_sysrs must return a SysrsDocument matching the file's own content."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(_sysrs_text("some-id"), encoding="utf-8")

            document = read_sysrs(path)

            self.assertIsInstance(document, SysrsDocument)
            self.assertEqual(document.frontmatter.id, "some-id")
            self.assertEqual(document.body.text, "System Requirements Specification: Sample Document")


class TestLoadById(unittest.TestCase):
    """Tests for load_by_id."""

    def test_returns_path_and_parsed_sysrs(self) -> None:
        """load_by_id must return both the resolved path and the parsed document."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            expected_path = base / "doc.md"
            expected_path.write_text(_sysrs_text("the-id"), encoding="utf-8")

            path, document = load_by_id(base, "the-id")

            self.assertEqual(path, expected_path)
            self.assertEqual(document.frontmatter.id, "the-id")

    def test_raises_not_found_for_unknown_id(self) -> None:
        """load_by_id must raise SysrsNotFoundError for an id with no matching file."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaises(SysrsNotFoundError):
                load_by_id(base, "does-not-exist")


if __name__ == "__main__":
    unittest.main()
