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

"""feat-250-c4-structurizr-skills Phase 110, Task 110.150 (ACC-011): pin the structurizr-validate-loop skill.

The first of the feature's five skills, ``.opencode/skill/structurizr-validate-loop/``
 — the mandatory loop over the Structurizr MCP's ``parse``, ``validate`` and
 ``inspect`` tools (REQ-003) — as measured to its stop rule in iteration 2
 (the measured winner was variant ``927d6c3fc039…``; the committed variant is
 ``48c9b87bdee8…``, differing only in the one-character DEC-citation typo the
 2026-11-07 review remediation fixed — a citation-only editorial change, the
 trigger description and instructions are byte-identical, so the measured
 behavioral identity is preserved). These tests pin, read-only from
the committed files (no network, no Docker, no model): the file location (the
project skill path ``.opencode/skill/`` — singular ``skill/`` dir, the plural
``skills/`` no longer exists — with exactly the five markdown files:
``SKILL.md``, ``NOTICE.md``, ``source-map.md`` and the two ``references/``
files, REQ-007's markdown-only rule); the frontmatter (exactly the
``name``/``description`` keys, ``name`` equal to the folder, a non-empty
third-person ``description``); the description's trigger surface (the four
positive phrases, the task naming, and the iteration-2 negative clause
replacing iteration 1's organic clause — whose over-broad trigger loaded the
skill on 4/5 no-trigger render requests, breaking the trap — so the other
skills' vocabulary is asserted ABSENT from the description,
case-insensitive substring); the mandatory loop wording (parse → validate
until ``OK`` → inspect → triage EVERY finding with the three labels
fix / expected under the MCP limits / reported in the final answer,
re-validate-after-edit, return the exact text that last got ``OK``,
parsed-only is NOT a pass, the DEC 7a626b12 precedent); the iteration-2
additions (the "How to call the tools" Code Mode rules, the final-answer
template markers, the single-file fallback protocol); the three REQ-006 limit
statements; the REQ-011 no-MCP wording; the adapted reference files' content
(including the inverted ``!docs``/``!adrs`` triage); and the ``NOTICE.md`` +
``source-map.md`` pair with its two-file adapted-text invariant and the
ideas-only marks (ACC-010).

Phrase pins are matched against whitespace-normalized text (every run of
whitespace collapsed to one space) so they survive the committed files'
hard line-wrapping; the description pins are matched case-insensitively on
 the raw description, since opencode surfaces it verbatim to agents.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "structurizr-validate-loop"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_NOTICE_PATH = _SKILL_DIR / "NOTICE.md"
_SOURCE_MAP_PATH = _SKILL_DIR / "source-map.md"
_VALIDATE_VS_INSPECT_PATH = _SKILL_DIR / "references" / "validate-vs-inspect.md"
_GOTCHAS_PATH = _SKILL_DIR / "references" / "dsl-gotchas.md"
_SKILL_NAME = "structurizr-validate-loop"
_EXPECTED_FILES: frozenset[str] = frozenset(
    {
        "SKILL.md",
        "NOTICE.md",
        "source-map.md",
        "references/validate-vs-inspect.md",
        "references/dsl-gotchas.md",
    }
)
_TRIGGER_PHRASES: tuple[str, ...] = (
    "validate a Structurizr workspace",
    "check the DSL",
    "inspect findings",
    "is my model valid",
)
_NEGATIVE_CLAUSE = "It checks DSL text only and does not itself produce any files."
# Vocabulary of the other four feature skills (and image rendering generally):
# absent from the description, case-insensitively, keeps the no-trigger trap
# intact (iteration 1's organic clause loaded the skill on 4/5 render requests).
_FORBIDDEN_DESCRIPTION_WORDS: tuple[str, ...] = ("render", "image", "png", "svg", "view", "design", "review")

_LOOP_PHRASES: tuple[str, ...] = (
    "Every DSL result runs through this loop before it is returned",
    "1. **Parse.** Run the `parse` tool on the DSL text.",
    "2. **Validate until OK.** Run the `validate` tool.",
    "Keep going until `validate` answers `OK`",
    "3. **Inspect.** Run the `inspect` tool on the validated text.",
    "4. **Triage EVERY finding** into exactly one of the three labels",
    "- **fix** — correct the DSL.",
    "- **expected under the MCP limits** — the finding is caused by a limit of the MCP",
    "- **reported in the final answer** — a genuine recommendation",
    "A finding that cannot be cleared under the MCP never blocks the result.",
    "5. **Return the exact text that last got `OK` from `validate`.**",
    "Any edit after the final validate requires re-validating",
    "if anything is edited after the final validate, re-run `validate`",
    "a parsed-only or reported-only result is not a pass",
    # DEC 7a626b12 precedent: the full id (the body carried a one-character
    # typo, fixed by the 2026-11-07 review remediation).
    "the repo's own PlantUML validation chain (DEC 7a626b12-b189-4561-a51d-ffb2e9e193b4)",
    "a structure-only check is not a pass",
)

_CODE_MODE_PHRASES: tuple[str, ...] = (
    "## How to call the tools",
    "One MCP call per block, with the raw answer",
    "(no `Promise.all`/ `allSettled`)",
    "never wrap even a single answer",
    "the block `return`s the tool's own answer",
    "not `return { validate: result }`",
    "No filesystem in Code Mode",
    "every call takes the workspace text inline",
    "inlines the exact file text as a plain literal",
    "not a variable, not a shorthand",
    "byte-identical to the final literal",
    "same trailing newline",
    "re-read it right before the final call when in doubt",
    "the file on disk is the result",
    "Fix the named error, not a guess",
    "Do not build experiment harnesses",
)

_TEMPLATE_MARKERS: tuple[str, ...] = (
    "Validation: `validate` answered OK on the exact text now in workspace.dsl.",
    "Findings (triaged):",
    '- fix: "<the finding\'s exact text>" — what you changed',
    '- expected: "<the finding\'s exact text>" — the MCP refuses `!docs`/`!adrs`',
    '- reported: "<the finding\'s exact text>"',
    "MCP limits: <any limit that shaped the result; name `!include`/`!docs` when relevant>",
    "quoting each finding's exact text",
)

_LIMIT_PHRASES: tuple[str, ...] = (
    "## The MCP limits",
    "- **DSL text only, single file.**",
    "there is no multi-file workspace",
    "- **`!include`, `!docs`, and `!adrs` are refused.**",
    "is not permitted (feature structurizr.feature.dsl.filesystem is not enabled)",
    "documentation is not enabled",
    "At most one attempt",
    "fall back to a single file",
    "Never use a `!theme` with a URL",
    "In the final answer, name `!include` and `!docs`",
    "- **No image rendering.**",
    "cannot produce image files (PNG/SVG)",
    "emit diagram source only — PlantUML, C4-PlantUML, or Mermaid text",
)

_NO_MCP_PHRASES: tuple[str, ...] = (
    "## When the MCP is absent",
    "validation is not possible",
    "never describe a DSL result as validated",
)

_VALIDATE_VS_INSPECT_PHRASES: tuple[str, ...] = (
    "Two tools, two questions",
    "Will this parse into a workspace?",
    "Does this follow C4 and Structurizr recommendations?",
    "Nothing is valid until it answers `OK`",
    "Never treat a finding list like a failed validate",
    "## Common validate errors",
    "## Common inspect findings",
    "expected under the MCP limits — the MCP refuses `!docs`; do not add it. Report the finding as expected in the final answer",
    "expected under the MCP limits — the MCP refuses `!adrs`; do not add it. Report the finding as expected in the final answer",
    "Report inspect findings grouped by rule id with counts",
    "Do not describe the workspace as broken because of them",
)

_VALIDATE_VS_INSPECT_RULE_IDS: tuple[str, ...] = (
    "workspace.scope",
    "model.relationship.technology",
    "model.relationship.description",
    "model.softwaresystem.documentation",
    "model.softwaresystem.decisions",
    "views.view.key",
)

_GOTCHAS_PHRASES: tuple[str, ...] = (
    "Each rule exists because",
    "## Declaration order",
    "The DSL is parsed top to bottom",
    "## Quoting",
    "Quote every name, description, and technology",
    "## Relationship description and technology",
    "## Flat identifiers",
    "## Explicit view keys",
    "View keys can only contain the following characters: a-zA-Z0-9_-",
)

_NOTICE_PHRASES: tuple[str, ...] = (
    "passionsplay/structurizr-skill",
    "5e45154e1c266e0517d456855b415ba770412f16",
    "Copyright (c) 2026 Benjamin Turner",
    "MIT License",
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,',
    "## Which local files adapt which source files",
    "`SKILL.md` adapts no text (ideas only",
    "carries no attribution line",
)

_SOURCE_MAP_PHRASES: tuple[str, ...] = (
    "adapted text exists in exactly the two files `NOTICE.md` lists",
    "## `SKILL.md` — ideas only",
    "No passage in `SKILL.md` copies text; it has no attribution line in `NOTICE.md`.",
    "## Dropped upstream content (no local passage)",
    "**inverted** per the locked adaptation rule",
)


def _read_text(path: Path) -> str:
    """Read a committed skill file verbatim (a missing file is a hard failure)."""
    assert path.is_file(), path
    result = path.read_text(encoding="utf-8")
    return result


def _norm(text: str) -> str:
    """Collapse every whitespace run to one space (hard-wrapping-robust pins)."""
    result = re.sub(r"\s+", " ", text)
    return result


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split the leading ``---`` YAML block from the body (simple line split, no yaml dependency)."""
    lines = text.splitlines()
    assert lines and lines[0] == "---", "SKILL.md must open with a --- frontmatter delimiter"
    closing = [index for index in range(1, len(lines)) if lines[index] == "---"]
    assert closing, "SKILL.md frontmatter has no closing --- delimiter"
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


def _skill_body() -> str:
    """The whitespace-normalized SKILL.md body (frontmatter stripped)."""
    _, body = _split_frontmatter(_read_text(_SKILL_PATH))
    result = _norm(body)
    return result


class TestSkillFileLocations(unittest.TestCase):
    """The five markdown files at the singular ``skill/`` path (REQ-007)."""

    def test_skill_dir_is_under_the_singular_skill_directory(self):
        self.assertTrue((_REPO_ROOT / ".opencode" / "skill").is_dir())
        self.assertFalse((_REPO_ROOT / ".opencode" / "skills").exists(), "plural skills/ dir must not exist")
        self.assertTrue(_SKILL_DIR.is_dir())

    def test_all_expected_files_exist(self):
        for relative in sorted(_EXPECTED_FILES):
            self.assertTrue((_SKILL_DIR / relative).is_file(), relative)

    def test_skill_dir_holds_exactly_the_five_markdown_files(self):
        result = sorted(str(path.relative_to(_SKILL_DIR)) for path in _SKILL_DIR.rglob("*") if path.is_file())

        self.assertEqual(set(result), _EXPECTED_FILES)
        for relative in result:
            self.assertTrue(relative.endswith(".md"), f"non-markdown file next to SKILL.md: {relative}")


class TestSkillFrontmatter(unittest.TestCase):
    """Exactly two frontmatter keys; name equals the folder; third-person description."""

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


class TestDescriptionTriggerSurface(unittest.TestCase):
    """The iteration-2 trigger surface: the four phrases plus the task naming,
    the negative clause, and the other skills' vocabulary ABSENT (the trap)."""

    def _description_lower(self) -> str:
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)
        return result["description"].lower()

    def test_description_names_the_task(self):
        self.assertIn("checking or validating", self._description_lower())

    def test_description_carries_the_four_positive_trigger_phrases(self):
        description = self._description_lower()

        for phrase in _TRIGGER_PHRASES:
            self.assertIn(phrase.lower(), description, phrase)

    def test_description_carries_the_iteration_2_negative_clause(self):
        self.assertIn(_NEGATIVE_CLAUSE.lower(), self._description_lower())

    def test_description_carries_no_other_skill_vocabulary(self):
        description = self._description_lower()

        for word in _FORBIDDEN_DESCRIPTION_WORDS:
            self.assertNotIn(word, description, f"no-trigger trap broken by description word: {word}")


class TestMandatoryLoopWording(unittest.TestCase):
    """REQ-003/ACC-002: parse → validate until OK → inspect → triage every
    finding, re-validate after edits, return the exact OK text, DEC precedent."""

    def test_loop_phrases_present(self):
        body = _skill_body()

        for phrase in _LOOP_PHRASES:
            self.assertIn(phrase, body, phrase)

    def test_dec_precedent_sentence_present(self):
        body = _skill_body()

        self.assertIn("A DSL result that was only parsed, and not validated to `OK`, is NOT a pass", body)


class TestHowToCallTheTools(unittest.TestCase):
    """Iteration-2 addition: the Code Mode call-shape rules (one call per block
    with the raw answer, no filesystem, the plain inline literal, fix the
    named error)."""

    def test_code_mode_phrases_present(self):
        body = _skill_body()

        for phrase in _CODE_MODE_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestFinalAnswerTemplate(unittest.TestCase):
    """Iteration-2 addition: the final-answer shape with its template markers
    and the quote-every-finding rule."""

    def test_template_markers_present(self):
        body = _skill_body()

        for phrase in _TEMPLATE_MARKERS:
            self.assertIn(phrase, body, phrase)


class TestMcpLimitStatements(unittest.TestCase):
    """REQ-006/ACC-003 in full: DSL text only / single file, the refused
    ``!include``/``!docs``/``!adrs`` with the refusal reading and the
    single-file fallback protocol, no image rendering."""

    def test_limit_phrases_present(self):
        body = _skill_body()

        for phrase in _LIMIT_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestNoMcpBehavior(unittest.TestCase):
    """REQ-011: without the MCP, validation is not possible and no result may
    be described as validated."""

    def test_no_mcp_phrases_present(self):
        body = _skill_body()

        for phrase in _NO_MCP_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestValidateVsInspectReference(unittest.TestCase):
    """The adapted two-tool table (passionsplay @ 5e45154e) with the inverted
    ``!docs``/``!adrs`` triage and both error/finding tables."""

    def test_reference_phrases_present(self):
        text = _norm(_read_text(_VALIDATE_VS_INSPECT_PATH))

        for phrase in _VALIDATE_VS_INSPECT_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_reference_rule_ids_present(self):
        text = _norm(_read_text(_VALIDATE_VS_INSPECT_PATH))

        for rule_id in _VALIDATE_VS_INSPECT_RULE_IDS:
            self.assertIn(rule_id, text, rule_id)


class TestDslGotchasReference(unittest.TestCase):
    """The adapted gotcha set, including the iteration-2 "Explicit view keys"
    section (ideas only, marked as such in the source map)."""

    def test_gotchas_phrases_present(self):
        text = _norm(_read_text(_GOTCHAS_PATH))

        for phrase in _GOTCHAS_PHRASES:
            self.assertIn(phrase, text, phrase)


class TestNoticeAndSourceMap(unittest.TestCase):
    """ACC-010: the MIT notice with its two-file mapping, the source map with
    its ideas-only marks, and the two files' mutual consistency."""

    def test_notice_carries_source_commit_copyright_and_mit_text(self):
        notice = _read_text(_NOTICE_PATH)

        for phrase in _NOTICE_PHRASES:
            self.assertIn(phrase, notice, phrase)
        self.assertEqual(notice.count("Copyright (c) 2026 Benjamin Turner"), 2)

    def test_notice_maps_exactly_the_two_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)

        self.assertIn("| `references/validate-vs-inspect.md` |", notice)
        self.assertIn("| `references/dsl-gotchas.md` |", notice)
        table_rows = [
            line for line in notice.splitlines() if line.startswith("| `references/") and line.rstrip().endswith("|")
        ]

        self.assertEqual(len(table_rows), 2)

    def test_source_map_phrases_present(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        for phrase in _SOURCE_MAP_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_source_map_marks_the_iteration_2_additions_ideas_only(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        self.assertEqual(text.count("added in iteration 2"), 3)
        self.assertEqual(text.count("extended in iteration 2"), 1)

    def test_notice_and_source_map_agree_on_the_two_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)
        source_map = _norm(_read_text(_SOURCE_MAP_PATH))

        for relative in ("references/validate-vs-inspect.md", "references/dsl-gotchas.md"):
            self.assertIn(relative, notice)
            self.assertIn(f"## `{relative}`", source_map)


if __name__ == "__main__":
    unittest.main()
