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

"""``@mcp.tool()`` wrapper: create_sysrs (Task 3.2).

Unlike ``adr.tools.create_adr`` (which accepts a full ``frontmatter``/``body``
pair and renders the body back out via ``render_adr``), ``create_sysrs``
accepts **body markdown only** and never renders anything: the caller's own
already-validated ``content`` text is persisted byte-for-byte, and only the
small frontmatter YAML block is code-generated and prepended -- mirrors
``vcr.tools.create_vcr``/``dec.tools.create_dec`` file-for-file.

Thin file-I/O adapter. The ``.md`` file itself is always the source of
truth (ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3); the in-memory cache
warmed after the write below (feat-107-doc-cache Phase 4, REQ-003) is only
ever a content-hash-validated memoization of that file's own current
state, never an independent fact, matching every other tool in this
codebase.

**Language variants (feat-197-i18n Phase 125, ADR 38efdb66 items 1/2/5/6).**
A 1:1 port of ``create_dec``'s ``language``/``id`` handling. ``create_sysrs``
gains two optional parameters, ``language`` (default ``"en"``) and ``id``.
With ``language`` omitted/``"en"`` the tool is byte-identical to before: it
assigns a fresh id and writes the flat ``docs/sysrs/sysrs-<id>-<slug>.md`` file
(and ``id`` must not be given). With a non-default ``language`` the tool
creates a *translation* of an existing System Requirements Specification: ``id`` -- the shared id of the
EN source document (REQ-003, the id is never language-qualified and is never
freshly assigned for a variant) -- is then **required**, the EN source must
already exist on disk (ADR item 2: the EN slug is the single filename
authority), and the variant is written to ``docs/sysrs/{language}/`` under the
EN source's exact basename with the shared id as its frontmatter ``id``
(fresh ``created``/``updated``, ``status="draft"`` -- this domain's create
status, as on every create). The body is validated through the variant's
heading-mapping table (:func:`~biz.dfch.specmgr.sysrs.models.v1.parse_sysrs_body`)
and then persisted byte-for-byte, like EN. An already-existing variant of the
same id and language is never overwritten (``FileExistsError``).
"""

from __future__ import annotations

import uuid

from ...general.models import ValidateResult, ValidationErrorEntry
from ...general.models.heading_table import resolve_heading_table
from ...general.tools._doc_paths import slugify
from ...general.tools._path_safety import DEFAULT_LANGUAGE, assert_language, validate_id
from ...general.tools._timestamps import now_timestamp
from ...general.tools.validate import _CAUGHT_EXCEPTIONS, _MAX_VALIDATE_ERROR_CHARS
from ...models.md import CURRENT_SCHEMA_VERSION
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import snippet
from ...server import mcp
from ..models.v1 import SysrsFrontmatter, parse_sysrs_body
from ._io import read_sysrs
from ._lock import sysrs_lock, sysrs_lock_key
from ._paths import SysrsNotFoundError, ensure_sysrs_base_dir, find_sysrs_path, sysrs_base_dir
from ._write import write_sysrs_file


@mcp.tool(
    name="create_sysrs",
    title="Create System Requirements Specification",
    description=(
        "Create a new System Requirements Specification: assigns a fresh id, derives a filename "
        "from the body's H1 title, validates the submitted body-only content, and writes the new "
        "document to the System Requirements Specification base directory. A content-validation "
        "failure of the submitted body returns a non-raising `ValidateResult` (`valid=False`, a "
        "single `errors[].message` capped at 300 chars as the generic `validate` tool caps it, "
        "feat-110) instead of raising `AssertionError`/`pydantic.ValidationError` (ADR "
        "f14f125e-eaad-4f4f-a6fd-3c931bed726e, GitHub issue #204 -- case 5 of the ADR 519d1206 "
        "non-raising-structured-result workaround chain); nothing is written in that case. The structure "
        "reference is the `get_sysrs_schema` tool (the generated JSON Schema); the "
        "`get_sysrs_template`/`get_sysrs_example` tools return the authoring template and a complete "
        "sample. Returns the newly created document's frontmatter only (no body); use the corresponding "
        "`get_sysrs` tool to fetch the full document afterward. "
        "The optional `language` parameter (default 'en', feat-197-i18n) selects the language to create "
        "the document in: omitted/'en' = a new flat docs/sysrs/ document with a fresh id, exactly the default "
        "behavior (`id` must then be omitted); a non-default ISO 639-1-shaped lowercase two-letter code "
        "(e.g. 'de') creates a TRANSLATION of an existing System Requirements Specification instead: "
        "`id` -- the shared id of the "
        "existing EN source document -- is then required (no fresh id is assigned; the variant carries the "
        "same id), the EN source must exist (else `SysrsNotFoundError`), and the variant is written to "
        "docs/sysrs/{language}/ under the EN source's exact file name with `status` draft; `content` is "
        "validated through that language's heading-mapping table (translated headings are accepted) and "
        "persisted verbatim. An existing variant of that id and language is never overwritten "
        "(`FileExistsError`). A malformed `language`, one with no packaged heading-mapping table, a missing "
        "`id` for a non-default language, or an `id` given for the default language is a `ValueError` "
        "raised before any file access."
    ),
)
def create_sysrs(  # pylint: disable=too-many-locals
    content: str,
    language: str = DEFAULT_LANGUAGE,
    id: str | None = None,
) -> SysrsFrontmatter | ValidateResult:
    """Create and write a new System Requirements Specification document.

    ``content`` is body markdown only (the ``Sysrs`` H1 and its sections) --
    it must not carry a YAML frontmatter block. The entire frontmatter is
    built by this tool: a fresh id (``uuid.uuid4()``), ``type="sysrs"``,
    ``status="draft"`` (always, never caller-supplied on create),
    ``created``/``updated`` both set to the current timestamp, and
    ``version`` set to the current ``models.md`` schema version.

    ``content`` is validated by constructing a
    :class:`~biz.dfch.specmgr.sysrs.models.v1.Sysrs` from it
    (``Sysrs.from_text(format_text(content))``). A structural failure
    raises ``AssertionError`` and a field/cross-field failure raises
    ``pydantic.ValidationError`` -- but this tool catches both
    (feat-204-create-error, ADR f14f125e-eaad-4f4f-a6fd-3c931bed726e --
    case 5 of the ADR 519d1206-4d2a-4500-9046-6db635209996 non-raising,
    structured-result workaround chain) and returns the enriched message
    (domain/tool/channel context prepended by the shared tool-boundary
    wrapper, :func:`~biz.dfch.specmgr.models.md._errors.wrap_tool_errors`,
    on top of the engine's own field-path/line/snippet enrichment,
    feat-27-validation Phases 1/2) as the non-raising
    ``ValidateResult(valid=False, ...)`` (see Returns below) instead --
    nothing is written in that case.

    No body rendering is ever needed: the caller's own already-validated
    ``content`` is persisted byte-for-byte, exactly as submitted; only the
    small, code-constructed frontmatter YAML block is (re)generated.

    **Language variants (feat-197-i18n Phase 125).** With a non-default
    ``language`` this tool creates a translation of an existing EN
    document rather than a new one -- see the module docstring: the
    shared ``id`` of the EN source is a required argument (the variant's
    frontmatter ``id`` is that same id, never a fresh one, REQ-003), the EN
    source must exist, and the variant is written to
    ``docs/sysrs/{language}/`` under the EN source's exact basename
    (ADR 38efdb66 item 2). ``content`` is validated through the variant's
    heading-mapping table, and the existing-variant guard
    (``FileExistsError``) runs under the variant's own per-language lock.

    Parameters
    ----------
    content:
        The new document's body markdown, with no frontmatter block (for a
        non-default ``language``: the translation, whose fixed-text
        headings may be translated per that language's table).
    language:
        The language to create the document in: ``"en"`` (the default)
        creates a new, flat ``docs/sysrs/`` document with a freshly assigned
        id -- today's exact behavior; any other ISO 639-1-shaped lowercase
        two-letter code (e.g. ``"de"``) creates a translation variant of
        an existing EN document in ``docs/sysrs/{language}/``. Shape-guarded
        (and its heading-mapping table resolved) before any filesystem
        access.
    id:
        The shared id of the existing EN source document. Required when
        ``language`` is not the default (the variant reuses it as its own
        frontmatter id); must be omitted for the default language (a new
        document's id is always server-assigned).

    Returns
    -------
    SysrsFrontmatter | ValidateResult
        The newly created document's frontmatter only (no body), with its
        assigned id in ``.id``. Use the corresponding ``get_sysrs`` tool to
        fetch the full document afterward. On a content-validation failure
        of ``content``, a non-raising
        :class:`~biz.dfch.specmgr.general.models.ValidateResult`
        (``valid=False``) with exactly one ``errors`` entry whose
        ``message`` is the enriched exception text capped at 300 chars
        exactly as the generic ``validate`` tool caps it (feat-110, via
        :func:`~biz.dfch.specmgr.models.md._markdown.snippet`), instead of
        ``AssertionError``/``pydantic.ValidationError`` -- nothing is written
        in that case (feat-204-create-error, ADR
        f14f125e-eaad-4f4f-a6fd-3c931bed726e -- case 5 of the ADR
        519d1206-4d2a-4500-9046-6db635209996 non-raising, structured-result
        workaround chain).

    Raises
    ------
    ValueError
        ``language`` is not an ISO 639-1-shaped lowercase two-letter code,
        a non-default ``language`` has no packaged heading-mapping table,
        ``id`` is missing for a non-default ``language``, ``id`` is given
        for the default language, or ``id`` is not a well-formed UUID --
        all raised before any filesystem access; nothing is written.
    SysrsNotFoundError
        A non-default ``language`` was given but no EN source document
        with ``id`` exists (a variant requires its EN source, ADR 38efdb66
        item 2); nothing is written.
    FileExistsError
        A variant of ``id`` in this non-default ``language`` already
        exists (a variant is never overwritten); nothing is written.
    """
    assert_language(language)
    is_variant = language != DEFAULT_LANGUAGE
    if is_variant:
        if id is None:
            raise ValueError(
                f"id is required to create a {language!r} variant: pass the shared id of the existing EN "
                f"source document (a translation reuses its id; no fresh id is assigned)"
            )
        validate_id("sysrs", id)
        resolve_heading_table(language)
    elif id is not None:
        raise ValueError(
            f"id {id!r} can only be given together with a non-default language: a new {DEFAULT_LANGUAGE!r} "
            f"document always gets a freshly assigned id"
        )

    try:
        with wrap_tool_errors(domain="sysrs", tool="create_sysrs", channel=BODY_CHANNEL):
            body = parse_sysrs_body(content, language=language)
    except _CAUGHT_EXCEPTIONS as ex:
        message = snippet(str(ex), max_chars=_MAX_VALIDATE_ERROR_CHARS)
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=message)])

    if is_variant:
        assert id is not None
        result = _create_variant(id, language, content)
        return result

    new_id = str(uuid.uuid4())
    now = now_timestamp()
    new_frontmatter = SysrsFrontmatter(
        id=new_id,
        type="sysrs",
        status="draft",
        created=now,
        updated=now,
        version=CURRENT_SCHEMA_VERSION,
    )
    filename = f"sysrs-{new_id}-{slugify(body.text)}.md"
    base_dir = ensure_sysrs_base_dir()
    path = base_dir / filename
    write_sysrs_file(path, new_frontmatter, content)
    read_sysrs(path)  # warm the cache with this write's own validated content (feat-107-doc-cache Phase 4, REQ-003)
    return new_frontmatter


def _create_variant(id_: str, language: str, content: str) -> SysrsFrontmatter:
    """Create the ``language`` variant of the existing EN ``sysrs`` document ``id_`` (ADR 38efdb66 item 2).

    Resolves the EN source's path (the flat directory's id-scan), reuses its
    exact basename inside ``docs/sysrs/{language}/``, and writes the
    already-validated ``content`` byte-for-byte with a frontmatter carrying
    the shared id (REQ-003). Runs under the variant's own per-language lock
    so the existence guard and the write are atomic with respect to every
    other mutation of this variant.

    Parameters
    ----------
    id_:
        The shared id of the EN source document.
    language:
        The (shape-guarded, table-resolved, non-default) target language.
    content:
        The already-validated variant body markdown.

    Returns
    -------
    SysrsFrontmatter
        The variant's frontmatter (``id`` == ``id_``).

    Raises
    ------
    SysrsNotFoundError
        No EN source document with ``id_`` exists.
    FileExistsError
        The variant file already exists.
    """
    assert isinstance(id_, str), type(id_)
    assert id_.strip()
    assert language != DEFAULT_LANGUAGE, language
    assert isinstance(content, str), type(content)

    with sysrs_lock(sysrs_lock_key(id_, language)):
        try:
            source_path = find_sysrs_path(sysrs_base_dir(), id_)
        except SysrsNotFoundError as ex:
            raise SysrsNotFoundError(
                f"cannot create the {language!r} variant of sysrs {id_!r}: "
                f"no (parseable) {DEFAULT_LANGUAGE!r} source document with this id exists. "
                f"A language variant requires its {DEFAULT_LANGUAGE!r} source "
                f"-- create the {DEFAULT_LANGUAGE!r} document first, and pass its id."
            ) from ex
        path = ensure_sysrs_base_dir(language) / source_path.name
        if path.exists():
            raise FileExistsError(
                f"the {language!r} variant of sysrs {id_!r} already exists at {path}; "
                f"use the generic `update`/`edit` tools with language={language!r} to change it"
            )
        now = now_timestamp()
        new_frontmatter = SysrsFrontmatter(
            id=id_,
            type="sysrs",
            status="draft",
            created=now,
            updated=now,
            version=CURRENT_SCHEMA_VERSION,
        )
        write_sysrs_file(path, new_frontmatter, content)
        read_sysrs(path)  # warm the variant's own cache entry (path-keyed; the EN entry is untouched)
    return new_frontmatter
