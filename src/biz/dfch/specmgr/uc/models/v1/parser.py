"""Parse an on-disk Use Case ``.md`` file into a :class:`UseCase` (feature plan Task 1.3A).

Pipeline stage 1 of "parse -> validate" (mirrors ``models/adr/v1/parser.py``'s "parse ->
validate -> render" split, ADR's plan §7). This module only does the "parse" half; "validate"
is letting :class:`UseCase`/its nested models' own Pydantic validators run -- including the
cross-field ``model_validator`` checks added in Task 1.3B (step numbering, action numbering,
step-reference cross-resolution) -- there is no separate validation pass here.

Two error channels, by design (same split as ADR's parser):

- :class:`UcParseError` -- the markdown *structure* doesn't fit the Cockburn-derived heading/
  list layout documented in ``uc_schema.json``/``uc_example.md``: an unrecognized/duplicate/
  misplaced heading, a heading nesting level this schema doesn't define, a malformed numbered-
  list line, or stray non-blank text before the first heading. These are structural problems no
  amount of Pydantic field validation could catch, because the offending content never even
  makes it into a field.
- ``pydantic.ValidationError`` -- once headings/lists are correctly mapped onto field values,
  constructing :class:`UseCase` from that data raises this the normal Pydantic way (missing
  mandatory section, bad ``level``, non-contiguous step numbers, a dangling extension
  ``step_reference``, ...). Deliberately not caught/wrapped here.

Unlike ADR's fixed all-heading layout, the Use Case markdown format (``uc_example.md``) also
uses ordinary Markdown lists for structured content: numbered lists for
``Main Success Scenario`` steps and ``Extension`` actions, bullet lists for most other
``list[str]`` fields. Heading titles in the example additionally carry a
``" (required)"``/``" (optional)`` annotation suffix, stripped before matching against the
fixed title tables below (documentation convention, not itself validated).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import frontmatter
from markdown_it import MarkdownIt
from markdown_it.token import Token

from .characteristic_information import CharacteristicInformation
from .extension import Extension
from .extension_action import ExtensionAction
from .extensions import Extensions
from .main_success_scenario import MainSuccessScenario
from .open_issues import OpenIssues
from .related_information import RelatedInformation
from .related_use_cases import RelatedUseCases
from .step import Step
from .sub_variation import SubVariation
from .sub_variations import SubVariations
from .use_case import UseCase
from .use_case_frontmatter import UseCaseFrontmatter

__all__ = ["UcParseError", "parse_uc"]

#: Fixed H2 heading text (annotation suffix already stripped) -> UseCase field name.
_H2_FIELD_BY_TITLE = {
    "Characteristic Information": "characteristic_information",
    "Main Success Scenario": "main_success_scenario",
    "Extensions": "extensions",
    "Sub-Variations": "sub_variations",
    "Open Issues": "open_issues",
    "Related Information": "related_information",
}

#: Fixed H3 heading text (under "Characteristic Information") -> field name, and whether the
#: field is a "list" (bullet list content) or "text" (single joined text block).
_CHARACTERISTIC_INFORMATION_FIELDS: dict[str, tuple[str, str]] = {
    "Goal in Context": ("goal_in_context", "text"),
    "Scope": ("scope", "text"),
    "Level": ("level", "text"),
    "Preconditions": ("preconditions", "list"),
    "Success End Condition": ("success_end_condition", "list"),
    "Failed End Condition": ("failed_end_condition", "list"),
    "Primary Actor": ("primary_actor", "text"),
    "Secondary Actors": ("secondary_actors", "list"),
    "Trigger": ("trigger", "text"),
    "Frequency": ("frequency", "text"),
    "Priority": ("priority", "text"),
    "Performance Target": ("performance_target", "text"),
    "Channels to Primary Actor": ("channels_to_primary_actor", "list"),
    "Channels to Secondary Actors": ("channels_to_secondary_actors", "list"),
    # "Related Use Cases" handled specially -- see _parse_related_use_cases.
}

#: Fixed H3 heading text (under "Related Information") -> field name (both are optional lists).
_RELATED_INFORMATION_FIELDS = {
    "Notes": "notes",
    "Assumptions": "assumptions",
}

#: ``### {step_reference}. {condition}`` (e.g. "3a. Company is out of one of the ordered items").
_EXTENSION_HEADING_PATTERN = re.compile(r"^(?P<step_reference>[0-9]+[a-z]?)\.\s*(?P<condition>.+)$")

#: ``### Step {N}: {label}`` (label is descriptive only, not itself a modeled field).
_SUB_VARIATION_HEADING_PATTERN = re.compile(r"^Step\s+(?P<step_reference>[0-9]+):\s*.+$", re.IGNORECASE)

#: A single numbered-list line, e.g. "1. Buyer calls in..." or "3a1. Company informs...".
_NUMBERED_ITEM_PATTERN = re.compile(r"^(?P<number>[0-9]+[a-z]?[0-9]*)\.\s+(?P<description>.+)$")

#: A single bullet-list line, e.g. "- We know Buyer".
_BULLET_ITEM_PATTERN = re.compile(r"^-\s+(?P<text>.+)$")

#: "- Superordinate: ..." / "- Subordinate: ..." bullets under "Related Use Cases".
_RELATED_USE_CASE_BULLET_PATTERN = re.compile(r"^(?P<label>Superordinate|Subordinate):\s*(?P<value>.+)$", re.IGNORECASE)

#: Heading annotation suffix stripped before matching against the fixed title tables above.
_ANNOTATION_SUFFIX_PATTERN = re.compile(r"\s*\((?:required|optional)\)\s*$", re.IGNORECASE)

#: ATX heading marker stripped from the raw source line to recover the heading's literal text.
_ATX_MARKER_PATTERN = re.compile(r"^#{1,6}\s*")

_MD = MarkdownIt("commonmark")


class UcParseError(ValueError):
    """The markdown body's heading/list structure does not fit the v1 use case schema.

    Raised for structural problems -- as opposed to ``pydantic.ValidationError``, raised once
    heading/list content has been correctly mapped onto fields but a field's own value (or a
    cross-field invariant) is invalid (see this module's docstring for the full split).
    """


@dataclass
class _Node:
    """One heading, resolved into the document's nesting (outline) tree.

    Directly adapted from ``models/adr/v1/parser.py``'s ``_Node`` -- same "table of contents"
    nesting rule, same ``heading_line``/``content_start``/``end`` line-index bookkeeping.
    """

    level: int
    title: str
    heading_line: int
    content_start: int
    children: list["_Node"] = field(default_factory=list)
    end: int = 0

    @property
    def own_content_end(self) -> int:
        """End of this heading's *own* content, i.e. before its first child heading."""
        return self.children[0].heading_line if self.children else self.end


def parse_uc(text: str) -> UseCase:
    """Parse a full on-disk use case ``.md`` file's text into a :class:`UseCase`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body together, exactly
        as read from disk.

    Returns
    -------
    UseCase
        The structured document. Raises :class:`UcParseError` for a malformed heading/list
        structure, or ``pydantic.ValidationError`` for a structurally-sound document whose
        field values (or cross-field invariants) fail schema validation.
    """
    post = frontmatter.loads(text)
    fm = UseCaseFrontmatter.model_validate(post.metadata)

    lines = post.content.splitlines()
    heading_tokens = [tok for tok in _MD.parse(post.content) if tok.type == "heading_open"]
    _reject_leading_content(lines, heading_tokens)
    roots = _build_outline(heading_tokens, lines)

    if not roots or roots[0].level != 1:
        raise UcParseError("the document must start with a single top-level (H1) title heading")
    title = roots[0].title
    if len(roots) > 1:
        raise UcParseError(f"more than one top-level (H1) heading found; second one is {roots[1].title!r}")

    fields: dict[str, object] = {}
    seen_h2: set[str] = set()
    for node in roots[0].children:
        if node.level != 2:
            raise UcParseError(f"heading level H{node.level} is not part of the use case schema: {node.title!r}")
        field_name = _H2_FIELD_BY_TITLE.get(_strip_annotation(node.title))
        if field_name is None:
            raise UcParseError(f"unrecognized H2 heading {node.title!r}")
        if field_name in seen_h2:
            raise UcParseError(f"duplicate H2 heading for {field_name!r}")
        seen_h2.add(field_name)
        fields[field_name] = _parse_h2_section(field_name, node, lines)

    return UseCase(frontmatter=fm, title=title, **fields)


def _parse_h2_section(field_name: str, node: _Node, lines: list[str]) -> object:
    if field_name == "characteristic_information":
        return _parse_characteristic_information(node, lines)
    if field_name == "main_success_scenario":
        return MainSuccessScenario(steps=_parse_steps(lines[node.content_start : node.end]))
    if field_name == "extensions":
        return Extensions(items=[_parse_extension(child, lines) for child in node.children])
    if field_name == "sub_variations":
        return SubVariations(items=[_parse_sub_variation(child, lines) for child in node.children])
    if field_name == "open_issues":
        return OpenIssues(items=_parse_bullet_list(lines[node.content_start : node.end]))
    if field_name == "related_information":
        return _parse_related_information(node, lines)
    raise AssertionError(f"unhandled field_name {field_name!r}")  # pragma: no cover -- defensive


def _parse_characteristic_information(node: _Node, lines: list[str]) -> CharacteristicInformation:
    fields: dict[str, object] = {}
    seen_h3: set[str] = set()
    for child in node.children:
        if child.level != 3:
            raise UcParseError(f"heading level H{child.level} is not part of the use case schema: {child.title!r}")
        title = _strip_annotation(child.title)
        if title == "Related Use Cases":
            fields["related_use_cases"] = _parse_related_use_cases(lines[child.content_start : child.end])
            seen_h3.add("related_use_cases")
            continue
        entry = _CHARACTERISTIC_INFORMATION_FIELDS.get(title)
        if entry is None:
            raise UcParseError(f"unrecognized H3 heading under Characteristic Information: {child.title!r}")
        field_name, kind = entry
        if field_name in seen_h3:
            raise UcParseError(f"duplicate H3 heading {child.title!r}")
        seen_h3.add(field_name)
        section_lines = lines[child.content_start : child.end]
        fields[field_name] = _parse_bullet_list(section_lines) if kind == "list" else _join_text(section_lines)
    return CharacteristicInformation(**fields)


def _parse_related_use_cases(lines: list[str]) -> RelatedUseCases | None:
    bullets = [m for m in (_BULLET_ITEM_PATTERN.match(raw.strip()) for raw in lines if raw.strip()) if m]
    if not bullets:
        return None
    superordinate: str | None = None
    subordinate: list[str] | None = None
    for bullet in bullets:
        match = _RELATED_USE_CASE_BULLET_PATTERN.match(bullet.group("text"))
        if match is None:
            raise UcParseError(f"unrecognized Related Use Cases bullet: {bullet.group('text')!r}")
        label, value = match.group("label").lower(), match.group("value").strip()
        if label == "superordinate":
            superordinate = value
        else:
            subordinate = [item.strip() for item in value.split(",") if item.strip()]
    return RelatedUseCases(superordinate=superordinate, subordinate=subordinate)


def _parse_related_information(node: _Node, lines: list[str]) -> RelatedInformation:
    fields: dict[str, object] = {}
    seen_h3: set[str] = set()
    for child in node.children:
        if child.level != 3:
            raise UcParseError(f"heading level H{child.level} is not part of the use case schema: {child.title!r}")
        title = _strip_annotation(child.title)
        field_name = _RELATED_INFORMATION_FIELDS.get(title)
        if field_name is None:
            raise UcParseError(f"unrecognized H3 heading under Related Information: {child.title!r}")
        if field_name in seen_h3:
            raise UcParseError(f"duplicate H3 heading {child.title!r}")
        seen_h3.add(field_name)
        fields[field_name] = _parse_bullet_list(lines[child.content_start : child.end])
    return RelatedInformation(**fields)


def _parse_extension(node: _Node, lines: list[str]) -> Extension:
    if node.level != 3:
        raise UcParseError(f"heading level H{node.level} is not part of the use case schema: {node.title!r}")
    match = _EXTENSION_HEADING_PATTERN.match(node.title)
    if match is None:
        raise UcParseError(f"unrecognized Extension heading (expected '{{stepRef}}. {{condition}}'): {node.title!r}")
    step_reference = match.group("step_reference")
    condition = match.group("condition").strip()
    items = _parse_numbered_items(lines[node.content_start : node.end])
    actions = [ExtensionAction(number=number, description=description) for number, description in items]
    return Extension(step_reference=step_reference, condition=condition, actions=actions)


def _parse_sub_variation(node: _Node, lines: list[str]) -> SubVariation:
    if node.level != 3:
        raise UcParseError(f"heading level H{node.level} is not part of the use case schema: {node.title!r}")
    match = _SUB_VARIATION_HEADING_PATTERN.match(_strip_annotation(node.title))
    if match is None:
        raise UcParseError(f"unrecognized Sub-Variation heading (expected 'Step {{N}}: {{label}}'): {node.title!r}")
    step_reference = match.group("step_reference")
    variations = _parse_bullet_list(lines[node.content_start : node.end])
    return SubVariation(step_reference=step_reference, variations=variations)


def _parse_steps(lines: list[str]) -> list[Step]:
    return [Step(number=int(number), description=description) for number, description in _parse_numbered_items(lines)]


def _parse_numbered_items(lines: list[str]) -> list[tuple[str, str]]:
    """Parse a numbered markdown list into ``(number, description)`` pairs.

    A non-blank line not matching the numbered-item pattern is treated as a continuation of the
    previous item's description (e.g. ``uc_example.md``'s indented free-text lines under step
    3 and extension action 3a1), joined onto it with a single space.
    """
    items: list[list[str]] = []  # each entry: [number, description]
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        match = _NUMBERED_ITEM_PATTERN.match(stripped)
        if match is not None:
            items.append([match.group("number"), match.group("description").strip()])
            continue
        if not items:
            raise UcParseError(f"expected a numbered list item, got: {raw!r}")
        items[-1][1] = f"{items[-1][1]} {stripped}"
    return [(number, description) for number, description in items]  # pylint: disable=unnecessary-comprehension


def _parse_bullet_list(lines: list[str]) -> list[str]:
    return [
        m.group("text").strip() for m in (_BULLET_ITEM_PATTERN.match(raw.strip()) for raw in lines if raw.strip()) if m
    ]


def _join_text(lines: list[str]) -> str:
    return "\n".join(lines).strip("\n").strip()


def _strip_annotation(title: str) -> str:
    return _ANNOTATION_SUFFIX_PATTERN.sub("", title).strip()


def _build_outline(tokens: list[Token], lines: list[str]) -> list[_Node]:
    """Turn a flat, document-order heading token list into a heading *outline* tree.

    Identical "table of contents" nesting rule to ``models/adr/v1/parser.py``'s
    ``_build_outline``.
    """
    flat: list[_Node] = []
    roots: list[_Node] = []
    stack: list[_Node] = []
    for token in tokens:
        assert token.map is not None, "heading_open token must have a map"
        node = _Node(
            level=_heading_level(token),
            title=_heading_title(lines, token),
            heading_line=token.map[0],
            content_start=token.map[1],
        )
        flat.append(node)
        while stack and stack[-1].level >= node.level:
            stack.pop()
        (stack[-1].children if stack else roots).append(node)
        stack.append(node)

    eof = len(lines)
    for index, node in enumerate(flat):
        node.end = eof
        for later in flat[index + 1 :]:
            if later.level <= node.level:
                node.end = later.heading_line
                break
    return roots


def _reject_leading_content(lines: list[str], heading_tokens: list[Token]) -> None:
    first_heading_line = (
        heading_tokens[0].map[0] if heading_tokens and heading_tokens[0].map is not None else len(lines)
    )
    if _join_text(lines[:first_heading_line]):
        raise UcParseError("content found before the first (H1) heading, which the use case schema does not allow")


def _heading_level(token: Token) -> int:
    # ``token.tag`` is always "h1".."h6" for a ``heading_open`` token (guaranteed by MarkdownIt).
    return int(token.tag[1])


def _heading_title(lines: list[str], token: Token) -> str:
    assert token.map is not None, "heading_open token must have a map"
    raw_line = lines[token.map[0]]
    return _ATX_MARKER_PATTERN.sub("", raw_line).strip()
