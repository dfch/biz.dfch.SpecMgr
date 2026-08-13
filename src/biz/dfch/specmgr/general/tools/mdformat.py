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

"""``@mcp.tool()`` wrapper: mdformat.

Formats a markdown file in place, preserving YAML frontmatter blocks (if
present) and formatting only the body markdown. Returns a boolean indicating
whether the file's content changed.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from ...models.md._markdown import format_text
from ...server import mcp


@mcp.tool(
    name="mdformat",
    title="Format markdown document",
    description=(
        "Format a markdown file in place, preserving any YAML frontmatter. "
        "Returns True if the file was changed, False if already formatted."
    ),
)
def mdformat(path: str) -> bool:
    """Format the markdown file at ``path`` in place.

    Reads the file, detects any leading YAML frontmatter block (e.g. in ADR/UC
    files), and normalizes only the body markdown using ``mdformat``. The
    frontmatter itself is re-serialized to preserve valid YAML (key order may
    change, value types and quoting may normalize), but never modified in
    content. Files without frontmatter are formatted as-is.

    The file is only written to disk if the formatted content differs from the
    original; if no changes are needed, the file is left untouched (mtime
    unchanged).

    The returned boolean indicates whether the file's content changed and was
    written back to disk:
    - ``True``: file was reformatted and written.
    - ``False``: file was already in canonical form; no write occurred.

    Parameters
    ----------
    path:
        The filesystem path to the ``.md`` file to format (absolute or
        relative to the current working directory).

    Returns
    -------
    bool
        ``True`` if the file was modified and written; ``False`` if it was
        already in canonical form and left untouched.

    Raises
    ------
    FileNotFoundError
        The file at ``path`` does not exist.
    PermissionError
        The file cannot be read or written (permission denied).
    OSError
        Any other file I/O error.
    """
    file_path = Path(path)
    original_text = file_path.read_text(encoding="utf-8")

    # Parse YAML frontmatter if present.
    post = frontmatter.loads(original_text)

    # Format the body markdown only; preserve frontmatter verbatim.
    if post.metadata:
        post.content = format_text(post.content)
        formatted_text = frontmatter.dumps(post)
    else:
        # No frontmatter; format the whole text as markdown.
        formatted_text = format_text(original_text)

    # Ensure exactly one trailing newline (canonical form).
    if not formatted_text.endswith("\n"):
        formatted_text += "\n"

    # Only write if content changed.
    if formatted_text != original_text:
        file_path.write_text(formatted_text, encoding="utf-8")
        return True

    return False
