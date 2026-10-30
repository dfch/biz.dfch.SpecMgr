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

"""The ``list_languages`` tool's result model (feat-197-i18n Phase 140, REQ-012, ACC-008).

:class:`LanguageListResult` is the small, bounded answer to "which languages does this artifact exist in?":
the ordered language codes (``"en"`` first when the EN source exists, then every other language that holds a
variant, sorted by code) plus one :class:`LanguageEntry` per language carrying the resolved path and whether the
on-disk document parses -- a variant that fails to parse still counts as present (it exists), flagged
``parseable=False`` with the parse error, never silently dropped and never raised. The listing is one result per
artifact, never paged: the set of languages is bounded by the number of packaged heading-mapping tables.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["LanguageEntry", "LanguageListResult"]


class LanguageEntry(BaseModel):
    """One language variant of an artifact, as found on disk.

    Parameters
    ----------
    language:
        The language code (``"en"`` for the flat default-language document, otherwise the ISO 639-1-shaped
        ``{language}`` subdirectory name).
    path:
        The absolute, resolved on-disk path of this language's document.
    parseable:
        ``True`` if the document parses as its domain's schema in its language; ``False`` if it exists but fails to
        parse (or its language has no packaged heading-mapping table).
    error:
        ``None`` when ``parseable``; otherwise the parse-failure message -- the string form of the domain's own
        parse exception, byte-identical to the domain's ``list_<d>`` failed-row ``error`` (and ``get_<d>``'s
        ``ParseFailureResult.error``) for the same file in the same language.
    """

    language: str
    path: str
    parseable: bool
    error: str | None = None


class LanguageListResult(BaseModel):
    """The languages one artifact (``type``/``id``) currently exists in.

    Parameters
    ----------
    type:
        The artifact's document type (one of the eleven i18n-eligible domains), echoed back.
    id:
        The artifact's id (shared by every language variant), echoed back.
    languages:
        The language codes found, ``"en"`` first when the EN source exists (ACC-008), then the other languages
        sorted by code. ``"en"`` is never invented: an artifact with variants but no EN source lists no ``"en"``.
    entries:
        One :class:`LanguageEntry` per entry of ``languages``, in the same order.
    """

    type: str
    id: str
    languages: list[str]
    entries: list[LanguageEntry]
