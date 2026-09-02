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

"""Tests for the ``update_risk`` ``@mcp.prompt()`` (Task 3.13)."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.rsk.prompts.update_risk import update_risk


class TestUpdateRiskPrompt(unittest.TestCase):
    """Tests for the update_risk prompt."""

    def test_mentions_id(self):
        """The id argument must be interpolated into the returned text."""
        result = update_risk("abc-123")
        self.assertIn("abc-123", result)

    def test_mentions_get_rsk_tool_first(self):
        """The prompt must instruct the LLM to call get_rsk first,
        before the generic `update` write call."""
        result = update_risk("abc-123")
        self.assertIn("get_rsk(id)", result)
        self.assertLess(result.index("get_rsk(id)"), result.index('update(id, type="rsk", content)'))

    def test_mentions_both_generic_mutation_tools(self):
        """Both the generic `update` (type="rsk") and `set_status`
        (type="rsk") call shapes must be named."""
        result = update_risk("abc-123")
        for tool in ('update(id, type="rsk", content)', 'set_status(id, type="rsk", status)'):
            self.assertIn(tool, result)

    def test_mentions_range_update_flow(self):
        """The prompt must teach the line-range flow: read the exact body
        via get_rsk(id, raw=True), identify the 1-based line to start at
        and how many lines to replace (N+1 is end-of-body), call
        `update` with offset/limit passing only the replacement lines;
        whole-body for multi-section or uncertain changes."""
        result = update_risk("abc-123")
        self.assertIn("get_rsk(id, raw=True)", result)
        self.assertIn("1-based line to start at and how many", result)
        self.assertIn("offset = N+1", result)
        self.assertIn('update(id, type="rsk", content, offset=..., limit=...)', result)
        self.assertIn("multi-section change, or whenever you are", result)
        self.assertIn("byte-identical", result)
        self.assertLess(
            result.index("get_rsk(id, raw=True)"),
            result.index('update(id, type="rsk", content, offset=..., limit=...)'),
        )

    def test_instructions_interpolated_when_given(self):
        """A given instructions string must appear verbatim in the returned text."""
        result = update_risk("abc-123", instructions="Move the residual risk one zone down.")
        self.assertIn("Move the residual risk one zone down.", result)

    def test_prompts_for_input_when_instructions_absent(self):
        """Absent instructions must tell the LLM to ask the user, not guess."""
        result = update_risk("abc-123")
        self.assertIn("ask the user", result)

    def test_mentions_whole_body_replace_warning(self):
        """The whole-body-replace caveat for the generic `update` tool must be present."""
        result = update_risk("abc-123")
        self.assertIn("whole-body replace", result)

    def test_mentions_status_never_via_update(self):
        """The prompt must clarify that the generic `update` tool never changes status."""
        result = update_risk("abc-123")
        self.assertIn("`update` never accepts or changes `status`", result)

    def test_mentions_status_vocabulary(self):
        """The six accepted risk statuses must all be named."""
        result = update_risk("abc-123")
        self.assertIn("open, mitigating, accepted, occurred, closed, dropped", result)

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from rsk/data/rsk_update_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "rsk_update_instructions.md"
            instructions_path.write_text("first $id / $instructions", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = update_risk("abc-123", instructions="Move the residual risk one zone down.")
                instructions_path.write_text("second $id / $instructions", encoding="utf-8")
                second = update_risk("abc-123", instructions="Move the residual risk one zone down.")

            self.assertEqual(first, "first abc-123 / Move the residual risk one zone down.")
            self.assertEqual(second, "second abc-123 / Move the residual risk one zone down.")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    update_risk("abc-123")


if __name__ == "__main__":
    unittest.main()
