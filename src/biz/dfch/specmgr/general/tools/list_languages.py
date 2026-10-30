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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: list_languages (feat-197-i18n Phase 140, Task 140.120, REQ-012, ACC-008).

The generic, read-only language-listing tool for one artifact: given a ``type`` (one of the eleven i18n-eligible
domains ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``vcr``/``sysrs``) and an ``id``, it
reports the language codes the artifact currently exists in -- the dedicated tool ADR 38efdb66 item 7 names in place of
an "all languages" mode of ``list_<d>``. The result is a
:class:`~biz.dfch.specmgr.general.models.language_list_result.LanguageListResult`: ``languages`` (``"en"`` first when
the EN source exists -- ACC-008 -- then every other language that holds a variant, sorted by code) plus one entry per
language with its resolved path and a ``parseable`` flag (a variant that exists but fails to parse is listed, flagged,
with the parse error -- never dropped, never raised).

**Layout probing, not scanning.** The tool never uses or alters the EN-only scans of the other tools (REQ-013): it
probes the flat ``docs/{type}/`` directory and each shape-valid ``docs/{type}/{language}/`` subdirectory through the
domain's own language-aware readers (:mod:`._language_variants`). Only ``*.md`` documents participate: a non-``.md``
sibling (the ``.pdf`` next to a ``sysrs`` document) and a shape-invalid directory name (``Notes``, ``de-DE``) are
ignored. An id with variants but no EN source is reported as such (no ``"en"``); an id that exists in no language at
all raises the domain's own not-found error. Strictly read-only: it writes, creates, and invalidates nothing.

**Error semantics.** ``feat`` and ``adr`` are permanently English (REQ-002/REQ-009): they are rejected with the
permanent "always English" ``ValueError``, before the id is looked at; an unknown ``type``, a path-injection attempt, or
a wrong-format ``id`` is a ``ValueError`` before any filesystem access (``_path_safety.validate_id``).
"""

from __future__ import annotations

from ...server import mcp
from ..models.language_list_result import LanguageListResult
from ._domains import WholeBodyOrAdrType
from ._language_guard import LANGUAGE_AWARE_DOMAINS, assert_language_aware_type
from ._language_variants import list_language_variants
from ._path_safety import validate_id

__all__ = ["list_languages"]


@mcp.tool(
    name="list_languages",
    title="List the languages an artifact exists in",
    description=(
        "Read-only. Report the language codes one artifact currently exists in. `type` is one of "
        f"{', '.join(LANGUAGE_AWARE_DOMAINS)} (feat and adr documents are always English and are rejected "
        "with a ValueError) and `id` the artifact's id, shared by every language variant. Returns a "
        "`LanguageListResult`: `languages` -- 'en' first when the EN source exists (it is never invented: an id "
        "with variants but no EN source lists no 'en'), then every other language holding a variant, sorted by "
        "code -- and one `entries` row per language with `language`, `path` (the resolved absolute file path), "
        "`parseable`, and `error`; a variant that exists but fails to parse is listed with `parseable=false` and "
        "the parse error (byte-identical to the domain's list_<d>/get_<d> failure text for that file), never "
        "dropped and never raised. Only .md documents under docs/{type}/ (EN) and docs/{type}/{language}/ "
        "participate; non-.md siblings and directory names that are not a two-letter lowercase language code are "
        "ignored. An id that exists in no language raises the domain's own not-found error; an unknown type or a "
        "path-injection/wrong-format id is a ValueError raised before any file access. It writes, creates and "
        "invalidates nothing. To translate use the translate_artifact prompt; to compare a variant with its "
        "source use check_translation_drift."
    ),
)
def list_languages(type: WholeBodyOrAdrType, id: str) -> LanguageListResult:
    """List the languages the artifact ``id`` of ``type`` currently exists in.

    Parameters
    ----------
    type:
        The document type: one of the eleven i18n-eligible domains ``req``, ``uc``, ``tsk``, ``qa``, ``prb``,
        ``gol``, ``rsk``, ``dec``, ``sop``, ``vcr``, ``sysrs``. ``feat`` and ``adr`` are accepted by the schema
        only so that they get an explanation: they are permanently English and are rejected.
    id:
        The artifact's specmgr-assigned id (shared by every language variant).

    Returns
    -------
    LanguageListResult
        ``languages`` (``"en"`` first when the EN source exists, then the other languages sorted by code) and one
        entry per language: ``language``, resolved ``path``, ``parseable``, and the parse ``error`` of an
        unparseable variant.

    Raises
    ------
    ValueError
        ``type`` is ``feat``/``adr`` (always English) or unknown, or ``id`` is a path-injection attempt or not in
        the domain's own format (raised before any filesystem access).
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError / PrbNotFoundError /
    GolNotFoundError / RskNotFoundError / DecNotFoundError / SopNotFoundError / VcrNotFoundError /
    SysrsNotFoundError
        The artifact exists in no language at all (neither the EN source nor any variant) -- the domain's own
        not-found error, as ``get_<d>`` raises it.
    """
    assert_language_aware_type(type)
    validate_id(type, id)

    result = list_language_variants(type, id)
    return result
