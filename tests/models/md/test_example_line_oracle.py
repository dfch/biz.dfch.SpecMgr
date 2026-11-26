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

"""feat-253-md-line-offset ACC-009: example-file oracle for every parsed child's `_line` (GitHub issue #253).

Parses the packaged `{domain}_example.md` of every whole-body domain (all of
them are built on the shared `models/md` engine) and checks, for every parsed
child at every nesting level, that line `child._line` of the mdformat-
normalized body is the first line of that child's own text (`str(child)`).

The same oracle also runs over the packaged guidance documents of the
non-whole-body `models/md` consumers -- the six REQ-004 names (`rsk`'s TARA
and risk-matrix documents, and `general`'s DTAIS, EARS, ISO/IEC/IEEE 29148
and RASCI documents) plus `general`'s ISO/IEC 25010 document as added
coverage (its model `models/iso25010.py` is not in REQ-004's consumer
list), parsed by each model's own `parse_*` function.

The oracle needs no hand-computed line numbers. Two renderings of the same
line count as equal: leading/trailing whitespace is ignored (a nested child is
rendered dedented, while the body carries the parent's indent), and so is the
number of an ordered-list marker (mdformat renumbers an ordered list item that
is rendered on its own, e.g. `01.` in the body becomes `1.`).
"""

from __future__ import annotations

import functools
import re
import unittest
from collections.abc import Callable
from importlib.resources import files

import frontmatter

from biz.dfch.specmgr.general.models.dtais import parse_dtais
from biz.dfch.specmgr.general.models.ears import parse_ears
from biz.dfch.specmgr.general.models.iso29148 import parse_iso29148
from biz.dfch.specmgr.general.models.rasci import parse_rasci
from biz.dfch.specmgr.general.tools._domains import WHOLE_BODY_DOMAINS, whole_body_domain
from biz.dfch.specmgr.models.iso25010 import parse_iso25010
from biz.dfch.specmgr.models.md import MarkdownStr
from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.rsk.models.v1 import parse_risk_matrix, parse_tara

#: The packaged guidance documents of the non-whole-body `models/md` consumers (see the module docstring):
#: `{file name: (data package, parse function)}`. None of them has YAML frontmatter.
_GUIDANCE_DOCUMENTS: dict[str, tuple[str, Callable[[str], MarkdownStr]]] = {
    "rsk_tara.md": ("biz.dfch.specmgr.rsk.data", parse_tara),
    "rsk_risk_matrix.md": ("biz.dfch.specmgr.rsk.data", parse_risk_matrix),
    "general_dtais.md": ("biz.dfch.specmgr.general.data", parse_dtais),
    "general_ears.md": ("biz.dfch.specmgr.general.data", parse_ears),
    "general_iso29148.md": ("biz.dfch.specmgr.general.data", parse_iso29148),
    "general_rasci.md": ("biz.dfch.specmgr.general.data", parse_rasci),
    "general_iso25010.md": ("biz.dfch.specmgr.general.data", parse_iso25010),
}

#: The leading number of an ordered-list marker (`1.`, `01)`), ignored by `_comparable`.
_ORDERED_MARKER_NUMBER = re.compile(r"^\d+(?=[.)](?:\s|$))")


def _comparable(line: str) -> str:
    """Return `line` without surrounding whitespace and without the number of an ordered-list marker.

    Args:
        line: One line of the normalized body, or the first line of a child's text.

    Returns:
        The comparable form of `line`.
    """
    result = _ORDERED_MARKER_NUMBER.sub("", line.strip())
    return result


def _children(node: MarkdownStr) -> list[MarkdownStr]:
    """Return every parsed child of `node` at every nesting level, depth first, in field order.

    Args:
        node: A parsed `models/md` instance.

    Returns:
        Every `MarkdownStr` held by a declared field of `node` or of one of its descendants.
    """
    result: list[MarkdownStr] = []
    for field_name in type(node).model_fields:
        value = getattr(node, field_name)
        for item in value if isinstance(value, list) else [value]:
            if isinstance(item, MarkdownStr):
                result.append(item)
                result.extend(_children(item))
    return result


@functools.cache
def _parse_example(domain: str) -> tuple[str, list[MarkdownStr]]:
    """Parse `domain`'s packaged example file and return its normalized body plus every parsed child.

    Cached, so each example is parsed once per test process.

    Args:
        domain: A whole-body domain name (one of `WHOLE_BODY_DOMAINS`).

    Returns:
        The mdformat-normalized body text (the text the domain parser hands to
        the engine) and every parsed child of the body (see `_children`).
    """
    text = files(f"biz.dfch.specmgr.{domain}.data").joinpath(f"{domain}_example.md").read_text(encoding="utf-8")
    body_text = format_text(frontmatter.loads(text).content)
    document = whole_body_domain(domain).parse_text(text)
    result = (body_text, _children(document.body))
    return result


@functools.cache
def _parse_guidance_document(name: str) -> tuple[str, list[MarkdownStr]]:
    """Parse the packaged guidance document `name` and return its normalized text plus every parsed child.

    Cached, so each document is parsed once per test process.

    Args:
        name: A file name (one of the keys of `_GUIDANCE_DOCUMENTS`).

    Returns:
        The mdformat-normalized text (the text the model's `parse_*` function
        hands to the engine) and every parsed child of the root document
        (see `_children`).
    """
    package, parse = _GUIDANCE_DOCUMENTS[name]
    text = files(package).joinpath(name).read_text(encoding="utf-8")
    result = (format_text(text), _children(parse(text)))
    return result


def _line_mismatches(label: str, body_text: str, children: list[MarkdownStr]) -> list[str]:
    """Return one description per parsed child whose `_line` is not the first line of its own text.

    Args:
        label: The name of the parsed document, used as the prefix of each description.
        body_text: The mdformat-normalized text the engine parsed.
        children: Every parsed child of the document (see `_children`).

    Returns:
        `"{label}: {path} reports line {n}, ..."` for every mismatching child;
        empty when every child's `_line` is correct.
    """
    lines = body_text.splitlines()
    result: list[str] = []
    for child in children:
        rendered = str(child)
        expected = _comparable(rendered.splitlines()[0]) if rendered else ""
        actual = _comparable(lines[child._line - 1]) if 0 < child._line <= len(lines) else None
        if actual != expected:
            result.append(f"{label}: {child._path} reports line {child._line} ({actual!r}), expected {expected!r}")
    return result


class TestExampleFileLineOracle(unittest.TestCase):
    """ACC-009: every parsed child's `_line` points at the first line of its own text in the normalized body."""

    def test_every_example_has_parsed_children(self) -> None:
        sut = {domain: len(_parse_example(domain)[1]) for domain in WHOLE_BODY_DOMAINS}

        result = [domain for domain, count in sut.items() if count == 0]

        self.assertEqual(result, [])

    def test_every_parsed_child_line_is_the_first_line_of_its_text(self) -> None:
        sut = [
            mismatch for domain in WHOLE_BODY_DOMAINS for mismatch in _line_mismatches(domain, *_parse_example(domain))
        ]

        self.assertFalse(sut, f"{len(sut)} child line(s) wrong, first: {sut[:5]}")


class TestGuidanceDocumentLineOracle(unittest.TestCase):
    """ACC-009 (REQ-004): the same oracle over the packaged guidance documents of the non-whole-body consumers."""

    def test_every_guidance_document_has_parsed_children(self) -> None:
        sut = {name: len(_parse_guidance_document(name)[1]) for name in _GUIDANCE_DOCUMENTS}

        result = [name for name, count in sut.items() if count == 0]

        self.assertEqual(result, [])

    def test_every_parsed_child_line_is_the_first_line_of_its_text(self) -> None:
        for name in _GUIDANCE_DOCUMENTS:
            with self.subTest(document=name):
                sut = _line_mismatches(name, *_parse_guidance_document(name))

                self.assertFalse(sut, f"{len(sut)} child line(s) wrong, first: {sut[:5]}")


if __name__ == "__main__":
    unittest.main()
