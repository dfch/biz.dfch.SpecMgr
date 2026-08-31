# Implement feat-33

**Session ID:** ses_fa96c677fffekeHRfbIjY1sIU4
**Created:** 8/31/2026, 8:48:28 AM
**Updated:** 8/31/2026, 11:28:04 AM

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '116,170p' pyproject.toml"
}
```

**Output:**

```
[tool.setuptools.package-data]
"biz.dfch.specmgr" = [
    "py.typed"
]
"biz.dfch.specmgr.adr" = [
    "data/*.md"
]
"biz.dfch.specmgr.dec" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.feat" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.gol" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.prb" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.qa" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.req" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.rsk" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.tsk" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.uc" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.general" = [
    "data/*.md"
]

[tool.coverage.run]
source = ["src"]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 23.1s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat src/biz/dfch/specmgr/dec/models/v1/__init__.py\necho \"=== dec/models/__init__.py ===\"\ncat src/biz/dfch/specmgr/dec/models/__init__.py\necho \"=== dec/__init__.py ===\"\ncat src/biz/dfch/specmgr/dec/__init__.py\necho \"=== markdown_section2_with_comment.py ===\"\ncat src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py"
}
```

**Output:**

```
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

"""Decision (DEC) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors the ``gol/models/v1`` layout: a free-function ``parse_dec`` entry
point, document-level ``DecDocument(frontmatter, body)`` wrapper,
frontmatter and body subclasses under this same package, and the
``DecSummary`` listing model for the (Phase-2) ``list_dec`` tool. Body
classes map directly to heading sections in a decision markdown file --
see ``body.py`` for the full hierarchy.
"""

from ._util import SCHEMA_COMMENT_VERSION
from .body import (
    AcceptanceCriteria,
    Confirmation,
    Consequences,
    ConsideredOptions,
    Context,
    Decision,
    DecisionDrivers,
    DecisionOutcome,
    Decisions,
    Goals,
    MoreInformation,
    Option,
    ProsAndCons,
    RelatedArtifacts,
    Requirements,
    UpdateEntry,
    Updates,
)
from .document import DecDocument
from .frontmatter import DecFrontmatter
from .parser import parse_dec
from .summary import DecSummary

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "Confirmation",
    "Consequences",
    "ConsideredOptions",
    "Context",
    "DecDocument",
    "DecFrontmatter",
    "DecSummary",
    "Decision",
    "DecisionDrivers",
    "DecisionOutcome",
    "Decisions",
    "Goals",
    "MoreInformation",
    "Option",
    "ProsAndCons",
    "RelatedArtifacts",
    "Requirements",
    "UpdateEntry",
    "Updates",
    "parse_dec",
]
=== dec/models/__init__.py ===
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

"""Decision (DEC) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.

Mirrors ``rsk/models``'s layout: a versioned sub-package (``v1``, ...)
holding the frontmatter/body classes, the document wrapper and parser for
``dec`` documents, and the one-line ``DecSummary`` for the paged
``list_dec`` tool.
"""

from .v1 import (
    SCHEMA_COMMENT_VERSION,
    AcceptanceCriteria,
    Confirmation,
    Consequences,
    ConsideredOptions,
    Context,
    DecDocument,
    DecFrontmatter,
    DecSummary,
    Decision,
    DecisionDrivers,
    DecisionOutcome,
    Decisions,
    Goals,
    MoreInformation,
    Option,
    ProsAndCons,
    RelatedArtifacts,
    Requirements,
    UpdateEntry,
    Updates,
    parse_dec,
)

__all__ = [
    "SCHEMA_COMMENT_VERSION",
    "AcceptanceCriteria",
    "Confirmation",
    "Consequences",
    "ConsideredOptions",
    "Context",
    "DecDocument",
    "DecFrontmatter",
    "DecSummary",
    "Decision",
    "DecisionDrivers",
    "DecisionOutcome",
    "Decisions",
    "Goals",
    "MoreInformation",
    "Option",
    "ProsAndCons",
    "RelatedArtifacts",
    "Requirements",
    "UpdateEntry",
    "Updates",
    "parse_dec",
]
=== dec/__init__.py ===
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

"""Decision (DEC) domain -- decisions in general (not architecture-only).

This is a domain-first package, mirroring ``gol``'s layout (per ADR
ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts,
and resources for managing ``dec`` documents. A DEC keeps the ADR's general
structure (MADR-style headings, ``Options`` collection) but is built on the
generic ``models/md`` parser with the simple surface used by GOL/RSK/QA --
no fine-grained mutation tools, no by-id resource.

Import this package to register all decision tools/prompts/
resources against the shared ``mcp`` application instance at once::

    from biz.dfch.specmgr import dec  # noqa: F401 (side-effects only)

``tools`` (``create_dec``, ``parse_dec``,
``list_dec``, ``get_dec``, ``get_dec_example``, ``get_dec_template``,
``delete_dec``, ``validate_dec``), ``resources`` (``specmgr://dec/schema``,
``specmgr://dec/example``, ``specmgr://dec/template``), and ``prompts``
(``create_dec``, ``update_dec``) all exist; whole-body and line-range
updates of an existing document go through the generic ``update`` tool in
``general.tools`` (``type="dec"``), and status changes go through the
generic ``set_status`` tool in ``general.tools`` (``type="dec"``). Like
GOL, DEC has no
``specmgr://dec/{id}`` resource -- id-based reads go through the ``get_dec``
tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged
``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
"""

from . import prompts, resources, tools  # noqa: F401

__all__ = [
    "prompts",
    "resources",
    "tools",
]
=== markdown_section2_with_comment.py ===
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

"""Opt-in `MarkdownSection2` variant allowing a leading explanatory comment."""

from __future__ import annotations

from pydantic import Field

from .markdown_comment import MarkdownComment
from .markdown_section2 import MarkdownSection2


class MarkdownSection2WithComment(MarkdownSection2):
    """Adds an optional leading `<!-- ... -->` comment before another field.

    Must be paired with >=1 other declared field to hold the section's body
    content -- comment-only use raises (see `get_extent`/`from_text`).
    """

    comment: MarkdownComment | None = Field(
        default=None, description="Optional explanatory HTML comment (`<!-- ... -->`)."
    )

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Enforce the >=1-other-field constraint, then defer to `MarkdownSection2.get_extent`."""
        assert len(cls._get_field_names()) > 1, (
            f"{cls.__name__}: 'comment' must be paired with at least one other declared field "
            "to absorb the section's body content"
        )
        return super().get_extent(text)

    @classmethod
    def from_text(cls, text: str) -> MarkdownSection2WithComment:
        """Enforce the >=1-other-field constraint, then defer to `MarkdownSection2.from_text`."""
        assert len(cls._get_field_names()) > 1, (
            f"{cls.__name__}: 'comment' must be paired with at least one other declared field "
            "to absorb the section's body content"
        )
        return super().from_text(text)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 8.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat src/biz/dfch/specmgr/models/md/markdown_list_item.py\necho \"=== markdown_section4.py ===\"\ncat src/biz/dfch/specmgr/models/md/markdown_section4.py\necho \"=== grep numbered list precedent (1. ) ===\"\ngrep -rln \"^1\\. \" --include=\"*.md\" .specmgr/feat/*/example* 2>/dev/null | head\ngrep -rn \"MarkdownListItem\\b\" src/biz/dfch/specmgr/*/models/v1/body.py | grep -v __pycache__ | head -20"
}
```

**Output:**

```
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

"""One item of a markdown bullet or numbered list, usable only via `list[MarkdownListItem]`."""

from __future__ import annotations

import re

from pydantic import computed_field

from .markdown_str import MarkdownStr
from .markdown_paragraph import MarkdownParagraph
from ._markdown import format_text, parse

#: The two markdown-it block-container token types a list item can be nested under.
#: `MarkdownListItem` is deliberately shared between bullet (`ul`) and ordered (`ol`)
#: lists rather than split into per-kind subclasses -- the marker style ("-", "1.")
#: is incidental, not structural, and is always regenerated by the final `mdformat`
#: normalization pass (see `_markdown.format_text`), never tracked by this class.
_LIST_OPEN_TYPES = ("bullet_list_open", "ordered_list_open")

#: Matches a bullet ("-", "*", "+") or ordered (e.g. "1.", "1)") list item marker plus
#: the single space `mdformat` always renders after it, at the start of a line.
_MARKER_RE = re.compile(r"^(?:[-*+]|\d+[.)]) ")


class MarkdownListItem(MarkdownStr):
    """One item ("li") of a markdown bullet or numbered list.

    Used only as `items: list[MarkdownListItem]` (or `list[MarkdownListItem] |
    None`) on a `MarkdownSection`/`MarkdownParagraph`/`MarkdownListItem` --
    there is no separate list-container class, and a bare item cannot be
    parsed as a top-level/scalar field on its own; every item is assumed to
    start with at least one paragraph (its own lead text).

    Leaf (no declared nested fields, the default): `_value` holds the item's
    complete extent verbatim, marker included. Composite (a subclass declares
    fields): `_value` holds only the item's own leading paragraph, marker
    included -- the marker cannot be reconstructed from class metadata alone,
    so it is kept verbatim -- and the remainder is dedented and delegated to
    nested field parsing; `__str__` re-indents the children's rendered output
    by the marker's own width before recombining.

    Round-trip note: a tight source list currently round-trips to a
    structurally-equivalent loose list rather than byte-exact (loose lists
    remain byte-exact) -- an accepted, documented exception; see
    `from_text`/`__str__` docstrings below for the full mechanics.
    """

    @classmethod
    def get_extent(cls, text: str) -> int:
        """Return the extent of this list item, as a line count.

        There is only an extent at all if the *first* token parsed from
        `text` is a list-open wrapper (`bullet_list_open`/`ordered_list_open`)
        immediately followed by a `list_item_open` token -- i.e. `text`
        starts with (at least) one list item, whether `text` is a whole
        remaining multi-item list (only the *first* item's extent is
        reported) or an already-isolated single-item slice (the only shape
        `bullet_list_open`/`ordered_list_open` allow on their own, since
        CommonMark cannot represent a lone list item without its wrapper).
        Otherwise this returns `0`, same as the base class's "no extent" case.

        For bullet lists (`bullet_list_open`), `list_item_open`'s own `.map`
        already spans the item's *entire* content, including any nested list
        and continuation paragraphs.

        For numbered lists (`ordered_list_open`), `mdformat` renders loose
        lists differently: `list_item_open.map` only covers the first
        paragraph, and continuation paragraphs appear as separate
        `paragraph_open`/`paragraph_close` tokens *after* `ordered_list_close`
        but *before* the next `ordered_list_open` (or end of tokens). This
        method detects that case and extends the extent to include those
        trailing continuation paragraphs, ensuring consistent parsing for both
        list types.

        Args:
            text: Markdown source, pre-formatted with `mdformat`.

        Returns:
            0: `text` does not start with a list item (no extent).
            int > 0: line count (see `MarkdownStr.get_extent`) covered by the
                first list item in `text`.
        """
        assert isinstance(text, str), type(text)
        assert text == format_text(text), "text is not in 'mdformat'."

        tokens = parse(text)

        if len(tokens) < 2 or tokens[0].type not in _LIST_OPEN_TYPES or tokens[1].type != "list_item_open":
            return 0

        own_map = tokens[1].map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: list_item_open token has no line map"

        extent = own_map[1]

        # For numbered lists where each item is rendered as its own ordered_list
        # (detected by ordered_list_open.map ending at the same line as list_item_open.map),
        # continuation paragraphs appear after ordered_list_close but before the next
        # ordered_list_open. This happens for top-level lists with continuation paragraphs.
        if tokens[0].type == "ordered_list_open":
            list_open_map = tokens[0].map
            if list_open_map and len(list_open_map) == 2 and list_open_map[1] == own_map[1]:
                # Single-item ordered list: check if there's another ordered_list_open
                # after this list's ordered_list_close. If so, continuation paragraphs
                # may appear between them.
                ordered_list_close_idx = None
                for i, tok in enumerate(tokens):
                    if tok.type == "ordered_list_close":
                        ordered_list_close_idx = i
                        break

                if ordered_list_close_idx is not None:
                    # Check if there's a next ordered_list_open after this close
                    has_next_list = any(tok.type == "ordered_list_open" for tok in tokens[ordered_list_close_idx + 1 :])

                    if has_next_list:
                        # Scan for continuation paragraphs between ordered_list_close
                        # and next ordered_list_open
                        for i in range(ordered_list_close_idx + 1, len(tokens)):
                            tok = tokens[i]
                            if tok.type == "ordered_list_open":
                                break
                            if tok.type == "paragraph_open" and tok.map and len(tok.map) == 2:
                                extent = max(extent, tok.map[1])

        return extent

    @classmethod
    def from_text(cls, text: str) -> MarkdownListItem:
        """Create an instance from markdown text starting with a list item.

        Validates that `text` starts with a list-open wrapper
        (`bullet_list_open`/`ordered_list_open`) followed by a
        `list_item_open`/`paragraph_open` pair -- every item is assumed to
        start with at least one paragraph. There is no `@alias` check, same
        as `MarkdownParagraph` -- an item's text is free-form content, not a
        title.

        If `cls` declares no nested `MarkdownStr` fields (leaf case), nothing
        else will ever retain this item's text, so `_value` is set to the
        complete extent `from_text` received (marker and any nested content
        included, verbatim).

        Otherwise the item's own leading paragraph's line span is stripped
        off `text`, the remainder is dedented (`mdformat` dedents an
        indented sub-block automatically once it is renormalized on its own)
        and delegated to `MarkdownStr.from_text` (via `super()`) for the
        declared fields' population. `_value` is set to the leading
        paragraph's own lines verbatim, *marker included* -- unlike
        `MarkdownParagraph`, whose marker-free `_value` needs no
        reconstruction, an item cannot reconstruct its own marker from class
        metadata alone (see the class docstring), so it is kept as-is instead.
        """
        assert isinstance(text, str), f"text: '{type(text)}' != 'str'."
        assert text == format_text(text), "text is not in 'mdformat'."

        tokens = parse(text)
        assert len(tokens) >= 5, "Expected at least a list-open/list_item_open/paragraph triple"

        t_list_open = tokens[0]
        t_item_open = tokens[1]
        t_para_open = tokens[2]
        t_para_close = tokens[4]

        assert t_list_open.type in _LIST_OPEN_TYPES, (
            f"{cls.__name__}: expected a list wrapper, got '{t_list_open.type}'."
        )
        assert t_item_open.type == "list_item_open" and t_item_open.tag == "li", (
            f"{cls.__name__}: expected 'list_item_open'/'li', got '{t_item_open.type}'/'{t_item_open.tag}'."
        )
        assert t_para_open.type == "paragraph_open", (
            f"{cls.__name__}: expected every list item to start with a paragraph, got '{t_para_open.type}'."
        )
        assert t_para_close.nesting == -1, (
            f"Token[4]: expected a closing tag, got '{t_para_close.type}' '{t_para_close.nesting}'."
        )

        field_names = cls._get_field_names()

        if not field_names:
            instance = cls()
            instance._value = text
            return instance

        own_map = t_para_open.map
        assert own_map and len(own_map) == 2, f"{cls.__name__}: paragraph_open token has no line map"
        own_lines = own_map[1]

        lines = text.splitlines()
        body_lines = lines[own_lines:]
        body_text = format_text("\n".join(body_lines)) if body_lines else ""

        instance = super().from_text(body_text)
        instance._value = "\n".join(lines[:own_lines])
        return instance

    def __str__(self) -> str:
        """Return markdown representation, including this item's own marker.

        Leaf case (no declared nested fields): `_value` already holds the
        complete extent verbatim (marker included, see `from_text`), so this
        defers to `super().__str__()` (`MarkdownStr.__str__`'s leaf branch,
        which returns `_value` unchanged).

        Composite case: re-indents `super().__str__()`'s children output (the
        declared fields' own rendering, dedented since `from_text`) by this
        item's own marker width, derived from `_value`'s first line, then
        recombines it with `_value` -- mirroring `MarkdownSection.__str__`'s
        composite reconstruction, just with a marker-width indent instead of
        a heading prefix.
        """
        if not self._get_field_names():
            return super().__str__()

        first_line = self._value.splitlines()[0] if self._value else ""
        match = _MARKER_RE.match(first_line)
        assert match, f"{type(self).__name__}: expected a list item marker at the start of {first_line!r}"
        indent_width = match.end()

        body = super().__str__()
        reindented = "\n".join((" " * indent_width + line) if line else "" for line in body.splitlines())

        return format_text(f"{self._value}\n\n{reindented}\n")

    @computed_field  # type: ignore
    @property
    def text(self) -> str:
        """Computed property that extracts this item's leading paragraph text.

        Re-parses `_value` (which, whether leaf or composite, always starts
        with this item's own leading paragraph, see `from_text`) and returns
        the first paragraph's inline text, with the item's marker and any
        indentation stripped -- mirroring `MarkdownSection.name`'s pattern of
        deriving a plain-text convenience view from the stored markdown.

        Returns:
            The leading paragraph's text without markdown list markup, or an
            empty string if `_value` is unset (e.g. before `from_text` runs).

        Example:
            >>> item = MarkdownListItem.from_text("- We know Buyer\\n")
            >>> item.text
            'We know Buyer'
        """
        tokens = parse(self._value)

        for i, token in enumerate(tokens):
            if token.type == "inline" and i > 0 and tokens[i - 1].type == "paragraph_open":
                return token.content.strip()

        return ""


class MarkdownListItemWithNotes(MarkdownListItem):
    """One list item that captures continuation paragraphs (loose-list notes) via a declared `notes` field.

    Mirrors `ExtensionItem`'s docstring: adds `notes` for captured continuation
    paragraphs inside a list item, so they appear in ``model_dump()``/JSON output
    instead of being lost to Pydantic's private-attribute invisibility. Delegates
    ``get_extent()`` / ``from_text()`` / ``__str__()`` to the inherited
    ``MarkdownListItem`` (no new extent logic needed; ``MarkdownStr.process_list_field()``
    iterates items by ``get_extent()`` and the field-distribution loop picks up
    remaining text).
    """

    notes: list[MarkdownParagraph] | None = None
=== markdown_section4.py ===
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

"""Markdown section starting with h4 heading."""

from __future__ import annotations

from pydantic import model_validator

from .markdown_section import MarkdownSection
from .markdown import markdown


@markdown(type="heading_open", tag="h4")
class MarkdownSection4(MarkdownSection):
    """Markdown content starting with an h4 heading, no nested headings allowed.

    Tokens [0:3] form the opening h4 heading triple (heading_open/inline/heading_close).
    All tokens after index 3 must not contain any heading tags (h1-h6).
    """

    @model_validator(mode="after")
    def validate_headings(self) -> MarkdownSection4:
        """Validate heading level and no nested headings.

        Base class validates the heading triple structure.
        This validates: specific tag h4 and no nested headings in tokens [3:].
        """
        # assert self._tokens[0].tag == "h4", f"Expected h4, got {self._tokens[0].tag}"
        # assert not any(
        #     t.tag in ("h1", "h2", "h3", "h4", "h5", "h6") for t in self._tokens[3:] if t.type == "heading_open"
        # ), "Nested headings not allowed"
        return self
=== grep numbered list precedent (1. ) ===
.specmgr/feat/feat-33-vcr/example.md
src/biz/dfch/specmgr/dec/models/v1/body.py:21:`MarkdownSection3`/`MarkdownParagraph`/`MarkdownListItem` engine: each class
src/biz/dfch/specmgr/dec/models/v1/body.py:45:    MarkdownListItem,
src/biz/dfch/specmgr/dec/models/v1/body.py:116:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/dec/models/v1/body.py:127:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/dec/models/v1/body.py:138:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/dec/models/v1/body.py:150:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/feat/models/v1/body.py:22:`MarkdownParagraph`/`MarkdownListItem` engine, plus `tsk`'s own `TaskItem`
src/biz/dfch/specmgr/feat/models/v1/body.py:58:    MarkdownListItem,
src/biz/dfch/specmgr/feat/models/v1/body.py:83:class RequirementItem(MarkdownListItem):
src/biz/dfch/specmgr/feat/models/v1/body.py:86:    A leaf `MarkdownListItem` subclass (no checkbox marker, unlike `TaskItem`):
src/biz/dfch/specmgr/gol/models/v1/body.py:21:`MarkdownListItem` engine: each class below models one markdown heading
src/biz/dfch/specmgr/gol/models/v1/body.py:49:    MarkdownListItem,
src/biz/dfch/specmgr/gol/models/v1/body.py:125:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/gol/models/v1/body.py:137:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/gol/models/v1/body.py:150:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/gol/models/v1/body.py:162:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/req/models/v1/body.py:21:`MarkdownListItem` engine: each class below models one markdown heading
src/biz/dfch/specmgr/req/models/v1/body.py:35:    MarkdownListItem,
src/biz/dfch/specmgr/req/models/v1/body.py:56:    items: list[MarkdownListItem] = Field(
src/biz/dfch/specmgr/req/models/v1/body.py:160:    items: list[MarkdownListItem] = Field(

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 16.7s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/tests/dec/models/v1/test_parser.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/tests/dec/models/v1/test_parser.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Tests for :func:`parse_dec`: the `DecDocument`-level `from_text` entry point.
19: 
20: Covers the ACC-001 (structural violations -> engine `AssertionError`) and
21: ACC-002 (model-level violations -> `pydantic.ValidationError`) matrices from
22: `.specmgr/feat/feat-21-decision/README.md`. Note: ACC-002's `list_dec`
23: paging-clamp part is a Phase 2 tool test (`tests/dec/tools/`), not covered
24: here.
25: """
26: 
27: from __future__ import annotations
28: 
29: import textwrap
30: import unittest
31: 
32: import frontmatter
33: from pydantic import ValidationError
34: 
35: from biz.dfch.specmgr.dec.models.v1 import DecDocument
36: from biz.dfch.specmgr.dec.models.v1.parser import parse_dec
37: from biz.dfch.specmgr.models.md._markdown import format_text
38: 
39: # Zero optional sections: the H1, the mandatory `## Context and Problem
40: # Statement`, and the mandatory `## Decision Outcome` (with its lead
41: # paragraph) -- nothing else. This is the shape a freshly created `dec`
42: # document may legitimately have (ACC-002: every optional section defaults
43: # to `None` end to end through the full parser).
44: _MINIMAL_DOC = textwrap.dedent(
45:     """\
46:     ---
47:     id: dec-001
48:     type: dec
49:     version: 1.0.0
50:     status: draft
51:     created: 2026-08-26
52:     updated: 2026-08-26
53:     ---
54: 
55:     # Choose a Document Store
56: 
57:     ## Context and Problem Statement
58: 
59:     The current store cannot serve the dashboard read path.
60: 
61:     ## Decision Outcome
62: 
63:     We chose the document store.
64:     """
65: )
66: 
67: # Every section present: both outcome H3s, `Related Artifacts` with two
68: # sub-lists, `Pros and Cons` with two options (a number gap), `More
69: # Information`, and two `Updates` entries (the leading-zero option number
70: # below is part of ACC-002's computed-field matrix).
71: _FULL_DOC = textwrap.dedent(
72:     """\
73:     ---
74:     id: dec-001
75:     type: dec
76:     version: 1.0.0
77:     status: accepted
78:     created: 2026-08-26
79:     updated: 2026-08-27
80:     ---
81: 
82:     # Choose a Document Store
83: 
84:     ## Context and Problem Statement
85: 
86:     The current store cannot serve the dashboard read path.
87: 
88:     ## Decision Drivers
89: 
90:     - Latency under 100 ms at p95.
91: 
92:     ## Considered Options
93: 
94:     We weighed a key-value store and a document store.
95: 
96:     ## Decision Outcome
97: 
98:     We chose the document store.
99: 
100:     ### Consequences
101: 
102:     Reporting reads from the nightly export.
103: 
104:     ### Confirmation
105: 
106:     A two-week load test.
107: 
108:     ## Related Artifacts
109: 
110:     ### Requirements
111: 
112:     - REQ-9687: Order dashboard read latency
113: 
114:     ### Goals
115: 
116:     - GOL-0007: Cost-neutral platform migration
117: 
118:     ## Pros and Cons
119: 
120:     ### Option 1: Document Store
121: 
122:     Meets the latency budget.
123: 
124:     ### Option 03: Key-Value Store
125: 
126:     Even faster reads.
127: 
128:     ## More Information
129: 
130:     Harness config in the platform repository.
131: 
132:     ## Updates
133: 
134:     ### 2026-08-26 — Created
135: 
136:     Initial decision record drafted.
137: 
138:     ### 2026-08-27 — Confirmed
139: 
140:     Load test passed.
141:     """
142: )
143: 
144: 
145: class TestParseDec(unittest.TestCase):
146:     """`parse_dec` on valid documents (ACC-001/ACC-002 round-trip)."""
147: 
148:     def test_parses_minimal_document(self) -> None:
149:         """A minimal, valid document (zero optional sections) parses into a DecDocument with the expected shape."""
150:         document = parse_dec(_MINIMAL_DOC)
151: 
152:         self.assertIsInstance(document, DecDocument)
153:         self.assertEqual(document.frontmatter.id, "dec-001")
154:         self.assertEqual(document.frontmatter.type, "dec")
155:         self.assertEqual(document.frontmatter.status, "draft")
156:         self.assertEqual(document.frontmatter.created, "2026-08-26")
157:         self.assertEqual(document.body.text, "Choose a Document Store")
158:         self.assertIn("cannot serve the dashboard read path", document.body.context.text)
159:         self.assertEqual(document.body.outcome.statement.text, "We chose the document store.")
160:         self.assertIsNone(document.body.outcome.consequences)
161:         self.assertIsNone(document.body.outcome.confirmation)
162:         self.assertIsNone(document.body.drivers)
163:         self.assertIsNone(document.body.considered)
164:         self.assertIsNone(document.body.related_artifacts)
165:         self.assertIsNone(document.body.pros_and_cons)
166:         self.assertIsNone(document.body.more_information)
167:         self.assertIsNone(document.body.updates)
168: 
169:     def test_parses_full_document(self) -> None:
170:         """A document with every section present parses, with the computed fields correct (ACC-002)."""
171:         document = parse_dec(_FULL_DOC)
172: 
173:         self.assertEqual(document.frontmatter.id, "dec-001")
174:         self.assertEqual(document.frontmatter.status, "accepted")
175:         self.assertEqual(document.body.text, "Choose a Document Store")
176:         self.assertIsNotNone(document.body.drivers)
177:         self.assertIsNotNone(document.body.considered)
178: 
179:         outcome = document.body.outcome
180:         self.assertEqual(outcome.statement.text, "We chose the document store.")
181:         self.assertIsNotNone(outcome.consequences)
182:         self.assertIn("nightly export", outcome.consequences.text)
183:         self.assertIsNotNone(outcome.confirmation)
184:         self.assertIn("two-week load test", outcome.confirmation.text)
185: 
186:         related_artifacts = document.body.related_artifacts
187:         self.assertIsNotNone(related_artifacts)
188:         self.assertEqual(
189:             [item.text for item in related_artifacts.requirements.items],
190:             ["REQ-9687: Order dashboard read latency"],
191:         )
192:         self.assertIsNone(related_artifacts.decisions)
193:         self.assertEqual(
194:             [item.text for item in related_artifacts.goals.items], ["GOL-0007: Cost-neutral platform migration"]
195:         )
196:         self.assertIsNone(related_artifacts.acceptance_criteria)
197: 
198:         pros_and_cons = document.body.pros_and_cons
199:         self.assertIsNotNone(pros_and_cons)
200:         # "Option 03" normalizes to the integer 3; the 1 -> 3 gap is allowed.
201:         self.assertEqual(
202:             [(option.number, option.name) for option in pros_and_cons.options],
203:             [(1, "Document Store"), (3, "Key-Value Store")],
204:         )
205: 
206:         self.assertIsNotNone(document.body.more_information)
207:         self.assertIn("Harness config", document.body.more_information.text)
208: 
209:         updates = document.body.updates
210:         self.assertIsNotNone(updates)
211:         self.assertEqual(len(updates.updates), 2)
212:         self.assertEqual(updates.updates[0].content.text, "Initial decision record drafted.")
213:         self.assertEqual(updates.updates[1].content.text, "Load test passed.")
214: 
215:     def test_full_document_round_trips(self) -> None:
216:         """The body of the full document round-trips byte-exact through `parse_dec`."""
217:         text = _FULL_DOC
218: 
219:         document = parse_dec(text)
220: 
221:         self.assertEqual(str(document.body), format_text(frontmatter.loads(text).content))
222: 
223:     def test_defaults_frontmatter_when_absent(self) -> None:
224:         """Omitting the frontmatter block entirely still parses, applying DecFrontmatter's defaults."""
225:         text = "\n".join(_MINIMAL_DOC.splitlines()[8:]) + "\n"
226: 
227:         document = parse_dec(text)
228: 
229:         self.assertIsNone(document.frontmatter.id)
230:         self.assertEqual(document.frontmatter.type, "dec")
231:         self.assertEqual(document.frontmatter.status, "draft")
232:         self.assertEqual(document.frontmatter.version, "1.0.0")
233: 
234:     def test_related_artifacts_sub_lists_independently_optional(self) -> None:
235:         """Each of the four sub-lists can be present/absent independently (ACC-002)."""
236:         text = textwrap.dedent(
237:             """\
238:             # Choose a Document Store
239: 
240:             ## Context and Problem Statement
241: 
242:             The current store cannot serve the dashboard read path.
243: 
244:             ## Decision Outcome
245: 
246:             We chose the document store.
247: 
248:             ## Related Artifacts
249: 
250:             ### Decisions
251: 
252:             - DEC-2703: Nightly order export
253:             """
254:         )
255: 
256:         document = parse_dec(text)
257: 
258:         related_artifacts = document.body.related_artifacts
259:         self.assertIsNotNone(related_artifacts)
260:         self.assertIsNone(related_artifacts.requirements)
261:         self.assertEqual([item.text for item in related_artifacts.decisions.items], ["DEC-2703: Nightly order export"])
262:         self.assertIsNone(related_artifacts.goals)
263:         self.assertIsNone(related_artifacts.acceptance_criteria)
264: 
265:     def test_related_artifacts_with_zero_sub_lists_parses(self) -> None:
266:         """A `## Related Artifacts` H2 with none of the four sub-lists is valid (all children optional)."""
267:         text = textwrap.dedent(
268:             """\
269:             # Choose a Document Store
270: 
271:             ## Context and Problem Statement
272: 
273:             The current store cannot serve the dashboard read path.
274: 
275:             ## Decision Outcome
276: 
277:             We chose the document store.
278: 
279:             ## Related Artifacts
280:             """
281:         )
282: 
283:         document = parse_dec(text)
284: 
285:         related_artifacts = document.body.related_artifacts
286:         self.assertIsNotNone(related_artifacts)
287:         self.assertIsNone(related_artifacts.requirements)
288:         self.assertIsNone(related_artifacts.decisions)
289:         self.assertIsNone(related_artifacts.goals)
290:         self.assertIsNone(related_artifacts.acceptance_criteria)
291: 
292: 
293: class TestParseDecValueViolations(unittest.TestCase):
294:     """Model-level violations raise `pydantic.ValidationError` (ACC-002)."""
295: 
296:     def test_status_outside_closed_set_raises_validation_error(self) -> None:
297:         """A frontmatter `status` outside DecFrontmatter's closed six-set fails validation."""
298:         text = _MINIMAL_DOC.replace("status: draft", "status: in-review")
299: 
300:         with self.assertRaises(ValidationError):
301:             parse_dec(text)
302: 
303:     def test_gol_only_implemented_status_raises_validation_error(self) -> None:
304:         """`implemented` belongs to GOL's seven-value set, not DEC's six."""
305:         text = _MINIMAL_DOC.replace("status: draft", "status: implemented")
306: 
307:         with self.assertRaises(ValidationError):
308:             parse_dec(text)
309: 
310:     def test_type_other_than_dec_raises_validation_error(self) -> None:
311:         """A frontmatter `type` other than `dec` fails validation."""
312:         text = _MINIMAL_DOC.replace("type: dec", "type: gol")
313: 
314:         with self.assertRaises(ValidationError):
315:             parse_dec(text)
316: 
317:     def test_duplicate_option_number_raises_validation_error(self) -> None:
318:         """Two `### Option 1:` headings fail the `Decision` after-validator."""
319:         text = _FULL_DOC.replace("### Option 03: Key-Value Store", "### Option 1: Key-Value Store")
320: 
321:         with self.assertRaises(ValidationError):
322:             parse_dec(text)
323: 
324:     def test_duplicate_option_number_via_leading_zero_raises_validation_error(self) -> None:
325:         """`### Option 1:` and `### Option 01:` are the same number -- a duplicate."""
326:         text = _FULL_DOC.replace("### Option 03: Key-Value Store", "### Option 01: Key-Value Store")
327: 
328:         with self.assertRaises(ValidationError):
329:             parse_dec(text)
330: 
331:     def test_option_number_and_name_computed(self) -> None:
332:         """`Option.number`/`Option.name` are computed from the heading (ACC-002)."""
333:         document = parse_dec(_FULL_DOC)
334: 
335:         pros_and_cons = document.body.pros_and_cons
336:         self.assertIsNotNone(pros_and_cons)
337:         first, second = pros_and_cons.options
338: 
339:         self.assertEqual(first.number, 1)
340:         self.assertEqual(first.name, "Document Store")
341:         # Leading zeros are accepted: "03" computes to the integer 3.
342:         self.assertEqual(second.number, 3)
343:         self.assertEqual(second.name, "Key-Value Store")
344: 
345: 
346: class TestParseDecStructuralViolations(unittest.TestCase):
347:     """Structural violations raise the engine's `AssertionError` (ACC-001)."""
348: 
349:     def test_unknown_h2_raises_assertion_error(self) -> None:
350:         """An H2 heading no field claims is a structural failure."""
351:         text = textwrap.dedent(
352:             """\
353:             # Choose a Document Store
354: 
355:             ## Context and Problem Statement
356: 
357:             The current store cannot serve the dashboard read path.
358: 
359:             ## Unknown Section
360: 
361:             Some unknown prose.
362: 
363:             ## Decision Outcome
364: 
365:             We chose the document store.
366:             """
367:         )
368: 
369:         with self.assertRaises(AssertionError):
370:             parse_dec(text)
371: 
372:     def test_missing_context_raises_assertion_error(self) -> None:
373:         """A missing mandatory `## Context and Problem Statement` is a structural failure."""
374:         text = textwrap.dedent(
375:             """\
376:             # Choose a Document Store
377: 
378:             ## Decision Outcome
379: 
380:             We chose the document store.
381:             """
382:         )
383: 
384:         with self.assertRaises(AssertionError):
385:             parse_dec(text)
386: 
387:     def test_missing_decision_outcome_raises_assertion_error(self) -> None:
388:         """A missing mandatory `## Decision Outcome` is a structural failure."""
389:         text = textwrap.dedent(
390:             """\
391:             # Choose a Document Store
392: 
393:             ## Context and Problem Statement
394: 
395:             The current store cannot serve the dashboard read path.
396:             """
397:         )
398: 
399:         with self.assertRaises(AssertionError):
400:             parse_dec(text)
401: 
402:     def test_outcome_without_lead_prose_raises_assertion_error(self) -> None:
403:         """`## Decision Outcome` with a bare list in place of the lead paragraph is a structural failure."""
404:         text = textwrap.dedent(
405:             """\
406:             # Choose a Document Store
407: 
408:             ## Context and Problem Statement
409: 
410:             The current store cannot serve the dashboard read path.
411: 
412:             ## Decision Outcome
413: 
414:             - a list item
415:             """
416:         )
417: 
418:         with self.assertRaises(AssertionError):
419:             parse_dec(text)
420: 
421:     def test_pros_and_cons_with_zero_options_raises_assertion_error(self) -> None:
422:         """A `## Pros and Cons` H2 present with zero options is a structural failure."""
423:         text = textwrap.dedent(
424:             """\
425:             # Choose a Document Store
426: 
427:             ## Context and Problem Statement
428: 
429:             The current store cannot serve the dashboard read path.
430: 
431:             ## Decision Outcome
432: 
433:             We chose the document store.
434: 
435:             ## Pros and Cons
436:             """
437:         )
438: 
439:         with self.assertRaises(AssertionError):
440:             parse_dec(text)
441: 
442:     def test_option_heading_without_title_raises_assertion_error(self) -> None:
443:         """`### Option 1` without `: title` fails the option alias at parse time."""
444:         text = textwrap.dedent(
445:             """\
446:             # Choose a Document Store
447: 
448:             ## Context and Problem Statement
449: 
450:             The current store cannot serve the dashboard read path.
451: 
452:             ## Decision Outcome
453: 
454:             We chose the document store.
455: 
456:             ## Pros and Cons
457: 
458:             ### Option 1
459:             """
460:         )
461: 
462:         with self.assertRaises(AssertionError):
463:             parse_dec(text)
464: 
465:     def test_updates_with_zero_entries_raises_assertion_error(self) -> None:
466:         """A `## Updates` H2 present with zero entries is a structural failure."""
467:         text = textwrap.dedent(
468:             """\
469:             # Choose a Document Store
470: 
471:             ## Context and Problem Statement
472: 
473:             The current store cannot serve the dashboard read path.
474: 
475:             ## Decision Outcome
476: 
477:             We chose the document store.
478: 
479:             ## Updates
480:             """
481:         )
482: 
483:         with self.assertRaises(AssertionError):
484:             parse_dec(text)
485: 
486:     def test_updates_entry_without_lead_paragraph_raises_assertion_error(self) -> None:
487:         """An `## Updates` entry whose heading carries no lead paragraph is a structural failure."""
488:         text = textwrap.dedent(
489:             """\
490:             # Choose a Document Store
491: 
492:             ## Context and Problem Statement
493: 
494:             The current store cannot serve the dashboard read path.
495: 
496:             ## Decision Outcome
497: 
498:             We chose the document store.
499: 
500:             ## Updates
501: 
502:             ### 2026-08-26 — Created
503:             """
504:         )
505: 
506:         with self.assertRaises(AssertionError):
507:             parse_dec(text)
508: 
509:     def test_updates_before_more_information_raises_assertion_error(self) -> None:
510:         """Misordering: `## Updates` must come after `## More Information`."""
511:         text = textwrap.dedent(
512:             """\
513:             # Choose a Document Store
514: 
515:             ## Context and Problem Statement
516: 
517:             The current store cannot serve the dashboard read path.
518: 
519:             ## Decision Outcome
520: 
521:             We chose the document store.
522: 
523:             ## Updates
524: 
525:             ### 2026-08-26 — Created
526: 
527:             Some update text.
528: 
529:             ## More Information
530: 
531:             Some more information text.
532:             """
533:         )
534: 
535:         with self.assertRaises(AssertionError):
536:             parse_dec(text)
537: 
538:     def test_related_artifacts_after_pros_and_cons_raises_assertion_error(self) -> None:
539:         """Misordering: `## Related Artifacts` must come before `## Pros and Cons`."""
540:         text = textwrap.dedent(
541:             """\
542:             # Choose a Document Store
543: 
544:             ## Context and Problem Statement
545: 
546:             The current store cannot serve the dashboard read path.
547: 
548:             ## Decision Outcome
549: 
550:             We chose the document store.
551: 
552:             ## Pros and Cons
553: 
554:             ### Option 1: Document Store
555: 
556:             Meets the latency budget.
557: 
558:             ## Related Artifacts
559: 
560:             ### Requirements
561: 
562:             - REQ-9687: Order dashboard read latency
563:             """
564:         )
565: 
566:         with self.assertRaises(AssertionError):
567:             parse_dec(text)
568: 
569:     def test_consequences_outside_decision_outcome_raises_assertion_error(self) -> None:
570:         """Misordering: `### Consequences` only belongs under `## Decision Outcome`."""
571:         text = textwrap.dedent(
572:             """\
573:             # Choose a Document Store
574: 
575:             ### Consequences
576: 
577:             Some consequence prose.
578: 
579:             ## Context and Problem Statement
580: 
581:             The current store cannot serve the dashboard read path.
582: 
583:             ## Decision Outcome
584: 
585:             We chose the document store.
586:             """
587:         )
588: 
589:         with self.assertRaises(AssertionError):
590:             parse_dec(text)
591: 
592:     def test_confirmation_outside_decision_outcome_raises_assertion_error(self) -> None:
593:         """Misordering: `### Confirmation` only belongs under `## Decision Outcome`."""
594:         text = textwrap.dedent(
595:             """\
596:             # Choose a Document Store
597: 
598:             ### Confirmation
599: 
600:             Some confirmation prose.
601: 
602:             ## Context and Problem Statement
603: 
604:             The current store cannot serve the dashboard read path.
605: 
606:             ## Decision Outcome
607: 
608:             We chose the document store.
609:             """
610:         )
611: 
612:         with self.assertRaises(AssertionError):
613:             parse_dec(text)
614: 
615:     def test_old_adr_pros_and_cons_heading_raises_assertion_error(self) -> None:
616:         """The old ADR heading `## Pros and Cons of the Options` is rejected (LITERAL alias)."""
617:         text = _FULL_DOC.replace("## Pros and Cons", "## Pros and Cons of the Options")
618: 
619:         with self.assertRaises(AssertionError):
620:             parse_dec(text)
621: 
622:     def test_duplicate_h2_raises_assertion_error(self) -> None:
623:         """A duplicated `## Context and Problem Statement` H2 is a structural failure."""
624:         text = textwrap.dedent(
625:             """\
626:             # Choose a Document Store
627: 
628:             ## Context and Problem Statement
629: 
630:             First context prose.
631: 
632:             ## Context and Problem Statement
633: 
634:             Second context prose.
635: 
636:             ## Decision Outcome
637: 
638:             We chose the document store.
639:             """
640:         )
641: 
642:         with self.assertRaises(AssertionError):
643:             parse_dec(text)
644: 
645:     def test_nonblank_leading_content_before_h1_raises_assertion_error(self) -> None:
646:         """Non-blank content before the H1 is a structural failure."""
647:         text = textwrap.dedent(
648:             """\
649:             Some leading prose.
650: 
651:             # Choose a Document Store
652: 
653:             ## Context and Problem Statement
654: 
655:             The current store cannot serve the dashboard read path.
656: 
657:             ## Decision Outcome
658: 
659:             We chose the document store.
660:             """
661:         )
662: 
663:         with self.assertRaises(AssertionError):
664:             parse_dec(text)
665: 
666:     def test_second_h1_raises_assertion_error(self) -> None:
667:         """A second H1 is a structural failure."""
668:         text = textwrap.dedent(
669:             """\
670:             # Choose a Document Store
671: 
672:             ## Context and Problem Statement
673: 
674:             The current store cannot serve the dashboard read path.
675: 
676:             ## Decision Outcome
677: 
678:             We chose the document store.
679: 
680:             # Second Title
681:             """
682:         )
683: 
684:         with self.assertRaises(AssertionError):
685:             parse_dec(text)
686: 
687: 
688: if __name__ == "__main__":
689:     unittest.main()

(End of file - total 689 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 58.1s)

_Thinking:_

**Tool: task**

**Input:**

````json
{
  "description": "Implement VCR Phase 1",
  "prompt": "You are implementing exactly ONE phase of a feature plan for the biz.dfch.SpecMgr repo. Do NOT start any other phase (no tools/resources/prompts/server.py registration yet). Do NOT commit. Stop and report back when this phase is done or if you hit a blocker.\n\n## Plan location\nRead in full: `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/README.md` (especially \"Design Notes\" for the persisted `Verifies` class sketch, and the Task List's \"Phase 1: Models and parser\").\nAlso read the two finalized draft artifacts (Phase 0 output, already committed):\n- `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/example.md`\n- `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/template.md`\n\nAlso read `.specmgr/conventions.md` at the repo root for mandatory coding conventions (type hints, `result` variable naming, assert guidelines, etc.) before writing any code.\n\n## Phase to implement: \"Phase 1: Models and parser\"\n\nExact tasks from the plan (verbatim):\n- Task 1.1: `vcr/models/v1/frontmatter.py` (`VcrFrontmatter`, closed `status` vocabulary).\n- Task 1.2: `vcr/models/v1/body.py` (`Verifies`, `Coverage`, `AcceptanceCriterion`/`AcceptanceCriteria`, `MoreInformation`, reused `Updates`).\n- Task 1.3: `vcr/models/v1/document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`.\n- Task 1.4: Unit tests for every model class and the parser.\n\n## Precedent to mirror (this repo, already shipped -- read these files directly before writing anything)\n\n`vcr` is a from-scratch, simple-surface domain almost identical in shape to the already-shipped `dec` domain (no per-domain mutation tools, generic `update`/`set_status` dispatch, `MarkdownSection1WithComment` H1 + `## `/`### `/`#### ` children, `Updates` as the last optional section). Use `dec` as your primary structural template, NOT `sop` (referenced in the plan text but not yet implemented in this repo's `src/` -- ignore any `sop` reference for structural precedent):\n\n- `src/biz/dfch/specmgr/dec/models/v1/frontmatter.py` -- `DecFrontmatter` closed-status-vocabulary pattern (`Literal[\"dec\"]` type discriminator + `field_validator` over a `frozenset` of allowed values). Mirror this exactly for `VcrFrontmatter`, but `type: Literal[\"vcr\"] = \"vcr\"` and `status` closed to exactly `draft`/`progress`/`complete`/`approved` (REQ-004: no other status values, hyphen-free, grounded in INCOSE A26). Do NOT reuse DEC's six-value set.\n- `src/biz/dfch/specmgr/dec/models/v1/body.py` -- read in full. Two precedents inside it matter most:\n  - `Option`/`ProsAndCons`/`Decision._validate_option_numbers_unique` -- the exact pattern for a numbered-heading repeating collection with a duplicate-number `model_validator` (mirror this for `AcceptanceCriterion`/`AcceptanceCriteria`/`Vcr._validate_ac_numbers_unique`, except `AcceptanceCriterion`'s heading also carries a closed-vocabulary `Method` word, not just a name).\n  - `UpdateEntry`/`Updates` -- mirror verbatim (free-form H3 title, `content: MarkdownParagraph`, `updates: list[UpdateEntry]` with `min_length=1`, optional as a whole H2, last section).\n- `src/biz/dfch/specmgr/rsk/models/v1/assessment.py` -- `Probability`/`Impact`'s `@alias(regex)` + `@computed_field` value-in-heading pattern (mirrors how `AcceptanceCriterion.number`/`.method` should be computed from its own heading, alongside DEC's `Option.number`/`.name`).\n- `src/biz/dfch/specmgr/rsk/models/v1/body.py` -- `Strategy`'s single-line closed-vocabulary `MarkdownSection2` + `field_validator` regex pattern (mirror this for `Coverage`: `full`/`partial`/`none`, REQ-002).\n- `src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py` -- read this; `Verifies` is a `MarkdownSection2WithComment` subclass (see the exact class sketch below).\n- `src/biz/dfch/specmgr/models/md/markdown_section4.py` -- the base class for `#### Test Steps` (an H4 leaf under `AcceptanceCriterion`).\n- `src/biz/dfch/specmgr/models/md/markdown_list_item.py` -- `MarkdownListItem` is shared between bullet and numbered/ordered lists (the marker style is incidental, not structural) -- use `items: list[MarkdownListItem]` with `min_length=1` for `TestSteps`' numbered procedure list, exactly like DEC's `Requirements`/`Decisions`/`Goals`/`AcceptanceCriteria` H3 bullet-list fields (differs only in H-level: yours is H4, `min_length=1`).\n- `src/biz/dfch/specmgr/dec/models/v1/document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`, and `src/biz/dfch/specmgr/dec/models/__init__.py` -- mirror these five files' shape exactly (rename every `Dec`/`dec` occurrence to `Vcr`/`vcr`). `VcrSummary` should be a **plain** subclass of `general.models.summary.DocSummary` with **no extra fields** (mirror `DecSummary` exactly, NOT `RskSummary`'s enriched-fields precedent -- the plan does not call for exposing `## Coverage` in the listing, keep it simple).\n- Existing tests to mirror: `tests/dec/models/v1/test_frontmatter.py`, `tests/dec/models/v1/test_body.py`, `tests/dec/models/v1/test_parser.py` (read these fully). Tests build inline `textwrap.dedent` fixtures -- there is no packaged example/template data yet (that's Phase 3's job), so do NOT depend on reading `.specmgr/feat/feat-33-vcr/example.md`/`template.md` from a test (they are planning artifacts, not package data).\n\n## Exact schema to implement (grounded in the plan's Design Notes + example.md/template.md you just read)\n\n### `VcrFrontmatter` (frontmatter.py)\n- `type: Literal[\"vcr\"] = \"vcr\"`.\n- `status` closed set: exactly `{\"draft\", \"progress\", \"complete\", \"approved\"}` (REQ-004). Reject anything else (including DEC's own six-value set, RSK's, etc.) with `ValueError` via `field_validator`, same channel as `DecFrontmatter._validate_status`.\n\n### `Vcr` body (body.py) -- top-level H1 container (`MarkdownSection1WithComment`, free-form H1 title, LITERAL/REGEX `@alias` matching every other domain's `.+` pattern)\n\nField order (mirrors example.md/template.md order exactly):\n1. `comment` -- inherited from `MarkdownSection1WithComment`. Optional.\n2. `verifies: Verifies` -- `## Verifies`. Mandatory. Use the **exact** class sketch already persisted in the plan README's Design Notes section (search for \"Candidate `Verifies` class sketch\" -- copy it verbatim as your starting point, adjusting only for style/lint compliance): `MarkdownSection2WithComment` subclass with `value: MarkdownParagraph` (regex `^(REQ|UC) [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$`, `field_validator`-enforced against `value.text`) and a **mandatory** `notes: MarkdownParagraph` (paraphrase), in that field order.\n3. `coverage: Coverage` -- `## Coverage`. Mandatory. `MarkdownSection2` with `value: MarkdownParagraph`, `field_validator`-regex-enforced closed set `^(full|partial|none)$` against `value.text` (mirror RSK's `Strategy` exactly, just this 3-value TARA-shaped closed set instead).\n4. `acceptance_criteria: AcceptanceCriteria` -- `## Acceptance Criteria`. Mandatory, `>= 1` entries (`min_length=1`).\n   - `AcceptanceCriterion` -- a leaf-ish `MarkdownSection3` (mirrors DEC's `Option`) with a regex `@alias` on the whole heading: `^AC-\\d{3} \\((Demonstration|Test|Analysis|Inspection|Special)\\): .+$` (3-digit zero-padded number, DTAIS closed vocabulary as the parenthesized Method, then `: <criterion text>`). Two `@computed_field`s parsed from the retained heading text via a private module-level compiled regex (mirror RSK's `Probability`/`Impact`/DEC's `Option` idiom exactly): `number: int` (the 3-digit number, normalize to int; note unlike DEC's `Option` there is no leading-zero ambiguity to worry about beyond DEC's own precedent -- keep it simple, just `int(match.group(1))`) and `method: str` (one of the 5 DTAIS words, exactly as written in the heading -- do not lowercase/normalize it). It may also carry `test_steps: TestSteps | None = None` (a declared field, so `#### Test Steps` is absorbed as a nested child, optional).\n     - `TestSteps` -- `MarkdownSection4` (H4, `#### Test Steps`, LITERAL `@alias`) with `items: list[MarkdownListItem]`, `min_length=1` (numbered procedure list).\n   - `AcceptanceCriteria` -- `MarkdownSection2` (LITERAL `@alias` \"Acceptance Criteria\") with `criteria: list[AcceptanceCriterion]`, `min_length=1`.\n   - Duplicate-number rejection: a `model_validator(mode=\"after\")` on `Vcr` itself (NOT on `AcceptanceCriteria`), mirroring DEC's `Decision._validate_option_numbers_unique` exactly (iterate `self.acceptance_criteria.criteria`, `seen: set[int]`, raise `ValueError` on a repeat -- `acceptance_criteria` is mandatory here, unlike DEC's optional `pros_and_cons`, so no `is not None` guard is needed, but keep the same structure/docstring style).\n5. `more_information: MoreInformation | None = None` -- `## More Information`. Optional, free-form prose (mirror DEC's `MoreInformation` exactly).\n6. `updates: Updates | None = None` -- `## Updates`. Optional, last section. Mirror DEC's `UpdateEntry`/`Updates` exactly (free-form H3 title, `content: MarkdownParagraph`, `>= 1` entries if present).\n\n## Deliverables (all under `src/biz/dfch/specmgr/vcr/models/v1/` and `src/biz/dfch/specmgr/vcr/models/`, plus `tests/vcr/models/v1/`)\n\n1. `vcr/models/v1/frontmatter.py` -- `VcrFrontmatter`.\n2. `vcr/models/v1/body.py` -- `Verifies`, `Coverage`, `TestSteps`, `AcceptanceCriterion`, `AcceptanceCriteria`, `MoreInformation`, `UpdateEntry`, `Updates`, `Vcr` (with the duplicate-AC-number `model_validator`).\n3. `vcr/models/v1/document.py` -- `VcrDocument` (mirror `DecDocument` exactly).\n4. `vcr/models/v1/parser.py` -- `parse_vcr` (mirror `parse_dec` exactly, including the `_stringify_metadata` helper).\n5. `vcr/models/v1/summary.py` -- `VcrSummary` (plain `DocSummary` subclass, mirror `DecSummary` exactly).\n6. `vcr/models/v1/_util.py` -- `SCHEMA_COMMENT_VERSION = \"v1\"` (mirror `dec/models/v1/_util.py` exactly).\n7. `vcr/models/v1/__init__.py` -- re-export everything (mirror `dec/models/v1/__init__.py`'s `__all__` shape, substituting the VCR class names).\n8. `vcr/models/__init__.py` -- mirror `dec/models/__init__.py` exactly (re-export from `.v1`).\n9. Empty `__init__.py` files as needed for the new `vcr`, `vcr/models`, `vcr/models/v1` packages to be importable (there is NO top-level `vcr/__init__.py` domain-registration file yet -- that (importing `prompts`/`resources`/`tools`) is Phase 2/3/4's job, not yours; do NOT create `vcr/tools/`, `vcr/resources/`, or `vcr/prompts/` in this phase, and do NOT add `vcr` to `server.py`'s import line yet).\n10. `tests/vcr/models/v1/test_frontmatter.py`, `test_body.py`, `test_parser.py` -- mirror `tests/dec/models/v1/`'s three files' structure/coverage (minimal-document round-trip, full-document round-trip with every optional section present, frontmatter closed-vocabulary violations, structural `AssertionError` cases for missing/misordered/malformed sections, duplicate-AC-number `ValidationError`, `AcceptanceCriterion.number`/`.method` computed-field correctness, `TestSteps` presence/absence). Also add the necessary `tests/vcr/__init__.py`, `tests/vcr/models/__init__.py`, `tests/vcr/models/v1/__init__.py` package files.\n\n## Phase-end quality gate (run yourself, report exact command output)\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\nAll four must pass cleanly (vulture may need a `whitelist.py` addition if it flags a genuine framework false positive -- e.g. Pydantic `@field_validator`/`@model_validator`/`@computed_field` methods only ever invoked via decorator; check `whitelist.py`'s existing `# dec (feat-21 Phase 1): ...` comment block for the exact precedent/pattern before adding anything, and only add an entry after confirming with the existing pattern that it's a genuine framework false positive, not real dead code).\n\n## Progress-section discipline\n\nUpdate `.specmgr/feat/feat-33-vcr/README.md`'s Progress section yourself: mark Phase 1's four tasks `[x]` in the Task List, update Current Status, and prepend one new dated \"Recent Updates\" entry describing what you built (mirror the tone/detail level of the existing entries in that same file, e.g. the Phase-0 entry). Do NOT touch the \"Acceptance Criteria\" checkboxes (ACC-001..006) yet -- those get marked once every phase they depend on completes; you may note in your Updates entry that ACC-001/002/003/004 (schema-level acceptance criteria) are now satisfied by this phase's implementation + tests, but leave the checkboxes themselves for me (the orchestrator) to confirm before checking off, per the plan's own discipline.\n\n## Report back\n\n1. Full list of files created.\n2. The exact quality-gate command outputs (or a summary confirming all four passed, with test count).\n3. Confirmation you did NOT touch `server.py`, did NOT create `vcr/tools`/`vcr/resources`/`vcr/prompts`, and did NOT create a top-level `vcr/__init__.py` domain-registration file.\n4. Any blockers or genuine ambiguities not resolved by the plan text (stop and ask rather than guessing).\n\nDo NOT commit anything."
}
````

**Error:**

```
The task tool was called with invalid arguments: SchemaError(Missing key
  at ["subagent_type"]).
Please rewrite the input so it satisfies the expected schema.
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 1250.4s)

_Thinking:_

**Tool: task**

**Input:**

````json
{
  "description": "Implement VCR Phase 1",
  "prompt": "You are implementing exactly ONE phase of a feature plan for the biz.dfch.SpecMgr repo. Do NOT start any other phase (no tools/resources/prompts/server.py registration yet). Do NOT commit. Stop and report back when this phase is done or if you hit a blocker.\n\n## Plan location\nRead in full: `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/README.md` (especially \"Design Notes\" for the persisted `Verifies` class sketch, and the Task List's \"Phase 1: Models and parser\").\nAlso read the two finalized draft artifacts (Phase 0 output, already committed):\n- `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/example.md`\n- `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/template.md`\n\nAlso read `.specmgr/conventions.md` at the repo root for mandatory coding conventions (type hints, `result` variable naming, assert guidelines, etc.) before writing any code.\n\n## Phase to implement: \"Phase 1: Models and parser\"\n\nExact tasks from the plan (verbatim):\n- Task 1.1: `vcr/models/v1/frontmatter.py` (`VcrFrontmatter`, closed `status` vocabulary).\n- Task 1.2: `vcr/models/v1/body.py` (`Verifies`, `Coverage`, `AcceptanceCriterion`/`AcceptanceCriteria`, `MoreInformation`, reused `Updates`).\n- Task 1.3: `vcr/models/v1/document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`.\n- Task 1.4: Unit tests for every model class and the parser.\n\n## Precedent to mirror (this repo, already shipped -- read these files directly before writing anything)\n\n`vcr` is a from-scratch, simple-surface domain almost identical in shape to the already-shipped `dec` domain (no per-domain mutation tools, generic `update`/`set_status` dispatch, `MarkdownSection1WithComment` H1 + `## `/`### `/`#### ` children, `Updates` as the last optional section). Use `dec` as your primary structural template, NOT `sop` (referenced in the plan text but not yet implemented in this repo's `src/` -- ignore any `sop` reference for structural precedent):\n\n- `src/biz/dfch/specmgr/dec/models/v1/frontmatter.py` -- `DecFrontmatter` closed-status-vocabulary pattern (`Literal[\"dec\"]` type discriminator + `field_validator` over a `frozenset` of allowed values). Mirror this exactly for `VcrFrontmatter`, but `type: Literal[\"vcr\"] = \"vcr\"` and `status` closed to exactly `draft`/`progress`/`complete`/`approved` (REQ-004: no other status values, hyphen-free, grounded in INCOSE A26). Do NOT reuse DEC's six-value set.\n- `src/biz/dfch/specmgr/dec/models/v1/body.py` -- read in full. Two precedents inside it matter most:\n  - `Option`/`ProsAndCons`/`Decision._validate_option_numbers_unique` -- the exact pattern for a numbered-heading repeating collection with a duplicate-number `model_validator` (mirror this for `AcceptanceCriterion`/`AcceptanceCriteria`/`Vcr._validate_ac_numbers_unique`, except `AcceptanceCriterion`'s heading also carries a closed-vocabulary `Method` word, not just a name).\n  - `UpdateEntry`/`Updates` -- mirror verbatim (free-form H3 title, `content: MarkdownParagraph`, `updates: list[UpdateEntry]` with `min_length=1`, optional as a whole H2, last section).\n- `src/biz/dfch/specmgr/rsk/models/v1/assessment.py` -- `Probability`/`Impact`'s `@alias(regex)` + `@computed_field` value-in-heading pattern (mirrors how `AcceptanceCriterion.number`/`.method` should be computed from its own heading, alongside DEC's `Option.number`/`.name`).\n- `src/biz/dfch/specmgr/rsk/models/v1/body.py` -- `Strategy`'s single-line closed-vocabulary `MarkdownSection2` + `field_validator` regex pattern (mirror this for `Coverage`: `full`/`partial`/`none`, REQ-002).\n- `src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py` -- read this; `Verifies` is a `MarkdownSection2WithComment` subclass (see the exact class sketch below).\n- `src/biz/dfch/specmgr/models/md/markdown_section4.py` -- the base class for `#### Test Steps` (an H4 leaf under `AcceptanceCriterion`).\n- `src/biz/dfch/specmgr/models/md/markdown_list_item.py` -- `MarkdownListItem` is shared between bullet and numbered/ordered lists (the marker style is incidental, not structural) -- use `items: list[MarkdownListItem]` with `min_length=1` for `TestSteps`' numbered procedure list, exactly like DEC's `Requirements`/`Decisions`/`Goals`/`AcceptanceCriteria` H3 bullet-list fields (differs only in H-level: yours is H4, `min_length=1`).\n- `src/biz/dfch/specmgr/dec/models/v1/document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`, and `src/biz/dfch/specmgr/dec/models/__init__.py` -- mirror these five files' shape exactly (rename every `Dec`/`dec` occurrence to `Vcr`/`vcr`). `VcrSummary` should be a **plain** subclass of `general.models.summary.DocSummary` with **no extra fields** (mirror `DecSummary` exactly, NOT `RskSummary`'s enriched-fields precedent -- the plan does not call for exposing `## Coverage` in the listing, keep it simple).\n- Existing tests to mirror: `tests/dec/models/v1/test_frontmatter.py`, `tests/dec/models/v1/test_body.py`, `tests/dec/models/v1/test_parser.py` (read these fully). Tests build inline `textwrap.dedent` fixtures -- there is no packaged example/template data yet (that's Phase 3's job), so do NOT depend on reading `.specmgr/feat/feat-33-vcr/example.md`/`template.md` from a test (they are planning artifacts, not package data).\n\n## Exact schema to implement (grounded in the plan's Design Notes + example.md/template.md you just read)\n\n### `VcrFrontmatter` (frontmatter.py)\n- `type: Literal[\"vcr\"] = \"vcr\"`.\n- `status` closed set: exactly `{\"draft\", \"progress\", \"complete\", \"approved\"}` (REQ-004). Reject anything else (including DEC's own six-value set, RSK's, etc.) with `ValueError` via `field_validator`, same channel as `DecFrontmatter._validate_status`.\n\n### `Vcr` body (body.py) -- top-level H1 container (`MarkdownSection1WithComment`, free-form H1 title, LITERAL/REGEX `@alias` matching every other domain's `.+` pattern)\n\nField order (mirrors example.md/template.md order exactly):\n1. `comment` -- inherited from `MarkdownSection1WithComment`. Optional.\n2. `verifies: Verifies` -- `## Verifies`. Mandatory. Use the **exact** class sketch already persisted in the plan README's Design Notes section (search for \"Candidate `Verifies` class sketch\" -- copy it verbatim as your starting point, adjusting only for style/lint compliance): `MarkdownSection2WithComment` subclass with `value: MarkdownParagraph` (regex `^(REQ|UC) [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$`, `field_validator`-enforced against `value.text`) and a **mandatory** `notes: MarkdownParagraph` (paraphrase), in that field order.\n3. `coverage: Coverage` -- `## Coverage`. Mandatory. `MarkdownSection2` with `value: MarkdownParagraph`, `field_validator`-regex-enforced closed set `^(full|partial|none)$` against `value.text` (mirror RSK's `Strategy` exactly, just this 3-value TARA-shaped closed set instead).\n4. `acceptance_criteria: AcceptanceCriteria` -- `## Acceptance Criteria`. Mandatory, `>= 1` entries (`min_length=1`).\n   - `AcceptanceCriterion` -- a leaf-ish `MarkdownSection3` (mirrors DEC's `Option`) with a regex `@alias` on the whole heading: `^AC-\\d{3} \\((Demonstration|Test|Analysis|Inspection|Special)\\): .+$` (3-digit zero-padded number, DTAIS closed vocabulary as the parenthesized Method, then `: <criterion text>`). Two `@computed_field`s parsed from the retained heading text via a private module-level compiled regex (mirror RSK's `Probability`/`Impact`/DEC's `Option` idiom exactly): `number: int` (the 3-digit number, normalize to int; note unlike DEC's `Option` there is no leading-zero ambiguity to worry about beyond DEC's own precedent -- keep it simple, just `int(match.group(1))`) and `method: str` (one of the 5 DTAIS words, exactly as written in the heading -- do not lowercase/normalize it). It may also carry `test_steps: TestSteps | None = None` (a declared field, so `#### Test Steps` is absorbed as a nested child, optional).\n     - `TestSteps` -- `MarkdownSection4` (H4, `#### Test Steps`, LITERAL `@alias`) with `items: list[MarkdownListItem]`, `min_length=1` (numbered procedure list).\n   - `AcceptanceCriteria` -- `MarkdownSection2` (LITERAL `@alias` \"Acceptance Criteria\") with `criteria: list[AcceptanceCriterion]`, `min_length=1`.\n   - Duplicate-number rejection: a `model_validator(mode=\"after\")` on `Vcr` itself (NOT on `AcceptanceCriteria`), mirroring DEC's `Decision._validate_option_numbers_unique` exactly (iterate `self.acceptance_criteria.criteria`, `seen: set[int]`, raise `ValueError` on a repeat -- `acceptance_criteria` is mandatory here, unlike DEC's optional `pros_and_cons`, so no `is not None` guard is needed, but keep the same structure/docstring style).\n5. `more_information: MoreInformation | None = None` -- `## More Information`. Optional, free-form prose (mirror DEC's `MoreInformation` exactly).\n6. `updates: Updates | None = None` -- `## Updates`. Optional, last section. Mirror DEC's `UpdateEntry`/`Updates` exactly (free-form H3 title, `content: MarkdownParagraph`, `>= 1` entries if present).\n\n## Deliverables (all under `src/biz/dfch/specmgr/vcr/models/v1/` and `src/biz/dfch/specmgr/vcr/models/`, plus `tests/vcr/models/v1/`)\n\n1. `vcr/models/v1/frontmatter.py` -- `VcrFrontmatter`.\n2. `vcr/models/v1/body.py` -- `Verifies`, `Coverage`, `TestSteps`, `AcceptanceCriterion`, `AcceptanceCriteria`, `MoreInformation`, `UpdateEntry`, `Updates`, `Vcr` (with the duplicate-AC-number `model_validator`).\n3. `vcr/models/v1/document.py` -- `VcrDocument` (mirror `DecDocument` exactly).\n4. `vcr/models/v1/parser.py` -- `parse_vcr` (mirror `parse_dec` exactly, including the `_stringify_metadata` helper).\n5. `vcr/models/v1/summary.py` -- `VcrSummary` (plain `DocSummary` subclass, mirror `DecSummary` exactly).\n6. `vcr/models/v1/_util.py` -- `SCHEMA_COMMENT_VERSION = \"v1\"` (mirror `dec/models/v1/_util.py` exactly).\n7. `vcr/models/v1/__init__.py` -- re-export everything (mirror `dec/models/v1/__init__.py`'s `__all__` shape, substituting the VCR class names).\n8. `vcr/models/__init__.py` -- mirror `dec/models/__init__.py` exactly (re-export from `.v1`).\n9. Empty `__init__.py` files as needed for the new `vcr`, `vcr/models`, `vcr/models/v1` packages to be importable (there is NO top-level `vcr/__init__.py` domain-registration file yet -- that (importing `prompts`/`resources`/`tools`) is Phase 2/3/4's job, not yours; do NOT create `vcr/tools/`, `vcr/resources/`, or `vcr/prompts/` in this phase, and do NOT add `vcr` to `server.py`'s import line yet).\n10. `tests/vcr/models/v1/test_frontmatter.py`, `test_body.py`, `test_parser.py` -- mirror `tests/dec/models/v1/`'s three files' structure/coverage (minimal-document round-trip, full-document round-trip with every optional section present, frontmatter closed-vocabulary violations, structural `AssertionError` cases for missing/misordered/malformed sections, duplicate-AC-number `ValidationError`, `AcceptanceCriterion.number`/`.method` computed-field correctness, `TestSteps` presence/absence). Also add the necessary `tests/vcr/__init__.py`, `tests/vcr/models/__init__.py`, `tests/vcr/models/v1/__init__.py` package files.\n\n## Phase-end quality gate (run yourself, report exact command output)\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\nAll four must pass cleanly (vulture may need a `whitelist.py` addition if it flags a genuine framework false positive -- e.g. Pydantic `@field_validator`/`@model_validator`/`@computed_field` methods only ever invoked via decorator; check `whitelist.py`'s existing `# dec (feat-21 Phase 1): ...` comment block for the exact precedent/pattern before adding anything, and only add an entry after confirming with the existing pattern that it's a genuine framework false positive, not real dead code).\n\n## Progress-section discipline\n\nUpdate `.specmgr/feat/feat-33-vcr/README.md`'s Progress section yourself: mark Phase 1's four tasks `[x]` in the Task List, update Current Status, and prepend one new dated \"Recent Updates\" entry describing what you built (mirror the tone/detail level of the existing entries in that same file, e.g. the Phase-0 entry). Do NOT touch the \"Acceptance Criteria\" checkboxes (ACC-001..006) yet -- those get marked once every phase they depend on completes; you may note in your Updates entry that ACC-001/002/003/004 (schema-level acceptance criteria) are now satisfied by this phase's implementation + tests, but leave the checkboxes themselves for me (the orchestrator) to confirm before checking off, per the plan's own discipline.\n\n## Report back\n\n1. Full list of files created.\n2. The exact quality-gate command outputs (or a summary confirming all four passed, with test count).\n3. Confirmation you did NOT touch `server.py`, did NOT create `vcr/tools`/`vcr/resources`/`vcr/prompts`, and did NOT create a top-level `vcr/__init__.py` domain-registration file.\n4. Any blockers or genuine ambiguities not resolved by the plan text (stop and ask rather than guessing).\n\nDo NOT commit anything.",
  "subagent_type": "phase-implementer"
}
````

**Output:**

```
<task id="ses_fa95ed59cffer4mlrfro1XLn1v" state="completed">
<task_result>
Working tree is clean of stray artifacts (no commits made). Here's my final report.

## Report

### Files created
**`src/biz/dfch/specmgr/vcr/`** (new domain package, models only):
- `vcr/__init__.py` — empty/docstring-only (no `tools`/`resources`/`prompts` import; Phase 2/3/4's job)
- `vcr/models/__init__.py` — mirrors `dec/models/__init__.py`
- `vcr/models/v1/__init__.py` — mirrors `dec/models/v1/__init__.py`
- `vcr/models/v1/_util.py` — `SCHEMA_COMMENT_VERSION = "v1"`
- `vcr/models/v1/frontmatter.py` — `VcrFrontmatter` (closed `draft`/`progress`/`complete`/`approved` status set)
- `vcr/models/v1/body.py` — `Verifies`, `Coverage`, `TestSteps`, `AcceptanceCriterion`, `AcceptanceCriteria`, `MoreInformation`, `UpdateEntry`, `Updates`, `Vcr` (with `_validate_ac_numbers_unique`)
- `vcr/models/v1/document.py` — `VcrDocument`
- `vcr/models/v1/parser.py` — `parse_vcr`
- `vcr/models/v1/summary.py` — `VcrSummary` (plain `DocSummary` subclass)

**`tests/vcr/`**:
- `tests/vcr/__init__.py`, `tests/vcr/models/__init__.py`, `tests/vcr/models/v1/__init__.py`
- `tests/vcr/models/v1/test_frontmatter.py` (18 tests)
- `tests/vcr/models/v1/test_body.py` (62 tests)
- `tests/vcr/models/v1/test_parser.py` (23 tests)

**Modified**: `whitelist.py` (3 new genuine vulture false-positive entries: `_validate_ac_numbers_unique`, `verifies`, `test_steps`), `.specmgr/feat/feat-33-vcr/README.md` (Task List checkboxes, Current Status, one Updates entry, one Decisions Made entry).

### Quality gate — all green
- `uv run --frozen ruff format --check` → `1308 files already formatted`
- `uv run --frozen ruff check` → `All checks passed!`
- `uv run --frozen vulture src/ whitelist.py --min-confidence 60` → clean (no output)
- `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` → `Ran 2331 tests in ~103s` → `OK` (103 of those are new VCR tests)

### Confirmation
Did **not** touch `server.py`, did **not** create `vcr/tools`/`vcr/resources`/`vcr/prompts`, and there is no domain-registration `vcr/__init__.py` importing those sub-packages — it stays an empty/docstring-only file. Did not commit.

### Design decision made (logged in the plan's Decisions Made section)
`AcceptanceCriterion` ended up a **composite** `MarkdownSection3` (because of the declared `test_steps` field), unlike DEC's `Option`/RSK's `Probability`/`Impact`, which are leaf sections. This means:
1. The `number`/`method` computed-field regex matches against `self.text` directly (heading-only, marker already stripped) rather than `self.text.splitlines()[0]` (the DEC/RSK leaf idiom) — a mechanical adaptation, not an ambiguity.
2. An `AcceptanceCriterion`'s body can contain **only** an optional `#### Test Steps` — there is no free-form description/notes paragraph field, per the phase's literal "exact schema" instructions.

**Flag for the orchestrator**: consequence of (2) is that the already-finalized `example.md` (AC-001/002/004 have descriptive prose paragraphs under the heading, outside `Test Steps`) does **not** validate against this Phase 1 schema as implemented. Per the phase instructions, my tests deliberately don't depend on `example.md`/`template.md` (that's Phase 3's job), so this didn't block Phase 1, but it will need resolving before Phase 3 packages those files as real example/template data — either by revising `example.md`'s AC prose into the heading text only, or by adding a description field to the schema then. I did not guess at that now since the Phase 1 spec was explicit and this is a real, previously-unnoticed tension worth your review before Phase 3.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 753.7s)

_Thinking:_

I caught a schema gap: my Phase 1 spec omitted a free-form description paragraph under each `### AC-NNN` heading, but the already-finalized (committed) `example.md` has one on 3 of its 4 ACs. This is my own delegation error, not a genuine open design question — the plan's own Phase 0 discipline says the schema must match the empirically-validated example. I'll correct this by resuming the same subagent rather than escalating.

**Tool: task**

**Input:**

````json
{
  "description": "Fix VCR AcceptanceCriterion schema gap",
  "prompt": "Correction to Phase 1 (same phase, not a new one). You correctly flagged a real gap: `AcceptanceCriterion` as specified has no field to hold the free-form descriptive paragraph that already-finalized `example.md` demonstrates under 3 of its 4 `### AC-NNN (Method): ...` headings (AC-001, AC-002, AC-004 each carry a prose paragraph directly under the heading before/without `#### Test Steps`; AC-003 has none, going straight to `#### Test Steps`). This is my own specification error, not a genuine open design question -- the plan's own Phase 0 discipline requires the schema to match the empirically-validated `example.md`, not the more abstract Design Notes outline sketch (which omitted the paragraph for brevity).\n\n## Fix required\n\nAdd a `description: MarkdownParagraph | None = None` field to `AcceptanceCriterion`, declared BEFORE `test_steps` (matching document order: heading -> optional description paragraph -> optional `#### Test Steps`). Both are independently optional (AC-003 in `example.md` has no description paragraph but does have Test Steps; AC-002/AC-004 have a description paragraph but no Test Steps; AC-001 has both).\n\nUpdate:\n1. `src/biz/dfch/specmgr/vcr/models/v1/body.py` -- add the `description` field to `AcceptanceCriterion`, in the right declaration order, with an appropriate docstring entry (mirror how other optional-prose fields are documented elsewhere in this file, e.g. `MoreInformation`'s docstring tone).\n2. `tests/vcr/models/v1/test_body.py` and `test_parser.py` -- add/adjust test coverage for: an AC with only a description paragraph (no Test Steps), an AC with only Test Steps (no description), an AC with both, and an AC with neither (heading only -- confirm this still parses, since both fields are optional).\n3. As a real empirical check (not a permanent test dependency yet -- Phase 3 will package `example.md`/`template.md` as real package data), write a throwaway scratch script (e.g. `/tmp`) that reads `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/example.md`, strips its frontmatter, and calls your new `parse_vcr` (or `Vcr.from_text` directly on the body) against it end-to-end, confirming it now parses successfully with the corrected schema. Do the same for `template.md`. Report the outcome. Delete the scratch script when done; do not commit it.\n4. Re-run the full phase-end quality gate:\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\n5. Update your prior Recent-Updates entry in `.specmgr/feat/feat-33-vcr/README.md` (or add a short follow-up entry) noting this correction and that `example.md`/`template.md` now empirically validate against the Phase 1 schema end to end.\n\nDo not touch anything outside `vcr/models/v1/body.py`, the vcr test files, `whitelist.py` (only if a new genuine vulture false positive appears from the new field), and the plan README's Progress section. Do NOT commit. Report back: the diff summary, the scratch-script validation outcome for both `example.md` and `template.md`, and the quality-gate results.",
  "subagent_type": "phase-implementer",
  "task_id": "ses_fa95ed59cffer4mlrfro1XLn1v"
}
````

**Output:**

```
<task id="ses_fa95ed59cffer4mlrfro1XLn1v" state="completed">
<task_result>
## Report

### Diff summary

**`src/biz/dfch/specmgr/vcr/models/v1/body.py`** (the only source file touched):
1. `AcceptanceCriterion` — added `description: MarkdownParagraph | None = None`, declared **before** `test_steps` (heading → optional description → optional Test Steps), both independently optional. Updated class docstring and the module-level ASCII outline accordingly.
2. `Updates` — changed base class from `MarkdownSection2` to `MarkdownSection2WithComment` (mirroring `feat`'s `Updates(MarkdownSection3WithComment)`), since the scratch-script validation surfaced that `example.md`/`template.md`'s permanent "newest first" anchor comment under `## Updates` had no schema support. Updated docstring + outline.

**Test files** (`tests/vcr/models/v1/test_body.py`, `test_parser.py`):
- New `TestAcceptanceCriterionDescriptionAndTestSteps` class (4 tests: description-only, test-steps-only, both, neither).
- New `test_updates_with_leading_comment` test.
- Reference-document fixtures (`_REFERENCE_TEXT` in `test_body.py`, `_FULL_DOC` in `test_parser.py`) reshaped to a 3-AC scenario mirroring `example.md`'s exact combination coverage (AC-001: both fields; AC-003: description only; AC-004: neither), plus a leading comment under `## Updates`.
- Assertions in `test_acceptance_criteria`/`test_parses_full_document`/`test_ac_number_and_method_computed`/`test_more_information_and_updates` updated for the new shape.
- Net test count: 72 in `test_body.py` (+10), 23 in `test_parser.py` (unchanged count, content adjusted).

**`whitelist.py`**: unchanged this round — `description` is already a ubiquitous field/kwarg name used throughout the codebase, so no new vulture false positive appeared.

**`.specmgr/feat/feat-33-vcr/README.md`**: one new Recent-Updates entry and one new Decisions Made entry (superseding, not overwriting, the prior one) describing both corrections.

### Scratch-script validation outcome
Wrote `/tmp/vcr_scratch_validate.py`, ran it against both drafts, then deleted it (never committed):
- **Before the fix**: both `example.md` and `template.md` failed with `AssertionError` — first on the missing `description` field (leftover paragraph text under `### AC-NNN` headings), then, after that fix, on `## Updates`' leading comment (no `WithComment` support).
- **After both fixes**: both **parsed successfully end to end** via `parse_vcr` — frontmatter, `Verifies`, `Coverage`, every `AcceptanceCriterion`'s `description`/`test_steps` combination (confirmed all 4: AC-001 both / AC-002 description-only / AC-003 test-steps-only / AC-004 neither, in `example.md`), `More Information`, and `Updates` with its comment.
- Byte-exact round-trip (`str(body) == format_text(frontmatter.loads(text).content)`) is `False` for both, but a `difflib` diff showed the **only** difference is blank lines inserted between numbered `Test Steps` list items — the pre-existing, already-documented `MarkdownListItem` "tight numbered list round-trips to loose" quirk, unrelated to VCR and not a schema defect.

### Quality gate — all green
- `uv run --frozen ruff format --check` → `1308 files already formatted`
- `uv run --frozen ruff check` → `All checks passed!`
- `uv run --frozen vulture src/ whitelist.py --min-confidence 60` → clean, no output
- `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"` → `Ran 2336 tests` → `OK`

No commits made; scope stayed within `vcr/models/v1/body.py`, the vcr test files, and the plan README (whitelist.py touched but ended up with no net change beyond the prior turn's entries).
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.6s)

Excellent — a second real gap caught and fixed empirically. Let me independently verify.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git status --short\necho \"---\"\nfind src/biz/dfch/specmgr/vcr tests/vcr -type f | sort"
}
```

**Output:**

```
 M .specmgr/feat/feat-33-vcr/README.md
 M whitelist.py
?? src/biz/dfch/specmgr/vcr/
?? tests/vcr/
---
src/biz/dfch/specmgr/vcr/__init__.py
src/biz/dfch/specmgr/vcr/models/__init__.py
src/biz/dfch/specmgr/vcr/models/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/body.py
src/biz/dfch/specmgr/vcr/models/v1/document.py
src/biz/dfch/specmgr/vcr/models/v1/frontmatter.py
src/biz/dfch/specmgr/vcr/models/v1/__init__.py
src/biz/dfch/specmgr/vcr/models/v1/parser.py
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/body.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/document.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/frontmatter.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/__init__.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/parser.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/summary.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/__pycache__/_util.cpython-313.pyc
src/biz/dfch/specmgr/vcr/models/v1/summary.py
src/biz/dfch/specmgr/vcr/models/v1/_util.py
src/biz/dfch/specmgr/vcr/__pycache__/__init__.cpython-313.pyc
tests/vcr/__init__.py
tests/vcr/models/__init__.py
tests/vcr/models/__pycache__/__init__.cpython-313.pyc
tests/vcr/models/v1/__init__.py
tests/vcr/models/v1/__pycache__/__init__.cpython-313.pyc
tests/vcr/models/v1/__pycache__/test_body.cpython-313.pyc
tests/vcr/models/v1/__pycache__/test_frontmatter.cpython-313.pyc
tests/vcr/models/v1/__pycache__/test_parser.cpython-313.pyc
tests/vcr/models/v1/test_body.py
tests/vcr/models/v1/test_frontmatter.py
tests/vcr/models/v1/test_parser.py
tests/vcr/__pycache__/__init__.cpython-313.pyc

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.4s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/vcr/models/v1/body.py"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/vcr/models/v1/body.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Verification Case Record (VCR) body models: whole-section fields under a single H1.
19: 
20: Built on the generic `models.md` `MarkdownSection1WithComment`/`MarkdownSection2`/
21: `MarkdownSection2WithComment`/`MarkdownSection3`/`MarkdownSection4`/
22: `MarkdownParagraph`/`MarkdownListItem` engine, mirroring `dec/models/v1/body.py`'s
23: "one class per heading" shape and `rsk/models/v1/body.py`'s free-form-H1 +
24: optional-leading-comment pattern. `Vcr` is the top-level H1 container:
25: 
26: ```
27: # {H1 title}
28: <!-- optional leading comment -->        comment: MarkdownComment | None
29: 
30: ## Verifies                              verifies: Verifies
31: <!-- optional leading comment -->
32: REQ|UC <uuid>: <title>
33: {mandatory paraphrase}
34: ## Coverage                              coverage: Coverage
35: {full | partial | none}
36: ## Acceptance Criteria                   acceptance_criteria: AcceptanceCriteria (>=1 entry)
37: ### AC-NNN (Method): <criterion text>
38: {free-form description}                  (optional, per AC)
39: #### Test Steps                          (optional, per AC)
40: ## More Information                      more_information: MoreInformation | None
41: {free-form}
42: ## Updates                                updates: Updates | None
43: <!-- optional leading comment -->
44: ### {free-form title}                    (>=1 entry if present)
45: ```
46: 
47: Field declaration order on `Vcr` enforces the markdown order (title ->
48: optional comment (inherited) -> Verifies -> Coverage -> Acceptance Criteria
49: -> optional More Information -> optional Updates), since `models.md`'s
50: `MarkdownStr.from_text` distributes text among declared fields in that same
51: order. See `.specmgr/feat/feat-33-vcr/README.md`'s Design Notes for the full
52: schema rationale (REQ-001..004).
53: """
54: 
55: from __future__ import annotations
56: 
57: import re
58: 
59: from pydantic import Field, computed_field, field_validator, model_validator
60: 
61: from ....models.md import (
62:     MarkdownListItem,
63:     MarkdownParagraph,
64:     MarkdownSection1WithComment,
65:     MarkdownSection2,
66:     MarkdownSection2WithComment,
67:     MarkdownSection3,
68:     MarkdownSection4,
69:     alias,
70:     AliasType,
71: )
72: 
73: #: Matches `## Verifies`' single-line `value` paragraph: exactly one `REQ`
74: #: or `UC` cross-reference, tagged with its type, followed by a standard
75: #: 8-4-4-4-12 hex UUID and a title (REQ-001). No id-prefix precedent existed
76: #: elsewhere in the codebase to reuse for the UUID shape, so this introduces
77: #: one -- see `.specmgr/feat/feat-33-vcr/README.md` Design Notes' persisted
78: #: `Verifies` class sketch.
79: _VERIFIES_PATTERN = r"^(REQ|UC) [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}: .+$"
80: 
81: 
82: class Verifies(MarkdownSection2WithComment):
83:     """`## Verifies` -- exactly one REQ or UC cross-reference. Mandatory.
84: 
85:     Modeled as a single non-list value field (SOP's `Accountable` / RSK's
86:     `Strategy`&`Owner` / REQ&GOL's `Source` precedent), not a bullet list
87:     -- a single-value field is structurally incapable of holding more than
88:     one reference, so no cardinality `model_validator` is needed. `value`
89:     and `notes` are two mandatory fields in fixed declaration order,
90:     mirroring RSK's `Assessment.probability`/`.impact` two-mandatory-
91:     fields-in-sequence idiom (just `MarkdownParagraph` instead of
92:     `Probability`/`Impact`).
93: 
94:     Parameters
95:     ----------
96:     comment:
97:         Optional explanatory HTML comment (`<!-- ... -->`). Inherited from
98:         `MarkdownSection2WithComment`.
99:     value:
100:         Single-line `"REQ|UC <uuid>: <title>"`. Mandatory.
101:         `field_validator`-regex-checked against `_VERIFIES_PATTERN`
102:         (standard 8-4-4-4-12 hex UUID shape -- no UUID-format precedent
103:         existed elsewhere in the codebase to reuse, so this introduces
104:         one).
105:     notes:
106:         One-paragraph paraphrase of why this REQ/UC is verified here.
107:         Mandatory (unlike `MarkdownListItemWithNotes.notes`, which is
108:         optional).
109:     """
110: 
111:     value: MarkdownParagraph = Field(description='Single-line value: "REQ|UC <uuid>: <title>".')
112:     notes: MarkdownParagraph = Field(description="Mandatory one-paragraph paraphrase.")
113: 
114:     @field_validator("value")
115:     @classmethod
116:     def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
117:         """Enforce `_VERIFIES_PATTERN` against `value.text` (mirrors `req.Level`/`rsk.Strategy`)."""
118:         if not re.fullmatch(_VERIFIES_PATTERN, value.text):
119:             raise ValueError(f"value must match pattern {_VERIFIES_PATTERN!r}, got {value.text!r}")
120:         return value
121: 
122: 
123: #: `## Coverage`'s closed 3-value set (REQ-002) -- `full`/`partial`/`none`,
124: #: mirroring RSK's `## Strategy` TARA 4-value pattern but for verification
125: #: coverage instead of a risk-response strategy.
126: _COVERAGE_PATTERN = r"^(full|partial|none)$"
127: 
128: 
129: class Coverage(MarkdownSection2):
130:     """`## Coverage` -- single-line closed-vocabulary coverage assessment. Mandatory.
131: 
132:     One of the three closed values: `full`, `partial`, `none`. There is no
133:     separate pass/fail/waived outcome field anywhere in this domain --
134:     `## Coverage` is the only outcome signal (REQ-002).
135:     """
136: 
137:     value: MarkdownParagraph = Field(description="Single-line coverage assessment. One of `full`, `partial`, `none`.")
138: 
139:     @field_validator("value")
140:     @classmethod
141:     def _validate_value(cls, value: MarkdownParagraph) -> MarkdownParagraph:
142:         """Enforce `_COVERAGE_PATTERN` against `value.text` (mirrors `rsk.Strategy`)."""
143:         if not re.fullmatch(_COVERAGE_PATTERN, value.text):
144:             raise ValueError(f"value must match pattern {_COVERAGE_PATTERN!r}, got {value.text!r}")
145:         return value
146: 
147: 
148: class TestSteps(MarkdownSection4):
149:     """`#### Test Steps` under an `AcceptanceCriterion` -- numbered verification procedure. Optional.
150: 
151:     The class name's implicit `AliasType.SPACE_SEPARATED` derivation
152:     ("Test Steps") already matches this heading's own wording, so no
153:     explicit `@alias` is declared (same as DEC's `Confirmation`/
154:     `Consequences`).
155: 
156:     Parameters
157:     ----------
158:     items:
159:         The numbered procedure list, in document order. Must contain at
160:         least one item (``min_length=1``) -- an H4 with zero steps is a
161:         structural error.
162:     """
163: 
164:     items: list[MarkdownListItem] = Field(
165:         min_length=1,
166:         description="Numbered procedure list, in document order. Must contain at least one item.",
167:     )
168: 
169: 
170: #: Matches a `AC-NNN (Method): <criterion text>` heading as retained by
171: #: `AcceptanceCriterion.text` (the composite-section heading text, marker
172: #: already stripped -- see `AcceptanceCriterion`'s own docstring for why
173: #: this differs from DEC's `Option`/RSK's `Probability`/`Impact`, which are
174: #: leaf sections and therefore keep the `###`/body text in `.text` too),
175: #: capturing the 3-digit number (group 1) and the closed DTAIS method word
176: #: (group 2). Confirmed against 6 valid/8 invalid hand-written heading
177: #: fixtures via a throwaway `/tmp` scratch script during Phase 0 (Task 0.2)
178: #: -- see `.specmgr/feat/feat-33-vcr/README.md`'s Updates log.
179: _AC_HEADING_PATTERN = r"AC-(\d{3}) \((Demonstration|Test|Analysis|Inspection|Special)\): .+"
180: _AC_HEADING_RE = re.compile(_AC_HEADING_PATTERN)
181: 
182: 
183: @alias(value=rf"^{_AC_HEADING_PATTERN}$", type=AliasType.REGEX)
184: class AcceptanceCriterion(MarkdownSection3):
185:     """`### AC-NNN (Method): <criterion text>` under `## Acceptance Criteria` -- one verification criterion.
186: 
187:     The number, method, and criterion text all live in the heading itself
188:     (e.g. `### AC-001 (Test): The revoke endpoint returns 204 within 1s`),
189:     constrained by the regex `@alias` above and enforced by `match_alias`
190:     (`re.fullmatch`) at parse time -- a missing/out-of-range/malformed
191:     number, an unknown method word, or a title-less heading all fail the
192:     parse eagerly (REQ-003). AC numbers need not be contiguous (gaps are
193:     allowed, numbers are never renumbered); duplicates are rejected by
194:     `Vcr`'s own after-validator (the `ValidationError` channel, mirroring
195:     DEC's `Decision._validate_option_numbers_unique`).
196: 
197:     Unlike DEC's `Option`/RSK's `Probability`/`Impact` (all *leaf* sections
198:     with zero other declared fields, so their own `.text` computed property
199:     returns the *complete* extent verbatim, heading marker and any body
200:     text both included), this class declares two other fields
201:     (`description`, `test_steps`), making it a *composite* section: its own
202:     `.text` therefore returns only the heading's own inline content (marker
203:     stripped, body text excluded -- see `MarkdownSection.text`'s composite
204:     branch). `number`/`method` below are matched against that heading-only
205:     `.text` directly, not `.text.splitlines()[0]` -- the DEC/RSK idiom's
206:     exact mechanics don't apply verbatim here because of this leaf/composite
207:     difference, even though the underlying idea (compute a value from the
208:     retained heading text via a private module-level compiled regex) is the
209:     same. A consequence: an `AcceptanceCriterion`'s body may contain nothing
210:     besides an optional free-form `description` paragraph followed by an
211:     optional `#### Test Steps` -- both independently optional (e.g. one
212:     criterion may carry only a description, another only `Test Steps`,
213:     another both, another neither), in that fixed declaration order.
214: 
215:     Parameters
216:     ----------
217:     description:
218:         The lead paragraph directly under the heading -- free-form prose
219:         elaborating on the criterion beyond what fits in the heading
220:         itself (mirrors `MoreInformation`'s "free-form, no fixed format"
221:         tone). Optional; independent of `test_steps`.
222:     test_steps:
223:         `#### Test Steps` sub-section (a numbered verification procedure).
224:         Optional; independent of `description`.
225:     number:
226:         Computed. The criterion's 3-digit number (e.g. `1` for
227:         `### AC-001 (Test): ...`). Never stored separately -- derived from
228:         the retained heading text.
229:     method:
230:         Computed. The closed DTAIS method word carried by the heading
231:         (e.g. `"Test"` for `### AC-001 (Test): ...`), exactly as written
232:         (not lowercased/normalized). Never stored separately -- derived
233:         from the retained heading text.
234:     """
235: 
236:     description: MarkdownParagraph | None = Field(
237:         default=None,
238:         description="The lead paragraph directly under the heading -- free-form prose elaborating on the "
239:         "criterion. Optional; independent of `test_steps`.",
240:     )
241:     test_steps: TestSteps | None = Field(
242:         default=None, description="`#### Test Steps` sub-section. Optional; independent of `description`."
243:     )
244: 
245:     @computed_field  # type: ignore
246:     @property
247:     def number(self) -> int:
248:         """The criterion's 3-digit number carried by this heading (e.g. `1` for `### AC-001 (Test): ...`).
249: 
250:         Returns:
251:             The integer number parsed from the retained heading text.
252: 
253:         Raises:
254:             AssertionError: the retained heading text does not match
255:                 `AcceptanceCriterion`'s declared `@alias` (unreachable via
256:                 the engine: `match_alias` already enforced it at parse time).
257:         """
258:         match = _AC_HEADING_RE.fullmatch(self.text)
259:         assert match, f"AcceptanceCriterion: expected heading 'AC-NNN (Method): <text>', got {self.text!r}"
260:         result: int = int(match.group(1))
261:         return result
262: 
263:     @computed_field  # type: ignore
264:     @property
265:     def method(self) -> str:
266:         """The closed DTAIS method word carried by this heading (e.g. `"Test"` for `### AC-001 (Test): ...`).
267: 
268:         Returns:
269:             The method word parsed from the retained heading text, exactly
270:             as written (not lowercased/normalized).
271: 
272:         Raises:
273:             AssertionError: the retained heading text does not match
274:                 `AcceptanceCriterion`'s declared `@alias` (unreachable via
275:                 the engine: `match_alias` already enforced it at parse time).
276:         """
277:         match = _AC_HEADING_RE.fullmatch(self.text)
278:         assert match, f"AcceptanceCriterion: expected heading 'AC-NNN (Method): <text>', got {self.text!r}"
279:         result: str = match.group(2)
280:         return result
281: 
282: 
283: @alias(value="Acceptance Criteria", type=AliasType.LITERAL)
284: class AcceptanceCriteria(MarkdownSection2):
285:     """`## Acceptance Criteria` -- the dynamic `### AC-NNN (Method): ...` collection. Mandatory.
286: 
287:     Requires at least one entry (``min_length=1``, REQ-003) -- an H2 with
288:     zero criteria is a structural error.
289: 
290:     Parameters
291:     ----------
292:     criteria:
293:         The `### AC-NNN (Method): <criterion text>` entries, in document
294:         order. Must contain at least one entry.
295:     """
296: 
297:     criteria: list[AcceptanceCriterion] = Field(
298:         min_length=1,
299:         description="Dynamic collection of `### AC-NNN (Method): <criterion text>` entries, in document order. "
300:         "Must contain at least one entry.",
301:     )
302: 
303: 
304: class MoreInformation(MarkdownSection2):
305:     """`## More Information` -- free-form optional supplementary text, no fixed format. Optional."""
306: 
307: 
308: @alias(value=".+", type=AliasType.REGEX)
309: class UpdateEntry(MarkdownSection3):
310:     """`### {free-form title}` under `## Updates` -- one update entry.
311: 
312:     The H3 heading text is free-form (date-led titles like
313:     `2026-08-31 — Created` are convention, not enforced). Mirrors DEC's
314:     `UpdateEntry` shape.
315: 
316:     Parameters
317:     ----------
318:     content:
319:         The lead paragraph right after the H3 heading -- this entry's own
320:         update text. Mandatory.
321:     """
322: 
323:     content: MarkdownParagraph = Field(
324:         description="The lead paragraph directly under the H3 heading -- this entry's own update text. Mandatory."
325:     )
326: 
327: 
328: class Updates(MarkdownSection2WithComment):
329:     """`## Updates` -- a dynamic list of free-form-titled `### ` update entries. Optional as a whole, and the
330:     last section of the document if present.
331: 
332:     Unlike DEC's own `Updates` (a plain `MarkdownSection2`, since
333:     `dec_example.md` carries no comment there), VCR's own `example.md`/
334:     `template.md` (Phase 0) both demonstrate a permanent "newest first"
335:     ordering-hint HTML comment directly under this heading -- the same
336:     structural-anchor role `feat`'s `Updates(MarkdownSection3WithComment)`
337:     already gives its own comment (not authoring guidance, see
338:     `.specmgr/feat/feat-33-vcr/README.md` Design Notes' "clean-example
339:     convention" bullet), so this is `MarkdownSection2WithComment` instead.
340:     No dedicated per-entry tools -- entries are appended by editing the
341:     whole body.
342: 
343:     Parameters
344:     ----------
345:     comment:
346:         Optional explanatory HTML comment (`<!-- ... -->`), e.g.
347:         `<!-- Newest entry first -- prepend new entries directly below
348:         this comment. -->`. Inherited from `MarkdownSection2WithComment`.
349:     updates:
350:         The dynamic collection of `### ` entries, in document order. Requires
351:         at least one entry (``min_length=1``) -- an H2 with zero entries is
352:         a structural error.
353:     """
354: 
355:     updates: list[UpdateEntry] = Field(
356:         min_length=1,
357:         description="Dynamic collection of `### {free-form title}` entries, in document order. "
358:         "Must contain at least one entry.",
359:     )
360: 
361: 
362: @alias(value=".+", type=AliasType.REGEX)
363: class Vcr(MarkdownSection1WithComment):
364:     """The `vcr` body: a single H1 section with the fields below.
365: 
366:     The H1 heading text is free-form. `comment` is inherited from
367:     `MarkdownSection1WithComment` (see its own docstring) -- not redeclared
368:     here.
369: 
370:     Parameters
371:     ----------
372:     comment:
373:         Optional explanatory HTML comment (`<!-- ... -->`) preceding
374:         `verifies`. Inherited from `MarkdownSection1WithComment`.
375:     verifies:
376:         `## Verifies` (exactly one REQ/UC cross-reference). Mandatory.
377:     coverage:
378:         `## Coverage` (closed 3-value set). Mandatory.
379:     acceptance_criteria:
380:         `## Acceptance Criteria` (>=1 `### AC-NNN (Method): ...` entry).
381:         Mandatory.
382:     more_information:
383:         `## More Information`. Optional.
384:     updates:
385:         `## Updates`. Optional; last section.
386:     """
387: 
388:     verifies: Verifies = Field(description="`## Verifies` section. Mandatory.")
389:     coverage: Coverage = Field(description="`## Coverage` section. Mandatory.")
390:     acceptance_criteria: AcceptanceCriteria = Field(
391:         description="`## Acceptance Criteria` section (>=1 entry). Mandatory."
392:     )
393:     more_information: MoreInformation | None = Field(
394:         default=None, description="`## More Information` section. Optional."
395:     )
396:     updates: Updates | None = Field(default=None, description="`## Updates` section. Optional; last.")
397: 
398:     @model_validator(mode="after")
399:     def _validate_ac_numbers_unique(self) -> Vcr:
400:         """Reject duplicate AC numbers across `## Acceptance Criteria`.
401: 
402:         `AcceptanceCriterion.number`/`.method` are `@computed_field`s --
403:         Pydantic only evaluates a computed field's getter on access (e.g.
404:         during `model_dump()`/serialization), never during construction/
405:         validation of the underlying model itself. Accessing `.number` here
406:         therefore both forces every criterion's number to evaluate eagerly
407:         and checks the cross-field invariant: no two criteria may carry the
408:         same number (`### AC-001` and a hypothetical second `### AC-001`
409:         are the same number and therefore a duplicate). Gaps are allowed
410:         (criteria are never renumbered). A duplicate raises `ValueError`,
411:         which Pydantic channels into `ValidationError` -- mirrors DEC's
412:         `Decision._validate_option_numbers_unique` exactly, except
413:         `acceptance_criteria` is mandatory here (unlike DEC's optional
414:         `pros_and_cons`), so no `is not None` guard is needed.
415:         """
416:         seen: set[int] = set()
417:         for criterion in self.acceptance_criteria.criteria:
418:             number = criterion.number
419:             if number in seen:
420:                 raise ValueError(f"AC number {number} is used by more than one `### AC-NNN` heading")
421:             seen.add(number)
422:         return self

(End of file - total 422 lines)
</content>
````

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.2s)

This is high-quality, well-reasoned code. Let me run the quality gate independently.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo \"===check===\" && uv run --frozen ruff check 2>&1 | tail -10 && echo \"===vulture===\" && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -20"
}
```

**Output:**

```
1308 files already formatted
===check===
All checks passed!
===vulture===

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.6s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen python -m unittest discover -v -s tests/vcr -t . -p \"test_*.py\" 2>&1 | tail -30"
}
```

**Output:**

```
A missing mandatory `## Verifies` is a structural failure. ... ok
test_nonblank_leading_content_before_h1_raises_assertion_error (tests.vcr.models.v1.test_parser.TestParseVcrStructuralViolations.test_nonblank_leading_content_before_h1_raises_assertion_error)
Non-blank content before the H1 is a structural failure. ... ok
test_second_h1_raises_assertion_error (tests.vcr.models.v1.test_parser.TestParseVcrStructuralViolations.test_second_h1_raises_assertion_error)
A second H1 is a structural failure. ... ok
test_test_steps_with_zero_items_raises_assertion_error (tests.vcr.models.v1.test_parser.TestParseVcrStructuralViolations.test_test_steps_with_zero_items_raises_assertion_error)
A `#### Test Steps` present with zero items is a structural failure. ... ok
test_unknown_h2_raises_assertion_error (tests.vcr.models.v1.test_parser.TestParseVcrStructuralViolations.test_unknown_h2_raises_assertion_error)
An H2 heading no field claims is a structural failure. ... ok
test_updates_before_more_information_raises_assertion_error (tests.vcr.models.v1.test_parser.TestParseVcrStructuralViolations.test_updates_before_more_information_raises_assertion_error)
Misordering: `## Updates` must come after `## More Information`. ... ok
test_ac_number_and_method_computed (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_ac_number_and_method_computed)
`AcceptanceCriterion.number`/`.method` are computed from the heading. ... ok
test_coverage_outside_closed_set_raises_validation_error (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_coverage_outside_closed_set_raises_validation_error)
A `## Coverage` value outside `full`/`partial`/`none` fails validation. ... ok
test_dec_only_accepted_status_raises_validation_error (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_dec_only_accepted_status_raises_validation_error)
`accepted` belongs to DEC's six-value set, not VCR's four. ... ok
test_duplicate_ac_number_raises_validation_error (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_duplicate_ac_number_raises_validation_error)
Two `### AC-001` headings fail the `Vcr` after-validator. ... ok
test_status_outside_closed_set_raises_validation_error (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_status_outside_closed_set_raises_validation_error)
A frontmatter `status` outside VcrFrontmatter's closed four-set fails validation. ... ok
test_type_other_than_vcr_raises_validation_error (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_type_other_than_vcr_raises_validation_error)
A frontmatter `type` other than `vcr` fails validation. ... ok
test_verifies_value_with_unknown_type_tag_raises_validation_error (tests.vcr.models.v1.test_parser.TestParseVcrValueViolations.test_verifies_value_with_unknown_type_tag_raises_validation_error)
A `## Verifies` value tagged with something other than `REQ`/`UC` fails validation. ... ok

----------------------------------------------------------------------
Ran 108 tests in 1.779s

OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.8s)

Let me independently confirm the corrected schema now parses `example.md`/`template.md` directly, and run the full suite once more.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen python -c \"\nfrom biz.dfch.specmgr.vcr.models.v1.parser import parse_vcr\nfor p in ['.specmgr/feat/feat-33-vcr/example.md', '.specmgr/feat/feat-33-vcr/template.md']:\n    text = open(p, encoding='utf-8').read()\n    doc = parse_vcr(text)\n    print(p, '-> OK', doc.frontmatter.status, doc.body.coverage.value.text, len(doc.body.acceptance_criteria.criteria))\n\"\n"
}
```

**Output:**

```
.specmgr/feat/feat-33-vcr/example.md -> OK progress partial 4
.specmgr/feat/feat-33-vcr/template.md -> OK draft partial 2

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 123.2s)

Confirmed independently. Now the full test suite.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen coverage run -m unittest discover -v -s tests -t . -p \"test_*.py\" 2>&1 | tail -5"
}
```

**Output:**

```
(no output)

<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 113.9s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && timeout 280 uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" 2>&1 | tail -15",
  "timeout": 290000
}
```

**Output:**

```
'
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content', '']
['### Sec3 only', '', 'content', 'more content']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '', '#### Nested', '', 'more']
['### Sec3', '', 'content', '', '##### Nested', '', 'more']
['### Sec3', '', 'content', '', '###### Nested', '', 'more']
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content']
[]
['### Sec3', '', 'content', '']


[0] # Title

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 108.7s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && timeout 280 uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/full_test_run.log 2>&1; echo \"EXIT:$?\"; tail -20 /tmp/full_test_run.log",
  "timeout": 290000
}
```

**Output:**

```
EXIT:0
2. This is another list item

3. ~Another~ item

This is the outro of the document.
'
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content', '']
['### Sec3 only', '', 'content', 'more content']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '']
['### Sec3', '', 'content', '', '#### Nested', '', 'more']
['### Sec3', '', 'content', '', '##### Nested', '', 'more']
['### Sec3', '', 'content', '', '###### Nested', '', 'more']
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content']
[]
['### Sec3', '', 'content', '']


[0] # Title

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"Ran [0-9]* tests\\|^OK\\|FAILED\" /tmp/full_test_run.log"
}
```

**Output:**

```
9:Ran 2336 tests in 102.781s
11:OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.7s)

All green: 2336 tests pass, ruff/vulture clean, and both `example.md`/`template.md` now empirically validate against the corrected schema. Phase 1 verified. Let me review the README diff and commit.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff --stat"
}
```

**Output:**

```
 .specmgr/feat/feat-33-vcr/README.md | 191 +++++++++++++++++++++++++++++++-----
 whitelist.py                        |   5 +
 2 files changed, 173 insertions(+), 23 deletions(-)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.3s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff whitelist.py"
}
```

**Output:**

```
diff --git a/whitelist.py b/whitelist.py
index 803962c..c10013b 100644
--- a/whitelist.py
+++ b/whitelist.py
@@ -46,6 +46,7 @@ _._optional_blank_to_none
 _._required_non_blank
 _._validate_items_eagerly
 _._validate_newest_first
+_._validate_ac_numbers_unique
 _._validate_option_numbers_unique
 _._validate_partial_title
 _._validate_status
@@ -168,6 +169,10 @@ current_status
 blockers
 decisions_made
 related_prs_commits
+# vcr (feat-33 Phase 1): `Vcr`/`AcceptanceCriterion` fields read only via
+# (de)serialization; nothing in `src/` accesses them as plain attributes yet.
+verifies
+test_steps
 
 # --- MCP `@mcp.resource(...)`/`@mcp.tool()` entry points -------------------------
 # Invoked by the MCP framework once registered, not called directly in `src/`.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

This matches the existing precedent exactly (mirrors the `dec` comment pattern). Everything checks out. Committing Phase 1.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add src/biz/dfch/specmgr/vcr tests/vcr whitelist.py .specmgr/feat/feat-33-vcr/README.md && git status --short"
}
```

**Output:**

```
M  .specmgr/feat/feat-33-vcr/README.md
A  src/biz/dfch/specmgr/vcr/__init__.py
A  src/biz/dfch/specmgr/vcr/models/__init__.py
A  src/biz/dfch/specmgr/vcr/models/v1/__init__.py
A  src/biz/dfch/specmgr/vcr/models/v1/_util.py
A  src/biz/dfch/specmgr/vcr/models/v1/body.py
A  src/biz/dfch/specmgr/vcr/models/v1/document.py
A  src/biz/dfch/specmgr/vcr/models/v1/frontmatter.py
A  src/biz/dfch/specmgr/vcr/models/v1/parser.py
A  src/biz/dfch/specmgr/vcr/models/v1/summary.py
A  tests/vcr/__init__.py
A  tests/vcr/models/__init__.py
A  tests/vcr/models/v1/__init__.py
A  tests/vcr/models/v1/test_body.py
A  tests/vcr/models/v1/test_frontmatter.py
A  tests/vcr/models/v1/test_parser.py
M  whitelist.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 126.2s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr/models/v1 schema, parser, and unit tests (Phase 1)\" -m \"VcrFrontmatter (closed draft/progress/complete/approved status), and\nbody models: Verifies (single-value REQ|UC cross-reference + mandatory\nnotes), Coverage (full/partial/none), AcceptanceCriterion/\nAcceptanceCriteria (### AC-NNN (Method): ... with DTAIS closed vocabulary,\noptional description + optional #### Test Steps, duplicate-number\nmodel_validator), MoreInformation, Updates. VcrDocument/parse_vcr/\nVcrSummary mirror dec's shape. 108 new tests; example.md/template.md now\nempirically parse end to end against this schema.\n\nNo tools/resources/prompts/server.py registration yet (Phase 2-4).\""
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................

<shell_metadata>
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
</shell_metadata>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.0s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git log --oneline -3 && echo \"---status---\" && git status --short"
}
```

**Output:**

```
9984847 docs(feat-33-vcr): draft template.md, confirm AC-NNN regex/duplicate check (Phase 0)
28bd472 docs(feat-33): Verification Case Record (vcr)
22f8f86 docs(feat-33): add session transcript "design"
---status---
M  .specmgr/feat/feat-33-vcr/README.md
A  src/biz/dfch/specmgr/vcr/__init__.py
A  src/biz/dfch/specmgr/vcr/models/__init__.py
A  src/biz/dfch/specmgr/vcr/models/v1/__init__.py
A  src/biz/dfch/specmgr/vcr/models/v1/_util.py
A  src/biz/dfch/specmgr/vcr/models/v1/body.py
A  src/biz/dfch/specmgr/vcr/models/v1/document.py
A  src/biz/dfch/specmgr/vcr/models/v1/frontmatter.py
A  src/biz/dfch/specmgr/vcr/models/v1/parser.py
A  src/biz/dfch/specmgr/vcr/models/v1/summary.py
A  tests/vcr/__init__.py
A  tests/vcr/models/__init__.py
A  tests/vcr/models/v1/__init__.py
A  tests/vcr/models/v1/test_body.py
A  tests/vcr/models/v1/test_frontmatter.py
A  tests/vcr/models/v1/test_parser.py
M  whitelist.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

Commit did not complete (pre-commit's coverage-run timed out under the tool's 120s limit, but the process may still be running in background or got killed). Let's check and retry with a longer timeout.

**Tool: bash**

**Input:**

```json
{
  "command": "ps aux | grep -i \"coverage run\\|unittest\" | grep -v grep"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 226.7s)

No leftover process — it was killed. Re-running the commit with a longer timeout.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr/models/v1 schema, parser, and unit tests (Phase 1)\" -m \"VcrFrontmatter (closed draft/progress/complete/approved status), and\nbody models: Verifies (single-value REQ|UC cross-reference + mandatory\nnotes), Coverage (full/partial/none), AcceptanceCriterion/\nAcceptanceCriteria (### AC-NNN (Method): ... with DTAIS closed vocabulary,\noptional description + optional #### Test Steps, duplicate-number\nmodel_validator), MoreInformation, Updates. VcrDocument/parse_vcr/\nVcrSummary mirror dec's shape. 108 new tests; example.md/template.md now\nempirically parse end to end against this schema.\n\nNo tools/resources/prompts/server.py registration yet (Phase 2-4).\"",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Failed
- hook id: specmgr-docs
- exit code: 1
- files were modified by this hook

✓ Wrote 372 module file(s) to /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/GENERATED.md
diff --git a/docs/GENERATED.md b/docs/GENERATED.md
index 450b6ea..12eff1b 100644
--- a/docs/GENERATED.md
+++ b/docs/GENERATED.md
@@ -425,6 +425,18 @@ First-line docstrings from each module, organized by domain:
 - `uc/tools/parse_uc.py` — ``@mcp.tool()`` wrapper: parse_uc.
 - `uc/tools/validate_uc.py` — ``@mcp.tool()`` wrapper: validate_uc (Task 3.1.5).
 
+**vcr/**
+
+- `vcr/__init__.py` — Verification Case Record (VCR) domain -- how a REQ/UC is verified.
+- `vcr/models/__init__.py` — Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.
+- `vcr/models/v1/__init__.py` — Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.
+- `vcr/models/v1/_util.py` — Shared, private constants for the ``vcr.models.v1`` subpackage.
+- `vcr/models/v1/body.py` — Verification Case Record (VCR) body models: whole-section fields under a single H1.
+- `vcr/models/v1/document.py` — Pydantic model for a full verification case record document (frontmatter + body).
+- `vcr/models/v1/frontmatter.py` — Verification Case Record (VCR) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
+- `vcr/models/v1/parser.py` — Parse raw verification case record (VCR) ``.md`` text into a :class:`VcrDocument`.
+- `vcr/models/v1/summary.py` — Pydantic model for one line of VCR listing output (Phase 2, ``list_vcr``).
+
 ## Test Coverage
 
-**Test files**: 283
+**Test files**: 286
diff --git a/docs/api/README.md b/docs/api/README.md
index 934084d..8412f2a 100644
--- a/docs/api/README.md
+++ b/docs/api/README.md
@@ -369,3 +369,12 @@ Auto-generated API documentation for `biz.dfch.specmgr`.
 - [`biz.dfch.specmgr.uc.tools.list_uc`](biz.dfch.specmgr.uc.tools.list_uc.md) — ``@mcp.tool()`` wrapper: list_uc (feat-13-list-paging Task 2.3).
 - [`biz.dfch.specmgr.uc.tools.parse_uc`](biz.dfch.specmgr.uc.tools.parse_uc.md) — ``@mcp.tool()`` wrapper: parse_uc.
 - [`biz.dfch.specmgr.uc.tools.validate_uc`](biz.dfch.specmgr.uc.tools.validate_uc.md) — ``@mcp.tool()`` wrapper: validate_uc (Task 3.1.5).
+- [`biz.dfch.specmgr.vcr`](biz.dfch.specmgr.vcr.md) — Verification Case Record (VCR) domain -- how a REQ/UC is verified.
+- [`biz.dfch.specmgr.vcr.models`](biz.dfch.specmgr.vcr.models.md) — Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.
+- [`biz.dfch.specmgr.vcr.models.v1`](biz.dfch.specmgr.vcr.models.v1.md) — Verification Case Record (VCR) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.
+- [`biz.dfch.specmgr.vcr.models.v1._util`](biz.dfch.specmgr.vcr.models.v1._util.md) — Shared, private constants for the ``vcr.models.v1`` subpackage.
+- [`biz.dfch.specmgr.vcr.models.v1.body`](biz.dfch.specmgr.vcr.models.v1.body.md) — Verification Case Record (VCR) body models: whole-section fields under a single H1.
+- [`biz.dfch.specmgr.vcr.models.v1.document`](biz.dfch.specmgr.vcr.models.v1.document.md) — Pydantic model for a full verification case record document (frontmatter + body).
+- [`biz.dfch.specmgr.vcr.models.v1.frontmatter`](biz.dfch.specmgr.vcr.models.v1.frontmatter.md) — Verification Case Record (VCR) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
+- [`biz.dfch.specmgr.vcr.models.v1.parser`](biz.dfch.specmgr.vcr.models.v1.parser.md) — Parse raw verification case record (VCR) ``.md`` text into a :class:`VcrDocument`.
+- [`biz.dfch.specmgr.vcr.models.v1.summary`](biz.dfch.specmgr.vcr.models.v1.summary.md) — Pydantic model for one line of VCR listing output (Phase 2, ``list_vcr``).

specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.6s)

_Thinking:_

The `specmgr-docs` hook auto-regenerated `docs/api/` and `docs/GENERATED.md` — I'll stage those and re-commit, per the standard formatter-hook UX.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add docs/ && git status --short | head -20"
}
```

**Output:**

```
M  .specmgr/feat/feat-33-vcr/README.md
M  docs/GENERATED.md
M  docs/api/README.md
A  docs/api/biz.dfch.specmgr.vcr.md
A  docs/api/biz.dfch.specmgr.vcr.models.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1._util.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1.body.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1.document.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1.frontmatter.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1.parser.md
A  docs/api/biz.dfch.specmgr.vcr.models.v1.summary.md
A  src/biz/dfch/specmgr/vcr/__init__.py
A  src/biz/dfch/specmgr/vcr/models/__init__.py
A  src/biz/dfch/specmgr/vcr/models/v1/__init__.py
A  src/biz/dfch/specmgr/vcr/models/v1/_util.py
A  src/biz/dfch/specmgr/vcr/models/v1/body.py
A  src/biz/dfch/specmgr/vcr/models/v1/document.py
A  src/biz/dfch/specmgr/vcr/models/v1/frontmatter.py
A  src/biz/dfch/specmgr/vcr/models/v1/parser.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 212.7s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr/models/v1 schema, parser, and unit tests (Phase 1)\" -m \"VcrFrontmatter (closed draft/progress/complete/approved status), and\nbody models: Verifies (single-value REQ|UC cross-reference + mandatory\nnotes), Coverage (full/partial/none), AcceptanceCriterion/\nAcceptanceCriteria (### AC-NNN (Method): ... with DTAIS closed vocabulary,\noptional description + optional #### Test Steps, duplicate-number\nmodel_validator), MoreInformation, Updates. VcrDocument/parse_vcr/\nVcrSummary mirror dec's shape. 108 new tests; example.md/template.md now\nempirically parse end to end against this schema.\n\nIncludes docs/api + docs/GENERATED.md regenerated by the specmgr-docs\npre-commit hook.\n\nNo tools/resources/prompts/server.py registration yet (Phase 2-4).\"",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[feat-33-vcr c574949] feat(feat-33-vcr): add vcr/models/v1 schema, parser, and unit tests (Phase 1)
 28 files changed, 10322 insertions(+), 24 deletions(-)
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1._util.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1.body.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1.document.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1.frontmatter.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1.parser.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.models.v1.summary.md
 create mode 100644 src/biz/dfch/specmgr/vcr/__init__.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/__init__.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/__init__.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/_util.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/body.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/document.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/frontmatter.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/parser.py
 create mode 100644 src/biz/dfch/specmgr/vcr/models/v1/summary.py
 create mode 100644 tests/vcr/__init__.py
 create mode 100644 tests/vcr/models/__init__.py
 create mode 100644 tests/vcr/models/v1/__init__.py
 create mode 100644 tests/vcr/models/v1/test_body.py
 create mode 100644 tests/vcr/models/v1/test_frontmatter.py
 create mode 100644 tests/vcr/models/v1/test_parser.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.2s)

Phase 1 committed. Moving to Phase 2.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && for f in _paths _lock _io _write create_dec parse_dec get_dec get_dec_example get_dec_template list_dec delete_dec validate_dec __init__; do echo \"=== dec/tools/$f.py ===\"; cat \"src/biz/dfch/specmgr/dec/tools/$f.py\"; echo; done"
}
```

**Output:**

```
=== dec/tools/_paths.py ===
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

"""Decision base directory resolution and id -> path lookup (Task 2.1).

A thin, decision-specific layer over the generic ``general.tools._doc_paths``
module, rather than a second hand-written copy of ``gol.tools._paths``/
``prb.tools._paths`` -- the base-directory/id-lookup plumbing is identical in
shape, only the parsed document type and its id accessor differ. Mirrors
``gol.tools._paths`` file-for-file.

Mirrors ``gol.tools._paths``'s read-only/write split: :func:`dec_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_dec_base_dir` does, for ``create_dec``. There is
deliberately no in-memory id -> path cache either -- every lookup re-scans
the base directory and re-parses each file, matching this codebase's "the
on-disk file is the sole source of truth" design.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ...general.tools._doc_paths import (
    DocNotFoundError,
    doc_base_dir,
    ensure_doc_base_dir,
    find_doc_path_by_id,
    iter_doc_paths,
)
from ..models.v1 import DecDocument, parse_dec

__all__ = [
    "DEC_TYPE_NAME",
    "DecNotFoundError",
    "dec_base_dir",
    "ensure_dec_base_dir",
    "find_dec_path",
    "iter_dec_paths",
]

#: The doc-type subdirectory name passed to ``general.tools._doc_paths``
#: (``{docs root}/dec/``, e.g. ``docs/dec``).
DEC_TYPE_NAME = "dec"


class DecNotFoundError(LookupError):
    """No decision file found matching the given id.

    A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
    a subclass of it -- the same relationship ``gol.tools._paths.GolNotFoundError``
    has to nothing generic, so callers can keep catching a decision-specific
    exception type without depending on the generic module's own exception.
    """


def dec_base_dir() -> Path:
    """Return the configured decision base directory, without creating it.

    Thin wrapper over ``general.tools._doc_paths.doc_base_dir(DEC_TYPE_NAME)``
    -- see that function's own docstring for the env var/default it reads.

    Returns
    -------
    Path
        The resolved decision base directory.
    """
    result = doc_base_dir(DEC_TYPE_NAME)
    return result


def ensure_dec_base_dir() -> Path:
    """Return the configured decision base directory, creating it if missing.

    Only ``create_dec`` should call this -- every other tool/resource uses
    the read-only :func:`dec_base_dir` instead.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist decision base directory.
    """
    result = ensure_doc_base_dir(DEC_TYPE_NAME)
    return result


def iter_dec_paths() -> Iterator[Path]:
    """Yield every decision ``*.md`` file under :func:`dec_base_dir`, sorted by name.

    Yields nothing (rather than raising) if the base directory does not exist.

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    result = iter_doc_paths(dec_base_dir())
    return result


def _get_dec_id(doc: DecDocument) -> str | None:
    """Extract the id from a parsed :class:`DecDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
    result = doc.frontmatter.id
    return result


def find_dec_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path under ``base_dir``.

    Scans every ``*.md`` file under ``base_dir``, parsing each via
    :func:`~biz.dfch.specmgr.dec.models.v1.parse_dec` and comparing
    ``frontmatter.id`` against ``id_``. A file that fails to parse
    (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
    one broken file must not prevent lookup of a different, valid id.
    Mirrors ``gol.tools._paths.find_gol_path``'s own skip-on-parse-failure
    rule.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    Path
        The resolved file path.

    Raises
    ------
    DecNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    try:
        result = find_doc_path_by_id(base_dir, id_, parse_dec, _get_dec_id)
    except DocNotFoundError as ex:
        raise DecNotFoundError(
            f"no decision found with id {id_!r}. The id must be the bare document UUID, without a "
            f"domain prefix (use '<uuid>', not 'dec-<uuid>')."
        ) from ex
    return result

=== dec/tools/_lock.py ===
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

"""Per-document in-process lock guarding decision mutations.

Ported from ``gol.tools._lock.gol_lock`` unchanged except for naming -- see
that module's own docstring for the full rationale (the read-modify-write
race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
to when an MCP host dispatches two overlapping calls against the same id).
The generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="dec"``) wrap their whole sequence in ``with dec_lock(id):``.

Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id
-> path lookup plumbing was generalized because it was already shared,
read-only, dependency-light code; a lock, by contrast, is a mutation-time
correctness primitive. Kept as its own small, DEC-specific module, mirroring
GOL/PRB/REQ's own non-generalized precedent; migrating all of them onto one
shared module remains optional future cleanup.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

__all__ = ["dec_lock"]

#: Guards creation of/lookup into `_locks` -- held only for the instant it
#: takes to get-or-create a per-id lock, never for the duration of a
#: mutation itself.
_registry_lock = threading.Lock()

#: One lock per decision id, created lazily on first use and never
#: removed -- the id space is small and long-lived relative to a server
#: process's lifetime, so there is no meaningful growth/cleanup concern here.
_locks: dict[str, threading.Lock] = {}


def _lock_for(id_: str) -> threading.Lock:
    """Return the (lazily created) lock instance for ``id_``."""
    with _registry_lock:
        lock = _locks.get(id_)
        if lock is None:
            lock = threading.Lock()
            _locks[id_] = lock
        return lock


@contextmanager
def dec_lock(id_: str) -> Iterator[None]:
    """Serialize the read-modify-write mutation sequence for decision ``id_``.

    Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
    sequence in ``with dec_lock(id):`` so two concurrent calls targeting the
    same id run one after another instead of interleaving, preventing the
    lost-update race described in this module's docstring.
    """
    lock = _lock_for(id_)
    with lock:
        yield

=== dec/tools/_io.py ===
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

"""Thin file read helpers over ``parse_dec`` (Task 2.1).

Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
is no ``write_dec``/``render_dec`` counterpart here, since ``create_dec``
and the generic ``update`` tool in ``general.tools`` persist the caller's
own already-validated body markdown byte-for-byte rather than rendering it
back out from a parsed model -- no
renderer is needed for that shape, so none is added speculatively here.
Mirrors ``gol.tools._io`` file-for-file.

No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
separate from any future ``@mcp.tool()``-decorated function so they stay
independently testable.
"""

from __future__ import annotations

from pathlib import Path

from ..models.v1 import DecDocument, parse_dec
from ._paths import find_dec_path

__all__ = ["load_by_id", "read_dec"]


def read_dec(path: Path) -> DecDocument:
    """Read and parse the decision at ``path``.

    Parameters
    ----------
    path:
        The filesystem path to the decision ``.md`` file.

    Returns
    -------
    DecDocument
        The parsed, validated document.
    """
    assert isinstance(path, Path), type(path)

    result = parse_dec(path.read_text(encoding="utf-8"))
    return result


def load_by_id(base_dir: Path, id_: str) -> tuple[Path, DecDocument]:
    """Resolve ``id_`` under ``base_dir`` and read the matching decision.

    Parameters
    ----------
    base_dir:
        The directory to scan for ``*.md`` files.
    id_:
        The id to look up.

    Returns
    -------
    tuple[Path, DecDocument]
        The resolved file path and the parsed document -- callers that
        mutate the document need the path to write it back afterward.

    Raises
    ------
    DecNotFoundError
        If no file matches (propagated from :func:`._paths.find_dec_path`).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = find_dec_path(base_dir, id_)
    result = (path, read_dec(path))
    return result

=== dec/tools/_write.py ===
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

"""Shared frontmatter+body composition/write helper for ``create_dec`` and
the generic ``update`` tool in ``general.tools`` (``type="dec"``).

Deliberately **not** part of ``dec.tools._io`` -- that module's own docstring
rules out a ``write_dec``/``render_dec`` counterpart to ``read_dec``, since
neither ``create_dec`` nor the generic ``update`` tool in ``general.tools``
ever render a body back out from a
parsed :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument` model. What
:func:`write_dec_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.dec.models.v1.DecFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_dec.py`` into its own module so the generic
``update`` and ``set_status`` tools in ``general.tools`` (``type="dec"``)
do not have to duplicate it. Mirrors ``gol.tools._write`` file-for-file.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from ..models.v1 import DecFrontmatter

__all__ = ["write_dec_file"]


def write_dec_file(path: Path, frontmatter_: DecFrontmatter, content: str) -> None:
    """Compose a full decision file (frontmatter + body) and write it to ``path``.

    ``content`` is embedded verbatim -- it is never reformatted/re-rendered
    here. One caveat inherent to the underlying ``python-frontmatter``
    library, not specially handled here: its ``YAMLHandler`` strips trailing
    whitespace from ``content`` when serializing, so the written body may
    differ from ``content`` by trailing whitespace only, never in substance.

    Parameters
    ----------
    path:
        The destination file path.
    frontmatter_:
        The already-constructed, already-validated frontmatter to serialize
        as the file's YAML block.
    content:
        The raw body markdown, exactly as submitted by the caller.
    """
    post = frontmatter.Post(content=content, **frontmatter_.model_dump())
    text = frontmatter.dumps(post)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")

=== dec/tools/create_dec.py ===
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

"""``@mcp.tool()`` wrapper: create_dec (Task 2.2).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_dec`` accepts
**body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``gol.tools.create_gol`` file-for-file.

Thin file-I/O adapter; there is no in-memory cache of a parsed
:class:`~biz.dfch.specmgr.dec.models.v1.DecDocument` -- the ``.md`` file
itself is always the source of truth, matching every other tool in this
codebase.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from ...general.tools._doc_paths import slugify
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import DecDocument, DecFrontmatter, Decision
from ._paths import ensure_dec_base_dir
from ._write import write_dec_file


@mcp.tool(
    name="create_dec",
    title="Create decision",
    description=(
        "Create a new decision: assigns a fresh id, derives a filename from the body's "
        "H1 title, validates the submitted body-only content, and writes the new "
        "document to the decision base directory."
    ),
)
def create_dec(content: str) -> DecDocument:
    """Create and write a new decision document.

    ``content`` is body markdown only (the ``Decision`` H1 and its sections)
    -- it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh id (``uuid.uuid4()``), ``type="dec"``,
    ``status="draft"`` (always, never caller-supplied on create),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.dec.models.v1.Decision` from it
    (``Decision.from_text(format_text(content))``); a structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError``, both uncaught -- nothing is written in
    either case.

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block.

    Returns
    -------
    DecDocument
        The newly created document, with its assigned id in
        ``frontmatter.id``.
    """
    body = Decision.from_text(format_text(content))

    new_id = str(uuid.uuid4())
    now = datetime.now().isoformat(timespec="microseconds")
    new_frontmatter = DecFrontmatter(
        id=new_id,
        type="dec",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    new_doc = DecDocument(frontmatter=new_frontmatter, body=body)

    filename = f"dec-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_dec_base_dir()
    write_dec_file(base_dir / filename, new_frontmatter, content)
    return new_doc

=== dec/tools/parse_dec.py ===
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

"""``@mcp.tool()`` wrapper: parse_dec (Task 2.2).

Reads a decision markdown file from disk and parses it into a structured
:class:`DecDocument`, mirroring ``gol.tools.parse_gol``'s own pattern --
read path → parse via free-function returning typed document model. Errors
(propagated uncaught from the parser's ``AssertionError``/
``pydantic.ValidationError`` or raised by ``Path.read_text()``) surface as
MCP tool errors to the caller.
"""

from __future__ import annotations

from pathlib import Path

from ...server import mcp
from ..models.v1 import DecDocument, parse_dec as _parse_dec


@mcp.tool(
    name="parse_dec",
    title="Parse decision",
    description=(
        "Parse a decision markdown file (YAML frontmatter + body) from disk "
        "into a structured :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument`."
    ),
)
def parse_dec(path: str) -> DecDocument:
    """Parse the decision file at ``path`` into a :class:`DecDocument`.

    Reads the file from disk, then parses and validates its content. "Parse"
    here also means "validate": letting :class:`Decision` /
    :class:`DecFrontmatter` / :class:`DecDocument`'s own Pydantic validators
    run during parsing is the only validation pass there is -- there is
    no separate validation step. Any structural problem (unrecognized/misplaced
    heading, list the schema doesn't expect) or field/cross-field validation
    failure is not caught or wrapped here: it propagates naturally as
    ``AssertionError``/``pydantic.ValidationError``, so the MCP layer reports
    it as a tool error with the underlying message, giving the caller something
    concrete to self-correct from.  Similarly, file-access errors migrate as
    ``FileNotFoundError``/``PermissionError``/``OSError``.

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to parse (absolute or
        relative to the current working directory).

    Returns
    -------
    DecDocument
        The parsed, validated document.
    """
    text = Path(path).read_text(encoding="utf-8")
    return _parse_dec(text)

=== dec/tools/get_dec.py ===
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

"""``@mcp.tool()`` wrapper: get_dec (Task 2.2).

Mirrors ``gol.tools.get_gol`` -- a thin file-I/O/id-lookup adapter that
re-reads and re-parses the current on-disk state on every call; there is no
in-memory cache of a parsed :class:`DecDocument`: the ``.md`` file itself is
always the source of truth.

This tool is the sole id-based read path for DEC: there is no
``specmgr://dec/{id}`` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614,
same reasoning as GOL/REQ/UC/TSK/QA/PRB's own ``get_*`` tools).

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 8) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against.
"""

from __future__ import annotations

from ...general.tools._splice import body_text
from ...server import mcp
from ..models.v1 import DecDocument
from ._io import load_by_id
from ._paths import dec_base_dir


@mcp.tool(
    name="get_dec",
    title="Get decision",
    description=(
        "Read, parse, and return a full decision document (frontmatter and body) by its id. "
        "Pass raw=True to return the frontmatter-stripped body text verbatim instead."
    ),
)
def get_dec(id: str, raw: bool = False) -> DecDocument | str:
    """Read and return the decision identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    raw:
        With ``False`` (the default), return the parsed document, exactly
        as before. With ``True``, return the frontmatter-stripped body
        text verbatim as a plain string -- the same text whose 1-based
        lines the generic ``update`` tool's ``begin``/``end`` coordinates
        address (shared body-extraction helper with the splice).

    Returns
    -------
    DecDocument | str
        With ``raw=False``: the current on-disk document, freshly re-read
        and re-parsed. With ``raw=True``: the body text as a plain string.
        Raises :class:`._paths.DecNotFoundError` if no decision has this id.
    """
    base_dir = dec_base_dir()
    path, doc = load_by_id(base_dir, id)
    if raw:
        result: DecDocument | str = body_text(path)
        return result
    result = doc
    return result

=== dec/tools/get_dec_example.py ===
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

"""``@mcp.tool()`` wrapper: get_dec_example (Task 2.2).

Returns a complete, valid sample decision document as raw markdown -- useful
as a learning example for drafting a new DEC document by hand, or for an LLM
to see the expected shape without re-deriving it from the JSON Schema alone.
Named ``get_dec_example`` rather than the bare ``get_example`` since tool
names are global across the whole MCP server -- domain-qualifying it now
avoids a future collision.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.tool(
    name="get_dec_example",
    title="Get DEC example",
    description=(
        "Return a complete, valid sample decision document as raw markdown -- frontmatter "
        "and body -- exercising every section, for use as a learning example."
    ),
)
def get_dec_example() -> str:
    """Return the packaged DEC example's full markdown text, verbatim.

    The example file is shipped as package data (declared in ``pyproject.toml``'s
    ``[tool.setuptools.package-data]``), so its presence is a build-time
    guarantee, not something that can be missing at runtime in a correctly
    installed package. Reads the file fresh on every call (no in-memory
    cache). A missing or corrupted packaged file is not caught or wrapped
    here -- it propagates as a hard :class:`FileNotFoundError`, the same
    let-it-raise convention every other tool/resource in this codebase
    follows.

    Returns
    -------
    str
        The example document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("dec", "example")

=== dec/tools/get_dec_template.py ===
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

"""``@mcp.tool()`` wrapper: get_dec_template (Task 2.2).

Returns a decision document with every field present, populated with short
placeholder ("blind text") content -- a structural authoring aid for drafting
a new DEC document by hand, distinct from ``get_dec_example``, which returns
a complete, *valid* sample document. Named ``get_dec_template`` rather than
the bare ``get_template``, mirroring ``get_dec_example``'s own
domain-qualified naming rationale -- tool names are global across the whole
MCP server.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.tool(
    name="get_dec_template",
    title="Get DEC template",
    description=(
        "Return a DEC document template -- frontmatter and every body field present, populated "
        "with short placeholder ('blind text') content -- as raw markdown, for use as a starting "
        "point when drafting a new decision."
    ),
)
def get_dec_template() -> str:
    """Return the packaged DEC template's full markdown text, verbatim.

    The template file is shipped as package data (declared in ``pyproject.toml``'s
    ``[tool.setuptools.package-data]``), so its presence is a build-time
    guarantee, not something that can be missing at runtime in a correctly
    installed package. Reads the file fresh on every call (no in-memory
    cache). A missing or corrupted packaged file is not caught or wrapped
    here -- it propagates as a hard :class:`FileNotFoundError`, the same
    let-it-raise convention every other tool/resource in this codebase
    follows.

    Unlike ``get_dec_example``, the returned text is **not** guaranteed to
    satisfy ``parse_dec``/``DecDocument``'s field-level validators -- this
    is a structural authoring aid, not a valid document instance.

    Returns
    -------
    str
        The template document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("dec", "template")

=== dec/tools/list_dec.py ===
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

"""``@mcp.tool()`` wrapper: list_dec (Task 2.2).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13: "Expose ``list_<domain>`` as a paged
MCP tool, not a resource") -- like GOL (another new domain built after that
ADR was accepted), DEC must not repeat the resource-then-convert history of
REQ/UC/TSK/QA/PRB (launched as a ``specmgr://<domain>/list`` resource,
converted later in feat-13-list-paging). See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging contract
shared by every ``list_<domain>`` tool, and
``.specmgr/feat/feat-21-decision/README.md`` ACC-002 for this tool's own
paging-clamp clause.
"""

from __future__ import annotations

from pydantic import ValidationError

from ...general.models import PagedResult
from ...general.tools._paging import normalize_paging, paginate
from ...server import mcp
from ..models.v1 import DecSummary
from ._io import read_dec
from ._paths import iter_dec_paths


@mcp.tool(
    name="list_dec",
    title="List decisions",
    description=(
        "Ids, titles, statuses, and refs of decisions in the configured decision base directory, "
        "one page at a time, for context before addressing one by id. 'ref' is an opaque, "
        "extensionless identifier -- not a filename to read from disk -- for documents that "
        "have no assigned id; use it with the get_dec tool instead. max_results/offset control "
        "paging (default page size 25, capped at 100); out-of-range values are clamped, not errored."
    ),
)
def list_dec(max_results: int | None = None, offset: int | None = None) -> PagedResult[DecSummary]:
    """Return one page of one-line decision summaries from the configured base directory.

    A file that fails to parse (``AssertionError`` or
    ``pydantic.ValidationError`` -- the same two error channels
    :func:`~biz.dfch.specmgr.dec.models.v1.parse_dec` raises) is silently
    skipped -- a single malformed file must not break listing every other
    valid one (mirrors ``dec.tools._paths.find_dec_path``'s own
    skip-on-parse-failure rule). The complete, skip-broken-file-filtered
    list is materialized first, then paginated in memory, so the returned
    ``total`` always reflects the count of parseable documents only,
    independent of paging.

    Parameters
    ----------
    max_results:
        Maximum number of summaries to return in this page. Defaults to
        ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);
        otherwise clamped into range (see
        :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
    offset:
        Zero-based index of the first summary to include in this page.
        Defaults to ``0`` when not given (``None``); negative values are
        floored to ``0``.

    Returns
    -------
    PagedResult[DecSummary]
        One entry per successfully-parsed ``*.md`` file within the
        requested page, in filename-sorted order. ``results`` is empty if
        the base directory does not exist, holds no decisions, or ``offset``
        is past the end of the full list.
    """
    summaries: list[DecSummary] = []
    for path in iter_dec_paths():
        try:
            doc = read_dec(path)
        except (AssertionError, ValidationError):
            continue
        summaries.append(
            DecSummary(
                id=doc.frontmatter.id,
                title=doc.body.text,
                status=doc.frontmatter.status,
                ref=path.stem,
            )
        )
    return paginate(summaries, *normalize_paging(max_results, offset))

=== dec/tools/delete_dec.py ===
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

"""``@mcp.tool()`` wrapper: delete_dec (Task 2.2).

Registered stub only -- reserves the ``delete_dec`` name/slot in the DEC
lifecycle tool surface without committing to a deletion strategy yet
(soft-delete via ``status``, archival, hard removal from disk, or something
else -- undecided, matching the other six domains' own ``delete_*`` stubs,
a shared cross-domain decision deferred to future work). Always raises
``NotImplementedError`` unconditionally, without resolving ``id`` or
touching the filesystem at all, so it cannot be mistaken for a working
no-op.
"""

from __future__ import annotations

from typing import NoReturn

from ...server import mcp


@mcp.tool(
    name="delete_dec",
    title="Delete decision (not yet implemented)",
    description="Stub only -- always raises NotImplementedError. Reserves the name for a future implementation.",
    # `NoReturn` has no pydantic-serializable schema; this stub never returns anyway, so
    # skip structured-output schema derivation entirely rather than lying with a fake return type.
    structured_output=False,
)
def delete_dec(id: str) -> NoReturn:
    """Always raise ``NotImplementedError``; deletion is not yet implemented.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier. Unused -- accepted only
        to fix this tool's future signature; never resolved or validated.

    Raises
    ------
    NotImplementedError
        Always.
    """
    raise NotImplementedError("delete_dec is not yet implemented")

=== dec/tools/validate_dec.py ===
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

"""``@mcp.tool()`` wrapper: validate_dec (Task 2.2).

Unlike ``validate_adr`` (which is id-based and re-reads a file from disk),
``validate_dec`` is a **disk-free, id-free dry run**: it validates a
submitted ``content`` string directly, without ever touching the decision
base directory or resolving an id. This lets a caller check a draft before
ever calling ``create_dec`` or the generic ``update`` tool in
``general.tools`` (or independently of either), and is exactly the same
check both of those tools already run internally on their own ``content``
argument, exposed standalone here.
"""

from __future__ import annotations

import frontmatter

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.v1 import Decision, parse_dec


@mcp.tool(
    name="validate_dec",
    title="Validate decision content",
    description=(
        "Disk-free, id-free dry run validating decision content. `full=False` (default) "
        "validates body-only content (no frontmatter); `full=True` validates a complete document "
        "(frontmatter + body)."
    ),
)
def validate_dec(content: str, full: bool = False) -> bool:
    """Validate ``content`` as decision markdown, without reading or writing any file.

    "Validate" means letting :class:`~biz.dfch.specmgr.dec.models.v1.Decision`/
    :class:`~biz.dfch.specmgr.dec.models.v1.DecFrontmatter`/
    :class:`~biz.dfch.specmgr.dec.models.v1.DecDocument`'s own Pydantic
    validators run during parsing -- there is no separate validation pass.
    Successfully constructing the model *is* the validation, so this
    function only ever returns ``True``; any parse/validation failure
    instead propagates as ``AssertionError``/``pydantic.ValidationError``,
    exactly as ``create_dec`` and the generic ``update`` tool do.

    Whether ``content`` carries a YAML frontmatter block is detected via
    ``frontmatter.loads(content).metadata`` (non-empty means "has
    frontmatter") -- the same ``python-frontmatter`` library every parser in
    this codebase already depends on, rather than a hand-rolled
    ``startswith("---")`` heuristic.

    Parameters
    ----------
    content:
        The decision markdown to validate.
    full:
        ``False`` (default): ``content`` must be body markdown only (the
        shape ``create_dec`` and the generic ``update`` tool accept) --
        raises ``ValueError``
        if a frontmatter block is found instead. ``True``: ``content`` must
        be a complete document, frontmatter and body together (the shape
        ``parse_dec`` expects for an on-disk file) -- raises the symmetric
        ``ValueError`` if no frontmatter block is found.

    Returns
    -------
    bool
        Always ``True`` on success.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        parse_dec(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        Decision.from_text(format_text(content))

    return True

=== dec/tools/__init__.py ===
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

"""MCP tool wrappers for decisions (mirrors ``gol/tools/``'s own shape).

``parse_dec`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_dec_example`` returns a complete, valid
sample decision document as raw markdown; ``get_dec_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem (Task 2.2).
``get_dec`` reads, parses, and returns a full decision document by id -- the
sole id-based read path for DEC (there is no ``specmgr://dec/{id}`` resource,
ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_dec`` returns one page of
id/title/status/ref summaries of every decision, shipped as a paged tool
from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). ``create_dec``
assigns a fresh id, builds the frontmatter itself, and writes a new document
(body markdown only, no frontmatter) under the decision base directory
(``dec.tools._paths``/``_io``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="dec"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="dec"``), also
bumping ``updated``, leaving the body untouched.
``delete_dec`` is a registered stub -- always raises
``NotImplementedError``, reserving the name for a future real
implementation. ``validate_dec`` is a disk-free, id-free dry run against a
submitted ``content`` string, independent of the other tools. Import this
package to register all decision tools at once::

    from biz.dfch.specmgr.dec import tools  # noqa: F401 (side-effects only)
"""

from .create_dec import create_dec
from .delete_dec import delete_dec
from .get_dec import get_dec
from .get_dec_example import get_dec_example
from .get_dec_template import get_dec_template
from .list_dec import list_dec
from .parse_dec import parse_dec
from .validate_dec import validate_dec

__all__ = [
    "create_dec",
    "delete_dec",
    "get_dec",
    "get_dec_example",
    "get_dec_template",
    "list_dec",
    "parse_dec",
    "validate_dec",
]


```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat src/biz/dfch/specmgr/general/tools/update.py"
}
```

**Output:**

```
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

"""``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).

The generic, cross-domain whole-body *and* line-range replace tool for the
nine whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
``gol``/``rsk``/``dec``/``feat``). It dispatches on the explicit ``type``
parameter to
a private per-domain adapter (``_update_<d>``), each a **verbatim port** of
the corresponding per-domain ``update_<d>`` tool's function body (same
domain lock, same ``load_by_id``, same frontmatter carry-over with only
``updated`` bumped, same verbatim persistence via the domain's own
``write_<d>_file``, same domain ``XNotFoundError``) plus the REQ-002 range
branch: with ``begin``/``end`` given, the on-disk body is re-read via
:func:`._splice.body_text`, spliced via :func:`._splice.splice_body`, and
the *spliced result* is validated as a whole document and persisted
verbatim instead of the raw fragment.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects to
the builtin shadow. The 9-way union return type is annotation-only -- the
MCP input schema is built from the parameters, and the SDK serializes
whichever concrete document is returned.

``feat`` is the one domain whose adapter (``_update_feat``) diverges from
the other eight's identical shape in how it resolves ``id``: via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes, "Addressing").
It bumps ``updated`` to the same microsecond timestamp as every other
domain -- an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date)
was reversed for cross-domain consistency; see that feature's Decisions
Made.

ADR is deliberately *not* a ``type`` here: its section-level MADR mutation
contract (``update_frontmatter``/``update_section``/``option_*``) has no
whole-body replace by design.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Literal

from ...dec.models.v1 import DecDocument, DecFrontmatter, Decision
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatDocument, FeatFrontmatter, Feature
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolDocument, GolFrontmatter, Goal
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.md._markdown import format_text
from ...prb.models.v1 import Prb, PrbDocument, PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import Qa, QaDocument, QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqDocument, ReqFrontmatter, Requirement
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import Risk, RskDocument, RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...tsk.models.v1 import Task, TskDocument, TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir
from ...tsk.tools._write import write_tsk_file
from ...uc.models.v2 import UcDocument, UcFrontmatter, UseCase
from ...uc.tools._io import load_by_id as load_uc_by_id
from ...uc.tools._lock import uc_lock
from ...uc.tools._paths import uc_base_dir
from ...uc.tools._write import write_uc_file
from ._splice import body_text, splice_body

__all__ = ["update"]

#: The generic tool's 9-way return union -- annotation-only (see module docstring).
_UpdateDocument = (
    ReqDocument
    | UcDocument
    | TskDocument
    | QaDocument
    | PrbDocument
    | GolDocument
    | RskDocument
    | DecDocument
    | FeatDocument
)


def _update_req(id_: str, content: str, begin: int | None, end: int | None) -> ReqDocument:
    """Replace the body of the requirement identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain requirement update tool's
    function body (same ``req_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_req_file``, ``ReqNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch: with ``begin``/``end`` given (both-or-neither is
    enforced by the public :func:`update` before dispatch), the on-disk
    body is re-read via :func:`body_text`, spliced via
    :func:`splice_body`, and the *spliced result* is validated and
    persisted verbatim instead of the raw fragment.
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = req_base_dir()
        with req_lock(id_):
            path, existing = load_req_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Requirement.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = ReqFrontmatter(**fm_data)
            new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
            write_req_file(path, new_frontmatter, spliced)
        return new_doc

    body = Requirement.from_text(format_text(content))

    base_dir = req_base_dir()
    with req_lock(id_):
        path, existing = load_req_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = ReqFrontmatter(**fm_data)
        new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
        write_req_file(path, new_frontmatter, content)
    return new_doc


def _update_uc(id_: str, content: str, begin: int | None, end: int | None) -> UcDocument:
    """Replace the body of the use case identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain use-case update tool's function
    body (same ``uc_lock``, ``load_by_id``, frontmatter carry-over with only
    ``updated`` bumped, ``write_uc_file``, ``UcNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = uc_base_dir()
        with uc_lock(id_):
            path, existing = load_uc_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = UseCase.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = UcFrontmatter(**fm_data)
            new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
            write_uc_file(path, new_frontmatter, spliced)
        return new_doc

    body = UseCase.from_text(format_text(content))

    base_dir = uc_base_dir()
    with uc_lock(id_):
        path, existing = load_uc_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = UcFrontmatter(**fm_data)
        new_doc = UcDocument(frontmatter=new_frontmatter, body=body)
        write_uc_file(path, new_frontmatter, content)
    return new_doc


def _update_tsk(id_: str, content: str, begin: int | None, end: int | None) -> TskDocument:
    """Replace the body of the task list identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain task list update tool's
    function body (same ``tsk_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_tsk_file``, ``TskNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = tsk_base_dir()
        with tsk_lock(id_):
            path, existing = load_tsk_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Task.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = TskFrontmatter(**fm_data)
            new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
            write_tsk_file(path, new_frontmatter, spliced)
        return new_doc

    body = Task.from_text(format_text(content))

    base_dir = tsk_base_dir()
    with tsk_lock(id_):
        path, existing = load_tsk_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = TskFrontmatter(**fm_data)
        new_doc = TskDocument(frontmatter=new_frontmatter, body=body)
        write_tsk_file(path, new_frontmatter, content)
    return new_doc


def _update_qa(id_: str, content: str, begin: int | None, end: int | None) -> QaDocument:
    """Replace the body of the QA document identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain QA document update tool's
    function body (same ``qa_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_qa_file``, ``QaNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 3), plus the REQ-002
    range branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = qa_base_dir()
        with qa_lock(id_):
            path, existing = load_qa_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Qa.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = QaFrontmatter(**fm_data)
            new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
            write_qa_file(path, new_frontmatter, spliced)
        return new_doc

    body = Qa.from_text(format_text(content))

    base_dir = qa_base_dir()
    with qa_lock(id_):
        path, existing = load_qa_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = QaFrontmatter(**fm_data)
        new_doc = QaDocument(frontmatter=new_frontmatter, body=body)
        write_qa_file(path, new_frontmatter, content)
    return new_doc


def _update_prb(id_: str, content: str, begin: int | None, end: int | None) -> PrbDocument:
    """Replace the body of the problem statement identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain problem statement update
    tool's function body (same ``prb_lock``, ``load_by_id``, frontmatter
    carry-over with only ``updated`` bumped, ``write_prb_file``,
    ``PrbNotFoundError``; that per-domain tool was retired in feat-22
    Phase 3), plus the REQ-002 range branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = prb_base_dir()
        with prb_lock(id_):
            path, existing = load_prb_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Prb.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = PrbFrontmatter(**fm_data)
            new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
            write_prb_file(path, new_frontmatter, spliced)
        return new_doc

    body = Prb.from_text(format_text(content))

    base_dir = prb_base_dir()
    with prb_lock(id_):
        path, existing = load_prb_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = PrbFrontmatter(**fm_data)
        new_doc = PrbDocument(frontmatter=new_frontmatter, body=body)
        write_prb_file(path, new_frontmatter, content)
    return new_doc


def _update_gol(id_: str, content: str, begin: int | None, end: int | None) -> GolDocument:
    """Replace the body of the goal identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain goal update tool's function
    body (same ``gol_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_gol_file``, ``GolNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = gol_base_dir()
        with gol_lock(id_):
            path, existing = load_gol_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Goal.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = GolFrontmatter(**fm_data)
            new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
            write_gol_file(path, new_frontmatter, spliced)
        return new_doc

    body = Goal.from_text(format_text(content))

    base_dir = gol_base_dir()
    with gol_lock(id_):
        path, existing = load_gol_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = GolFrontmatter(**fm_data)
        new_doc = GolDocument(frontmatter=new_frontmatter, body=body)
        write_gol_file(path, new_frontmatter, content)
    return new_doc


def _update_rsk(id_: str, content: str, begin: int | None, end: int | None) -> RskDocument:
    """Replace the body of the risk identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain risk update tool's function
    body (same ``rsk_lock``, ``load_by_id``, frontmatter carry-over with
    only ``updated`` bumped, ``write_rsk_file``, ``RskNotFoundError``; that
    per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
    branch (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = rsk_base_dir()
        with rsk_lock(id_):
            path, existing = load_rsk_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Risk.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = RskFrontmatter(**fm_data)
            new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
            write_rsk_file(path, new_frontmatter, spliced)
        return new_doc

    body = Risk.from_text(format_text(content))

    base_dir = rsk_base_dir()
    with rsk_lock(id_):
        path, existing = load_rsk_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = RskFrontmatter(**fm_data)
        new_doc = RskDocument(frontmatter=new_frontmatter, body=body)
        write_rsk_file(path, new_frontmatter, content)
    return new_doc


def _update_dec(id_: str, content: str, begin: int | None, end: int | None) -> DecDocument:
    """Replace the body of the decision identified by ``id_`` (whole-body or line-range mode).

    Verbatim port of the previous per-domain decision update tool's
    function body (same ``dec_lock``, ``load_by_id``, frontmatter carry-over
    with only ``updated`` bumped, ``write_dec_file``, ``DecNotFoundError``;
    that per-domain tool was retired in feat-22 Phase 8, when the DEC
    domain -- merged from dev while still on the old per-domain mechanism
    -- was converted to the generic tools), plus the REQ-002 range branch
    (see :func:`_update_req`).
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = dec_base_dir()
        with dec_lock(id_):
            path, existing = load_dec_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Decision.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = DecFrontmatter(**fm_data)
            new_doc = DecDocument(frontmatter=new_frontmatter, body=body)
            write_dec_file(path, new_frontmatter, spliced)
        return new_doc

    body = Decision.from_text(format_text(content))

    base_dir = dec_base_dir()
    with dec_lock(id_):
        path, existing = load_dec_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = DecFrontmatter(**fm_data)
        new_doc = DecDocument(frontmatter=new_frontmatter, body=body)
        write_dec_file(path, new_frontmatter, content)
    return new_doc


def _update_feat(id_: str, content: str, begin: int | None, end: int | None) -> FeatDocument:
    """Replace the body of the feature identified by ``id_`` (whole-body or line-range mode).

    Mirrors :func:`_update_dec`'s shape (same ``feat_lock``, ``load_by_id``,
    ``write_feat_file``, ``FeatNotFoundError``) with one feat-only
    divergence (see the module docstring): ``id_`` resolves via
    ``feat.tools._paths``'s bespoke folder-per-document shortcut (through
    ``load_by_id``/``feat_base_dir``), not a flat-file directory scan.
    ``updated`` is bumped to the same microsecond timestamp as every other
    domain.
    """
    if begin is not None or end is not None:
        assert begin is not None and end is not None, "the public `update` guard enforces both-or-neither"

        base_dir = feat_base_dir()
        with feat_lock(id_):
            path, existing = load_feat_by_id(base_dir, id_)
            spliced = splice_body(body_text(path), begin, end, content)
            body = Feature.from_text(format_text(spliced))
            now = datetime.now().isoformat(timespec="microseconds")
            fm_data = existing.frontmatter.model_dump()
            fm_data["updated"] = now
            new_frontmatter = FeatFrontmatter(**fm_data)
            new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
            write_feat_file(path, new_frontmatter, spliced)
        return new_doc

    body = Feature.from_text(format_text(content))

    base_dir = feat_base_dir()
    with feat_lock(id_):
        path, existing = load_feat_by_id(base_dir, id_)
        now = datetime.now().isoformat(timespec="microseconds")
        fm_data = existing.frontmatter.model_dump()
        fm_data["updated"] = now
        new_frontmatter = FeatFrontmatter(**fm_data)
        new_doc = FeatDocument(frontmatter=new_frontmatter, body=body)
        write_feat_file(path, new_frontmatter, content)
    return new_doc


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str, str, int | None, int | None], _UpdateDocument]] = {
    "req": _update_req,
    "uc": _update_uc,
    "tsk": _update_tsk,
    "qa": _update_qa,
    "prb": _update_prb,
    "gol": _update_gol,
    "rsk": _update_rsk,
    "dec": _update_dec,
    "feat": _update_feat,
}


@mcp.tool(
    name="update",
    title="Update document",
    description=(
        "Whole-body or line-range replace of an existing document's content across the nine "
        "whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat), preserving "
        "its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` "
        "is the full replacement body (body markdown only, no frontmatter block). With both, "
        "`content` replaces the 1-based inclusive body-line range `begin`..`end` of the current "
        "on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace "
        "through end of body); the spliced result is validated as a whole document before "
        "anything is written. `status` is never settable -- use the generic `set_status` tool."
    ),
)
def update(
    id: str,
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat"],
    content: str,
    begin: int | None = None,
    end: int | None = None,
) -> _UpdateDocument:
    """Replace the body of an existing document, in whole-body or line-range mode.

    Cross-domain generic for the nine whole-body document types
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``);
    dispatches on ``type`` to the domain's own ported adapter (same lock,
    same id resolution, same frontmatter carry-over, same verbatim
    persistence, same domain not-found error).

    **Whole-body mode** (no ``begin``/``end``): ``content`` is body
    markdown only, with no YAML frontmatter block -- the same shape the
    per-domain ``update_<d>`` tools accept. Validated the same way: the
    domain body model's ``from_text(format_text(content))``, letting
    ``AssertionError`` (structural failure) or ``pydantic.ValidationError``
    (field/cross-field failure) propagate uncaught, with nothing written in
    either case.

    **Range mode** (both ``begin`` and ``end`` given): ``content`` is a
    replacement *fragment* for the current on-disk body's 1-based,
    inclusive line range ``begin..end``, where ``N`` is the number of lines
    of the current frontmatter-stripped body (the text ``get_<d>(id,
    raw=True)`` returns) and ``N+1`` is a virtual position past the last
    line (``begin = end = N+1`` appends at end of body; ``end = N+1``
    extends the range through the last line). The on-disk body is re-read
    under the domain lock, spliced (drop lines ``begin..min(end, N)``,
    insert the fragment's lines at position ``begin - 1``), and the
    *spliced result* -- not the fragment -- is validated as a whole body
    exactly like whole-body mode and then persisted verbatim, so unchanged
    regions of the on-disk body stay byte-identical. An empty ``content``
    deletes the range (legal iff the result still validates). The YAML
    frontmatter is never addressable: coordinates are body-relative by
    construction.

    In both modes the existing file's frontmatter is carried over with
    every field preserved except ``updated`` (bumped to the current
    microsecond timestamp); ``status`` in particular is never settable
    through this tool -- the generic ``set_status`` tool in
    ``general.tools`` is the only status-change path.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``.
    content:
        Whole-body mode: the replacement body markdown, with no
        frontmatter block. Range mode: the replacement fragment for lines
        ``begin..end`` (may be empty to delete the range).
    begin:
        Optional 1-based first line of the range to replace. Must be given
        together with ``end`` (exactly one of the two is a ``ValueError``).
    end:
        Optional 1-based last line of the range to replace (inclusive);
        ``N+1`` (one past the last body line) extends the range through
        end of body. Must be given together with ``begin``.

    Returns
    -------
    ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
    GolDocument | RskDocument | DecDocument | FeatDocument
        The updated document of the dispatched domain type.

    Raises
    ------
    ValueError
        Misused range coordinates: exactly one of ``begin``/``end`` given
        (raised before any file access), or ``begin < 1``, ``begin > end``,
        or ``end > N + 1`` (raised after the on-disk body is read; the
        message names the offending value(s) and the allowed range).
        Nothing is written in any of these cases.
    AssertionError
        The (spliced) body is structurally invalid (e.g. a range that
        deletes the H1). Nothing is written.
    pydantic.ValidationError
        A field/cross-field validation failure in the (spliced) body (e.g.
        a range producing an out-of-vocabulary value). Nothing is written.
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
    PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
    FeatNotFoundError
        No document of the dispatched ``type`` has this id -- the
        domain's own not-found error, unchanged from the per-domain tools.
    """
    if (begin is None) != (end is None):
        raise ValueError(f"begin and end must be given together (both or neither), got begin={begin!r}, end={end!r}")

    adapter = _ADAPTERS[type]
    result = adapter(id, content, begin, end)
    return result

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.5s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '1,120p' src/biz/dfch/specmgr/general/tools/set_status.py"
}
```

**Output:**

```
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

"""``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).

The generic, cross-domain status-change tool for all ten document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``).
It dispatches on the explicit ``type`` parameter to a private per-domain
adapter (``_set_status_<d>``), each a **verbatim port** of the
corresponding per-domain status tool's function body (same domain lock,
same ``load_by_id``, same raw-body re-read and verbatim re-persistence,
same frontmatter reconstruction through the domain's own
``XFrontmatter`` constructor -- so the domain's closed status vocabulary
validates -- and the same domain ``XNotFoundError``; those per-domain
tools were retired in feat-22 Phase 4). The ADR adapter ports the
previous per-domain ADR status tool's function body (same ``adr_lock``,
``load_by_id``, and ``write_adr`` render round-trip,
``AdrNotFoundError``) including its delegation to
``models.adr.v1.mutations.set_status``, which composes ``status`` as
``"superseded by {superseded_by}"`` when ``superseded_by`` is given.

The ``feat`` adapter (``_set_status_feat``) diverges from the other eight
whole-body domains' identical shape in the same way ``_update_feat``
(in ``update.py``) does: it resolves ``id`` via
``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
flat-file directory scan (see
``.specmgr/feat/feat-31-feature/README.md`` Design Notes). It bumps
``updated`` to the same microsecond timestamp as every other domain --
an earlier, deliberate divergence (a plain ``YYYY-MM-DD`` date) was
reversed for cross-domain consistency; see that feature's Decisions Made.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow. The 10-way union return type is annotation-only --
the MCP input schema is built from the parameters, and the SDK
serializes whichever concrete document is returned.

``superseded_by`` is accepted only for ``type="adr"``: the
"superseded by X" status pattern is ADR-specific (no other domain's
``XFrontmatter.status`` accepts it). The public :func:`set_status`
rejects it for any other ``type`` with a ``ValueError`` before any file
access.

Neither any ``create_<d>`` tool nor the generic :func:`update` tool
accepts a ``status`` argument at all -- this tool is the sole
status-change entry point for every domain.

``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
because the pure, in-memory operation it delegates to shares this
wrapper's own name.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Literal

import frontmatter

from ...adr.tools._io import load_by_id as load_adr_by_id
from ...adr.tools._io import write_adr
from ...adr.tools._lock import adr_lock
from ...adr.tools._paths import adr_base_dir
from ...dec.models.v1 import DecDocument, DecFrontmatter
from ...dec.tools._io import load_by_id as load_dec_by_id
from ...dec.tools._lock import dec_lock
from ...dec.tools._paths import dec_base_dir
from ...dec.tools._write import write_dec_file
from ...feat.models.v1 import FeatDocument, FeatFrontmatter
from ...feat.tools._io import load_by_id as load_feat_by_id
from ...feat.tools._lock import feat_lock
from ...feat.tools._paths import feat_base_dir
from ...feat.tools._write import write_feat_file
from ...gol.models.v1 import GolDocument, GolFrontmatter
from ...gol.tools._io import load_by_id as load_gol_by_id
from ...gol.tools._lock import gol_lock
from ...gol.tools._paths import gol_base_dir
from ...gol.tools._write import write_gol_file
from ...models.adr import Adr
from ...models.adr.v1 import mutations
from ...prb.models.v1 import PrbDocument, PrbFrontmatter
from ...prb.tools._io import load_by_id as load_prb_by_id
from ...prb.tools._lock import prb_lock
from ...prb.tools._paths import prb_base_dir
from ...prb.tools._write import write_prb_file
from ...qa.models.v2 import QaDocument, QaFrontmatter
from ...qa.tools._io import load_by_id as load_qa_by_id
from ...qa.tools._lock import qa_lock
from ...qa.tools._paths import qa_base_dir
from ...qa.tools._write import write_qa_file
from ...req.models.v1 import ReqDocument, ReqFrontmatter
from ...req.tools._io import load_by_id as load_req_by_id
from ...req.tools._lock import req_lock
from ...req.tools._paths import req_base_dir
from ...req.tools._write import write_req_file
from ...rsk.models.v1 import RskDocument, RskFrontmatter
from ...rsk.tools._io import load_by_id as load_rsk_by_id
from ...rsk.tools._lock import rsk_lock
from ...rsk.tools._paths import rsk_base_dir
from ...rsk.tools._write import write_rsk_file
from ...server import mcp
from ...tsk.models.v1 import TskDocument, TskFrontmatter
from ...tsk.tools._io import load_by_id as load_tsk_by_id
from ...tsk.tools._lock import tsk_lock
from ...tsk.tools._paths import tsk_base_dir

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"_set_status_dec\\|_ADAPTERS\\|def set_status\\|Literal\\[\" src/biz/dfch/specmgr/general/tools/set_status.py"
}
```

**Output:**

```
330:def _set_status_dec(id_: str, status: str, superseded_by: str | None) -> DecDocument:
360:    Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
404:_ADAPTERS: dict[str, Callable[[str, str, str | None], _SetStatusDocument]] = {
412:    "dec": _set_status_dec,
433:def set_status(
435:    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat", "adr"],
507:    adapter = _ADAPTERS[type]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.7s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/general/tools/set_status.py",
  "offset": 325,
  "limit": 100
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/general/tools/set_status.py</path>
<type>file</type>
<content>
325:         new_doc = RskDocument(frontmatter=new_frontmatter, body=existing.body)
326:         write_rsk_file(path, new_frontmatter, raw_body)
327:     return new_doc
328: 
329: 
330: def _set_status_dec(id_: str, status: str, superseded_by: str | None) -> DecDocument:
331:     """Replace the status of the decision identified by ``id_``.
332: 
333:     Verbatim port of the previous per-domain decision status tool's
334:     function body (same ``dec_lock``, ``load_by_id``, ``write_dec_file``,
335:     ``DecNotFoundError``; that per-domain tool was retired in feat-22
336:     Phase 8, when the DEC domain -- merged from dev while still on the
337:     old per-domain mechanism -- was converted to the generic tools) --
338:     see :func:`_set_status_req` for the full semantics.
339:     """
340:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
341: 
342:     base_dir = dec_base_dir()
343:     with dec_lock(id_):
344:         path, existing = load_dec_by_id(base_dir, id_)
345:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
346: 
347:         now = datetime.now().isoformat(timespec="microseconds")
348:         fm_data = existing.frontmatter.model_dump()
349:         fm_data["status"] = status
350:         fm_data["updated"] = now
351:         new_frontmatter = DecFrontmatter(**fm_data)
352:         new_doc = DecDocument(frontmatter=new_frontmatter, body=existing.body)
353:         write_dec_file(path, new_frontmatter, raw_body)
354:     return new_doc
355: 
356: 
357: def _set_status_feat(id_: str, status: str, superseded_by: str | None) -> FeatDocument:
358:     """Replace the status of the feature identified by ``id_``.
359: 
360:     Mirrors :func:`_set_status_dec`'s shape (same ``feat_lock``,
361:     ``load_by_id``, ``write_feat_file``, ``FeatNotFoundError``) -- see
362:     :func:`_set_status_req` for the full semantics -- with the same
363:     feat-only divergence ``_update_feat`` (in ``update.py``) documents:
364:     ``id_`` resolves via ``feat.tools._paths``'s bespoke folder-per-document
365:     shortcut, not a flat-file directory scan. ``updated`` is bumped to the
366:     same microsecond timestamp as every other domain.
367:     """
368:     assert superseded_by is None, "the public `set_status` guard rejects superseded_by for non-adr types"
369: 
370:     base_dir = feat_base_dir()
371:     with feat_lock(id_):
372:         path, existing = load_feat_by_id(base_dir, id_)
373:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
374: 
375:         now = datetime.now().isoformat(timespec="microseconds")
376:         fm_data = existing.frontmatter.model_dump()
377:         fm_data["status"] = status
378:         fm_data["updated"] = now
379:         new_frontmatter = FeatFrontmatter(**fm_data)
380:         new_doc = FeatDocument(frontmatter=new_frontmatter, body=existing.body)
381:         write_feat_file(path, new_frontmatter, raw_body)
382:     return new_doc
383: 
384: 
385: def _set_status_adr(id_: str, status: str, superseded_by: str | None) -> Adr:
386:     """Replace the status of the ADR identified by ``id_``.
387: 
388:     Port of the previous per-domain ADR status tool's function body
389:     (same ``adr_lock``, ``load_by_id``, delegation to
390:     ``models.adr.v1.mutations.set_status`` -- which composes ``status`` as
391:     ``"superseded by {superseded_by}"`` when ``superseded_by`` is given --
392:     and the ``write_adr`` render round-trip, ``AdrNotFoundError``; that
393:     per-domain tool was retired in feat-22 Phase 4).
394:     """
395:     base_dir = adr_base_dir()
396:     with adr_lock(id_):
397:         path, adr = load_adr_by_id(base_dir, id_)
398:         new_adr = mutations.set_status(adr, status, superseded_by)
399:         write_adr(path, new_adr)
400:     return new_adr
401: 
402: 
403: #: Dispatch table mapping the ``type`` value to its private adapter.
404: _ADAPTERS: dict[str, Callable[[str, str, str | None], _SetStatusDocument]] = {
405:     "req": _set_status_req,
406:     "uc": _set_status_uc,
407:     "tsk": _set_status_tsk,
408:     "qa": _set_status_qa,
409:     "prb": _set_status_prb,
410:     "gol": _set_status_gol,
411:     "rsk": _set_status_rsk,
412:     "dec": _set_status_dec,
413:     "feat": _set_status_feat,
414:     _TYPE_ADR: _set_status_adr,
415: }
416: 
417: 
418: @mcp.tool(
419:     name="set_status",
420:     title="Set document status",
421:     description=(
422:         "Replace the status of an existing document across all ten domains (`type` is one of "
423:         "req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr), also bumping `updated` (the nine "
424:         "whole-body domains) and leaving the body untouched. The new `status` must be one of the "

(Showing lines 325-424 of 509. Use offset=425 to continue.)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 10.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && find tests/general -iname \"*update*\" -o -iname \"*set_status*\" | grep -v __pycache__\necho \"---\"\ngrep -n \"\\\"dec\\\"\\|'dec'\\|DecDocument\\|dec_lock\\|dec\\b\" tests/general/tools/test_update.py | head -30"
}
```

**Output:**

```
tests/general/tools/test_set_status.py
tests/general/tools/test_update.py
---
28:``tsk``, ``gol``, ``rsk``, and ``dec`` each have a genuine field-level
30:or cross-field validators -- for ``dec``, a duplicated ``### Option``
54:from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
55:from biz.dfch.specmgr.dec.tools.create_dec import create_dec
636:        doc_type="dec",
637:        create=create_dec,
978:        self.assertEqual(type_prop["enum"], ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat"])

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '1,120p' tests/general/tools/test_update.py"
}
```

**Output:**

```
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

"""Tests for the generic ``update`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 2).

Parameterized over all eight whole-body document types; seeds a real,
persisted document per type in a temp ``SPECMGR_DOCS_DIR`` via the domain's
own ``create_<d>`` tool (mirroring the fixture strategy of the per-domain
``tests/<d>/tools/test_update_<d>.py`` files still on disk at this phase).
Covers ACC-001 (whole-body mode) and ACC-002 (range mode) plus the
registration smoke test of Task 2.8.

Note on the per-type out-of-vocabulary field-value cases: ``req``, ``uc``,
``tsk``, ``gol``, ``rsk``, and ``dec`` each have a genuine field-level
``pydantic.ValidationError`` path in their body schema (closed vocabularies
or cross-field validators -- for ``dec``, a duplicated ``### Option``
number), while ``qa`` and ``prb`` bodies are free-form text only -- no
closed vocabulary, no field constraint -- so their out-of-vocabulary input
(an unrecognized section heading) fails structurally with ``AssertionError``
instead. Each type's case data flags which of the two its field-error input
raises.
"""

from __future__ import annotations

import asyncio
import importlib
import re
import tempfile
import textwrap
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.general.tools._splice import body_text
from biz.dfch.specmgr.gol.tools._paths import GolNotFoundError
from biz.dfch.specmgr.gol.tools.create_gol import create_gol
from biz.dfch.specmgr.prb.tools._paths import PrbNotFoundError
from biz.dfch.specmgr.prb.tools.create_prb import create_prb
from biz.dfch.specmgr.qa.tools._paths import QaNotFoundError
from biz.dfch.specmgr.qa.tools.create_qa import create_qa
from biz.dfch.specmgr.req.tools._paths import ReqNotFoundError
from biz.dfch.specmgr.req.tools.create_req import create_req
from biz.dfch.specmgr.rsk.tools._paths import RskNotFoundError
from biz.dfch.specmgr.rsk.tools.create_rsk import create_rsk
from biz.dfch.specmgr.tsk.tools._paths import TskNotFoundError
from biz.dfch.specmgr.tsk.tools.create_tsk import create_tsk
from biz.dfch.specmgr.uc.tools._paths import UcNotFoundError
from biz.dfch.specmgr.uc.tools.create_uc import create_uc

update_module = importlib.import_module("biz.dfch.specmgr.general.tools.update")
update = update_module.update

#: ISO-8601 microsecond timestamp shape (the ``updated`` bump precision).
_MICROSECOND_TIMESTAMP = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}"

_REQ_MINIMAL_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 80 °C.

    ## Description

    If the engine becomes too hot, the lifetime of the system decreases.

    ## Characteristics

    1. Safety
    1. Reliability

    ## Level

    MUST

    ## Source

    The International Safety Board Association (TISBA)
    """
)

_REQ_UPDATED_BODY = textwrap.dedent(
    """\
    # Maximum Engine Temperature

    WHILE the engine is running, THE temperature must be a maximum of 90 °C.

    ## Description

    Updated description text.

    ## Characteristics

    1. Safety

    ## Level

    SHOULD

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"feat\\b\\|\\\"feat\\\"\\|'feat'\\|FeatDocument\\|_CASES\\s*=\\|doc_type=\\|@dataclass\" tests/general/tools/test_update.py | head -60"
}
```

**Output:**

```
18:"""Tests for the generic ``update`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 2).
478:@dataclass(frozen=True)
512:        doc_type="req",
529:        doc_type="uc",
551:        doc_type="tsk",
568:        doc_type="qa",
585:        doc_type="prb",
602:        doc_type="gol",
619:        doc_type="rsk",
636:        doc_type="dec",
705:            with self.subTest(doc_type=case.doc_type):
722:            with self.subTest(doc_type=case.doc_type):
736:            with self.subTest(doc_type=case.doc_type):
749:            with self.subTest(doc_type=case.doc_type):
767:            with self.subTest(doc_type=case.doc_type):
780:            with self.subTest(doc_type=case.doc_type):
795:            with self.subTest(doc_type=case.doc_type):
810:            with self.subTest(doc_type=case.doc_type):
824:            with self.subTest(doc_type=case.doc_type):
837:            with self.subTest(doc_type=case.doc_type):
853:            with self.subTest(doc_type=case.doc_type):
864:            with self.subTest(doc_type=case.doc_type):
878:            with self.subTest(doc_type=case.doc_type):
893:            with self.subTest(doc_type=case.doc_type):
908:            with self.subTest(doc_type=case.doc_type):
921:            with self.subTest(doc_type=case.doc_type):
954:            with self.subTest(doc_type=case.doc_type):
978:        self.assertEqual(type_prop["enum"], ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat"])

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -rln \"update_module\\|from biz.dfch.specmgr.general.tools.update\\|from biz.dfch.specmgr.general.tools import update\" tests/feat/ 2>/dev/null\necho \"---\"\nsed -n '470,660p' tests/general/tools/test_update.py"
}
```

**Output:**

```
tests/feat/prompts/test_update_feat.py
tests/feat/tools/test_get_feat.py
tests/feat/tools/test_integration.py
---
    """``datetime`` stand-in with a frozen ``now`` (the 1..N ≡ whole-body equivalence test)."""

    @classmethod
    def now(cls, tz: Any = None) -> datetime:
        result = datetime(2026, 8, 27, 12, 0, 0, 123456)
        return result


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eight whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    minimal_body: str
    updated_body: str
    #: A unique line of ``minimal_body``; replacing just that line keeps the document valid.
    middle_marker: str
    middle_replacement: str
    #: The fragment appended at ``begin = end = N+1`` (a valid trailing optional section).
    append_fragment: str
    #: The line from which ``end = N+1`` replaces through end of body.
    eof_marker: str
    eof_fragment: str
    #: A valid optional trailing section appended to the seed for the empty-fragment
    #: deletion test (its lines, ``N_minimal+1..N``, are deleted).
    deletable_suffix: str
    #: The line to replace with ``field_error_fragment`` (or the fragment is appended
    #: at ``N+1`` when ``field_error_is_append``) to produce the domain's field-level
    #: failure.
    field_error_marker: str
    field_error_fragment: str
    field_error_is_append: bool
    #: Whether that field-level failure raises ``pydantic.ValidationError``
    #: (``req``/``uc``/``tsk``/``gol``/``rsk``) or structural ``AssertionError``
    #: (``qa``/``prb`` -- their body schemas have no field-level validation).
    field_error_is_validation: bool


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        not_found_error=ReqNotFoundError,
        minimal_body=_REQ_MINIMAL_BODY,
        updated_body=_REQ_UPDATED_BODY,
        middle_marker="If the engine becomes too hot, the lifetime of the system decreases.",
        middle_replacement="Updated description text.",
        append_fragment="\n## Notes\n\nA note.\n",
        eof_marker="## Level",
        eof_fragment="## Level\n\nSHOULD\n\n## Source\n\nThe TISBA.\n",
        deletable_suffix="\n## Notes\n\nA note.\n",
        field_error_marker="MUST",
        field_error_fragment="NOT-A-VALID-LEVEL",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
        minimal_body=_UC_MINIMAL_BODY,
        updated_body=_UC_UPDATED_BODY,
        middle_marker="Buyer issues request directly to our company.",
        middle_replacement="Buyer issues an updated request directly to our company.",
        append_fragment="\n## Open Issues\n\n- Is the scope final?\n",
        eof_marker="## Main Success Scenario",
        eof_fragment=(
            "## Main Success Scenario\n\n"
            "1. Buyer calls in with a purchase request.\n"
            "2. Company creates order in system.\n"
            "3. Company ships the order.\n"
        ),
        deletable_suffix="\n## Open Issues\n\n- Is the scope final?\n",
        field_error_marker="## Extensions",
        field_error_fragment="## Extensions\n\n### Extension 99a. Out-of-range reference\n\n1. Not resolvable.\n",
        field_error_is_append=True,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        minimal_body=_TSK_MINIMAL_BODY,
        updated_body=_TSK_UPDATED_BODY,
        middle_marker="Started the task list.",
        middle_replacement="Started the task list with a kickoff note.",
        append_fragment="\n### Progress\n\nFinished the first item.\n",
        eof_marker="## Recent Updates",
        eof_fragment="## Recent Updates\n\n### Kickoff\n\nStarted the task list.\n",
        deletable_suffix="\n### Progress\n\nFinished the first item.\n",
        field_error_marker="- [ ] Do the first thing",
        field_error_fragment="- [z] Not a valid checkbox marker",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
        minimal_body=_QA_MINIMAL_BODY,
        updated_body=_QA_UPDATED_BODY,
        middle_marker="Some intro text.",
        middle_replacement="Updated intro text.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Safety",
        eof_fragment="## Safety\n\nInterview notes here.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="## Functional Suitability",
        field_error_fragment="## Not A Category",
        field_error_is_append=False,
        field_error_is_validation=False,
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
        minimal_body=_PRB_MINIMAL_BODY,
        updated_body=_PRB_UPDATED_BODY,
        middle_marker="Something is wrong.",
        middle_replacement="Something is very wrong indeed.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Future State",
        eof_fragment="## Future State\n\nIt will actually be fixed.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="### Summary",
        field_error_fragment="### Not A Question",
        field_error_is_append=False,
        field_error_is_validation=False,
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
        minimal_body=_GOL_MINIMAL_BODY,
        updated_body=_GOL_UPDATED_BODY,
        middle_marker="THE company shall provide engines that are competitive in power output and fuel consumption.",
        middle_replacement="THE company shall provide competitive engines in power output and fuel consumption.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Source",
        eof_fragment="## Source\n\nThe 2028 market analysis.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="## Source",
        field_error_fragment="## Priority\n\n100\n\n## Source",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
        minimal_body=_RSK_MINIMAL_BODY,
        updated_body=_RSK_UPDATED_BODY,
        middle_marker="A root condition.",
        middle_replacement="A revised root condition.",
        append_fragment="\n## Owner\n\nThe safety team.\n",
        eof_marker="## Residual Assessment",
        eof_fragment="## Residual Assessment\n\n### Probability 1\n\n### Impact 2\n",
        deletable_suffix="\n## Owner\n\nThe safety team.\n",
        field_error_marker="reduce",
        field_error_fragment="not-a-strategy",
        field_error_is_append=False,
        field_error_is_validation=True,
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
        minimal_body=_DEC_MINIMAL_BODY,
        updated_body=_DEC_UPDATED_BODY,
        middle_marker="Something is wrong with the status quo.",
        middle_replacement="Something is very wrong with the status quo.",
        append_fragment="\n## More Information\n\nSome notes.\n",
        eof_marker="## Decision Outcome",
        eof_fragment="## Decision Outcome\n\nWe chose the revised arrangement.\n",
        deletable_suffix="\n## More Information\n\nSome notes.\n",
        field_error_marker="## Decision Outcome",
        field_error_fragment=(
            "\n## Pros and Cons\n"
            "\n### Option 1: First option\n"
            "\nThe first option text.\n"
            "\n### Option 1: Duplicate option\n"
            "\nThe duplicate option text.\n"
        ),
        field_error_is_append=True,
        field_error_is_validation=True,
    ),
]



```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 10.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"\\\"dec\\\"\\|'dec'\\|@dataclass\\|doc_type=\\|enum\\\"\\]\" tests/general/tools/test_set_status.py | head -40"
}
```

**Output:**

```
295:@dataclass(frozen=True)
314:        doc_type="req",
323:        doc_type="uc",
332:        doc_type="tsk",
341:        doc_type="qa",
350:        doc_type="prb",
359:        doc_type="gol",
368:        doc_type="rsk",
377:        doc_type="dec",
435:            with self.subTest(doc_type=case.doc_type):
444:            with self.subTest(doc_type=case.doc_type):
466:            with self.subTest(doc_type=case.doc_type):
479:            with self.subTest(doc_type=case.doc_type):
498:            with self.subTest(doc_type=case.doc_type):
558:            with self.subTest(doc_type=case.doc_type):

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '1,60p' tests/general/tools/test_set_status.py\necho \"...\"\nsed -n '290,400p' tests/general/tools/test_set_status.py"
}
```

**Output:**

```
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

"""Tests for the generic ``set_status`` ``@mcp.tool()`` wrapper (feat-22-consolidate-mutation-tools, Phase 4).

Parameterized over all nine document types (ACC-004); seeds a real,
persisted document per type -- the eight whole-body domains via the
domain's own ``create_<d>`` tool in a temp ``SPECMGR_DOCS_DIR`` (mirroring
the fixture strategy of ``tests/general/tools/test_update.py``), the ADR
by rendering a minimal valid model into a temp ``SPECMGR_ADR_DIR`` -- and
covers: status changed + ``updated`` bumped (microsecond timestamp) + body
untouched (eight domains: raw body byte-identical; ADR: re-render round-
trip equal apart from status); each domain's closed-vocabulary
enforcement (positive value from the domain's own ``_ALLOWED_STATUSES``;
negative value valid in one domain but invalid in the tested one -- each a
``pydantic.ValidationError`` with the file left byte-identical on disk);
the ADR-only ``superseded_by`` composition (``"superseded by X"`` in the
file) and the guard that rejects it for every non-``adr`` type *before*
any file access; and the per-domain not-found errors for an unknown id.

The per-type case data ties each ``valid_status``/``invalid_status`` pair
to the domain's own closed set (the authoritative source of truth in
``models/<v>/frontmatter.py`` -- imported as a private name here on
purpose) -- the case-data test asserts the membership relations rather
than trusting the pair literals.
"""

from __future__ import annotations

import re
import tempfile
import textwrap
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from unittest import mock

import frontmatter
from pydantic import ValidationError

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, AdrNotFoundError
from biz.dfch.specmgr.dec.models.v1.frontmatter import _ALLOWED_STATUSES as _DEC_ALLOWED_STATUSES
from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
...
    We chose the structured arrangement.
    """
)


@dataclass(frozen=True)
class _Case:
    """Per-type test data for the eight whole-body document types."""

    doc_type: str
    create: Callable[[str], Any]
    not_found_error: type[Exception]
    minimal_body: str
    #: A value from the domain's OWN closed set (the positive vocabulary case).
    valid_status: str
    #: A value valid in one other domain but outside this one's closed set
    #: (the negative vocabulary case).
    invalid_status: str
    #: The domain's own closed set (the source of truth, imported above).
    allowed_statuses: frozenset[str]


_CASES: list[_Case] = [
    _Case(
        doc_type="req",
        create=create_req,
        not_found_error=ReqNotFoundError,
        minimal_body=_REQ_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="open",
        allowed_statuses=_REQ_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="uc",
        create=create_uc,
        not_found_error=UcNotFoundError,
        minimal_body=_UC_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="implemented",
        allowed_statuses=_UC_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="tsk",
        create=create_tsk,
        not_found_error=TskNotFoundError,
        minimal_body=_TSK_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_TSK_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="qa",
        create=create_qa,
        not_found_error=QaNotFoundError,
        minimal_body=_QA_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_QA_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="prb",
        create=create_prb,
        not_found_error=PrbNotFoundError,
        minimal_body=_PRB_MINIMAL_BODY,
        valid_status="active",
        invalid_status="implemented",
        allowed_statuses=_PRB_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="gol",
        create=create_gol,
        not_found_error=GolNotFoundError,
        minimal_body=_GOL_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="open",
        allowed_statuses=_GOL_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="rsk",
        create=create_rsk,
        not_found_error=RskNotFoundError,
        minimal_body=_RSK_MINIMAL_BODY,
        valid_status="mitigating",
        invalid_status="implemented",
        allowed_statuses=_RSK_ALLOWED_STATUSES,
    ),
    _Case(
        doc_type="dec",
        create=create_dec,
        not_found_error=DecNotFoundError,
        minimal_body=_DEC_MINIMAL_BODY,
        valid_status="accepted",
        invalid_status="implemented",
        allowed_statuses=_DEC_ALLOWED_STATUSES,
    ),
]

_ADR_ID = "adr-test-id"
_ADR_SEED_BODY = AdrBody(
    title="A title",
    context_and_problem_statement="Context.",
    considered_options="Options.",
    decision_outcome="Outcome.",
)


class TempDocsDirTestCase(unittest.TestCase):
    """Common fixture: temp dirs set as the docs root via SPECMGR_DOCS_DIR and the ADR base dir via SPECMGR_ADR_DIR."""

    def setUp(self) -> None:
        self.docs_root = Path(self.enterContext(tempfile.TemporaryDirectory()))

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 14.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat tests/dec/tools/test_get_dec_example.py"
}
```

**Output:**

```
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

"""Tests for the ``get_dec_example`` ``@mcp.tool()`` wrapper (Task 2.2, real packaged data from Task 3.1)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.dec.tools.get_dec_example import get_dec_example
from biz.dfch.specmgr.general.tools import _packaged_data


class TestGetDecExampleTool(unittest.TestCase):
    """Tests for the get_dec_example tool."""

    def test_returns_real_packaged_example(self) -> None:
        """Against the real, committed packaged data file, without any patching."""
        result = get_dec_example()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("---\n"))
        self.assertIn("type: dec", result)
        self.assertIn("# Hybrid Working Arrangement for the Engineering Organization", result)

    def test_delegates_to_shared_data_reader(self) -> None:
        """The tool must return whatever general.tools._packaged_data.read_packaged_text() returns."""
        with tempfile.TemporaryDirectory() as tmp:
            example_path = Path(tmp) / "dec_example.md"
            example_path.write_text("---\ntype: dec\n---\n\n# Title\n", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=example_path):
                result = get_dec_example()

            self.assertEqual(result, "---\ntype: dec\n---\n\n# Title\n")

    def test_raises_file_not_found_when_example_missing(self) -> None:
        """A missing packaged example file must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                with self.assertRaises(FileNotFoundError):
                    get_dec_example()


if __name__ == "__main__":
    unittest.main()

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 40.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"enum\\\"\\]\\|registration\\|schema\" tests/general/tools/test_set_status.py | head -20\necho \"---full context near enum in test_update---\"\nsed -n '955,985p' tests/general/tools/test_update.py"
}
```

**Output:**

```
---full context near enum in test_update---
                self._seed(case, case.minimal_body)

                with self.assertRaises(case.not_found_error):
                    update(id="no-such-id", type=case.doc_type, content="frag", begin=1, end=1)


class TestUpdateRegistration(unittest.TestCase):
    """Task 2.8: the live ``mcp`` registration carries ``update`` with the 9-value ``type`` enum and
    optional integer ``begin``/``end`` in its input schema."""

    @classmethod
    def setUpClass(cls) -> None:
        from biz.dfch.specmgr.server import mcp

        cls._tools = asyncio.run(mcp.list_tools())

    def test_update_registered_with_type_enum_and_optional_range(self) -> None:
        """``update`` must be registered exactly once, with the 9-value ``type`` enum and optional int ``begin``/``end``."""
        matching = [t for t in self._tools if t.name == "update"]
        self.assertEqual(len(matching), 1)

        schema = matching[0].input_schema
        type_prop = schema["properties"]["type"]
        self.assertEqual(type_prop["enum"], ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat"])
        self.assertEqual(type_prop["type"], "string")
        for name in ("begin", "end"):
            prop = schema["properties"][name]
            self.assertEqual(prop["anyOf"], [{"type": "integer"}, {"type": "null"}])
            self.assertIsNone(prop["default"])
        self.assertEqual(schema["required"], ["id", "type", "content"])


```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"class Test.*Registration\\|list_tools\\|input_schema\" tests/general/tools/test_set_status.py"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.0s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && find tests -maxdepth 1 -name \"*.py\" | grep -v __pycache__\necho \"---\"\ngrep -rln \"list_tools\\|len(cls._tools)\\|assertEqual.*len.*tools\" tests/*.py tests/general 2>/dev/null | grep -v __pycache__"
}
```

**Output:**

```
tests/test_paths.py
tests/test_cli.py
tests/test_package.py
tests/__init__.py
---
tests/general/tools/test_update.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat tests/test_package.py | head -60"
}
```

**Output:**

```
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

"""Smoke test: the base library imports without the ``cli``/``mcp`` extras."""

import unittest

from biz.dfch import specmgr


class TestPackage(unittest.TestCase):
    """Smoke tests for the base ``biz.dfch.specmgr`` package."""

    def test_import(self) -> None:
        """The base package exposes an empty ``__all__``."""
        self.assertEqual(specmgr.__all__, [])


if __name__ == "__main__":
    unittest.main()

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '1,70p' src/biz/dfch/specmgr/general/tools/_doc_paths.py"
}
```

**Output:**

```
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

"""Generic, doc-type-agnostic base directory resolution, filename slugification,
and id -> path lookup (plan Task 3.10).

Generalizes ``adr.tools._paths``'s shape into a single module shared across
document domains (REQ now, UC later) instead of a copy per domain: one root
env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
for ``type_name="req"``).

**ADR is deliberately left untouched** -- it keeps its own
``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).
Migrating ADR onto this shared module is optional future cleanup, not
bundled into this change.

As with ``adr.tools._paths``, this module has no ``mcp``/file-write
dependency beyond read-only directory listing: :func:`doc_base_dir` never
creates the directory (a read-only tool shouldn't have that side effect),
only :func:`ensure_doc_base_dir` does. There is deliberately no in-memory
id -> path cache either -- every lookup re-scans the base directory and
re-parses each file, matching this codebase's "the on-disk file is the sole
source of truth" design.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TypeVar

__all__ = [
    "DEFAULT_DOCS_ROOT",
    "DOCS_DIR_ENV_VAR",
    "DocNotFoundError",
    "doc_base_dir",
    "ensure_doc_base_dir",
    "find_doc_path_by_id",
    "iter_doc_paths",
    "slugify",
]

#: Environment variable that overrides the shared documents root directory.
DOCS_DIR_ENV_VAR = "SPECMGR_DOCS_DIR"

#: Default documents root directory, relative to the current working directory.
DEFAULT_DOCS_ROOT = Path("docs")

#: Anything that isn't a lowercase ASCII letter or digit, run-collapsed.
_NON_ALNUM_RUN_PATTERN = re.compile(r"[^a-z0-9]+")

#: Maximum length of a slugified title (mirrors ``adr.tools._paths``'s filename scheme).
_SLUG_MAX_LENGTH = 60

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 1910.4s)

_Thinking:_

**Tool: task**

**Input:**

````json
{
  "description": "Implement VCR Phase 2",
  "prompt": "You are implementing exactly ONE phase of a feature plan for the biz.dfch.SpecMgr repo. Do NOT start any other phase (no resources/prompts registration, no server.py import line yet -- that's Phase 3/4). Do NOT commit. Stop and report back when this phase is done or if you hit a blocker.\n\n## Plan location\nRead in full: `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/README.md` (Task List's \"Phase 2: Tools\").\nRead `.specmgr/conventions.md` at the repo root for mandatory coding conventions before writing any code.\n\nPhase 1 is already committed: `src/biz/dfch/specmgr/vcr/models/v1/` (VcrFrontmatter, Vcr body with Verifies/Coverage/AcceptanceCriteria/MoreInformation/Updates, VcrDocument, parse_vcr, VcrSummary) exists and is fully tested. Read `src/biz/dfch/specmgr/vcr/models/v1/__init__.py` to see exactly what's importable.\n\n## Phase to implement: \"Phase 2: Tools\"\n\nExact tasks from the plan (verbatim):\n- Task 2.1: `create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr` (with `raw` param), `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub, `validate_vcr`.\n- Task 2.2: Generic `update`/`set_status` dispatch entries (`type=\"vcr\"`) in `general/tools/`.\n\n## Primary precedent: mirror the `dec` domain's tools file-for-file (it is the closest already-shipped, simple-surface, flat-file domain -- NOT `sop`, which doesn't exist in this repo's `src/` yet)\n\nRead every one of these files in full before writing anything (all under `src/biz/dfch/specmgr/dec/tools/`): `_paths.py`, `_lock.py`, `_io.py`, `_write.py`, `create_dec.py`, `parse_dec.py`, `get_dec.py`, `get_dec_example.py`, `get_dec_template.py`, `list_dec.py`, `delete_dec.py`, `validate_dec.py`, `__init__.py`.\n\n### Deliverable 1: `src/biz/dfch/specmgr/vcr/tools/` -- mirror every one of the 13 files above verbatim, renaming every `Dec`/`dec` occurrence to `Vcr`/`vcr` (class names, function names, error-message text, docstrings, module docstrings, the `filename = f\"dec-{new_id}-...\"` pattern becomes `f\"vcr-{new_id}-...\"`, etc.):\n- `_paths.py` -- `VCR_TYPE_NAME = \"vcr\"`, `VcrNotFoundError`, `vcr_base_dir`, `ensure_vcr_base_dir`, `iter_vcr_paths`, `find_vcr_path` (built on the same generic `general.tools._doc_paths` helpers `dec` uses -- do NOT invent a new shared-module dependency).\n- `_lock.py` -- `vcr_lock`.\n- `_io.py` -- `read_vcr`, `load_by_id`.\n- `_write.py` -- `write_vcr_file`.\n- `create_vcr.py` -- `@mcp.tool(name=\"create_vcr\", ...)`. Body-only content, fresh `uuid.uuid4()` id, `type=\"vcr\"`, `status=\"draft\"` always on create (note: `\"draft\"` IS in VCR's own closed set, so this is fine -- unlike if it weren't), filename `f\"vcr-{new_id}-{slugify(body.text)}.md\"`.\n- `parse_vcr.py` -- `@mcp.tool(name=\"parse_vcr\", ...)`.\n- `get_vcr.py` -- `@mcp.tool(name=\"get_vcr\", ...)`, `raw: bool = False` param exactly like `get_dec`.\n- `get_vcr_example.py` -- `@mcp.tool(name=\"get_vcr_example\", ...)`, reads `read_packaged_text(\"vcr\", \"example\")`.\n- `get_vcr_template.py` -- `@mcp.tool(name=\"get_vcr_template\", ...)`, reads `read_packaged_text(\"vcr\", \"template\")`.\n- `list_vcr.py` -- `@mcp.tool(name=\"list_vcr\", ...)`, paged, uses `VcrSummary`.\n- `delete_vcr.py` -- `@mcp.tool(name=\"delete_vcr\", ...)` stub, always `NotImplementedError`.\n- `validate_vcr.py` -- `@mcp.tool(name=\"validate_vcr\", ...)`, disk-free/id-free dry run, `full: bool = False` param.\n- `__init__.py` -- re-exports all 8 tool functions.\n\n### Deliverable 2: packaged example/template data (required for `get_vcr_example`/`get_vcr_template` to actually work and be tested -- this is data payload, not the Phase-3 `@mcp.resource()` wrapper itself, which comes later)\n\nCopy the two already-finalized, already-empirically-validated planning drafts verbatim (byte-for-byte, do not edit their content) into the package data location:\n- `.specmgr/feat/feat-33-vcr/example.md` -> `src/biz/dfch/specmgr/vcr/data/vcr_example.md`\n- `.specmgr/feat/feat-33-vcr/template.md` -> `src/biz/dfch/specmgr/vcr/data/vcr_template.md`\n\nAdd to `pyproject.toml`'s `[tool.setuptools.package-data]` section (insert the new `\"biz.dfch.specmgr.vcr\"` entry right after the existing `\"biz.dfch.specmgr.uc\"` entry and before the trailing `\"biz.dfch.specmgr.general\"` entry -- matching every other domain's `data/*.md`/`data/*.json` two-pattern shape, even though no `vcr_schema.json` exists yet -- Phase 3 will add it, the pattern just needs to already be declared):\n```toml\n\"biz.dfch.specmgr.vcr\" = [\n    \"data/*.md\",\n    \"data/*.json\"\n]\n```\n\n### Deliverable 3: generic `update`/`set_status` dispatch entries (`general/tools/`)\n\nRead `src/biz/dfch/specmgr/general/tools/update.py` and `src/biz/dfch/specmgr/general/tools/set_status.py` in full -- both are large, generic dispatch tools already serving nine (update) / ten (set_status) domains via a `type` parameter. You must add `vcr` as a **tenth**/**eleventh** entry to each, mirroring the existing `dec` entry's exact shape (`_update_dec`/`_set_status_dec` -- both read `dec_lock`, `load_dec_by_id`, `dec_base_dir`, `write_dec_file`, `DecFrontmatter`, `DecDocument`, `Decision`). Concretely, in **both** files:\n\n1. Add the import block for `vcr` (alphabetically positioned among the existing per-domain import blocks -- `vcr` sorts after `uc` and before `server`/`models.md` imports that are already interspersed; just slot it in the same relative alphabetical position `dec`/`feat`/`gol`/... already follow): `VcrDocument`/`VcrFrontmatter`/`Vcr` (`Verifies`? no -- `Vcr` is the body class name) from `...vcr.models.v1`, `load_by_id as load_vcr_by_id` from `...vcr.tools._io`, `vcr_lock` from `...vcr.tools._lock`, `vcr_base_dir` from `...vcr.tools._paths`, `write_vcr_file` from `...vcr.tools._write`.\n2. In `update.py`: add `_update_vcr(id_: str, content: str, begin: int | None, end: int | None) -> VcrDocument`, mirroring `_update_dec` exactly (docstring included, adjusted for VCR naming). Add `VcrDocument` to the `_UpdateDocument` union type. Add `\"vcr\": _update_vcr,` to `_ADAPTERS`, positioned right after `\"dec\": _update_dec,` and before `\"feat\": _update_feat,`... actually check the existing ordering carefully and slot `vcr` as the newest domain, likely last (after `\"feat\": _update_feat,`) -- read the dict's current final entries and decide based on chronological-addition convention (dec/feat were added in that order as they were built; vcr is next, so append it last). Update the `Literal[...]` parameter type list (add `\"vcr\"` at the end, after `\"feat\"`). Update the module docstring and the tool's own docstring wherever they enumerate \"nine\"/\"the nine whole-body domains\"/the explicit domain list (`req/uc/tsk/qa/prb/gol/rsk/dec/feat`) -- change to \"ten\"/add `vcr` at the end of every such list, including the `@mcp.tool()` `description=` string, the `Parameters`/`Returns`/`Raises` docstring sections (add `VcrDocument`/`VcrNotFoundError` where `FeatDocument`/`FeatNotFoundError` appear).\n3. In `set_status.py`: add `_set_status_vcr(id_: str, status: str, superseded_by: str | None) -> VcrDocument`, mirroring `_set_status_dec` exactly (including the `assert superseded_by is None` guard -- vcr is not `adr`, so `superseded_by` must never be set for it). Add `VcrDocument` to the `_SetStatusDocument` union type. Add `\"vcr\": _set_status_vcr,` to `_ADAPTERS`, positioned right after `\"feat\": _set_status_feat,` and before `_TYPE_ADR: _set_status_adr,` (since `adr` is always last -- it is the one domain with `superseded_by`). Update the `Literal[...]` parameter type list (insert `\"vcr\"` right before `\"adr\"`). Update the module docstring and tool docstring's domain-count language (\"all ten document types\" -> \"all eleven document types\") and every explicit domain list, plus `Raises` docstring sections (add `VcrNotFoundError`).\n\n## Deliverable 4: tests\n\n### `tests/vcr/tools/` -- mirror `tests/dec/tools/`'s files file-for-file, renaming `Dec`/`dec` -> `Vcr`/`vcr` throughout:\n`test_create_dec.py`, `test_delete_dec.py`, `test_get_dec_example.py`, `test_get_dec.py`, `test_get_dec_template.py`, `test_integration.py`, `test__io.py`, `test_list_dec.py`, `test__lock.py`, `test_parse_dec.py`, `test__paths.py`, `test_validate_dec.py`, `test__write.py`, plus `__init__.py`. Read each dec test file fully before mirroring it -- some construct fixture body text inline (mirror using a minimal valid VCR body: `## Verifies` + `## Coverage` + `## Acceptance Criteria` with one `### AC-001 (Test): ...` entry, matching Phase 1's own test fixtures in `tests/vcr/models/v1/test_parser.py` -- reuse/adapt that same minimal fixture). For `test_get_vcr_example.py`/`test_get_vcr_template.py`, the \"real packaged data\" assertions must reference real content that now exists in `vcr/data/vcr_example.md`/`vcr_template.md` (e.g. assert `\"type: vcr\"` is present, and the real H1 title text from `example.md`, `\"API Key Revocation Latency Verification\"`).\n\n### `tests/general/tools/test_update.py` -- add a `vcr` case to the existing table-driven `_CASES` list\nRead the whole file first. Add:\n1. Import lines for `VcrNotFoundError` (from `biz.dfch.specmgr.vcr.tools._paths`) and `create_vcr` (from `biz.dfch.specmgr.vcr.tools.create_vcr`), alphabetically positioned among the existing per-domain imports.\n2. `_VCR_MINIMAL_BODY`/`_VCR_UPDATED_BODY` module-level fixture constants (textwrap.dedent), a minimal valid VCR body (H1, `## Verifies` with a `REQ <uuid>: <title>` value + mandatory notes paragraph, `## Coverage` = `partial`, `## Acceptance Criteria` with exactly one `### AC-001 (Test): ...` entry) and an updated variant differing in one field (mirror the shape of `_DEC_MINIMAL_BODY`/`_DEC_UPDATED_BODY` nearby in the same file for the exact fixture-authoring convention used).\n3. A new `_Case(doc_type=\"vcr\", create=create_vcr, not_found_error=VcrNotFoundError, ...)` entry appended to `_CASES` (after the `dec` entry), providing: `minimal_body`/`updated_body` (the two constants above), a `middle_marker`/`middle_replacement` pair (some unique line replaced), an `append_fragment` (a valid trailing addition, e.g. adding `## More Information`), an `eof_marker`/`eof_fragment` pair, a `deletable_suffix`, and a **genuine field-level `pydantic.ValidationError` case** for `field_error_marker`/`field_error_fragment`/`field_error_is_append`/`field_error_is_validation=True` -- use a **duplicate AC number** (mirroring DEC's own duplicate-`### Option` case exactly: append a second `### AC-001 (...): ...` heading, which `Vcr`'s `_validate_ac_numbers_unique` after-validator rejects).\n4. Update the `TestUpdateRegistration.test_update_registered_with_type_enum_and_optional_range` test's enum assertion: `[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"dec\", \"feat\", \"vcr\"]`.\n5. Update the module docstring's \"eight whole-body document types\" language if it becomes stale (check the exact current wording and adjust the count/list only if it now under- or over-counts; `feat` was historically excluded from this table for its own bespoke-addressing reasons documented in the file -- `vcr` is NOT excluded, it belongs in `_CASES` like every other flat-file domain).\n\n### `tests/general/tools/test_set_status.py` -- add a `vcr` case the same way\nRead the whole file first. Add:\n1. Import for `VcrNotFoundError`/`create_vcr`, plus `from biz.dfch.specmgr.vcr.models.v1.frontmatter import _ALLOWED_STATUSES as _VCR_ALLOWED_STATUSES` (mirroring the exact `_DEC_ALLOWED_STATUSES` import line above it).\n2. A `_VCR_MINIMAL_BODY` fixture (can reuse/adapt the same one from `test_update.py`, this file has its own independent copy per existing convention -- check how `_DEC_MINIMAL_BODY` is defined in each file independently and follow the same pattern, do not try to share constants across files).\n3. A new `_Case(doc_type=\"vcr\", create=create_vcr, not_found_error=VcrNotFoundError, minimal_body=_VCR_MINIMAL_BODY, valid_status=\"progress\", invalid_status=\"accepted\", allowed_statuses=_VCR_ALLOWED_STATUSES)` appended after the `dec` entry (`\"progress\"` is one of VCR's own four values; `\"accepted\"` is valid in DEC/GOL's own sets but outside VCR's four-value set -- confirm this pairing is correct against `VcrFrontmatter`'s actual closed set before using it).\n\n## Phase-end quality gate (run yourself, report exact command output/summary)\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\nAll four must pass cleanly. If a pre-commit-style doc-generation drift check matters here, you do NOT need to run `specmgr docs`/`specmgr mcp-docs` yourself in this phase (that's covered by the orchestrator at commit time via pre-commit) -- just make sure the four commands above are clean.\n\n## Progress-section discipline\n\nUpdate `.specmgr/feat/feat-33-vcr/README.md`'s Progress section: mark Phase 2's two tasks `[x]`, update Current Status, prepend one new dated Recent-Updates entry (mirror the tone/detail of the Phase 0/Phase 1 entries already there).\n\n## Report back\n\n1. Full list of files created/modified (group by: `vcr/tools/*`, `vcr/data/*`, `pyproject.toml`, `general/tools/update.py`, `general/tools/set_status.py`, `tests/vcr/tools/*`, `tests/general/tools/test_update.py`, `tests/general/tools/test_set_status.py`).\n2. Quality-gate results (pass/fail + test count).\n3. Confirmation you did NOT touch `server.py`, did NOT create `vcr/resources`/`vcr/prompts`, did NOT add `vcr` to `server.py`'s import line, and did NOT create the `specmgr://vcr/schema`/`example`/`template` `@mcp.resource()` wrappers (those are Phase 3).\n4. Any blockers or genuine ambiguities not resolved by the plan text or by the `dec` precedent (stop and ask rather than guessing).\n\nDo NOT commit anything.",
  "subagent_type": "phase-implementer"
}
````

**Output:**

```
<task id="ses_fa92edbeaffeKyLJ6IYmphGqpE" state="completed">
<task_result>
Confirmed: no diff to `server.py` or `vcr/__init__.py`, and no commit was made (HEAD is still Phase 1's commit).

## Report

**Phase 2: Tools — complete.**

### Files created/modified

**`vcr/tools/*`** (new package, mirrors `dec/tools/` file-for-file):
`_paths.py`, `_lock.py`, `_io.py`, `_write.py`, `create_vcr.py`, `parse_vcr.py`, `get_vcr.py`, `get_vcr_example.py`, `get_vcr_template.py`, `list_vcr.py`, `delete_vcr.py`, `validate_vcr.py`, `__init__.py`

**`vcr/data/*`**: `vcr_example.md`, `vcr_template.md` (copied byte-for-byte from `.specmgr/feat/feat-33-vcr/{example,template}.md`, confirmed via `diff` — zero output)

**`pyproject.toml`**: added `"biz.dfch.specmgr.vcr" = ["data/*.md", "data/*.json"]` after the `uc` entry, before `general`

**`general/tools/update.py`**: added `vcr` imports, `_update_vcr` adapter (verbatim port of `_update_dec`), added `VcrDocument` to `_UpdateDocument` union, `"vcr": _update_vcr` appended last in `_ADAPTERS`, `Literal[...]` extended, module/tool docstrings updated (nine→ten, `FeatNotFoundError`→+`VcrNotFoundError`)

**`general/tools/set_status.py`**: added `vcr` imports, `_set_status_vcr` adapter (verbatim port of `_set_status_dec`, includes `assert superseded_by is None`), added `VcrDocument` to `_SetStatusDocument` union, `"vcr": _set_status_vcr` inserted after `feat`/before `_TYPE_ADR`, `Literal[...]` extended, docstrings updated (ten→eleven domains)

**`tests/vcr/tools/*`** (new, 13 files mirroring `tests/dec/tools/`): `__init__.py`, `test__io.py`, `test__lock.py`, `test__paths.py`, `test__write.py`, `test_create_vcr.py`, `test_delete_vcr.py`, `test_get_vcr.py`, `test_get_vcr_example.py`, `test_get_vcr_template.py`, `test_integration.py`, `test_list_vcr.py`, `test_parse_vcr.py`, `test_validate_vcr.py`

**`tests/general/tools/test_update.py`**: added `VcrNotFoundError`/`create_vcr` imports, `_VCR_MINIMAL_BODY`/`_VCR_UPDATED_BODY` fixtures, a `vcr` `_Case` entry (duplicate-`AC-001` field-error → `ValidationError`), fixed the enum assertion, updated docstring counts

**`tests/general/tools/test_set_status.py`**: added `_VCR_ALLOWED_STATUSES`/`VcrNotFoundError`/`create_vcr` imports, `_VCR_MINIMAL_BODY`, a `vcr` `_Case` entry (`valid_status="progress"`, `invalid_status="accepted"`), updated docstring counts

Also updated `.specmgr/feat/feat-33-vcr/README.md`: Phase 2 tasks marked `[x]`, Current Status updated, one new dated Updates entry prepended.

### Quality gate (all pass)

```

uv run --frozen ruff format --check → 1346 files already formatted
uv run --frozen ruff check → All checks passed!
uv run --frozen vulture src/ whitelist.py --min-confidence 60 → (no output, clean)
uv run --frozen python -m unittest discover -v -s tests -t . -p "test\_\*.py" → Ran 2400 tests, OK (up from 2336)

```

### Confirmations

- Did **not** touch `server.py` (no diff).
- Did **not** create `vcr/resources` or `vcr/prompts`.
- Did **not** add `vcr` to `server.py`'s import line.
- Did **not** create `specmgr://vcr/schema`/`example`/`template` `@mcp.resource()` wrappers.
- Did **not** commit — `git log` HEAD is still the Phase-1 commit; new/modified files are staged (`git add`) but uncommitted, so `pylint`/CI can see them without creating a commit.

### Design decision made (for the Decisions Made log)

None required beyond what the plan already specified — I followed the `dec` precedent and the plan's literal instructions exactly (adapter placement, fixture shapes, `valid_status`/`invalid_status` pairing).

### Note for the orchestrator (non-blocking, but worth knowing)

Because `general/tools/update.py`/`set_status.py` now import `vcr.tools._io`/`_lock`/`_paths`/`_write` at module level, and `vcr/__init__.py` deliberately does **not** yet bootstrap `vcr.tools` (that's Phase 4), running `tests/vcr/tools/` **in isolation** (e.g. `python -m unittest discover -s tests/vcr/tools`) can trip a circular-import `ImportError` in files that import `vcr.models.v1` directly (e.g. `test__io.py`) before anything else has loaded `general.tools`. This is a transient artifact of Phase 2's own scope boundary (every other domain's `__init__.py` bootstraps its own `tools` package first, which VCR can't do yet without exceeding Phase 2 scope). It resolves itself automatically once Phase 4 wires `vcr/__init__.py` to `from . import prompts, resources, tools` like `dec/__init__.py` does. **The full repo-wide suite — the specified quality gate — is unaffected and passes cleanly (2400 tests, OK)**, confirmed by two clean full-suite runs. Flagging this so Phase 3/4's implementer isn't surprised if they run a narrow subdirectory test invocation before wiring `vcr/__init__.py`.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.7s)

Let me independently verify Phase 2's work before proceeding.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git status --short | head -50"
}
```

**Output:**

```
M  .specmgr/feat/feat-33-vcr/README.md
 M pyproject.toml
 M src/biz/dfch/specmgr/general/tools/set_status.py
 M src/biz/dfch/specmgr/general/tools/update.py
A  src/biz/dfch/specmgr/vcr/data/vcr_example.md
A  src/biz/dfch/specmgr/vcr/data/vcr_template.md
A  src/biz/dfch/specmgr/vcr/tools/__init__.py
A  src/biz/dfch/specmgr/vcr/tools/_io.py
A  src/biz/dfch/specmgr/vcr/tools/_lock.py
A  src/biz/dfch/specmgr/vcr/tools/_paths.py
A  src/biz/dfch/specmgr/vcr/tools/_write.py
A  src/biz/dfch/specmgr/vcr/tools/create_vcr.py
A  src/biz/dfch/specmgr/vcr/tools/delete_vcr.py
A  src/biz/dfch/specmgr/vcr/tools/get_vcr.py
A  src/biz/dfch/specmgr/vcr/tools/get_vcr_example.py
A  src/biz/dfch/specmgr/vcr/tools/get_vcr_template.py
A  src/biz/dfch/specmgr/vcr/tools/list_vcr.py
A  src/biz/dfch/specmgr/vcr/tools/parse_vcr.py
A  src/biz/dfch/specmgr/vcr/tools/validate_vcr.py
 M tests/general/tools/test_set_status.py
 M tests/general/tools/test_update.py
A  tests/vcr/tools/__init__.py
A  tests/vcr/tools/test__io.py
A  tests/vcr/tools/test__lock.py
A  tests/vcr/tools/test__paths.py
A  tests/vcr/tools/test__write.py
A  tests/vcr/tools/test_create_vcr.py
A  tests/vcr/tools/test_delete_vcr.py
A  tests/vcr/tools/test_get_vcr.py
A  tests/vcr/tools/test_get_vcr_example.py
A  tests/vcr/tools/test_get_vcr_template.py
A  tests/vcr/tools/test_integration.py
A  tests/vcr/tools/test_list_vcr.py
A  tests/vcr/tools/test_parse_vcr.py
A  tests/vcr/tools/test_validate_vcr.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff --stat -- src/biz/dfch/specmgr/server.py src/biz/dfch/specmgr/vcr/__init__.py\necho \"---diff pyproject---\"\ngit diff pyproject.toml"
}
```

**Output:**

```
---diff pyproject---
diff --git a/pyproject.toml b/pyproject.toml
index 8f84142..690eb52 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -156,6 +156,10 @@ namespaces = true
     "data/*.md",
     "data/*.json"
 ]
+"biz.dfch.specmgr.vcr" = [
+    "data/*.md",
+    "data/*.json"
+]
 "biz.dfch.specmgr.general" = [
     "data/*.md"
 ]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.0s)

Good, no diff on server.py/vcr/__init__.py. Now let's run the quality gate independently.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo \"===check===\" && uv run --frozen ruff check 2>&1 | tail -10 && echo \"===vulture===\" && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1"
}
```

**Output:**

```
1346 files already formatted
===check===
All checks passed!
===vulture===

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 104.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && timeout 280 uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/full_test_run2.log 2>&1; echo \"EXIT:$?\"; grep -n \"Ran [0-9]* tests\\|^OK\\|FAILED\\|ERROR:\" /tmp/full_test_run2.log",
  "timeout": 290000
}
```

**Output:**

```
EXIT:0
9:Ran 2400 tests in 97.861s
11:OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.5s)

All 2400 tests pass. Let's spot-check the dispatch table entries and key files for correctness.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"vcr\\|Vcr\" src/biz/dfch/specmgr/general/tools/update.py | head -40"
}
```

**Output:**

```
22:``gol``/``rsk``/``dec``/``feat``/``vcr``). It dispatches on the explicit ``type``
108:from ...vcr.models.v1 import Vcr, VcrDocument, VcrFrontmatter
109:from ...vcr.tools._io import load_by_id as load_vcr_by_id
110:from ...vcr.tools._lock import vcr_lock
111:from ...vcr.tools._paths import vcr_base_dir
112:from ...vcr.tools._write import write_vcr_file
128:    | VcrDocument
491:def _update_vcr(id_: str, content: str, begin: int | None, end: int | None) -> VcrDocument:
494:    Mirrors :func:`_update_dec`'s shape (same ``vcr_lock``, ``load_by_id``,
495:    frontmatter carry-over with only ``updated`` bumped, ``write_vcr_file``,
496:    ``VcrNotFoundError``), plus the REQ-002 range branch (see
502:        base_dir = vcr_base_dir()
503:        with vcr_lock(id_):
504:            path, existing = load_vcr_by_id(base_dir, id_)
506:            body = Vcr.from_text(format_text(spliced))
510:            new_frontmatter = VcrFrontmatter(**fm_data)
511:            new_doc = VcrDocument(frontmatter=new_frontmatter, body=body)
512:            write_vcr_file(path, new_frontmatter, spliced)
515:    body = Vcr.from_text(format_text(content))
517:    base_dir = vcr_base_dir()
518:    with vcr_lock(id_):
519:        path, existing = load_vcr_by_id(base_dir, id_)
523:        new_frontmatter = VcrFrontmatter(**fm_data)
524:        new_doc = VcrDocument(frontmatter=new_frontmatter, body=body)
525:        write_vcr_file(path, new_frontmatter, content)
540:    "vcr": _update_vcr,
549:        "whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr), "
560:    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat", "vcr"],
568:    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``);
609:        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``, ``vcr``.
625:    GolDocument | RskDocument | DecDocument | FeatDocument | VcrDocument
644:    FeatNotFoundError / VcrNotFoundError

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.3s)

This looks correct and complete. Let's check set_status.py similarly and the docs regen status.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"vcr\\|Vcr\" src/biz/dfch/specmgr/general/tools/set_status.py | head -40"
}
```

**Output:**

```
21:(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``/``adr``).
127:from ...vcr.models.v1 import VcrDocument, VcrFrontmatter
128:from ...vcr.tools._io import load_by_id as load_vcr_by_id
129:from ...vcr.tools._lock import vcr_lock
130:from ...vcr.tools._paths import vcr_base_dir
131:from ...vcr.tools._write import write_vcr_file
150:    | VcrDocument
391:def _set_status_vcr(id_: str, status: str, superseded_by: str | None) -> VcrDocument:
394:    Mirrors :func:`_set_status_dec`'s shape (same ``vcr_lock``,
395:    ``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
396:    :func:`_set_status_req` for the full semantics. ``vcr`` is not
401:    base_dir = vcr_base_dir()
402:    with vcr_lock(id_):
403:        path, existing = load_vcr_by_id(base_dir, id_)
410:        new_frontmatter = VcrFrontmatter(**fm_data)
411:        new_doc = VcrDocument(frontmatter=new_frontmatter, body=existing.body)
412:        write_vcr_file(path, new_frontmatter, raw_body)
445:    "vcr": _set_status_vcr,
455:        "req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr, adr), also bumping `updated` (the ten "
467:    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "feat", "vcr", "adr"],
474:    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``/``adr``);
502:        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``, ``vcr``, ``adr``.
515:    GolDocument | RskDocument | DecDocument | FeatDocument | VcrDocument | Adr
529:    FeatNotFoundError / VcrNotFoundError / AdrNotFoundError

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.1s)

Both dispatch entries are correctly wired. Let's quickly diff the packaged data files against the originals to confirm byte-for-byte fidelity.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && diff .specmgr/feat/feat-33-vcr/example.md src/biz/dfch/specmgr/vcr/data/vcr_example.md && echo \"example: identical\"\ndiff .specmgr/feat/feat-33-vcr/template.md src/biz/dfch/specmgr/vcr/data/vcr_template.md && echo \"template: identical\""
}
```

**Output:**

```
example: identical
template: identical

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.9s)

Everything checks out. Let's stage and commit Phase 2.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add -A && git status --short | wc -l"
}
```

**Output:**

```
35

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 203.2s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr tools and generic update/set_status dispatch (Phase 2)\" -m \"vcr/tools/ (create_vcr, parse_vcr, list_vcr, get_vcr(raw=), get_vcr_example,\nget_vcr_template, delete_vcr stub, validate_vcr) mirrors dec/tools/\nfile-for-file. Packaged vcr/data/vcr_example.md and vcr_template.md\n(byte-for-byte copies of the already-validated .specmgr planning drafts),\ndeclared in pyproject.toml package-data.\n\ngeneral/tools/update.py and set_status.py gain a vcr dispatch entry\n(_update_vcr/_set_status_vcr), mirroring the dec adapter exactly.\n\ntests/vcr/tools/ mirrors tests/dec/tools/; tests/general/tools/\ntest_update.py and test_set_status.py gain a vcr _Case entry each\n(duplicate-AC-number ValidationError case for update; progress/accepted\nvalid/invalid status pair for set_status).\n\nNo resources/prompts/server.py registration yet (Phase 3-4).\"",
  "timeout": 300000
}
```

**Output:**

````
...output truncated...

Full output saved to: /home/user/.local/share/opencode/tool-output/tool_056f28d22001gDKnUkaIBcxtsD

+      context: Extra variables to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Returns:
+      The validated Pydantic model.
+
+- `parse_file(path: 'str | Path', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`
+
+- `parse_obj(obj: 'Any') -> 'Self'`
+
+- `parse_raw(b: 'str | bytes', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`
+
+- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`
+
+- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`
+
+- `update_forward_refs(**localns: 'Any') -> 'None'`
+
+- `validate(value: 'Any') -> 'Self'`
+
+- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
+
+- `copy(self, *, include: 'AbstractSetIntStr | MappingIntStrAny | None' = None, exclude: 'AbstractSetIntStr | MappingIntStrAny | None' = None, update: 'Dict[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'`
+  Returns a copy of the model.
+
+  !!! warning "Deprecated"
+      This method is now deprecated; use `model_copy` instead.
+
+  If you need `include` or `exclude`, use:
+
+  ```python {test="skip" lint="skip"}
+  data = self.model_dump(include=include, exclude=exclude, round_trip=True)
+  data = {**data, **(update or {})}
+  copied = self.model_validate(data)
+  ```
+
+  Args:
+      include: Optional set or mapping specifying which fields to include in the copied model.
+      exclude: Optional set or mapping specifying which fields to exclude in the copied model.
+      update: Optional dictionary of field-value pairs to override field values in the copied model.
+      deep: If True, the values of fields that are Pydantic models will be deep-copied.
+
+  Returns:
+      A copy of the model with included, excluded and updated fields as specified.
+
+- `dict(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False) -> 'Dict[str, Any]'`
+
+- `from_orm(obj: 'Any') -> 'Self'`
+
+- `json(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any') -> 'str'`
+
+- `model_construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
+  Creates a new instance of the `Model` class with validated data.
+
+  Creates a new model setting `__dict__` and `__pydantic_fields_set__` from trusted or pre-validated data.
+  Default values are respected, but no other validation is performed.
+
+  !!! note
+      `model_construct()` generally respects the `model_config.extra` setting on the provided model.
+      That is, if `model_config.extra == 'allow'`, then all extra passed values are added to the model instance's `__dict__`
+      and `__pydantic_extra__` fields. If `model_config.extra == 'ignore'` (the default), then all extra passed values are ignored.
+      Because no validation is performed with a call to `model_construct()`, having `model_config.extra == 'forbid'` does not result in
+      an error if extra values are passed, but they will be ignored.
+
+  Args:
+      _fields_set: A set of field names that were originally explicitly set during instantiation. If provided,
+          this is directly used for the [`model_fields_set`][pydantic.BaseModel.model_fields_set] attribute.
+          Otherwise, the field names from the `values` argument will be used.
+      values: Trusted or pre-validated data dictionary.
+
+  Returns:
+      A new instance of the `Model` class with validated data.
+
+- `model_copy(self, *, update: 'Mapping[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'`
+  !!! abstract "Usage Documentation"
+      [`model_copy`](../concepts/models.md#model-copy)
+
+  Returns a copy of the model.
+
+  !!! note
+      The underlying instance's [`__dict__`][object.__dict__] attribute is copied. This
+      might have unexpected side effects if you store anything in it, on top of the model
+      fields (e.g. the value of [cached properties][functools.cached_property]).
+
+  Args:
+      update: Values to change/add in the new model. Note: the data is not validated
+          before creating the new model. You should trust this data.
+      deep: Set to `True` to make a deep copy of the model.
+
+  Returns:
+      New model instance.
+
+- `model_dump(self, *, mode: "Literal['json', 'python'] | str" = 'python', include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'dict[str, Any]'`
+  !!! abstract "Usage Documentation"
+      [`model_dump`](../concepts/serialization.md#python-mode)
+
+  Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
+
+  Args:
+      mode: The mode in which `to_python` should run.
+          If mode is 'json', the output will only contain JSON serializable types.
+          If mode is 'python', the output may contain non-JSON-serializable Python objects.
+      include: A set of fields to include in the output.
+      exclude: A set of fields to exclude from the output.
+      context: Additional context to pass to the serializer.
+      by_alias: Whether to use the field's alias in the dictionary key if defined.
+      exclude_unset: Whether to exclude fields that have not been explicitly set.
+      exclude_defaults: Whether to exclude fields that are set to their default value.
+      exclude_none: Whether to exclude fields that have a value of `None`.
+      exclude_computed_fields: Whether to exclude computed fields.
+          While this can be useful for round-tripping, it is usually recommended to use the dedicated
+          `round_trip` parameter instead.
+      round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
+      warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
+          "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
+      fallback: A function to call when an unknown value is encountered. If not provided,
+          a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
+      serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.
+      polymorphic_serialization: Whether to use model and dataclass polymorphic serialization for this call.
+
+  Returns:
+      A dictionary representation of the model.
+
+- `model_dump_json(self, *, indent: 'int | None' = None, ensure_ascii: 'bool' = False, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False, polymorphic_serialization: 'bool | None' = None) -> 'str'`
+  !!! abstract "Usage Documentation"
+      [`model_dump_json`](../concepts/serialization.md#json-mode)
+
+  Generates a JSON representation of the model using Pydantic's `to_json` method.
+
+  Args:
+      indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
+      ensure_ascii: If `True`, the output is guaranteed to have all incoming non-ASCII characters escaped.
+          If `False` (the default), these characters will be output as-is.
+      include: Field(s) to include in the JSON output.
+      exclude: Field(s) to exclude from the JSON output.
+      context: Additional context to pass to the serializer.
+      by_alias: Whether to serialize using field aliases.
+      exclude_unset: Whether to exclude fields that have not been explicitly set.
+      exclude_defaults: Whether to exclude fields that are set to their default value.
+      exclude_none: Whether to exclude fields that have a value of `None`.
+      exclude_computed_fields: Whether to exclude computed fields.
+          While this can be useful for round-tripping, it is usually recommended to use the dedicated
+          `round_trip` parameter instead.
+      round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
+      warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
+          "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
+      fallback: A function to call when an unknown value is encountered. If not provided,
+          a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
+      serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.
+      polymorphic_serialization: Whether to use model and dataclass polymorphic serialization for this call.
+
+  Returns:
+      A JSON string representation of the model.
+
+- `model_json_schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', schema_generator: 'type[GenerateJsonSchema]' = <class 'pydantic.json_schema.GenerateJsonSchema'>, mode: 'JsonSchemaMode' = 'validation', *, union_format: "Literal['any_of', 'primitive_type_array']" = 'any_of') -> 'dict[str, Any]'`
+  Generates a JSON schema for a model class.
+
+  Args:
+      by_alias: Whether to use attribute aliases or not.
+      ref_template: The reference template.
+      union_format: The format to use when combining schemas from unions together. Can be one of:
+
+          - `'any_of'`: Use the [`anyOf`](https://json-schema.org/understanding-json-schema/reference/combining#anyOf)
+          keyword to combine schemas (the default).
+          - `'primitive_type_array'`: Use the [`type`](https://json-schema.org/understanding-json-schema/reference/type)
+          keyword as an array of strings, containing each type of the combination. If any of the schemas is not a primitive
+          type (`string`, `boolean`, `null`, `integer` or `number`) or contains constraints/metadata, falls back to
+          `any_of`.
+      schema_generator: To override the logic used to generate the JSON schema, as a subclass of
+          `GenerateJsonSchema` with your desired modifications
+      mode: The mode in which to generate the schema.
+
+  Returns:
+      The JSON schema for the given model class.
+
+- `model_parametrized_name(params: 'tuple[type[Any], ...]') -> 'str'`
+  Compute the class name for parametrizations of generic classes.
+
+  This method can be overridden to achieve a custom naming scheme for generic BaseModels.
+
+  Args:
+      params: Tuple of types of the class. Given a generic class
+          `Model` with 2 type variables and a concrete model `Model[str, int]`,
+          the value `(str, int)` would be passed to `params`.
+
+  Returns:
+      String representing the new class where `params` are passed to `cls` as type variables.
+
+  Raises:
+      TypeError: Raised when trying to generate concrete names for non-generic models.
+
+- `model_post_init(self, context: 'Any', /) -> 'None'`
+  Override this method to perform additional initialization after `__init__` and `model_construct`.
+  This is useful if you want to do some validation that requires the entire model to be initialized.
+
+- `model_rebuild(*, force: 'bool' = False, raise_errors: 'bool' = True, _parent_namespace_depth: 'int' = 2, _types_namespace: 'MappingNamespace | None' = None) -> 'bool | None'`
+  Try to rebuild the pydantic-core schema for the model.
+
+  This may be necessary when one of the annotations is a ForwardRef which could not be resolved during
+  the initial attempt to build the schema, and automatic rebuilding fails.
+
+  Args:
+      force: Whether to force the rebuilding of the model schema, defaults to `False`.
+      raise_errors: Whether to raise errors, defaults to `True`.
+      _parent_namespace_depth: The depth level of the parent namespace, defaults to 2.
+      _types_namespace: The types namespace, defaults to `None`.
+
+  Returns:
+      Returns `None` if the schema is already "complete" and rebuilding was not required.
+      If rebuilding _was_ required, returns `True` if rebuilding was successful, otherwise `False`.
+
+- `model_validate(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, from_attributes: 'bool | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
+  Validate a pydantic model instance.
+
+  Args:
+      obj: The object to validate.
+      strict: Whether to enforce types strictly.
+      extra: Whether to ignore, allow, or forbid extra data during model validation.
+          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
+      from_attributes: Whether to extract data from object attributes.
+      context: Additional context to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Raises:
+      ValidationError: If the object could not be validated.
+
+  Returns:
+      The validated model instance.
+
+- `model_validate_json(json_data: 'str | bytes | bytearray', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
+  !!! abstract "Usage Documentation"
+      [JSON Parsing](../concepts/json.md#json-parsing)
+
+  Validate the given JSON data against the Pydantic model.
+
+  Args:
+      json_data: The JSON data to validate.
+      strict: Whether to enforce types strictly.
+      extra: Whether to ignore, allow, or forbid extra data during model validation.
+          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
+      context: Extra variables to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Returns:
+      The validated Pydantic model.
+
+  Raises:
+      ValidationError: If `json_data` is not a JSON string or the object could not be validated.
+
+- `model_validate_strings(obj: 'Any', *, strict: 'bool | None' = None, extra: 'ExtraValues | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, by_name: 'bool | None' = None) -> 'Self'`
+  Validate the given object with string data against the Pydantic model.
+
+  Args:
+      obj: The object containing string data to validate.
+      strict: Whether to enforce types strictly.
+      extra: Whether to ignore, allow, or forbid extra data during model validation.
+          See the [`extra` configuration value][pydantic.ConfigDict.extra] for details.
+      context: Extra variables to pass to the validator.
+      by_alias: Whether to use the field's alias when validating against the provided input data.
+      by_name: Whether to use the field's name when validating against the provided input data.
+
+  Returns:
+      The validated Pydantic model.
+
+- `parse_file(path: 'str | Path', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`
+
+- `parse_obj(obj: 'Any') -> 'Self'`
+
+- `parse_raw(b: 'str | bytes', *, content_type: 'str | None' = None, encoding: 'str' = 'utf8', proto: 'DeprecatedParseProtocol | None' = None, allow_pickle: 'bool' = False) -> 'Self'`
+
+- `schema(by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}') -> 'Dict[str, Any]'`
+
+- `schema_json(*, by_alias: 'bool' = True, ref_template: 'str' = '#/$defs/{model}', **dumps_kwargs: 'Any') -> 'str'`
+
+- `update_forward_refs(**localns: 'Any') -> 'None'`
+
+- `validate(value: 'Any') -> 'Self'`
+
diff --git a/docs/api/biz.dfch.specmgr.general.tools.set_status.md b/docs/api/biz.dfch.specmgr.general.tools.set_status.md
index 381a96d..b4f084c 100644
--- a/docs/api/biz.dfch.specmgr.general.tools.set_status.md
+++ b/docs/api/biz.dfch.specmgr.general.tools.set_status.md
@@ -2,8 +2,8 @@
 
 ``@mcp.tool()`` wrapper: set_status (feat-22-consolidate-mutation-tools, Phase 4).
 
-The generic, cross-domain status-change tool for all ten document types
-(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``).
+The generic, cross-domain status-change tool for all eleven document types
+(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``/``adr``).
 It dispatches on the explicit ``type`` parameter to a private per-domain
 adapter (``_set_status_<d>``), each a **verbatim port** of the
 corresponding per-domain status tool's function body (same domain lock,
@@ -18,7 +18,7 @@ previous per-domain ADR status tool's function body (same ``adr_lock``,
 ``models.adr.v1.mutations.set_status``, which composes ``status`` as
 ``"superseded by {superseded_by}"`` when ``superseded_by`` is given.
 
-The ``feat`` adapter (``_set_status_feat``) diverges from the other eight
+The ``feat`` adapter (``_set_status_feat``) diverges from the other nine
 whole-body domains' identical shape in the same way ``_update_feat``
 (in ``update.py``) does: it resolves ``id`` via
 ``feat.tools._paths``'s bespoke folder-per-document shortcut, not a
@@ -30,7 +30,7 @@ reversed for cross-domain consistency; see that feature's Decisions Made.
 
 The parameter is intentionally named ``type`` (it matches the frontmatter
 field vocabulary the client already knows); no enabled ruff rule objects
-to the builtin shadow. The 10-way union return type is annotation-only --
+to the builtin shadow. The 11-way union return type is annotation-only --
 the MCP input schema is built from the parameters, and the SDK
 serializes whichever concrete document is returned.
 
@@ -163,16 +163,26 @@ function body (same ``uc_lock``, ``load_by_id``, ``write_uc_file``,
 Phase 4) -- see :func:`_set_status_req` for the full semantics.
 
 
-### `set_status(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'feat', 'adr']", status: 'str', superseded_by: 'str | None' = None) -> '_SetStatusDocument'`
+### `_set_status_vcr(id_: 'str', status: 'str', superseded_by: 'str | None') -> 'VcrDocument'`
 
-Replace the status of an existing document, across all ten domains.
+Replace the status of the verification case record identified by ``id_``.
+
+Mirrors :func:`_set_status_dec`'s shape (same ``vcr_lock``,
+``load_by_id``, ``write_vcr_file``, ``VcrNotFoundError``) -- see
+:func:`_set_status_req` for the full semantics. ``vcr`` is not
+``adr``, so ``superseded_by`` must never be given.
+
+
+### `set_status(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'feat', 'vcr', 'adr']", status: 'str', superseded_by: 'str | None' = None) -> '_SetStatusDocument'`
+
+Replace the status of an existing document, across all eleven domains.
 
 Cross-domain generic for every document type
-(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``);
+(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``/``adr``);
 dispatches on ``type`` to the domain's own ported adapter (same lock,
 same id resolution, same body handling, same domain not-found error).
 
-For the nine whole-body domains the existing file's frontmatter is
+For the ten whole-body domains the existing file's frontmatter is
 carried over with every field preserved except ``status`` (replaced)
 and ``updated`` (bumped to the current microsecond timestamp); the
 body is never touched -- its raw, on-disk markdown (not a render of
@@ -186,7 +196,7 @@ The new ``status`` must be in the domain's own closed vocabulary: the
 frontmatter is reconstructed through the domain's own
 ``XFrontmatter`` constructor, so the domain's own validator enforces
 its set. Where that set lives is documented per domain -- see each
-``XFrontmatter.status`` field (the nine whole-body domains'
+``XFrontmatter.status`` field (the ten whole-body domains'
 ``models/<v>/frontmatter.py`` and ``models/adr/v1/frontmatter.py``)
 rather than any list in this docstring.
 
@@ -196,7 +206,7 @@ id:
     The document's specmgr-assigned identifier.
 type:
     The document type / domain: one of ``req``, ``uc``, ``tsk``,
-    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``, ``adr``.
+    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``, ``vcr``, ``adr``.
 status:
     The new status. Must be one of the dispatched domain's own
     accepted values (see its ``XFrontmatter.status`` field). For
@@ -209,7 +219,7 @@ superseded_by:
 Returns
 -------
 ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
-GolDocument | RskDocument | DecDocument | FeatDocument | Adr
+GolDocument | RskDocument | DecDocument | FeatDocument | VcrDocument | Adr
     The updated document of the dispatched domain type.
 
 Raises
@@ -223,7 +233,7 @@ pydantic.ValidationError
     ``"superseded by ..."`` string). Nothing is written.
 ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
 PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
-FeatNotFoundError / AdrNotFoundError
+FeatNotFoundError / VcrNotFoundError / AdrNotFoundError
     No document of the dispatched ``type`` has this id -- the
     domain's own not-found error, unchanged from the per-domain tools.
 
diff --git a/docs/api/biz.dfch.specmgr.general.tools.update.md b/docs/api/biz.dfch.specmgr.general.tools.update.md
index 4bb55e9..dfb45ef 100644
--- a/docs/api/biz.dfch.specmgr.general.tools.update.md
+++ b/docs/api/biz.dfch.specmgr.general.tools.update.md
@@ -3,8 +3,8 @@
 ``@mcp.tool()`` wrapper: update (feat-22-consolidate-mutation-tools, Phase 2).
 
 The generic, cross-domain whole-body *and* line-range replace tool for the
-nine whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
-``gol``/``rsk``/``dec``/``feat``). It dispatches on the explicit ``type``
+ten whole-body document types (``req``/``uc``/``tsk``/``qa``/``prb``/
+``gol``/``rsk``/``dec``/``feat``/``vcr``). It dispatches on the explicit ``type``
 parameter to
 a private per-domain adapter (``_update_<d>``), each a **verbatim port** of
 the corresponding per-domain ``update_<d>`` tool's function body (same
@@ -18,7 +18,7 @@ verbatim instead of the raw fragment.
 
 The parameter is intentionally named ``type`` (it matches the frontmatter
 field vocabulary the client already knows); no enabled ruff rule objects to
-the builtin shadow. The 9-way union return type is annotation-only -- the
+the builtin shadow. The 10-way union return type is annotation-only -- the
 MCP input schema is built from the parameters, and the SDK serializes
 whichever concrete document is returned.
 
@@ -145,12 +145,22 @@ per-domain tool was retired in feat-22 Phase 3), plus the REQ-002 range
 branch (see :func:`_update_req`).
 
 
-### `update(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'feat']", content: 'str', begin: 'int | None' = None, end: 'int | None' = None) -> '_UpdateDocument'`
+### `_update_vcr(id_: 'str', content: 'str', begin: 'int | None', end: 'int | None') -> 'VcrDocument'`
+
+Replace the body of the verification case record identified by ``id_`` (whole-body or line-range mode).
+
+Mirrors :func:`_update_dec`'s shape (same ``vcr_lock``, ``load_by_id``,
+frontmatter carry-over with only ``updated`` bumped, ``write_vcr_file``,
+``VcrNotFoundError``), plus the REQ-002 range branch (see
+:func:`_update_req`).
+
+
+### `update(id: 'str', type: "Literal['req', 'uc', 'tsk', 'qa', 'prb', 'gol', 'rsk', 'dec', 'feat', 'vcr']", content: 'str', begin: 'int | None' = None, end: 'int | None' = None) -> '_UpdateDocument'`
 
 Replace the body of an existing document, in whole-body or line-range mode.
 
-Cross-domain generic for the nine whole-body document types
-(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``);
+Cross-domain generic for the ten whole-body document types
+(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``);
 dispatches on ``type`` to the domain's own ported adapter (same lock,
 same id resolution, same frontmatter carry-over, same verbatim
 persistence, same domain not-found error).
@@ -191,7 +201,7 @@ id:
     The document's specmgr-assigned identifier.
 type:
     The document type / domain: one of ``req``, ``uc``, ``tsk``,
-    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``.
+    ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``, ``vcr``.
 content:
     Whole-body mode: the replacement body markdown, with no
     frontmatter block. Range mode: the replacement fragment for lines
@@ -207,7 +217,7 @@ end:
 Returns
 -------
 ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |
-GolDocument | RskDocument | DecDocument | FeatDocument
+GolDocument | RskDocument | DecDocument | FeatDocument | VcrDocument
     The updated document of the dispatched domain type.
 
 Raises
@@ -226,7 +236,7 @@ pydantic.ValidationError
     a range producing an out-of-vocabulary value). Nothing is written.
 ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError /
 PrbNotFoundError / GolNotFoundError / RskNotFoundError / DecNotFoundError /
-FeatNotFoundError
+FeatNotFoundError / VcrNotFoundError
     No document of the dispatched ``type`` has this id -- the
     domain's own not-found error, unchanged from the per-domain tools.
 
diff --git a/docs/coverage.svg b/docs/coverage.svg
index 113b287..3efd5da 100644
--- a/docs/coverage.svg
+++ b/docs/coverage.svg
@@ -1,5 +1,5 @@
-<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="95" height="20" role="img" aria-label="coverage: 98%">
-  <title>coverage: 98%</title>
+<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="95" height="20" role="img" aria-label="coverage: 99%">
+  <title>coverage: 99%</title>
   <linearGradient id="s" x2="0" y2="100%">
     <stop offset="0" stop-color="#bbb"/>
     <stop offset="1" stop-opacity=".1"/>
@@ -15,7 +15,7 @@
   <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
     <text aria-hidden="true" x="300.0" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="500">coverage</text>
     <text x="300.0" y="140" transform="scale(.1)" fill="#fff" textLength="500">coverage</text>
-    <text aria-hidden="true" x="775.0" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="250">98%</text>
-    <text x="775.0" y="140" transform="scale(.1)" fill="#fff" textLength="250">98%</text>
+    <text aria-hidden="true" x="775.0" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="250">99%</text>
+    <text x="775.0" y="140" transform="scale(.1)" fill="#fff" textLength="250">99%</text>
   </g>
 </svg>
\ No newline at end of file

specmgr mcp-docs.........................................................Failed
- hook id: specmgr-mcp-docs
- exit code: 1
- files were modified by this hook

✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/MCP.md
diff --git a/docs/MCP.md b/docs/MCP.md
index c5bed8e..e17008d 100644
--- a/docs/MCP.md
+++ b/docs/MCP.md
@@ -3,7 +3,7 @@
 Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --
 do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 
-31 resource(s), 1 resource template(s), 87 tool(s), 23 prompt(s).
+31 resource(s), 1 resource template(s), 95 tool(s), 23 prompt(s).
 
 ## Table of Contents
 
@@ -292,6 +292,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`create_rsk`](#tool-create_rsk) | Create a new risk: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the risk base directory. |
 | [`create_tsk`](#tool-create_tsk) | Create a new task list: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the task list base directory. |
 | [`create_uc`](#tool-create_uc) | Create a new use case: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the use-case base directory. |
+| [`create_vcr`](#tool-create_vcr) | Create a new verification case record: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the verification case record base directory. |
 | [`delete_dec`](#tool-delete_dec) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_feat`](#tool-delete_feat) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_gol`](#tool-delete_gol) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
@@ -301,6 +302,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`delete_rsk`](#tool-delete_rsk) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_tsk`](#tool-delete_tsk) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`delete_uc`](#tool-delete_uc) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
+| [`delete_vcr`](#tool-delete_vcr) | Stub only -- always raises NotImplementedError. Reserves the name for a future implementation. |
 | [`get_adr`](#tool-get_adr) | Read, parse, and return a full ADR document (frontmatter and body) by its id. |
 | [`get_dec`](#tool-get_dec) | Read, parse, and return a full decision document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. |
 | [`get_dec_example`](#tool-get_dec_example) | Return a complete, valid sample decision document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
@@ -329,6 +331,9 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`get_uc`](#tool-get_uc) | Read, parse, and return a full use-case document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. |
 | [`get_uc_example`](#tool-get_uc_example) | Return a complete, valid sample use case document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`get_uc_template`](#tool-get_uc_template) | Return a UC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new use case. |
+| [`get_vcr`](#tool-get_vcr) | Read, parse, and return a full verification case record document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead. |
+| [`get_vcr_example`](#tool-get_vcr_example) | Return a complete, valid sample verification case record document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
+| [`get_vcr_template`](#tool-get_vcr_template) | Return a VCR document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new verification case record. |
 | [`list_adr`](#tool-list_adr) | Ids, titles, statuses, and refs of ADRs in the configured ADR base directory (SPECMGR_ADR_DIR), one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use get_adr with it instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_dec`](#tool-list_dec) | Ids, titles, statuses, and refs of decisions in the configured decision base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_dec tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_feat`](#tool-list_feat) | Ids, titles, statuses, and refs of features in the configured feature base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_feat tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
@@ -339,6 +344,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`list_rsk`](#tool-list_rsk) | Ids, titles, statuses, and refs of risks in the configured risk base directory, one page at a time, for context before addressing one by id. Each line also carries the initial/residual 5x5 zone levels, the TARA strategy word, the first `## Scope` entry, and the residual-risk coordinates (residual_probability/residual_impact/residual_product). 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_rsk tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_tsk`](#tool-list_tsk) | Ids, titles, statuses, and refs of task lists in the configured task list base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_tsk tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`list_uc`](#tool-list_uc) | Ids, titles, statuses, and refs of use cases in the configured use-case base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_uc tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
+| [`list_vcr`](#tool-list_vcr) | Ids, titles, statuses, and refs of verification case records in the configured verification case record base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_vcr tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored. |
 | [`mdformat`](#tool-mdformat) | Format a markdown file in place, preserving any YAML frontmatter. Returns True if the file was changed, False if already formatted. |
 | [`option_create`](#tool-option_create) | Append a new 'Option N: ...' sub-section (plan §5), returning its assigned full title. |
 | [`option_delete`](#tool-option_delete) | Remove the option named full_title (plan §5), returning the remaining full titles. |
@@ -354,8 +360,9 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`parse_rsk`](#tool-parse_rsk) | Parse a risk markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.rsk.models.v1.RskDocument`. |
 | [`parse_tsk`](#tool-parse_tsk) | Parse a task list markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.tsk.models.v1.TskDocument`. |
 | [`parse_uc`](#tool-parse_uc) | Parse a use-case markdown file (YAML frontmatter + body) from disk into a structured document. |
-| [`set_status`](#tool-set_status) | Replace the status of an existing document across all ten domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr), also bumping `updated` (the nine whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point. |
-| [`update`](#tool-update) | Whole-body or line-range replace of an existing document's content across the nine whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool. |
+| [`parse_vcr`](#tool-parse_vcr) | Parse a verification case record markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.vcr.models.v1.VcrDocument`. |
+| [`set_status`](#tool-set_status) | Replace the status of an existing document across all eleven domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr, adr), also bumping `updated` (the ten whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point. |
+| [`update`](#tool-update) | Whole-body or line-range replace of an existing document's content across the ten whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool. |
 | [`update_frontmatter`](#tool-update_frontmatter) | Whole-object replace of an ADR's frontmatter (plan §3), preserving its existing id. |
 | [`update_section`](#tool-update_section) | Whole-section replace/delete of one AdrBody field (plan §4). |
 | [`validate_adr`](#tool-validate_adr) | Re-read and re-parse an ADR by id, letting the models' own Pydantic validators run. |
@@ -368,6 +375,7 @@ Full ADR document (frontmatter and body) for the given id, as structured JSON --
 | [`validate_rsk`](#tool-validate_rsk) | Disk-free, id-free dry run validating risk content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
 | [`validate_tsk`](#tool-validate_tsk) | Disk-free, id-free dry run validating task list content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
 | [`validate_uc`](#tool-validate_uc) | Disk-free, id-free dry run validating use case content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
+| [`validate_vcr`](#tool-validate_vcr) | Disk-free, id-free dry run validating verification case record content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body). |
 | [`webfetch`](#tool-webfetch) | Fetch a URL over HTTP GET with a bearer token, but only if the URL matches the configured base URL (case-insensitively). Returns the raw response body text. Intended primarily for Web Server instances using PAT authentication. |
 
 ### Tool: create_adr
@@ -471,6 +479,16 @@ Create a new use case: assigns a fresh id, derives a filename from the body's H1
 | --- | --- | --- |
 | `content` | `string` | Yes |
 
+### Tool: create_vcr
+
+**Create verification case record**
+
+Create a new verification case record: assigns a fresh id, derives a filename from the body's H1 title, validates the submitted body-only content, and writes the new document to the verification case record base directory.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `content` | `string` | Yes |
+
 ### Tool: delete_dec
 
 **Delete decision (not yet implemented)**
@@ -561,6 +579,16 @@ Stub only -- always raises NotImplementedError. Reserves the name for a future i
 | --- | --- | --- |
 | `id` | `string` | Yes |
 
+### Tool: delete_vcr
+
+**Delete verification case record (not yet implemented)**
+
+Stub only -- always raises NotImplementedError. Reserves the name for a future implementation.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `id` | `string` | Yes |
+
 ### Tool: get_adr
 
 **Get ADR**
@@ -778,6 +806,29 @@ Return a complete, valid sample use case document as raw markdown -- frontmatter
 
 Return a UC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new use case.
 
+### Tool: get_vcr
+
+**Get verification case record**
+
+Read, parse, and return a full verification case record document (frontmatter and body) by its id. Pass raw=True to return the frontmatter-stripped body text verbatim instead.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `id` | `string` | Yes |
+| `raw` | `boolean` | No |
+
+### Tool: get_vcr_example
+
+**Get VCR example**
+
+Return a complete, valid sample verification case record document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example.
+
+### Tool: get_vcr_template
+
+**Get VCR template**
+
+Return a VCR document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new verification case record.
+
 ### Tool: list_adr
 
 **List ADRs**
@@ -888,6 +939,17 @@ Ids, titles, statuses, and refs of use cases in the configured use-case base dir
 | `max_results` | `integer | None` | No |
 | `offset` | `integer | None` | No |
 
+### Tool: list_vcr
+
+**List verification case records**
+
+Ids, titles, statuses, and refs of verification case records in the configured verification case record base directory, one page at a time, for context before addressing one by id. 'ref' is an opaque, extensionless identifier -- not a filename to read from disk -- for documents that have no assigned id; use it with the get_vcr tool instead. max_results/offset control paging (default page size 25, capped at 100); out-of-range values are clamped, not errored.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `max_results` | `integer | None` | No |
+| `offset` | `integer | None` | No |
+
 ### Tool: mdformat
 
 **Format markdown document**
@@ -1044,16 +1106,26 @@ Parse a use-case markdown file (YAML frontmatter + body) from disk into a struct
 | --- | --- | --- |
 | `path` | `string` | Yes |
 
+### Tool: parse_vcr
+
+**Parse verification case record**
+
+Parse a verification case record markdown file (YAML frontmatter + body) from disk into a structured :class:`~biz.dfch.specmgr.vcr.models.v1.VcrDocument`.
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `path` | `string` | Yes |
+
 ### Tool: set_status
 
 **Set document status**
 
-Replace the status of an existing document across all ten domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr), also bumping `updated` (the nine whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point.
+Replace the status of an existing document across all eleven domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr, adr), also bumping `updated` (the ten whole-body domains) and leaving the body untouched. The new `status` must be one of the domain's own closed vocabulary values (see the domain's `XFrontmatter.status` field); anything else raises `pydantic.ValidationError` and writes nothing. `superseded_by` is accepted only for `type="adr"` -- it composes the status as "superseded by {superseded_by}"; with any other `type` it is a `ValueError`. Neither `create_*` nor the generic `update` tool accepts a `status` argument at all -- this is the sole status-change entry point.
 
 | Parameter | Type | Required |
 | --- | --- | --- |
 | `id` | `string` | Yes |
-| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, feat, adr)` | Yes |
+| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr, adr)` | Yes |
 | `status` | `string` | Yes |
 | `superseded_by` | `string | None` | No |
 
@@ -1061,12 +1133,12 @@ Replace the status of an existing document across all ten domains (`type` is one
 
 **Update document**
 
-Whole-body or line-range replace of an existing document's content across the nine whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool.
+Whole-body or line-range replace of an existing document's content across the ten whole-body domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr), preserving its id/type/status/created/version; only `updated` changes. With no `begin`/`end`, `content` is the full replacement body (body markdown only, no frontmatter block). With both, `content` replaces the 1-based inclusive body-line range `begin`..`end` of the current on-disk body (`N+1` = end-of-body sentinel: append after the last line, or replace through end of body); the spliced result is validated as a whole document before anything is written. `status` is never settable -- use the generic `set_status` tool.
 
 | Parameter | Type | Required |
 | --- | --- | --- |
 | `id` | `string` | Yes |
-| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, feat)` | Yes |
+| `type` | `string (enum: req, uc, tsk, qa, prb, gol, rsk, dec, feat, vcr)` | Yes |
 | `content` | `string` | Yes |
 | `begin` | `integer | None` | No |
 | `end` | `integer | None` | No |
@@ -1203,6 +1275,17 @@ Disk-free, id-free dry run validating use case content. `full=False` (default) v
 | `content` | `string` | Yes |
 | `full` | `boolean` | No |
 
+### Tool: validate_vcr
+
+**Validate verification case record content**
+
+Disk-free, id-free dry run validating verification case record content. `full=False` (default) validates body-only content (no frontmatter); `full=True` validates a complete document (frontmatter + body).
+
+| Parameter | Type | Required |
+| --- | --- | --- |
+| `content` | `string` | Yes |
+| `full` | `boolean` | No |
+
 ### Tool: webfetch
 
 **Fetch a URL with bearer authentication**

specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped

````

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 15.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git status --short | head -20"
}
```

**Output:**

```
M  .specmgr/feat/feat-33-vcr/README.md
 M docs/GENERATED.md
 M docs/MCP.md
 M docs/api/README.md
 M docs/api/biz.dfch.specmgr.general.models.paged_result.md
 M docs/api/biz.dfch.specmgr.general.tools.set_status.md
 M docs/api/biz.dfch.specmgr.general.tools.update.md
 M docs/coverage.svg
M  pyproject.toml
M  src/biz/dfch/specmgr/general/tools/set_status.py
M  src/biz/dfch/specmgr/general/tools/update.py
A  src/biz/dfch/specmgr/vcr/data/vcr_example.md
A  src/biz/dfch/specmgr/vcr/data/vcr_template.md
A  src/biz/dfch/specmgr/vcr/tools/__init__.py
A  src/biz/dfch/specmgr/vcr/tools/_io.py
A  src/biz/dfch/specmgr/vcr/tools/_lock.py
A  src/biz/dfch/specmgr/vcr/tools/_paths.py
A  src/biz/dfch/specmgr/vcr/tools/_write.py
A  src/biz/dfch/specmgr/vcr/tools/create_vcr.py
A  src/biz/dfch/specmgr/vcr/tools/delete_vcr.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.7s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff docs/api/biz.dfch.specmgr.general.models.paged_result.md | head -50"
}
```

**Output:**

```
diff --git a/docs/api/biz.dfch.specmgr.general.models.paged_result.md b/docs/api/biz.dfch.specmgr.general.models.paged_result.md
index e3a0195..806b184 100644
--- a/docs/api/biz.dfch.specmgr.general.models.paged_result.md
+++ b/docs/api/biz.dfch.specmgr.general.models.paged_result.md
@@ -4860,3 +4860,444 @@ results:
 
 - `validate(value: 'Any') -> 'Self'`
 
+
+### `PagedResult[VcrSummary]`
+
+One page of results plus the paging metadata needed to fetch the next page.
+
+Every ``list_<domain>`` MCP tool (``list_adr``, ``list_req``, ``list_uc``,
+``list_tsk``, ``list_qa``) returns this same shape, parameterized by that
+domain's own summary model (e.g. ``PagedResult[ReqSummary]``), so callers
+learn one paging contract instead of five.
+
+Parameters
+----------
+total:
+    The total number of items available across all pages (e.g. every
+    parseable document in a domain's directory), independent of
+    ``offset``/``max_results``.
+offset:
+    The zero-based index of the first item included in ``results``, as
+    actually applied (already normalized -- see
+    ``general.tools._paging.normalize_paging``).
+max_results:
+    The maximum number of items requested for this page, as actually
+    applied (already normalized).
+truncated:
+    ``True`` if further items exist beyond this page (i.e.
+    ``offset + max_results < total``); ``False`` otherwise, including
+    when ``offset`` is past the end of the full item list.
+results:
+    The page's items, i.e. ``items[offset : offset + max_results]`` of
+    the full, materialized item list.
+
+**Methods:**
+
+- `construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
+
+- `from_orm(obj: 'Any') -> 'Self'`
+
+- `model_construct(_fields_set: 'set[str] | None' = None, **values: 'Any') -> 'Self'`
+  Creates a new instance of the `Model` class with validated data.
+
+  Creates a new model setting `__dict__` and `__pydantic_fields_set__` from trusted or pre-validated data.
+  Default values are respected, but no other validation is performed.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.2s)

_Thinking:_

This is expected/legitimate drift (a new `PagedResult[VcrSummary]` doc section reflecting `list_vcr`). Staging and re-committing.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add -A && git status --short | wc -l"
}
```

**Output:**

```
55

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 202.8s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr tools and generic update/set_status dispatch (Phase 2)\" -m \"vcr/tools/ (create_vcr, parse_vcr, list_vcr, get_vcr(raw=), get_vcr_example,\nget_vcr_template, delete_vcr stub, validate_vcr) mirrors dec/tools/\nfile-for-file. Packaged vcr/data/vcr_example.md and vcr_template.md\n(byte-for-byte copies of the already-validated .specmgr planning drafts),\ndeclared in pyproject.toml package-data.\n\ngeneral/tools/update.py and set_status.py gain a vcr dispatch entry\n(_update_vcr/_set_status_vcr), mirroring the dec adapter exactly.\n\ntests/vcr/tools/ mirrors tests/dec/tools/; tests/general/tools/\ntest_update.py and test_set_status.py gain a vcr _Case entry each\n(duplicate-AC-number ValidationError case for update; progress/accepted\nvalid/invalid status pair for set_status).\n\nIncludes docs/api, docs/MCP.md, docs/GENERATED.md, docs/coverage.svg\nregenerated by pre-commit hooks (the 8 new vcr tools are transitively\nimportable -- and therefore already live-registered on the shared mcp\nsingleton -- via general/tools/update.py|set_status.py's vcr.tools\nimports, even though vcr/__init__.py itself and server.py's own import\nline don't reference vcr yet; that explicit wiring is Phase 4).\n\nNo resources/prompts/server.py registration yet (Phase 3-4).\"",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[feat-33-vcr 19aeb13] feat(feat-33-vcr): add vcr tools and generic update/set_status dispatch (Phase 2)
 55 files changed, 4326 insertions(+), 80 deletions(-)
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools._io.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools._lock.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools._paths.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools._write.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.create_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.delete_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.get_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.get_vcr_example.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.get_vcr_template.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.list_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.parse_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.tools.validate_vcr.md
 create mode 100644 src/biz/dfch/specmgr/vcr/data/vcr_example.md
 create mode 100644 src/biz/dfch/specmgr/vcr/data/vcr_template.md
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/__init__.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/_io.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/_lock.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/_paths.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/_write.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/create_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/delete_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/get_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/get_vcr_example.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/get_vcr_template.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/list_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/parse_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/tools/validate_vcr.py
 create mode 100644 tests/vcr/tools/__init__.py
 create mode 100644 tests/vcr/tools/test__io.py
 create mode 100644 tests/vcr/tools/test__lock.py
 create mode 100644 tests/vcr/tools/test__paths.py
 create mode 100644 tests/vcr/tools/test__write.py
 create mode 100644 tests/vcr/tools/test_create_vcr.py
 create mode 100644 tests/vcr/tools/test_delete_vcr.py
 create mode 100644 tests/vcr/tools/test_get_vcr.py
 create mode 100644 tests/vcr/tools/test_get_vcr_example.py
 create mode 100644 tests/vcr/tools/test_get_vcr_template.py
 create mode 100644 tests/vcr/tools/test_integration.py
 create mode 100644 tests/vcr/tools/test_list_vcr.py
 create mode 100644 tests/vcr/tools/test_parse_vcr.py
 create mode 100644 tests/vcr/tools/test_validate_vcr.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.5s)

Phase 2 committed. Moving to Phase 3.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
      "status": "pending",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
    "status": "pending",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 8.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && for f in dec_example dec_template __init__; do echo \"=== dec/resources/$f.py ===\"; cat \"src/biz/dfch/specmgr/dec/resources/$f.py\"; echo; done\necho \"=== dec/prompts/create_dec.py ===\"\ncat src/biz/dfch/specmgr/dec/prompts/create_dec.py\necho \"=== dec/prompts/update_dec.py ===\"\ncat src/biz/dfch/specmgr/dec/prompts/update_dec.py\necho \"=== dec/prompts/__init__.py ===\"\ncat src/biz/dfch/specmgr/dec/prompts/__init__.py"
}
```

**Output:**

```
=== dec/resources/dec_example.py ===
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

"""Resource: specmgr://dec/example (feat-21 Task 3.4).

Read-only, addressable counterpart of the ``get_dec_example`` tool, mirroring
this repo's existing tool+resource pairs (e.g. ADR's ``get_adr`` tool /
``specmgr://adr/{id}`` resource) for a host that wants to fetch the example as
context without an explicit tool call. Deliberately does not import from
``dec.tools`` (nor vice versa): both this resource and the ``get_dec_example``
tool import the shared, doc-type-agnostic ``general.tools._packaged_data``
helper directly, so neither sub-package depends on the other just for this
one file read. Mirrors ``gol.resources.gol_example`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://dec/schema``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://dec/example",
    name="dec_example",
    title="Decision (DEC) Example",
    description=(
        "A complete, valid sample decision document as raw markdown -- frontmatter and "
        "body -- exercising every section, for use as a learning example."
    ),
    mime_type="text/markdown",
)
def dec_example() -> str:
    """Return the packaged DEC example's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as ``dec.tools.get_dec_example.get_dec_example`` -- this is simply
    that same read exposed as an MCP resource instead of a ``@mcp.tool()``.

    Returns
    -------
    str
        The example document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("dec", "example")

=== dec/resources/dec_template.py ===
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

"""Resource: specmgr://dec/template (feat-21 Task 3.4).

Read-only, addressable counterpart of the ``get_dec_template`` tool,
mirroring this repo's existing tool+resource pairs (e.g.
``get_dec_example`` / ``specmgr://dec/example``) for a host that wants to
fetch the template as context without an explicit tool call. Deliberately
does not import from ``dec.tools`` (nor vice versa): both this resource and
the ``get_dec_template`` tool import the shared, doc-type-agnostic
``general.tools._packaged_data`` helper directly, so neither sub-package
depends on the other just for this one file read. Mirrors
``gol.resources.gol_template`` file-for-file.

The resource's URI is deliberately unversioned (no ``/v1``), matching
``specmgr://dec/schema``/``specmgr://dec/example``'s own precedent.
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://dec/template",
    name="dec_template",
    title="Decision (DEC) Template",
    description=(
        "A DEC document template -- frontmatter and every body field present, populated with "
        "short placeholder ('blind text') content -- as raw markdown, for use as a starting "
        "point when drafting a new decision."
    ),
    mime_type="text/markdown",
)
def dec_template() -> str:
    """Return the packaged DEC template's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as ``dec.tools.get_dec_template.get_dec_template`` -- this is
    simply that same read exposed as an MCP resource instead of a
    ``@mcp.tool()``. Unlike GOL's template, the committed DEC template is
    guaranteed to round-trip through ``parse_dec``: its placeholder content
    satisfies every structural constraint (the RSK precedent, feat-21
    Design Notes).

    Returns
    -------
    str
        The template document's raw markdown source, including its YAML
        frontmatter block.
    """
    return read_packaged_text("dec", "template")

=== dec/resources/__init__.py ===
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

"""MCP resource registrations for Decision (DEC) documents (feat-21 Task 3.4).

``dec_schema`` registers the persisted-JSON-Schema resource
(``specmgr://dec/schema``). ``dec_example`` registers the packaged sample
decision document resource (``specmgr://dec/example``). ``dec_template``
registers the packaged decision template resource (``specmgr://dec/template``)
-- every section present, populated with short placeholder ("blind text")
content that still round-trips through ``parse_dec`` (the RSK precedent).
Import this package to register all decision resources against the shared
``mcp`` application instance::

    from biz.dfch.specmgr.dec import resources  # noqa: F401 (side-effects only)

Like GOL, DEC has no by-id single-document *resource* -- id-based reads go
through the ``get_dec`` tool only (``dec.tools.get_dec``), and no
``specmgr://dec/list`` resource either -- listing goes through the
``list_dec`` ``@mcp.tool()`` (``dec.tools.list_dec``) from the start, per
ADR ec9f5262-9912-49d0-903f-fcfb54f28c13, so that paging parameters
(``max_results``/``offset``) could be accepted.
"""

from . import dec_example, dec_schema, dec_template  # noqa: F401

__all__ = [
    "dec_example",
    "dec_schema",
    "dec_template",
]

=== dec/prompts/create_dec.py ===
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

"""``@mcp.prompt()``: create_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through drafting a brand-new Decision (DEC) document using the existing
``dec/tools/``/``dec/resources/`` surface (``list_dec``,
``specmgr://dec/template``/``specmgr://dec/example``,
``specmgr://dec/schema``, ``create_dec``, ``validate_dec``).

Unlike ``adr.prompts.create_adr``, this prompt has no frontmatter-related
parameters to pre-fill: ``create_dec`` builds the entire DEC frontmatter
itself (``id``/``type``/``status``/``created``/``updated``/``version``) --
the caller only ever supplies body markdown. The body keeps the ADR's
general structure (context, drivers, considered options, outcome, related
artifacts, pros/cons, more information, updates) but is narrated through
DEC's own section names, with ``## Pros and Cons`` -- not ADR's
``## Pros and Cons of the Options`` -- as the options container.

Naming note: this prompt is named ``create_dec``, the same name as the
``@mcp.tool()`` in ``dec/tools/create_dec.py``. This is not a collision --
the MCP protocol keeps prompts and tools in separate registries
(``prompts/list`` vs. ``tools/list``) -- but is called out here explicitly
so the two are not mistaken for the same registration (same precedent as
``gol.prompts.create_gol``/``req.prompts.create_req``).

This prompt only ever *narrates* the interview flow (checking for a
duplicate via ``list_dec``, building a ``TodoWrite`` list, eliciting the
mandatory context and outcome plus each optional section via the
``question`` tool, then calling ``create_dec``) -- it never calls
``TodoWrite``/``question``/``list_dec``/``create_dec`` itself, exactly like
every other prompt in this codebase (see ``tsk.prompts.implement_task``'s
own docstring for the same contract).

The actual instructional text lives in its own packaged data file,
``dec/data/dec_create_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$topic``), not ``str.format``, precisely so the instructions file
itself is free to use plain, unescaped ``{...}`` braces for the DEC
markdown headings it narrates to the LLM (e.g. ``# {title}``) without
those colliding with this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="create_dec",
    title="Create a decision",
    description=(
        "Guides the LLM through checking for an existing similar decision, gathering the "
        "required information, and driving create_dec/validate_dec to author a new DEC document."
    ),
)
def create_dec(topic: str) -> str:
    """Return instructional text for drafting a new decision about ``topic``.

    Parameters
    ----------
    topic:
        Free-text description of the decision to be drafted -- becomes
        the seed for the document's title and context.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``TodoWrite``, ``question``, ``list_dec``, or ``create_dec``
        itself -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("dec", "create_instructions", "md"))
    return template.substitute(topic=topic)
=== dec/prompts/update_dec.py ===
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

"""``@mcp.prompt()``: update_dec (Task 4.1).

Returns instructional text -- not itself a tool call -- that guides an LLM
through revising an existing Decision (DEC) document by id, using the
existing ``dec/tools/`` surface (``get_dec``, ``validate_dec``) plus the
generic ``update``/``set_status`` tools in ``general/tools/`` (called with
``type="dec"``; ``get_dec``'s ``raw=True`` parameter serves the line-range
flow's line numbers). There is no ``specmgr://dec/{id}`` resource to point
at -- id-based reads always go through the ``get_dec`` tool only (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614).

Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
``option_*`` equivalent here: DEC's lifecycle surface is deliberately
small -- a whole-body or line-range replace (the generic ``update`` tool
with ``type="dec"``) plus a single, dedicated status-change path (the
generic ``set_status`` tool with ``type="dec"``) -- mirroring
``req.prompts.update_req``/``rsk.prompts.update_risk``.

Like ``req.prompts.update_req``/``rsk.prompts.update_risk`` (and unlike
``gol.prompts.update_gol``, which takes only the document ``id``), this
prompt also accepts an optional ``instructions`` argument pre-filled with
the requested change; when absent, the substituted fallback tells the LLM
to ask the user before making any change rather than guessing.

This prompt only ever *narrates* the revision flow (reading current state
via `get_dec`, showing which sections are present vs. empty, eliciting
revisions via the `question` tool, then calling the generic `update` tool
with `type="dec"`, with the generic `set_status` tool with `type="dec"`
mentioned as a separate, optional follow-up) -- it never calls
``get_dec``/``question``/``update``/``set_status`` itself, exactly like
every other prompt in this codebase.

The actual instructional text lives in its own packaged data file,
``dec/data/dec_update_instructions.md``, read fresh on every call via
``general.tools._packaged_data.read_packaged_text``, rather than as an
inline Python string constant. Placeholders use ``string.Template``
(``$id``/``$instructions``), not ``str.format``, precisely so the
instructions file itself is free to use plain, unescaped ``{...}`` braces
for the DEC markdown it narrates to the LLM without those colliding with
this module's own substitution.
"""

from __future__ import annotations

from string import Template

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.prompt(
    name="update_dec",
    title="Update a decision",
    description=(
        "Guides the LLM through revising an existing decision by id: reading current "
        "state, applying the requested change with the right tool, and validating."
    ),
)
def update_dec(id: str, instructions: str | None = None) -> str:
    """Return instructional text for revising the decision identified by ``id``.

    Parameters
    ----------
    id:
        The existing document's specmgr-assigned identifier.
    instructions:
        Free-text description of the requested change. When absent, the
        returned instructions tell the LLM to ask the user first rather
        than guessing.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call. This function never calls
        ``get_dec``, ``question``, ``update``, or ``set_status`` itself
        -- it only narrates that sequence for the LLM to carry out.
    """
    template = Template(read_packaged_text("dec", "update_instructions", "md"))
    return template.substitute(
        id=id,
        instructions=instructions or "(not given -- ask the user before making any change)",
    )
=== dec/prompts/__init__.py ===
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

"""MCP prompt wrappers for Decisions (Task 4.1).

Each returns plain instructional text (auto-wrapped as a single
``UserMessage`` by the SDK) that guides an LLM through driving the
existing ``dec/tools/``/``dec/resources/`` surface in the right order --
one module per prompt, mirroring ``gol/prompts/``'s own one-module-per-
prompt split. Import this package to register all decision prompts at
once::

    from biz.dfch.specmgr.dec import prompts  # noqa: F401 (side-effects only)
"""

from .create_dec import create_dec
from .update_dec import update_dec

__all__ = [
    "create_dec",
    "update_dec",
]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.2s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat src/biz/dfch/specmgr/dec/data/dec_create_instructions.md\necho \"=== update ===\"\ncat src/biz/dfch/specmgr/dec/data/dec_update_instructions.md"
}
```

**Output:**

```
You are drafting a new Decision (DEC) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_dec` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_dec` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing decision on this topic first

Call the `list_dec` tool before creating anything. If a decision with
a similar title or topic already exists, tell the user about it and ask
(via the `question` tool) whether they want to revise that one (via the
`update_dec` prompt) instead of creating a duplicate. Only proceed to
step 1 if this is genuinely a new decision.

## 1. Structure recap (body markdown only, no frontmatter block)

- `# {title}` -- H1, mandatory, free-form.
- `## Context and Problem Statement` -- mandatory prose: the situation
  and the problem the decision addresses.
- `## Decision Drivers` -- optional prose: the requirements,
  constraints, and stakeholder interests that shape the decision.
- `## Considered Options` -- optional prose: a free-form summary of
  the options that were weighed.
- `## Decision Outcome` -- mandatory: a lead paragraph naming the
  chosen option (e.g. "We chose option 1 because ..."), followed by
  optional `### Consequences` and `### Confirmation` H3 sections.
- `## Related Artifacts` -- optional container for up to four `### `
  cross-reference bullet lists: Requirements, Decisions, Goals,
  Acceptance Criteria (each `{ID}: {description}` per line).
- `## Pros and Cons` -- optional appendix of `### Option {N}: {name}`
  sections, one per weighed option (the title after the colon is
  mandatory, numbers start at 1 and are never renumbered). The H2 is
  present only if at least one option exists.
- `## More Information` -- optional freeform supplementary text.
- `## Updates` -- optional, and the last section if present: dated
  `### {title}` entries (e.g. `2026-08-27 — Created`), each with a
  mandatory lead paragraph.

Section order is binding: Context and Problem Statement -> Decision
Drivers -> Considered Options -> Decision Outcome -> Related Artifacts
-> Pros and Cons -> More Information -> Updates. The ADR heading
`## Pros and Cons of the Options` is not part of this schema and must
not be used.

## 2. Build a todo list, then gather the information one at a time

Build a todo list with one entry per: the mandatory `## Context and
Problem Statement` and `## Decision Outcome`, and each optional section
(`## Decision Drivers`, `## Considered Options`, `## Related
Artifacts`, `## Pros and Cons`, `## More Information`, `## Updates`).
Then use the `question` tool to elicit the mandatory fields first --
the context and the outcome -- then each optional field in turn,
explicitly telling the user they may skip any optional field they
cannot or do not want to answer yet -- a freshly created decision may
have zero optional sections.

## 3. Use the template/example/schema as references

Fetch `specmgr://dec/template` or `specmgr://dec/example` as a starting
point/style reference, then check `specmgr://dec/schema` (the generated
JSON Schema) to confirm field names and constraints before drafting the
body. Do not invent field names or section headings that are not present
there.

## 4. Tool call sequence

1. Assemble the full body-only markdown per the structure above, from
   the information gathered in step 2.
2. Call `create_dec(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_dec(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_dec`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions

Any later change to this decision should go through the `update_dec` prompt
(or directly through the generic `update(id, type="dec", content)` and
`set_status(id, type="dec", status)` tools), not by re-running this prompt.
=== update ===
You are revising an existing Decision (DEC) document, id: $id

Requested change: $instructions

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update` -- every change to the document
goes through the specmgr MCP tools listed below.

## 1. Read current state first

Call `get_dec(id)` to load the document's current frontmatter and body.
Never assume prior state -- the on-disk file is always the source of
truth and may have been hand-edited since you last saw it.

## 2. If no change was specified

If "Requested change" above says "(not given)", ask the user what they
want to change before calling any write tool.

## 3. Show which sections are present and which are empty

Show the user which of the sections -- the mandatory `## Context and
Problem Statement` and `## Decision Outcome` (always present), and the
optional `## Decision Drivers`, `## Considered Options`, `## Related
Artifacts`, `## Pros and Cons`, `## More Information`, `## Updates` --
are already present with content and which are still absent. Use the
`question` tool to ask which ones (if any) they want to add to or
revise.

## 4. Map the requested change to the right tool

- A change to the body -- the `context`, `drivers`, `considered`,
  `outcome` (lead paragraph, `### Consequences`, `### Confirmation`),
  `related_artifacts`, `pros_and_cons` options, `more_information`, or
  `updates` entries -- -> the generic `update` tool called with
  `type="dec"`: a **line-range replace** for a localized change, or a
  **whole-body replace** otherwise. `content` is body markdown only (no
  frontmatter block) in both cases.
  - **Line-range replace** (a localized change -- one paragraph, field,
    or section): first call `get_dec(id, raw=True)` to see the exact
    body text, identify the 1-based, inclusive line range to replace --
    the `N+1` position is end-of-body: `begin = end = N+1` appends after
    the last line, `end = N+1` extends the range through the last line
    -- and call `update(id, type="dec", content, begin=..., end=...)`
    passing only the replacement lines. The server splices the fragment
    into the current on-disk body and validates the result as a whole
    document before writing anything, so every out-of-range line stays
    byte-identical.
  - **Whole-body replace** (a multi-section change, or whenever you are
    uncertain about the line range): call `update(id, type="dec", content)`
    with no `begin`/`end` -- `content` is then the full replacement body:
    read the current body first (step 1) and carry forward every section
    you are not intentionally changing, or it will be dropped.
    `id`/`type`/`status`/`created`/`version` are preserved automatically
    regardless of what you submit; only `updated` changes.
- A change to `status` -> `set_status(id, type="dec", status)` instead
  -- `update` never accepts or changes `status`. `status` must be one
  of: draft, proposed, accepted, rejected, superseded, deprecated.
  Mention this as a separate, optional follow-up -- e.g. `accepted`
  once the decision has genuinely been agreed to, `rejected` or
  `superseded` if the decision was not adopted or is replaced by
  another one -- do not call `set_status` unless the user actually
  asks for a status change.

## 5. Check the schema, and validate before writing if useful

Fetch `specmgr://dec/schema` to confirm field names and constraints
before drafting the replacement body. Optionally call
`validate_dec(content, full=False)` beforehand to dry-run the new body
without writing anything -- `update` already performs the same
validation internally, so this step is never required, only a
convenience.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat src/biz/dfch/specmgr/general/resources/__init__.py\necho \"=== general/data listing ===\"\nls src/biz/dfch/specmgr/general/data/\necho \"=== rsk/resources/tara.py ===\"\ncat src/biz/dfch/specmgr/rsk/resources/tara.py\necho \"=== rsk_tara.md ===\"\ncat src/biz/dfch/specmgr/rsk/data/rsk_tara.md"
}
```

**Output:**

```
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

"""MCP resource registrations that are not specific to any single document
domain.

See ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain".

``version`` registers the server package version resource. ``iso25010``
registers the ISO/IEC 25010:2023 product quality model resource. Domain-
specific resources (e.g. ``adr_list``/``adr_get``) live under their own
domain package instead (``biz.dfch.specmgr.adr.resources``). Import this
package to load all cross-cutting resources at once::

    from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)
"""

from . import iso25010, version  # noqa: F401

__all__ = [
    "iso25010",
    "version",
]
=== general/data listing ===
general_compact_history_instructions.md
general_iso25010.md
=== rsk/resources/tara.py ===
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

"""Resource: specmgr://rsk/tara (Task 3.15).

Static, domain-knowledge resource: what TARA is (Transfer, Accept, Reduce,
Avoid), the four valid ``## Strategy`` words verbatim (exactly the model's
closed set), when and how to apply each, and how the strategy interacts with
``## Mitigation`` and the frontmatter ``status`` vocabulary.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://tsk/example``/``/template``) rather than parsed into structured
models -- the audience is an LLM agent that needs to read guidance, not code
that needs data (``specmgr://iso25010``'s structured parse is the precedent
for machine-readable reference data; these are prose). The content was
drafted in Phase 1 of ``.specmgr/feat/feat-15-add-artifact-type-risk`` and
packaged here in Phase 3; the TARA words have a single source of truth
(``rsk.models.v1.body.Strategy``'s closed set).
"""

from __future__ import annotations

from ...general.tools._packaged_data import read_packaged_text
from ...server import mcp


@mcp.resource(
    "specmgr://rsk/tara",
    name="rsk_tara",
    title="Risk (RSK) TARA Guidance",
    description=(
        "What TARA is (Transfer, Accept, Reduce, Avoid), the four valid `## Strategy` words, "
        "and when and how to apply each, as raw markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def tara() -> str:
    """Return the packaged TARA guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other ``rsk`` resource/tool -- reads the file fresh on
    every call.

    Returns
    -------
    str
        The TARA guidance document's raw markdown source.
    """
    return read_packaged_text("rsk", "tara")
=== rsk_tara.md ===
# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit. Shift the consequence
  to a party better able to bear it: an insurer, a vendor contract with
  liability clauses, or another organization that owns the exposure.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe. Do not proceed with the activity that
  carries it: eliminate the `## Cause` or the `## Trigger` (drop the
  feature, change the design, refuse the input). An `avoid` strategy
  typically closes the risk entry (`status: closed`/`dropped`) rather than
  leaving residual exposure.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded. Apply `## Mitigation`
  measures that lower the probability or the impact (guardrails, checks,
  whitelists, redundancy) so the residual risk lands in a lower zone.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded. No treatment is warranted: keep
  `## Mitigation` as `none` and monitor the risk in the register.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label, and a risk
near a quadrant boundary may legitimately take an adjacent strategy.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments and
holds the concrete measures bridging `## Initial Assessment` and
`## Residual Assessment`:

- `reduce`: concrete measures are mandatory (e.g. "Replace the parser with
  a maintained library; restrict uploads to a format whitelist."). The
  residual assessment must reflect their effect.
- `transfer`: name the transfer mechanism (contract clause, insurance
  policy, delegated owner). Residual exposure is what remains after the
  transfer.
- `avoid`: describe what is eliminated (the cause, the trigger, or the
  activity itself).
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — `## Mitigation` treatment is in progress (typically
  `strategy: reduce` or `transfer`); the residual assessment is provisional
  until the measures land.
- `accepted` — the residual risk is formally accepted (typically
  `strategy: accept`, or a `reduce` whose residual zone is tolerated).
- `occurred` — the risk event materialized; the entry is tracked as an
  incident alongside its mitigation history.
- `closed` — resolved or expired (typically `strategy: avoid`, or all
  measures completed and verified).
- `dropped` — removed from the register (not a real risk, a duplicate, or
  out of scope).

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields: an `open` entry already has
a `strategy` (every risk in a register has a disposition), and a
`mitigating` entry's `strategy` is whatever response is being executed.

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.4s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat tests/rsk/resources/test_tara.py\necho \"=== general/resources tests dir ===\"\nfind tests/general/resources -type f | grep -v __pycache__"
}
```

**Output:**

```
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

"""Tests for the `specmgr://rsk/tara` resource (`rsk.resources.tara.tara`)."""

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from biz.dfch.specmgr.general.tools import _packaged_data
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1 import Strategy
from biz.dfch.specmgr.rsk.resources.tara import tara

#: A bullet line holding exactly one backticked lowercase word -- the shape the
#: resource uses to document the four valid `## Strategy` words verbatim.
_VALID_WORD_BULLET = re.compile(r"^- `([a-z]+)`$", re.MULTILINE)

#: The four words the resource must document as the closed TARA set, in order.
_EXPECTED_TARA_WORDS = ["transfer", "accept", "reduce", "avoid"]

#: TARRA-era words the resource explicitly calls out as *not* accepted.
_REJECTED_WORDS = ["tolerate", "assign", "recover"]


class TestRskTaraResource(unittest.TestCase):
    """Tests for the `tara` resource function."""

    def test_returns_real_packaged_content(self):
        """Against the real, committed packaged data file, without any patching."""
        sut = tara

        result = sut()

        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("# TARA"))
        self.assertIn("## When to apply each strategy", result)
        self.assertIn("## Interaction with `## Mitigation`", result)
        self.assertIn("## Interaction with the frontmatter `status`", result)

    def test_documents_exactly_the_four_valid_tara_words(self):
        """The documented valid-word bullets must be exactly the model's closed TARA set."""
        result = tara()

        words = _VALID_WORD_BULLET.findall(result)

        self.assertEqual(words, _EXPECTED_TARA_WORDS)

    def test_documented_words_are_accepted_by_the_model(self):
        """Every documented word must parse through `Strategy`'s own validator."""
        for word in _EXPECTED_TARA_WORDS:
            with self.subTest(word=word):
                sut = Strategy.from_text(format_text(f"## Strategy\n\n{word}\n"))

                self.assertEqual(sut.value.text, word)

    def test_documented_rejected_words_are_rejected_by_the_model(self):
        """Every word the resource calls out as invalid must fail `Strategy`'s own validator."""
        for word in _REJECTED_WORDS:
            with self.subTest(word=word):
                with self.assertRaises(ValidationError):
                    Strategy.from_text(format_text(f"## Strategy\n\n{word}\n"))

    def test_reads_fresh_on_every_call(self):
        """No in-memory cache -- a second call must reflect an on-disk change since the first."""
        with tempfile.TemporaryDirectory() as tmp:
            tara_path = Path(tmp) / "rsk_tara.md"
            tara_path.write_text("first", encoding="utf-8")

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=tara_path):
                sut = tara

                first = sut()
                tara_path.write_text("second", encoding="utf-8")
                second = sut()

            self.assertEqual(first, "first")
            self.assertEqual(second, "second")

    def test_raises_file_not_found_when_missing(self):
        """A missing packaged rsk_tara.md must propagate FileNotFoundError uncaught."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "does-not-exist.md"

            with mock.patch.object(_packaged_data, "packaged_data_path", return_value=missing_path):
                sut = tara

                with self.assertRaises(FileNotFoundError):
                    sut()


if __name__ == "__main__":
    unittest.main()
=== general/resources tests dir ===
tests/general/resources/test_iso25010.py
tests/general/resources/test_version.py
tests/general/resources/__init__.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 20.3s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && ls docs/*.json 2>/dev/null; ls src/biz/dfch/specmgr/vcr/data/ 2>/dev/null\necho \"---general/data listing (again, for confirmation)---\"\nls src/biz/dfch/specmgr/general/data/\necho \"---general/resources listing---\"\nls src/biz/dfch/specmgr/general/resources/ | grep -v __pycache__\necho \"---general/resources/version.py and iso25010.py for pattern (brief)---\"\nsed -n '1,40p' src/biz/dfch/specmgr/general/resources/iso25010.py"
}
```

**Output:**

```
docs/dec_schema.json
docs/feat_schema.json
docs/gol_schema.json
docs/prb_schema.json
docs/qa_schema.json
docs/req_schema.json
docs/rsk_schema.json
docs/tsk_schema.json
docs/uc_schema.json
vcr_example.md
vcr_template.md
---general/data listing (again, for confirmation)---
general_compact_history_instructions.md
general_iso25010.md
---general/resources listing---
__init__.py
iso25010.py
version.py
---general/resources/version.py and iso25010.py for pattern (brief)---
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

"""Resource: specmgr://iso25010 (Task 0.8.3).

Reads the packaged ISO/IEC 25010:2023 product quality model markdown
(``general/data/general_iso25010.md``, via
``general.tools._packaged_data.read_packaged_text``) and parses it into a
structured :class:`~biz.dfch.specmgr.models.Iso25010`, mirroring
``req/resources/req_schema.py``'s packaged-data-read style.
"""

from __future__ import annotations

from ...models import Iso25010, parse_iso25010
from ...server import mcp
from ..tools._packaged_data import read_packaged_text


@mcp.resource(
    "specmgr://iso25010",
    name="iso25010",
    title="ISO/IEC 25010:2023 Product Quality Model",
    description=(
        "The nine main characteristics (and their sub-characteristics) of the ISO/IEC "
        "25010:2023 system/software product quality model, each with a description."

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 1010.6s)

Good, I have everything needed. Now let's write the comprehensive Phase 3 task prompt.

**Tool: task**

**Input:**

````json
{
  "description": "Implement VCR Phase 3",
  "prompt": "You are implementing exactly ONE phase of a feature plan for the biz.dfch.SpecMgr repo. Do NOT touch `server.py`'s import line, `AGENTS.md`, top-level `README.md`, or `.pre-commit-config.yaml` (those are Phase 4). Do NOT commit. Stop and report back when this phase is done or if you hit a blocker.\n\n## Plan location\nRead in full: `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/README.md` (Task List's \"Phase 3: Resources and prompts\", and the persisted \"Candidate `specmgr://dtais` resource sketch\" in Design Notes -- read that sketch carefully, it is your starting point for Task 3.3).\nRead `.specmgr/conventions.md` at the repo root for mandatory coding conventions.\n\nPhases 1-2 are already committed: `vcr/models/v1/` (schema+parser) and `vcr/tools/` (8 tools) + generic `update`/`set_status` dispatch entries all exist and are tested. Read `src/biz/dfch/specmgr/vcr/models/v1/__init__.py` and `src/biz/dfch/specmgr/vcr/tools/__init__.py` to see exactly what's importable. `src/biz/dfch/specmgr/vcr/data/vcr_example.md`/`vcr_template.md` already exist (packaged, byte-for-byte copies of the finalized `.specmgr/feat/feat-33-vcr/example.md`/`template.md`).\n\n## Phase to implement: \"Phase 3: Resources and prompts\"\n\nExact tasks from the plan (verbatim):\n- Task 3.1: `specmgr://vcr/schema`, `.../example`, `.../template` resources.\n- Task 3.2: `create_vcr`/`update_vcr` prompts.\n- Task 3.3: `general/data/general_dtais.md` content (fill in the draft outline persisted in Design Notes), `general/resources/dtais.py` (`specmgr://dtais`), registered in `general/resources/__init__.py`; unit tests.\n\n## Part A: `specmgr://vcr/schema` resource + its generator plumbing\n\nUnlike `example`/`template` (already-packaged markdown), the schema resource needs a JSON Schema file to exist first. Read `src/biz/dfch/specmgr/commands/schema.py` in full (the generic, doc-type-agnostic `specmgr schema` CLI command). Mirror its `dec` entries exactly:\n1. Add `from ..vcr.models.v1 import SCHEMA_COMMENT_VERSION as VCR_SCHEMA_COMMENT_VERSION` and `from ..vcr.models.v1.document import VcrDocument` imports (alphabetically positioned -- `vcr` sorts after `uc` and before nothing else currently in that import block, so it goes last among the per-domain imports, right before `_DEFAULT_OUTPUT_DIR = DOCS_DIR`).\n2. Add a `generate_vcr_schema() -> str` function mirroring `generate_dec_schema` exactly (docstring adjusted for VCR naming), using `VcrDocument.model_json_schema()` and `VCR_SCHEMA_COMMENT_VERSION`.\n3. Add `\"vcr\": generate_vcr_schema,` to the `_GENERATORS` registry dict, in alphabetical position (the dict is alphabetically sorted: `dec, feat, gol, prb, qa, req, rsk, tsk, uc` -- `vcr` sorts after `uc`, so append it last).\n4. Run `uv run --frozen specmgr schema --type vcr` to generate `docs/vcr_schema.json`, and separately `uv run --frozen specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data` to generate the packaged copy `src/biz/dfch/specmgr/vcr/data/vcr_schema.json` (mirrors every other domain's committed packaged JSON Schema copy, read by the resource via `importlib.resources`, not the `docs/` one). Both commands must succeed with exit code 0 the *second* time you run them (drift-check semantics: exit 1 only means \"changed\", which is expected/fine on first generation).\n5. Add `src/biz/dfch/specmgr/vcr/resources/vcr_schema.py` mirroring `src/biz/dfch/specmgr/dec/resources/dec_schema.py` exactly (renaming `Dec`/`dec` -> `Vcr`/`vcr`, URI `specmgr://vcr/schema`, reads `read_packaged_text(\"vcr\", \"schema\", \"json\")`).\n\n## Part B: `specmgr://vcr/example`/`specmgr://vcr/template` resources\n\nMirror `src/biz/dfch/specmgr/dec/resources/dec_example.py` and `dec_template.py` exactly (rename `Dec`/`dec` -> `Vcr`/`vcr`, URIs `specmgr://vcr/example`/`specmgr://vcr/template`, reads `read_packaged_text(\"vcr\", \"example\")`/`(\"vcr\", \"template\")`).\n\nAdd `src/biz/dfch/specmgr/vcr/resources/__init__.py` mirroring `dec/resources/__init__.py` exactly (re-exports `vcr_example`, `vcr_schema`, `vcr_template`; module docstring adjusted).\n\n## Part C: `create_vcr`/`update_vcr` prompts\n\nRead `src/biz/dfch/specmgr/dec/prompts/create_dec.py`, `update_dec.py`, `__init__.py`, and their packaged instruction files `src/biz/dfch/specmgr/dec/data/dec_create_instructions.md`/`dec_update_instructions.md` in full first.\n\n1. `src/biz/dfch/specmgr/vcr/prompts/create_vcr.py` -- mirror `create_dec.py` exactly (same `Template`/`$topic` substitution shape, same narration-only contract -- never calls `TodoWrite`/`question`/`list_vcr`/`create_vcr` itself, only narrates that sequence).\n2. `src/biz/dfch/specmgr/vcr/prompts/update_vcr.py` -- mirror `update_dec.py` exactly (`$id`/`$instructions` substitution, `raw=True` for line-range line numbers, narration-only contract).\n3. `src/biz/dfch/specmgr/vcr/prompts/__init__.py` -- mirror `dec/prompts/__init__.py` exactly.\n4. `src/biz/dfch/specmgr/vcr/data/vcr_create_instructions.md` -- adapt `dec_create_instructions.md`'s exact structure/tone to VCR's actual schema instead of DEC's. Use this section recap instead of DEC's:\n   - `# {title}` -- H1, free-form.\n   - `## Verifies` -- mandatory: optional leading HTML comment, then a single-line `REQ|UC <uuid>: <title>` value (a standard 8-4-4-4-12 hex UUID; `REQ` or `UC` literal type tag), then a mandatory one-paragraph `notes` paraphrase of why this REQ/UC is verified here.\n   - `## Coverage` -- mandatory: a single-line closed-vocabulary value, one of `full`/`partial`/`none`.\n   - `## Acceptance Criteria` -- mandatory, at least one `### AC-NNN (Method): <criterion text>` entry (3-digit zero-padded number starting at `001`, gaps allowed but no duplicate numbers; `Method` is one of the closed DTAIS set -- Demonstration, Test, Analysis, Inspection, Special, exactly as spelled, case-sensitive). Each entry may optionally carry a free-form descriptive paragraph directly under the heading, and/or a `#### Test Steps` numbered procedure list -- both independently optional.\n   - `## More Information` -- optional freeform supplementary text.\n   - `## Updates` -- optional, last section if present: an optional leading HTML comment (conventionally \"Newest entry first\"), then dated `### {title}` entries, each with a mandatory lead paragraph.\n   Section order is binding: Verifies -> Coverage -> Acceptance Criteria -> More Information -> Updates. Mention `create_vcr` builds the entire frontmatter (`id`/`type`/`status=\"draft\"`/`created`/`updated`/`version`) automatically -- the caller only ever supplies body markdown. Reference `specmgr://vcr/template`/`specmgr://vcr/example`/`specmgr://vcr/schema` and the `specmgr://dtais` resource (Part D below) for the DTAIS method vocabulary. Include the step-0 \"check `list_vcr` for a near-duplicate first\" convention (mirroring DEC's own step 0), and the same tool-call-sequence ending in `create_vcr(content)` / optional `validate_vcr(content, full=False)`.\n5. `src/biz/dfch/specmgr/vcr/data/vcr_update_instructions.md` -- adapt `dec_update_instructions.md`'s exact structure/tone the same way: reading current state via `get_vcr(id)`, showing which of `verifies`/`coverage`/`acceptance_criteria` (always present) and `more_information`/`updates` (optional) are present, mapping the requested change to `update(id, type=\"vcr\", content, begin=, end=)` (line-range, using `get_vcr(id, raw=True)` for line numbers) or whole-body replace, and `set_status(id, type=\"vcr\", status)` for a status-only change (status must be one of `draft`/`progress`/`complete`/`approved` -- NOT DEC's six-value set). Reference `specmgr://vcr/schema`, optional `validate_vcr(content, full=False)` dry run.\n\n## Part D: `specmgr://dtais` cross-cutting resource (general/, not vcr/)\n\nRead `src/biz/dfch/specmgr/rsk/resources/tara.py` and `src/biz/dfch/specmgr/rsk/data/rsk_tara.md` in full first -- your primary structural precedent (raw-markdown domain-knowledge resource, same shape, just cross-cutting instead of domain-scoped). Also read `src/biz/dfch/specmgr/general/resources/__init__.py` and `src/biz/dfch/specmgr/general/resources/iso25010.py` for the `general/resources/` package conventions.\n\n1. `src/biz/dfch/specmgr/general/data/general_dtais.md` -- write the full content, using the plan README's persisted draft outline as your starting point/skeleton but **filling in every `...`/TODO placeholder** with real guidance (mirror `rsk_tara.md`'s depth and structure exactly: a closed-vocabulary bullet list of the 5 words with a one-line definition each, a \"## When to apply each method\" section giving concrete guidance per method -- informed by INCOSE's Guide for Writing Requirements' and the MITRE SE Guide's own Demonstration/Test/Analysis/Inspection definitions (available at `.specmgr/feat/feat-32-sysrs/incose-guide-writing-requirements-2019.md` if you want to check it, though you can also write from well-established V&V domain knowledge directly) plus this feature's own addition, `Special` (any other verification approach: formal certification/compliance sign-off, supplier certificate of conformance, contractually-mandated special process) -- and a final \"## Relationship to `## Coverage`\" section explaining how an AC's method interacts with the overall `full`/`partial`/`none` coverage signal (e.g. `full` coverage typically means every AC has been verified via its stated method with a passing result; `partial` means some ACs are still pending/outstanding -- mirror `example.md`'s own AC-004-pending-Special-certification scenario as a concrete illustration). The five method words in the document MUST exactly match, verbatim and in the same order, the closed set enforced by `src/biz/dfch/specmgr/vcr/models/v1/body.py`'s `_AC_HEADING_PATTERN` (`Demonstration`, `Test`, `Analysis`, `Inspection`, `Special`) -- a test (see below) will assert this.\n2. `src/biz/dfch/specmgr/general/resources/dtais.py` -- copy the plan README's persisted sketch as your starting point, adjusted only for style/lint compliance; mirror `rsk/resources/tara.py`'s docstring depth.\n3. Update `src/biz/dfch/specmgr/general/resources/__init__.py`: add `dtais` to the `from . import ...` line and `__all__` (alphabetical: `dtais, iso25010, version`), per the plan's own persisted sketch.\n\n## Tests (mirror existing precedent test files exactly, adapted for VCR/DTAIS)\n\n- `tests/vcr/resources/test_vcr_schema.py`, `test_vcr_example.py`, `test_vcr_template.py`, `__init__.py` -- mirror `tests/dec/resources/test_dec_schema.py`/`test_dec_example.py`/`test_dec_template.py`.\n- `tests/vcr/prompts/test_create_vcr.py`, `test_update_vcr.py`, `__init__.py` -- mirror `tests/dec/prompts/test_create_dec.py`/`test_update_dec.py`.\n- `tests/general/resources/test_dtais.py` -- mirror `tests/rsk/resources/test_tara.py`'s structure exactly, but cross-check the documented method words against `vcr.models.v1.body`'s actual closed DTAIS set (import whatever is needed from there -- e.g. re-derive the expected word list from the `AcceptanceCriterion`'s own heading-pattern regex group, or hardcode the same 5-word list and add a second test that constructs a real `### AC-001 ({word}): text` fixture through `AcceptanceCriteria`/`Vcr.from_text` for each word to confirm it's genuinely accepted end-to-end, mirroring `test_tara.py`'s `test_documented_words_are_accepted_by_the_model`/`test_documented_rejected_words_are_rejected_by_the_model` pair -- use an invented rejected word like `\"Certification\"` (VCR's own retired 5th-method name, per this feature's Decisions Made) as the rejected-word case).\n- Read `tests/dec/tools/test_get_dec_example.py`-style \"read the real packaged file, no patching\" test convention and apply it to the new schema resource test too (assert `result[\"$comment\"] == \"v1\"` or similar, and that `\"vcr\"` appears somewhere sensible, e.g. in a `$defs` type discriminator).\n\n## Phase-end quality gate (run yourself, report exact command output/summary)\n\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\nAll four must pass cleanly. Also re-run `uv run --frozen specmgr schema --type vcr` and `--type vcr --output-dir src/biz/dfch/specmgr/vcr/data` one more time at the very end and confirm BOTH now exit 0 (no drift) since your own generator code and `VcrDocument` schema are now stable -- if either exits 1, the committed JSON is stale relative to your own generator; regenerate and re-check.\n\n## Progress-section discipline\n\nUpdate `.specmgr/feat/feat-33-vcr/README.md`'s Progress section: mark Phase 3's three tasks `[x]`, update Current Status, prepend one new dated Recent-Updates entry (mirror the tone/detail of the Phase 0/1/2 entries already there). You may also mark ACC-006 (verifies REQ-006, the `specmgr://dtais` resource) as satisfied in the Acceptance Criteria list's own text if you're confident it's fully met, but leave the actual `[ ]`/`[x]` checkbox mark itself for me (the orchestrator) to confirm.\n\n## Report back\n\n1. Full list of files created/modified, grouped by area (schema plumbing, vcr/resources, vcr/prompts + data, general/dtais, tests).\n2. Quality-gate results (pass/fail + test count) and the final drift-free confirmation for both `specmgr schema --type vcr` invocations.\n3. Confirmation you did NOT touch `server.py`, `AGENTS.md`, top-level `README.md`, or `.pre-commit-config.yaml`.\n4. Any blockers or genuine ambiguities not resolved by the plan text or precedent (stop and ask rather than guessing) -- in particular, flag if you had to make any non-mechanical judgment call while writing `general_dtais.md`'s \"When to apply each method\" guidance, so I can review it.\n\nDo NOT commit anything.",
  "subagent_type": "phase-implementer"
}
````

**Output:**

```
<task id="ses_fa9083b50ffe2XV91WwvOjRVtm" state="completed">
<task_result>
All green. Final report:

## Summary

### Files created/modified (grouped by area)

**Schema plumbing** (`commands/schema.py`):
- Added `VCR_SCHEMA_COMMENT_VERSION`/`VcrDocument` imports (alphabetically last, after `uc`), `generate_vcr_schema()`, and a `"vcr"` entry in `_GENERATORS`.
- Generated `docs/vcr_schema.json` and the packaged `src/biz/dfch/specmgr/vcr/data/vcr_schema.json`.

**`vcr/resources/`** (new):
- `vcr_schema.py`, `vcr_example.py`, `vcr_template.py`, `__init__.py` — mirror `dec/resources/` file-for-file.

**`vcr/prompts/`** (new):
- `create_vcr.py`, `update_vcr.py`, `__init__.py` — mirror `dec/prompts/` file-for-file.
- `vcr/data/vcr_create_instructions.md`, `vcr/data/vcr_update_instructions.md` — adapted from `dec`'s instructions to VCR's own section/status/DTAIS vocabulary.

**`general/dtais`** (new, cross-cutting):
- `general/data/general_dtais.md` — full DTAIS guidance (5 method words verbatim/in order matching `body.py`'s `_AC_HEADING_PATTERN`, "When to apply each method", "Relationship to `## Coverage`").
- `general/resources/dtais.py` — `specmgr://dtais` resource.
- `general/resources/__init__.py` — registered `dtais` alongside `iso25010`/`version`.

**Tests** (new):
- `tests/vcr/resources/{__init__,test_vcr_schema,test_vcr_example,test_vcr_template}.py`
- `tests/vcr/prompts/{__init__,test_create_vcr,test_update_vcr}.py`
- `tests/general/resources/test_dtais.py`

**Progress doc**: `.specmgr/feat/feat-33-vcr/README.md` — Phase 3 tasks marked `[x]`, Current Status updated, new dated Updates entry prepended.

All new/modified files are `git add`-staged, **not committed**.

### Quality gate results
- `ruff format --check`: pass (1378 files already formatted)
- `ruff check`: pass (all checks passed)
- `vulture src/ whitelist.py --min-confidence 60`: pass (no output, no new whitelist entries needed)
- `unittest discover`: **2452 tests, OK** (up from 2400 — 52 new tests)
- `specmgr schema --type vcr`: exit 0, unchanged
- `specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`: exit 0, unchanged

### Confirmation
Did **not** touch `server.py`, `AGENTS.md`, top-level `README.md`, or `.pre-commit-config.yaml` (verified via `git status`).

### Design decisions made (non-mechanical judgment calls)
1. **`general/resources/dtais.py` import order**: the plan's persisted sketch had `from ..tools._packaged_data import ...` before `from ...server import mcp`, but this codebase's actual isort convention (confirmed against `general/resources/iso25010.py`) sorts `...server` before `..tools` lexicographically (`.` < letters). Corrected to match.
2. **`general_dtais.md` "When to apply each method" content** — please review: I wrote concrete per-method guidance (Demonstration vs. Test distinguished by presence/absence of a quantitative threshold; Analysis for calculation/pre-existence-of-system cases; Inspection for artifact-only examination; Special for external certification/compliance) from established V&V domain knowledge, not copied from a single source. This is exactly the "how to write DTAIS guidance" judgment call the task asked me to flag.
3. **Rejected-word test semantics for DTAIS** (`tests/general/resources/test_dtais.py`): unlike RSK's `Strategy` (a `field_validator`-checked value, rejecting with `pydantic.ValidationError`), `AcceptanceCriterion` is a regex-`@alias`-matched heading class, so an invalid method word (`"Certification"`) fails via `AssertionError` (alias mismatch), not `ValidationError`. I verified this empirically before writing the test and used `AssertionError` accordingly — flagging in case a different error-channel expectation was intended.
4. Two instruction-file line-wraps in `vcr_update_instructions.md` needed re-wrapping so contiguous test-asserted substrings (`"1-based, inclusive line range"`, `"separate, optional"`) didn't straddle a line break — cosmetic only, no semantic change.

No blockers for Phase 4.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 8.2s)

Let me independently verify Phase 3's work thoroughly.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git status --short"
}
```

**Output:**

```
M  .specmgr/feat/feat-33-vcr/README.md
A  docs/vcr_schema.json
M  src/biz/dfch/specmgr/commands/schema.py
A  src/biz/dfch/specmgr/general/data/general_dtais.md
M  src/biz/dfch/specmgr/general/resources/__init__.py
A  src/biz/dfch/specmgr/general/resources/dtais.py
A  src/biz/dfch/specmgr/vcr/data/vcr_create_instructions.md
A  src/biz/dfch/specmgr/vcr/data/vcr_schema.json
A  src/biz/dfch/specmgr/vcr/data/vcr_update_instructions.md
A  src/biz/dfch/specmgr/vcr/prompts/__init__.py
A  src/biz/dfch/specmgr/vcr/prompts/create_vcr.py
A  src/biz/dfch/specmgr/vcr/prompts/update_vcr.py
A  src/biz/dfch/specmgr/vcr/resources/__init__.py
A  src/biz/dfch/specmgr/vcr/resources/vcr_example.py
A  src/biz/dfch/specmgr/vcr/resources/vcr_schema.py
A  src/biz/dfch/specmgr/vcr/resources/vcr_template.py
A  tests/general/resources/test_dtais.py
A  tests/vcr/prompts/__init__.py
A  tests/vcr/prompts/test_create_vcr.py
A  tests/vcr/prompts/test_update_vcr.py
A  tests/vcr/resources/__init__.py
A  tests/vcr/resources/test_vcr_example.py
A  tests/vcr/resources/test_vcr_schema.py
A  tests/vcr/resources/test_vcr_template.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

Good — no server.py, AGENTS.md, README.md, or .pre-commit-config.yaml diffs. Let's review the DTAIS content and run the quality gate.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/general/data/general_dtais.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/general/data/general_dtais.md</path>
<type>file</type>
<content>
1: # DTAIS Verification Methods
2: 
3: The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
4: `## Acceptance Criteria` (and any other domain that needs to describe how
5: a criterion is verified):
6: 
7: - `Demonstration` -- observing the system in operation, without
8:   instrumented measurement, to confirm a qualitative or operational
9:   characteristic.
10: - `Test` -- exercising the system under controlled, instrumented
11:   conditions and comparing measured results against a quantitative
12:   threshold.
13: - `Analysis` -- using calculation, modeling, or simulation (not direct
14:   observation of the built system) to show a requirement is met.
15: - `Inspection` -- visual or procedural examination of the system,
16:   design artifacts, or source code, without operating the system.
17: - `Special` -- any other verification approach not covered by the four
18:   methods above, e.g. a formal third-party certification/compliance
19:   sign-off, a supplier's certificate of conformance, or another
20:   contractually-mandated special process.
21: 
22: ## When to apply each method
23: 
24: - **`Demonstration`** -- use when the criterion is about observable
25:   behavior under realistic operating conditions and a pass/fail
26:   judgment can be made by watching the system perform, without needing
27:   instrumented measurement or a controlled test environment. Typical
28:   for showing that a feature works end to end, that a workflow
29:   completes, or that a user-facing capability is present. Not
30:   appropriate when the criterion carries a quantitative threshold (a
31:   latency budget, a throughput number, an error-rate ceiling) --
32:   those need `Test` instead, since a demonstration cannot rigorously
33:   confirm a numeric bound.
34: - **`Test`** -- use when the criterion states (or implies) a
35:   quantitative, measurable threshold: a performance budget, a
36:   tolerance, a pass/fail count against a specified input set, a
37:   boundary condition. Requires a controlled, instrumented environment
38:   and a documented, repeatable procedure -- this is exactly what the
39:   optional `#### Test Steps` sub-section under an acceptance criterion
40:   is for. Prefer `Test` over `Demonstration` whenever the criterion can
41:   be reduced to a measured number compared against a threshold.
42: - **`Analysis`** -- use when direct observation of the built system is
43:   not practical, not yet possible, or not the most rigorous way to
44:   confirm the requirement: calculation, modeling, simulation, or a
45:   static review of a design or specification (e.g. confirming a
46:   latency budget is achievable given known per-component overheads,
47:   without running a live test). Also the right choice for criteria
48:   that must be verified before the relevant part of the system exists
49:   yet, or for requirements about characteristics (capacity margins,
50:   worst-case bounds) that are more reliably shown by calculation than
51:   by sampling a live system.
52: - **`Inspection`** -- use when the criterion is about the presence,
53:   form, or content of an artifact -- source code, configuration,
54:   documentation, an error-message contract -- rather than about
55:   runtime behavior. Verified by visual or procedural examination
56:   without operating the system (e.g. reviewing a handler's source for
57:   a required error-handling branch, or checking that a document
58:   contains a required section). Prefer `Inspection` over
59:   `Demonstration`/`Test` whenever the system does not need to be run at
60:   all to confirm the criterion.
61: - **`Special`** -- use for verification approaches that fall outside
62:   the other four methods entirely: a required third-party
63:   certification or compliance sign-off (e.g. a security or regulatory
64:   compliance review board), a supplier's certificate of conformance
65:   for a purchased component, or another contractually-mandated special
66:   process that the document's own author cannot execute or verify
67:   directly. `Special` criteria are often the last ones to close on a
68:   verification case record, since they depend on an external party's
69:   own schedule rather than the author's own test/analysis/inspection
70:   activity.
71: 
72: ## Relationship to `## Coverage`
73: 
74: `## Coverage` is the document-level roll-up of every `### AC-NNN
75: (Method): ...` entry's verification status, not a second, independent
76: outcome field:
77: 
78: - **`full`** -- every acceptance criterion has actually been verified
79:   via its stated method, with a passing result. There is no
80:   outstanding criterion, regardless of method -- a `full` verification
81:   case record with a `Special` criterion means the required
82:   certification/sign-off has already been obtained, not merely
83:   requested.
84: - **`partial`** -- at least one acceptance criterion has been verified
85:   successfully, but at least one other is still pending or outstanding.
86:   The typical pattern is a mix of methods the author can execute
87:   directly (`Demonstration`/`Test`/`Analysis`/`Inspection`, already
88:   passing) alongside a `Special` criterion still awaiting an external
89:   party's action -- e.g. an `AC-004 (Special): ...` criterion whose
90:   formal certification sign-off has not yet arrived, so the document's
91:   `## Coverage` is `partial` even though every criterion the author
92:   could verify directly has already passed. `## More Information` is
93:   the right place to record exactly what is still outstanding and why.
94: - **`none`** -- no acceptance criterion has been successfully verified
95:   yet, e.g. a freshly drafted verification case record whose criteria
96:   are defined but not yet executed against any method.
97: 
98: `## Coverage` therefore always reflects the least-verified criterion in
99: the set: one still-outstanding `Special` (or any other method's)
100: criterion is enough to keep the whole document at `partial`, no matter
101: how many other criteria have already passed.

(End of file - total 101 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.0s)

This is high-quality, well-reasoned content that correctly mirrors `example.md`'s own AC-004-pending scenario. Now let's run the quality gate independently.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo \"===check===\" && uv run --frozen ruff check 2>&1 | tail -10 && echo \"===vulture===\" && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1"
}
```

**Output:**

```
1378 files already formatted
===check===
All checks passed!
===vulture===

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 100.0s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && timeout 280 uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/full_test_run3.log 2>&1; echo \"EXIT:$?\"; grep -n \"Ran [0-9]* tests\\|^OK\\|FAILED\\|ERROR:\" /tmp/full_test_run3.log",
  "timeout": 290000
}
```

**Output:**

```
EXIT:0
9:Ran 2452 tests in 93.786s
11:OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.9s)

All 2452 tests pass. Let's confirm the schema drift check and inspect the new resource files.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen specmgr schema --type vcr; echo \"EXIT:$?\"\nuv run --frozen specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data; echo \"EXIT:$?\"\ngit status --short docs/vcr_schema.json src/biz/dfch/specmgr/vcr/data/vcr_schema.json"
}
```

**Output:**

```
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/vcr_schema.json (unchanged)
EXIT:0
✓ Wrote src/biz/dfch/specmgr/vcr/data/vcr_schema.json (unchanged)
EXIT:0
A  docs/vcr_schema.json
A  src/biz/dfch/specmgr/vcr/data/vcr_schema.json

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.4s)

Both confirmed unchanged/drift-free. Let's spot-check the resources/prompts files.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && cat src/biz/dfch/specmgr/general/resources/dtais.py"
}
```

**Output:**

```
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

"""Resource: specmgr://dtais -- the DTAIS verification-method vocabulary (feat-33-vcr Task 3.3).

Static, domain-knowledge resource: what DTAIS is (Demonstration, Test,
Analysis, Inspection, Special), the five valid ``### AC-NNN (Method):
...`` method words verbatim (exactly `vcr.models.v1.body`'s closed set),
when and how to apply each, and how the chosen method interacts with a
verification case record's document-level ``## Coverage`` signal.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://rsk/tara``/``specmgr://rsk/risk-matrix``) rather than parsed
into structured models -- the audience is an LLM agent that needs to read
guidance, not code that needs data (``specmgr://iso25010``'s structured
parse is the precedent for machine-readable reference data; this is
prose). Registered as a flat, top-level ``specmgr://dtais`` URI (like
``specmgr://iso25010``, not ``specmgr://vcr/dtais``) since the DTAIS
vocabulary is domain-knowledge that other domains (e.g. a future `sysrs`)
may want to reference too, not owned by `vcr`'s own schema -- see
`.specmgr/feat/feat-33-vcr/README.md` REQ-006/Design Notes for the full
rationale.
"""

from __future__ import annotations

from ...server import mcp
from ..tools._packaged_data import read_packaged_text


@mcp.resource(
    "specmgr://dtais",
    name="dtais",
    title="DTAIS Verification Method Vocabulary",
    description=(
        "What DTAIS is (Demonstration, Test, Analysis, Inspection, Special), the five valid "
        "`### AC-NNN (Method): ...` method words, and when and how to apply each, as raw "
        "markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def dtais() -> str:
    """Return the packaged DTAIS guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other cross-cutting ``general`` resource -- reads the
    file fresh on every call.

    Returns
    -------
    str
        The DTAIS guidance document's raw markdown source.
    """
    return read_packaged_text("general", "dtais")

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.1s)

This matches the plan's sketch closely (with the import-order correction noted). Everything checks out. Let's commit Phase 3.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add -A && git status --short | wc -l"
}
```

**Output:**

```
24

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 188.4s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr resources/prompts and specmgr://dtais (Phase 3)\" -m \"commands/schema.py gains generate_vcr_schema + registry entry;\ndocs/vcr_schema.json and the packaged src/.../vcr/data/vcr_schema.json\ncopy generated and confirmed drift-free.\n\nvcr/resources/ (specmgr://vcr/schema, .../example, .../template) and\nvcr/prompts/ (create_vcr, update_vcr, with their own packaged\ninstruction files) mirror the dec domain's shape.\n\nCross-cutting specmgr://dtais resource (REQ-006): general/data/\ngeneral_dtais.md documents the closed 5-word DTAIS vocabulary\n(Demonstration, Test, Analysis, Inspection, Special), when to apply\neach, and its relationship to ## Coverage; general/resources/dtais.py\nregistered alongside iso25010/version.\n\n52 new tests (2452 total). No server.py/AGENTS.md/README.md/\npre-commit-config.yaml changes yet (Phase 4).\"",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Failed
- hook id: specmgr-docs
- exit code: 1
- files were modified by this hook

✓ Wrote 393 module file(s) to /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/api
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/GENERATED.md
diff --git a/docs/GENERATED.md b/docs/GENERATED.md
index 87fc267..1e76999 100644
--- a/docs/GENERATED.md
+++ b/docs/GENERATED.md
@@ -129,6 +129,7 @@ First-line docstrings from each module, organized by domain:
 - `general/prompts/__init__.py` — MCP prompt registrations that are not specific to any single document
 - `general/prompts/compact_history.py` — ``@mcp.prompt()``: compact_history (Various improvements, Task 0.21).
 - `general/resources/__init__.py` — MCP resource registrations that are not specific to any single document
+- `general/resources/dtais.py` — Resource: specmgr://dtais -- the DTAIS verification-method vocabulary (feat-33-vcr Task 3.3).
 - `general/resources/iso25010.py` — Resource: specmgr://iso25010 (Task 0.8.3).
 - `general/resources/version.py` — Resource: specmgr://version — MCP server package version number.
 - `general/tools/__init__.py` — MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).
@@ -436,6 +437,13 @@ First-line docstrings from each module, organized by domain:
 - `vcr/models/v1/frontmatter.py` — Verification Case Record (VCR) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
 - `vcr/models/v1/parser.py` — Parse raw verification case record (VCR) ``.md`` text into a :class:`VcrDocument`.
 - `vcr/models/v1/summary.py` — Pydantic model for one line of VCR listing output (Phase 2, ``list_vcr``).
+- `vcr/prompts/__init__.py` — MCP prompt wrappers for Verification Case Records (Task 3.2).
+- `vcr/prompts/create_vcr.py` — ``@mcp.prompt()``: create_vcr (Task 3.2).
+- `vcr/prompts/update_vcr.py` — ``@mcp.prompt()``: update_vcr (Task 3.2).
+- `vcr/resources/__init__.py` — MCP resource registrations for Verification Case Record (VCR) documents (Task 3.1).
+- `vcr/resources/vcr_example.py` — Resource: specmgr://vcr/example (Task 3.1).
+- `vcr/resources/vcr_schema.py` — Resource: specmgr://vcr/schema (Task 3.1, packaged data).
+- `vcr/resources/vcr_template.py` — Resource: specmgr://vcr/template (Task 3.1).
 - `vcr/tools/__init__.py` — MCP tool wrappers for verification case records (mirrors ``dec/tools/``'s own shape).
 - `vcr/tools/_io.py` — Thin file read helpers over ``parse_vcr`` (Task 2.1).
 - `vcr/tools/_lock.py` — Per-document in-process lock guarding verification case record mutations.
@@ -452,4 +460,4 @@ First-line docstrings from each module, organized by domain:
 
 ## Test Coverage
 
-**Test files**: 299
+**Test files**: 305
diff --git a/docs/api/README.md b/docs/api/README.md
index 157b425..3ad4058 100644
--- a/docs/api/README.md
+++ b/docs/api/README.md
@@ -109,6 +109,7 @@ Auto-generated API documentation for `biz.dfch.specmgr`.
 - [`biz.dfch.specmgr.general.prompts`](biz.dfch.specmgr.general.prompts.md) — MCP prompt registrations that are not specific to any single document
 - [`biz.dfch.specmgr.general.prompts.compact_history`](biz.dfch.specmgr.general.prompts.compact_history.md) — ``@mcp.prompt()``: compact_history (Various improvements, Task 0.21).
 - [`biz.dfch.specmgr.general.resources`](biz.dfch.specmgr.general.resources.md) — MCP resource registrations that are not specific to any single document
+- [`biz.dfch.specmgr.general.resources.dtais`](biz.dfch.specmgr.general.resources.dtais.md) — Resource: specmgr://dtais -- the DTAIS verification-method vocabulary (feat-33-vcr Task 3.3).
 - [`biz.dfch.specmgr.general.resources.iso25010`](biz.dfch.specmgr.general.resources.iso25010.md) — Resource: specmgr://iso25010 (Task 0.8.3).
 - [`biz.dfch.specmgr.general.resources.version`](biz.dfch.specmgr.general.resources.version.md) — Resource: specmgr://version — MCP server package version number.
 - [`biz.dfch.specmgr.general.tools`](biz.dfch.specmgr.general.tools.md) — MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).
@@ -378,6 +379,13 @@ Auto-generated API documentation for `biz.dfch.specmgr`.
 - [`biz.dfch.specmgr.vcr.models.v1.frontmatter`](biz.dfch.specmgr.vcr.models.v1.frontmatter.md) — Verification Case Record (VCR) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
 - [`biz.dfch.specmgr.vcr.models.v1.parser`](biz.dfch.specmgr.vcr.models.v1.parser.md) — Parse raw verification case record (VCR) ``.md`` text into a :class:`VcrDocument`.
 - [`biz.dfch.specmgr.vcr.models.v1.summary`](biz.dfch.specmgr.vcr.models.v1.summary.md) — Pydantic model for one line of VCR listing output (Phase 2, ``list_vcr``).
+- [`biz.dfch.specmgr.vcr.prompts`](biz.dfch.specmgr.vcr.prompts.md) — MCP prompt wrappers for Verification Case Records (Task 3.2).
+- [`biz.dfch.specmgr.vcr.prompts.create_vcr`](biz.dfch.specmgr.vcr.prompts.create_vcr.md) — ``@mcp.prompt()``: create_vcr (Task 3.2).
+- [`biz.dfch.specmgr.vcr.prompts.update_vcr`](biz.dfch.specmgr.vcr.prompts.update_vcr.md) — ``@mcp.prompt()``: update_vcr (Task 3.2).
+- [`biz.dfch.specmgr.vcr.resources`](biz.dfch.specmgr.vcr.resources.md) — MCP resource registrations for Verification Case Record (VCR) documents (Task 3.1).
+- [`biz.dfch.specmgr.vcr.resources.vcr_example`](biz.dfch.specmgr.vcr.resources.vcr_example.md) — Resource: specmgr://vcr/example (Task 3.1).
+- [`biz.dfch.specmgr.vcr.resources.vcr_schema`](biz.dfch.specmgr.vcr.resources.vcr_schema.md) — Resource: specmgr://vcr/schema (Task 3.1, packaged data).
+- [`biz.dfch.specmgr.vcr.resources.vcr_template`](biz.dfch.specmgr.vcr.resources.vcr_template.md) — Resource: specmgr://vcr/template (Task 3.1).
 - [`biz.dfch.specmgr.vcr.tools`](biz.dfch.specmgr.vcr.tools.md) — MCP tool wrappers for verification case records (mirrors ``dec/tools/``'s own shape).
 - [`biz.dfch.specmgr.vcr.tools._io`](biz.dfch.specmgr.vcr.tools._io.md) — Thin file read helpers over ``parse_vcr`` (Task 2.1).
 - [`biz.dfch.specmgr.vcr.tools._lock`](biz.dfch.specmgr.vcr.tools._lock.md) — Per-document in-process lock guarding verification case record mutations.
diff --git a/docs/api/biz.dfch.specmgr.commands.schema.md b/docs/api/biz.dfch.specmgr.commands.schema.md
index cc376ab..35ec407 100644
--- a/docs/api/biz.dfch.specmgr.commands.schema.md
+++ b/docs/api/biz.dfch.specmgr.commands.schema.md
@@ -159,6 +159,20 @@ the same byte-identical-output/drift-detection reason as
 :func:`generate_req_schema`.
 
 
+### `generate_vcr_schema() -> str`
+
+Generate VCR's JSON Schema (2020-12 dialect) from ``VcrDocument.model_json_schema()``.
+
+Mirrors :func:`generate_req_schema` exactly, but for ``vcr.models.v1``:
+the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
+default), and ``"$comment"`` holds ``vcr.models.v1.SCHEMA_COMMENT_VERSION``
+(currently ``"v1"``) instead of REQ's own version token.
+
+Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
+the same byte-identical-output/drift-detection reason as
+:func:`generate_req_schema`.
+
+
 ### `schema(type_: Annotated[str | None, <typer.models.OptionInfo object>] = None, output_dir: Annotated[pathlib.Path, <typer.models.OptionInfo object>] = PosixPath('/docs')) -> None`
 
 Generate JSON Schema (2020-12) for one or all registered document types.
diff --git a/docs/api/biz.dfch.specmgr.general.resources.md b/docs/api/biz.dfch.specmgr.general.resources.md
index b58eeba..16f2783 100644
--- a/docs/api/biz.dfch.specmgr.general.resources.md
+++ b/docs/api/biz.dfch.specmgr.general.resources.md
@@ -6,9 +6,13 @@ domain.
 See ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by document-type domain".
 
 ``version`` registers the server package version resource. ``iso25010``
-registers the ISO/IEC 25010:2023 product quality model resource. Domain-
-specific resources (e.g. ``adr_list``/``adr_get``) live under their own
-domain package instead (``biz.dfch.specmgr.adr.resources``). Import this
-package to load all cross-cutting resources at once::
+registers the ISO/IEC 25010:2023 product quality model resource. ``dtais``
+registers the DTAIS verification-method vocabulary resource
+(``specmgr://dtais``, feat-33-vcr REQ-006) -- cross-cutting domain
+knowledge for ``vcr``'s ``## Acceptance Criteria`` method vocabulary, not
+owned by ``vcr``'s own schema. Domain-specific resources (e.g.
+``adr_list``/``adr_get``) live under their own domain package instead
+(``biz.dfch.specmgr.adr.resources``). Import this package to load all
+cross-cutting resources at once::
 
     from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)

specmgr mcp-docs.........................................................Failed
- hook id: specmgr-mcp-docs
- exit code: 1
- files were modified by this hook

✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/MCP.md
diff --git a/docs/MCP.md b/docs/MCP.md
index e17008d..5f03b11 100644
--- a/docs/MCP.md
+++ b/docs/MCP.md
@@ -3,7 +3,7 @@
 Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --
 do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 
-31 resource(s), 1 resource template(s), 95 tool(s), 23 prompt(s).
+32 resource(s), 1 resource template(s), 95 tool(s), 23 prompt(s).
 
 ## Table of Contents
 
@@ -19,6 +19,7 @@ do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).
 | [`specmgr://dec/example`](#resource-dec_example) | A complete, valid sample decision document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`specmgr://dec/schema`](#resource-dec_schema) | The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document. |
 | [`specmgr://dec/template`](#resource-dec_template) | A DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision. |
+| [`specmgr://dtais`](#resource-dtais) | What DTAIS is (Demonstration, Test, Analysis, Inspection, Special), the five valid `### AC-NNN (Method): ...` method words, and when and how to apply each, as raw markdown domain-knowledge guidance. |
 | [`specmgr://feat/example`](#resource-feat_example) | A complete, valid sample feature document as raw markdown -- frontmatter and body -- exercising every section, for use as a learning example. |
 | [`specmgr://feat/schema`](#resource-feat_schema) | The generated FEAT JSON Schema (2020-12 dialect), generated by `specmgr schema` and kept current by a pre-commit hook/CI step. Includes a `$comment` schema-layout version marker for detecting a shape change without diffing the whole document. |
 | [`specmgr://feat/template`](#resource-feat_template) | A FEAT document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new feature. |
@@ -69,6 +70,13 @@ The generated DEC JSON Schema (2020-12 dialect), generated by `specmgr schema` a
 
 A DEC document template -- frontmatter and every body field present, populated with short placeholder ('blind text') content -- as raw markdown, for use as a starting point when drafting a new decision.
 
+### Resource: dtais
+
+- **URI:** `specmgr://dtais`
+- **MIME type:** `text/markdown`
+
+What DTAIS is (Demonstration, Test, Analysis, Inspection, Special), the five valid `### AC-NNN (Method): ...` method words, and when and how to apply each, as raw markdown domain-knowledge guidance.
+
 ### Resource: feat_example
 
 - **URI:** `specmgr://feat/example`

specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.5s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add -A && git status --short"
}
```

**Output:**

```
M  .specmgr/feat/feat-33-vcr/README.md
M  docs/GENERATED.md
M  docs/MCP.md
M  docs/api/README.md
M  docs/api/biz.dfch.specmgr.commands.schema.md
A  docs/api/biz.dfch.specmgr.general.resources.dtais.md
M  docs/api/biz.dfch.specmgr.general.resources.md
A  docs/api/biz.dfch.specmgr.vcr.prompts.create_vcr.md
A  docs/api/biz.dfch.specmgr.vcr.prompts.md
A  docs/api/biz.dfch.specmgr.vcr.prompts.update_vcr.md
A  docs/api/biz.dfch.specmgr.vcr.resources.md
A  docs/api/biz.dfch.specmgr.vcr.resources.vcr_example.md
A  docs/api/biz.dfch.specmgr.vcr.resources.vcr_schema.md
A  docs/api/biz.dfch.specmgr.vcr.resources.vcr_template.md
A  docs/vcr_schema.json
M  src/biz/dfch/specmgr/commands/schema.py
A  src/biz/dfch/specmgr/general/data/general_dtais.md
M  src/biz/dfch/specmgr/general/resources/__init__.py
A  src/biz/dfch/specmgr/general/resources/dtais.py
A  src/biz/dfch/specmgr/vcr/data/vcr_create_instructions.md
A  src/biz/dfch/specmgr/vcr/data/vcr_schema.json
A  src/biz/dfch/specmgr/vcr/data/vcr_update_instructions.md
A  src/biz/dfch/specmgr/vcr/prompts/__init__.py
A  src/biz/dfch/specmgr/vcr/prompts/create_vcr.py
A  src/biz/dfch/specmgr/vcr/prompts/update_vcr.py
A  src/biz/dfch/specmgr/vcr/resources/__init__.py
A  src/biz/dfch/specmgr/vcr/resources/vcr_example.py
A  src/biz/dfch/specmgr/vcr/resources/vcr_schema.py
A  src/biz/dfch/specmgr/vcr/resources/vcr_template.py
A  tests/general/resources/test_dtais.py
A  tests/vcr/prompts/__init__.py
A  tests/vcr/prompts/test_create_vcr.py
A  tests/vcr/prompts/test_update_vcr.py
A  tests/vcr/resources/__init__.py
A  tests/vcr/resources/test_vcr_example.py
A  tests/vcr/resources/test_vcr_schema.py
A  tests/vcr/resources/test_vcr_template.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 189.5s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): add vcr resources/prompts and specmgr://dtais (Phase 3)\" -m \"commands/schema.py gains generate_vcr_schema + registry entry;\ndocs/vcr_schema.json and the packaged src/.../vcr/data/vcr_schema.json\ncopy generated and confirmed drift-free.\n\nvcr/resources/ (specmgr://vcr/schema, .../example, .../template) and\nvcr/prompts/ (create_vcr, update_vcr, with their own packaged\ninstruction files) mirror the dec domain's shape.\n\nCross-cutting specmgr://dtais resource (REQ-006): general/data/\ngeneral_dtais.md documents the closed 5-word DTAIS vocabulary\n(Demonstration, Test, Analysis, Inspection, Special), when to apply\neach, and its relationship to ## Coverage; general/resources/dtais.py\nregistered alongside iso25010/version.\n\n52 new tests (2452 total). Includes docs/api, docs/MCP.md,\ndocs/GENERATED.md regenerated by pre-commit hooks. No server.py/\nAGENTS.md/README.md/pre-commit-config.yaml changes yet (Phase 4).\"",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
[feat-33-vcr 2d58ab0] feat(feat-33-vcr): add vcr resources/prompts and specmgr://dtais (Phase 3)
 37 files changed, 2732 insertions(+), 15 deletions(-)
 create mode 100644 docs/api/biz.dfch.specmgr.general.resources.dtais.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.prompts.create_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.prompts.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.prompts.update_vcr.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.resources.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.resources.vcr_example.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.resources.vcr_schema.md
 create mode 100644 docs/api/biz.dfch.specmgr.vcr.resources.vcr_template.md
 create mode 100644 docs/vcr_schema.json
 create mode 100644 src/biz/dfch/specmgr/general/data/general_dtais.md
 create mode 100644 src/biz/dfch/specmgr/general/resources/dtais.py
 create mode 100644 src/biz/dfch/specmgr/vcr/data/vcr_create_instructions.md
 create mode 100644 src/biz/dfch/specmgr/vcr/data/vcr_schema.json
 create mode 100644 src/biz/dfch/specmgr/vcr/data/vcr_update_instructions.md
 create mode 100644 src/biz/dfch/specmgr/vcr/prompts/__init__.py
 create mode 100644 src/biz/dfch/specmgr/vcr/prompts/create_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/prompts/update_vcr.py
 create mode 100644 src/biz/dfch/specmgr/vcr/resources/__init__.py
 create mode 100644 src/biz/dfch/specmgr/vcr/resources/vcr_example.py
 create mode 100644 src/biz/dfch/specmgr/vcr/resources/vcr_schema.py
 create mode 100644 src/biz/dfch/specmgr/vcr/resources/vcr_template.py
 create mode 100644 tests/general/resources/test_dtais.py
 create mode 100644 tests/vcr/prompts/__init__.py
 create mode 100644 tests/vcr/prompts/test_create_vcr.py
 create mode 100644 tests/vcr/prompts/test_update_vcr.py
 create mode 100644 tests/vcr/resources/__init__.py
 create mode 100644 tests/vcr/resources/test_vcr_example.py
 create mode 100644 tests/vcr/resources/test_vcr_schema.py
 create mode 100644 tests/vcr/resources/test_vcr_template.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.1s)

Phase 3 committed. Now the final phase: Phase 4, cross-cutting registration.

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
      "status": "in_progress",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
    "status": "in_progress",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 12.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && wc -l src/biz/dfch/specmgr/server.py\nsed -n '1,60p' src/biz/dfch/specmgr/server.py"
}
```

**Output:**

```
278 src/biz/dfch/specmgr/server.py
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

"""MCP server for ``biz-dfch-specmgr``.

Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).

Registers the following resources and tools so far (plan §8, §9a):

Resources
---------
specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/req_schema.json``) so it works from a
                        real, non-editable install.
specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
specmgr://req/template -- A requirement template (every field present, placeholder text)
                          as raw markdown.
specmgr://uc/schema --  The generated UC JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/uc_schema.json``) so it works from a
                        real, non-editable install.
specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
specmgr://uc/template -- A use-case template (every field present, placeholder text)
                          as raw markdown.
specmgr://tsk/schema -- The generated TSK JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/tsk_schema.json``) so it works from a
                        real, non-editable install.
specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
specmgr://tsk/template -- A task list template (every field present, placeholder text)
                          as raw markdown.
specmgr://qa/schema --  The generated QA JSON Schema, read from a packaged data copy
                        (kept in sync with ``docs/qa_schema.json``) so it works from a
                        real, non-editable install.
specmgr://qa/example -- A complete, valid sample question-and-answer document as raw
                        markdown.
specmgr://qa/template -- A question-and-answer template (every field present,
                          placeholder text) as raw markdown.
specmgr://prb/schema -- The generated PRB JSON Schema, read from a packaged data copy
                         (kept in sync with ``docs/prb_schema.json``) so it works from a
                         real, non-editable install.
specmgr://prb/example -- A complete, valid sample problem statement document as raw
                         markdown.
specmgr://prb/template -- A problem statement template (every field present,
                           placeholder text) as raw markdown.
specmgr://gol/schema -- The generated GOL JSON Schema, read from a packaged data copy

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.3s)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/server.py",
  "offset": 60,
  "limit": 220
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/src/biz/dfch/specmgr/server.py</path>
<type>file</type>
<content>
60: specmgr://gol/schema -- The generated GOL JSON Schema, read from a packaged data copy
61:                          (kept in sync with ``docs/gol_schema.json``) so it works from a
62:                          real, non-editable install.
63: specmgr://gol/example -- A complete, valid sample goal document as raw markdown.
64: specmgr://gol/template -- A goal template (every field present,
65:                            placeholder text) as raw markdown.
66: specmgr://rsk/schema -- The generated RSK JSON Schema, read from a packaged data copy
67:                         (kept in sync with ``docs/rsk_schema.json``) so it works from a
68:                         real, non-editable install.
69: specmgr://rsk/example -- A complete, valid sample risk document as raw markdown.
70: specmgr://rsk/template -- A risk template (every field present, placeholder text)
71:                            as raw markdown.
72: specmgr://rsk/tara --     The TARA risk-response framework: what TARA is (Transfer,
73:                            Accept, Reduce, Avoid), the four valid `## Strategy` words,
74:                            and when and how to apply each -- raw markdown domain-knowledge
75:                            guidance.
76: specmgr://rsk/risk-matrix -- The 5x5 risk matrix: probability/impact scale anchors, the
77:                            zone table, and the product thresholds (what 'high risk' and
78:                            'low risk' mean) -- raw markdown domain-knowledge guidance.
79: specmgr://dec/schema -- The generated DEC JSON Schema, read from a packaged data copy
80:                         (kept in sync with ``docs/dec_schema.json``) so it works from a
81:                         real, non-editable install.
82: specmgr://dec/example -- A complete, valid sample decision document as raw markdown.
83: specmgr://dec/template -- A decision template (every field present, placeholder text)
84:                           as raw markdown.
85: specmgr://feat/schema -- The generated FEAT JSON Schema, read from a packaged data copy
86:                         (kept in sync with ``docs/feat_schema.json``) so it works from a
87:                         real, non-editable install.
88: specmgr://feat/example -- A complete, valid sample feature document as raw markdown.
89: specmgr://feat/template -- A feature template (every field present, placeholder text)
90:                           as raw markdown.
91: specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
92:                         characteristics (and sub-characteristics), each with a description.
93: 
94: REQ has no ``specmgr://req/{id}`` resource, unlike ADR -- id-based reads go
95: through the ``get_req`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
96: UC has no ``specmgr://uc/{id}`` resource either, for the same reason -- id-based
97: reads go through the ``get_uc`` tool only. TSK has no ``specmgr://tsk/{id}``
98: resource either -- id-based reads go through the ``get_tsk`` tool only, and
99: there never was such a resource to remove in the first place. QA has no
100: ``specmgr://qa/{id}`` resource either, for the same reason -- id-based reads go
101: through the ``get_qa`` tool only. PRB has no ``specmgr://prb/{id}`` resource
102: either, for the same reason -- id-based reads go through the ``get_prb`` tool
103: only, and there is also no ``specmgr://prb/list`` resource -- ``list_prb``
104: ships as a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
105: GOL has no ``specmgr://gol/{id}`` resource either, for the same reason --
106: id-based reads go through the ``get_gol`` tool only, and there is also no
107:  ``specmgr://gol/list`` resource -- ``list_gol`` ships as a paged tool from
108:  day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). RSK has no
109:  ``specmgr://rsk/{id}`` resource either, for the same reason -- id-based reads go
110:  through the ``get_rsk`` tool only, and there never was such a resource to
111:  remove in the first place. DEC has no
112:  ``specmgr://dec/{id}`` resource either, for the same reason -- id-based reads go
113:  through the ``get_dec`` tool only, and there is also no
114:  ``specmgr://dec/list`` resource -- ``list_dec`` ships as a paged tool from
115:  day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). FEAT has no
116:  ``specmgr://feat/{id}`` resource either, for the same reason -- id-based
117:  reads go through the ``get_feat`` tool only, and there is also no
118:  ``specmgr://feat/list`` resource either -- ``list_feat`` ships as a paged
119:  tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
120: 
121: Tools
122: -----
123: ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
124: ``update_section``, ``option_list``, ``option_create``,
125: ``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
126: Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc`` (``raw=True`` returns the
127: frontmatter-stripped body text verbatim instead of the parsed document), ``list_uc``,
128: ``get_uc_example``,
129: ``get_uc_template``, ``create_uc``, ``delete_uc``
130: (stub, not yet implemented), ``validate_uc``.
131: Requirement tools (``req/tools/``): ``parse_req``, ``get_req`` (``raw=True`` returns the
132: frontmatter-stripped body text verbatim instead of the parsed document), ``list_req``,
133: ``get_req_example``,
134: ``get_req_template``, ``create_req``, ``delete_req``
135: (stub, not yet implemented), ``validate_req``.
136: Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk`` (``raw=True`` returns the
137: frontmatter-stripped body text verbatim instead of the parsed document), ``list_tsk``,
138: ``get_tsk_example``,
139: ``get_tsk_template``, ``create_tsk``, ``delete_tsk``
140: (stub, not yet implemented), ``validate_tsk``.
141: QA tools (``qa/tools/``): ``parse_qa``, ``get_qa`` (``raw=True`` returns the
142: frontmatter-stripped body text verbatim instead of the parsed document), ``list_qa``,
143: ``get_qa_example``,
144: ``get_qa_template``, ``create_qa``, ``delete_qa``
145: (stub, not yet implemented), ``validate_qa``.
146: Problem statement tools (``prb/tools/``): ``parse_prb``, ``get_prb`` (``raw=True`` returns
147: the frontmatter-stripped body text verbatim instead of the parsed document), ``list_prb``,
148: ``get_prb_example``, ``get_prb_template``, ``create_prb``,
149: ``delete_prb`` (stub, not yet implemented), ``validate_prb``.
150: Goal tools (``gol/tools/``): ``parse_gol``, ``get_gol`` (``raw=True`` returns the
151: frontmatter-stripped body text verbatim instead of the parsed document), ``list_gol``,
152: ``get_gol_example``, ``get_gol_template``, ``create_gol``,
153:  ``delete_gol`` (stub, not yet implemented), ``validate_gol``.
154:  Risk tools (``rsk/tools/``): ``parse_rsk``, ``get_rsk`` (``raw=True`` returns the
155: frontmatter-stripped body text verbatim instead of the parsed document), ``list_rsk``,
156:  ``get_rsk_example``,
157:  ``get_rsk_template``, ``create_rsk``, ``delete_rsk``
158:  (stub, not yet implemented), ``validate_rsk``.
159:   Decision tools (``dec/tools/``): ``parse_dec``, ``get_dec`` (``raw=True`` returns the
160: frontmatter-stripped body text verbatim instead of the parsed document), ``list_dec``,
161:   ``get_dec_example``,
162:   ``get_dec_template``, ``create_dec``, ``delete_dec``
163:   (stub, not yet implemented), ``validate_dec``.
164:   Feature tools (``feat/tools/``): ``parse_feat``, ``get_feat`` (``raw=True`` returns the
165: frontmatter-stripped body text verbatim instead of the parsed document), ``list_feat``,
166:   ``get_feat_example``,
167:   ``get_feat_template``, ``create_feat``, ``delete_feat``
168:   (stub, not yet implemented), ``validate_feat``. Unlike every other domain here, ``feat``
169:   uses bespoke, folder-per-document addressing (``feat/tools/_paths.py``, not the shared
170:   ``general/tools/_doc_paths.py``) and has no ``update_feat``/``set_status_feat`` tools of
171:   its own -- it dispatches through the generic ``update``/``set_status`` tools below from
172:   day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0), same as every other domain.
173:   General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
174: preserving YAML frontmatter blocks; ``update`` -- whole-body or line-range replace of an
175: existing document's content across the nine whole-body domains (``type`` is one of
176: ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``; optional 1-based
177: inclusive
178: ``begin``/``end`` body-line range with the ``N+1`` end-of-body sentinel; the spliced
179: result is validated as a whole document before anything is written); ``set_status`` --
180: replace an existing document's status across all ten domains (``type`` is one of
181: ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``), also
182: bumping
183: ``updated`` (the nine whole-body domains) and leaving the body untouched;
184: ``superseded_by`` is ``adr``-only (it composes the status as
185: ``"superseded by {superseded_by}"``);
186: ``webfetch`` -- fetch a URL over HTTP GET with a
187: bearer token, restricted to a configured base URL (``SPECMGR_WEBFETCH_BASE_URL``,
188: ``SPECMGR_WEBFETCH_BEARER``).
189: 
190: Prompts
191: -------
192: ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
193: text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
194: §11).
195: Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
196: instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).
197: Task list prompts (``tsk/prompts/``): ``create_task``, ``update_task`` -- instructional
198: text guiding an LLM through the TSK tool sequence above, plus ``implement_task`` --
199: reads an existing task list via ``get_tsk``, builds a ``TodoWrite`` list from its
200: items, and uses the ``question`` tool to resolve ambiguity before proceeding.
201: QA prompts (``qa/prompts/``): ``create_qa``, ``update_qa``, plus ``refine`` --
202: appends a fresh batch of unanswered interview questions (each with an empty
203: `_(awaiting response)_` placeholder) to an existing QA document, for
204: ``Elicitation Context`` or one or more of the nine ISO/IEC 25010:2023 quality
205: characteristics.
206: Problem statement prompts (``prb/prompts/``): ``create_prb``, ``update_prb`` --
207: instructional text guiding an LLM through a ``TodoWrite`` + ``question``-tool-
208: driven 5W2H interview flow, including agent-synthesized ``Summary``/``Gap``
209: text.
210: Goal prompts (``gol/prompts/``): ``create_gol``, ``update_gol`` --
211: instructional text guiding an LLM through a ``TodoWrite`` +
212: ``question``-tool-driven interview flow over the goal's mandatory
213: ``statement``/``Source`` fields and its optional sections.
214: Risk prompts (``rsk/prompts/``): ``create_risk``, ``update_risk`` -- instructional
215: text guiding an LLM through the RSK tool sequence above.
216: Decision prompts (``dec/prompts/``): ``create_dec``, ``update_dec`` --
217: instructional text guiding an LLM through a ``TodoWrite`` +
218: ``question``-tool-driven interview flow; ``create_dec`` first checks
219: ``list_dec`` for a near-duplicate decision.
220: Feature prompts (``feat/prompts/``): ``create_feat``, ``update_feat`` --
221: narrated instruction flows guiding an LLM through the FEAT tool sequence
222: above; ``create_feat`` first checks ``list_feat`` for a near-duplicate
223: feature.
224: General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
225: older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
226: ``README.md`` into an optional sibling ``history.md``, per ADR
227: e369ee2e-3353-4f92-991c-6367d76d832e.
228: 
229: Modules are grouped domain-first
230: (ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
231: document-type domain"): each document
232: domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``,
233: and later ``ac``) is a
234: top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
235: self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
236: tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010`` resources,
237: the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
238: ``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
239: Add a new domain by
240: creating its top-level package and importing it at the bottom of this
241: module, next to the existing
242: ``adr``/``dec``/``feat``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
243: imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
244: decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, and ``feat``
245: each register ``tools``, ``resources``, and ``prompts``; ``general`` now also
246: registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
247: has no ``prompts`` sub-package yet.
248: """
249: 
250: from __future__ import annotations
251: 
252: from collections.abc import AsyncGenerator
253: from contextlib import asynccontextmanager
254: 
255: from mcp.server import MCPServer
256: 
257: 
258: @asynccontextmanager
259: async def _lifespan(_server: MCPServer) -> AsyncGenerator[None, None]:
260:     """Placeholder lifespan: no shared state to initialise yet."""
261:     yield
262: 
263: 
264: mcp = MCPServer(
265:     name="specmgr",
266:     instructions="An artifact manager for system specifications.",
267:     lifespan=_lifespan,
268: )
269: 
270: # ---------------------------------------------------------------------------
271: # Resource/tool/prompt registration (side-effect: registers everything on
272: # mcp). Every domain package here (including the cross-cutting `general`
273: # package, which in turn imports its own `resources`/`tools` sub-packages)
274: # must be imported for its @mcp.tool()/@mcp.prompt()/@mcp.resource()
275: # decorators to actually run.
276: # ---------------------------------------------------------------------------
277: 
278: from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401

(End of file - total 278 lines)
</content>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 15.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"dec\\b\\|feat\\b\\|gol\\b\\|rsk\\b\\|prb\\b\" README.md | head -40"
}
```

**Output:**

```
(no output)
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.1s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && grep -n \"domain\\|artifact type\\|document type\" README.md | head -20"
}
```

**Output:**

```
81:_No domain document-management commands (create/update/status/etc.) exist
105:Every document type stores its `.md` files in a base directory on disk —
111:  shared with other document types.
112:- Requirements (REQ) and future document types: share one root directory,

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.2s)

_Thinking:_

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/README.md",
  "offset": 75,
  "limit": 45
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/README.md</path>
<type>file</type>
<content>
75: 
76: ## CLI Usage
77: 
78: With the CLI you can generate schema and documentation. We use these commands
79: in pre-commit hooks and `ci.yml`.
80: 
81: _No domain document-management commands (create/update/status/etc.) exist
82: in the CLI yet — those are currently MCP-only, see
83: [MCP Server](#mcp-server). The CLI covers `version`, `mcp` (below), and a
84: handful of cross-cutting/doc-generation commands (`specmgr --help` for the
85: full list)._
86: 
87: ```bash
88: specmgr version
89: ```
90: 
91: ## MCP Server
92: 
93: Requires the `mcp` extra. The server exposes resources, tools, and prompts
94: for document management, plus cross-cutting utilities (e.g. markdown
95: formatting).
96: 
97: **The full, up-to-date list of every resource, resource template, tool, and
98: prompt — with parameters, MIME types, and descriptions — lives in
99: [docs/MCP.md](docs/MCP.md).** That document generated from the live server
100: registration by `specmgr mcp-docs` and kept in sync by a pre-commit hook and
101: a CI check.
102: 
103: ### Environment Variables
104: 
105: Every document type stores its `.md` files in a base directory on disk —
106: the file is always the source of truth, re-read and re-parsed on every
107: tool call, so hand-editing a file between calls is safe.
108: 
109: - ADRs: base directory defaults to `docs/adr`, configurable via the
110:   `SPECMGR_ADR_DIR` environment variable. This is ADR-specific and not
111:   shared with other document types.
112: - Requirements (REQ) and future document types: share one root directory,
113:   configurable via the `SPECMGR_DOCS_DIR` environment variable (default
114:   `docs`), with each type's own subdirectory appended automatically (e.g.
115:   `docs/req` for requirements).
116: - The `webfetch` tool (bearer-authenticated, URL-filtered HTTP GET, intended
117:   primarily for Web Server instances using PAT authentication)
118:   requires two environment variables: `SPECMGR_WEBFETCH_BASE_URL` (the base
119:   URL requested URLs must case-insensitively start with) and

(Showing lines 75-119 of 352. Use offset=120 to continue.)
</content>
````

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 14.1s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && head -40 CHANGELOG.md"
}
```

**Output:**

```
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.14.0] - 2026-08-30

### Added

- **Eleventh domain feature (FEAT/Feature tooling)**: formalized the ad hoc
  `.specmgr/feat/<id>/README.md` convention (ADR e369ee2e-3353-4f92-991c-6367d76d832e)
  into a real, schema-backed `feat` document-type domain, with full MCP tool surface,
  resources, prompts, and cross-cutting registration. Deliberately special among domains:
  uses non-UUID `feat-NNN-slug` ids (chosen by user, derived from H1 title) and
  folder-per-document addressing (`.specmgr/feat/<id>/README.md`), deviating from ADR
  8cf940c5's flat-file UUID precedent. Mirrors GOL/RSK/DEC's simple surface (no
  fine-grained mutation tools, no renderer — writes persist raw validated body
  byte-for-byte) and uses the post-feat-22 generic `update`/`set_status` dispatch
  from day one:
  - `feat/models/v1/`: Pydantic schema (`FeatFrontmatter` with a closed 4-value
    status set `planning`/`progress`/`review`/`done`, `Feature` body with mandatory
    `## Plan`/`## Progress` composites containing structured `### Requirements`
    (regex-validated list), `### Acceptance Criteria` (checked list), `### Scope`
    (mandatory `#### Included`/`#### Explicitly Out Of Scope`), optional `### Dependencies`
    (`#### Depends On`/`#### Blocks`), `### Task List` (`#### Phase N` entries each with
    `- [ ] ...` checklist), `### Updates`/`### Decisions Made` (ISO8601-enforced
    `#### {timestamp} — {title}` entries, newest-first ordered), and optional leaves),
    parser (`parse_feat`), `FeatSummary` (adds `path: str` field — the only document
    type where direct hand/agent markdown editing remains the sanctioned workflow),
    and JSON schema generation, inside the domain package itself.
  - `feat/tools/`: `@mcp.tool()` wrappers for the FEAT lifecycle (`create_feat`,
    `parse_feat`, `list_feat`, `get_feat`, `get_feat_example`, `get_feat_template`,
    `validate_feat`), plus a stub for `delete_feat`. Bespoke `_paths.py` (hand-rolled
    like ADR's own, not the shared flat-file pattern): `feat_base_dir()`/
    `find_feat_path_by_id()` (no-scan shortcut + folder-name-mismatch rejection at
    tool layer), global `feat_create_lock()` (since id doesn't exist until scanning

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 1024.8s)

_Thinking:_

**Tool: task**

**Input:**

````json
{
  "description": "Implement VCR Phase 4",
  "prompt": "You are implementing the FINAL phase of a feature plan for the biz.dfch.SpecMgr repo: cross-cutting registration for the new `vcr` (Verification Case Record) domain. Do NOT commit. Stop and report back when done or if you hit a blocker.\n\n## Plan location\nRead in full: `/home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/.specmgr/feat/feat-33-vcr/README.md` (Task List's \"Phase 4: Cross-cutting registration\", and the full Acceptance Criteria list ACC-001..006).\nRead `.specmgr/conventions.md` at the repo root.\n\nPhases 1-3 are already committed: `vcr/models/v1/`, `vcr/tools/`, `vcr/resources/`, `vcr/prompts/`, packaged `vcr/data/*` (example/template/schema/instructions), the generic `update`/`set_status` dispatch entries, and the cross-cutting `specmgr://dtais` resource all exist and are fully tested (2452 tests passing as of the last commit). `vcr/__init__.py` currently does NOT import `prompts`/`resources`/`tools` (deliberately deferred to this phase), and `server.py` does NOT yet import `vcr` at all.\n\n## Phase to implement: \"Phase 4: Cross-cutting registration\"\n\nExact tasks from the plan (verbatim):\n- Task 4.1: `server.py` import line.\n- Task 4.2: `AGENTS.md` Status section bullet (mirroring the `sop`/`feat` bullets -- note `sop` does not exist in this repo's `src/` yet, so mirror the `feat`/`dec` bullets' actual shape instead).\n- Task 4.3: `README.md`, CI/pre-commit updates as needed.\n- Task 4.4: `specmgr docs`/`specmgr adr-toc` regeneration, full test suite, ruff/vulture gates.\n\n## Task 4.0 (implicit prerequisite, do this first): wire `vcr/__init__.py`\n\nRead `src/biz/dfch/specmgr/dec/__init__.py` in full -- mirror its exact shape for `src/biz/dfch/specmgr/vcr/__init__.py`: `from . import prompts, resources, tools` plus a module docstring describing the domain (adapt DEC's docstring content to VCR's actual schema/tools/resources/prompts -- see Phases 1-3's work for the accurate list: 8 tools `create_vcr`/`parse_vcr`/`list_vcr`/`get_vcr(raw=)`/`get_vcr_example`/`get_vcr_template`/`delete_vcr` stub/`validate_vcr`; 3 resources `specmgr://vcr/schema`/`.../example`/`.../template`; 2 prompts `create_vcr`/`update_vcr`; generic `update`/`set_status` dispatch with `type=\"vcr\"`; no `specmgr://vcr/{id}` resource (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614); no `specmgr://vcr/list` resource (`list_vcr` ships as a paged tool from day one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13)).\n\n## Task 4.1: `server.py`\n\nRead `src/biz/dfch/specmgr/server.py` in full (it's ~280 lines, mostly one giant module docstring enumerating every resource/tool/prompt by domain, plus the actual import line at the bottom). This is the single most authoritative live registration list per `AGENTS.md` -- you must update it accurately and completely, not just the import line. Concretely:\n\n1. **Bottom import line** (the actual code, not docstring): change\n   `from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401`\n   to add `vcr` in alphabetical position (after `uc`):\n   `from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc, vcr  # noqa: E402, F401`\n\n2. **Docstring \"Resources\" section**: after the `specmgr://feat/template` line and before `specmgr://iso25010`, add three lines for VCR's schema/example/template resources, in the exact same tabular style as the `feat`/`dec` lines immediately above them (match the column alignment style already used -- it's not perfectly monospaced/aligned across all entries, just follow the nearest neighbor's indentation pattern). Then add a `specmgr://dtais` line right after `specmgr://iso25010` (or immediately before it -- your call, whichever reads better given `dtais` and `iso25010` are both cross-cutting `general` resources), one line describing what it is (mirror `specmgr://rsk/tara`'s two-line description style, condensed to fit this docstring's terser one-liner format where other schema/example/template lines are single-line).\n\n3. **The \"REQ has no `specmgr://req/{id}`...\" paragraph**: append one more sentence for VCR, mirroring the FEAT sentence's exact pattern: \"VCR has no `specmgr://vcr/{id}` resource either, for the same reason -- id-based reads go through the `get_vcr` tool only, and there is also no `specmgr://vcr/list` resource either -- `list_vcr` ships as a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).\"\n\n4. **Docstring \"Tools\" section**: after the \"Feature tools (`feat/tools/`): ...\" paragraph and before \"General tools (`general/tools/`): ...\", add a new paragraph \"Verification case record tools (`vcr/tools/`): ...\" mirroring the DEC/FEAT tools paragraphs' exact style (list all 8 tools, note `raw=True` behavior on `get_vcr`, note `delete_vcr` is a stub).\n\n5. **The \"General tools\" paragraph's domain-count language**: it currently says \"the nine whole-body domains\" (for `update`) and \"all ten domains\"/\"the nine whole-body domains\" (for `set_status`) and lists `req/uc/tsk/qa/prb/gol/rsk/dec/feat` (for `update`) and `req/uc/tsk/qa/prb/gol/rsk/dec/feat/adr` (for `set_status`). Update both counts (nine->ten, ten->eleven where they refer to whole-body domains including vcr; the `set_status` \"all ten domains\" becomes \"all eleven domains\" since it now covers vcr+adr on top of the nine) and both domain lists to include `vcr` (positioned last among the whole-body domains, immediately before `adr` in the `set_status` list).\n\n6. **Docstring \"Prompts\" section**: after the \"Feature prompts (`feat/prompts/`): ...\" paragraph and before \"General prompts (`general/prompts/`): ...\", add a new paragraph \"Verification case record prompts (`vcr/prompts/`): `create_vcr`, `update_vcr` -- ...\" mirroring DEC's prompts paragraph style (narrated instruction flows; `create_vcr` first checks `list_vcr` for a near-duplicate verification case record).\n\n7. **The final \"Modules are grouped domain-first ...\" paragraph**: update the domain list \"`adr`, `uc`, `req`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `feat`, and later `ac`\" to insert `vcr` before \"and later `ac`\"; update the import-list sentence \"`adr`/`dec`/`feat`/`general`/`gol`/`prb`/`qa`/`req`/`rsk`/`tsk`/`uc`\" to add `vcr` in alphabetical position (after `uc`); update the final sentence \"`req`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, and `feat` each register `tools`, `resources`, and `prompts`\" to add `vcr` to that list (it registers all three too).\n\nAfter editing, re-read the entire docstring once more end to end to confirm it reads coherently and every VCR mention is internally consistent (tool names, resource URIs, ADR references) with what Phases 1-3 actually built.\n\n## Task 4.2: `AGENTS.md`\n\nRead the full `AGENTS.md` at the repo root. In the \"Status: domain packages implemented\" section, insert a new bullet for **`vcr/`** positioned after the **`feat/`** bullet and before the **`general/`** bullet (matching the existing bullets' chronological-addition ordering). Model it closely on the **`dec/`** bullet's shape and level of detail (same tools/resources/prompts/ADR-citation style), but describing VCR's actual schema accurately:\n\n- Domain key `vcr` (\"Verification Case Record\"): captures how a single REQ/UC is verified -- a `## Verifies` single-value cross-reference (exactly one `REQ|UC <uuid>: <title>` + mandatory notes paraphrase), a `## Coverage` closed-vocabulary outcome signal (`full`/`partial`/`none`), and a `## Acceptance Criteria` collection of `### AC-NNN (Method): <criterion text>` entries (3-digit zero-padded, closed DTAIS method vocabulary -- Demonstration/Test/Analysis/Inspection/Special -- each optionally carrying a free-form description paragraph and/or a `#### Test Steps` numbered procedure, duplicate-number rejection via `model_validator`), plus optional `## More Information`/`## Updates`.\n- 8 standard tools (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr(raw=False)`, `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub, `validate_vcr`); whole-body/line-range updates and status changes go through the generic `update`/`set_status` tools (`type=\"vcr\"`).\n- 3 resources (`specmgr://vcr/schema`/`.../example`/`.../template`; no `specmgr://vcr/{id}`, no `specmgr://vcr/list`).\n- `vcr/prompts/` (`create_vcr`/`update_vcr`).\n- Its schema lives at `vcr/models/v1/`, inside the domain package, not top-level `models/`.\n- Mention the cross-cutting `specmgr://dtais` resource (in `general/resources/`, not `vcr/resources/`) as the DTAIS method vocabulary this domain's `## Acceptance Criteria` depends on.\n\nAlso update these other AGENTS.md spots that enumerate domains by name:\n- The \"Still genuinely missing / not yet done\" list: add `validate_vcr` to the \"No `validate_adr` (or ...)\" bullet's parenthetical list, and add `delete_vcr` to the \"`delete_req`/.../`delete_feat` are stubs\" bullet's list.\n- The bullet \"`req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`feat` each register `tools`, `resources`, and `prompts`; `uc` registers `tools` and `resources` only\" -- add `vcr` to the first list (it also registers all three).\n- The \"`general/`\" bullet's own resource list (\"`specmgr://version`, `specmgr://iso25010`\") -- add `specmgr://dtais`, and adjust its own description sentence if needed (mirror how the DTAIS resource is described elsewhere in this same session's Phase 3 work).\n\nDo NOT touch the \"Models location\" paragraph (VCR already follows the default domain-first rule with no exception, so nothing to add there) or any `.specmgr/feat/` references unrelated to this feature.\n\n## Task 4.3: `README.md` (top-level) and CI/pre-commit\n\n**Top-level `README.md`**: read it in full. It does NOT enumerate domains by name individually (except ADR, which is a deliberate special case) -- VCR follows the exact same generic `SPECMGR_DOCS_DIR`-based pattern as every other non-ADR domain, so this file most likely needs **no changes**. Confirm this by reading the \"Environment Variables\" section; only touch it if you find a concrete inaccuracy (e.g. a stale total domain count) -- do not invent content to add.\n\n**`.pre-commit-config.yaml`**: read the whole file. You must:\n1. Add `vcr/models/v1` to the `files:` regex alternation of the shared `specmgr-schema` hook AND every one of the 9 existing `specmgr-schema-<domain>-package` hooks (`req`, `uc`, `tsk`, `rsk`, `qa`, `prb`, `gol`, `dec`, `feat`) -- i.e. change every occurrence of\n   `^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\\.py$`\n   to insert `vcr/models/v1` right after `uc/models/v2` and before `models/md` (matching the existing convention: domain entries alphabetically-ish ordered, with the special shared `models/md` engine always last). There are 10 occurrences of this exact regex string (1 in `specmgr-schema` + 9 in the per-package hooks) -- update all of them identically.\n2. Add a new hook block `specmgr-schema-vcr-package` (name: \"specmgr schema (vcr package copy)\"), appended after the existing `specmgr-schema-feat-package` block (the most recently added one), mirroring that block's exact shape/description wording (just VCR-ified: `src/biz/dfch/specmgr/vcr/data/vcr_schema.json`, `specmgr://vcr/schema`, `docs/vcr_schema.json`, entry `uv run --frozen specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`), with the SAME updated `files:` regex from step 1 (including `vcr/models/v1` in its own alternation, same as every other package-copy hook).\n3. Update the `specmgr-schema` hook's own `description:` text, which currently lists \"currently `dec`, `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, and `uc`\" -- add `vcr` to that list (positioned last, before \"and\").\n\n**`CHANGELOG.md`**: read the `[Unreleased]` section and the most recent dated entry (feat, \"Eleventh domain feature\") for the established format/depth. Add a new `### Added` entry under `[Unreleased]` for VCR, mirroring the FEAT entry's structure and detail level (domain key rationale, schema shape bullet list covering `vcr/models/v1/`, `vcr/tools/`, `vcr/resources/`, `vcr/prompts/`, the generic `update`/`set_status` dispatch wiring, and the cross-cutting `specmgr://dtais` resource) -- concise but complete, one bullet per major piece (models, tools, resources+prompts, dtais), not copy-pasted from FEAT's unrelated content.\n\n## Task 4.4: full regeneration + gates\n\nRun, in this order, and report each command's exact result:\n```\nuv run --frozen specmgr docs\nuv run --frozen specmgr mcp-docs\nuv run --frozen specmgr adr-toc\nuv run --frozen specmgr schema\nuv run --frozen specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\nThe four doc/schema-generation commands are expected to WRITE changed files the first time you run them (since `server.py`/`AGENTS.md`/etc. just changed) -- that's fine, `git add` the results. Run each one a SECOND time afterward and confirm it now reports \"unchanged\"/exit 0 (no further drift) before moving on -- if any command still reports a diff on the second run, something in your own edits is unstable and needs fixing before you finish. `specmgr adr-toc` should report \"no files to check\"/no change at all, since this feature never touches `docs/adr/`.\n\nAlso specifically verify (read the generated `docs/MCP.md`, do not just trust the exit code) that VCR's 8 tools, 3 resources, and 2 prompts, plus the standalone `specmgr://dtais` resource, all appear in it with sensible descriptions.\n\n## Progress-section discipline + final acceptance criteria pass\n\nUpdate `.specmgr/feat/feat-33-vcr/README.md`'s Progress section: mark Phase 4's four tasks `[x]` in the Task List, update Current Status to reflect the feature is now fully implemented end to end, and prepend one new dated Recent-Updates entry. Then walk through every Acceptance Criteria item (ACC-001 through ACC-006) in that same README and, for each one you can concretely confirm is met (cite the specific test file/resource/tool that proves it), mark its checkbox `[x]` -- do not mark one you cannot concretely justify. Set the frontmatter `status: planning` to `status: done` and bump `version`/`updated` per this repo's own feature-folder frontmatter convention (see other already-`done` feature folders like `.specmgr/feat/feat-31-feature/README.md` for the exact convention, if one is `done` -- otherwise use your best judgement consistent with the frontmatter schema described in `AGENTS.md`'s \"Development Artifacts\" section: `status` is one of `planning`/`in-progress`/`review`/`done`).\n\n## Report back\n\n1. Full list of files modified, grouped by area (`vcr/__init__.py`, `server.py`, `AGENTS.md`, `.pre-commit-config.yaml`, `CHANGELOG.md`, `README.md` if touched, regenerated `docs/*`).\n2. The exact output/confirmation of each Task 4.4 command, especially the \"run twice, confirm no further drift\" checks.\n3. Which ACC-001..006 checkboxes you marked done and your one-line justification for each.\n4. Final quality-gate summary (test count, all four core gates green).\n5. Any blockers or genuine ambiguities (stop and ask rather than guessing).\n\nDo NOT commit anything -- I (the orchestrator) will review and commit this final phase myself after verification.",
  "subagent_type": "phase-implementer"
}
````

**Output:**

```
<task id="ses_fa8efc9a7ffeTgpAVaNEXbd4Rp" state="completed">
<task_result>
## Report: Phase 4 (Cross-cutting registration) — feat-33-vcr

**Status: complete.** All Phase 4 tasks (4.1–4.4) plus the implicit Task 4.0 prerequisite are done. Working tree left uncommitted, as instructed.

### 1. Files modified, by area

- **`vcr/__init__.py`** (Task 4.0): `src/biz/dfch/specmgr/vcr/__init__.py` — now `from . import prompts, resources, tools`, docstring adapted from `dec/__init__.py`'s pattern to VCR's actual schema/tools/resources/prompts/ADR citations.
- **`server.py`** (Task 4.1): `src/biz/dfch/specmgr/server.py` — bottom import line gains `vcr`; docstring updated in 6 places (3 new resource lines, new `specmgr://dtais` line, new "no `{id}`/no `list`" sentence, new VCR tools paragraph, new VCR prompts paragraph, domain-count bumps in the `update`/`set_status` paragraph, and the closing domain-enumeration paragraph).
- **`AGENTS.md`** (Task 4.2): new `vcr/` bullet (after `feat/`, before `general/`); updated `general/`'s own resource list (+`specmgr://dtais`); domain-count bumps (`nine`→`ten`, `ten`→`eleven`); "still missing" `validate_*`/`delete_*` lists gain `validate_vcr`/`delete_vcr`; tools/resources/prompts registration summary bullet gains `vcr`; MCP-server-import summary sentence gains `vcr`.
- **`.pre-commit-config.yaml`** (Task 4.3): `vcr/models/v1` inserted into all 10 existing `files:` regex occurrences (shared `specmgr-schema` + 9 per-package hooks); new `specmgr-schema-vcr-package` hook block appended after `specmgr-schema-feat-package`; `specmgr-schema` hook's description text updated.
- **`CHANGELOG.md`** (Task 4.3): new `[Unreleased] ### Added` entry, "Twelfth domain feature (VCR/Verification Case Record tooling)", mirroring FEAT's structure/depth.
- **`README.md`** (Task 4.3): added `Verification Case Record (VCR)` to the artifact list (alphabetically last, after `Use Case (UC)`) — the "Environment Variables" section needed no change (already fully generic).
- **Regenerated docs** (Task 4.4): `docs/GENERATED.md`, `docs/MCP.md`, `docs/api/README.md`, `docs/api/biz.dfch.specmgr.server.md`, `docs/api/biz.dfch.specmgr.vcr.md`. `docs/adr/README.md` and every `docs/*_schema.json`/`vcr/data/vcr_schema.json` were regenerated but reported no diff/"unchanged".
- **`.specmgr/feat/feat-33-vcr/README.md`**: Task List Phase 4 checked off, all 6 ACC checkboxes marked `[x]` with justifications, Current Status updated, new dated Updates entry, frontmatter `status: planning→done`, `version: 1.0.0→1.1.0`, `updated` bumped.

### 2. Task 4.4 command results (each run twice)

| Command | 1st run | 2nd run (drift check) |
|---|---|---|
| `specmgr docs` | wrote 4 changed files | byte-identical (md5 match) |
| `specmgr mcp-docs` | wrote `docs/MCP.md` | byte-identical (md5 match) |
| `specmgr adr-toc` | wrote `docs/adr/README.md`, **empty diff** | empty diff again — confirmed no drift, as expected |
| `specmgr schema` (all types) | all 9 pre-existing types "(unchanged)"; `vcr` "(unchanged)" | same, all "(unchanged)" |
| `specmgr schema --type vcr --output-dir .../vcr/data` | "(unchanged)" | "(unchanged)" |
| `ruff format --check` | 1386 files already formatted | — |
| `ruff check` | All checks passed! | — |
| `vulture src/ whitelist.py --min-confidence 60` | no output (clean) | — |
| `unittest discover` | **2452 tests, OK** | re-ran once more standalone, also OK |

Manually read the generated `docs/MCP.md`: confirmed all 8 VCR tools, all 3 VCR resources, both VCR prompts, and the standalone `specmgr://dtais` resource appear with sensible descriptions.

### 3. ACC checkboxes marked

- **ACC-001** ✅ `Verifies` implemented exactly per spec, unit-tested in `tests/vcr/models/v1/test_body.py`/`test_parser.py`.
- **ACC-002** ✅ `Coverage` closed vocabulary tested in `tests/vcr/models/v1/test_body.py`.
- **ACC-003** ✅ `AC-NNN` heading regex/DTAIS vocabulary/duplicate rejection tested in `tests/vcr/models/v1/test_body.py`.
- **ACC-004** ✅ `VcrFrontmatter` status vocabulary tested in `tests/vcr/models/v1/test_frontmatter.py`.
- **ACC-005** ✅ Full domain exists end to end (`tests/vcr/` models/tools/resources/prompts + `general/tools` update/set_status cases); full suite passes.
- **ACC-006** ✅ `specmgr://dtais` exists, registered, documented in `docs/MCP.md`, content matches Design Notes sketch, tested in `tests/general/resources/test_dtais.py`.

### 4. Final quality-gate summary

**2452 tests, `OK`** (unchanged from Phase 3's count — Phase 4 added no new test files). `ruff format --check`, `ruff check`, and `vulture` all green.

### 5. Blockers / ambiguities

None. One deliberate judgment call worth flagging for your review: the task brief said root `README.md` "does NOT enumerate domains by name individually (except ADR)" and predicted no change needed — but the artifact list actually does enumerate every domain by name (confirmed by `feat-31-feature`'s own precedent of adding "Feature (FEAT)" there), so I added "Verification Case Record (VCR)" to keep it consistent with that established convention rather than leave it stale.
</task_result>
</task>
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 9.0s)

Let me now independently verify every claim before accepting this final phase.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git status --short"
}
```

**Output:**

```
 M .pre-commit-config.yaml
 M .specmgr/feat/feat-33-vcr/README.md
 M AGENTS.md
 M CHANGELOG.md
 M README.md
 M docs/GENERATED.md
 M docs/MCP.md
 M docs/api/README.md
 M docs/api/biz.dfch.specmgr.server.md
 M docs/api/biz.dfch.specmgr.vcr.md
 M src/biz/dfch/specmgr/server.py
 M src/biz/dfch/specmgr/vcr/__init__.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.3s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff src/biz/dfch/specmgr/vcr/__init__.py"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/vcr/__init__.py b/src/biz/dfch/specmgr/vcr/__init__.py
index d6e1a71..29f2b5c 100644
--- a/src/biz/dfch/specmgr/vcr/__init__.py
+++ b/src/biz/dfch/specmgr/vcr/__init__.py
@@ -15,12 +15,49 @@
 #
 # SPDX-License-Identifier: AGPL-3.0-or-later
 
-"""Verification Case Record (VCR) domain -- how a REQ/UC is verified.
-
-This is a domain-first package (per ADR ece4554b-725c-4f76-bc04-5d2b760363d2),
-still under construction: only ``vcr.models`` exists so far (Phase 1 --
-``.specmgr/feat/feat-33-vcr/README.md``). Deliberately does **not** yet import
-``tools``/``resources``/``prompts`` sub-packages -- those, and the resulting
-``from biz.dfch.specmgr import vcr  # noqa: F401`` domain-registration
-side-effect import, are Phase 2/3/4's job, not Phase 1's.
+"""Verification Case Record (VCR) domain -- how a single REQ/UC is verified.
+
+This is a domain-first package, mirroring ``dec``'s layout (per ADR
+ece4554b-725c-4f76-bc04-5d2b760363d2), containing models, tools, prompts, and
+resources for managing ``vcr`` documents. A VCR captures a coverage
+assessment plus a list of acceptance criteria, each with its own closed
+DTAIS verification method (Demonstration, Test, Analysis, Inspection,
+Special), for a single REQ or UC cross-reference. It is built on the
+generic ``models/md`` parser with the GOL/RSK/QA/DEC simple surface -- no
+fine-grained mutation tools (including no per-AC create/read/update/delete
+tools), no renderer: writes persist the caller's raw validated body
+byte-for-byte.
+
+Import this package to register all verification-case-record tools/prompts/
+resources against the shared ``mcp`` application instance at once::
+
+    from biz.dfch.specmgr import vcr  # noqa: F401 (side-effects only)
+
+``tools`` (``create_vcr``, ``parse_vcr``,
+``list_vcr``, ``get_vcr``, ``get_vcr_example``, ``get_vcr_template``,
+``delete_vcr``, ``validate_vcr``), ``resources`` (``specmgr://vcr/schema``,
+``specmgr://vcr/example``, ``specmgr://vcr/template``), and ``prompts``
+(``create_vcr``, ``update_vcr``) all exist; whole-body and line-range
+updates of an existing document go through the generic ``update`` tool in
+``general.tools`` (``type="vcr"``), and status changes go through the
+generic ``set_status`` tool in ``general.tools`` (``type="vcr"``). Like
+DEC, VCR has no
+``specmgr://vcr/{id}`` resource -- id-based reads go through the ``get_vcr``
+tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, there is no
+``specmgr://vcr/list`` resource -- ``list_vcr`` ships as a paged
+``@mcp.tool()`` from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
+
+The closed DTAIS verification-method vocabulary that this domain's
+``## Acceptance Criteria`` depends on is documented by the cross-cutting
+``specmgr://dtais`` resource, which lives in ``general.resources``, not
+here, since it is domain-knowledge other document types may also want to
+reference.
 """
+
+from . import prompts, resources, tools  # noqa: F401
+
+__all__ = [
+    "prompts",
+    "resources",
+    "tools",
+]

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.2s)

Good. Now let's check server.py's full diff for correctness.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff src/biz/dfch/specmgr/server.py"
}
```

**Output:**

```
diff --git a/src/biz/dfch/specmgr/server.py b/src/biz/dfch/specmgr/server.py
index dadf610..61c5de8 100644
--- a/src/biz/dfch/specmgr/server.py
+++ b/src/biz/dfch/specmgr/server.py
@@ -88,6 +88,17 @@ specmgr://feat/schema -- The generated FEAT JSON Schema, read from a packaged da
 specmgr://feat/example -- A complete, valid sample feature document as raw markdown.
 specmgr://feat/template -- A feature template (every field present, placeholder text)
                           as raw markdown.
+specmgr://vcr/schema -- The generated VCR JSON Schema, read from a packaged data copy
+                        (kept in sync with ``docs/vcr_schema.json``) so it works from a
+                        real, non-editable install.
+specmgr://vcr/example -- A complete, valid sample verification case record document as
+                        raw markdown.
+specmgr://vcr/template -- A verification case record template (every field present,
+                          placeholder text) as raw markdown.
+specmgr://dtais --      The DTAIS verification-method vocabulary (Demonstration, Test,
+                        Analysis, Inspection, Special), the five valid
+                        ``### AC-NNN (Method): ...`` method words, and when and how to
+                        apply each -- raw markdown domain-knowledge guidance.
 specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
                         characteristics (and sub-characteristics), each with a description.
 
@@ -116,6 +127,10 @@ id-based reads go through the ``get_gol`` tool only, and there is also no
  ``specmgr://feat/{id}`` resource either, for the same reason -- id-based
  reads go through the ``get_feat`` tool only, and there is also no
  ``specmgr://feat/list`` resource either -- ``list_feat`` ships as a paged
+ tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). VCR has no
+ ``specmgr://vcr/{id}`` resource either, for the same reason -- id-based
+ reads go through the ``get_vcr`` tool only, and there is also no
+ ``specmgr://vcr/list`` resource either -- ``list_vcr`` ships as a paged
  tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
 
 Tools
@@ -170,17 +185,21 @@ frontmatter-stripped body text verbatim instead of the parsed document), ``list_
   ``general/tools/_doc_paths.py``) and has no ``update_feat``/``set_status_feat`` tools of
   its own -- it dispatches through the generic ``update``/``set_status`` tools below from
   day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0), same as every other domain.
+  Verification case record tools (``vcr/tools/``): ``parse_vcr``, ``get_vcr``
+  (``raw=True`` returns the frontmatter-stripped body text verbatim instead of the
+  parsed document), ``list_vcr``, ``get_vcr_example``, ``get_vcr_template``,
+  ``create_vcr``, ``delete_vcr`` (stub, not yet implemented), ``validate_vcr``.
   General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
 preserving YAML frontmatter blocks; ``update`` -- whole-body or line-range replace of an
-existing document's content across the nine whole-body domains (``type`` is one of
-``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``; optional 1-based
-inclusive
+existing document's content across the ten whole-body domains (``type`` is one of
+``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``; optional
+1-based inclusive
 ``begin``/``end`` body-line range with the ``N+1`` end-of-body sentinel; the spliced
 result is validated as a whole document before anything is written); ``set_status`` --
-replace an existing document's status across all ten domains (``type`` is one of
-``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``adr``), also
-bumping
-``updated`` (the nine whole-body domains) and leaving the body untouched;
+replace an existing document's status across all eleven domains (``type`` is one of
+``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``feat``/``vcr``/``adr``),
+also bumping
+``updated`` (the ten whole-body domains) and leaving the body untouched;
 ``superseded_by`` is ``adr``-only (it composes the status as
 ``"superseded by {superseded_by}"``);
 ``webfetch`` -- fetch a URL over HTTP GET with a
@@ -221,6 +240,10 @@ Feature prompts (``feat/prompts/``): ``create_feat``, ``update_feat`` --
 narrated instruction flows guiding an LLM through the FEAT tool sequence
 above; ``create_feat`` first checks ``list_feat`` for a near-duplicate
 feature.
+Verification case record prompts (``vcr/prompts/``): ``create_vcr``,
+``update_vcr`` -- narrated instruction flows guiding an LLM through the VCR
+tool sequence above; ``create_vcr`` first checks ``list_vcr`` for a
+near-duplicate verification case record.
 General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
 older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
 ``README.md`` into an optional sibling ``history.md``, per ADR
@@ -230,18 +253,19 @@ Modules are grouped domain-first
 (ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
 document-type domain"): each document
 domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``,
-and later ``ac``) is a
+``vcr``, and later ``ac``) is a
 top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
 self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
-tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010`` resources,
-the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
+tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010``/``specmgr://dtais``
+resources, the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
 ``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
 Add a new domain by
 creating its top-level package and importing it at the bottom of this
 module, next to the existing
-``adr``/``dec``/``feat``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
+``adr``/``dec``/``feat``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``/``vcr``
 imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
-decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, and ``feat``
+decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``feat``,
+and ``vcr``
 each register ``tools``, ``resources``, and ``prompts``; ``general`` now also
 registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
 has no ``prompts`` sub-package yet.
@@ -275,4 +299,4 @@ mcp = MCPServer(
 # decorators to actually run.
 # ---------------------------------------------------------------------------
 
-from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401
+from . import adr, dec, feat, general, gol, prb, qa, req, rsk, tsk, uc, vcr  # noqa: E402, F401

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.6s)

This is thorough and accurate. Let's check the `.pre-commit-config.yaml` and `AGENTS.md` diffs.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff .pre-commit-config.yaml | head -150"
}
```

**Output:**

```
diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
index 1ea56d3..abbcd0c 100644
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -89,7 +89,7 @@ repos:
         description: >-
           Regenerate every registered doc-type JSON Schema (docs/{type}_schema.json)
           -- always runs with no `--type` (all registered types), currently `dec`,
-          `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, and `uc`. `specmgr schema` itself exits
+          `feat`, `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, `uc`, and `vcr`. `specmgr schema` itself exits
           non-zero when the
           regenerated content differs from what was already on disk, so no separate
           `git diff --exit-code` is needed here, unlike the other `specmgr-*` hooks
@@ -97,7 +97,7 @@ repos:
         entry: uv run --frozen specmgr schema
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-req-package
         name: specmgr schema (req package copy)
@@ -114,7 +114,7 @@ repos:
         entry: uv run --frozen specmgr schema --type req --output-dir src/biz/dfch/specmgr/req/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-uc-package
         name: specmgr schema (uc package copy)
@@ -131,7 +131,7 @@ repos:
         entry: uv run --frozen specmgr schema --type uc --output-dir src/biz/dfch/specmgr/uc/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-tsk-package
         name: specmgr schema (tsk package copy)
@@ -148,7 +148,7 @@ repos:
         entry: uv run --frozen specmgr schema --type tsk --output-dir src/biz/dfch/specmgr/tsk/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-rsk-package
         name: specmgr schema (rsk package copy)
@@ -165,7 +165,7 @@ repos:
         entry: uv run --frozen specmgr schema --type rsk --output-dir src/biz/dfch/specmgr/rsk/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-qa-package
         name: specmgr schema (qa package copy)
@@ -182,7 +182,7 @@ repos:
         entry: uv run --frozen specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-prb-package
         name: specmgr schema (prb package copy)
@@ -199,7 +199,7 @@ repos:
         entry: uv run --frozen specmgr schema --type prb --output-dir src/biz/dfch/specmgr/prb/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
       - id: specmgr-schema-gol-package
         name: specmgr schema (gol package copy)
         description: >-
@@ -215,7 +215,7 @@ repos:
         entry: uv run --frozen specmgr schema --type gol --output-dir src/biz/dfch/specmgr/gol/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-dec-package
         name: specmgr schema (dec package copy)
@@ -232,7 +232,7 @@ repos:
         entry: uv run --frozen specmgr schema --type dec --output-dir src/biz/dfch/specmgr/dec/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
 
       - id: specmgr-schema-feat-package
         name: specmgr schema (feat package copy)
@@ -249,4 +249,21 @@ repos:
         entry: uv run --frozen specmgr schema --type feat --output-dir src/biz/dfch/specmgr/feat/data
         language: system
         pass_filenames: false
-        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|models/md)/.*\.py$
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$
+
+      - id: specmgr-schema-vcr-package
+        name: specmgr schema (vcr package copy)
+        description: >-
+          Regenerate the packaged copy of VCR's JSON Schema
+          (src/biz/dfch/specmgr/vcr/data/vcr_schema.json), read by the
+          `specmgr://vcr/schema` MCP resource via `importlib.resources` so it
+          works from a real, non-editable install (unlike `docs/vcr_schema.json`,
+          which only resolves from an editable/source checkout). Same generator
+          as the `specmgr-schema` hook above, just a second `--output-dir` -- no
+          bespoke copy logic exists in `commands/schema.py`. Kept as an
+          independent hook (not chained into `specmgr-schema`) so each artifact's
+          drift check is its own clean gate.
+        entry: uv run --frozen specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data
+        language: system
+        pass_filenames: false
+        files: ^src/biz/dfch/specmgr/(dec/models/v1|feat/models/v1|gol/models/v1|prb/models/v1|qa/models/v2|req/models/v1|rsk/models/v1|tsk/models/v1|uc/models/v2|vcr/models/v1|models/md)/.*\.py$

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.0s)

Excellent, exactly as specified, all 10 occurrences updated plus the new hook. Now let's check AGENTS.md diff and CHANGELOG.md.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff AGENTS.md"
}
```

**Output:**

```
diff --git a/AGENTS.md b/AGENTS.md
index 60bce34..c8e1135 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -229,20 +229,59 @@ type or cross-cutting:
   exist, unlike every other domain's summary, whose `ref` field is
   deliberately *not* a path. See
   `.specmgr/feat/feat-31-feature/README.md` for the full design.
+- **`vcr/`** (Verification Case Record) — same tools/resources/prompts
+  shape as `req/`/`prb/`/`dec/` but for how a single REQ/UC is verified: a
+  `## Verifies` single-value cross-reference (exactly one mandatory
+  `REQ|UC <uuid>: <title>` line plus a mandatory `notes` paraphrase, not a
+  bullet list — a single-value field is structurally incapable of holding
+  more than one reference), a `## Coverage` closed-vocabulary outcome
+  signal (`full`/`partial`/`none`, mirroring RSK's `## Strategy` idiom),
+  and a `## Acceptance Criteria` collection of `### AC-NNN (Method): ...`
+  entries (3-digit zero-padded number, DEC-`Option`-style numbered H3, no
+  per-AC mutation tools; `Method` is a closed **DTAIS** vocabulary —
+  Demonstration, Test, Analysis, Inspection, Special — parsed from the
+  heading itself via regex, RSK `Probability`/`Impact`-style; each entry
+  optionally carries a free-form `description` paragraph and/or a
+  `#### Test Steps` numbered procedure; a `model_validator` rejects
+  duplicate `AC-NNN` numbers), plus optional `## More Information`/
+  `## Updates` (`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`,
+  `get_vcr_example`, `get_vcr_template`, `delete_vcr` stub,
+  `validate_vcr`); whole-body and line-range updates go through the
+  generic `update` tool in `general/tools/` (`type="vcr"`), status
+  changes through the generic `set_status` tool (`type="vcr"`), and the
+  `get_vcr` tool takes `raw: bool = False` — `raw=True` returns the
+  frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
+  index into); `vcr/resources/` (`specmgr://vcr/schema`,
+  `specmgr://vcr/example`, `specmgr://vcr/template`; no
+  `specmgr://vcr/{id}` — id-based reads are `get_vcr`-only, ADR
+  ddfb1109-422d-4507-8dbc-dc5e4bec9614; no `specmgr://vcr/list` —
+  `list_vcr` ships as a paged tool from day one, ADR
+  ec9f5262-9912-49d0-903f-fcfb54f28c13); `vcr/prompts/`
+  (`create_vcr`/`update_vcr`). Its schema lives at `vcr/models/v1/`,
+  inside the domain package, not top-level `models/`. The closed DTAIS
+  method vocabulary its `## Acceptance Criteria` depends on is documented
+  by the cross-cutting `specmgr://dtais` resource, which lives in
+  `general/resources/`, not `vcr/resources/`, since it is domain-knowledge
+  other document types may also want to reference (mirroring RSK's
+  `specmgr://rsk/tara` shape). See `.specmgr/feat/feat-33-vcr/README.md`
+  for the full design.
   - **`general/`** — cross-cutting, non-domain-specific package:
     `general/tools/` (`mdformat`, formats a markdown file in place while
     preserving YAML frontmatter blocks; `update`, the generic whole-body
-    *and* line-range replace for the nine whole-body domains — `type` is
-    one of req/uc/tsk/qa/prb/gol/rsk/dec/feat, optional 1-based inclusive
+    *and* line-range replace for the ten whole-body domains — `type` is
+    one of req/uc/tsk/qa/prb/gol/rsk/dec/feat/vcr, optional 1-based inclusive
     body-line
     `begin`/`end` with the `N+1` end-of-body sentinel, splice-then-
-    validate-whole; `set_status`, the generic status change for all ten
+    validate-whole; `set_status`, the generic status change for all eleven
     domains incl. adr — `superseded_by` is ADR-only, composing
     `"superseded by X"`), `general/resources/`
    (`specmgr://version`, `specmgr://iso25010` — the ISO/IEC 25010:2023
-   quality model), and `general/prompts/` (`compact_history` — rotates
+   quality model, `specmgr://dtais` — the DTAIS verification-method
+   vocabulary VCR's `## Acceptance Criteria` depends on, kept here rather
+   than under `vcr/resources/` since it is domain-knowledge other document
+   types may also want to reference), and `general/prompts/` (`compact_history` — rotates
     older `Recent Updates` entries out of any feature folder's `README.md`
-    into a sibling `history.md`). The nine `get_<d>` tools additionally
+    into a sibling `history.md`). The ten `get_<d>` tools additionally
     take a `raw: bool = False` parameter — `raw=True` returns the
     frontmatter-stripped body text as-is (the text `update`'s `begin`/`end`
     index into).
@@ -269,14 +308,14 @@ mirror of that same registration and must never be hand-edited.
 Still genuinely missing / not yet done (don't assume otherwise):
 - No `validate_adr` (or `validate_req`/`validate_uc`/`validate_tsk`/
   `validate_qa`/`validate_prb`/`validate_gol`/`validate_rsk`/
-  `validate_dec`/`validate_feat`) tool runs
+  `validate_dec`/`validate_feat`/`validate_vcr`) tool runs
   over the repo's
   own documents yet via pre-commit or CI. (ADR
   9c687bb1-8ee7-41c8-84ec-07606356bc73: "Enforce doc generation/lint/tests
   locally via pre-commit hook, not just CI")
 - `delete_req`/`delete_uc`/`delete_tsk`/`delete_qa`/`delete_prb`/
-  `delete_gol`/`delete_rsk`/`delete_dec`/`delete_feat` are stubs, not yet
-  implemented.
+  `delete_gol`/`delete_rsk`/`delete_dec`/`delete_feat`/`delete_vcr` are
+  stubs, not yet implemented.
 - No `ac` (Acceptance Criteria) domain exists yet, despite `server.py`'s
   docstring already reserving a spot for it ("... and later `ac`") — the
   convention for adding it (or any future domain) is fixed by ADR
@@ -284,9 +323,9 @@ Still genuinely missing / not yet done (don't assume otherwise):
   two generic tools in `general/tools/` (`update`'s `type`,
   `set_status`'s `type`) plus a `raw` parameter on the new `get_<d>` tool
   — not new `update_<d>`/`set_status_<d>` tools.
-- `req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`feat` each register `tools`,
-  `resources`, and `prompts`; `uc` registers `tools` and `resources`
-  only — it has no `prompts` sub-package yet.
+- `req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`feat`/`vcr` each register
+  `tools`, `resources`, and `prompts`; `uc` registers `tools` and
+  `resources` only — it has no `prompts` sub-package yet.
 
 `.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md` §10 ("Next steps") tracks per-item done/not-done
 status for the ADR feature specifically and should be kept in sync with
@@ -425,8 +464,8 @@ consumer of the base library.
 
 - Builds the `MCPServer` instance (`mcp` object) and a no-op `_lifespan`,
   then imports every domain package (`adr`, `dec`, `feat`, `general`,
-  `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, `uc`) as its last line purely for
-  the side effect of
+  `gol`, `prb`, `qa`, `req`, `rsk`, `tsk`, `uc`, `vcr`) as its last line
+  purely for the side effect of
   running their `@mcp.tool()`/`@mcp.resource()`/`@mcp.prompt()` decorators.
   When adding a new domain, add its import to that same last line —
   forgetting it means the new tools/resources/prompts silently never

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.5s)

This is thorough, accurate, and complete. Now let's check CHANGELOG.md and README.md diffs.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git diff CHANGELOG.md\necho \"=== README diff ===\"\ngit diff README.md"
}
```

**Output:**

```
diff --git a/CHANGELOG.md b/CHANGELOG.md
index eb8012c..a3686b6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,56 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ## [Unreleased]
 
+### Added
+
+- **Twelfth domain feature (VCR/Verification Case Record tooling)**: new
+  document-type domain, `vcr`, capturing how a single REQ/UC is verified --
+  a coverage assessment plus a list of DTAIS-classified acceptance
+  criteria. Fills a gap identified during `feat-32-sysrs` planning (no
+  existing domain modeled ISO/IEC/IEEE 29148's/MITRE SE Guide's
+  "Verification / Test and Evaluation" concept). Follows the domain-first
+  hierarchy (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and lands on the
+  "simple surface" from day one (ADR 36905d5b-8057-4294-8665-c7eed5534db0
+  -- no per-domain mutation tools, including no per-AC create/read/update/
+  delete tools):
+  - `vcr/models/v1/`: Pydantic schema (`VcrFrontmatter` with a closed
+    4-value status set `draft`/`progress`/`complete`/`approved`, `Vcr` body
+    with a mandatory `## Verifies` single-value cross-reference (exactly
+    one `REQ|UC <uuid>: <title>` line plus a mandatory `notes` paraphrase --
+    not a bullet list), a mandatory `## Coverage` closed-vocabulary outcome
+    signal (`full`/`partial`/`none`), a mandatory `## Acceptance Criteria`
+    collection of `### AC-NNN (Method): ...` entries (3-digit zero-padded
+    number, closed **DTAIS** method vocabulary parsed from the heading via
+    regex, optional `description` paragraph and/or `#### Test Steps`
+    numbered procedure, duplicate-number rejection via `model_validator`),
+    and optional `## More Information`/`## Updates`), parser (`parse_vcr`),
+    `VcrSummary`, and JSON schema generation, inside the domain package
+    itself.
+  - `vcr/tools/`: `@mcp.tool()` wrappers for the VCR lifecycle (`create_vcr`,
+    `parse_vcr`, `list_vcr`, `get_vcr` with `raw`, `get_vcr_example`,
+    `get_vcr_template`, `validate_vcr`), plus a stub for `delete_vcr`.
+    Generic `update(type="vcr", ...)`/`set_status(type="vcr", ...)` dispatch
+    adapters in `general/tools/update.py`/`set_status.py`.
+  - `vcr/resources/` (`specmgr://vcr/schema`, `specmgr://vcr/example`,
+    `specmgr://vcr/template` -- no `specmgr://vcr/{id}`, no
+    `specmgr://vcr/list`) and `vcr/prompts/` (`create_vcr`/`update_vcr`
+    narrated instruction flows; `create_vcr` first checks `list_vcr` for a
+    near-duplicate verification case record).
+  - A cross-cutting `specmgr://dtais` resource (`general/resources/dtais.py`
+    + `general/data/general_dtais.md`), explaining the DTAIS
+    verification-method vocabulary (Demonstration, Test, Analysis,
+    Inspection, Special) that VCR's `## Acceptance Criteria` depends on --
+    kept in `general/` rather than `vcr/`, since it is domain-knowledge
+    other document types may also want to reference, mirroring RSK's
+    `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` resources.
+  - `server.py` updated to import the new `vcr` domain package;
+    `.pre-commit-config.yaml`, `AGENTS.md`, and root `README.md` all
+    updated for the twelfth domain. `specmgr schema --type vcr` generates
+    `docs/vcr_schema.json` and the packaged copy.
+  - Comprehensive test coverage across `tests/vcr/models/`,
+    `tests/vcr/tools/`, `tests/vcr/resources/`, `tests/vcr/prompts/`, and
+    `tests/general/resources/test_dtais.py`.
+
 ## [0.14.0] - 2026-08-30
 
 ### Added
=== README diff ===
diff --git a/README.md b/README.md
index b8e4d31..30b9cde 100644
--- a/README.md
+++ b/README.md
@@ -28,6 +28,7 @@ At this time, we have these artifact:
 - Risk (RSK)
 - Task List (TSK)
 - Use Case (UC)
+- Verification Case Record (VCR)
 <!-- 
 - Acceptance Criterium (ACC)
 -->

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 9.9s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '15,35p' README.md"
}
```

**Output:**

```

This project is an **MCP server** that you can use to manage different
specification artifacts.

At this time, we have these artifact:

- Architecture Decision Record (ADR)
- Decision (DEC)
- Feature (FEAT)
- Goal (GOL)
- Problem Statement (PRB)
- Question and Answer (QA)
- Requirement (REQ)
- Risk (RSK)
- Task List (TSK)
- Use Case (UC)
- Verification Case Record (VCR)
<!-- 
- Acceptance Criterium (ACC)
-->


```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.5s)

Alphabetical, correctly placed. Now let's independently run the full quality gate and docs regeneration checks.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen ruff format --check 2>&1 | tail -5 && echo \"===check===\" && uv run --frozen ruff check 2>&1 | tail -10 && echo \"===vulture===\" && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1"
}
```

**Output:**

```
1386 files already formatted
===check===
All checks passed!
===vulture===

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 122.8s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && timeout 280 uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" > /tmp/full_test_run4.log 2>&1; echo \"EXIT:$?\"; grep -n \"Ran [0-9]* tests\\|^OK\\|FAILED\\|ERROR:\" /tmp/full_test_run4.log",
  "timeout": 290000
}
```

**Output:**

```
EXIT:0
9:Ran 2452 tests in 116.637s
11:OK

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 10.6s)

All 2452 tests pass. Let's confirm doc regeneration drift-freeness and adr-toc/schema.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen specmgr docs >/tmp/docs1.log 2>&1; echo \"docs exit:$?\"; git status --short docs/ | head\necho \"---\"\nuv run --frozen specmgr mcp-docs >/tmp/mcpdocs1.log 2>&1; echo \"mcp-docs exit:$?\"; git status --short docs/MCP.md\necho \"---\"\nuv run --frozen specmgr adr-toc >/tmp/adrtoc1.log 2>&1; echo \"adr-toc exit:$?\"; git status --short docs/adr/"
}
```

**Output:**

```
docs exit:0
 M docs/GENERATED.md
 M docs/MCP.md
 M docs/api/README.md
 M docs/api/biz.dfch.specmgr.server.md
 M docs/api/biz.dfch.specmgr.vcr.md
---
mcp-docs exit:0
 M docs/MCP.md
---
adr-toc exit:0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 10.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && uv run --frozen specmgr schema 2>&1; echo \"EXIT:$?\"\nuv run --frozen specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data 2>&1; echo \"EXIT:$?\""
}
```

**Output:**

```
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/dec_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/feat_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/gol_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/prb_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/qa_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/req_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/rsk_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/tsk_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/uc_schema.json (unchanged)
✓ Wrote /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr/docs/vcr_schema.json (unchanged)
EXIT:0
✓ Wrote src/biz/dfch/specmgr/vcr/data/vcr_schema.json (unchanged)
EXIT:0

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 5.8s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && sed -n '1,10p' .specmgr/feat/feat-33-vcr/README.md\necho \"---ACC checkboxes---\"\ngrep -n \"ACC-00\" .specmgr/feat/feat-33-vcr/README.md | head -10"
}
```

**Output:**

```
---
created: 2026-08-31 07:25:24.241609
id: feat-33-vcr
status: done
type: feat
updated: 2026-08-31 15:30:00
version: 1.1.0
---

# Feature: Add artifact type "Verification Case Record" (VCR)
---ACC checkboxes---
88:- [x] ACC-001: Verifies REQ-001 -- `Verifies` (`vcr/models/v1/body.py`) is
93:- [x] ACC-002: Verifies REQ-002 -- `Coverage`'s closed
96:- [x] ACC-003: Verifies REQ-003 -- the `### AC-NNN (Method): ...` heading
101:- [x] ACC-004: Verifies REQ-004 -- `VcrFrontmatter`'s closed
105:- [x] ACC-005: Verifies REQ-005 -- the full domain now exists end to end:
114:- [x] ACC-006: Verifies REQ-006 -- `specmgr://dtais` exists
576:files, only cross-cutting registration/docs). All ACC-001..006 confirmed
643:ACC-001..004 schema-level acceptance criteria) are now implemented and
750:Task List's Phase 4 checkboxes, walked every ACC-001..006 item and marked
1098:DTAIC -> DTAIS) throughout the current-design text (REQ-003, ACC-003,

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 4.2s)

All ACC checkboxes marked, status set to `done`, version bumped. Everything checks out. Let's stage and commit this final phase.

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git add -A && git status --short | wc -l"
}
```

**Output:**

```
12

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 3.8s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git status --short"
}
```

**Output:**

```
M  .pre-commit-config.yaml
M  .specmgr/feat/feat-33-vcr/README.md
M  AGENTS.md
M  CHANGELOG.md
M  README.md
M  docs/GENERATED.md
M  docs/MCP.md
M  docs/api/README.md
M  docs/api/biz.dfch.specmgr.server.md
M  docs/api/biz.dfch.specmgr.vcr.md
M  src/biz/dfch/specmgr/server.py
M  src/biz/dfch/specmgr/vcr/__init__.py

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 211.4s)

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git commit -m \"feat(feat-33-vcr): cross-cutting registration for the vcr domain (Phase 4)\" -m \"vcr/__init__.py now imports prompts/resources/tools (domain fully wired);\nserver.py imports vcr and its module docstring documents all 3 VCR\nresources, 8 tools, 2 prompts, and the specmgr://dtais resource, with\ndomain counts bumped (nine/ten whole-body domains -> ten/eleven).\n\nAGENTS.md gains a vcr/ Status bullet (mirroring dec/feat), updated\ndomain counts, and the delete_vcr/validate_vcr todo-list entries.\n\n.pre-commit-config.yaml: vcr/models/v1 added to all 10 existing\nspecmgr-schema* files: regexes, plus a new specmgr-schema-vcr-package\nhook mirroring the other 9 per-domain package-copy hooks.\n\nREADME.md gains \\\"Verification Case Record (VCR)\\\" in the artifact list;\nCHANGELOG.md gains an [Unreleased] entry for the twelfth domain feature.\n\ndocs/GENERATED.md, docs/MCP.md, docs/api/ regenerated and confirmed\ndrift-free (specmgr docs/mcp-docs/adr-toc/schema all exit 0 on a second\nrun). Full suite: 2452 tests, OK. ruff format/check and vulture clean.\n\nThis completes feat-33-vcr end to end: models, tools, resources,\nprompts, generic update/set_status dispatch, the cross-cutting\nspecmgr://dtais resource, and full cross-cutting registration. All\nACC-001..006 acceptance criteria confirmed; feature status set to done.\"",
  "timeout": 300000
}
```

**Output:**

```
ruff format..............................................................Passed
ruff check...............................................................Passed
vulture..................................................................Passed
unittest.................................................................Passed
specmgr coverage-badge...................................................Passed
specmgr docs.............................................................Passed
specmgr mcp-docs.........................................................Passed
specmgr adr-toc......................................(no files to check)Skipped
specmgr schema.......................................(no files to check)Skipped
specmgr schema (req package copy)....................(no files to check)Skipped
specmgr schema (uc package copy).....................(no files to check)Skipped
specmgr schema (tsk package copy)....................(no files to check)Skipped
specmgr schema (rsk package copy)....................(no files to check)Skipped
specmgr schema (qa package copy).....................(no files to check)Skipped
specmgr schema (prb package copy)....................(no files to check)Skipped
specmgr schema (gol package copy)....................(no files to check)Skipped
specmgr schema (dec package copy)....................(no files to check)Skipped
specmgr schema (feat package copy)...................(no files to check)Skipped
specmgr schema (vcr package copy)....................(no files to check)Skipped
[feat-33-vcr d900069] feat(feat-33-vcr): cross-cutting registration for the vcr domain (Phase 4)
 12 files changed, 511 insertions(+), 94 deletions(-)
 rewrite docs/api/biz.dfch.specmgr.vcr.md (94%)

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 6.6s)

_Thinking:_

**Tool: bash**

**Input:**

```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr.worktrees/feat-33-vcr && git log --oneline -6\necho \"---final status---\"\ngit status"
}
```

**Output:**

```
d900069 feat(feat-33-vcr): cross-cutting registration for the vcr domain (Phase 4)
2d58ab0 feat(feat-33-vcr): add vcr resources/prompts and specmgr://dtais (Phase 3)
19aeb13 feat(feat-33-vcr): add vcr tools and generic update/set_status dispatch (Phase 2)
c574949 feat(feat-33-vcr): add vcr/models/v1 schema, parser, and unit tests (Phase 1)
9984847 docs(feat-33-vcr): draft template.md, confirm AC-NNN regex/duplicate check (Phase 0)
28bd472 docs(feat-33): Verification Case Record (vcr)
---final status---
On branch feat-33-vcr
Your branch is ahead of 'origin/feat-33-vcr' by 5 commits.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean

```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 7.4s)

**Tool: todowrite**

**Input:**

```json
{
  "todos": [
    {
      "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
      "status": "completed",
      "priority": "high"
    },
    {
      "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
      "status": "completed",
      "priority": "high"
    }
  ]
}
```

**Output:**

```
[
  {
    "content": "Phase 0: Empirical schema validation (template.md draft, heading-regex/model_validator sanity check)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 1: Models and parser (vcr/models/v1/*, unit tests)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 2: Tools (8 standard tools + generic update/set_status dispatch)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 3: Resources and prompts (schema/example/template resources, create_vcr/update_vcr prompts, specmgr://dtais)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Phase 4: Cross-cutting registration (server.py, AGENTS.md, README.md, docs/adr-toc regen, full gate)",
    "status": "completed",
    "priority": "high"
  }
]
```

______________________________________________________________________

## Assistant (Phase-Orchestrator · Claude Sonnet 5 · 14.1s)

## feat-33-vcr complete — all 5 phases delivered and committed

Not pushed, per your instructions. Working tree is clean; branch is 5 commits ahead of `origin/feat-33-vcr`.

**Commits:**

```
9984847 docs(feat-33-vcr): draft template.md, confirm AC-NNN regex/duplicate check (Phase 0)
c574949 feat(feat-33-vcr): add vcr/models/v1 schema, parser, and unit tests (Phase 1)
19aeb13 feat(feat-33-vcr): add vcr tools and generic update/set_status dispatch (Phase 2)
2d58ab0 feat(feat-33-vcr): add vcr resources/prompts and specmgr://dtais (Phase 3)
d900069 feat(feat-33-vcr): cross-cutting registration for the vcr domain (Phase 4)
```

**Final acceptance-criteria walkthrough (all confirmed with concrete evidence):**

- **ACC-001** (`## Verifies`): `vcr/models/v1/body.py::Verifies` — single-value REQ|UC cross-reference + mandatory notes, regex-enforced; tested in `tests/vcr/models/v1/test_body.py`/`test_parser.py`.
- **ACC-002** (`## Coverage`): closed `full`/`partial`/`none` vocabulary, tested.
- **ACC-003** (`## Acceptance Criteria`): `### AC-NNN (Method): ...` regex, closed DTAIS vocabulary, duplicate-number rejection — all tested; empirically validated against `example.md`/`template.md` end-to-end via `parse_vcr`.
- **ACC-004** (frontmatter status): closed `draft`/`progress`/`complete`/`approved` set, tested.
- **ACC-005** (full domain): 8 tools, 3 resources, 2 prompts, generic `update`/`set_status` dispatch — all live-registered and tested (`tests/vcr/**`, 2452 tests total, all green).
- **ACC-006** (`specmgr://dtais`): resource shipped, registered in `general/resources/__init__.py` and `server.py`'s docstring, content covers all 5 DTAIS methods + `## Coverage` interaction, tested in `tests/general/resources/test_dtais.py`.

**Along the way I caught and corrected two real schema gaps** (both my own delegation errors, fixed by resuming the same subagent rather than escalating, since they were unambiguously implied by the already-finalized `example.md`):

1. Missing optional `description` paragraph on `AcceptanceCriterion`.
2. Missing comment support on `Updates` (`MarkdownSection2WithComment`).

Both are now empirically verified: `example.md` and `template.md` parse successfully end-to-end against the final schema.

**Final gate:** `ruff format --check` / `ruff check` / `vulture` all clean; full suite **2452 tests, OK**; `specmgr docs`/`mcp-docs`/`adr-toc`/`schema` all regenerated and confirmed drift-free on a second run.

No blockers hit, no user decisions were needed beyond the two self-corrections above (which I resolved directly since they followed unambiguously from already-decided, already-committed design artifacts). The feature folder's `status` is now `done`.

______________________________________________________________________
