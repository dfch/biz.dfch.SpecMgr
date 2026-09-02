# `biz.dfch.specmgr.general.tools._timestamps`

Shared, private timestamp-formatting helpers (feat-38-39-41-43-44 Phase 3, Task 3.1).

A private, cross-domain helper in the same package and in the same style as
:mod:`_path_safety`, :mod:`_doc_paths`, and :mod:`_splice`: it has **no**
``mcp`` dependency and performs **no filesystem access** -- the functions
only inspect/format :class:`~datetime.datetime` values and return ``str``.

This module is the single source of the canonical date+time variant (D4/D7,
``.specmgr/feat/feat-38-39-41-43-44/README.md`` Design Notes):
``yyyy-MM-dd HH:mm:ss.fff`` followed by either ``Z`` (UTC, i.e. a zero UTC
offset) or a signed ``±HH:mm`` offset -- space-separated (not ``T``), and
milliseconds truncated to *exactly* three digits (not the six-digit
microsecond precision :meth:`datetime.datetime.isoformat` produces by
default).

:func:`now_timestamp` REPLACES every one of this codebase's previous
``datetime.now().isoformat(timespec="microseconds")`` call sites (the 11
``create_<d>`` tools, the 22 ``update`` adapter sites, and the 11
``set_status`` adapter sites -- Task 3.3) with one shared, consistently
formatted implementation. :func:`format_timestamp` is the pure formatting
core :func:`now_timestamp` delegates to, exposed separately so the D7/D8
repo-document and test-fixture migrations (Tasks 3.4/3.5) can reuse the
exact same formatting logic for arbitrary, already-constructed
:class:`~datetime.datetime` values (e.g. a first-commit timestamp reinterpreted
as UTC, or a manually built midnight-UTC value) instead of re-deriving the
shape by hand. :func:`format_date` is a narrower helper for the handful of
callers that legitimately want just the ``yyyy-MM-dd`` portion (e.g. a
DEC/VCR/TSK ``UpdateEntry`` heading, which -- unlike frontmatter
``created``/``updated``, D5 -- is allowed to be date-only); frontmatter never
uses it.

## Functions

### `format_date(dt: 'datetime') -> 'str'`

Return just the `yyyy-MM-dd` portion of `dt`.

For the handful of body-entry-timestamp callers that legitimately allow
a date-only value (e.g. a DEC/VCR/TSK `UpdateEntry` heading, per Phase
2's alias) -- frontmatter `created`/`updated` never uses this (D5: those
two fields are date+time-only, enforced by
`models.md.frontmatter.MarkdownFrontmatter`'s own validator).

Args:
    dt: The datetime to format.

Returns:
    `dt.strftime("%Y-%m-%d")`.


### `format_timestamp(dt: 'datetime') -> 'str'`

Format `dt` as the canonical date+time variant (D4/D7).

Accepts either an aware or a naive `datetime`; a naive value is
formatted as-is (no UTC offset is invented for it), so its rendered
string carries no `Z`/offset suffix and will not match the date+time
`@alias`/`MarkdownFrontmatter` regex -- callers that need a suffixed
value (every current caller does) must pass an aware `datetime`, e.g.
via `datetime.now().astimezone()` (:func:`now_timestamp`'s own input)
or by attaching `timezone.utc` explicitly when migrating a legacy
value that is to be reinterpreted as UTC (D7).

Args:
    dt: The datetime to format.

Returns:
    `yyyy-MM-dd HH:mm:ss.fff` followed by `Z` (`dt`'s UTC offset is
    exactly zero) or `dt`'s own signed `±HH:mm` offset (aware `dt`),
    or with no suffix at all (naive `dt`). Milliseconds are truncated
    (not rounded) from `dt.microsecond`.


### `now_timestamp() -> 'str'`

Return the current local time as the canonical date+time variant (D4/D7).

The single shared replacement for this codebase's previous
``datetime.now().isoformat(timespec="microseconds")`` call sites (Task
3.3): local time with its actual UTC offset
(``datetime.now().astimezone()``), formatted by :func:`format_timestamp`
-- `Z` when that offset is exactly zero (e.g. under CI, which typically
runs UTC), else a signed `±HH:mm` offset, with milliseconds truncated to
exactly three digits.

Returns:
    The current local date+time, formatted per :func:`format_timestamp`.

