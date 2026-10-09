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

"""The non-raising, structured ``{valid, errors}`` result shape (feat-81-83-validation Phase 2, REQ-004).

Originally greenfield for the generic ``validate`` tool alone; since
feat-204-create-error (case 5 of the ADR 519d1206 non-raising chain) it
also backs the ``create_<d>``/``parse_<d>`` tools' own
content-validation-failure branches, and since feat-170 the generic
``update``/``edit`` tools'. This module therefore owns the two
module-scope constants every such branch must import --
:data:`_CAUGHT_EXCEPTIONS` (the exact exception channels to catch) and
:data:`_MAX_VALIDATE_ERROR_CHARS` (the ``ValidationErrorEntry.message``
cap, feat-110) -- and ``general.tools.validate`` re-exports them under
the same private names (its header imports them *before* its own
domain-model imports, so a ``create_<d>`` tool's
``from ...general.tools.validate import _CAUGHT_EXCEPTIONS,
_MAX_VALIDATE_ERROR_CHARS`` finds both names bound even while
``validate``'s own import of the domain packages is still mid-flight --
that ordering is load-bearing for the server's domain-import chain, see
the comment at the re-export site).
"""

from __future__ import annotations

import yaml
from pydantic import BaseModel, ValidationError

__all__ = ["ValidateResult", "ValidationErrorEntry"]

#: Exactly the three content-validation-failure channels the non-raising
#: branches must catch and turn into a ``{valid: False, errors: [...]}``
#: result: the structural ``AssertionError``, the field/cross-field
#: ``pydantic.ValidationError``, and ``yaml.YAMLError`` (malformed
#: frontmatter YAML -- unreachable for body-only ``create_<d>`` content,
#: which never parses a frontmatter block, but kept so every catch site
#: has the uniform shape). A bare ``ValueError`` (caller-usage errors:
#: id-shape guards, ``full``/content-shape mismatches, ...) is
#: deliberately NOT in this tuple, so it still propagates instead of
#: being absorbed (feat-170 REQ-004 / feat-204 REQ-003).
_CAUGHT_EXCEPTIONS: tuple[type[Exception], ...] = (AssertionError, ValidationError, yaml.YAMLError)

#: Caps ``ValidationErrorEntry.message``'s length (issue #110): a
#: structurally malformed document (e.g. an unexpected/duplicate heading)
#: can produce a ``str(AssertionError)``/``str(pydantic.ValidationError)``
#: several hundred characters long once ``wrap_tool_errors``'s
#: domain/tool/channel label is prepended. ``300`` deliberately matches
#: ``snippet()``'s own default ``max_chars`` (see
#: ``models/md/_markdown.py::snippet``), but is kept as its own named
#: constant rather than relying on that default implicitly, per
#: ``.specmgr/conventions.md``'s "Comparison Constants" rule. Re-exported
#: by ``general.tools.validate`` (one source of truth for the cap).
_MAX_VALIDATE_ERROR_CHARS = 300


class ValidationErrorEntry(BaseModel):
    """One error entry in a :class:`ValidateResult`'s ``errors`` list.

    Deliberately holds only ``message`` -- no ``field`` key. Pydantic-sourced
    validation errors do carry structured ``loc`` data internally (via
    ``.errors()``), but ``AssertionError``/YAML-sourced errors carry none;
    rather than populate a ``field`` key for some errors and leave it
    ``None``/absent for others depending on which validation layer raised,
    ``message`` alone is used for every error, keeping the shape predictable
    regardless of source (see
    ``.specmgr/feat/feat-81-83-validation/README.md`` Design Notes).

    Parameters
    ----------
    message:
        The already-enriched exception message (domain/tool/channel
        context plus feat-27-validation's field-path/line/cause-hint
        enrichment), derived from the caught exception's ``str()`` but
        capped at this module's own ``_MAX_VALIDATE_ERROR_CHARS``
        constant (300), re-exported by ``general.tools.validate``, via
        :func:`~biz.dfch.specmgr.models.md._markdown.snippet` (issue #110)
        rather than reused verbatim without limit -- a trailing
        ``"... (truncated)"`` suffix is appended when truncation occurred.
    """

    message: str


class ValidateResult(BaseModel):
    """The generic ``validate`` tool's return shape: never raises for a content-validation failure.

    In practice ``errors`` currently holds zero or one entries: each
    domain's validation logic performs exactly one guarded parse call, so at
    most one exception can ever be caught per invocation today -- the list
    shape is deliberate forward-compatibility (matching pydantic's own
    per-error ``.errors()`` structure, which is not yet exposed to callers),
    not an indication multiple concurrent errors are common.

    Parameters
    ----------
    valid:
        ``True`` if ``content`` validated successfully, ``False`` otherwise.
    errors:
        The validation failures caught, if any. Empty when ``valid`` is
        ``True``.
    """

    valid: bool
    errors: list[ValidationErrorEntry]
