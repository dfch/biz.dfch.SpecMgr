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

"""Tests for the ``repair`` ``@mcp.prompt()``.

``repair`` is narration-only text (it returns instructions, it never
executes a repair itself), so these tests can only assert what the
rendered instructions say -- not that a real repair round-trips. The real
end-to-end proof is ACC-002's manual smoke test against a genuinely broken
fixture document.
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.prompts import repair
from biz.dfch.specmgr.general.prompts.repair import repair as repair_fn
from biz.dfch.specmgr.general.tools import _packaged_data

_ID = "11111111-2222-3333-4444-555555555555"


def _one_line(text: str) -> str:
    """Collapse the rendered instructions' hard line breaks to single spaces.

    The packaged markdown is hand-wrapped at word boundaries outside inline
    spans, so a prose phrase may span two physical lines; assertions against
    such phrases run against this normalized form.
    """
    result = " ".join(text.split())
    return result


class TestRepairPrompt(unittest.TestCase):
    """Tests for the repair prompt's rendered instructions."""

    def test_type_interpolated_into_tool_names(self):
        """The type must render the concrete list_<d>/get_<d> tool names."""
        result = repair_fn("req")
        self.assertIn("list_req", result)
        self.assertIn("get_req", result)

    def test_type_case_insensitive(self):
        """A non-lowercase type must normalize to the same rendered text."""
        self.assertEqual(repair_fn("Req", _ID), repair_fn("req", _ID))

    def test_id_interpolated_when_given(self):
        """A given id must appear verbatim in the returned text."""
        result = repair_fn("req", _ID)
        self.assertIn(_ID, result)

    def test_id_not_given_placeholder_when_absent(self):
        """An absent id must render the explicit not-given placeholder."""
        result = repair_fn("req")
        self.assertIn("(not given", result)
        self.assertNotIn(_ID, result)

    def test_failed_row_discovery_named(self):
        """list_<d>'s failed row (marker, null id, populated ref/path/error) must be named."""
        result = _one_line(repair_fn("req"))
        self.assertIn("<failed to parse>", result)
        self.assertIn("list_req", result)
        self.assertIn("`ref`/`path`/`error`", result)
        self.assertIn("holds the parse failure (field path and cause", result)
        self.assertIn("closed-vocabulary failures", result)

    def test_get_parse_failure_result_named(self):
        """get_<d>'s non-raising parse-failure result (error/path, list-row-identical text) must be named."""
        result = _one_line(repair_fn("req", _ID))
        self.assertIn("get_req", result)
        self.assertIn("returned, NOT raised", result)
        self.assertIn("the same text `list_req()`'s failed row carries", result)
        self.assertIn("truly absent, `get_req` raises the domain's not-found error", result)

    def test_host_file_tools_directed(self):
        """The raw read and the write-back must point at the host's own file tools."""
        result = _one_line(repair_fn("req", _ID))
        self.assertIn("your host's own file-read tool", result)
        self.assertIn("your host's own file-write tool", result)

    def test_no_update_note(self):
        """The explicit note that the generic update tool cannot repair must be present."""
        result = repair_fn("req", _ID)
        self.assertIn("generic `update`", result)
        self.assertIn("structurally unable to repair", result)
        self.assertIn("NEVER write it back via the generic `update`", result)

    def test_frontmatter_preservation_rule(self):
        """Preserve id/created/status/version byte-for-byte; a repair is not an edit."""
        result = repair_fn("req", _ID)
        self.assertIn("byte-for-byte", result)
        self.assertIn("`id`, `created`, `status`, and `version`", result)
        self.assertIn("a repair is", result)
        self.assertIn("not an edit", result)

    def test_updated_left_untouched(self):
        """The updated field must be left untouched (a repair is not an edit)."""
        result = repair_fn("req", _ID)
        self.assertIn("`updated`", result)
        self.assertIn("must not move", result)

    def test_validate_loop_full_true(self):
        """The loop must name the generic validate tool with type, content, full=True."""
        result = repair_fn("req", _ID)
        self.assertIn("validate", result)
        self.assertIn('validate(type="req"', result)
        self.assertIn("full=True", result)

    def test_post_write_confirmation_step(self):
        """A post-write get_<d>(id)/list_<d>() confirmation against the file on disk must be required."""
        result_with_id = _one_line(repair_fn("req", _ID))
        self.assertIn("Confirm the repair against the file as it now exists on disk", result_with_id)
        self.assertIn("real parse of the real file counts as success", result_with_id)
        self.assertIn("`get_req` with the same id again", result_with_id)
        self.assertIn(
            "returns the parsed document (a real parse of the real file on disk) rather than a result carrying `error`",
            result_with_id,
        )
        self.assertIn("if it still returns the `error`/`path` result, the on-disk file is still broken", result_with_id)
        result_without_id = _one_line(repair_fn("req"))
        self.assertIn("Confirm the repair against the file as it now exists on disk", result_without_id)
        self.assertIn("`list_req()` again", result_without_id)

    def test_diagnose_only_degradation(self):
        """The diagnose-only degradation (report, touch nothing) must be stated."""
        result = repair_fn("req", _ID)
        self.assertIn("Diagnose-only degradation", result)
        self.assertIn("do not touch the file", result)

    def test_adr_exclusion_stated(self):
        """The ADR exclusion must be stated in the instructions."""
        result = repair_fn("req", _ID)
        self.assertIn("ADR is explicitly out", result)
        self.assertIn("scope", result)

    def test_raises_value_error_for_adr(self):
        """repair('adr') must fail fast (ADR exclusion)."""
        with self.assertRaises(ValueError) as ctx:
            repair_fn("adr", _ID)
        self.assertIn("adr", str(ctx.exception))

    def test_raises_value_error_for_unknown_type(self):
        """An unknown type must fail fast with the allowed domains named."""
        with self.assertRaises(ValueError) as ctx:
            repair_fn("bogus")
        self.assertIn("bogus", str(ctx.exception))
        self.assertIn("req", str(ctx.exception))

    def test_raises_value_error_for_blank_id(self):
        """A blank/whitespace-only id must fail fast rather than be treated as absent."""
        with self.assertRaises(ValueError):
            repair_fn("req", "   ")

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from
        general/data/general_repair_instructions.md, not an inline
        Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "general_repair_instructions.md"
            instructions_path.write_text("first $type / $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = repair_fn("req", _ID)
                instructions_path.write_text("second $type / $id", encoding="utf-8")
                second = repair_fn("req", _ID)

            self.assertEqual(first, f"first req / {_ID}")
            self.assertEqual(second, f"second req / {_ID}")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    repair_fn("req")


class TestRepairRegistration(unittest.TestCase):
    """The ``general.prompts`` package exposes ``repair``, and the live ``mcp`` registration carries it."""

    def test_exposed_in_package_all(self):
        """Importing general.prompts must expose repair in __all__."""
        import biz.dfch.specmgr.general.prompts as general_prompts

        self.assertIn("repair", general_prompts.__all__)
        self.assertIs(general_prompts.repair, repair)

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._prompts = asyncio.run(mcp.list_prompts())

    def test_repair_registered_on_mcp_server(self):
        """The live mcp application must register the repair prompt exactly once."""
        matching = [p for p in self._prompts if p.name == "repair"]
        self.assertEqual(len(matching), 1)


if __name__ == "__main__":
    unittest.main()
