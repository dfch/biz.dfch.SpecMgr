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

"""Parse raw feature (FEAT) ``.md`` text into a :class:`FeatDocument`.

Fills the ``from_text``/parser entry-point gap ``document.py``'s own docstring
flags: ``FeatDocument`` deliberately holds no such method itself, and the generic
``models/md`` engine only ever parses a *body* (``Feature.from_text``), never
the combination of frontmatter + body a full on-disk file is. This module is
the thin free-function glue between the two, mirroring
``dec/models/v1/parser.parse_dec``/``gol/models/v1/parser.parse_gol``'s own
layout -- a free function, not a classmethod on the document model.

Parsing requires the ``frontmatter`` extra (``python-frontmatter``) to split
YAML frontmatter from markdown body text before delegating to the generic
MarkdownStr engine. Two error channels:

- ``AssertionError`` for structural problems (unrecognized headings, missing
  mandatory sections), propagating naturally from ``process_field``/``from_text``.
- ``pydantic.ValidationError`` for value/validation failures on field values or
  cross-field invariants (e.g. a closed-set ``status`` violation, or an
  out-of-order ``### Updates``/``### Decisions Made`` entry) --
  deliberately left uncaught here, same as all other parsers in the project.

REQ-003 notes one deliberate exception scoped to the *tool* layer, not this
module: the invariant "frontmatter ``id`` equals the containing folder's
name" is enforced by ``feat/tools/_paths.py``/``_io.py`` (Phase 2), not
here -- this module's ``parse_feat(text: str)`` has no path/folder-name to
check against, matching every other domain's pure-text model-layer parser
signature.

Like ``dec.models.v1.parser.parse_dec``/``gol.models.v1.parser.parse_gol``,
there is no dedicated structural-error exception type (no ``FeatParseError``
equivalent); both error channels are plain ``AssertionError`` /
``pydantic.ValidationError`` that propagate uncaught.
"""

from __future__ import annotations

import frontmatter  # requires the ``frontmatter`` extra from pyproject.toml

from biz.dfch.specmgr.models.md._markdown import format_text

from .body import Feature
from .document import FeatDocument
from .frontmatter import FeatFrontmatter

__all__ = ["parse_feat"]


def parse_feat(text: str) -> FeatDocument:
    """Parse a full feature ``.md`` file's text into a :class:`FeatDocument`.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body
        together, exactly as read from disk (or submitted verbatim by an MCP
        tool call that never wrote it to disk at all).

    Returns
    -------
    FeatDocument
        The structured document. Raises ``AssertionError`` for a malformed
        heading/list structure, or ``pydantic.ValidationError`` for a
        structurally-sound document whose field values (or cross-field
        invariants) fail schema validation -- see this module's docstring
        for the full split.
    """
    post = frontmatter.loads(text)  # type: ignore[union-attr]
    fm = FeatFrontmatter.model_validate(_stringify_metadata(post.metadata))
    body = Feature.from_text(format_text(post.content))
    return FeatDocument(frontmatter=fm, body=body)


def _stringify_metadata(metadata: dict[str, object]) -> dict[str, object]:
    """Coerce YAML-native scalar types back to ``str`` (or ``None``).

    ``python-frontmatter`` parses the YAML block using PyYAML's standard loader,
    which auto-converts unquoted dates/timestamps into Python datetime objects,
    but every :class:`FeatFrontmatter` field inherited from
    :class:`~biz.dfch.specmgr.models.md.MarkdownFrontmatter` is ``str | None``,
    so a raw non-``str`` object would fail Pydantic's (deliberately non-coercive)
    string validation. Converting via ``str()`` reproduces what a human would have
    written.  ``None`` (from an empty YAML key like ``version:``) is passed
    through so the field's own optional-ness applies normally.

    Mirrors the same helper in ``dec/models/v1/parser._stringify_metadata``/
    ``gol/models/v1/parser._stringify_metadata``.
    """
    return {key: value if value is None or isinstance(value, str) else str(value) for key, value in metadata.items()}
