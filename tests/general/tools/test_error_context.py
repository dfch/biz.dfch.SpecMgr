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

"""feat-27-validation Phase 3, Task 3.4: tool-layer tests for the shared error-context wrapper.

ACC-003: asserts that the exception string surfaced by ``create_<d>``/``validate_<d>`` and the
generic ``update`` adapter (``general.tools.update``) prepends domain + tool context (built by
``models.md._errors.wrap_tool_errors``, Task 3.1) on top of the engine's own message
(feat-27-validation Phases 1/2). Covers ``tsk`` and ``req`` -- the two domains the task names --
plus one ``set_status`` case for completeness, since that generic tool's own adapters were
touched by Task 3.2 as well.

Unlike ``tests/general/tools/test_update.py``'s exhaustive, all-eleven-domain parametrization,
this file only needs one representative domain pair to prove the wrapper is actually wired in
at the tool boundary -- the wrapper's own mechanics (all three channels, ``also_catch``,
pass-through) are already fully covered by ``tests/models/md/test_errors.py``.
"""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.req.tools.validate_req import validate_req
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.tsk.tools.validate_tsk import validate_tsk

_TSK_MINIMAL_BODY = textwrap.dedent(
    """\
    # Simple Task List

    - [ ] Do the first thing

    ## Recent Updates

    ### 2026-08-15 - Kickoff

    Started the task list.
    """
)

_TSK_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized task list sections.\n"

_REQ_MINIMAL_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 °C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

_REQ_MALFORMED_BODY = "# Title\n\nJust a paragraph, no recognized sections.\n"

_REQ_OUT_OF_VOCABULARY_BODY = _REQ_MINIMAL_BODY.replace("MUST", "NOT-A-VALID-LEVEL")


class TempDocsDirTestCase(unittest.TestCase):
    """Common fixture: a temp dir set as the docs root via ``SPECMGR_DOCS_DIR``."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.dict("os.environ", {DOCS_DIR_ENV_VAR: str(self.docs_root)}))


class TestCreateToolErrorContext(TempDocsDirTestCase):
    """``create_<d>``: a structural/field failure names the domain and the tool."""

    def test_create_tsk_structural_failure_names_domain_and_tool(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            create_tsk(_TSK_MALFORMED_BODY)

        self.assertIn("tsk create_tsk", str(ctx.exception))

    def test_create_req_field_validation_failure_names_domain_and_tool(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            create_req(_REQ_OUT_OF_VOCABULARY_BODY)

        self.assertIn("req create_req", str(ctx.exception))


class TestValidateToolErrorContext(unittest.TestCase):
    """``validate_<d>``: a structural/field failure names the domain and the tool."""

    def test_validate_tsk_structural_failure_names_domain_and_tool(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            validate_tsk(_TSK_MALFORMED_BODY)

        self.assertIn("tsk validate_tsk", str(ctx.exception))

    def test_validate_req_field_validation_failure_names_domain_and_tool(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            validate_req(_REQ_OUT_OF_VOCABULARY_BODY)

        self.assertIn("req validate_req", str(ctx.exception))


class TestGenericUpdateToolErrorContext(TempDocsDirTestCase):
    """The generic ``update`` adapter: a structural/field failure names the domain and ``update``."""

    def test_update_tsk_structural_failure_names_domain_and_tool(self) -> None:
        created = create_tsk(_TSK_MINIMAL_BODY)

        with self.assertRaises(AssertionError) as ctx:
            update(id=created.frontmatter.id, type="tsk", content=_TSK_MALFORMED_BODY)

        self.assertIn("tsk update", str(ctx.exception))

    def test_update_req_field_validation_failure_names_domain_and_tool(self) -> None:
        created = create_req(_REQ_MINIMAL_BODY)

        with self.assertRaises(ValidationError) as ctx:
            update(id=created.frontmatter.id, type="req", content=_REQ_OUT_OF_VOCABULARY_BODY)

        self.assertIn("req update", str(ctx.exception))


class TestGenericSetStatusToolErrorContext(TempDocsDirTestCase):
    """The generic ``set_status`` adapter: an out-of-vocabulary status names the domain and ``set_status``."""

    def test_set_status_tsk_out_of_vocabulary_names_domain_and_tool(self) -> None:
        created = create_tsk(_TSK_MINIMAL_BODY)

        with self.assertRaises(ValidationError) as ctx:
            set_status(id=created.frontmatter.id, type="tsk", status="not-a-real-status")

        self.assertIn("tsk set_status", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
