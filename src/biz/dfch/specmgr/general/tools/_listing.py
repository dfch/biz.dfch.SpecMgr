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

"""Generic, doc-type-agnostic ``list_<domain>`` summary construction (feat-81-83-validation Phase 3, Task 3.1).

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
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import ValidationError

from ..models.summary import DocSummary

__all__ = [
    "DEFAULT_ERROR_TYPES",
    "FAILED_TO_PARSE_MARKER",
    "build_summaries",
    "default_failed_summary",
]

#: The fixed marker used for a failed entry's ``title``/``status`` fields
#: (REQ-006, resolved during plan refinement -- see the feature README's
#: Design Notes).
FAILED_TO_PARSE_MARKER = "<failed to parse>"

#: Default failure-catch set for :func:`build_summaries`: exactly the three
#: content-validation-failure channels a ``parse_<domain>`` function in this
#: codebase can raise -- structural (``AssertionError``), field/cross-field
#: (``pydantic.ValidationError``), and malformed frontmatter YAML
#: (``yaml.YAMLError``, genuinely raised unwrapped by ``parse_<domain>`` --
#: confirmed via ``models/md/_frontmatter_parse.py``). Omitting
#: ``yaml.YAMLError`` would leave a document with malformed YAML frontmatter
#: crashing ``list_<domain>`` outright instead of appearing as a failed
#: entry, exactly issue #83(b)'s complaint.
DEFAULT_ERROR_TYPES: tuple[type[Exception], ...] = (AssertionError, ValidationError, yaml.YAMLError)

#: Parsed-document type read by a caller-supplied ``read`` callback.
_DocT = TypeVar("_DocT")

#: Summary model type produced by a caller-supplied ``to_summary``/``to_failed_summary`` callback.
_SummaryT = TypeVar("_SummaryT", bound=DocSummary)


def default_failed_summary(
    cls: type[_SummaryT],
    path: Path,
    error: Exception,
    *,
    ref: str | None = None,
) -> _SummaryT:
    """Build a generic failed-entry summary for a plain :class:`DocSummary` subclass.

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
    """
    assert isinstance(path, Path), type(path)
    assert isinstance(error, Exception), type(error)
    assert ref is None or isinstance(ref, str), type(ref)

    resolved_ref = path.stem if ref is None else ref

    result = cls(
        id=None,
        title=FAILED_TO_PARSE_MARKER,
        status=FAILED_TO_PARSE_MARKER,
        ref=resolved_ref,
        path=str(path.resolve()),
        error=str(error),
    )
    return result


def build_summaries(
    paths: Iterable[Path],
    read: Callable[[Path], _DocT],
    to_summary: Callable[[_DocT, Path], _SummaryT],
    to_failed_summary: Callable[[Path, Exception], _SummaryT],
    error_types: tuple[type[Exception], ...] = DEFAULT_ERROR_TYPES,
) -> tuple[list[_SummaryT], int]:
    """Read and summarize every path, turning a parse failure into its own entry rather than skipping it.

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
    """
    summaries: list[_SummaryT] = []
    error_count = 0

    for path in paths:
        try:
            doc = read(path)
        except error_types as exc:
            summaries.append(to_failed_summary(path, exc))
            error_count += 1
            continue
        summaries.append(to_summary(doc, path))

    result = (summaries, error_count)
    return result
