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

"""Tests for the ``update_req`` ``@mcp.prompt()`` (Task 3.19)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.req.prompts.update_req import update_req


class TestUpdateReqPrompt(unittest.TestCase):
    """Tests for the update_req prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_req("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_req_tool_first(self):
        """The prompt must instruct the LLM to call get_req first,
        before the generic `update` write call."""
        result = update_req("abc-123")
        self.assertIn("get_req(id)", result)
        self.assertLess(result.index("get_req(id)"), result.index('update(id, type="req", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="req") and `set_status`
        (type="req") call shapes must be named."""
        result = update_req("abc-123")
        for tool in ('update(id, type="req", content)', 'set_status(id, type="req", status)'):
            self.assertIn(tool, result)

    def test_mentions_legacy_level_recovery_directive(self):
        """The prompt must carry the present-tense recovery directive: a
        get_req parse failure naming the ## Level value leads to reading
        specmgr://iso29148, repairing the file with the host's own
        file-read/file-write tools (no specmgr read returns the body of a
        document that fails to parse, and the generic update/edit tools
        cannot repair one), and a confirming get_req(id) call before
        proceeding with the requested change."""
        result = update_req("abc-123")
        self.assertIn("**Legacy `## Level` value recovery.**", result)
        self.assertIn("If `get_req(id)` returns a parse", result)
        self.assertIn("failure whose error names the `## Level` value", result)
        self.assertIn("Read the cross-cutting `specmgr://iso29148` resource to confirm the", result)
        self.assertIn("four kinds (BRS, StRS, SyRS, SRS)", result)
        for kind in ("BRS", "StRS", "SyRS", "SRS"):
            with self.subTest(kind=kind):
                self.assertIn(kind, result)
        self.assertIn("No specmgr read returns the body of a document that fails to parse", result)
        self.assertIn("read the raw file with the host's own file-read tool at", result)
        self.assertIn("the `path` the parse-failure result carries", result)
        self.assertIn("write the file back with", result)
        self.assertIn("the host's own file-write tool -- the generic `update`/`edit` tools", result)
        self.assertIn("Confirm the repair with a real `get_req(id)` call -- it must now parse", result)
        self.assertIn("before proceeding with the originally requested", result)
        self.assertLess(
            result.index("**Legacy `## Level` value recovery.**"),
            result.index("## 2. If no change was specified"),
        )

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_req(id, raw=True, numbered=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_req("abc-123")
        self.assertIn("get_req(id, raw=True, numbered=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="req", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_req(id, raw=True, numbered=True)"),
            result.index('update(id, type="req", content, offset=..., limit=...)'),
        )

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_req("abc-123", instructions="Change the status to accepted.")
        self.assertIn("Change the status to accepted.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_req("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_req("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_req("abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from req/data/req_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "req_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_req("abc-123", instructions="Change the status to accepted.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_req("abc-123", instructions="Change the status to accepted.")

            self.assertEqual(first, "first abc-123 / Change the status to accepted.")
            self.assertEqual(second, "second abc-123 / Change the status to accepted.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_req("abc-123")


if __name__ == "__main__":
    unittest.main()
