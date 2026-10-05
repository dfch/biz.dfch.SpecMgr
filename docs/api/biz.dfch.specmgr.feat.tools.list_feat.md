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
feature's own README, Decisions Made, for the full rationale). This was the
tool's shape through feat-107-doc-cache.

**feat-187-list-feat-timeout (GitHub issue #187), Task 110.110: the request
path never runs a full body parse.** ADR
3982712a-a46b-4b2b-809f-9c6925a49b44 rewires this tool's own per-folder
resolution away from the generic ``build_summaries``/``read_feat`` pair
(both of which would full-parse on a cold cache, the root cause of the
issue's cold-scan timeout -- 348.6 s measured over this repo's own corpus
at one point): for each live path, exactly one file read
(``path.read_text()``, ``FileNotFoundError`` silently skipped -- the same
vanished-mid-scan behavior ``build_summaries``'s own ``silent_skip_types``
gave, preserved here), then the clean (full-parse) cache's own
``peek_preloaded`` (a parse-free lookup against the one ``text`` already
read -- :func:`~biz.dfch.specmgr.feat.tools._cache.peek_feat`), falling
back on a clean miss to the dirty (frontmatter-stage) cache's own
``read_preloaded`` (:func:`~biz.dfch.specmgr.feat.tools._cache.read_feat_dirty_preloaded`,
which runs the cheap frontmatter+H1 derivation on a dirty miss and caches
it) -- never a second, independent file read between the two cache
queries. Each resolved folder's row follows the three-tier contract
(REQ-004): a clean **success** is today's exact row; a clean **failure**
(tier 1 malformed/missing frontmatter YAML, or a frontmatter schema
violation already caught at the clean stage) is a byte-identical failed
row (the clean cache's own fresh-exception reconstruction, so this text is
byte-identical to ``get_feat``'s ``ParseFailureResult.error`` for the same
file, ADR 9080b37c); a dirty **success** is a row built from the
frontmatter+H1 payload -- correct ``id``/``title``/``status``/``ref``/
``path``, but *transiently* healthy if this file also carries a body-level
defect the dirty stage never looks for (tier 3's documented limitation,
corrected once the background warmup's -- or any on-demand ``get_feat``
read's -- clean-stage pass reaches this file); a dirty **failure** is a
failed row too, for either tier 1 (malformed YAML -- byte-identical to
``get_feat``'s error by construction, since both stages run the identical
``parse_frontmatter`` call) or tier 2 (a missing/wrong-shape H1 -- a
dirty-stage-specific ``error`` text that does **not** yet match
``get_feat``'s own body-aware message for the same defect, converging to
byte-identical only once the clean stage has passed this file). This
convergence is what time-qualifies the ``list_<d>``/``get_<d>`` error
byte-identity property (ADR 9080b37c) for ``feat`` specifically -- every
other domain's property is unchanged. The opt-out flag
``SPECMGR_FEAT_WARMUP_DISABLED`` (``general.tools._startup_warmup``) stops
the background warmup from ever running at all, under which convergence
depends solely on on-demand clean reads (e.g. ``get_feat``) -- time-
qualified the same way, just without a dirty-stage interim ``error`` text
ever appearing for files the request path has not independently resolved
through the clean stage. ``_to_summary``/``_to_failed_summary`` below stay
exported and untouched (Phase 120's ACC-003 reference-implementation test
calls them directly against the still-unmodified generic
``build_summaries`` sweep for its byte-identical-convergence diff) even
though this tool's own production request path no longer calls either of
them -- see ``whitelist.py``'s own feat-187 entry for the resulting,
expected ``vulture`` false positive.

## Functions

### `_clean_summary(doc: 'FeatDocument', path: 'Path') -> 'FeatSummary'`

Build a healthy summary row for a clean-stage (full-parse) hit -- today's exact row shape.


### `_dirty_summary(payload: 'FeatFrontmatterSummary', path: 'Path') -> 'FeatSummary'`

Build a transiently-healthy summary row from the dirty stage's frontmatter+H1 payload (tier 3).


### `_failed_summary(path: 'Path', error: 'Exception') -> 'FeatSummary'`

Build a failed-entry summary row (tier 1/tier 2/clean-stage failure), via ``default_failed_summary``.


### `_to_failed_summary(path: 'Path', error: 'Exception') -> 'FeatSummary'`

Build a failed-entry summary row via the shared ``default_failed_summary``.

Kept for Phase 120's ACC-003 reference-implementation test (see the
module docstring) -- this tool's own production request path calls
``default_failed_summary`` directly instead (see :func:`_failed_summary`).


### `_to_summary(doc: 'FeatDocument', path: 'Path') -> 'FeatSummary'`

Build a healthy summary row from a fully-parsed document (the clean-stage/today's-sweep shape).

Kept for Phase 120's ACC-003 reference-implementation test (see the
module docstring) -- this tool's own production request path builds its
clean-stage success rows via :func:`_clean_summary` instead, which has
an identical body.


### `list_feat(max_results: 'int | None' = None, offset: 'int | None' = None) -> 'PagedResult[FeatSummary]'`

Return one page of one-line feature summaries from the configured base directory.

**The request path never fully parses a document's body (ADR
3982712a-a46b-4b2b-809f-9c6925a49b44, GitHub issue #187).** Each live
folder's ``README.md`` is read exactly once and resolved via one of two
cache stages, never a full ``parse_feat`` call on this request path
(see the module docstring for the full three-tier contract): a clean
(full-parse) cache hit yields today's exact row (success or a failed
entry byte-identical to ``get_feat``'s ``ParseFailureResult.error``);
on a clean miss, the dirty (frontmatter-stage) cache yields either a
*transiently* healthy row (correct ``id``/``title``/``status``, but a
body-level defect this file may have is not yet visible -- tier 3) or a
failed row for a tier-1 (malformed frontmatter YAML, byte-identical to
``get_feat`` by construction) or tier-2 (missing/wrong-shape H1,
dirty-stage-specific ``error`` text that converges to byte-identical
only once a full parse has passed this file) defect. A background
warmup thread (``general.tools._startup_warmup``) progressively
full-parses every folder so these rows converge over time; set
``SPECMGR_FEAT_WARMUP_DISABLED`` to disable it entirely (convergence
then depends solely on an on-demand clean read, e.g. a ``get_feat``
call for that folder). ``id=None``, ``title``/``status`` both the
fixed marker ``"<failed to parse>"``, ``ref``/``path`` populated the
same way as a successful entry, and ``error`` carrying the failure's
message -- a single malformed document must not break listing every
other valid one (feat-81-83-validation Phase 3, REQ-006). This
includes every one of the pre-existing, hand-authored feature folders
that predate this schema (out of scope for that feature, see its own
README's Scope section) -- they are no longer invisible, just reported
with an ``error`` (once their clean stage has converged). A folder
whose ``README.md`` vanishes mid-scan, racing a concurrent
``set_feat_id`` rename or a concurrent ``delete`` (``FileNotFoundError``
on this tool's own single read), is instead silently omitted from the
returned page -- contributing to neither ``results``, ``total``, nor
``error_count`` (feat-107-doc-cache Phase 8, REQ-016; this corrects
Phase 6's original choice, REQ-012, to report this exact case as a
failed entry via a now-removed, ``feat``-only ``_FEAT_ERROR_TYPES``).
The complete list (successes and failures both, excluding any silently
omitted path) is materialized first, then paginated in memory, so the
returned ``total``/``error_count`` always reflect the whole directory,
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

