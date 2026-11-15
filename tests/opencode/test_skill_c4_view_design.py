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

"""feat-250-c4-structurizr-skills Phase 140, Task 140.150 (ACC-011): pin the c4-view-design skill.

The feature's fourth skill, ``.opencode/skill/c4-view-design/`` — designing
which C4 views to create and keeping each view readable (REQ-004: about
20 elements per view, explicit view keys, the C4-PlantUML export gotchas
of the spike as a short reference note) — as measured to its stop rule in
Phase 140. These tests pin, read-only from the committed files (no
network, no Docker, no model): the file location (the project skill path
``.opencode/skill/`` — singular ``skill/`` dir — with exactly the six
markdown files: ``SKILL.md``, ``NOTICE.md``, ``source-map.md`` and the
three ``references/`` files, REQ-007's markdown-only rule); the
frontmatter (exactly the ``name``/``description`` keys, ``name`` equal to
the folder, a non-empty third-person ``description``); the description's
trigger surface (the positive trigger phrases, the single-task naming, the
negative clause, and the other skills' vocabulary asserted ABSENT from the
description, case-insensitive substring — the no-trigger trap of this
phase's case set); the REQ-004 content pins (the five rules in ``SKILL.md``,
the view-selection mapping in ``references/view-selection.md`` — the
adapted upstream Diagram Types + Diagram Selection Guide —, the about-20-
element bound and the explicit-keys rule in ``references/view-size-and-keys.
md``, the C4-PlantUML gotchas note with both traps in ``references/
c4-plantuml-gotchas.md``); the view-DSL-syntax ABSENT pin (the block
grammar / autoLayout / styles recipes are NOT re-adapted — the skill names
the `structurizr-dsl-authoring` skill for syntax instead, the locked scope
cut); the locked removals (the Elixir/OTP content ABSENT, the Docker-CLI
content ABSENT, no ``!include``/``!docs``/``!adrs`` advice, no image-view
content); the MCP-limit wording the skill depends on (no image rendering —
view design is verified through the model/export JSON, never a rendered
picture; single-file DSL text only); the REQ-011 no-MCP wording (view
design is still possible; the MCP-based checking is not; a result is never
described as validated/export-checked when the tools are absent); and the
``NOTICE.md`` + ``source-map.md`` pair with its one-file adapted-text
invariant and the ideas-only/observed marks (ACC-010).

Phrase pins are matched against whitespace-normalized text (every run of
whitespace collapsed to one space) so they survive the committed files'
hard line-wrapping; the description pins are matched case-insensitively
on the raw description, since opencode surfaces it verbatim to agents.

Measured variants (recorded in the Phase 140 Updates entry): v1 (iter1)
= `eae05f1d6ad768d544d6fc1d553ee1bf43fd4419819ea71777cb77ed73803e24`
(positive trigger 0/5 on `design-views` -- the description's "for a
system model" framing never matched the CREATE prompt), v2 (iter2) = v1
plus the create-flow hook in the description ("for a C4 model being built
in Structurizr DSL", the fifth trigger phrase "set up the views for this
model") and in the SKILL.md intro ("the views are part of the deliverable:
design them in the same pass") -- measured positive trigger 5/5, negative
0/5; v3 (iter3, the committed variant) = v2 plus the efficiency fix in
"Checking the result" and the single-pass bullet ("Write the whole
workspace in one pass", the validate-only scope note) -- iteration 2's
furthest trials reached 11/12 gates but were killed at the 1200 s timeout
by the degraded shared-server window; all content fixes are marked
ideas-only in the source map.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "c4-view-design"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_NOTICE_PATH = _SKILL_DIR / "NOTICE.md"
_SOURCE_MAP_PATH = _SKILL_DIR / "source-map.md"
_SELECTION_PATH = _SKILL_DIR / "references" / "view-selection.md"
_SIZE_PATH = _SKILL_DIR / "references" / "view-size-and-keys.md"
_GOTCHAS_PATH = _SKILL_DIR / "references" / "c4-plantuml-gotchas.md"
_SKILL_NAME = "c4-view-design"
_EXPECTED_FILES: frozenset[str] = frozenset(
    {
        "SKILL.md",
        "NOTICE.md",
        "source-map.md",
        "references/view-selection.md",
        "references/view-size-and-keys.md",
        "references/c4-plantuml-gotchas.md",
    }
)
_TRIGGER_PHRASES: tuple[str, ...] = (
    "which views to create",
    "design a container view",
    "keep a view readable",
    "view too crowded",
    "set up the views for this model",
)
_NEGATIVE_CLAUSE = "It explains the view design only and does not itself produce any files."
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
    "workspace.dsl",
    "syntax",
    "parse",
    "validate",
    "inspect",
    "triage",
    "review",
    "error",
)

_RULE_PHRASES: tuple[str, ...] = (
    # the create-flow hook (iteration-1 measured: the v1 description never
    # loaded on the CREATE prompt -- the views must be designed in the same
    # pass as the model is built)
    "the views are part of the deliverable: design them in the same pass",
    # the single-pass write bullet (iteration-3 efficiency fix)
    "Write the model and all of its views in one pass",
    "## The rules",
    "1. **Pick views by audience and question.**",
    "2. **Keep every view to about 20 elements.**",
    "3. **Give every view an explicit key.**",
    "4. **A readable view labels everything it shows.**",
    "5. **Use groups and filtered views to clarify, not to add.**",
    # the delegation (the locked scope cut: the view-DSL syntax lives in
    # the dsl-authoring skill, the loop lives in the validate-loop skill)
    "the `structurizr-dsl-authoring` skill's task",
    "the `structurizr-validate-loop` skill's task",
    "## Designing the views of a large model",
)

_MCP_CHECK_PHRASES: tuple[str, ...] = (
    "## Checking the result",
    # the iteration-3 efficiency fix (iteration-2 measured: the furthest
    # trials reached 11/12 gates but were killed at the 1200 s timeout
    # after 22 steps incl. 9 parse + 4 inspect round trips the task does
    # not need -- 937k input tokens re-prefilled on the slow shared server)
    "Write the whole workspace in one pass",
    "then check it with the structurizr MCP",
    "`validate` tool",
    "until it answers `OK`",
    "do not finish while `validate` is still reporting errors",
    # the light pointer must NOT prescribe the full loop (that is the
    # validate-loop skill's single task)
    "the full parse/validate/inspect loop with finding triage is the `structurizr-validate-loop` skill's task, and it is not needed here",
    "call whichever prefixed variant your host exposes",
)

_LIMIT_PHRASES: tuple[str, ...] = (
    "## The MCP limits",
    "- **No image rendering.**",
    "cannot produce image files (PNG/SVG)",
    "emit diagram source only",
    # REQ-006 as this skill depends on it: view design is verified through
    # the model/export JSON, never a rendered picture
    "View design is verified through the model and the export JSON, never through a rendered picture",
    "- **DSL text only, single file.**",
    "there is no multi-file workspace",
)

_NO_MCP_PHRASES: tuple[str, ...] = (
    "## When the MCP is absent",
    "View design is still possible without the MCP",
    "validation is not possible",
    "never describe a result as validated",
)

_SELECTION_PHRASES: tuple[str, ...] = (
    "## Diagram Types",
    '### Core Diagrams (the "4 Cs")',
    "| System Context | One software system | System + users + external systems | Everyone | Yes, always |",
    "| Container | One software system | Containers inside the system | Technical staff | Yes, always |",
    "| Component | One container | Components inside the container | Developers | Only if valuable |",
    "### Supporting Diagrams",
    "| System Landscape | Enterprise/org | All systems and their connections | Large organizations, enterprise views |",
    "| Dynamic | Feature/use case | Runtime interactions with numbered sequence | Complex interaction flows, specific scenarios |",
    "| Deployment | One+ systems in one environment | Infrastructure, nodes, deployed instances | Infrastructure documentation, ops audience |",
    "## Diagram Selection Guide",
    '**"Who is the audience?"**',
    '**"What question does the diagram answer?"**',
    '- "What does the system do and who uses it?" → System Context',
    '- "What are the main technical building blocks?" → Container',
    '- "How does feature Y work at runtime?" → Dynamic',
    '- "Where does it run?" → Deployment',
    "## The view kinds of the Structurizr DSL",
    "- **System Landscape**",
    "- **System Context**",
    "- **Container**",
    "- **Component**",
    "- **Dynamic**",
    "- **Deployment**",
    "- **Filtered**",
    "- **Custom**",
    "## Keeping a view readable",
    "**Groups**",
    "**Filtered views**",
)

_SIZE_PHRASES: tuple[str, ...] = (
    "## The size rule: about 20 elements per view",
    "about 20 elements per view",
    "29,664",
    "150-element",
    "explicit include list",
    "## Explicit view keys",
    "a-zA-Z0-9_-",
    "Container-001",
    "views.view.key",
    "automatically generated view key",
)

_GOTCHAS_PHRASES: tuple[str, ...] = (
    "# C4-PlantUML export gotchas",
    "**Custom elements are silently dropped.**",
    "**`include *`-pulled elements can be dropped too.**",
    "**Tags and styles are off by default.**",
    '`$tags=""`',
    '`c4plantuml.tags "true"`',
    '`c4plantuml.elementProperties "true"`',
    "**The default `Element` tag needs an explicit background colour.**",
    "white text on white",
)

# The view-DSL syntax mechanics (the locked scope cut): NOT re-adapted here
# — they live in `structurizr-dsl-authoring`'s `references/views-and-styles.
# md`. Absent from every content file of this skill.
_SYNTAX_ABSENT_WORDS: tuple[str, ...] = (
    "autoLayout",
    "include element.tag",
    "element.type==Container",
    "shape Person",
    "background #",
    "routing Orthogonal",
    "include *?",
)

# The locked removals: absent from every content file of this skill.
_REMOVAL_WORDS: tuple[str, ...] = (
    "elixir",
    "otp",
    "phoenix",
    "oban",
    "erlang",
    "beam",
    "docker",
    "podman",
    "wslc",
    "!include",
    "!docs",
    "!adrs",
    "!theme",
    "kroki",
    "image view",
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
    "`SKILL.md` adapts no text",
)

_SOURCE_MAP_PHRASES: tuple[str, ...] = (
    "adapted text exists in exactly the one file `NOTICE.md` lists",
    "## `SKILL.md` — ideas only",
    "No passage in `SKILL.md` copies text; it has no attribution line in `NOTICE.md`.",
    "## `references/view-selection.md`",
    "## `references/view-size-and-keys.md`",
    "## `references/c4-plantuml-gotchas.md`",
    "## Dropped upstream content (no local passage)",
    "Erlang/Elixir/OTP Modeling Guide",
    'Docker-CLI "Validation" section',
    "Related Skills",
    "Diagram Types",
    "Diagram Selection Guide",
    "e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b",
    "530a96451b93f8fb96337b58aaaa1ec8c0ad4589",
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


#: The content files the absence pins run over (NOTICE.md and source-map.md
#: legitimately name the removed content in their dropped-content lists).
_CONTENT_FILES: tuple[Path, ...] = (_SKILL_PATH, _SELECTION_PATH, _SIZE_PATH, _GOTCHAS_PATH)


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
        self.assertIn("designing which c4 views to create", self._description_lower())

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


class TestViewRulesSection(unittest.TestCase):
    """REQ-004: the five view-design rules in SKILL.md, incl. the delegation
    to the other skills (the locked scope cut)."""

    def test_rule_phrases_present(self):
        body = _skill_body()

        for phrase in _RULE_PHRASES:
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
    """REQ-006/ACC-003: the limits this skill depends on — no image
    rendering (view design is verified through the model/export JSON, never
    a rendered picture) and single-file DSL text only."""

    def test_limit_phrases_present(self):
        body = _skill_body()

        for phrase in _LIMIT_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestNoMcpBehavior(unittest.TestCase):
    """REQ-011: without the MCP, view design is still possible (model
    structure), the MCP-based checking is not, and no result may be
    described as validated or export-checked."""

    def test_no_mcp_phrases_present(self):
        body = _skill_body()

        for phrase in _NO_MCP_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestViewSelectionReference(unittest.TestCase):
    """The adapted view-selection reference: the upstream Diagram Types +
    Diagram Selection Guide (near-verbatim, NOTICE-attributed) plus the
    docs' view-kind content (restated, ideas only)."""

    def test_selection_phrases_present(self):
        text = _norm(_read_text(_SELECTION_PATH))

        for phrase in _SELECTION_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_names_the_dsl_authoring_skill_for_syntax(self):
        text = _read_text(_SELECTION_PATH)

        self.assertIn("structurizr-dsl-authoring", text)
        self.assertIn("views-and-styles.md", text)


class TestViewSizeAndKeysReference(unittest.TestCase):
    """The size rule and the explicit-keys rule (spike Finding 8 + the
    pinned-CLI observed facts)."""

    def test_size_phrases_present(self):
        text = _norm(_read_text(_SIZE_PATH))

        for phrase in _SIZE_PHRASES:
            self.assertIn(phrase, text, phrase)


class TestC4PlantumlGotchasReference(unittest.TestCase):
    """The short C4-PlantUML export gotchas note (spike Finding 4) with
    both traps (the silent `include *`/custom-element drops; the default
    `Element` tag white-on-white)."""

    def test_gotchas_phrases_present(self):
        text = _norm(_read_text(_GOTCHAS_PATH))

        for phrase in _GOTCHAS_PHRASES:
            self.assertIn(phrase, text, phrase)


class TestViewDslSyntaxAbsent(unittest.TestCase):
    """The locked scope cut: the view-DSL syntax mechanics are NOT
    re-adapted — the block grammar, autoLayout parameters and styles
    recipes live in `structurizr-dsl-authoring`'s `references/
    views-and-styles.md`; this skill names that skill for syntax."""

    def test_no_view_dsl_syntax_in_the_content_files(self):
        for path in _CONTENT_FILES:
            text = _norm(_read_text(path)).lower()
            for word in _SYNTAX_ABSENT_WORDS:
                self.assertNotIn(word.lower(), text, f"view-DSL syntax re-adapted in {path.name}: {word}")


class TestScopeCuts(unittest.TestCase):
    """The locked removals: no Elixir/OTP, no Docker-CLI, no
    ``!include``/``!docs``/``!adrs`` advice, no image-view/URL-theme
    content."""

    def test_no_removed_content_in_the_content_files(self):
        for path in _CONTENT_FILES:
            text = _norm(_read_text(path)).lower()
            for word in _REMOVAL_WORDS:
                self.assertNotIn(word.lower(), text, f"locked-removed content in {path.name}: {word}")


class TestNoticeAndSourceMap(unittest.TestCase):
    """ACC-010: the MIT notice with both sources and its one-file mapping,
    the source map with its ideas-only/observed marks and the dropped-
    content list, and the two files' mutual consistency (the adapted text
    exists exactly in the file NOTICE.md lists)."""

    def test_notice_carries_both_sources_and_the_mit_text(self):
        notice = _read_text(_NOTICE_PATH)

        for phrase in _NOTICE_PHRASES:
            self.assertIn(phrase, notice, phrase)
        # the two license headings + the two license blocks + the two
        # copyright lines (each source twice: its bullet, its block)
        self.assertEqual(notice.count("MIT License"), 4)
        self.assertEqual(notice.count("Copyright (c) 2026 Georges Martin"), 2)
        self.assertEqual(notice.count("Copyright (c) 2022 just-the-docs"), 2)

    def test_notice_maps_exactly_the_one_adapted_file(self):
        notice = _read_text(_NOTICE_PATH)

        self.assertIn("| `references/view-selection.md` |", notice)
        table_rows = [
            line for line in notice.splitlines() if line.startswith("| `references/") and line.rstrip().endswith("|")
        ]

        self.assertEqual(len(table_rows), 1)

    def test_source_map_phrases_present(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        for phrase in _SOURCE_MAP_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_source_map_marks_ideas_only_and_observed(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        self.assertIn("## `SKILL.md` — ideas only", text)
        self.assertGreaterEqual(text.count("Ideas only"), 3)
        self.assertGreaterEqual(text.count("observed"), 3)

    def test_notice_and_source_map_agree_on_the_adapted_file(self):
        notice = _read_text(_NOTICE_PATH)
        source_map = _norm(_read_text(_SOURCE_MAP_PATH))

        for relative in ("references/view-selection.md",):
            self.assertIn(relative, notice)
            self.assertIn(f"## `{relative}`", source_map)
        # the ideas-only files carry no adapted text, and the source map
        # names each of them
        for relative in ("references/view-size-and-keys.md", "references/c4-plantuml-gotchas.md"):
            self.assertIn(f"## `{relative}`", source_map)


if __name__ == "__main__":
    unittest.main()
