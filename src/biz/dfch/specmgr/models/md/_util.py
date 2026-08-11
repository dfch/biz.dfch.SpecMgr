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

"""Shared, private validation helpers for the ``models.md`` subpackage.

Deliberately independent of ``models.adr.v1._util`` -- per ADR
bc5e18ad-6bbf-4265-bae4-3e34984a2d29, ``models.md`` owns its own small
validator helpers rather than depending on the ADR-specific package, even
though the two modules currently look near-identical. A future decision may
converge them; that is not decided here.
"""

from __future__ import annotations

import re

#: The schema major version this ``models.md`` package implements. Only a
#: breaking change to :class:`MarkdownFrontmatter`'s shape would warrant
#: bumping this (and, unlike ``models.adr.v1``, there is currently no
#: sibling ``v2`` package convention for ``models.md`` -- see ADR
#: 832cd6c1-ef8a-4bfc-990e-a610823f61ae).
SCHEMA_MAJOR_VERSION = 1

#: The current, default schema version for newly created frontmatter blocks.
#: Bump the minor/patch component here for non-breaking schema evolutions.
CURRENT_SCHEMA_VERSION = f"{SCHEMA_MAJOR_VERSION}.0.0"

_SEMVER_PATTERN = re.compile(r"^(?P<major>\d+)\.\d+\.\d+$")


def blank_to_none(value: str | None) -> str | None:
    """Normalize a blank/whitespace-only string to ``None``.

    Used by optional frontmatter fields (``created``, ``updated``) so that
    "absent" and "whitespace-only" are treated as the same state.
    """
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return value


def default_if_blank(value: object, default: str) -> object:
    """Normalize a blank/whitespace-only (or ``None``) value to ``default``.

    Used as a ``mode="before"`` validator for mandatory-but-defaulted string
    fields (``MarkdownFrontmatter.status``) so an explicit but empty YAML key
    is treated the same as the key being absent entirely, rather than
    reaching the field's own validation with a blank value.
    """
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return value


def validate_schema_version(value: str) -> str:
    """Validate a schema version string against this package's major version.

    ``value`` must be a ``major.minor.patch`` string whose major component
    equals :data:`SCHEMA_MAJOR_VERSION`. Used by
    ``MarkdownFrontmatter.version``.
    """
    match = _SEMVER_PATTERN.match(value)
    if not match:
        raise ValueError(f"version must be 'major.minor.patch', got {value!r}")
    major = int(match.group("major"))
    if major != SCHEMA_MAJOR_VERSION:
        raise ValueError(
            f"version {value!r} has major component {major}, "
            f"but models.md only accepts major version {SCHEMA_MAJOR_VERSION}"
        )
    return value
