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

"""Tests for the ``update_sop`` ``@mcp.prompt()`` (Task 4.1, ACC-005).

``update_sop`` (the prompt) only ever returns instructional text -- it never
calls ``get_sop``/``question``/``update``/``set_status`` (the tools) itself
-- so these are string-content/ordering assertions on the narrated text
confirming every required step from the feature README's Design Notes is
actually present, in the right order.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.sop.prompts.update_sop import update_sop
from biz.dfch.specmgr.general.tools import _packaged_data


class TestUpdateSopPrompt(unittest.TestCase):
    """Tests for the update_sop prompt."""

    def test_returns_substituted_id(self):
        """A distinctive id must be interpolated, and no literal $id placeholder may remain."""
        result = update_sop("id-abc-123")
        self.assertIsInstance(result, str)
        self.assertIn("id-abc-123", result)
        self.assertNotIn("$id", result)

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text, and no literal
        $instructions placeholder may remain."""
        result = update_sop("id-abc-123", instructions="Change the procedure to add a step.")
        self.assertIn("Change the procedure to add a step.", result)
        self.assertNotIn("$instructions", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must be replaced by the standard fallback telling the LLM to ask
        the user before making any change, not guess."""
        result = update_sop("id-abc-123")
        self.assertIn("(not given -- ask the user before making any change)", result)

    def test_instructions_match_packaged_file(self):
        """The returned text must contain a distinctive, stable sentence from the real
        sop/data/sop_update_instructions.md -- evidence the text comes from packaged data."""
        result = update_sop("id-abc-123")
        self.assertIn("Never assume prior state", result)

    def test_mentions_get_sop_tool_first(self):
        """The prompt must instruct the LLM to call get_sop first,
        before the generic `update` write call."""
        result = update_sop("id-abc-123")
        self.assertIn("get_sop(id)", result)
        self.assertLess(result.index("get_sop(id)"), result.index('update(id, type="sop", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="sop") and `set_status`
        (type="sop") call shapes must be named -- sop has no per-domain
        mutation tools (ADR 36905d5b)."""
        result = update_sop("id-abc-123")
        for tool in ('update(id, type="sop", content)', 'set_status(id, type="sop", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_sop(id, raw=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_sop("id-abc-123")
        self.assertIn("get_sop(id, raw=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="sop", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_sop(id, raw=True)"),
            result.index('update(id, type="sop", content, offset=..., limit=...)'),
        )

    def test_mentions_rasci_read_first(self):
        """The prompt must include an explicit step to read specmgr://rasci before
        revising ## Roles and Responsibilities (REQ-011 discoverability)."""
        result = update_sop("id-abc-123")
        self.assertIn("specmgr://rasci", result)

    def test_does_not_narrate_per_domain_mutation_tools(self):
        """sop is dispatch-only -- the narration must use the generic `update`/
        `set_status` tools with type="sop", never a per-domain `update_sop(...)`/
        `set_status_sop(...)` call shape."""
        result = update_sop("id-abc-123")
        self.assertNotIn("update_sop(", result)
        self.assertNotIn("set_status_sop(", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from sop/data/sop_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "sop_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_sop("id-abc-123", instructions="Change the procedure.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_sop("id-abc-123", instructions="Change the procedure.")

            self.assertEqual(first, "first id-abc-123 / Change the procedure.")
            self.assertEqual(second, "second id-abc-123 / Change the procedure.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_sop("id-abc-123")


if __name__ == "__main__":
    unittest.main()
