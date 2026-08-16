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

"""Shared, private constants for the ``uc.models.v2`` subpackage."""

from __future__ import annotations

#: The generated-schema layout version for ``docs/uc_schema.json``. Matches
#: this package's own folder name (``uc/models/v2``) -- bump only when a
#: breaking change to the *generated schema's* structure warrants a new
#: ``vN`` sibling package, not on every minor field addition. Consumed by
#: ``commands.schema.generate_uc_schema()`` as the emitted JSON's
#: ``"$comment"`` value, so a caller that cached an earlier fetch can detect
#: the schema changed shape without diffing the whole document. Deliberately
#: a bare token (``"v2"``, no ``"uc "`` prefix) -- the doc type is already
#: unambiguous from context (file name / resource URI).
SCHEMA_COMMENT_VERSION = "v2"
