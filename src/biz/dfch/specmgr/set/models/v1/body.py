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

"""Set (SET) body models: a mandatory opaque `## Description` plus a mandatory mixed-tag `## Items` list.

Built on the generic `models.md` `MarkdownSection1`/`MarkdownSection2`/
`MarkdownListItemWithNotes` engine: each class below models one markdown
heading, and `Set` is the top-level H1 container. A `set` document bundles
one or more already-existing specmgr artifacts of any (mixed) type via
forward references only -- the items remain the source of truth, and nothing
in an item ever points back to the set (`SET` is deliberately not a tag of
the shared 12-tag reference vocabulary). See
`.specmgr/feat/feat-173-req-iso29148-level-set/README.md`'s Design Notes
(the 2026-11-01 finalized design) for the full rationale.

Field declaration order on `Set` enforces the markdown order (title ->
Description -> Items), since `models.md`'s `MarkdownStr.from_text`
distributes text among declared fields in that same order:

```
# {H1 title}

## Description                        description: Description (M, opaque)
{any markdown}

## Items                              items: Items (M, flat list, >=1 item)
- <TAG> <uuid-or-feat-id>: <title>
  (optional per-item notes paragraph)
```

There is nothing else: no `## Owner`, no `## Source`, no other section. A
`## Description` that carries a second top-level H2 (any heading other than
`## Items`), or any H2 after `## Items`, is left over after the last
declared field and rejected by the engine's own trailing-completeness error
-- no extra rule or custom error is needed (the TXT precedent keeps the
engine's default messages).

`Description` is a field-less `MarkdownSection2` leaf: the engine's
field-less-section rule (`MarkdownSection.from_text`'s leaf case) retains
the section's complete extent -- heading and body verbatim -- in `_value`,
so *any* markdown (paragraphs, lists, quotes, fenced code, nested H3 to H6)
round-trips without structural interpretation (the SYSRS `SystemPurpose`/
SOP `Purpose` free-form-prose precedent; the TXT opaque-body precedent for
why no field is declared). A fenced `## Items` line inside the description
yields no `heading_open` token, so it stays in the opaque content.

`Items`'s bullets are the shared 12-tag reference vocabulary in any mix
(`GOL`/`PRB`/`QA`/`UC`/`REQ`/`RSK`/`DEC`/`ADR`/`VCR`/`SYSRS`/`TXT`/`FEAT`):
the eleven UUID tags carry a canonical 8-4-4-4-12 hex id, `FEAT` carries
the full `feat-NNN-slug` id or the bare `feat-NNN` number (the same shapes
the `general.tools._references` extractor and `assert_feat_id` accept --
imported from their single source, `models.md._cross_reference`, so the
three cannot drift, the feat-177 precedent). Each bullet is a
`MarkdownListItemWithNotes` (the SYSRS cross-reference-list shape): the
bullet line itself plus an optional per-bullet notes paragraph. Duplicate
`(tag, id)` pairs are rejected by the root's own `model_validator` (the VCR
`AC-NNN`/DEC `Option N` duplicate-number guard precedent).
"""

from __future__ import annotations

import re

from pydantic import Field, field_validator, model_validator

from ....models.md import (
    MarkdownListItemWithNotes,
    MarkdownSection1,
    MarkdownSection2,
    alias,
    AliasType,
)
from ....models.md._cross_reference import FEAT_ID_PATTERN as _FEAT_FULL_ID_PATTERN, UUID_PATTERN

#: The shared full feat id shape (`models.md._cross_reference`'s anchored
#: :data:`FEAT_ID_PATTERN` minus the ``^``/``$`` anchors, e.g.
#: ``feat-[0-9]+-[a-z0-9-]+``): the single source, imported rather than
#: re-spelled so this module's `FEAT` bullet shape cannot drift from
#: ``assert_feat_id``'s own check (the feat-177 single-source precedent
#: that ``general.tools._path_safety`` and ``general.tools._references``
#: follow for the same constant, all three importing from the same
#: model-side home).
_FEAT_FULL_ID_SHAPE = _FEAT_FULL_ID_PATTERN.pattern.removeprefix("^").removesuffix("$")

#: :data:`_FEAT_FULL_ID_SHAPE` split at the hyphen preceding its final
#: character class, into the leading ``feat-NNN`` number prefix (e.g.
#: ``feat-[0-9]+``) and the trailing slug class with quantifier (e.g.
#: ``[a-z0-9-]+``) -- the same split ``general.tools._references`` performs
#: for the FEAT reference pattern.
_FEAT_ID_SPLIT = re.split(r"-(?=\[[^\]]*\]\+?$)", _FEAT_FULL_ID_SHAPE, maxsplit=1)
assert len(_FEAT_ID_SPLIT) == 2, (
    f"the shared full feat id shape {_FEAT_FULL_ID_SHAPE!r} must stay of the form "
    "'<number-part>-<slug-class><quantifier>' so it can be split into its number prefix and slug parts "
    "(the feat-177 single-source precedent, repeated here)"
)
_FEAT_ID_PREFIX, _FEAT_ID_SLUG = _FEAT_ID_SPLIT

#: Matches a `## Items` bullet item text for the eleven UUID reference tags:
#: `<TAG> <uuid>: <title>` -- the shared 12-tag vocabulary minus `FEAT`
#: (whose id is never a UUID), same tag order. Named groups so the root's
#: duplicate guard can extract the `(tag, id)` pair from a matched item.
#: `re.DOTALL` is required at match time: an item's `.text` keeps the
#: embedded newline of a soft-wrapped bullet line (`mdformat` does not
#: reflow), and `.` would not otherwise match it -- the same confirmed
#: behaviour the shared `validate_cross_reference_items` helper documents
#: (the SYSRS cross-reference-list precedent; such regexes must NOT call
#: `MarkdownListItem.single_line_text`, which is for non-DOTALL shapes).
_ITEMS_UUID_PATTERN = rf"^(?P<tag>GOL|PRB|QA|UC|REQ|RSK|DEC|ADR|VCR|SYSRS|TXT) (?P<id>{UUID_PATTERN}): .+$"

#: Matches a `## Items` bullet item text for the `FEAT` reference tag:
#: `FEAT <feat-NNN-slug|feat-NNN>: <title>` -- the one tag whose id is not a
#: UUID (the full `feat-NNN-slug` shape or the bare `feat-NNN` number, built
#: from the shared constant above). Carries the same `tag`/`id` named groups
#: as the UUID pattern so the root's duplicate guard extracts both shapes
#: uniformly.
_ITEMS_FEAT_PATTERN = rf"^(?P<tag>FEAT) (?P<id>{_FEAT_ID_PREFIX}(?:-{_FEAT_ID_SLUG})?): .+$"


class Description(MarkdownSection2):
    """`## Description` -- the set's own introductory free markdown. Mandatory, opaque.

    A field-less `MarkdownSection2` leaf: any markdown (paragraphs, lists,
    quotes, fenced code, nested H3 to H6 headings) is accepted verbatim and
    round-trips byte-for-byte -- the parser captures the section's complete
    extent without structural interpretation (the engine's field-less
    leaf-case rule, the SYSRS `SystemPurpose`/SOP `Purpose` free-form-prose
    precedent and the TXT opaque-body precedent).
    """


class Items(MarkdownSection2):
    """`## Items` -- the flat bullet list of bundled artifacts, in any mix of the 12 reference tags.
    Mandatory, at least one item.

    Parameters
    ----------
    items:
        Bullet list of `<TAG> <uuid-or-feat-id>: <title>` cross-references
        from the shared 12-tag reference vocabulary (the eleven UUID tags
        plus `FEAT`), any mix, each optionally followed by an indented notes
        paragraph (the `MarkdownListItemWithNotes` shape SYSRS uses). Must
        contain at least one item.
    """

    items: list[MarkdownListItemWithNotes] = Field(
        min_length=1,
        description="Bullet list of `<TAG> <uuid-or-feat-id>: <title>` cross-references from the shared "
        "12-tag reference vocabulary (any mix); must contain at least one item.",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: list[MarkdownListItemWithNotes]) -> list[MarkdownListItemWithNotes]:
        """Enforce the `<TAG> <uuid-or-feat-id>: <title>` shape against every item's own bullet text.

        Each item's `.text` (the leading paragraph only -- a notes paragraph
        is a separate field, never part of the checked text) must fullmatch
        either the UUID-tag pattern or the `FEAT` pattern, with `re.DOTALL`
        (a soft-wrapped bullet title keeps its embedded newline, the
        `validate_cross_reference_items` precedent). A malformed bullet
        raises `ValueError`, which Pydantic channels into
        `ValidationError` with the engine's own field path and 1-based line.
        """
        for item in items:
            if not (
                re.fullmatch(_ITEMS_UUID_PATTERN, item.text, re.DOTALL)
                or re.fullmatch(_ITEMS_FEAT_PATTERN, item.text, re.DOTALL)
            ):
                raise ValueError(
                    f"item must match pattern {_ITEMS_UUID_PATTERN!r} or {_ITEMS_FEAT_PATTERN!r}, got {item.text!r}"
                )
        return items


@alias(value=".+", type=AliasType.REGEX)
class Set(MarkdownSection1):
    """The `set` body: a single H1 section with a mandatory opaque `## Description` and a mandatory
    `## Items` list.

    The H1 heading text is free-form. Deliberately a plain
    `MarkdownSection1` (no root comment field): a set document's fixed
    sections start directly under the H1.

    Parameters
    ----------
    description:
        `## Description` (opaque free markdown). Mandatory.
    items:
        `## Items` (>=1 mixed-tag `<TAG> <id>: <title>` bullet, optional
        per-bullet notes). Mandatory; last section.
    """

    description: Description = Field(description="`## Description` section (opaque free markdown). Mandatory.")
    items: Items = Field(description="`## Items` section (>=1 mixed-tag bullet). Mandatory; last.")

    @model_validator(mode="after")
    def _validate_item_pairs_unique(self) -> Set:
        """Reject duplicate `(tag, id)` pairs across `## Items`.

        Two bullets that reference the same artifact -- the same reference
        tag and the same id (the id lowercased; the tag arrives uppercase
        from the bullet pattern) -- are a duplicate and rejected (the VCR
        `AC-NNN`/DEC `Option N` duplicate-number guard precedent). The id
        is compared
        exactly as spelled in the bullet: the bare `feat-NNN` number and
        the full `feat-NNN-slug` id are two different spellings of one
        feature and are therefore two different pairs here (a resolver's
        concern, not the schema's). A duplicate raises `ValueError`, which
        Pydantic channels into `ValidationError`.
        """
        seen: set[tuple[str, str]] = set()
        for item in self.items.items:
            match = re.fullmatch(_ITEMS_UUID_PATTERN, item.text, re.DOTALL) or re.fullmatch(
                _ITEMS_FEAT_PATTERN, item.text, re.DOTALL
            )
            assert match, "the items field validator already enforced both patterns"
            pair = (match.group("tag"), match.group("id").lower())
            if pair in seen:
                raise ValueError(f"item {pair[0]} {pair[1]} is used by more than one `## Items` bullet")
            seen.add(pair)
        return self
