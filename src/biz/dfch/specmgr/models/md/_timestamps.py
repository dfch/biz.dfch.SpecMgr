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

"""Shared, private ``T``-canonical datetime-formatting helpers for the ``models.md`` frontmatter
read path and the MCP write side (feat-146 Phase 1, ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf).

This module is the single source of the machine-written canonical date+time
form: ``yyyy-MM-ddTHH:mm:ss.fff`` (``T``-separated, ISO 8601's standard
extended combined form per ADR 23a14195-339c-48af-99d2-97c9964041ae)
followed by either ``Z`` (UTC, i.e. a zero UTC offset) or a signed
``±HH:mm`` offset, with milliseconds truncated to *exactly* three digits
(not the six-digit microsecond precision :meth:`datetime.datetime.isoformat`
produces by default). It lives here -- under ``models.md`` -- rather than in
``general.tools._timestamps`` because ``models/*`` must not import anything
under ``general`` (``general``'s own ``__init__`` transitively imports
``server.mcp``, an ``mcp``-extra-only dependency that would silently land on
the dependency-free base library; see
``models/adr/v1/summary.py``'s module docstring for the precedent).
``general.tools._timestamps.format_timestamp`` now delegates to
:func:`format_timestamp` below, so the write side and this read-side
normalization share exactly one formatting implementation.

The second function, :func:`normalize_yaml_datetime`, exists because of the
PyYAML coercion hazard (verified empirically): ``python-frontmatter`` parses
the frontmatter YAML block with PyYAML's standard loader, which auto-converts
*unquoted* timestamp values (in either the ``T`` or the space separator)
into Python :class:`~datetime.datetime` objects. Every
``MarkdownFrontmatter`` field is ``str | None``, so each domain parser's own
``_stringify_metadata`` helper must stringify such a coerced value before
Pydantic validation. A bare ``str()`` does the wrong thing in three ways:
it drops the milliseconds of a whole-millisecond value (``.123`` renders as
``.123000`` -- a rejected six-digit fraction), it renders a zero UTC offset
as ``+00:00`` instead of ``Z``, and it keeps the space separator instead of
converging the value to the ``T`` canonical form. :func:`normalize_yaml_datetime`
returns the ``T``-canonical form via :func:`format_timestamp` -- but only
when the coercion was information-preserving; a value whose original text
carried sub-millisecond fraction digits (``.123456``) would otherwise be
silently truncated into an *accepted* shape, so those are left as bare
``str()`` text for the frontmatter pattern's own actionable rejection
(six-digit fractions remain rejected -- feat-146 REQ-003/ACC-002).
"""

from __future__ import annotations

from datetime import datetime

__all__ = ["format_timestamp", "normalize_yaml_datetime"]

#: Milliseconds are truncated (not rounded) from a `datetime`'s microsecond
#: component to exactly three digits -- simpler than rounding, and matches
#: this feature's "milliseconds truncated to exactly three digits" wording
#: verbatim (feat-38-39-41-43-44 REQ-007, carried over unchanged).
_MICROSECONDS_PER_MILLISECOND = 1_000

#: A zero UTC offset formats as the literal `Z`, not `+00:00`.
_UTC_SUFFIX = "Z"


def format_timestamp(dt: datetime) -> str:
    """Format `dt` as the machine-written ``T``-canonical date+time form (feat-146).

    Accepts either an aware or a naive `datetime`; a naive value is
    formatted as-is (no UTC offset is invented for it), so its rendered
    string carries no `Z`/offset suffix and will not match the date+time
    `MarkdownFrontmatter` pattern -- callers that need a suffixed
    value (every write-side caller does) must pass an aware `datetime`,
    e.g. via `datetime.now().astimezone()` (`now_timestamp`'s own input)
    or by attaching `timezone.utc` explicitly when reinterpreting a
    legacy value as UTC.

    Args:
        dt: The datetime to format.

    Returns:
        `yyyy-MM-ddTHH:mm:ss.fff` followed by `Z` (`dt`'s UTC offset is
        exactly zero) or `dt`'s own signed `±HH:mm` offset (aware `dt`),
        or with no suffix at all (naive `dt`). Milliseconds are truncated
        (not rounded) from `dt.microsecond`.
    """
    assert isinstance(dt, datetime), type(dt)

    milliseconds = dt.microsecond // _MICROSECONDS_PER_MILLISECOND
    base = f"{dt.strftime('%Y-%m-%dT%H:%M:%S')}.{milliseconds:03d}"

    offset = dt.utcoffset()
    if offset is None:
        result = base
        return result
    if offset.total_seconds() == 0:
        result = f"{base}{_UTC_SUFFIX}"
        return result
    suffix = dt.strftime("%z")
    result = f"{base}{suffix[:3]}:{suffix[3:]}"
    return result


def normalize_yaml_datetime(value: datetime) -> str:
    """Return the text form of a PyYAML-coerced ``datetime`` frontmatter value (feat-146, REQ-006).

    Called by every whole-body domain parser's own ``_stringify_metadata``
    helper for a non-``str``, non-``None`` metadata value that is a
    ``datetime`` (i.e. an *unquoted* YAML timestamp PyYAML coerced; quoted
    values never reach this function -- they are already ``str``).

    When the coercion was information-preserving (``value.microsecond`` is a
    whole number of milliseconds, so the original text carried either no
    fraction at all or exactly the three fraction digits the canonical form
    requires), returns the ``T``-canonical form via :func:`format_timestamp`
    -- the value converges to the machine-written shape (``Z`` for a zero
    UTC offset, a signed ``±HH:mm`` offset otherwise, no suffix for a naive
    value, where the frontmatter pattern's own actionable rejection still
    applies since timezone-less values remain rejected).

    When the original text carried sub-millisecond fraction digits
    (``value.microsecond`` is not a whole number of milliseconds), a bare
    ``str(value)`` is returned instead: that text keeps the six-digit
    fraction (and the space separator), so the frontmatter pattern rejects
    it with its own actionable error -- the canonical form cannot
    represent a six-digit fraction without loss, and silently truncating
    one would turn a rejected value into an accepted one.

    Args:
        value: The coerced datetime, exactly as PyYAML produced it.

    Returns:
        The value's text form as validated by ``MarkdownFrontmatter``'s
        own date+time pattern (canonical or rejected-by-design, never
        lossy).
    """
    assert isinstance(value, datetime), type(value)

    if value.microsecond % _MICROSECONDS_PER_MILLISECOND != 0:
        result = str(value)
        return result
    result = format_timestamp(value)
    return result
