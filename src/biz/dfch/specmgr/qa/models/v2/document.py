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

"""Pydantic model for a full Question and Answer (QA) v2 document (frontmatter + body).

Pairs `frontmatter.py`'s `QaFrontmatter` with `body.py`'s `Qa`. `QaDocument`
holds no file/id/path information itself -- that lives on `frontmatter.id`.

`frontmatter` is `QaFrontmatter` (QA's frontmatter shape has never been
versioned independently of the body schema, so it lives directly in
`qa/models/v2/` alongside the rest of the schema, not under its own `v1`/`v2`
split). `body` is `Qa` from `qa/models/v2/body.py`.

Frontmatter *stripping* is deliberately not this module's responsibility: a
caller splits a raw ``.md`` file's ``---...---`` block from its body via
``python-frontmatter`` (``frontmatter.loads(text)``), validates ``.metadata``
as `QaFrontmatter` and ``.content`` as `Qa.from_text(...)` separately, then
constructs a `QaDocument` from the two already-parsed pieces -- see
`qa/models/v2/parser.py::parse_qa` for that glue.
"""

from __future__ import annotations

from pydantic import BaseModel

from .body import Qa
from .frontmatter import QaFrontmatter

__all__ = ["QaDocument"]


class QaDocument(BaseModel):
    """A full Question and Answer (QA) v2 document: YAML frontmatter and body.

    Attributes
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`~biz.dfch.specmgr.qa.models.v2.frontmatter.QaFrontmatter`.
    body:
        The parsed Q&A sections. See :class:`~biz.dfch.specmgr.qa.models.v2.body.Qa`.
    """

    frontmatter: QaFrontmatter
    body: Qa
