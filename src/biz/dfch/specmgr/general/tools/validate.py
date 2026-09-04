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

# pylint: disable=redefined-builtin  # type intentionally shadows the builtin: public tool API, issue #41

"""``@mcp.tool()`` wrapper: validate (feat-81-83-validation, Phase 2).

The generic, cross-domain, type-dispatched dry-run validation tool for the
twelve whole-body document types
(``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
``feat``/``vcr``/``sysrs``). It dispatches on the explicit ``type``
parameter to a private per-domain adapter (``_validate_<d>``), each a
verbatim port of the deleted ``validate_<d>`` tool's body: ``has_frontmatter``
detection via ``bool(frontmatter.loads(content).metadata)``, then either
``<Model>.from_text(format_text(content))`` (``full=False``, body-only path)
or ``parse_<d>(content)`` (``full=True``, full-document path), wrapped in
``wrap_tool_errors(domain=..., tool="validate", channel=...)`` for message
enrichment (feat-27-validation) -- same as every deleted per-domain tool,
except the generic tool's own name (``"validate"``) is now the ``tool=``
label, mirroring ``update``'s/``set_status``'s own generic-tool-name
convention rather than the retired per-domain tool name.

Unlike ``update``/``set_status``/``set_classification``/``delete``,
``validate`` is disk-free and id-free (a content-based dry run) for all
twelve domains -- no lock, no filesystem access, no id resolution is
needed, exactly like every one of today's per-domain ``validate_<d>`` tools
already was.

**Non-raising contract (REQ-004)**: unlike every other generic tool in this
package, ``validate`` never raises for a content-validation failure. The
public :func:`validate` wraps each adapter call in
``try``/``except (AssertionError, pydantic.ValidationError, yaml.YAMLError)``
and turns a caught exception into
``{"valid": False, "errors": [{"message": str(exception)}]}`` instead of
letting it propagate -- reusing feat-27-validation's already-enriched
message verbatim as the sole error entry's ``message``. A ``full``/
content-shape mismatch (``full=True`` with body-only content, or
``full=False`` with a complete document) is a caller-usage error, not a
content-validation failure, and is **not** in that catch set: it is a bare
``ValueError`` raised by the adapter itself, before the wrapped parse call
ever runs, and it still propagates through :func:`validate` unchanged, same
as it always did through the retired per-domain tools. An unsupported
``type`` (including ``"adr"``) is likewise a ``ValueError``, raised before
any adapter runs at all.

ADR is deliberately *not* a ``type`` here, mirroring ``update``'s/
``set_classification``'s/``delete``'s own exclusion: ``validate_adr`` is
structurally the odd one out among the (previously) thirteen
``validate_<d>`` tools -- ``id``-based and disk-touching, with no ``full``
parameter, and its own structural-failure channel is ``AdrParseError``
(a ``ValueError`` subclass) rather than ``AssertionError`` -- so it is kept
as its own standalone tool, unchanged, and excluded from this
consolidation. See ADR 078bf395-0a5f-4afd-84f6-b7a2191a00e6, which extends
ADR 36905d5b-8057-4294-8665-c7eed5534db0's dispatch-only convention
(previously covering only mutation-adjacent tools) to this read-only/
dry-run tool category.

The parameter is intentionally named ``type`` (it matches the frontmatter
field vocabulary the client already knows); no enabled ruff rule objects
to the builtin shadow.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import frontmatter
import yaml
from pydantic import ValidationError

from ...dec.models.v1 import Decision, parse_dec
from ...feat.models.v1 import Feature, parse_feat
from ...general.models import ValidateResult, ValidationErrorEntry
from ...gol.models.v1 import Goal, parse_gol
from ...models.md._errors import BODY_CHANNEL, wrap_tool_errors
from ...models.md._markdown import format_text
from ...prb.models.v1 import Prb, parse_prb
from ...qa.models.v2 import Qa, parse_qa
from ...req.models.v1 import Requirement, parse_req
from ...rsk.models.v1 import Risk, parse_rsk
from ...server import mcp
from ...sop.models.v1 import Sop, parse_sop
from ...sysrs.models.v1 import Sysrs, parse_sysrs
from ...tsk.models.v1 import Task, parse_tsk
from ...uc.models.v2 import UseCase, parse_uc
from ...vcr.models.v1 import Vcr, parse_vcr

__all__ = ["validate"]

#: The twelve whole-body domains the generic validate tool covers (ADR excluded).
_VALIDATE_TYPES = ("req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "sysrs")

#: Exactly the three content-validation-failure channels REQ-004 requires be caught and turned
#: into a non-raising {valid: False, errors: [...]} result. A bare ValueError (the full/
#: content-shape-mismatch case, or an unsupported type) is deliberately NOT in this tuple, so it
#: still propagates instead of being absorbed.
_CAUGHT_EXCEPTIONS: tuple[type[Exception], ...] = (AssertionError, ValidationError, yaml.YAMLError)


def _validate_req(content: str, full: bool) -> None:
    """Validate ``content`` as requirement markdown -- verbatim port of the retired ``validate_req``.

    See the module docstring for the shared ``has_frontmatter``/``full``
    semantics every adapter in this module follows.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="req", tool="validate"):
            parse_req(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="req", tool="validate", channel=BODY_CHANNEL):
            Requirement.from_text(format_text(content))


def _validate_uc(content: str, full: bool) -> None:
    """Validate ``content`` as use case markdown -- verbatim port of the retired ``validate_uc``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="uc", tool="validate"):
            parse_uc(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="uc", tool="validate", channel=BODY_CHANNEL):
            UseCase.from_text(format_text(content))


def _validate_tsk(content: str, full: bool) -> None:
    """Validate ``content`` as task list markdown -- verbatim port of the retired ``validate_tsk``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="tsk", tool="validate"):
            parse_tsk(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="tsk", tool="validate", channel=BODY_CHANNEL):
            Task.from_text(format_text(content))


def _validate_qa(content: str, full: bool) -> None:
    """Validate ``content`` as QA markdown -- verbatim port of the retired ``validate_qa``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="qa", tool="validate"):
            parse_qa(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="qa", tool="validate", channel=BODY_CHANNEL):
            Qa.from_text(format_text(content))


def _validate_prb(content: str, full: bool) -> None:
    """Validate ``content`` as problem statement markdown -- verbatim port of the retired ``validate_prb``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="prb", tool="validate"):
            parse_prb(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="prb", tool="validate", channel=BODY_CHANNEL):
            Prb.from_text(format_text(content))


def _validate_gol(content: str, full: bool) -> None:
    """Validate ``content`` as goal markdown -- verbatim port of the retired ``validate_gol``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="gol", tool="validate"):
            parse_gol(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="gol", tool="validate", channel=BODY_CHANNEL):
            Goal.from_text(format_text(content))


def _validate_rsk(content: str, full: bool) -> None:
    """Validate ``content`` as risk markdown -- verbatim port of the retired ``validate_rsk``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="rsk", tool="validate"):
            parse_rsk(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="rsk", tool="validate", channel=BODY_CHANNEL):
            Risk.from_text(format_text(content))


def _validate_dec(content: str, full: bool) -> None:
    """Validate ``content`` as decision markdown -- verbatim port of the retired ``validate_dec``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="dec", tool="validate"):
            parse_dec(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="dec", tool="validate", channel=BODY_CHANNEL):
            Decision.from_text(format_text(content))


def _validate_sop(content: str, full: bool) -> None:
    """Validate ``content`` as SOP markdown -- verbatim port of the retired ``validate_sop``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="sop", tool="validate"):
            parse_sop(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="sop", tool="validate", channel=BODY_CHANNEL):
            Sop.from_text(format_text(content))


def _validate_feat(content: str, full: bool) -> None:
    """Validate ``content`` as feature markdown -- verbatim port of the retired ``validate_feat``.

    See :func:`_validate_req` for the shared semantics. Note that
    ``full=True`` does **not** check the "frontmatter ``id`` equals
    containing folder's name" invariant -- that is enforced at the
    addressing/tool layer (``feat.tools._paths``), not here, since this
    disk-free tool has no path/folder-name to check against.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="feat", tool="validate"):
            parse_feat(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="feat", tool="validate", channel=BODY_CHANNEL):
            Feature.from_text(format_text(content))


def _validate_vcr(content: str, full: bool) -> None:
    """Validate ``content`` as verification case record markdown -- verbatim port of the retired ``validate_vcr``.

    See :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="vcr", tool="validate"):
            parse_vcr(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="vcr", tool="validate", channel=BODY_CHANNEL):
            Vcr.from_text(format_text(content))


def _validate_sysrs(content: str, full: bool) -> None:
    """Validate ``content`` as System Requirements Specification markdown.

    Verbatim port of the retired ``validate_sysrs`` -- see
    :func:`_validate_req` for the shared semantics.
    """
    has_frontmatter = bool(frontmatter.loads(content).metadata)  # type: ignore[union-attr]

    if full:
        if not has_frontmatter:
            raise ValueError(
                "full=True requires 'content' to be a complete document (YAML frontmatter block "
                "plus body) -- no frontmatter block was found. Pass full=False (the default) to "
                "validate body-only content instead."
            )
        with wrap_tool_errors(domain="sysrs", tool="validate"):
            parse_sysrs(content)
    else:
        if has_frontmatter:
            raise ValueError(
                "full=False requires 'content' to be body markdown only -- a YAML frontmatter "
                "block was found. Pass full=True to validate a complete document instead."
            )
        with wrap_tool_errors(domain="sysrs", tool="validate", channel=BODY_CHANNEL):
            Sysrs.from_text(format_text(content))


#: Dispatch table mapping the ``type`` value to its private adapter.
_ADAPTERS: dict[str, Callable[[str, bool], None]] = {
    "req": _validate_req,
    "uc": _validate_uc,
    "tsk": _validate_tsk,
    "qa": _validate_qa,
    "prb": _validate_prb,
    "gol": _validate_gol,
    "rsk": _validate_rsk,
    "dec": _validate_dec,
    "sop": _validate_sop,
    "feat": _validate_feat,
    "vcr": _validate_vcr,
    "sysrs": _validate_sysrs,
}


@mcp.tool(
    name="validate",
    title="Validate document content",
    description=(
        "Disk-free, id-free dry run validating document content across the twelve whole-body "
        "domains (`type` is one of req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr, sysrs; "
        "`adr` is not supported -- use `validate_adr` instead). `full=False` (default) validates "
        "body-only content (no frontmatter); `full=True` validates a complete document "
        "(frontmatter + body). Never raises for a content-validation failure: always returns "
        "`{valid: bool, errors: list[{message: str}]}` -- `errors` is empty when `valid` is "
        "`True`. A `full`/content-shape mismatch, or an unsupported `type`, is a caller-usage "
        "error and still raises `ValueError` before any validation runs. This is the sole "
        "validate entry point for these twelve domains -- the former per-domain `validate_<d>` "
        "tools are removed; `validate_adr` remains a separate, unchanged, id-based tool."
    ),
)
def validate(
    type: Literal["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr", "sysrs"],
    content: str,
    full: bool = False,
) -> ValidateResult:
    """Validate ``content`` as markdown of the given document ``type``, without reading or writing any file.

    Cross-domain generic for every whole-body document type
    (``req``/``uc``/``tsk``/``qa``/``prb``/``gol``/``rsk``/``dec``/``sop``/
    ``feat``/``vcr``/``sysrs``); dispatches on ``type`` to the domain's own
    private adapter (same ``has_frontmatter`` detection, same
    ``full=True``/``full=False`` body-only-vs-complete-document semantics,
    same ``wrap_tool_errors`` message enrichment as every retired
    per-domain ``validate_<d>`` tool). "Validate" means letting the
    domain's own Pydantic model/document validators run during parsing --
    there is no separate validation pass; successfully constructing the
    model *is* the validation.

    Unlike every other generic tool in ``general.tools``, ``validate``
    never raises for a content-validation failure (REQ-004): a caught
    ``AssertionError``, ``pydantic.ValidationError``, or ``yaml.YAMLError``
    (``full=True`` only, malformed frontmatter YAML) is turned into
    ``ValidateResult(valid=False, errors=[ValidationErrorEntry(message=str(exception))])``
    instead of propagating -- reusing feat-27-validation's already-enriched
    message (field path, line reference, cause/fix hint, plus this tool's
    own domain/``validate``/channel prefix) verbatim as the sole error
    entry's ``message``.

    A ``full``/content-shape mismatch is a caller-usage error, not a
    content-validation failure, and is **not** caught: ``content`` must be
    body markdown only when ``full=False`` (the shape ``create_<d>`` and
    the generic ``update`` tool accept), or a complete document
    (frontmatter and body together) when ``full=True`` -- passing the
    wrong shape raises ``ValueError`` before the domain's own parse/
    validation logic ever runs. An unsupported ``type`` (including
    ``"adr"``, which has its own standalone ``validate_adr`` tool) is
    likewise a ``ValueError``, raised before any adapter is dispatched.

    Parameters
    ----------
    type:
        The document type / domain: one of ``req``, ``uc``, ``tsk``,
        ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``, ``feat``,
        ``vcr``, ``sysrs``.
    content:
        The markdown to validate.
    full:
        ``False`` (default): ``content`` must be body markdown only.
        ``True``: ``content`` must be a complete document (frontmatter and
        body together).

    Returns
    -------
    ValidateResult
        ``{valid: True, errors: []}`` on success;
        ``{valid: False, errors: [{message: "..."}]}`` on a caught
        content-validation failure.

    Raises
    ------
    ValueError
        ``type`` is not one of the twelve supported domains (including
        ``"adr"``), or ``full`` does not match whether ``content`` carries
        a frontmatter block.
    """
    if type not in _ADAPTERS:
        raise ValueError(
            f"unknown document type {type!r}; expected one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/"
            "feat/vcr/sysrs ('adr' is not supported -- use validate_adr instead)"
        )

    adapter = _ADAPTERS[type]
    try:
        adapter(content, full)
    except _CAUGHT_EXCEPTIONS as ex:
        return ValidateResult(valid=False, errors=[ValidationErrorEntry(message=str(ex))])
    return ValidateResult(valid=True, errors=[])
