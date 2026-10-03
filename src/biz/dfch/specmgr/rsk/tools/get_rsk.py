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

# pylint: disable=redefined-builtin  # id/type intentionally shadow the builtins: public tool API, issue #41

"""``@mcp.tool()`` wrapper: get_rsk (Task 3.8).

Mirrors ``tsk.tools.get_tsk`` -- a thin file-I/O/id-lookup adapter. The
``.md`` file itself remains the sole source of truth (ADR
33c5ab08-ff58-4c73-8c32-23abaf3838e3); its underlying ``load_by_id`` now
routes through a content-hash-validated, per-domain in-memory cache (ADR
bfd76370-b59b-4d65-b550-a969f6c93c9d, ``._cache``) that skips re-parsing
when a file's content hash is unchanged since its last read, so a stale
entry is structurally impossible.

Implemented as a tool, not a resource, from the start -- id-based single-
document reads for RSK never had a ``specmgr://rsk/{id}`` resource in the
first place, matching TSK's own shape (ADR
ddfb1109-422d-4507-8dbc-dc5e4bec9614: "Expose id-based document reads as a
tool, not a resource").

``raw=True`` (feat-22-consolidate-mutation-tools, Phase 2) returns the
frontmatter-stripped body text verbatim instead of the parsed document --
produced by the same
:func:`~biz.dfch.specmgr.general.tools._splice.body_text` helper the
generic ``update`` tool's range splice uses, so the line numbers a client
counts in a raw read index byte-for-byte into the text the server splices
against. With optional read-style ``offset``/``limit`` coordinates
(feat-28-get-update, Phase 2), the same raw read instead returns the window
of that text, served by the shared
:func:`~biz.dfch.specmgr.general.tools._splice.window_body` helper (clamping
out-of-range values, never erroring). With an optional ``numbered=True``
(feat-153-off-by-n, Phase 3), each returned body line is additionally
prefixed with its 1-based absolute body-line number in the ``"<n>: "``
form.
"""

from __future__ import annotations

from ...general.models import ParseFailureResult
from ...general.tools._doc_paths import find_parse_failure
from ...general.tools._path_safety import assert_within, validate_id
from ...general.tools._splice import body_text, validate_read_args, window_body
from ...server import mcp
from ..models.v1 import RskDocument
from ._io import load_by_id, read_rsk
from ._paths import RskNotFoundError, rsk_base_dir


@mcp.tool(
    name="get_rsk",
    title="Get risk",
    description=(
        "Read, parse, and return a full risk document (frontmatter and body) by its id. "
        "Pass raw=True to return the frontmatter-stripped body text verbatim instead. With "
        "raw=True, optional read-style `offset`/`limit` window the raw read: `offset` (1-based, "
        "default 1) is the first body line to return, `limit` (line count, default through end "
        "of body) how many; out-of-range values clamp (`offset > N` returns the empty string), "
        "and coordinates with raw=False raise ValueError."
        " A document that exists but fails to parse returns a `ParseFailureResult` "
        "(`error`/`path`/`id`) instead of raising; "
        "its `error` text is byte-identical to the domain's own `list` tool's failed-row `error` "
        "for the same file (identical field path and cause, including the trailing pydantic "
        "documentation line; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c). "
        "An invalid id (path-injection attempt or wrong format) is also a ValueError, raised before "
        "any file access."
        " With raw=True, an optional `numbered=True` prefixes every returned body line with its 1-based "
        'absolute body-line number in the `"<n>: "` form (plain decimal, no padding) -- under '
        "`offset`/`limit` windowing the numbers start at the clamped offset and never restart at 1, so a "
        "number seen in the output can be fed straight back into the generic `update` tool's `offset`. "
        "`numbered` is meaningful only with raw=True: combining it with raw=False raises ValueError (like "
        "`offset`/`limit`), and a numbered read of a document that fails to parse returns the "
        "`ParseFailureResult` described above, never numbered text. Numbered output must never be fed back "
        'verbatim into `content` for `update` or `create_rsk` -- strip the `"<n>: "` prefix from each '
        "line first (it is likewise never a valid `edit` `old_str`)."
    ),
)
def get_rsk(
    id: str, raw: bool = False, offset: int | None = None, limit: int | None = None, numbered: bool = False
) -> RskDocument | str | ParseFailureResult:
    """Read and return the risk identified by ``id``.

    Parameters
    ----------
    id:
        The document's specmgr-assigned identifier.
    raw:
        With ``False`` (the default), return the parsed document, exactly
        as before. With ``True``, return the frontmatter-stripped body
        text verbatim as a plain string -- the same text whose 1-based
        lines the generic ``update`` tool's ``offset``/``limit``
        coordinates address (shared body-extraction helper with the
        splice) -- optionally windowed by ``offset``/``limit`` (see below).
    offset:
        With ``raw=True`` only: the 1-based first body line of the window
        to return (default 1; values below 1 floor to 1, values past the
        last body line return the empty string).
    limit:
        With ``raw=True`` only: the number of body lines the window spans
        (default through the end of the body; capped at the remaining
        lines, a negative value returns the empty string).
    numbered:
        With ``raw=True`` only: when ``True``, prefix every returned body
        line with its 1-based absolute body-line number in the ``"<n>: "``
        form (plain decimal, no padding) -- under ``offset``/``limit``
        windowing the numbers start at the clamped ``offset`` and never
        restart at 1, so a number seen in the output can be fed straight
        back into the generic ``update`` tool's ``offset``. Numbered
        output must never be fed back verbatim as ``content`` for
        ``update`` or ``create_rsk`` -- strip the ``"<n>: "`` prefix from
        each line first (it is likewise never a valid ``edit`` ``old_str``).
        Combining it with ``raw=False`` raises ``ValueError`` (see
        ``Raises``).

    Returns
    -------
    RskDocument | str | ParseFailureResult
        With ``raw=False``: the current on-disk document, freshly re-read
        and re-parsed. With ``raw=True``: the body text (or its
        ``offset``/``limit`` window) as a plain string. With
        ``numbered=True``, every returned line is additionally prefixed
        with its ``"<n>: "`` 1-based absolute body-line number. When the
        document
        exists but fails to parse, a
        :class:`~biz.dfch.specmgr.general.models.ParseFailureResult`
        (``error``/``path``/``id``) is returned instead of raising --
        ``error`` is byte-identical to the domain's own ``list`` tool's failed-row ``error`` for
        the same file (identical field path and cause, including the trailing pydantic
        documentation line; ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c);
        ``raw=True`` never returns a broken document's raw text.
        Raises :class:`._paths.RskNotFoundError` if no risk has this id.

    Raises
    ------
    ValueError
        ``id`` is a path-injection attempt or not a well-formed id for this domain
        (raised before any filesystem access), or ``offset``/``limit`` coordinates
        are given with ``raw=False`` (a parsed document requires the whole body),
        or ``numbered=True`` is given with ``raw=False`` (numbering is a
        ``raw=True``-only feature) -- both read-argument misuses raised before
        any file access.
    """
    validate_id("rsk", id)
    validate_read_args(raw, offset, limit, numbered)

    base_dir = rsk_base_dir()
    try:
        path, doc = load_by_id(base_dir, id)
    except RskNotFoundError:
        parse_failure = find_parse_failure(base_dir, id, read_rsk)
        if parse_failure is None:
            raise
        failure_path, failure_error = parse_failure
        assert_within(base_dir, failure_path)
        return ParseFailureResult(error=failure_error, path=str(failure_path.resolve()), id=id)
    assert_within(base_dir, path)
    if raw:
        text = body_text(path)
        if offset is None and limit is None and not numbered:
            result: RskDocument | str = text
            return result
        result = window_body(text, 1 if offset is None else offset, limit, numbered=numbered)
        return result
    result = doc
    return result
