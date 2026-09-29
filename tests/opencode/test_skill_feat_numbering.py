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

"""feat-163 Phase 130, Task 130.110: ACC-006 consistency test for the feat-numbering project skill.

The repo's second project OpenCode skill, ``.opencode/skills/feat-numbering/SKILL.md``
(feat-150's ``repair`` skill, ``.opencode/skill/repair/SKILL.md``, being the first), teaches
the FEAT Task List numbering scheme. These tests pin: the file's location; its frontmatter
(exactly the ``name``/``description`` keys, ``name`` matching the folder, a non-empty
third-person ``description`` carrying the four plan-named trigger keywords FEAT/Task
List/Phase/specmgr -- keyword matching is case-insensitive, a deliberate choice documented
here, since opencode surfaces the description verbatim to agents in whatever casing it was
authored in); the scheme wording (the canonical "Task List numbering scheme:" paragraph,
extracted from both packaged prompt instruction files and asserted to occur verbatim in
the skill body once whitespace is normalized, plus the key constants and the three
``specmgr://feat/*`` resource pointers); the concrete examples (each must also occur in
the packaged template or example, so the skill cannot drift from the packaged shapes);
and the absence of stale legacy guidance (no ``unpadded`` wording anywhere, no 1-2 digit
phase numbers, no task number with a non-3-digit component -- the negative lookarounds
keep the 3-digit examples such as ``Phase 100``/``Task 100.100`` from matching).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from biz.dfch.specmgr.feat.resources.feat_example import feat_example
from biz.dfch.specmgr.feat.resources.feat_template import feat_template
from biz.dfch.specmgr.general.tools import _packaged_data

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skills" / "feat-numbering"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_SKILL_NAME = "feat-numbering"
_TRIGGER_KEYWORDS: tuple[str, ...] = ("FEAT", "Task List", "Phase", "specmgr")
_RESOURCE_URIS: tuple[str, ...] = (
    "specmgr://feat/template",
    "specmgr://feat/example",
    "specmgr://feat/schema",
)
_CANONICAL_START = "Task List numbering scheme:"
_CANONICAL_END = "removals leave gaps."
_SCHEME_FRAGMENTS: tuple[str, ...] = (
    "starting at 100",
    "step 10",
    "3-digit",
    "Phase 105",
    "Task 100.105",
    "permanent",
    "The schema enforces only the number SHAPES",
)
_EXAMPLES_IN_BOTH: tuple[str, ...] = ("Phase 100", "Task 100.100")
_EXAMPLES_IN_EXAMPLE_ONLY: tuple[str, ...] = ("Phase 110", "Task 110.100", "Task 110.110")
_LEGACY_PHASE_PATTERN = re.compile(r"(?<!\d)Phase \d{1,2}(?!\d)")
_TASK_NUMBER_PATTERN = re.compile(r"(?<!\d)Task (\d+)\.(\d+)(?!\d)")


def _legacy_task_numbers(text: str) -> list[str]:
    """Return every ``Task X.Y`` token in ``text`` whose components are not both 3-digit.

    Wider than the legacy 1-2 digit shape: any width drift (``Task 0.1``, ``Task 99.100``,
    ``Task 1000.100``) is flagged, while the scheme's own 3-digit examples (``Task 100.100``
    ...) and the letter placeholder ``Task NNN.MMM`` stay clean.
    """
    result: list[str] = []
    for match in _TASK_NUMBER_PATTERN.finditer(text):
        phase_component, task_component = match.groups()
        if len(phase_component) != 3 or len(task_component) != 3:
            result.append(f"Task {phase_component}.{task_component}")
    return result


def _skill_text() -> str:
    """Read the committed skill file verbatim (a missing file is a hard failure)."""
    assert _SKILL_PATH.is_file(), _SKILL_PATH
    result = _SKILL_PATH.read_text(encoding="utf-8")
    return result


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split the leading ``---`` YAML block from the body (simple line split, no yaml dependency)."""
    lines = text.splitlines()
    assert lines and lines[0] == "---", "skill file must open with a --- frontmatter delimiter"
    closing = [index for index in range(1, len(lines)) if lines[index] == "---"]
    assert closing, "skill file frontmatter has no closing --- delimiter"
    frontmatter: str = "\n".join(lines[1 : closing[0]])
    body: str = "\n".join(lines[closing[0] + 1 :])
    result: tuple[str, str] = (frontmatter, body)
    return result


def _parse_frontmatter(frontmatter: str) -> dict[str, str]:
    """Parse the skill's single-line ``key: value`` frontmatter entries (no yaml dependency)."""
    result: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        assert separator, f"frontmatter line is not key: value: {line}"
        result[key.strip()] = value.strip()
    return result


def _normalize_whitespace(text: str) -> str:
    """Collapse every whitespace run to one space (the prompt files wrap at 80 columns)."""
    result = re.sub(r"\s+", " ", text)
    return result


def _canonical_paragraph(instruction_text: str) -> str:
    """Extract the canonical scheme paragraph from a packaged prompt instruction text."""
    normalized = _normalize_whitespace(instruction_text)
    start = normalized.index(_CANONICAL_START)
    end = normalized.index(_CANONICAL_END, start) + len(_CANONICAL_END)
    result = normalized[start:end]
    return result


class TestSkillFileLocation(unittest.TestCase):
    """ACC-006: the skill exists at its default project-skill path."""

    def test_skill_file_exists(self):
        """Task 130.100's file is committed at .opencode/skills/feat-numbering/SKILL.md."""
        self.assertTrue(_SKILL_DIR.is_dir())
        self.assertTrue(_SKILL_PATH.is_file())


class TestSkillFrontmatter(unittest.TestCase):
    """ACC-006: exactly two frontmatter keys; name matches the folder; third-person
    description carrying the four trigger keywords."""

    def test_frontmatter_has_exactly_the_two_required_keys(self):
        """The opencode skill spec allows exactly name + description here -- nothing else."""
        frontmatter, _ = _split_frontmatter(_skill_text())

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(set(result), {"name", "description"})

    def test_name_matches_folder(self):
        """``name`` must be lowercase hyphen-separated and equal the containing folder name."""
        frontmatter, _ = _split_frontmatter(_skill_text())

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(result["name"], _SKILL_DIR.name)
        self.assertEqual(result["name"], _SKILL_NAME)
        self.assertLessEqual(len(result["name"]), 64)
        self.assertEqual(result["name"], result["name"].lower())

    def test_description_present_and_third_person(self):
        """A non-empty description that does not start with a first/second-person subject."""
        frontmatter, _ = _split_frontmatter(_skill_text())

        result = _parse_frontmatter(frontmatter)
        description = result["description"]

        self.assertTrue(description.strip())
        self.assertFalse(description.lstrip().startswith(("I ", "I'm", "We ", "You ")))

    def test_description_carries_trigger_keywords(self):
        """FEAT/Task List/Phase/specmgr all occur in the description (case-insensitive)."""
        frontmatter, _ = _split_frontmatter(_skill_text())

        result = _parse_frontmatter(frontmatter)
        description = result["description"].lower()

        for keyword in _TRIGGER_KEYWORDS:
            self.assertIn(keyword.lower(), description)


class TestSkillSchemeAgreement(unittest.TestCase):
    """ACC-006: the skill's scheme wording agrees with the packaged prompts and points
    agents at the three authoritative ``specmgr://feat/*`` resources."""

    def test_scheme_paragraph_verbatim_from_both_prompts(self):
        """The canonical paragraph from both instruction files must occur verbatim (modulo
        whitespace) in the skill body -- the skill mirrors the prompts, it does not reword."""
        create_text = _packaged_data.read_packaged_text("feat", "create_instructions", "md")
        update_text = _packaged_data.read_packaged_text("feat", "update_instructions", "md")
        _, body = _split_frontmatter(_skill_text())

        create_paragraph = _canonical_paragraph(create_text)
        update_paragraph = _canonical_paragraph(update_text)
        normalized_body = _normalize_whitespace(body)

        self.assertEqual(create_paragraph, update_paragraph)
        self.assertIn(create_paragraph, normalized_body)

    def test_key_scheme_constants_present(self):
        """Start value, step, width, the in-between example, permanence, shape-only enforcement."""
        _, body = _split_frontmatter(_skill_text())

        normalized_body = _normalize_whitespace(body)

        for fragment in _SCHEME_FRAGMENTS:
            self.assertIn(fragment, normalized_body)

    def test_resource_pointers_present(self):
        """All three specmgr://feat/template|example|schema URIs are named in the body."""
        _, body = _split_frontmatter(_skill_text())

        for uri in _RESOURCE_URIS:
            self.assertIn(uri, body)


class TestSkillPackagedDataCrossAgreement(unittest.TestCase):
    """ACC-006: the skill's concrete examples actually occur in the packaged
    template/example, so the skill cannot drift from the packaged shapes."""

    def test_examples_occur_in_skill_and_packaged_data(self):
        """Every named example occurs in the skill body and in the right packaged document."""
        template = feat_template()
        example = feat_example()
        _, body = _split_frontmatter(_skill_text())

        for token in _EXAMPLES_IN_BOTH + _EXAMPLES_IN_EXAMPLE_ONLY:
            self.assertIn(token, body)
        for token in _EXAMPLES_IN_BOTH:
            self.assertIn(token, template)
            self.assertIn(token, example)
        for token in _EXAMPLES_IN_EXAMPLE_ONLY:
            self.assertIn(token, example)


class TestSkillNoStaleLegacyWording(unittest.TestCase):
    """ACC-006: no stale legacy guidance in the skill.

    The lookarounds keep the 3-digit examples from matching: ``Phase 100`` fails
    ``Phase \\d{1,2}(?!\\d)`` because a third digit follows the first two, and
    ``Task 100.100`` passes the task-number guard because both of its dot-separated
    components are exactly 3 digits long (any other width -- ``Task 1.1``, ``Task 99.100``,
    ``Task 1000.100`` -- is flagged).
    """

    def test_no_unpadded_wording_anywhere(self):
        """Even the word describing the legacy shape is absent from the whole file."""
        self.assertNotIn("unpadded", _skill_text().lower())

    def test_no_legacy_short_phase_numbers(self):
        """No 1-2 digit phase number (``Phase 0``/``Phase 1``/``Phase 12`` style)."""
        _, body = _split_frontmatter(_skill_text())

        self.assertIsNone(_LEGACY_PHASE_PATTERN.search(body))

    def test_no_legacy_short_task_numbers(self):
        """No task number with a non-3-digit component (``Task 0.1``/``Task 99.100`` style)."""
        _, body = _split_frontmatter(_skill_text())

        self.assertEqual(_legacy_task_numbers(body), [])


if __name__ == "__main__":
    unittest.main()
