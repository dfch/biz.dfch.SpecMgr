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

"""Shared frontmatter+body composition/write helper for ``create_set`` and
the generic ``update`` tool in ``general.tools`` (``type="set"``).

Deliberately **not** part of ``set.tools._io`` -- that module's own
docstring rules out a ``write_set``/``render_set`` counterpart to
``read_set``, since neither ``create_set`` nor the generic ``update`` tool
in ``general.tools`` ever render a body back out from a parsed
:class:`~biz.dfch.specmgr.set.models.v1.SetDocument` model. What
:func:`write_set_file` does instead is a strictly narrower thing: combine an
already-constructed, already-validated
:class:`~biz.dfch.specmgr.set.models.v1.SetFrontmatter` with the caller's
own already-validated *raw* body text (never reformatted/re-rendered) into
one file. Factored out of ``create_set.py`` into its own module so the
generic ``update`` and ``set_status`` tools in ``general.tools``
(``type="set"``) do not have to duplicate it. Mirrors ``vcr.tools._write``
file-for-file.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from ..models.v1 import SetFrontmatter

__all__ = ["write_set_file"]


def write_set_file(path: Path, frontmatter_: SetFrontmatter, content: str) -> None:
    """Compose a full set document file (frontmatter + body) and write it to ``path``.

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
