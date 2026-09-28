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

"""The ``get_<d>`` tools' own non-raising, structured result for the one narrowly-scoped
failure mode: a document that exists on disk but fails to parse
(feat-150-mcp-lifecycle-commands Phase 1a, ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c,
"Extend the non-raising structured-result workaround to get_<d>'s parse-failure case").

This is a distinct, purpose-built model shared by every ``get_<d>`` tool
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/``feat``/``vcr``/
``sysrs``) -- it is not a reuse or subclass of
:class:`~biz.dfch.specmgr.general.models.validate_result.ValidateResult` (the generic
``validate`` tool's own ``{valid, errors}`` shape) or of
:class:`~biz.dfch.specmgr.general.models.invalid_status_result.InvalidStatusResult` (the
generic ``set_status`` tool's own ``{valid, ...}`` shape). ``ParseFailureResult`` is the
third member of the same ADR 519d1206-4d2a-4500-9046-6db635209996 workaround chain:
``validate`` (case 1), ``set_status``'s invalid-status case (case 2), and now
``get_<d>``'s parse-failure case (case 3) -- each a narrow, non-raising, structured result
that sidesteps a client-side ``isError: true`` result truncation (empirically confirmed on
OpenCode 1.18.27) that would otherwise discard the actionable parse-failure message before
it reaches the calling agent.

It is returned by ``get_<d>`` in place of raising the domain's ``XNotFoundError`` when the
requested id resolves to an on-disk file whose content fails to parse. ``raw=True`` is
deliberately excluded from this path: a broken document must never return its raw text
through ``get_<d>`` -- the invariant that no specmgr MCP tool can return the raw content of
a document that fails to parse is load-bearing for the ``repair`` prompt's design (REQ-001).
The ``error`` text carries the same parse defect as the domain's own ``list_<d>`` tool's
failed-row ``error`` field for the same broken file -- identical field path and cause,
since both are the string form of the same domain parse exception; the trailing pydantic
documentation line may differ by read order/cache state (the ``DocCache``'s exception
reconstruction drops it on warm re-raises), so treat the two as the same defect, not
byte-equal text (Option B, 2026-09-26; the str-faithful reconstruction is tracked as
follow-up issue #162) -- a testable consistency invariant, not a loose convention.
"""

from __future__ import annotations

from pydantic import BaseModel

__all__ = ["ParseFailureResult"]


class ParseFailureResult(BaseModel):
    """``get_<d>``'s non-raising result for a document that exists but fails to parse.

    There is no successful variant of this model -- it is only ever constructed and returned
    when the requested id resolves to an on-disk file whose content fails to parse, instead
    of the domain's ``XNotFoundError`` propagating. Every other ``get_<d>`` outcome is
    unchanged: a healthy document returns the parsed ``<D>Document`` (or the body ``str``
    when ``raw=True``), a truly absent id still raises the domain's ``XNotFoundError``, and
    an invalid id shape / path injection is still a ``ValueError`` from ``validate_id``
    before any file access.

    Parameters
    ----------
    error:
        The parse-failure message -- the string form (``str()``) of the domain's own parse
        exception, captured by the domain's cache-backed ``read_<d>`` reader exactly as the
        domain's own ``list_<d>`` tool captures it for its failed row, so it carries the same
        parse defect as ``list_<d>``'s failed-row ``error`` field for the same broken file
        (identical field path and cause; the trailing pydantic documentation line may differ
        by read order/cache state, since the ``DocCache``'s exception reconstruction drops
        it on warm re-raises -- Option B, 2026-09-26, follow-up issue #162).
    path:
        The absolute, on-disk path (``Path.resolve()``d) of the file that failed to parse.
    id:
        The requested id, echoed back verbatim.
    """

    error: str
    path: str
    id: str
