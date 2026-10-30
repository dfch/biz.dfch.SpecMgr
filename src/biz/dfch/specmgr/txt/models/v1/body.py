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

"""Free-Form Text (TXT) body models: an opaque free-form `body` plus a mandatory `## Updates` log.

Built on the generic `models.md` `MarkdownSection1`/
`MarkdownSection2WithComment`/`MarkdownSection3`/`MarkdownStr` engine,
mirroring `vcr/models/v1/body.py`'s own `UpdateEntry`/`UpdateEntryContent`/
`Updates` shape (each domain owning its concrete leaf classes per the
domain-first convention). `Txt` is the top-level H1 container:

```
# {H1 title}

{any markdown, mandatory}              body: TxtBody

## Updates                              updates: Updates
<!-- optional leading comment -->
### {timestamp} ( - | : ) {title}      (>=1 entry, newest first)
{any markdown, mandatory}
```

Everything between the H1 and the first *top-level* (not inside a code
fence) `## Updates` H2 is opaque to the parser -- paragraphs, lists, code
blocks, and H2 to H6 headings alike (REQ-002). That is the one reason
`TxtBody` overrides `get_extent` with a boundary: the plain `MarkdownStr`
base implementation would consume *all* remaining text, `## Updates`
included, and every document would fail the engine's trailing-completeness
check. The boundary scan stops at the first top-level H2 whose text is
`Updates`; a `## Updates` line inside a code fence yields no `heading_open`
token, so fenced occurrences stay in the body (REQ-003). A duplicate
`## Updates`, or any H2 after `## Updates`, is then left over after the
`updates` field and rejected by the engine's own trailing-completeness
error -- no extra rule or custom error is needed (REQ-011 keeps the
engine's default messages).

The root is a plain `MarkdownSection1`, *not*
`MarkdownSection1WithComment`: with a plain root a leading HTML comment
directly under the H1 stays inside the (opaque) `body`, which is the
desired behaviour; a `WithComment` root would take it as the root's own
`comment` and leave the body empty (REQ-002's comment-only-body case).

Field declaration order on `Txt` enforces the markdown order (title ->
body -> Updates), since `models.md`'s `MarkdownStr.from_text` distributes
text among declared fields in that same order. See
`.specmgr/feat/feat-229-txt/README.md`'s Design Notes for the full schema
rationale (REQ-001..REQ-006).
"""

from __future__ import annotations

import re

from pydantic import Field, computed_field, model_validator

from ....models.md import (
    MarkdownSection1,
    MarkdownSection2WithComment,
    MarkdownSection3,
    MarkdownStr,
    alias,
    AliasType,
)
from ....models.md._markdown import parse
from ....models.md._ordering import validate_newest_first


class TxtBody(MarkdownStr):
    """`Txt.body`'s opaque free-form markdown -- everything between the H1 and the first top-level `## Updates`.

    Leaf class (no declared fields) applying no `@markdown` type/tag
    restriction of its own. Unlike the unmodified `MarkdownStr` base
    implementation -- which consumes *everything* remaining in the given
    text, `## Updates` included, and would therefore make every `txt`
    document fail the engine's trailing-completeness check -- this class
    overrides `get_extent` with the one boundary the schema needs (REQ-003):
    stop at the first *top-level* (nesting level 0, i.e. not inside a code
    fence or any other block) H2 whose text is `Updates`. A fenced
    `## Updates` yields no `heading_open` token, so it stays in the body.
    When no such heading exists (the missing-`## Updates` case), the extent
    falls back to the base implementation (everything remaining) and the
    mandatory `updates` field then fails with the engine's own
    missing-mandatory-field error.

    Mandatory: `Txt` declares `body` non-`Optional`, so a document whose H1
    is followed directly by `## Updates` (or by only whitespace, which
    `mdformat` normalizes away) finds a zero extent for the body and is
    rejected by the engine's existing mandatory-field error -- no extra
    validator (REQ-002). A comment-only body (just an HTML comment between
    the H1 and `## Updates`) *is* accepted, the comment being part of the
    opaque body -- current parser behaviour, no extra policy (REQ-002).

    Adds a `text` computed property (mirroring `UpdateEntryContent.text`'s
    own idiom and `qa`'s `IntroductionBody.text`, feat-114) so this
    otherwise-private `_value` is reachable through
    `model_dump()`/`model_dump_json()` (REQ-006).
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the body's extent as a line count, stopping before the first top-level `## Updates` H2.

        Scans the token stream for the first `heading_open` token that is an
        H2 at nesting level 0 (top-level, not inside a code fence or any
        other block) whose own heading text is `Updates`, and returns that
        heading's start line as the extent (a line count, per
        `MarkdownStr.get_extent`'s convention -- the body covers exactly the
        lines before it). When no such heading exists, falls back to
        `super().get_extent(text)` (the base `MarkdownStr` implementation:
        everything remaining), so the mandatory `updates` field declared
        after `body` fails with the engine's own error (REQ-011).

        One cost note: the boundary check re-tokenizes the entire body text
        via `parse(text)` on every parse, in addition to the engine's own
        tokenization of the same text -- an O(body-size) cost paid twice per
        parse, inherent to this override. If a "large txt body is slow"
        report ever surfaces, this is the cause to investigate first.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            int: the number of lines, from the start of `text`, covered by
                the body (see `MarkdownStr.get_extent` for the line-count
                convention).
        """
        toks = parse(text)
        for i, tok in enumerate(toks):
            if (
                tok.type == "heading_open"
                and tok.tag == "h2"
                and tok.level == 0
                and toks[i + 1].content.strip() == "Updates"
            ):
                return tok.map[0]
        return super().get_extent(text)

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Return this body's raw markdown text verbatim (or `""` if unset)."""
        return self._value


class UpdateEntryContent(MarkdownStr):
    """`UpdateEntry.content`'s opaque markdown blob -- any markdown content, not just plain paragraphs.

    Leaf class (no declared fields) applying no `@markdown` type/tag
    restriction of its own -- unlike `MarkdownParagraph`/`MarkdownSection*`/
    `MarkdownComment`. Because of that, `get_extent`/`from_text` fall back to
    the unmodified `MarkdownStr` base implementation, which simply consumes
    everything remaining in the given text regardless of its shape. Since
    `content` is the sole (and last) field on `UpdateEntry` -- nothing
    follows it before the next heading -- "everything remaining" is exactly
    correct, and no custom stop-condition override is needed.

    Mandatory: `UpdateEntry` declares `content` non-`Optional`, so the
    engine's existing mandatory-field zero-extent check (the base
    `MarkdownStr.get_extent` returning `0` for blank text) still rejects a
    heading with no body content -- no new validator code (REQ-004).

    Adds a `text` computed property (mirroring `qa`'s `IntroductionBody.text`
    idiom, feat-114) so this otherwise-private `_value` is reachable through
    `model_dump()`/`model_dump_json()`.
    """

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Return this update entry's raw markdown text verbatim (or `""` if unset)."""
        return self._value


#: Matches a `{full date+time} ( - | : ) {title}` heading line as retained in
#: a composite `MarkdownSection3`'s `.text` (which carries the heading's
#: inline content, no `###` marker), capturing the timestamp (named group
#: `timestamp`) and the title (named group `title`). Mirrors
#: `vcr.models.v1.body._UPDATE_ENTRY_HEADING_PATTERN` exactly (REQ-004).
_UPDATE_ENTRY_HEADING_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2}))(?: - | : )(?P<title>.+)"
)


@alias(
    value=r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})(?: - | : ).+$",
    type=AliasType.REGEX,
)
class UpdateEntry(MarkdownSection3):
    """`### {timestamp} ( - | : ) {title}` under `## Updates` -- one update entry.

    The H3 heading text carries a full date+time timestamp and a title,
    joined by either ``" - "`` (space, hyphen, space) or ``" : "`` (space,
    colon, space): e.g. `### 2026-08-31 07:40:12.500+02:00 - Created` or
    `### 2026-08-31T07:40:12.500+02:00 : Created`. The em-dash separator is
    rejected. The timestamp is the full ``yyyy-MM-dd`` + (``T`` or space) +
    ``HH:mm:ss.SSS`` + explicit UTC offset (``+02:00``, ``-05:00``) or
    ``Z`` for UTC variant -- date-only is rejected (ADR
    8c889262-152b-4b8e-ae2c-75371f7a9edf). Mirrors VCR's own `UpdateEntry`
    shape exactly (REQ-004).

    Parameters
    ----------
    content:
        This entry's own update text, directly under the H3 heading (any
        markdown content, not just a single paragraph). Mandatory.
    timestamp:
        Computed. The timestamp carried by the heading, verbatim. Never
        stored separately -- derived from the retained heading text.
    title:
        Computed. The title carried by the heading (the text after
        ``" - "``/``" : "``). Never stored separately -- derived from the
        retained heading text.
    """

    content: UpdateEntryContent = Field(
        description="This entry's own update text, directly under the H3 heading (any markdown content). Mandatory."
    )

    @computed_field  # type: ignore
    @property
    def timestamp(self) -> str:
        """The timestamp carried by this heading (e.g. `2026-08-31 07:40:12.500+02:00`).

        Returns:
            The timestamp string parsed from the retained heading text.

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("timestamp")
        return result

    @computed_field  # type: ignore
    @property
    def title(self) -> str:
        """The title carried by this heading (e.g. `Created` for `### 2026-08-31 07:40:12.500+02:00 - Created`).

        Returns:
            The title parsed from the retained heading text (the text
            after ``" - "``/``" : "``).

        Raises:
            AssertionError: the retained heading text does not match
                `UpdateEntry`'s declared `@alias` (unreachable via the
                engine: `match_alias` already enforced it at parse time).
        """
        match = _UPDATE_ENTRY_HEADING_PATTERN.fullmatch(self.text)
        assert match, f"UpdateEntry: expected heading '{{timestamp}} ( - | : ) {{title}}', got {self.text!r}"
        result: str = match.group("title")
        return result


class Updates(MarkdownSection2WithComment):
    """`## Updates` -- a dynamic, newest-first list of timestamp-led `### ` update entries. Mandatory, and the last
    section of the document.

    TXT's own template (Phase 120) demonstrates a permanent "newest first"
    ordering-hint HTML comment directly under this heading -- the same
    structural-anchor role `feat`'s own
    `Updates(MarkdownSection3WithComment)` already gives its own comment
    (not authoring guidance), so this is
    `MarkdownSection2WithComment`, mirroring VCR's own `Updates`. No
    dedicated per-entry tools -- entries are prepended (newest-first) by
    editing the whole body.

    Parameters
    ----------
    comment:
        Optional explanatory HTML comment (`<!-- ... -->`), e.g.
        `<!-- Newest entry first -- prepend new entries directly below
        this comment. -->`. Inherited from `MarkdownSection2WithComment`.
    updates:
        The dynamic collection of `### ` entries, in document order,
        newest-first (enforced, see `_validate_newest_first`). Requires
        at least one entry (``min_length=1``) -- an H2 with zero entries is
        a structural error (REQ-004).
    """

    updates: list[UpdateEntry] = Field(
        min_length=1,
        description="Dynamic collection of `### {timestamp} ( - | : ) {title}` entries, in document order, "
        "newest-first. Must contain at least one entry.",
    )

    @model_validator(mode="after")
    def _validate_newest_first(self) -> Updates:
        """Reject entries that are not in newest-first order.

        Delegates to the shared `models.md._ordering.validate_newest_first`
        helper (full date+time aware-datetime comparison, equal values
        allowed) -- mirrors `vcr.models.v1.body.Updates._validate_newest_first`
        without duplicating its logic. Raises on the first out-of-order pair.
        """
        validate_newest_first([update.timestamp for update in self.updates], "Updates")
        return self


@alias(value=".+", type=AliasType.REGEX)
class Txt(MarkdownSection1):
    """The `txt` body: a single H1 section with an opaque free-form `body` and a mandatory `## Updates` log.

    The H1 heading text is free-form. Deliberately a plain
    `MarkdownSection1`, *not* `MarkdownSection1WithComment`: with a plain
    root a leading HTML comment directly under the H1 stays inside the
    opaque `body` (the desired behaviour -- a comment-only body is accepted,
    REQ-002), while a `WithComment` root would take it as the root's own
    `comment` and leave the body empty (failing the mandatory `body`).

    Parameters
    ----------
    body:
        The opaque free-form markdown between the H1 and the first
        top-level `## Updates` (REQ-002/REQ-003). Mandatory.
    updates:
        `## Updates` (>=1 newest-first `### ` entry). Mandatory; last
        section (REQ-004).
    """

    body: TxtBody = Field(description="Opaque free-form body between the H1 and `## Updates`. Mandatory.")
    updates: Updates = Field(description="`## Updates` section (>=1 newest-first entry). Mandatory; last.")
