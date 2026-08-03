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

"""Shared, private validation helpers for the ``models.adr`` subpackage."""

from __future__ import annotations

import re

#: The schema major version this ``v1`` package implements. Matches this
#: package's folder name (plan §6) and is the value every
#: ``AdrFrontmatter.version`` produced by this package must share the major
#: component with -- a ``v1.AdrFrontmatter`` can never legitimately carry a
#: ``"2.x.x"`` version.
SCHEMA_MAJOR_VERSION = 1

#: The current, default schema version for newly created v1 documents.
#: Bump the minor/patch component here for non-breaking schema evolutions
#: that don't warrant a new ``vN`` package (plan §6); only a breaking change
#: gets a new major version, hence a new sibling package.
CURRENT_SCHEMA_VERSION = f"{SCHEMA_MAJOR_VERSION}.0.0"

_SEMVER_PATTERN = re.compile(r"^(?P<major>\d+)\.\d+\.\d+$")


def blank_to_none(value: str | None) -> str | None:
    """Normalize a blank/whitespace-only string to ``None``.

    Used by optional frontmatter/body fields so that "absent" and
    "whitespace-only" are treated as the same state, consistent with the
    render-time rule that an absent optional section omits its heading.
    """
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def default_if_blank(value: object, default: str) -> object:
    """Normalize a blank/whitespace-only (or ``None``) value to ``default``.

    Used as a ``mode="before"`` validator for mandatory-but-defaulted
    string fields (``AdrFrontmatter.status``) so an explicit but empty YAML
    key -- e.g. MADR's own bare-bones template ships a placeholder
    ``status:`` with nothing after the colon, which a YAML loader parses as
    ``None``, not an absent key -- is treated the same as the key being
    absent entirely, rather than failing type validation before the
    field's own membership check ever runs. Mirrors :func:`blank_to_none`,
    but substitutes a caller-supplied default instead of ``None``, for
    fields that are not ``Optional``.
    """
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return value


def validate_schema_version(value: str) -> str:
    """Validate a schema version string against this package's major version.

    ``value`` must be a ``major.minor.patch`` string whose major component
    equals :data:`SCHEMA_MAJOR_VERSION`. Used by ``AdrFrontmatter.version``
    (plan §3/§6) -- this schema-tracking field is a specmgr-only extension
    to the frontmatter block, not part of the MADR standard, kept alongside
    the MADR-defined keys (``status``, ``date``, ...) purely so it survives
    the parse/render round-trip of the on-disk ``.md`` file.
    """
    match = _SEMVER_PATTERN.match(value)
    if not match:
        raise ValueError(f"version must be 'major.minor.patch', got {value!r}")
    major = int(match.group("major"))
    if major != SCHEMA_MAJOR_VERSION:
        raise ValueError(
            f"version {value!r} has major component {major}, "
            f"but models.adr.v1 only accepts major version {SCHEMA_MAJOR_VERSION}"
        )
    return value
