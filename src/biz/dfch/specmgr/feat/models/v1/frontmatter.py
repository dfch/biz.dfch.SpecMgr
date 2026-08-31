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

"""Feature (FEAT) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.

Mirrors the pattern established by `rsk/models/v1/frontmatter.py::RskFrontmatter`:
a subtype of `MarkdownFrontmatter` that restricts `type` to a fixed
``Literal["feat"]`` and narrows the free-form ``status`` to a closed,
hyphen-free four-value lifecycle set, *and* redeclares the default away from
the base's ``"draft"`` (a `feat` document starts life ``"planning"``, not
``"draft"`` -- ``"draft"`` is not part of `feat`'s own closed set) -- see
`.specmgr/feat/feat-31-feature/README.md` Design Notes ("Frontmatter").

`created`/`updated` are inherited unchanged from `MarkdownFrontmatter` as
plain, unvalidated ``str | None`` -- the base model performs no format
validation on either field for any domain (the specific microsecond
timestamp convention every domain, including `feat`, uses is a
tool-layer/`_write.py` concern, not a model-layer one).
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator

from biz.dfch.specmgr.models.md import MarkdownFrontmatter
from biz.dfch.specmgr.models.md._util import default_if_blank

#: Fixed, closed set of accepted ``status`` values for features -- a
#: deliberately hyphen-free four-value lifecycle (``"progress"``, not
#: ``"in-progress"``), per explicit user direction:
#: ``planning`` (design/requirements still being written), ``progress``
#: (implementation under way), ``review`` (implementation done, pending
#: verification), or ``done`` (shipped).
_ALLOWED_STATUSES = frozenset(
    {
        "planning",
        "progress",
        "review",
        "done",
    }
)

#: Default ``status`` value when the key is absent or blank -- the starting
#: state of a feature's lifecycle. The base `MarkdownFrontmatter`'s own
#: default is ``"draft"``, which is not part of `feat`'s own set.
DEFAULT_FEAT_STATUS = "planning"


class FeatFrontmatter(MarkdownFrontmatter):
    """Feature (FEAT) frontmatter: `MarkdownFrontmatter` narrowed for the ``feat`` document type.

    Parameters
    ----------
    type:
        Fixed discriminator, always ``"feat"``. Narrows the base's mandatory,
        default-less ``str`` field to a ``Literal["feat"] = "feat"``, so a document
        omitting ``type`` entirely still parses as a feature document.
    status:
        One of ``"planning"``, ``"progress"``, ``"review"``, ``"done"``.
        Narrows the base's free-form ``str`` field to this closed four-value
        set; absent/blank defaults to ``"planning"``
        (``_default_blank_status_to_planning`` below, which runs before the
        base's inherited ``_default_blank_status_to_draft``).
    version:
        The ``models.md`` schema major.minor.patch version this document's
        frontmatter was written with. DO NOT CHANGE!

    All other fields (``id``, ``created``, ``updated``, ``version``) are inherited
    unchanged from :class:`MarkdownFrontmatter`.
    """

    type: Literal["feat"] = "feat"  # type: ignore
    status: str = DEFAULT_FEAT_STATUS

    @field_validator("status", mode="before")
    @classmethod
    def _default_blank_status_to_planning(cls, value: object) -> object:
        """Map an absent/blank ``status`` to ``"planning"`` (not the base's ``"draft"``).

        Runs before the base's inherited ``_default_blank_status_to_draft``
        (Pydantic applies child-class ``mode="before"`` validators first), so
        by the time the base's validator sees the value it is already
        ``"planning"`` and passes it through unchanged.
        """
        return default_if_blank(value, DEFAULT_FEAT_STATUS)

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in _ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
        return value
