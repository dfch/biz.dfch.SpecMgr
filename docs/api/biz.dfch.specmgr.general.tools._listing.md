# `biz.dfch.specmgr.general.tools._listing`

Generic, doc-type-agnostic ``list_<domain>`` summary construction (feat-81-83-validation Phase 3, Task 3.1).

Mirrors ``general.tools._doc_paths``'s existing callback-based
generalization pattern (``find_doc_path_by_id``): a single module shared
across every ``list_<domain>`` MCP tool, replacing the copy-pasted
try/except/append loop that was, until this feature, byte-for-byte
identical across ``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``dec``/
``sop``/``vcr``/``sysrs`` (``rsk``/``feat`` differ only in how one summary
is *constructed*, handled below by their own ``to_summary``/
``to_failed_summary`` callbacks).

**Before this feature**, a file that failed to parse was silently skipped:
it contributed to neither ``results`` nor ``total``, indistinguishable from
an empty or misconfigured directory (issue #83(b)). **After this feature**,
:func:`build_summaries` turns every failed file into its own summary entry
(marker ``title``/``status``, the real ``ref``/``path``, and the caught
exception's message in ``error``) so it appears inline in ``results`` and
contributes to both ``total`` and the new ``error_count``. This module has
no ``mcp`` import dependency, same as ``_doc_paths.py``/``_paging.py``.

**A file vanishing mid-scan is silently omitted, not reported as a failed
entry (feat-107-doc-cache Phase 8, REQ-016).** :func:`build_summaries` now
takes a ``silent_skip_types`` parameter (default ``(FileNotFoundError,)``),
checked *before* ``error_types``: a path whose ``read`` call raises one of
these types contributes to neither ``results`` nor ``total`` nor
``error_count`` -- as if it had never been in the directory listing to
begin with. A file that vanishes between ``list_<domain>``'s
directory-listing snapshot and this function's own per-path ``read(path)``
call (e.g. a concurrent ``delete`` tool call racing this lock-free scan,
ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3) is the same "deleted outside
specmgr's own tooling" event REQ-005's reconcile-on-scan already handles
*silently* when the deletion completes *before* the scan starts -- treating
a deletion that lands *during* the scan identically, rather than as a
distinct, error-worthy outcome, keeps the two deletion-timing cases
indistinguishable to the caller, which they should be (see the feature's
own README, Decisions Made, for the full rationale). This also corrects
``feat.tools.list_feat``'s own previously-shipped, ``feat``-only divergent
behavior for the identical case (a failed entry via its own
``_FEAT_ERROR_TYPES``, added in Phase 6/REQ-012) to match this same
silent-omission rule every domain now gets.

## Functions

### `build_summaries(paths: 'Iterable[Path]', read: 'Callable[[Path], _DocT]', to_summary: 'Callable[[_DocT, Path], _SummaryT]', to_failed_summary: 'Callable[[Path, Exception], _SummaryT]', error_types: 'tuple[type[Exception], ...]' = (<class 'AssertionError'>, <class 'pydantic_core.ValidationError'>, <class 'yaml.error.YAMLError'>), silent_skip_types: 'tuple[type[Exception], ...]' = (<class 'FileNotFoundError'>,)) -> 'tuple[list[_SummaryT], int]'`

Read and summarize every path, turning a parse failure into its own entry rather than skipping it.

For each ``path`` in ``paths``: ``read(path)`` is called inside a
``try``/``except silent_skip_types``, checked *before*
``except error_types`` (feat-107-doc-cache Phase 8, REQ-016). On
success, ``to_summary(doc, path)`` builds the entry. On a failure
caught by ``silent_skip_types``, ``path`` is silently omitted --
contributing to neither ``results`` nor ``error_count`` -- as if it had
never been in the directory listing to begin with. On a failure caught
by ``error_types`` instead, ``to_failed_summary(path, exc)`` builds a
failed entry -- the file is never silently dropped
(feat-81-83-validation Phase 3, REQ-006).

Parameters
----------
paths:
    The on-disk paths to read and summarize, e.g. from an
    ``iter_<domain>_paths()`` generator.
read:
    Reads and parses one path into a domain document object (e.g.
    ``read_req``). Any exception in ``silent_skip_types`` or
    ``error_types`` it raises is caught; anything else propagates.
to_summary:
    Builds one summary entry from a successfully-parsed document and
    its path (e.g. constructing a ``ReqSummary``).
to_failed_summary:
    Builds one summary entry for a path whose ``read`` call raised an
    exception caught by ``error_types`` (e.g.
    :func:`default_failed_summary` bound to the domain's own summary
    type, or ``rsk``'s sentinel-based builder). Never called for a
    ``silent_skip_types`` match.
error_types:
    The exception types to catch from ``read`` and turn into a failed
    entry. Defaults to :data:`DEFAULT_ERROR_TYPES`.
silent_skip_types:
    The exception types to catch from ``read`` and silently omit --
    checked before ``error_types``, so a type listed in both is
    silently omitted, never turned into a failed entry. Defaults to
    ``(FileNotFoundError,)`` (feat-107-doc-cache Phase 8, REQ-016): a
    file vanishing between the directory-listing snapshot that
    produced ``paths`` and this function's own per-path ``read(path)``
    call (e.g. a concurrent ``delete`` tool call racing this
    intentionally lock-free scan, ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3)
    is the same "deleted outside specmgr's own tooling" event
    REQ-005's reconcile-on-scan already handles silently for a
    deletion that completes *before* the scan starts -- a deletion
    landing *during* the scan is treated identically, not as a
    distinct, error-worthy outcome.

Returns
-------
tuple[list[_SummaryT], int]
    ``(summaries, error_count)`` -- every path's entry (success or
    failure) in the same order as ``paths``, excluding any path
    silently omitted via ``silent_skip_types``, and the count of
    failed entries among them.


### `default_failed_summary(cls: 'type[_SummaryT]', path: 'Path', error: 'Exception', *, ref: 'str | None' = None) -> '_SummaryT'`

Build a generic failed-entry summary for a plain :class:`DocSummary` subclass.

Suitable for every domain whose summary type adds no fields beyond the
shared :class:`~biz.dfch.specmgr.general.models.summary.DocSummary`
base (i.e. every domain except ``rsk``, whose failed entries are built
from a parsed sentinel document instead -- see
``rsk.tools._sentinel.build_failed_rsk_summary``).

Parameters
----------
cls:
    The domain's own ``DocSummary`` subclass to instantiate (e.g.
    ``ReqSummary``).
path:
    The on-disk path of the file that failed to parse.
error:
    The exception caught while parsing ``path``.
ref:
    The entry's ``ref`` value. Defaults to ``path.stem`` (every flat-file
    domain's own successful-entry derivation); pass e.g.
    ``path.parent.name`` for a folder-per-document domain like ``feat``.

Returns
-------
_SummaryT
    A ``cls`` instance with ``id=None``, ``title``/``status`` both set
    to :data:`FAILED_TO_PARSE_MARKER`, ``ref``/``path`` (always
    ``.resolve()``d) populated the same way a successful entry would
    be, and ``error=str(error)``.

