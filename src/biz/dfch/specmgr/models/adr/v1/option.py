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

"""Pydantic model for one ``### Option N: {title}`` sub-section (plan §5)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AdrOption(BaseModel):
    """One entry of the dynamic ``## Pros and Cons of the Options`` collection.

    Rendered as ``### Option {number}: {partial_title}``. Options are never
    individually mandatory -- zero options is a valid ADR state -- and the
    whole-section deletion sentinel from plan §4 does not apply to them;
    removal only ever happens through the dedicated ``option_delete`` tool
    (plan §5, §8), not by submitting a blank/``"REMOVE"`` value here.

    Parameters
    ----------
    number:
        Monotonically increasing, unpadded, never-reused counter assigned at
        creation time. Deleting an option leaves a gap; remaining options are
        neither renumbered nor reordered.
    partial_title:
        The ``{title}`` portion after ``"Option {number}: "``. Must be
        non-blank and single-line (no embedded line breaks).
    content:
        Opaque markdown blob for the option's body (no enforced
        Good/Bad/Neutral structure). May be empty -- unlike the mandatory
        whole-section body fields, an option's content is never required to
        be non-blank.
    """

    number: int = Field(gt=0)
    partial_title: str
    content: str = ""

    @field_validator("partial_title")
    @classmethod
    def _validate_partial_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("partial_title must not be blank")
        if "\n" in value or "\r" in value:
            raise ValueError("partial_title must not contain line breaks")
        return value

    @property
    def full_title(self) -> str:
        """The rendered heading text, e.g. ``"Option 1: Use Postgres"``."""
        return f"Option {self.number}: {self.partial_title}"
