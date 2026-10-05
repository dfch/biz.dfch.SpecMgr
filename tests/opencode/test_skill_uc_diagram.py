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

"""feat-185-uc-diagrams Phase 140, Task 140.100: host-surface pin for the uc-diagram skill + command.

The repo's third OpenCode host artifact (after feat-150's ``repair`` trio and
feat-163's ``feat-numbering`` skill), the thin self-triggering
``.opencode/skill/uc-diagram/SKILL.md`` — plus the included optional
``.opencode/command/uc-diagram.md`` — points agents at the UC → PlantUML
pipeline instead of restating it. These tests pin: the file's locations
(notably the **singular** ``.opencode/skill/`` path — the repair-trio
location, the repo's deliberate choice alongside ``.opencode/skills/`` which
holds ``feat-numbering``; the skill lives in ``skill/`` because it belongs
to the same host-artifact family as ``repair``, the ``task``-deferring
trio shape); the skill's frontmatter (exactly the ``name``/``description``
keys, ``name`` matching the folder, a non-empty third-person ``description``
carrying the trigger keywords PlantUML/use case diagram/sequence diagram/
specmgr — keyword matching is case-insensitive, a deliberate choice
documented here, since opencode surfaces the description verbatim to agents
in whatever casing it was authored in); the key body wording (the
``generate_uc_sequence_diagram`` prompt pointer, the ``specmgr://uc/plantuml``
rulebook URI read-first, the deterministic-only CLI mentions, the
``UNATTRIBUTED``/``question``/never-commit contract, and the plantuml-mcp
watch note with its no-dependency caveat); and the command's frontmatter
(a ``description`` naming ``$1`` as the UC id, **no** ``agent:`` field —
there is no dedicated subagent, the flow is the prompt itself) plus its
body's prompt-flow and step-10 report pointers.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "uc-diagram"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_COMMAND_PATH = _REPO_ROOT / ".opencode" / "command" / "uc-diagram.md"
_SKILL_NAME = "uc-diagram"
_TRIGGER_KEYWORDS: tuple[str, ...] = ("PlantUML", "use case diagram", "sequence diagram", "specmgr")
_PROMPT_NAME = "generate_uc_sequence_diagram"
_RULEBOOK_URI = "specmgr://uc/plantuml"
_CLI_MENTIONS: tuple[str, ...] = (
    "specmgr diagram uc",
    "--check",
    "specmgr plantuml-check",
    "specmgr plantuml-encode",
)
_CONTRACT_WORDS: tuple[str, ...] = ("UNATTRIBUTED", "question", "never commit")
_WATCH_NOTE_PHRASES: tuple[str, ...] = (
    "plantuml-mcp",
    "prefer it",
    "no dependency",
)


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
    """The skill + command exist at their committed paths (singular skill/ dir)."""

    def test_skill_file_exists_at_the_singular_skill_path(self):
        self.assertTrue(_SKILL_DIR.is_dir())
        self.assertTrue(_SKILL_PATH.is_file())

    def test_command_file_exists(self):
        self.assertTrue(_COMMAND_PATH.is_file())


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
    """The thin pointer set: prompt, rulebook URI, CLI, question/never-commit
    contract, and the plantuml-mcp watch note with its no-dependency caveat."""

    def test_prompt_pointer_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        self.assertIn(_PROMPT_NAME, body)

    def test_rulebook_uri_is_read_first(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        self.assertIn(_RULEBOOK_URI, body)
        self.assertIn("Read the rulebook first", body)
        self.assertLess(body.index(_RULEBOOK_URI), body.index(_CLI_MENTIONS[0]))

    def test_deterministic_only_cli_mentions_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for mention in _CLI_MENTIONS:
            self.assertIn(mention, body)

    def test_sequence_diagram_is_prompt_flow_only(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        self.assertIn("the only sanctioned path for a sequence diagram", body)

    def test_question_and_never_commit_contract_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for word in _CONTRACT_WORDS:
            self.assertIn(word, body)

    def test_plantuml_mcp_watch_note_present_with_no_dependency(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for phrase in _WATCH_NOTE_PHRASES:
            self.assertIn(phrase, body)


class TestCommandFrontmatterAndBody(unittest.TestCase):
    """The command names $1 as the UC id, carries no agent: field (no dedicated
    subagent — the flow is the prompt itself), and runs the prompt flow."""

    def test_frontmatter_carries_a_description_only(self):
        frontmatter, _ = _split_frontmatter(_read_text(_COMMAND_PATH))

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(set(result), {"description"})
        self.assertIn("$1", result["description"])
        self.assertNotIn("agent", result)

    def test_body_runs_the_prompt_flow_and_reports_per_step_10(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))

        self.assertIn(_PROMPT_NAME, body)
        self.assertIn(_RULEBOOK_URI, body)
        self.assertIn("step 10", body)
        self.assertIn("Do not commit", body)


if __name__ == "__main__":
    unittest.main()
