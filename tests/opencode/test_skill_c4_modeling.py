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

"""feat-250-c4-structurizr-skills Phase 130, Task 130.150 (ACC-011): pin the c4-modeling skill.

The feature's third skill, ``.opencode/skill/c4-modeling/`` — the C4
modeling decisions: the levels, what counts as a container (and what does
not), how to model external systems in the pinned DSL, naming/description
rules, and the common modeling mistakes (REQ-001) — as measured to its
stop rule in Phase 130. These tests pin, read-only from the committed
files (no network, no Docker, no model): the file location (the project
skill path ``.opencode/skill/`` — singular ``skill/`` dir — with exactly
the five markdown files: ``SKILL.md``, ``NOTICE.md``, ``source-map.md``
and the two ``references/`` files, REQ-007's markdown-only rule); the
frontmatter (exactly the ``name``/``description`` keys, ``name`` equal to
the folder, a non-empty third-person ``description``); the description's
trigger surface (the positive trigger phrases, the single-task naming,
the negative clause, and the other skills' vocabulary asserted ABSENT
from the description, case-insensitive substring — the no-trigger trap of
this phase's case set); the REQ-001 content pins (the six decisions in
``SKILL.md``, the C4 levels and container/not-container rules, the
pinned-DSL external-system fact, the notation/relationship-label rules,
the workflow steps 1–3, the common modeling decisions, the generic common
mistakes #1–9, the diagram-staleness table); the locked removals (the
Elixir/OTP content ABSENT, the Docker-CLI validation content ABSENT, the
diagram types/selection guide ABSENT — the scope cut); the light
MCP-validate pointer (NOT the full loop — the validate-loop skill's
single task); the REQ-006 limit statements the skill depends on (DSL text
only / single file, the refused ``!include``/``!docs``, no image
rendering); the REQ-011 no-MCP wording; and the ``NOTICE.md`` +
``source-map.md`` pair with its two-file adapted-text invariant and the
ideas-only marks (ACC-010).

Phrase pins are matched against whitespace-normalized text (every run of
whitespace collapsed to one space) so they survive the committed files'
hard line-wrapping; the description pins are matched case-insensitively
on the raw description, since opencode surfaces it verbatim to agents.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "c4-modeling"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_NOTICE_PATH = _SKILL_DIR / "NOTICE.md"
_SOURCE_MAP_PATH = _SKILL_DIR / "source-map.md"
_LEVELS_PATH = _SKILL_DIR / "references" / "levels-and-notation.md"
_DECISIONS_PATH = _SKILL_DIR / "references" / "modeling-decisions.md"
_SKILL_NAME = "c4-modeling"
_EXPECTED_FILES: frozenset[str] = frozenset(
    {
        "SKILL.md",
        "NOTICE.md",
        "source-map.md",
        "references/levels-and-notation.md",
        "references/modeling-decisions.md",
    }
)
_TRIGGER_PHRASES: tuple[str, ...] = (
    "create a C4 model",
    "decide what is a container",
    "model an external system",
    "C4 levels",
    "label these relationships",
)
_NEGATIVE_CLAUSE = "It explains the modeling decisions only and does not itself produce any files."
# Vocabulary of the other four feature skills (and image rendering
# generally): absent from the description, case-insensitively, keeps the
# no-trigger trap intact (this phase's no-trigger case measures exactly
# this — an over-broad description loads the skill on a render-to-image
# request and fails `no_mounted_skill_loaded`).
_FORBIDDEN_DESCRIPTION_WORDS: tuple[str, ...] = (
    "render",
    "image",
    "png",
    "svg",
    "view",
    "validate",
    "inspect",
    "triage",
    "review",
    "design",
    "parse",
    "syntax",
    "workspace.dsl",
    "error",
)

_DECISION_PHRASES: tuple[str, ...] = (
    "## The decisions",
    "1. **Pick the abstraction level first.**",
    "Person (a user or role), Software System (Level 1), Container (Level 2), Component (Level 3), Code (Level 4)",
    "2. **A container is a runtime boundary**",
    "A C4 container is not a Docker container",
    # the shared/embedded-library trap (iteration-1 measured: the library
    # was modeled as a container/component with "embeds" relationships)
    "When several elements share or embed a library, the library is STILL no element",
    'no "embeds" relationship to it',
    "3. **External and third-party systems are top-level, tagged",
    "In this DSL version there is no `externalSystem` keyword",
    "4. **Name and describe every element.**",
    "5. **Label every relationship with its intent and a technology.**",
    # technology on EVERY relationship (iteration-1 measured: 0% technology
    # coverage on the person-to-container and "embeds" relationships)
    "EVERY relationship names a protocol",
    "a relationship without a technology is incomplete",
    "6. **Split containers on runtime boundaries**",
    "`references/levels-and-notation.md`",
    "`references/modeling-decisions.md`",
)

_LEVELS_PHRASES: tuple[str, ...] = (
    "## Level 1: Software System",
    "Is NOT: a product domain, bounded context, business capability",
    "## Level 2: Container",
    "A **runtime boundary** — not a code-organization unit",
    "Examples: server-side web app, SPA (client-side), mobile app, database",
    "**NOT containers**: JARs, DLLs, assemblies, libraries, modules",
    "**NOT Docker containers** — the name is coincidental",
    "A single-page app is TWO containers",
    "Cloud services you own (S3 buckets, RDS instances) are containers, not external systems",
    "## Level 3: Component",
    "Language-dependent: classes (OOP), modules (JS), grouped functions",
    "## Level 4: Code",
    "## Notation Rules",
    "### Required Elements",
    "### Technology Labels",
    "Every relationship includes a protocol/technology",
    "### Relationship Lines",
    "Unidirectional only",
    '"sends customer update events to", "reads credentials from"',
    '"Uses", "Connects to", "Interacts with", "Talks to", "Communicates with"',
    "## Workflow: Adding Elements to a Model",
    "### Step 1: Identify the Abstraction Level",
    "### Step 2: Define the Element",
    "### Step 3: Define Relationships",
)

_DECISIONS_PHRASES: tuple[str, ...] = (
    "## When to Split a Container",
    "Parts deploy independently",
    "## When to Add Components",
    "architecturally significant",
    "## When to Model External Systems",
    "You don't own or control it",
    "there is no `externalSystem` keyword",
    "**top-level** `softwareSystem` (or `element`) carrying the `External` tag",
    "the export JSON's `externalSystems` section is never populated",
    "## Common Mistakes",
    "1. **Confusing containers with Docker containers**",
    "2. **Treating libraries as containers**",
    "When several elements share or embed a library, the library is still no element",
    "3. **Vague relationship labels**",
    "4. **Missing technology on inter-container relationships**",
    "9. **Modeling organizational structure**",
    "## Diagram Staleness",
    "| System Context | Slow | Low — create and maintain |",
)

_MCP_CHECK_PHRASES: tuple[str, ...] = (
    "## Checking the result",
    "check the workspace text with the structurizr MCP",
    "`validate` tool",
    # validate-until-OK, the light pointer (iteration-1 measured: trials
    # finishing while validate still reported errors)
    "until it answers `OK`",
    "do not finish while `validate` is still reporting errors",
    "model whose workspace does not validate is not done",
    "call whichever prefixed variant your host exposes",
    # the light pointer must NOT prescribe the full loop (that is the
    # validate-loop skill's single task)
)

_LIMIT_PHRASES: tuple[str, ...] = (
    "## The MCP limits",
    "- **DSL text only, single file.**",
    "there is no multi-file workspace",
    "Inline everything into the one file",
    "`!include` and `!docs` are refused",
    "- **No image rendering.**",
    "cannot produce image files (PNG/SVG)",
    "emit diagram source only — PlantUML, C4-PlantUML, or Mermaid text",
)

_NO_MCP_PHRASES: tuple[str, ...] = (
    "## When the MCP is absent",
    "validation is not possible",
    "never describe a DSL result as validated",
)

_NOTICE_PHRASES: tuple[str, ...] = (
    "jrjsmrtn/c4-skills",
    "e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b",
    "Copyright (c) 2026 Georges Martin",
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
    "Erlang/Elixir/OTP Modeling Guide",
    "Diagram Types",
    "Diagram Selection Guide",
    'Docker-CLI "Validation" section',
    "Related Skills",
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
    """The trigger surface: the positive phrases, the single-task naming,
    the negative clause, and the other skills' vocabulary ABSENT (the
    no-trigger trap of this phase's case set)."""

    def _description_lower(self) -> str:
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)
        return result["description"].lower()

    def test_description_names_the_task(self):
        self.assertIn("making c4 modeling decisions", self._description_lower())

    def test_description_carries_the_positive_trigger_phrases(self):
        description = self._description_lower()

        for phrase in _TRIGGER_PHRASES:
            self.assertIn(phrase.lower(), description, phrase)

    def test_description_carries_the_negative_clause(self):
        self.assertIn(_NEGATIVE_CLAUSE.lower(), self._description_lower())

    def test_description_carries_no_other_skill_vocabulary(self):
        description = self._description_lower()

        for word in _FORBIDDEN_DESCRIPTION_WORDS:
            self.assertNotIn(word, description, f"no-trigger trap broken by description word: {word}")


class TestDecisionsSection(unittest.TestCase):
    """REQ-001: the six modeling decisions in SKILL.md, incl. the
    pinned-DSL external-system fact."""

    def test_decision_phrases_present(self):
        body = _skill_body()

        for phrase in _DECISION_PHRASES:
            self.assertIn(phrase, body, phrase)

    def test_no_full_loop_prescribed(self):
        # the light pointer is this skill's; the mandatory loop (parse
        # until..., triage EVERY finding, the exact-OK-text rule) belongs
        # to the validate-loop skill and must not be prescribed here
        body = _skill_body()

        self.assertNotIn("Triage EVERY finding", body)
        self.assertNotIn("The mandatory loop", body)
        self.assertIn("the `structurizr-validate-loop` skill's task", body)


class TestMcpCheckPointer(unittest.TestCase):
    """The light validate-before-finish pointer (not the full loop)."""

    def test_check_pointer_phrases_present(self):
        body = _skill_body()

        for phrase in _MCP_CHECK_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestMcpLimitStatements(unittest.TestCase):
    """REQ-006/ACC-003: the limits this skill depends on — DSL text only /
    single file, the refused ``!include``/``!docs``, no image rendering."""

    def test_limit_phrases_present(self):
        body = _skill_body()

        for phrase in _LIMIT_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestNoMcpBehavior(unittest.TestCase):
    """REQ-011: without the MCP, validation is not possible and no result
    may be described as validated."""

    def test_no_mcp_phrases_present(self):
        body = _skill_body()

        for phrase in _NO_MCP_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestLevelsAndNotationReference(unittest.TestCase):
    """The adapted levels/notation/workflow reference (upstream
    `c4-model`), with the locked Elixir removals and the scope cut."""

    def test_levels_phrases_present(self):
        text = _norm(_read_text(_LEVELS_PATH))

        for phrase in _LEVELS_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_no_elixir_or_otp_content(self):
        text = _norm(_read_text(_LEVELS_PATH)).lower()

        for word in ("elixir", "otp", "phoenix", "oban", "genServer", "beam", "erlang"):
            self.assertNotIn(word, text, f"locked-removed content in levels-and-notation.md: {word}")

    def test_no_diagram_types_or_selection_guide(self):
        # the locked scope cut: "which views to create" is the
        # c4-view-design skill's single task (REQ-004/REQ-007)
        text = _read_text(_LEVELS_PATH)

        self.assertNotIn("## Diagram Types", text)
        self.assertNotIn("Diagram Selection Guide", text)
        self.assertNotIn("Core Diagrams", text)


class TestModelingDecisionsReference(unittest.TestCase):
    """The adapted decisions/mistakes/staleness reference (upstream
    `c4-model`), the generic mistakes only, plus the pinned-DSL
    external-system fact."""

    def test_decision_phrases_present(self):
        text = _norm(_read_text(_DECISIONS_PATH))

        for phrase in _DECISIONS_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_only_the_generic_mistakes_remain(self):
        text = _read_text(_DECISIONS_PATH)

        self.assertIn("## Common Mistakes", text)
        self.assertNotIn("10. **", text, "Elixir/OTP-specific mistake #10 must be dropped")
        for word in ("GenServers as containers", "supervisor trees", "OTP application", "Phoenix PubSub"):
            self.assertNotIn(word, text)

    def test_no_elixir_or_docker_cli_content(self):
        text = _norm(_read_text(_DECISIONS_PATH)).lower()

        for word in ("elixir", "phoenix", "oban", "podman", "wslc", "docker run", "$runtime"):
            self.assertNotIn(word, text, f"locked-removed content in modeling-decisions.md: {word}")

    def test_no_diagram_types_or_selection_guide(self):
        text = _read_text(_DECISIONS_PATH)

        self.assertNotIn("Diagram Selection Guide", text)
        self.assertNotIn("Core Diagrams", text)


class TestNoticeAndSourceMap(unittest.TestCase):
    """ACC-010: the MIT notice with its two-file mapping, the source map
    with its ideas-only marks and the dropped-content list, and the two
    files' mutual consistency (the adapted text exists exactly in the
    files NOTICE.md lists)."""

    def test_notice_carries_the_source_commit_copyright_and_mit_text(self):
        notice = _read_text(_NOTICE_PATH)

        for phrase in _NOTICE_PHRASES:
            self.assertIn(phrase, notice, phrase)
        # the section heading + the first line of the license block
        self.assertEqual(notice.count("MIT License"), 2)
        self.assertEqual(notice.count("Copyright (c) 2026 Georges Martin"), 2)

    def test_notice_maps_exactly_the_two_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)

        self.assertIn("| `references/levels-and-notation.md` |", notice)
        self.assertIn("| `references/modeling-decisions.md` |", notice)
        table_rows = [
            line for line in notice.splitlines() if line.startswith("| `references/") and line.rstrip().endswith("|")
        ]

        self.assertEqual(len(table_rows), 2)

    def test_source_map_phrases_present(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        for phrase in _SOURCE_MAP_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_source_map_marks_skill_md_ideas_only(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        self.assertIn("## `SKILL.md` — ideas only", text)
        self.assertGreaterEqual(text.count("Ideas only"), 1)

    def test_notice_and_source_map_agree_on_the_two_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)
        source_map = _norm(_read_text(_SOURCE_MAP_PATH))

        for relative in ("references/levels-and-notation.md", "references/modeling-decisions.md"):
            self.assertIn(relative, notice)
            self.assertIn(f"## `{relative}`", source_map)


if __name__ == "__main__":
    unittest.main()
