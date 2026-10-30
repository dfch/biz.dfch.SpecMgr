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

"""``@mcp.tool()`` wrapper: check_translation_drift (feat-197-i18n Phase 140, Tasks 140.100/140.110, REQ-014, ACC-009).

The generic, read-only drift check between a translated language variant and its source document (the EN source by
default): one deterministic run reports BOTH drift kinds (ACC-009) in a single, structured,
non-raising :class:`~biz.dfch.specmgr.general.models.translation_drift.TranslationDriftResult`:

* **structural drift** (REQ-014a, Task 140.100) -- sections of the variant that are *missing*, *extra*, or
  *reordered* relative to the source's canonical schema. Both documents' *raw* body text is reduced to a heading
  skeleton (the same fence-aware heading recognizer the parse boundary uses), each heading is mapped back to canonical
  English through the document language's heading table, and the free text of the data-carrying headings
  (``Option N: <title>``, ``Step N: <title>``, ``Extension N<l>. <title>``, ``AC-NNN (Method): <text>``) is dropped so
  only the schema-constant token is compared; timestamp-led update entries are change-log rows and are not compared.
  See :mod:`~biz.dfch.specmgr.general.models.translation_drift` for the full rule. A document that fails to parse at
  all is reported as an ``unparseable`` structural finding carrying the parse error (byte-identical to the domain's
  ``list_<d>`` failed-row ``error``), never swallowed and never raised;
* **staleness** (REQ-014b, Task 140.110) -- the source's frontmatter ``updated`` timestamp is strictly newer than the
  variant's. Compared as parsed offset-aware datetimes (not strings), so the ``T``/space separators and any UTC offset
  compare correctly; equal or older is not stale; a missing/unparseable timestamp is reported in ``staleness_error``.

Drift is about structure and staleness, never about wording or translation quality: prose, list items, frontmatter
values and ``prb``'s regex-locked English ``problem_statement`` lead paragraph (ADR 38efdb66 item 11) are invisible
to it. The tool is strictly read-only: it writes, creates, and invalidates nothing.

**Languages.** ``language`` is the variant (always non-EN: ``"en"`` is the canonical source form, never a translation
target -- the ``translate_artifact`` prompt's own rule); ``source_language`` (default ``"en"``) may be any language
with a heading table, since both sides are resolved the same way. Both are shape-guarded and table-probed before any
filesystem access (``_language_guard.guard_language``); ``language == source_language`` is a ``ValueError``.

**Error semantics.** ``feat``/``adr`` are rejected with the permanent "always English" ``ValueError`` (before the id is
looked at); an unknown ``type``, a path-injection/wrong-format ``id`` or ``language``/``source_language``, a table-less
language, ``language='en'`` and equal languages are ``ValueError``s before any filesystem access. A source or variant
document that does not exist at all raises the domain's own not-found error (naming the missing language); one that
exists but fails to parse is a finding in the result, never an exception.
"""

from __future__ import annotations

import frontmatter
import yaml

from ...models.md._markdown import format_text
from ...server import mcp
from ..models.heading_table import resolve_heading_table
from ..models.translation_drift import (
    DriftFinding,
    SkeletonEntry,
    TranslationDriftResult,
    check_staleness,
    compare_skeletons,
    heading_skeleton,
)
from ._domains import WholeBodyOrAdrType
from ._language_guard import LANGUAGE_AWARE_DOMAINS, assert_language_aware_type, guard_language
from ._language_variants import Location, locate
from ._path_safety import DEFAULT_LANGUAGE, validate_id

__all__ = ["check_translation_drift"]


def _locate_or_explain(type_: str, id_: str, language: str, role: str) -> Location:
    """Locate one side of the comparison; a truly absent document raises the domain's not-found error, named."""
    try:
        result = locate(type_, id_, language)
    except LookupError as ex:
        raise type(ex)(f"the {role} document ({language!r}) of {type_} {id_!r} does not exist: {ex}") from ex
    return result


def _read_side(
    location: Location,
) -> tuple[list[SkeletonEntry] | None, object, DriftFinding | None]:
    """Read one document's heading skeleton and raw ``updated`` value, plus its ``unparseable`` finding if any.

    The skeleton and the timestamp are read from the raw on-disk text (frontmatter split, body mdformat-normalized
    exactly as the parser does), independent of whether the document parses -- a document whose frontmatter cannot
    be split yields ``(None, None, ...)`` for them (its parse error is already carried by the finding).
    """
    finding: DriftFinding | None = None
    if not location.parseable:
        assert location.error is not None
        finding = DriftFinding(
            kind="unparseable",
            language=location.language,
            error=location.error,
            message=f"the {location.language!r} document at {location.path} fails to parse: {location.error}",
        )
    text = location.path.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(text)
    except (yaml.YAMLError, ValueError):
        skeleton: list[SkeletonEntry] | None = None
        updated: object = None
        return skeleton, updated, finding
    skeleton = heading_skeleton(format_text(post.content), resolve_heading_table(location.language))
    updated = post.metadata.get("updated")
    return skeleton, updated, finding


@mcp.tool(
    name="check_translation_drift",
    title="Check a translation for structural drift and staleness",
    description=(
        "Read-only. Compare a translated language variant with its source document (the 'en' source by default) "
        "and report both drift kinds in one structured, non-raising `TranslationDriftResult`. `type` is one of "
        f"{', '.join(LANGUAGE_AWARE_DOMAINS)} (feat and adr documents are always English and are rejected with a "
        "ValueError); `id` the artifact's id (shared by both languages); `language` the translated variant "
        "(never 'en'); `source_language` (default 'en') the language compared against. STRUCTURAL drift: every "
        "section heading of both documents is mapped back to canonical English through the language's heading "
        "table (the free text of Option N:/Step N:/Extension N./AC-NNN (Method): headings is ignored, only the "
        "schema-constant token is compared; timestamp-led update entries are not compared) and `structural` lists "
        "each `missing` (a source section the variant lacks), `extra` (a variant section the source lacks) and "
        "`reordered` section with its canonical `heading`, `path`, `level` and positions; a document that fails to "
        "parse is an `unparseable` finding carrying the parse error (byte-identical to list_<d>'s failure text), "
        "never raised. STALENESS: `stale` is true iff the source's frontmatter `updated` is strictly newer than the "
        "variant's (compared as offset-aware datetimes; equal is not stale), with both timestamps, the signed "
        "`source_ahead_by_seconds`, and `staleness_error` when a timestamp is missing or unparseable. `in_sync` is "
        "true iff there is no structural finding, the variant is not stale and staleness could be determined. "
        "Wording, prose, frontmatter values and prb's English problem_statement are never compared. A source or "
        "variant that does not exist at all raises the domain's not-found error; invalid type/id/language "
        "(path-injection, wrong shape, a language without a heading table, language 'en', equal languages) is a "
        "ValueError raised before any file access. It writes, creates and invalidates nothing; to translate or "
        "update a variant use the translate_artifact prompt."
    ),
)
def check_translation_drift(
    type: WholeBodyOrAdrType,
    id: str,
    language: str,
    source_language: str = DEFAULT_LANGUAGE,
) -> TranslationDriftResult:
    """Check a translated variant for structural drift and staleness against its source.

    Parameters
    ----------
    type:
        The document type: one of the eleven i18n-eligible domains ``req``, ``uc``, ``tsk``, ``qa``, ``prb``,
        ``gol``, ``rsk``, ``dec``, ``sop``, ``vcr``, ``sysrs`` (``feat``/``adr`` are permanently English and
        rejected).
    id:
        The artifact's specmgr-assigned id (shared by both languages).
    language:
        The translated variant's language: an ISO 639-1-shaped lowercase two-letter code with a packaged heading
        table, never ``"en"``.
    source_language:
        The language the variant is compared against (default ``"en"``); any language with a heading table, and
        different from ``language``.

    Returns
    -------
    TranslationDriftResult
        ``structural`` (the ``missing``/``extra``/``reordered``/``unparseable`` findings), ``stale`` with both
        ``updated`` timestamps and the signed delta (``staleness_error`` when not comparable), the two resolved
        paths, and ``in_sync`` (no structural finding, not stale, staleness determined).

    Raises
    ------
    ValueError
        ``type`` is ``feat``/``adr`` (always English) or unknown; ``id`` is a path-injection attempt or not in the
        domain's own format; ``language``/``source_language`` is not a two-letter lowercase code or has no packaged
        heading table; ``language`` is ``"en"``; or ``language == source_language`` (all raised before any
        filesystem access).
    ReqNotFoundError / UcNotFoundError / TskNotFoundError / QaNotFoundError / PrbNotFoundError /
    GolNotFoundError / RskNotFoundError / DecNotFoundError / SopNotFoundError / VcrNotFoundError /
    SysrsNotFoundError
        The source or the variant document does not exist at all (the domain's own not-found error, naming the
        missing side); a document that exists but fails to parse is an ``unparseable`` finding instead.
    """
    assert_language_aware_type(type)
    validate_id(type, id)
    guard_language(type, language)
    guard_language(type, source_language)
    if language == DEFAULT_LANGUAGE:
        raise ValueError(
            f"language {language!r} cannot be a translation variant: {DEFAULT_LANGUAGE!r} is the canonical source "
            f"form and is never a translation target; pass the translated language (e.g. 'de')"
        )
    if language == source_language:
        raise ValueError(f"language and source_language must differ, both are {language!r}")

    source = _locate_or_explain(type, id, source_language, "source")
    variant = _locate_or_explain(type, id, language, "variant")

    source_skeleton, source_updated, source_failure = _read_side(source)
    variant_skeleton, variant_updated, variant_failure = _read_side(variant)

    structural = [finding for finding in (source_failure, variant_failure) if finding is not None]
    if source_skeleton is not None and variant_skeleton is not None:
        structural.extend(compare_skeletons(source_skeleton, variant_skeleton))
    staleness = check_staleness(source_updated, variant_updated)

    result = TranslationDriftResult(
        type=type,
        id=id,
        source_language=source_language,
        language=language,
        source_path=str(source.path),
        variant_path=str(variant.path),
        in_sync=not structural and not staleness.stale and staleness.error is None,
        structural=structural,
        stale=staleness.stale,
        source_updated=staleness.source_updated,
        variant_updated=staleness.variant_updated,
        source_ahead_by_seconds=staleness.source_ahead_by_seconds,
        staleness_error=staleness.error,
    )
    return result
