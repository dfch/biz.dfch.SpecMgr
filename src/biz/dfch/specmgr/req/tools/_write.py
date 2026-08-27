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

"""Shared frontmatter+body composition/write helper for ``create_req`` and
the generic ``update`` tool in ``general.tools`` (``type="req"``).

Deliberately **not** part of ``req.tools._io`` -- that module's own docstring
rules out a ``write_req``/``render_req`` counterpart to ``read_req``, since
Task 3.9's design never renders a body back out from a parsed
:class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` model (unlike
``adr.tools._io.write_adr``, which does via ``render_adr``). What
:func:`write_req_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter` with the caller's own
already-validated *raw* body text (never reformatted/re-rendered) into one
file. Factored out of ``create_req.py`` into its own module so the generic
``update`` tool in ``general.tools`` does not have to duplicate it.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from ..models.v1 import ReqFrontmatter

__all__ = ["write_req_file"]


def write_req_file(path: Path, frontmatter_: ReqFrontmatter, content: str) -> None:
    """Compose a full requirement file (frontmatter + body) and write it to ``path``.

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
