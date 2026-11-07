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

"""feat-173-req-iso29148-level-set Phase 180, Task 180.120: host-surface pin for the specmgr-set skill.

The repo's next OpenCode host artifact (the ``specmgr-refs``/``uc-diagram``
pattern), the thin self-triggering ``.opencode/skill/specmgr-set/SKILL.md``,
points agents at the set-bundling knowledge and the ``create_set`` prompt
flow instead of restating the tools' own descriptions. These tests pin: the
file's location (the project skill path ``.opencode/skill/specmgr-set/`` --
every project skill lives under the singular ``skill/`` directory); the
skill's frontmatter (exactly the ``name``/``description`` keys, ``name``
matching the folder, a non-empty third-person ``description`` carrying the
trigger keywords bundle/group/set -- keyword matching is case-insensitive,
a deliberate choice documented here, since opencode surfaces the description
verbatim to agents in whatever casing it was authored in); and the key body
wording (the convenience-bundle invariant, the items-remain-the-source-of-
truth rule, the forward-references-only rule with the absent-``SET``-tag
consequence, the mixed-types rule over the 12 reference tags, the fixed
H1/Description/Items shape, the ``list_set`` near-duplicate check, the
``create_set`` prompt pointer, the ``question``/never-commit contract).
There is deliberately NO dedicated ``/set`` command (design decision,
2026-11-01) -- the flow is the skill plus the ``create_set``/``update_set``
prompts themselves.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "specmgr-set"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_SKILL_NAME = "specmgr-set"
_TRIGGER_KEYWORDS: tuple[str, ...] = (
    "bundle",
    "group",
    "make a set",
    "put these documents together",
    "specmgr",
)
_PROMPT_NAMES: tuple[str, ...] = ("create_set", "update_set")
_INVARIANCE_PHRASES: tuple[str, ...] = (
    "convenience bundle",
    "The items remain the source of truth",
    "Forward references only",
    "Mixed types allowed",
    "The shape is fixed",
)
_TAG_KEYWORDS: tuple[str, ...] = (
    "GOL",
    "PRB",
    "QA",
    "UC",
    "REQ",
    "RSK",
    "DEC",
    "ADR",
    "VCR",
    "SYSRS",
    "TXT",
    "FEAT",
)
_WORKFLOW_WORDS: tuple[str, ...] = ("list_set", "question", "never commit")


def _read_text(path: Path) -> str:
    """Read a committed host-artifact file verbatim (a missing file is a hard failure)."""
    assert path.is_file(), path
    result = path.read_text(encoding="utf-8")
    return result


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split the leading ``---`` YAML block from the body (simple line split, no yaml dependency)."""
    lines = text.splitlines()
    assert lines and lines[0] == "---", "host artifact must open with a --- frontmatter delimiter"
    closing = [index for index in range(1, len(lines)) if lines[index] == "---"]
    assert closing, "host artifact frontmatter has no closing --- delimiter"
    frontmatter: str = "\n".join(lines[1 : closing[0]])
    body: str = "\n".join(lines[closing[0] + 1 :])
    result: tuple[str, str] = (frontmatter, body)
    return result


def _parse_frontmatter(frontmatter: str) -> dict[str, str]:
    """Parse the single-line ``key: value`` frontmatter entries (no yaml dependency)."""
    result: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        assert separator, f"frontmatter line is not key: value: {line}"
        result[key.strip()] = value.strip()
    return result


class TestHostArtifactLocations(unittest.TestCase):
    """The skill exists at its committed path (singular skill/ dir); no /set command."""

    def test_skill_file_exists_at_the_singular_skill_path(self):
        self.assertTrue(_SKILL_DIR.is_dir())
        self.assertTrue(_SKILL_PATH.is_file())

    def test_there_is_no_dedicated_set_command(self):
        # the design decision (2026-11-01): no /set command -- the flow is the
        # skill plus the create_set/update_set prompts themselves
        self.assertFalse((_REPO_ROOT / ".opencode" / "command" / "set.md").exists())


class TestSkillFrontmatter(unittest.TestCase):
    """Exactly two frontmatter keys; name matches the folder; third-person
    description carrying the trigger keywords."""

    def test_frontmatter_has_exactly_the_two_required_keys(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(set(result), {"name", "description"})

    def test_name_matches_folder(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(result["name"], _SKILL_DIR.name)
        self.assertEqual(result["name"], _SKILL_NAME)
        self.assertLessEqual(len(result["name"]), 64)
        self.assertEqual(result["name"], result["name"].lower())

    def test_description_present_and_third_person(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)
        description = result["description"]

        self.assertTrue(description.strip())
        self.assertFalse(description.lstrip().startswith(("I ", "I'm", "We ", "You ")))

    def test_description_carries_trigger_keywords(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)
        description = result["description"].lower()

        for keyword in _TRIGGER_KEYWORDS:
            self.assertIn(keyword.lower(), description)


class TestSkillBodyWording(unittest.TestCase):
    """The invariants and the workflow: bundle semantics, the 12 tags, the
    fixed shape, the near-duplicate check, the prompt pointers, the
    question/never-commit contract."""

    def test_invariants_are_named(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for phrase in _INVARIANCE_PHRASES:
            self.assertIn(phrase, body)

    def test_all_twelve_reference_tags_are_named(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for tag in _TAG_KEYWORDS:
            self.assertIn(tag, body)

    def test_forward_reference_only_names_the_absent_set_tag(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        self.assertIn("`SET` is not a tag", body)

    def test_prompt_pointers_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for name in _PROMPT_NAMES:
            self.assertIn(name, body)

    def test_workflow_words_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for word in _WORKFLOW_WORDS:
            self.assertIn(word, body)


if __name__ == "__main__":
    unittest.main()
