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

"""Tests for the ``generate_uc_sequence_diagram`` ``@mcp.prompt()`` (feat-185-uc-diagrams, Phase 120).

The prompt is narration-only text (it returns the rulebook §3.8 agent-flow
instructions for one use case, it never executes the flow itself), so these
tests can only assert what the rendered instructions say -- not that a real
diagram round-trips. The real end-to-end proof is ACC-002's Phase 140
walkthrough. The instructions live in the packaged data file
``uc/data/uc_generate_uc_sequence_diagram_instructions.md`` (the packaged
prompt-instructions convention; ``$id`` substituted via ``string.Template``).
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.server import mcp
from biz.dfch.specmgr.uc.prompts import generate_uc_sequence_diagram
from biz.dfch.specmgr.uc.prompts.generate_uc_sequence_diagram import generate_uc_sequence_diagram as generate_fn

_ID = "11111111-2222-3333-4444-555555555555"


def _one_line(text: str) -> str:
    """Collapse the rendered instructions' hard line breaks to single spaces.

    The packaged markdown is hand-wrapped at word boundaries outside inline
    spans, so a prose phrase may span two physical lines; assertions against
    such phrases run against this normalized form.
    """
    result = " ".join(text.split())
    return result


class TestGenerateUcSequenceDiagramPrompt(unittest.TestCase):
    """Tests for the generate_uc_sequence_diagram prompt's rendered instructions."""

    def test_id_interpolated_when_given(self):
        """The given id must appear verbatim, including the file-name derivation."""
        result = generate_fn(_ID)
        self.assertIn(_ID, result)
        self.assertIn(f"diagrams/uc/{_ID}.sequence.puml", result)

    def test_blank_id_raises_value_error(self):
        """A blank id must raise ValueError before any packaged read."""
        with self.assertRaises(ValueError):
            generate_fn("   ")

    def test_reads_the_rulebook_first(self):
        """Step 1 is the read-first rulebook (the update_sop specmgr://rasci precedent): the
        specmgr://uc/plantuml resource must be named before any other step's tool call."""
        result = generate_fn(_ID)
        self.assertIn("specmgr://uc/plantuml", result)
        self.assertLess(result.index("specmgr://uc/plantuml"), result.index("get_uc("))

    def test_step_sequence_in_order(self):
        """The ten narrated steps must appear in the flow's own order (rulebook §3.8)."""
        result = generate_fn(_ID)
        markers = [
            "## 1. Read the rulebook first",
            "## 2. Build a TodoWrite plan",
            "## 3. Read the UC",
            "## 4. Subfunction judgment (rulebook §2.11)",
            "## 5. Fetch the skeleton",
            "## 6. Attribute every UNATTRIBUTED marker",
            "## 7. Zero-marker rule",
            "## 8. Validation loop (rulebook §3.8)",
            "## 9. Write the file (host-native)",
            "## 10. Never commit",
        ]
        positions = [result.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_broken_document_stops_the_flow(self):
        """A get_uc ParseFailureResult must stop the flow (report, do not write)."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("ParseFailureResult", result)
        self.assertIn("do not write any file", result)

    def test_question_contract_named(self):
        """The question tool MUST be used whenever not confident (rulebook §3.8 / REQ-004)."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("the `question` tool", result)
        self.assertIn("MUST ask the user", result)

    def test_prefilled_arrows_are_positional_not_semantic(self):
        """The pre-filled arrows' positional-not-semantic caveat (and the correction permission) must be present."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("positional, not semantic", result)
        self.assertIn("MAY correct any pre-filled arrow", result)

    def test_zero_marker_rule_named(self):
        """The zero-marker rule must be the write gate."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("only with zero `UNATTRIBUTED` markers remaining", result)

    def test_validation_loop_named_with_all_three_outcomes(self):
        """The validate loop must name the short-circuit, the no-write outcome, and the structure-only header."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("validate_plantuml(text)", result)
        self.assertIn("never called on a structure red", result)
        self.assertIn("do not write", result)
        self.assertIn("' validated: structure-only", result)
        self.assertIn("first line", result)

    def test_host_native_write_and_no_specmgr_writer(self):
        """The write must be host-native and the no-specmgr-writes-.puml rule must be stated."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("your host's own file-write tool", result)
        self.assertIn("no specmgr tool writes `.puml` files", result)

    def test_never_commit_named(self):
        """The never-commit rule must be the final step."""
        result = _one_line(generate_fn(_ID))
        self.assertIn("Do **not** `git add` or commit", result)


class TestGenerateUcSequenceDiagramInstructionsPackaging(unittest.TestCase):
    """The instructions must come from the packaged data file (the convention's own pin)."""

    def test_instructions_loaded_from_packaged_data_file(self):
        """The instructional text must come from uc/data/uc_generate_uc_sequence_diagram_instructions.md,
        not an inline Python string -- reads fresh on every call, no cache."""
        with tempfile.TemporaryDirectory() as tmp:
            instructions_path = Path(tmp) / "uc_generate_uc_sequence_diagram_instructions.md"
            instructions_path.write_text("first $id", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=instructions_path):
                first = generate_fn(_ID)
                instructions_path.write_text("second $id", encoding="utf-8")
                second = generate_fn(_ID)

            self.assertEqual(first, f"first {_ID}")
            self.assertEqual(second, f"second {_ID}")

    def test_raises_file_not_found_when_instructions_missing(self):
        """A missing packaged instructions file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    generate_fn(_ID)


class TestGenerateUcSequenceDiagramRegistration(unittest.TestCase):
    """The ``uc.prompts`` package exposes the prompt, and the live ``mcp`` registration carries it."""

    def test_exposed_in_package_all(self):
        """Importing uc.prompts must expose generate_uc_sequence_diagram in __all__."""
        import biz.dfch.specmgr.uc.prompts as uc_prompts

        self.assertIn("generate_uc_sequence_diagram", uc_prompts.__all__)
        self.assertIs(uc_prompts.generate_uc_sequence_diagram, generate_uc_sequence_diagram)

    @classmethod
    def setUpClass(cls) -> None:
        cls._prompts = asyncio.run(mcp.list_prompts())

    def test_registered_on_mcp_server(self):
        """The live mcp application must register the prompt exactly once."""
        matching = [p for p in self._prompts if p.name == "generate_uc_sequence_diagram"]
        self.assertEqual(len(matching), 1)


if __name__ == "__main__":
    unittest.main()
