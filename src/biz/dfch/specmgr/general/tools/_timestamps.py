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

"""Shared, private timestamp-formatting helpers for the MCP write side (feat-38-39-41-43-44 Phase 3,
Task 3.1; the ``T``-canonical form since feat-146 Phase 1).

A private, cross-domain helper in the same package and in the same style as
:mod:`_path_safety`, :mod:`_doc_paths`, and :mod:`_splice`: it has **no**
``mcp`` dependency and performs **no filesystem access** -- the functions
only inspect/format :class:`~datetime.datetime` values and return ``str``.

The machine-written canonical date+time variant (feat-146, ADR
8c889262-152b-4b8e-ae2c-75371f7a9edf) is ``yyyy-MM-ddTHH:mm:ss.fff``
(``T``-separated -- ISO 8601's standard extended combined form per ADR
23a14195) followed by either ``Z`` (UTC, i.e. a zero UTC offset) or a signed
``±HH:mm`` offset, with milliseconds truncated to *exactly* three digits.
The read side (``MarkdownFrontmatter``'s ``created``/``updated`` pattern)
accepts the space separator as well, but the MCP is the only writer of
frontmatter and always writes the ``T`` form. The formatting core itself
lives in :mod:`biz.dfch.specmgr.models.md._timestamps` (dependency-free, so
the domain parsers' own frontmatter read path can use it too -- ``models``
must not import ``general``); :func:`format_timestamp` below delegates to it,
and :func:`now_timestamp` is the one-line call site every
``create_<d>``/``update``/``set_status``/``set_classification`` adapter uses.

:func:`now_timestamp` REPLACES every one of this codebase's previous
``datetime.now().isoformat(timespec="microseconds")`` call sites (every
``create_<d>`` tool, the 22 ``update`` adapter sites, and every
``set_status`` adapter site -- Task 3.3) with one shared, consistently
formatted implementation. (The previous ``format_date`` helper -- a
narrower ``yyyy-MM-dd``-only variant for the date-only entry-heading bodies
feat-38-39-41-43-44 D4/REQ-004 allowed -- was removed in feat-146 Phase 1:
entry headings are date+time-only in every domain now, so it had zero
callers.)
"""

from __future__ import annotations

from datetime import datetime

from biz.dfch.specmgr.models.md._timestamps import format_timestamp as _shared_format_timestamp

__all__ = ["format_timestamp", "now_timestamp"]


def format_timestamp(dt: datetime) -> str:
    """Format `dt` as the machine-written ``T``-canonical date+time form (feat-146).

    Delegates to
    :func:`biz.dfch.specmgr.models.md._timestamps.format_timestamp` (the
    single formatting implementation, shared with the frontmatter read
    path) and keeps its own contract verbatim: accepts either an aware or a
    naive `datetime`; a naive value is formatted as-is (no UTC offset is
    invented for it), so its rendered string carries no `Z`/offset suffix
    and will not match the date+time `MarkdownFrontmatter` pattern --
    callers that need a suffixed value (every current caller does) must pass
    an aware `datetime`, e.g. via `datetime.now().astimezone()`
    (:func:`now_timestamp`'s own input) or by attaching `timezone.utc`
    explicitly when reinterpreting a legacy value as UTC.

    Args:
        dt: The datetime to format.

    Returns:
        `yyyy-MM-ddTHH:mm:ss.fff` followed by `Z` (`dt`'s UTC offset is
        exactly zero) or `dt`'s own signed `±HH:mm` offset (aware `dt`),
        or with no suffix at all (naive `dt`). Milliseconds are truncated
        (not rounded) from `dt.microsecond`.
    """
    assert isinstance(dt, datetime), type(dt)

    result = _shared_format_timestamp(dt)
    return result


def now_timestamp() -> str:
    """Return the current local time as the machine-written ``T``-canonical date+time form (feat-146).

    The single shared replacement for this codebase's previous
    ``datetime.now().isoformat(timespec="microseconds")`` call sites (Task
    3.3): local time with its actual UTC offset
    (``datetime.now().astimezone()``), formatted by :func:`format_timestamp`
    -- `T`-separated (the machine-written canonical form; the read side
    accepts the space separator too, but the MCP always writes `T`), `Z`
    when the local UTC offset is exactly zero (e.g. under CI, which
    typically runs UTC), else a signed `±HH:mm` offset, with milliseconds
    truncated to exactly three digits.

    Returns:
        The current local date+time, formatted per :func:`format_timestamp`.
    """
    result = format_timestamp(datetime.now().astimezone())
    return result
