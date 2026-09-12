# `biz.dfch.specmgr.feat.tools.list_feat`

``@mcp.tool()`` wrapper: list_feat (Task 2.3).

Ships as a paged ``@mcp.tool()`` from day one (ADR
ec9f5262-9912-49d0-903f-fcfb54f28c13). Mirrors ``dec.tools.list_dec``'s
overall shape, with two feat-only differences: (1) it scans
``<base>/*/README.md`` via :func:`~biz.dfch.specmgr.feat.tools._paths.iter_feat_paths`,
not ``<base>/*.md``; (2) each :class:`~biz.dfch.specmgr.feat.models.v1.FeatSummary`
uses ``ref = path.parent.name`` (the containing folder's own name, which by
convention already equals ``id`` for a healthy document) rather than
``path.stem`` (which would just be the fixed, uninformative ``"README"``).
``path`` itself (REQ-004's original Addressing section) is no longer a
`feat`-only field -- feat-81-83-validation Phase 3/4 (REQ-007) generalized
it onto the shared ``DocSummary`` base every whole-body domain's summary
now carries.

feat-81-83-validation Phase 3 (REQ-006/REQ-007) routed this tool through
the shared ``general.tools._listing.build_summaries`` helper: a folder
whose ``README.md`` fails to parse now appears inline in ``results`` as a
failed entry (marker ``title``/``status``, ``ref``, ``path``, and
``error``) and contributes to both ``total`` and the new ``error_count``,
instead of being silently skipped -- this includes every one of the
pre-existing, hand-authored feature folders that predate this schema (out
of scope for that feature, see its own README's Scope section), which are
therefore no longer invisible, just reported with an ``error``.
Phase 4 (Task 4.2) retrofitted ``FeatSummary.path`` (both for successful
and failed entries) to the same resolved, absolute
(``.resolve()``d) form every other whole-body domain already uses --
Phase 3 had deliberately left it in its pre-existing unresolved
``str(path)`` form; that divergence no longer exists.

**A folder vanishing mid-scan is silently omitted, not reported as a failed
entry (feat-107-doc-cache Phase 8, REQ-016).** Phase 6 (REQ-012) had this
tool pass its own, ``feat``-only ``_FEAT_ERROR_TYPES = (*DEFAULT_ERROR_TYPES,
FileNotFoundError)`` to ``build_summaries``, reporting a folder whose
``README.md`` vanishes between the directory-listing snapshot and this
tool's own per-path read (e.g. a concurrent ``set_feat_id`` rename racing
this lock-free scan) as a failed entry. Phase 8 corrected that choice:
``general.tools._listing.build_summaries``'s own new ``silent_skip_types``
default (``(FileNotFoundError,)``, REQ-016) now silently omits this case
instead -- the same rule every one of the other whole-body domains'
``list_<domain>`` gets, and the same treatment REQ-005's reconcile-on-scan
already gives a deletion that completes *before* the scan starts (see the
feature's own README, Decisions Made, for the full rationale). ``_FEAT_ERROR_TYPES``
is therefore no longer needed here -- this tool now relies on
``build_summaries``'s own defaults for both ``error_types`` and
``silent_skip_types``.

## Functions

### `_to_failed_summary(path: 'Path', error: 'Exception') -> 'FeatSummary'`


### `_to_summary(doc: 'FeatDocument', path: 'Path') -> 'FeatSummary'`


### `list_feat(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[FeatSummary]'`

Return one page of one-line feature summaries from the configured base directory.

A folder whose ``README.md`` fails to parse (``AssertionError``,
``pydantic.ValidationError``, or ``yaml.YAMLError`` -- the same channels
:func:`~biz.dfch.specmgr.feat.models.v1.parse_feat` raises) appears
inline in ``results`` as its own failed entry (``id=None``,
``title``/``status`` both the fixed marker ``"<failed to parse>"``,
``ref``/``path`` populated the same way as a successful entry, and
``error`` carrying the exception's message) rather than being silently
skipped (feat-81-83-validation Phase 3, REQ-006) -- a single malformed
document must not break listing every other valid one. This includes
every one of the pre-existing, hand-authored feature folders that
predate this schema (out of scope for that feature, see its own
README's Scope section) -- they are no longer invisible, just reported
with an ``error``. A folder whose ``README.md`` vanishes mid-scan,
racing a concurrent ``set_feat_id`` rename or a concurrent ``delete``
(``FileNotFoundError``), is instead silently omitted from the returned
page -- contributing to neither ``results``, ``total``, nor
``error_count`` -- via ``build_summaries``'s own ``silent_skip_types``
default (feat-107-doc-cache Phase 8, REQ-016; this corrects Phase 6's
original choice, REQ-012, to report this exact case as a failed entry
via a now-removed, ``feat``-only ``_FEAT_ERROR_TYPES``). The complete
list (successes and failures both, excluding any silently omitted
path) is materialized first, then paginated in memory, so the returned
``total``/``error_count`` always reflect the whole directory,
independent of paging.

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

Returns
-------
PagedResult[FeatSummary]
    One entry per ``README.md`` file within the requested page
    (successes and failures both), in folder-name-sorted order.
    ``results`` is empty if the base directory does not exist, holds no
    feature folders at all, or ``offset`` is past the end of the full
    list.

