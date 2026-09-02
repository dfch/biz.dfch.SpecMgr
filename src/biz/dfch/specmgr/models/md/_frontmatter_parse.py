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

"""Shared frontmatter-parsing error enrichment (feat-27-validation Phase 2, Tasks 2.1/2.2).

Every one of the twelve domains' ``parser.py`` modules (eleven whole-body domains plus ADR)
shares the exact same three-line shape::

    post = frontmatter.loads(text)                                    # yaml.YAMLError
    fm = SomeFrontmatter.model_validate(_stringify_metadata(post.metadata))  # ValidationError
    body = SomeBody.from_text(format_text(post.content))

This module centralizes the first two lines' error handling behind :func:`parse_frontmatter`,
so every domain parser gets identical enrichment of both frontmatter error channels without
duplicating the line-remap/message-building logic twelve times (REQ-005):

- ``yaml.YAMLError`` (malformed YAML) -- :func:`enrich_frontmatter_yaml_error` returns a
  same-type, re-raiseable copy whose location marks name "the frontmatter block" (instead of
  PyYAML's own opaque ``"<unicode string>"``) and whose line numbers are remapped from
  block-relative (relative to the YAML substring ``frontmatter.loads`` hands to PyYAML) to
  document-relative (REQ-004). No new exception type -- the returned object is the exact same
  ``type(error)`` (e.g. ``yaml.parser.ParserError``), per REQ-006.
- ``pydantic.ValidationError`` (out-of-vocabulary/invalid field values) --
  :func:`enrich_frontmatter_validation_error` returns a same-type, re-raiseable copy whose
  per-field messages are prefixed with the domain and the frontmatter field's own
  document-relative line (when locatable), per REQ-004/REQ-006.

This module deliberately is NOT ``models/md/_errors.py`` -- that name is reserved for Phase
3's Task 3.1 shared tool-boundary (domain + tool + frontmatter-vs-body) context wrapper, which
is free to reuse the helpers here (:func:`frontmatter_opening_line` in particular) rather than
duplicate them.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import TypeVar

import frontmatter
import yaml
import yaml.error
from pydantic import BaseModel, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

__all__ = [
    "parse_frontmatter",
    "frontmatter_opening_line",
    "enrich_frontmatter_yaml_error",
    "enrich_frontmatter_validation_error",
]

#: Displayed in place of PyYAML's own ``"<unicode string>"`` mark name (REQ-004).
_FRONTMATTER_BLOCK_NAME = "the frontmatter block"

#: A YAML frontmatter delimiter line (mirrors ``frontmatter.default_handlers.YAMLHandler``'s
#: own ``FM_BOUNDARY`` pattern), used to find the frontmatter block's own closing line when
#: locating a field's document-relative line number.
_DELIMITER_PATTERN = re.compile(r"^-{3,}\s*$")

#: The ``pydantic_core`` error "type" tag used for every enriched validation error below. Not
#: one of pydantic's own recognized built-in types, so ``ValidationError``'s rendering never
#: appends an unrelated "For further information visit https://errors.pydantic.dev/..." URL
#: for a message this module itself already fully composed.
_ENRICHED_ERROR_TYPE = "frontmatter_value_error"

FrontmatterT = TypeVar("FrontmatterT", bound=BaseModel)


def frontmatter_opening_line(text: str) -> int:
    """Return the 1-based document line number of the frontmatter's opening ``---`` delimiter.

    ``frontmatter.loads``/``frontmatter.parse`` call ``text.strip()`` internally before
    splitting on the ``---`` boundary (see ``frontmatter.parse``), so the opening delimiter is
    always the stripped text's own line 1 -- but any leading blank/whitespace lines in the
    *original*, unstripped ``text`` shift that delimiter's real document-relative line number.
    This restores that offset by counting the newlines within the leading whitespace
    ``str.strip()``/``str.lstrip()`` would remove.

    Parameters
    ----------
    text:
        The complete, original file content (frontmatter block and body together), exactly as
        passed to ``frontmatter.loads``.

    Returns
    -------
    int
        The 1-based document line number of the opening ``---`` delimiter line.
    """
    assert isinstance(text, str), type(text)

    leading_whitespace = text[: len(text) - len(text.lstrip())]
    result = 1 + leading_whitespace.count("\n")
    return result


def enrich_frontmatter_yaml_error(text: str, error: yaml.YAMLError) -> yaml.YAMLError:
    """Return a same-type, re-raiseable copy of ``error`` naming the frontmatter block and
    carrying document-relative line numbers (REQ-004/REQ-006).

    PyYAML's ``mark.line`` is 0-based and relative to the YAML substring
    ``frontmatter.loads`` hands it (block-relative), and ``mark.name`` is the opaque
    placeholder ``"<unicode string>"`` PyYAML uses for any string (as opposed to file) input.
    Both are replaced -- the mark's ``column``/``buffer``/``pointer`` (which drive the
    "offending snippet" PyYAML prints) are left untouched, so the underlying PyYAML detail
    (the ``context``/``problem`` messages and the source snippet) is carried alongside the
    corrected location, not replaced by it.

    Parameters
    ----------
    text:
        The complete, original file content passed to ``frontmatter.loads``.
    error:
        The ``yaml.YAMLError`` raised by ``frontmatter.loads(text)``.

    Returns
    -------
    yaml.YAMLError
        A new instance of ``type(error)`` (e.g. ``yaml.parser.ParserError``) -- the exact same
        exception type, per REQ-006 -- with enriched location marks. If ``error`` is not a
        ``yaml.error.MarkedYAMLError`` (no mark to remap), ``error`` itself is returned
        unchanged.
    """
    assert isinstance(text, str), type(text)
    assert isinstance(error, yaml.YAMLError), type(error)

    if not isinstance(error, yaml.error.MarkedYAMLError):
        result = error
        return result

    opening_line = frontmatter_opening_line(text)
    result = type(error)(
        context=error.context,
        context_mark=_remap_mark(error.context_mark, opening_line),
        problem=error.problem,
        problem_mark=_remap_mark(error.problem_mark, opening_line),
        note=error.note,
    )
    return result


def _remap_mark(mark: yaml.error.Mark | None, opening_line: int) -> yaml.error.Mark | None:
    """Return a copy of ``mark`` renamed to the frontmatter block and shifted to a
    document-relative line, or ``None`` if ``mark`` itself is ``None`` (context/problem marks
    are optional on a ``MarkedYAMLError``)."""
    assert isinstance(opening_line, int) and opening_line >= 1, opening_line

    if mark is None:
        return None
    result = yaml.error.Mark(
        name=_FRONTMATTER_BLOCK_NAME,
        index=mark.index,
        line=mark.line + (opening_line - 1),
        column=mark.column,
        buffer=mark.buffer,
        pointer=mark.pointer,
    )
    return result


def enrich_frontmatter_validation_error(text: str, error: ValidationError, *, domain: str) -> ValidationError:
    """Return a same-type, re-raiseable copy of ``error`` whose per-field messages name the
    domain, the frontmatter block, and (when locatable) a document-relative line number
    (REQ-004/Task 2.2/REQ-006).

    Parameters
    ----------
    text:
        The complete, original file content whose frontmatter failed field validation.
    error:
        The ``pydantic.ValidationError`` raised by ``SomeFrontmatter.model_validate(...)``.
    domain:
        The short domain code (e.g. ``"tsk"``, ``"req"``, ``"adr"``) to name in each enriched
        message.

    Returns
    -------
    pydantic.ValidationError
        A new ``pydantic.ValidationError`` (the exact same exception type, per REQ-006, since
        ``pydantic.ValidationError`` *is* ``pydantic_core.ValidationError`` and
        ``ValidationError.from_exception_data`` is its own public constructor) whose per-field
        messages are the enriched ones built by this function.
    """
    assert isinstance(text, str), type(text)
    assert isinstance(error, ValidationError), type(error)
    assert isinstance(domain, str) and domain.strip(), domain

    line_errors: list[InitErrorDetails] = [
        InitErrorDetails(
            type=PydanticCustomError(_ENRICHED_ERROR_TYPE, _describe_validation_error(text, domain, detail)),
            loc=detail["loc"],
            input=detail["input"],
        )
        for detail in error.errors()
    ]
    result = ValidationError.from_exception_data(error.title, line_errors)
    return result


def _describe_validation_error(text: str, domain: str, detail: dict[str, object]) -> str:
    """Build one enriched per-field message: domain + frontmatter block + field path + a
    document-relative line number (when locatable) + the original pydantic message."""
    loc = detail.get("loc", ())
    assert isinstance(loc, tuple), type(loc)

    field_path = ".".join(str(part) for part in loc) if loc else None
    location = f"{domain} frontmatter block"
    if field_path is not None:
        location += f", field {field_path!r}"
        line = _field_line(text, field_path)
        if line is not None:
            location += f" (document line {line})"
    result = f"{location}: {detail['msg']}"
    return result


def _field_line(text: str, field_name: str) -> int | None:
    """Return the 1-based document line number of ``field_name``'s own ``key:`` line within
    ``text``'s frontmatter block, or ``None`` if it cannot be located (e.g. a dotted/nested
    ``field_name``, which never appears as its own top-level ``key:`` line)."""
    assert isinstance(text, str), type(text)
    assert isinstance(field_name, str) and field_name.strip(), field_name

    lines, first_line = _frontmatter_content_lines(text)
    pattern = re.compile(rf"^{re.escape(field_name)}\s*:")
    for offset, line in enumerate(lines):
        if pattern.match(line.lstrip()):
            result = first_line + offset
            return result
    return None


def _frontmatter_content_lines(text: str) -> tuple[list[str], int]:
    """Return the frontmatter block's own content lines (the lines strictly between the
    opening and closing ``---`` delimiters) and the 1-based document line number of the first
    one."""
    assert isinstance(text, str), type(text)

    opening_line = frontmatter_opening_line(text)
    lines = text.splitlines()
    start_index = opening_line  # 0-based index of the line right after the opening delimiter
    end_index = len(lines)
    for index in range(start_index, len(lines)):
        if _DELIMITER_PATTERN.match(lines[index]):
            end_index = index
            break
    result = lines[start_index:end_index], start_index + 1
    return result


def parse_frontmatter(
    text: str,
    frontmatter_cls: type[FrontmatterT],
    *,
    domain: str,
    stringify_metadata: Callable[[dict[str, object]], dict[str, object]] | None = None,
) -> tuple[FrontmatterT, str]:
    """Parse ``text``'s YAML frontmatter block into ``frontmatter_cls``, enriching both
    frontmatter error channels uniformly (Phase 2, Tasks 2.1/2.2), and return the validated
    frontmatter plus the frontmatter-stripped body text.

    Every domain ``parser.py`` module's own ``parse_<d>`` function calls this once in place of
    its previous bare ``frontmatter.loads(text)`` / ``SomeFrontmatter.model_validate(...)``
    pair, so every domain gets identical enrichment without duplicating it.

    Parameters
    ----------
    text:
        The complete file content, YAML frontmatter block and markdown body together, exactly
        as read from disk (or submitted verbatim by an MCP tool call).
    frontmatter_cls:
        The concrete frontmatter model to validate the parsed metadata against (a
        ``MarkdownFrontmatter`` subclass for every whole-body domain, or ADR's own
        ``AdrFrontmatter``/UC v1's own ``UseCaseFrontmatter``, both plain
        ``pydantic.BaseModel`` subclasses with no shared base).
    domain:
        The short domain code (e.g. ``"tsk"``, ``"req"``, ``"adr"``) named in the enriched
        ``pydantic.ValidationError`` message.
    stringify_metadata:
        Optional metadata-normalizing callable, mirroring every domain parser's own
        ``_stringify_metadata`` helper (coercing YAML-native scalar types, e.g. dates, back to
        ``str``). Defaults to ``None``, passing ``post.metadata`` through unchanged -- matching
        ``uc/models/v1/parser.py``'s own (deliberately different) behavior, whose
        ``UseCaseFrontmatter`` fields are typed ``date``, not ``str | None``.

    Returns
    -------
    tuple[FrontmatterT, str]
        The validated frontmatter instance and the frontmatter-stripped body text
        (``post.content``), ready for ``SomeBody.from_text(format_text(...))``.

    Raises
    ------
    yaml.YAMLError
        For malformed frontmatter YAML -- the exact same exception type ``frontmatter.loads``
        itself would raise, enriched per :func:`enrich_frontmatter_yaml_error`.
    pydantic.ValidationError
        For a structurally-sound frontmatter block whose field values fail schema validation --
        the exact same exception type ``frontmatter_cls.model_validate`` itself would raise,
        enriched per :func:`enrich_frontmatter_validation_error`.
    """
    assert isinstance(text, str), type(text)
    assert isinstance(domain, str) and domain.strip(), domain

    try:
        post = frontmatter.loads(text)  # type: ignore[union-attr]
    except yaml.YAMLError as error:
        raise enrich_frontmatter_yaml_error(text, error) from error

    metadata = post.metadata if stringify_metadata is None else stringify_metadata(post.metadata)
    try:
        fm = frontmatter_cls.model_validate(metadata)
    except ValidationError as error:
        raise enrich_frontmatter_validation_error(text, error, domain=domain) from error

    result = fm, post.content
    return result
