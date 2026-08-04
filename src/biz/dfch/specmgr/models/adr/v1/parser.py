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
from dataclasses import dataclass

import frontmatter
from markdown_it import MarkdownIt
from markdown_it.token import Token

from .adr import Adr
from .body import AdrBody
from .frontmatter import AdrFrontmatter
from .option import AdrOption

__all__ = ["AdrParseError", "parse_adr"]

#: Fixed H2 heading text -> AdrBody field name (plan §4's table), excluding
#: the derived "Pros and Cons of the Options" container (plan §5, handled
#: separately below -- it has no field of its own).
_H2_FIELD_BY_TITLE = {
    "Context and Problem Statement": "context_and_problem_statement",
    "Decision Drivers": "decision_drivers",
    "Considered Options": "considered_options",
    "Decision Outcome": "decision_outcome",
    "More Information": "more_information",
}

#: The one recognized-but-not-stored H2: rendered automatically from
#: ``options`` (plan §5), never parsed into a field.
_PROS_AND_CONS_HEADING = "Pros and Cons of the Options"

#: Fixed H3 heading text -> AdrBody field name (the two sub-sections of
#: "Decision Outcome", plan §4's table).
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


@dataclass(frozen=True)
class _Heading:
    """One heading token, resolved to its literal text and content span."""

    level: int
    title: str
    content: str


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
        validation (see this module's docstring).
    """
    post = frontmatter.loads(text)
    fm = AdrFrontmatter.model_validate(_stringify_metadata(post.metadata))
    body = _parse_body(post.content)
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
    """Mutable state threaded through :func:`_parse_body`'s single heading pass."""

    fields: dict[str, str]
    options: list[AdrOption]
    seen_h2: set[str]
    seen_h3: set[str]
    seen_option_numbers: set[int]
    has_title: bool = False


def _parse_body(content: str) -> AdrBody:
    """Parse the markdown body (frontmatter stripped) into an :class:`AdrBody`."""
    lines = content.splitlines()
    headings = _collect_headings(lines)

    state = _BodyAccumulator(fields={}, options=[], seen_h2=set(), seen_h3=set(), seen_option_numbers=set())
    for heading in headings:
        if heading.level == 1:
            _handle_h1(heading, state)
        elif heading.level == 2:
            _handle_h2(heading, state)
        elif heading.level == 3:
            _handle_h3(heading, state)
        else:
            raise AdrParseError(f"heading level H{heading.level} is not part of the ADR schema: {heading.title!r}")

    return AdrBody.model_validate({**state.fields, "options": state.options})


def _handle_h1(heading: _Heading, state: _BodyAccumulator) -> None:
    if state.has_title:
        raise AdrParseError(f"more than one top-level (H1) title found; second one is {heading.title!r}")
    state.fields["title"] = heading.title
    state.has_title = True


def _handle_h2(heading: _Heading, state: _BodyAccumulator) -> None:
    if heading.title == _PROS_AND_CONS_HEADING:
        return  # derived container (plan §5); its own text is never stored
    field_name = _H2_FIELD_BY_TITLE.get(heading.title)
    if field_name is None:
        raise AdrParseError(f"unrecognized H2 heading {heading.title!r}")
    if field_name in state.seen_h2:
        raise AdrParseError(f"duplicate H2 heading {heading.title!r}")
    state.seen_h2.add(field_name)
    state.fields[field_name] = heading.content


def _handle_h3(heading: _Heading, state: _BodyAccumulator) -> None:
    option_match = _OPTION_HEADING_PATTERN.match(heading.title)
    if option_match is not None:
        _handle_option_heading(heading, option_match, state)
        return
    field_name = _H3_FIELD_BY_TITLE.get(heading.title)
    if field_name is None:
        raise AdrParseError(f"unrecognized H3 heading {heading.title!r}")
    if field_name in state.seen_h3:
        raise AdrParseError(f"duplicate H3 heading {heading.title!r}")
    state.seen_h3.add(field_name)
    state.fields[field_name] = heading.content


def _handle_option_heading(heading: _Heading, option_match: re.Match[str], state: _BodyAccumulator) -> None:
    number = int(option_match.group("number"))
    if number in state.seen_option_numbers:
        raise AdrParseError(f"duplicate option number {number} (heading {heading.title!r})")
    state.seen_option_numbers.add(number)
    state.options.append(
        AdrOption(number=number, partial_title=option_match.group("partial_title"), content=heading.content)
    )


def _collect_headings(lines: list[str]) -> list[_Heading]:
    """Walk the token stream and resolve every heading to text + own content.

    "Own content" of a heading is every line between the end of its own
    heading line(s) and the start of the very next heading in document
    order (of H1/H2/H3 only; H4+ are treated as opaque content only within
    H3 "Option N: ..." sections), or end of file for the last heading.

    H4+ headings that appear anywhere other than within option content are
    rejected during this phase; those within option content are preserved as
    text, not collected as separate heading structures.
    """
    all_tokens = [tok for tok in _MD.parse("\n".join(lines)) if tok.type == "heading_open"]
    _reject_leading_content(lines, all_tokens)

    # First pass: validate that H4+ only appear after H3 option headings
    schema_tokens = [tok for tok in all_tokens if int(tok.tag[1]) <= 3]
    _reject_h4_outside_options(lines, all_tokens, schema_tokens)

    # Second pass: collect only H1/H2/H3 tokens for schema structure
    headings: list[_Heading] = []
    for index, token in enumerate(schema_tokens):
        assert token.map is not None, "heading_open token must have a map"
        content_start = token.map[1]
        next_token_map = schema_tokens[index + 1].map if index + 1 < len(schema_tokens) else None
        content_end = next_token_map[0] if next_token_map is not None else len(lines)
        headings.append(
            _Heading(
                level=_heading_level(token),
                title=_heading_title(lines, token),
                content=_join_content(lines[content_start:content_end]),
            )
        )
    return headings


def _reject_h4_outside_options(lines: list[str], all_tokens: list[Token], schema_tokens: list[Token]) -> None:
    """Reject any H4+ heading that doesn't appear within an H3 option section."""
    h4_plus_tokens = [tok for tok in all_tokens if int(tok.tag[1]) >= 4]
    if not h4_plus_tokens:
        return

    # Build a set of (start_line, end_line) ranges for each option section
    option_ranges: list[tuple[int, int]] = []
    for i, token in enumerate(schema_tokens):
        if int(token.tag[1]) == 3:
            title = _heading_title(lines, token)
            if _OPTION_HEADING_PATTERN.match(title):
                assert token.map is not None
                section_start = token.map[0]
                # Option section ends at the next schema heading, or end of file
                next_token = schema_tokens[i + 1] if i + 1 < len(schema_tokens) else None
                section_end = next_token.map[0] if next_token and next_token.map else len(lines)
                option_ranges.append((section_start, section_end))

    # Check each H4+ token
    for h4_token in h4_plus_tokens:
        assert h4_token.map is not None
        h4_line = h4_token.map[0]
        # Check if this H4+ is within any option section
        in_option = any(start <= h4_line < end for start, end in option_ranges)
        if not in_option:
            title = _heading_title(lines, h4_token)
            raise AdrParseError(f"heading level H{int(h4_token.tag[1])} is not part of the ADR schema: {title!r}")


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
