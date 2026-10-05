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

"""feat-152 Phase 110, Task 110.120: ACC-005 consistency test for the specmgr-refs project skill.

The repo's third project OpenCode skill, ``.opencode/skills/specmgr-refs/SKILL.md``
(feat-163's ``feat-numbering`` skill, ``.opencode/skills/feat-numbering/SKILL.md``,
being the previous one and feat-150's ``repair`` skill,
``.opencode/skill/repair/SKILL.md``, the first), is the agent-initiated router over the
feat-144 cross-reference retrieval stack (the ``list_references`` MCP tool, the
``ref-finder`` subagent, and the ``/refs`` command). These tests pin: the file's location
(pin a); its frontmatter (pin b -- exactly the ``name``/``description`` keys, ``name``
matching the folder, a non-empty third-person ``description`` carrying the eight
plan-locked trigger keywords -- keyword matching is case-insensitive, a deliberate choice
documented here, since opencode surfaces the description verbatim to agents in whatever
casing it was authored in); the inherited ``ref-finder`` reporting vocabulary (pin c --
every token of the locked ``_REPORTING_TOKENS`` tuple occurs in the body as a literal
substring, backticks included); the single-document delegation pointer (pin d -- the
locked delegation phrase in the whitespace-normalized body, plus all three names of the
existing stack); the read-only posture (pin e -- both locked read-only phrases in the
whitespace-normalized body); and the workflow presence (pin f -- the three codified
workflow headings as literal body substrings, plus the load-bearing workflow constants
(the canonical 12-domain string, the ``N = 2`` default-depth wording, and the deliberate
``adr``-exclusion wording) in the whitespace-normalized body). All pins are mechanical
string checks on the committed file; none of them import from ``src/``, so the test
guards the skill wording, not the tool behavior.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skills" / "specmgr-refs"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_SKILL_NAME = "specmgr-refs"
_TRIGGER_KEYWORDS: tuple[str, ...] = (
    "specmgr",
    "cross-reference",
    "list_references",
    "what does document X reference",
    "list the references of X",
    "show me the reference graph",
    "do all cross-references resolve",
    "which documents reference X",
)
_REPORTING_TOKENS: tuple[str, ...] = (
    "**NOT FOUND**",
    "`type`",
    "`id`",
    "`title`",
    "`path`",
    "`total`",
    "`error_count`",
    "`truncated`",
)
_DELEGATION_PHRASE = "is a pointer to the existing stack, never a copy of it"
_DELEGATION_NAMES: tuple[str, ...] = ("list_references", "ref-finder", "/refs")
_READONLY_PHRASES: tuple[str, ...] = ("never edit, write, create, or delete", "never commit")
_WORKFLOW_HEADINGS: tuple[str, ...] = (
    "## Graph workflow (multi-hop traversal)",
    "## Batch workflow (resolution validation)",
    '## Reverse workflow ("which documents reference X?")',
)
_WORKFLOW_CONSTANTS: tuple[str, ...] = (
    "req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs",
    "N = 2",
    "deliberate",
)


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


class TestSkillFileLocation(unittest.TestCase):
    """Pin a: the skill exists at its project-skill path."""

    def test_skill_file_exists(self):
        """Task 110.100's file is committed at .opencode/skills/specmgr-refs/SKILL.md."""
        self.assertTrue(_SKILL_DIR.is_dir())
        self.assertTrue(_SKILL_PATH.is_file())


class TestSkillFrontmatter(unittest.TestCase):
    """Pin b: exactly two frontmatter keys; name matches the folder; third-person
    description carrying the eight trigger keywords."""

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
        """All eight locked trigger keywords occur in the description (case-insensitive)."""
        frontmatter, _ = _split_frontmatter(_skill_text())

        result = _parse_frontmatter(frontmatter)
        description = result["description"].lower()

        for keyword in _TRIGGER_KEYWORDS:
            self.assertIn(keyword.lower(), description)


class TestSkillReportingVocabulary(unittest.TestCase):
    """Pin c: the inherited ``ref-finder`` reporting vocabulary occurs in the body verbatim."""

    def test_reporting_tokens_present_in_body(self):
        """**NOT FOUND** and the backticked row/result fields all occur as literal substrings."""
        _, body = _split_frontmatter(_skill_text())

        for token in _REPORTING_TOKENS:
            self.assertIn(token, body)


class TestSkillDelegationPointer(unittest.TestCase):
    """Pin d: single-document handling is a pointer to the existing stack, not a copy."""

    def test_delegation_phrase_present(self):
        """The locked delegation phrase occurs in the body once whitespace is normalized."""
        _, body = _split_frontmatter(_skill_text())

        normalized_body = _normalize_whitespace(body)

        self.assertIn(_DELEGATION_PHRASE, normalized_body)

    def test_delegation_names_present(self):
        """The body names all three of the existing stack: list_references, ref-finder, /refs."""
        _, body = _split_frontmatter(_skill_text())

        for name in _DELEGATION_NAMES:
            self.assertIn(name, body)


class TestSkillReadOnlyPosture(unittest.TestCase):
    """Pin e: the read-only posture is stated in the body."""

    def test_readonly_phrases_present(self):
        """Both locked read-only phrases occur in the body once whitespace is normalized."""
        _, body = _split_frontmatter(_skill_text())

        normalized_body = _normalize_whitespace(body)

        for phrase in _READONLY_PHRASES:
            self.assertIn(phrase, normalized_body)


class TestSkillWorkflowPresence(unittest.TestCase):
    """Pin f: the three codified workflows are present in the body — the feature's
    core deliverable cannot be stripped silently."""

    def test_workflow_headings_present(self):
        """Every codified workflow heading occurs in the body as a literal substring."""
        _, body = _split_frontmatter(_skill_text())

        for heading in _WORKFLOW_HEADINGS:
            self.assertIn(heading, body)

    def test_workflow_constants_present(self):
        """The load-bearing workflow constants occur in the body once whitespace is normalized."""
        _, body = _split_frontmatter(_skill_text())

        normalized_body = _normalize_whitespace(body)

        for constant in _WORKFLOW_CONSTANTS:
            self.assertIn(constant, normalized_body)


if __name__ == "__main__":
    unittest.main()
