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

"""feat-197-i18n Phase 140, Task 140.130: host-surface pin for the translation-status skill + command.

The thin self-triggering ``.opencode/skill/translation-status/SKILL.md`` -- plus the
``.opencode/command/translation-status.md`` command -- points agents at the two read-only MCP tools
``list_languages`` and ``check_translation_drift`` instead of restating them. Like ``translate-artifact`` there is no
dedicated subagent: the flow is the two tool calls themselves. These tests pin: the file locations (the **singular**
``.opencode/skill/`` path); the skill's frontmatter (exactly the ``name``/``description`` keys, ``name`` matching the
folder, a non-empty third-person ``description`` carrying the trigger phrasing -- keyword matching is
case-insensitive -- and no ``: `` inside the plain YAML scalar); the key body wording (both tools named, the
``feat``/``adr`` exclusion, "no tool translates", the translate hand-off, the never-edit/never-commit contract); the
command's frontmatter (a ``description`` naming ``$1``..``$3``, **no** ``agent:`` field) and body (the two-step
flow: ``list_languages`` always, ``check_translation_drift`` when a language is given, the ``/translate`` suggestion,
read-only); and that the two tools it points at are real, registered tools.
"""

from __future__ import annotations

import asyncio
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "translation-status"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_COMMAND_PATH = _REPO_ROOT / ".opencode" / "command" / "translation-status.md"
_SKILL_NAME = "translation-status"
_TRIGGER_PHRASES: tuple[str, ...] = (
    "which languages exist for REQ",
    "list the translations of",
    "is the German translation of",
    "check translation drift",
    "specmgr",
    "/translation-status",
)
_TOOL_NAMES: tuple[str, ...] = ("list_languages", "check_translation_drift")
_IN_SCOPE_DOMAINS: tuple[str, ...] = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs")


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


def _flat(text: str) -> str:
    """Collapse hard line breaks to single spaces (a phrase may span two physical lines)."""
    result = " ".join(text.split())
    return result


class TestHostArtifactLocations(unittest.TestCase):
    """The skill + command exist at their committed paths (singular skill/ dir)."""

    def test_skill_file_exists_at_the_singular_skill_path(self):
        self.assertTrue(_SKILL_DIR.is_dir())
        self.assertTrue(_SKILL_PATH.is_file())

    def test_command_file_exists(self):
        self.assertTrue(_COMMAND_PATH.is_file())

    def test_no_dedicated_subagent_exists(self):
        agent_dir = _REPO_ROOT / ".opencode" / "agent"
        self.assertEqual([p.name for p in agent_dir.glob("*translation*")], [])
        self.assertEqual([p.name for p in agent_dir.glob("*drift*")], [])


class TestSkillFrontmatter(unittest.TestCase):
    """Exactly two frontmatter keys; name matches the folder; third-person description with the trigger phrasing."""

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

        description = _parse_frontmatter(frontmatter)["description"]

        self.assertTrue(description.strip())
        self.assertFalse(description.lstrip().startswith(("I ", "I'm", "We ", "You ")))

    def test_description_carries_trigger_phrasing(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        description = _parse_frontmatter(frontmatter)["description"].lower()

        for phrase in _TRIGGER_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), description)

    def test_description_names_both_tools(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        description = _parse_frontmatter(frontmatter)["description"]

        for tool in _TOOL_NAMES:
            with self.subTest(tool=tool):
                self.assertIn(tool, description)

    def test_description_states_the_scope_and_the_feat_adr_exclusion(self):
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        description = _parse_frontmatter(frontmatter)["description"]

        for domain in _IN_SCOPE_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(domain, description)
        self.assertIn("feat and adr are always English and out of scope", description)

    def test_description_is_valid_plain_yaml_scalar(self):
        """No `: ` inside the plain scalar (it would not be valid YAML)."""
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        description = _parse_frontmatter(frontmatter)["description"]

        self.assertNotIn(": ", description)


class TestSkillBodyWording(unittest.TestCase):
    """The thin pointer set: both tools, what they report, the boundaries."""

    def test_both_tools_are_named_with_their_calls(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        self.assertIn("`list_languages(type, id)`", flat)
        self.assertIn('`check_translation_drift(type, id, language, source_language="en")`', flat)

    def test_listing_contract_points_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        self.assertIn("`en` first when the English source exists", flat)
        self.assertIn("`parseable`", flat)
        self.assertIn("`en` is never invented", flat)

    def test_drift_contract_points_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        for token in (
            "`missing`",
            "`extra`",
            "`reordered`",
            "`unparseable`",
            "`stale`",
            "`in_sync`",
            "`source_ahead_by_seconds`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, flat)
        self.assertIn("`problem_statement`", flat)
        self.assertIn("never compared", flat)

    def test_boundaries_stated(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        self.assertIn("No tool translates", flat)
        self.assertIn("`translate-artifact` skill", flat)
        self.assertIn("`/translate`", flat)
        self.assertIn("never edits, writes, or commits anything", flat)
        self.assertIn("`feat` and `adr` are always English", flat)
        self.assertIn("`en` is never a drift `language`", flat)
        self.assertIn("general/data/headings/<language>.json", flat)
        self.assertIn("question mechanism", flat)


class TestCommandFrontmatterAndBody(unittest.TestCase):
    """The command names its inputs, carries no agent: field, and runs the two-step tool flow."""

    def test_frontmatter_carries_a_description_only(self):
        frontmatter, _ = _split_frontmatter(_read_text(_COMMAND_PATH))

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(set(result), {"description"})
        for placeholder in ("$1", "$2", "$3"):
            with self.subTest(placeholder=placeholder):
                self.assertIn(placeholder, result["description"])
        self.assertNotIn("agent", result)

    def test_body_runs_the_two_tools_in_order(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))
        flat = _flat(body)

        self.assertIn("`list_languages($1, $2)`", flat)
        self.assertIn("`check_translation_drift($1, $2, $3)`", flat)
        self.assertLess(body.index("list_languages"), body.index("check_translation_drift"))
        self.assertIn("If `$3` is given", flat)

    def test_body_reports_both_drift_kinds_and_suggests_translate_without_acting(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))
        flat = _flat(body)

        for token in (
            "`missing`",
            "`extra`",
            "`reordered`",
            "`unparseable`",
            "`stale`",
            "`staleness_error`",
            "`in_sync`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, flat)
        self.assertIn("/translate $1 $2 $3", flat)
        self.assertIn("only reads and reports", flat)
        self.assertIn("Do not translate, edit, write, or commit", flat)

    def test_body_states_the_inputs_and_the_exclusions(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))
        flat = _flat(body)

        for domain in _IN_SCOPE_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(domain, flat)
        self.assertIn("`feat` and `adr` are always English and out of scope", flat)
        self.assertIn("`en` is never checked", flat)
        self.assertIn("`question` tool", flat)


class TestSurfaceMatchesTheRegisteredTools(unittest.TestCase):
    """The tools the host surface points at are real, registered tools, and no translating tool exists."""

    def test_both_tools_are_registered(self):
        from biz.dfch.specmgr.server import mcp

        tools = {tool.name for tool in asyncio.run(mcp.list_tools())}

        for tool in _TOOL_NAMES:
            with self.subTest(tool=tool):
                self.assertIn(tool, tools)

    def test_no_registered_tool_translates(self):
        from biz.dfch.specmgr.server import mcp

        tools = {tool.name for tool in asyncio.run(mcp.list_tools())}

        self.assertEqual({name for name in tools if "translat" in name}, {"check_translation_drift"})

    def test_the_skill_the_command_hands_off_to_exists(self):
        self.assertTrue((_REPO_ROOT / ".opencode" / "skill" / "translate-artifact" / "SKILL.md").is_file())
        self.assertTrue((_REPO_ROOT / ".opencode" / "command" / "translate.md").is_file())


if __name__ == "__main__":
    unittest.main()
