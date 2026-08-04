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

"""ADR base directory resolution, filename slugification, and id -> path
lookup (plan §9a).

Deliberately excludes any ``mcp``/file-write dependency beyond read-only
directory listing/parsing, so this module stays testable without an MCP
server: ``adr_base_dir`` never creates the directory (a read-only tool
shouldn't have that side effect), only ``ensure_adr_base_dir`` does, and
only ``create_adr`` (in ``tools.py``) calls it.

There is deliberately no in-memory id -> path cache (plan §9a): every
lookup re-scans the base directory and re-parses each file's frontmatter,
matching the "the on-disk file is the sole source of truth" design (plan
§7) and avoiding a staleness problem against concurrent human edits.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from ...models.adr import AdrParseError, parse_adr

__all__ = [
    "ADR_DIR_ENV_VAR",
    "DEFAULT_ADR_DIR",
    "AdrNotFoundError",
    "adr_base_dir",
    "ensure_adr_base_dir",
    "find_adr_path",
    "iter_adr_paths",
    "slugify",
]

#: Environment variable that overrides the ADR base directory (plan §9a).
ADR_DIR_ENV_VAR = "SPECMGR_ADR_DIR"

#: Default ADR base directory, relative to the current working directory.
DEFAULT_ADR_DIR = Path("docs/adr")

#: Anything that isn't a lowercase ASCII letter or digit, run-collapsed.
_NON_ALNUM_RUN_PATTERN = re.compile(r"[^a-z0-9]+")

#: Maximum length of a slugified title (plan §9a's filename scheme).
_SLUG_MAX_LENGTH = 60


class AdrNotFoundError(LookupError):
    """No ADR file found matching the given id."""


def adr_base_dir() -> Path:
    """Return the configured ADR base directory, without creating it.

    Reads :data:`ADR_DIR_ENV_VAR` from the environment, falling back to
    :data:`DEFAULT_ADR_DIR`. Read-only tools (``get_adr``, ``option_list``,
    ...) use this so merely reading never has the side effect of creating
    the directory -- see :func:`ensure_adr_base_dir` for the write path.
    """
    value = os.environ.get(ADR_DIR_ENV_VAR)
    return Path(value) if value else DEFAULT_ADR_DIR


def ensure_adr_base_dir() -> Path:
    """Return the configured ADR base directory, creating it if missing.

    Only ``create_adr`` (``tools.py``) calls this -- every other tool uses
    the read-only :func:`adr_base_dir` instead.
    """
    path = adr_base_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(title: str) -> str:
    """Derive a filename-safe slug from an ADR title (plan §9a).

    Lowercases ``title``, collapses every run of non-``[a-z0-9]``
    characters into a single ``-``, strips leading/trailing ``-``,
    truncates to :data:`_SLUG_MAX_LENGTH` characters (stripping a trailing
    ``-`` again in case the truncation lands mid-run), and falls back to
    ``"adr"`` if the result would otherwise be empty (e.g. a title with no
    alphanumeric characters at all).
    """
    slug = _NON_ALNUM_RUN_PATTERN.sub("-", title.lower()).strip("-")
    slug = slug[:_SLUG_MAX_LENGTH].strip("-")
    return slug or "adr"


def iter_adr_paths(base_dir: Path) -> Iterator[Path]:
    """Yield every ``*.md`` file directly under ``base_dir``, sorted by name.

    Yields nothing (rather than raising) if ``base_dir`` does not exist.
    """
    if not base_dir.exists():
        return iter(())
    return iter(sorted(base_dir.glob("*.md")))


def find_adr_path(base_dir: Path, id_: str) -> Path:
    """Resolve an ``id`` to its on-disk file path (plan §9a).

    Scans every ``*.md`` file under ``base_dir``, parsing each and
    comparing ``frontmatter.id`` against ``id_``. A file that fails to
    parse (:class:`AdrParseError` or ``pydantic.ValidationError``) is
    silently skipped -- one broken file must not prevent lookup of a
    different, valid id.

    Raises
    ------
    AdrNotFoundError
        If no file's ``frontmatter.id`` matches ``id_``.
    """
    for path in iter_adr_paths(base_dir):
        try:
            adr = parse_adr(path.read_text(encoding="utf-8"))
        except (AdrParseError, ValidationError):
            continue
        if adr.frontmatter.id == id_:
            return path
    raise AdrNotFoundError(f"no ADR found with id {id_!r}")
