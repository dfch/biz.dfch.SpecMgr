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

"""Translation drift detection: the pure heading-skeleton comparison, the staleness comparison, and the
``check_translation_drift`` tool's result models (feat-197-i18n Phase 140, REQ-014, ACC-009).

Drift between a translated language variant and its source document comes in two kinds (REQ-014), and this module
holds the deterministic, I/O-free core of both:

**(a) Structural drift** -- a section of the variant that is *missing*, *extra*, or *reordered* relative to the
source's canonical schema. :func:`heading_skeleton` reduces a document's body text to its ordered list of
:class:`SkeletonEntry` (one per heading, ``h2`` and deeper), and :func:`compare_skeletons` diffs two skeletons into
:class:`DriftFinding` rows. The skeleton is computed on the document's *raw* body text with the very same
heading/fence recognizer the parse boundary uses (:func:`~biz.dfch.specmgr.general.models.heading_table.
iter_heading_lines`, which :func:`~biz.dfch.specmgr.general.models.heading_table.normalize_heading_lines` is also
built on), so the drift check and the parser can never disagree on what a heading is. Each heading is reduced to a
language-invariant **structural key**:

1. its text is mapped back to canonical English through the language's heading table (``table.get(text, text)``,
   ADR 38efdb66 item 5 -- a heading without an entry is already canonical or genuinely unknown);
2. a **data-carrying heading** -- one whose schema alias carries a free-text group, ADR 38efdb66 item 3 -- is reduced
   to its schema-constant token part, dropping the free text the translator legitimately changes
   (:data:`_TOKEN_PATTERNS`): ``Option N: <title>`` -> ``Option N:`` (dec), ``Step N: <title>`` -> ``Step N:``
   (sop, uc), ``Extension N<l>. <title>`` -> ``Extension N<l>.`` (uc), ``AC-NNN (Method): <text>`` ->
   ``AC-NNN (Method):`` (vcr). A heading whose *whole* text is the schema-constant token (rsk's
   ``Probability {1..5}``/``Impact {1..5}``) needs no reduction -- it already compares as a whole, so a changed
   closed-vocabulary value shows up as a ``missing`` + ``extra`` pair (REQ-010: those tokens stay canonical and
   identical in every language);
3. a **timestamp-led update entry** (``### <timestamp> - <title>`` under ``## Updates``/``## Recent Updates``,
   :data:`_UPDATE_ENTRY_PATTERN`) is a change-log row, not a schema section: a translation keeps its own history, so
   the entry (and anything nested inside it) is *not compared*; the enclosing ``## Updates`` section still is;
4. the **key** of a heading is its canonical ancestor chain plus itself (``Initial Assessment > Probability 3``), so
   a heading that legitimately recurs under different parents (rsk's two ``Probability``/``Impact`` pairs) never
   collides; a repeat under the same parent is disambiguated by an occurrence suffix. A renamed, missing, or extra
   section therefore carries its whole subtree: every sub-section of it is reported as well (the first finding of
   each subtree is its root).

The ``h1`` title is free prose (every domain's own H1 alias is ``.+``, or a fixed prefix plus free text) and is not
part of the skeleton, and prose that is not a heading at all -- paragraphs, list items, fenced code, ``prb``'s
regex-locked ``problem_statement`` lead paragraph (ADR item 11, exempt in every language) -- is invisible to it by
construction: drift detection is about structure and staleness, never about wording or translation quality.

**(b) Staleness** -- the source's frontmatter ``updated`` timestamp is newer than the variant's
(:func:`check_staleness`). Both are compared as *parsed, offset-aware datetimes* (never as strings), so the ``T`` and
space separators and any UTC offset (``Z``/``+01:00``) the frontmatter accepts compare correctly (ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf); equal or older is *not* stale; a missing or unparseable timestamp is reported,
never raised.

:class:`TranslationDriftResult` is the single structured, non-raising answer the ``check_translation_drift`` tool
returns: both drift kinds in one run (ACC-009).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from .heading_table import iter_heading_lines

__all__ = [
    "DriftFinding",
    "DriftKind",
    "Staleness",
    "SkeletonEntry",
    "TranslationDriftResult",
    "check_staleness",
    "compare_skeletons",
    "heading_skeleton",
]

#: The kinds of structural finding: the three REQ-014a drift kinds, plus ``unparseable`` -- a document that cannot be
#: parsed at all (carries the parse error; never swallowed, never raised).
DriftKind = Literal["missing", "extra", "reordered", "unparseable"]

#: The first heading level that is part of the skeleton: ``h1`` is the free-form document title and is excluded.
_MIN_SKELETON_LEVEL = 2

#: Separator of the canonical ancestor chain in a heading's structural key/path.
_PATH_SEPARATOR = " > "

#: The schema-constant token parts of the data-carrying headings (ADR 38efdb66 item 3): each pattern fullmatches a
#: canonical-mapped heading text and its single group is the token kept as the structural key. Derived from the
#: free-text ``@alias`` REGEX patterns of the twelve i18n-eligible domains' models -- ``dec`` ``^Option \d+: .+$``,
#: ``sop``/``uc`` ``^Step \d+: .+$``, ``uc`` ``^Extension \d+[a-z]?\. .+$``, ``vcr`` ``AC-(\d{3}) (<DTAIS>): .+`` --
#: a drift-pin test walks the models' aliases and fails if a new free-text alias appears that no rule here covers.
_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(Option \d+:) .+"),
    re.compile(r"(Step \d+:) .+"),
    re.compile(r"(Extension \d+[a-z]?\.) .+"),
    re.compile(r"(AC-\d{3} \((?:Demonstration|Test|Analysis|Inspection|Special)\):) .+"),
)

#: The timestamp-led update-entry heading (``<timestamp> ( - | : ) <title>``): the alias every domain's own
#: ``UpdateEntry``/``Recent Updates`` entry shares. Such an entry is a change-log row, excluded from the comparison.
_UPDATE_ENTRY_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\.\d{3}(?:Z|[+-]\d{2}:\d{2})(?: - | : ).+")


@dataclass(frozen=True)
class SkeletonEntry:
    """One compared heading of a document's skeleton.

    Attributes
    ----------
    level:
        The heading level (2-6).
    text:
        The heading text exactly as it appears in the document (its own language).
    token:
        The canonical, language-invariant token of the heading (the table-mapped text, reduced to its
        schema-constant part for a data-carrying heading).
    path:
        The canonical ancestor chain including ``token``, :data:`_PATH_SEPARATOR`-joined.
    key:
        ``path`` made unique within the document by an occurrence suffix (``#2``, ``#3``, ...) for a repeat.
    position:
        The 1-based position of this heading among the document's compared headings.
    """

    level: int
    text: str
    token: str
    path: str
    key: str
    position: int


class DriftFinding(BaseModel):
    """One structural finding of the drift check (REQ-014a).

    Parameters
    ----------
    kind:
        ``"missing"`` -- a source section the variant lacks; ``"extra"`` -- a variant section the source lacks;
        ``"reordered"`` -- a section both have but in a different relative order (the sections outside the longest
        common order are reported); ``"unparseable"`` -- the document cannot be parsed (carries ``error``).
    heading:
        The canonical English heading token (the schema form), or ``None`` for ``"unparseable"``.
    path:
        The canonical ancestor chain including ``heading``, ``" > "``-joined, or ``None`` for ``"unparseable"``.
    level:
        The heading level (2-6), or ``None`` for ``"unparseable"``.
    text:
        The heading text as it appears on disk in the document where the finding was made (the source for
        ``missing``, the variant for ``extra``/``reordered``) -- what the translator wrote for an ``extra`` section.
    source_position:
        The 1-based position among the source's compared headings (``None`` for ``extra``).
    variant_position:
        The 1-based position among the variant's compared headings (``None`` for ``missing``).
    language:
        For ``"unparseable"``: the language of the document that fails to parse.
    error:
        For ``"unparseable"``: the parse-failure message (byte-identical to the domain's ``list_<d>`` failed-row
        ``error`` for the same file).
    message:
        A one-line, human-readable description of the finding.
    """

    kind: DriftKind
    heading: str | None = None
    path: str | None = None
    level: int | None = None
    text: str | None = None
    source_position: int | None = None
    variant_position: int | None = None
    language: str | None = None
    error: str | None = None
    message: str


class TranslationDriftResult(BaseModel):
    """The ``check_translation_drift`` tool's non-raising result: structural drift and staleness in one run.

    Parameters
    ----------
    type:
        The artifact's document type, echoed back.
    id:
        The artifact's id (shared by both languages), echoed back.
    source_language:
        The language compared *against* (``"en"`` by default).
    language:
        The translated variant's language.
    source_path:
        The absolute, resolved path of the source document.
    variant_path:
        The absolute, resolved path of the variant document.
    in_sync:
        ``True`` iff there is no structural finding, the variant is not stale, and staleness could be determined
        (``staleness_error`` is ``None``) -- an unverifiable timestamp never counts as in sync.
    structural:
        The structural findings (empty when the variant's section structure matches the source's).
    stale:
        ``True`` iff the source's ``updated`` timestamp is strictly newer than the variant's (REQ-014b).
    source_updated:
        The source's frontmatter ``updated`` value as written (``None`` if missing/unreadable).
    variant_updated:
        The variant's frontmatter ``updated`` value as written (``None`` if missing/unreadable).
    source_ahead_by_seconds:
        Signed ``source_updated - variant_updated`` in seconds (positive = the source is newer), or ``None`` when
        either timestamp is missing or unparseable.
    staleness_error:
        ``None`` when both timestamps were compared; otherwise why they could not be (missing, unparseable, no UTC
        offset, frontmatter unreadable).
    """

    type: str
    id: str
    source_language: str
    language: str
    source_path: str
    variant_path: str
    in_sync: bool
    structural: list[DriftFinding]
    stale: bool
    source_updated: str | None
    variant_updated: str | None
    source_ahead_by_seconds: float | None
    staleness_error: str | None


@dataclass(frozen=True)
class Staleness:
    """The outcome of :func:`check_staleness` (the staleness half of a :class:`TranslationDriftResult`).

    Attributes
    ----------
    stale:
        ``True`` iff the source is strictly newer than the variant.
    source_updated:
        The source's timestamp as written, or ``None`` if missing.
    variant_updated:
        The variant's timestamp as written, or ``None`` if missing.
    source_ahead_by_seconds:
        Signed ``source - variant`` in seconds, or ``None`` if not comparable.
    error:
        ``None`` if compared; otherwise why not.
    """

    stale: bool
    source_updated: str | None
    variant_updated: str | None
    source_ahead_by_seconds: float | None
    error: str | None


def _canonical_token(text: str, table: dict[str, str] | None) -> str | None:
    """Return the language-invariant token of a heading ``text``, or ``None`` for an excluded update entry."""
    assert isinstance(text, str), type(text)
    assert table is None or isinstance(table, dict), type(table)

    mapped = text if table is None else table.get(text, text)
    if _UPDATE_ENTRY_PATTERN.fullmatch(mapped) is not None:
        result: str | None = None
        return result
    for pattern in _TOKEN_PATTERNS:
        match = pattern.fullmatch(mapped)
        if match is not None:
            result = match.group(1)
            return result
    result = mapped
    return result


def heading_skeleton(body: str, table: dict[str, str] | None) -> list[SkeletonEntry]:
    """Reduce a document's (mdformat-normalized) body text to its ordered, language-invariant heading skeleton.

    See the module docstring for the structural-key rule. ``h1`` headings and timestamp-led update entries (with
    everything nested inside them) are not part of the skeleton.

    Parameters
    ----------
    body:
        The frontmatter-stripped, mdformat-normalized body text.
    table:
        The document language's ``<translated> -> <canonical>`` heading table, or ``None`` for a canonical (EN)
        document.

    Returns
    -------
    list[SkeletonEntry]
        One entry per compared heading, in document order, ``position`` numbered from 1.
    """
    assert isinstance(body, str), type(body)
    assert table is None or isinstance(table, dict), type(table)

    result: list[SkeletonEntry] = []
    #: The open ancestor chain: ``(level, token, excluded)``.
    stack: list[tuple[int, str, bool]] = []
    occurrences: dict[str, int] = {}
    for _index, level, text in iter_heading_lines(body):
        if level < _MIN_SKELETON_LEVEL:
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        token = _canonical_token(text, table)
        excluded = token is None or any(entry[2] for entry in stack)
        stack.append((level, text if token is None else token, excluded))
        if excluded:
            continue
        assert token is not None
        path = _PATH_SEPARATOR.join([entry[1] for entry in stack])
        occurrences[path] = occurrences.get(path, 0) + 1
        key = path if occurrences[path] == 1 else f"{path}#{occurrences[path]}"
        result.append(SkeletonEntry(level, text, token, path, key, len(result) + 1))
    return result


def _longest_common_subsequence(a: list[str], b: list[str]) -> list[str]:
    """Return one longest common subsequence of ``a`` and ``b`` (standard dynamic programming, deterministic)."""
    lengths = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            if a[i] == b[j]:
                lengths[i][j] = lengths[i + 1][j + 1] + 1
            else:
                lengths[i][j] = max(lengths[i + 1][j], lengths[i][j + 1])
    result: list[str] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            result.append(a[i])
            i += 1
            j += 1
        elif lengths[i + 1][j] >= lengths[i][j + 1]:
            i += 1
        else:
            j += 1
    return result


def compare_skeletons(source: list[SkeletonEntry], variant: list[SkeletonEntry]) -> list[DriftFinding]:
    """Diff a variant's skeleton against its source's into ``missing``/``extra``/``reordered`` findings (REQ-014a).

    Findings come in a deterministic order: every ``missing`` (source order), every ``extra`` (variant order), then
    every ``reordered`` (variant order). A section both documents have but in a different relative order is
    ``reordered``: the sections *outside* one longest common subsequence of the two documents' shared sections are
    reported (so one moved section yields one finding, not a cascade).

    Parameters
    ----------
    source:
        The source document's skeleton.
    variant:
        The variant document's skeleton.

    Returns
    -------
    list[DriftFinding]
        The structural findings; empty when the two skeletons agree.
    """
    assert isinstance(source, list), type(source)
    assert isinstance(variant, list), type(variant)

    source_by_key = {entry.key: entry for entry in source}
    variant_by_key = {entry.key: entry for entry in variant}
    result: list[DriftFinding] = []
    for entry in source:
        if entry.key not in variant_by_key:
            result.append(
                DriftFinding(
                    kind="missing",
                    heading=entry.token,
                    path=entry.path,
                    level=entry.level,
                    text=entry.text,
                    source_position=entry.position,
                    message=f"section '{entry.path}' of the source is missing in the variant",
                )
            )
    for entry in variant:
        if entry.key not in source_by_key:
            result.append(
                DriftFinding(
                    kind="extra",
                    heading=entry.token,
                    path=entry.path,
                    level=entry.level,
                    text=entry.text,
                    variant_position=entry.position,
                    message=f"section '{entry.path}' of the variant ({entry.text!r}) does not exist in the source",
                )
            )
    common_source = [entry.key for entry in source if entry.key in variant_by_key]
    common_variant = [entry.key for entry in variant if entry.key in source_by_key]
    kept = set(_longest_common_subsequence(common_source, common_variant))
    for entry in variant:
        if entry.key in source_by_key and entry.key not in kept:
            counterpart = source_by_key[entry.key]
            result.append(
                DriftFinding(
                    kind="reordered",
                    heading=entry.token,
                    path=entry.path,
                    level=entry.level,
                    text=entry.text,
                    source_position=counterpart.position,
                    variant_position=entry.position,
                    message=(
                        f"section '{entry.path}' is at position {entry.position} in the variant but "
                        f"{counterpart.position} in the source (relative order differs)"
                    ),
                )
            )
    return result


def _parse_timestamp(value: object, label: str) -> tuple[datetime | None, str | None, str | None]:
    """Parse one frontmatter ``updated`` value into ``(aware datetime, as-written text, error)`` (each may be None)."""
    if value is None:
        return None, None, f"{label} `updated` is missing"
    if isinstance(value, datetime):
        parsed = value
        text = value.isoformat()
    elif isinstance(value, str):
        text = value
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None, text, f"{label} `updated` value {value!r} is not a valid ISO 8601 date+time"
    else:
        return None, str(value), f"{label} `updated` value {value!r} is not a timestamp"
    if parsed.utcoffset() is None:
        return None, text, f"{label} `updated` value {text!r} carries no UTC offset, so it cannot be compared"
    return parsed, text, None


def check_staleness(source_updated: object, variant_updated: object) -> Staleness:
    """Compare the source's and the variant's ``updated`` timestamps (REQ-014b).

    Both values are parsed to offset-aware datetimes and compared as instants -- never as strings -- so the ``T``
    and space separators and any UTC offset compare correctly. The variant is stale iff the source is strictly
    newer; equal or older is not stale. A missing, unparseable, or offset-less timestamp on either side is
    reported in ``error`` (``stale`` stays ``False``, nothing is raised).

    Parameters
    ----------
    source_updated:
        The source frontmatter's ``updated`` value (a string as written, a ``datetime`` PyYAML coerced, or ``None``).
    variant_updated:
        The variant frontmatter's ``updated`` value, likewise.

    Returns
    -------
    Staleness
        The staleness verdict with both timestamps as written and the signed delta.
    """
    source_dt, source_text, source_error = _parse_timestamp(source_updated, "source")
    variant_dt, variant_text, variant_error = _parse_timestamp(variant_updated, "variant")
    errors = [error for error in (source_error, variant_error) if error is not None]
    if source_dt is None or variant_dt is None:
        result = Staleness(False, source_text, variant_text, None, "; ".join(errors))
        return result
    delta = (source_dt - variant_dt).total_seconds()
    result = Staleness(delta > 0, source_text, variant_text, delta, None)
    return result
