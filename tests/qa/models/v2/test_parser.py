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

"""Tests for `qa.models.v2.parser.parse_qa` (ACC-003, ACC-004 -- both revised 2026-08-23).

Per the feature README's Decisions Made, REQ-004/ACC-004 were revised: there
is no `QaFrontmatter.version`-based dispatch/gate (that field was found to
encode the shared `models.md` parsing engine's own schema version, hardcoded
to major 1, and can never carry a major-2 value). `parse_qa` mirrors
`uc/models/v2/parser.py::parse_uc`'s unconditional-v2-parsing shape instead.

Covers:
- A full v2-shaped reference document (with `version: 1.0.0` frontmatter --
  the only value `QaFrontmatter.version` will ever accept) parses
  successfully end to end via `parse_qa`.
- A v1-shaped body (missing the mandatory `## Elicitation Context` section
  v2 requires) combined with otherwise-valid frontmatter fails to parse via
  v2's `parse_qa`, raising the same structural `AssertionError`
  `Qa.from_text` raises on its own -- with no fallback to v1 parsing (there
  is no v1 code path reachable here at all).
- ACC-003 cross-check: `QaDocument.frontmatter`'s declared type really is
  `qa.models.v2.frontmatter.QaFrontmatter` itself, not a lookalike duplicate
  (feat-14 Phase 8: `QaFrontmatter` moved from the now-removed `qa/models/v1/`
  into `qa/models/v2/` directly).
"""

from __future__ import annotations

import textwrap
import typing
import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.models.md._markdown import format_text
from biz.dfch.specmgr.qa.models.v2.document import QaDocument
from biz.dfch.specmgr.qa.models.v2.frontmatter import QaFrontmatter
from biz.dfch.specmgr.qa.models.v2.parser import parse_qa

# The reference example from the feature README's Design Notes (also used by
# `tests/qa/models/v2/test_body.py`), reused verbatim as the v2 body.
_REFERENCE_BODY = format_text(
    """\
# Widget Frobnicator Q&A

## General

### Introduction

<!-- filled in during the kickoff interview -->

This document captures the requirements interview for the Widget Frobnicator.

### Raw Requirements

The frobnicator must handle at least 500 widgets/minute.

## Elicitation Context

> Who are the primary stakeholders for this system?

Product management and the on-call SRE team.

## Functional Suitability

<!-- comment belongs to the question right after it -->

> What happens when the input queue is empty?

The frobnicator idles and polls every 100ms.

That polling interval is configurable via `poll_interval_ms`.

> How should malformed widgets be handled?

Malformed widgets are rejected and logged. The rejection flow is:

1. Validate the widget schema.
2. Log the failure with the widget's id.
3. Increment the `rejected_total` counter.

No retry is attempted for malformed input.

## Performance Efficiency

## Compatibility

## Interaction Capability

## Reliability

## Security

## Maintainability

## Flexibility

## Safety

## More Information

See the original ticket for background on throughput targets.
"""
)

# A v1-shaped body: every ISO/IEC 25010:2023 category is present, but the
# mandatory `## Elicitation Context` section -- v2-only, not part of v1's
# schema at all -- is missing. `Qa.from_text` (v2) must reject this
# structurally; there is no fallback to v1 parsing to "rescue" it.
_V1_SHAPED_BODY_MISSING_ELICITATION_CONTEXT = format_text(
    """\
# Simple Q&A Document

## General

### Introduction

Some intro text.

### Raw Requirements

Some raw requirements text.

## Functional Suitability

## Performance Efficiency

## Compatibility

## Interaction Capability

## Reliability

## Security

## Maintainability

## Flexibility

## Safety
"""
)


def _make_document(body: str, version: str = "1.0.0") -> str:
    frontmatter = textwrap.dedent(
        f"""\
        ---
        id: qa-002
        type: qa
        version: {version}
        status: draft
        created: '2026-08-23 00:00:00.000Z'
        updated: '2026-08-23 00:00:00.000Z'
        ---

        """
    )
    return frontmatter + body


_VALID_DOC = _make_document(_REFERENCE_BODY)


class TestParseQaAcceptsV2ShapedDocument(unittest.TestCase):
    """A v2-shaped document parses successfully via `parse_qa` (ACC-004)."""

    def test_parses_full_reference_document(self) -> None:
        document = parse_qa(_VALID_DOC)

        self.assertIsInstance(document, QaDocument)
        self.assertEqual(document.frontmatter.id, "qa-002")
        self.assertEqual(document.frontmatter.version, "1.0.0")
        self.assertEqual(document.body.text, "Widget Frobnicator Q&A")

    def test_body_reflects_v2_shape(self) -> None:
        document = parse_qa(_VALID_DOC)

        self.assertIsNotNone(document.body.elicitation_context.questions)
        self.assertEqual(len(document.body.elicitation_context.questions), 1)
        self.assertEqual(len(document.body.functional_suitability.questions), 2)
        self.assertIsNone(document.body.compatibility.questions)


class TestParseQaRejectsV1ShapedBody(unittest.TestCase):
    """A v1-shaped body fails to parse via v2's `parse_qa`, with no fallback to v1 parsing (ACC-004)."""

    def test_missing_elicitation_context_raises_the_same_structural_error_from_from_text(self) -> None:
        """feat-27 Phase 1 note: the engine's "expected ..., found no match" message now names
        the missing field by its own type identity (`ElicitationContext`, a domain-specific
        `MarkdownSection` subclass) rather than its bare attribute name (`elicitation_context`)
        -- see `models.md.markdown_str._field_label`."""
        text = _make_document(_V1_SHAPED_BODY_MISSING_ELICITATION_CONTEXT)

        with self.assertRaises(AssertionError) as ctx:
            parse_qa(text)

        self.assertIn("ElicitationContext", str(ctx.exception))

    def test_invalid_frontmatter_status_raises_validation_error(self) -> None:
        """A frontmatter value that fails `QaFrontmatter`'s own validation surfaces `ValidationError` unchanged."""
        text = _make_document(_REFERENCE_BODY).replace("status: draft", "status: not-a-real-status")

        with self.assertRaises(ValidationError):
            parse_qa(text)


class TestQaDocumentFrontmatterIsSharedQaFrontmatter(unittest.TestCase):
    """ACC-003: `QaDocument.frontmatter`'s declared type is `qa.models.v2.frontmatter.QaFrontmatter` itself."""

    def test_frontmatter_field_type_is_qa_frontmatter(self) -> None:
        hints = typing.get_type_hints(QaDocument)

        self.assertIs(hints["frontmatter"], QaFrontmatter)

    def test_frontmatter_field_info_annotation_is_qa_frontmatter(self) -> None:
        field_info = QaDocument.model_fields["frontmatter"]

        self.assertIs(field_info.annotation, QaFrontmatter)


if __name__ == "__main__":
    unittest.main()
