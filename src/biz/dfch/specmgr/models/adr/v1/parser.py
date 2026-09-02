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

"""Parse an on-disk ADR ``.md`` file into an :class:`Adr` (plan §7, §10 item 2).

Pipeline stage 1 of "parse -> validate -> render" (plan §7). This module only
does the "parse" half; "validate" is simply letting :class:`Adr`/
:class:`AdrBody`/:class:`AdrFrontmatter`'s own Pydantic validators run (the
same schema-driven check the future ``validate_adr`` MCP tool uses, plan
§7/§8) -- there is no separate validation pass here. "render" is a later,
separate module (plan §10 item 2, second half).

Two error channels, by design:

- :class:`AdrParseError` -- the markdown *structure* doesn't fit the fixed
  MADR-derived heading layout (plan §2): an unrecognized/duplicate/misplaced
  heading, more than one H1, a heading nesting level this schema doesn't
  define (H4+), a "superseded"-style duplicate option number, or stray
  non-blank text before the first heading. These are structural problems a
  human hand-editing the file (plan §7) could introduce that no amount of
  Pydantic field validation could catch, because the offending content never
  even makes it into a field.
- ``pydantic.ValidationError`` -- once headings are correctly mapped onto
  field names, constructing :class:`AdrFrontmatter`/:class:`AdrBody`/
  :class:`Adr` from that data raises this the normal Pydantic way (missing
  mandatory section, bad ``status``, bad ``version``, ...). Deliberately not
  caught/wrapped here -- it is already "one schema-driven validate_adr check,
  shared identically between LLM tool calls and human edits" (plan §7).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.token import Token

from biz.dfch.specmgr.models.md._frontmatter_parse import parse_frontmatter

from .adr import Adr
from .body import AdrBody
from .frontmatter import AdrFrontmatter
from .option import AdrOption

__all__ = ["AdrParseError", "parse_adr"]

#: Fixed H2 heading text -> AdrBody field name (plan §4's table) for the
#: "leaf" sections -- ones with no recognized sub-heading of their own, so
#: anything nested underneath them (any heading level, any title) is just
#: opaque content of that field, never separate structure. Excludes
#: "Decision Outcome" (a composite section, handled on its own below) and
#: the derived "Pros and Cons of the Options" container (plan §5, likewise
#: composite and never stored as a field itself).
_LEAF_H2_FIELD_BY_TITLE = {
    "Context and Problem Statement": "context_and_problem_statement",
    "Decision Drivers": "decision_drivers",
    "Considered Options": "considered_options",
    "More Information": "more_information",
}

#: The one composite H2 with a field of its own: its own text (before any
#: recognized child heading) is "decision_outcome"; "Consequences" and
#: "Confirmation" are its recognized H3 children (plan §4's table).
_DECISION_OUTCOME_HEADING = "Decision Outcome"

#: The one recognized-but-not-stored H2: rendered automatically from
#: ``options`` (plan §5), never parsed into a field. Composite like
#: "Decision Outcome" above -- its only recognized children are
#: "Option N: ..." headings.
_PROS_AND_CONS_HEADING = "Pros and Cons of the Options"

#: Fixed H3 heading text -> AdrBody field name (the two sub-sections of
#: "Decision Outcome", plan §4's table). These are themselves "leaf"
#: headings: anything nested underneath one (H4+, any title) is opaque
#: content of that field, exactly like an "Option N: ..." heading's content.
_H3_FIELD_BY_TITLE = {
    "Consequences": "consequences",
    "Confirmation": "confirmation",
}

#: ``### Option N: {partial_title}`` (plan §5) -- the other kind of H3.
_OPTION_HEADING_PATTERN = re.compile(r"^Option (?P<number>\d+): (?P<partial_title>.+)$")

#: ATX heading marker stripped from the raw source line to recover the
#: heading's literal text (works for Setext headings too, where there is no
#: leading ``#`` to strip and this is a no-op).
_ATX_MARKER_PATTERN = re.compile(r"^#{1,6}\s*")

_MD = MarkdownIt("commonmark")


class AdrParseError(ValueError):
    """The markdown body's heading structure does not fit the v1 schema.

    Raised for structural problems -- as opposed to
    ``pydantic.ValidationError``, raised once heading content has been
    correctly mapped onto fields but a field's own value is invalid (see
    this module's docstring for the full split).
    """


@dataclass
class _Node:
    """One heading, resolved into the document's nesting (outline) tree.

    Unlike the old flat "one entry per H1/H2/H3 token" model, a :class:`_Node`
    also knows its *direct children* -- every subsequent heading, of any
    level, that is nested more deeply and not itself nested under some other
    heading in between (the same "outline" rule browsers/editors use to build
    a table of contents from arbitrary heading levels, including skipped
    ones). This is what lets a "leaf" heading (plan §4/§5's H2 sections other
    than "Decision Outcome", plus "Consequences"/"Confirmation"/"Option N:
    ...") swallow *any* heading nested underneath it -- whatever its level or
    title -- as opaque text content, while a "composite" heading ("Decision
    Outcome", "Pros and Cons of the Options") still validates its direct
    children against the fixed patterns it recognizes.

    heading_line/content_start/end are line indices into the body's
    ``lines``: ``heading_line`` is the heading's own line, ``content_start``
    is the first line after it, and ``end`` is the exclusive end of this
    heading's *entire* subtree (i.e. up to the next heading anywhere in the
    document, at this level or shallower, or end of file).
    """

    level: int
    title: str
    heading_line: int
    content_start: int
    children: list["_Node"] = field(default_factory=list)
    end: int = 0

    @property
    def own_content_end(self) -> int:
        """End of this heading's *own* text, i.e. before its first child."""
        return self.children[0].heading_line if self.children else self.end


def parse_adr(text: str) -> Adr:
    """Parse a full on-disk ADR ``.md`` file's text into an :class:`Adr`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk.

    Returns
    -------
    Adr
        The structured document. Raises :class:`AdrParseError` for a
        malformed heading structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values fail schema
        validation (see this module's docstring). Raises ``yaml.YAMLError``
        for malformed frontmatter YAML -- both frontmatter error channels
        are enriched by
        :func:`~biz.dfch.specmgr.models.md._frontmatter_parse.parse_frontmatter`
        (feat-27-validation Phase 2).
    """
    fm, content = parse_frontmatter(text, AdrFrontmatter, domain="adr", stringify_metadata=_stringify_metadata)
    body = _parse_body(content)
    return Adr(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block with a standard YAML
    loader, which auto-converts an unquoted ``date: 2024-01-01`` into a
    ``datetime.date`` -- but every :class:`AdrFrontmatter` field is
    ``str | None`` (plan §3: "not enforced here since the ``.md`` file is
    the source of truth"), so a raw ``date`` object would fail Pydantic's
    (deliberately non-coercive) string validation. Converting via ``str()``
    reproduces the same ``YYYY-MM-DD`` text a human would have written.
    ``None`` (an empty YAML key) is passed through so the field's own
    optional-ness applies normally.
    """
    return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}


@dataclass
class _BodyAccumulator:
    """Mutable state threaded through :func:`_parse_body`'s tree walk."""

    fields: dict[str, str]
    options: list[AdrOption]
    seen_h2: set[str]
    seen_h3: set[str]
    seen_option_numbers: set[int]
    has_title: bool = False


def _parse_body(content: str) -> AdrBody:
    """Parse the markdown body (frontmatter stripped) into an :class:`AdrBody`."""
    lines = content.splitlines()
    all_tokens = [tok for tok in _MD.parse("\n".join(lines)) if tok.type == "heading_open"]
    _reject_leading_content(lines, all_tokens)
    roots = _build_outline(all_tokens, lines)

    state = _BodyAccumulator(fields={}, options=[], seen_h2=set(), seen_h3=set(), seen_option_numbers=set())
    for root in roots:
        if root.level == 1:
            _handle_title(root, state)
            for child in root.children:
                _handle_h2_node(child, lines, state)
        elif root.level == 2:
            _handle_h2_node(root, lines, state)
        else:
            raise AdrParseError(f"heading level H{root.level} is not part of the ADR schema: {root.title!r}")

    return AdrBody.model_validate({**state.fields, "options": state.options})


def _build_outline(tokens: list[Token], lines: list[str]) -> list[_Node]:
    """Turn a flat, document-order token list into a heading *outline* tree.

    Standard "table of contents" nesting rule: a heading's children are
    every subsequent heading that is more deeply nested and not already
    claimed by an intervening shallower-or-equal heading -- regardless of
    whether intermediate levels are skipped (e.g. an H4 directly under an
    H2, with no H3 in between, is still that H2's direct child).
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


def _handle_title(node: _Node, state: _BodyAccumulator) -> None:
    if state.has_title:
        raise AdrParseError(f"more than one top-level (H1) title found; second one is {node.title!r}")
    state.fields["title"] = node.title
    state.has_title = True


def _handle_h2_node(node: _Node, lines: list[str], state: _BodyAccumulator) -> None:
    if node.level != 2:
        raise AdrParseError(f"heading level H{node.level} is not part of the ADR schema: {node.title!r}")

    if node.title == _PROS_AND_CONS_HEADING:
        for child in node.children:
            _handle_composite_child(child, lines, state)
        return

    if node.title == _DECISION_OUTCOME_HEADING:
        _store_field("decision_outcome", _join_content(lines[node.content_start : node.own_content_end]), state)
        for child in node.children:
            _handle_composite_child(child, lines, state)
        return

    field_name = _LEAF_H2_FIELD_BY_TITLE.get(node.title)
    if field_name is None:
        raise AdrParseError(f"unrecognized H2 heading {node.title!r}")
    # Leaf section: swallow its entire subtree verbatim, whatever headings (if any) it nests.
    _store_field(field_name, _join_content(lines[node.content_start : node.end]), state)


def _handle_composite_child(node: _Node, lines: list[str], state: _BodyAccumulator) -> None:
    """Validate/collect one direct child of a composite H2 ("Decision Outcome" or
    "Pros and Cons of the Options"): either an "Option N: ..." heading or one of the
    fixed H3 sub-fields. Anything else -- wrong level, or an H3 with an unrecognized
    title -- is a structural error."""
    option_match = _OPTION_HEADING_PATTERN.match(node.title) if node.level == 3 else None
    if option_match is not None:
        number = int(option_match.group("number"))
        if number in state.seen_option_numbers:
            raise AdrParseError(f"duplicate option number {number} (heading {node.title!r})")
        state.seen_option_numbers.add(number)
        state.options.append(
            AdrOption(
                number=number,
                partial_title=option_match.group("partial_title"),
                content=_join_content(lines[node.content_start : node.end]),
            )
        )
        return

    if node.level != 3:
        raise AdrParseError(f"heading level H{node.level} is not part of the ADR schema: {node.title!r}")

    field_name = _H3_FIELD_BY_TITLE.get(node.title)
    if field_name is None:
        raise AdrParseError(f"unrecognized H3 heading {node.title!r}")
    if field_name in state.seen_h3:
        raise AdrParseError(f"duplicate H3 heading {node.title!r}")
    state.seen_h3.add(field_name)
    # Leaf sub-field: swallow its entire subtree verbatim, whatever headings (if any) it nests.
    state.fields[field_name] = _join_content(lines[node.content_start : node.end])


def _store_field(field_name: str, value: str, state: _BodyAccumulator) -> None:
    if field_name in state.seen_h2:
        raise AdrParseError(f"duplicate H2 heading for {field_name!r}")
    state.seen_h2.add(field_name)
    state.fields[field_name] = value


def _reject_leading_content(lines: list[str], heading_tokens: list[Token]) -> None:
    first_heading_line = (
        heading_tokens[0].map[0] if heading_tokens and heading_tokens[0].map is not None else len(lines)
    )
    if _join_content(lines[:first_heading_line]):
        raise AdrParseError("content found before the first (H1) heading, which the ADR schema does not allow")


def _heading_level(token: Token) -> int:
    # ``token.tag`` is always "h1".."h6" for a ``heading_open`` token (guaranteed by MarkdownIt).
    return int(token.tag[1])


def _heading_title(lines: list[str], token: Token) -> str:
    assert token.map is not None, "heading_open token must have a map"
    raw_line = lines[token.map[0]]
    return _ATX_MARKER_PATTERN.sub("", raw_line).strip()


def _join_content(lines: list[str]) -> str:
    text = "\n".join(lines).strip("\n")
    return text.strip()
