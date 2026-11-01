# `biz.dfch.specmgr.sysrs.tools.list_sysrs`

``@mcp.tool()`` wrapper: list_sysrs (Task 3.2).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13: "Expose ``list_<domain>`` as a paged
MCP tool, not a resource") -- like GOL/DEC/SOP/VCR (domains built after that
ADR was accepted), SYSRS must not repeat the resource-then-convert history
of REQ/UC/TSK/QA/PRB (launched as a ``specmgr://<domain>/list`` resource,
converted later in feat-13-list-paging). See
``.specmgr/feat/feat-13-list-paging/README.md`` for the full paging contract
shared by every ``list_<domain>`` tool.

feat-81-83-validation Phase 3 (REQ-006/REQ-007) routed this tool through
the shared ``general.tools._listing.build_summaries`` helper: a file that
fails to parse now appears inline in ``results`` as a failed entry (marker
``title``/``status``, ``ref``, ``path``, and ``error``) and contributes to
both ``total`` and the new ``error_count``, instead of being silently
skipped.

**feat-200-list (GitHub issue #200), Task 110.100: the optional ``glob``
parameter.** This tool now takes an optional, case-insensitive ``glob``
pattern matched against each document's own id (a UUID; REQ-002/REQ-004):
the shared ``general.tools._listing.filter_summaries_by_glob`` helper runs
on the materialized row list, between this tool's own row build and the
``total``/paging step, so it never re-scans the filesystem on its own. A
failed-to-parse row carries ``id=None`` and therefore never matches, so a
glob-given result has no failed rows and ``error_count = 0`` by
construction (REQ-003); ``total`` is the match count and
``offset``/``max_results`` paging keeps its existing meaning on that
smaller set (ACC-004). ``glob=None`` (the default) leaves every outcome
byte-identical to the pre-glob behaviour (REQ-005), and an empty string is
a pattern, not an off-switch (it matches no id and yields a zero-row
result).

**Language variants (feat-197-i18n Phase 125, ADR 38efdb66 items 1/6/7).**
A 1:1 port of ``list_dec``'s ``language`` handling. The optional
``language`` parameter (default ``"en"``) selects which directory this tool
scans: omitted/``"en"`` = the flat ``docs/sysrs/`` directory -- today's exact
behavior; any other shape-validated code (e.g. ``"de"``) = only the
``docs/sysrs/{language}/`` subdirectory, listing exactly the existing
variants of that language (ACC-007). There is deliberately NO "all
languages" mode (the ``DocSummary`` row shape carries no language column
and would repeat ids). The language is shape-guarded before any filesystem
access, and a shape-valid language without a packaged heading-mapping table
is rejected up front with the table loader's actionable error. The row
shape is unchanged -- no language column.

## Functions

### `_to_failed_summary(path: 'Path', error: 'Exception') -> 'SysrsSummary'`


### `_to_summary(doc: 'SysrsDocument', path: 'Path') -> 'SysrsSummary'`


### `list_sysrs(max_results: 'int | None' = None, offset: 'int | None' = None, glob: 'str | None' = None, language: 'str' = 'en') -> 'PagedResult[SysrsSummary]'`

Return one page of one-line System Requirements Specification summaries from the configured base directory.

A file that fails to parse (``AssertionError``, ``pydantic.ValidationError``,
or ``yaml.YAMLError`` -- the same channels
:func:`~biz.dfch.specmgr.sysrs.models.v1.parse_sysrs` raises) appears
inline in ``results`` as its own failed entry (``id=None``,
``title``/``status`` both the fixed marker ``"<failed to parse>"``,
``ref``/``path`` populated the same way as a successful entry, and
``error`` carrying the exception's message) rather than being silently
skipped (feat-81-83-validation Phase 3, REQ-006) -- a single malformed
file must not break listing every other valid one. The complete list
(successes and failures both) is materialized first, then -- when
``glob`` is given -- filtered to the rows whose ``id`` matches it (the
shared ``general.tools._listing.filter_summaries_by_glob`` helper,
applied between the row build and the ``total``/paging step), then
paginated in memory, so the returned ``total``/``error_count`` always
reflect the whole directory (or that filtered subset), independent of
paging.

Parameters
----------
max_results:
    Maximum number of summaries to return in this page. Defaults to
    ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);
    otherwise clamped into range (see
    :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).
offset:
    Zero-based index of the first summary to include in this page.
    Defaults to ``0`` when not given (``None``); negative values are
    floored to ``0``.
glob:
    Optional glob pattern matched, case-insensitively, against each
    document's own id (a UUID) -- e.g. ``"dead*"`` (feat-200-list,
    GitHub issue #200, REQ-002/REQ-004). Defaults to ``None`` (no
    filtering: the complete directory is listed, exactly as before --
    REQ-005). An empty string is a pattern, not an off-switch: it
    matches no id (ids are never empty) and yields a zero-row result.
    Failed-to-parse rows carry ``id=None`` and therefore never match
    any pattern, so a glob-given result has no failed rows and
    ``error_count = 0`` by construction (REQ-003); ``total`` is the
    match count and ``offset``/``max_results`` paging keeps its existing
    meaning on that smaller set.
language:
    The language whose directory to list (feat-197-i18n Phase 125, ADR
    38efdb66 items 1/6/7): ``"en"`` (the default, same as omitting it)
    scans the flat ``docs/sysrs/`` directory -- today's exact behavior;
    any other ISO 639-1-shaped lowercase two-letter code (e.g.
    ``"de"``) scans only ``docs/sysrs/{language}/``, listing exactly the
    existing variants of that language (ACC-007). There is deliberately
    no "all languages" mode (the row shape carries no language column
    and would repeat ids). Shape-guarded before any filesystem access
    (like ``id``); a shape-valid code without a packaged
    heading-mapping table is rejected up front with the table loader's
    actionable error.

Returns
-------
PagedResult[SysrsSummary]
    One entry per ``*.md`` file within the requested page (successes
    and failures both -- only entries whose ``id`` matches ``glob`` when
    it is given), in filename-sorted order. ``results`` is empty if the
    base directory does not exist, holds no System Requirements
    Specifications, ``offset`` is past the end of the full list, or no
    id matches ``glob``.

Raises
------
ValueError
    ``language`` is not an ISO 639-1-shaped lowercase two-letter code (raised
    before any filesystem access), or a non-default ``language`` has no packaged
    heading-mapping table (raised before any filesystem access).

