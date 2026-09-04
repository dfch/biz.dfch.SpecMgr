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

## Functions

### `build_summaries(paths: 'Iterable[Path]', read: 'Callable[[Path], _DocT]', to_summary: 'Callable[[_DocT, Path], _SummaryT]', to_failed_summary: 'Callable[[Path, Exception], _SummaryT]', error_types: 'tuple[type[Exception], ...]' = (<class 'AssertionError'>, <class 'pydantic_core.ValidationError'>, <class 'yaml.error.YAMLError'>)) -> 'tuple[list[_SummaryT], int]'`

Read and summarize every path, turning a parse failure into its own entry rather than skipping it.

For each ``path`` in ``paths``: ``read(path)`` is called inside a
``try``/``except error_types``. On success, ``to_summary(doc, path)``
builds the entry. On a caught failure, ``to_failed_summary(path, exc)``
builds a failed entry instead -- the file is never silently dropped
(feat-81-83-validation Phase 3, REQ-006).

Parameters
----------
paths:
    The on-disk paths to read and summarize, e.g. from an
    ``iter_<domain>_paths()`` generator.
read:
    Reads and parses one path into a domain document object (e.g.
    ``read_req``). Any exception in ``error_types`` it raises is caught;
    anything else propagates.
to_summary:
    Builds one summary entry from a successfully-parsed document and
    its path (e.g. constructing a ``ReqSummary``).
to_failed_summary:
    Builds one summary entry for a path whose ``read`` call raised a
    caught exception (e.g. :func:`default_failed_summary` bound to the
    domain's own summary type, or ``rsk``'s sentinel-based builder).
error_types:
    The exception types to catch from ``read``. Defaults to
    :data:`DEFAULT_ERROR_TYPES`.

Returns
-------
tuple[list[_SummaryT], int]
    ``(summaries, error_count)`` -- every path's entry (success or
    failure) in the same order as ``paths``, and the count of failed
    entries among them.


### `default_failed_summary(cls: 'type[_SummaryT]', path: 'Path', error: 'Exception', *, ref: 'str | None' = None, resolve: 'bool' = True) -> '_SummaryT'`

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
resolve:
    Whether ``path`` should be ``.resolve()``d before being stored in
    the entry's ``path`` field. Defaults to ``True`` for the ten plain
    domains; ``feat`` passes ``False`` in Phase 3 to keep its existing,
    as-yet-unretrofitted unresolved ``str(path)`` behavior (Phase 4,
    Task 4.2 flips this).

Returns
-------
_SummaryT
    A ``cls`` instance with ``id=None``, ``title``/``status`` both set
    to :data:`FAILED_TO_PARSE_MARKER`, ``ref``/``path`` populated the
    same way a successful entry would be, and ``error=str(error)``.

