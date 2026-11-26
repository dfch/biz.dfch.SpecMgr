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

"""feat-163 Phase 140, Task 140.110: REQ-008/ACC-005 prompt <-> schema optionality regression test.

Pins the mandatory/optional section sets claimed by the two packaged prompt
instruction files (``feat_create_instructions.md`` step 2 and
``feat_update_instructions.md`` step 3) against the required/optional field
sets the ``feat`` model itself declares on its two container sections
``Plan`` and ``Progress`` (``feat/models/v1/body.py``): if a future prompt
edit mislabels a section's optionality, or renames a section, the
corresponding test fails loudly instead of the prompt drifting silently from
the schema.

Model side: derived programmatically from ``Plan.model_fields`` and
``Progress.model_fields`` via each Pydantic v2 field's ``is_required()`` --
nothing is hardcoded. Scope: the 14 H3 section fields of the two containers
alone. The containers' H4 leaves (``Scope``'s ``Included``/``Explicitly Out
Of Scope``, ``Dependencies``'s ``Depends On``/``Blocks``) are covered by
their parent container's optionality for this test's purpose -- the prompts'
step-2/step-3 lists name the H3 sections, not the H4 leaves, and the model
declares every leaf of a mandatory container as mandatory and every leaf of
an optional container as optional, so the parent's optionality is exactly
what the prompts claim.

Prompt side: each instruction file's stable sentence is parsed with two
narrow, well-commented regexes (one per list), extracting every
backtick-quoted section display name from that list; each display name is
mapped to its model field name by the explicit ``_SECTION_FIELD_NAMES``
table below (a leaf display name maps to its parent container's field, since
a leaf and its container share optionality and the partition is asserted on
the 14 container fields). A display name missing from the table is a hard
failure, as is a pattern that no longer matches its file.
"""

from __future__ import annotations

import re
import unittest

from biz.dfch.specmgr.feat.models.v1.body import Plan, Progress
from biz.dfch.specmgr.general.tools import _packaged_data

#: Display-name -> model-field-name table for every backtick-quoted section
#: name the two prompt lists can carry: the 14 H3 container sections plus
#: the 4 H4 leaves, each leaf mapped to its parent container's field.
_SECTION_FIELD_NAMES: dict[str, str] = {
    "Overview": "overview",
    "Requirements": "requirements",
    "Acceptance Criteria": "acceptance_criteria",
    "Scope": "scope",
    "Included": "scope",
    "Explicitly Out Of Scope": "scope",
    "Dependencies": "dependencies",
    "Depends On": "dependencies",
    "Blocks": "dependencies",
    "Design Notes": "design_notes",
    "Related Decisions": "related_decisions",
    "Task List": "task_list",
    "Current Status": "current_status",
    "Blockers": "blockers",
    "Updates": "updates",
    "Decisions Made": "decisions_made",
    "Related PRs / Commits": "related_prs_commits",
    "More Information": "more_information",
}

# Create prompt, step 2: "Build a todo list with one entry per: the
# mandatory `Overview`, ... `Updates`, and each optional section
# (`Dependencies`, ... `More Information`)." -- two narrow patterns, one per
# list, each anchored on the sentence's own stable wording.
_CREATE_MANDATORY_PATTERN = re.compile(r"one entry per: the mandatory (?P<list>.*?)each optional section", re.DOTALL)
_CREATE_OPTIONAL_PATTERN = re.compile(r"each optional section \((?P<list>.*?)\)\.", re.DOTALL)

# Update prompt, step 3: "Show the user which of the sections -- the
# mandatory `Overview`, ... and `Updates` (always present), and the optional
# `Dependencies` ... and `More Information` -- are already present with
# content..." -- likewise one narrow pattern per list.
_UPDATE_MANDATORY_PATTERN = re.compile(r"sections -- the mandatory (?P<list>.*?)\(always present\)", re.DOTALL)
_UPDATE_OPTIONAL_PATTERN = re.compile(r"and the optional (?P<list>.*?)--\s*are already present", re.DOTALL)


def _required_field_names(model: type) -> set[str]:
    """Return the model's required field names (Pydantic v2 ``is_required()``)."""
    result: set[str] = {name for name, field in model.model_fields.items() if field.is_required()}
    return result


def _optional_field_names(model: type) -> set[str]:
    """Return the model's optional field names (the ``is_required()`` complement)."""
    result: set[str] = {name for name, field in model.model_fields.items() if not field.is_required()}
    return result


def _extract_field_names(span: str, where: str) -> set[str]:
    """Map every backtick-quoted display name in ``span`` to its model field name.

    A display name missing from ``_SECTION_FIELD_NAMES`` is a hard failure
    (an unknown/renamed section in the prompt), as is a span carrying no
    backtick-quoted names at all.
    """
    names = re.findall(r"`([^`]+)`", span)
    assert names, f"{where}: no backtick-quoted section names extracted"
    unknown = [name for name in names if name not in _SECTION_FIELD_NAMES]
    assert not unknown, f"{where}: display name(s) not in the mapping table: {unknown}"
    result: set[str] = {_SECTION_FIELD_NAMES[name] for name in names}
    return result


class TestPromptSchemaOptionality(unittest.TestCase):
    """REQ-008/ACC-005: each prompt's mandatory/optional partition == the model's required/optional fields."""

    def _assert_prompt_partition(
        self,
        instruction_text: str,
        mandatory_pattern: re.Pattern[str],
        optional_pattern: re.Pattern[str],
        where: str,
    ) -> None:
        """Assert one prompt file's mandatory/optional section partition against Plan+Progress."""
        mandatory_match = mandatory_pattern.search(instruction_text)
        assert mandatory_match is not None, f"{where}: mandatory-list pattern did not match (prompt sentence drifted?)"
        optional_match = optional_pattern.search(instruction_text)
        assert optional_match is not None, f"{where}: optional-list pattern did not match (prompt sentence drifted?)"

        prompt_mandatory = _extract_field_names(mandatory_match.group("list"), f"{where} mandatory list")
        prompt_optional = _extract_field_names(optional_match.group("list"), f"{where} optional list")

        model_required = _required_field_names(Plan) | _required_field_names(Progress)
        model_optional = _optional_field_names(Plan) | _optional_field_names(Progress)

        self.assertEqual(
            prompt_mandatory,
            model_required,
            f"{where}: the prompt's mandatory sections do not match the model's required fields",
        )
        self.assertEqual(
            prompt_optional,
            model_optional,
            f"{where}: the prompt's optional sections do not match the model's optional fields",
        )
        self.assertEqual(
            prompt_mandatory | prompt_optional,
            model_required | model_optional,
            f"{where}: the prompt's two lists do not partition the 14 container sections (missing or extra)",
        )
        self.assertEqual(
            prompt_mandatory & prompt_optional,
            set(),
            f"{where}: a section is listed as both mandatory and optional in the prompt",
        )

    def test_create_prompt_section_optionality_matches_model(self) -> None:
        """Create step 2's mandatory/optional partition must equal Plan+Progress required/optional."""
        instruction_text = _packaged_data.read_packaged_text("feat", "create_instructions", "md")
        self._assert_prompt_partition(
            instruction_text,
            _CREATE_MANDATORY_PATTERN,
            _CREATE_OPTIONAL_PATTERN,
            "create prompt step 2",
        )

    def test_update_prompt_section_optionality_matches_model(self) -> None:
        """Update step 3's mandatory/optional partition must equal Plan+Progress required/optional."""
        instruction_text = _packaged_data.read_packaged_text("feat", "update_instructions", "md")
        self._assert_prompt_partition(
            instruction_text,
            _UPDATE_MANDATORY_PATTERN,
            _UPDATE_OPTIONAL_PATTERN,
            "update prompt step 3",
        )


if __name__ == "__main__":
    unittest.main()
