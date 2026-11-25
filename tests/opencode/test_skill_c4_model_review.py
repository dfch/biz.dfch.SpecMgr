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

"""feat-250-c4-structurizr-skills Phase 150, Task 150.150 (ACC-004/ACC-010/ACC-011): pin the c4-model-review skill.

The feature's fifth skill, ``.opencode/skill/c4-model-review/`` — reviewing
an existing C4 model built in Structurizr DSL for quality: walking the
model's elements, relationships, and views against a read-only C4
checklist and reporting the findings (REQ-005: the report deliverable;
the REVIEW case shape — pre-seeded, CLI-valid workspace, the agent
reviews, never creates or fixes) — as measured to its stop rule in
Phase 150. These tests pin, read-only from the committed files (no
network, no Docker, no model): the file location (the project skill
path ``.opencode/skill/`` — singular ``skill/`` dir — with exactly the
six markdown files: ``SKILL.md``, ``NOTICE.md``, ``source-map.md`` and
the three ``references/*-checklist.md`` files, REQ-007's markdown-only
rule); the frontmatter (exactly the ``name``/``description`` keys,
``name`` equal to the folder, a non-empty third-person
``description``); the description's trigger surface (the positive
trigger phrases, the single-task naming, the read-only negative clause,
and the other skills' vocabulary asserted ABSENT from the description,
case-insensitive substring — the no-trigger trap of this phase's case
set); the READ-ONLY wording (ACC-004/ACC-011: the skill states it
reports findings and never edits the model — no file is changed,
created, deleted, or renamed — the review is delivered in the final
message, not in a file; writing/fixing DSL is routed to the
``structurizr-dsl-authoring`` skill and the parse/validate/inspect loop
to the ``structurizr-validate-loop`` skill); the workflow (read the
workspace once; ``parse``/``validate``/``inspect`` each once, a
broken workspace is the first finding reported — never fixed; walk the
three checklists; report); the report format (one line of context, one
bullet per finding, Error/Warning/Suggestion, a closing line, the
name-everything / no-padding / no-own-opinion rules, and the
iteration-2 no-view-element-listing rule); the REQ-006 MCP-limit
wording (no image rendering — the review is over model structure,
never a rendered picture; DSL text only, single file — the MCP refuses
``!include``/``!docs``/``!adrs``, so the documentation/decisions
findings are expected under the MCP limits, not model mistakes to fix
with them); the REQ-011 no-MCP wording (the checklists can still be
walked over the DSL text — model structure, not tool output; the
MCP-based checking is not possible; a result is never described as
validated/parse-checked/export-checked when the tools are absent); the
three checklist files' locked content anchors (element — incl. the
library-not-a-container Error, the do-not-flag-a-tagged-element rule,
the description-contradiction-only completeness rule and the KEPT
"Docker Confusion" anti-pattern note; relationship — incl. the
near-verbatim vague-label table; view — incl. the explicit-key and
about-20-element criteria with the no-element-listing wording); the
locked removals (all Docker-CLI machinery, the Elixir/OTP content, the
dropped upstream phases/sections, no ``!docs``/``!adrs``/``!include``
advice); and the ``NOTICE.md`` ↔ ``source-map.md`` invariant (exactly
one MIT source — ``jrjsmrtn/c4-skills`` @ ``e86d8a91…`` — and exactly
three adapted files, matching ``source-map.md``'s passage map; ideas-
only marks where text was rewritten).

Phrase pins are matched against whitespace-normalized text (every run
of whitespace collapsed to one space) so they survive the committed
files' hard line-wrapping; the description pins are matched
case-insensitively on the raw description, since opencode surfaces it
verbatim to agents.

Measured variants (recorded in the Phase 150 Updates entry): v1 =
`d615896ad24abe7be1601f6411ec45e26f58bc49fa453107515d1cdf206103ed`
(measured on the intermediate seed — its near-misses, all six
detection gates passing with 4 of 5 failing ONLY `no_false_findings`,
drove seed revision 3 + the v2 fixes), v2 (the committed, frozen
variant) = v1 plus the two checklist fixes (the
do-not-flag-a-tagged-element rule, the description-contradiction-only
completeness rule) plus the no-view-element-listing report rule
(source-map marked ideas-only, iteration-2) =
`89e0bc4bb4867b8885a3e393eaf1c76d3811dd39bd17702a533788f0b7620fc0`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL_DIR = _REPO_ROOT / ".opencode" / "skill" / "c4-model-review"
_SKILL_PATH = _SKILL_DIR / "SKILL.md"
_NOTICE_PATH = _SKILL_DIR / "NOTICE.md"
_SOURCE_MAP_PATH = _SKILL_DIR / "source-map.md"
_ELEMENT_PATH = _SKILL_DIR / "references" / "element-checklist.md"
_RELATIONSHIP_PATH = _SKILL_DIR / "references" / "relationship-checklist.md"
_VIEW_PATH = _SKILL_DIR / "references" / "view-checklist.md"
_SKILL_NAME = "c4-model-review"
_UPSTREAM_SHA = "e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b"
_EXPECTED_FILES: frozenset[str] = frozenset(
    {
        "SKILL.md",
        "NOTICE.md",
        "source-map.md",
        "references/element-checklist.md",
        "references/relationship-checklist.md",
        "references/view-checklist.md",
    }
)
_TRIGGER_PHRASES: tuple[str, ...] = (
    "review this C4 model",
    "check the model for problems",
    "audit the architecture model",
    "find quality issues in the model",
    "is this model ready to publish",
)
_NEGATIVE_CLAUSE = "It reports the review findings only; it never edits the model or writes any files."
# Vocabulary of the other four feature skills (and image rendering
# generally): absent from the description, case-insensitively, keeps
# the no-trigger trap intact (the no-trigger case measures exactly
# this — an over-broad description loads the skill on a render-to-
# image request and fails `no_mounted_skill_loaded`).
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
    "error",
    "create a c4 model",
    "c4 levels",
    "decide what is a container",
    "model an external system",
    "label these relationships",
    "design",
    "view too crowded",
    "set up the views for this model",
)

_READ_ONLY_PHRASES: tuple[str, ...] = (
    "This skill is read-only: it reports findings and never edits the model",
    "no file is changed, created, deleted, or renamed",
    "the review is delivered in your final message, not in a file",
    "here you only look, judge, and report",
)

_ROUTING_PHRASES: tuple[str, ...] = (
    "How to write or fix DSL text is the `structurizr-dsl-authoring` skill's task",
    "the parse/validate/inspect loop with finding triage is the `structurizr-validate-loop` skill's task",
)

_WORKFLOW_PHRASES: tuple[str, ...] = (
    "## The workflow",
    "1. **Read the workspace DSL** with your host's file tool",
    "Read it once, completely.",
    "2. **Check the structure with the structurizr MCP**",
    "`parse` (does the text parse at all), `validate` (does the workspace validate), and `inspect`",
    "the Checkstyle-style findings: disconnected elements, elements not on any view, generated view keys",
    "If the workspace does not parse or validate, that is the first finding — report it with the tool's exact message "
    "and stop the checklist; do not fix it.",
    "Call each tool once; do not re-run a tool over text that has not changed.",
    "call whichever prefixed variant your host exposes",
    "3. **Walk the checklists** over the DSL text",
    "references/relationship-checklist.md",
    "references/view-checklist.md",
    "(people, systems, containers, components, completeness — incl. disconnected elements)",
    "Judge every element and relationship in the model, not just the ones the tools flag",
    "a library modeled as a container, a third-party element without the `External` tag, a vague relationship "
    "label, an over-crowded view",
    "4. **Report the findings** in your final message, in the format below.",
)

_REPORT_PHRASES: tuple[str, ...] = (
    "## The report format",
    "one line of context: which file was reviewed and that nothing was edited",
    "**one bullet per finding**",
    "Categorise each finding as **Error** (wrong abstraction or notation",
    "**Warning** (vague label, missing description, potential confusion)",
    "**Suggestion** (organisation, optional views, clarity)",
    "a closing line on what you checked and found fine, so the reader knows the review was complete",
    "Name the element, relationship, or view in every finding",
    "a finding that does not say where the problem is is not a finding",
)

_REPORT_DISCIPLINE_PHRASES: tuple[str, ...] = (
    "Do not pad the list with generic advice: only report what is actually wrong in this model.",
    "judge this model, not a different one",
    "a defensible design choice (what to model, how to split elements, which technology to name) is not a finding",
    # the iteration-2 fix (iteration-1 skill trials reported the crowded
    # view correctly but enumerated the pulled-in elements in the finding
    # line, naming clean elements)
    "When a finding is about a view's size, name the view and give the element count — do not list the elements "
    "the view contains.",
)

_LIMIT_PHRASES: tuple[str, ...] = (
    "## The MCP limits",
    "- **No image rendering.**",
    "The MCP cannot produce image files (PNG/SVG); its export tools emit diagram source only.",
    "The review is over the model structure — the DSL text and the MCP facts — never over a rendered picture, "
    "and it must not claim to have seen one.",
    "- **DSL text only, single file.**",
    "The tools work on the workspace's DSL text given as one input",
    "the MCP refuses `!include`, `!docs`, and `!adrs`",
    "a multi-file workspace cannot be checked",
    "the documentation/decisions findings that `inspect` reports for a single-file workspace are expected under "
    "the MCP limits",
    "report them as such, not as model mistakes the author should fix with `!docs`/`!adrs`",
)

_NO_MCP_PHRASES: tuple[str, ...] = (
    "## When the MCP is absent",
    "The review can still read the DSL text and walk the checklists — that part is model structure, not tool output.",
    "What is not possible without the MCP is the MCP-based checking: parsing, validation, and `inspect` findings.",
    "Validation is not possible",
    "you must never describe a review as validated, parse-checked, or export-checked when the tools are absent",
    "say plainly that the review is over the DSL text only",
)

_ELEMENT_PHRASES: tuple[str, ...] = (
    "# Element checklist",
    "Walk every element in the model against these criteria.",
    "Judge the DSL text itself — the names, descriptions, tags, and placement of each element — not a rendered "
    "picture.",
    "## People / actors",
    'Every person has a clear, specific name (not "User" unless truly generic).',
    "Every person has a description stating their role or goal.",
    "No duplicate people representing the same role.",
    "External vs internal actors are distinguished (via tags or naming).",
    "## Software systems",
    "The system being modeled has a name and a description.",
    "External systems are clearly identified — tagged `External` or similar.",
    "A third-party thing operated by a different organization must be a top-level element carrying that tag",
    "without the tag is a **Warning**: readers cannot tell owned from external.",
    # the iteration-2 fix (the proof data showed baselines flagging
    # correctly tagged elements for "not being a softwareSystem")
    "A top-level `element` (or `softwareSystem`) with the `External` tag is the correct representation of a "
    "third party — do not flag such an element for not being a `softwareSystem`.",
    "Each external system has a description explaining what it provides.",
    "No system is modeled that should actually be a container (e.g. a database you own).",
    "System names are unique and unambiguous.",
    "## Containers",
    "Every container represents a **runtime boundary** (a separately running process or a data store).",
    "No libraries, modules, or packages modeled as containers.",
    "A shared rules library, a JAR, a module, or a package is code-level: it runs inside another element's process "
    "and is not an element of its own.",
    "Finding one modeled as a container is an **Error** — name the container and say what level it actually "
    "belongs at.",
    "Every container has a technology specified.",
    'not a bare list of technology names — "Technology Soup" is a description that is just technology names, '
    "where the description should state the responsibility",
    'Database containers use the "Database" tag for the cylinder shape.',
    "No containers that should be external systems (services you don't own or deploy).",
    "## Components (if present)",
    "Components represent architecturally significant groupings, not just folder structure",
    'the "Code Structure Mirror" — components that exactly match package or module structure model code '
    "organization, not architecture",
    "Every component has a technology specified.",
    "Components are within a single container (not spanning containers).",
    "a stale component diagram that no longer matches the code is worse than none",
    "## Completeness",
    # the iteration-2 fix (a read-only review has no external ground
    # truth for "known paths")
    "A missing relationship is a finding only when the model's own descriptions claim it (a description that "
    "names a counterpart the model has no edge to).",
    "Do not invent communication paths the model does not claim.",
    "No orphaned elements — elements with no relationships.",
    "The MCP `inspect` tool reports these as disconnected elements and as elements not included on any views",
    "an orphan is a **Warning** (it is either dead weight or a relationship the model forgot) — name the element "
    "and say what is missing.",
    'A system context view and a container view exist at minimum (the "Missing Middle" — a system context view '
    "with no container view jumps straight to components).",
    "## Anti-patterns worth flagging",
    # the KEPT anti-pattern note (the locked removal is the Docker-CLI
    # machinery, not this model-level definition)
    '**The "Docker Confusion"** — Docker containers modeled as C4 containers, or C4 containers modeled as Docker '
    "containers.",
    "C4 containers are runtime boundaries; Docker is a deployment mechanism (it belongs in the deployment view).",
    '**The "Technology Soup"** — element descriptions that are just technology names, where the description should '
    "state the responsibility.",
)

_RELATIONSHIP_PHRASES: tuple[str, ...] = (
    "# Relationship checklist",
    "Walk every relationship in the model: its label, its technology, and its direction.",
    "## Labels",
    'Every relationship has a label describing **intent** — what is communicated in that direction, not just "uses".',
    "Labels match the arrow direction (the source does X **to** the destination).",
    "No vague labels.",
    'the classic set is "Uses", "Connects to", "Interacts with", "Communicates with" — each is a **Warning**; '
    "name the two elements involved and ask what the label should actually say.",
    "Suggest specific alternatives for vague labels:",
    # the near-verbatim upstream vague-label table
    '| "Uses" | What does it use it for? | "queries order history from" |',
    '| "Connects to" | What data flows? | "sends email notifications via" |',
    '| "Interacts with" | What\'s the interaction? | "submits search queries to" |',
    '| "Communicates with" | What\'s communicated? | "publishes order events to" |',
    "## Technology",
    'Inter-container relationships specify a protocol or technology (e.g. "JSON/HTTPS", "SQL/TCP", "gRPC", "AMQP").',
    'Person-to-container relationships specify the interface technology (e.g. "HTTPS", "WebSocket").',
    "Intra-container relationships (component to component) may omit the technology.",
    "## Direction",
    "Arrows point in the direction of dependency or data flow.",
    "No bidirectional relationships (split them into two if needed).",
    "Implied relationships make sense (e.g. person to container implies person to system).",
)

_VIEW_PHRASES: tuple[str, ...] = (
    "# View checklist",
    "The review judges the views as recorded in the DSL — which views exist, how they are keyed, and what they "
    "carry — never a rendered picture",
    "The design rules for choosing and splitting views are the `c4-view-design` skill's task",
    "## Existence and scope",
    "A system context view exists (required for all projects), showing the system at the centre with its users "
    "and external systems, without internal containers, components, or technology detail.",
    "A container view exists (required for all projects), showing the containers within the system boundary",
    "A component view (if present) is scoped to a single container and only created where the internal structure "
    "matters.",
    "A dynamic view (if present) is scoped to one feature or use case with numbered interactions",
    "A deployment view (if present) is scoped to one environment and shows deployment nodes, not just containers.",
    "## Keys and size",
    "Every view has an explicit key (characters `a-zA-Z0-9_-`, no spaces).",
    "A view whose DSL omits the key is assigned an auto-generated key (`Container-001` style) that is not "
    "guaranteed to be stable over time",
    "the MCP `inspect` tool reports it as a `views.view.key` finding",
    "An auto-generated key is a **Warning**: name the view and say the key should be explicit.",
    "about 20 elements per view is the practical bound (a far larger single view exports to an unusable diagram)",
    # the iteration-2 fix counterpart (SKILL.md's report-format rule)
    "name the view and state how many elements it carries (do not list the elements themselves)",
    "the split itself is the `c4-view-design` skill's job — you only report the problem",
    "A view that includes everything by wildcard (`include *`) over a large model is the usual cause of the size "
    "problem above.",
    "## Content",
    "no view mixes abstraction levels (e.g. a system context view showing containers)",
    "the element and relationship checklists above apply to what each view shows, not only to the model",
)

# The locked removals: absent from every content file of this skill
# (NOTICE.md and source-map.md legitimately name the removed content in
# their attribution/dropped-content lists).
_ELIXIR_ABSENT_WORDS: tuple[str, ...] = ("elixir", "otp", "erlang", "genserver", "supervision tree", "phoenix", "beam")
_DOCKER_CLI_ABSENT_WORDS: tuple[str, ...] = (
    "podman",
    "wslc",
    "$runtime",
    "docker run",
    "docker compose",
    "structurizr:2026.09.19",
    "mount the project root",
)
_DROPPED_SECTION_ABSENT_WORDS: tuple[str, ...] = (
    "phase 1",
    "phase 2",
    "phase 6",
    "phase 7",
    "phase 8",
    "when to use",
    "required inputs",
    "related skills",
    "shape person",
    "shape cylinder",
    "colour blindness",
    "!identifiers hierarchical",
)

_NOTICE_PHRASES: tuple[str, ...] = (
    "# License notice",
    "This skill adapts text from one MIT-licensed source:",
    "jrjsmrtn/c4-skills",
    "the `c4-review` skill",
    f"`{_UPSTREAM_SHA}` (pinned and verified)",
    "License: MIT",
    "Copyright (c) 2026 Georges Martin",
    "## Which local files adapt which source files",
    "`SKILL.md` adapts no text",
    "## MIT License (jrjsmrtn/c4-skills)",
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,',
)

_SOURCE_MAP_PHRASES: tuple[str, ...] = (
    "# Source map",
    "adapted text exists in exactly the three files `NOTICE.md` lists",
    f"`jrjsmrtn/c4-skills` @ `{_UPSTREAM_SHA}`",
    'MIT, "Copyright (c) 2026 Georges Martin"',
    "`skills/c4-review/SKILL.md` (single-file skill)",
    "## `SKILL.md` — ideas only",
    "No passage in `SKILL.md` copies text; it has no attribution line in `NOTICE.md`.",
    "## `references/element-checklist.md`",
    "## `references/relationship-checklist.md`",
    "## `references/view-checklist.md`",
    "## Dropped upstream content (no local passage)",
    "The upstream frontmatter's `metadata`/`license` fields",
    '"When to Use" and "Required Inputs"',
    "Docker-CLI form",
    "Phase 6: Style Review",
    "Phase 8: Structural Issues",
    "\"The 'Everything Uses Everything' Model\"",
    "\"The 'Missing Middle'\"",
    "\"The 'Stale Component Diagram'\"",
    "\"The 'Technology Soup'\"",
    "\"The 'Docker Confusion'\" (kept in the element anti-patterns)",
    "GenServer Container",
    "Supervision Tree Diagram",
    "Umbrella = Microservices",
    '"Validation" (the review-completion criteria',
    '"Related Skills"',
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
#: legitimately name the removed content in their attribution/dropped-
#: content lists).
_CONTENT_FILES: tuple[Path, ...] = (_SKILL_PATH, _ELEMENT_PATH, _RELATIONSHIP_PATH, _VIEW_PATH)


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
    the read-only negative clause, and the other skills' vocabulary ABSENT
    (the no-trigger trap of this phase's case set)."""

    def _description_lower(self) -> str:
        frontmatter, _ = _split_frontmatter(_read_text(_SKILL_PATH))

        result = _parse_frontmatter(frontmatter)
        return result["description"].lower()

    def test_description_names_the_task(self):
        self.assertIn("reviewing an existing c4 model built in structurizr dsl for quality", self._description_lower())
        self.assertIn(
            "walking the model's elements, relationships, and views against a read-only c4 checklist and "
            "reporting the findings",
            self._description_lower(),
        )

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


class TestReadOnlyWording(unittest.TestCase):
    """ACC-004/ACC-011: the skill states it reports findings and never
    edits the model or any file; writing/fixing DSL and the
    parse/validate/inspect loop are routed to the other skills."""

    def test_read_only_phrases_present(self):
        body = _skill_body()

        for phrase in _READ_ONLY_PHRASES:
            self.assertIn(phrase, body, phrase)

    def test_routing_to_the_other_skills(self):
        body = _skill_body()

        for phrase in _ROUTING_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestWorkflow(unittest.TestCase):
    """The four-step workflow: read once, check structure with the MCP
    (each tool once; a broken workspace is the first finding — reported,
    never fixed), walk the checklists, report."""

    def test_workflow_phrases_present(self):
        body = _skill_body()

        for phrase in _WORKFLOW_PHRASES:
            self.assertIn(phrase, body, phrase)

    def test_broken_workspace_is_reported_never_fixed(self):
        body = _skill_body()

        self.assertIn(
            "that is the first finding — report it with the tool's exact message and stop the checklist; "
            "do not fix it.",
            body,
        )
        self.assertNotIn("fix it", body.replace("do not fix it.", ""))


class TestReportFormat(unittest.TestCase):
    """REQ-005's report deliverable: the shape (context line, one bullet
    per finding, Error/Warning/Suggestion, closing line) and the
    discipline (name everything, no padding, no own opinion, the
    iteration-2 no-view-element-listing rule)."""

    def test_report_shape_phrases_present(self):
        body = _skill_body()

        for phrase in _REPORT_PHRASES:
            self.assertIn(phrase, body, phrase)

    def test_report_discipline_phrases_present(self):
        body = _skill_body()

        for phrase in _REPORT_DISCIPLINE_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestMcpLimitStatements(unittest.TestCase):
    """REQ-006/ACC-003: the limits this skill depends on — no image
    rendering (the review is over model structure, never a rendered
    picture) and single-file DSL text only (the MCP refuses
    ``!include``/``!docs``/``!adrs``; the documentation/decisions
    findings are expected under the MCP limits, never advice to add
    them)."""

    def test_limit_phrases_present(self):
        body = _skill_body()

        for phrase in _LIMIT_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestNoMcpBehavior(unittest.TestCase):
    """REQ-011: without the MCP, the checklists can still be walked over
    the DSL text (model structure, not tool output), the MCP-based
    checking is not possible, and no result may be described as
    validated/parse-checked/export-checked."""

    def test_no_mcp_phrases_present(self):
        body = _skill_body()

        for phrase in _NO_MCP_PHRASES:
            self.assertIn(phrase, body, phrase)


class TestElementChecklist(unittest.TestCase):
    """The element checklist anchors: the per-kind items, the
    library-not-a-container Error, the do-not-flag-a-tagged-element rule
    (iteration-2), the description-contradiction-only completeness rule
    (iteration-2), and the KEPT "Docker Confusion" anti-pattern note."""

    def test_element_phrases_present(self):
        text = _norm(_read_text(_ELEMENT_PATH))

        for phrase in _ELEMENT_PHRASES:
            self.assertIn(phrase, text, phrase)


class TestRelationshipChecklist(unittest.TestCase):
    """The relationship checklist anchors: the intent/direction/vague-
    label items and the near-verbatim upstream vague-label table."""

    def test_relationship_phrases_present(self):
        text = _norm(_read_text(_RELATIONSHIP_PATH))

        for phrase in _RELATIONSHIP_PHRASES:
            self.assertIn(phrase, text, phrase)


class TestViewChecklist(unittest.TestCase):
    """The view checklist anchors: the per-kind existence criteria, the
    explicit-key rule (the `Container-001`/`views.view.key` observed
    facts), the about-20-element bound with the no-element-listing
    wording (iteration-2), and the delegation of the split to
    `c4-view-design`."""

    def test_view_phrases_present(self):
        text = _norm(_read_text(_VIEW_PATH))

        for phrase in _VIEW_PHRASES:
            self.assertIn(phrase, text, phrase)


class TestLockedRemovals(unittest.TestCase):
    """The locked removals: no Elixir/OTP content, no Docker-CLI
    machinery (the KEPT "Docker Confusion" anti-pattern note is model-
    level and pinned present), no dropped upstream sections, no
    ``!docs``/``!adrs``/``!include`` advice."""

    def test_no_elixir_or_otp_in_the_content_files(self):
        for path in _CONTENT_FILES:
            text = _norm(_read_text(path)).lower()
            for word in _ELIXIR_ABSENT_WORDS:
                self.assertNotIn(word, text, f"locked-removed Elixir/OTP content in {path.name}: {word}")

    def test_no_docker_cli_machinery_in_the_content_files(self):
        for path in _CONTENT_FILES:
            text = _norm(_read_text(path)).lower()
            for word in _DOCKER_CLI_ABSENT_WORDS:
                self.assertNotIn(word, text, f"locked-removed Docker-CLI machinery in {path.name}: {word}")

    def test_no_dropped_upstream_sections_in_the_content_files(self):
        for path in _CONTENT_FILES:
            text = _norm(_read_text(path)).lower()
            for word in _DROPPED_SECTION_ABSENT_WORDS:
                self.assertNotIn(word, text, f"locked-removed upstream section in {path.name}: {word}")


class TestKeptDockerConfusionNote(unittest.TestCase):
    """The removal is the Docker-CLI machinery, not the model-level
    anti-pattern: the "Docker Confusion" note stays in the element
    checklist with its definition."""

    def test_docker_confusion_note_present_in_the_element_checklist(self):
        text = _norm(_read_text(_ELEMENT_PATH))

        self.assertIn("## Anti-patterns worth flagging", text)
        self.assertIn(
            '**The "Docker Confusion"** — Docker containers modeled as C4 containers, or C4 containers modeled '
            "as Docker containers.",
            text,
        )
        self.assertIn("Docker is a deployment mechanism (it belongs in the deployment view).", text)


class TestNoticeAndSourceMap(unittest.TestCase):
    """ACC-010: the MIT notice with its ONE source (jrjsmrtn/c4-skills @
    e86d8a91… ) and its three-file mapping, the source map with its
    ideas-only/observed marks and the dropped-content list, and the two
    files' mutual consistency (the adapted text exists exactly in the
    three files NOTICE.md lists)."""

    def test_notice_carries_the_single_source_and_the_mit_text(self):
        notice = _norm(_read_text(_NOTICE_PATH))

        for phrase in _NOTICE_PHRASES:
            self.assertIn(phrase, notice, phrase)
        # the one-source invariant: exactly one license heading, one
        # license block line, one copyright bullet, one license-block
        # copyright (each once: this skill has one MIT source, unlike
        # the two-source notice of the first three feature skills)
        self.assertEqual(notice.count("MIT License"), 2)
        self.assertEqual(notice.count("Copyright (c) 2026 Georges Martin"), 2)

    def test_notice_maps_exactly_the_three_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)
        table_rows = [
            line for line in notice.splitlines() if line.startswith("| `references/") and line.rstrip().endswith("|")
        ]
        referenced = [line.split("|")[1].strip().strip("`") for line in table_rows]

        self.assertEqual(len(table_rows), 3, "exactly three adapted files")
        self.assertEqual(
            set(referenced),
            {"references/element-checklist.md", "references/relationship-checklist.md", "references/view-checklist.md"},
        )
        for relative in referenced:
            self.assertTrue((_SKILL_DIR / relative).is_file(), relative)

    def test_source_map_phrases_present(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        for phrase in _SOURCE_MAP_PHRASES:
            self.assertIn(phrase, text, phrase)

    def test_source_map_marks_ideas_only_and_observed(self):
        text = _norm(_read_text(_SOURCE_MAP_PATH))

        self.assertIn("## `SKILL.md` — ideas only", text)
        self.assertGreaterEqual(text.count("Ideas only"), 3)
        self.assertGreaterEqual(text.count("observed"), 2)

    def test_notice_and_source_map_agree_on_the_adapted_files(self):
        notice = _read_text(_NOTICE_PATH)
        source_map = _norm(_read_text(_SOURCE_MAP_PATH))

        for relative in (
            "references/element-checklist.md",
            "references/relationship-checklist.md",
            "references/view-checklist.md",
        ):
            self.assertIn(relative, notice)
            self.assertIn(f"## `{relative}`", source_map)
        # the same single source and the same pinned commit in both
        self.assertIn("jrjsmrtn/c4-skills", notice)
        self.assertIn("jrjsmrtn/c4-skills", source_map)
        self.assertIn(_UPSTREAM_SHA, notice)
        self.assertIn(_UPSTREAM_SHA, source_map)
        # SKILL.md adapts no text: named as ideas-only in the source map,
        # and carrying no attribution row in the NOTICE table
        self.assertIn("## `SKILL.md` — ideas only", source_map)
        self.assertNotIn("| `SKILL.md` |", notice)


if __name__ == "__main__":
    unittest.main()
