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

"""Shared frontmatter+body composition/write helper for ``create_feat`` and
the generic ``update`` tool in ``general.tools`` (``type="feat"``).

Mirrors ``dec.tools._write.write_dec_file``'s shape and "content embedded
verbatim, never reformatted/re-rendered" contract, with one feat-only
addition: :func:`write_feat_file` also creates the document's own
``<base>/<id>/`` parent folder if it does not exist yet, since ``feat`` is
folder-per-document (unlike ``dec``'s flat ``<base>/<filename>.md``) --
``create_feat`` writes into a brand new folder on every call, and the
generic ``update``/``set_status`` tools (``type="feat"``) always target an
already-existing folder, so this is a no-op for them (``exist_ok=True``).
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from ..models.v1 import FeatFrontmatter

__all__ = ["write_feat_file"]


def write_feat_file(path: Path, frontmatter_: FeatFrontmatter, content: str) -> None:
    """Compose a full feature file (frontmatter + body) and write it to ``path``.

    ``content`` is embedded verbatim -- it is never reformatted/re-rendered
    here. One caveat inherent to the underlying ``python-frontmatter``
    library, not specially handled here: its ``YAMLHandler`` strips trailing
    whitespace from ``content`` when serializing, so the written body may
    differ from ``content`` by trailing whitespace only, never in substance.

    Parameters
    ----------
    path:
        The destination file path, e.g. ``<base>/<id>/README.md``. Its
        parent folder is created (with any missing intermediate
        directories) if it does not exist yet.
    frontmatter_:
        The already-constructed, already-validated frontmatter to serialize
        as the file's YAML block.
    content:
        The raw body markdown, exactly as submitted by the caller.
    """
    assert isinstance(path, Path), type(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    post = frontmatter.Post(content=content, **frontmatter_.model_dump())
    text = frontmatter.dumps(post)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
