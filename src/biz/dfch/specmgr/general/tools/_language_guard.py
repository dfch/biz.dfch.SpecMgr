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

"""The write-side ``language`` guard shared by the generic, type-dispatched tools (feat-197-i18n Phase 120).

The generic ``update``/``edit``/``set_status``/``set_classification``/
``delete`` tools dispatch on ``type`` across every whole-body domain (and,
for ``set_status``, ``adr``), but the ``language`` parameter they all gained
in Phase 120 is honored by only a growing subset of those domains: in
Phase 120 just the pilot domain ``dec`` (:data:`LANGUAGE_AWARE_DOMAINS`;
Phase 125 extends the set to the remaining ten i18n-eligible domains).
:func:`guard_language` is the one up-front check every one of those tools
runs, before any filesystem access and before dispatch:

1. :func:`~biz.dfch.specmgr.general.tools._path_safety.assert_language` --
   the shape guard (REQ-008/ACC-013), run for *every* ``type`` and every
   value, including the paths that end up rejecting the value anyway.
2. The default language (``"en"``) always passes: it is the byte-identical,
   flat, pre-i18n path for every domain.
3. A non-default language for a language-aware domain resolves its
   heading-mapping table (so a shape-valid code without a packaged table is
   an actionable ``ValueError`` before any filesystem access).
4. A non-default language for ``feat`` or ``adr`` is rejected with
   permanently-worded text (REQ-002/REQ-009: these two domains are always
   English); for every other, not-yet-enabled domain the rejection says
   the language is not yet supported (Phase 125 enables them).
"""

from __future__ import annotations

from ..models.heading_table import resolve_heading_table
from ._domains import ADR, FEAT
from ._path_safety import DEFAULT_LANGUAGE, assert_language

__all__ = ["LANGUAGE_AWARE_DOMAINS", "guard_language"]

#: The domains whose generic-tool adapters honor a non-default ``language`` today
#: (feat-197-i18n Phase 120: the pilot domain only; Phase 125 adds the remaining ten).
LANGUAGE_AWARE_DOMAINS: tuple[str, ...] = ("dec",)


def guard_language(type_: str, language: str) -> None:
    """Validate ``language`` for the dispatched ``type_``, before any filesystem access.

    Parameters
    ----------
    type_:
        The dispatched document type (a whole-body domain, or ``adr`` for
        ``set_status``).
    language:
        The caller-supplied ``language`` parameter.

    Raises
    ------
    ValueError
        ``language`` is not an ISO 639-1-shaped lowercase two-letter code
        (:func:`~biz.dfch.specmgr.general.tools._path_safety.assert_language`);
        a non-default ``language`` was given for ``feat``/``adr`` (always
        English -- permanent) or for a domain that does not yet support
        language variants (temporary, Phase 125); or a non-default
        ``language`` of a language-aware domain has no packaged
        heading-mapping table (the table loader's actionable error).
    """
    assert isinstance(type_, str), type(type_)
    assert isinstance(language, str), type(language)

    assert_language(language)
    if language == DEFAULT_LANGUAGE:
        return
    if type_ in LANGUAGE_AWARE_DOMAINS:
        resolve_heading_table(language)
        return
    if type_ in (FEAT, ADR):
        raise ValueError(
            f"language {language!r} is not supported for type {type_!r}: {type_} documents are always English "
            f"(they have no language variants); omit `language` or pass 'en'"
        )
    raise ValueError(
        f"language {language!r} is not yet supported for type {type_!r}; only {', '.join(LANGUAGE_AWARE_DOMAINS)} "
        f"documents support language variants so far -- omit `language` or pass 'en'"
    )
