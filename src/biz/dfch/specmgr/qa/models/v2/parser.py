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

"""Parse raw Question and Answer (QA) ``.md`` text into a :class:`QaDocument` (v2).

Mirrors `qa/models/v1/parser.py::parse_qa`'s structure exactly (same
``frontmatter.loads``/``_stringify_metadata`` approach), and -- per
REQ-004's revised wording (2026-08-23, see the feature README's Decisions
Made) -- mirrors `uc/models/v2/parser.py::parse_uc`'s unconditional-v2-
parsing shape exactly too: there is no runtime `version` inspection/gate
here at all. `QaFrontmatter.version` was found to encode the shared
`models.md` parsing engine's own schema version (hardcoded to major 1,
`models/md/_util.py::SCHEMA_MAJOR_VERSION`), not a per-document-type body-
schema version, and can never carry a major-2 value for any document that
validates as `QaFrontmatter` at all -- so no `version`-based dispatch is
possible. This function always parses the body via v2's own `Qa` schema; a
v1-shaped (or otherwise non-v2-shaped) document simply fails naturally with
whatever structural `AssertionError`/`pydantic.ValidationError`
`Qa.from_text`/`QaFrontmatter.model_validate` raises on its own -- there is
no fallback to v1 parsing and no explicit version check, since there is no
v1 code path reachable here at all.

``_stringify_metadata`` is duplicated locally here (not imported from
`qa/models/v1/parser.py`), matching this codebase's "v2 has zero dependency
on v1 beyond `QaFrontmatter`" constraint (REQ-003 / feature README Design
Notes).

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants -- deliberately left uncaught here, same as all other
  parsers in the project.
"""

from __future__ import annotations

import frontmatter  # requires the ``frontmatter`` extra from pyproject.toml

from biz.dfch.specmgr.models.md._markdown import format_text

from ..v1.frontmatter import QaFrontmatter
from .body import Qa
from .document import QaDocument

__all__ = ["parse_qa"]


def parse_qa(text: str) -> QaDocument:
    """Parse a full Question and Answer (QA) ``.md`` file's text into a :class:`QaDocument` (v2).

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by an MCP
        tool call that never wrote it to disk at all).

    Returns
    -------
    QaDocument
        The structured v2 document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values (or cross-field
        invariants) fail schema validation -- see this module's docstring
        for the full split.
    """
    post = frontmatter.loads(text)  # type: ignore[union-attr]
    fm = QaFrontmatter.model_validate(_stringify_metadata(post.metadata))
    body = Qa.from_text(format_text(post.content))
    return QaDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python datetime objects,
    but every :class:`QaFrontmatter` field inherited from
    :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
    so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
    string validation. Converting via ``str()`` reproduces what a human would have
    written.  ``None`` (from an empty YAML key like ``version:``) is passed
    through so the field's own optional-ness applies normally.

    Duplicated locally from ``qa/models/v1/parser._stringify_metadata`` (not
    imported), per this module's "zero dependency on v1 beyond
    `QaFrontmatter`" constraint.
    """
    return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}
