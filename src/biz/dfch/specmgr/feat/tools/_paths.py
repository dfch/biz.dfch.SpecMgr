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

"""Feature (FEAT) base directory resolution and id -> path lookup (Task 2.1).

**Hand-rolled, ADR-style** (mirrors ``adr.tools._paths``), deliberately
**not** built on the shared, flat-file ``general.tools._doc_paths`` --
that module assumes one file per document directly under the base
directory (``<base>/<type>-<uuid>-<slug>.md``); ``feat`` is folder-per-
document instead (``<base>/<id>/README.md``, a fixed filename), and
``id`` is a chosen ``feat-NNN-slug`` string, not a server-generated UUID.
See ``.specmgr/feat/feat-31-feature/README.md`` Design Notes
("Addressing") for the full rationale.

Mirrors ``adr.tools._paths``'s read-only/write split: :func:`feat_base_dir`
never creates the directory (a read-only tool shouldn't have that side
effect), only :func:`ensure_feat_base_dir` does, for ``create_feat``. There
is deliberately no in-memory id -> path cache either -- every lookup
re-reads whatever is currently on disk, matching this codebase's "the
on-disk file is the sole source of truth" design.

**The key behavioral divergence from every other (UUID-addressed) domain**:
since ``id`` *is* the containing folder's own name by convention (REQ-004),
:func:`find_feat_path_by_id` shortcuts directly to ``<base>/<id_>/README.md``
instead of scanning every document under the base directory and comparing
each one's parsed ``frontmatter.id`` -- there is no directory scan, and
therefore no partial-id-match support either (a bare ``"feat-31"`` never
resolves to ``"feat-31-feature"``; see this feature's own Decisions Made log
for why that was considered and explicitly rejected).

**Parse-failure handling on the shortcut read.** Every other domain's
``find_*_path`` scans multiple files and *skips* a file that fails to parse
(``AssertionError``/``pydantic.ValidationError``) so one broken file never
blocks lookup of a different, valid id -- there is no "different file" to
fall back to here, since the shortcut only ever reads one path. A parse
failure on that single target file is therefore treated the same as the
file not existing at all: both raise :class:`FeatNotFoundError`, just with
a message that distinguishes "the folder/file is missing" from "the folder
exists but its content is unparseable, or its frontmatter ``id`` does not
match the folder name it lives in" -- so ``load_by_id``/``get_feat``/every
mutating tool built on this module gets one single, consistent
not-found-shaped error to handle, without needing to separately catch
``AssertionError``/``ValidationError`` themselves.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from ...general.tools._doc_paths import slugify
from ..models.v1 import parse_feat

__all__ = [
    "DEFAULT_FEAT_DIR",
    "FEAT_DIR_ENV_VAR",
    "FEAT_TYPE_NAME",
    "README_FILENAME",
    "FeatNotFoundError",
    "ensure_feat_base_dir",
    "feat_base_dir",
    "feature_title",
    "find_feat_path_by_id",
    "iter_feat_paths",
    "slugify",
]

#: Environment variable that overrides the feature base directory. Mandatory-
#: equivalent, like every other domain's own env var (``SPECMGR_ADR_DIR``,
#: the shared ``SPECMGR_DOCS_DIR``) -- without it, tests would have no way
#: to avoid reading/writing the real ``.specmgr/feat/`` (this very feature
#: plan's own folder).
FEAT_DIR_ENV_VAR = "SPECMGR_FEAT_DIR"

#: Default feature base directory, relative to the current working
#: directory -- the same folder this feature's own plan file lives in, in
#: production.
DEFAULT_FEAT_DIR = Path(".specmgr/feat")

#: The doc-type name, for symmetry with every other domain's own
#: ``<D>_TYPE_NAME`` constant (e.g. ``dec.tools._paths.DEC_TYPE_NAME``),
#: even though it plays no role in path construction here (unlike the
#: generic ``general.tools._doc_paths`` domains, ``feat``'s base directory
#: is not ``{docs root}/feat`` -- it *is* the configured base directory
#: itself).
FEAT_TYPE_NAME = "feat"

#: The fixed filename every feature document is stored under, inside its
#: own ``<base>/<id>/`` folder.
README_FILENAME = "README.md"

#: The literal prefix every well-formed ``Feature`` H1 heading carries.
#: ``Feature.text`` (inherited from ``MarkdownSection``) always returns the
#: *whole* heading line, e.g. ``"Feature: My Title"`` -- not just the
#: free-form title after the colon -- because `Feature`'s own ``@alias``
#: regex (``"^Feature: .+$"``) matches the entire line, and `Feature`
#: declares no ``title`` computed field of its own (unlike `Phase`/
#: `UpdateEntry`/`DecisionEntry`, each of which does). Both `create_feat`
#: (folder-name slug derivation) and `list_feat` (`FeatSummary.title`) need
#: just the free-form part, so :func:`feature_title` strips it once here
#: rather than duplicating the same two lines in both tools.
_TITLE_PREFIX = "Feature: "


class FeatNotFoundError(LookupError):
    """No feature folder/document found matching the given id.

    Raised both when ``<base>/<id_>/README.md`` does not exist at all, and
    when it exists but fails to parse or its frontmatter ``id`` does not
    match the folder name it was found under -- see this module's own
    docstring for why both cases collapse to the same exception type here.
    """


def feat_base_dir() -> Path:
    """Return the configured feature base directory, without creating it.

    Reads :data:`FEAT_DIR_ENV_VAR` from the environment, falling back to
    :data:`DEFAULT_FEAT_DIR`. Read-only tools (``get_feat``, ``list_feat``,
    ...) use this so merely reading never has the side effect of creating
    the directory -- see :func:`ensure_feat_base_dir` for the write path.

    Returns
    -------
    Path
        The resolved feature base directory.
    """
    value = os.environ.get(FEAT_DIR_ENV_VAR)
    result = Path(value) if value else DEFAULT_FEAT_DIR
    return result


def ensure_feat_base_dir() -> Path:
    """Return the configured feature base directory, creating it if missing.

    Only ``create_feat`` should call this -- every other tool uses the
    read-only :func:`feat_base_dir` instead.

    Returns
    -------
    Path
        The resolved, now-guaranteed-to-exist feature base directory.
    """
    path = feat_base_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def feature_title(text: str) -> str:
    """Strip the literal ``"Feature: "`` prefix off a ``Feature.text`` heading value.

    Parameters
    ----------
    text:
        A ``Feature.text`` value, e.g. ``"Feature: My Title"``.

    Returns
    -------
    str
        ``text`` with the literal ``"Feature: "`` prefix removed, if
        present (it always is for any ``Feature`` that parsed
        successfully, since the prefix is enforced by `Feature`'s own
        ``@alias`` regex) -- returned unchanged otherwise.
    """
    assert isinstance(text, str), type(text)

    result = text.removeprefix(_TITLE_PREFIX)
    return result


def iter_feat_paths(base_dir: Path) -> Iterator[Path]:
    """Yield every ``<base_dir>/*/README.md`` path, sorted by folder name.

    Unlike every generic-``_doc_paths``-based domain's ``iter_*_paths``
    (which globs ``*.md`` directly under the base directory), this globs
    one level deeper -- ``*/README.md`` -- since ``feat`` is folder-per-
    document, not flat-file. Yields nothing (rather than raising) if
    ``base_dir`` does not exist.

    Parameters
    ----------
    base_dir:
        The feature base directory to scan (typically :func:`feat_base_dir`'s
        return value).

    Returns
    -------
    Iterator[Path]
        An iterator over the matching, sorted paths.
    """
    assert isinstance(base_dir, Path), type(base_dir)

    if not base_dir.exists():
        return iter(())
    result = iter(sorted(base_dir.glob(f"*/{README_FILENAME}")))
    return result


def find_feat_path_by_id(base_dir: Path, id_: str) -> Path:
    """Resolve ``id_`` to its on-disk ``README.md`` path under ``base_dir``.

    Shortcuts directly to ``<base_dir>/<id_>/README.md`` -- since ``id`` is,
    by REQ-004's addressing convention, the containing folder's own name,
    there is no need (and deliberately no support) for a full directory
    scan or partial-id matching (see this module's own docstring).

    Parameters
    ----------
    base_dir:
        The feature base directory (typically :func:`feat_base_dir`'s
        return value).
    id_:
        The id to look up -- must be the *exact* folder name, e.g.
        ``"feat-31-feature"``, not a bare ``"feat-31"`` prefix.

    Returns
    -------
    Path
        The resolved ``README.md`` path.

    Raises
    ------
    FeatNotFoundError
        If ``<base_dir>/<id_>/README.md`` does not exist, if it exists but
        fails to parse (``AssertionError``/``pydantic.ValidationError``),
        or if it parses but its frontmatter ``id`` does not match ``id_``
        (a folder/frontmatter mismatch, surfaced rather than silently
        worked around).
    """
    assert isinstance(base_dir, Path), type(base_dir)
    assert isinstance(id_, str), type(id_)
    assert id_.strip()

    path = base_dir / id_ / README_FILENAME
    if not path.exists():
        raise FeatNotFoundError(
            f"no feature found with id {id_!r}: {path} does not exist. The id must be the exact "
            f"containing folder's name (e.g. 'feat-31-feature'), not a bare prefix like 'feat-31' -- "
            f"use list_feat to discover the exact id first."
        )

    try:
        doc = parse_feat(path.read_text(encoding="utf-8"))
    except (AssertionError, ValidationError) as ex:
        raise FeatNotFoundError(
            f"feature folder {id_!r} exists at {path}, but its content could not be parsed as a valid "
            f"feature document ({type(ex).__name__}: {ex})."
        ) from ex

    if doc.frontmatter.id != id_:
        raise FeatNotFoundError(
            f"feature folder {id_!r} exists at {path}, but its frontmatter id ({doc.frontmatter.id!r}) "
            f"does not match the containing folder's own name ({id_!r}) -- the folder was likely "
            f"renamed or copied without updating its frontmatter."
        )

    result = path
    return result
