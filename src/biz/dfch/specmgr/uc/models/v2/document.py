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

"""Pydantic model for a full use-case document (frontmatter + body).

Mirrors `models.adr.v1.Adr`'s own frontmatter+body pairing. `UcDocument` holds
no file/id/path information itself -- that lives on `frontmatter.id`, same
convention as `AdrFrontmatter.id`.

Frontmatter *stripping* is deliberately not this module's responsibility
(feat-5-md-model-parser's REQ-003/`MarkdownFrontmatter`'s own convention):
a caller splits a raw `.md` file's `---...---` block from its body via
`python-frontmatter` (`frontmatter.loads(text)`), validates `.metadata` as
`UcFrontmatter` and `.content` as `UseCase.from_text(...)` separately, then
constructs a `UcDocument` from the two already-parsed pieces -- there is no
`UcDocument.from_text`/parser function here (unlike `models.adr.v1.parser`,
which is a separate, not-yet-ported concern; see `.specmgr/feat/feat-4-use-cases/README.md`).
"""

from __future__ import annotations

from pydantic import BaseModel

from .frontmatter import UcFrontmatter
from .use_case import UseCase

__all__ = ["UcDocument"]


class UcDocument(BaseModel):
    """A full use-case document: YAML frontmatter and body.

    Parameters
    ----------
    frontmatter:
        The YAML frontmatter block. See :class:`UcFrontmatter`.
    body:
        The parsed use-case sections. See :class:`UseCase`.
    """

    frontmatter: UcFrontmatter
    body: UseCase
