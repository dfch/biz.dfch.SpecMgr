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

"""The write-side ``language`` guard shared by the generic, type-dispatched tools (feat-197-i18n Phases 120/125).

The generic ``update``/``edit``/``set_status``/``set_classification``/
``delete`` tools dispatch on ``type`` across every whole-body domain (and,
for ``set_status``, ``adr``), and the ``language`` parameter they all gained
in Phase 120 is honored by every i18n-eligible domain (:data:`LANGUAGE_AWARE_DOMAINS`:
Phase 120 enabled the pilot domain ``dec``, Phase 125 the remaining ten --
every whole-body domain except ``feat``). :func:`guard_language` is the one up-front check every one of those tools
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
   English). Since Phase 125 enabled every other whole-body domain, the
   remaining rejection ("not yet supported") is a defensive fallback only:
   it is reachable solely for a type that is neither language-aware nor
   ``feat``/``adr`` (e.g. a future domain registered in the domain list
   before its adapters exist -- the import-time ``_LANGUAGE_ADAPTERS`` /
   :data:`LANGUAGE_AWARE_DOMAINS` asserts in every generic tool make that
   state fail loudly at import, so the fallback never fires through the
   server).

The read-only translation tools (``list_languages``/``check_translation_drift``, feat-197-i18n Phase 140) take a
``type`` that is itself the subject of the question rather than a ``language`` of a dispatched write, so they use
:func:`assert_language_aware_type` -- the same permanent "always English" wording for ``feat``/``adr`` -- before any
id validation, and :func:`guard_language` for their language arguments.
"""

from __future__ import annotations

from ..models.heading_table import resolve_heading_table
from ._domains import ADR, FEAT, WHOLE_BODY_NO_FEAT_DOMAINS
from ._path_safety import DEFAULT_LANGUAGE, assert_language

__all__ = ["LANGUAGE_AWARE_DOMAINS", "assert_language_aware_type", "guard_language"]

#: The domains whose generic-tool adapters honor a non-default ``language``
#: (feat-197-i18n Phases 120/125: the twelve i18n-eligible domains req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr,
#: sysrs, txt -- derived from the shared domain registry, i.e. every whole-body domain except ``feat``, so the name set
#: is never hand-listed a second time; ``feat`` and ``adr`` are permanently English).
LANGUAGE_AWARE_DOMAINS: tuple[str, ...] = WHOLE_BODY_NO_FEAT_DOMAINS


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
        English -- permanent) or for a type that supports no language
        variants (the defensive fallback, see the module docstring); or a non-default
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
        f"language {language!r} is not supported for type {type_!r}; only {', '.join(LANGUAGE_AWARE_DOMAINS)} "
        f"documents support language variants -- omit `language` or pass 'en'"
    )


def assert_language_aware_type(type_: str) -> None:
    """Reject a ``type`` whose documents have no language variants, before any filesystem access.

    The type-level counterpart of :func:`guard_language` for the read-only translation tools
    (``list_languages``/``check_translation_drift``, feat-197-i18n Phase 140), which are *about* language variants
    and therefore cannot meaningfully accept ``feat`` or ``adr``: a language-aware domain
    (:data:`LANGUAGE_AWARE_DOMAINS`) passes; ``feat``/``adr`` are rejected with the same permanent wording as
    :func:`guard_language` ("`feat` documents are always English", REQ-002/REQ-009); any other value is an unknown
    type. Run it *before* ``validate_id`` so a ``feat`` request with a ``feat-NNN-slug`` id still gets the
    permanent explanation rather than an id-shape error.

    Parameters
    ----------
    type_:
        The caller-supplied document type.

    Raises
    ------
    ValueError
        ``type_`` is ``feat``/``adr`` (always English, permanent) or not a known document type.
    """
    assert isinstance(type_, str), type(type_)

    if type_ in LANGUAGE_AWARE_DOMAINS:
        return
    if type_ in (FEAT, ADR):
        raise ValueError(
            f"type {type_!r} does not support language variants: {type_} documents are always English "
            f"(they have no language variants); only {', '.join(LANGUAGE_AWARE_DOMAINS)} documents do"
        )
    raise ValueError(f"unknown document type {type_!r}; expected one of {', '.join(LANGUAGE_AWARE_DOMAINS)}")
