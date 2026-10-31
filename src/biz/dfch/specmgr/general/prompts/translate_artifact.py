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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public prompt API, issue #41

"""``@mcp.prompt()``: translate_artifact (feat-197-i18n, Phase 130, REQ-011).

Returns instructional text -- not itself a tool call -- that guides an LLM
through producing (or updating) a target-language variant of a specmgr
document from its source-language content. Translation is LLM judgment
work wrapped around deterministic tools that already exist, so this prompt
(plus the ``translate-artifact`` skill and the ``/translate`` command) is
the whole translation surface: there is no MCP tool that translates and
no dedicated subagent (the ``generate_uc_sequence_diagram`` /
``uc-diagram`` precedent, not the ``repair`` / ``doc-repairer`` one).

The narrated flow: read the ``specmgr://i18n`` resource first; check the
language pair; read the source via ``get_<d>(id, raw=True, language=...)``
(a ``ParseFailureResult`` stops the flow -- an English source is pointed to
``repair``); probe the target variant to decide **create**
(``create_<d>(content, language, id)``) versus **update** (the generic
``update``/``edit`` with ``language``); read the target language's heading
table and translate only free-form prose plus the fixed-text heading text
through that table, never the closed-vocabulary / schema-constant tokens
(REQ-010) nor -- per ADR 38efdb66 item 11 -- ``prb``'s ``problem_statement``
lead paragraph; write with bounded retries on the non-raising
``ValidateResult`` (a translated body cannot be dry-run: the generic
``validate`` tool is canonical-only and has no ``language`` parameter, so
the write tools' own validation is the feedback channel); verify with
``get_<d>(id, language=...)`` against the file on disk; and report. It
never commits, never writes English, and never changes a document's
frontmatter ``id``/``status``. A language without a heading table stops
the flow (the table file ``general/data/headings/<language>.json`` must be
added first -- never invented here).

``type`` is one of the twelve i18n-eligible domains (imported from
``general.tools._language_guard.LANGUAGE_AWARE_DOMAINS``, the single
source of truth); ``feat`` and ``adr`` are permanently English and
explicitly rejected. Like ``repair``, the prompt validates its arguments
up front and raises ``ValueError`` -- before any text is rendered.

This prompt is cross-cutting (it takes ``type`` + ``id`` + languages), so
-- like ``repair`` and ``compact_history`` -- it lives under
``general.prompts``. ``translate_artifact`` is a deliberate exception to
the ``<verb>_<domain>`` prompt-naming convention, following the bare-word
cross-cutting precedent of ``repair``.

The instructional text lives in its own packaged data file,
``general/data/general_translate_artifact_instructions.md``, read fresh on
every call via ``general.tools._packaged_data.read_packaged_text``.
Placeholders use ``string.Template`` (``$type``/``$id``/``$language``/
``$source_language``), not ``str.format``, so the packaged file is free to
use plain, unescaped ``{...}`` braces of its own.
"""

from __future__ import annotations

from string import Template

from ...general.models.heading_table import resolve_heading_table
from ...general.tools._domains import ADR, FEAT
from ...general.tools._language_guard import LANGUAGE_AWARE_DOMAINS
from ...general.tools._packaged_data import read_packaged_text
from ...general.tools._path_safety import DEFAULT_LANGUAGE, assert_language
from ...server import mcp


@mcp.prompt(
    name="translate_artifact",
    title="Translate a specmgr document into another language",
    description=(
        "Guides the LLM through producing (or updating) a target-language variant of a whole-body "
        "specmgr document (req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/txt; feat and adr are always "
        "English and out of scope): read the specmgr://i18n resource first, read the source via "
        "get_<d>(id, raw=True, language=...) (a ParseFailureResult stops the flow), decide create "
        "(create_<d>(content, language, id)) versus update (the generic update/edit with language), "
        "translate only free-form prose and fixed-text heading text via the language's heading table "
        "-- never the closed-vocabulary/schema-constant tokens (RSK Strategy/Probability/Impact, VCR "
        "Coverage/AC method words, REQ Level/Priority, Option/Step/Extension tokens, cross-reference "
        "tags, timestamps, ...) nor PRB's problem_statement -- retry the write a bounded number of "
        "times on a non-raising ValidateResult (the validate tool cannot dry-run a translation), "
        "verify with get_<d>(id, language=...), and report. A language without a heading table stops "
        "the flow. Never commits, never writes English, never changes the frontmatter id/status."
    ),
)
def translate_artifact(type: str, id: str, language: str, source_language: str = DEFAULT_LANGUAGE) -> str:
    """Return instructional text for translating the document ``id`` into ``language``.

    Parameters
    ----------
    type:
        The document domain to translate: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``vcr``,
        ``sysrs``, ``txt`` (matched case-insensitively). ``feat`` and ``adr``
        are permanently English and rejected with an actionable error; so is
        any other unknown value.
    id:
        The shared id of the artifact (the EN source's id, which every
        language variant reuses).
    language:
        The target language: an ISO 639-1-shaped lowercase two-letter code
        (``"de"``; matched case-insensitively) with a packaged heading
        table. ``"en"`` is rejected (English is the canonical source
        language and is never written by this flow), as is a code equal to
        ``source_language``.
    source_language:
        The language to translate from; defaults to ``"en"``. A non-EN
        source needs a heading table too, and the EN document with the
        same id must still exist.

    Returns
    -------
    str
        Instructional text (auto-wrapped as a single ``UserMessage`` by
        the MCP SDK), not itself a tool call.

    Raises
    ------
    ValueError
        ``type`` is ``feat``/``adr`` (always English) or unknown; ``id`` is
        blank/whitespace-only; ``language`` or ``source_language`` is not an
        ISO 639-1-shaped lowercase two-letter code or has no heading-mapping
        table; ``language`` is ``"en"``; or ``language`` equals
        ``source_language``.
    """
    assert isinstance(type, str), f"translate_artifact() expects type as a str, got {type!r}"
    assert isinstance(id, str), f"translate_artifact() expects id as a str, got {id!r}"
    assert isinstance(language, str), f"translate_artifact() expects language as a str, got {language!r}"
    assert isinstance(source_language, str), (
        f"translate_artifact() expects source_language as a str, got {source_language!r}"
    )
    if not id.strip():
        raise ValueError(
            f"translate_artifact() received a blank id for type {type!r}; pass the artifact's shared id "
            "(the EN source's id)."
        )
    normalized_type = type.strip().lower()
    if normalized_type in (FEAT, ADR):
        raise ValueError(
            f"translate_artifact() does not support type {normalized_type!r}: {normalized_type} documents are "
            "always English (they have no language variants); expected one of "
            f"{'/'.join(LANGUAGE_AWARE_DOMAINS)}."
        )
    if normalized_type not in LANGUAGE_AWARE_DOMAINS:
        raise ValueError(
            f"translate_artifact() does not support type {normalized_type!r}; expected one of "
            f"{'/'.join(LANGUAGE_AWARE_DOMAINS)} ('feat' and 'adr' are always English and out of scope)."
        )
    normalized_language = language.strip().lower()
    normalized_source = source_language.strip().lower()
    assert_language(normalized_language)
    assert_language(normalized_source)
    if normalized_language == DEFAULT_LANGUAGE:
        raise ValueError(
            "translate_artifact() cannot target 'en': English is the canonical source language and is never "
            "written by the translation flow; pass the language to translate into (for example 'de')."
        )
    if normalized_language == normalized_source:
        raise ValueError(
            f"translate_artifact() received the same source and target language {normalized_language!r}; "
            "there is nothing to translate."
        )
    # Fail fast (before any text is rendered) when either language has no heading table.
    resolve_heading_table(normalized_language)
    resolve_heading_table(normalized_source)
    template = Template(read_packaged_text("general", "translate_artifact_instructions", "md"))
    result = template.substitute(
        type=normalized_type,
        id=id.strip(),
        language=normalized_language,
        source_language=normalized_source,
    )
    return result
