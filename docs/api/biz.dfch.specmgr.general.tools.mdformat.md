# `biz.dfch.specmgr.general.tools.mdformat`

``@mcp.tool()`` wrapper: mdformat.

Formats a markdown file in place, preserving YAML frontmatter blocks (if
present) and formatting only the body markdown. Returns a boolean indicating
whether the file's content changed.

## Functions

### `mdformat(path: 'str') -> 'bool'`

Format the markdown file at ``path`` in place.

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

