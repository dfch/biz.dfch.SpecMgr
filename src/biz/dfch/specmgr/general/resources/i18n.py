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

"""Resource: specmgr://i18n (feat-197-i18n, Phase 130, REQ-010/REQ-011).

Static, cross-cutting domain-knowledge resource documenting how specmgr
stores and translates language variants of the same artifact: the
directory layout and the EN-slug basename rule (ADR 38efdb66), the
language vocabulary and the per-language heading-mapping tables, the
tool surface that honors ``language``, the exact never-translate list per
domain (REQ-010: the closed-vocabulary and schema-constant tokens plus the
``prb`` ``problem_statement`` exemption), how to translate headings via
the table, the create-versus-update decision, and the guard/error
semantics. It is the read-first document of the ``translate_artifact``
prompt.

Served as raw packaged markdown (``text/markdown``, mirroring
``specmgr://dtais``/``specmgr://rasci``/``specmgr://reference-graph``'s
raw-passthrough style: the audience is an LLM agent that needs to read
guidance, not code that needs data). There is no dedicated parse model, so
there is no per-call drift-guard parse -- the pins in
``tests/general/resources/test_i18n.py`` play that role: they check the
resource's load-bearing statements against the implemented behavior (the
heading tables, the language guard, and the schemas' own enforcement of the
tokens the never-translate list calls schema-enforced).

Registered as a flat, top-level ``specmgr://i18n`` URI (like
``specmgr://dtais``/``specmgr://rasci``), since the language-variant
convention spans eleven document domains -- it is not owned by any single
domain's schema.

The sibling resource **template** ``specmgr://i18n/headings/{language}``
(``i18n_headings``, registered the way ``specmgr://adr/{id}`` is) serves a
language's heading-mapping table as JSON text (``application/json``), so the
``translate_artifact`` flow can obtain the table without any host file tool.
It is a thin, read-only view over
:func:`~biz.dfch.specmgr.general.models.heading_table.load_heading_table`
(the same validation as every parse): the ``language`` is shape-guarded by
:func:`~biz.dfch.specmgr.general.tools._path_safety.assert_language` first,
``en`` (canonical, no table) and a shape-valid language without a table file
are actionable ``ValueError``s, and nothing touches the filesystem with an
unvalidated value. It does not translate anything.
"""

from __future__ import annotations

import json

from ...server import mcp
from ..models.heading_table import load_heading_table
from ..tools._packaged_data import read_packaged_text
from ..tools._path_safety import DEFAULT_LANGUAGE, assert_language


@mcp.resource(
    "specmgr://i18n",
    name="i18n",
    title="Multi-Language Artifact Variants (i18n) Guidance",
    description=(
        "How language variants of the same artifact are stored and translated: the "
        "docs/{type}/{language}/ layout and the EN-slug basename rule, the language vocabulary and "
        "per-language heading tables, the tool surface honoring `language`, the exact "
        "never-translate list per domain (closed-vocabulary/schema-constant tokens, the prb "
        "problem_statement exemption), how to translate headings, the create-versus-update "
        "decision, and the guard/error semantics (feat and adr are always English) -- raw "
        "markdown domain-knowledge guidance."
    ),
    mime_type="text/markdown",
)
def i18n() -> str:
    """Return the packaged i18n guidance's full markdown text, verbatim.

    Same packaged-data source and no-cache, hard-failure-on-missing-file
    design as every other cross-cutting ``general`` resource -- reads the
    file fresh on every call.

    Returns
    -------
    str
        The i18n guidance document's raw markdown source.

    Raises
    ------
    FileNotFoundError
        If the packaged ``general_i18n.md`` is missing.
    """
    result: str = read_packaged_text("general", "i18n")
    return result


@mcp.resource(
    "specmgr://i18n/headings/{language}",
    name="i18n_headings",
    title="Heading-Mapping Table of a Language",
    description=(
        "The heading-mapping table of one language as JSON: a flat object mapping each translated "
        "heading text to its canonical English heading text (the table the parsers apply to a "
        "language variant and the translate_artifact flow translates headings with). Read-only; "
        "`en` is canonical and has no table, and a language without a packaged table is an error."
    ),
    mime_type="application/json",
)
def i18n_headings(language: str) -> str:
    """Return the heading-mapping table of ``language`` as JSON text.

    A read-only view over
    :func:`~biz.dfch.specmgr.general.models.heading_table.load_heading_table`
    (lazy once-per-process load, so the loader's own validation -- valid
    JSON, a flat ``str -> str`` object, pairwise-distinct values -- applies
    unchanged). The table maps ``<translated heading text>`` to
    ``<canonical English heading text>``.

    Parameters
    ----------
    language:
        The language code: an ISO 639-1-shaped lowercase two-letter code
        (``"de"``) with a packaged heading table.

    Returns
    -------
    str
        The table as a JSON object (UTF-8 characters unescaped).

    Raises
    ------
    ValueError
        ``language`` is not of the ISO 639-1 lowercase two-letter shape
        (checked first, before any filesystem access); ``language`` is
        ``"en"`` (English is the canonical form and has no table); or the
        language has no packaged table (the loader's actionable error).
    """
    assert isinstance(language, str), type(language)

    assert_language(language)
    if language == DEFAULT_LANGUAGE:
        raise ValueError(
            f"language {language!r} has no heading-mapping table: English is the canonical form of every "
            "heading, so there is nothing to map; ask for the table of a translation language (for example 'de')"
        )
    table = load_heading_table(language)
    result = json.dumps(table, ensure_ascii=False, indent=2)
    return result
