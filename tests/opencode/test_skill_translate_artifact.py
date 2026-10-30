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

"""feat-197-i18n Phase 130, Task 130.110: host-surface pin for the translate-artifact skill + command.

The thin self-triggering ``.opencode/skill/translate-artifact/SKILL.md`` -- plus the optional
``.opencode/command/translate.md`` -- points agents at the ``translate_artifact`` MCP prompt flow and the
``specmgr://i18n`` guidance instead of restating them. Like ``uc-diagram`` (and unlike ``repair``) there is no
dedicated subagent: the flow is the prompt itself. These tests pin: the file locations (the **singular**
``.opencode/skill/`` path -- the repair/uc-diagram family's location); the skill's frontmatter (exactly the
``name``/``description`` keys, ``name`` matching the folder, a non-empty third-person ``description`` carrying the
trigger phrasing -- keyword matching is case-insensitive, as in ``test_skill_uc_diagram.py``); the key body wording
(the prompt name, the ``specmgr://i18n`` resource read first, the ``translate_artifact`` flow's contract: the
create-versus-update flow, the closed-vocabulary never-translate rule, the ``prb`` ``problem_statement`` exemption,
the no-dry-run/``ValidateResult`` retry, the ``question``/never-commit contract, the feat/adr exclusion); and the
command's frontmatter (a ``description`` naming ``$1``..``$4``, **no** ``agent:`` field) plus its body's prompt-flow
and step-9 report pointers. The prompt this host surface points at is real and registered (cross-checked).
"""

from __future__ import annotations

import asyncio
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "translate-artifact"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_COMMAND_PATH = _REPO_ROOT / ".opencode" / "command" / "translate.md"
_SKILL_NAME = "translate-artifact"
_TRIGGER_PHRASES: tuple[str, ...] = (
    "translate this requirement into German",
    "create a German version of REQ",
    "update the French translation of",
    "specmgr",
    "/translate",
)
_PROMPT_NAME = "translate_artifact"
_RESOURCE_URI = "specmgr://i18n"
_IN_SCOPE_DOMAINS: tuple[str, ...] = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr", "sysrs")
_CONTRACT_WORDS: tuple[str, ...] = ("question", "Never commit", "Never translate a closed-vocabulary")


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
        self.assertEqual([p.name for p in agent_dir.glob("*transl*")], [])


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
    """The thin pointer set: resource read first, prompt, the flow's contract, the exclusion."""

    def test_prompt_pointer_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        self.assertIn(_PROMPT_NAME, body)
        self.assertIn("the only sanctioned path for a translation", _flat(body))

    def test_resource_uri_is_read_first(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        self.assertIn(_RESOURCE_URI, body)
        self.assertIn("Read the guidance first", body)
        self.assertLess(body.index(_RESOURCE_URI), body.index(_PROMPT_NAME))

    def test_flow_contract_points_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        self.assertIn("get_<d>(id, raw=True, language=...)", flat)
        self.assertIn("`ParseFailureResult` stops the flow", flat)
        self.assertIn("create-versus-update", flat)
        self.assertIn("non-raising `ValidateResult`", flat)
        self.assertIn("cannot dry-run a translation", flat)
        self.assertIn("never the closed-vocabulary tokens", flat)
        self.assertIn("`problem_statement`", flat)
        self.assertIn("get_<d>(id, language=...)", flat)

    def test_heading_table_is_read_through_the_resource_template_without_host_file_tools(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        self.assertIn("specmgr://i18n/headings/{language}", flat)
        self.assertIn("no host file tool needed", flat)

    def test_feat_adr_exclusion_and_no_table_rule_stated(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))
        flat = _flat(body)

        self.assertIn("`feat` and `adr` are always English", flat)
        self.assertIn("no language variants and no `language` parameter", flat)
        self.assertIn("general/data/headings/<language>.json", flat)
        self.assertIn("never invent one", flat)

    def test_question_and_never_commit_contract_present(self):
        _, body = _split_frontmatter(_read_text(_SKILL_PATH))

        for word in _CONTRACT_WORDS:
            with self.subTest(word=word):
                self.assertIn(word, body)


class TestCommandFrontmatterAndBody(unittest.TestCase):
    """The command names its inputs, carries no agent: field (no dedicated subagent), and runs the prompt flow."""

    def test_frontmatter_carries_a_description_only(self):
        frontmatter, _ = _split_frontmatter(_read_text(_COMMAND_PATH))

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(set(result), {"description"})
        for placeholder in ("$1", "$2", "$3", "$4"):
            with self.subTest(placeholder=placeholder):
                self.assertIn(placeholder, result["description"])
        self.assertNotIn("agent", result)

    def test_body_runs_the_prompt_flow_and_reports_per_step_9(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))

        self.assertIn(_PROMPT_NAME, body)
        self.assertIn(_RESOURCE_URI, body)
        self.assertIn("step 9", body)
        self.assertIn("Do not commit", _flat(body))
        self.assertIn("do not write the English document", _flat(body))

    def test_body_states_the_inputs_and_the_exclusions(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))
        flat = _flat(body)

        for domain in _IN_SCOPE_DOMAINS:
            with self.subTest(domain=domain):
                self.assertIn(domain, flat)
        self.assertIn("`feat` and `adr` are always English and out of scope", flat)
        self.assertIn("`en` is never a target", flat)
        self.assertIn("`problem_statement`", flat)
        self.assertIn("`question` tool", flat)
        self.assertIn("specmgr://i18n/headings/<language>", flat)


class TestSurfaceMatchesTheRegisteredPrompt(unittest.TestCase):
    """The prompt and resource the host surface points at are real, registered artifacts."""

    def test_prompt_and_resource_are_registered(self):
        from biz.dfch.specmgr.server import mcp

        prompts = {p.name for p in asyncio.run(mcp.list_prompts())}
        resources = {str(r.uri) for r in mcp._resource_manager.list_resources()}
        templates = {t.uri_template for t in mcp._resource_manager.list_templates()}

        self.assertIn(_PROMPT_NAME, prompts)
        self.assertIn(_RESOURCE_URI, resources)
        self.assertIn("specmgr://i18n/headings/{language}", templates)


if __name__ == "__main__":
    unittest.main()
