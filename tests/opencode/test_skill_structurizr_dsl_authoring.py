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

"""feat-250-c4-structurizr-skills Phase 120, Task 120.150 (ACC-011): pin the structurizr-dsl-authoring skill.

The feature's second skill, ``.opencode/skill/structurizr-dsl-authoring/`` —
how to write and repair Structurizr DSL workspace text (REQ-002) — as
measured to its stop rule in Phase 120. These tests pin, read-only from
the committed files (no network, no Docker, no model): the file location
(the project skill path ``.opencode/skill/`` — singular ``skill/`` dir —
with exactly the six markdown files: ``SKILL.md``, ``NOTICE.md``,
``source-map.md`` and the three ``references/`` files, REQ-007's
markdown-only rule); the frontmatter (exactly the ``name``/``description``
keys, ``name`` equal to the folder, a non-empty third-person
``description``); the description's trigger surface (the positive trigger
phrases, the single-task naming, the negative clause, and the other
skills' vocabulary asserted ABSENT from the description,
case-insensitive substring — the no-trigger trap of this phase's case
set); the authoring rules (declaration order, quoting, braces, flat
identifiers, relationship description + technology, element descriptions,
explicit view keys); the light MCP-check pointer (validate before
finishing — NOT the full parse/validate/inspect loop, which is the
validate-loop skill's single task); the three REQ-006 limit statements in
full (DSL text only / single file, the refused ``!include``/``!docs``/
``!adrs`` with the refusal reading, no image rendering, no URL theme);
the REQ-011 no-MCP wording; the adapted reference files' content; and the
``NOTICE.md`` + ``source-map.md`` pair with its three-file adapted-text
invariant and the ideas-only marks (ACC-010).

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
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "structurizr-dsl-authoring"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_NOTICE_PATH = _SKILL_DIR / "NOTICE.md"
_SOURCE_MAP_PATH = _SKILL_DIR / "source-map.md"
_SYNTAX_PATH = _SKILL_DIR / "references" / "syntax.md"
_VIEWS_PATH = _SKILL_DIR / "references" / "views-and-styles.md"
_GOTCHAS_PATH = _SKILL_DIR / "references" / "gotchas.md"
_SKILL_NAME = "structurizr-dsl-authoring"
_EXPECTED_FILES: frozenset[str] = frozenset(
    {
        "SKILL.md",
        "NOTICE.md",
        "source-map.md",
        "references/syntax.md",
        "references/views-and-styles.md",
        "references/gotchas.md",
    }
)
_TRIGGER_PHRASES: tuple[str, ...] = (
    "write a Structurizr DSL workspace",
    "author or edit workspace.dsl",
    "DSL syntax",
    "fix a DSL parse error",
)
_NEGATIVE_CLAUSE = "It describes how to write DSL text only and does not itself produce any files."
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
)

_AUTHORING_RULES: tuple[str, ...] = (
    "## The authoring rules",
    "1. **Declare elements before the relationships that use them.**",
    'The destination element "x" does not exist',
    "2. **Quote every value that contains spaces**",
    "Too many tokens, expected:",
    'use `""`',
    "3. **Braces:**",
    "the opening `{` sits on the same line as the statement",
    "4. **Identifiers are flat and unique**",
    'The identifier "x" is already in use',
    "5. **Every relationship gets a description and a technology:**",
    '`a -> b "Reads orders from" "HTTPS/JSON"`',
    "6. **Every element gets a description**",
    "7. **Give every view an explicit key**",
)

_MCP_CHECK_PHRASES: tuple[str, ...] = (
    "## Checking the result",
    "check the workspace text with the structurizr MCP",
    "`validate` tool",
    "a DSL file that does not validate is not done",
    "call whichever prefixed variant your host exposes",
    # the light pointer must NOT prescribe the full loop (that is the
    # validate-loop skill's single task)
)

_LIMIT_PHRASES: tuple[str, ...] = (
    "## The MCP limits",
    "- **DSL text only, single file.**",
    "there is no multi-file workspace",
    "Inline everything into the one file",
    "- **`!include`, `!docs`, and `!adrs` are refused.**",
    "is not permitted (feature structurizr.feature.dsl.filesystem is not enabled)",
    "documentation is not enabled",
    "expected under the MCP limits",
    "deliver the single file instead",
    "- **No image rendering.**",
    "cannot produce image files (PNG/SVG)",
    "emit diagram source only — PlantUML, C4-PlantUML, or Mermaid text",
    "**Never a `!theme` with a URL**",
)

_NO_MCP_PHRASES: tuple[str, ...] = (
    "## When the MCP is absent",
    "validation is not possible",
    "never describe a DSL result as validated",
)

_SYNTAX_PHRASES: tuple[str, ...] = (
    "## Syntax fundamentals",
    "Lines are processed **sequentially** — no forward references",
    "Keywords are **case-insensitive**",
    "### Constants and Variables",
    '!const SYSTEM_NAME "My System"',
    '!var VERSION "1.0"',
    "${SYSTEM_NAME}",
    "## Workspace structure",
    "workspace [name] [description] {",
    "!identifiers hierarchical",
    "!impliedRelationships true",
    "### Person",
    "### Software System",
    "### Container",
    "### Component",
    "### Custom element",
    "<id> = element <name> [metadata] [description] [tags]",
    "### Group",
    "## Relationships",
    "<source> -> <destination> [description] [technology] [tags]",
    "-/>",
    "### Uniqueness",
    "Relationships between the same source and destination must have **unique descriptions**",
    "## Identifiers",
    "### Flat (default)",
    "### Hierarchical (recommended)",
    'The identifier "api" is already in use',
    "system.api",
)

_VIEWS_PHRASES: tuple[str, ...] = (
    "## Views",
    "### System Landscape",
    "systemLandscape [key] [description]",
    "### System Context",
    "systemContext <systemId> [key] [description]",
    "### Container View",
    "### Component View",
    "### Dynamic View",
    "dynamic <scope> [key] [description]",
    '1: user -> system.api "submits order" "HTTPS"',
    "### Deployment View",
    "### Filtered View",
    "filtered <baseViewKey> <include|exclude> <tags> [key] [description]",
    "### AutoLayout",
    "autoLayout [direction] [rankSeparation] [nodeSeparation]",
    "### Include/Exclude with Expressions",
    "include element.type==Container",
    "include *?",
    "## Styles",
    "### Element Styles",
    "### Relationship Styles",
    "### Styling All Elements/Relationships",
    'element "Element" { ... }',
    "### Light/Dark Mode",
    "### Standard Style Recipe",
    "background #08427B",
    "## Themes",
    "theme default",
    "amazon-web-services-2020.04.30",
    "## Terminology",
    "terminology {",
    "## Configuration",
    "scope <landscape|softwaresystem|none>",
    "## Directives for existing elements",
    "!element <identifier> {",
    "!elements element.tag==Container {",
    "## Common patterns",
    "### Tagging for Filtered Views",
    "### Async/Sync Relationship Distinction",
)

_GOTCHAS_PHRASES: tuple[str, ...] = (
    "## Error table",
    "Too many tokens, expected: person <name> [description] [tags]",
    'The identifier "x" is already in use at line N',
    'The destination element "x" does not exist at line N',
    "Relationships cannot be added between parents and children",
    "View keys can only contain the following characters: a-zA-Z0-9_-",
    "## Declaration order",
    "imperative, not declarative",
    "the special `this` keyword refers to the element in scope",
    "## Quoting",
    "## Relationship description and technology",
    "authoring knowledge, not an error message",
    "## Element descriptions",
    "the second string is its **metadata**",
    "## Flat identifiers",
    "## Implied relationships",
    "!impliedRelationships false",
    "## Explicit view keys",
    "## Under the MCP",
    "Never reference a theme by URL",
)

_NOTICE_PHRASES: tuple[str, ...] = (
    "jrjsmrtn/c4-skills",
    "e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b",
    "Copyright (c) 2026 Georges Martin",
    "structurizr/structurizr.github.io",
    "530a96451b93f8fb96337b58aaaa1ec8c0ad4589",
    "Copyright (c) 2022 just-the-docs",
    "MIT License",
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,',
    "## Which local files adapt which source files",
    "`SKILL.md` adapts no text (ideas only",
    "carries no attribution line",
)

_SOURCE_MAP_PHRASES: tuple[str, ...] = (
    "adapted text exists in exactly the three files `NOTICE.md` lists",
    "## `SKILL.md` — ideas only",
    "No passage in `SKILL.md` copies text; it has no attribution line in `NOTICE.md`.",
    "## Dropped upstream content (no local passage)",
    "Elixir/OTP/Phoenix/Ash/Oban/umbrella",
    'Docker-CLI "Validation" section',
    "`!include`, `!docs` and `!adrs` directive sections",
    "Workspace Extension",
    "Multiple Workspaces",
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
    """The six markdown files at the singular ``skill/`` path (REQ-007)."""

    def test_skill_dir_is_under_the_singular_skill_directory(self):
        self.assertTrue((_REPO_ROOT / ".opencode" / "skill").is_dir())
        self.assertFalse((_REPO_ROOT / ".opencode" / "skills").exists(), "plural skills/ dir must not exist")
        self.assertTrue(_SKILL_DIR.is_dir())

    def test_all_expected_files_exist(self):
        for relative in sorted(_EXPECTED_FILES):
            self.assertTrue((_SKILL_DIR / relative).is_file(), relative)

    def test_skill_dir_holds_exactly_the_six_markdown_files(self):
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
        self.assertIn("authoring or fixing structurizr dsl workspace text", self._description_lower())

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


class TestAuthoringRules(unittest.TestCase):
    """REQ-002: the seven authoring rules with the pinned-CLI error strings."""

    def test_authoring_rule_phrases_present(self):
        body = _skill_body()

        for phrase in _AUTHORING_RULES:
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
    """REQ-006/ACC-003 in full: DSL text only / single file, the refused
    ``!include``/``!docs``/``!adrs`` with the refusal reading and the
    single-file fallback, no image rendering, no URL theme."""

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


class TestSyntaxReference(unittest.TestCase):
    """The adapted syntax reference (upstream `structurizr-dsl` + the
    Structurizr docs basics/identifiers pages)."""

    def test_syntax_phrases_present(self):
        text = _norm(_read_text(_SYNTAX_PATH))

        for phrase in _SYNTAX_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_no_included_directives_in_element_blocks(self):
        text = _read_text(_SYNTAX_PATH)

        # the locked removal: no `!docs`/`!adrs` inside the element blocks
        for section in text.split("## Model elements")[1].split("## Relationships")[0]:
            self.assertNotIn("!docs", section)
            self.assertNotIn("!adrs", section)


class TestViewsAndStylesReference(unittest.TestCase):
    """The adapted views/styles/themes/terminology/configuration reference,
    minus the image view and the URL theme."""

    def test_views_phrases_present(self):
        text = _norm(_read_text(_VIEWS_PATH))

        for phrase in _VIEWS_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_no_image_view_section(self):
        text = _read_text(_VIEWS_PATH)

        self.assertNotIn("### Image View", text)

    def test_no_theme_url(self):
        text = _read_text(_VIEWS_PATH)

        self.assertNotIn('"https://', text)


class TestGotchasReference(unittest.TestCase):
    """The adapted error table (the pinned CLI's own strings) and the rule
    behind each error, plus the MCP notes."""

    def test_gotchas_phrases_present(self):
        text = _norm(_read_text(_GOTCHAS_PATH))

        for phrase in _GOTCHAS_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_no_elixir_or_docker_cli_content(self):
        text = _norm(_read_text(_GOTCHAS_PATH)).lower()

        for word in ("elixir", "phoenix", "oban", "podman", "wslc", "docker run"):
            self.assertNotIn(word, text, f"locked-removed content in gotchas.md: {word}")


class TestNoticeAndSourceMap(unittest.TestCase):
    """ACC-010: the two MIT notices with their three-file mapping, the
    source map with its ideas-only marks, and the three files' mutual
    consistency (the adapted text exists exactly in the files NOTICE.md
    lists)."""

    def test_notice_carries_both_sources_commit_copyright_and_mit_text(self):
        notice = _read_text(_NOTICE_PATH)

        for phrase in _NOTICE_PHRASES:
            self.assertIn(phrase, notice, phrase)
        # the two section headings + the first line of each license block
        self.assertEqual(notice.count("MIT License"), 4)
        self.assertEqual(notice.count("Copyright (c) 2026 Georges Martin"), 2)
        self.assertEqual(notice.count("Copyright (c) 2022 just-the-docs"), 2)

    def test_notice_maps_exactly_the_three_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)

        self.assertIn("| `references/syntax.md` |", notice)
        self.assertIn("| `references/views-and-styles.md` |", notice)
        self.assertIn("| `references/gotchas.md` |", notice)
        table_rows = [
            line for line in notice.splitlines() if line.startswith("| `references/") and line.rstrip().endswith("|")
        ]

        self.assertEqual(len(table_rows), 3)

    def test_source_map_phrases_present(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        for phrase in _SOURCE_MAP_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_source_map_marks_skill_md_ideas_only(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        self.assertIn("## `SKILL.md` — ideas only", text)
        self.assertGreaterEqual(text.count("Ideas only"), 1)

    def test_notice_and_source_map_agree_on_the_three_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)
        source_map = _norm(_read_text(_SOURCE_MAP_PATH))

        for relative in ("references/syntax.md", "references/views-and-styles.md", "references/gotchas.md"):
            self.assertIn(relative, notice)
            self.assertIn(f"## `{relative}`", source_map)


if __name__ == "__main__":
    unittest.main()
