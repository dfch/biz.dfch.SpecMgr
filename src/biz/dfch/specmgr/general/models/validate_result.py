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

"""The generic ``validate`` tool's non-raising, structured result shape (feat-81-83-validation Phase 2, REQ-004).

No precedent exists elsewhere in this codebase for a non-raising structured
result -- every other validating tool (``create_<d>``, the generic
``update``/``set_status``/``set_classification``) raises on failure. This
module is greenfield, backing only ``general.tools.validate``.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["ValidateResult", "ValidationErrorEntry"]


class ValidationErrorEntry(BaseModel):
    """One error entry in a :class:`ValidateResult`'s ``errors`` list.

    Deliberately holds only ``message`` -- no ``field`` key. Pydantic-sourced
    validation errors do carry structured ``loc`` data internally (via
    ``.errors()``), but ``AssertionError``/YAML-sourced errors carry none;
    rather than populate a ``field`` key for some errors and leave it
    ``None``/absent for others depending on which validation layer raised,
    ``message`` alone is used for every error, keeping the shape predictable
    regardless of source (see
    ``.specmgr/feat/feat-81-83-validation/README.md`` Design Notes).

    Parameters
    ----------
    message:
        The full, already-enriched exception message (domain/tool/channel
        context plus feat-27-validation's field-path/line/cause-hint
        enrichment), reused verbatim from the caught exception's ``str()``.
    """

    message: str


class ValidateResult(BaseModel):
    """The generic ``validate`` tool's return shape: never raises for a content-validation failure.

    In practice ``errors`` currently holds zero or one entries: each
    domain's validation logic performs exactly one guarded parse call, so at
    most one exception can ever be caught per invocation today -- the list
    shape is deliberate forward-compatibility (matching pydantic's own
    per-error ``.errors()`` structure, which is not yet exposed to callers),
    not an indication multiple concurrent errors are common.

    Parameters
    ----------
    valid:
        ``True`` if ``content`` validated successfully, ``False`` otherwise.
    errors:
        The validation failures caught, if any. Empty when ``valid`` is
        ``True``.
    """

    valid: bool
    errors: list[ValidationErrorEntry]
